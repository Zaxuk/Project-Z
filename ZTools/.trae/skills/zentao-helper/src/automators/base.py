"""
自动化操作器基类
所有自动化操作器继承此基类
"""

from abc import ABC, abstractmethod
from typing import Optional

from ..utils.logger import get_logger
from ..utils.response import ApiResponse
from ..zentao.api_client import ZentaoApiClient


class BaseAutomator(ABC):
    """
    自动化操作器基类
    定义自动化操作的通用接口
    """

    def __init__(self, api_client: ZentaoApiClient):
        self.logger = get_logger()
        self.api_client = api_client

    @abstractmethod
    def execute(self, **kwargs) -> ApiResponse:
        """
        执行自动化操作

        Args:
            **kwargs: 操作参数

        Returns:
            操作结果
        """
        pass

    def _confirm_action(self, message: str) -> bool:
        """
        确认操作（预留）

        Args:
            message: 确认消息

        Returns:
            是否确认
        """
        # 在实际使用中，这里可以集成 iFlow 的确认机制
        return True