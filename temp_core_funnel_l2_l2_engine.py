"""L2 引擎

L2 层的主引擎，整合所�?L2 组件
"""

from typing import Optional

from aerotest.browser.dom.views import EnhancedDOMTreeNode
from aerotest.browser.dom.views import SerializedDOMState
from aerotest.core.funnel.base import BaseFunnelLayer
from aerotest.core.funnel.l2.attribute_matcher import AttributeMatcher
from aerotest.core.funnel.l2.scorer import Scorer
from aerotest.core.funnel.l2.text_matcher import TextMatcher
from aerotest.core.funnel.l2.type_matcher import TypeMatcher
from aerotest.core.funnel.types import ActionSlot, FunnelContext, MatchResult


class L2Engine(BaseFunnelLayer):
    """L2 启发式属性匹配引�?
    
    基于 L1 提取的槽位信息，�?DOM 树中匹配目标元素�?
    1. 类型筛选：根据元素类型过滤候�?
    2. 属性匹配：基于各种属性匹配关键词
    3. 评分排序：计算综合得分并排序
    4. 返回 Top-N：返回最佳候�?
    
    Example:
        ```python
        engine = L2Engine()
        
        # 异步处理
        context = FunnelContext(...)
        context.action_slot = slot
        context = await engine.process(context, dom_state)
        candidates = context.l2_candidates
        
        # 同步匹配
        results = engine.match_elements(dom_state, slot)
        ```
    """
    
    def __init__(self, top_n: int = 10):
        """
        初始�?L2 引擎
        
        Args:
            top_n: 返回�?N 个候�?
        """
        super().__init__("L2")
        
        # 初始化各个组�?
        self.attribute_matcher = AttributeMatcher()
        self.text_matcher = TextMatcher()
        self.type_matcher = TypeMatcher()
        self.scorer = Scorer()
        
        self.top_n = top_n
        
        self.logger.info(f"L2 引擎初始化完�?(Top-N: {top_n})")
    
    async def process(
        self,
        context: FunnelContext,
        dom_state: Optional[SerializedDOMState] = None,
    ) -> FunnelContext:
        """
        基于槽位信息匹配 DOM 元素
        
        Args:
            context: 漏斗上下文（需要包�?action_slot�?
            dom_state: DOM 状�?
            
        Returns:
            更新后的上下文（包含 l2_candidates�?
        """
        self.log_start()
        
        if not context.action_slot:
            self.logger.warning("没有槽位信息，跳�?L2")
            return context
        
        if not dom_state:
            self.logger.warning("没有 DOM 状态，跳过 L2")
            return context
        
        slot = context.action_slot
        
        # 执行匹配
        results = self.match_elements(dom_state, slot)
        
        # 更新上下�?
        context.l2_candidates = results
        
        # 记录详细信息
        if results:
            best_score = results[0].score
            self.logger.info(
                f"L2 处理完成: {len(results)} 个候选，"
                f"最高得�? {best_score:.2f}"
            )
        
        self.log_end(len(results))
        return context
    
    def match_elements(
        self,
        dom_state: SerializedDOMState,
        slot: ActionSlot,
    ) -> list[MatchResult]:
        """
        匹配元素（同步版本，用于外部调用�?
        
        Args:
            dom_state: DOM 状�?
            slot: 动作槽位
            
        Returns:
            匹配结果列表（按得分降序�?
        """
        # 1. 获取所有可交互元素
        candidates = self._get_interactive_elements(dom_state)
        
        self.logger.debug(f"初始候�? {len(candidates)} 个元�?)
        
        # 2. 类型筛选（如果有类型信息）
        if slot.target_type:
            candidates = self.type_matcher.match_by_type(candidates, slot.target_type)
            self.logger.debug(f"类型筛选后: {len(candidates)} 个元�?)
        
        if not candidates:
            self.logger.warning("类型筛选后无候选元�?)
            return []
        
        # 3. 评分和排�?
        results = self.scorer.score_elements(candidates, slot, top_n=self.top_n)
        
        return results
    
    def _get_interactive_elements(
        self,
        dom_state: SerializedDOMState,
    ) -> list[EnhancedDOMTreeNode]:
        """
        获取所有可交互元素
        
        Args:
            dom_state: DOM 状�?
            
        Returns:
            可交互元素列�?
        """
        interactive_elements = []
        
        # 遍历所有元�?
        for node in dom_state.simplified_nodes:
            # 只保留标记为可点击的元素，或者是表单元素
            if node.is_clickable:
                interactive_elements.append(node)
            elif node.tag_name and node.tag_name.lower() in ["input", "textarea", "select"]:
                interactive_elements.append(node)
        
        return interactive_elements

