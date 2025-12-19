"""真实登录测试

测试用例：登录到 https://192.168.11.99/
"""

import asyncio
import pytest
from loguru import logger

# 暂时跳过，因为需要真实浏览器环境
pytestmark = pytest.mark.skip(reason="需要真实浏览器环境和CDP连接")


class TestRealLogin:
    """真实登录测试"""

    @pytest.mark.asyncio
    async def test_login_workflow(self):
        """
        测试登录流程
        
        步骤：
        1. 打开 https://192.168.11.99/
        2. account 输入 admin
        3. password 输入 123456
        4. 点击 sign in
        5. 断言：跳转到 https://192.168.11.99/dashboards/index
        6. 断言：页面包含 dashboard 文本内容
        """
        from aerotest.browser.cdp.session import CDPSession
        from aerotest.core.ooda.ooda_engine import OODAEngine
        from aerotest.core.ooda.types import (
            ActionType,
            ExecutionContext,
            TestStep,
        )

        logger.info("=" * 60)
        logger.info("开始测试：登录流程")
        logger.info("=" * 60)

        # 创建 CDP Session（需要先启动 Chrome）
        # chrome --remote-debugging-port=9222
        cdp_session = CDPSession()
        
        try:
            # 连接到 Chrome
            await cdp_session.connect()
            logger.info("✅ CDP 连接成功")

            # 创建 OODA 引擎
            engine = OODAEngine(
                cdp_session=cdp_session,
                use_l3=True,
                use_l4=True,
                use_l5=True,
            )
            logger.info("✅ OODA 引擎创建成功")

            # 创建执行上下文
            context = ExecutionContext(
                target_id="login_test",
                variables={
                    "base_url": "https://192.168.11.99/",
                    "username": "admin",
                    "password": "123456",
                },
            )

            # 步骤 1: 导航到登录页面
            step1 = TestStep(
                step_id="1",
                description="打开 https://192.168.11.99/",
                action_type=ActionType.NAVIGATE,
            )
            
            logger.info("\n步骤 1: 打开登录页面")
            result1 = await engine.execute_step(step1, context)
            assert result1.success, f"步骤 1 失败: {result1.error}"
            logger.info(f"  ✅ 步骤 1 完成，耗时: {result1.duration_ms:.2f}ms")

            # 步骤 2: 输入用户名
            step2 = TestStep(
                step_id="2",
                description="account 输入 admin",
                action_type=ActionType.INPUT,
            )
            
            logger.info("\n步骤 2: 输入用户名")
            result2 = await engine.execute_step(step2, context)
            assert result2.success, f"步骤 2 失败: {result2.error}"
            logger.info(f"  ✅ 步骤 2 完成，耗时: {result2.duration_ms:.2f}ms")
            if step2.orientation:
                logger.info(f"  匹配策略: {step2.orientation.strategy}")
                logger.info(f"  置信度: {step2.orientation.confidence:.2f}")

            # 步骤 3: 输入密码
            step3 = TestStep(
                step_id="3",
                description="password 输入 123456",
                action_type=ActionType.INPUT,
            )
            
            logger.info("\n步骤 3: 输入密码")
            result3 = await engine.execute_step(step3, context)
            assert result3.success, f"步骤 3 失败: {result3.error}"
            logger.info(f"  ✅ 步骤 3 完成，耗时: {result3.duration_ms:.2f}ms")
            if step3.orientation:
                logger.info(f"  匹配策略: {step3.orientation.strategy}")
                logger.info(f"  置信度: {step3.orientation.confidence:.2f}")

            # 步骤 4: 点击登录按钮
            step4 = TestStep(
                step_id="4",
                description="点击 sign in 按钮",
                action_type=ActionType.CLICK,
            )
            
            logger.info("\n步骤 4: 点击登录按钮")
            result4 = await engine.execute_step(step4, context)
            assert result4.success, f"步骤 4 失败: {result4.error}"
            logger.info(f"  ✅ 步骤 4 完成，耗时: {result4.duration_ms:.2f}ms")
            if step4.orientation:
                logger.info(f"  匹配策略: {step4.orientation.strategy}")
                logger.info(f"  置信度: {step4.orientation.confidence:.2f}")

            # 等待跳转
            await asyncio.sleep(2)

            # 断言 1: 检查 URL
            current_url = await cdp_session.get_page_url()
            logger.info(f"\n当前 URL: {current_url}")
            assert "dashboards/index" in current_url, f"URL 断言失败，期望包含 'dashboards/index'，实际: {current_url}"
            logger.info("  ✅ URL 断言通过")

            # 断言 2: 检查页面内容
            step5 = TestStep(
                step_id="5",
                description="验证页面包含 dashboard 文本",
                action_type=ActionType.ASSERT,
                expected_value="dashboard",
            )
            
            logger.info("\n步骤 5: 验证页面内容")
            result5 = await engine.execute_step(step5, context)
            assert result5.success, f"步骤 5 失败: {result5.error}"
            logger.info(f"  ✅ 步骤 5 完成，耗时: {result5.duration_ms:.2f}ms")

            # 打印总结
            logger.info("\n" + "=" * 60)
            logger.info("✅ 登录测试全部通过")
            logger.info("=" * 60)

            total_time = (
                result1.duration_ms +
                result2.duration_ms +
                result3.duration_ms +
                result4.duration_ms +
                result5.duration_ms
            )
            logger.info(f"总耗时: {total_time:.2f}ms")

        finally:
            # 清理资源
            if cdp_session:
                await cdp_session.disconnect()
                logger.info("✅ CDP 连接已断开")


async def run_test_manually():
    """手动运行测试（不使用 pytest）"""
    test = TestRealLogin()
    await test.test_login_workflow()


if __name__ == "__main__":
    # 直接运行测试
    asyncio.run(run_test_manually())
