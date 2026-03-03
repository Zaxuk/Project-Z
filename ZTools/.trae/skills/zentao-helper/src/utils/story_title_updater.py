"""
需求标题更新器
处理需求标题的更新，包括提取标签、添加等级和上线时间
"""

import re
from datetime import datetime, timedelta
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

        格式：【需求等级】【标签1】【标签2】【标签N】YYMMDD 剩余原需求标题

        注意：如果标题已经包含等级标签，会先移除所有格式化内容再重新生成

        Args:
            original_title: 原需求标题
            grade: 需求等级
            online_time: 需求上线时间（支持相对时间描述或日期格式）

        Returns:
            更新后的需求标题
        """
        if not original_title:
            return ""

        # 1. 提取原始需求标题（去除所有格式化内容）
        base_title = self._extract_base_title(original_title)

        # 2. 提取标签（原需求标题中用【】括起来的部分，但排除等级标签）
        tags = self._extract_tags_excluding_grade(original_title, grade)

        # 3. 将上线时间转换为 YYMMDD 格式
        formatted_date = self._format_online_time(online_time)

        # 4. 构建新标题
        new_title = f"【{grade}】"

        # 添加标签
        for tag in tags:
            new_title += f"【{tag}】"

        # 添加上线时间（YYMMDD格式，不加方括号，用空格与剩余标题隔离）
        new_title += f"{formatted_date} {base_title}"

        return new_title

    def _extract_base_title(self, title: str) -> str:
        """
        提取原始需求标题

        去除所有格式化内容：等级标签、其他标签、日期

        Args:
            title: 原需求标题

        Returns:
            原始需求标题
        """
        # 1. 移除所有【】括起来的内容（包括等级标签和其他标签）
        base = re.sub(r'【[^】]*】', '', title)

        # 2. 移除日期格式（6位数字 YYMMDD）
        base = re.sub(r'\d{6}', '', base)

        # 3. 清理多余空格
        base = base.strip()

        return base

    def _extract_tags_excluding_grade(self, title: str, grade: str) -> List[str]:
        """
        提取标签，排除等级标签

        Args:
            title: 需求标题
            grade: 当前等级（需要排除）

        Returns:
            标签列表（不包含等级标签）
        """
        # 匹配所有【】括起来的内容
        pattern = r'【([^】]+)】'
        all_tags = re.findall(pattern, title)

        # 过滤掉等级标签（A-, A, A+, A++, B）
        grade_pattern = r'^[AB][+-]*$'
        tags = [tag for tag in all_tags if not re.match(grade_pattern, tag)]

        return tags

    def _format_online_time(self, online_time: str) -> str:
        """
        将上线时间转换为 YYMMDD 格式

        Args:
            online_time: 上线时间描述（如"下周周一"）或日期字符串

        Returns:
            YYMMDD 格式的日期字符串
        """
        today = datetime.now()
        weekday = today.weekday()  # 0=周一, 6=周日

        # 处理相对时间描述
        if '下下周' in online_time:
            # 下下周
            days_to_add = 14
            if '周一' in online_time:
                days_to_add += (0 - weekday) % 7
            elif '周四' in online_time:
                days_to_add += (3 - weekday) % 7
            target_date = today + timedelta(days=days_to_add)
        elif '下周' in online_time:
            # 下周
            days_to_add = 7
            if '周一' in online_time:
                days_to_add += (0 - weekday) % 7
            elif '周四' in online_time:
                days_to_add += (3 - weekday) % 7
            target_date = today + timedelta(days=days_to_add)
        elif re.match(r'^\d{4}-\d{2}-\d{2}$', online_time):
            # YYYY-MM-DD 格式
            target_date = datetime.strptime(online_time, '%Y-%m-%d')
        elif re.match(r'^\d{6}$', online_time):
            # YYMMDD 格式，直接返回
            return online_time
        elif re.match(r'^\d{8}$', online_time):
            # YYYYMMDD 格式，转换为 YYMMDD
            return online_time[2:]
        else:
            # 默认返回下周周一
            days_to_add = 7 + (0 - weekday) % 7
            target_date = today + timedelta(days=days_to_add)

        # 返回 YYMMDD 格式
        return target_date.strftime('%y%m%d')

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

        去除标签、等级和上线时间，保留原始需求标题

        Args:
            title: 原需求标题
            tags: 提取的标签列表

        Returns:
            剩余标题（原始需求标题）
        """
        # 1. 移除所有标签
        remaining = title
        for tag in tags:
            remaining = remaining.replace(f"【{tag}】", "")

        # 2. 移除可能的上线时间（格式：[2026-03-10] 或 [20260310] 等）
        remaining = re.sub(r'\[\d{4}[-/]?\d{2}[-/]?\d{2}\]', '', remaining)
        remaining = re.sub(r'\[\d{8}\]', '', remaining)

        # 3. 移除已经存在的 YYMMDD 格式日期（6位数字）
        remaining = re.sub(r'\d{6}', '', remaining)

        # 4. 清理多余空格和标点
        remaining = remaining.strip()
        # 移除开头的逗号、顿号等
        remaining = re.sub(r'^[，、,]\s*', '', remaining)

        # 5. 如果剩余标题为空，返回原标题（可能是首次处理）
        if not remaining.strip():
            # 移除所有标签后如果为空，返回原标题（去除所有【】内容）
            remaining = re.sub(r'【[^】]*】', '', title).strip()

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
