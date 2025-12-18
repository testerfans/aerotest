"""L3 引擎

L3 空间布局推理引擎，整合所�?L3 组件
"""

from typing import Optional

from aerotest.browser.dom.event_listener_detector import EventListenerDetector
from aerotest.browser.dom.views import SerializedDOMState
from aerotest.core.funnel.base import BaseFunnelLayer
from aerotest.core.funnel.l3.anchor_locator import AnchorLocator
from aerotest.core.funnel.l3.proximity_detector import ProximityDetector
from aerotest.core.funnel.types import FunnelContext, MatchResult
from aerotest.utils import get_logger

logger = get_logger("aerotest.funnel.l3")


class L3Engine(BaseFunnelLayer):
    """L3 空间布局推理引擎
    
    使用空间位置关系和锚点定位解决非标准控件问题�?
    1. 检测空间关�?
    2. 提取锚点信息
    3. 定位锚点元素
    4. 邻近搜索
    5. 转换�?MatchResult
    6. 返回候�?
    
    Example:
        ```python
        engine = L3Engine()
        
        # 处理包含空间关系的指�?
        context = FunnelContext(instruction="点击用户名输入框右边的按�?)
        context = await engine.process(context, dom_state)
        
        candidates = context.l3_candidates
        if candidates:
            print(f"找到 {len(candidates)} 个候�?)
            print(f"最佳匹�? {candidates[0].element.tag_name}")
        ```
    """
    
    def __init__(
        self,
        max_distance: float = 300.0,
        top_n: int = 5,
        use_event_listeners: bool = True,
    ):
        """
        初始�?L3 引擎
        
        Args:
            max_distance: 最大搜索距离（像素�?
            top_n: 返回�?N 个结�?
            use_event_listeners: 是否使用事件监听器检测（增强非标控件识别�?
        """
        super().__init__("L3")
        
        # 初始化组�?
        self.anchor_locator = AnchorLocator()
        self.proximity_detector = ProximityDetector(max_distance=max_distance)
        self.event_detector = EventListenerDetector() if use_event_listeners else None
        
        self.max_distance = max_distance
        self.top_n = top_n
        self.use_event_listeners = use_event_listeners
        
        self.logger.info(
            f"L3 引擎初始化完�?"
            f"(max_distance={max_distance}px, top_n={top_n}, "
            f"event_listeners={use_event_listeners})"
        )
    
    async def process(
        self,
        context: FunnelContext,
        dom_state: Optional[SerializedDOMState] = None,
    ) -> FunnelContext:
        """
        空间布局推理处理
        
        Args:
            context: 漏斗上下�?
            dom_state: DOM 状�?
            
        Returns:
            更新后的上下文（包含 l3_candidates�?
        """
        self.log_start()
        
        if not context.action_slot:
            self.logger.warning("没有槽位信息，跳�?L3")
            return context
        
        if not dom_state:
            self.logger.warning("没有 DOM 状态，跳过 L3")
            return context
        
        instruction = context.instruction
        
        # 1. 检查是否包含空间关�?
        if not self.anchor_locator.has_spatial_relation(instruction):
            self.logger.info("指令不包含空间关系，跳过 L3")
            return context
        
        # 2. 提取锚点信息
        anchor_info = self.anchor_locator.extract_anchor(instruction)
        if not anchor_info:
            self.logger.warning("无法提取锚点信息")
            return context
        
        # 3. 定位锚点元素
        anchor_element = self.anchor_locator.locate_anchor(anchor_info, dom_state)
        if not anchor_element:
            self.logger.warning("无法定位锚点元素")
            return context
        
        self.logger.info(f"锚点元素: {anchor_element.tag_name}")
        
        # 4. 获取所有候选元�?
        candidates = self._get_all_elements(dom_state)
        
        # 5. 邻近搜索
        proximity_results = self.proximity_detector.find_nearby_elements(
            anchor=anchor_element,
            candidates=candidates,
            direction=anchor_info.direction,
            max_distance=anchor_info.distance or self.max_distance,
        )
        
        # 5.5. 增强：检查事件监听器（非标控件检测）
        if self.use_event_listeners and self.event_detector:
            enhanced_results = []
            for result in proximity_results:
                element = result.element
                
                # 检查是否有事件监听器（如果节点有该属性）
                if hasattr(element, 'event_listeners') and element.event_listeners:
                    # 有事件监听器，提升得�?
                    has_interactive = self.event_detector.has_interactive_events(
                        element.event_listeners
                    )
                    if has_interactive:
                        # 提升 0.1 �?
                        result.score = min(1.0, result.score + 0.1)
                        self.logger.debug(
                            f"元素 {element.backend_node_id} 有事件监听器�?
                            f"得分提升�?{result.score:.2f}"
                        )
                
                enhanced_results.append(result)
            
            proximity_results = enhanced_results
        
        # 6. 转换�?MatchResult
        match_results = []
        for i, proximity_result in enumerate(proximity_results[:self.top_n]):
            reasons = [
                f"距离锚点 {proximity_result.distance:.1f}px",
                f"角度 {proximity_result.angle:.1f}°",
                f"方向匹配: {proximity_result.direction_match}",
            ]
            
            # 添加事件监听器信�?
            element = proximity_result.element
            if hasattr(element, 'event_listeners') and element.event_listeners:
                event_types = [l.type for l in element.event_listeners]
                reasons.append(f"事件监听�? {', '.join(event_types)}")
            
            match_result = MatchResult(
                element=proximity_result.element,
                score=proximity_result.score,
                matched_attributes={
                    "distance": proximity_result.distance,
                    "angle": proximity_result.angle,
                },
                match_reasons=reasons,
                layer="L3",
            )
            match_results.append(match_result)
        
        context.l3_candidates = match_results
        
        # 记录结果
        if match_results:
            best = match_results[0]
            self.logger.info(
                f"L3 处理完成: {len(match_results)} 个候选，"
                f"最佳得�? {best.score:.2f}"
            )
        
        self.log_end(len(match_results))
        return context
    
    def _get_all_elements(
        self,
        dom_state: SerializedDOMState,
    ) -> list:
        """
        获取所有元�?
        
        Args:
            dom_state: DOM 状�?
            
        Returns:
            所有元素列�?
        """
        # 返回所有简化节�?
        return list(dom_state.simplified_nodes)

