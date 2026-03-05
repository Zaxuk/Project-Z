# -*- coding: utf-8 -*-
"""
测试需求收集器
"""

import pytest
from unittest.mock import Mock

from src.collectors.story_collector import StoryCollector
from src.utils.response import ApiResponse, ErrorCode


class TestStoryCollector:
    """测试需求收集器"""

    @pytest.fixture
    def mock_api_client(self):
        """创建 Mock API 客户端"""
        return Mock()

    @pytest.fixture
    def collector(self, mock_api_client):
        """创建收集器实例"""
        return StoryCollector(mock_api_client)

    class TestCollect:
        """测试收集需求"""

        def test_collect_success(self, collector, mock_api_client):
            """测试成功收集需求"""
            # Arrange
            mock_api_client.get_my_stories.return_value = ApiResponse.success_response({
                'stories': [
                    {"id": 1, "title": "需求1", "status": "active"},
                    {"id": 2, "title": "需求2", "status": "active"}
                ],
                'total': 2
            })

            # Act
            result = collector.collect()

            # Assert
            assert result.success is True
            assert result.data['count'] == 2

        def test_collect_empty_list(self, collector, mock_api_client):
            """测试空需求列表"""
            # Arrange
            mock_api_client.get_my_stories.return_value = ApiResponse.success_response({
                'stories': [],
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
            mock_api_client.get_my_stories.return_value = ApiResponse.error_response(
                ErrorCode.API_ERROR,
                "获取需求列表失败"
            )

            # Act
            result = collector.collect()

            # Assert
            assert result.success is False
            assert result.error.code == ErrorCode.API_ERROR

        def test_collect_with_status_filter(self, collector, mock_api_client):
            """测试带状态过滤的收集"""
            # Arrange
            mock_api_client.get_my_stories.return_value = ApiResponse.success_response({
                'stories': [
                    {"id": 1, "title": "需求1", "status": "active"}
                ],
                'total': 1
            })

            # Act
            result = collector.collect(status='active')

            # Assert
            assert result.success is True
            mock_api_client.get_my_stories.assert_called_once_with('active')

    class TestFormatDisplay:
        """测试格式化显示"""

        def test_format_with_stories(self, collector):
            """测试格式化有需求的情况"""
            # Arrange
            data = {
                'stories': [
                    {"id": 1, "title": "测试需求", "status": "active"}
                ],
                'total': 1
            }

            # Act
            result = collector.format_display(data)

            # Assert
            assert "需求列表" in result
            assert "测试需求" in result

        def test_format_empty_stories(self, collector):
            """测试格式化空需求"""
            # Arrange
            data = {
                'stories': [],
                'total': 0
            }

            # Act
            result = collector.format_display(data)

            # Assert
            assert "暂无需求" in result

        def test_format_with_status_mapping(self, collector):
            """测试状态映射"""
            # Arrange
            data = {
                'stories': [
                    {"id": 1, "title": "需求1", "status": "active"}
                ],
                'total': 1
            }

            # Act
            result = collector.format_display(data)

            # Assert
            assert "激活" in result or "active" in result

    class TestStatusMap:
        """测试状态映射表"""

        def test_status_map_has_draft(self, collector):
            """测试草稿状态映射"""
            assert 'draft' in collector.STATUS_MAP

        def test_status_map_has_active(self, collector):
            """测试激活状态映射"""
            assert 'active' in collector.STATUS_MAP

        def test_status_map_has_closed(self, collector):
            """测试关闭状态映射"""
            assert 'closed' in collector.STATUS_MAP

    class TestStageMap:
        """测试阶段映射表"""

        def test_stage_map_has_wait(self, collector):
            """测试等待阶段映射"""
            assert 'wait' in collector.STAGE_MAP

        def test_stage_map_has_developing(self, collector):
            """测试研发中阶段映射"""
            assert 'developing' in collector.STAGE_MAP

        def test_stage_map_has_released(self, collector):
            """测试已发布阶段映射"""
            assert 'released' in collector.STAGE_MAP

    class TestFormatDisplayDetailed:
        """测试格式化显示的详细场景"""

        def test_format_with_full_story_info(self, collector):
            """测试格式化包含完整信息的需求"""
            # Arrange
            data = {
                'stories': [
                    {
                        "id": 123,
                        "title": "完整信息需求",
                        "status": "active",
                        "priority": 3,
                        "assigned_to": "user1",
                        "opened_by": "admin",
                        "opened_date": "2024-03-01",
                        "product": "产品A",
                        "plan": "计划1",
                        "stage": "developing",
                        "estimate": 16
                    }
                ],
                'total': 1
            }

            # Act
            result = collector.format_display(data)

            # Assert
            assert "完整信息需求" in result
            assert "产品A" in result
            assert "计划1" in result
            assert "研发中" in result
            assert "16" in result
            assert "admin" in result

        def test_format_with_changed_status(self, collector):
            """测试格式化已变更状态的需求"""
            # Arrange
            data = {
                'stories': [
                    {
                        "id": 456,
                        "title": "已变更需求",
                        "status": "changed",
                        "priority": 1,
                        "stage": "wait"
                    }
                ],
                'total': 1
            }

            # Act
            result = collector.format_display(data)

            # Assert
            assert "已变更" in result or "changed" in result
            assert "已变更需求" in result

        def test_format_with_closed_status(self, collector):
            """测试格式化已关闭状态的需求"""
            # Arrange
            data = {
                'stories': [
                    {
                        "id": 789,
                        "title": "已关闭需求",
                        "status": "closed",
                        "priority": 2,
                        "stage": "released"
                    }
                ],
                'total': 1
            }

            # Act
            result = collector.format_display(data)

            # Assert
            assert "已关闭" in result or "closed" in result
            assert "已关闭需求" in result

        def test_format_with_unknown_status(self, collector):
            """测试格式化未知状态的需求"""
            # Arrange
            data = {
                'stories': [
                    {
                        "id": 999,
                        "title": "未知状态需求",
                        "status": "unknown_status",
                        "priority": 0
                    }
                ],
                'total': 1
            }

            # Act
            result = collector.format_display(data)

            # Assert
            assert "未知状态需求" in result

        def test_format_with_invalid_priority(self, collector):
            """测试格式化无效优先级的需求"""
            # Arrange
            data = {
                'stories': [
                    {
                        "id": 111,
                        "title": "无效优先级需求",
                        "status": "active",
                        "priority": "invalid"
                    }
                ],
                'total': 1
            }

            # Act
            result = collector.format_display(data)

            # Assert
            assert "无效优先级需求" in result

        def test_format_with_multiple_stories(self, collector):
            """测试格式化多个需求"""
            # Arrange
            data = {
                'stories': [
                    {"id": 1, "title": "需求1", "status": "active"},
                    {"id": 2, "title": "需求2", "status": "draft"},
                    {"id": 3, "title": "需求3", "status": "closed"}
                ],
                'total': 3
            }

            # Act
            result = collector.format_display(data)

            # Assert
            assert "需求1" in result
            assert "需求2" in result
            assert "需求3" in result
            assert "共 3 个" in result
