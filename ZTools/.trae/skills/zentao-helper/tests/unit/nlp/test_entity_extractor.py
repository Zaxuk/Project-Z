# -*- coding: utf-8 -*-
"""
测试实体提取器
"""

import pytest

from src.nlp.entity_extractor import EntityExtractor


class TestEntityExtractor:
    """测试实体提取器"""

    @pytest.fixture
    def extractor(self):
        """创建提取器实例"""
        return EntityExtractor()

    class TestExtractStoryId:
        """测试提取需求 ID"""

        def test_extract_from_hash_format(self, extractor):
            """测试从 需求#123 格式提取"""
            # Act
            result = extractor.extract_story_id("查看需求#123")

            # Assert
            assert result == "123"

        def test_extract_from_story_hash(self, extractor):
            """测试从 story#123 格式提取"""
            # Act
            result = extractor.extract_story_id("story#456")

            # Assert
            assert result == "456"

        def test_extract_from_plain_number(self, extractor):
            """测试从 需求123 格式提取"""
            # Act
            result = extractor.extract_story_id("需求 456")

            # Assert
            assert result == "456"

        def test_extract_with_number_prefix(self, extractor):
            """测试从 123号需求 格式提取"""
            # Act
            result = extractor.extract_story_id("123号需求")

            # Assert
            assert result == "123"

        def test_extract_not_found(self, extractor):
            """测试未找到 ID"""
            # Act
            result = extractor.extract_story_id("查看需求")

            # Assert
            assert result is None

    class TestExtractTaskId:
        """测试提取任务 ID"""

        def test_extract_from_hash_format(self, extractor):
            """测试从 #123 格式提取"""
            # Act
            result = extractor.extract_task_id("完成任务 #789")

            # Assert
            assert result == "789"

        def test_extract_from_task_prefix(self, extractor):
            """测试从 任务#123 格式提取"""
            # Act
            result = extractor.extract_task_id("任务#100")

            # Assert
            assert result == "100"

        def test_extract_from_task_number(self, extractor):
            """测试从 任务123 格式提取"""
            # Act
            result = extractor.extract_task_id("查看任务 200")

            # Assert
            assert result == "200"

        def test_extract_not_found(self, extractor):
            """测试未找到 ID"""
            # Act
            result = extractor.extract_task_id("完成任务")

            # Assert
            assert result is None

    class TestExtractUsername:
        """测试提取用户名"""

        def test_extract_from_assign_format(self, extractor):
            """测试从分配语句提取"""
            # Act
            result = extractor.extract_username("分配给张三")

            # Assert
            assert result is not None

        def test_extract_from_to_format(self, extractor):
            """测试从 给 格式提取"""
            # Act
            result = extractor.extract_username("给李四")

            # Assert
            assert result is not None

        def test_extract_not_found(self, extractor):
            """测试未找到用户名"""
            # Act
            result = extractor.extract_username("分配任务")

            # Assert
            assert result is None

    class TestExtractSubtaskNames:
        """测试提取子任务名称"""

        def test_extract_from_comma_separated(self, extractor):
            """测试从逗号分隔提取"""
            # Act
            result = extractor.extract_subtask_names("拆成开发,测试,部署")

            # Assert
            assert result is not None
            assert len(result) == 3

        def test_extract_from_dunhao_separated(self, extractor):
            """测试从顿号分隔提取"""
            # Act
            result = extractor.extract_subtask_names("拆分为前端开发、后端开发、测试")

            # Assert
            assert result is not None
            assert len(result) == 3

        def test_extract_not_found(self, extractor):
            """测试未找到子任务"""
            # Act
            result = extractor.extract_subtask_names("完成")

            # Assert
            assert result is None

    class TestExtractStatus:
        """测试提取状态"""

        def test_extract_wait(self, extractor):
            """测试提取未开始"""
            # Act
            result = extractor.extract_status("未开始")

            # Assert
            assert result is not None

        def test_extract_doing(self, extractor):
            """测试提取进行中"""
            # Act
            result = extractor.extract_status("进行中")

            # Assert
            assert result is not None

        def test_extract_done(self, extractor):
            """测试提取已完成"""
            # Act
            result = extractor.extract_status("已完成")

            # Assert
            assert result is not None

    class TestExtractAll:
        """测试提取所有实体"""

        def test_extract_all_entities(self, extractor):
            """测试提取所有实体"""
            # Act
            result = extractor.extract_all("拆解需求 #123 分配给张三")

            # Assert
            assert isinstance(result, dict)
            assert "story_id" in result or "task_id" in result

        def test_extract_all_empty(self, extractor):
            """测试空文本"""
            # Act
            result = extractor.extract_all("")

            # Assert
            assert isinstance(result, dict)
            assert result['task_id'] is None

    class TestExtractFilterNoTask:
        """测试提取未创建任务过滤条件"""

        def test_extract_filter_no_task_true(self, extractor):
            """测试提取到过滤条件"""
            # Act
            result = extractor.extract_filter_no_task("显示未创建任务的需求")

            # Assert
            assert result is True

        def test_extract_filter_no_task_false(self, extractor):
            """测试未提取到过滤条件"""
            # Act
            result = extractor.extract_filter_no_task("显示所有需求")

            # Assert
            assert result is False

        def test_extract_filter_no_task_variations(self, extractor):
            """测试不同变体"""
            variations = [
                "没有任务的需求",
                "没建任务的需求",
                "未建任务",
                "无任务",
                "未分配",
                "未分配任务"
            ]
            for text in variations:
                assert extractor.extract_filter_no_task(text) is True

    class TestExtractKeywords:
        """测试提取关键字"""

        def test_extract_keywords_with_quotes(self, extractor):
            """测试带引号的关键字"""
            # Act
            result = extractor.extract_keywords('包含"面板"的需求')

            # Assert
            assert result is not None
            assert "面板" in result

        def test_extract_keywords_contain(self, extractor):
            """测试包含关键字"""
            # Act
            result = extractor.extract_keywords("包含订单的需求")

            # Assert
            assert result is not None
            # 关键字可能包含"订单"或"订单的需求"
            assert any("订单" in k for k in result)

        def test_extract_keywords_keyword_is(self, extractor):
            """测试关键字是格式"""
            # Act
            result = extractor.extract_keywords("关键字是首页面板")

            # Assert
            assert result is not None
            assert "首页面板" in result

        def test_extract_keywords_about(self, extractor):
            """测试关于格式"""
            # Act
            result = extractor.extract_keywords("关于面板的查询")

            # Assert
            assert result is not None
            assert "面板" in result

        def test_extract_keywords_related(self, extractor):
            """测试相关格式"""
            # Act
            result = extractor.extract_keywords("面板相关的需求")

            # Assert
            assert result is not None
            assert "面板" in result

        def test_extract_keywords_title_contain(self, extractor):
            """测试标题包含格式"""
            # Act
            result = extractor.extract_keywords("标题包含订单的需求")

            # Assert
            assert result is not None
            assert "订单" in result

        def test_extract_keywords_not_found(self, extractor):
            """测试未找到关键字"""
            # Act
            result = extractor.extract_keywords("显示所有需求")

            # Assert
            assert result is None

    class TestDebugMode:
        """测试调试模式"""

        def test_extract_task_with_debug(self, extractor):
            """测试调试模式下的任务ID提取"""
            # Arrange
            extractor.debug = True

            # Act
            result = extractor.extract_task_id("任务#123")

            # Assert
            assert result == "123"

        def test_extract_story_with_debug(self, extractor):
            """测试调试模式下的需求ID提取"""
            # Arrange
            extractor.debug = True

            # Act
            result = extractor.extract_story_id("需求#456")

            # Assert
            assert result == "456"

    class TestExtractUsername:
        """测试提取用户名"""

        def test_extract_from_assign_to(self, extractor):
            """测试从分配给提取"""
            # Act
            result = extractor.extract_username("分配给张三")

            # Assert
            assert result is not None

        def test_extract_from_to(self, extractor):
            """测试从给提取"""
            # Act
            result = extractor.extract_username("给李四")

            # Assert
            assert result is not None

        def test_extract_not_found(self, extractor):
            """测试未找到用户名"""
            # Act
            result = extractor.extract_username("完成任务")

            # Assert
            assert result is None

    class TestExtractTaskId:
        """测试提取任务 ID"""

        def test_extract_from_hash_format(self, extractor):
            """测试从 #123 格式提取"""
            # Act
            result = extractor.extract_task_id("查看#123")

            # Assert
            assert result == "123"

        def test_extract_from_task_format(self, extractor):
            """测试从任务#123 格式提取"""
            # Act
            result = extractor.extract_task_id("任务#456")

            # Assert
            assert result == "456"

        def test_extract_not_found(self, extractor):
            """测试未找到任务ID"""
            # Act
            result = extractor.extract_task_id("查看需求")

            # Assert
            assert result is None
