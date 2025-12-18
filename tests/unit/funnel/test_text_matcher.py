"""文本匹配器测试"""

import pytest

from aerotest.core.funnel.l2.text_matcher import TextMatcher


class TestTextMatcher:
    """测试文本匹配器"""
    
    @pytest.fixture
    def matcher(self):
        """创建匹配器实例"""
        return TextMatcher()
    
    def test_exact_match_success(self, matcher):
        """测试精确匹配成功"""
        score = matcher.exact_match("submit", "submit")
        assert score == 1.0
        
        score = matcher.exact_match("Submit", "submit")
        assert score == 1.0  # 不区分大小写
    
    def test_exact_match_fail(self, matcher):
        """测试精确匹配失败"""
        score = matcher.exact_match("submit", "sumit")
        assert score == 0.0
    
    def test_fuzzy_match(self, matcher):
        """测试模糊匹配"""
        score = matcher.fuzzy_match("submit", "sumit")
        assert 0.7 < score < 1.0
        
        score = matcher.fuzzy_match("submit", "submit-button")
        assert score > 0.5
    
    def test_contains_match(self, matcher):
        """测试包含匹配"""
        score = matcher.contains_match("submit-button", "submit")
        assert 0.6 <= score <= 1.0
        
        score = matcher.contains_match("hello", "submit")
        assert score == 0.0
    
    def test_partial_ratio_match(self, matcher):
        """测试部分匹配"""
        score = matcher.partial_ratio_match("click submit button", "submit")
        assert score > 0.8
    
    def test_match_auto_exact(self, matcher):
        """测试自动匹配 - 精确"""
        score = matcher.match("submit", "submit")
        assert score == 1.0
    
    def test_match_auto_contains(self, matcher):
        """测试自动匹配 - 包含"""
        score = matcher.match("submit-button", "submit")
        assert score > 0.6
    
    def test_match_auto_fuzzy(self, matcher):
        """测试自动匹配 - 模糊"""
        score = matcher.match("sumit", "submit")
        assert score > 0.7
    
    def test_match_strategy_exact(self, matcher):
        """测试指定策略 - 精确"""
        score = matcher.match("submit", "submit", strategy="exact")
        assert score == 1.0
        
        score = matcher.match("submit-btn", "submit", strategy="exact")
        assert score == 0.0
    
    def test_match_any(self, matcher):
        """测试匹配任意关键词"""
        score = matcher.match_any(
            "submit-button",
            ["submit", "confirm", "send"],
        )
        assert score > 0.6  # 应该匹配到 "submit"
    
    def test_match_all(self, matcher):
        """测试匹配所有关键词"""
        score = matcher.match_all(
            "submit confirmation button",
            ["submit", "button"],
        )
        assert score > 0.5
    
    def test_is_similar(self, matcher):
        """测试相似度判断"""
        assert matcher.is_similar("submit", "submit") is True
        assert matcher.is_similar("submit", "sumit", threshold=0.7) is True
        assert matcher.is_similar("submit", "cancel", threshold=0.8) is False
    
    def test_empty_text(self, matcher):
        """测试空文本"""
        assert matcher.exact_match("", "submit") == 0.0
        assert matcher.fuzzy_match("", "submit") == 0.0
        assert matcher.contains_match("", "submit") == 0.0
    
    def test_case_insensitive(self, matcher):
        """测试大小写不敏感"""
        score1 = matcher.match("Submit", "submit")
        score2 = matcher.match("SUBMIT", "submit")
        assert score1 == score2 == 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

