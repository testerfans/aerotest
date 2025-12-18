"""槽位填充�?

将意图识别和实体提取的结果组合成完整的动作槽�?
"""

from typing import Optional

from aerotest.core.funnel.l1.entity_extractor import EntityExtractor
from aerotest.core.funnel.l1.intent_recognizer import IntentRecognizer
from aerotest.core.funnel.types import ActionSlot, ActionType, ElementType
from aerotest.utils import get_logger

logger = get_logger("aerotest.funnel.l1.slot")


class SlotFiller:
    """槽位填充�?
    
    整合意图识别和实体提取的结果，生成完整的动作槽位
    
    处理流程�?
    1. 使用 IntentRecognizer 识别动作类型
    2. 使用 EntityExtractor 提取目标信息
    3. 组合结果并填�?ActionSlot
    4. 提取输入值（对于 INPUT 动作�?
    5. 计算综合置信�?
    
    Example:
        ```python
        filler = SlotFiller()
        
        slot = filler.fill("点击提交按钮")
        # ActionSlot(
        #     action=ActionType.CLICK,
        #     target="提交按钮",
        #     target_type=ElementType.BUTTON,
        #     keywords=["提交", "按钮"],
        #     attributes={"type": "submit"},
        #     value=None,
        #     confidence=0.85
        # )
        ```
    """
    
    def __init__(self):
        """初始化槽位填充器"""
        self.intent_recognizer = IntentRecognizer()
        self.entity_extractor = EntityExtractor()
        logger.debug("槽位填充器初始化完成")
    
    def fill(self, text: str) -> ActionSlot:
        """
        填充动作槽位
        
        Args:
            text: 自然语言指令
            
        Returns:
            填充完整的动作槽�?
        """
        text = text.strip()
        
        if not text:
            logger.warning("空文本，返回默认槽位")
            return self._default_slot()
        
        # 1. 识别动作
        action = self.intent_recognizer.recognize(text)
        action_confidence = self.intent_recognizer.get_confidence(text, action)
        
        # 2. 提取实体
        entity_info = self.entity_extractor.extract(
            text,
            action_keywords=self._get_action_keywords(action),
        )
        entity_confidence = self.entity_extractor.get_confidence(
            text,
            entity_info["target_type"],
        )
        
        # 3. 提取输入值（如果�?INPUT 动作�?
        value = None
        if action == ActionType.INPUT:
            value = self._extract_input_value(text)
        
        # 4. 计算综合置信�?
        confidence = self._calculate_confidence(
            action_confidence,
            entity_confidence,
            action,
            entity_info["target_type"],
        )
        
        # 5. 构建槽位
        slot = ActionSlot(
            action=action,
            target=entity_info["target"],
            target_type=entity_info["target_type"],
            keywords=entity_info["keywords"],
            attributes=entity_info["attributes"],
            value=value,
            confidence=confidence,
        )
        
        logger.debug(f"槽位填充: '{text}' -> {slot}")
        return slot
    
    def _get_action_keywords(self, action: ActionType) -> list[str]:
        """获取动作的关键词列表（用于实体提取时过滤�?""
        from aerotest.core.funnel.l1.action_patterns import ACTION_KEYWORDS
        
        action_data = ACTION_KEYWORDS.get(action, {})
        return action_data.get("keywords", [])
    
    def _extract_input_value(self, text: str) -> Optional[str]:
        """
        提取输入�?
        
        对于 INPUT 动作，尝试提取要输入的�?
        
        Args:
            text: 指令文本
            
        Returns:
            输入值（如果能提取到�?
        
        Example:
            "输入用户�?admin" -> "admin"
            "在密码框输入 123456" -> "123456"
        """
        import re
        
        # 模式：动作词 + 目标 + �?
        patterns = [
            r"输入.*[\"'](.*?)[\"']",  # 输入 "�?
            r"填写.*[\"'](.*?)[\"']",  # 填写 "�?
            r"输入.*\s+(\S+)$",        # 输入 �?
            r"填写.*\s+(\S+)$",        # 填写 �?
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                value = match.group(1).strip()
                if value:
                    logger.debug(f"提取到输入�? '{value}'")
                    return value
        
        return None
    
    def _calculate_confidence(
        self,
        action_confidence: float,
        entity_confidence: float,
        action: ActionType,
        element_type: Optional[ElementType],
    ) -> float:
        """
        计算综合置信�?
        
        Args:
            action_confidence: 动作识别置信�?
            entity_confidence: 实体提取置信�?
            action: 动作类型
            element_type: 元素类型
            
        Returns:
            综合置信�?
        """
        # 基础置信度：两者的加权平均
        # 动作识别更重要（权重 0.6�?
        base_confidence = action_confidence * 0.6 + entity_confidence * 0.4
        
        # 调整因子
        adjustment = 0.0
        
        # 如果动作和元素类型匹配，提升置信�?
        if self._action_element_match(action, element_type):
            adjustment += 0.1
        
        # 如果元素类型未知，降低置信度
        if element_type is None:
            adjustment -= 0.1
        
        # 确保�?[0.0, 1.0] 范围�?
        final_confidence = max(0.0, min(1.0, base_confidence + adjustment))
        
        return final_confidence
    
    def _action_element_match(
        self,
        action: ActionType,
        element_type: Optional[ElementType],
    ) -> bool:
        """
        检查动作和元素类型是否匹配
        
        Args:
            action: 动作类型
            element_type: 元素类型
            
        Returns:
            是否匹配
        """
        if element_type is None:
            return False
        
        # 定义动作和元素的匹配关系
        matches = {
            ActionType.CLICK: [ElementType.BUTTON, ElementType.LINK],
            ActionType.INPUT: [ElementType.INPUT, ElementType.TEXTAREA],
            ActionType.SELECT: [ElementType.SELECT, ElementType.CHECKBOX, ElementType.RADIO],
        }
        
        expected_elements = matches.get(action, [])
        return element_type in expected_elements
    
    def _default_slot(self) -> ActionSlot:
        """返回默认槽位"""
        return ActionSlot(
            action=ActionType.UNKNOWN,
            target=None,
            target_type=None,
            keywords=[],
            attributes={},
            value=None,
            confidence=0.0,
        )
    
    def parse_batch(self, instructions: list[str]) -> list[ActionSlot]:
        """
        批量解析指令
        
        Args:
            instructions: 指令列表
            
        Returns:
            槽位列表
        """
        return [self.fill(instruction) for instruction in instructions]

