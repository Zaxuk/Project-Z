# -*- coding: utf-8 -*-
"""
测试信息收集器基类
"""

import pytest
from unittest.mock import Mock, patch

from src.collectors.base import BaseCollector
from src.utils.response import ApiResponse


class TestCollector(BaseCollector):
    """测试用的收集器"""

    def collect(self, **kwargs) -> ApiResponse:
        """收集信息"""
        return ApiResponse.success_response({'items': []})


class TestBaseCollector:
    """测试信息收集器基类"""

    @pytest.fixture
    def mock_api_client(self):
        """创建 Mock API 客户端"""
        return Mock()

    @pytest.fixture
    def collector(self, mock_api_client):
        """创建收集器实例"""
        return TestCollector(mock_api_client)

    def test_init(self, collector, mock_api_client):
        """测试初始化"""
        # Assert
        assert collector.api_client is mock_api_client
        assert collector.logger is not None

    def test_collect_abstract_method(self, collector):
        """测试收集抽象方法"""
        # Act
        result = collector.collect()

        # Assert
        assert result.success is True
        assert result.data['items'] == []

    def test_format_display(self, collector):
        """测试格式化显示"""
        # Act
        result = collector._format_display("测试数据")

        # Assert
        assert result == "测试数据"

    def test_format_display_with_dict(self, collector):
        """测试格式化显示字典"""
        # Arrange
        data = {'key': 'value', 'count': 10}

        # Act
        result = collector._format_display(data)

        # Assert
        assert "key" in result
        assert "value" in result

    def test_format_display_with_list(self, collector):
        """测试格式化显示列表"""
        # Arrange
        data = [1, 2, 3, 4, 5]

        # Act
        result = collector._format_display(data)

        # Assert
        assert "1" in result
        assert "2" in result
