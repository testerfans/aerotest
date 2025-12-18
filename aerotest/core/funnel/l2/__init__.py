"""L2: 启发式属性匹配层

使用启发式规则匹�?DOM 元素�?
- 属性匹配：基于元素属性（id, name, placeholder 等）匹配
- 文本匹配：基于元素文本内容匹配（精确/模糊/包含�?
- 类型匹配：基于元素类型筛�?
- 评分排序：计算综合得分并排序

示例�?
    输入: ActionSlot(keywords=["提交", "submit"])
    输出: [
        MatchResult(element=button1, score=0.95),
        MatchResult(element=button2, score=0.75),
    ]
"""

from aerotest.core.funnel.l2.attribute_matcher import AttributeMatcher
from aerotest.core.funnel.l2.l2_engine import L2Engine
from aerotest.core.funnel.l2.scorer import Scorer
from aerotest.core.funnel.l2.text_matcher import TextMatcher
from aerotest.core.funnel.l2.type_matcher import TypeMatcher

__all__ = [
    "L2Engine",
    "AttributeMatcher",
    "TextMatcher",
    "TypeMatcher",
    "Scorer",
]

