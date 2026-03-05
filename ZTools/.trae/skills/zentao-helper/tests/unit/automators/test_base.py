# -*- coding: utf-8 -*-
"""
测试自动化操作器基类
"""

import pytest
from unittest.mock import Mock, patch

from src.automators.base import BaseAutomator
from src.utils.response import ApiResponse


class TestAutomator(BaseAutomator):
    """测试用的自动化操作器"""

    def execute(self, **kwargs) -> ApiResponse:
        """执行操作"""
        return ApiResponse.success_response({'result': 'success'})


class TestBaseAutomator:
    """测试自动化操作器基类"""

    @pytest.fixture
    def mock_api_client(self):
        """创建 Mock API 客户端"""
        return Mock()

    @pytest.fixture
    def automator(self, mock_api_client):
        """创建自动化操作器实例"""
        return TestAutomator(mock_api_client)

    def test_init(self, automator, mock_api_client):
        """测试初始化"""
        # Assert
        assert automator.api_client is mock_api_client
        assert automator.logger is not None

    def test_execute_abstract_method(self, automator):
        """测试执行抽象方法"""
        # Act
        result = automator.execute()

        # Assert
        assert result.success is True
        assert result.data['result'] == 'success'

    def test_confirm_action(self, automator):
        """测试确认操作"""
        # Act
        result = automator._confirm_action("确认执行操作？")

        # Assert
        assert result is True

    def test_confirm_action_with_different_messages(self, automator):
        """测试不同消息的确认操作"""
        # Act & Assert
        assert automator._confirm_action("消息1") is True
        assert automator._confirm_action("消息2") is True
        assert automator._confirm_action("") is True
