"""五层漏斗集成测试

完整测试五层漏斗的端到端功能
"""

import asyncio
from typing import Optional

import pytest

from aerotest.browser.cdp.session import CDPSession
from aerotest.browser.dom.cdp_types import DOMRect, EnhancedDOMTreeNode, NodeType
from aerotest.browser.dom.views import SerializedDOMState
from aerotest.core.funnel.l1.l1_engine import L1Engine
from aerotest.core.funnel.l2.l2_engine import L2Engine
from aerotest.core.funnel.l3.l3_engine import L3Engine
from aerotest.core.funnel.l4.l4_engine import L4Engine
from aerotest.core.funnel.l5.l5_engine import L5Engine
from aerotest.core.funnel.types import ActionSlot, FunnelContext, MatchResult


class TestFiveLayerFunnelIntegration:
    """测试五层漏斗完整流程"""
    
    @pytest.fixture
    def sample_dom_state(self):
        """创建示例 DOM 状态（模拟真实页面）"""
        nodes = [
            # 用户名标签
            EnhancedDOMTreeNode(
                backend_node_id=1,
                node_type=NodeType.ELEMENT_NODE,
                node_name="LABEL",
                tag_name="label",
                attributes={"innerText": "用户名", "for": "username"},
                bounding_box=DOMRect(x=100, y=100, width=80, height=30),
                is_visible=True,
                is_clickable=False,
            ),
            # 用户名输入框
            EnhancedDOMTreeNode(
                backend_node_id=2,
                node_type=NodeType.ELEMENT_NODE,
                node_name="INPUT",
                tag_name="input",
                attributes={
                    "id": "username",
                    "placeholder": "请输入用户名",
                    "type": "text",
                },
                bounding_box=DOMRect(x=190, y=100, width=200, height=30),
                is_visible=True,
                is_clickable=True,
            ),
            # 清除按钮（无明确文本）
            EnhancedDOMTreeNode(
                backend_node_id=3,
                node_type=NodeType.ELEMENT_NODE,
                node_name="BUTTON",
                tag_name="button",
                attributes={
                    "class": "clear-btn",
                    "aria-label": "清除",
                },
                bounding_box=DOMRect(x=400, y=100, width=40, height=30),
                is_visible=True,
                is_clickable=True,
            ),
            # 密码标签
            EnhancedDOMTreeNode(
                backend_node_id=4,
                node_type=NodeType.ELEMENT_NODE,
                node_name="LABEL",
                tag_name="label",
                attributes={"innerText": "密码", "for": "password"},
                bounding_box=DOMRect(x=100, y=150, width=80, height=30),
                is_visible=True,
                is_clickable=False,
            ),
            # 密码输入框
            EnhancedDOMTreeNode(
                backend_node_id=5,
                node_type=NodeType.ELEMENT_NODE,
                node_name="INPUT",
                tag_name="input",
                attributes={
                    "id": "password",
                    "placeholder": "请输入密码",
                    "type": "password",
                },
                bounding_box=DOMRect(x=190, y=150, width=200, height=30),
                is_visible=True,
                is_clickable=True,
            ),
            # 商品卡片 1 (¥99)
            EnhancedDOMTreeNode(
                backend_node_id=6,
                node_type=NodeType.ELEMENT_NODE,
                node_name="DIV",
                tag_name="div",
                attributes={
                    "class": "product-card",
                    "innerText": "商品 A\n¥99",
                },
                bounding_box=DOMRect(x=100, y=200, width=150, height=100),
                is_visible=True,
                is_clickable=True,
            ),
            # 商品卡片 2 (¥79) - 最便宜
            EnhancedDOMTreeNode(
                backend_node_id=7,
                node_type=NodeType.ELEMENT_NODE,
                node_name="DIV",
                tag_name="div",
                attributes={
                    "class": "product-card",
                    "innerText": "商品 B\n¥79",
                },
                bounding_box=DOMRect(x=270, y=200, width=150, height=100),
                is_visible=True,
                is_clickable=True,
            ),
            # 商品卡片 3 (¥129)
            EnhancedDOMTreeNode(
                backend_node_id=8,
                node_type=NodeType.ELEMENT_NODE,
                node_name="DIV",
                tag_name="div",
                attributes={
                    "class": "product-card",
                    "innerText": "商品 C\n¥129",
                },
                bounding_box=DOMRect(x=440, y=200, width=150, height=100),
                is_visible=True,
                is_clickable=True,
            ),
        ]
        
        return SerializedDOMState(
            simplified_nodes=nodes,
            selector_map={},
        )
    
    # ====================================================================
    # 测试用例 1: L1-L2 简单场景（属性匹配）
    # ====================================================================
    
    @pytest.mark.asyncio
    async def test_case_1_l1_l2_simple_attribute_match(self, sample_dom_state):
        """
        测试用例 1: 简单属性匹配场景
        
        场景：用户输入用户名
        期望：L1 提取意图，L2 通过 placeholder 属性匹配
        预期层级：L1-L2
        预期时间：< 50ms
        """
        print("\n" + "="*70)
        print("测试用例 1: 简单属性匹配（L1-L2）")
        print("="*70)
        
        # 初始化引擎
        l1_engine = L1Engine()
        l2_engine = L2Engine()
        
        # 用户指令
        instruction = "在用户名输入框输入 admin"
        print(f"📝 指令: {instruction}")
        
        # Step 1: L1 提取槽位
        print("\n🔍 Step 1: L1 槽位提取")
        slot = await l1_engine.extract_slot(instruction)
        
        # 断言：L1 成功提取
        assert slot is not None, "L1 应该成功提取槽位"
        assert slot.action_type.value == "INPUT", f"动作类型应为 INPUT，实际: {slot.action_type.value}"
        assert "用户名" in (slot.target_text or ""), "目标应包含'用户名'"
        assert slot.value == "admin", f"值应为 'admin'，实际: {slot.value}"
        print(f"✅ L1 提取成功: {slot}")
        
        # Step 2: L2 属性匹配
        print("\n🔍 Step 2: L2 属性匹配")
        l2_results = await l2_engine.match_elements(sample_dom_state, slot)
        
        # 断言：L2 找到匹配
        assert len(l2_results) > 0, "L2 应该找到匹配的元素"
        best_match = l2_results[0]
        assert best_match.score > 0.7, f"L2 得分应 > 0.7，实际: {best_match.score}"
        assert best_match.element.backend_node_id == 2, "应匹配到用户名输入框"
        print(f"✅ L2 匹配成功: 得分={best_match.score:.2f}, 元素ID={best_match.element.backend_node_id}")
        
        # 总结
        print("\n" + "="*70)
        print("✅ 测试用例 1 通过: L1-L2 简单场景正常工作")
        print("="*70)
    
    # ====================================================================
    # 测试用例 2: L1-L2-L3 空间关系场景
    # ====================================================================
    
    @pytest.mark.asyncio
    async def test_case_2_l1_l2_l3_spatial_layout(self, sample_dom_state):
        """
        测试用例 2: 空间关系场景
        
        场景：点击用户名输入框右边的清除按钮
        期望：L1 提取意图，L2 失败（按钮无明确文本），L3 通过空间布局找到
        预期层级：L1-L2-L3
        预期时间：< 120ms
        """
        print("\n" + "="*70)
        print("测试用例 2: 空间布局推理（L1-L2-L3）")
        print("="*70)
        
        # 初始化引擎
        l1_engine = L1Engine()
        l2_engine = L2Engine()
        l3_engine = L3Engine()
        
        # 用户指令
        instruction = "点击用户名输入框右边的清除按钮"
        print(f"📝 指令: {instruction}")
        
        # Step 1: L1 提取槽位
        print("\n🔍 Step 1: L1 槽位提取")
        slot = await l1_engine.extract_slot(instruction)
        
        assert slot is not None, "L1 应该成功提取槽位"
        assert slot.action_type.value == "CLICK", f"动作类型应为 CLICK"
        print(f"✅ L1 提取成功: {slot}")
        
        # Step 2: L2 尝试匹配（应该失败或得分低）
        print("\n🔍 Step 2: L2 属性匹配（预期失败或低分）")
        l2_results = await l2_engine.match_elements(sample_dom_state, slot)
        
        if len(l2_results) == 0 or l2_results[0].score < 0.8:
            print(f"⚠️ L2 失败或低分（预期行为），进入 L3")
        
        # Step 3: L3 空间布局推理
        print("\n🔍 Step 3: L3 空间布局推理")
        context = FunnelContext(
            instruction=instruction,
            action_slot=slot,
            l2_candidates=l2_results,
        )
        
        context = await l3_engine.process(context, sample_dom_state)
        
        # 断言：L3 找到目标
        assert context.l3_candidates is not None, "L3 应该返回候选"
        assert len(context.l3_candidates) > 0, "L3 应该找到匹配"
        best_match = context.l3_candidates[0]
        assert best_match.element.backend_node_id == 3, "应找到清除按钮"
        print(f"✅ L3 成功: 得分={best_match.score:.2f}, 元素ID={best_match.element.backend_node_id}")
        
        # 总结
        print("\n" + "="*70)
        print("✅ 测试用例 2 通过: L1-L2-L3 空间布局推理正常工作")
        print("="*70)
    
    # ====================================================================
    # 测试用例 3: L1-L2-L4 AI 推理场景（需要 Mock）
    # ====================================================================
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="需要 Qwen API 或 Mock")
    async def test_case_3_l1_l2_l4_ai_reasoning(self, sample_dom_state, mocker):
        """
        测试用例 3: AI 推理场景
        
        场景：选择最便宜的商品
        期望：L1 提取意图，L2 找到 3 个商品，L4 通过 AI 推理选择最便宜的
        预期层级：L1-L2-L4
        预期时间：< 2s（含 AI 调用）
        """
        print("\n" + "="*70)
        print("测试用例 3: AI 推理（L1-L2-L4）")
        print("="*70)
        
        # 初始化引擎
        l1_engine = L1Engine()
        l2_engine = L2Engine()
        l4_engine = L4Engine()
        
        # Mock Qwen API 响应
        mock_response = {"selected_index": 1, "reason": "商品 B 价格最低（¥79）"}
        mocker.patch.object(
            l4_engine.qwen_client,
            "chat_with_json",
            return_value=mock_response
        )
        
        # 用户指令
        instruction = "选择最便宜的商品"
        print(f"📝 指令: {instruction}")
        
        # Step 1: L1 提取槽位
        print("\n🔍 Step 1: L1 槽位提取")
        slot = await l1_engine.extract_slot(instruction)
        
        assert slot is not None
        assert slot.action_type.value == "CLICK"
        print(f"✅ L1 提取成功")
        
        # Step 2: L2 找到商品
        print("\n🔍 Step 2: L2 找到所有商品")
        l2_results = await l2_engine.match_elements(sample_dom_state, slot)
        
        assert len(l2_results) >= 3, "应找到至少 3 个商品"
        print(f"✅ L2 找到 {len(l2_results)} 个商品")
        
        # Step 3: L4 AI 推理
        print("\n🔍 Step 3: L4 AI 推理选择最便宜")
        context = FunnelContext(
            instruction=instruction,
            action_slot=slot,
            l2_candidates=l2_results,
        )
        
        context = await l4_engine.process(context, sample_dom_state)
        
        # 断言：L4 选择了正确的商品
        assert context.l4_candidates is not None
        assert len(context.l4_candidates) > 0
        best_match = context.l4_candidates[0]
        assert best_match.element.backend_node_id == 7, "应选择商品 B（¥79）"
        print(f"✅ L4 成功: 选择了最便宜的商品")
        
        # 总结
        print("\n" + "="*70)
        print("✅ 测试用例 3 通过: L1-L2-L4 AI 推理正常工作")
        print("="*70)
    
    # ====================================================================
    # 测试用例 4: 完整流程（L1-L2-L3-L4-L5）
    # ====================================================================
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="需要真实浏览器环境")
    async def test_case_4_full_pipeline(self):
        """
        测试用例 4: 完整五层漏斗流程
        
        场景：完整的用户登录流程
        步骤：
          1. 打开登录页
          2. 输入用户名（L1-L2）
          3. 输入密码（L1-L2）
          4. 点击登录按钮（L1-L2）
          5. 验证登录成功
        
        预期：所有步骤成功执行
        预期时间：< 10s
        """
        print("\n" + "="*70)
        print("测试用例 4: 完整用例流程")
        print("="*70)
        
        # TODO: 需要实现 OODA Engine 和真实浏览器环境
        # 这是一个端到端测试
        pass
    
    # ====================================================================
    # 测试用例 5: 性能基准测试
    # ====================================================================
    
    @pytest.mark.asyncio
    async def test_case_5_performance_benchmark(self, sample_dom_state):
        """
        测试用例 5: 性能基准测试
        
        验证各层性能符合要求：
        - L1: < 50ms
        - L2: < 200ms
        - L3: < 500ms
        """
        print("\n" + "="*70)
        print("测试用例 5: 性能基准测试")
        print("="*70)
        
        import time
        
        # 测试 L1 性能
        l1_engine = L1Engine()
        start = time.time()
        for _ in range(100):
            await l1_engine.extract_slot("点击提交按钮")
        l1_time = (time.time() - start) / 100 * 1000
        
        print(f"L1 平均耗时: {l1_time:.2f}ms")
        assert l1_time < 50, f"L1 应 < 50ms，实际: {l1_time:.2f}ms"
        
        # 测试 L2 性能
        l2_engine = L2Engine()
        slot = await l1_engine.extract_slot("在用户名输入框输入 admin")
        start = time.time()
        for _ in range(10):
            await l2_engine.match_elements(sample_dom_state, slot)
        l2_time = (time.time() - start) / 10 * 1000
        
        print(f"L2 平均耗时: {l2_time:.2f}ms")
        assert l2_time < 200, f"L2 应 < 200ms，实际: {l2_time:.2f}ms"
        
        # 总结
        print("\n" + "="*70)
        print("✅ 测试用例 5 通过: 性能符合要求")
        print(f"   L1: {l1_time:.2f}ms (目标 < 50ms)")
        print(f"   L2: {l2_time:.2f}ms (目标 < 200ms)")
        print("="*70)


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"])

