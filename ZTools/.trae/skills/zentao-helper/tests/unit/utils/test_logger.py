# -*- coding: utf-8 -*-
"""
测试结构化日志模块
"""

import pytest
import json
import logging
import sys
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

from src.utils.logger import JsonFormatter, Logger, get_logger


class TestJsonFormatter:
    """测试 JSON 格式化器"""

    def test_format_basic_log(self):
        """测试基本日志格式化"""
        # Arrange
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="测试消息",
            args=(),
            exc_info=None
        )
        record.module = "test_module"
        record.funcName = "test_func"

        # Act
        result = formatter.format(record)

        # Assert
        log_entry = json.loads(result)
        assert log_entry['level'] == 'INFO'
        assert log_entry['message'] == '测试消息'
        assert log_entry['module'] == 'test_module'
        assert log_entry['function'] == 'test_func'
        assert log_entry['line'] == 10

    def test_format_with_trace_id(self):
        """测试带 trace_id 的日志"""
        # Arrange
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.DEBUG,
            pathname="test.py",
            lineno=20,
            msg="调试消息",
            args=(),
            exc_info=None
        )
        record.trace_id = "abc-123-xyz"

        # Act
        result = formatter.format(record)

        # Assert
        log_entry = json.loads(result)
        assert log_entry['trace_id'] == "abc-123-xyz"

    def test_format_with_extra_fields(self):
        """测试带额外字段的日志"""
        # Arrange
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.WARNING,
            pathname="test.py",
            lineno=30,
            msg="警告消息",
            args=(),
            exc_info=None
        )
        record.extra_fields = {"user_id": "123", "action": "login"}

        # Act
        result = formatter.format(record)

        # Assert
        log_entry = json.loads(result)
        assert log_entry['user_id'] == "123"
        assert log_entry['action'] == "login"

    def test_format_with_exception(self):
        """测试带异常的日志"""
        # Arrange
        formatter = JsonFormatter()
        try:
            raise ValueError("测试异常")
        except ValueError:
            record = logging.LogRecord(
                name="test",
                level=logging.ERROR,
                pathname="test.py",
                lineno=40,
                msg="错误消息",
                args=(),
                exc_info=sys.exc_info()
            )

        # Act
        result = formatter.format(record)

        # Assert
        log_entry = json.loads(result)
        assert 'exception' in log_entry
        assert 'ValueError' in log_entry['exception']


class TestLogger:
    """测试日志管理器"""

    def test_init(self):
        """测试初始化"""
        logger = Logger(name="TestLogger", level="DEBUG", format_type="json")
        assert logger.logger.name == "TestLogger"
        assert logger.logger.level == logging.DEBUG

    def test_init_with_text_format(self):
        """测试文本格式初始化"""
        log = Logger(name="TextLogger", level="INFO", format_type="text")
        assert log.logger.name == "TextLogger"
        assert log.logger.level == logging.INFO

    def test_logger_handlers_cleared_on_init(self):
        """测试初始化时清除现有处理器"""
        # 创建第一个 logger
        logger1 = Logger(name="SameLogger", level="DEBUG")
        initial_handlers_count = len(logger1.logger.handlers)

        # 创建同名 logger，应该清除之前的 handlers
        logger2 = Logger(name="SameLogger", level="INFO")
        # 处理器应该被替换而不是累加
        assert len(logger2.logger.handlers) == initial_handlers_count


class TestGetLogger:
    """测试获取日志实例"""

    @patch('src.utils.config_loader.get_config')
    def test_get_logger_with_defaults(self, mock_get_config):
        """测试使用默认配置获取日志"""
        # Arrange
        mock_config = Mock()
        mock_config.get_logging_config.return_value = {
            'level': 'DEBUG',
            'format': 'json'
        }
        mock_get_config.return_value = mock_config

        # Act
        logger = get_logger()

        # Assert
        assert isinstance(logger, Logger)

    @patch('src.utils.config_loader.get_config')
    def test_get_logger_with_custom_params(self, mock_get_config):
        """测试使用自定义参数获取日志"""
        # Arrange
        mock_config = Mock()
        mock_config.get_logging_config.return_value = {}
        mock_get_config.return_value = mock_config

        # Act
        logger = get_logger(name="CustomLogger", level="WARNING", format_type="text")

        # Assert
        assert logger.logger.name == "CustomLogger"
        assert logger.logger.level == logging.WARNING
