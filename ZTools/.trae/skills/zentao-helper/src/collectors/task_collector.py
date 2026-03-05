"""
任务收集器
收集指派给我的任务信息
"""

from typing import Optional

from .base import BaseCollector
from ..utils.response import ApiResponse, ErrorCode, ErrorMessage
from ..utils.progress_bar import ProgressBar


class TaskCollector(BaseCollector):
    """
    任务收集器
    """

    # 状态映射表
    STATUS_MAP = {
        'wait': '⏳ 等待',
        'doing': '🔨 进行中',
        'done': '✅ 已完成',
        'pause': '⏸️ 暂停',
        'closed': '❌ 已关闭',
        'cancel': '🚫 已取消',
        'unknown': '❓ 未知'
    }

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

        try:
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

        except Exception as e:
            raise

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
            return "暂无任务"

        lines = [f"📋 任务列表 (共 {total} 个)\n"]
        lines.append("=" * 80 + "\n")

        for i, task in enumerate(tasks, 1):
            task_id = task.get('id', 0)
            title = task.get('title', '')
            project_name = task.get('project_name', '')
            task_name = task.get('name', title)
            created_at = task.get('created_at', '')
            deadline = task.get('deadline', '')
            url = task.get('url', '')
            status = task.get('status', 'unknown')

            # 获取状态的中文显示
            status_display = self.STATUS_MAP.get(status, f'❓ {status}')

            lines.append(f"{i}. 任务 #{task_id} [{status_display}]\n")
            if project_name:
                lines.append(f"   项目: {project_name}\n")
            lines.append(f"   名称: {task_name}\n")
            
            # 添加时间和链接字段
            if created_at:
                lines.append(f"   创建时间: {created_at}\n")
            if deadline:
                lines.append(f"   截止时间: {deadline}\n")
            if url:
                lines.append(f"   禅道链接: {url}\n")
            
            lines.append("-" * 60 + "\n")

        return ''.join(lines)
