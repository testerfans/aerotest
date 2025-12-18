"""属性匹配器测试"""

import pytest

from aerotest.browser.dom.cdp_types import EnhancedDOMTreeNode, NodeType
from aerotest.core.funnel.l2.attribute_matcher import AttributeMatcher


class TestAttributeMatcher:
    """测试属性匹配器"""
    
    @pytest.fixture
    def matcher(self):
        """创建匹配器实例"""
        return AttributeMatcher()
    
    @pytest.fixture
    def sample_elements(self):
        """创建示例元素"""
        return [
            # 提交按钮 (有 id)
            EnhancedDOMTreeNode(
                backend_node_id=1,
                node_type=NodeType.ELEMENT_NODE,
                node_name="BUTTON",
                tag_name="button",
                attributes={"id": "submit-btn", "innerText": "提交"},
            ),
            # 确认按钮 (有 name)
            EnhancedDOMTreeNode(
                backend_node_id=2,
                node_type=NodeType.ELEMENT_NODE,
                node_name="BUTTON",
                tag_name="button",
                attributes={"name": "confirm", "innerText": "确认"},
            ),
            # 输入框 (有 placeholder)
            EnhancedDOMTreeNode(
                backend_node_id=3,
                node_type=NodeType.ELEMENT_NODE,
                node_name="INPUT",
                tag_name="input",
                attributes={"placeholder": "请输入用户名", "type": "text"},
            ),
            # 无关元素
            EnhancedDOMTreeNode(
                backend_node_id=4,
                node_type=NodeType.ELEMENT_NODE,
                node_name="DIV",
                tag_name="div",
                attributes={"class": "container"},
            ),
        ]
    
    def test_match_by_attribute_id(self, matcher, sample_elements):
        """测试按 ID 匹配"""
        results = matcher.match_by_attribute(
            elements=sample_elements,
            keywords=["submit"],
            attribute="id",
        )
        
        assert len(results) > 0
        element, score = results[0]
        assert element.backend_node_id == 1
        assert score > 0.5
    
    def test_match_by_attribute_placeholder(self, matcher, sample_elements):
        """测试按 placeholder 匹配"""
        results = matcher.match_by_attribute(
            elements=sample_elements,
            keywords=["用户名"],
            attribute="placeholder",
        )
        
        assert len(results) > 0
        element, score = results[0]
        assert element.backend_node_id == 3
        # placeholder 权重最高 (1.0)
        assert score > 0.7
    
    def test_match_by_attribute_innerText(self, matcher, sample_elements):
        """测试按 innerText 匹配"""
        results = matcher.match_by_attribute(
            elements=sample_elements,
            keywords=["提交"],
            attribute="innerText",
        )
        
        assert len(results) > 0
        element, score = results[0]
        assert element.backend_node_id == 1
    
    def test_match_by_all_attributes(self, matcher, sample_elements):
        """测试匹配所有属性"""
        all_results = matcher.match_by_all_attributes(
            elements=sample_elements,
            keywords=["submit", "提交"],
        )
        
        # 应该匹配到多个属性
        assert len(all_results) > 0
        assert "id" in all_results or "innerText" in all_results
    
    def test_get_best_matches(self, matcher, sample_elements):
        """测试获取最佳匹配"""
        results = matcher.get_best_matches(
            elements=sample_elements,
            keywords=["submit", "提交"],
            top_n=5,
        )
        
        assert len(results) > 0
        
        # 第一个结果应该是得分最高的
        best_match = results[0]
        assert best_match.score > 0.5
        assert best_match.element.backend_node_id == 1
        assert len(best_match.matched_attributes) > 0
        assert len(best_match.match_reasons) > 0
    
    def test_exact_match(self, matcher):
        """测试精确匹配"""
        score = matcher._match_keywords("submit", ["submit"])
        assert score == 1.0
    
    def test_contains_match(self, matcher):
        """测试包含匹配"""
        score = matcher._match_keywords("submit-button", ["submit"])
        assert 0.7 <= score < 1.0
    
    def test_partial_match(self, matcher):
        """测试部分匹配"""
        result = matcher._partial_match("submit-btn", "submit")
        assert result is True
        
        result = matcher._partial_match("hello world", "submit")
        assert result is False
    
    def test_no_match(self, matcher, sample_elements):
        """测试无匹配"""
        results = matcher.match_by_attribute(
            elements=sample_elements,
            keywords=["nonexistent"],
            attribute="id",
        )
        
        assert len(results) == 0
    
    def test_attribute_weights(self, matcher):
        """测试属性权重"""
        assert matcher.get_attribute_weight("placeholder") == 1.0
        assert matcher.get_attribute_weight("id") == 0.9
        assert matcher.get_attribute_weight("class") == 0.4
        assert matcher.get_attribute_weight("unknown") == 0.5
    
    def test_multiple_keywords(self, matcher, sample_elements):
        """测试多个关键词"""
        results = matcher.get_best_matches(
            elements=sample_elements,
            keywords=["提交", "确认", "submit"],
            top_n=5,
        )
        
        # 应该匹配到多个元素
        assert len(results) >= 2
    
    def test_normalized_score(self, matcher, sample_elements):
        """测试得分归一化"""
        results = matcher.get_best_matches(
            elements=sample_elements,
            keywords=["submit", "提交", "button", "btn"],
            top_n=5,
        )
        
        # 所有得分应该在 0.0-1.0 范围内
        for result in results:
            assert 0.0 <= result.score <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

