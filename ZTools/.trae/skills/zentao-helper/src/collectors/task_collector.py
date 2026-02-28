"""
任务收集器
收集指派给我的任务信息
"""

from typing import Optional

from .base import BaseCollector
from ..utils.response import ApiResponse, ErrorCode, ErrorMessage


class TaskCollector(BaseCollector):
    """
    任务收集器
    """

    def collect(self, status: Optional[str] = None, **kwargs) -> ApiResponse:
        """
        收集任务列表

        Args:
            status: 任务状态过滤 (all, wait, doing, done, closed)
            **kwargs: 其他参数

        Returns:
            任务列表
        """
        self.logger.info(f"收集任务列表, status: {status}")

        result = self.api_client.get_my_tasks(status)

        if result.success:
            tasks = result.data.get('tasks', [])
            total = result.data.get('total', 0)

            self.logger.info(f"成功收集 {len(tasks)} 个任务 (总计: {total})")

            return ApiResponse.success_response({
                'tasks': tasks,
                'total': total,
                'count': len(tasks)
            })
        else:
            self.logger.error(f"收集任务失败: {result.error.message}")
            return result

    def format_display(self, data: dict) -> str:
        """
        格式化显示任务列表

        Args:
            data: 任务数据

        Returns:
            格式化后的文本
        """
        tasks = data.get('tasks', [])
        total = data.get('total', 0)

        if not tasks:
            return f"暂无任务"

        lines = [f"任务列表 (共 {total} 个):\n"]

        # 按状态分组
        status_groups = {
            'wait': [],
            'doing': [],
            'done': [],
            'closed': [],
            'other': []
        }

        for task in tasks:
            status = task.get('status', '')
            if status in status_groups:
                status_groups[status].append(task)
            else:
                status_groups['other'].append(task)

        status_names = {
            'wait': '待办',
            'doing': '进行中',
            'done': '已完成',
            'closed': '已关闭',
            'other': '其他'
        }

        # 显示非空组
        for status, group_tasks in status_groups.items():
            if not group_tasks:
                continue

            lines.append(f"\n  [{status_names[status]}] ({len(group_tasks)} 个)\n")

            for task in group_tasks:
                line = f"    #{task['id']} - {task['title']}\n"
                line += f"      类型: {task.get('type', '')} | 优先级: {task.get('priority', 0)}\n"

                if task.get('assigned_to'):
                    line += f"      指派给: {task['assigned_to']}\n"

                if task.get('estimate'):
                    line += f"      预估: {task['estimate']}h"

                if task.get('left'):
                    line += f" | 剩余: {task['left']}h"

                lines.append(line + "\n")

        return ''.join(lines)
