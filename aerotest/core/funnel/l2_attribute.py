"""L2 属性匹配层"""

from typing import Any, Dict, Optional

from rapidfuzz import fuzz

from aerotest.core.funnel.base import BaseFunnelLayer
from aerotest.core.funnel.engine import FunnelResult
from aerotest.core.types import ElementLocatorStrategy
from aerotest.utils import get_logger

logger = get_logger("aerotest.funnel.l2")


class L2AttributeLayer(BaseFunnelLayer):
    """L2 属性匹配层 - 基于 DOM 属性的模糊匹配"""

    def __init__(self, fuzzy_threshold: float = 80.0):
        super().__init__(ElementLocatorStrategy.L2_ATTRIBUTE)
        self.fuzzy_threshold = fuzzy_threshold

        # 优先级属性列�?
        self.priority_attributes = [
            "placeholder",
            "aria-label",
            "title",
            "name",
            "id",
            "class",
            "data-testid",
            "data-test",
        ]

        logger.info(f"L2 属性匹配层初始化完�?(fuzzy_threshold={fuzzy_threshold})")

    def can_handle(self, selector: str) -> bool:
        """判断是否能处理该选择�?""
        # L2 层可以处理任何文本描�?
        return len(selector.strip()) > 0

    async def locate(
        self, selector: str, context: Dict[str, Any], dom_adapter: Any
    ) -> Optional[FunnelResult]:
        """
        通过属性匹配定位元�?

        Args:
            selector: 元素选择�?
            context: 上下文信�?
            dom_adapter: DOM 适配�?

        Returns:
            FunnelResult �?None
        """
        logger.debug(f"L2 属性层处理: {selector}")

        # TODO: 获取所有可交互元素
        # elements = await dom_adapter.find_clickable_elements()

        # TODO: 遍历元素，计算属性匹配分�?
        # best_match = None
        # best_score = 0.0

        # for element in elements:
        #     score = self._calculate_match_score(element, selector)
        #     if score > best_score and score >= self.fuzzy_threshold:
        #         best_score = score
        #         best_match = element

        # if best_match:
        #     return FunnelResult(
        #         strategy=self.strategy,
        #         element=best_match,
        #         confidence=best_score / 100.0,
        #         metadata={"selector": selector}
        #     )

        return None

    def _calculate_match_score(self, element: Any, target: str) -> float:
        """
        计算元素与目标文本的匹配分数

        Args:
            element: DOM 元素
            target: 目标文本

        Returns:
            匹配分数 (0-100)
        """
        best_score = 0.0

        # 按优先级检查各属�?
        for attr in self.priority_attributes:
            attr_value = element.attributes.get(attr, "")
            if attr_value:
                # 使用 rapidfuzz 计算模糊匹配分数
                score = fuzz.ratio(target.lower(), attr_value.lower())
                best_score = max(best_score, score)

        # 检�?innerText
        if element.text_content:
            text_score = fuzz.ratio(target.lower(), element.text_content.lower())
            best_score = max(best_score, text_score)

        return best_score

