"""
任务拆解器
将一个任务拆解为多个子任务
"""

import sys
from typing import Optional, List

from .base import BaseAutomator
from ..utils.response import ApiResponse, ErrorCode, ErrorMessage
from ..utils.logger import get_logger


class TaskSplitter(BaseAutomator):
    """
    任务拆解器
    支持从自然语言中提取子任务名称或交互式输入
    """

    def __init__(self, api_client):
        super().__init__(api_client)
        self.logger = get_logger()

    def execute(self, parent_task_id: str = None, subtask_names: List[str] = None,
                user_input: str = None, **kwargs) -> ApiResponse:
        """
        执行任务拆解

        Args:
            parent_task_id: 父任务ID
            subtask_names: 子任务名称列表
            user_input: 原始用户输入（用于提取子任务名称）
            **kwargs: 其他参数

        Returns:
            拆解结果
        """
        if not parent_task_id:
            return ApiResponse.error_response(
                ErrorCode.MISSING_PARAMETER,
                "请指定要拆解的任务ID，例如：拆解任务#123"
            )

        # 验证父任务是否存在
        task_result = self.api_client.get_task(int(parent_task_id))
        if not task_result.success:
            return ApiResponse.error_response(
                ErrorCode.TASK_NOT_FOUND,
                ErrorMessage.TASK_NOT_FOUND
            )

        parent_task = task_result.data
        self.logger.info(f"开始拆解任务 #{parent_task_id}: {parent_task.get('title', '')}")

        # 获取子任务名称
        if not subtask_names:
            if user_input:
                # 尝试从用户输入中提取
                from ..nlp.entity_extractor import EntityExtractor
                extractor = EntityExtractor()
                subtask_names = extractor.extract_subtask_names(user_input)

            if not subtask_names:
                # 交互式输入
                subtask_names = self._interactive_input_subtasks()

            if not subtask_names:
                return ApiResponse.error_response(
                    ErrorCode.MISSING_PARAMETER,
                    "未提供子任务名称，拆解已取消"
                )

        # 执行拆解
        return self._perform_split(int(parent_task_id), subtask_names)

    def _interactive_input_subtasks(self) -> List[str]:
        """
        交互式输入子任务名称

        Returns:
            子任务名称列表
        """
        print(f"\n请输入子任务名称（每行一个，空行结束）：")

        subtasks = []
        while True:
            try:
                line = input("> ")
                if not line.strip():
                    break
                subtasks.append(line.strip())
            except (EOFError, KeyboardInterrupt):
                print("\n输入已取消")
                return []

        return subtasks

    def _perform_split(self, parent_task_id: int, subtask_names: List[str]) -> ApiResponse:
        """
        执行实际的拆解操作

        Args:
            parent_task_id: 父任务ID
            subtask_names: 子任务名称列表

        Returns:
            拆解结果
        """
        self.logger.info(f"拆解任务 #{parent_task_id} 为 {len(subtask_names)} 个子任务")

        created_tasks = []
        failed_tasks = []

        # 获取当前用户信息，用于指派
        user_info = self.api_client._get_current_user()
        assigned_to = user_info.get('account') if user_info else None

        for i, name in enumerate(subtask_names, 1):
            try:
                result = self.api_client.create_task(
                    parent_id=parent_task_id,
                    name=name,
                    assigned_to=assigned_to
                )

                if result.success:
                    created_task = result.data
                    created_tasks.append({
                        'id': created_task.get('id'),
                        'name': name,
                        'index': i
                    })
                    self.logger.info(f"成功创建子任务 #{created_task.get('id')}: {name}")
                else:
                    failed_tasks.append({
                        'name': name,
                        'index': i,
                        'error': result.error.message if result.error else '未知错误'
                    })
                    self.logger.error(f"创建子任务失败: {name}")

            except Exception as e:
                failed_tasks.append({
                    'name': name,
                    'index': i,
                    'error': str(e)
                })
                self.logger.error(f"创建子任务异常: {name}, {str(e)}")

        # 返回结果
        success_count = len(created_tasks)
        fail_count = len(failed_tasks)

        if success_count > 0:
            message = f"成功拆解任务 #{parent_task_id}，创建了 {success_count} 个子任务"
            if fail_count > 0:
                message += f"，失败 {fail_count} 个"

            return ApiResponse.success_response({
                'parent_task_id': parent_task_id,
                'created_tasks': created_tasks,
                'failed_tasks': failed_tasks,
                'success_count': success_count,
                'fail_count': fail_count
            })
        else:
            return ApiResponse.error_response(
                ErrorCode.API_ERROR,
                f"拆解失败，所有子任务创建失败"
            )

    def format_display(self, data: dict) -> str:
        """
        格式化显示拆解结果

        Args:
            data: 拆解结果数据

        Returns:
            格式化后的文本
        """
        parent_id = data.get('parent_task_id')
        created_tasks = data.get('created_tasks', [])
        failed_tasks = data.get('failed_tasks', [])
        success_count = data.get('success_count', 0)
        fail_count = data.get('fail_count', 0)

        lines = [f"任务拆解结果 (父任务: #{parent_id})\n"]
        lines.append(f"成功: {success_count} 个 | 失败: {fail_count} 个\n\n")

        if created_tasks:
            lines.append("成功创建的子任务:\n")
            for task in created_tasks:
                lines.append(f"  {task['index']}. #{task['id']} - {task['name']}\n")
            lines.append("\n")

        if failed_tasks:
            lines.append("创建失败的子任务:\n")
            for task in failed_tasks:
                lines.append(f"  {task['index']}. {task['name']} - {task['error']}\n")

        return ''.join(lines)
