"""用例执行器单元测试"""

import pytest

from aerotest.core.ooda import (
    ActionType,
    CaseExecutor,
    ExecutionContext,
    TestCase,
    TestStep,
)


class TestCaseExecutor:
    """测试用例执行器"""

    @pytest.fixture
    def executor(self):
        """创建执行器实例"""
        return CaseExecutor(
            use_l3=False,
            use_l4=False,
            use_l5=False,
            max_retries=1,
        )

    @pytest.fixture
    def context(self):
        """创建执行上下文"""
        return ExecutionContext(
            target_id="test_target",
            variables={"username": "admin", "password": "123456"},
        )

    @pytest.fixture
    def test_case(self):
        """创建测试用例"""
        return TestCase(
            case_id="TC001",
            name="登录测试",
            description="测试用户登录功能",
            steps=[
                TestStep(
                    step_id="1",
                    description="输入用户名",
                    action_type=ActionType.INPUT,
                ),
                TestStep(
                    step_id="2",
                    description="输入密码",
                    action_type=ActionType.INPUT,
                ),
                TestStep(
                    step_id="3",
                    description="点击登录按钮",
                    action_type=ActionType.CLICK,
                ),
            ],
        )

    def test_init(self, executor):
        """测试初始化"""
        assert executor is not None
        assert executor.ooda_engine is not None
        assert executor.max_retries == 1

    @pytest.mark.asyncio
    async def test_execute_case(self, executor, test_case, context):
        """测试执行用例"""
        result = await executor.execute_case(test_case, context)

        assert result is not None
        assert result.stats["total"] == 3
        assert len(result.step_results) <= 3  # 可能因失败而中断

    @pytest.mark.asyncio
    async def test_execute_case_with_empty_steps(self, executor, context):
        """测试空步骤用例"""
        case = TestCase(
            case_id="TC002",
            name="空用例",
            steps=[],
        )

        result = await executor.execute_case(case, context)

        assert result is not None
        assert result.stats["total"] == 0

    @pytest.mark.asyncio
    async def test_execute_step_with_retry(self, executor, context):
        """测试步骤重试"""
        step = TestStep(
            step_id="1",
            description="点击不存在的元素",
            action_type=ActionType.CLICK,
        )

        result = await executor._execute_step_with_retry(step, context)

        assert result is not None
        # 由于元素不存在，可能会重试

    @pytest.mark.asyncio
    async def test_batch_execute(self, executor, context):
        """测试批量执行"""
        cases = [
            TestCase(
                case_id=f"TC{i:03d}",
                name=f"测试用例 {i}",
                steps=[
                    TestStep(
                        step_id="1",
                        description=f"步骤 {i}",
                        action_type=ActionType.WAIT,
                    )
                ],
            )
            for i in range(3)
        ]

        results = await executor.batch_execute(cases, context)

        assert len(results) == 3
        assert all(r is not None for r in results)

    @pytest.mark.asyncio
    async def test_execute_case_stop_on_failure(self, executor, context):
        """测试失败时停止"""
        case = TestCase(
            case_id="TC003",
            name="失败测试",
            steps=[
                TestStep(
                    step_id="1",
                    description="点击不存在的元素",
                    action_type=ActionType.CLICK,
                ),
                TestStep(
                    step_id="2",
                    description="不应该执行",
                    action_type=ActionType.CLICK,
                ),
            ],
        )

        context.config["stop_on_failure"] = True
        result = await executor.execute_case(case, context)

        assert result is not None
        # 第一个步骤失败后应停止
        assert len(result.step_results) <= 1

    @pytest.mark.asyncio
    async def test_execute_case_continue_on_failure(self, executor, context):
        """测试失败时继续"""
        case = TestCase(
            case_id="TC004",
            name="继续执行测试",
            steps=[
                TestStep(
                    step_id="1",
                    description="点击不存在的元素",
                    action_type=ActionType.CLICK,
                ),
                TestStep(
                    step_id="2",
                    description="继续执行",
                    action_type=ActionType.WAIT,
                ),
            ],
        )

        context.config["stop_on_failure"] = False
        result = await executor.execute_case(case, context)

        assert result is not None
        # 应该执行所有步骤
        assert len(result.step_results) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

