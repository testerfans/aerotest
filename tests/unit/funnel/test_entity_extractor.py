"""实体提取器测试"""

import pytest

from aerotest.core.funnel.l1.entity_extractor import EntityExtractor
from aerotest.core.funnel.types import ElementType


class TestEntityExtractor:
    """测试实体提取器"""
    
    @pytest.fixture
    def extractor(self):
        """创建提取器实例"""
        return EntityExtractor()
    
    def test_extract_button(self, extractor):
        """测试提取按钮信息"""
        result = extractor.extract("点击提交按钮")
        
        assert result["target"] == "提交按钮"
        assert result["target_type"] == ElementType.BUTTON
        assert "提交" in result["keywords"]
        assert "按钮" in result["keywords"]
    
    def test_extract_input(self, extractor):
        """测试提取输入框信息"""
        result = extractor.extract("输入用户名")
        
        assert result["target_type"] == ElementType.INPUT
        assert "用户名" in result["keywords"]
    
    def test_extract_with_common_names(self, extractor):
        """测试常见名称识别"""
        test_cases = [
            ("提交", ElementType.BUTTON),
            ("用户名", ElementType.INPUT),
            ("密码", ElementType.INPUT),
            ("邮箱", ElementType.INPUT),
        ]
        
        for text, expected_type in test_cases:
            result = extractor.extract(text)
            assert result["target_type"] == expected_type, f"Failed: {text}"
    
    def test_remove_action_words(self, extractor):
        """测试移除动作词"""
        result = extractor.extract("点击提交按钮", action_keywords=["点击"])
        
        # 动作词应该被移除
        assert "提交按钮" in result["target"]
        assert "点击" not in result["keywords"] or len(result["keywords"]) > 1
    
    def test_attribute_inference_submit(self, extractor):
        """测试属性推断 - 提交按钮"""
        result = extractor.extract("提交按钮")
        
        # 应该推断出 type=submit
        assert result["attributes"].get("type") == "submit"
    
    def test_attribute_inference_password(self, extractor):
        """测试属性推断 - 密码输入框"""
        result = extractor.extract("密码输入框")
        
        # 应该推断出 type=password
        assert result["attributes"].get("type") == "password"
    
    def test_attribute_inference_email(self, extractor):
        """测试属性推断 - 邮箱输入框"""
        result = extractor.extract("邮箱输入框")
        
        # 应该推断出 type=email
        assert result["attributes"].get("type") == "email"
    
    def test_extract_checkbox(self, extractor):
        """测试提取复选框信息"""
        result = extractor.extract("勾选同意复选框")
        
        assert result["target_type"] == ElementType.CHECKBOX
        assert "同意" in result["keywords"]
    
    def test_extract_select(self, extractor):
        """测试提取下拉框信息"""
        result = extractor.extract("选择下拉框")
        
        assert result["target_type"] == ElementType.SELECT
    
    def test_extract_link(self, extractor):
        """测试提取链接信息"""
        result = extractor.extract("点击链接")
        
        assert result["target_type"] == ElementType.LINK
    
    def test_keywords_extraction(self, extractor):
        """测试关键词提取"""
        result = extractor.extract("提交注册表单按钮")
        
        keywords = result["keywords"]
        # 应该包含多个有用的关键词
        assert len(keywords) > 0
        assert any(k in ["提交", "注册", "表单", "按钮"] for k in keywords)
    
    def test_empty_text(self, extractor):
        """测试空文本"""
        result = extractor.extract("")
        
        assert result["target"] == ""
        assert result["target_type"] is None
        assert result["keywords"] == []
    
    def test_english_text(self, extractor):
        """测试英文文本"""
        result = extractor.extract("submit button")
        
        assert result["target_type"] == ElementType.BUTTON
        assert "submit" in result["keywords"] or "button" in result["keywords"]
    
    def test_confidence(self, extractor):
        """测试置信度计算"""
        # 明确的类型关键词应该有高置信度
        confidence = extractor.get_confidence("提交按钮", ElementType.BUTTON)
        assert confidence > 0.7
        
        # 不匹配的类型应该有低置信度
        confidence = extractor.get_confidence("随便看看", ElementType.BUTTON)
        assert confidence < 0.6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

