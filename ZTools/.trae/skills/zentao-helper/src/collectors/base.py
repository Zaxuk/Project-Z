"""
信息收集器基类
所有收集器继承此基类
"""

from abc import ABC, abstractmethod
from typing import Optional

from ..utils.logger import get_logger
from ..utils.response import ApiResponse
from ..zentao.api_client import ZentaoApiClient


class BaseCollector(ABC):
    """
    信息收集器基类
    定义收集器的通用接口
    """

    def __init__(self, api_client: ZentaoApiClient):
        self.logger = get_logger()
        self.api_client = api_client

    @abstractmethod
    def collect(self, **kwargs) -> ApiResponse:
        """
        收集信息

        Args:
            **kwargs: 查询参数

        Returns:
            收集结果
        """
        pass

    def _format_display(self, data: any) -> str:
        """
        格式化显示数据

        Args:
            data: 要显示的数据

        Returns:
            格式化后的文本
        """
        return str(data)