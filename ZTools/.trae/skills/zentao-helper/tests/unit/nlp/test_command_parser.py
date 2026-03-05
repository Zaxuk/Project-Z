# -*- coding: utf-8 -*-
"""
测试命令解析器
"""

import pytest
from unittest.mock import Mock, patch

from src.nlp.command_parser import CommandParser


class TestCommandParser:
    """测试命令解析器"""

    @pytest.fixture
    def parser(self):
        """创建解析器实例"""
        with patch('src.nlp.command_parser.get_logger') as mock_logger:
            mock_logger.return_value = Mock()
            return CommandParser()

    class TestParse:
        """测试解析方法"""

        def test_parse_view_stories(self, parser):
            """测试解析查看需求指令"""
            # Arrange
            with patch.object(parser.intent_classifier, 'classify', return_value='view_stories'), \
                 patch.object(parser.entity_extractor, 'extract_all', return_value={}):
                
                # Act
                result = parser.parse("查看我的需求")

                # Assert
                assert result['intent'] == 'view_stories'
                assert result['raw'] == "查看我的需求"
                assert result['confidence'] == 0.9

        def test_parse_view_tasks(self, parser):
            """测试解析查看任务指令"""
            # Arrange
            with patch.object(parser.intent_classifier, 'classify', return_value='view_tasks'), \
                 patch.object(parser.entity_extractor, 'extract_all', return_value={}):
                
                # Act
                result = parser.parse("查看我的任务")

                # Assert
                assert result['intent'] == 'view_tasks'
                assert result['raw'] == "查看我的任务"

        def test_parse_split_story(self, parser):
            """测试解析拆解需求指令"""
            # Arrange
            entities = {'story_id': '123'}
            with patch.object(parser.intent_classifier, 'classify', return_value='split_story'), \
                 patch.object(parser.entity_extractor, 'extract_all', return_value=entities):
                
                # Act
                result = parser.parse("拆解需求#123")

                # Assert
                assert result['intent'] == 'split_story'
                assert result['entities']['story_id'] == '123'

        def test_parse_assign_task(self, parser):
            """测试解析分配任务指令"""
            # Arrange
            entities = {'task_id': '456', 'username': '张三'}
            with patch.object(parser.intent_classifier, 'classify', return_value='assign_task'), \
                 patch.object(parser.entity_extractor, 'extract_all', return_value=entities):
                
                # Act
                result = parser.parse("把任务#456分配给张三")

                # Assert
                assert result['intent'] == 'assign_task'
                assert result['entities']['task_id'] == '456'
                assert result['entities']['username'] == '张三'

        def test_parse_help(self, parser):
            """测试解析帮助指令"""
            # Arrange
            with patch.object(parser.intent_classifier, 'classify', return_value='help'), \
                 patch.object(parser.entity_extractor, 'extract_all', return_value={}):
                
                # Act
                result = parser.parse("帮助")

                # Assert
                assert result['intent'] == 'help'

        def test_parse_with_empty_text(self, parser):
            """测试解析空文本"""
            # Arrange
            with patch.object(parser.intent_classifier, 'classify', return_value='unknown'), \
                 patch.object(parser.entity_extractor, 'extract_all', return_value={}):
                
                # Act
                result = parser.parse("")

                # Assert
                assert result['intent'] == 'unknown'
                assert result['raw'] == ""

        def test_parse_with_entities(self, parser):
            """测试解析包含多个实体的指令"""
            # Arrange
            entities = {
                'story_id': '123',
                'task_id': '456',
                'username': '李四',
                'execution_id': '10'
            }
            with patch.object(parser.intent_classifier, 'classify', return_value='unknown'), \
                 patch.object(parser.entity_extractor, 'extract_all', return_value=entities):
                
                # Act
                result = parser.parse("需求#123 任务#456 给李四 项目#10")

                # Assert
                assert result['entities'] == entities

    class TestGetHelp:
        """测试获取帮助信息"""

        def test_get_help_returns_string(self, parser):
            """测试帮助信息返回字符串"""
            # Act
            result = parser.get_help()

            # Assert
            assert isinstance(result, str)
            assert len(result) > 0

        def test_get_help_contains_usage(self, parser):
            """测试帮助信息包含使用说明"""
            # Act
            result = parser.get_help()

            # Assert
            assert "ZenTao Helper" in result
            assert "支持的指令" in result

        def test_get_help_contains_examples(self, parser):
            """测试帮助信息包含示例"""
            # Act
            result = parser.get_help()

            # Assert
            assert "查看需求" in result
            assert "查看任务" in result
            assert "拆解需求" in result
            assert "任务分配" in result
