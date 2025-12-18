"""L3 数据类型定义

定义 L3 空间布局推理层使用的数据结构
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from aerotest.browser.dom.views import EnhancedDOMTreeNode


class Direction(str, Enum):
    """方向枚举"""
    LEFT = "left"           # 左边
    RIGHT = "right"         # 右边
    ABOVE = "above"         # 上方
    BELOW = "below"         # 下方
    INSIDE = "inside"       # 内部
    NEAR = "near"           # 附近
    FAR = "far"             # 远处


class DistanceUnit(str, Enum):
    """距离单位"""
    PIXEL = "px"            # 像素
    PERCENT = "%"           # 百分�?
    RELATIVE = "relative"   # 相对距离（近/远）


@dataclass
class Position:
    """位置信息"""
    x: float                # X 坐标
    y: float                # Y 坐标
    width: float            # 宽度
    height: float           # 高度
    
    @property
    def center_x(self) -> float:
        """中心 X 坐标"""
        return self.x + self.width / 2
    
    @property
    def center_y(self) -> float:
        """中心 Y 坐标"""
        return self.y + self.height / 2
    
    @property
    def left(self) -> float:
        """左边�?""
        return self.x
    
    @property
    def right(self) -> float:
        """右边�?""
        return self.x + self.width
    
    @property
    def top(self) -> float:
        """上边�?""
        return self.y
    
    @property
    def bottom(self) -> float:
        """下边�?""
        return self.y + self.height


@dataclass
class AnchorInfo:
    """锚点信息
    
    从指令中提取的锚点（参照物）信息
    
    Example:
        指令: "点击用户名输入框右边的按�?
        AnchorInfo {
            description: "用户名输入框",
            direction: Direction.RIGHT,
            distance: None,
            target_description: "按钮"
        }
    """
    
    description: str                    # 锚点描述
    direction: Optional[Direction]      # 相对方向
    distance: Optional[float]           # 距离（像素）
    distance_unit: DistanceUnit         # 距离单位
    target_description: str             # 目标描述
    confidence: float = 1.0             # 置信�?
    
    def has_direction(self) -> bool:
        """是否有方向信�?""
        return self.direction is not None


@dataclass
class ProximityResult:
    """邻近检测结�?
    
    Attributes:
        element: 找到的元�?
        distance: 与锚点的距离（像素）
        direction_match: 方向是否匹配
        angle: 相对于锚点的角度（度�?
        score: 综合得分
    """
    
    element: EnhancedDOMTreeNode
    distance: float
    direction_match: bool
    angle: float                        # 角度�?-360度）
    score: float
    
    def __lt__(self, other: "ProximityResult") -> bool:
        """支持排序（按得分降序�?""
        return self.score > other.score


@dataclass
class SpatialRelation:
    """空间关系
    
    描述两个元素之间的空间关�?
    """
    
    element1: EnhancedDOMTreeNode       # 元素 1（通常是锚点）
    element2: EnhancedDOMTreeNode       # 元素 2（通常是目标）
    distance: float                     # 距离（像素）
    direction: Direction                # 方向
    angle: float                        # 角度（度�?
    overlap: float                      # 重叠度（0.0-1.0�?
    
    def is_aligned_horizontally(self, threshold: float = 0.2) -> bool:
        """是否水平对齐"""
        # 如果两个元素的中�?Y 坐标相近，则认为水平对齐
        # threshold: 允许的偏差比�?
        return abs(self.angle - 0) < threshold or abs(self.angle - 180) < threshold
    
    def is_aligned_vertically(self, threshold: float = 0.2) -> bool:
        """是否垂直对齐"""
        # 如果两个元素的中�?X 坐标相近，则认为垂直对齐
        return abs(self.angle - 90) < threshold or abs(self.angle - 270) < threshold


@dataclass
class EventListenerInfo:
    """事件监听器信�?""
    
    element: EnhancedDOMTreeNode
    event_types: list[str]              # 事件类型列表（click, input, etc.�?
    has_click: bool                     # 是否有点击监�?
    has_input: bool                     # 是否有输入监�?
    listener_count: int                 # 监听器总数
    
    def is_interactive(self) -> bool:
        """是否是可交互元素"""
        return self.listener_count > 0 or self.has_click


@dataclass
class L3Context:
    """L3 上下�?
    
    �?L3 处理过程中传递的上下文信�?
    """
    
    anchor_info: Optional[AnchorInfo] = None
    anchor_element: Optional[EnhancedDOMTreeNode] = None
    proximity_results: list[ProximityResult] = field(default_factory=list)
    spatial_relations: list[SpatialRelation] = field(default_factory=list)
    event_listeners: dict[int, EventListenerInfo] = field(default_factory=dict)

