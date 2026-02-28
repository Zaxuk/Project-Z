"""
ZenTao Helper Skill 主入口
iFlow Skill 规范实现
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
    符合 iFlow Skill 规范
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

    def execute(self, user_input: str) -> dict:
        """
        Skill 主入口方法
        解析并执行自然语言指令

        Args:
            user_input: 用户输入的自然语言指令

        Returns:
            执行结果字典（符合 iFlow 规范）
        """
        try:
            self.logger.info(f"接收到用户指令: {user_input}")

            # 解析命令
            command = self.command_parser.parse(user_input)
            intent = command['intent']
            entities = command['entities']

            self.logger.info(f"解析结果 - 意图: {intent}, 实体: {entities}")

            # 处理帮助意图
            if intent == 'help':
                return self._handle_help()

            # 确保会话有效
            if not self._ensure_session():
                return ApiResponse.error_response(
                    ErrorCode.SESSION_EXPIRED,
                    ErrorMessage.SESSION_EXPIRED
                ).to_dict()

            # 根据意图执行对应操作
            if intent == 'query_stories':
                result = self._handle_query_stories(entities)
            elif intent == 'query_tasks':
                result = self._handle_query_tasks(entities)
            elif intent == 'split_task':
                result = self._handle_split_task(entities, user_input)
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

        Returns:
            会话是否有效
        """
        if self.session_manager.is_session_valid():
            # 加载会话到 API 客户端
            session_data = self.session_manager.load_session()
            if session_data:
                cookies = session_data.get('cookies', {})
                token = session_data.get('token')
                if token:
                    self.api_client.session.headers.update({'Token': token})
                self.api_client.set_cookies(cookies)
                return True

        # 会话无效，尝试交互式登录
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
        """处理查询需求意图"""
        status = entities.get('status')
        result = self.story_collector.collect(status=status)

        if result.success:
            # 格式化显示
            display_text = self.story_collector.format_display(result.data)
            return ApiResponse.success_response({
                'message': display_text,
                'data': result.data,
                'type': 'stories'
            })

        return result

    def _handle_query_tasks(self, entities: dict) -> ApiResponse:
        """处理查询任务意图"""
        status = entities.get('status')
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

    def _handle_split_task(self, entities: dict, user_input: str) -> ApiResponse:
        """处理任务拆解意图"""
        task_id = entities.get('task_id')
        subtask_names = entities.get('subtask_names')

        result = self.task_splitter.execute(
            parent_task_id=task_id,
            subtask_names=subtask_names,
            user_input=user_input
        )

        if result.success:
            # 格式化显示
            display_text = self.task_splitter.format_display(result.data)
            return ApiResponse.success_response({
                'message': display_text,
                'data': result.data,
                'type': 'task_split'
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
    import sys

    # 检查是否有命令行参数
    if len(sys.argv) > 1:
        # 从命令行参数获取指令
        user_input = ' '.join(sys.argv[1:])
        skill = ZenTaoHelperSkill()
        result = skill.execute(user_input)

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
