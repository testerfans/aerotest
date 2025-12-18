"""槽位填充器测试"""

import pytest

from aerotest.core.funnel.l1.slot_filler import SlotFiller
from aerotest.core.funnel.types import ActionType, ElementType


class TestSlotFiller:
    """测试槽位填充器"""
    
    @pytest.fixture
    def filler(self):
        """创建填充器实例"""
        return SlotFiller()
    
    def test_fill_click_button(self, filler):
        """测试填充点击按钮槽位"""
        slot = filler.fill("点击提交按钮")
        
        assert slot.action == ActionType.CLICK
        assert slot.target == "提交按钮"
        assert slot.target_type == ElementType.BUTTON
        assert "提交" in slot.keywords
        assert slot.confidence > 0.5
    
    def test_fill_input_text(self, filler):
        """测试填充输入槽位"""
        slot = filler.fill("输入用户名")
        
        assert slot.action == ActionType.INPUT
        assert slot.target_type == ElementType.INPUT
        assert "用户名" in slot.keywords
    
    def test_fill_with_value(self, filler):
        """测试提取输入值"""
        # 引号包围的值
        slot = filler.fill("输入用户名 'admin'")
        assert slot.value == "admin"
        
        # 空格分隔的值
        slot = filler.fill("输入密码 123456")
        assert slot.value == "123456"
    
    def test_fill_select(self, filler):
        """测试填充选择槽位"""
        slot = filler.fill("选择下拉框")
        
        assert slot.action in [ActionType.SELECT, ActionType.CLICK]
        assert slot.target_type == ElementType.SELECT
    
    def test_action_element_match(self, filler):
        """测试动作和元素匹配"""
        # CLICK + BUTTON 应该匹配
        slot = filler.fill("点击按钮")
        assert slot.action == ActionType.CLICK
        assert slot.target_type == ElementType.BUTTON
        # 匹配应该提升置信度
        assert slot.confidence > 0.6
    
    def test_submit_button_attributes(self, filler):
        """测试提交按钮属性推断"""
        slot = filler.fill("点击提交按钮")
        
        # 应该推断出 type=submit
        assert slot.attributes.get("type") == "submit"
    
    def test_password_input_attributes(self, filler):
        """测试密码输入框属性推断"""
        slot = filler.fill("输入密码")
        
        # 应该推断出 type=password
        assert slot.attributes.get("type") == "password"
    
    def test_confidence_calculation(self, filler):
        """测试置信度计算"""
        # 明确的指令应该有高置信度
        slot = filler.fill("点击提交按钮")
        assert slot.confidence > 0.7
        
        # 模糊的指令应该有较低置信度
        slot = filler.fill("随便看看")
        assert slot.confidence < 0.5
    
    def test_empty_text(self, filler):
        """测试空文本"""
        slot = filler.fill("")
        
        assert slot.action == ActionType.UNKNOWN
        assert slot.confidence == 0.0
    
    def test_keywords_extraction(self, filler):
        """测试关键词提取"""
        slot = filler.fill("点击提交注册表单按钮")
        
        # 应该包含多个关键词
        assert len(slot.keywords) > 0
        assert any(k in ["提交", "注册", "表单", "按钮"] for k in slot.keywords)
    
    def test_batch_parsing(self, filler):
        """测试批量解析"""
        instructions = [
            "点击提交按钮",
            "输入用户名",
            "选择下拉框",
        ]
        
        slots = filler.parse_batch(instructions)
        
        assert len(slots) == 3
        assert slots[0].action == ActionType.CLICK
        assert slots[1].action == ActionType.INPUT
        assert slots[2].action in [ActionType.SELECT, ActionType.CLICK]
    
    def test_complex_instruction(self, filler):
        """测试复杂指令"""
        slot = filler.fill("在用户名输入框中输入 admin123")
        
        assert slot.action == ActionType.INPUT
        assert "用户名" in slot.keywords
        assert slot.value == "admin123"
    
    def test_english_instruction(self, filler):
        """测试英文指令"""
        slot = filler.fill("click submit button")
        
        assert slot.action == ActionType.CLICK
        assert slot.target_type == ElementType.BUTTON


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

