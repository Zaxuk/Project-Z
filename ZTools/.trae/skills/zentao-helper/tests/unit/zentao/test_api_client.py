# -*- coding: utf-8 -*-
"""
测试 ZenTao API 客户端
"""

import json
import requests
import pytest
from unittest.mock import Mock, patch

from src.zentao.api_client import ZentaoApiClient
from src.utils.response import ErrorCode, ApiResponse


class TestZentaoApiClient:
    """测试 ZenTao API 客户端"""

    @pytest.fixture
    def client(self):
        """创建 API 客户端实例"""
        with patch('src.zentao.api_client.get_config') as mock_config:
            mock_config.return_value = Mock()
            mock_config.return_value.get_zentao_config.return_value = {
                'base_url': 'http://test.zentao.com/',
                'timeout': 30,
                'retry_times': 3,
                'retry_backoff': 1
            }
            client = ZentaoApiClient()
            # Mock session
            client.session = Mock()
            return client

    class TestGetStory:
        """测试获取需求详情"""

        def test_get_story_success(self, client):
            """测试成功获取需求详情"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "success",
                "data": json.dumps({
                    "story": {
                        "id": 123,
                        "title": "测试需求标题",
                        "spec": "<p>测试需求内容</p>",
                        "status": "active",
                        "pri": 1,
                        "assignedTo": "test_user",
                        "openedBy": "creator",
                        "openedDate": "2024-01-01 10:00:00",
                        "product": 1,
                        "productTitle": "测试产品",
                        "stage": "wait",
                        "estimate": 4,
                        "execution": 10,
                        "executions": [{"id": 10, "name": "测试项目"}]
                    }
                })
            }
            client.session.get.return_value = mock_response

            # Act
            result = client.get_story(123)

            # Assert
            assert result.success is True
            assert result.data["id"] == 123
            assert result.data["title"] == "测试需求标题"
            assert result.data["content"] == "<p>测试需求内容</p>"

        def test_get_story_not_found(self, client):
            """测试需求不存在"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "success",
                "data": json.dumps({
                    "story": None
                })
            }
            client.session.get.return_value = mock_response

            # Act
            result = client.get_story(99999)

            # Assert
            assert result.success is False
            assert result.error.code == ErrorCode.STORY_NOT_FOUND

        def test_get_story_api_error(self, client):
            """测试 API 错误"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 500
            client.session.get.return_value = mock_response

            # Act
            result = client.get_story(123)

            # Assert
            assert result.success is False
            assert result.error.code == ErrorCode.API_ERROR

    class TestGetTask:
        """测试获取任务详情"""

        def test_get_task_success(self, client):
            """测试成功获取任务详情"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "success",
                "data": json.dumps({
                    "task": {
                        "id": 456,
                        "name": "测试任务",
                        "status": "wait",
                        "assignedTo": "user1",
                        "openedBy": "creator",
                        "openedDate": "2024-01-01",
                        "pri": 1,
                        "estimate": 4,
                        "execution": 10,
                        "project": 10,
                        "parent": 0
                    }
                })
            }
            client.session.get.return_value = mock_response

            # Act
            result = client.get_task(456)

            # Assert
            assert result.success is True
            assert result.data["id"] == 456
            assert result.data["title"] == "测试任务"

        def test_get_task_not_found(self, client):
            """测试任务不存在"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "success",
                "data": json.dumps({
                    "task": None
                })
            }
            client.session.get.return_value = mock_response

            # Act
            result = client.get_task(99999)

            # Assert
            assert result.success is False

    class TestGetExecutions:
        """测试获取项目列表"""

        def test_get_executions_success(self, client):
            """测试成功获取项目列表"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "success",
                "data": json.dumps({
                    "projects": [
                        {"id": 1, "name": "项目1", "status": "doing", "begin": "2024-01-01", "end": "2024-12-31"},
                        {"id": 2, "name": "项目2", "status": "wait", "begin": "2024-02-01", "end": "2024-11-30"}
                    ]
                })
            }
            client.session.get.return_value = mock_response

            # Act
            result = client.get_executions()

            # Assert
            assert result.success is True
            assert len(result.data) == 2
            assert result.data[0]["name"] == "项目1"

        def test_get_executions_api_error(self, client):
            """测试 API 错误"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 500
            client.session.get.return_value = mock_response

            # Act
            result = client.get_executions()

            # Assert
            assert result.success is False

        def test_get_executions_dict_format(self, client):
            """测试字典格式的项目列表"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "success",
                "data": json.dumps({
                    "projects": {
                        "1": {"id": 1, "name": "项目1", "status": "doing", "begin": "2024-01-01", "end": "2024-12-31"},
                        "2": {"id": 2, "name": "项目2", "status": "wait", "begin": "2024-02-01", "end": "2024-11-30"}
                    }
                })
            }
            client.session.get.return_value = mock_response

            # Act
            result = client.get_executions()

            # Assert
            assert result.success is True
            assert len(result.data) == 2

        def test_get_executions_single_dict(self, client):
            """测试单个项目字典格式"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "success",
                "data": json.dumps({
                    "projects": {
                        "id": 1, "name": "项目1", "status": "doing", "begin": "2024-01-01", "end": "2024-12-31"
                    }
                })
            }
            client.session.get.return_value = mock_response

            # Act
            result = client.get_executions()

            # Assert
            assert result.success is True
            assert len(result.data) == 1

        def test_get_executions_string_values(self, client):
            """测试字符串值的项目列表"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "success",
                "data": json.dumps({
                    "projects": {
                        "1": "项目1",
                        "2": "项目2"
                    }
                })
            }
            client.session.get.return_value = mock_response

            # Act
            result = client.get_executions()

            # Assert
            assert result.success is True
            assert len(result.data) == 2

        def test_get_executions_done_closed_filtered(self, client):
            """测试已完成和已关闭项目被过滤"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "success",
                "data": json.dumps({
                    "projects": [
                        {"id": 1, "name": "项目1", "status": "doing", "begin": "2024-01-01", "end": "2024-12-31"},
                        {"id": 2, "name": "项目2", "status": "done", "begin": "2024-02-01", "end": "2024-11-30"},
                        {"id": 3, "name": "项目3", "status": "closed", "begin": "2024-03-01", "end": "2024-10-31"}
                    ]
                })
            }
            client.session.get.return_value = mock_response

            # Act
            result = client.get_executions()

            # Assert
            assert result.success is True
            assert len(result.data) == 1  # 只有 doing 状态的项目

        def test_get_executions_invalid_response(self, client):
            """测试无效响应"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "success",
                "data": "invalid json"
            }
            client.session.get.return_value = mock_response

            # Act
            result = client.get_executions()

            # Assert
            assert result.success is False

    class TestUpdateStoryTitle:
        """测试更新需求标题"""

        def test_update_story_title_success(self, client):
            """测试成功更新需求标题"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "success",
                "data": json.dumps({
                    "result": "success"
                })
            }
            client.session.post.return_value = mock_response

            # Act
            result = client.update_story_title(123, "新标题")

            # Assert
            assert result.success is True

        def test_update_story_title_api_error(self, client):
            """测试更新标题 API 错误"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 500
            client.session.post.return_value = mock_response

            # Act
            result = client.update_story_title(123, "新标题")

            # Assert
            assert result.success is False

    class TestGetStoryTaskCount:
        """测试获取需求任务数量"""

        def test_get_story_task_count_success(self, client):
            """测试成功获取任务数量"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "success",
                "data": json.dumps({
                    "story": {
                        "id": 123,
                        "title": "测试需求",
                        "tasks": {
                            "10": [
                                {"id": 1, "name": "任务1", "deleted": "0"},
                                {"id": 2, "name": "任务2", "deleted": "0"}
                            ]
                        }
                    }
                })
            }
            client.session.get.return_value = mock_response

            # Act
            result = client.get_story_task_count(123)

            # Assert
            assert result == 2

        def test_get_story_task_count_empty(self, client):
            """测试无任务的情况"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "success",
                "data": json.dumps({
                    "story": {
                        "id": 123,
                        "title": "测试需求",
                        "tasks": {}
                    }
                })
            }
            client.session.get.return_value = mock_response

            # Act
            result = client.get_story_task_count(123)

            # Assert
            assert result == 0

    class TestReviewStory:
        """测试评审需求"""

        def test_review_story_not_story_status(self, client):
            """测试非变更状态的需求无需评审"""
            # Arrange
            mock_get_response = Mock()
            mock_get_response.status_code = 200
            mock_get_response.json.return_value = {
                "status": "success",
                "data": json.dumps({
                    "story": {
                        "id": 123,
                        "title": "测试需求",
                        "status": "active",
                        "version": 1
                    }
                })
            }
            client.session.get.return_value = mock_get_response

            # Act
            result = client.review_story(123, result="pass")

            # Assert
            assert result.success is True

    class TestParseTaskSelectHtml:
        """测试解析任务选择 HTML"""

        def test_parse_task_select_html_success(self, client):
            """测试成功解析任务列表 HTML"""
            # Arrange
            html = """
            <select>
                <option value='123'>项目A / 任务1</option>
                <option value='456'>项目B / 任务2</option>
            </select>
            """

            # Act
            result = client._parse_task_select_html(html)

            # Assert
            assert len(result) == 2
            assert result[0]['id'] == 123
            assert result[0]['name'] == '任务1'
            assert result[0]['project_name'] == '项目A'

        def test_parse_task_select_html_empty(self, client):
            """测试空 HTML"""
            # Act
            result = client._parse_task_select_html("")

            # Assert
            assert len(result) == 0

        def test_parse_task_select_html_no_project(self, client):
            """测试没有项目名的任务"""
            # Arrange
            html = "<option value='789'>简单任务</option>"

            # Act
            result = client._parse_task_select_html(html)

            # Assert
            assert len(result) == 1
            assert result[0]['id'] == 789
            assert result[0]['name'] == '简单任务'
            assert result[0]['project_name'] == ''

    class TestGetTaskDetail:
        """测试获取任务详情（内部方法）"""

        def test_get_task_detail_success(self, client):
            """测试成功获取任务详情"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "success",
                "data": json.dumps({
                    "task": {
                        "id": 123,
                        "openedDate": "2024-01-01 10:00:00",
                        "deadline": "2024-01-15",
                        "status": "doing"
                    }
                })
            }
            client.session.get.return_value = mock_response

            # Act
            result = client._get_task_detail(123)

            # Assert
            assert result is not None
            assert result['created_at'] == "2024-01-01 10:00:00"
            assert result['deadline'] == "2024-01-15"
            assert result['status'] == "doing"

        def test_get_task_detail_not_found(self, client):
            """测试任务不存在"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 404
            client.session.get.return_value = mock_response

            # Act
            result = client._get_task_detail(999)

            # Assert
            assert result is None

    class TestSplitTask:
        """测试任务拆解"""

        def test_split_task_success(self, client):
            """测试成功拆解任务"""
            # Arrange
            with patch.object(client, '_get_task_detail_full', return_value={
                'id': 100,
                'project': 10,
                'name': '父任务'
            }):
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.url = 'http://test.zentao.com/task-view-101.html'
                client.session.post.return_value = mock_response

                # Act
                result = client.split_task(100, ["子任务1", "子任务2"])

                # Assert
                assert result.success is True
                assert 'created_tasks' in result.data

        def test_split_task_parent_not_found(self, client):
            """测试父任务不存在"""
            # Arrange
            with patch.object(client, '_get_task_detail_full', return_value=None):
                # Act
                result = client.split_task(999, ["子任务1"])

                # Assert
                assert result.success is False
                assert result.error.code == ErrorCode.TASK_NOT_FOUND

    class TestGetMyTasks:
        """测试获取我的任务"""

        def test_get_my_tasks_success(self, client):
            """测试成功获取任务列表"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = """
            <select>
                <option value='201'>项目A / 任务1</option>
                <option value='202'>项目B / 任务2</option>
            </select>
            """
            client.session.get.return_value = mock_response

            with patch.object(client, '_get_task_detail', return_value={
                'created_at': '2024-01-01',
                'deadline': '2024-01-15',
                'status': 'doing'
            }):
                # Act
                result = client.get_my_tasks()

                # Assert
                assert result.success is True
                assert len(result.data['tasks']) == 2

        def test_get_my_tasks_empty(self, client):
            """测试空任务列表"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "<select></select>"
            client.session.get.return_value = mock_response

            # Act
            result = client.get_my_tasks()

            # Assert
            assert result.success is True
            assert len(result.data['tasks']) == 0

        def test_get_my_tasks_http_error(self, client):
            """测试 HTTP 错误"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 500
            client.session.get.return_value = mock_response

            # Act
            result = client.get_my_tasks()

            # Assert
            assert result.success is False

    class TestGetTaskDetailFull:
        """测试获取任务完整详情"""

        def test_get_task_detail_full_success(self, client):
            """测试成功获取任务完整详情"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "success",
                "data": json.dumps({
                    "task": {
                        "id": 100,
                        "name": "测试任务",
                        "project": 10,
                        "status": "doing",
                        "assignedTo": "user1"
                    }
                })
            }
            client.session.get.return_value = mock_response

            # Act
            result = client._get_task_detail_full(100)

            # Assert
            assert result is not None
            assert result['id'] == 100
            assert result['name'] == "测试任务"

        def test_get_task_detail_full_not_found(self, client):
            """测试任务不存在"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 404
            client.session.get.return_value = mock_response

            # Act
            result = client._get_task_detail_full(999)

            # Assert
            assert result is None

    class TestCreateTask:
        """测试创建任务"""

        def test_create_task_success(self, client):
            """测试成功创建任务"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.url = 'http://test.zentao.com/task-view-123.html'
            client.session.post.return_value = mock_response

            # Act
            result = client.create_task(
                execution_id=10,
                name="测试任务",
                assigned_to="user1",
                estimate=4,
                deadline="2024-03-15"
            )

            # Assert
            assert result.success is True
            assert result.data['id'] == 123

        def test_create_task_no_redirect(self, client):
            """测试创建任务但没有重定向到任务页面"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.url = 'http://test.zentao.com/project-task-10.html'
            client.session.post.return_value = mock_response

            # Act
            result = client.create_task(
                execution_id=10,
                name="测试任务"
            )

            # Assert
            assert result.success is True

        def test_create_task_with_error(self, client):
            """测试创建任务返回错误"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.url = 'http://test.zentao.com/task-create-10-0.html'
            mock_response.text = '<div class="error">错误信息</div>'
            client.session.post.return_value = mock_response

            # Act
            result = client.create_task(
                execution_id=10,
                name="测试任务"
            )

            # Assert
            assert result.success is False

        def test_create_task_http_error(self, client):
            """测试 HTTP 错误"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 500
            client.session.post.return_value = mock_response

            # Act
            result = client.create_task(
                execution_id=10,
                name="测试任务"
            )

            # Assert
            assert result.success is False

    class TestAssignTask:
        """测试任务分配"""

        def test_assign_task_success(self, client):
            """测试成功分配任务"""
            # Arrange
            with patch.object(client, '_get_task_detail_full') as mock_get_detail:
                mock_get_detail.return_value = {
                    'id': 100,
                    'name': '测试任务',
                    'project': 10
                }

                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.url = 'http://test.zentao.com/execution-task-10.html'
                client.session.post.return_value = mock_response

                # Act
                result = client.assign_task(100, 'user1')

                # Assert
                assert result is not None
                assert result.success is True
                assert result.data['assigned_to'] == 'user1'

        def test_assign_task_task_not_found(self, client):
            """测试任务不存在"""
            # Arrange
            with patch.object(client, '_get_task_detail_full') as mock_get_detail:
                mock_get_detail.return_value = None

                # Act
                result = client.assign_task(999, 'user1')

                # Assert
                assert result is not None
                assert result.success is False

        def test_assign_task_no_project(self, client):
            """测试任务没有项目信息"""
            # Arrange
            with patch.object(client, '_get_task_detail_full') as mock_get_detail:
                mock_get_detail.return_value = {
                    'id': 100,
                    'name': '测试任务'
                }

                # Act
                result = client.assign_task(100, 'user1')

                # Assert
                assert result is not None
                assert result.success is False

        def test_assign_task_failure(self, client):
            """测试分配失败"""
            # Arrange
            with patch.object(client, '_get_task_detail_full') as mock_get_detail:
                mock_get_detail.return_value = {
                    'id': 100,
                    'name': '测试任务',
                    'project': 10
                }

                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.url = 'http://test.zentao.com/task-assign-100.html'
                client.session.post.return_value = mock_response

                # Act
                result = client.assign_task(100, 'user1')

                # Assert
                assert result is not None
                assert result.success is False

        def test_assign_task_http_error(self, client):
            """测试 HTTP 错误"""
            # Arrange
            with patch.object(client, '_get_task_detail_full') as mock_get_detail:
                mock_get_detail.return_value = {
                    'id': 100,
                    'name': '测试任务',
                    'project': 10
                }

                mock_response = Mock()
                mock_response.status_code = 500
                client.session.post.return_value = mock_response

                # Act
                result = client.assign_task(100, 'user1')

                # Assert
                assert result is not None
                assert result.success is False

        def test_assign_task_json_success(self, client):
            """测试 JSON 成功响应"""
            # Arrange
            with patch.object(client, '_get_task_detail_full') as mock_get_detail:
                mock_get_detail.return_value = {
                    'id': 100,
                    'name': '测试任务',
                    'project': 10
                }

                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.url = 'http://test.zentao.com/task-view-100.html'
                mock_response.text = '<html>Content</html>'
                mock_response.json.return_value = {'status': 'success'}
                client.session.post.return_value = mock_response

                # Act
                result = client.assign_task(100, 'user1')

                # Assert
                assert result is not None
                assert result.success is True

        def test_assign_task_json_failure(self, client):
            """测试 JSON 失败响应"""
            # Arrange
            with patch.object(client, '_get_task_detail_full') as mock_get_detail:
                mock_get_detail.return_value = {
                    'id': 100,
                    'name': '测试任务',
                    'project': 10
                }

                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.url = 'http://test.zentao.com/task-assign-100.html'
                mock_response.text = '<html>Content</html>'
                mock_response.json.return_value = {'status': 'failed', 'message': '分配失败'}
                client.session.post.return_value = mock_response

                # Act
                result = client.assign_task(100, 'user1')

                # Assert
                assert result is not None
                assert result.success is False

    class TestGetMyStories:
        """测试获取我的需求"""

        def test_get_my_stories_success(self, client):
            """测试成功获取需求列表"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "success",
                "data": json.dumps({
                    "stories": [
                        {"id": 1, "title": "需求1", "status": "active"},
                        {"id": 2, "title": "需求2", "status": "draft"}
                    ]
                })
            }
            client.session.get.return_value = mock_response

            # Act
            result = client.get_my_stories()

            # Assert
            assert result is not None
            assert result.success is True

        def test_get_my_stories_with_status(self, client):
            """测试带状态过滤获取需求"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "success",
                "data": json.dumps({
                    "stories": [
                        {"id": 1, "title": "需求1", "status": "active"}
                    ]
                })
            }
            client.session.get.return_value = mock_response

            # Act
            result = client.get_my_stories(status='active')

            # Assert
            assert result is not None
            assert result.success is True

        def test_get_my_stories_http_error(self, client):
            """测试 HTTP 错误 - 返回空列表"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 500
            client.session.get.return_value = mock_response

            # Act
            result = client.get_my_stories()

            # Assert - HTTP 错误时返回成功响应（空列表）
            assert result is not None
            assert result.success is True
            assert result.data['stories'] == []
            assert result.data['total'] == 0

        def test_get_my_stories_api_error(self, client):
            """测试 API 返回错误状态 - 返回空列表"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "error",
                "message": "权限不足"
            }
            client.session.get.return_value = mock_response

            # Act
            result = client.get_my_stories()

            # Assert - API 错误时返回成功响应（空列表）
            assert result is not None
            assert result.success is True
            assert result.data['stories'] == []
            assert result.data['total'] == 0

        def test_get_my_stories_empty(self, client):
            """测试空需求列表"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "success",
                "data": json.dumps({
                    "stories": []
                })
            }
            client.session.get.return_value = mock_response

            # Act
            result = client.get_my_stories()

            # Assert
            assert result is not None
            assert result.success is True
            assert len(result.data['stories']) == 0

    class TestVerifySession:
        """测试会话验证"""

        def test_verify_session_success(self, client):
            """测试会话有效"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.url = 'http://test.zentao.com/my-story-assignedTo-id_desc-9999-1-1.json'
            mock_response.json.return_value = {
                "status": "success",
                "data": json.dumps({"stories": []})
            }
            client.session.get.return_value = mock_response

            # Act
            result = client.verify_session()

            # Assert
            assert result is True

        def test_verify_session_redirected(self, client):
            """测试会话失效（被重定向到登录页）"""
            # Arrange
            mock_response = Mock()
            mock_response.url = 'http://test.zentao.com/user-login.html'
            client.session.get.return_value = mock_response

            # Act
            result = client.verify_session()

            # Assert
            assert result is False

        def test_verify_session_error_response(self, client):
            """测试返回错误状态"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.url = 'http://test.zentao.com/my-story-assignedTo-id_desc-9999-1-1.json'
            mock_response.json.return_value = {
                "status": "error"
            }
            client.session.get.return_value = mock_response

            # Act
            result = client.verify_session()

            # Assert
            assert result is False

    class TestGetTask:
        """测试获取任务详情"""

        def test_get_task_success(self, client):
            """测试成功获取任务"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "success",
                "data": json.dumps({
                    "task": {
                        "id": 100,
                        "name": "测试任务",
                        "status": "doing",
                        "pri": 1,
                        "assignedTo": "user1",
                        "openedBy": "admin",
                        "openedDate": "2024-01-01",
                        "estimate": 8,
                        "execution": 10,
                        "project": 5,
                        "parent": 0
                    }
                })
            }
            client.session.get.return_value = mock_response

            # Act
            result = client.get_task(100)

            # Assert
            assert result is not None
            assert result.success is True
            assert result.data['title'] == "测试任务"
            assert result.data['status'] == "doing"

        def test_get_task_not_found(self, client):
            """测试任务不存在"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 404
            client.session.get.return_value = mock_response

            # Act
            result = client.get_task(999)

            # Assert
            assert result is not None
            assert result.success is False

        def test_get_task_parse_error(self, client):
            """测试解析失败"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "success",
                "data": "invalid json"
            }
            client.session.get.return_value = mock_response

            # Act
            result = client.get_task(100)

            # Assert
            assert result is not None
            assert result.success is False

    class TestGetStory:
        """测试获取需求详情"""

        def test_get_story_success(self, client):
            """测试成功获取需求"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "success",
                "data": json.dumps({
                    "story": {
                        "id": 50,
                        "title": "测试需求",
                        "spec": "需求描述内容",
                        "status": "active",
                        "pri": 1,
                        "assignedTo": "user1",
                        "openedBy": "admin",
                        "openedDate": "2024-01-01",
                        "productTitle": "产品A",
                        "product": 10,
                        "stage": "developing",
                        "estimate": 16,
                        "executions": [{"id": 20, "name": "执行1"}]
                    }
                })
            }
            client.session.get.return_value = mock_response

            # Act
            result = client.get_story(50)

            # Assert
            assert result is not None
            assert result.success is True
            assert result.data['title'] == "测试需求"
            assert result.data['status'] == "active"
            assert result.data['execution'] == 20

        def test_get_story_not_found(self, client):
            """测试需求不存在"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 404
            client.session.get.return_value = mock_response

            # Act
            result = client.get_story(999)

            # Assert
            assert result is not None
            assert result.success is False

        def test_get_story_with_plan_dict(self, client):
            """测试计划字段为字典格式"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "success",
                "data": json.dumps({
                    "story": {
                        "id": 50,
                        "title": "测试需求",
                        "status": "active",
                        "spec": "需求描述",
                        "pri": 1,
                        "assignedTo": "user1",
                        "openedBy": "admin",
                        "openedDate": "2024-01-01",
                        "productTitle": "产品A",
                        "product": 10,
                        "stage": "developing",
                        "estimate": 16,
                        "planTitle": {"1": "计划1", "2": "计划2"}
                    }
                })
            }
            client.session.get.return_value = mock_response

            # Act
            result = client.get_story(50)

            # Assert
            assert result is not None
            assert result.success is True
            assert result.data['plan'] == "计划1"

        def test_get_story_with_execution_field(self, client):
            """测试从 execution 字段获取执行ID"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "success",
                "data": json.dumps({
                    "story": {
                        "id": 50,
                        "title": "测试需求",
                        "status": "active",
                        "spec": "需求描述",
                        "pri": 1,
                        "assignedTo": "user1",
                        "openedBy": "admin",
                        "openedDate": "2024-01-01",
                        "productTitle": "产品A",
                        "product": 10,
                        "stage": "developing",
                        "estimate": 16,
                        "execution": 25
                    }
                })
            }
            client.session.get.return_value = mock_response

            # Act
            result = client.get_story(50)

            # Assert
            assert result is not None
            assert result.success is True
            assert result.data['execution'] == 25

        def test_get_story_with_plan_field(self, client):
            """测试从 plan 字段获取执行ID"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "success",
                "data": json.dumps({
                    "story": {
                        "id": 50,
                        "title": "测试需求",
                        "status": "active",
                        "spec": "需求描述",
                        "pri": 1,
                        "assignedTo": "user1",
                        "openedBy": "admin",
                        "openedDate": "2024-01-01",
                        "productTitle": "产品A",
                        "product": 10,
                        "stage": "developing",
                        "estimate": 16,
                        "plan": {"30": "计划A", "40": "计划B"}
                    }
                })
            }
            client.session.get.return_value = mock_response

            # Act
            result = client.get_story(50)

            # Assert
            assert result is not None
            assert result.success is True
            assert result.data['execution'] == 30

        def test_get_story_parse_error(self, client):
            """测试 JSON 解析错误"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "success",
                "data": "invalid json"
            }
            client.session.get.return_value = mock_response

            # Act
            result = client.get_story(50)

            # Assert
            assert result is not None
            assert result.success is False

    class TestUpdateStoryTitle:
        """测试更新需求标题"""

        def test_update_story_title_success(self, client):
            """测试成功更新需求标题"""
            # Arrange
            with patch.object(client, 'get_story') as mock_get_story:
                mock_get_story.return_value = ApiResponse.success_response({
                    'id': 123,
                    'title': '旧标题',
                    'content': '需求内容',
                    'product_id': 10,
                    'priority': 1,
                    'estimate': 8,
                    'stage': 'wait',
                    'assigned_to': 'user1'
                })

                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {'status': 'success'}
                client.session.post.return_value = mock_response

                # Act
                result = client.update_story_title(123, '【A】新标题')

                # Assert
                assert result is not None
                assert result.success is True

        def test_update_story_title_get_story_failed(self, client):
            """测试获取需求失败但继续更新"""
            # Arrange
            with patch.object(client, 'get_story') as mock_get_story:
                mock_get_story.return_value = ApiResponse.error_response(
                    ErrorCode.STORY_NOT_FOUND,
                    '需求不存在'
                )

                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {'status': 'success'}
                client.session.post.return_value = mock_response

                # Act
                result = client.update_story_title(123, '【A】新标题')

                # Assert
                assert result is not None

        def test_update_story_title_http_error(self, client):
            """测试 HTTP 错误"""
            # Arrange
            with patch.object(client, 'get_story') as mock_get_story:
                mock_get_story.return_value = ApiResponse.success_response({
                    'id': 123,
                    'title': '旧标题',
                    'content': '需求内容',
                    'product_id': 10
                })

                mock_response = Mock()
                mock_response.status_code = 500
                client.session.post.return_value = mock_response

                # Act
                result = client.update_story_title(123, '【A】新标题')

                # Assert
                assert result is not None
                assert result.success is False

        def test_update_story_title_error_response(self, client):
            """测试返回错误响应"""
            # Arrange
            with patch.object(client, 'get_story') as mock_get_story:
                mock_get_story.return_value = ApiResponse.success_response({
                    'id': 123,
                    'title': '旧标题',
                    'content': '需求内容',
                    'product_id': 10
                })

                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {'status': 'failed', 'message': '权限不足'}
                client.session.post.return_value = mock_response

                # Act
                result = client.update_story_title(123, '【A】新标题')

                # Assert
                assert result is not None
                assert result.success is False

        def test_update_story_title_non_json_error(self, client):
            """测试非 JSON 错误响应"""
            # Arrange
            with patch.object(client, 'get_story') as mock_get_story:
                mock_get_story.return_value = ApiResponse.success_response({
                    'id': 123,
                    'title': '旧标题',
                    'content': '需求内容',
                    'product_id': 10
                })

                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.side_effect = ValueError("Invalid JSON")
                mock_response.text = '<div class="error">系统错误</div>'
                client.session.post.return_value = mock_response

                # Act
                result = client.update_story_title(123, '【A】新标题')

                # Assert
                assert result is not None
                assert result.success is False

        def test_update_story_title_non_json_success(self, client):
            """测试非 JSON 成功响应"""
            # Arrange
            with patch.object(client, 'get_story') as mock_get_story:
                mock_get_story.return_value = ApiResponse.success_response({
                    'id': 123,
                    'title': '旧标题',
                    'content': '需求内容',
                    'product_id': 10
                })

                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.side_effect = ValueError("Invalid JSON")
                mock_response.text = '<html>Success</html>'
                client.session.post.return_value = mock_response

                # Act
                result = client.update_story_title(123, '【A】新标题')

                # Assert
                assert result is not None
                assert result.success is True

    class TestReviewStory:
        """测试评审需求"""

        def test_review_story_success(self, client):
            """测试成功评审需求"""
            # Arrange
            with patch.object(client, 'get_story') as mock_get_story:
                mock_get_story.return_value = ApiResponse.success_response({
                    'id': 123,
                    'status': 'changed',
                    'assigned_to': 'user1',
                    'estimate': 8
                })

                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.text = 'parent.location = "/story-view-123.html"'
                client.session.post.return_value = mock_response

                # Act
                result = client.review_story(123, result='pass')

                # Assert
                assert result is not None
                assert result.success is True

        def test_review_story_not_changed(self, client):
            """测试需求状态不是已变更"""
            # Arrange
            with patch.object(client, 'get_story') as mock_get_story:
                mock_get_story.return_value = ApiResponse.success_response({
                    'id': 123,
                    'status': 'active',
                    'assigned_to': 'user1'
                })

                # Act
                result = client.review_story(123, result='pass')

                # Assert
                assert result is not None
                assert result.success is True
                assert '无需评审' in result.data['message']

        def test_review_story_json_success(self, client):
            """测试 JSON 成功响应"""
            # Arrange
            with patch.object(client, 'get_story') as mock_get_story:
                mock_get_story.return_value = ApiResponse.success_response({
                    'id': 123,
                    'status': 'changed',
                    'assigned_to': 'user1',
                    'estimate': 8
                })

                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.text = '<html>Some content</html>'
                mock_response.json.return_value = {'status': 'success'}
                client.session.post.return_value = mock_response

                # Act
                result = client.review_story(123, result='pass')

                # Assert
                assert result is not None
                assert result.success is True

        def test_review_story_json_failure(self, client):
            """测试 JSON 失败响应"""
            # Arrange
            with patch.object(client, 'get_story') as mock_get_story:
                mock_get_story.return_value = ApiResponse.success_response({
                    'id': 123,
                    'status': 'changed',
                    'assigned_to': 'user1',
                    'estimate': 8
                })

                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.text = '<html>Some content</html>'
                mock_response.json.return_value = {'status': 'failed', 'message': '评审失败'}
                client.session.post.return_value = mock_response

                # Act
                result = client.review_story(123, result='pass')

                # Assert
                assert result is not None
                assert result.success is False

        def test_review_story_http_error(self, client):
            """测试 HTTP 错误"""
            # Arrange
            with patch.object(client, 'get_story') as mock_get_story:
                mock_get_story.return_value = ApiResponse.success_response({
                    'id': 123,
                    'status': 'changed',
                    'assigned_to': 'user1',
                    'estimate': 8
                })

                mock_response = Mock()
                mock_response.status_code = 500
                client.session.post.return_value = mock_response

                # Act
                result = client.review_story(123, result='pass')

                # Assert
                assert result is not None
                assert result.success is False

        def test_review_story_get_story_failed(self, client):
            """测试获取需求失败"""
            # Arrange
            with patch.object(client, 'get_story') as mock_get_story:
                mock_get_story.return_value = ApiResponse.error_response(
                    ErrorCode.STORY_NOT_FOUND,
                    '需求不存在'
                )

                # Act
                result = client.review_story(123, result='pass')

                # Assert
                assert result is not None
                assert result.success is False

    class TestCreateTask:
        """测试创建任务"""

        def test_create_task_success(self, client):
            """测试成功创建任务"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.url = 'http://test.zentao.com/task-view-456.html'
            client.session.post.return_value = mock_response

            # Act
            result = client.create_task(
                execution_id=10,
                name='【研发】测试任务',
                assigned_to='user1',
                estimate=8,
                story_id=123
            )

            # Assert
            assert result is not None
            assert result.success is True

        def test_create_task_with_deadline(self, client):
            """测试带截止日期的创建"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.url = 'http://test.zentao.com/task-view-789.html'
            client.session.post.return_value = mock_response

            # Act
            result = client.create_task(
                execution_id=10,
                name='【测试】带截止日期的任务',
                assigned_to='user2',
                estimate=4,
                deadline='2024-03-15',
                story_id=123
            )

            # Assert
            assert result is not None
            assert result.success is True

        def test_create_task_project_task_url(self, client):
            """测试创建任务后重定向到项目任务列表"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.url = 'http://test.zentao.com/project-task-10.html'
            client.session.post.return_value = mock_response

            # Act
            result = client.create_task(
                execution_id=10,
                name='测试任务'
            )

            # Assert
            assert result is not None
            assert result.success is True

        def test_create_task_error_page(self, client):
            """测试创建任务返回错误页面"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.url = 'http://test.zentao.com/task-create-10-0.html'
            mock_response.text = '<div class="error">任务名称不能为空</div>'
            client.session.post.return_value = mock_response

            # Act
            result = client.create_task(
                execution_id=10,
                name=''
            )

            # Assert
            assert result is not None
            assert result.success is False

        def test_create_task_http_error(self, client):
            """测试 HTTP 错误"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 500
            client.session.post.return_value = mock_response

            # Act
            result = client.create_task(
                execution_id=10,
                name='测试任务'
            )

            # Assert
            assert result is not None
            assert result.success is False

    class TestLogin:
        """测试登录方法"""

        def test_login_success(self, client):
            """测试成功登录"""
            # Arrange
            with patch('requests.Session') as mock_session_class, \
                 patch.object(client, '_get_current_user_v8', return_value={
                     'id': 1,
                     'account': 'test_user',
                     'realname': '测试用户'
                 }):
                mock_session = Mock()
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    'status': 'success',
                    'result': 'success'
                }
                mock_session.get.return_value = mock_response
                mock_session.post.return_value = mock_response
                mock_session.cookies = {'session': 'abc123'}
                mock_session_class.return_value = mock_session

                # Act
                result = client.login('test_user', 'password123')

                # Assert
                assert result is not None
                assert result.success is True
                assert 'cookies' in result.data

        def test_login_failure(self, client):
            """测试登录失败"""
            # Arrange
            with patch('requests.Session') as mock_session_class:
                mock_session = Mock()
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    'status': 'failed',
                    'message': '用户名或密码错误'
                }
                mock_session.get.return_value = mock_response
                mock_session.post.return_value = mock_response
                mock_session_class.return_value = mock_session

                # Act
                result = client.login('test_user', 'wrong_password')

                # Assert
                assert result is not None
                assert result.success is False
                assert result.error.code == ErrorCode.LOGIN_FAILED

        def test_login_timeout(self, client):
            """测试登录超时"""
            # Arrange
            import requests
            with patch('requests.Session') as mock_session_class:
                mock_session = Mock()
                mock_session.get.side_effect = requests.Timeout("连接超时")
                mock_session_class.return_value = mock_session

                # Act
                result = client.login('test_user', 'password123')

                # Assert
                assert result is not None
                assert result.success is False
                assert result.error.code == ErrorCode.TIMEOUT

        def test_login_connection_error(self, client):
            """测试登录连接错误"""
            # Arrange
            import requests
            with patch('requests.Session') as mock_session_class:
                mock_session = Mock()
                mock_session.get.side_effect = requests.ConnectionError("连接被拒绝")
                mock_session_class.return_value = mock_session

                # Act
                result = client.login('test_user', 'password123')

                # Assert
                assert result is not None
                assert result.success is False
                assert result.error.code == ErrorCode.NETWORK_ERROR

    class TestGetUsers:
        """测试获取用户列表"""

        def test_get_users_success(self, client):
            """测试成功获取用户列表"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'status': 'success',
                'users': [
                    {'id': 1, 'account': 'user1', 'realname': '用户1'},
                    {'id': 2, 'account': 'user2', 'realname': '用户2'}
                ]
            }
            client.session.get.return_value = mock_response

            # Act
            result = client._get_users()

            # Assert
            assert len(result) == 2
            assert '1' in result
            assert '2' in result

        def test_get_users_cache(self, client):
            """测试用户缓存"""
            # Arrange
            client._users_cache = {
                '1': Mock(),
                '2': Mock()
            }

            # Act
            result = client._get_users()

            # Assert
            assert len(result) == 2
            # 不应该调用 API
            client.session.get.assert_not_called()

        def test_get_users_error(self, client):
            """测试获取用户列表失败"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 500
            client.session.get.return_value = mock_response

            # Act
            result = client._get_users()

            # Assert
            assert len(result) == 0

    class TestSetCookies:
        """测试设置 Cookies"""

        def test_set_cookies(self, client):
            """测试设置 cookies"""
            # Arrange
            from requests.cookies import RequestsCookieJar
            client.session.cookies = RequestsCookieJar()
            cookies = {'session': 'abc123', 'token': 'xyz'}

            # Act
            client.set_cookies(cookies)

            # Assert
            assert client.session.cookies.get('session') == 'abc123'
            assert client.session.cookies.get('token') == 'xyz'

    class TestGetCookies:
        """测试获取 Cookies"""

        def test_get_cookies(self, client):
            """测试获取 cookies"""
            # Arrange
            from requests.cookies import RequestsCookieJar
            client.session.cookies = RequestsCookieJar()
            client.session.cookies.set('session', 'abc123')
            client.session.cookies.set('token', 'xyz')

            # Act
            result = client.get_cookies()

            # Assert
            assert 'session' in result
            assert result['session'] == 'abc123'
            assert 'token' in result
            assert result['token'] == 'xyz'

    class TestGetCurrentUserV8:
        """测试获取当前用户信息 (禅道 8.x)"""

        def test_get_current_user_success(self, client):
            """测试成功获取当前用户信息"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.url = 'http://test.zentao.com/my-index.html'
            client.session.get.return_value = mock_response

            # Act
            result = client._get_current_user_v8()

            # Assert
            assert result is not None
            assert result['account'] == 'current_user'

        def test_get_current_user_from_ajax(self, client):
            """测试从 AJAX 接口获取用户信息"""
            # Arrange
            mock_response_index = Mock()
            mock_response_index.status_code = 302
            mock_response_index.url = 'http://test.zentao.com/user-login.html'

            mock_response_ajax = Mock()
            mock_response_ajax.status_code = 200
            mock_response_ajax.json.return_value = {
                'status': 'success',
                'user': {'id': 1, 'account': 'testuser', 'realname': '测试用户'}
            }

            def side_effect(*args, **kwargs):
                if 'my-index' in args[0]:
                    return mock_response_index
                else:
                    return mock_response_ajax

            client.session.get.side_effect = side_effect

            # Act
            result = client._get_current_user_v8()

            # Assert
            assert result is not None
            assert result['account'] == 'testuser'

        def test_get_current_user_exception(self, client):
            """测试获取用户信息时发生异常"""
            # Arrange
            client.session.get.side_effect = Exception("网络错误")

            # Act
            result = client._get_current_user_v8()

            # Assert
            assert result is None

    class TestGetTaskDetail:
        """测试获取任务详情 (内部方法)"""

        def test_get_task_detail_success(self, client):
            """测试成功获取任务详情"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'status': 'success',
                'data': json.dumps({
                    'task': {
                        'id': 123,
                        'openedDate': '2024-01-15 10:00:00',
                        'deadline': '2024-01-20',
                        'status': 'doing'
                    }
                })
            }
            client.session.get.return_value = mock_response

            # Act
            result = client._get_task_detail(123)

            # Assert
            assert result is not None
            assert result['created_at'] == '2024-01-15 10:00:00'
            assert result['deadline'] == '2024-01-20'
            assert result['status'] == 'doing'

        def test_get_task_detail_not_found(self, client):
            """测试任务不存在"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 404
            client.session.get.return_value = mock_response

            # Act
            result = client._get_task_detail(999)

            # Assert
            assert result is None

        def test_get_task_detail_invalid_json(self, client):
            """测试返回无效 JSON"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'status': 'success',
                'data': 'invalid json'
            }
            client.session.get.return_value = mock_response

            # Act
            result = client._get_task_detail(123)

            # Assert
            assert result is None

    class TestGetTaskDetailFull:
        """测试获取任务完整详情"""

        def test_get_task_detail_full_success(self, client):
            """测试成功获取任务详情"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'status': 'success',
                'data': json.dumps({
                    'task': {
                        'id': 123,
                        'name': '测试任务',
                        'status': 'doing',
                        'project': 10
                    }
                })
            }
            client.session.get.return_value = mock_response

            # Act
            result = client._get_task_detail_full(123)

            # Assert
            assert result is not None
            assert result['id'] == 123
            assert result['name'] == '测试任务'

        def test_get_task_detail_full_not_found(self, client):
            """测试任务不存在"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 404
            client.session.get.return_value = mock_response

            # Act
            result = client._get_task_detail_full(999)

            # Assert
            assert result is None

        def test_get_task_detail_full_invalid_response(self, client):
            """测试无效响应"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'status': 'error',
                'message': '任务不存在'
            }
            client.session.get.return_value = mock_response

            # Act
            result = client._get_task_detail_full(123)

            # Assert
            assert result is None

        def test_get_task_detail_full_no_task_key(self, client):
            """测试响应缺少 task 键"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'status': 'success',
                'data': json.dumps({
                    'other_key': 'value'
                })
            }
            client.session.get.return_value = mock_response

            # Act
            result = client._get_task_detail_full(123)

            # Assert
            assert result is None

        def test_get_task_detail_full_invalid_json(self, client):
            """测试 JSON 解析错误"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'status': 'success',
                'data': 'invalid json'
            }
            client.session.get.return_value = mock_response

            # Act
            result = client._get_task_detail_full(123)

            # Assert
            assert result is None

    class TestParseTaskSelectHtml:
        """测试解析任务选择框 HTML"""

        def test_parse_task_select_html_success(self, client):
            """测试成功解析 HTML"""
            # Arrange
            html = """
            <select>
                <option value='1'>项目A / 任务1</option>
                <option value='2'>项目B / 任务2</option>
                <option value='3'>任务3</option>
            </select>
            """

            # Act
            result = client._parse_task_select_html(html)

            # Assert
            assert len(result) == 3
            assert result[0]['id'] == 1
            assert result[0]['name'] == '任务1'
            assert result[0]['project_name'] == '项目A'
            assert result[1]['id'] == 2
            assert result[1]['name'] == '任务2'
            assert result[2]['id'] == 3
            assert result[2]['name'] == '任务3'
            assert result[2]['project_name'] == ''

        def test_parse_task_select_html_empty(self, client):
            """测试空 HTML"""
            # Arrange
            html = "<select></select>"

            # Act
            result = client._parse_task_select_html(html)

            # Assert
            assert len(result) == 0

        def test_parse_task_select_html_html_entities(self, client):
            """测试 HTML 实体解码"""
            # Arrange
            html = "<option value='1'>&lt;测试&gt; / 任务&amp;1</option>"

            # Act
            result = client._parse_task_select_html(html)

            # Assert
            assert len(result) == 1
            assert result[0]['name'] == '任务&1'
            assert result[0]['project_name'] == '<测试>'

    class TestGetStoryTaskCount:
        """测试获取需求任务数量"""

        def test_get_story_task_count_success(self, client):
            """测试成功获取任务数量"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'status': 'success',
                'data': json.dumps({
                    'story': {
                        'id': 123,
                        'title': '测试需求',
                        'tasks': {
                            '10': [
                                {'id': 1, 'name': '任务1', 'deleted': '0'},
                                {'id': 2, 'name': '任务2', 'deleted': '0'}
                            ]
                        }
                    }
                })
            }
            client.session.get.return_value = mock_response

            # Act
            result = client.get_story_task_count(123)

            # Assert
            assert result == 2

        def test_get_story_task_count_empty(self, client):
            """测试无任务的情况"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'status': 'success',
                'data': json.dumps({
                    'story': {
                        'id': 123,
                        'title': '测试需求',
                        'tasks': {}
                    }
                })
            }
            client.session.get.return_value = mock_response

            # Act
            result = client.get_story_task_count(123)

            # Assert
            assert result == 0

        def test_get_story_task_count_api_error(self, client):
            """测试 API 错误"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 500
            client.session.get.return_value = mock_response

            # Act
            result = client.get_story_task_count(123)

            # Assert
            assert result == 0

        def test_get_story_task_count_invalid_response(self, client):
            """测试无效响应"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'status': 'success',
                'data': 'invalid json'
            }
            client.session.get.return_value = mock_response

            # Act
            result = client.get_story_task_count(123)

            # Assert
            assert result == 0

        def test_get_story_task_count_list_format(self, client):
            """测试任务列表格式"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'status': 'success',
                'data': json.dumps({
                    'story': {
                        'id': 123,
                        'title': '测试需求',
                        'tasks': [
                            {'id': 1, 'name': '任务1', 'deleted': '0'},
                            {'id': 2, 'name': '任务2', 'deleted': '0'},
                            {'id': 3, 'name': '任务3', 'deleted': '1'}  # 已删除
                        ]
                    }
                })
            }
            client.session.get.return_value = mock_response

            # Act
            result = client.get_story_task_count(123)

            # Assert
            assert result == 2  # 只计算未删除的任务

        def test_get_story_task_count_deleted_tasks(self, client):
            """测试过滤已删除任务"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'status': 'success',
                'data': json.dumps({
                    'story': {
                        'id': 123,
                        'title': '测试需求',
                        'tasks': {
                            '10': [
                                {'id': 1, 'name': '任务1', 'deleted': '0'},
                                {'id': 2, 'name': '任务2', 'deleted': '1'},  # 已删除
                                {'id': 3, 'name': '任务3', 'deleted': 1}     # 已删除(数字)
                            ]
                        }
                    }
                })
            }
            client.session.get.return_value = mock_response

            # Act
            result = client.get_story_task_count(123)

            # Assert
            assert result == 1  # 只计算未删除的任务

    class TestSplitTask:
        """测试任务拆解"""

        def test_split_task_success(self, client):
            """测试成功拆解任务"""
            # Arrange
            with patch.object(client, '_get_task_detail_full') as mock_get_parent:
                mock_get_parent.return_value = {
                    'id': 100,
                    'name': '父任务',
                    'project': 10
                }

                with patch.object(client, 'create_task') as mock_create:
                    def create_side_effect(*args, **kwargs):
                        # 模拟创建任务，返回递增的ID
                        task_name = kwargs.get('name', '')
                        if '子任务1' in task_name:
                            return ApiResponse.success_response({'id': 101})
                        elif '子任务2' in task_name:
                            return ApiResponse.success_response({'id': 102})
                        else:
                            return ApiResponse.success_response({'id': 103})

                    mock_create.side_effect = create_side_effect

                    # Act
                    result = client.split_task(100, ['子任务1', '子任务2', '子任务3'])

                    # Assert
                    assert result is not None
                    assert result.success is True
                    assert result.data['parent_task_id'] == 100
                    assert result.data['success_count'] == 3
                    assert result.data['fail_count'] == 0
                    assert len(result.data['created_tasks']) == 3

        def test_split_task_parent_not_found(self, client):
            """测试父任务不存在"""
            # Arrange
            with patch.object(client, '_get_task_detail_full') as mock_get_parent:
                mock_get_parent.return_value = None

                # Act
                result = client.split_task(999, ['子任务1', '子任务2'])

                # Assert
                assert result is not None
                assert result.success is False
                assert result.error.code == ErrorCode.TASK_NOT_FOUND

        def test_split_task_no_project(self, client):
            """测试父任务没有项目信息"""
            # Arrange
            with patch.object(client, '_get_task_detail_full') as mock_get_parent:
                mock_get_parent.return_value = {
                    'id': 100,
                    'name': '父任务'
                    # 缺少 project 字段
                }

                # Act
                result = client.split_task(100, ['子任务1'])

                # Assert
                assert result is not None
                assert result.success is False
                assert result.error.code == ErrorCode.API_ERROR

        def test_split_task_partial_failure(self, client):
            """测试部分子任务创建失败"""
            # Arrange
            with patch.object(client, '_get_task_detail_full') as mock_get_parent:
                mock_get_parent.return_value = {
                    'id': 100,
                    'name': '父任务',
                    'project': 10
                }

                with patch.object(client, 'create_task') as mock_create:
                    def create_side_effect(*args, **kwargs):
                        task_name = kwargs.get('name', '')
                        if '成功' in task_name:
                            return ApiResponse.success_response({'id': 101})
                        else:
                            return ApiResponse.error_response(
                                ErrorCode.API_ERROR,
                                '创建失败'
                            )

                    mock_create.side_effect = create_side_effect

                    # Act
                    result = client.split_task(100, ['成功任务1', '失败任务', '成功任务2'])

                    # Assert
                    assert result is not None
                    assert result.success is True
                    assert result.data['success_count'] == 2
                    assert result.data['fail_count'] == 1
                    assert len(result.data['created_tasks']) == 2
                    assert len(result.data['failed_tasks']) == 1

        def test_split_task_all_failed(self, client):
            """测试所有子任务创建失败"""
            # Arrange
            with patch.object(client, '_get_task_detail_full') as mock_get_parent:
                mock_get_parent.return_value = {
                    'id': 100,
                    'name': '父任务',
                    'project': 10
                }

                with patch.object(client, 'create_task') as mock_create:
                    mock_create.return_value = ApiResponse.error_response(
                        ErrorCode.API_ERROR,
                        '创建失败'
                    )

                    # Act
                    result = client.split_task(100, ['子任务1', '子任务2'])

                    # Assert
                    assert result is not None
                    assert result.success is True  # 方法本身成功执行
                    assert result.data['success_count'] == 0
                    assert result.data['fail_count'] == 2
                    assert len(result.data['created_tasks']) == 0
                    assert len(result.data['failed_tasks']) == 2

        def test_split_task_exception(self, client):
            """测试异常处理"""
            # Arrange
            with patch.object(client, '_get_task_detail_full') as mock_get_parent:
                mock_get_parent.side_effect = Exception("网络错误")

                # Act
                result = client.split_task(100, ['子任务1'])

                # Assert
                assert result is not None
                assert result.success is False
                assert result.error.code == ErrorCode.API_ERROR
                assert '任务拆解失败' in result.error.message

    class TestAssignTask:
        """测试任务分配"""

        def test_assign_task_success(self, client):
            """测试成功分配任务"""
            # Arrange
            with patch.object(client, '_get_task_detail_full') as mock_get_task:
                mock_get_task.return_value = {
                    'id': 100,
                    'name': '测试任务',
                    'project': 10
                }

                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.url = 'http://test.zentao.com/task-view-100.html'
                client.session.post.return_value = mock_response

                # Act
                result = client.assign_task(100, 'user1')

                # Assert
                assert result is not None
                assert result.success is True
                assert result.data['assigned_to'] == 'user1'

        def test_assign_task_to_execution_url(self, client):
            """测试分配到执行页面"""
            # Arrange
            with patch.object(client, '_get_task_detail_full') as mock_get_task:
                mock_get_task.return_value = {
                    'id': 100,
                    'name': '测试任务',
                    'project': 10
                }

                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.url = 'http://test.zentao.com/execution-task-10.html'
                client.session.post.return_value = mock_response

                # Act
                result = client.assign_task(100, 'user2')

                # Assert
                assert result is not None
                assert result.success is True

        def test_assign_task_not_found(self, client):
            """测试任务不存在"""
            # Arrange
            with patch.object(client, '_get_task_detail_full') as mock_get_task:
                mock_get_task.return_value = None

                # Act
                result = client.assign_task(999, 'user1')

                # Assert
                assert result is not None
                assert result.success is False
                assert result.error.code == ErrorCode.TASK_NOT_FOUND

        def test_assign_task_no_project(self, client):
            """测试任务没有项目信息"""
            # Arrange
            with patch.object(client, '_get_task_detail_full') as mock_get_task:
                mock_get_task.return_value = {
                    'id': 100,
                    'name': '测试任务'
                    # 缺少 project 字段
                }

                # Act
                result = client.assign_task(100, 'user1')

                # Assert
                assert result is not None
                assert result.success is False
                assert result.error.code == ErrorCode.API_ERROR

        def test_assign_task_failure(self, client):
            """测试分配失败（URL不匹配）"""
            # Arrange
            with patch.object(client, '_get_task_detail_full') as mock_get_task:
                mock_get_task.return_value = {
                    'id': 100,
                    'name': '测试任务',
                    'project': 10
                }

                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.url = 'http://test.zentao.com/some-other-page.html'
                client.session.post.return_value = mock_response

                # Act
                result = client.assign_task(100, 'user1')

                # Assert
                assert result is not None
                assert result.success is False

        def test_assign_task_http_error(self, client):
            """测试 HTTP 错误"""
            # Arrange
            with patch.object(client, '_get_task_detail_full') as mock_get_task:
                mock_get_task.return_value = {
                    'id': 100,
                    'name': '测试任务',
                    'project': 10
                }

                mock_response = Mock()
                mock_response.status_code = 500
                client.session.post.return_value = mock_response

                # Act
                result = client.assign_task(100, 'user1')

                # Assert
                assert result is not None
                assert result.success is False

        def test_assign_task_timeout(self, client):
            """测试超时"""
            # Arrange
            import requests
            with patch.object(client, '_get_task_detail_full') as mock_get_task:
                mock_get_task.return_value = {
                    'id': 100,
                    'name': '测试任务',
                    'project': 10
                }

                client.session.post.side_effect = requests.Timeout("连接超时")

                # Act
                result = client.assign_task(100, 'user1')

                # Assert
                assert result is not None
                assert result.success is False
                assert result.error.code == ErrorCode.TIMEOUT

    class TestGetExecutions:
        """测试获取执行/项目列表"""

        def test_get_executions_list_format(self, client):
            """测试列表格式的项目数据"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'status': 'success',
                'data': json.dumps({
                    'projects': [
                        {'id': 1, 'name': '项目1', 'status': 'doing', 'begin': '2024-01-01', 'end': '2024-12-31'},
                        {'id': 2, 'name': '项目2', 'status': 'wait', 'begin': '2024-02-01', 'end': '2024-11-30'},
                        {'id': 3, 'name': '已完成项目', 'status': 'done', 'begin': '2023-01-01', 'end': '2023-12-31'},
                        {'id': 4, 'name': '已关闭项目', 'status': 'closed', 'begin': '2023-01-01', 'end': '2023-12-31'}
                    ]
                })
            }
            client.session.get.return_value = mock_response

            # Act
            result = client.get_executions()

            # Assert
            assert result is not None
            assert result.success is True
            assert len(result.data) == 2  # 只返回未完成的
            assert result.data[0]['id'] == 1
            assert result.data[1]['id'] == 2

        def test_get_executions_dict_format(self, client):
            """测试字典格式的项目数据"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'status': 'success',
                'data': json.dumps({
                    'projects': {
                        '1': {'id': 1, 'name': '项目1', 'status': 'doing'},
                        '2': {'id': 2, 'name': '项目2', 'status': 'wait'}
                    }
                })
            }
            client.session.get.return_value = mock_response

            # Act
            result = client.get_executions()

            # Assert
            assert result is not None
            assert result.success is True
            assert len(result.data) == 2

        def test_get_executions_single_project(self, client):
            """测试单个项目字典格式"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'status': 'success',
                'data': json.dumps({
                    'id': 1,
                    'name': '单个项目',
                    'status': 'doing'
                })
            }
            client.session.get.return_value = mock_response

            # Act
            result = client.get_executions()

            # Assert
            assert result is not None
            assert result.success is True
            assert len(result.data) == 1
            assert result.data[0]['name'] == '单个项目'

        def test_get_executions_string_values(self, client):
            """测试字符串值格式的项目数据"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'status': 'success',
                'data': json.dumps({
                    '1': '项目1',
                    '2': '项目2',
                    'abc': '无效项目'  # 应该被跳过
                })
            }
            client.session.get.return_value = mock_response

            # Act
            result = client.get_executions()

            # Assert
            assert result is not None
            assert result.success is True
            assert len(result.data) == 2

        def test_get_executions_http_error(self, client):
            """测试 HTTP 错误"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 500
            client.session.get.return_value = mock_response

            # Act
            result = client.get_executions()

            # Assert
            assert result is not None
            assert result.success is False

        def test_get_executions_api_error(self, client):
            """测试 API 返回错误状态"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'status': 'error',
                'message': '权限不足'
            }
            client.session.get.return_value = mock_response

            # Act
            result = client.get_executions()

            # Assert
            assert result is not None
            assert result.success is False

        def test_get_executions_parse_error(self, client):
            """测试 JSON 解析错误"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'status': 'success',
                'data': 'invalid json'
            }
            client.session.get.return_value = mock_response

            # Act
            result = client.get_executions()

            # Assert
            assert result is not None
            assert result.success is False

    class TestGetMyStoriesFallback:
        """测试获取需求列表（备用方法）"""

        def test_get_my_stories_fallback_success(self, client):
            """测试成功获取需求列表"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'status': 'success',
                'data': json.dumps({
                    'stories': [
                        {
                            'id': 1,
                            'title': '需求1',
                            'status': 'active',
                            'pri': 1,
                            'assignedTo': 'user1',
                            'openedBy': 'admin',
                            'openedDate': '2024-01-01',
                            'productTitle': '产品A',
                            'planTitle': '计划1',
                            'stage': 'developing',
                            'estimate': 8
                        },
                        {
                            'id': 2,
                            'title': '需求2',
                            'status': 'draft',
                            'pri': 2,
                            'assignedTo': 'user2',
                            'openedBy': 'admin',
                            'openedDate': '2024-01-02',
                            'productTitle': '产品B',
                            'planTitle': '计划2',
                            'stage': 'wait',
                            'estimate': 4
                        }
                    ]
                })
            }
            client.session.get.return_value = mock_response

            # Act
            result = client._get_my_stories_fallback()

            # Assert
            assert result is not None
            assert result.success is True
            assert len(result.data['stories']) == 2
            assert result.data['total'] == 2

        def test_get_my_stories_fallback_with_status(self, client):
            """测试带状态过滤"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'status': 'success',
                'data': json.dumps({
                    'stories': [
                        {'id': 1, 'title': '需求1', 'status': 'active'}
                    ]
                })
            }
            client.session.get.return_value = mock_response

            # Act
            result = client._get_my_stories_fallback(status='active')

            # Assert
            assert result is not None
            assert result.success is True
            # 验证 params 被正确设置
            call_args = client.session.get.call_args
            assert call_args[1]['params'] == {'status': 'active'}

        def test_get_my_stories_fallback_empty(self, client):
            """测试空需求列表"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'status': 'success',
                'data': json.dumps({
                    'stories': []
                })
            }
            client.session.get.return_value = mock_response

            # Act
            result = client._get_my_stories_fallback()

            # Assert
            assert result is not None
            assert result.success is True
            assert len(result.data['stories']) == 0
            assert result.data['total'] == 0

        def test_get_my_stories_fallback_http_error(self, client):
            """测试 HTTP 错误"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 500
            client.session.get.return_value = mock_response

            # Act
            result = client._get_my_stories_fallback()

            # Assert
            assert result is not None
            assert result.success is False

        def test_get_my_stories_fallback_api_error(self, client):
            """测试 API 返回错误状态"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'status': 'error',
                'message': '权限不足'
            }
            client.session.get.return_value = mock_response

            # Act
            result = client._get_my_stories_fallback()

            # Assert
            assert result is not None
            assert result.success is False

        def test_get_my_stories_fallback_parse_error(self, client):
            """测试 JSON 解析错误"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'status': 'success',
                'data': 'invalid json'
            }
            client.session.get.return_value = mock_response

            # Act
            result = client._get_my_stories_fallback()

            # Assert
            assert result is not None
            assert result.success is False

    class TestGetMyTasks:
        """测试获取指派给我的任务"""

        def test_get_my_tasks_success(self, client):
            """测试成功获取任务列表"""
            # Arrange
            html_response = """
            <select>
                <option value='1'>项目A / 任务1</option>
                <option value='2'>项目B / 任务2</option>
            </select>
            """

            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = html_response
            client.session.get.return_value = mock_response

            with patch.object(client, '_get_task_detail') as mock_get_detail:
                mock_get_detail.side_effect = [
                    {'created_at': '2024-01-01', 'deadline': '2024-01-10', 'status': 'doing'},
                    {'created_at': '2024-01-02', 'deadline': '2024-01-15', 'status': 'wait'}
                ]

                # Act
                result = client.get_my_tasks()

                # Assert
                assert result is not None
                assert result.success is True
                assert len(result.data['tasks']) == 2
                assert result.data['total'] == 2

        def test_get_my_tasks_with_status(self, client):
            """测试带状态过滤"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = '<select></select>'
            client.session.get.return_value = mock_response

            # Act
            result = client.get_my_tasks(status='doing')

            # Assert
            assert result is not None
            assert result.success is True
            # 验证 URL 中包含状态参数
            call_args = client.session.get.call_args
            assert 'doing' in call_args[0][0]

        def test_get_my_tasks_http_error(self, client):
            """测试 HTTP 错误"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 500
            client.session.get.return_value = mock_response

            # Act
            result = client.get_my_tasks()

            # Assert
            assert result is not None
            assert result.success is False

        def test_get_my_tasks_timeout(self, client):
            """测试超时"""
            # Arrange
            import requests
            client.session.get.side_effect = requests.Timeout("连接超时")

            # Act
            result = client.get_my_tasks()

            # Assert
            assert result is not None
            assert result.success is False
            assert result.error.code == ErrorCode.TIMEOUT


    class TestGetStoryDetailMinimal:
        """测试获取需求最小化详情"""

        def test_get_story_detail_minimal_success(self, client):
            """测试成功获取需求最小化详情"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'status': 'success',
                'data': json.dumps({
                    'story': {
                        'id': 123,
                        'title': '测试需求',
                        'status': 'active',
                        'pri': 1,
                        'assignedTo': 'user1',
                        'openedBy': 'admin',
                        'openedDate': '2024-01-01',
                        'productTitle': '产品A',
                        'planTitle': '计划1',
                        'stage': 'developing',
                        'estimate': 8
                    }
                })
            }
            client.session.get.return_value = mock_response

            # Act
            result = client._get_story_detail_minimal(123)

            # Assert
            assert result is not None
            assert result['id'] == 123
            assert result['title'] == '测试需求'

        def test_get_story_detail_minimal_not_found(self, client):
            """测试需求不存在"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 404
            client.session.get.return_value = mock_response

            # Act
            result = client._get_story_detail_minimal(999)

            # Assert
            assert result is None

        def test_get_story_detail_minimal_error_response(self, client):
            """测试错误响应"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'status': 'error',
                'message': '需求不存在'
            }
            client.session.get.return_value = mock_response

            # Act
            result = client._get_story_detail_minimal(123)

            # Assert
            assert result is None

        def test_get_story_detail_minimal_no_story_key(self, client):
            """测试响应缺少 story 键"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'status': 'success',
                'data': json.dumps({
                    'other_key': 'value'
                })
            }
            client.session.get.return_value = mock_response

            # Act
            result = client._get_story_detail_minimal(123)

            # Assert
            assert result is None

        def test_get_story_detail_minimal_invalid_json(self, client):
            """测试 JSON 解析错误"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'status': 'success',
                'data': 'invalid json'
            }
            client.session.get.return_value = mock_response

            # Act
            result = client._get_story_detail_minimal(123)

            # Assert
            assert result is None

    class TestReviewStoryMoreBranches:
        """测试评审需求的更多分支"""

        def test_review_story_already_reviewed(self, client):
            """测试需求已评审（通过JSON解析判断）"""
            # Arrange
            with patch.object(client, 'get_story') as mock_get_story:
                mock_get_story.return_value = ApiResponse.success_response({
                    'id': 123,
                    'status': 'changed',
                    'assigned_to': 'user1',
                    'estimate': 8
                })

                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.text = '<html>Some content</html>'
                # JSON解析失败，但包含成功标记
                mock_response.json.side_effect = ValueError("Invalid JSON")
                client.session.post.return_value = mock_response

                # Act
                result = client.review_story(123, result='pass')

                # Assert
                assert result is not None
                assert result.success is True

        def test_review_story_timeout(self, client):
            """测试评审需求超时"""
            # Arrange
            import requests
            with patch.object(client, 'get_story') as mock_get_story:
                mock_get_story.return_value = ApiResponse.success_response({
                    'id': 123,
                    'status': 'changed',
                    'assigned_to': 'user1',
                    'estimate': 8
                })

                client.session.post.side_effect = requests.Timeout("连接超时")

                # Act
                result = client.review_story(123, result='pass')

                # Assert
                assert result is not None
                assert result.success is False
                assert result.error.code == ErrorCode.TIMEOUT

        def test_review_story_exception(self, client):
            """测试评审需求异常"""
            # Arrange
            with patch.object(client, 'get_story') as mock_get_story:
                mock_get_story.return_value = ApiResponse.success_response({
                    'id': 123,
                    'status': 'changed',
                    'assigned_to': 'user1',
                    'estimate': 8
                })

                client.session.post.side_effect = Exception("网络错误")

                # Act
                result = client.review_story(123, result='pass')

                # Assert
                assert result is not None
                assert result.success is False
                assert result.error.code == ErrorCode.API_ERROR

    class TestGetMyStoriesPagination:
        """测试获取需求列表的分页逻辑"""

        def test_get_my_stories_pagination_multiple_pages(self, client):
            """测试多页数据获取"""
            # Arrange
            responses = []
            for page in range(1, 4):
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    'status': 'success',
                    'data': json.dumps({
                        'stories': [
                            {'id': page * 10 + i, 'title': f'需求{page}-{i}', 'status': 'active'}
                            for i in range(5)
                        ]
                    })
                }
                responses.append(mock_response)

            # 最后一页返回空列表
            last_response = Mock()
            last_response.status_code = 200
            last_response.json.return_value = {
                'status': 'success',
                'data': json.dumps({'stories': []})
            }
            responses.append(last_response)

            client.session.get.side_effect = responses

            # Act
            result = client.get_my_stories()

            # Assert
            assert result is not None
            assert result.success is True
            # 应该获取了3页数据，共15个需求

        def test_get_my_stories_pagination_less_than_limit(self, client):
            """测试返回数据少于limit时停止分页"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'status': 'success',
                'data': json.dumps({
                    'stories': [
                        {'id': 1, 'title': '需求1', 'status': 'active'}
                    ]  # 只有1个，少于limit=200
                })
            }
            client.session.get.return_value = mock_response

            # Act
            result = client.get_my_stories()

            # Assert
            assert result is not None
            assert result.success is True
            # 只调用了一次API
            assert client.session.get.call_count == 1

        def test_get_my_stories_pagination_max_pages(self, client):
            """测试达到最大页数限制"""
            # Arrange
            responses = []
            for _ in range(11):  # 超过10页限制
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    'status': 'success',
                    'data': json.dumps({
                        'stories': [{'id': 1, 'title': '需求', 'status': 'active'}] * 200
                    })
                }
                responses.append(mock_response)

            client.session.get.side_effect = responses

            # Act
            result = client.get_my_stories()

            # Assert
            assert result is not None
            assert result.success is True
            # 应该最多调用10次
            assert client.session.get.call_count == 10

        def test_get_my_stories_parse_error_in_loop(self, client):
            """测试分页过程中解析错误"""
            # Arrange
            mock_response1 = Mock()
            mock_response1.status_code = 200
            mock_response1.json.return_value = {
                'status': 'success',
                'data': json.dumps({
                    'stories': [{'id': 1, 'title': '需求1', 'status': 'active'}]
                })
            }

            mock_response2 = Mock()
            mock_response2.status_code = 200
            mock_response2.json.return_value = {
                'status': 'success',
                'data': 'invalid json'  # 解析错误
            }

            client.session.get.side_effect = [mock_response1, mock_response2]

            # Act
            result = client.get_my_stories()

            # Assert
            assert result is not None
            assert result.success is True  # 返回已获取的数据

    class TestGetStoryMoreBranches:
        """测试获取需求详情的更多分支"""

        def test_get_story_no_executions(self, client):
            """测试需求没有executions字段"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'status': 'success',
                'data': json.dumps({
                    'story': {
                        'id': 50,
                        'title': '测试需求',
                        'status': 'active',
                        'spec': '需求描述',
                        'pri': 1,
                        'assignedTo': 'user1',
                        'openedBy': 'admin',
                        'openedDate': '2024-01-01',
                        'productTitle': '产品A',
                        'product': 10,
                        'stage': 'developing',
                        'estimate': 16
                        # 缺少 executions 字段
                    }
                })
            }
            client.session.get.return_value = mock_response

            # Act
            result = client.get_story(50)

            # Assert
            assert result is not None
            assert result.success is True
            assert result.data['execution'] == 0  # 默认值为0

    class TestUpdateStoryTitleMoreBranches:
        """测试更新需求标题的更多分支"""

        def test_update_story_title_exception(self, client):
            """测试更新需求标题时发生异常"""
            # Arrange
            with patch.object(client, 'get_story') as mock_get_story:
                mock_get_story.return_value = ApiResponse.success_response({
                    'id': 123,
                    'title': '旧标题',
                    'content': '需求内容',
                    'product_id': 10
                })

                client.session.post.side_effect = Exception("网络错误")

                # Act
                result = client.update_story_title(123, '【A】新标题')

                # Assert
                assert result is not None
                assert result.success is False

    class TestCreateTaskMoreBranches:
        """测试创建任务的更多分支"""

        def test_create_task_exception(self, client):
            """测试创建任务时发生异常"""
            # Arrange
            client.session.post.side_effect = Exception("网络错误")

            # Act
            result = client.create_task(
                execution_id=10,
                name='测试任务'
            )

            # Assert
            assert result is not None
            assert result.success is False

    class TestAssignTaskMoreBranches:
        """测试任务分配的更多分支"""

        def test_assign_task_exception(self, client):
            """测试分配任务时发生异常"""
            # Arrange
            with patch.object(client, '_get_task_detail_full') as mock_get_task:
                mock_get_task.return_value = {
                    'id': 100,
                    'name': '测试任务',
                    'project': 10
                }

                client.session.post.side_effect = Exception("网络错误")

                # Act
                result = client.assign_task(100, 'user1')

                # Assert
                assert result is not None
                assert result.success is False

    class TestGetExecutionsMoreBranches:
        """测试获取执行列表的更多分支"""

        def test_get_executions_exception(self, client):
            """测试获取执行列表时发生异常"""
            # Arrange
            client.session.get.side_effect = Exception("网络错误")

            # Act
            result = client.get_executions()

            # Assert
            assert result is not None
            assert result.success is False

    class TestGetMyStoriesFallbackMoreBranches:
        """测试获取需求列表备用方法的更多分支"""

        def test_get_my_stories_fallback_exception(self, client):
            """测试获取需求列表时发生异常"""
            # Arrange
            client.session.get.side_effect = Exception("网络错误")

            # Act
            result = client._get_my_stories_fallback()

            # Assert
            assert result is not None
            assert result.success is False

    class TestGetMyTasksMoreBranches:
        """测试获取任务列表的更多分支"""

        def test_get_my_tasks_exception(self, client):
            """测试获取任务列表时发生异常"""
            # Arrange
            client.session.get.side_effect = Exception("网络错误")

            # Act
            result = client.get_my_tasks()

            # Assert
            assert result is not None
            assert result.success is False

    class TestLinkStoryToExecution:
        """测试将需求关联到执行/项目"""

        def test_link_story_to_execution_success(self, client):
            """测试成功关联需求到执行/项目"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'status': 'success',
                'data': {'id': 123}
            }
            client.session.post.return_value = mock_response

            # Act
            result = client.link_story_to_execution(123, 456)

            # Assert
            assert result is not None
            assert result.success is True
            assert result.data['story_id'] == 123
            assert result.data['execution_id'] == 456

        def test_link_story_to_execution_html_response_success(self, client):
            """测试返回HTML响应（无错误关键词）- 应视为成功"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.side_effect = json.JSONDecodeError("test", "", 0)
            mock_response.text = '<html>linkStory redirect</html>'
            client.session.post.return_value = mock_response

            # Act
            result = client.link_story_to_execution(123, 456)

            # Assert
            assert result is not None
            assert result.success is True

        def test_link_story_to_execution_html_response_with_error(self, client):
            """测试返回HTML响应（包含错误关键词）- 应视为失败"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.side_effect = json.JSONDecodeError("test", "", 0)
            mock_response.text = '<html>error permission denied</html>'
            client.session.post.return_value = mock_response

            # Act
            result = client.link_story_to_execution(123, 456)

            # Assert
            assert result is not None
            assert result.success is False

        def test_link_story_to_execution_failure(self, client):
            """测试关联失败"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'status': 'error',
                'message': '需求已关联'
            }
            client.session.post.return_value = mock_response

            # Act
            result = client.link_story_to_execution(123, 456)

            # Assert
            assert result is not None
            assert result.success is False

        def test_link_story_to_execution_http_error(self, client):
            """测试HTTP错误"""
            # Arrange
            mock_response = Mock()
            mock_response.status_code = 500
            client.session.post.return_value = mock_response

            # Act
            result = client.link_story_to_execution(123, 456)

            # Assert
            assert result is not None
            assert result.success is False

        def test_link_story_to_execution_timeout(self, client):
            """测试超时"""
            # Arrange
            client.session.post.side_effect = requests.Timeout("请求超时")

            # Act
            result = client.link_story_to_execution(123, 456)

            # Assert
            assert result is not None
            assert result.success is False
            assert result.error.code == ErrorCode.TIMEOUT

        def test_link_story_to_execution_exception(self, client):
            """测试异常"""
            # Arrange
            client.session.post.side_effect = Exception("网络错误")

            # Act
            result = client.link_story_to_execution(123, 456)

            # Assert
            assert result is not None
            assert result.success is False


class TestErrorResponse:
    """测试错误响应"""

    def test_error_code_values(self):
        """测试错误码值"""
        assert ErrorCode.API_ERROR == "API_ERROR"
        assert ErrorCode.TIMEOUT == "TIMEOUT"
        assert ErrorCode.STORY_NOT_FOUND == "STORY_NOT_FOUND"
        assert ErrorCode.TASK_NOT_FOUND == "TASK_NOT_FOUND"
