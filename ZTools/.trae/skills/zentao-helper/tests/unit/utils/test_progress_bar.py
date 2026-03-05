# -*- coding: utf-8 -*-
"""
测试进度条模块
"""

import pytest
from io import StringIO
from unittest.mock import patch

from src.utils.progress_bar import ProgressBar, Spinner


class TestProgressBar:
    """测试进度条"""

    class TestInit:
        """测试初始化"""

        def test_init_with_defaults(self):
            """测试默认初始化"""
            # Act
            pbar = ProgressBar()

            # Assert
            assert pbar.total is None
            assert pbar.desc == ""
            assert pbar.unit == "项"
            assert pbar.current == 0

        def test_init_with_params(self):
            """测试带参数初始化"""
            # Act
            output = StringIO()
            pbar = ProgressBar(total=100, desc="测试中", unit="个", bar_width=20, file=output)

            # Assert
            assert pbar.total == 100
            assert pbar.desc == "测试中"
            assert pbar.unit == "个"
            assert pbar.bar_width == 20

    class TestContextManager:
        """测试上下文管理器"""

        def test_context_manager(self):
            """测试上下文管理器"""
            # Act & Assert
            output = StringIO()
            with ProgressBar(total=10, desc="测试", file=output) as pbar:
                assert pbar.start_time is not None
                pbar.update(5)
                assert pbar.current == 5

        def test_context_manager_exit(self):
            """测试上下文管理器退出"""
            # Act
            output = StringIO()
            with ProgressBar(total=10, file=output) as pbar:
                pass

            # Assert
            assert pbar._closed is True

    class TestUpdate:
        """测试更新进度"""

        def test_update_single(self):
            """测试单次更新"""
            # Arrange
            output = StringIO()
            pbar = ProgressBar(total=10, file=output)

            # Act
            pbar.start()
            pbar.update(1)

            # Assert
            assert pbar.current == 1

        def test_update_multiple(self):
            """测试多次更新"""
            # Arrange
            output = StringIO()
            pbar = ProgressBar(total=10, file=output)

            # Act
            pbar.start()
            pbar.update(3)
            pbar.update(2)

            # Assert
            assert pbar.current == 5

    class TestSetPostfix:
        """测试设置后缀信息"""

        def test_set_postfix(self):
            """测试设置后缀"""
            # Arrange
            output = StringIO()
            pbar = ProgressBar(total=10, file=output)

            # Act
            pbar.start()
            pbar.set_postfix(当前=5, 总数=10)

            # Assert
            assert pbar.postfix == {'当前': 5, '总数': 10}

        def test_set_postfix_update(self):
            """测试更新后缀"""
            # Arrange
            output = StringIO()
            pbar = ProgressBar(total=10, file=output)

            # Act
            pbar.start()
            pbar.set_postfix(当前=5)
            pbar.set_postfix(速度="10/s")

            # Assert
            assert pbar.postfix == {'当前': 5, '速度': '10/s'}

    class TestClose:
        """测试关闭进度条"""

        def test_close(self):
            """测试关闭"""
            # Arrange
            output = StringIO()
            pbar = ProgressBar(total=10, file=output)
            pbar.start()

            # Act
            pbar.close()

            # Assert
            assert pbar._closed is True

        def test_close_idempotent(self):
            """测试关闭幂等性"""
            # Arrange
            output = StringIO()
            pbar = ProgressBar(total=10, file=output)
            pbar.start()

            # Act
            pbar.close()
            pbar.close()  # 第二次关闭不应报错

            # Assert
            assert pbar._closed is True


