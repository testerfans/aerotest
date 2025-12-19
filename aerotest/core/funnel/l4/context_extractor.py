"""上下文提取器

从 DOM 和指令中提取相关上下文信息
"""

from typing import Any, Optional

from aerotest.browser.dom.views import EnhancedDOMTreeNode
from aerotest.browser.dom.views import SerializedDOMState
from aerotest.core.funnel.types import ActionSlot, MatchResult
from aerotest.utils import get_logger

logger = get_logger("aerotest.funnel.l4.context")


class ContextExtractor:
    """上下文提取器
    
    从 DOM 和用户指令中提取对 AI 推理有用的上下文信息：
    - 候选元素信息
    - 页面结构信息
    - 业务逻辑提示
    
    Example:
        ```python
        extractor = ContextExtractor()
        
        context = extractor.extract_context(
            instruction="选择最便宜的商品",
            candidates=[...],
        )
        ```
    """
    
    def __init__(self):
        """初始化上下文提取器"""
        logger.debug("上下文提取器初始化完成")
    
    def extract_context(
        self,
        instruction: str,
        candidates: list[MatchResult],
        dom_state: Optional[SerializedDOMState] = None,
    ) -> dict[str, Any]:
        """
        提取上下文信息
        
        Args:
            instruction: 用户指令
            candidates: 候选元素列表
            dom_state: DOM 状态
            
        Returns:
            上下文信息字典
        """
        context = {
            "instruction": instruction,
            "candidates_count": len(candidates),
            "elements": [],
            "intent": self._analyze_intent(instruction),
        }
        
        # 提取每个候选元素的信息
        for i, result in enumerate(candidates):
            element_info = self._extract_element_info(result.element, index=i)
            context["elements"].append(element_info)
        
        # 提取特定类型的信息
        if self._has_comparison_intent(instruction):
            context["comparison_values"] = self._extract_comparison_values(candidates)
        
        if self._has_position_intent(instruction):
            context["positions"] = self._extract_positions(candidates)
        
        logger.debug(f"提取上下文: {len(context['elements'])} 个元素")
        
        return context
    
    def _extract_element_info(
        self,
        element: EnhancedDOMTreeNode,
        index: int,
    ) -> dict[str, Any]:
        """
        提取单个元素的信息
        
        Args:
            element: DOM 元素
            index: 元素索引
            
        Returns:
            元素信息字典
        """
        info = {
            "index": index,
            "tag": element.tag_name,
            "attributes": {},
            "text": "",
            "position": None,
        }
        
        # 提取重要属性
        important_attrs = [
            "id", "name", "class", "type", "value",
            "placeholder", "aria-label", "title", "href",
            "data-price", "data-id", "data-value",  # 常见的 data 属性
        ]
        
        for attr in important_attrs:
            value = element.attributes.get(attr)
            if value:
                info["attributes"][attr] = value
        
        # 提取文本
        text = element.attributes.get("innerText") or element.attributes.get("textContent", "")
        if text:
            info["text"] = text.strip()
        
        # 提取位置
        if element.bounding_box:
            bbox = element.bounding_box
            info["position"] = {
                "x": bbox.x,
                "y": bbox.y,
                "width": bbox.width,
                "height": bbox.height,
            }
        
        return info
    
    def _analyze_intent(self, instruction: str) -> dict[str, Any]:
        """
        分析用户意图
        
        Args:
            instruction: 用户指令
            
        Returns:
            意图信息
        """
        intent = {
            "has_comparison": self._has_comparison_intent(instruction),
            "has_position": self._has_position_intent(instruction),
            "has_condition": self._has_condition_intent(instruction),
        }
        
        # 识别比较类型
        if intent["has_comparison"]:
            intent["comparison_type"] = self._identify_comparison_type(instruction)
        
        # 识别位置类型
        if intent["has_position"]:
            intent["position_type"] = self._identify_position_type(instruction)
        
        return intent
    
    def _has_comparison_intent(self, instruction: str) -> bool:
        """判断是否包含比较意图"""
        comparison_keywords = [
            "最", "最高", "最大", "最多", "最好",
            "最低", "最便宜", "最小", "最少",
            "更", "更大", "更小", "更多", "更少",
        ]
        
        return any(keyword in instruction for keyword in comparison_keywords)
    
    def _has_position_intent(self, instruction: str) -> bool:
        """判断是否包含位置意图"""
        position_keywords = [
            "第一", "第二", "第三", "最后", "首个",
            "最后", "倒数", "中间", "居中",
        ]
        
        return any(keyword in instruction for keyword in position_keywords)
    
    def _has_condition_intent(self, instruction: str) -> bool:
        """判断是否包含条件意图"""
        condition_keywords = [
            "包含", "不包含", "等于", "不等于",
            "大于", "小于", "符合", "满足",
        ]
        
        return any(keyword in instruction for keyword in condition_keywords)
    
    def _identify_comparison_type(self, instruction: str) -> str:
        """识别比较类型"""
        if any(k in instruction for k in ["最高", "最大", "价格最高"]):
            return "max_price"
        elif any(k in instruction for k in ["最便宜", "最低", "价格最低"]):
            return "min_price"
        elif any(k in instruction for k in ["最大", "最多"]):
            return "max_value"
        elif any(k in instruction for k in ["最小", "最少"]):
            return "min_value"
        else:
            return "unknown"
    
    def _identify_position_type(self, instruction: str) -> str:
        """识别位置类型"""
        if "第一" in instruction or "首个" in instruction:
            return "first"
        elif "最后" in instruction or "倒数第一" in instruction:
            return "last"
        elif "第二" in instruction:
            return "second"
        elif "第三" in instruction:
            return "third"
        else:
            return "unknown"
    
    def _extract_comparison_values(
        self,
        candidates: list[MatchResult],
    ) -> list[dict[str, Any]]:
        """提取比较值（如价格）"""
        import re
        
        values = []
        
        for i, result in enumerate(candidates):
            element = result.element
            
            # 尝试从各种地方提取数值
            text = element.attributes.get("innerText", "")
            value_attr = element.attributes.get("value", "")
            data_price = element.attributes.get("data-price", "")
            
            # 合并所有文本
            all_text = f"{text} {value_attr} {data_price}"
            
            # 提取数字（支持价格格式）
            price_pattern = r"[\￥$€]?\s*(\d+(?:\.\d+)?)"
            matches = re.findall(price_pattern, all_text)
            
            if matches:
                try:
                    value = float(matches[0])
                    values.append({
                        "index": i,
                        "value": value,
                        "text": all_text.strip(),
                    })
                except ValueError:
                    pass
        
        return values
    
    def _extract_positions(
        self,
        candidates: list[MatchResult],
    ) -> list[dict[str, Any]]:
        """提取位置信息"""
        positions = []
        
        for i, result in enumerate(candidates):
            element = result.element
            
            if element.bounding_box:
                bbox = element.bounding_box
                positions.append({
                    "index": i,
                    "x": bbox.x,
                    "y": bbox.y,
                    "order": i,  # 在列表中的顺序
                })
        
        return positions
