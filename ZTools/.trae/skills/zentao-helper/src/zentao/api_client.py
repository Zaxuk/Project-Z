"""
禅道 API 客户端
实现统一的 API 调用接口，含重试/熔断机制（Manifesto 要求）
"""

import requests
import time
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
        实现指数退避重试策略（Manifesto 要求）
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

    def _get_users(self) -> Dict[str, User]:
        """
        获取用户列表（带缓存）
        Returns:
            用户ID到用户对象的映射
        """
        if self._users_cache:
            return self._users_cache

        try:
            url = f"{self.base_url}/api.php/v1/users"
            response = self.session.get(url, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success' and 'users' in data:
                    users = {}
                    for user_data in data['users']:
                        user = User.from_api(user_data)
                        users[str(user.id)] = user
                    self._users_cache = users
                    return users

        except Exception as e:
            self.logger.error(f"获取用户列表失败: {str(e)}")

        return {}

    def login(self, username: str, password: str) -> ApiResponse:
        """
        登录禅道

        Args:
            username: 用户名
            password: 密码

        Returns:
            登录结果
        """
        try:
            # 禅道登录接口
            url = f"{self.base_url}/api.php/v1/tokens"
            data = {
                'account': username,
                'password': password
            }

            response = self.session.post(url, json=data, timeout=self.timeout)

            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success' and 'token' in result:
                    # 登录成功，保存 token 和 cookies
                    self.session.headers.update({
                        'Token': result['token']
                    })

                    # 获取用户信息
                    user_info = self._get_current_user()
                    if user_info:
                        return ApiResponse.success_response({
                            'token': result['token'],
                            'cookies': dict(self.session.cookies),
                            'user_info': user_info
                        })

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
        except Exception as e:
            self.logger.error(f"登录失败: {str(e)}")
            return ApiResponse.error_response(
                ErrorCode.API_ERROR,
                f"{ErrorMessage.API_ERROR}: {str(e)}"
            )

    def _get_current_user(self) -> Optional[Dict]:
        """获取当前用户信息"""
        try:
            url = f"{self.base_url}/api.php/v1/user"
            response = self.session.get(url, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success' and 'user' in data:
                    return data['user']
        except Exception as e:
            self.logger.error(f"获取用户信息失败: {str(e)}")

        return None

    def get_my_tasks(self, status: Optional[str] = None) -> ApiResponse:
        """
        获取指派给我的任务

        Args:
            status: 任务状态过滤，可选值：all, wait, doing, done, closed

        Returns:
            任务列表
        """
        try:
            # 获取当前用户
            user_info = self._get_current_user()
            if not user_info:
                return ApiResponse.error_response(
                    ErrorCode.SESSION_EXPIRED,
                    ErrorMessage.SESSION_EXPIRED
                )

            my_account = user_info.get('account')

            # 构建查询参数
            params = {
                'assignedTo': my_account,
                'page': 1,
                'limit': 100
            }

            if status and status != 'all':
                params['status'] = status

            url = f"{self.base_url}/api.php/v1/tasks"
            response = self.session.get(url, params=params, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success' and 'tasks' in data:
                    users = self._get_users()
                    tasks = [Task.from_api(task, users) for task in data['tasks']]

                    result = TaskListResult(
                        tasks=tasks,
                        total=data.get('total', len(tasks)),
                        page=params['page'],
                        page_size=params['limit']
                    )

                    return ApiResponse.success_response(result.to_dict())

            return ApiResponse.error_response(
                ErrorCode.API_ERROR,
                ErrorMessage.API_ERROR
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

    def get_my_stories(self, status: Optional[str] = None) -> ApiResponse:
        """
        获取指派给我的需求

        Args:
            status: 需求状态过滤，可选值：all, draft, active, closed

        Returns:
            需求列表
        """
        try:
            # 获取当前用户
            user_info = self._get_current_user()
            if not user_info:
                return ApiResponse.error_response(
                    ErrorCode.SESSION_EXPIRED,
                    ErrorMessage.SESSION_EXPIRED
                )

            my_account = user_info.get('account')

            # 构建查询参数
            params = {
                'assignedTo': my_account,
                'page': 1,
                'limit': 100
            }

            if status and status != 'all':
                params['status'] = status

            url = f"{self.base_url}/api.php/v1/stories"
            response = self.session.get(url, params=params, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success' and 'stories' in data:
                    users = self._get_users()
                    stories = [Story.from_api(story, users) for story in data['stories']]

                    result = StoryListResult(
                        stories=stories,
                        total=data.get('total', len(stories)),
                        page=params['page'],
                        page_size=params['limit']
                    )

                    return ApiResponse.success_response(result.to_dict())

            return ApiResponse.error_response(
                ErrorCode.API_ERROR,
                ErrorMessage.API_ERROR
            )

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

    def get_task(self, task_id: int) -> ApiResponse:
        """
        获取单个任务详情

        Args:
            task_id: 任务ID

        Returns:
            任务详情
        """
        try:
            url = f"{self.base_url}/api.php/v1/tasks/{task_id}"
            response = self.session.get(url, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success' and 'task' in data:
                    users = self._get_users()
                    task = Task.from_api(data['task'], users)
                    return ApiResponse.success_response(task.to_dict())

            return ApiResponse.error_response(
                ErrorCode.TASK_NOT_FOUND,
                ErrorMessage.TASK_NOT_FOUND
            )

        except requests.Timeout:
            self.logger.error(f"获取任务详情超时: {task_id}")
            return ApiResponse.error_response(
                ErrorCode.TIMEOUT,
                ErrorMessage.TIMEOUT
            )
        except Exception as e:
            self.logger.error(f"获取任务详情失败: {task_id}, {str(e)}")
            return ApiResponse.error_response(
                ErrorCode.API_ERROR,
                f"{ErrorMessage.API_ERROR}: {str(e)}"
            )

    def create_task(self, parent_id: Optional[int] = None, name: str = None,
                    assigned_to: str = None, **kwargs) -> ApiResponse:
        """
        创建任务（用于任务拆解）

        Args:
            parent_id: 父任务ID
            name: 任务名称
            assigned_to: 指派人
            **kwargs: 其他任务属性

        Returns:
            创建结果
        """
        try:
            url = f"{self.base_url}/api.php/v1/tasks"
            data = {
                'name': name,
                'assignedTo': assigned_to
            }

            if parent_id:
                data['parent'] = parent_id

            data.update(kwargs)

            response = self.session.post(url, json=data, timeout=self.timeout)

            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success' and 'task' in result:
                    return ApiResponse.success_response(result['task'])

            return ApiResponse.error_response(
                ErrorCode.API_ERROR,
                ErrorMessage.API_ERROR
            )

        except Exception as e:
            self.logger.error(f"创建任务失败: {str(e)}")
            return ApiResponse.error_response(
                ErrorCode.API_ERROR,
                f"{ErrorMessage.API_ERROR}: {str(e)}"
            )

    def assign_task(self, task_id: int, assigned_to: str) -> ApiResponse:
        """
        分配任务

        Args:
            task_id: 任务ID
            assigned_to: 指派人账号

        Returns:
            分配结果
        """
        try:
            url = f"{self.base_url}/api.php/v1/tasks/{task_id}"
            data = {
                'assignedTo': assigned_to
            }

            response = self.session.put(url, json=data, timeout=self.timeout)

            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    return ApiResponse.success_response(result)

            return ApiResponse.error_response(
                ErrorCode.API_ERROR,
                ErrorMessage.API_ERROR
            )

        except Exception as e:
            self.logger.error(f"分配任务失败: {task_id}, {str(e)}")
            return ApiResponse.error_response(
                ErrorCode.API_ERROR,
                f"{ErrorMessage.API_ERROR}: {str(e)}"
            )

    def search_user(self, keyword: str) -> ApiResponse:
        """
        搜索用户

        Args:
            keyword: 搜索关键词（用户名或真实姓名）

        Returns:
            用户列表
        """
        try:
            url = f"{self.base_url}/api.php/v1/users"
            params = {
                'search': keyword,
                'limit': 10
            }

            response = self.session.get(url, params=params, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success' and 'users' in data:
                    users = [User.from_api(u).to_dict() for u in data['users']]
                    return ApiResponse.success_response(users)

            return ApiResponse.success_response([])

        except Exception as e:
            self.logger.error(f"搜索用户失败: {keyword}, {str(e)}")
            return ApiResponse.error_response(
                ErrorCode.API_ERROR,
                f"{ErrorMessage.API_ERROR}: {str(e)}"
            )