"""用例执行器

用于执行完整的测试用例
"""

from datetime import datetime
from typing import Optional

from loguru import logger

from aerotest.core.ooda.ooda_engine import OODAEngine
from aerotest.core.ooda.types import (
    ActionStatus,
    ExecutionContext,
    ExecutionResult,
    TestCase,
)
from aerotest.utils.logger import get_logger


class CaseExecutor:
    """用例执行器
    
    用于执行完整的测试用例，管理步骤执行顺序和异常处理
    
    Example:
        ```python
        executor = CaseExecutor(cdp_session)
        
        # 创建用例
        case = TestCase(
            case_id="TC001",
            name="登录测试",
            steps=[
                TestStep(step_id="1", description="输入用户名", ...),
                TestStep(step_id="2", description="输入密码", ...),
                TestStep(step_id="3", description="点击登录", ...),
            ]
        )
        
        # 执行用例
        result = await executor.execute_case(case, context)
        ```
    """

    def __init__(
        self,
        cdp_session=None,
        use_l3: bool = True,
        use_l4: bool = True,
        use_l5: bool = True,
        max_retries: int = 2,
        logger=None,
    ):
        """
        初始化用例执行器
        
        Args:
            cdp_session: CDP Session（可选）
            use_l3: 是否启用 L3 空间布局推理
            use_l4: 是否启用 L4 AI 推理
            use_l5: 是否启用 L5 视觉识别
            max_retries: 最大重试次数
            logger: 日志记录器
        """
        self.logger = logger or get_logger(__name__)
        self.cdp_session = cdp_session
        self.max_retries = max_retries

        # 初始化 OODA 引擎
        self.ooda_engine = OODAEngine(
            cdp_session=cdp_session,
            use_l3=use_l3,
            use_l4=use_l4,
            use_l5=use_l5,
        )

        self.logger.info(
            f"用例执行器初始化完成 "
            f"(L3={use_l3}, L4={use_l4}, L5={use_l5}, "
            f"max_retries={max_retries})"
        )

    async def execute_case(
        self,
        case: TestCase,
        context: Optional[ExecutionContext] = None,
    ) -> ExecutionResult:
        """
        执行测试用例
        
        Args:
            case: 测试用例
            context: 执行上下文（可选）
            
        Returns:
            执行结果
        """
        self.logger.info(f"开始执行用例: {case.case_id} - {case.name}")
        start_time = datetime.now()
        case.start_time = start_time
        case.status = ActionStatus.RUNNING

        # 初始化上下文
        if context is None:
            context = ExecutionContext()

        # 合并用例环境和上下文
        if case.environment:
            context.config.update(case.environment)

        # 初始化统计信息
        stats = {
            "total": len(case.steps),
            "success": 0,
            "failed": 0,
            "skipped": 0,
        }

        # 步骤结果列表
        step_results = []

        try:
            # 逐个执行步骤
            for i, step in enumerate(case.steps):
                self.logger.info(
                    f"执行步骤 {i + 1}/{len(case.steps)}: "
                    f"{step.step_id} - {step.description}"
                )

                # 执行步骤（带重试）
                result = await self._execute_step_with_retry(step, context)

                # 记录结果
                step_results.append(result)

                # 更新统计
                if result.status == ActionStatus.SUCCESS:
                    stats["success"] += 1
                elif result.status == ActionStatus.FAILED:
                    stats["failed"] += 1
                    # 失败时，根据配置决定是否继续
                    if context.config.get("stop_on_failure", True):
                        self.logger.warning(
                            f"步骤失败，停止执行: {step.step_id}"
                        )
                        break
                elif result.status == ActionStatus.SKIPPED:
                    stats["skipped"] += 1

                # 添加到历史记录
                context.history.append(step)

            # 更新用例状态
            if stats["failed"] > 0:
                case.status = ActionStatus.FAILED
            elif stats["skipped"] == stats["total"]:
                case.status = ActionStatus.SKIPPED
            else:
                case.status = ActionStatus.SUCCESS

        except Exception as e:
            self.logger.error(f"用例执行异常: {str(e)}", exc_info=True)
            case.status = ActionStatus.FAILED

        finally:
            case.end_time = datetime.now()
            case.duration_ms = (
                (case.end_time - case.start_time).total_seconds() * 1000
            )

        # 构建结果
        result = ExecutionResult(
            success=(case.status == ActionStatus.SUCCESS),
            status=case.status,
            data=case,
            duration_ms=case.duration_ms,
            step_results=step_results,
            stats=stats,
        )

        self.logger.info(
            f"用例执行完成: {case.case_id} - "
            f"状态: {case.status}, "
            f"成功: {stats['success']}/{stats['total']}, "
            f"耗时: {case.duration_ms:.2f}ms"
        )

        return result

    async def _execute_step_with_retry(
        self,
        step,
        context: ExecutionContext,
    ) -> ExecutionResult:
        """
        执行步骤（带重试）
        
        Args:
            step: 测试步骤
            context: 执行上下文
            
        Returns:
            执行结果
        """
        retry_count = 0
        last_error = None

        while retry_count <= self.max_retries:
            try:
                # 执行步骤
                result = await self.ooda_engine.execute_step(step, context)

                # 如果成功，直接返回
                if result.success:
                    return result

                # 如果失败但可重试
                last_error = result.error

                if retry_count < self.max_retries:
                    self.logger.warning(
                        f"步骤执行失败，进行第 {retry_count + 1} 次重试: "
                        f"{step.step_id}"
                    )
                    retry_count += 1
                    step.action.retry_count = retry_count
                    step.action.status = ActionStatus.RETRY
                else:
                    # 达到最大重试次数
                    self.logger.error(
                        f"步骤执行失败，已达最大重试次数: {step.step_id}"
                    )
                    return result

            except Exception as e:
                last_error = str(e)
                self.logger.error(
                    f"步骤执行异常 (retry={retry_count}): {str(e)}",
                    exc_info=True,
                )

                if retry_count < self.max_retries:
                    retry_count += 1
                else:
                    # 达到最大重试次数，返回失败结果
                    return ExecutionResult(
                        success=False,
                        status=ActionStatus.FAILED,
                        error=last_error,
                    )

        # 不应该到达这里，但作为保险
        return ExecutionResult(
            success=False,
            status=ActionStatus.FAILED,
            error=last_error or "未知错误",
        )

    async def batch_execute(
        self,
        cases: list[TestCase],
        context: Optional[ExecutionContext] = None,
    ) -> list[ExecutionResult]:
        """
        批量执行测试用例
        
        Args:
            cases: 测试用例列表
            context: 执行上下文（可选）
            
        Returns:
            执行结果列表
        """
        self.logger.info(f"开始批量执行 {len(cases)} 个用例")

        results = []
        for i, case in enumerate(cases):
            self.logger.info(f"执行用例 {i + 1}/{len(cases)}: {case.name}")
            result = await self.execute_case(case, context)
            results.append(result)

        # 统计
        total = len(results)
        success = sum(1 for r in results if r.success)
        failed = total - success

        self.logger.info(
            f"批量执行完成: 成功 {success}/{total}, 失败 {failed}"
        )

        return results
