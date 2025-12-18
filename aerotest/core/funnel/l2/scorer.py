"""评分�?

计算元素匹配的综合得�?
"""

from typing import Optional

from aerotest.browser.dom.views import EnhancedDOMTreeNode
from aerotest.core.funnel.l2.attribute_matcher import AttributeMatcher
from aerotest.core.funnel.l2.text_matcher import TextMatcher
from aerotest.core.funnel.l2.type_matcher import TypeMatcher
from aerotest.core.funnel.types import ActionSlot, ElementType, MatchResult
from aerotest.utils import get_logger

logger = get_logger("aerotest.funnel.l2.scorer")


class Scorer:
    """评分�?
    
    计算元素与槽位的综合匹配得分，整合：
    - 属性匹配得�?
    - 文本匹配得分
    - 类型匹配得分
    
    Example:
        ```python
        scorer = Scorer()
        
        result = scorer.calculate_score(
            element=button_element,
            slot=action_slot,
        )
        
        print(f"得分: {result.score:.2f}")
        print(f"匹配原因: {result.match_reasons}")
        ```
    """
    
    def __init__(self):
        """初始化评分器"""
        self.attribute_matcher = AttributeMatcher()
        self.text_matcher = TextMatcher()
        self.type_matcher = TypeMatcher()
        logger.debug("评分器初始化完成")
    
    def calculate_score(
        self,
        element: EnhancedDOMTreeNode,
        slot: ActionSlot,
    ) -> MatchResult:
        """
        计算综合得分
        
        Args:
            element: DOM 元素
            slot: 动作槽位
            
        Returns:
            匹配结果
        """
        matched_attributes: dict[str, float] = {}
        match_reasons: list[str] = []
        total_score = 0.0
        
        # 1. 类型匹配
        type_bonus = 0.0
        if slot.target_type:
            is_type_match = self.type_matcher.is_type_match(element, slot.target_type)
            if is_type_match:
                type_bonus = 0.2
                match_reasons.append(f"类型匹配: {slot.target_type.value}")
        
        # 2. 属性匹�?
        if slot.keywords:
            # 遍历常用属�?
            for attr in ["id", "name", "placeholder", "aria-label", "title", "innerText"]:
                attr_value = element.attributes.get(attr)
                if not attr_value:
                    continue
                
                # 计算文本匹配得分
                text_score = self.text_matcher.match_any(attr_value, slot.keywords)
                
                if text_score > 0.5:
                    # 应用属性权�?
                    attr_weight = self.attribute_matcher.get_attribute_weight(attr)
                    weighted_score = text_score * attr_weight
                    
                    matched_attributes[attr] = weighted_score
                    match_reasons.append(
                        f"{attr}匹配: '{attr_value[:20]}...' (得分: {weighted_score:.2f})"
                    )
        
        # 3. 计算总分
        if matched_attributes:
            # 取最高的 2 个属性得�?
            sorted_scores = sorted(matched_attributes.values(), reverse=True)
            top_scores = sorted_scores[:2]
            total_score = sum(top_scores) / len(top_scores) if top_scores else 0.0
        
        # 4. 应用类型奖励
        final_score = min(1.0, total_score + type_bonus)
        
        # 5. 构建结果
        result = MatchResult(
            element=element,
            score=final_score,
            matched_attributes=matched_attributes,
            match_reasons=match_reasons,
            layer="L2",
        )
        
        return result
    
    def score_elements(
        self,
        elements: list[EnhancedDOMTreeNode],
        slot: ActionSlot,
        top_n: int = 10,
    ) -> list[MatchResult]:
        """
        为元素列表打分并排序
        
        Args:
            elements: 元素列表
            slot: 动作槽位
            top_n: 返回�?N 个结�?
            
        Returns:
            排序后的匹配结果列表
        """
        results = []
        
        for element in elements:
            result = self.calculate_score(element, slot)
            if result.score > 0.3:  # 过滤低分元素
                results.append(result)
        
        # 排序
        results.sort(key=lambda x: x.score, reverse=True)
        
        logger.info(f"评分完成: {len(results)} 个候选，返回�?{top_n} �?)
        return results[:top_n]

