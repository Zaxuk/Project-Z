# -*- coding: utf-8 -*-
"""
测试需求标题更新器
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.utils.story_title_updater import StoryTitleUpdater


class TestStoryTitleUpdater:
    """测试需求标题更新器"""

    @pytest.fixture
    def updater(self):
        """创建更新器实例"""
        return StoryTitleUpdater()

    class TestUpdateTitle:
        """测试更新标题"""

        def test_update_title_basic(self, updater):
            """测试基本标题更新"""
            # Act
            result = updater.update_title(
                original_title="测试需求",
                grade="A",
                online_time="下周周一"
            )

            # Assert
            assert result.startswith("【A】")
            assert "测试需求" in result

        def test_update_title_with_priority(self, updater):
            """测试带优先级的标题更新"""
            # Act
            result = updater.update_title(
                original_title="测试需求",
                grade="A+",
                online_time="下周周一",
                priority="紧急"
            )

            # Assert
            assert "【A+】" in result
            assert "【紧急】" in result
            assert "测试需求" in result

        def test_update_title_remove_urgent_priority(self, updater):
            """测试移除紧急优先级标签"""
            # Act
            result = updater.update_title(
                original_title="【紧急】测试需求",
                grade="A",
                online_time="下周周一",
                priority="普通"
            )

            # Assert
            assert "【A】" in result
            assert "【紧急】" not in result
            assert "测试需求" in result

        def test_update_title_empty(self, updater):
            """测试空标题"""
            # Act
            result = updater.update_title(
                original_title="",
                grade="A",
                online_time="下周周一"
            )

            # Assert
            assert result == ""

        def test_update_title_with_existing_tags(self, updater):
            """测试保留已有标签"""
            # Arrange
            original = "【特1】旧需求"

            # Act
            result = updater.update_title(
                original_title=original,
                grade="A",
                online_time="下周周一"
            )

            # Assert
            assert "【A】" in result
            assert "【特1】" in result

    class TestExtractBaseTitle:
        """测试提取基础标题"""

        def test_extract_base_title_with_tags(self, updater):
            """测试从带标签标题中提取"""
            # Act
            result = updater._extract_base_title("【A】【特1】240315 测试需求")

            # Assert
            assert result == "测试需求"

        def test_extract_base_title_without_tags(self, updater):
            """测试无标签标题"""
            # Act
            result = updater._extract_base_title("测试需求")

            # Assert
            assert result == "测试需求"

        def test_extract_base_title_empty(self, updater):
            """测试空标题"""
            # Act
            result = updater._extract_base_title("")

            # Assert
            assert result == ""

    class TestExtractValidTags:
        """测试提取有效标签"""

        def test_extract_valid_tags_with_tags(self, updater):
            """测试提取有效标签"""
            # Act
            result = updater._extract_valid_tags("【特1】【特2】240315 测试需求")

            # Assert
            assert "特1" in result
            assert "特2" in result

    class TestExtractTags:
        """测试提取标签"""

        def test_extract_tags_with_multiple(self, updater):
            """测试提取多个标签"""
            # Act
            result = updater._extract_tags("【A】【特1】【特2】测试需求")

            # Assert
            assert "A" in result
            assert "特1" in result
            assert "特2" in result

        def test_extract_tags_no_tags(self, updater):
            """测试无标签"""
            # Act
            result = updater._extract_tags("测试需求")

            # Assert
            assert len(result) == 0

    class TestExtractRemainingTitle:
        """测试提取剩余标题"""

        def test_extract_remaining_with_tags(self, updater):
            """测试从带标签标题提取"""
            # Act
            result = updater._extract_remaining_title("【A】【特1】240315 测试需求", ["A", "特1"])

            # Assert
            assert "测试需求" in result

        def test_extract_remaining_with_date_brackets(self, updater):
            """测试带日期括号的标题"""
            # Act
            result = updater._extract_remaining_title("【A】[2024-03-15] 测试需求", ["A"])

            # Assert
            assert "测试需求" in result

        def test_extract_remaining_empty_after_removal(self, updater):
            """测试移除后为空的情况"""
            # Act
            result = updater._extract_remaining_title("【A】【特1】", ["A", "特1"])

            # Assert
            assert result == ""  # 或者返回原标题

    class TestExtractGradeFromTitle:
        """测试从标题提取等级"""

        def test_extract_grade_a_plus(self, updater):
            """测试提取 A+ 等级"""
            # Act
            result = updater.extract_grade_from_title("【A+】测试需求")

            # Assert
            assert result == "A+"

        def test_extract_grade_b(self, updater):
            """测试提取 B 等级"""
            # Act
            result = updater.extract_grade_from_title("【B】测试需求")

            # Assert
            assert result == "B"

        def test_extract_grade_not_found(self, updater):
            """测试未找到等级"""
            # Act
            result = updater.extract_grade_from_title("【特1】测试需求")

            # Assert
            assert result is None

    class TestExtractOnlineTimeFromTitle:
        """测试从标题提取上线时间"""

        def test_extract_online_time_with_dashes(self, updater):
            """测试带横线的日期格式"""
            # Act
            result = updater.extract_online_time_from_title("【A】[2024-03-15] 测试需求")

            # Assert
            assert result == "2024-03-15"

        def test_extract_online_time_without_dashes(self, updater):
            """测试无横线的日期格式"""
            # Act
            result = updater.extract_online_time_from_title("【A】[20240315] 测试需求")

            # Assert
            assert result == "20240315"

        def test_extract_online_time_not_found(self, updater):
            """测试未找到上线时间"""
            # Act
            result = updater.extract_online_time_from_title("【A】测试需求")

            # Assert
            assert result is None

    class TestHasGradeInTitle:
        """测试检查标题是否包含等级"""

        def test_has_grade_true(self, updater):
            """测试包含等级"""
            # Act
            result = updater.has_grade_in_title("【A+】测试需求")

            # Assert
            assert result is True

        def test_has_grade_false(self, updater):
            """测试不包含等级"""
            # Act
            result = updater.has_grade_in_title("【特1】测试需求")

            # Assert
            assert result is False

        def test_extract_valid_tags_no_tags(self, updater):
            """测试无标签"""
            # Act
            result = updater._extract_valid_tags("测试需求")

            # Assert
            assert len(result) == 0

        def test_extract_valid_tags_exclude_grade(self, updater):
            """测试排除等级标签"""
            # Act
            result = updater._extract_valid_tags("【A+】【特1】测试需求")

            # Assert
            assert "A+" not in result
            assert "特1" in result

    class TestFormatOnlineTime:
        """测试格式化上线时间"""

        def test_format_online_time_next_week_monday(self, updater):
            """测试下周周一"""
            # Act
            result = updater._format_online_time("下周周一")

            # Assert
            assert len(result) == 6  # YYMMDD 格式
            assert result.isdigit()

        def test_format_online_time_date_format(self, updater):
            """测试日期格式"""
            # Act
            result = updater._format_online_time("2024-03-15")

            # Assert
            assert result == "240315"

        def test_format_online_time_yymmdd_format(self, updater):
            """测试 YYMMDD 格式"""
            # Act
            result = updater._format_online_time("240315")

            # Assert
            assert result == "240315"

        def test_format_online_time_yyyymmdd_format(self, updater):
            """测试 YYYYMMDD 格式"""
            # Act
            result = updater._format_online_time("20240315")

            # Assert
            assert result == "240315"

        def test_format_online_time_default(self, updater):
            """测试默认格式"""
            # Act
            result = updater._format_online_time("其他时间")

            # Assert
            assert len(result) == 6
            assert result.isdigit()

    class TestExtractTagsExcludingGrade:
        """测试提取标签（排除等级）"""

        def test_extract_tags_excluding_grade(self, updater):
            """测试排除等级标签"""
            # Act
            result = updater._extract_tags_excluding_grade("【A】【特1】【特2】测试", "A")

            # Assert
            assert "A" not in result
            assert "特1" in result
            assert "特2" in result

        def test_extract_tags_no_grade(self, updater):
            """测试无等级标签"""
            # Act
            result = updater._extract_tags_excluding_grade("【特1】【特2】测试", "A")

            # Assert
            assert "特1" in result
            assert "特2" in result

    class TestFormatOnlineTimeExtended:
        """测试格式化上线时间 - 扩展"""

        def test_format_online_time_tomorrow(self, updater):
            """测试明天"""
            # Act
            result = updater._format_online_time("明天")

            # Assert
            assert len(result) == 6
            assert result.isdigit()

        def test_format_online_time_this_week(self, updater):
            """测试本周"""
            # Act
            result = updater._format_online_time("本周五")

            # Assert
            assert len(result) == 6
            assert result.isdigit()

        def test_format_online_time_next_week(self, updater):
            """测试下周"""
            # Act
            result = updater._format_online_time("下周周一")

            # Assert
            assert len(result) == 6
            assert result.isdigit()

        def test_format_online_time_next_next_week(self, updater):
            """测试下下周"""
            # Act
            result = updater._format_online_time("下下周一")

            # Assert
            assert len(result) == 6
            assert result.isdigit()

        def test_format_online_time_next_week_thursday(self, updater):
            """测试下周四"""
            # Act
            result = updater._format_online_time("下周四")

            # Assert
            assert len(result) == 6
            assert result.isdigit()

        def test_format_online_time_next_next_week_thursday(self, updater):
            """测试下下周四"""
            # Act
            result = updater._format_online_time("下下周四")

            # Assert
            assert len(result) == 6
            assert result.isdigit()

    class TestExtractBaseTitleExtended:
        """测试提取基础标题 - 扩展"""

        def test_extract_base_title_with_date(self, updater):
            """测试带日期的标题"""
            # Act
            result = updater._extract_base_title("【A】240315 测试需求")

            # Assert
            assert result == "测试需求"

        def test_extract_base_title_with_multiple_tags(self, updater):
            """测试带多个标签的标题"""
            # Act
            result = updater._extract_base_title("【A】【特1】【特2】240315 测试需求")

            # Assert
            assert result == "测试需求"

    class TestExtractValidTagsExtended:
        """测试提取有效标签 - 扩展"""

        def test_extract_valid_tags_with_long_tag(self, updater):
            """测试带过长的标签"""
            # Act
            result = updater._extract_valid_tags("【这是一个很长的标签】测试需求")

            # Assert
            assert "这是一个很长的标签" not in result

        def test_extract_valid_tags_with_punctuation(self, updater):
            """测试带标点符号的标签"""
            # Act
            result = updater._extract_valid_tags("【标签，带标点】测试需求")

            # Assert
            assert "标签，带标点" not in result

        def test_extract_valid_tags_with_question(self, updater):
            """测试带问号的标签"""
            # Act
            result = updater._extract_valid_tags("【标签?】测试需求")

            # Assert
            assert "标签?" not in result

    class TestHasOnlineTimeInTitle:
        """测试检查标题是否包含上线时间"""

        def test_has_online_time_with_brackets(self, updater):
            """测试带方括号的上线时间"""
            # Act
            result = updater.has_online_time_in_title("【A】[2024-03-15] 测试需求")

            # Assert
            assert result is True

        def test_has_online_time_with_slashes(self, updater):
            """测试带斜杠的上线时间"""
            # Act
            result = updater.has_online_time_in_title("【A】[2024/03/15] 测试需求")

            # Assert
            assert result is True

        def test_has_online_time_without_separators(self, updater):
            """测试无分隔符的上线时间"""
            # Act
            result = updater.has_online_time_in_title("【A】[20240315] 测试需求")

            # Assert
            assert result is True

        def test_has_online_time_not_found(self, updater):
            """测试未找到上线时间"""
            # Act
            result = updater.has_online_time_in_title("【A】测试需求")

            # Assert
            assert result is False
