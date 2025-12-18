"""L4 引擎

L4 AI 推理引擎，整合所�?L4 组件
"""

from typing import Optional

from aerotest.browser.dom.views import SerializedDOMState
from aerotest.core.funnel.base import BaseFunnelLayer
from aerotest.core.funnel.l4.context_extractor import ContextExtractor
from aerotest.core.funnel.l4.prompt_builder import PromptBuilder
from aerotest.core.funnel.l4.qwen_client import QwenClient
from aerotest.core.funnel.types import FunnelContext, MatchResult
from aerotest.utils import get_logger

logger = get_logger("aerotest.funnel.l4")


class L4Engine(BaseFunnelLayer):
    """L4 AI 推理引擎
    
    使用 Qwen-Max/Plus 进行语义理解和复杂逻辑推理�?
    1. 检查是否需�?L4
    2. 提取上下文信�?
    3. 构建 Prompt
    4. 调用 Qwen API
    5. 解析结果
    6. 返回最佳匹�?
    
    Example:
        ```python
        engine = L4Engine()
        
        # 处理复杂逻辑
        context = FunnelContext(instruction="选择最便宜的商�?)
        context.l2_candidates = [...]  # L2 的候�?
        context = await engine.process(context, dom_state)
        
        if context.l4_candidates:
            print(f"AI 选择: {context.l4_candidates[0].element.tag_name}")
        ```
    """
    
    def __init__(
        self,
        confidence_threshold: float = 0.7,
        use_l4_for_ambiguity: bool = True,
    ):
        """
        初始�?L4 引擎
        
        Args:
            confidence_threshold: 置信度阈值（低于此值才使用 L4�?
            use_l4_for_ambiguity: 是否在模糊场景使�?L4
        """
        super().__init__("L4")
        
        # 初始化组�?
        self.qwen_client = QwenClient()
        self.prompt_builder = PromptBuilder()
        self.context_extractor = ContextExtractor()
        
        self.confidence_threshold = confidence_threshold
        self.use_l4_for_ambiguity = use_l4_for_ambiguity
        
        self.logger.info(
            f"L4 引擎初始化完�?"
            f"(threshold={confidence_threshold})"
        )
    
    async def process(
        self,
        context: FunnelContext,
        dom_state: Optional[SerializedDOMState] = None,
    ) -> FunnelContext:
        """
        AI 推理处理
        
        Args:
            context: 漏斗上下�?
            dom_state: DOM 状�?
            
        Returns:
            更新后的上下文（包含 l4_candidates�?
        """
        self.log_start()
        
        if not context.action_slot:
            self.logger.warning("没有槽位信息，跳�?L4")
            return context
        
        instruction = context.instruction
        
        # 1. 检查是否需�?L4
        # 如果 L2/L3 已经有高置信度结果，跳过 L4
        if context.l2_candidates and len(context.l2_candidates) > 0:
            best_score = context.l2_candidates[0].score
            if best_score >= self.confidence_threshold:
                self.logger.info(f"L2 置信度足够高({best_score:.2f})，跳�?L4")
                return context
        
        if context.l3_candidates and len(context.l3_candidates) > 0:
            best_score = context.l3_candidates[0].score
            if best_score >= self.confidence_threshold:
                self.logger.info(f"L3 置信度足够高({best_score:.2f})，跳�?L4")
                return context
        
        # 2. 获取候选元素（优先 L3，其�?L2�?
        candidates = context.l3_candidates if context.l3_candidates else context.l2_candidates
        
        if not candidates or len(candidates) == 0:
            self.logger.warning("没有候选元素，跳过 L4")
            return context
        
        self.logger.info(f"使用 L4 处理 {len(candidates)} 个候�?)
        
        # 3. 提取上下�?
        ai_context = self.context_extractor.extract_context(
            instruction=instruction,
            candidates=candidates,
            dom_state=dom_state,
        )
        
        # 4. 构建 Prompt
        messages = self.prompt_builder.build_element_selection_prompt(
            instruction=instruction,
            candidates=candidates,
            context=ai_context,
        )
        
        # 5. 调用 Qwen API
        try:
            result = await self.qwen_client.chat_with_json(messages)
            
            # 6. 解析结果
            if "selected_index" in result:
                selected_index = result["selected_index"]
                reason = result.get("reason", "")
                
                if 0 <= selected_index < len(candidates):
                    selected_result = candidates[selected_index]
                    
                    # 创建新的 MatchResult（提升置信度�?
                    l4_result = MatchResult(
                        element=selected_result.element,
                        score=0.95,  # L4 的结果给予高置信�?
                        matched_attributes=selected_result.matched_attributes,
                        match_reasons=[
                            f"AI 推理选择 (索引: {selected_index})",
                            f"原因: {reason}",
                        ],
                        layer="L4",
                    )
                    
                    context.l4_candidates = [l4_result]
                    
                    self.logger.info(
                        f"L4 处理完成: 选择元素 {selected_index}, "
                        f"原因: {reason}"
                    )
                else:
                    self.logger.error(f"AI 返回的索引超出范�? {selected_index}")
            else:
                self.logger.error(f"AI 返回格式错误: {result}")
        
        except Exception as e:
            self.logger.error(f"L4 处理失败: {str(e)}")
            # 失败时不影响整体流程，返回原 context
        
        self.log_end(len(context.l4_candidates) if context.l4_candidates else 0)
        return context


# 关闭时清理资�?
async def cleanup_l4_engine(engine: L4Engine):
    """清理 L4 引擎资源"""
    await engine.qwen_client.close()

