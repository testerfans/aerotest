"""OODA 引擎使用示例

演示如何使用 OODA 引擎和用例执行器
"""

import asyncio

from aerotest.core.ooda import (
    ActionType,
    CaseExecutor,
    ExecutionContext,
    OODAEngine,
    TestCase,
    TestStep,
)
from aerotest.utils.logger import get_logger

logger = get_logger("examples.ooda")


async def example_single_step():
    """示例 1: 执行单个步骤"""
    logger.info("=" * 60)
    logger.info("示例 1: 执行单个步骤")
    logger.info("=" * 60)

    # 创建 OODA 引擎
    engine = OODAEngine(
        use_l3=True,  # 启用 L3 空间布局
        use_l4=False,  # 不启用 L4 AI 推理
        use_l5=False,  # 不启用 L5 视觉识别
    )

    # 创建执行上下文
    context = ExecutionContext(
        target_id="mock_target",
        variables={"username": "admin"},
    )

    # 创建测试步骤
    step = TestStep(
        step_id="1",
        description="点击登录按钮",
        action_type=ActionType.CLICK,
    )

    # 执行步骤
    result = await engine.execute_step(step, context)

    # 打印结果
    logger.info(f"执行结果: {result.success}")
    logger.info(f"状态: {result.status}")
    logger.info(f"耗时: {result.duration_ms:.2f}ms")

    if step.orientation:
        logger.info(f"匹配策略: {step.orientation.strategy}")
        logger.info(f"置信度: {step.orientation.confidence:.2f}")


async def example_test_case():
    """示例 2: 执行完整测试用例"""
    logger.info("\n" + "=" * 60)
    logger.info("示例 2: 执行完整测试用例")
    logger.info("=" * 60)

    # 创建用例执行器
    executor = CaseExecutor(
        use_l3=True,
        use_l4=False,
        use_l5=False,
        max_retries=2,  # 最多重试 2 次
    )

    # 创建测试用例
    case = TestCase(
        case_id="TC001",
        name="用户登录测试",
        description="测试用户登录功能的完整流程",
        steps=[
            TestStep(
                step_id="1",
                description="导航到登录页面",
                action_type=ActionType.NAVIGATE,
            ),
            TestStep(
                step_id="2",
                description="输入用户名 admin",
                action_type=ActionType.INPUT,
            ),
            TestStep(
                step_id="3",
                description="输入密码 123456",
                action_type=ActionType.INPUT,
            ),
            TestStep(
                step_id="4",
                description="点击登录按钮",
                action_type=ActionType.CLICK,
            ),
            TestStep(
                step_id="5",
                description="等待 2 秒",
                action_type=ActionType.WAIT,
            ),
        ],
    )

    # 创建执行上下文
    context = ExecutionContext(
        target_id="mock_target",
        variables={
            "base_url": "https://example.com",
            "username": "admin",
            "password": "123456",
        },
        config={
            "stop_on_failure": True,  # 失败时停止
        },
    )

    # 执行用例
    result = await executor.execute_case(case, context)

    # 打印结果
    logger.info(f"用例执行结果: {result.success}")
    logger.info(f"状态: {result.status}")
    logger.info(f"总耗时: {result.duration_ms:.2f}ms")
    logger.info(f"统计: {result.stats}")

    # 打印每个步骤的结果
    for i, step_result in enumerate(result.step_results, 1):
        logger.info(
            f"  步骤 {i}: {step_result.status} "
            f"({step_result.duration_ms:.2f}ms)"
        )


