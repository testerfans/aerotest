"""模拟登录测试

使用 mock 数据测试五层漏斗机制
"""

import pytest
from loguru import logger

from aerotest.core.funnel.l1.l1_engine import L1Engine
from aerotest.core.funnel.l2.l2_engine import L2Engine
from aerotest.core.funnel.types import FunnelContext
from aerotest.browser.dom.views import EnhancedDOMTreeNode, NodeType


class TestLoginMock:
    """模拟登录测试"""

    @pytest.mark.asyncio
    async def test_l1_extract_login_steps(self):
        """测试 L1 层提取登录步骤"""
        logger.info("=" * 60)
        logger.info("测试 L1 层：提取登录步骤")
        logger.info("=" * 60)

        engine = L1Engine()

        # 测试步骤 1: 输入用户名
        step1 = "account 输入 admin"
        context1 = FunnelContext(instruction=step1)
        context1 = await engine.process(context1, None)

        assert context1.action_slot is not None, "L1 应该提取出槽位"
        assert context1.action_slot.action_type.value == "input", "动作类型应该是 input"
        assert context1.action_slot.target == "account", "目标应该是 account"
        assert context1.action_slot.value == "admin", "值应该是 admin"
        
        logger.info(f"✅ 步骤 1 提取成功:")
        logger.info(f"  动作: {context1.action_slot.action_type.value}")
        logger.info(f"  目标: {context1.action_slot.target}")
        logger.info(f"  值: {context1.action_slot.value}")

        # 测试步骤 2: 输入密码
        step2 = "password 输入 123456"
        context2 = FunnelContext(instruction=step2)
        context2 = await engine.process(context2, None)

        assert context2.action_slot is not None, "L1 应该提取出槽位"
        assert context2.action_slot.action_type.value == "input", "动作类型应该是 input"
        assert context2.action_slot.target == "password", "目标应该是 password"
        assert context2.action_slot.value == "123456", "值应该是 123456"
        
        logger.info(f"\n✅ 步骤 2 提取成功:")
        logger.info(f"  动作: {context2.action_slot.action_type.value}")
        logger.info(f"  目标: {context2.action_slot.target}")
        logger.info(f"  值: {context2.action_slot.value}")

        # 测试步骤 3: 点击按钮
        step3 = "点击 sign in"
        context3 = FunnelContext(instruction=step3)
        context3 = await engine.process(context3, None)

        assert context3.action_slot is not None, "L1 应该提取出槽位"
        assert context3.action_slot.action_type.value == "click", "动作类型应该是 click"
        assert "sign in" in context3.action_slot.target.lower(), "目标应该包含 sign in"
        
        logger.info(f"\n✅ 步骤 3 提取成功:")
        logger.info(f"  动作: {context3.action_slot.action_type.value}")
        logger.info(f"  目标: {context3.action_slot.target}")

        logger.info("\n" + "=" * 60)
        logger.info("✅ L1 层测试全部通过")
        logger.info("=" * 60)

    @pytest.mark.asyncio
    async def test_l2_match_account_input(self):
        """测试 L2 层匹配 account 输入框"""
        logger.info("\n" + "=" * 60)
        logger.info("测试 L2 层：匹配 account 输入框")
        logger.info("=" * 60)

        # 创建模拟 DOM 树
        mock_dom = self._create_mock_login_page()

        # 创建引擎
        l1_engine = L1Engine()
        l2_engine = L2Engine()

        # L1 提取槽位
        instruction = "account 输入 admin"
        context = FunnelContext(instruction=instruction)
        context = await l1_engine.process(context, None)

        assert context.action_slot is not None, "L1 应该提取出槽位"

        # L2 匹配元素
        context = await l2_engine.process(context, mock_dom)

        assert len(context.l2_candidates) > 0, "L2 应该找到候选元素"
        best_match = context.l2_candidates[0]
        
        logger.info(f"✅ 找到 {len(context.l2_candidates)} 个候选元素")
        logger.info(f"  最佳匹配:")
        logger.info(f"    元素: {best_match.element.tag_name}")
        logger.info(f"    得分: {best_match.score:.2f}")
        logger.info(f"    层级: {best_match.layer}")
        
        if best_match.element.attributes:
            logger.info(f"    属性: {best_match.element.attributes}")

        # 验证匹配结果
        assert best_match.score > 0.7, "最佳匹配得分应该 > 0.7"
        assert best_match.element.tag_name == "input", "应该是 input 元素"

        logger.info("\n" + "=" * 60)
        logger.info("✅ L2 层测试通过")
        logger.info("=" * 60)

    @pytest.mark.asyncio
    async def test_l2_match_password_input(self):
        """测试 L2 层匹配 password 输入框"""
        logger.info("\n" + "=" * 60)
        logger.info("测试 L2 层：匹配 password 输入框")
        logger.info("=" * 60)

        # 创建模拟 DOM 树
        mock_dom = self._create_mock_login_page()

        # 创建引擎
        l1_engine = L1Engine()
        l2_engine = L2Engine()

        # L1 提取槽位
        instruction = "password 输入 123456"
        context = FunnelContext(instruction=instruction)
        context = await l1_engine.process(context, None)

        assert context.action_slot is not None, "L1 应该提取出槽位"

        # L2 匹配元素
        context = await l2_engine.process(context, mock_dom)

        assert len(context.l2_candidates) > 0, "L2 应该找到候选元素"
        best_match = context.l2_candidates[0]
        
        logger.info(f"✅ 找到 {len(context.l2_candidates)} 个候选元素")
        logger.info(f"  最佳匹配:")
        logger.info(f"    元素: {best_match.element.tag_name}")
        logger.info(f"    得分: {best_match.score:.2f}")
        logger.info(f"    层级: {best_match.layer}")
        
        if best_match.element.attributes:
            logger.info(f"    属性: {best_match.element.attributes}")

        # 验证匹配结果
        assert best_match.score > 0.7, "最佳匹配得分应该 > 0.7"
        assert best_match.element.tag_name == "input", "应该是 input 元素"
        assert best_match.element.attributes.get("type") == "password", "应该是密码输入框"

        logger.info("\n" + "=" * 60)
        logger.info("✅ L2 层测试通过")
        logger.info("=" * 60)

    @pytest.mark.asyncio
    async def test_l2_match_signin_button(self):
        """测试 L2 层匹配 sign in 按钮"""
        logger.info("\n" + "=" * 60)
        logger.info("测试 L2 层：匹配 sign in 按钮")
        logger.info("=" * 60)

        # 创建模拟 DOM 树
        mock_dom = self._create_mock_login_page()

        # 创建引擎
        l1_engine = L1Engine()
        l2_engine = L2Engine()

        # L1 提取槽位
        instruction = "点击 sign in"
        context = FunnelContext(instruction=instruction)
        context = await l1_engine.process(context, None)

        assert context.action_slot is not None, "L1 应该提取出槽位"

        # L2 匹配元素
        context = await l2_engine.process(context, mock_dom)

        assert len(context.l2_candidates) > 0, "L2 应该找到候选元素"
        best_match = context.l2_candidates[0]
        
        logger.info(f"✅ 找到 {len(context.l2_candidates)} 个候选元素")
        logger.info(f"  最佳匹配:")
        logger.info(f"    元素: {best_match.element.tag_name}")
        logger.info(f"    得分: {best_match.score:.2f}")
        logger.info(f"    层级: {best_match.layer}")
        
        if best_match.element.attributes:
            logger.info(f"    属性: {best_match.element.attributes}")

        # 验证匹配结果
        assert best_match.score > 0.7, "最佳匹配得分应该 > 0.7"
        assert best_match.element.tag_name == "button", "应该是 button 元素"

        logger.info("\n" + "=" * 60)
        logger.info("✅ L2 层测试通过")
        logger.info("=" * 60)

    def _create_mock_login_page(self) -> EnhancedDOMTreeNode:
        """创建模拟登录页面 DOM 树"""
        
        # 创建根节点
        root = EnhancedDOMTreeNode(
            backend_node_id=1,
            node_id=1,
            node_type=NodeType.ELEMENT_NODE,
            tag_name="html",
        )

        # 创建 body
        body = EnhancedDOMTreeNode(
            backend_node_id=2,
            node_id=2,
            node_type=NodeType.ELEMENT_NODE,
            tag_name="body",
            parent=root,
        )
        root.children.append(body)

        # 创建登录表单容器
        form = EnhancedDOMTreeNode(
            backend_node_id=3,
            node_id=3,
            node_type=NodeType.ELEMENT_NODE,
            tag_name="form",
            parent=body,
            attributes={"id": "loginForm", "class": "login-form"},
        )
        body.children.append(form)

        # 创建 account 输入框
        account_input = EnhancedDOMTreeNode(
            backend_node_id=4,
            node_id=4,
            node_type=NodeType.ELEMENT_NODE,
            tag_name="input",
            parent=form,
            attributes={
                "type": "text",
                "id": "account",
                "name": "account",
                "placeholder": "请输入账号",
                "class": "form-control",
            },
        )
        form.children.append(account_input)

        # 创建 password 输入框
        password_input = EnhancedDOMTreeNode(
            backend_node_id=5,
            node_id=5,
            node_type=NodeType.ELEMENT_NODE,
            tag_name="input",
            parent=form,
            attributes={
                "type": "password",
                "id": "password",
                "name": "password",
                "placeholder": "请输入密码",
                "class": "form-control",
            },
        )
        form.children.append(password_input)

        # 创建 sign in 按钮
        signin_button = EnhancedDOMTreeNode(
            backend_node_id=6,
            node_id=6,
            node_type=NodeType.ELEMENT_NODE,
            tag_name="button",
            parent=form,
            attributes={
                "type": "submit",
                "id": "signinButton",
                "class": "btn btn-primary",
            },
        )
        
        # 按钮文本
        button_text = EnhancedDOMTreeNode(
            backend_node_id=7,
            node_id=7,
            node_type=NodeType.TEXT_NODE,
            parent=signin_button,
            text_content="Sign In",
        )
        signin_button.children.append(button_text)
        form.children.append(signin_button)

        return root


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"])
