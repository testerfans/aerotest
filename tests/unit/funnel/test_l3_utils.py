"""L3 工具函数测试"""

import pytest

from aerotest.browser.dom.cdp_types import DOMRect, EnhancedDOMTreeNode, NodeType
from aerotest.core.funnel.l3.types import Direction, Position
from aerotest.core.funnel.l3.utils import (
    calculate_angle,
    calculate_distance,
    calculate_overlap,
    get_element_position,
    is_horizontally_aligned,
    is_in_direction,
    is_vertically_aligned,
)


class TestL3Utils:
    """测试 L3 工具函数"""
    
    def test_get_element_position(self):
        """测试获取元素位置"""
        element = EnhancedDOMTreeNode(
            backend_node_id=1,
            node_type=NodeType.ELEMENT_NODE,
            node_name="DIV",
            tag_name="div",
            bounding_box=DOMRect(x=10, y=20, width=100, height=50),
        )
        
        pos = get_element_position(element)
        
        assert pos is not None
        assert pos.x == 10
        assert pos.y == 20
        assert pos.width == 100
        assert pos.height == 50
        assert pos.center_x == 60  # 10 + 100/2
        assert pos.center_y == 45  # 20 + 50/2
    
    def test_calculate_distance(self):
        """测试计算距离"""
        pos1 = Position(x=0, y=0, width=10, height=10)
        pos2 = Position(x=30, y=40, width=10, height=10)
        
        # 中心点: (5, 5) 和 (35, 45)
        # 距离 = sqrt((35-5)^2 + (45-5)^2) = sqrt(900 + 1600) = 50
        distance = calculate_distance(pos1, pos2)
        
        assert distance == 50.0
    
    def test_calculate_angle(self):
        """测试计算角度"""
        pos1 = Position(x=0, y=0, width=10, height=10)
        
        # 正右方
        pos2 = Position(x=100, y=0, width=10, height=10)
        angle = calculate_angle(pos1, pos2)
        assert 0 <= angle < 10  # 接近 0度
        
        # 正下方
        pos3 = Position(x=0, y=100, width=10, height=10)
        angle = calculate_angle(pos1, pos3)
        assert 85 <= angle <= 95  # 接近 90度
        
        # 正左方
        pos4 = Position(x=-100, y=0, width=10, height=10)
        angle = calculate_angle(pos1, pos4)
        assert 175 <= angle <= 185  # 接近 180度
        
        # 正上方
        pos5 = Position(x=0, y=-100, width=10, height=10)
        angle = calculate_angle(pos1, pos5)
        assert 265 <= angle <= 275  # 接近 270度
    
    def test_is_in_direction(self):
        """测试方向判断"""
        anchor = Position(x=100, y=100, width=50, height=50)
        
        # 右边的元素
        right_elem = Position(x=200, y=100, width=50, height=50)
        assert is_in_direction(anchor, right_elem, Direction.RIGHT) is True
        assert is_in_direction(anchor, right_elem, Direction.LEFT) is False
        
        # 下方的元素
        below_elem = Position(x=100, y=200, width=50, height=50)
        assert is_in_direction(anchor, below_elem, Direction.BELOW) is True
        assert is_in_direction(anchor, below_elem, Direction.ABOVE) is False
    
    def test_calculate_overlap(self):
        """测试重叠度计算"""
        pos1 = Position(x=0, y=0, width=100, height=100)
        
        # 完全重叠
        pos2 = Position(x=0, y=0, width=100, height=100)
        assert calculate_overlap(pos1, pos2) == 1.0
        
        # 不重叠
        pos3 = Position(x=200, y=200, width=100, height=100)
        assert calculate_overlap(pos1, pos3) == 0.0
        
        # 部分重叠
        pos4 = Position(x=50, y=50, width=100, height=100)
        overlap = calculate_overlap(pos1, pos4)
        assert 0 < overlap < 1.0
    
    def test_is_horizontally_aligned(self):
        """测试水平对齐"""
        pos1 = Position(x=0, y=100, width=50, height=50)
        
        # 水平对齐（Y 坐标相同）
        pos2 = Position(x=100, y=100, width=50, height=50)
        assert is_horizontally_aligned(pos1, pos2) is True
        
        # 不对齐
        pos3 = Position(x=100, y=200, width=50, height=50)
        assert is_horizontally_aligned(pos1, pos3) is False
    
    def test_is_vertically_aligned(self):
        """测试垂直对齐"""
        pos1 = Position(x=100, y=0, width=50, height=50)
        
        # 垂直对齐（X 坐标相同）
        pos2 = Position(x=100, y=100, width=50, height=50)
        assert is_vertically_aligned(pos1, pos2) is True
        
        # 不对齐
        pos3 = Position(x=200, y=100, width=50, height=50)
        assert is_vertically_aligned(pos1, pos3) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

