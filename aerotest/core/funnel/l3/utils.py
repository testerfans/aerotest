"""L3 工具函数

空间布局计算的辅助函数
"""

import math
from typing import Optional

from aerotest.browser.dom.views import EnhancedDOMTreeNode
from aerotest.core.funnel.l3.types import Direction, Position


def get_element_position(element: EnhancedDOMTreeNode) -> Optional[Position]:
    """
    获取元素位置信息
    
    Args:
        element: DOM 元素
        
    Returns:
        位置信息，如果元素没有位置信息则返回 None
    """
    # 从元素的 bounding_box 获取位置
    if not element.bounding_box:
        return None
    
    bbox = element.bounding_box
    return Position(
        x=bbox.x,
        y=bbox.y,
        width=bbox.width,
        height=bbox.height,
    )


def calculate_distance(pos1: Position, pos2: Position) -> float:
    """
    计算两个位置之间的欧几里得距离（中心点）
    
    Args:
        pos1: 位置 1
        pos2: 位置 2
        
    Returns:
        距离（像素）
    """
    dx = pos2.center_x - pos1.center_x
    dy = pos2.center_y - pos1.center_y
    return math.sqrt(dx * dx + dy * dy)


def calculate_angle(pos1: Position, pos2: Position) -> float:
    """
    计算从 pos1 指向 pos2 的角度
    
    Args:
        pos1: 起始位置
        pos2: 目标位置
        
    Returns:
        角度（度，0-360），0度为正右方，90度为正下方
    """
    dx = pos2.center_x - pos1.center_x
    dy = pos2.center_y - pos1.center_y
    
    # 计算弧度
    angle_rad = math.atan2(dy, dx)
    
    # 转换为度数（0-360）
    angle_deg = math.degrees(angle_rad)
    
    # 确保在 0-360 范围内
    if angle_deg < 0:
        angle_deg += 360
    
    return angle_deg


def is_in_direction(
    anchor_pos: Position,
    element_pos: Position,
    direction: Direction,
    tolerance: float = 45.0,
) -> bool:
    """
    判断元素是否在锚点的指定方向
    
    Args:
        anchor_pos: 锚点位置
        element_pos: 元素位置
        direction: 方向
        tolerance: 角度容差（度）
        
    Returns:
        是否在指定方向
    """
    angle = calculate_angle(anchor_pos, element_pos)
    
    # 方向到角度范围的映射
    direction_angles = {
        Direction.RIGHT: (0, 0),        # 0度
        Direction.BELOW: (90, 90),      # 90度
        Direction.LEFT: (180, 180),     # 180度
        Direction.ABOVE: (270, 270),    # 270度
    }
    
    if direction not in direction_angles:
        # NEAR, FAR, INSIDE 等不基于角度判断
        return True
    
    target_angle_min, target_angle_max = direction_angles[direction]
    
    # 检查角度是否在容差范围内
    if target_angle_min == target_angle_max:
        # 单一方向
        target_angle = target_angle_min
        
        # 处理 0度和 360度的边界
        if target_angle == 0:
            return angle <= tolerance or angle >= (360 - tolerance)
        else:
            return abs(angle - target_angle) <= tolerance
    
    return False


def calculate_overlap(pos1: Position, pos2: Position) -> float:
    """
    计算两个位置的重叠度
    
    Args:
        pos1: 位置 1
        pos2: 位置 2
        
    Returns:
        重叠度（0.0-1.0），0 表示不重叠，1 表示完全重叠
    """
    # 计算重叠区域
    overlap_left = max(pos1.left, pos2.left)
    overlap_right = min(pos1.right, pos2.right)
    overlap_top = max(pos1.top, pos2.top)
    overlap_bottom = min(pos1.bottom, pos2.bottom)
    
    # 如果没有重叠
    if overlap_left >= overlap_right or overlap_top >= overlap_bottom:
        return 0.0
    
    # 计算重叠面积
    overlap_width = overlap_right - overlap_left
    overlap_height = overlap_bottom - overlap_top
    overlap_area = overlap_width * overlap_height
    
    # 计算两个矩形的面积
    area1 = pos1.width * pos1.height
    area2 = pos2.width * pos2.height
    
    # 重叠度 = 重叠面积 / 较小矩形的面积
    smaller_area = min(area1, area2)
    
    if smaller_area == 0:
        return 0.0
    
    return overlap_area / smaller_area


def is_horizontally_aligned(
    pos1: Position,
    pos2: Position,
    threshold: float = 0.2,
) -> bool:
    """
    判断两个元素是否水平对齐
    
    Args:
        pos1: 位置 1
        pos2: 位置 2
        threshold: 对齐阈值（相对于高度的比例）
        
    Returns:
        是否水平对齐
    """
    # 计算中心 Y 坐标的差异
    dy = abs(pos1.center_y - pos2.center_y)
    
    # 相对于较小高度的比例
    min_height = min(pos1.height, pos2.height)
    
    if min_height == 0:
        return False
    
    return dy / min_height <= threshold


def is_vertically_aligned(
    pos1: Position,
    pos2: Position,
    threshold: float = 0.2,
) -> bool:
    """
    判断两个元素是否垂直对齐
    
    Args:
        pos1: 位置 1
        pos2: 位置 2
        threshold: 对齐阈值（相对于宽度的比例）
        
    Returns:
        是否垂直对齐
    """
    # 计算中心 X 坐标的差异
    dx = abs(pos1.center_x - pos2.center_x)
    
    # 相对于较小宽度的比例
    min_width = min(pos1.width, pos2.width)
    
    if min_width == 0:
        return False
    
    return dx / min_width <= threshold
