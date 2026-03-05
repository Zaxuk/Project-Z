# -*- coding: utf-8 -*-
"""
测试统一 API 响应结构
"""

import pytest
from datetime import datetime

from src.utils.response import ApiResponse, ApiError, ErrorCode


class TestApiError:
    """测试 API 错误信息"""

    def test_api_error_creation(self):
        """测试创建 API 错误"""
        # Act
        error = ApiError(code="TEST_ERROR", message="测试错误", details="详细错误信息")

        # Assert
        assert error.code == "TEST_ERROR"
        assert error.message == "测试错误"
        assert error.details == "详细错误信息"

    def test_api_error_without_details(self):
        """测试创建无详细信息的 API 错误"""
        # Act
        error = ApiError(code="TEST_ERROR", message="测试错误")

        # Assert
        assert error.code == "TEST_ERROR"
        assert error.message == "测试错误"
        assert error.details is None


class TestApiResponse:
    """测试统一 API 响应结构"""

    def test_success_response_creation(self):
        """测试创建成功响应"""
        # Act
        response = ApiResponse.success_response(data={"id": 123, "name": "测试"})

        # Assert
        assert response.success is True
        assert response.data == {"id": 123, "name": "测试"}
        assert response.error is None
        assert response.timestamp is not None

    def test_error_response_creation(self):
        """测试创建错误响应"""
        # Act
        response = ApiResponse.error_response(
            code=ErrorCode.API_ERROR,
            message="API 调用失败",
            details="详细错误信息"
        )

        # Assert
        assert response.success is False
        assert response.data is None
        assert response.error is not None
        assert response.error.code == ErrorCode.API_ERROR
        assert response.error.message == "API 调用失败"
        assert response.error.details == "详细错误信息"

    def test_error_response_without_details(self):
        """测试创建无详细信息的错误响应"""
        # Act
        response = ApiResponse.error_response(
            code=ErrorCode.TASK_NOT_FOUND,
            message="任务不存在"
        )

        # Assert
        assert response.success is False
        assert response.error.code == ErrorCode.TASK_NOT_FOUND
        assert response.error.message == "任务不存在"
        assert response.error.details is None

    def test_to_dict_success_response(self):
        """测试成功响应转字典"""
        # Arrange
        response = ApiResponse.success_response(data={"count": 10})

        # Act
        result = response.to_dict()

        # Assert
        assert result["success"] is True
        assert result["data"] == {"count": 10}
        assert "error" not in result
        assert "timestamp" in result

    def test_to_dict_error_response(self):
        """测试错误响应转字典"""
        # Arrange
        response = ApiResponse.error_response(
            code=ErrorCode.SESSION_EXPIRED,
            message="会话已过期",
            details="请重新登录"
        )

        # Act
        result = response.to_dict()

        # Assert
        assert result["success"] is False
        assert "data" not in result
        assert result["error"]["code"] == ErrorCode.SESSION_EXPIRED
        assert result["error"]["message"] == "会话已过期"
        assert result["error"]["details"] == "请重新登录"

    def test_to_dict_error_without_details(self):
        """测试无详细信息的错误响应转字典"""
        # Arrange
        response = ApiResponse.error_response(
            code=ErrorCode.NETWORK_ERROR,
            message="网络错误"
        )

        # Act
        result = response.to_dict()

        # Assert
        assert result["success"] is False
        assert result["error"]["code"] == ErrorCode.NETWORK_ERROR
        assert result["error"]["message"] == "网络错误"
        assert "details" not in result["error"]

    def test_post_init_sets_timestamp(self):
        """测试 __post_init__ 自动设置时间戳"""
        # Act
        response = ApiResponse(success=True)

        # Assert
        assert response.timestamp is not None
        assert isinstance(response.timestamp, str)

    def test_post_init_preserves_custom_timestamp(self):
        """测试保留自定义时间戳"""
        # Arrange
        custom_timestamp = "2024-03-15T10:30:00"

        # Act
        response = ApiResponse(success=True, timestamp=custom_timestamp)

        # Assert
        assert response.timestamp == custom_timestamp


class TestErrorCode:
    """测试错误码常量"""

    def test_error_code_values(self):
        """测试错误码值"""
        assert ErrorCode.SESSION_EXPIRED == "SESSION_EXPIRED"
        assert ErrorCode.LOGIN_FAILED == "LOGIN_FAILED"
        assert ErrorCode.TASK_NOT_FOUND == "TASK_NOT_FOUND"
        assert ErrorCode.STORY_NOT_FOUND == "STORY_NOT_FOUND"
        assert ErrorCode.USER_NOT_FOUND == "USER_NOT_FOUND"
        assert ErrorCode.API_ERROR == "API_ERROR"
        assert ErrorCode.NETWORK_ERROR == "NETWORK_ERROR"
        assert ErrorCode.UNKNOWN_INTENT == "UNKNOWN_INTENT"
        assert ErrorCode.MISSING_PARAMETER == "MISSING_PARAMETER"
        assert ErrorCode.INVALID_PARAMETER == "INVALID_PARAMETER"
        assert ErrorCode.PERMISSION_DENIED == "PERMISSION_DENIED"
        assert ErrorCode.TIMEOUT == "TIMEOUT"
