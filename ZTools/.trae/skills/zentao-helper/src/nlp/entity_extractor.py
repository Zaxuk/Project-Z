"""
实体提取器
从自然语言中提取任务ID、用户名等实体
"""

import re
from typing import Optional, List, Dict

from ..utils.logger import get_logger
from ..utils.config_loader import get_config


class EntityExtractor:
    """
    实体提取器
    提取各种实体：任务ID、用户名、需求ID等
    """

    def __init__(self):
        self.logger = get_logger()
        self.config = get_config()
        self.debug = self.config.get_nlp_config().get('debug', False)

    def extract_task_id(self, text: str) -> Optional[str]:
        """
        提取任务ID

        支持格式：
        - #123
        - 任务#123
        - task#123
        - 任务123
        - 123号任务

        Args:
            text: 用户输入的文本

        Returns:
            任务ID字符串，如果未找到返回 None
        """
        patterns = [
            r'(?:任务|task|需求|story)?#(\d+)',  # #123 或 任务#123
            r'(?:任务|task)\s*(\d+)',  # 任务123
            r'(\d+)\s*(?:号|编号|id)\s*(?:任务|task|需求|story)?',  # 123号任务
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                task_id = match.group(1)
                if self.debug:
                    self.logger.debug(f"提取任务ID: {text} -> {task_id}")
                return task_id

        return None

    def extract_story_id(self, text: str) -> Optional[str]:
        """
        提取需求ID

        支持格式：
        - #123（如果是上下文是需求）
        - 需求#123
        - story#123
        - 需求123

        Args:
            text: 用户输入的文本

        Returns:
            需求ID字符串，如果未找到返回 None
        """
        patterns = [
            r'(?:需求|story)#(\d+)',  # 需求#123
            r'(?:需求|story)\s*(\d+)',  # 需求123
            r'(\d+)\s*(?:号|编号|id)\s*(?:需求|story)',  # 123号需求
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                story_id = match.group(1)
                if self.debug:
                    self.logger.debug(f"提取需求ID: {text} -> {story_id}")
                return story_id

        return None

    def extract_username(self, text: str) -> Optional[str]:
        """
        提取用户名

        支持格式：
        - @张三
        - 给张三
        - 指派给张三
        - 分配给张三

        Args:
            text: 用户输入的文本

        Returns:
            用户名字符串，如果未找到返回 None
        """
        patterns = [
            r'@(\w+)',  # @张三
            r'(?:给|指派|分配)\s*(?:给|给)?\s*(\w+)',  # 给张三、指派给张三
            r'(?:指定|指定给)\s*(\w+)',  # 指定张三
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                username = match.group(1)
                if self.debug:
                    self.logger.debug(f"提取用户名: {text} -> {username}")
                return username

        return None

    def extract_subtask_names(self, text: str) -> Optional[List[str]]:
        """
        从文本中提取子任务名称

        支持格式：
        - 拆解任务#123为前端开发和后端开发
        - 拆分为A、B和C
        - 分解成A, B, C

        Args:
            text: 用户输入的文本

        Returns:
            子任务名称列表，如果未找到返回 None
        """
        # 尝试从"拆成/拆分为/分解为"等关键词后提取
        patterns = [
            r'拆(?:成|分为|解成|解为)\s*(.+)',  # 拆成...
            r'分解为\s*(.+)',  # 分解为...
            r'拆分成\s*(.+)',  # 拆分成...
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                subtask_text = match.group(1)

                # 按分隔符拆分：顿号、逗号、和、与
                subtasks = re.split(r'[、,和与\s]+', subtask_text.strip())
                subtasks = [s.strip() for s in subtasks if s.strip()]

                if subtasks:
                    if self.debug:
                        self.logger.debug(f"提取子任务: {text} -> {subtasks}")
                    return subtasks

        return None

    def extract_status(self, text: str) -> Optional[str]:
        """
        提取状态过滤

        支持格式：
        - 未开始
        - 进行中
        - 已完成
        - 已关闭

        Args:
            text: 用户输入的文本

        Returns:
            状态字符串，如果未找到返回 None
        """
        status_map = {
            '未开始': 'wait',
            '待办': 'wait',
            '进行中': 'doing',
            '正在做': 'doing',
            '已完成': 'done',
            '完成': 'done',
            '已关闭': 'closed',
            '关闭': 'closed'
        }

        for cn_status, en_status in status_map.items():
            if cn_status in text:
                if self.debug:
                    self.logger.debug(f"提取状态: {text} -> {en_status}")
                return en_status

        return None

    def extract_all(self, text: str) -> Dict[str, any]:
        """
        提取所有实体

        Args:
            text: 用户输入的文本

        Returns:
            包含所有实体的字典
        """
        return {
            'task_id': self.extract_task_id(text),
            'story_id': self.extract_story_id(text),
            'username': self.extract_username(text),
            'subtask_names': self.extract_subtask_names(text),
            'status': self.extract_status(text)
        }