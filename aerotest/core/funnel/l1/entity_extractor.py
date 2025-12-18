"""实体提取�?

从自然语言指令中提取目标元素的特征信息
"""

import re
from typing import Optional

import jieba

from aerotest.core.funnel.l1.element_types import (
    COMMON_ELEMENT_NAMES,
    CONTEXT_PATTERNS,
    ELEMENT_ATTRIBUTE_HINTS,
    ELEMENT_TYPE_KEYWORDS,
)
from aerotest.core.funnel.types import ElementType
from aerotest.utils import get_logger

logger = get_logger("aerotest.funnel.l1.entity")


class EntityExtractor:
    """实体提取�?
    
    从自然语言中提取目标元素的特征�?
    - 目标描述：元素的文本描述
    - 元素类型：button, input, link �?
    - 关键词：用于匹配的关键词列表
    - 属性提示：可能有用的属性信�?
    
    策略�?
    1. 去除动作词：移除已知的动作关键词
    2. 类型识别：识别元素类�?
    3. 关键词提取：提取有效的关键词
    4. 属性推断：推断可能的属�?
    
    Example:
        ```python
        extractor = EntityExtractor()
        
        result = extractor.extract("点击提交按钮")
        # {
        #     "target": "提交按钮",
        #     "target_type": ElementType.BUTTON,
        #     "keywords": ["提交", "按钮"],
        #     "attributes": {"type": "submit"}
        # }
        ```
    """
    
    def __init__(self):
        """初始化实体提取器"""
        self._load_keywords()
        logger.debug("实体提取器初始化完成")
    
    def _load_keywords(self):
        """加载关键词到 jieba 词典"""
        # 添加元素类型关键�?
        for element_type, data in ELEMENT_TYPE_KEYWORDS.items():
            for keyword in data["keywords"]:
                jieba.add_word(keyword, freq=500)
        
        # 添加常见元素�?
        for name in COMMON_ELEMENT_NAMES.keys():
            jieba.add_word(name, freq=800)
    
    def extract(self, text: str, action_keywords: Optional[list[str]] = None) -> dict:
        """
        提取目标元素信息
        
        Args:
            text: 自然语言指令
            action_keywords: 动作关键词列表（用于过滤�?
            
        Returns:
            包含目标信息的字典：
            - target: 目标描述（原始文本）
            - target_type: 元素类型
            - keywords: 关键词列�?
            - attributes: 属性提�?
        """
        text = text.strip()
        
        if not text:
            logger.warning("空文本，返回空结�?)
            return self._empty_result()
        
        # 1. 移除动作�?
        target_text = self._remove_action_words(text, action_keywords or [])
        
        # 2. 识别元素类型
        element_type = self._recognize_element_type(target_text)
        
        # 3. 提取关键�?
        keywords = self._extract_keywords(target_text, element_type)
        
        # 4. 推断属�?
        attributes = self._infer_attributes(target_text, element_type)
        
        result = {
            "target": target_text if target_text else text,
            "target_type": element_type,
            "keywords": keywords,
            "attributes": attributes,
        }
        
        logger.debug(f"实体提取: '{text}' -> {result}")
        return result
    
    def _remove_action_words(self, text: str, action_keywords: list[str]) -> str:
        """
        移除动作�?
        
        Args:
            text: 原始文本
            action_keywords: 要移除的动作关键�?
            
        Returns:
            移除动作词后的文�?
        """
        result = text
        
        # 移除常见的动作词
        common_actions = [
            "点击", "�?, "选择", "单击", "双击",
            "输入", "填写", "录入", "键入",
            "打开", "访问", "跳转",
            "等待", "暂停",
            "click", "input", "select", "open", "wait",
        ]
        
        all_actions = list(set(common_actions + action_keywords))
        
        for action in all_actions:
            # 从开头移�?
            if result.startswith(action):
                result = result[len(action):].strip()
        
        return result
    
    def _recognize_element_type(self, text: str) -> Optional[ElementType]:
        """
        识别元素类型
        
        Args:
            text: 目标文本
            
        Returns:
            元素类型
        """
        text_lower = text.lower()
        
        # 1. 精确匹配常见名称
        for name, element_type in COMMON_ELEMENT_NAMES.items():
            if name in text:
                return element_type
        
        # 2. 关键词匹�?
        matched_types = []
        for element_type, data in ELEMENT_TYPE_KEYWORDS.items():
            keywords = data["keywords"]
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    matched_types.append(element_type)
                    break
        
        if len(matched_types) == 1:
            return matched_types[0]
        
        # 3. 模式匹配
        for element_type, data in ELEMENT_TYPE_KEYWORDS.items():
            patterns = data["patterns"]
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return element_type
        
        # 4. 上下文推�?
        for pattern, element_type in CONTEXT_PATTERNS.items():
            if pattern in text:
                return element_type
        
        # 5. 如果有多个匹配，选择最具体�?
        if matched_types:
            # 优先级：input/button > 其他
            for et in [ElementType.INPUT, ElementType.BUTTON]:
                if et in matched_types:
                    return et
            return matched_types[0]
        
        return None
    
    def _extract_keywords(
        self,
        text: str,
        element_type: Optional[ElementType],
    ) -> list[str]:
        """
        提取关键�?
        
        Args:
            text: 目标文本
            element_type: 元素类型
            
        Returns:
            关键词列�?
        """
        keywords = []
        
        # 分词
        words = list(jieba.cut(text))
        
        # 过滤无意义的�?
        stop_words = ["�?, "�?, "�?, "�?, "�?, "�?, "�?, "�?, "�?]
        
        for word in words:
            word = word.strip()
            if word and word not in stop_words and len(word) > 0:
                keywords.append(word)
        
        # 添加原始文本（如果不太长�?
        if len(text) <= 20 and text not in keywords:
            keywords.append(text)
        
        # 去重但保持顺�?
        seen = set()
        unique_keywords = []
        for keyword in keywords:
            if keyword not in seen:
                seen.add(keyword)
                unique_keywords.append(keyword)
        
        return unique_keywords
    
    def _infer_attributes(
        self,
        text: str,
        element_type: Optional[ElementType],
    ) -> dict[str, str]:
        """
        推断元素属�?
        
        Args:
            text: 目标文本
            element_type: 元素类型
            
        Returns:
            属性字�?
        """
        attributes = {}
        
        if not element_type:
            return attributes
        
        # 根据元素类型推断常见属�?
        hints = ELEMENT_ATTRIBUTE_HINTS.get(element_type, [])
        
        for hint in hints:
            if "=" in hint:
                key, value = hint.split("=", 1)
                # 只添加第一个（最可能的）
                if key not in attributes:
                    attributes[key] = value
                    break
        
        # 特殊推断：根据文本内�?
        text_lower = text.lower()
        
        # 提交按钮
        if "提交" in text or "submit" in text_lower:
            attributes["type"] = "submit"
        
        # 密码输入�?
        if "密码" in text or "password" in text_lower:
            attributes["type"] = "password"
        
        # 邮箱输入�?
        if "邮箱" in text or "email" in text_lower:
            attributes["type"] = "email"
        
        # 搜索按钮/输入�?
        if "搜索" in text or "search" in text_lower:
            if element_type == ElementType.INPUT:
                attributes["type"] = "search"
            attributes["role"] = "search"
        
        return attributes
    
    def _empty_result(self) -> dict:
        """返回空结�?""
        return {
            "target": "",
            "target_type": None,
            "keywords": [],
            "attributes": {},
        }
    
    def get_confidence(
        self,
        text: str,
        element_type: Optional[ElementType],
    ) -> float:
        """
        获取识别置信�?
        
        Args:
            text: 文本
            element_type: 识别的元素类�?
            
        Returns:
            置信度（0.0-1.0�?
        """
        if not element_type:
            return 0.3
        
        text_lower = text.lower()
        
        # 检查是否有明确的类型关键词
        keywords = ELEMENT_TYPE_KEYWORDS.get(element_type, {}).get("keywords", [])
        
        for keyword in keywords:
            if keyword.lower() in text_lower:
                return 0.9  # 高置信度
        
        # 检查常见名�?
        for name, et in COMMON_ELEMENT_NAMES.items():
            if et == element_type and name in text:
                return 0.8
        
        # 默认置信�?
        return 0.5

