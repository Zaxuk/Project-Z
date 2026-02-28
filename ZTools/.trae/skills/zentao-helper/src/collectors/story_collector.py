"""
需求收集器
收集指派给我的需求信息
"""

from typing import Optional

from .base import BaseCollector
from ..utils.response import ApiResponse, ErrorCode, ErrorMessage


class StoryCollector(BaseCollector):
    """
    需求收集器
    """

    def collect(self, status: Optional[str] = None, **kwargs) -> ApiResponse:
        """
        收集需求列表

        Args:
            status: 需求状态过滤 (all, draft, active, closed)
            **kwargs: 其他参数

        Returns:
            需求列表
        """
        self.logger.info(f"收集需求列表, status: {status}")

        result = self.api_client.get_my_stories(status)

        if result.success:
            stories = result.data.get('stories', [])
            total = result.data.get('total', 0)

            self.logger.info(f"成功收集 {len(stories)} 个需求 (总计: {total})")

            return ApiResponse.success_response({
                'stories': stories,
                'total': total,
                'count': len(stories)
            })
        else:
            self.logger.error(f"收集需求失败: {result.error.message}")
            return result

    def format_display(self, data: dict) -> str:
        """
        格式化显示需求列表

        Args:
            data: 需求数据

        Returns:
            格式化后的文本
        """
        stories = data.get('stories', [])
        total = data.get('total', 0)

        if not stories:
            return f"暂无需求"

        lines = [f"需求列表 (共 {total} 个):\n"]

        for story in stories:
            status_map = {
                'draft': '草稿',
                'active': '激活',
                'closed': '已关闭',
                'changed': '已变更'
            }

            status_text = status_map.get(story.get('status', ''), story.get('status', ''))

            line = f"  #{story['id']} - {story['title']}\n"
            line += f"    状态: {status_text} | 优先级: {story.get('priority', 0)}\n"

            if story.get('assigned_to'):
                line += f"    指派给: {story['assigned_to']}\n"

            if story.get('module'):
                line += f"    模块: {story['module']}\n"

            lines.append(line)

        return ''.join(lines)
