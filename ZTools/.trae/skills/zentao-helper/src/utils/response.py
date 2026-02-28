"""
统一 API 响应结构 (Manifesto 要求)
所有内部 API 必须返回统一的 JSON 结构
"""

from datetime import datetime
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class ApiError:
    """API 错误信息"""
    code: str
    message: str
    details: Optional[str] = None


@dataclass
class ApiResponse:
    """
    统一 API 响应结构
    符合 Manifesto 要求的内部响应标准
    """
    success: bool
    data: Any = None
    error: Optional[ApiError] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "success": self.success,
            "timestamp": self.timestamp
        }

        if self.data is not None:
            result["data"] = self.data

        if self.error is not None:
            result["error"] = {
                "code": self.error.code,
                "message": self.error.message
            }
            if self.error.details:
                result["error"]["details"] = self.error.details

        return result

    @classmethod
    def success_response(cls, data: Any = None) -> 'ApiResponse':
        """创建成功响应"""
        return cls(success=True, data=data)

    @classmethod
    def error_response(cls, code: str, message: str, details: str = None) -> 'ApiResponse':
        """创建错误响应"""
        error = ApiError(code=code, message=message, details=details)
        return cls(success=False, error=error)


# 常用错误码定义
class ErrorCode:
    """错误码常量"""
    SESSION_EXPIRED = "SESSION_EXPIRED"
    LOGIN_FAILED = "LOGIN_FAILED"
    TASK_NOT_FOUND = "TASK_NOT_FOUND"
    STORY_NOT_FOUND = "STORY_NOT_FOUND"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    API_ERROR = "API_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"
    UNKNOWN_INTENT = "UNKNOWN_INTENT"
    MISSING_PARAMETER = "MISSING_PARAMETER"
    INVALID_PARAMETER = "INVALID_PARAMETER"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    TIMEOUT = "TIMEOUT"


# 常用错误消息
class ErrorMessage:
    """错误消息常量"""
    SESSION_EXPIRED = "会话已过期，请重新登录"
    LOGIN_FAILED = "登录失败，请检查用户名和密码"
    TASK_NOT_FOUND = "任务不存在或无权访问"
    STORY_NOT_FOUND = "需求不存在或无权访问"
    USER_NOT_FOUND = "用户不存在"
    API_ERROR = "禅道 API 调用失败"
    NETWORK_ERROR = "网络连接失败"
    UNKNOWN_INTENT = "无法理解您的指令，请尝试更明确的表达"
    MISSING_PARAMETER = "缺少必要参数"
    INVALID_PARAMETER = "参数格式不正确"
    PERMISSION_DENIED = "没有权限执行此操作"
    TIMEOUT = "请求超时"