"""
任务分配器
将任务分配给指定用户
"""

import sys
from typing import Optional

from .base import BaseAutomator
from ..utils.response import ApiResponse, ErrorCode, ErrorMessage
from ..utils.logger import get_logger


class TaskAssigner(BaseAutomator):
    """
    任务分配器
    """

    def __init__(self, api_client):
        super().__init__(api_client)
        self.logger = get_logger()

    def execute(self, task_id: str = None, username: str = None,
                user_input: str = None, **kwargs) -> ApiResponse:
        """
        执行任务分配

        Args:
            task_id: 任务ID
            username: 用户名
            user_input: 原始用户输入（用于提取用户名）
            **kwargs: 其他参数

        Returns:
            分配结果
        """
        if not task_id:
            return ApiResponse.error_response(
                ErrorCode.MISSING_PARAMETER,
                "请指定要分配的任务ID，例如：把任务#456分配给张三"
            )

        if not username:
            if user_input:
                # 尝试从用户输入中提取
                from ..nlp.entity_extractor import EntityExtractor
                extractor = EntityExtractor()
                username = extractor.extract_username(user_input)

            if not username:
                # 交互式输入
                username = self._interactive_input_username()

            if not username:
                return ApiResponse.error_response(
                    ErrorCode.MISSING_PARAMETER,
                    "请指定要分配的用户，分配已取消"
                )

        # 验证任务是否存在
        task_result = self.api_client.get_task(int(task_id))
        if not task_result.success:
            return ApiResponse.error_response(
                ErrorCode.TASK_NOT_FOUND,
                ErrorMessage.TASK_NOT_FOUND
            )

        task = task_result.data
        self.logger.info(f"开始分配任务 #{task_id}: {task.get('name', '')} 给 {username}")

        # 搜索用户（可选，用于验证用户名）
        user_search_result = self.api_client.search_user(username)
        if user_search_result.success:
            users = user_search_result.data
            if len(users) == 0:
                self.logger.warning(f"未找到用户: {username}")
            elif len(users) > 1:
                # 多个匹配，让用户选择（简化处理：使用第一个）
                username = users[0].get('account', username)
                self.logger.info(f"找到多个匹配用户，使用: {username}")
            else:
                # 精确匹配
                username = users[0].get('account', username)

        # 执行分配
        return self._perform_assign(int(task_id), username)

    def _interactive_input_username(self) -> Optional[str]:
        """
        交互式输入用户名

        Returns:
            用户名
        """
        try:
            username = input("\n请输入要分配给的用户名: ")
            return username.strip() if username.strip() else None
        except (EOFError, KeyboardInterrupt):
            print("\n输入已取消")
            return None

    def _perform_assign(self, task_id: int, username: str) -> ApiResponse:
        """
        执行实际的分配操作

        Args:
            task_id: 任务ID
            username: 用户名

        Returns:
            分配结果
        """
        self.logger.info(f"分配任务 #{task_id} 给 {username}")

        result = self.api_client.assign_task(task_id, username)

        if result.success:
            self.logger.info(f"成功分配任务 #{task_id} 给 {username}")

            # 获取更新后的任务信息
            updated_task = self.api_client.get_task(task_id)

            return ApiResponse.success_response({
                'task_id': task_id,
                'assigned_to': username,
                'task': updated_task.data if updated_task.success else None
            })
        else:
            self.logger.error(f"分配任务失败: {result.error.message}")
            return ApiResponse.error_response(
                ErrorCode.API_ERROR,
                f"分配任务失败: {result.error.message}"
            )

    def format_display(self, data: dict) -> str:
        """
        格式化显示分配结果

        Args:
            data: 分配结果数据

        Returns:
            格式化后的文本
        """
        task_id = data.get('task_id')
        assigned_to = data.get('assigned_to')
        task = data.get('task')

        lines = [f"任务分配结果\n"]
        lines.append(f"任务 #{task_id} 已成功分配给: {assigned_to}\n")

        if task:
            lines.append(f"\n任务信息:\n")
            lines.append(f"  标题: {task.get('name', '')}\n")
            lines.append(f"  状态: {task.get('status', '')}\n")
            lines.append(f"  类型: {task.get('type', '')}\n")

        return ''.join(lines)
