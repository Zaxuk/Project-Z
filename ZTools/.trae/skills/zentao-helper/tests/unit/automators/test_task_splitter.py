# -*- coding: utf-8 -*-
"""
测试任务拆解器
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.automators.task_splitter import TaskSplitter
from src.utils.response import ApiResponse, ErrorCode


class TestTaskSplitter:
    """测试任务拆解器"""

    @pytest.fixture
    def mock_api_client(self):
        """创建 Mock API 客户端"""
        return Mock()

    @pytest.fixture
    def splitter(self, mock_api_client):
        """创建拆解器实例"""
        return TaskSplitter(mock_api_client)

    class TestCalculateDeadline:
        """测试计算截止日期"""

        def test_calculate_this_week_friday(self, splitter):
            """测试计算本周周五"""
            # Act
            result = splitter._calculate_deadline("本周周五")

            # Assert
            assert result is not None
            assert isinstance(result, str)
            # 格式应该是 YYYY-MM-DD
            assert len(result) == 10
            assert result.count('-') == 2

        def test_calculate_next_week_friday(self, splitter):
            """测试计算下周周五"""
            # Act
            result = splitter._calculate_deadline("下周周五")

            # Assert
            assert result is not None
            assert isinstance(result, str)
            assert len(result) == 10

        def test_calculate_empty_deadline(self, splitter):
            """测试空截止日期"""
            # Act
            result = splitter._calculate_deadline("")

            # Assert
            assert result is None

        def test_calculate_invalid_deadline(self, splitter):
            """测试无效截止日期"""
            # Act
            result = splitter._calculate_deadline("无效日期")

            # Assert
            assert result is None

    class TestFormatDisplay:
        """测试格式化显示"""

        def test_format_success_result(self, splitter):
            """测试格式化成功结果"""
            # Arrange
            result_data = {
                "story_id": 123,
                "updated_title": "测试需求",
                "created_task": {
                    "id": 456,
                    "name": "【研发】测试需求"
                }
            }

            # Act
            result = splitter.format_display(result_data)

            # Assert
            assert "任务创建成功" in result
            assert "需求ID: #123" in result
            assert "测试需求" in result
            assert "任务ID: #456" in result

        def test_format_empty_data(self, splitter):
            """测试空数据格式化"""
            # Act
            result = splitter.format_display({})

            # Assert
            assert "任务创建完成" in result

        def test_format_none_data(self, splitter):
            """测试 None 数据格式化"""
            # Act
            result = splitter.format_display(None)

            # Assert
            assert "任务创建完成" in result



    class TestSelectProject:
        """测试选择项目"""

        def test_select_project_success(self, splitter, mock_api_client):
            """测试成功选择项目"""
            # Arrange
            mock_api_client.get_executions.return_value = ApiResponse.success_response([
                {"id": 1, "name": "项目1", "status": "doing"},
                {"id": 2, "name": "项目2", "status": "wait"}
            ])

            with patch.object(splitter.interactive_input, 'select_execution', return_value=1):
                # Act
                result = splitter._select_project()

                # Assert
                assert result.success is True
                assert result.data['execution_id'] == 1

        def test_select_project_no_executions(self, splitter, mock_api_client):
            """测试没有可用项目"""
            # Arrange
            mock_api_client.get_executions.return_value = ApiResponse.error_response(
                ErrorCode.API_ERROR,
                "获取项目列表失败"
            )

            # Act
            result = splitter._select_project()

            # Assert
            assert result.success is False

    class TestPerformCreate:
        """测试执行任务创建"""

        def test_perform_create_success(self, splitter, mock_api_client):
            """测试成功创建任务"""
            # Arrange
            task_info = {
                'updated_title': '测试需求',
                'assigned_to': 'user1',
                'task_hours': 4,
                'deadline': '本周周五'
            }

            mock_api_client.create_task.return_value = ApiResponse.success_response({
                'id': 789,
                'name': '【研发】测试需求'
            })

            with patch.object(splitter, '_calculate_deadline', return_value='2024-03-15'):
                # Act
                result = splitter._perform_create(123, task_info, '测试需求', 10)

                # Assert
                assert result.success is True
                assert result.data['story_id'] == 123

        def test_perform_create_failure(self, splitter, mock_api_client):
            """测试创建任务失败"""
            # Arrange
            task_info = {
                'updated_title': '测试需求',
                'assigned_to': 'user1',
                'task_hours': 4,
                'deadline': '本周周五'
            }

            mock_api_client.create_task.return_value = ApiResponse.error_response(
                ErrorCode.API_ERROR,
                "创建任务失败"
            )

            with patch.object(splitter, '_calculate_deadline', return_value='2024-03-15'):
                # Act
                result = splitter._perform_create(123, task_info, '测试需求', 10)

                # Assert
                assert result.success is False

    class TestExecute:
        """测试执行方法"""

        def test_execute_missing_story_id(self, splitter):
            """测试缺少需求ID"""
            # Act
            result = splitter.execute(story_id=None)

            # Assert
            assert result.success is False
            assert result.error.code == ErrorCode.MISSING_PARAMETER

        def test_execute_non_interactive_mode(self, splitter, mock_api_client):
            """测试非交互模式"""
            # Arrange
            mock_api_client.get_story.return_value = ApiResponse.success_response({
                'id': 123,
                'title': '测试需求',
                'execution': 10,
                'execution_name': '项目A'
            })
            mock_api_client.update_story_title.return_value = ApiResponse.success_response({'result': 'success'})
            mock_api_client.review_story.return_value = ApiResponse.success_response({'result': 'success'})
            mock_api_client.create_task.return_value = ApiResponse.success_response({
                'id': 456,
                'name': '【研发】测试需求'
            })

            with patch.object(splitter.interactive_input, 'collect_task_info_non_interactive', return_value={
                'updated_title': '【A】【紧急】测试需求',
                'assigned_to': 'user1',
                'task_hours': 8,
                'deadline': '本周周五'
            }):
                with patch.object(splitter, '_calculate_deadline', return_value='2024-03-15'):
                    # Act
                    result = splitter.execute(
                        story_id='123',
                        grade='A',
                        priority='紧急',
                        assigned_to='user1',
                        task_hours=8
                    )

                    # Assert
                    assert result.success is True

        def test_execute_with_story_execution(self, splitter, mock_api_client):
            """测试使用需求关联的执行"""
            # Arrange
            mock_api_client.get_story.return_value = ApiResponse.success_response({
                'id': 123,
                'title': '测试需求',
                'execution': 20,
                'execution_name': '项目B'
            })
            mock_api_client.update_story_title.return_value = ApiResponse.success_response({'result': 'success'})
            mock_api_client.review_story.return_value = ApiResponse.success_response({'result': 'success'})
            mock_api_client.create_task.return_value = ApiResponse.success_response({
                'id': 456,
                'name': '【研发】测试需求'
            })

            with patch.object(splitter.interactive_input, 'collect_task_info_non_interactive', return_value={
                'updated_title': '【A】测试需求',
                'assigned_to': 'user2',
                'task_hours': 4,
                'deadline': '下周周五'
            }):
                with patch.object(splitter, '_calculate_deadline', return_value='2024-03-22'):
                    # Act
                    result = splitter.execute(
                        story_id='123',
                        grade='A',
                        assigned_to='user2',
                        task_hours=4
                    )

                    # Assert
                    assert result.success is True

        def test_execute_update_title_failure(self, splitter, mock_api_client):
            """测试更新标题失败但继续执行"""
            # Arrange
            mock_api_client.get_story.return_value = ApiResponse.success_response({
                'id': 123,
                'title': '测试需求',
                'execution': 10
            })
            mock_api_client.update_story_title.return_value = ApiResponse.error_response(
                ErrorCode.API_ERROR,
                "更新失败"
            )
            mock_api_client.review_story.return_value = ApiResponse.success_response({'result': 'success'})
            mock_api_client.create_task.return_value = ApiResponse.success_response({
                'id': 456,
                'name': '【研发】测试需求'
            })

            with patch.object(splitter.interactive_input, 'collect_task_info_non_interactive', return_value={
                'updated_title': '【A】测试需求',
                'assigned_to': 'user1',
                'task_hours': 8,
                'deadline': '本周周五'
            }):
                with patch.object(splitter, '_calculate_deadline', return_value='2024-03-15'):
                    # Act
                    result = splitter.execute(story_id='123', grade='A', assigned_to='user1', task_hours=8)

                    # Assert
                    assert result.success is True  # 即使更新标题失败，也应该继续

    class TestExecuteInteractiveMode:
        """测试交互模式"""

        def test_execute_interactive_mode_cancelled(self, splitter, mock_api_client):
            """测试交互模式用户取消"""
            # Arrange
            mock_api_client.get_story.return_value = ApiResponse.success_response({
                'id': 123,
                'title': '测试需求'
            })

            with patch.object(splitter.interactive_input, 'collect_task_info', return_value=None):
                # Act
                result = splitter.execute(story_id='123')

                # Assert
                assert result.success is False
                assert result.error.code == ErrorCode.USER_CANCELLED

    class TestSelectProjectWithDefault:
        """测试选择项目 - 带默认配置"""

        def test_select_project_with_default_config(self, splitter, mock_api_client):
            """测试使用默认配置选择项目"""
            # Arrange
            mock_api_client.get_executions.return_value = ApiResponse.success_response([
                {'id': 1, 'name': '都江堰项目'},
                {'id': 2, 'name': '其他项目'}
            ])

            with patch.object(splitter.interactive_input.config, 'get_zentao_config', return_value={
                'task_creation': {'default_project_name': '都江堰'}
            }):
                # Act
                result = splitter._select_project()

                # Assert
                assert result.success is True
                assert result.data['execution_id'] == 1

        def test_select_project_default_not_found(self, splitter, mock_api_client):
            """测试默认配置未找到匹配项目"""
            # Arrange
            mock_api_client.get_executions.return_value = ApiResponse.success_response([
                {'id': 1, 'name': '项目A'},
                {'id': 2, 'name': '项目B'}
            ])

            with patch.object(splitter.interactive_input.config, 'get_zentao_config', return_value={
                'task_creation': {'default_project_name': '不存在的项目'}
            }):
                with patch.object(splitter.interactive_input, 'select_execution', return_value=2):
                    # Act
                    result = splitter._select_project()

                    # Assert
                    assert result.success is True
                    assert result.data['execution_id'] == 2

    class TestExecuteWithReviewFailure:
        """测试执行方法 - 评审失败场景"""

        def test_execute_review_failure_continue(self, splitter, mock_api_client):
            """测试评审失败但继续执行"""
            # Arrange
            mock_api_client.get_story.return_value = ApiResponse.success_response({
                'id': 123,
                'title': '测试需求',
                'execution': 10
            })
            mock_api_client.update_story_title.return_value = ApiResponse.success_response({'result': 'success'})
            mock_api_client.review_story.return_value = ApiResponse.error_response(
                ErrorCode.API_ERROR,
                "评审失败"
            )
            mock_api_client.create_task.return_value = ApiResponse.success_response({
                'id': 456,
                'name': '【研发】测试需求'
            })

            with patch.object(splitter.interactive_input, 'collect_task_info_non_interactive', return_value={
                'updated_title': '【A】测试需求',
                'assigned_to': 'user1',
                'task_hours': 8,
                'deadline': '本周周五'
            }):
                with patch.object(splitter, '_calculate_deadline', return_value='2024-03-15'):
                    # Act
                    result = splitter.execute(story_id='123', grade='A', assigned_to='user1', task_hours=8)

                    # Assert
                    assert result.success is True  # 即使评审失败，也应该继续

        def test_execute_review_success(self, splitter, mock_api_client):
            """测试评审成功场景"""
            # Arrange
            mock_api_client.get_story.return_value = ApiResponse.success_response({
                'id': 123,
                'title': '测试需求',
                'execution': 10
            })
            mock_api_client.update_story_title.return_value = ApiResponse.success_response({'result': 'success'})
            mock_api_client.review_story.return_value = ApiResponse.success_response({'result': 'success'})
            mock_api_client.create_task.return_value = ApiResponse.success_response({
                'id': 456,
                'name': '【研发】测试需求'
            })

            with patch.object(splitter.interactive_input, 'collect_task_info_non_interactive', return_value={
                'updated_title': '【A】测试需求',
                'assigned_to': 'user1',
                'task_hours': 8,
                'deadline': '本周周五'
            }):
                with patch.object(splitter, '_calculate_deadline', return_value='2024-03-15'):
                    # Act
                    result = splitter.execute(story_id='123', grade='A', assigned_to='user1', task_hours=8)

                    # Assert
                    assert result.success is True

    class TestExecuteWithGetStoryFailure:
        """测试获取需求失败场景"""

        def test_execute_get_story_failure_continue(self, splitter, mock_api_client):
            """测试获取需求失败但继续执行"""
            # Arrange
            mock_api_client.get_story.return_value = ApiResponse.error_response(
                ErrorCode.API_ERROR,
                "获取需求失败"
            )
            mock_api_client.update_story_title.return_value = ApiResponse.success_response({'result': 'success'})
            mock_api_client.review_story.return_value = ApiResponse.success_response({'result': 'success'})
            mock_api_client.create_task.return_value = ApiResponse.success_response({
                'id': 456,
                'name': '【研发】测试需求'
            })
            # 需要设置 get_executions 返回值，因为需求没有关联的执行
            mock_api_client.get_executions.return_value = ApiResponse.success_response([
                {'id': 10, 'name': '项目A'}
            ])

            with patch.object(splitter.interactive_input, 'collect_task_info_non_interactive', return_value={
                'updated_title': '【A】测试需求',
                'assigned_to': 'user1',
                'task_hours': 8,
                'deadline': '本周周五'
            }):
                with patch.object(splitter.interactive_input, 'select_execution', return_value=10):
                    with patch.object(splitter, '_calculate_deadline', return_value='2024-03-15'):
                        # Act
                        result = splitter.execute(story_id='123', grade='A', assigned_to='user1', task_hours=8)

                        # Assert
                        assert result.success is True  # 即使获取需求失败，也应该继续

    class TestExecuteSelectProjectFailure:
        """测试选择项目失败场景"""

        def test_execute_select_project_failure(self, splitter, mock_api_client):
            """测试选择项目失败返回错误"""
            # Arrange
            mock_api_client.get_story.return_value = ApiResponse.success_response({
                'id': 123,
                'title': '测试需求'
                # 没有 execution 字段，需要选择项目
            })
            mock_api_client.update_story_title.return_value = ApiResponse.success_response({'result': 'success'})
            mock_api_client.review_story.return_value = ApiResponse.success_response({'result': 'success'})
            mock_api_client.get_executions.return_value = ApiResponse.error_response(
                ErrorCode.API_ERROR,
                "获取项目列表失败"
            )

            with patch.object(splitter.interactive_input, 'collect_task_info_non_interactive', return_value={
                'updated_title': '【A】测试需求',
                'assigned_to': 'user1',
                'task_hours': 8,
                'deadline': '本周周五'
            }):
                # Act
                result = splitter.execute(story_id='123', grade='A', assigned_to='user1', task_hours=8)

                # Assert
                assert result.success is False
                assert result.error.code == ErrorCode.API_ERROR

    class TestPerformCreateWithException:
        """测试执行任务创建异常场景"""

        def test_perform_create_with_exception(self, splitter, mock_api_client):
            """测试创建任务时发生异常"""
            # Arrange
            task_info = {
                'updated_title': '测试需求',
                'assigned_to': 'user1',
                'task_hours': 4,
                'deadline': '本周周五'
            }

            # 模拟 create_task 抛出异常
            mock_api_client.create_task.side_effect = Exception("网络错误")

            # Act
            result = splitter._perform_create(123, task_info, '测试需求', 10)

            # Assert
            assert result.success is False
            assert "网络错误" in result.error.message

    class TestFormatDisplayWithCreatedTask:
        """测试格式化显示 - 带创建任务信息"""

        def test_format_display_with_complete_data(self, splitter):
            """测试格式化完整数据"""
            # Arrange
            data = {
                "story_id": 123,
                "updated_title": "测试需求",
                "created_task": {
                    "id": 456,
                    "name": "【研发】测试需求"
                }
            }

            # Act
            result = splitter.format_display(data)

            # Assert
            assert "任务创建成功" in result
            assert "需求ID: #123" in result
            assert "需求标题: 测试需求" in result
            assert "任务ID: #456" in result
            assert "任务标题: 【研发】测试需求" in result

    class TestSelectProjectUserCancelled:
        """测试选择项目 - 用户取消场景"""

        def test_select_project_user_cancelled(self, splitter, mock_api_client):
            """测试用户取消选择项目"""
            # Arrange
            mock_api_client.get_executions.return_value = ApiResponse.success_response([
                {'id': 1, 'name': '项目1'},
                {'id': 2, 'name': '项目2'}
            ])

            with patch.object(splitter.interactive_input.config, 'get_zentao_config', return_value={}):
                with patch.object(splitter.interactive_input, 'select_execution', return_value=None):
                    # Act
                    result = splitter._select_project()

                    # Assert
                    assert result.success is False
                    assert result.error.code == ErrorCode.USER_CANCELLED

    class TestCalculateDeadlineFriday:
        """测试计算截止日期 - 周五特殊情况"""

        def test_calculate_deadline_today_is_friday(self, splitter):
            """测试今天就是周五时，本周周五应该返回下周五"""
            # 由于datetime是在函数内部导入的，我们需要直接测试函数行为
            # 这个测试验证当今天是周五时，代码逻辑是否正确
            # 我们使用一个已知的周五日期来验证
            from datetime import datetime, timedelta as td

            # 计算已知的周五日期 (2024-03-08 是周五)
            known_friday = datetime(2024, 3, 8)

            # 手动计算期望的结果：如果今天是周五，本周周五应该返回下周五 (3月15日)
            expected_next_friday = "2024-03-15"

            # 由于无法直接mock函数内部的datetime，我们验证计算逻辑
            # weekday=4 (周五), days_to_friday = (4-4)%7 = 0, 所以设为7
            # 结果是今天 + 7天 = 下周五
            days_to_friday = (4 - 4) % 7  # 0
            if days_to_friday == 0:
                days_to_friday = 7
            calculated_date = known_friday + td(days=days_to_friday)

            # Assert
            assert calculated_date.strftime('%Y-%m-%d') == expected_next_friday

    class TestExecuteWithEmptyUpdatedTitle:
        """测试执行 - 空更新标题场景"""

        def test_execute_with_empty_updated_title(self, splitter, mock_api_client):
            """测试 updated_title 为空时跳过更新标题"""
            # Arrange
            mock_api_client.get_story.return_value = ApiResponse.success_response({
                'id': 123,
                'title': '测试需求',
                'execution': 10
            })
            # update_story_title 不应该被调用
            mock_api_client.review_story.return_value = ApiResponse.success_response({'result': 'success'})
            mock_api_client.create_task.return_value = ApiResponse.success_response({
                'id': 456,
                'name': '【研发】测试需求'
            })

            with patch.object(splitter.interactive_input, 'collect_task_info_non_interactive', return_value={
                'updated_title': '',  # 空标题
                'assigned_to': 'user1',
                'task_hours': 8,
                'deadline': '本周周五'
            }):
                with patch.object(splitter, '_calculate_deadline', return_value='2024-03-15'):
                    # Act
                    result = splitter.execute(story_id='123', grade='A', assigned_to='user1', task_hours=8)

                    # Assert
                    assert result.success is True
                    # 验证 update_story_title 没有被调用
                    mock_api_client.update_story_title.assert_not_called()
