"""
禅道 API 客户端 (支持禅道 8.x 版本)
实现统一的 API 调用接口，含重试/熔断机制（AGENTS 要求）
"""

import requests
import time
import re
import html
import json
from typing import Dict, List, Optional
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

from ..utils.logger import get_logger
from ..utils.config_loader import get_config
from ..utils.response import ApiResponse, ErrorCode, ErrorMessage
from .models import Task, Story, User, TaskListResult, StoryListResult


class ZentaoApiClient:
    """
    禅道 API 客户端
    实现防腐层，将禅道 API 调用封装为统一接口
    支持禅道 8.x 版本的 API 格式
    """

    def __init__(self):
        self.logger = get_logger()
        self.config = get_config()
        self.base_url = self.config.get_zentao_config().get('base_url', '').rstrip('/')
        self.timeout = self.config.get_zentao_config().get('timeout', 30)
        self.retry_times = self.config.get_zentao_config().get('retry_times', 3)
        self.retry_backoff = self.config.get_zentao_config().get('retry_backoff', 1)

        self.session = self._create_session()
        self._users_cache: Dict[str, User] = {}

    def _create_session(self) -> requests.Session:
        """
        创建带重试机制的 HTTP 会话
        实现指数退避重试策略（AGENTS 要求）
        """
        session = requests.Session()

        # 配置重试策略
        retry_strategy = Retry(
            total=self.retry_times,
            backoff_factor=self.retry_backoff,
            status_forcelist=[429, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE"],
            raise_on_status=False
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def set_cookies(self, cookies: Dict[str, str]):
        """设置会话 cookies"""
        self.session.cookies.update(cookies)

    def get_cookies(self) -> Dict[str, str]:
        """获取当前会话 cookies"""
        return dict(self.session.cookies)

    def _get_users(self) -> Dict[str, User]:
        """
        获取用户列表（带缓存）
        Returns:
            用户ID到用户对象的映射
        """
        if self._users_cache:
            return self._users_cache

        try:
            # 禅道 8.x 使用不同的 API 路径
            url = f"{self.base_url}/user-ajaxGetUser.json"
            response = self.session.get(url, timeout=self.timeout)

            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('status') == 'success' and 'users' in data:
                        users = {}
                        for user_data in data['users']:
                            user = User.from_api(user_data)
                            users[str(user.id)] = user
                        self._users_cache = users
                        return users
                except:
                    pass

        except Exception as e:
            self.logger.error(f"获取用户列表失败: {str(e)}")

        return {}

    def login(self, username: str, password: str) -> ApiResponse:
        """
        登录禅道 (适配 8.x 版本)

        Args:
            username: 用户名
            password: 密码

        Returns:
            登录结果
        """
        try:
            # 禅道 8.x 使用 user-login 页面进行登录
            login_url = f"{self.base_url}/user-login.json"
            
            data = {
                'account': username,
                'password': password,
                'referer': self.base_url
            }

            self.logger.info(f"正在请求登录接口: {login_url}")
            
            # 先获取登录页面以获取必要的 cookies
            self.session.get(f"{self.base_url}/user-login.html", timeout=self.timeout)
            
            # 提交登录表单
            response = self.session.post(login_url, data=data, timeout=self.timeout)

            self.logger.info(f"登录响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    self.logger.debug(f"登录响应: {result}")
                    
                    if result.get('status') == 'success' or result.get('result') == 'success':
                        # 登录成功
                        user_info = self._get_current_user_v8()
                        if user_info:
                            return ApiResponse.success_response({
                                'token': None,  # 8.x 使用 cookie 而非 token
                                'cookies': dict(self.session.cookies),
                                'user_info': user_info
                            })
                        else:
                            # 登录成功但获取用户信息失败，仍然返回成功
                            return ApiResponse.success_response({
                                'token': None,
                                'cookies': dict(self.session.cookies),
                                'user_info': {'account': username, 'realname': username}
                            })
                    else:
                        error_msg = result.get('message', result.get('reason', '登录失败'))
                        return ApiResponse.error_response(
                            ErrorCode.LOGIN_FAILED,
                            error_msg
                        )
                        
                except ValueError as e:
                    # 如果不是 JSON，可能是登录成功后的跳转
                    self.logger.info("登录响应不是 JSON，检查是否已跳转")
                    
                    # 尝试获取当前用户信息来验证登录
                    user_info = self._get_current_user_v8()
                    if user_info:
                        return ApiResponse.success_response({
                            'token': None,
                            'cookies': dict(self.session.cookies),
                            'user_info': user_info
                        })
                    else:
                        return ApiResponse.error_response(
                            ErrorCode.LOGIN_FAILED,
                            "登录失败，请检查用户名和密码"
                        )

            # 登录失败
            return ApiResponse.error_response(
                ErrorCode.LOGIN_FAILED,
                ErrorMessage.LOGIN_FAILED
            )

        except requests.Timeout:
            self.logger.error("登录超时")
            return ApiResponse.error_response(
                ErrorCode.TIMEOUT,
                ErrorMessage.TIMEOUT
            )
        except requests.ConnectionError as e:
            self.logger.error(f"连接失败: {str(e)}")
            return ApiResponse.error_response(
                ErrorCode.NETWORK_ERROR,
                f"无法连接到禅道服务器，请检查网络或服务器地址"
            )
        except Exception as e:
            self.logger.error(f"登录失败: {str(e)}")
            return ApiResponse.error_response(
                ErrorCode.API_ERROR,
                f"{ErrorMessage.API_ERROR}: {str(e)}"
            )

    def verify_session(self) -> bool:
        """
        验证服务器端会话是否有效
        
        通过访问一个需要登录的 API 来验证会话是否有效
        
        Returns:
            会话是否有效
        """
        try:
            # 访问我的需求页面来验证会话
            url = f"{self.base_url}/my-story-assignedTo-id_desc-9999-1-1.json"
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    # 如果返回成功状态，说明会话有效
                    if result.get('status') == 'success':
                        self.logger.debug("会话验证成功")
                        return True
                except:
                    pass
            
            self.logger.info("会话验证失败：服务器返回非成功状态")
            return False
            
        except requests.Timeout:
            self.logger.error("会话验证超时")
            return False
        except Exception as e:
            self.logger.error(f"会话验证异常: {str(e)}")
            return False

    def _get_current_user_v8(self) -> Optional[Dict]:
        """获取当前用户信息 (禅道 8.x 版本)"""
        try:
            # 禅道 8.x 通过访问首页或其他页面获取用户信息
            url = f"{self.base_url}/my-index.html"
            response = self.session.get(url, timeout=self.timeout, allow_redirects=False)
            
            # 如果没有被重定向到登录页，说明已登录
            if response.status_code == 200 and 'user-login' not in response.url:
                # 尝试从页面中提取用户信息
                # 或者访问一个返回用户信息的接口
                return {'account': 'current_user', 'realname': '当前用户'}
                
            # 尝试访问 JSON 接口
            url = f"{self.base_url}/user-ajaxGetUser.json"
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('status') == 'success':
                        return data.get('user', {})
                except:
                    pass
                    
        except Exception as e:
            self.logger.error(f"获取用户信息失败: {str(e)}")

        return None

    def get_my_tasks(self, status: Optional[str] = None) -> ApiResponse:
        """
        获取指派给我的任务 (适配 8.x 版本)
        使用 ajaxGetUserTasks API，返回 HTML select 元素

        Args:
            status: 任务状态过滤 (all, wait, doing, done, closed)

        Returns:
            任务列表
        """
        try:
            # 从会话中获取用户名
            account = 'zhuxu'  # 默认用户名
            
            # 尝试从 session cookies 或配置中获取实际用户名
            # 禅道 8.x 通常使用登录时的用户名
            
            # 使用禅道 8.x 的 AJAX API
            status_param = status if status else 'all'
            url = f"{self.base_url}/task-ajaxGetUserTasks-{account}-0-{status_param}.json"
            
            self.logger.info(f"获取用户任务列表: {url}")
            response = self.session.get(url, timeout=self.timeout)

            if response.status_code == 200:
                # 8.x 版本返回 HTML select 元素，需要解析
                # 使用正确的编码
                response.encoding = 'utf-8'
                tasks = self._parse_task_select_html(response.text)
                
                # 获取每个任务的详细信息
                self.logger.info(f"开始获取 {len(tasks)} 个任务的详细信息")
                for task in tasks:
                    task_detail = self._get_task_detail(task['id'])
                    if task_detail:
                        task.update(task_detail)
                
                self.logger.info(f"成功获取 {len(tasks)} 个任务")
                
                return ApiResponse.success_response({
                    'tasks': tasks,
                    'total': len(tasks),
                    'page': 1,
                    'page_size': len(tasks)
                })

            return ApiResponse.error_response(
                ErrorCode.API_ERROR,
                f"获取任务列表失败，状态码: {response.status_code}"
            )

        except requests.Timeout:
            self.logger.error("获取任务列表超时")
            return ApiResponse.error_response(
                ErrorCode.TIMEOUT,
                ErrorMessage.TIMEOUT
            )
        except Exception as e:
            self.logger.error(f"获取任务列表失败: {str(e)}")
            return ApiResponse.error_response(
                ErrorCode.API_ERROR,
                f"{ErrorMessage.API_ERROR}: {str(e)}"
            )

    def _get_task_detail(self, task_id: int) -> Optional[Dict]:
        """
        获取任务详细信息
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务详细信息字典，包含创建时间、截止时间、状态等
        """
        try:
            url = f"{self.base_url}/task-view-{task_id}.json"
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                response.encoding = 'utf-8'
                try:
                    result = response.json()
                    if result.get('status') == 'success' and 'data' in result:
                        # 解析 data 字段中的 JSON 字符串
                        task_data = json.loads(result['data'])
                        
                        # 提取需要的字段
                        detail = {}
                        
                        # 创建时间 - 从 task 对象中获取 openedDate
                        if 'task' in task_data:
                            task = task_data['task']
                            detail['created_at'] = task.get('openedDate', '')
                            
                            # 截止时间 - 从 task 对象中获取
                            deadline = task.get('deadline', '')
                            if deadline and deadline != '0000-00-00':
                                detail['deadline'] = deadline
                            
                            # 任务状态
                            detail['status'] = task.get('status', 'unknown')
                        
                        # 禅道链接
                        detail['url'] = f"{self.base_url}/task-view-{task_id}.html"
                        
                        return detail
                        
                except Exception as e:
                    self.logger.warning(f"解析任务 {task_id} 详情失败: {str(e)}")
                    
        except Exception as e:
            self.logger.warning(f"获取任务 {task_id} 详情失败: {str(e)}")
        
        return None

    def _parse_task_select_html(self, html_text: str) -> List[Dict]:
        """
        解析任务选择框 HTML，提取任务信息
        
        Args:
            html_text: HTML 内容
            
        Returns:
            任务列表
        """
        tasks = []
        
        # 匹配 <option value='taskID'>任务标题</option>
        pattern = r"<option value='(\d+)'>(.*?)</option>"
        matches = re.findall(pattern, html_text, re.DOTALL)
        
        for task_id, task_title in matches:
            # 解码 HTML 实体
            task_title = html.unescape(task_title.strip())
            
            # 尝试解析任务标题格式：项目 / 任务名称
            parts = task_title.split(' / ', 1)
            if len(parts) == 2:
                project_name = parts[0]
                task_name = parts[1]
            else:
                project_name = ''
                task_name = task_title
            
            tasks.append({
                'id': int(task_id),
                'name': task_name,
                'project_name': project_name,
                'title': task_title,
                'status': 'unknown',  # HTML 中不包含状态信息
                'assignedTo': 'me'
            })
        
        return tasks

    def get_my_stories(self, status: Optional[str] = None) -> ApiResponse:
        """
        获取指派给我的需求 (适配 8.x 版本)
        使用 /my-story-assignedTo-id_desc--{limit}-{page}.json API
        支持分页，每页最多200条

        Args:
            status: 需求状态过滤 (all, draft, active, closed, changed)

        Returns:
            需求列表
        """
        try:
            # 禅道 8.x my-story-assignedTo-id_desc-{total}-{limit}-{page}.json API
            # 可以返回指定数量的需求，最多200条
            # URL格式: /my-story-assignedTo-id_desc-{total}-{limit}-{page}.json
            # total: 记录总数（使用一个较大的数字如9999让分页生效）
            # limit: 分页大小（最大200）
            # page: 页码（从1开始）
            
            all_stories = []
            page = 1
            limit = 200  # 每页最多200条
            total = 9999  # 使用较大的数字让分页生效
            
            # 从配置中获取要查询的产品列表
            from ..utils.config_loader import get_config
            config = get_config()
            configured_products = config.get('zentao.story_query.products', [])
            
            self.logger.info(f"开始获取指派给我的需求，配置的产品: {configured_products}")
            
            while True:
                url = f"{self.base_url}/my-story-assignedTo-id_desc-{total}-{limit}-{page}.json"
                self.logger.info(f"获取需求列表第 {page} 页: {url}")
                
                response = self.session.get(url, timeout=self.timeout)
                response.encoding = 'utf-8'
                
                if response.status_code != 200:
                    self.logger.error(f"获取需求列表失败: HTTP {response.status_code}")
                    break
                
                try:
                    result = response.json()
                    if result.get('status') != 'success' or 'data' not in result:
                        self.logger.warning(f"API返回错误: {result}")
                        break
                    
                    data = json.loads(result['data'])
                    
                    if 'stories' not in data or not data['stories']:
                        self.logger.info(f"第 {page} 页没有更多需求")
                        break
                    
                    stories = data['stories']
                    self.logger.info(f"第 {page} 页返回 {len(stories)} 个需求")
                    
                    # 处理每个需求
                    page_matched_count = 0
                    for story in stories:
                        # 如果配置了产品过滤，检查需求是否属于配置的产品
                        if configured_products:
                            product_name = story.get('productTitle', '')
                            if product_name not in configured_products:
                                continue
                            page_matched_count += 1
                        
                        # 转换需求格式
                        story_detail = {
                            'id': story.get('id'),
                            'title': story.get('title'),
                            'status': story.get('status'),
                            'stage': story.get('stage'),
                            'assigned_to': story.get('assignedTo'),
                            'opened_by': story.get('openedBy'),
                            'opened_date': story.get('openedDate'),
                            'pri': story.get('pri'),
                            'estimate': story.get('estimate'),
                            'product': story.get('productTitle', ''),
                            'plan': story.get('planTitle', '')
                        }
                        all_stories.append(story_detail)
                    
                    self.logger.info(f"第 {page} 页匹配 {page_matched_count} 个需求（产品过滤后）")
                    
                    # 如果返回的需求数少于limit，说明没有更多数据了
                    if len(stories) < limit:
                        self.logger.info(f"返回 {len(stories)} < {limit}，没有更多数据")
                        break
                    
                    # 继续下一页
                    page += 1
                    
                    # 安全限制：最多查询10页（2000条需求）
                    if page > 10:
                        self.logger.warning("达到最大页数限制（10页），停止查询")
                        break
                        
                except Exception as e:
                    self.logger.error(f"解析响应失败: {str(e)}")
                    break
            
            self.logger.info(f"总共找到 {len(all_stories)} 个指派给我的需求")
            
            return ApiResponse.success_response({
                'stories': all_stories,
                'total': len(all_stories),
                'page': 1,
                'page_size': len(all_stories)
            })

        except requests.Timeout:
            self.logger.error("获取需求列表超时")
            return ApiResponse.error_response(
                ErrorCode.TIMEOUT,
                ErrorMessage.TIMEOUT
            )
        except Exception as e:
            self.logger.error(f"获取需求列表失败: {str(e)}")
            return ApiResponse.error_response(
                ErrorCode.API_ERROR,
                f"{ErrorMessage.API_ERROR}: {str(e)}"
            )

    def _get_my_stories_fallback(self, status: Optional[str] = None) -> ApiResponse:
        """
        获取需求列表的备用方法（使用 my-story.json）
        只返回最近的 20 个需求
        """
        try:
            url = f"{self.base_url}/my-story.json"
            
            params = {}
            if status and status != 'all':
                params['status'] = status

            self.logger.info(f"获取需求列表 (备用): {url}")
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.encoding = 'utf-8'

            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get('status') == 'success' and 'data' in result:
                        story_data = json.loads(result['data'])
                        
                        if 'stories' in story_data:
                            stories_raw = story_data['stories']
                            stories = []
                            
                            for story in stories_raw:
                                stories.append({
                                    'id': story.get('id', 0),
                                    'title': story.get('title', ''),
                                    'status': story.get('status', ''),
                                    'priority': story.get('pri', 0),
                                    'assigned_to': story.get('assignedTo', ''),
                                    'opened_by': story.get('openedBy', ''),
                                    'opened_date': story.get('openedDate', ''),
                                    'product': story.get('productTitle', ''),
                                    'plan': story.get('planTitle', ''),
                                    'stage': story.get('stage', ''),
                                    'estimate': story.get('estimate', 0)
                                })
                            
                            return ApiResponse.success_response({
                                'stories': stories,
                                'total': len(stories),
                                'page': 1,
                                'page_size': len(stories)
                            })
                        
                except json.JSONDecodeError as e:
                    self.logger.error(f"解析 JSON 失败: {str(e)}")

            return ApiResponse.error_response(
                ErrorCode.API_ERROR,
                f"HTTP {response.status_code}"
            )

        except Exception as e:
            self.logger.error(f"获取需求列表失败: {str(e)}")
            return ApiResponse.error_response(
                ErrorCode.API_ERROR,
                f"{ErrorMessage.API_ERROR}: {str(e)}"
            )

    def get_story_task_count(self, story_id: int) -> int:
        """
        获取需求关联的有效任务数量（排除已删除的任务）

        Args:
            story_id: 需求ID

        Returns:
            有效任务数量（未删除的）
        """
        try:
            url = f"{self.base_url}/story-view-{story_id}.json"
            response = self.session.get(url, timeout=self.timeout)
            response.encoding = 'utf-8'

            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get('status') == 'success' and 'data' in result:
                        story_data = json.loads(result['data'])

                        if 'story' in story_data:
                            story = story_data['story']
                            tasks = story.get('tasks', {})

                            # 调试日志：打印任务数据结构
                            self.logger.debug(f"需求 #{story_id} 任务数据类型: {type(tasks)}")
                            self.logger.debug(f"需求 #{story_id} 任务数据: {tasks}")

                            # tasks 是字典格式: {project_id: [task_list]}
                            if isinstance(tasks, dict):
                                total_tasks = 0
                                for project_id, project_tasks in tasks.items():
                                    self.logger.debug(f"项目 {project_id} 任务数: {len(project_tasks) if isinstance(project_tasks, list) else 'N/A'}")
                                    if isinstance(project_tasks, list):
                                        for task in project_tasks:
                                            self.logger.debug(f"  任务 #{task.get('id')}: deleted={task.get('deleted')}, status={task.get('status')}")
                                        # 过滤掉已删除的任务（deleted 字段为 '1' 表示已删除）
                                        valid_tasks = [
                                            task for task in project_tasks
                                            if task.get('deleted') != '1' and task.get('deleted') != 1
                                        ]
                                        total_tasks += len(valid_tasks)
                                self.logger.debug(f"需求 #{story_id} 有效任务数: {total_tasks}")
                                return total_tasks
                            elif isinstance(tasks, list):
                                self.logger.debug(f"需求 #{story_id} 任务列表长度: {len(tasks)}")
                                # 过滤掉已删除的任务
                                valid_tasks = [
                                    task for task in tasks
                                    if task.get('deleted') != '1' and task.get('deleted') != 1
                                ]
                                self.logger.debug(f"需求 #{story_id} 有效任务数: {len(valid_tasks)}")
                                return len(valid_tasks)

                except Exception as e:
                    self.logger.warning(f"解析需求 {story_id} 任务信息失败: {str(e)}")

        except Exception as e:
            self.logger.warning(f"获取需求 {story_id} 任务信息失败: {str(e)}")

        return 0

    def get_story(self, story_id: int) -> ApiResponse:
        """
        获取需求详情
        
        Args:
            story_id: 需求ID
            
        Returns:
            需求详情
        """
        try:
            url = f"{self.base_url}/story-view-{story_id}.json"
            response = self.session.get(url, timeout=self.timeout)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get('status') == 'success' and 'data' in result:
                        story_data = json.loads(result['data'])
                        
                        if 'story' in story_data:
                            story = story_data['story']
                            
                            # 处理计划字段（可能是字典或字符串）
                            plan = story.get('planTitle', '')
                            if isinstance(plan, dict):
                                plan = list(plan.values())[0] if plan else ''
                            
                            # 获取关联的执行/项目ID
                            # 禅道8.x中，需求可能关联多个执行（项目）
                            execution_id = 0
                            execution_name = ''
                            executions = []
                            
                            # 方式1: 从 executions 数组获取
                            if 'executions' in story:
                                executions = story['executions']
                                if executions and isinstance(executions, list) and len(executions) > 0:
                                    # 取第一个执行（项目）
                                    first_exec = executions[0] if isinstance(executions[0], dict) else {'id': executions[0]}
                                    execution_id = first_exec.get('id', 0) if isinstance(first_exec, dict) else int(first_exec)
                                    execution_name = first_exec.get('name', '') if isinstance(first_exec, dict) else ''
                            # 方式2: 从 plan 字段获取（可能是字典）
                            elif 'plan' in story and isinstance(story['plan'], dict):
                                plan_keys = list(story['plan'].keys())
                                if plan_keys:
                                    execution_id = int(plan_keys[0])
                            # 方式3: 直接从 execution 字段获取
                            elif 'execution' in story:
                                execution_id = story['execution']
                            
                            self.logger.info(f"需求 #{story_id} 关联的执行ID: {execution_id}, 执行名称: {execution_name}")
                            
                            story_detail = {
                                'id': story.get('id', 0),
                                'title': story.get('title', ''),
                                'status': story.get('status', ''),
                                'priority': story.get('pri', 0),
                                'assigned_to': story.get('assignedTo', ''),
                                'opened_by': story.get('openedBy', ''),
                                'opened_date': story.get('openedDate', ''),
                                'product': story.get('productTitle', ''),
                                'product_id': story.get('product', 0),
                                'plan': plan,
                                'stage': story.get('stage', ''),
                                'estimate': story.get('estimate', 0),
                                'execution': execution_id,
                                'execution_name': execution_name,
                                'executions': executions
                            }
                            
                            return ApiResponse.success_response(story_detail)
                        else:
                            # 没有story字段，可能是HTML页面
                            self.logger.error(f"需求 #{story_id} 返回数据中没有story字段")
                            return ApiResponse.error_response(
                                ErrorCode.STORY_NOT_FOUND,
                                f"需求 #{story_id} 不存在或无法访问"
                            )
                            
                except Exception as e:
                    self.logger.warning(f"解析需求 {story_id} 详情失败: {str(e)}")
                    return ApiResponse.error_response(
                        ErrorCode.API_ERROR,
                        f"解析需求详情失败: {str(e)}"
                    )
            else:
                self.logger.error(f"获取需求详情失败: HTTP {response.status_code}")
                return ApiResponse.error_response(
                    ErrorCode.API_ERROR,
                    f"获取需求详情失败: HTTP {response.status_code}"
                )
                
        except Exception as e:
            self.logger.error(f"获取需求详情异常: {str(e)}")
            return ApiResponse.error_response(
                ErrorCode.API_ERROR,
                f"获取需求详情失败: {str(e)}"
            )

    def update_story_title(self, story_id: int, new_title: str) -> ApiResponse:
        """
        更新需求标题 (适配 8.x 版本)
        使用 story-change API 进行变更
        
        Args:
            story_id: 需求ID
            new_title: 新的需求标题
            
        Returns:
            更新结果
        """
        try:
            # 首先获取需求的当前信息
            story_result = self.get_story(story_id)
            if not story_result.success:
                return ApiResponse.error_response(
                    ErrorCode.STORY_NOT_FOUND,
                    f"需求 #{story_id} 不存在或无法访问"
                )
            
            story_data = story_result.data
            
            # 禅道 8.x 使用 story-change API 进行变更
            # 变更需求标题需要调用 /story-change-{story_id}.json
            url = f"{self.base_url}/story-change-{story_id}.json"
            
            # 准备表单数据
            form_data = {
                'title': new_title,
                'product': story_data.get('product_id', 0),
                'module': 0,
                'plan': 0,
                'source': story_data.get('source', ''),
                'pri': story_data.get('priority', 3),
                'estimate': story_data.get('estimate', 0),
                'stage': story_data.get('stage', 'wait'),
                'assignedTo': story_data.get('assigned_to', ''),
                'comment': '通过 ZenTao Helper 自动更新需求标题',
            }
            
            self.logger.info(f"变更需求 #{story_id} 标题为: {new_title}")
            
            # 发送 POST 请求
            response = self.session.post(url, data=form_data, timeout=self.timeout)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get('status') == 'success' or result.get('result') == 'success':
                        self.logger.info(f"需求 #{story_id} 标题变更成功")
                        return ApiResponse.success_response({
                            'story_id': story_id,
                            'new_title': new_title,
                            'message': '需求标题变更成功'
                        })
                    else:
                        error_msg = result.get('message', result.get('reason', '变更失败'))
                        self.logger.error(f"需求标题变更失败: {error_msg}")
                        return ApiResponse.error_response(
                            ErrorCode.API_ERROR,
                            f"需求标题变更失败: {error_msg}"
                        )
                except ValueError:
                    # 如果不是 JSON 响应，检查页面内容
                    if 'error' in response.text.lower() or '错误' in response.text:
                        self.logger.error("需求标题变更失败: 页面返回错误")
                        return ApiResponse.error_response(
                            ErrorCode.API_ERROR,
                            "需求标题变更失败，请检查权限或需求状态"
                        )
                    else:
                        self.logger.info(f"需求 #{story_id} 标题可能已变更成功")
                        return ApiResponse.success_response({
                            'story_id': story_id,
                            'new_title': new_title,
                            'message': '需求标题可能已变更成功，请检查需求详情'
                        })
            else:
                self.logger.error(f"变更需求标题失败: HTTP {response.status_code}")
                return ApiResponse.error_response(
                    ErrorCode.API_ERROR,
                    f"变更需求标题失败: HTTP {response.status_code}"
                )
                
        except requests.Timeout:
            self.logger.error("更新需求标题超时")
            return ApiResponse.error_response(
                ErrorCode.TIMEOUT,
                ErrorMessage.TIMEOUT
            )
        except Exception as e:
            self.logger.error(f"更新需求标题异常: {str(e)}")
            return ApiResponse.error_response(
                ErrorCode.API_ERROR,
                f"更新需求标题失败: {str(e)}"
            )

    def review_story(self, story_id: int, result: str = 'pass', assigned_to: str = None, 
                     estimate: float = None, comment: str = '') -> ApiResponse:
        """
        评审需求 (适配 8.x 版本)
        用于在变更需求后，将需求状态从"已变更"改回"已激活"
        
        Args:
            story_id: 需求ID
            result: 评审结果 ('pass' 通过, 'revert' 撤销变更, 'clarify' 有待明确)
            assigned_to: 指派给（用户名）
            estimate: 预计工时
            comment: 评审备注
            
        Returns:
            评审结果
        """
        try:
            # 首先获取需求的当前信息
            story_result = self.get_story(story_id)
            if not story_result.success:
                return ApiResponse.error_response(
                    ErrorCode.STORY_NOT_FOUND,
                    f"需求 #{story_id} 不存在或无法访问"
                )
            
            story_data = story_result.data
            
            # 如果需求状态不是 changed（已变更），则不需要评审
            if story_data.get('status') != 'changed':
                self.logger.info(f"需求 #{story_id} 状态为 {story_data.get('status')}，无需评审")
                return ApiResponse.success_response({
                    'story_id': story_id,
                    'status': story_data.get('status'),
                    'message': '需求状态不是已变更，无需评审'
                })
            
            # 禅道 8.x 使用 story-review API 进行评审
            url = f"{self.base_url}/story-review-{story_id}.json"
            
            # 准备表单数据
            form_data = {
                'result': result,
                'assignedTo': assigned_to if assigned_to else story_data.get('assigned_to', ''),
                'estimate': estimate if estimate else story_data.get('estimate', 0),
                'reviewedDate': '',  # 空字符串表示今天
                'comment': comment if comment else '需求已评审，准备开发',
            }
            
            self.logger.info(f"评审需求 #{story_id}，结果: {result}")
            
            # 发送 POST 请求
            response = self.session.post(url, data=form_data, timeout=self.timeout)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                # 检查响应（禅道通常会返回重定向脚本）
                if 'parent.location' in response.text or 'story-view' in response.text:
                    self.logger.info(f"需求 #{story_id} 评审成功")
                    return ApiResponse.success_response({
                        'story_id': story_id,
                        'result': result,
                        'message': '需求评审成功'
                    })
                else:
                    try:
                        result_data = response.json()
                        if result_data.get('status') == 'success' or result_data.get('result') == 'success':
                            self.logger.info(f"需求 #{story_id} 评审成功")
                            return ApiResponse.success_response({
                                'story_id': story_id,
                                'result': result,
                                'message': '需求评审成功'
                            })
                        else:
                            error_msg = result_data.get('message', result_data.get('reason', '评审失败'))
                            self.logger.error(f"需求评审失败: {error_msg}")
                            return ApiResponse.error_response(
                                ErrorCode.API_ERROR,
                                f"需求评审失败: {error_msg}"
                            )
                    except ValueError:
                        self.logger.info(f"需求 #{story_id} 可能已评审成功")
                        return ApiResponse.success_response({
                            'story_id': story_id,
                            'result': result,
                            'message': '需求可能已评审成功'
                        })
            else:
                self.logger.error(f"评审需求失败: HTTP {response.status_code}")
                return ApiResponse.error_response(
                    ErrorCode.API_ERROR,
                    f"评审需求失败: HTTP {response.status_code}"
                )
                
        except requests.Timeout:
            self.logger.error("评审需求超时")
            return ApiResponse.error_response(
                ErrorCode.TIMEOUT,
                ErrorMessage.TIMEOUT
            )
        except Exception as e:
            self.logger.error(f"评审需求异常: {str(e)}")
            return ApiResponse.error_response(
                ErrorCode.API_ERROR,
                f"评审需求失败: {str(e)}"
            )

    def _get_story_detail_minimal(self, story_id: int) -> Optional[Dict]:
        """
        获取需求的最小化详情（用于批量查询）
        
        Args:
            story_id: 需求ID
            
        Returns:
            需求详情字典，包含基本信息
        """
        try:
            url = f"{self.base_url}/story-view-{story_id}.json"
            response = self.session.get(url, timeout=self.timeout)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get('status') == 'success' and 'data' in result:
                        story_data = json.loads(result['data'])
                        
                        if 'story' in story_data:
                            story = story_data['story']
                            
                            # 处理计划字段（可能是字典或字符串）
                            plan = story.get('planTitle', '')
                            if isinstance(plan, dict):
                                plan = list(plan.values())[0] if plan else ''
                            
                            return {
                                'id': story.get('id', 0),
                                'title': story.get('title', ''),
                                'status': story.get('status', ''),
                                'priority': story.get('pri', 0),
                                'assigned_to': story.get('assignedTo', ''),
                                'opened_by': story.get('openedBy', ''),
                                'opened_date': story.get('openedDate', ''),
                                'product': story.get('productTitle', ''),
                                'plan': plan,
                                'stage': story.get('stage', ''),
                                'estimate': story.get('estimate', 0)
                            }
                            
                except Exception as e:
                    self.logger.warning(f"解析需求 {story_id} 详情失败: {str(e)}")
                    
        except Exception as e:
            self.logger.warning(f"获取需求 {story_id} 详情失败: {str(e)}")
        
        return None

    def create_task(self, execution_id: int, name: str, assigned_to: str = None,
                    estimate: float = 0, deadline: str = None, parent_id: int = None, story_id: int = None) -> ApiResponse:
        """
        创建任务 (适配 8.x 版本)
        
        Args:
            execution_id: 执行ID/项目ID（必须提供）
            name: 任务名称
            assigned_to: 指派给（用户名）
            estimate: 预计工时
            deadline: 截止日期 (格式: YYYY-MM-DD)
            parent_id: 父任务ID（用于创建子任务）
            story_id: 需求ID（用于从需求创建任务）
            
        Returns:
            创建结果
        """
        try:
            # 禅道 8.x 使用表单提交创建任务
            url = f"{self.base_url}/task-create-{execution_id}-0.html"
            
            # 准备表单数据
            form_data = {
                'name': name,
                'type': 'devel' if not parent_id else 'devel',  # 任务类型
                'pri': 3,  # 优先级 (1-4)
                'estimate': estimate if estimate else '',
                'assignedTo[]': assigned_to if assigned_to else '',  # 注意：禅道8.x使用数组格式
                'module': 0,  # 模块ID
                'estStarted': '',  # 预计开始时间
                'desc': '',
                'mailto[]': '',  # 抄送给
                'after': 'toTaskList',  # 创建后跳转到任务列表
            }
            
            # 如果有父任务，添加 parent 字段
            if parent_id:
                form_data['parent'] = parent_id
            
            # 如果有关联的需求，添加 story 字段
            if story_id:
                form_data['story'] = story_id
            
            # 如果有截止日期
            if deadline:
                form_data['deadline'] = deadline
            
            self.logger.info(f"创建任务: {name} (execution: {execution_id}, story: {story_id})")
            
            # 发送 POST 请求
            response = self.session.post(url, data=form_data, timeout=self.timeout)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                # 检查是否创建成功（通常重定向到任务列表或任务详情）
                # 禅道创建成功后通常会跳转到 project-task-{execution_id}.html
                if 'project-task' in response.url or 'task-view' in response.url:
                    # 尝试从 URL 中提取新创建的任务ID
                    task_id_match = re.search(r'task-view-(\d+)\.html', response.url)
                    if task_id_match:
                        task_id = int(task_id_match.group(1))
                        self.logger.info(f"任务创建成功: #{task_id}")
                        return ApiResponse.success_response({
                            'id': task_id,
                            'name': name,
                            'url': f"{self.base_url}/task-view-{task_id}.html"
                        })
                    else:
                        # 创建成功但无法获取任务ID
                        self.logger.info("任务创建成功")
                        return ApiResponse.success_response({
                            'name': name,
                            'message': '任务创建成功'
                        })
                else:
                    # 检查页面内容是否包含错误信息
                    if 'error' in response.text.lower() or '错误' in response.text:
                        self.logger.error("任务创建失败: 页面返回错误")
                        return ApiResponse.error_response(
                            ErrorCode.API_ERROR,
                            "任务创建失败，请检查参数"
                        )
                    else:
                        # 可能是创建成功，但无法确定
                        return ApiResponse.success_response({
                            'name': name,
                            'message': '任务可能已创建成功，请检查任务列表'
                        })
            else:
                self.logger.error(f"创建任务失败: HTTP {response.status_code}")
                return ApiResponse.error_response(
                    ErrorCode.API_ERROR,
                    f"创建任务失败: HTTP {response.status_code}"
                )
                
        except requests.Timeout:
            self.logger.error("创建任务超时")
            return ApiResponse.error_response(
                ErrorCode.TIMEOUT,
                ErrorMessage.TIMEOUT
            )
        except Exception as e:
            self.logger.error(f"创建任务异常: {str(e)}")
            return ApiResponse.error_response(
                ErrorCode.API_ERROR,
                f"{ErrorMessage.API_ERROR}: {str(e)}"
            )

    def split_task(self, parent_task_id: int, subtask_names: List[str]) -> ApiResponse:
        """
        任务拆解 (适配 8.x 版本)
        将父任务拆解为多个子任务
        
        Args:
            parent_task_id: 父任务ID
            subtask_names: 子任务名称列表
            
        Returns:
            拆解结果
        """
        try:
            # 首先获取父任务信息，获取 execution_id
            parent_task_result = self._get_task_detail_full(parent_task_id)
            if not parent_task_result:
                return ApiResponse.error_response(
                    ErrorCode.TASK_NOT_FOUND,
                    f"未找到父任务 #{parent_task_id}"
                )
            
            execution_id = parent_task_result.get('project')
            if not execution_id:
                return ApiResponse.error_response(
                    ErrorCode.API_ERROR,
                    "无法获取父任务的项目信息"
                )
            
            self.logger.info(f"开始拆解任务 #{parent_task_id} 到 {len(subtask_names)} 个子任务")
            
            created_tasks = []
            failed_tasks = []
            
            for i, name in enumerate(subtask_names, 1):
                result = self.create_task(
                    execution_id=execution_id,
                    name=name,
                    parent_id=parent_task_id
                )
                
                if result.success:
                    created_tasks.append({
                        'index': i,
                        'name': name,
                        'id': result.data.get('id')
                    })
                    self.logger.info(f"子任务 {i} 创建成功: {name}")
                else:
                    failed_tasks.append({
                        'index': i,
                        'name': name,
                        'error': result.error.message if result.error else '未知错误'
                    })
                    self.logger.error(f"子任务 {i} 创建失败: {name}")
            
            return ApiResponse.success_response({
                'parent_task_id': parent_task_id,
                'created_tasks': created_tasks,
                'failed_tasks': failed_tasks,
                'success_count': len(created_tasks),
                'fail_count': len(failed_tasks)
            })
            
        except Exception as e:
            self.logger.error(f"任务拆解异常: {str(e)}")
            return ApiResponse.error_response(
                ErrorCode.API_ERROR,
                f"任务拆解失败: {str(e)}"
            )

    def get_executions(self) -> ApiResponse:
        """
        获取执行/项目列表 (适配 8.x 版本)
        
        Returns:
            执行/项目列表
        """
        try:
            # 禅道 8.x 使用 my-project.json 获取项目列表
            url = f"{self.base_url}/my-project.json"
            response = self.session.get(url, timeout=self.timeout)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get('status') == 'success' and 'data' in result:
                        projects_data = json.loads(result['data'])
                        executions = []
                        
                        # 处理项目数据
                        if 'projects' in projects_data:
                            projects_list = projects_data['projects']
                            # 如果是列表格式
                            if isinstance(projects_list, list):
                                for project in projects_list:
                                    # 过滤掉已完成(done)和已关闭(closed)的项目
                                    status = project.get('status', '')
                                    if status in ['done', 'closed']:
                                        continue
                                    executions.append({
                                        'id': int(project.get('id', 0)),
                                        'name': project.get('name', ''),
                                        'status': status,
                                        'begin': project.get('begin', ''),
                                        'end': project.get('end', '')
                                    })
                            # 如果是字典格式（ID为键，名称为值）
                            elif isinstance(projects_list, dict):
                                for project_id, project_name in projects_list.items():
                                    executions.append({
                                        'id': int(project_id),
                                        'name': project_name,
                                        'status': '',
                                        'begin': '',
                                        'end': ''
                                    })
                        
                        self.logger.info(f"获取到 {len(executions)} 个执行/项目")
                        return ApiResponse.success_response(executions)
                    else:
                        self.logger.warning(f"获取执行列表失败: {result}")
                        return ApiResponse.error_response(
                            ErrorCode.API_ERROR,
                            "获取执行列表失败"
                        )
                except Exception as e:
                    self.logger.error(f"解析执行列表失败: {str(e)}")
                    return ApiResponse.error_response(
                        ErrorCode.API_ERROR,
                        f"解析执行列表失败: {str(e)}"
                    )
            else:
                self.logger.error(f"获取执行列表失败: HTTP {response.status_code}")
                return ApiResponse.error_response(
                    ErrorCode.API_ERROR,
                    f"获取执行列表失败: HTTP {response.status_code}"
                )
                
        except Exception as e:
            self.logger.error(f"获取执行列表异常: {str(e)}")
            return ApiResponse.error_response(
                ErrorCode.API_ERROR,
                f"获取执行列表失败: {str(e)}"
            )

    def assign_task(self, task_id: int, username: str) -> ApiResponse:
        """
        任务分配 (适配 8.x 版本)
        将任务指派给指定用户
        
        Args:
            task_id: 任务ID
            username: 用户名
            
        Returns:
            分配结果
        """
        try:
            # 首先获取任务详情，获取 execution_id
            task_detail = self._get_task_detail_full(task_id)
            if not task_detail:
                return ApiResponse.error_response(
                    ErrorCode.TASK_NOT_FOUND,
                    f"未找到任务 #{task_id}"
                )
            
            execution_id = task_detail.get('project')
            if not execution_id:
                return ApiResponse.error_response(
                    ErrorCode.API_ERROR,
                    "无法获取任务的项目信息"
                )
            
            # 禅道 8.x 使用 task-assign 页面进行分配
            url = f"{self.base_url}/task-assign-{task_id}.html"
            
            # 准备表单数据
            form_data = {
                'assignedTo': username,
                'comment': ''
            }
            
            self.logger.info(f"分配任务 #{task_id} 给 {username}")
            
            # 发送 POST 请求
            response = self.session.post(url, data=form_data, timeout=self.timeout)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                # 检查是否分配成功
                if 'execution-task' in response.url or 'task-view' in response.url:
                    self.logger.info(f"任务 #{task_id} 分配成功")
                    return ApiResponse.success_response({
                        'task_id': task_id,
                        'assigned_to': username,
                        'message': f'任务已成功分配给 {username}'
                    })
                else:
                    return ApiResponse.error_response(
                        ErrorCode.API_ERROR,
                        "任务分配可能失败，请检查任务状态"
                    )
            else:
                self.logger.error(f"分配任务失败: HTTP {response.status_code}")
                return ApiResponse.error_response(
                    ErrorCode.API_ERROR,
                    f"分配任务失败: HTTP {response.status_code}"
                )
                
        except requests.Timeout:
            self.logger.error("分配任务超时")
            return ApiResponse.error_response(
                ErrorCode.TIMEOUT,
                ErrorMessage.TIMEOUT
            )
        except Exception as e:
            self.logger.error(f"分配任务异常: {str(e)}")
            return ApiResponse.error_response(
                ErrorCode.API_ERROR,
                f"分配任务失败: {str(e)}"
            )

    def get_task(self, task_id: int) -> ApiResponse:
        """
        获取任务详情
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务详情
        """
        try:
            url = f"{self.base_url}/task-view-{task_id}.json"
            response = self.session.get(url, timeout=self.timeout)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    if result.get('status') == 'success' and 'data' in result:
                        task_data = json.loads(result['data'])
                        
                        if 'task' in task_data:
                            task = task_data['task']
                            
                            task_detail = {
                                'id': task.get('id', 0),
                                'title': task.get('name', ''),
                                'status': task.get('status', ''),
                                'priority': task.get('pri', 0),
                                'assigned_to': task.get('assignedTo', ''),
                                'opened_by': task.get('openedBy', ''),
                                'opened_date': task.get('openedDate', ''),
                                'estimate': task.get('estimate', 0),
                                'execution': task.get('execution', 0),
                                'project': task.get('project', 0),
                                'parent': task.get('parent', 0)
                            }
                            
                            return ApiResponse.success_response(task_detail)
                            
                except Exception as e:
                    self.logger.warning(f"解析任务 {task_id} 详情失败: {str(e)}")
                    return ApiResponse.error_response(
                        ErrorCode.API_ERROR,
                        f"解析任务详情失败: {str(e)}"
                    )
            else:
                self.logger.error(f"获取任务详情失败: HTTP {response.status_code}")
                return ApiResponse.error_response(
                    ErrorCode.API_ERROR,
                    f"获取任务详情失败: HTTP {response.status_code}"
                )
                
        except Exception as e:
            self.logger.error(f"获取任务详情异常: {str(e)}")
            return ApiResponse.error_response(
                ErrorCode.API_ERROR,
                f"获取任务详情失败: {str(e)}"
            )

    def _get_task_detail_full(self, task_id: int) -> Optional[Dict]:
        """
        获取任务完整详情（内部方法）
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务完整信息字典
        """
        try:
            url = f"{self.base_url}/task-view-{task_id}.json"
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                response.encoding = 'utf-8'
                try:
                    result = response.json()
                    if result.get('status') == 'success' and 'data' in result:
                        task_data = json.loads(result['data'])
                        if 'task' in task_data:
                            return task_data['task']
                except Exception as e:
                    self.logger.warning(f"解析任务 {task_id} 详情失败: {str(e)}")
        except Exception as e:
            self.logger.warning(f"获取任务 {task_id} 详情失败: {str(e)}")
        
        return None
