"""
需求标题更新器
处理需求标题的更新，包括提取标签、添加等级和上线时间
"""

import re
from typing import Optional, List, Tuple


class StoryTitleUpdater:
    """
    需求标题更新器
    处理需求标题的格式化和更新
    """

    def __init__(self):
        pass

    def update_title(self, original_title: str, grade: str, online_time: str) -> str:
        """
        更新需求标题

        格式：【[需求等级]【标签1】【标签2】【标签N】[需求上线时间]剩余原需求标题

        Args:
            original_title: 原需求标题
            grade: 需求等级
            online_time: 需求上线时间

        Returns:
            更新后的需求标题
        """
        if not original_title:
            return ""

        # 1. 提取标签（原需求标题中用【】括起来的部分）
        tags = self._extract_tags(original_title)

        # 2. 提取剩余标题（去除标签和可能的上线时间）
        remaining_title = self._extract_remaining_title(original_title, tags)

        # 3. 构建新标题
        new_title = f"【{grade}】"

        # 添加标签
        for tag in tags:
            new_title += f"【{tag}】"

        # 添加上线时间
        new_title += f"[{online_time}]"

        # 添加剩余标题
        new_title += remaining_title

        return new_title

    def _extract_tags(self, title: str) -> List[str]:
        """
        从标题中提取标签

        标签格式：【标签内容】

        Args:
            title: 需求标题

        Returns:
            标签列表
        """
        # 匹配所有【】括起来的内容
        pattern = r'【([^】]+)】'
        matches = re.findall(pattern, title)
        return matches

    def _extract_remaining_title(self, title: str, tags: List[str]) -> str:
        """
        提取剩余标题

        去除标签和可能的上线时间

        Args:
            title: 原需求标题
            tags: 提取的标签列表

        Returns:
            剩余标题
        """
        # 1. 移除所有标签
        remaining = title
        for tag in tags:
            remaining = remaining.replace(f"【{tag}】", "")

        # 2. 移除可能的上线时间（格式：[2026-03-10] 或 [20260310] 等）
        remaining = re.sub(r'\[\d{4}[-/]?\d{2}[-/]?\d{2}\]', '', remaining)
        remaining = re.sub(r'\[\d{8}\]', '', remaining)

        # 3. 清理多余空格和标点
        remaining = remaining.strip()
        # 移除开头的逗号、顿号等
        remaining = re.sub(r'^[，、,]\s*', '', remaining)

        return remaining

    def extract_grade_from_title(self, title: str) -> Optional[str]:
        """
        从标题中提取需求等级

        格式：A-/A/A+/A++/B

        Args:
            title: 需求标题

        Returns:
            需求等级，如果未找到返回 None
        """
        # 匹配【A-】、【A】、【A+】、【A++】、【B】
        pattern = r'【([AB][+-]*)】'
        match = re.search(pattern, title)
        if match:
            return match.group(1)
        return None

    def extract_online_time_from_title(self, title: str) -> Optional[str]:
        """
        从标题中提取上线时间

        格式：[2026-03-10] 或 [20260310]

        Args:
            title: 需求标题

        Returns:
            上线时间，如果未找到返回 None
        """
        # 匹配 [2026-03-10] 或 [20260310]
        pattern = r'\[(\d{4}[-/]?\d{2}[-/]?\d{2})\]'
        match = re.search(pattern, title)
        if match:
            return match.group(1)
        return None

    def has_grade_in_title(self, title: str) -> bool:
        """
        检查标题中是否包含需求等级

        Args:
            title: 需求标题

        Returns:
            是否包含需求等级
        """
        pattern = r'【[AB][+-]*】'
        return bool(re.search(pattern, title))

    def has_online_time_in_title(self, title: str) -> bool:
        """
        检查标题中是否包含上线时间

        Args:
            title: 需求标题

        Returns:
            是否包含上线时间
        """
        pattern = r'\[\d{4}[-/]?\d{2}[-/]?\d{2}\]'
        return bool(re.search(pattern, title))
