"""L1 引擎集成测试"""

import pytest

from aerotest.core.funnel.l1.l1_engine import L1Engine
from aerotest.core.funnel.types import ActionType, ElementType, FunnelContext


class TestL1Engine:
    """测试 L1 引擎"""
    
    @pytest.fixture
    def engine(self):
        """创建引擎实例"""
        return L1Engine()
    
    @pytest.mark.asyncio
    async def test_process_click_button(self, engine):
        """测试处理点击按钮指令"""
        context = FunnelContext(instruction="点击提交按钮")
        context = await engine.process(context)
        
        slot = context.action_slot
        assert slot is not None
        assert slot.action == ActionType.CLICK
        assert slot.target_type == ElementType.BUTTON
        assert len(slot.keywords) > 0
        assert slot.confidence > 0.5
    
    @pytest.mark.asyncio
    async def test_process_input_text(self, engine):
        """测试处理输入文本指令"""
        context = FunnelContext(instruction="输入用户名")
        context = await engine.process(context)
        
        slot = context.action_slot
        assert slot.action == ActionType.INPUT
        assert slot.target_type == ElementType.INPUT
        assert "用户名" in slot.keywords
    
    def test_extract_slot_sync(self, engine):
        """测试同步提取槽位"""
        slot = engine.extract_slot("点击提交按钮")
        
        assert slot.action == ActionType.CLICK
        assert slot.target_type == ElementType.BUTTON
        assert len(slot.keywords) > 0
    
    def test_synonym_expansion(self, engine):
        """测试同义词扩展"""
        slot = engine.extract_slot("点击提交按钮")
        
        keywords = slot.keywords
        # 应该包含同义词
        assert len(keywords) > 2
        # 应该包含 "提交" 的同义词
        assert any(k in ["确认", "保存", "submit"] for k in keywords)
    
    def test_synonym_expansion_disabled(self):
        """测试禁用同义词扩展"""
        engine = L1Engine(enable_synonym_expansion=False)
        slot = engine.extract_slot("点击提交按钮")
        
        # 关键词数量应该较少
        assert len(slot.keywords) <= 3
    
    def test_extract_batch(self, engine):
        """测试批量提取"""
        instructions = [
            "点击提交按钮",
            "输入用户名",
            "选择下拉框",
        ]
        
        slots = engine.extract_batch(instructions)
        
        assert len(slots) == 3
        assert slots[0].action == ActionType.CLICK
        assert slots[1].action == ActionType.INPUT
    
    def test_validate_slot_valid(self, engine):
        """测试验证有效槽位"""
        slot = engine.extract_slot("点击提交按钮")
        
        is_valid = engine.validate_slot(slot)
        assert is_valid is True
    
    def test_validate_slot_low_confidence(self, engine):
        """测试验证低置信度槽位"""
        from aerotest.core.funnel.types import ActionSlot, ActionType
        
        slot = ActionSlot(
            action=ActionType.UNKNOWN,
            keywords=["test"],
            confidence=0.1,  # 低置信度
        )
        
        is_valid = engine.validate_slot(slot)
        assert is_valid is False
    
    def test_validate_slot_no_keywords(self, engine):
        """测试验证无关键词槽位"""
        from aerotest.core.funnel.types import ActionSlot, ActionType
        
        slot = ActionSlot(
            action=ActionType.CLICK,
            keywords=[],  # 无关键词
            confidence=0.8,
        )
        
        is_valid = engine.validate_slot(slot)
        assert is_valid is False
    
    def test_complex_instruction(self, engine):
        """测试复杂指令"""
        slot = engine.extract_slot("在用户名输入框中输入 admin123")
        
        assert slot.action == ActionType.INPUT
        assert "用户名" in slot.keywords
        assert slot.value == "admin123"
    
    def test_english_instruction(self, engine):
        """测试英文指令"""
        slot = engine.extract_slot("click submit button")
        
        assert slot.action == ActionType.CLICK
        assert slot.target_type == ElementType.BUTTON
    
    def test_submit_button_attributes(self, engine):
        """测试提交按钮属性推断"""
        slot = engine.extract_slot("点击提交按钮")
        
        assert slot.attributes.get("type") == "submit"
    
    @pytest.mark.asyncio
    async def test_integration_flow(self, engine):
        """测试完整的集成流程"""
        # 创建上下文
        context = FunnelContext(instruction="点击提交按钮")
        
        # L1 处理
        context = await engine.process(context)
        
        # 验证结果
        assert context.action_slot is not None
        
        slot = context.action_slot
        assert slot.action == ActionType.CLICK
        assert slot.target == "提交按钮"
        assert slot.target_type == ElementType.BUTTON
        assert len(slot.keywords) > 0
        assert slot.confidence > 0.5
        
        # 验证同义词扩展
        assert "提交" in slot.keywords
        assert any(k in ["确认", "保存", "submit"] for k in slot.keywords)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

