"""邻近检测器测试"""

import pytest

from aerotest.browser.dom.cdp_types import DOMRect, EnhancedDOMTreeNode, NodeType
from aerotest.core.funnel.l3.proximity_detector import ProximityDetector
from aerotest.core.funnel.l3.types import Direction


class TestProximityDetector:
    """测试邻近检测器"""
    
    @pytest.fixture
    def detector(self):
        """创建检测器实例"""
        return ProximityDetector()
    
    @pytest.fixture
    def sample_elements(self):
        """创建示例元素"""
        # 锚点元素（中心）
        anchor = EnhancedDOMTreeNode(
            backend_node_id=1,
            node_type=NodeType.ELEMENT_NODE,
            node_name="INPUT",
            tag_name="input",
            bounding_box=DOMRect(x=100, y=100, width=200, height=30),
        )
        
        # 右边的元素
        right_elem = EnhancedDOMTreeNode(
            backend_node_id=2,
            node_type=NodeType.ELEMENT_NODE,
            node_name="BUTTON",
            tag_name="button",
            bounding_box=DOMRect(x=320, y=100, width=50, height=30),
        )
        
        # 下方的元素
        below_elem = EnhancedDOMTreeNode(
            backend_node_id=3,
            node_type=NodeType.ELEMENT_NODE,
            node_name="DIV",
            tag_name="div",
            bounding_box=DOMRect(x=100, y=150, width=200, height=50),
        )
        
        # 左边的元素
        left_elem = EnhancedDOMTreeNode(
            backend_node_id=4,
            node_type=NodeType.ELEMENT_NODE,
            node_name="LABEL",
            tag_name="label",
            bounding_box=DOMRect(x=20, y=100, width=70, height=30),
        )
        
        # 远处的元素
        far_elem = EnhancedDOMTreeNode(
            backend_node_id=5,
            node_type=NodeType.ELEMENT_NODE,
            node_name="DIV",
            tag_name="div",
            bounding_box=DOMRect(x=500, y=500, width=100, height=100),
        )
        
        return {
            "anchor": anchor,
            "right": right_elem,
            "below": below_elem,
            "left": left_elem,
            "far": far_elem,
        }
    
    def test_find_nearby_elements_right(self, detector, sample_elements):
        """测试查找右边的元素"""
        anchor = sample_elements["anchor"]
        candidates = [
            sample_elements["right"],
            sample_elements["below"],
            sample_elements["left"],
        ]
        
        results = detector.find_nearby_elements(
            anchor=anchor,
            candidates=candidates,
            direction=Direction.RIGHT,
        )
        
        assert len(results) >= 1
        assert results[0].element.backend_node_id == 2  # 右边的元素
        assert results[0].direction_match is True
    
    def test_find_nearby_elements_below(self, detector, sample_elements):
        """测试查找下方的元素"""
        anchor = sample_elements["anchor"]
        candidates = [
            sample_elements["right"],
            sample_elements["below"],
            sample_elements["left"],
        ]
        
        results = detector.find_nearby_elements(
            anchor=anchor,
            candidates=candidates,
            direction=Direction.BELOW,
        )
        
        assert len(results) >= 1
        assert results[0].element.backend_node_id == 3  # 下方的元素
    
    def test_find_nearby_elements_no_direction(self, detector, sample_elements):
        """测试查找所有邻近元素（无方向限制）"""
        anchor = sample_elements["anchor"]
        candidates = [
            sample_elements["right"],
            sample_elements["below"],
            sample_elements["left"],
        ]
        
        results = detector.find_nearby_elements(
            anchor=anchor,
            candidates=candidates,
            direction=None,
        )
        
        # 应该找到所有邻近的元素
        assert len(results) == 3
    
    def test_max_distance_filter(self, detector, sample_elements):
        """测试最大距离过滤"""
        anchor = sample_elements["anchor"]
        candidates = [
            sample_elements["right"],
            sample_elements["far"],  # 很远的元素
        ]
        
        results = detector.find_nearby_elements(
            anchor=anchor,
            candidates=candidates,
            max_distance=100.0,  # 很小的距离
        )
        
        # 远处的元素应该被过滤掉
        assert len(results) == 1
        assert results[0].element.backend_node_id != 5
    
    def test_calculate_spatial_relation(self, detector, sample_elements):
        """测试计算空间关系"""
        anchor = sample_elements["anchor"]
        right_elem = sample_elements["right"]
        
        relation = detector.calculate_spatial_relation(anchor, right_elem)
        
        assert relation is not None
        assert relation.direction == Direction.RIGHT
        assert relation.distance > 0
        assert 0 <= relation.angle < 90  # 大致在右边（0度附近）
    
    def test_get_closest_element(self, detector, sample_elements):
        """测试获取最近的元素"""
        anchor = sample_elements["anchor"]
        candidates = [
            sample_elements["right"],
            sample_elements["below"],
            sample_elements["far"],
        ]
        
        closest = detector.get_closest_element(
            anchor=anchor,
            candidates=candidates,
        )
        
        assert closest is not None
        # 应该是下方的元素（最近）
        assert closest.backend_node_id in [2, 3]
    
    def test_filter_by_distance_range(self, detector, sample_elements):
        """测试按距离范围过滤"""
        anchor = sample_elements["anchor"]
        candidates = [
            sample_elements["right"],
            sample_elements["below"],
            sample_elements["left"],
        ]
        
        results = detector.find_nearby_elements(
            anchor=anchor,
            candidates=candidates,
        )
        
        # 过滤出距离在 50-100 像素之间的元素
        filtered = detector.filter_by_distance_range(
            results,
            min_distance=10.0,
            max_distance=100.0,
        )
        
        assert len(filtered) <= len(results)
    
    def test_exclude_anchor_itself(self, detector, sample_elements):
        """测试排除锚点本身"""
        anchor = sample_elements["anchor"]
        candidates = [
            anchor,  # 包含锚点本身
            sample_elements["right"],
        ]
        
        results = detector.find_nearby_elements(
            anchor=anchor,
            candidates=candidates,
        )
        
        # 结果中不应包含锚点本身
        assert all(r.element.backend_node_id != anchor.backend_node_id for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

