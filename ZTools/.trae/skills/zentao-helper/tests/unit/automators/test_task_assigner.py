# -*- coding: utf-8 -*-
"""
测试任务分配器
"""

import pytest
from unittest.mock import Mock, patch

from src.automators.task_assigner import TaskAssigner
from src.utils.response import ApiResponse, ErrorCode


class TestTaskAssigner:
    """测试任务分配器"""

    @pytest.fixture
    def mock_api_client(self):
        """创建 Mock API 客户端"""
        return Mock()

    @pytest.fixture
    def assigner(self, mock_api_client):
        """创建分配器实例"""
        return TaskAssigner(mock_api_client)

    class TestExecute:
        """测试执行方法"""

        def test_execute_missing_task_id(self, assigner):
            """测试缺少任务 ID"""
            # Act
            result = assigner.execute(task_id=None, username="user1")

            # Assert
            assert result.success is False
            assert result.error.code == ErrorCode.MISSING_PARAMETER
            assert "任务ID" in result.error.message

        def test_execute_task_not_found(self, assigner, mock_api_client):
            """测试任务不存在"""
            # Arrange
            mock_api_client.get_task.return_value = ApiResponse.error_response(
                ErrorCode.TASK_NOT_FOUND,
                "任务不存在"
            )

            # Act
            result = assigner.execute(task_id="123", username="user1")

            # Assert
            assert result.success is False
            assert result.error.code == ErrorCode.TASK_NOT_FOUND

        def test_execute_success(self, assigner, mock_api_client):
            """测试成功分配"""
            # Arrange
            mock_api_client.get_task.return_value = ApiResponse.success_response({
                "id": 123,
                "name": "测试任务"
            })
            mock_api_client.search_user.return_value = ApiResponse.success_response([
                {"account": "user1", "realname": "用户一"}
            ])
            mock_api_client.assign_task.return_value = ApiResponse.success_response({
                "result": "success"
            })

            # Act
            result = assigner.execute(task_id="123", username="user1")

            # Assert
            assert result.success is True

    class TestInteractiveInputUsername:
        """测试交互式输入用户名"""

        def test_interactive_input_username_success(self, assigner):
            """测试成功交互式输入"""
            # Arrange
            with patch('builtins.input', return_value='testuser'):
                # Act
                result = assigner._interactive_input_username()

                # Assert
                assert result == 'testuser'

        def test_interactive_input_username_empty(self, assigner):
            """测试空输入"""
            # Arrange
            with patch('builtins.input', return_value='   '):
                # Act
                result = assigner._interactive_input_username()

                # Assert
                assert result is None

        def test_interactive_input_username_eof_error(self, assigner):
            """测试 EOF 错误"""
            # Arrange
            with patch('builtins.input', side_effect=EOFError()):
                # Act
                result = assigner._interactive_input_username()

                # Assert
                assert result is None

        def test_interactive_input_username_keyboard_interrupt(self, assigner):
            """测试键盘中断"""
            # Arrange
            with patch('builtins.input', side_effect=KeyboardInterrupt()):
                # Act
                result = assigner._interactive_input_username()

                # Assert
                assert result is None

    class TestExecuteWithInteractiveInput:
        """测试执行方法 - 交互式输入"""

        def test_execute_with_interactive_input(self, assigner, mock_api_client):
            """测试通过交互式输入获取用户名"""
            # Arrange
            mock_api_client.get_task.return_value = ApiResponse.success_response({
                "id": 123,
                "name": "测试任务"
            })
            mock_api_client.search_user.return_value = ApiResponse.success_response([
                {"account": "interactive_user", "realname": "交互用户"}
            ])
            mock_api_client.assign_task.return_value = ApiResponse.success_response({
                "result": "success"
            })

            with patch.object(assigner, '_interactive_input_username', return_value='interactive_user'):
                # Act
                result = assigner.execute(task_id="123", username=None)

                # Assert
                assert result.success is True
                assert result.data["assigned_to"] == "interactive_user"

        def test_execute_with_cancelled_input(self, assigner, mock_api_client):
            """测试取消交互式输入"""
            # Arrange
            with patch.object(assigner, '_interactive_input_username', return_value=None):
                # Act
                result = assigner.execute(task_id="123", username=None)

                # Assert
                assert result.success is False
                assert result.error.code == ErrorCode.MISSING_PARAMETER

    class TestPerformAssign:
        """测试执行分配"""

        def test_perform_assign_success(self, assigner, mock_api_client):
            """测试成功执行分配"""
            # Arrange
            mock_api_client.assign_task.return_value = ApiResponse.success_response({
                "result": "success"
            })
            mock_api_client.get_task.return_value = ApiResponse.success_response({
                "id": 123,
                "name": "测试任务"
            })

            # Act
            result = assigner._perform_assign(123, "user1")

            # Assert
            assert result.success is True
            assert result.data["task_id"] == 123
            assert result.data["assigned_to"] == "user1"

        def test_perform_assign_failure(self, assigner, mock_api_client):
            """测试分配失败"""
            # Arrange
            mock_api_client.assign_task.return_value = ApiResponse.error_response(
                ErrorCode.API_ERROR,
                "API错误"
            )

            # Act
            result = assigner._perform_assign(123, "user1")

            # Assert
            assert result.success is False
            assert result.error.code == ErrorCode.API_ERROR

    class TestFormatDisplay:
        """测试格式化显示"""

        def test_format_success_result(self, assigner):
            """测试格式化成功结果"""
            # Arrange
            result_data = {
                "task_id": 123,
                "assigned_to": "user1",
                "task": {
                    "name": "测试任务",
                    "status": "wait",
                    "type": "开发"
                }
            }

            # Act
            result = assigner.format_display(result_data)

            # Assert
            assert "任务分配结果" in result
            assert "#123" in result
            assert "user1" in result
            assert "测试任务" in result

        def test_format_without_task_info(self, assigner):
            """测试无任务信息的格式化"""
            # Arrange
            result_data = {
                "task_id": 123,
                "assigned_to": "user1"
            }

            # Act
            result = assigner.format_display(result_data)

            # Assert
            assert "任务分配结果" in result

    class TestExecuteExtended:
        """测试执行方法 - 扩展"""

        def test_execute_multiple_users_found(self, assigner, mock_api_client):
            """测试找到多个匹配用户"""
            # Arrange
            mock_api_client.get_task.return_value = ApiResponse.success_response({
                "id": 123,
                "name": "测试任务"
            })
            mock_api_client.search_user.return_value = ApiResponse.success_response([
                {"account": "user1", "realname": "用户一"},
                {"account": "user2", "realname": "用户二"}
            ])
            mock_api_client.assign_task.return_value = ApiResponse.success_response({
                "result": "success"
            })

            # Act
            result = assigner.execute(task_id="123", username="user")

            # Assert
            assert result.success is True
            assert result.data["assigned_to"] == "user1"  # 使用第一个匹配

        def test_execute_no_users_found(self, assigner, mock_api_client):
            """测试未找到匹配用户"""
            # Arrange
            mock_api_client.get_task.return_value = ApiResponse.success_response({
                "id": 123,
                "name": "测试任务"
            })
            mock_api_client.search_user.return_value = ApiResponse.success_response([])
            mock_api_client.assign_task.return_value = ApiResponse.success_response({
                "result": "success"
            })

            # Act
            result = assigner.execute(task_id="123", username="unknown")

            # Assert
            assert result.success is True  # 仍然尝试分配

        def test_execute_extract_username_from_input(self, assigner, mock_api_client):
            """测试从输入中提取用户名"""
            # Arrange
            mock_api_client.get_task.return_value = ApiResponse.success_response({
                "id": 123,
                "name": "测试任务"
            })
            mock_api_client.search_user.return_value = ApiResponse.success_response([
                {"account": "zhangsan", "realname": "张三"}
            ])
            mock_api_client.assign_task.return_value = ApiResponse.success_response({
                "result": "success"
            })

            # Act
            result = assigner.execute(task_id="123", username=None, user_input="分配给张三")

            # Assert
            assert result.success is True
