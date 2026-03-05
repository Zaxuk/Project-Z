"""
需求收集器
收集指派给我的需求信息
"""

from typing import Optional

from .base import BaseCollector
from ..utils.response import ApiResponse, ErrorCode, ErrorMessage
from ..utils.progress_bar import ProgressBar


class StoryCollector(BaseCollector):
    """
    需求收集器
    """

    # 状态映射表
    STATUS_MAP = {
        'draft': '📝 草稿',
        'active': '🔥 激活',
        'closed': '✅ 已关闭',
        'changed': '🔄 已变更'
    }

    # 阶段映射表
    STAGE_MAP = {
        'wait': '等待',
        'planned': '已计划',
        'projected': '已立项',
        'developing': '研发中',
        'developed': '研发完毕',
        'testing': '测试中',
        'tested': '测试完毕',
        'verified': '已验收',
        'released': '已发布'
    }

    def collect(self, status: Optional[str] = None, **kwargs) -> ApiResponse:
        """
        收集需求列表

        Args:
            status: 需求状态过滤 (all, draft, active, closed, changed)
            **kwargs: 其他参数

        Returns:
            需求列表
        """
        self.logger.info(f"收集需求列表, status: {status}")

        try:
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

        except Exception as e:
            raise

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
            return "暂无需求"

        lines = [f"📖 需求列表 (共 {total} 个)\n"]
        lines.append("=" * 80 + "\n")

        for i, story in enumerate(stories, 1):
            story_id = story.get('id', 0)
            title = story.get('title', '')
            status = story.get('status', 'unknown')
            priority = story.get('priority', 0)
            assigned_to = story.get('assigned_to', '')
            opened_by = story.get('opened_by', '')
            opened_date = story.get('opened_date', '')
            product = story.get('product', '')
            plan = story.get('plan', '')
            stage = story.get('stage', '')
            estimate = story.get('estimate', 0)

            # 获取状态和阶段的中文显示
            status_display = self.STATUS_MAP.get(status, f'❓ {status}')
            stage_display = self.STAGE_MAP.get(stage, stage)

            lines.append(f"{i}. 需求 #{story_id} [{status_display}]\n")
            
            if product:
                lines.append(f"   产品: {product}\n")
            if plan:
                lines.append(f"   计划: {plan}\n")
            
            lines.append(f"   标题: {title}\n")
            
            # 优先级显示（转换为整数）
            try:
                priority_int = int(priority) if priority else 0
            except (ValueError, TypeError):
                priority_int = 0
            priority_icon = "🔴" if priority_int >= 3 else "🟡" if priority_int == 2 else "🟢" if priority_int == 1 else "⚪"
            lines.append(f"   优先级: {priority_icon} {priority_int}\n")
            
            if stage_display:
                lines.append(f"   阶段: {stage_display}\n")
            if estimate:
                lines.append(f"   预计工时: {estimate}h\n")
            if opened_date:
                lines.append(f"   创建时间: {opened_date}\n")
            if opened_by:
                lines.append(f"   创建者: {opened_by}\n")
            
            # 禅道链接
            url = f"http://zentao.diansan.com/story-view-{story_id}.html"
            lines.append(f"   禅道链接: {url}\n")
            
            lines.append("-" * 60 + "\n")

        return ''.join(lines)
