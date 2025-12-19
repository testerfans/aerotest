"""五层漏斗模块

实现 AeroTest AI 的核心定位能力，通过五层递进式筛选机制准确定位页面元素：

L1: 规则槽位 (Rule-based Slotting)
    - NLP 意图识别
    - 实体提取
    - 槽位填充

L2: 启发式属性匹配 (Heuristic Attribute Match)
    - 属性匹配
    - 文本匹配
    - 类型匹配

L3: 空间布局推理 (Spatial Layout Reasoning)
    - 锚点定位
    - 邻近检测
    - 事件监听穿透

L4: Qwen 推理 (AI Reasoning)
    - 语义理解
    - 上下文提取
    - 模糊推理

L5: Qwen2-VL 视觉 (Visual Recognition)
    - 截图识别
    - 坐标定位
    - Canvas 处理

来源: AeroTest AI 原创设计
"""

from aerotest.core.funnel.base import BaseFunnelLayer, FunnelResult
from aerotest.core.funnel.types import ActionSlot, MatchResult

__all__ = [
    "BaseFunnelLayer",
    "FunnelResult",
    "ActionSlot",
    "MatchResult",
]
