"""
结构化日志模块 (Manifesto 要求)
使用 JSON 格式输出，便于日志分析和追踪
"""

import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict
from pathlib import Path

# 添加项目根目录到 Python 路径
SKILL_ROOT = Path(__file__).parent.parent.parent.parent


class JsonFormatter(logging.Formatter):
    """JSON 格式化器，输出结构化日志"""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 添加 trace_id（如果存在）
        if hasattr(record, 'trace_id'):
            log_entry['trace_id'] = record.trace_id

        # 添加异常信息（如果存在）
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)

        # 添加额外字段
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)

        return json.dumps(log_entry, ensure_ascii=False)


class Logger:
    """日志管理器，符合 Manifesto 要求的结构化日志"""

    def __init__(self, name: str = "ZenTaoHelper", level: str = "INFO", format_type: str = "json"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper(), logging.INFO))

        # 避免重复添加处理器
        if not self.logger.handlers:
            # 控制台处理器
            handler = logging.StreamHandler(sys.stdout)

            # 根据配置选择格式
            if format_type.lower() == "json":
                formatter = JsonFormatter()
            else:
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                )

            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def _log(self, level: str, message: str, extra: Dict[str, Any] = None, trace_id: str = None):
        """通用日志方法"""
        record = self.logger.makeRecord(
            self.logger.name,
            getattr(logging, level.upper()),
            fn=None,
            lno=0,
            msg=message,
            args=(),
            exc_info=None
        )

        if extra:
            record.extra_fields = extra
        if trace_id:
            record.trace_id = trace_id

        self.logger.handle(record)

    def debug(self, message: str, extra: Dict[str, Any] = None, trace_id: str = None):
        """调试日志"""
        self._log("debug", message, extra, trace_id)

    def info(self, message: str, extra: Dict[str, Any] = None, trace_id: str = None):
        """信息日志"""
        self._log("info", message, extra, trace_id)

    def warning(self, message: str, extra: Dict[str, Any] = None, trace_id: str = None):
        """警告日志"""
        self._log("warning", message, extra, trace_id)

    def error(self, message: str, extra: Dict[str, Any] = None, trace_id: str = None, exc_info=None):
        """错误日志"""
        if exc_info:
            self.logger.error(message, extra=extra, exc_info=exc_info)
        else:
            self._log("error", message, extra, trace_id)

    def critical(self, message: str, extra: Dict[str, Any] = None, trace_id: str = None):
        """严重错误日志"""
        self._log("critical", message, extra, trace_id)


def get_logger(name: str = "ZenTaoHelper", level: str = None, format_type: str = None) -> Logger:
    """获取日志实例"""
    # 从配置读取默认值
    if level is None or format_type is None:
        from .config_loader import get_config
        config = get_config()
        log_config = config.get_logging_config()
        if level is None:
            level = log_config.get('level', 'INFO')
        if format_type is None:
            format_type = log_config.get('format', 'json')

    return Logger(name, level, format_type)