async def example_batch_execution():
    """示例 3: 批量执行用例"""
    logger.info("\n" + "=" * 60)
    logger.info("示例 3: 批量执行用例")
    logger.info("=" * 60)

    # 创建执行器
    executor = CaseExecutor(use_l3=True, use_l4=False, use_l5=False)

    # 创建多个用例
    cases = [
        TestCase(
            case_id="TC001",
            name="登录测试",
            steps=[
                TestStep(
                    step_id="1",
                    description="输入用户名",
                    action_type=ActionType.INPUT,
                ),
                TestStep(
                    step_id="2",
                    description="点击登录",
                    action_type=ActionType.CLICK,
                ),
            ],
        ),
        TestCase(
            case_id="TC002",
            name="搜索测试",
            steps=[
                TestStep(
                    step_id="1",
                    description="输入搜索关键词",
                    action_type=ActionType.INPUT,
                ),
                TestStep(
                    step_id="2",
                    description="点击搜索按钮",
                    action_type=ActionType.CLICK,
                ),
            ],
        ),
        TestCase(
            case_id="TC003",
            name="注销测试",
            steps=[
                TestStep(
                    step_id="1",
                    description="点击用户菜单",
                    action_type=ActionType.CLICK,
                ),
                TestStep(
                    step_id="2",
                    description="点击注销",
                    action_type=ActionType.CLICK,
                ),
            ],
        ),
    ]

    # 创建上下文
    context = ExecutionContext(target_id="mock_target")

    # 批量执行
    results = await executor.batch_execute(cases, context)

    # 打印结果
    logger.info(f"批量执行完成，共 {len(results)} 个用例")

    success_count = sum(1 for r in results if r.success)
    logger.info(f"成功: {success_count}/{len(results)}")

    for i, result in enumerate(results, 1):
        logger.info(
            f"  用例 {i}: {result.status} "
            f"({result.duration_ms:.2f}ms, "
            f"{result.stats['success']}/{result.stats['total']} 步骤成功)"
        )


async def example_ooda_details():
    """示例 4: 查看 OODA 循环详细信息"""
    logger.info("\n" + "=" * 60)
    logger.info("示例 4: OODA 循环详细信息")
    logger.info("=" * 60)

    engine = OODAEngine(use_l3=True, use_l4=False, use_l5=False)
    context = ExecutionContext(target_id="mock_target")

    step = TestStep(
        step_id="1",
        description="点击用户名输入框右边的清除按钮",
        action_type=ActionType.CLICK,
    )

    result = await engine.execute_step(step, context)

    # 打印 OODA 各阶段详情
    logger.info("\n📊 OODA 循环详情:")

    if step.observation:
        logger.info(
            f"\n1️⃣ Observe (观察):"
            f"\n  - 可见元素: {len(step.observation.visible_elements)}"
            f"\n  - 可交互元素: {len(step.observation.interactive_elements)}"
        )

    if step.orientation:
        logger.info(
            f"\n2️⃣ Orient (定向):"
            f"\n  - 策略: {step.orientation.strategy}"
            f"\n  - 置信度: {step.orientation.confidence:.2f}"
            f"\n  - 候选元素: {len(step.orientation.candidate_elements)}"
        )

        if step.orientation.action_slot:
            logger.info(
                f"  - L1 槽位: {step.orientation.action_slot.action_type}"
            )

    if step.decision:
        logger.info(
            f"\n3️⃣ Decide (决策):"
            f"\n  - 操作类型: {step.decision.action_type}"
            f"\n  - 是否执行: {step.decision.should_execute}"
            f"\n  - 原因: {step.decision.reason}"
        )

    if step.action:
        logger.info(
            f"\n4️⃣ Act (行动):"
            f"\n  - 状态: {step.action.status}"
            f"\n  - 耗时: {step.action.duration_ms:.2f}ms"
            f"\n  - 重试次数: {step.action.retry_count}"
        )

        if step.action.error:
            logger.info(f"  - 错误: {step.action.error}")


async def main():
    """主函数"""
    logger.info("🚀 OODA 引擎使用示例")
    logger.info("=" * 60)

    # 运行所有示例
    await example_single_step()
    await example_test_case()
    await example_batch_execution()
    await example_ooda_details()

    logger.info("\n" + "=" * 60)
    logger.info("✅ 所有示例执行完成")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

