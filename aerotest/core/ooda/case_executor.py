"""ç¨ä¾æ§è¡å¨

ç¨äºæ§è¡å®æ´çæµè¯ç¨ä¾
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
    """ç¨ä¾æ§è¡å¨
    
    ç¨äºæ§è¡å®æ´çæµè¯ç¨ä¾ï¼ç®¡çæ­¥éª¤æ§è¡é¡ºåºåå¼å¸¸å¤ç
    
    Example:
        ```python
        executor = CaseExecutor(cdp_session)
        
        # åå»ºç¨ä¾
        case = TestCase(
            case_id="TC001",
            name="ç»å½æµè¯",
            steps=[
                TestStep(step_id="1", description="è¾å¥ç¨æ·å", ...),
                TestStep(step_id="2", description="è¾å¥å¯ç ", ...),
                TestStep(step_id="3", description="ç¹å»ç»å½", ...),
            ]
        )
        
        # æ§è¡ç¨ä¾
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
        åå§åç¨ä¾æ§è¡å¨
        
        Args:
            cdp_session: CDP Sessionï¼å¯éï¼
            use_l3: æ¯å¦å¯ç¨ L3 ç©ºé´å¸å±æ¨ç
            use_l4: æ¯å¦å¯ç¨ L4 AI æ¨ç
            use_l5: æ¯å¦å¯ç¨ L5 è§è§è¯å«
            max_retries: æå¤§éè¯æ¬¡æ°
            logger: æ¥å¿è®°å½å¨
        """
        self.logger = logger or get_logger(__name__)
        self.cdp_session = cdp_session
        self.max_retries = max_retries

        # åå§å OODA å¼æ
        self.ooda_engine = OODAEngine(
            cdp_session=cdp_session,
            use_l3=use_l3,
            use_l4=use_l4,
            use_l5=use_l5,
        )

        self.logger.info(
            f"ç¨ä¾æ§è¡å¨åå§åå®æ "
            f"(L3={use_l3}, L4={use_l4}, L5={use_l5}, "
            f"max_retries={max_retries})"
        )

    async def execute_case(
        self,
        case: TestCase,
        context: Optional[ExecutionContext] = None,
    ) -> ExecutionResult:
        """
        æ§è¡æµè¯ç¨ä¾
        
        Args:
            case: æµè¯ç¨ä¾
            context: æ§è¡ä¸ä¸æï¼å¯éï¼
            
        Returns:
            æ§è¡ç»æ
        """
        self.logger.info(f"å¼å§æ§è¡ç¨ä¾: {case.case_id} - {case.name}")
        start_time = datetime.now()
        case.start_time = start_time
        case.status = ActionStatus.RUNNING

        # åå§åä¸ä¸æ
        if context is None:
            context = ExecutionContext()

        # åå¹¶ç¨ä¾ç¯å¢åä¸ä¸æ
        if case.environment:
            context.config.update(case.environment)

        # åå§åç»è®¡ä¿¡æ¯
        stats = {
            "total": len(case.steps),
            "success": 0,
            "failed": 0,
            "skipped": 0,
        }

        # æ­¥éª¤ç»æåè¡¨
        step_results = []

        try:
            # éä¸ªæ§è¡æ­¥éª¤
            for i, step in enumerate(case.steps):
                self.logger.info(
                    f"æ§è¡æ­¥éª¤ {i + 1}/{len(case.steps)}: "
                    f"{step.step_id} - {step.description}"
                )

                # æ§è¡æ­¥éª¤ï¼å¸¦éè¯ï¼
                result = await self._execute_step_with_retry(step, context)

                # è®°å½ç»æ
                step_results.append(result)

                # æ´æ°ç»è®¡
                if result.status == ActionStatus.SUCCESS:
                    stats["success"] += 1
                elif result.status == ActionStatus.FAILED:
                    stats["failed"] += 1
                    # å¤±è´¥æ¶ï¼æ ¹æ®éç½®å³å®æ¯å¦ç»§ç»­
                    if context.config.get("stop_on_failure", True):
                        self.logger.warning(
                            f"æ­¥éª¤å¤±è´¥ï¼åæ­¢æ§è¡: {step.step_id}"
                        )
                        break
                elif result.status == ActionStatus.SKIPPED:
                    stats["skipped"] += 1

                # æ·»å å°åå²è®°å½
                context.history.append(step)

            # æ´æ°ç¨ä¾ç¶æ
            if stats["failed"] > 0:
                case.status = ActionStatus.FAILED
            elif stats["skipped"] == stats["total"]:
                case.status = ActionStatus.SKIPPED
            else:
                case.status = ActionStatus.SUCCESS

        except Exception as e:
            self.logger.error(f"ç¨ä¾æ§è¡å¼å¸¸: {str(e)}", exc_info=True)
            case.status = ActionStatus.FAILED

        finally:
            case.end_time = datetime.now()
            case.duration_ms = (
                (case.end_time - case.start_time).total_seconds() * 1000
            )

        # æå»ºç»æ
        result = ExecutionResult(
            success=(case.status == ActionStatus.SUCCESS),
            status=case.status,
            data=case,
            duration_ms=case.duration_ms,
            step_results=step_results,
            stats=stats,
        )

        self.logger.info(
            f"ç¨ä¾æ§è¡å®æ: {case.case_id} - "
            f"ç¶æ: {case.status}, "
            f"æå: {stats['success']}/{stats['total']}, "
            f"èæ¶: {case.duration_ms:.2f}ms"
        )

        return result

    async def _execute_step_with_retry(
        self,
        step,
        context: ExecutionContext,
    ) -> ExecutionResult:
        """
        æ§è¡æ­¥éª¤ï¼å¸¦éè¯ï¼
        
        Args:
            step: æµè¯æ­¥éª¤
            context: æ§è¡ä¸ä¸æ
            
        Returns:
            æ§è¡ç»æ
        """
        retry_count = 0
        last_error = None

        while retry_count <= self.max_retries:
            try:
                # æ§è¡æ­¥éª¤
                result = await self.ooda_engine.execute_step(step, context)

                # å¦ææåï¼ç´æ¥è¿å
                if result.success:
                    return result

                # å¦æå¤±è´¥ä½å¯éè¯
                last_error = result.error

                if retry_count < self.max_retries:
                    self.logger.warning(
                        f"æ­¥éª¤æ§è¡å¤±è´¥ï¼è¿è¡ç¬¬ {retry_count + 1} æ¬¡éè¯: "
                        f"{step.step_id}"
                    )
                    retry_count += 1
                    step.action.retry_count = retry_count
                    step.action.status = ActionStatus.RETRY
                else:
                    # è¾¾å°æå¤§éè¯æ¬¡æ°
                    self.logger.error(
                        f"æ­¥éª¤æ§è¡å¤±è´¥ï¼å·²è¾¾æå¤§éè¯æ¬¡æ°: {step.step_id}"
                    )
                    return result

            except Exception as e:
                last_error = str(e)
                self.logger.error(
                    f"æ­¥éª¤æ§è¡å¼å¸¸ (retry={retry_count}): {str(e)}",
                    exc_info=True,
                )

                if retry_count < self.max_retries:
                    retry_count += 1
                else:
                    # è¾¾å°æå¤§éè¯æ¬¡æ°ï¼è¿åå¤±è´¥ç»æ
                    return ExecutionResult(
                        success=False,
                        status=ActionStatus.FAILED,
                        error=last_error,
                    )

        # ä¸åºè¯¥å°è¾¾è¿éï¼ä½ä½ä¸ºä¿é©
        return ExecutionResult(
            success=False,
            status=ActionStatus.FAILED,
            error=last_error or "æªç¥éè¯¯",
        )

    async def batch_execute(
        self,
        cases: list[TestCase],
        context: Optional[ExecutionContext] = None,
    ) -> list[ExecutionResult]:
        """
        æ¹éæ§è¡æµè¯ç¨ä¾
        
        Args:
            cases: æµè¯ç¨ä¾åè¡¨
            context: æ§è¡ä¸ä¸æï¼å¯éï¼
            
        Returns:
            æ§è¡ç»æåè¡¨
        """
        self.logger.info(f"å¼å§æ¹éæ§è¡ {len(cases)} ä¸ªç¨ä¾")

        results = []
        for i, case in enumerate(cases):
            self.logger.info(f"æ§è¡ç¨ä¾ {i + 1}/{len(cases)}: {case.name}")
            result = await self.execute_case(case, context)
            results.append(result)

        # ç»è®¡
        total = len(results)
        success = sum(1 for r in results if r.success)
        failed = total - success

        self.logger.info(
            f"æ¹éæ§è¡å®æ: æå {success}/{total}, å¤±è´¥ {failed}"
        )

        return results
