"""OODA 引擎

实现完整�?OODA (Observe-Orient-Decide-Act) 循环
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

from loguru import logger

from aerotest.browser.dom.views import EnhancedDOMTreeNode
from aerotest.browser.dom.dom_service import DomService
from aerotest.core.funnel.l1.l1_engine import L1Engine
from aerotest.core.funnel.l2.l2_engine import L2Engine
from aerotest.core.funnel.l3.l3_engine import L3Engine
from aerotest.core.funnel.l4.l4_engine import L4Engine
from aerotest.core.funnel.l5.l5_engine import L5Engine
from aerotest.core.funnel.types import ActionSlot, MatchResult
from aerotest.core.ooda.types import (
    Action,
    ActionStatus,
    ActionType,
    Decision,
    ExecutionContext,
    ExecutionResult,
    Observation,
    Orientation,
    TestStep,
)
from aerotest.utils.logger import get_logger


class OODAEngine:
    """OODA 引擎
    
    实现完整�?OODA 循环，用于智�?UI 自动化测�?
    
    工作流程�?
    1. Observe: 观察当前页面状�?
    2. Orient: 分析并定位目标元素（五层漏斗�?
    3. Decide: 决策执行策略
    4. Act: 执行操作并验证结�?
    
    Example:
        ```python
        engine = OODAEngine(cdp_session)
        
        # 执行单个步骤
        step = TestStep(
            step_id="1",
            description="点击登录按钮",
            action_type=ActionType.CLICK
        )
        result = await engine.execute_step(step, context)
        ```
    """

    def __init__(
        self,
        cdp_session=None,
        use_l3: bool = True,
        use_l4: bool = True,
        use_l5: bool = True,
        logger=None,
    ):
        """
        初始�?OODA 引擎
        
        Args:
            cdp_session: CDP Session（可选）
            use_l3: 是否启用 L3 空间布局推理
            use_l4: 是否启用 L4 AI 推理
            use_l5: 是否启用 L5 视觉识别
            logger: 日志记录�?
        """
        self.logger = logger or get_logger(__name__)
        self.cdp_session = cdp_session

        # 初始�?DOM 服务
        self.dom_service = DomService(cdp_session)

        # 初始化五层漏�?
        self.l1_engine = L1Engine()
        self.l2_engine = L2Engine()
        self.l3_engine = L3Engine() if use_l3 else None
        self.l4_engine = L4Engine() if use_l4 else None
        self.l5_engine = L5Engine(cdp_session) if use_l5 else None

        self.use_l3 = use_l3
        self.use_l4 = use_l4
        self.use_l5 = use_l5

        self.logger.info(
            f"OODA 引擎初始化完�?"
            f"(L3={use_l3}, L4={use_l4}, L5={use_l5})"
        )

    async def execute_step(
        self,
        step: TestStep,
        context: ExecutionContext,
    ) -> ExecutionResult:
        """
        执行单个测试步骤（完整的 OODA 循环�?
        
        Args:
            step: 测试步骤
            context: 执行上下�?
            
        Returns:
            执行结果
        """
        self.logger.info(f"开始执行步�? {step.step_id} - {step.description}")
        start_time = datetime.now()
        step.start_time = start_time
        step.status = ActionStatus.RUNNING

        try:
            # 1. Observe: 观察页面状�?
            observation = await self._observe(context)
            step.observation = observation
            self.logger.debug(f"Observe 完成")

            # 2. Orient: 分析定位目标元素
            orientation = await self._orient(step, observation, context)
            step.orientation = orientation
            self.logger.debug(
                f"Orient 完成 - 策略: {orientation.strategy}, "
                f"置信�? {orientation.confidence:.2f}"
            )

            # 3. Decide: 决策执行策略
            decision = await self._decide(step, orientation, context)
            step.decision = decision
            self.logger.debug(f"Decide 完成 - 操作: {decision.action_type}")

            # 4. Act: 执行操作
            action = await self._act(decision, context)
            step.action = action
            self.logger.debug(f"Act 完成 - 状�? {action.status}")

            # 5. 验证结果
            if step.expected_value is not None:
                await self._verify(step, action, context)

            # 6. 更新步骤状�?
            step.status = action.status
            step.end_time = datetime.now()
            step.duration_ms = (
                (step.end_time - step.start_time).total_seconds() * 1000
            )

            # 7. 构建结果
            result = ExecutionResult(
                success=(action.status == ActionStatus.SUCCESS),
                status=action.status,
                data=action.result,
                error=action.error,
                duration_ms=step.duration_ms,
                metadata={
                    "strategy": orientation.strategy,
                    "confidence": orientation.confidence,
                },
            )

            self.logger.info(
                f"步骤执行完成: {step.step_id} - "
                f"状�? {step.status}, 耗时: {step.duration_ms:.2f}ms"
            )

            return result

        except Exception as e:
            self.logger.error(f"步骤执行失败: {step.step_id} - {str(e)}", exc_info=True)
            step.status = ActionStatus.FAILED
            step.error = str(e)
            step.end_time = datetime.now()
            step.duration_ms = (
                (step.end_time - step.start_time).total_seconds() * 1000
            )

            return ExecutionResult(
                success=False,
                status=ActionStatus.FAILED,
                error=str(e),
                duration_ms=step.duration_ms,
            )

    async def _observe(self, context: ExecutionContext) -> Observation:
        """
        Observe: 观察当前页面状�?
        
        Args:
            context: 执行上下�?
            
        Returns:
            观察结果
        """
        self.logger.debug("开�?Observe 阶段")

        observation = Observation()

        # 获取 DOM �?
        if context.target_id:
            try:
                # 使用增强�?DOM 树（包含事件监听器）
                if hasattr(self.dom_service, "get_dom_tree_with_events"):
                    dom_tree = await self.dom_service.get_dom_tree_with_events(
                        context.target_id
                    )
                else:
                    dom_tree = self.dom_service.get_dom_tree(context.target_id)

                observation.dom_tree = dom_tree

                # 收集可见和可交互元素
                self._collect_elements(dom_tree, observation)

            except Exception as e:
                self.logger.warning(f"获取 DOM 树失�? {str(e)}")

        # 获取页面信息（如果有 CDP Session�?
        if self.cdp_session and context.target_id:
            try:
                # TODO: �?CDP Session 获取 URL, title �?
                # observation.url = await self.cdp_session.get_url(context.target_id)
                # observation.title = await self.cdp_session.get_title(context.target_id)
                pass
            except Exception as e:
                self.logger.warning(f"获取页面信息失败: {str(e)}")

        self.logger.debug(
            f"Observe 完成 - "
            f"可见元素: {len(observation.visible_elements)}, "
            f"可交互元�? {len(observation.interactive_elements)}"
        )

        return observation

    def _collect_elements(
        self, node: EnhancedDOMTreeNode, observation: Observation
    ):
        """
        递归收集可见和可交互元素
        
        Args:
            node: DOM 节点
            observation: 观察结果
        """
        if node.is_visible:
            observation.visible_elements.append(node)

        if node.is_clickable or (
            hasattr(node, "event_listeners") and node.event_listeners
        ):
            observation.interactive_elements.append(node)

        for child in node.children:
            self._collect_elements(child, observation)

    async def _orient(
        self,
        step: TestStep,
        observation: Observation,
        context: ExecutionContext,
    ) -> Orientation:
        """
        Orient: 分析并定位目标元素（五层漏斗�?
        
        Args:
            step: 测试步骤
            observation: 观察结果
            context: 执行上下�?
            
        Returns:
            定向结果
        """
        self.logger.debug("开�?Orient 阶段")

        orientation = Orientation(current_step=step)

        # L1: 槽位提取
        try:
            action_slot = await self.l1_engine.extract_slot(
                step.description, context.variables
            )
            orientation.action_slot = action_slot

            if not action_slot:
                self.logger.warning("L1 槽位提取失败")
                return orientation

            self.logger.debug(f"L1 槽位提取成功: {action_slot}")

        except Exception as e:
            self.logger.error(f"L1 失败: {str(e)}")
            return orientation

        # L2: 启发式属性匹�?
        try:
            if observation.dom_tree:
                l2_matches = await self.l2_engine.match_elements(
                    observation.dom_tree, action_slot, context.variables
                )

                if l2_matches:
                    orientation.candidate_elements = l2_matches
                    orientation.best_match = l2_matches[0]
                    orientation.strategy = "L2"
                    orientation.confidence = l2_matches[0].score

                    self.logger.debug(
                        f"L2 匹配成功: {len(l2_matches)} 个候�? "
                        f"最佳得�? {l2_matches[0].score:.2f}"
                    )

                    # 如果 L2 得分足够高，直接返回
                    if l2_matches[0].score >= 0.8:
                        return orientation

        except Exception as e:
            self.logger.error(f"L2 失败: {str(e)}")

        # L3: 空间布局推理
        if self.use_l3 and self.l3_engine and not orientation.best_match:
            try:
                l3_matches = await self.l3_engine.process(
                    step.description, observation.dom_tree, context.variables
                )

                if l3_matches:
                    orientation.candidate_elements = l3_matches
                    orientation.best_match = l3_matches[0]
                    orientation.strategy = "L3"
                    orientation.confidence = l3_matches[0].score

                    self.logger.debug(
                        f"L3 匹配成功: {len(l3_matches)} 个候�? "
                        f"最佳得�? {l3_matches[0].score:.2f}"
                    )

                    # 如果 L3 得分足够高，直接返回
                    if l3_matches[0].score >= 0.7:
                        return orientation

            except Exception as e:
                self.logger.error(f"L3 失败: {str(e)}")

        # L4: AI 推理
        if self.use_l4 and self.l4_engine and not orientation.best_match:
            try:
                l4_result = await self.l4_engine.process(
                    step.description, observation.dom_tree, context.variables
                )

                if l4_result:
                    orientation.best_match = l4_result
                    orientation.strategy = "L4"
                    orientation.confidence = l4_result.score

                    self.logger.debug(f"L4 推理成功: 得分 {l4_result.score:.2f}")

                    # 如果 L4 得分足够高，直接返回
                    if l4_result.score >= 0.6:
                        return orientation

            except Exception as e:
                self.logger.error(f"L4 失败: {str(e)}")

        # L5: 视觉识别
        if self.use_l5 and self.l5_engine and not orientation.best_match:
            try:
                l5_result = await self.l5_engine.process(
                    step.description, context.target_id, context.variables
                )

                if l5_result:
                    orientation.best_match = l5_result
                    orientation.strategy = "L5"
                    orientation.confidence = l5_result.score

                    self.logger.debug(f"L5 识别成功: 得分 {l5_result.score:.2f}")

            except Exception as e:
                self.logger.error(f"L5 失败: {str(e)}")

        self.logger.debug(
            f"Orient 完成 - 策略: {orientation.strategy}, "
            f"置信�? {orientation.confidence:.2f}"
        )

        return orientation

    async def _decide(
        self,
        step: TestStep,
        orientation: Orientation,
        context: ExecutionContext,
    ) -> Decision:
        """
        Decide: 决策执行策略
        
        Args:
            step: 测试步骤
            orientation: 定向结果
            context: 执行上下�?
            
        Returns:
            决策结果
        """
        self.logger.debug("开�?Decide 阶段")

        decision = Decision(action_type=step.action_type)

        # 检查是否找到目标元�?
        if not orientation.best_match:
            decision.should_execute = False
            decision.reason = "未找到目标元�?
            self.logger.warning("Decide: 未找到目标元素，跳过执行")
            return decision

        # 设置目标元素
        decision.target_element = orientation.best_match.element

        # 设置操作参数
        if orientation.action_slot:
            if orientation.action_slot.value:
                decision.parameters["value"] = orientation.action_slot.value

            if orientation.action_slot.target_attributes:
                decision.parameters.update(orientation.action_slot.target_attributes)

        # 决策原因
        decision.reason = (
            f"使用 {orientation.strategy} 策略, "
            f"置信�? {orientation.confidence:.2f}"
        )

        self.logger.debug(f"Decide 完成 - 操作: {decision.action_type}")

        return decision

    async def _act(
        self, decision: Decision, context: ExecutionContext
    ) -> Action:
        """
        Act: 执行操作
        
        Args:
            decision: 决策结果
            context: 执行上下�?
            
        Returns:
            行动结果
        """
        self.logger.debug("开�?Act 阶段")

        action = Action(
            action_type=decision.action_type,
            target_element=decision.target_element,
            parameters=decision.parameters,
        )

        action.start_time = datetime.now()
        action.status = ActionStatus.RUNNING

        try:
            # 检查是否应该执�?
            if not decision.should_execute:
                action.status = ActionStatus.SKIPPED
                action.result = None
                action.error = decision.reason
                self.logger.info(f"操作跳过: {decision.reason}")
                return action

            # 执行操作（根据类型）
            if decision.action_type == ActionType.CLICK:
                result = await self._execute_click(decision, context)
                action.result = result
                action.status = ActionStatus.SUCCESS

            elif decision.action_type == ActionType.INPUT:
                result = await self._execute_input(decision, context)
                action.result = result
                action.status = ActionStatus.SUCCESS

            elif decision.action_type == ActionType.WAIT:
                result = await self._execute_wait(decision, context)
                action.result = result
                action.status = ActionStatus.SUCCESS

            elif decision.action_type == ActionType.ASSERT:
                result = await self._execute_assert(decision, context)
                action.result = result
                action.status = ActionStatus.SUCCESS

            else:
                # 其他操作类型暂未实现
                action.status = ActionStatus.FAILED
                action.error = f"不支持的操作类型: {decision.action_type}"
                self.logger.warning(action.error)

        except Exception as e:
            self.logger.error(f"操作执行失败: {str(e)}", exc_info=True)
            action.status = ActionStatus.FAILED
            action.error = str(e)

        finally:
            action.end_time = datetime.now()
            action.duration_ms = (
                (action.end_time - action.start_time).total_seconds() * 1000
            )

        self.logger.debug(f"Act 完成 - 状�? {action.status}")

        return action

    async def _execute_click(
        self, decision: Decision, context: ExecutionContext
    ) -> Any:
        """
        执行点击操作
        
        Args:
            decision: 决策结果
            context: 执行上下�?
            
        Returns:
            执行结果
        """
        self.logger.info(
            f"执行点击: "
            f"元素 {decision.target_element.backend_node_id} "
            f"({decision.target_element.tag_name})"
        )

        # TODO: 实际�?CDP 点击操作
        # if self.cdp_session:
        #     await self.cdp_session.click(
        #         decision.target_element.backend_node_id,
        #         context.target_id
        #     )

        # 模拟延迟
        await asyncio.sleep(0.1)

        return {"clicked": True, "element_id": decision.target_element.backend_node_id}

    async def _execute_input(
        self, decision: Decision, context: ExecutionContext
    ) -> Any:
        """
        执行输入操作
        
        Args:
            decision: 决策结果
            context: 执行上下�?
            
        Returns:
            执行结果
        """
        value = decision.parameters.get("value", "")

        self.logger.info(
            f"执行输入: "
            f"元素 {decision.target_element.backend_node_id}, "
            f"�? '{value}'"
        )

        # TODO: 实际�?CDP 输入操作
        # if self.cdp_session:
        #     await self.cdp_session.input(
        #         decision.target_element.backend_node_id,
        #         value,
        #         context.target_id
        #     )

        # 模拟延迟
        await asyncio.sleep(0.1)

        return {"input": True, "value": value}

    async def _execute_wait(
        self, decision: Decision, context: ExecutionContext
    ) -> Any:
        """
        执行等待操作
        
        Args:
            decision: 决策结果
            context: 执行上下�?
            
        Returns:
            执行结果
        """
        duration = decision.parameters.get("duration", 1.0)

        self.logger.info(f"执行等待: {duration} �?)

        await asyncio.sleep(duration)

        return {"waited": True, "duration": duration}

    async def _execute_assert(
        self, decision: Decision, context: ExecutionContext
    ) -> Any:
        """
        执行断言操作
        
        Args:
            decision: 决策结果
            context: 执行上下�?
            
        Returns:
            执行结果
        """
        expected = decision.parameters.get("expected")
        actual = decision.parameters.get("actual")

        self.logger.info(f"执行断言: expected={expected}, actual={actual}")

        if expected == actual:
            return {"assert": True, "passed": True}
        else:
            raise AssertionError(f"断言失败: expected={expected}, actual={actual}")

    async def _verify(
        self, step: TestStep, action: Action, context: ExecutionContext
    ):
        """
        验证执行结果
        
        Args:
            step: 测试步骤
            action: 行动结果
            context: 执行上下�?
        """
        if step.expected_value is None:
            return

        self.logger.debug(f"验证结果: expected={step.expected_value}")

        # TODO: 实现回执验证
        # 1. 等待页面响应
        # 2. 检查元素状态变�?
        # 3. 验证期望�?

