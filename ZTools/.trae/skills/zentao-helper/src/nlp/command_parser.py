"""
命令解析器
将自然语言指令解析为结构化命令
"""

from typing import Dict, Any

from .intent_classifier import IntentClassifier
from .entity_extractor import EntityExtractor
from ..utils.logger import get_logger


class CommandParser:
    """
    命令解析器
    负责解析用户的自然语言指令
    """

    def __init__(self):
        self.logger = get_logger()
        self.intent_classifier = IntentClassifier()
        self.entity_extractor = EntityExtractor()

    def parse(self, text: str) -> Dict[str, Any]:
        """
        解析用户指令

        Args:
            text: 用户输入的文本

        Returns:
            解析结果字典，包含:
            - intent: 意图ID
            - entities: 实体字典
            - raw: 原始输入文本
            - confidence: 置信度（预留）
        """
        # 分类意图
        intent = self.intent_classifier.classify(text)

        # 提取实体
        entities = self.entity_extractor.extract_all(text)

        # 构建解析结果
        result = {
            'intent': intent,
            'entities': entities,
            'raw': text,
            'confidence': 0.9  # 默认置信度，预留
        }

        self.logger.info(
            f"命令解析: {text}",
            extra={
                'intent': intent,
                'entities': entities
            }
        )

        return result

    def get_help(self) -> str:
        """
        获取帮助信息

        Returns:
            帮助文本
        """
        help_text = """
ZenTao Helper 使用帮助

支持的指令：

1. 查看需求
   - 查看我的需求
   - 显示需求列表
   - 我的需求

2. 查看任务
   - 查看我的任务
   - 显示任务列表
   - 我的任务

3. 任务拆解
   - 拆解任务#123
   - 拆解任务#123为前端开发和后端开发
   - 拆分成A、B和C

4. 任务分配
   - 把任务#456分配给张三
   - 指派任务#789给wangxiaoming
   - @张三 任务#123

5. 帮助
   - 帮助
   - 能做什么

提示：
- 使用 # 或 任务# 来指定任务ID
- 使用 @用户名 或 给用户名 来指定用户
- 首次使用会提示登录禅道
"""
        return help_text