class TestSpinner:
    """测试加载动画"""

    class TestInit:
        """测试初始化"""

        def test_init_with_defaults(self):
            """测试默认初始化"""
            # Act
            spinner = Spinner()

            # Assert
            assert spinner.desc == "加载中"  # 默认描述是"加载中"
            assert spinner._running is False

        def test_init_with_desc(self):
            """测试带描述初始化"""
            # Act
            spinner = Spinner(desc="自定义描述")

            # Assert
            assert spinner.desc == "自定义描述"

    class TestStartStop:
        """测试开始和停止"""

        @patch('sys.stdout', new_callable=StringIO)
        def test_start_stop(self, mock_stdout):
            """测试开始和停止"""
            # Arrange
            spinner = Spinner(desc="测试")

            # Act
            spinner.start()
            assert spinner._running is True
            spinner.stop()

            # Assert
            assert spinner._running is False

        @patch('sys.stdout', new_callable=StringIO)
        def test_stop_with_message(self, mock_stdout):
            """测试带消息停止"""
            # Arrange
            spinner = Spinner(desc="测试")
            spinner.start()

            # Act
            spinner.stop(message="完成")

            # Assert
            assert spinner._running is False

        @patch('sys.stdout', new_callable=StringIO)
        def test_stop_with_error(self, mock_stdout):
            """测试错误状态停止"""
            # Arrange
            spinner = Spinner(desc="测试")
            spinner.start()

            # Act
            spinner.stop(success=False)

            # Assert
            assert spinner._running is False

        @patch('sys.stdout', new_callable=StringIO)
        def test_succeed(self, mock_stdout):
            """测试成功方法"""
            # Arrange
            spinner = Spinner(desc="测试")
            spinner.start()

            # Act
            spinner.succeed("操作成功")

            # Assert
            assert spinner._running is False

        @patch('sys.stdout', new_callable=StringIO)
        def test_fail(self, mock_stdout):
            """测试失败方法"""
            # Arrange
            spinner = Spinner(desc="测试")
            spinner.start()

            # Act
            spinner.fail("操作失败")

            # Assert
            assert spinner._running is False

        @patch('sys.stdout', new_callable=StringIO)
        def test_stop_when_not_running(self, mock_stdout):
            """测试停止未运行的spinner"""
            # Arrange
            spinner = Spinner(desc="测试")
            # 不调用start

            # Act - 不应抛出异常
            spinner.stop()

            # Assert
            assert spinner._running is False

    class TestSpinnerTimeFormat:
        """测试Spinner时间格式化"""

        def test_format_time_seconds(self):
            """测试秒级时间格式化"""
            spinner = Spinner()
            result = spinner._format_time(45.5)
            assert result == "45s"

        def test_format_time_minutes(self):
            """测试分钟级时间格式化"""
            spinner = Spinner()
            result = spinner._format_time(125.0)  # 2分5秒
            assert result == "2m5s"

        def test_format_time_hours(self):
            """测试小时级时间格式化"""
            spinner = Spinner()
            result = spinner._format_time(3665.0)  # 1小时1分5秒
            assert result == "1h1m"


class TestProgressBarIndeterminate:
    """测试不确定进度条"""

    def test_indeterminate_progress(self):
        """测试不确定进度显示"""
        # Arrange
        output = StringIO()
        pbar = ProgressBar(desc="处理中", file=output)  # total=None

        # Act
        pbar.start()
        pbar.update(1)
        pbar.update(1)

        # Assert
        assert pbar.current == 2
        assert pbar.total is None

    def test_indeterminate_with_postfix(self):
        """测试不确定进度带后缀"""
        # Arrange
        output = StringIO()
        pbar = ProgressBar(desc="处理中", file=output)

        # Act
        pbar.start()
        pbar.set_postfix(状态="运行中")

        # Assert
        assert pbar.postfix == {'状态': '运行中'}


class TestProgressBarTimeFormat:
    """测试进度条时间格式化"""

    def test_format_time_seconds(self):
        """测试秒级时间格式化"""
        pbar = ProgressBar()
        result = pbar._format_time(45.5)
        assert result == "45s"

    def test_format_time_minutes(self):
        """测试分钟级时间格式化"""
        pbar = ProgressBar()
        result = pbar._format_time(125.0)  # 2分5秒
        assert result == "02:05"

    def test_format_time_hours(self):
        """测试小时级时间格式化"""
        pbar = ProgressBar()
        result = pbar._format_time(3665.0)  # 1小时1分5秒
        assert result == "1:01:05"


class TestDummyProgressBar:
    """测试虚拟进度条"""

    def test_dummy_progress_bar(self):
        """测试虚拟进度条所有方法"""
        from src.utils.progress_bar import DummyProgressBar

        # Arrange & Act - 所有方法都不应抛出异常
        dummy = DummyProgressBar()
        dummy.start()
        dummy.update(1)
        dummy.set_postfix(测试="值")
        dummy.close()

        # 测试上下文管理器
        with DummyProgressBar() as d:
            d.update(1)

    def test_dummy_spinner(self):
        """测试虚拟加载动画"""
        from src.utils.progress_bar import DummySpinner

        # Arrange & Act - 所有方法都不应抛出异常
        dummy = DummySpinner()
        dummy.start()
        dummy.stop()
        dummy.succeed()
        dummy.fail()


class TestGetProgressBar:
    """测试获取进度条函数"""

    def test_get_progress_bar_enabled(self):
        """测试获取启用的进度条"""
        from src.utils.progress_bar import get_progress_bar, ProgressBar

        # Act
        pbar = get_progress_bar(enabled=True, total=10, desc="测试")

        # Assert
        assert isinstance(pbar, ProgressBar)
        assert pbar.total == 10

    def test_get_progress_bar_disabled(self):
        """测试获取禁用的进度条"""
        from src.utils.progress_bar import get_progress_bar, DummyProgressBar

        # Act
        pbar = get_progress_bar(enabled=False, total=10, desc="测试")

        # Assert
        assert isinstance(pbar, DummyProgressBar)

    def test_get_spinner_enabled(self):
        """测试获取启用的spinner"""
        from src.utils.progress_bar import get_spinner, Spinner

        # Act
        spinner = get_spinner(enabled=True, desc="测试")

        # Assert
        assert isinstance(spinner, Spinner)

    def test_get_spinner_disabled(self):
        """测试获取禁用的spinner"""
        from src.utils.progress_bar import get_spinner, DummySpinner

        # Act
        spinner = get_spinner(enabled=False, desc="测试")

        # Assert
        assert isinstance(spinner, DummySpinner)
