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
        - 需求 123

        Args:
            text: 用户输入的文本

        Returns:
            需求ID字符串，如果未找到返回 None
        """
        patterns = [
            r'(?:需求|story)#(\d+)',  # 需求#123
            r'(?:需求|story)\s*(\d+)',  # 需求123 或 需求 123
            r'(\d+)\s*(?:号|编号|id)\s*(?:需求|story)',  # 123号需求
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                story_id = match.group(1)
                if self.debug:
                    self.logger.debug(f"提取需求ID: {text} -> {story_id}")
                return story_id

        # 检查是否包含"需求"和数字的组合（用于处理"需求11530，拆解任务"这种格式）
        story_pattern = r'需求(\d+)'
        match = re.search(story_pattern, text)
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
        # 先检查是否包含"未分配"，如果包含则不提取用户名
        if '未分配' in text:
            return None
        
        patterns = [
            r'@(\w+)',  # @张三
            r'\b(?:给|指派|分配)\s*(?:给)?\s*(\w+)\b',  # 给张三、指派给张三
            r'\b(?:指定|指定给)\s*(\w+)\b',  # 指定张三
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                username = match.group(1)
                # 过滤常见的非用户名词汇
                if username not in ['需求', '任务', '给']:
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
        - 所有/全部（返回 'all'）

        Args:
            text: 用户输入的文本

        Returns:
            状态字符串，如果未找到返回 None
        """
        # 检查是否要求查看所有
        if '所有' in text or '全部' in text:
            if self.debug:
                self.logger.debug(f"提取状态: {text} -> all")
            return 'all'
        
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

    def extract_filter_no_task(self, text: str) -> bool:
        """
        提取是否过滤未创建任务的需求

        支持格式：
        - 未创建任务
        - 没有任务
        - 没建任务
        - 未建任务
        - 未分配
        - 未分配任务

        Args:
            text: 用户输入的文本

        Returns:
            是否需要过滤未创建任务的需求
        """
        keywords = ['未创建任务', '没有任务', '没建任务', '未建任务', '无任务', '未分配', '未分配任务']
        for keyword in keywords:
            if keyword in text:
                if self.debug:
                    self.logger.debug(f"提取过滤条件: {text} -> 未创建任务")
                return True
        return False

    def extract_keywords(self, text: str) -> Optional[List[str]]:
        """
        提取需求标题关键字

        支持格式：
        - 包含"面板"的需求 / 包含'面板'的需求 / 包含面板
        - 标题包含订单
        - 关键字是首页面板
        - 过滤面板相关的
        - 关于面板的
        - xxx相关的需求

        Args:
            text: 用户输入的文本

        Returns:
            关键字列表，如果未找到返回 None
        """
        keywords = []
        
        # 1. 匹配 "包含'xxx'" 或 "包含\"xxx\"" 格式（带引号的关键字）
        quoted_pattern = r'包含["\']([^"\']+?)["\']'
        matches = re.findall(quoted_pattern, text)
        for match in matches:
            keyword = match.strip()
            if keyword and len(keyword) >= 2:
                keywords.append(keyword)
        
        # 2. 匹配 "包含xxx" 格式（不带引号，但xxx后面跟着"的需求"或结束）
        # 排除一些常见词
        contain_pattern = r'包含([^"\'\s]{2,20})(?:的?需求|的?标题|$|\s)'
        matches = re.findall(contain_pattern, text)
        exclude_words = ['未创建任务', '没有任务', '任务', '需求', '查询', '过滤']
        for match in matches:
            keyword = match.strip()
            if keyword and keyword not in exclude_words:
                keywords.append(keyword)
        
        # 3. 匹配 "关键字是xxx" 格式
        keyword_is_pattern = r'关键字是["\']?([^"\'\s]{2,}?)["\']?(?:的|需求|$|\s)'
        match = re.search(keyword_is_pattern, text)
        if match:
            keyword = match.group(1).strip()
            if keyword:
                keywords.append(keyword)
        
        # 4. 匹配 "关于xxx的" 格式
        about_pattern = r'关于["\']?([^"\'\s]{2,}?)["\']?的'
        match = re.search(about_pattern, text)
        if match:
            keyword = match.group(1).strip()
            if keyword:
                keywords.append(keyword)
        
        # 5. 匹配 "xxx相关" 格式（但排除常见词）
        related_pattern = r'([^\s"\']{2,20}?)相关'
        matches = re.findall(related_pattern, text)
        for match in matches:
            keyword = match.strip()
            if keyword and keyword not in exclude_words:
                keywords.append(keyword)
        
        # 6. 匹配 "标题包含xxx" 格式
        title_contain_pattern = r'标题包含["\']?([^"\'\s]{2,}?)["\']?(?:的|需求|$|\s)'
        match = re.search(title_contain_pattern, text)
        if match:
            keyword = match.group(1).strip()
            if keyword:
                keywords.append(keyword)

        # 去重并保持顺序
        seen = set()
        unique_keywords = []
        for k in keywords:
            k_lower = k.lower()
            if k_lower not in seen:
                seen.add(k_lower)
                unique_keywords.append(k)

        if unique_keywords:
            if self.debug:
                self.logger.debug(f"提取关键字: {text} -> {unique_keywords}")
            return unique_keywords

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
            'status': self.extract_status(text),
            'filter_no_task': self.extract_filter_no_task(text),
            'keywords': self.extract_keywords(text)
        }