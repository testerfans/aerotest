"""属性匹配器

基于元素属性匹配关键词，是 L2 层的核心组件之一
"""

from typing import Optional

from aerotest.browser.dom.views import EnhancedDOMTreeNode
from aerotest.core.funnel.types import MatchResult
from aerotest.utils import get_logger

logger = get_logger("aerotest.funnel.l2.attribute")


class AttributeMatcher:
    """属性匹配器
    
    基于元素的各种属性匹配关键词，不同属性有不同的权重：
    - placeholder: 最高权�?(1.0) - 最直接的提示信�?
    - id/name: 高权�?(0.9) - 通常是有意义的标�?
    - aria-label: 高权�?(0.85) - 无障碍标�?
    - title: 中高权重 (0.8) - 提示信息
    - value: 中权�?(0.7) - 当前�?
    - innerText: 中低权重 (0.6) - 可见文本
    - class: 低权�?(0.4) - 可能包含无关的样式类�?
    
    Example:
        ```python
        matcher = AttributeMatcher()
        
        # 单属性匹�?
        results = matcher.match_by_attribute(
            elements=dom_elements,
            keywords=["提交", "submit"],
            attribute="id",
        )
        
        # 多属性匹�?
        all_results = matcher.match_by_all_attributes(
            elements=dom_elements,
            keywords=["提交", "submit"],
        )
        ```
    """
    
    # 属性权重映�?
    ATTRIBUTE_WEIGHTS = {
        "placeholder": 1.0,
        "id": 0.9,
        "name": 0.9,
        "aria-label": 0.85,
        "title": 0.8,
        "value": 0.7,
        "innerText": 0.6,
        "class": 0.4,
        "type": 0.5,
        "role": 0.7,
        "alt": 0.75,
    }
    
    def __init__(self):
        """初始化属性匹配器"""
        logger.debug("属性匹配器初始化完�?)
    
    def match_by_attribute(
        self,
        elements: list[EnhancedDOMTreeNode],
        keywords: list[str],
        attribute: str,
    ) -> list[tuple[EnhancedDOMTreeNode, float]]:
        """
        基于单个属性匹配元�?
        
        Args:
            elements: 元素列表
            keywords: 关键词列�?
            attribute: 属性名
            
        Returns:
            (元素, 匹配得分) 元组列表
        """
        results = []
        attribute_weight = self.ATTRIBUTE_WEIGHTS.get(attribute, 0.5)
        
        for element in elements:
            # 获取属性�?
            attr_value = self._get_attribute_value(element, attribute)
            
            if not attr_value:
                continue
            
            # 匹配关键�?
            match_score = self._match_keywords(attr_value, keywords)
            
            if match_score > 0:
                # 应用属性权�?
                final_score = match_score * attribute_weight
                results.append((element, final_score))
                
                logger.debug(
                    f"属性匹�? {attribute}='{attr_value[:30]}...' "
                    f"score={final_score:.2f}"
                )
        
        return results
    
    def match_by_all_attributes(
        self,
        elements: list[EnhancedDOMTreeNode],
        keywords: list[str],
        attributes: Optional[list[str]] = None,
    ) -> dict[str, list[tuple[EnhancedDOMTreeNode, float]]]:
        """
        基于所有属性匹配元�?
        
        Args:
            elements: 元素列表
            keywords: 关键词列�?
            attributes: 要检查的属性列表（None 表示所有属性）
            
        Returns:
            属性名 -> [(元素, 得分)] 的映�?
        """
        if attributes is None:
            attributes = list(self.ATTRIBUTE_WEIGHTS.keys())
        
        results = {}
        
        for attribute in attributes:
            matches = self.match_by_attribute(elements, keywords, attribute)
            if matches:
                results[attribute] = matches
        
        return results
    
    def get_best_matches(
        self,
        elements: list[EnhancedDOMTreeNode],
        keywords: list[str],
        top_n: int = 10,
    ) -> list[MatchResult]:
        """
        获取最佳匹配（综合所有属性）
        
        Args:
            elements: 元素列表
            keywords: 关键词列�?
            top_n: 返回�?N 个结�?
            
        Returns:
            匹配结果列表（按得分降序�?
        """
        # 匹配所有属�?
        all_matches = self.match_by_all_attributes(elements, keywords)
        
        # 聚合每个元素的得�?
        element_scores: dict[int, dict] = {}
        
        for attribute, matches in all_matches.items():
            for element, score in matches:
                node_id = element.backend_node_id
                
                if node_id not in element_scores:
                    element_scores[node_id] = {
                        "element": element,
                        "total_score": 0.0,
                        "matched_attributes": {},
                        "match_reasons": [],
                    }
                
                # 累加得分（取最高分，避免重复计分）
                if score > element_scores[node_id]["matched_attributes"].get(attribute, 0.0):
                    element_scores[node_id]["matched_attributes"][attribute] = score
                    element_scores[node_id]["total_score"] = sum(
                        element_scores[node_id]["matched_attributes"].values()
                    )
                    
                    # 添加匹配原因
                    attr_value = self._get_attribute_value(element, attribute)
                    reason = f"{attribute}匹配: '{attr_value[:20]}...' (得分: {score:.2f})"
                    if reason not in element_scores[node_id]["match_reasons"]:
                        element_scores[node_id]["match_reasons"].append(reason)
        
        # 转换�?MatchResult
        results = []
        for data in element_scores.values():
            # 归一化得分（避免超过 1.0�?
            normalized_score = min(1.0, data["total_score"])
            
            result = MatchResult(
                element=data["element"],
                score=normalized_score,
                matched_attributes=data["matched_attributes"],
                match_reasons=data["match_reasons"],
                layer="L2",
            )
            results.append(result)
        
        # 排序并返�?Top-N
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_n]
    
    def _get_attribute_value(
        self,
        element: EnhancedDOMTreeNode,
        attribute: str,
    ) -> Optional[str]:
        """
        获取元素的属性�?
        
        Args:
            element: DOM 元素
            attribute: 属性名
            
        Returns:
            属性�?
        """
        # 特殊处理 innerText
        if attribute == "innerText":
            return element.attributes.get("innerText") or element.attributes.get("textContent", "")
        
        # 特殊处理 class
        if attribute == "class":
            return element.attributes.get("class", "")
        
        # 其他属�?
        return element.attributes.get(attribute)
    
    def _match_keywords(
        self,
        text: str,
        keywords: list[str],
    ) -> float:
        """
        匹配关键�?
        
        Args:
            text: 要匹配的文本
            keywords: 关键词列�?
            
        Returns:
            匹配得分 (0.0-1.0)
        """
        if not text or not keywords:
            return 0.0
        
        text_lower = text.lower().strip()
        max_score = 0.0
        
        for keyword in keywords:
            keyword_lower = keyword.lower().strip()
            
            if not keyword_lower:
                continue
            
            # 1. 精确匹配 (最高分)
            if text_lower == keyword_lower:
                return 1.0
            
            # 2. 完整包含匹配
            if keyword_lower in text_lower:
                # 计算覆盖�?
                coverage = len(keyword_lower) / len(text_lower)
                score = 0.7 + coverage * 0.3  # 0.7-1.0
                max_score = max(max_score, score)
            
            # 3. 部分匹配（单词边界）
            elif self._partial_match(text_lower, keyword_lower):
                max_score = max(max_score, 0.5)
        
        return max_score
    
    def _partial_match(self, text: str, keyword: str) -> bool:
        """
        部分匹配（检查是否包含关键词的一部分�?
        
        Args:
            text: 文本
            keyword: 关键�?
            
        Returns:
            是否匹配
        """
        # 简单实现：检查关键词是否是文本中某个单词的子�?
        words = text.split()
        for word in words:
            if keyword in word or word in keyword:
                return True
        return False
    
    def get_attribute_weight(self, attribute: str) -> float:
        """
        获取属性权�?
        
        Args:
            attribute: 属性名
            
        Returns:
            权重�?
        """
        return self.ATTRIBUTE_WEIGHTS.get(attribute, 0.5)

