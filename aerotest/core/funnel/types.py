"""漏斗数据类型定义

定义五层漏斗使用的核心数据结�?
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from aerotest.browser.dom.views import EnhancedDOMTreeNode


class ActionType(str, Enum):
    """动作类型"""
    CLICK = "click"
    INPUT = "input"
    SELECT = "select"
    NAVIGATE = "navigate"
    WAIT = "wait"
    HOVER = "hover"
    DRAG = "drag"
    SCROLL = "scroll"
    UNKNOWN = "unknown"


class ElementType(str, Enum):
    """元素类型"""
    BUTTON = "button"
    INPUT = "input"
    TEXTAREA = "textarea"
    SELECT = "select"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    LINK = "link"
    DIV = "div"
    SPAN = "span"
    LABEL = "label"
    UNKNOWN = "unknown"


@dataclass
class ActionSlot:
    """动作槽位
    
    从自然语言中提取的结构化操作信�?
    
    Attributes:
        action: 动作类型
        target: 目标描述（原始文本）
        target_type: 目标元素类型
        keywords: 关键词列�?
        attributes: 属性提示（�?id, name 等）
        value: 输入值（对于 input 动作�?
        confidence: 置信度（0.0-1.0�?
    
    Example:
        ```python
        slot = ActionSlot(
            action=ActionType.CLICK,
            target="提交按钮",
            target_type=ElementType.BUTTON,
            keywords=["提交", "按钮", "submit"],
            attributes={"type": "submit"},
            value=None,
            confidence=0.95,
        )
        ```
    """
    
    action: ActionType
    target: Optional[str] = None
    target_type: Optional[ElementType] = None
    keywords: list[str] = field(default_factory=list)
    attributes: dict[str, str] = field(default_factory=dict)
    value: Optional[str] = None
    confidence: float = 1.0
    
    def __post_init__(self):
        """验证数据"""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence 必须�?0.0 �?1.0 之间")


@dataclass
class MatchResult:
    """匹配结果
    
    L2 层的元素匹配结果，包含匹配的元素和详细的得分信息
    
    Attributes:
        element: 匹配�?DOM 元素
        score: 综合得分�?.0-1.0�?
        matched_attributes: 匹配的属性及其得�?
        match_reasons: 匹配原因列表（用于调试和解释�?
        layer: 匹配所在的层级（L2, L3, L4, L5�?
    
    Example:
        ```python
        result = MatchResult(
            element=button_element,
            score=0.95,
            matched_attributes={
                "id": 0.9,
                "innerText": 0.8,
            },
            match_reasons=[
                "ID 'submit-btn' 包含关键�?'submit'",
                "文本 '提交' 精确匹配",
            ],
            layer="L2",
        )
        ```
    """
    
    element: EnhancedDOMTreeNode
    score: float
    matched_attributes: dict[str, float] = field(default_factory=dict)
    match_reasons: list[str] = field(default_factory=list)
    layer: str = "L2"
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """验证数据"""
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("score 必须�?0.0 �?1.0 之间")
    
    def __lt__(self, other: "MatchResult") -> bool:
        """支持排序（按分数降序�?""
        return self.score > other.score


@dataclass
class FunnelContext:
    """漏斗上下�?
    
    在漏斗各层之间传递的上下文信�?
    
    Attributes:
        instruction: 原始自然语言指令
        action_slot: L1 提取的槽位信�?
        l2_candidates: L2 的候选结�?
        l3_candidates: L3 的候选结�?
        l4_candidates: L4 的候选结�?
        final_result: 最终选择的元�?
        metadata: 额外的元数据
    """
    
    instruction: str
    action_slot: Optional[ActionSlot] = None
    l2_candidates: list[MatchResult] = field(default_factory=list)
    l3_candidates: list[MatchResult] = field(default_factory=list)
    l4_candidates: list[MatchResult] = field(default_factory=list)
    final_result: Optional[MatchResult] = None
    metadata: dict[str, Any] = field(default_factory=dict)

