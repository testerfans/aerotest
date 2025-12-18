"""锚点定位器测试"""

import pytest

from aerotest.browser.dom.cdp_types import DOMRect, EnhancedDOMTreeNode, NodeType
from aerotest.browser.dom.views import SerializedDOMState
from aerotest.core.funnel.l3.anchor_locator import AnchorLocator
from aerotest.core.funnel.l3.types import Direction


class TestAnchorLocator:
    """测试锚点定位器"""
    
    @pytest.fixture
    def locator(self):
        """创建定位器实例"""
        return AnchorLocator()
    
    @pytest.fixture
    def sample_dom_state(self):
        """创建示例 DOM 状态"""
        nodes = [
            # 用户名输入框
            EnhancedDOMTreeNode(
                backend_node_id=1,
                node_type=NodeType.ELEMENT_NODE,
                node_name="INPUT",
                tag_name="input",
                attributes={
                    "placeholder": "请输入用户名",
                    "id": "username",
                    "type": "text",
                },
                bounding_box=DOMRect(x=100, y=100, width=200, height=30),
                is_clickable=True,
            ),
            # 清除按钮
            EnhancedDOMTreeNode(
                backend_node_id=2,
                node_type=NodeType.ELEMENT_NODE,
                node_name="BUTTON",
                tag_name="button",
                attributes={
                    "innerText": "清除",
                    "class": "clear-btn",
                },
                bounding_box=DOMRect(x=310, y=100, width=50, height=30),
                is_clickable=True,
            ),
            # 搜索框
            EnhancedDOMTreeNode(
                backend_node_id=3,
                node_type=NodeType.ELEMENT_NODE,
                node_name="INPUT",
                tag_name="input",
                attributes={
                    "placeholder": "搜索",
                    "id": "search",
                    "type": "search",
                },
                bounding_box=DOMRect(x=100, y=200, width=300, height=40),
                is_clickable=True,
            ),
        ]
        
        return SerializedDOMState(
            simplified_nodes=nodes,
            selector_map={},
        )
    
    def test_extract_anchor_right(self, locator):
        """测试提取右边的锚点"""
        instruction = "点击用户名输入框右边的按钮"
        
        anchor_info = locator.extract_anchor(instruction)
        
        assert anchor_info is not None
        assert "用户名" in anchor_info.description or "输入框" in anchor_info.description
        assert anchor_info.direction == Direction.RIGHT
        assert "按钮" in anchor_info.target_description
    
    def test_extract_anchor_below(self, locator):
        """测试提取下方的锚点"""
        instruction = "点击搜索框下方的结果"
        
        anchor_info = locator.extract_anchor(instruction)
        
        assert anchor_info is not None
        assert "搜索框" in anchor_info.description
        assert anchor_info.direction == Direction.BELOW
        assert "结果" in anchor_info.target_description
    
    def test_extract_anchor_with_distance(self, locator):
        """测试提取带距离的锚点"""
        instruction = "点击按钮旁边的链接"
        
        anchor_info = locator.extract_anchor(instruction)
        
        assert anchor_info is not None
        assert anchor_info.distance is not None
        assert anchor_info.distance > 0
    
    def test_locate_anchor(self, locator, sample_dom_state):
        """测试定位锚点元素"""
        anchor_info = locator.extract_anchor("点击用户名输入框右边的按钮")
        
        assert anchor_info is not None
        
        anchor_element = locator.locate_anchor(anchor_info, sample_dom_state)
        
        assert anchor_element is not None
        assert anchor_element.backend_node_id == 1  # 用户名输入框
    
    def test_has_spatial_relation(self, locator):
        """测试空间关系检测"""
        # 有空间关系
        assert locator.has_spatial_relation("点击用户名输入框右边的按钮") is True
        assert locator.has_spatial_relation("搜索框下方的结果") is True
        
        # 无空间关系
        assert locator.has_spatial_relation("点击提交按钮") is False
    
    def test_no_anchor(self, locator):
        """测试无锚点的指令"""
        instruction = "点击提交按钮"
        
        anchor_info = locator.extract_anchor(instruction)
        
        assert anchor_info is None
    
    def test_recognize_multiple_directions(self, locator):
        """测试识别多种方向"""
        test_cases = [
            ("左边", Direction.LEFT),
            ("右侧", Direction.RIGHT),
            ("上方", Direction.ABOVE),
            ("下面", Direction.BELOW),
            ("里面", Direction.INSIDE),
            ("旁边", Direction.NEAR),
        ]
        
        for direction_word, expected_direction in test_cases:
            direction = locator._recognize_direction(direction_word)
            assert direction == expected_direction


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

