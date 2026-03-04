"""
ZenTao Helper Skill 主入口
Trae Skill 实现
"""

import sys
import getpass
from pathlib import Path

# 添加 src 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.utils.logger import get_logger
from src.utils.config_loader import get_config
from src.utils.response import ApiResponse, ErrorCode, ErrorMessage
from src.auth.session_manager import SessionManager
from src.zentao.api_client import ZentaoApiClient
from src.nlp.command_parser import CommandParser
from src.collectors.story_collector import StoryCollector
from src.collectors.task_collector import TaskCollector
from src.automators.task_splitter import TaskSplitter
from src.automators.task_assigner import TaskAssigner


class ZenTaoHelperSkill:
    """
    禅道自动化助手 Skill
    符合 Trae Skill 规范
    """

    def __init__(self):
        self.logger = get_logger()
        self.config = get_config()

        # 初始化各模块
        self.session_manager = SessionManager()
        self.api_client = ZentaoApiClient()
        self.command_parser = CommandParser()

        # 初始化收集器
        self.story_collector = StoryCollector(self.api_client)
        self.task_collector = TaskCollector(self.api_client)

        # 初始化自动化操作器
        self.task_splitter = TaskSplitter(self.api_client)
        self.task_assigner = TaskAssigner(self.api_client)

        self.logger.info("ZenTao Helper Skill 初始化完成")

    def execute(self, user_input: str, **kwargs) -> dict:
        """
        Skill 主入口方法
        解析并执行自然语言指令

        Args:
            user_input: 用户输入的自然语言指令
            **kwargs: 额外参数（非交互模式参数）

        Returns:
            执行结果字典（符合 Trae 规范）
        """
        try:
            self.logger.debug(f"接收到用户指令: {user_input}")

            # 解析命令
            command = self.command_parser.parse(user_input)
            intent = command['intent']
            entities = command['entities']

            self.logger.debug(f"解析结果 - 意图: {intent}, 实体: {entities}")

            # 处理帮助意图
            if intent == 'help':
                return self._handle_help().to_dict()

            # 确保会话有效
            if not self._ensure_session():
                return ApiResponse.error_response(
                    ErrorCode.SESSION_EXPIRED,
                    ErrorMessage.SESSION_EXPIRED
                ).to_dict()

            # 根据意图执行对应操作
            if intent == 'query_stories':
                result = self._handle_query_stories(entities)
            elif intent == 'query_unassigned_stories':
                result = self._handle_query_unassigned_stories(entities)
            elif intent == 'query_tasks':
                result = self._handle_query_tasks(entities)
            elif intent == 'split_task':
                result = self._handle_split_task(entities, user_input, **kwargs)
            elif intent == 'assign_task':
                result = self._handle_assign_task(entities, user_input)
            else:
                result = ApiResponse.error_response(
                    ErrorCode.UNKNOWN_INTENT,
                    ErrorMessage.UNKNOWN_INTENT
                )

            return result.to_dict()

        except Exception as e:
            self.logger.error(f"执行指令时发生异常: {str(e)}", exc_info=True)
            return ApiResponse.error_response(
                ErrorCode.API_ERROR,
                f"执行失败: {str(e)}"
            ).to_dict()

    def _ensure_session(self) -> bool:
        """
        确保会话有效，无效则提示登录
        
        流程：
        1. 检查本地会话文件是否存在且未过期
        2. 加载会话到 API 客户端
        3. 验证服务器端会话是否有效
        4. 如果服务器端会话无效，提示用户重新登录

        Returns:
            会话是否有效
        """
        # 检查本地会话是否存在
        if not self.session_manager.is_session_valid():
            self.logger.debug("本地会话不存在或已过期")
            return self._interactive_login()

        # 加载会话到 API 客户端
        session_data = self.session_manager.load_session()
        if not session_data:
            self.logger.debug("加载会话失败")
            return self._interactive_login()

        cookies = session_data.get('cookies', {})
        token = session_data.get('token')
        if token:
            self.api_client.session.headers.update({'Token': token})
        self.api_client.set_cookies(cookies)

        # 验证服务器端会话是否有效
        self.logger.debug("验证服务器端会话...")
        if self.api_client.verify_session():
            self.logger.debug("会话验证成功")
            return True

        # 服务器端会话已过期，清除本地会话并提示重新登录
        self.logger.debug("服务器端会话已过期，需要重新登录")
        self.session_manager.clear_session()
        return self._interactive_login()

    def _interactive_login(self) -> bool:
        """
        交互式登录

        Returns:
            是否登录成功
        """
        print("\n" + "="*50)
        print("需要登录禅道")
        print("="*50)

        try:
            username = input("用户名: ")
            password = getpass.getpass("密码: ")

            print("\n正在登录...")
            result = self.api_client.login(username, password)

            if result.success:
                data = result.data

                # 保存会话
                session_data = {
                    'user': username,
                    'token': data.get('token'),
                    'cookies': data.get('cookies'),
                    'user_info': data.get('user_info')
                }

                if self.session_manager.save_session(session_data):
                    print(f"\n登录成功！欢迎, {data.get('user_info', {}).get('realname', username)}")
                    return True
                else:
                    print("\n保存会话失败")
                    return False
            else:
                print(f"\n登录失败: {result.error.message}")
                return False

        except (EOFError, KeyboardInterrupt):
            print("\n登录已取消")
            return False
        except Exception as e:
            print(f"\n登录异常: {str(e)}")
            return False

    def _handle_help(self) -> ApiResponse:
        """处理帮助意图"""
        help_text = self.command_parser.get_help()
        return ApiResponse.success_response({
            'message': help_text,
            'type': 'help'
        })

    def _handle_query_stories(self, entities: dict) -> ApiResponse:
        """处理查询需求意图

        默认只查询已计划(planned)和已立项(projected)阶段的需求，
        除非用户明确指定了状态或要求查看所有需求
        支持过滤未创建任务的需求
        支持按标题关键字过滤
        """
        # 首先验证会话是否有效
        if not self.api_client.verify_session():
            self.logger.warning("会话已过期，需要重新登录")
            return ApiResponse.error_response(
                ErrorCode.AUTH_ERROR,
                "会话已过期，请使用 '登录禅道' 命令重新登录"
            )

        status = entities.get('status')
        filter_no_task = entities.get('filter_no_task', False)
        keywords = entities.get('keywords', [])
        
        # 如果没有从实体中提取到关键字，使用配置中的默认关键字
        if not keywords:
            default_keywords = self.config.get('zentao.story_query.keywords', [])
            if default_keywords:
                keywords = default_keywords
                self.logger.debug(f"使用配置中的默认关键字: {keywords}")

        # 获取所有需求
        result = self.story_collector.collect(status=status)

        if result.success:
            stories = result.data.get('stories', [])

            # 如果用户没有指定状态，默认过滤已计划和已立项的需求
            if not status:
                filtered_stories = [
                    story for story in stories
                    if story.get('stage') in ['planned', 'projected']
                ]

                self.logger.debug(f"默认过滤后: {len(filtered_stories)} 个需求 (已计划/已立项)")
            elif status == 'all':
                # 用户要求查看所有需求，不过滤
                filtered_stories = stories
                self.logger.debug(f"显示所有需求: {len(filtered_stories)} 个")
            else:
                # 用户指定了具体状态，按状态过滤
                filtered_stories = stories
            
            # 如果有关键字，按标题关键字过滤
            if keywords:
                self.logger.debug(f"按关键字 {keywords} 过滤需求...")
                keyword_filtered_stories = []

                for story in filtered_stories:
                    title = story.get('title', '')
                    # 检查标题是否包含任一关键字（不区分大小写）
                    if any(keyword.lower() in title.lower() for keyword in keywords):
                        keyword_filtered_stories.append(story)

                filtered_stories = keyword_filtered_stories
                self.logger.debug(f"关键字过滤后: {len(filtered_stories)} 个需求")

            # 如果需要过滤未创建任务的需求
            if filter_no_task:
                self.logger.debug(f"开始检查 {len(filtered_stories)} 个需求的任务创建情况...")
                stories_no_task = []

                for story in filtered_stories:
                    story_id = story.get('id', 0)
                    task_count = self.api_client.get_story_task_count(story_id)

                    if task_count == 0:
                        stories_no_task.append(story)
                        self.logger.debug(f"需求 #{story_id} 未创建任务")
                    else:
                        self.logger.debug(f"需求 #{story_id} 已创建 {task_count} 个任务")

                filtered_stories = stories_no_task
                self.logger.debug(f"过滤后: {len(filtered_stories)} 个未创建任务的需求")
            
            result_data = {
                'stories': filtered_stories,
                'total': len(filtered_stories),
                'count': len(filtered_stories)
            }
            
            # 格式化显示
            display_text = self.story_collector.format_display(result_data)
            return ApiResponse.success_response({
                'message': display_text,
                'data': result_data,
                'type': 'stories'
            })

        return result

    def _handle_query_unassigned_stories(self, entities: dict) -> ApiResponse:
        """处理查询未分配需求意图

        查询所有未创建任务的需求，复用 _handle_query_stories 逻辑
        """
        # 强制设置 filter_no_task=True，复用查询需求的逻辑
        entities['filter_no_task'] = True
        # 未分配需求查询所有阶段，不进行阶段过滤
        entities['status'] = 'all'
        return self._handle_query_stories(entities)

    def _handle_query_tasks(self, entities: dict) -> ApiResponse:
        """处理查询任务意图
        
        默认只查询等待和进行中的任务，除非用户明确指定了状态或要求查看所有任务
        """
        status = entities.get('status')
        
        # 如果用户没有指定状态，默认查询等待和进行中的任务
        if not status:
            # 先查询等待中的任务
            wait_result = self.task_collector.collect(status='wait')
            # 再查询进行中的任务
            doing_result = self.task_collector.collect(status='doing')
            
            # 合并结果
            if wait_result.success and doing_result.success:
                wait_tasks = wait_result.data.get('tasks', [])
                doing_tasks = doing_result.data.get('tasks', [])
                all_tasks = wait_tasks + doing_tasks
                
                result_data = {
                    'tasks': all_tasks,
                    'total': len(all_tasks),
                    'count': len(all_tasks)
                }
                
                # 格式化显示
                display_text = self.task_collector.format_display(result_data)
                return ApiResponse.success_response({
                    'message': display_text,
                    'data': result_data,
                    'type': 'tasks'
                })
            elif wait_result.success:
                return wait_result
            elif doing_result.success:
                return doing_result
            else:
                return wait_result
        else:
            # 用户指定了状态，按指定状态查询
            result = self.task_collector.collect(status=status)

            if result.success:
                # 格式化显示
                display_text = self.task_collector.format_display(result.data)
                return ApiResponse.success_response({
                    'message': display_text,
                    'data': result.data,
                    'type': 'tasks'
                })

            return result

    def _handle_split_task(self, entities: dict, user_input: str, **kwargs) -> ApiResponse:
        """处理从需求创建任务意图"""
        story_id = entities.get('story_id')

        if not story_id:
            return ApiResponse.error_response(
                ErrorCode.MISSING_PARAMETER,
                "请指定需求ID，例如：拆解需求#123"
            )

        # 从需求创建任务（支持非交互模式参数）
        result = self.task_splitter.execute(
            story_id=story_id,
            user_input=user_input,
            **kwargs
        )

        if result.success:
            # 格式化显示
            display_text = self.task_splitter.format_display(result.data)
            return ApiResponse.success_response({
                'message': display_text,
                'data': result.data,
                'type': 'task_create'
            })

        return result

    def _handle_assign_task(self, entities: dict, user_input: str) -> ApiResponse:
        """处理任务分配意图"""
        task_id = entities.get('task_id')
        username = entities.get('username')

        result = self.task_assigner.execute(
            task_id=task_id,
            username=username,
            user_input=user_input
        )

        if result.success:
            # 格式化显示
            display_text = self.task_assigner.format_display(result.data)
            return ApiResponse.success_response({
                'message': display_text,
                'data': result.data,
                'type': 'task_assign'
            })

        return result


