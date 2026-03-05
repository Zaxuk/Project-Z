# -*- coding: utf-8 -*-
"""
测试任务收集器
"""

import pytest
from unittest.mock import Mock

from src.collectors.task_collector import TaskCollector
from src.utils.response import ApiResponse, ErrorCode


class TestTaskCollector:
    """测试任务收集器"""

    @pytest.fixture
    def mock_api_client(self):
        """创建 Mock API 客户端"""
        return Mock()

    @pytest.fixture
    def collector(self, mock_api_client):
        """创建收集器实例"""
        return TaskCollector(mock_api_client)

    class TestCollect:
        """测试收集任务"""

        def test_collect_success(self, collector, mock_api_client):
            """测试成功收集任务"""
            # Arrange
            mock_api_client.get_my_tasks.return_value = ApiResponse.success_response({
                'tasks': [
                    {"id": 1, "name": "任务1", "status": "wait"},
                    {"id": 2, "name": "任务2", "status": "doing"}
                ],
                'total': 2
            })

            # Act
            result = collector.collect()

            # Assert
            assert result.success is True
            assert result.data['count'] == 2

        def test_collect_empty_list(self, collector, mock_api_client):
            """测试空任务列表"""
            # Arrange
            mock_api_client.get_my_tasks.return_value = ApiResponse.success_response({
                'tasks': [],
                'total': 0
            })

            # Act
            result = collector.collect()

            # Assert
            assert result.success is True
            assert result.data['count'] == 0

        def test_collect_api_error(self, collector, mock_api_client):
            """测试 API 错误"""
            # Arrange
            mock_api_client.get_my_tasks.return_value = ApiResponse.error_response(
                ErrorCode.API_ERROR,
                "获取任务列表失败"
            )

            # Act
            result = collector.collect()

            # Assert
            assert result.success is False
            assert result.error.code == ErrorCode.API_ERROR

        def test_collect_exception(self, collector, mock_api_client):
            """测试异常抛出"""
            # Arrange
            mock_api_client.get_my_tasks.side_effect = Exception("网络错误")

            # Act & Assert
            with pytest.raises(Exception) as exc_info:
                collector.collect()
            assert "网络错误" in str(exc_info.value)

        def test_collect_with_status_filter(self, collector, mock_api_client):
            """测试带状态过滤的收集"""
            # Arrange
            mock_api_client.get_my_tasks.return_value = ApiResponse.success_response({
                'tasks': [
                    {"id": 1, "name": "任务1", "status": "doing"}
                ],
                'total': 1
            })

            # Act
            result = collector.collect(status='doing')

            # Assert
            assert result.success is True
            mock_api_client.get_my_tasks.assert_called_once_with('doing')

    class TestFormatDisplay:
        """测试格式化显示"""

        def test_format_with_tasks(self, collector):
            """测试格式化有任务的情况"""
            # Arrange
            data = {
                'tasks': [
                    {"id": 1, "name": "测试任务", "status": "wait"}
                ],
                'total': 1
            }

            # Act
            result = collector.format_display(data)

            # Assert
            assert "任务列表" in result
            assert "测试任务" in result

        def test_format_empty_tasks(self, collector):
            """测试格式化空任务"""
            # Arrange
            data = {
                'tasks': [],
                'total': 0
            }

            # Act
            result = collector.format_display(data)

            # Assert
            assert "暂无任务" in result

        def test_format_with_status_mapping(self, collector):
            """测试状态映射"""
            # Arrange
            data = {
                'tasks': [
                    {"id": 1, "name": "任务1", "status": "doing"}
                ],
                'total': 1
            }

            # Act
            result = collector.format_display(data)

            # Assert
            assert "进行中" in result or "doing" in result

    class TestStatusMap:
        """测试状态映射表"""

        def test_status_map_has_wait(self, collector):
            """测试等待状态映射"""
            assert 'wait' in collector.STATUS_MAP

        def test_status_map_has_doing(self, collector):
            """测试进行中状态映射"""
            assert 'doing' in collector.STATUS_MAP

        def test_status_map_has_done(self, collector):
            """测试已完成状态映射"""
            assert 'done' in collector.STATUS_MAP

        def test_status_map_has_closed(self, collector):
            """测试已关闭状态映射"""
            assert 'closed' in collector.STATUS_MAP

        def test_status_map_has_unknown(self, collector):
            """测试未知状态映射"""
            assert 'unknown' in collector.STATUS_MAP

    class TestFormatDisplayExtended:
        """测试格式化显示 - 扩展"""

        def test_format_with_project_name(self, collector):
            """测试带项目名称的格式化"""
            # Arrange
            data = {
                'tasks': [
                    {"id": 1, "name": "任务1", "status": "wait", "project_name": "项目A"}
                ],
                'total': 1
            }

            # Act
            result = collector.format_display(data)

            # Assert
            assert "项目A" in result

        def test_format_with_time_fields(self, collector):
            """测试带时间字段的格式化"""
            # Arrange
            data = {
                'tasks': [
                    {"id": 1, "name": "任务1", "status": "wait", "created_at": "2024-01-01", "deadline": "2024-12-31"}
                ],
                'total': 1
            }

            # Act
            result = collector.format_display(data)

            # Assert
            assert "创建时间" in result
            assert "截止时间" in result

        def test_format_with_url(self, collector):
            """测试带URL的格式化"""
            # Arrange
            data = {
                'tasks': [
                    {"id": 1, "name": "任务1", "status": "wait", "url": "http://example.com/task/1"}
                ],
                'total': 1
            }

            # Act
            result = collector.format_display(data)

            # Assert
            assert "禅道链接" in result
            assert "http://example.com/task/1" in result

        def test_format_with_title_field(self, collector):
            """测试使用title字段而非name字段"""
            # Arrange
            data = {
                'tasks': [
                    {"id": 1, "title": "任务标题", "status": "wait"}
                ],
                'total': 1
            }

            # Act
            result = collector.format_display(data)

            # Assert
            assert "任务标题" in result

        def test_format_with_unknown_status(self, collector):
            """测试未知状态的格式化"""
            # Arrange
            data = {
                'tasks': [
                    {"id": 1, "name": "任务1", "status": "custom_status"}
                ],
                'total': 1
            }

            # Act
            result = collector.format_display(data)

            # Assert
            assert "custom_status" in result

        def test_format_multiple_tasks(self, collector):
            """测试多个任务的格式化"""
            # Arrange
            data = {
                'tasks': [
                    {"id": 1, "name": "任务1", "status": "wait"},
                    {"id": 2, "name": "任务2", "status": "doing"},
                    {"id": 3, "name": "任务3", "status": "done"}
                ],
                'total': 3
            }

            # Act
            result = collector.format_display(data)

            # Assert
            assert "任务 #1" in result
            assert "任务 #2" in result
            assert "任务 #3" in result
            assert "共 3 个" in result
