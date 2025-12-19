"""意图识别器

从自然语言指令中识别用户的操作意图
"""

import re
from typing import Optional

import jieba

from aerotest.core.funnel.l1.action_patterns import (
    ACTION_KEYWORDS,
    ACTION_PRIORITY,
    CONTEXT_HINTS,
)
from aerotest.core.funnel.types import ActionType
from aerotest.utils import get_logger

logger = get_logger("aerotest.funnel.l1.intent")


class IntentRecognizer:
    """意图识别器
    
    识别用户想要执行的动作类型
    
    策略：
    1. 关键词匹配：检查指令中是否包含动作关键词
    2. 模式匹配：使用正则表达式匹配动作模式
    3. 上下文推断：根据目标元素类型推断动作
    4. 优先级排序：当匹配到多个动作时，选择优先级最高的
    
    Example:
        ```python
        recognizer = IntentRecognizer()
        
        action = recognizer.recognize("点击提交按钮")
        assert action == ActionType.CLICK
        
        action = recognizer.recognize("输入用户名")
        assert action == ActionType.INPUT
        ```
    """
    
    def __init__(self):
        """初始化意图识别器"""
        self._load_keywords()
        logger.debug("意图识别器初始化完成")
    
    def _load_keywords(self):
        """加载关键词到 jieba 词典"""
        for action, data in ACTION_KEYWORDS.items():
            for keyword in data["keywords"]:
                jieba.add_word(keyword, freq=1000)
    
    def recognize(self, text: str) -> ActionType:
        """
        识别操作意图
        
        Args:
            text: 自然语言指令
            
        Returns:
            动作类型
        """
        text = text.strip().lower()
        
        if not text:
            logger.warning("空文本，返回 UNKNOWN")
            return ActionType.UNKNOWN
        
        # 1. 关键词匹配
        matched_actions = self._match_by_keywords(text)
        
        if len(matched_actions) == 1:
            action = matched_actions[0]
            logger.debug(f"关键词匹配成功: '{text}' -> {action}")
            return action
        
        # 2. 如果有多个匹配，使用上下文推断
        if len(matched_actions) > 1:
            action = self._infer_from_context(text, matched_actions)
            if action:
                logger.debug(f"上下文推断成功: '{text}' -> {action}")
                return action
            
            # 3. 使用优先级选择
            action = self._select_by_priority(matched_actions)
            logger.debug(f"优先级选择: '{text}' -> {action}")
            return action
        
        # 4. 模式匹配
        action = self._match_by_patterns(text)
        if action:
            logger.debug(f"模式匹配成功: '{text}' -> {action}")
            return action
        
        # 5. 默认返回 CLICK（最常见的操作）
        logger.warning(f"无法识别意图，默认返回 CLICK: '{text}'")
        return ActionType.CLICK
    
    def _match_by_keywords(self, text: str) -> list[ActionType]:
        """
        通过关键词匹配动作
        
        Args:
            text: 文本
            
        Returns:
            匹配到的动作列表
        """
        # 分词
        words = list(jieba.cut(text))
        words_lower = [w.lower() for w in words]
        
        matched = []
        
        for action, data in ACTION_KEYWORDS.items():
            keywords = data["keywords"]
            
            # 检查是否有关键词在分词结果中
            for keyword in keywords:
                if keyword.lower() in words_lower or keyword.lower() in text:
                    matched.append(action)
                    break
        
        return matched
    
    def _match_by_patterns(self, text: str) -> Optional[ActionType]:
        """
        通过模式匹配动作
        
        Args:
            text: 文本
            
        Returns:
            匹配到的动作
        """
        for action, data in ACTION_KEYWORDS.items():
            patterns = data["patterns"]
            
            for pattern in patterns:
                if re.match(pattern, text):
                    return action
        
        return None
    
    def _infer_from_context(
        self,
        text: str,
        candidates: list[ActionType],
    ) -> Optional[ActionType]:
        """
        从上下文推断动作
        
        Args:
            text: 文本
            candidates: 候选动作列表
            
        Returns:
            推断的动作
        """
        # 检查是否包含上下文关键词
        for hint, action in CONTEXT_HINTS.items():
            if hint in text and action in candidates:
                return action
        
        return None
    
    def _select_by_priority(self, actions: list[ActionType]) -> ActionType:
        """
        按优先级选择动作
        
        Args:
            actions: 动作列表
            
        Returns:
            优先级最高的动作
        """
        if not actions:
            return ActionType.UNKNOWN
        
        # 按优先级排序
        sorted_actions = sorted(
            actions,
            key=lambda a: ACTION_PRIORITY.get(a, 0),
            reverse=True,
        )
        
        return sorted_actions[0]
    
    def get_confidence(self, text: str, action: ActionType) -> float:
        """
        获取识别置信度
        
        Args:
            text: 文本
            action: 动作类型
            
        Returns:
            置信度（0.0-1.0）
        """
        text_lower = text.lower()
        
        # 检查关键词匹配数量
        keywords = ACTION_KEYWORDS.get(action, {}).get("keywords", [])
        match_count = sum(
            1 for keyword in keywords
            if keyword.lower() in text_lower
        )
        
        if match_count == 0:
            return 0.3  # 默认置信度
        elif match_count == 1:
            return 0.7  # 单个关键词匹配
        else:
            return 0.95  # 多个关键词匹配
