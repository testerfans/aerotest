"""类型匹配器测试"""

import pytest

from aerotest.browser.dom.cdp_types import EnhancedDOMTreeNode, NodeType
from aerotest.core.funnel.l2.type_matcher import TypeMatcher
from aerotest.core.funnel.types import ElementType


class TestTypeMatcher:
    """测试类型匹配器"""
    
    @pytest.fixture
    def matcher(self):
        """创建匹配器实例"""
        return TypeMatcher()
    
    @pytest.fixture
    def sample_elements(self):
        """创建示例元素"""
        return [
            # 按钮
            EnhancedDOMTreeNode(
                backend_node_id=1,
                node_type=NodeType.ELEMENT_NODE,
                node_name="BUTTON",
                tag_name="button",
                attributes={},
            ),
            # 提交按钮 (input)
            EnhancedDOMTreeNode(
                backend_node_id=2,
                node_type=NodeType.ELEMENT_NODE,
                node_name="INPUT",
                tag_name="input",
                attributes={"type": "submit"},
            ),
            # 文本输入框
            EnhancedDOMTreeNode(
                backend_node_id=3,
                node_type=NodeType.ELEMENT_NODE,
                node_name="INPUT",
                tag_name="input",
                attributes={"type": "text"},
            ),
            # 复选框
            EnhancedDOMTreeNode(
                backend_node_id=4,
                node_type=NodeType.ELEMENT_NODE,
                node_name="INPUT",
                tag_name="input",
                attributes={"type": "checkbox"},
            ),
            # 链接
            EnhancedDOMTreeNode(
                backend_node_id=5,
                node_type=NodeType.ELEMENT_NODE,
                node_name="A",
                tag_name="a",
                attributes={"href": "https://example.com"},
            ),
        ]
    
    def test_match_by_tag(self, matcher, sample_elements):
        """测试按标签名筛选"""
        buttons = matcher.match_by_tag(sample_elements, "button")
        assert len(buttons) == 1
        assert buttons[0].backend_node_id == 1
    
    def test_match_by_type_button(self, matcher, sample_elements):
        """测试按类型筛选 - 按钮"""
        buttons = matcher.match_by_type(sample_elements, ElementType.BUTTON)
        assert len(buttons) == 2  # button 和 input[type=submit]
    
    def test_match_by_type_input(self, matcher, sample_elements):
        """测试按类型筛选 - 输入框"""
        inputs = matcher.match_by_type(sample_elements, ElementType.INPUT)
        assert len(inputs) == 1  # input[type=text]
    
    def test_match_by_type_checkbox(self, matcher, sample_elements):
        """测试按类型筛选 - 复选框"""
        checkboxes = matcher.match_by_type(sample_elements, ElementType.CHECKBOX)
        assert len(checkboxes) == 1
    
    def test_match_by_type_link(self, matcher, sample_elements):
        """测试按类型筛选 - 链接"""
        links = matcher.match_by_type(sample_elements, ElementType.LINK)
        assert len(links) == 1
    
    def test_match_by_role(self, matcher):
        """测试按 role 筛选"""
        elements = [
            EnhancedDOMTreeNode(
                backend_node_id=1,
                node_type=NodeType.ELEMENT_NODE,
                node_name="DIV",
                tag_name="div",
                attributes={"role": "button"},
            ),
        ]
        
        buttons = matcher.match_by_role(elements, "button")
        assert len(buttons) == 1
    
    def test_is_type_match(self, matcher, sample_elements):
        """测试类型匹配判断"""
        button = sample_elements[0]
        assert matcher.is_type_match(button, ElementType.BUTTON) is True
        assert matcher.is_type_match(button, ElementType.INPUT) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

