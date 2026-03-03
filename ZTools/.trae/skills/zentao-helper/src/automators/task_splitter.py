"""
任务拆解器（优化版）
将一个任务拆解为多个子任务，支持交互式输入需求信息
"""

import sys
from typing import Optional, List

from .base import BaseAutomator
from ..utils.response import ApiResponse, ErrorCode, ErrorMessage
from ..utils.logger import get_logger
from ..utils.interactive_input import InteractiveInput
from ..utils.story_title_updater import StoryTitleUpdater


class TaskSplitter(BaseAutomator):
    """
    任务拆解器（优化版）
    支持交互式输入需求信息，自动更新需求标题
    """

    def __init__(self, api_client):
        super().__init__(api_client)
        self.logger = get_logger()
        self.interactive_input = InteractiveInput()
        self.title_updater = StoryTitleUpdater()

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

        # 收集任务创建信息
        task_info = self.interactive_input.collect_task_info(parent_task.get('title', ''))
        if not task_info:
            return ApiResponse.error_response(
                ErrorCode.USER_CANCELLED,
                "已取消任务拆解"
            )

        # 更新需求标题
        updated_title = self.title_updater.update_title(
            parent_task.get('title', ''),
            task_info['grade'],
            task_info['online_time']
        )

        self.logger.info(f"更新需求标题为: {updated_title}")

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
        return self._perform_split(
            int(parent_task_id),
            subtask_names,
            task_info,
            updated_title
        )

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

    def _perform_split(self, parent_task_id: int, subtask_names: List[str],
                     task_info: dict, updated_title: str) -> ApiResponse:
        """
        执行实际的拆解操作

        Args:
            parent_task_id: 父任务ID
            subtask_names: 子任务名称列表
            task_info: 任务信息
            updated_title: 更新后的需求标题

        Returns:
            拆解结果
        """
        self.logger.info(f"拆解任务 #{parent_task_id} 为 {len(subtask_names)} 个子任务")

        created_tasks = []
        failed_tasks = []

        # 获取执行ID（从父任务中获取）
        parent_task_result = self.api_client.get_task(parent_task_id)
        execution_id = parent_task_result.data.get('execution', 0) if parent_task_result.success else 0

        for i, name in enumerate(subtask_names, 1):
            try:
                # 生成任务标题
                task_title = task_info['task_title'] if task_info['task_title'] else f"【任务】{name}"

                # 计算截止日期
                deadline = self._calculate_deadline(task_info['deadline'])

                result = self.api_client.create_task(
                    execution_id=execution_id,
                    name=task_title,
                    assigned_to=task_info['assigned_to'] if task_info['assigned_to'] else None,
                    estimate=task_info['task_hours'] if task_info['task_hours'] else 0,
                    deadline=deadline,
                    parent_id=parent_task_id
                )

                if result.success:
                    created_task = result.data
                    created_tasks.append({
                        'id': created_task.get('id'),
                        'name': name,
                        'title': task_title,
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
                'updated_title': updated_title,
                'task_info': task_info,
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

    def _calculate_deadline(self, deadline_text: str) -> Optional[str]:
        """
        计算截止日期

        Args:
            deadline_text: 截至时间文本（本周周五/下周周五）

        Returns:
            截至日期字符串（YYYY-MM-DD 格式）
        """
        if not deadline_text:
            return None

        from datetime import datetime, timedelta

        today = datetime.now()
        weekday = today.weekday()  # 0=周一, 6=周日

        # 计算本周周五
        days_to_friday = 4 - weekday  # 周五=4
        if days_to_friday < 0:
            days_to_friday += 7  # 已过周五，下周

        this_friday = today + timedelta(days=days_to_friday)

        # 计算下周周五
        next_friday = this_friday + timedelta(days=7)

        if '本周周五' in deadline_text:
            return this_friday.strftime('%Y-%m-%d')
        elif '下周周五' in deadline_text:
            return next_friday.strftime('%Y-%m-%d')

        return None

    def format_display(self, data: dict) -> str:
        """
        格式化显示拆解结果

        Args:
            data: 拆解结果数据

        Returns:
            格式化后的文本
        """
        parent_id = data.get('parent_task_id')
        updated_title = data.get('updated_title', '')
        task_info = data.get('task_info', {})
        created_tasks = data.get('created_tasks', [])
        failed_tasks = data.get('failed_tasks', [])
        success_count = data.get('success_count', 0)
        fail_count = data.get('fail_count', 0)

        lines = [f"任务拆解结果 (父任务: #{parent_id})\n"]
        lines.append(f"成功: {success_count} 个 | 失败: {fail_count} 个\n\n")

        if updated_title:
            lines.append(f"更新后的需求标题:\n  {updated_title[:100]}\n\n")

        if task_info:
            lines.append("任务信息:\n")
            lines.append(f"  需求等级: {task_info.get('grade', '')}\n")
            lines.append(f"  需求优先级: {task_info.get('priority', '')}\n")
            lines.append(f"  需求上线时间: {task_info.get('online_time', '')}\n")
            lines.append(f"  任务执行人: {task_info.get('assigned_to', '未设置')}\n")
            lines.append(f"  任务时长: {task_info.get('task_hours', '未设置')} 小时\n")
            lines.append(f"  任务截至时间: {task_info.get('deadline', '未设置')}\n\n")

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
