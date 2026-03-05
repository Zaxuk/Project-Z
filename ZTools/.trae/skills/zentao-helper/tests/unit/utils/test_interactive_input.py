# -*- coding: utf-8 -*-
"""
测试交互式输入模块
"""

import pytest
from unittest.mock import Mock, patch

from src.utils.interactive_input import InteractiveInput


class TestInteractiveInput:
    """测试交互式输入处理器"""

    @pytest.fixture
    def interactive_input(self):
        """创建交互式输入处理器实例"""
        with patch('src.utils.interactive_input.get_config') as mock_config:
            mock_config.return_value = Mock()
            mock_config.return_value.get_zentao_config.return_value = {
                'task_creation': {
                    'default_assigned_to': 'default_user',
                    'grade_hours': {
                        'A-': 1,
                        'A': 2,
                        'A+': 4,
                        'A++': 8,
                        'B': 1
                    }
                }
            }
            return InteractiveInput()

    class TestCollectTaskInfoNonInteractive:
        """测试非交互式收集任务信息"""

        def test_collect_task_info_non_interactive_default(self, interactive_input):
            """测试使用默认参数"""
            # Act
            result = interactive_input.collect_task_info_non_interactive("测试需求")

            # Assert
            assert result is not None
            assert result['grade'] == 'A'
            assert result['priority'] == '非紧急'
            assert result['task_hours'] == 2  # A等级的默认时长
            assert result['assigned_to'] == 'default_user'

        def test_collect_task_info_non_interactive_custom(self, interactive_input):
            """测试使用自定义参数"""
            # Act
            result = interactive_input.collect_task_info_non_interactive(
                story_title="测试需求",
                grade='A+',
                priority='紧急',
                online_time='下周周一',
                assigned_to='custom_user',
                task_hours=6,
                deadline='下周周五'
            )

            # Assert
            assert result is not None
            assert result['grade'] == 'A+'
            assert result['priority'] == '紧急'
            assert result['task_hours'] == 6
            assert result['assigned_to'] == 'custom_user'
            assert result['deadline'] == '下周周五'

        def test_collect_task_info_non_interactive_invalid_grade(self, interactive_input):
            """测试无效的等级参数"""
            # Act
            result = interactive_input.collect_task_info_non_interactive(
                story_title="测试需求",
                grade='Z'  # 无效等级
            )

            # Assert
            assert result is not None
            assert result['grade'] == 'A'  # 应使用默认值

        def test_collect_task_info_non_interactive_invalid_priority(self, interactive_input):
            """测试无效的优先级参数"""
            # Act
            result = interactive_input.collect_task_info_non_interactive(
                story_title="测试需求",
                priority='高'  # 无效优先级
            )

            # Assert
            assert result is not None
            assert result['priority'] == '非紧急'  # 应使用默认值

        def test_collect_task_info_non_interactive_no_default_assigned(self, interactive_input):
            """测试没有默认执行人"""
            # Arrange
            interactive_input.config.get_zentao_config.return_value = {
                'task_creation': {
                    'grade_hours': {'A': 2}
                }
            }

            # Act
            result = interactive_input.collect_task_info_non_interactive(
                story_title="测试需求"
            )

            # Assert
            assert result is not None
            assert result['assigned_to'] is None

        def test_collect_task_info_non_interactive_auto_hours(self, interactive_input):
            """测试根据等级自动计算时长"""
            # Act
            result_a_plus = interactive_input.collect_task_info_non_interactive(
                story_title="测试需求",
                grade='A+',
                task_hours=None
            )

            # Assert
            assert result_a_plus['task_hours'] == 4  # A+等级的默认时长

    class TestGetOnlineTimeText:
        """测试获取上线时间文本"""

        def test_get_online_time_text_next_monday(self, interactive_input):
            """测试下周周一"""
            result = interactive_input._get_online_time_text('next_monday')
            assert result == '下周周一'

        def test_get_online_time_text_next_thursday(self, interactive_input):
            """测试下周周四"""
            result = interactive_input._get_online_time_text('next_thursday')
            assert result == '下周周四'

        def test_get_online_time_text_next_next_monday(self, interactive_input):
            """测试下下周周一"""
            result = interactive_input._get_online_time_text('next_next_monday')
            assert result == '下下周周一'

        def test_get_online_time_text_unknown(self, interactive_input):
            """测试未知规则"""
            result = interactive_input._get_online_time_text('unknown_rule')
            assert result == 'unknown_rule'

    class TestGetDeadlineText:
        """测试获取截止时间文本"""

        def test_get_deadline_text_this_friday(self, interactive_input):
            """测试本周周五"""
            result = interactive_input._get_deadline_text('this_friday')
            assert result == '本周周五'

        def test_get_deadline_text_next_friday(self, interactive_input):
            """测试下周周五"""
            result = interactive_input._get_deadline_text('next_friday')
            assert result == '下周周五'

        def test_get_deadline_text_unknown(self, interactive_input):
            """测试未知规则"""
            result = interactive_input._get_deadline_text('unknown_rule')
            assert result == 'unknown_rule'

    class TestInputCustomDate:
        """测试自定义日期输入"""

        def test_input_custom_date_valid(self, interactive_input):
            """测试有效日期输入"""
            with patch('builtins.input', return_value='260331'):
                result = interactive_input._input_custom_date()
                assert result == '260331'

        def test_input_custom_date_invalid_format(self, interactive_input):
            """测试无效格式"""
            with patch('builtins.input', side_effect=['123', '260331']):
                result = interactive_input._input_custom_date()
                assert result == '260331'

        def test_input_custom_date_invalid_date(self, interactive_input):
            """测试无效日期"""
            with patch('builtins.input', side_effect=['260231', '260331']):  # 2月31日不存在
                result = interactive_input._input_custom_date()
                assert result == '260331'

        def test_input_custom_date_empty(self, interactive_input):
            """测试空输入"""
            with patch('builtins.input', return_value=''):
                result = interactive_input._input_custom_date()
                assert result is None

        def test_input_custom_date_eof_error(self, interactive_input):
            """测试EOF错误"""
            with patch('builtins.input', side_effect=EOFError()):
                result = interactive_input._input_custom_date()
                assert result is None

    class TestSelectExecution:
        """测试选择执行/项目"""

        def test_select_execution_empty_list(self, interactive_input):
            """测试空列表"""
            with patch('builtins.input', return_value=''):
                result = interactive_input.select_execution([])
                assert result is None

        def test_select_execution_with_valid_choice(self, interactive_input):
            """测试有效选择"""
            executions = [
                {'id': 1, 'name': '项目1', 'status': 'doing'},
                {'id': 2, 'name': '项目2', 'status': 'wait'}
            ]
            with patch('builtins.input', return_value='1'):
                result = interactive_input.select_execution(executions)
                assert result == 1

        def test_select_execution_with_second_choice(self, interactive_input):
            """测试选择第二个"""
            executions = [
                {'id': 1, 'name': '项目1'},
                {'id': 2, 'name': '项目2'}
            ]
            with patch('builtins.input', return_value='2'):
                result = interactive_input.select_execution(executions)
                assert result == 2

        def test_select_execution_cancel(self, interactive_input):
            """测试取消选择"""
            executions = [
                {'id': 1, 'name': '项目1'}
            ]
            with patch('builtins.input', return_value=''):
                result = interactive_input.select_execution(executions)
                assert result is None

        def test_select_execution_invalid_choice(self, interactive_input):
            """测试无效选择后重新选择"""
            executions = [
                {'id': 1, 'name': '项目1'}
            ]
            with patch('builtins.input', side_effect=['5', '1']):  # 先选5（无效），再选1
                result = interactive_input.select_execution(executions)
                assert result == 1

        def test_select_execution_invalid_input(self, interactive_input):
            """测试非数字输入"""
            executions = [
                {'id': 1, 'name': '项目1'}
            ]
            with patch('builtins.input', side_effect=['abc', '1']):
                result = interactive_input.select_execution(executions)
                assert result == 1

        def test_select_execution_with_default_project(self, interactive_input):
            """测试使用默认项目名称匹配"""
            executions = [
                {'id': 1, 'name': '都江堰项目'},
                {'id': 2, 'name': '其他项目'}
            ]
            # 不需要input，因为匹配到了默认项目
            result = interactive_input.select_execution(executions, default_project_name='都江堰')
            assert result == 1

        def test_select_execution_default_project_not_found(self, interactive_input):
            """测试默认项目名称未找到匹配"""
            executions = [
                {'id': 1, 'name': '项目1'},
                {'id': 2, 'name': '项目2'}
            ]
            with patch('builtins.input', return_value='1'):
                result = interactive_input.select_execution(executions, default_project_name='不存在的项目')
                assert result == 1

        def test_select_execution_manual_input_empty(self, interactive_input):
            """测试空列表时手动输入为空"""
            with patch('builtins.input', return_value=''):
                result = interactive_input.select_execution([])
                assert result is None

        def test_select_execution_manual_input_valid(self, interactive_input):
            """测试空列表时手动输入有效ID"""
            with patch('builtins.input', return_value='123'):
                result = interactive_input.select_execution([])
                assert result == 123

        def test_select_execution_manual_input_invalid(self, interactive_input):
            """测试空列表时手动输入无效"""
            with patch('builtins.input', side_effect=['abc', '0', '123']):
                result = interactive_input.select_execution([])
                assert result == 123

        def test_select_execution_eof_error(self, interactive_input):
            """测试EOF错误"""
            executions = [
                {'id': 1, 'name': '项目1'}
            ]
            with patch('builtins.input', side_effect=EOFError()):
                result = interactive_input.select_execution(executions)
                assert result is None

        def test_select_execution_keyboard_interrupt(self, interactive_input):
            """测试键盘中断"""
            executions = [
                {'id': 1, 'name': '项目1'}
            ]
            with patch('builtins.input', side_effect=KeyboardInterrupt()):
                result = interactive_input.select_execution(executions)
                assert result is None

    class TestInputGrade:
        """测试输入需求等级"""

        def test_input_grade_default(self, interactive_input):
            """测试默认等级A"""
            with patch('builtins.input', return_value=''):
                result = interactive_input._input_grade()
                assert result == 'A'

        def test_input_grade_a_minus(self, interactive_input):
            """测试等级A-"""
            with patch('builtins.input', return_value='1'):
                result = interactive_input._input_grade()
                assert result == 'A-'

        def test_input_grade_a_plus(self, interactive_input):
            """测试等级A+"""
            with patch('builtins.input', return_value='3'):
                result = interactive_input._input_grade()
                assert result == 'A+'

        def test_input_grade_a_plus_plus(self, interactive_input):
            """测试等级A++"""
            with patch('builtins.input', return_value='4'):
                result = interactive_input._input_grade()
                assert result == 'A++'

        def test_input_grade_b(self, interactive_input):
            """测试等级B"""
            with patch('builtins.input', return_value='5'):
                result = interactive_input._input_grade()
                assert result == 'B'

        def test_input_grade_invalid_then_valid(self, interactive_input):
            """测试无效选择后重新选择"""
            with patch('builtins.input', side_effect=['6', '2']):
                result = interactive_input._input_grade()
                assert result == 'A'

        def test_input_grade_eof_error(self, interactive_input):
            """测试EOF错误"""
            with patch('builtins.input', side_effect=EOFError()):
                result = interactive_input._input_grade()
                assert result is None

        def test_input_grade_keyboard_interrupt(self, interactive_input):
            """测试键盘中断"""
            with patch('builtins.input', side_effect=KeyboardInterrupt()):
                result = interactive_input._input_grade()
                assert result is None

    class TestInputPriority:
        """测试输入需求优先级"""

        def test_input_priority_default(self, interactive_input):
            """测试默认优先级非紧急"""
            with patch('builtins.input', return_value=''):
                result = interactive_input._input_priority()
                assert result == '非紧急'

        def test_input_priority_not_urgent(self, interactive_input):
            """测试选择非紧急"""
            with patch('builtins.input', return_value='1'):
                result = interactive_input._input_priority()
                assert result == '非紧急'

        def test_input_priority_urgent(self, interactive_input):
            """测试选择紧急"""
            with patch('builtins.input', return_value='2'):
                result = interactive_input._input_priority()
                assert result == '紧急'

        def test_input_priority_invalid_then_valid(self, interactive_input):
            """测试无效选择后重新选择"""
            with patch('builtins.input', side_effect=['3', '1']):
                result = interactive_input._input_priority()
                assert result == '非紧急'

        def test_input_priority_eof_error(self, interactive_input):
            """测试EOF错误"""
            with patch('builtins.input', side_effect=EOFError()):
                result = interactive_input._input_priority()
                assert result is None

        def test_input_priority_keyboard_interrupt(self, interactive_input):
            """测试键盘中断"""
            with patch('builtins.input', side_effect=KeyboardInterrupt()):
                result = interactive_input._input_priority()
                assert result is None

    class TestInputOnlineTime:
        """测试输入需求上线时间"""

        def test_input_online_time_default(self, interactive_input):
            """测试默认时间下下周周一"""
            with patch('builtins.input', return_value=''):
                result = interactive_input._input_online_time()
                assert result == '下下周周一'

        def test_input_online_time_next_monday(self, interactive_input):
            """测试下周周一"""
            with patch('builtins.input', return_value='1'):
                result = interactive_input._input_online_time()
                assert result == '下周周一'

        def test_input_online_time_next_thursday(self, interactive_input):
            """测试下周周四"""
            with patch('builtins.input', return_value='2'):
                result = interactive_input._input_online_time()
                assert result == '下周周四'

        def test_input_online_time_next_next_monday(self, interactive_input):
            """测试下下周周一"""
            with patch('builtins.input', return_value='3'):
                result = interactive_input._input_online_time()
                assert result == '下下周周一'

        def test_input_online_time_next_next_thursday(self, interactive_input):
            """测试下下周周四"""
            with patch('builtins.input', return_value='4'):
                result = interactive_input._input_online_time()
                assert result == '下下周周四'

        def test_input_online_time_custom_date(self, interactive_input):
            """测试自定义日期"""
            with patch('builtins.input', side_effect=['5', '260331']):
                result = interactive_input._input_online_time()
                assert result == '260331'

        def test_input_online_time_invalid_then_valid(self, interactive_input):
            """测试无效选择后重新选择"""
            with patch('builtins.input', side_effect=['6', '1']):
                result = interactive_input._input_online_time()
                assert result == '下周周一'

        def test_input_online_time_eof_error(self, interactive_input):
            """测试EOF错误"""
            with patch('builtins.input', side_effect=EOFError()):
                result = interactive_input._input_online_time()
                assert result is None

        def test_input_online_time_keyboard_interrupt(self, interactive_input):
            """测试键盘中断"""
            with patch('builtins.input', side_effect=KeyboardInterrupt()):
                result = interactive_input._input_online_time()
                assert result is None

    class TestInputAssignedTo:
        """测试输入任务执行人"""

        def test_input_assigned_to_default(self, interactive_input):
            """测试使用默认执行人"""
            with patch('builtins.input', return_value=''):
                result = interactive_input._input_assigned_to()
                assert result == 'default_user'

        def test_input_assigned_to_custom(self, interactive_input):
            """测试自定义执行人"""
            with patch('builtins.input', return_value='custom_user'):
                result = interactive_input._input_assigned_to()
                assert result == 'custom_user'

        def test_input_assigned_to_no_default(self, interactive_input):
            """测试没有默认执行人"""
            interactive_input.config.get_zentao_config.return_value = {}
            with patch('builtins.input', return_value=''):
                result = interactive_input._input_assigned_to()
                assert result is None

        def test_input_assigned_to_eof_error(self, interactive_input):
            """测试EOF错误"""
            with patch('builtins.input', side_effect=EOFError()):
                result = interactive_input._input_assigned_to()
                assert result is None

        def test_input_assigned_to_keyboard_interrupt(self, interactive_input):
            """测试键盘中断"""
            with patch('builtins.input', side_effect=KeyboardInterrupt()):
                result = interactive_input._input_assigned_to()
                assert result is None

    class TestInputTaskHours:
        """测试输入任务时长"""

        def test_input_task_hours_default(self, interactive_input):
            """测试使用默认时长"""
            with patch('builtins.input', return_value=''):
                result = interactive_input._input_task_hours('A')
                assert result == 2  # A等级的默认时长

        def test_input_task_hours_custom(self, interactive_input):
            """测试自定义时长"""
            with patch('builtins.input', return_value='5'):
                result = interactive_input._input_task_hours('A')
                assert result == 5.0

        def test_input_task_hours_invalid_number(self, interactive_input):
            """测试无效数字"""
            with patch('builtins.input', side_effect=['abc', '3']):
                result = interactive_input._input_task_hours('A')
                assert result == 3.0

        def test_input_task_hours_zero(self, interactive_input):
            """测试输入0（无效）"""
            with patch('builtins.input', side_effect=['0', '-1', '4']):
                result = interactive_input._input_task_hours('A')
                assert result == 4.0

        def test_input_task_hours_no_default(self, interactive_input):
            """测试没有默认时长"""
            interactive_input.config.get_zentao_config.return_value = {}
            with patch('builtins.input', return_value='6'):
                result = interactive_input._input_task_hours('A')
                assert result == 6.0

        def test_input_task_hours_eof_error(self, interactive_input):
            """测试EOF错误"""
            with patch('builtins.input', side_effect=EOFError()):
                result = interactive_input._input_task_hours('A')
                assert result is None

        def test_input_task_hours_keyboard_interrupt(self, interactive_input):
            """测试键盘中断"""
            with patch('builtins.input', side_effect=KeyboardInterrupt()):
                result = interactive_input._input_task_hours('A')
                assert result is None

    class TestInputDeadline:
        """测试输入任务截止时间"""

        def test_input_deadline_default(self, interactive_input):
            """测试默认截止时间本周周五"""
            with patch('builtins.input', return_value=''):
                result = interactive_input._input_deadline(8)
                assert result == '本周周五'

        def test_input_deadline_this_friday(self, interactive_input):
            """测试本周周五"""
            with patch('builtins.input', return_value='1'):
                result = interactive_input._input_deadline(8)
                assert result == '本周周五'

        def test_input_deadline_next_friday(self, interactive_input):
            """测试下周周五"""
            with patch('builtins.input', return_value='2'):
                result = interactive_input._input_deadline(8)
                assert result == '下周周五'

        def test_input_deadline_invalid_then_valid(self, interactive_input):
            """测试无效选择后重新选择"""
            with patch('builtins.input', side_effect=['3', '1']):
                result = interactive_input._input_deadline(8)
                assert result == '本周周五'

        def test_input_deadline_eof_error(self, interactive_input):
            """测试EOF错误"""
            with patch('builtins.input', side_effect=EOFError()):
                result = interactive_input._input_deadline(8)
                assert result is None

        def test_input_deadline_keyboard_interrupt(self, interactive_input):
            """测试键盘中断"""
            with patch('builtins.input', side_effect=KeyboardInterrupt()):
                result = interactive_input._input_deadline(8)
                assert result is None

    class TestConfirmAllInfo:
        """测试确认所有信息"""

        def test_confirm_all_info_yes(self, interactive_input):
            """测试确认（y）"""
            with patch('builtins.input', return_value='y'):
                result = interactive_input._confirm_all_info('A', '非紧急', '下周周一', 'user1', 8, '本周周五', '测试标题')
                assert result is True

        def test_confirm_all_info_empty(self, interactive_input):
            """测试确认（空输入）"""
            with patch('builtins.input', return_value=''):
                result = interactive_input._confirm_all_info('A', '非紧急', '下周周一', 'user1', 8, '本周周五', '测试标题')
                assert result is True

        def test_confirm_all_info_no(self, interactive_input):
            """测试取消（n）"""
            with patch('builtins.input', return_value='n'):
                result = interactive_input._confirm_all_info('A', '非紧急', '下周周一', 'user1', 8, '本周周五', '测试标题')
                assert result is False

        def test_confirm_all_info_invalid_then_yes(self, interactive_input):
            """测试无效输入后确认"""
            with patch('builtins.input', side_effect=['invalid', 'y']):
                result = interactive_input._confirm_all_info('A', '非紧急', '下周周一', 'user1', 8, '本周周五', '测试标题')
                assert result is True

        def test_confirm_all_info_eof_error(self, interactive_input):
            """测试EOF错误"""
            with patch('builtins.input', side_effect=EOFError()):
                result = interactive_input._confirm_all_info('A', '非紧急', '下周周一', 'user1', 8, '本周周五', '测试标题')
                assert result is False

    class TestGenerateTaskTitle:
        """测试生成任务标题"""

        def test_generate_task_title(self, interactive_input):
            """测试生成任务标题"""
            with patch('src.utils.story_title_updater.StoryTitleUpdater') as mock_updater_class:
                mock_updater = Mock()
                mock_updater.update_title.return_value = '【A】【标签】260331 测试需求'
                mock_updater_class.return_value = mock_updater

                result = interactive_input._generate_task_title('测试需求', 'A', '下周周一')
                assert result == '【研发】【A】【标签】260331 测试需求'
                mock_updater.update_title.assert_called_once_with('测试需求', 'A', '下周周一')

    class TestInputTaskTitle:
        """测试输入任务标题"""

        def test_input_task_title_default(self, interactive_input):
            """测试使用默认标题"""
            with patch.object(interactive_input, '_generate_task_title', return_value='【研发】默认标题'):
                with patch('builtins.input', return_value=''):
                    result = interactive_input._input_task_title('需求标题', 'A', '下周周一')
                    assert result == '【研发】默认标题'

        def test_input_task_title_custom(self, interactive_input):
            """测试自定义标题"""
            with patch.object(interactive_input, '_generate_task_title', return_value='【研发】默认标题'):
                with patch('builtins.input', return_value='自定义标题'):
                    result = interactive_input._input_task_title('需求标题', 'A', '下周周一')
                    assert result == '自定义标题'

        def test_input_task_title_eof_error(self, interactive_input):
            """测试EOF错误"""
            with patch.object(interactive_input, '_generate_task_title', return_value='【研发】默认标题'):
                with patch('builtins.input', side_effect=EOFError()):
                    result = interactive_input._input_task_title('需求标题', 'A', '下周周一')
                    assert result is None

        def test_input_task_title_keyboard_interrupt(self, interactive_input):
            """测试键盘中断"""
            with patch.object(interactive_input, '_generate_task_title', return_value='【研发】默认标题'):
                with patch('builtins.input', side_effect=KeyboardInterrupt()):
                    result = interactive_input._input_task_title('需求标题', 'A', '下周周一')
                    assert result is None

    class TestCollectTaskInfo:
        """测试收集任务信息主方法"""

        def test_collect_task_info_success(self, interactive_input):
            """测试成功收集信息"""
            with patch.object(interactive_input, '_input_grade', return_value='A'):
                with patch.object(interactive_input, '_input_priority', return_value='非紧急'):
                    with patch.object(interactive_input, '_input_online_time', return_value='下周周一'):
                        with patch.object(interactive_input, '_input_assigned_to', return_value='user1'):
                            with patch.object(interactive_input, '_input_task_hours', return_value=8):
                                with patch.object(interactive_input, '_input_deadline', return_value='本周周五'):
                                    with patch.object(interactive_input, '_confirm_all_info', return_value=True):
                                        with patch('src.utils.story_title_updater.StoryTitleUpdater') as mock_updater_class:
                                            mock_updater = Mock()
                                            mock_updater.update_title.return_value = '【A】260331 测试需求'
                                            mock_updater_class.return_value = mock_updater

                                            result = interactive_input.collect_task_info('测试需求')

                                            assert result is not None
                                            assert result['grade'] == 'A'
                                            assert result['priority'] == '非紧急'
                                            assert result['assigned_to'] == 'user1'
                                            assert result['task_hours'] == 8

        def test_collect_task_info_cancelled(self, interactive_input):
            """测试用户取消"""
            with patch.object(interactive_input, '_input_grade', return_value='A'):
                with patch.object(interactive_input, '_input_priority', return_value='非紧急'):
                    with patch.object(interactive_input, '_input_online_time', return_value='下周周一'):
                        with patch.object(interactive_input, '_input_assigned_to', return_value='user1'):
                            with patch.object(interactive_input, '_input_task_hours', return_value=8):
                                with patch.object(interactive_input, '_input_deadline', return_value='本周周五'):
                                    with patch.object(interactive_input, '_confirm_all_info', return_value=False):
                                        with patch('src.utils.story_title_updater.StoryTitleUpdater') as mock_updater_class:
                                            mock_updater = Mock()
                                            mock_updater.update_title.return_value = '【A】260331 测试需求'
                                            mock_updater_class.return_value = mock_updater

                                            result = interactive_input.collect_task_info('测试需求')

                                            assert result is None

        def test_collect_task_info_with_long_title(self, interactive_input):
            """测试长标题截断显示"""
            long_title = 'A' * 100  # 很长的标题
            with patch.object(interactive_input, '_input_grade', return_value='A'):
                with patch.object(interactive_input, '_input_priority', return_value='非紧急'):
                    with patch.object(interactive_input, '_input_online_time', return_value='下周周一'):
                        with patch.object(interactive_input, '_input_assigned_to', return_value='user1'):
                            with patch.object(interactive_input, '_input_task_hours', return_value=8):
                                with patch.object(interactive_input, '_input_deadline', return_value='本周周五'):
                                    with patch.object(interactive_input, '_confirm_all_info', return_value=True):
                                        with patch('src.utils.story_title_updater.StoryTitleUpdater') as mock_updater_class:
                                            mock_updater = Mock()
                                            mock_updater.update_title.return_value = long_title
                                            mock_updater_class.return_value = mock_updater

                                            result = interactive_input.collect_task_info('测试需求')

                                            assert result is not None
                                            assert result['updated_title'] == long_title
