"""
意图分类器
基于关键词匹配的轻量级 NLP 模块
预留 LLM API 扩展接口
"""

import re
from typing import Dict, List, Optional

from ..utils.logger import get_logger
from ..utils.config_loader import get_config


class IntentClassifier:
    """
    意图分类器
    将自然语言指令分类为预定义的意图
    """

    # 意图定义：意图ID -> 关键词列表
    INTENTS = {
        'query_stories': [
            '需求', 'story', '需求列表', '我的需求', '显示需求',
            '查看需求', '展示需求', 'stories'
        ],
        'query_tasks': [
            '任务', 'task', '任务列表', '我的任务', '显示任务',
            '查看任务', '展示任务', 'tasks'
        ],
        'split_task': [
            '拆解', '分解', 'split', '拆分', '拆成',
            '拆分为', '拆解成', '分解成'
        ],
        'assign_task': [
            '分配', '指派', 'assign', '给',
            '指派给', '分配给'
        ],
        'help': [
            '帮助', 'help', '怎么用', '能做什么',
            '支持什么', '如何使用'
        ]
    }

    def __init__(self):
        self.logger = get_logger()
        self.config = get_config()
        self.debug = self.config.get_nlp_config().get('debug', False)

        # 预留：LLM 客户端（未来扩展）
        self._llm_client = None
        self._llm_enabled = self.config.get_nlp_config().get('llm', {}).get('enabled', False)

        if self._llm_enabled:
            self._init_llm_client()

    def _init_llm_client(self):
        """
        初始化 LLM 客户端（预留扩展）
        未来可以集成 OpenAI、DeepSeek 等 LLM API
        """
        try:
            llm_config = self.config.get_nlp_config().get('llm', {})
            provider = llm_config.get('provider', '')
            api_key = llm_config.get('api_key', '')
            model = llm_config.get('model', '')

            if provider == 'openai':
                # self._llm_client = OpenAIClient(api_key, model)
                self.logger.info("OpenAI LLM 客户端已初始化（预留）")
            elif provider == 'deepseek':
                # self._llm_client = DeepSeekClient(api_key, model)
                self.logger.info("DeepSeek LLM 客户端已初始化（预留）")
            else:
                self.logger.warning(f"不支持的 LLM 提供商: {provider}")

        except Exception as e:
            self.logger.error(f"初始化 LLM 客户端失败: {str(e)}")

    def classify(self, text: str) -> str:
        """
        分类用户意图

        Args:
            text: 用户输入的文本

        Returns:
            意图ID，如果无法识别返回 'unknown'
        """
        # 如果启用了 LLM，使用 LLM 分类（预留扩展）
        if self._llm_enabled and self._llm_client:
            return self._classify_with_llm(text)

        # 否则使用关键词匹配
        return self._classify_with_keywords(text)

    def _classify_with_keywords(self, text: str) -> str:
        """
        使用关键词匹配分类

        Args:
            text: 用户输入的文本

        Returns:
            意图ID
        """
        text_lower = text.lower()

        best_intent = 'unknown'
        max_score = 0

        for intent, keywords in self.INTENTS.items():
            # 计算匹配分数（匹配的关键词数量）
            score = sum(1 for kw in keywords if kw.lower() in text_lower)

            if score > max_score:
                max_score = score
                best_intent = intent

        if self.debug:
            self.logger.debug(
                f"意图分类: {text} -> {best_intent} (score: {max_score})",
                extra={'input_text': text, 'intent': best_intent, 'score': max_score}
            )

        return best_intent

    def _classify_with_llm(self, text: str) -> str:
        """
        使用 LLM 分类（预留扩展）

        Args:
            text: 用户输入的文本

        Returns:
            意图ID
        """
        # 预留：LLM 分类逻辑
        # 示例：
        # prompt = f"""
        # 你是一个意图分类器。请将以下用户输入分类为以下意图之一：
        # {list(self.INTENTS.keys())}
        #
        # 用户输入: {text}
        #
        # 只返回意图ID，不要返回其他内容。
        # """
        #
        # response = self._llm_client.chat([{"role": "user", "content": prompt}])
        # return response.intent

        self.logger.warning("LLM 分类功能尚未实现，使用关键词匹配")
        return self._classify_with_keywords(text)

    def get_all_intents(self) -> List[str]:
        """获取所有支持的意图"""
        return list(self.INTENTS.keys())

    def add_intent(self, intent_id: str, keywords: List[str]):
        """
        动态添加意图（用于扩展）

        Args:
            intent_id: 意图ID
            keywords: 关键词列表
        """
        self.INTENTS[intent_id] = keywords
        self.logger.info(f"添加新意图: {intent_id}")