# iFlow Skill 入口点
def skill_main(user_input: str) -> dict:
    """
    iFlow Skill 入口点函数

    Args:
        user_input: 用户输入

    Returns:
        执行结果字典
    """
    skill = ZenTaoHelperSkill()
    return skill.execute(user_input)


# 命令行测试入口
if __name__ == "__main__":
    import argparse

    # 创建参数解析器
    parser = argparse.ArgumentParser(description='ZenTao Helper Skill')
    parser.add_argument('command', nargs='*', help='用户指令')
    parser.add_argument('--grade', '-g', choices=['A-', 'A', 'A+', 'A++', 'B'], help='需求等级')
    parser.add_argument('--priority', '-p', choices=['非紧急', '紧急'], help='需求优先级')
    parser.add_argument('--online-time', '-o', help='需求上线时间（如：下周周一、下下周周四、260331）')
    parser.add_argument('--assigned-to', '-a', help='任务执行人')
    parser.add_argument('--hours', type=float, help='任务时长（小时）')
    parser.add_argument('--deadline', '-d', help='任务截至时间（如：本周周五、下周周五）')

    args = parser.parse_args()

    # 检查是否有命令行参数
    if args.command:
        # 从命令行参数获取指令
        user_input = ' '.join(args.command)
        skill = ZenTaoHelperSkill()
        
        # 构建额外参数
        kwargs = {}
        if args.grade:
            kwargs['grade'] = args.grade
        if args.priority:
            kwargs['priority'] = args.priority
        if args.online_time:
            kwargs['online_time'] = args.online_time
        if args.assigned_to:
            kwargs['assigned_to'] = args.assigned_to
        if args.hours:
            kwargs['task_hours'] = args.hours
        if args.deadline:
            kwargs['deadline'] = args.deadline

        result = skill.execute(user_input, **kwargs)

        if result.get('success'):
            print(result.get('data', {}).get('message', '操作成功'))
        else:
            error = result.get('error', {})
            print(f"错误: {error.get('message', '未知错误')}")
    else:
        # 交互式模式
        print("ZenTao Helper Skill - 测试模式")
        print("输入 'exit' 退出\n")

        skill = ZenTaoHelperSkill()

        while True:
            try:
                user_input = input("> ")
                if user_input.lower() in ['exit', '退出', 'quit']:
                    break

                result = skill.execute(user_input)

                if result.get('success'):
                    print(result.get('data', {}).get('message', '操作成功'))
                else:
                    error = result.get('error', {})
                    print(f"错误: {error.get('message', '未知错误')}")

            except KeyboardInterrupt:
                print("\n退出")
                break
            except Exception as e:
                print(f"异常: {str(e)}")
