# -*- coding: utf-8 -*-
"""
测试意图分类器
"""

import pytest
from unittest.mock import Mock, patch

from src.nlp.intent_classifier import IntentClassifier


class TestIntentClassifier:
    """测试意图分类器"""

    @pytest.fixture
    def classifier(self):
        """创建分类器实例"""
        return IntentClassifier()

    class TestClassify:
        """测试意图分类"""

        def test_classify_query_tasks(self, classifier):
            """测试查询任务意图"""
            # Act
            result = classifier.classify("查看我的任务")

            # Assert
            assert result == "query_tasks"

        def test_classify_query_stories(self, classifier):
            """测试查询需求意图"""
            # Act
            result = classifier.classify("列出所有需求")

            # Assert
            assert result == "query_stories"

        def test_classify_split_task(self, classifier):
            """测试拆解任务意图"""
            # Act
            result = classifier.classify("拆解需求 #123")

            # Assert
            assert result == "split_task"

        def test_classify_assign_task(self, classifier):
            """测试分配任务意图"""
            # Act
            result = classifier.classify("分配任务 #456 给张三")

            # Assert
            assert result == "assign_task"

        def test_classify_query_unassigned(self, classifier):
            """测试查询未分配需求意图"""
            # Act
            result = classifier.classify("未分配需求")

            # Assert
            assert result == "query_unassigned_stories"

        def test_classify_help(self, classifier):
            """测试帮助意图"""
            # Act
            result = classifier.classify("帮助")

            # Assert
            assert result == "help"

        def test_classify_unknown(self, classifier):
            """测试未知意图"""
            # Act
            result = classifier.classify("随便说说")

            # Assert
            assert result == "unknown"

    class TestClassifyWithKeywords:
        """测试关键词分类"""

        def test_classify_with_split_keywords(self, classifier):
            """测试拆解关键词"""
            # Act
            result = classifier._classify_with_keywords("拆分任务")

            # Assert
            assert result == "split_task"

        def test_classify_with_assign_keywords(self, classifier):
            """测试分配关键词"""
            # Act
            result = classifier._classify_with_keywords("指派给张三")

            # Assert
            assert result == "assign_task"

        def test_classify_with_story_keywords(self, classifier):
            """测试需求关键词"""
            # Act
            result = classifier._classify_with_keywords("显示需求列表")

            # Assert
            assert result == "query_stories"

        def test_classify_with_task_keywords(self, classifier):
            """测试任务关键词"""
            # Act
            result = classifier._classify_with_keywords("我的任务")

            # Assert
            assert result == "query_tasks"

        def test_classify_with_unassigned_keywords(self, classifier):
            """测试未分配需求关键词"""
            # Act
            result = classifier._classify_with_keywords("没有任务的需求")

            # Assert
            assert result == "query_unassigned_stories"

        def test_classify_with_help_keywords(self, classifier):
            """测试帮助关键词"""
            # Act
            result = classifier._classify_with_keywords("能做什么")

            # Assert
            assert result == "help"

        def test_classify_with_unknown_input(self, classifier):
            """测试未知输入"""
            # Act
            result = classifier._classify_with_keywords("随便说说")

            # Assert
            assert result == "unknown"

    class TestGetAllIntents:
        """测试获取所有意图"""

        def test_get_all_intents(self, classifier):
            """测试获取所有意图列表"""
            # Act
            result = classifier.get_all_intents()

            # Assert
            assert isinstance(result, list)
            assert "query_tasks" in result
            assert "query_stories" in result
            assert "split_task" in result
            assert "assign_task" in result

    class TestAddIntent:
        """测试添加意图"""

        def test_add_intent(self, classifier):
            """测试动态添加意图"""
            # Act
            classifier.add_intent("new_intent", ["新关键词1", "新关键词2"])

            # Assert
            assert "new_intent" in classifier.INTENTS
            assert classifier.INTENTS["new_intent"] == ["新关键词1", "新关键词2"]

        def test_classify_new_intent(self, classifier):
            """测试新添加意图的分类"""
            # Arrange
            classifier.add_intent("test_intent", ["测试意图"])

            # Act
            result = classifier._classify_with_keywords("这是测试意图")

            # Assert
            assert result == "test_intent"

    class TestClassifyWithLLM:
        """测试 LLM 分类（预留）"""

        def test_classify_with_llm_fallback(self, classifier):
            """测试 LLM 分类回退到关键词匹配"""
            # Act
            result = classifier._classify_with_llm("拆解任务")

            # Assert
            assert result == "split_task"

    class TestDebugMode:
        """测试调试模式"""

        def test_classify_with_debug(self, classifier):
            """测试调试模式下的分类"""
            # Arrange
            classifier.debug = True

            # Act
            result = classifier._classify_with_keywords("查看任务")

            # Assert
            assert result == "query_tasks"

    class TestInit:
        """测试初始化"""

        def test_init_with_llm_enabled(self):
            """测试启用 LLM 的初始化"""
            # Arrange
            with patch('src.nlp.intent_classifier.get_config') as mock_get_config:
                mock_config = Mock()
                mock_config.get_nlp_config.return_value = {
                    'debug': False,
                    'llm': {
                        'enabled': True,
                        'provider': 'openai',
                        'api_key': 'test-key',
                        'model': 'gpt-3.5-turbo'
                    }
                }
                mock_get_config.return_value = mock_config

                # Act
                classifier = IntentClassifier()

                # Assert
                assert classifier._llm_enabled is True

        def test_init_with_llm_disabled(self):
            """测试禁用 LLM 的初始化"""
            # Arrange
            with patch('src.nlp.intent_classifier.get_config') as mock_get_config:
                mock_config = Mock()
                mock_config.get_nlp_config.return_value = {
                    'debug': False,
                    'llm': {
                        'enabled': False
                    }
                }
                mock_get_config.return_value = mock_config

                # Act
                classifier = IntentClassifier()

                # Assert
                assert classifier._llm_enabled is False

        def test_init_with_debug_enabled(self):
            """测试启用调试模式"""
            # Arrange
            with patch('src.nlp.intent_classifier.get_config') as mock_get_config:
                mock_config = Mock()
                mock_config.get_nlp_config.return_value = {
                    'debug': True,
                    'llm': {
                        'enabled': False
                    }
                }
                mock_get_config.return_value = mock_config

                # Act
                classifier = IntentClassifier()

                # Assert
                assert classifier.debug is True

    class TestInitLLMClient:
        """测试初始化 LLM 客户端"""

        def test_init_llm_client_openai(self):
            """测试初始化 OpenAI 客户端"""
            # Arrange
            with patch('src.nlp.intent_classifier.get_config') as mock_get_config:
                mock_config = Mock()
                mock_config.get_nlp_config.return_value = {
                    'debug': False,
                    'llm': {
                        'enabled': True,
                        'provider': 'openai',
                        'api_key': 'test-key',
                        'model': 'gpt-3.5-turbo'
                    }
                }
                mock_get_config.return_value = mock_config

                # Act
                classifier = IntentClassifier()

                # Assert
                assert classifier._llm_enabled is True

        def test_init_llm_client_deepseek(self):
            """测试初始化 DeepSeek 客户端"""
            # Arrange
            with patch('src.nlp.intent_classifier.get_config') as mock_get_config:
                mock_config = Mock()
                mock_config.get_nlp_config.return_value = {
                    'debug': False,
                    'llm': {
                        'enabled': True,
                        'provider': 'deepseek',
                        'api_key': 'test-key',
                        'model': 'deepseek-chat'
                    }
                }
                mock_get_config.return_value = mock_config

                # Act
                classifier = IntentClassifier()

                # Assert
                assert classifier._llm_enabled is True

        def test_init_llm_client_unsupported_provider(self):
            """测试不支持的 LLM 提供商"""
            # Arrange
            with patch('src.nlp.intent_classifier.get_config') as mock_get_config:
                mock_config = Mock()
                mock_config.get_nlp_config.return_value = {
                    'debug': False,
                    'llm': {
                        'enabled': True,
                        'provider': 'unsupported',
                        'api_key': 'test-key',
                        'model': 'test-model'
                    }
                }
                mock_get_config.return_value = mock_config

                # Act
                classifier = IntentClassifier()

                # Assert
                assert classifier._llm_enabled is True

    class TestClassifyWithLLMEnabled:
        """测试启用 LLM 时的分类"""

        def test_classify_with_llm_enabled_but_no_client(self, classifier):
            """测试 LLM 启用但没有客户端"""
            # Arrange
            classifier._llm_enabled = True
            classifier._llm_client = None

            # Act
            result = classifier.classify("查看任务")

            # Assert
            assert result == "query_tasks"
