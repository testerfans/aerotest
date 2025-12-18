"""OODA 引擎单元测试"""

import pytest

from aerotest.core.ooda import (
    ActionType,
    ExecutionContext,
    OODAEngine,
    TestStep,
)


class TestOODAEngine:
    """测试 OODA 引擎"""

    @pytest.fixture
    def engine(self):
        """创建 OODA 引擎实例"""
        return OODAEngine(use_l3=False, use_l4=False, use_l5=False)

    @pytest.fixture
    def context(self):
        """创建执行上下文"""
        return ExecutionContext(
            target_id="test_target",
            variables={"username": "admin"},
        )

    def test_init(self, engine):
        """测试初始化"""
        assert engine is not None
        assert engine.l1_engine is not None
        assert engine.l2_engine is not None

    def test_init_with_layers(self):
        """测试启用所有层"""
        engine = OODAEngine(use_l3=True, use_l4=False, use_l5=False)

        assert engine.l3_engine is not None
        assert engine.l4_engine is None
        assert engine.l5_engine is None

    @pytest.mark.asyncio
    async def test_execute_step_click(self, engine, context):
        """测试执行点击步骤"""
        step = TestStep(
            step_id="1",
            description="点击登录按钮",
            action_type=ActionType.CLICK,
        )

        result = await engine.execute_step(step, context)

        # 由于没有真实 DOM，预期会失败或跳过
        assert result is not None
        assert result.duration_ms >= 0

    @pytest.mark.asyncio
    async def test_execute_step_input(self, engine, context):
        """测试执行输入步骤"""
        step = TestStep(
            step_id="2",
            description="输入用户名",
            action_type=ActionType.INPUT,
        )

        result = await engine.execute_step(step, context)

        assert result is not None
        assert result.duration_ms >= 0

    @pytest.mark.asyncio
    async def test_execute_step_wait(self, engine, context):
        """测试执行等待步骤"""
        step = TestStep(
            step_id="3",
            description="等待1秒",
            action_type=ActionType.WAIT,
        )

        result = await engine.execute_step(step, context)

        assert result is not None
        assert result.duration_ms >= 0

    @pytest.mark.asyncio
    async def test_observe(self, engine, context):
        """测试 Observe 阶段"""
        observation = await engine._observe(context)

        assert observation is not None
        assert observation.visible_elements is not None
        assert observation.interactive_elements is not None

    @pytest.mark.asyncio
    async def test_orient_without_dom(self, engine, context):
        """测试 Orient 阶段（无 DOM）"""
        step = TestStep(
            step_id="1",
            description="点击登录按钮",
            action_type=ActionType.CLICK,
        )

        observation = await engine._observe(context)
        orientation = await engine._orient(step, observation, context)

        assert orientation is not None
        assert orientation.current_step == step

    @pytest.mark.asyncio
    async def test_decide(self, engine, context):
        """测试 Decide 阶段"""
        step = TestStep(
            step_id="1",
            description="点击登录按钮",
            action_type=ActionType.CLICK,
        )

        observation = await engine._observe(context)
        orientation = await engine._orient(step, observation, context)
        decision = await engine._decide(step, orientation, context)

        assert decision is not None
        assert decision.action_type == ActionType.CLICK

    @pytest.mark.asyncio
    async def test_act_click(self, engine, context):
        """测试 Act 阶段 - 点击"""
        from aerotest.core.ooda.types import Decision

        decision = Decision(action_type=ActionType.CLICK)
        decision.should_execute = False  # 跳过实际执行

        action = await engine._act(decision, context)

        assert action is not None
        assert action.status is not None

    @pytest.mark.asyncio
    async def test_execute_click(self, engine, context):
        """测试执行点击操作"""
        from aerotest.browser.dom.cdp_types import DOMRect, EnhancedDOMTreeNode, NodeType
        from aerotest.core.ooda.types import Decision

        # 创建模拟元素
        element = EnhancedDOMTreeNode(
            backend_node_id=123,
            node_type=NodeType.ELEMENT_NODE,
            node_name="BUTTON",
            tag_name="button",
            attributes={},
            bounding_box=DOMRect(x=100, y=100, width=80, height=30),
            is_visible=True,
            is_clickable=True,
            children=[],
        )

        decision = Decision(
            action_type=ActionType.CLICK,
            target_element=element,
        )

        result = await engine._execute_click(decision, context)

        assert result is not None
        assert result.get("clicked") is True

    @pytest.mark.asyncio
    async def test_execute_input(self, engine, context):
        """测试执行输入操作"""
        from aerotest.browser.dom.cdp_types import DOMRect, EnhancedDOMTreeNode, NodeType
        from aerotest.core.ooda.types import Decision

        # 创建模拟元素
        element = EnhancedDOMTreeNode(
            backend_node_id=456,
            node_type=NodeType.ELEMENT_NODE,
            node_name="INPUT",
            tag_name="input",
            attributes={},
            bounding_box=DOMRect(x=100, y=150, width=200, height=30),
            is_visible=True,
            is_clickable=True,
            children=[],
        )

        decision = Decision(
            action_type=ActionType.INPUT,
            target_element=element,
            parameters={"value": "test123"},
        )

        result = await engine._execute_input(decision, context)

        assert result is not None
        assert result.get("input") is True
        assert result.get("value") == "test123"

    @pytest.mark.asyncio
    async def test_execute_wait(self, engine, context):
        """测试执行等待操作"""
        from aerotest.core.ooda.types import Decision

        decision = Decision(
            action_type=ActionType.WAIT,
            parameters={"duration": 0.1},  # 0.1 秒
        )

        result = await engine._execute_wait(decision, context)

        assert result is not None
        assert result.get("waited") is True

    @pytest.mark.asyncio
    async def test_full_ooda_cycle(self, engine, context):
        """测试完整 OODA 循环"""
        step = TestStep(
            step_id="1",
            description="点击登录按钮",
            action_type=ActionType.CLICK,
        )

        result = await engine.execute_step(step, context)

        # 验证完整流程
        assert result is not None
        assert step.observation is not None
        assert step.orientation is not None
        assert step.decision is not None
        assert step.action is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

