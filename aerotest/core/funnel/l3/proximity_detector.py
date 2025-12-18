"""邻近检测器

基于空间位置关系查找邻近元素
"""

from typing import Optional

from aerotest.browser.dom.views import EnhancedDOMTreeNode
from aerotest.core.funnel.l3.types import Direction, ProximityResult, SpatialRelation
from aerotest.core.funnel.l3.utils import (
    calculate_angle,
    calculate_distance,
    calculate_overlap,
    get_element_position,
    is_horizontally_aligned,
    is_in_direction,
    is_vertically_aligned,
)
from aerotest.utils import get_logger

logger = get_logger("aerotest.funnel.l3.proximity")


class ProximityDetector:
    """邻近检测器
    
    基于空间位置关系查找邻近元素�?
    1. 计算元素间距�?
    2. 判断方向关系
    3. 计算对齐�?
    4. 综合评分排序
    
    Example:
        ```python
        detector = ProximityDetector()
        
        # 查找锚点右边的元�?
        results = detector.find_nearby_elements(
            anchor=anchor_element,
            candidates=all_elements,
            direction=Direction.RIGHT,
            max_distance=200.0,
        )
        
        # 获取最佳匹�?
        if results:
            best = results[0]
            print(f"找到元素，距�? {best.distance:.1f}px")
        ```
    """
    
    def __init__(
        self,
        max_distance: float = 300.0,
        direction_tolerance: float = 45.0,
        alignment_bonus: float = 0.2,
    ):
        """
        初始化邻近检测器
        
        Args:
            max_distance: 最大搜索距离（像素�?
            direction_tolerance: 方向容差（度�?
            alignment_bonus: 对齐奖励分数
        """
        self.max_distance = max_distance
        self.direction_tolerance = direction_tolerance
        self.alignment_bonus = alignment_bonus
        logger.debug("邻近检测器初始化完�?)
    
    def find_nearby_elements(
        self,
        anchor: EnhancedDOMTreeNode,
        candidates: list[EnhancedDOMTreeNode],
        direction: Optional[Direction] = None,
        max_distance: Optional[float] = None,
    ) -> list[ProximityResult]:
        """
        查找邻近元素
        
        Args:
            anchor: 锚点元素
            candidates: 候选元素列�?
            direction: 方向限制（None 表示不限制）
            max_distance: 最大距离（None 使用默认值）
            
        Returns:
            邻近检测结果列表（按得分降序）
        """
        if max_distance is None:
            max_distance = self.max_distance
        
        anchor_pos = get_element_position(anchor)
        if not anchor_pos:
            logger.warning("锚点元素没有位置信息")
            return []
        
        results = []
        
        for candidate in candidates:
            # 排除锚点本身
            if candidate.backend_node_id == anchor.backend_node_id:
                continue
            
            candidate_pos = get_element_position(candidate)
            if not candidate_pos:
                continue
            
            # 计算距离
            distance = calculate_distance(anchor_pos, candidate_pos)
            
            # 距离过滤
            if distance > max_distance:
                continue
            
            # 计算角度
            angle = calculate_angle(anchor_pos, candidate_pos)
            
            # 方向匹配
            direction_match = True
            if direction:
                direction_match = is_in_direction(
                    anchor_pos,
                    candidate_pos,
                    direction,
                    self.direction_tolerance,
                )
            
            # 如果指定了方向但不匹配，跳过
            if direction and not direction_match:
                continue
            
            # 计算得分
            score = self._calculate_proximity_score(
                anchor_pos=anchor_pos,
                candidate_pos=candidate_pos,
                distance=distance,
                direction_match=direction_match,
                direction=direction,
            )
            
            result = ProximityResult(
                element=candidate,
                distance=distance,
                direction_match=direction_match,
                angle=angle,
                score=score,
            )
            
            results.append(result)
        
        # 排序（按得分降序�?
        results.sort(reverse=True)
        
        logger.info(f"邻近搜索: 找到 {len(results)} 个候�?)
        
        return results
    
    def _calculate_proximity_score(
        self,
        anchor_pos,
        candidate_pos,
        distance: float,
        direction_match: bool,
        direction: Optional[Direction],
    ) -> float:
        """
        计算邻近得分
        
        Args:
            anchor_pos: 锚点位置
            candidate_pos: 候选元素位�?
            distance: 距离
            direction_match: 方向是否匹配
            direction: 方向
            
        Returns:
            得分�?.0-1.0�?
        """
        # 1. 基础分：距离越近得分越高
        # 使用反比例函数：score = 1 / (1 + distance/100)
        distance_score = 1.0 / (1.0 + distance / 100.0)
        
        # 2. 方向匹配奖励
        direction_bonus = 0.2 if direction_match else 0.0
        
        # 3. 对齐奖励
        alignment_bonus = 0.0
        
        if direction in [Direction.LEFT, Direction.RIGHT]:
            # 水平方向，检查是否垂直对�?
            if is_horizontally_aligned(anchor_pos, candidate_pos):
                alignment_bonus = self.alignment_bonus
        elif direction in [Direction.ABOVE, Direction.BELOW]:
            # 垂直方向，检查是否水平对�?
            if is_vertically_aligned(anchor_pos, candidate_pos):
                alignment_bonus = self.alignment_bonus
        
        # 4. 重叠惩罚
        overlap = calculate_overlap(anchor_pos, candidate_pos)
        overlap_penalty = overlap * 0.3  # 重叠越多，惩罚越�?
        
        # 综合得分
        score = distance_score + direction_bonus + alignment_bonus - overlap_penalty
        
        # 确保�?0-1 范围�?
        score = max(0.0, min(1.0, score))
        
        return score
    
    def calculate_spatial_relation(
        self,
        anchor: EnhancedDOMTreeNode,
        element: EnhancedDOMTreeNode,
    ) -> Optional[SpatialRelation]:
        """
        计算两个元素的空间关�?
        
        Args:
            anchor: 锚点元素
            element: 目标元素
            
        Returns:
            空间关系
        """
        anchor_pos = get_element_position(anchor)
        element_pos = get_element_position(element)
        
        if not anchor_pos or not element_pos:
            return None
        
        distance = calculate_distance(anchor_pos, element_pos)
        angle = calculate_angle(anchor_pos, element_pos)
        overlap = calculate_overlap(anchor_pos, element_pos)
        
        # 判断主要方向
        direction = self._determine_direction(angle)
        
        return SpatialRelation(
            element1=anchor,
            element2=element,
            distance=distance,
            direction=direction,
            angle=angle,
            overlap=overlap,
        )
    
    def _determine_direction(self, angle: float) -> Direction:
        """
        根据角度确定方向
        
        Args:
            angle: 角度（度�?-360�?
            
        Returns:
            方向
        """
        # 0�?= 右，90�?= 下，180�?= 左，270�?= �?
        if angle < 45 or angle >= 315:
            return Direction.RIGHT
        elif 45 <= angle < 135:
            return Direction.BELOW
        elif 135 <= angle < 225:
            return Direction.LEFT
        else:
            return Direction.ABOVE
    
    def filter_by_distance_range(
        self,
        results: list[ProximityResult],
        min_distance: float = 0.0,
        max_distance: float = float('inf'),
    ) -> list[ProximityResult]:
        """
        按距离范围过滤结�?
        
        Args:
            results: 邻近检测结�?
            min_distance: 最小距�?
            max_distance: 最大距�?
            
        Returns:
            过滤后的结果
        """
        return [
            r for r in results
            if min_distance <= r.distance <= max_distance
        ]
    
    def get_closest_element(
        self,
        anchor: EnhancedDOMTreeNode,
        candidates: list[EnhancedDOMTreeNode],
        direction: Optional[Direction] = None,
    ) -> Optional[EnhancedDOMTreeNode]:
        """
        获取最近的元素
        
        Args:
            anchor: 锚点元素
            candidates: 候选元素列�?
            direction: 方向限制
            
        Returns:
            最近的元素
        """
        results = self.find_nearby_elements(anchor, candidates, direction)
        
        if results:
            return results[0].element
        
        return None

