"""漏斗基础类

定义漏斗各层的基类和通用接口
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional

from aerotest.browser.dom.views import SerializedDOMState
from aerotest.core.funnel.types import ActionSlot, FunnelContext, MatchResult
from aerotest.utils import get_logger

logger = get_logger("aerotest.funnel")


class BaseFunnelLayer(ABC):
    """漏斗层基类
    
    所有漏斗层（L1-L5）的基类，定义统一的接口
    """
    
    def __init__(self, layer_name: str):
        """
        初始化漏斗层
        
        Args:
            layer_name: 层名称（L1, L2, L3, L4, L5）
        """
        self.layer_name = layer_name
        self.logger = get_logger(f"aerotest.funnel.{layer_name.lower()}")
    
    @abstractmethod
    async def process(
        self,
        context: FunnelContext,
        dom_state: Optional[SerializedDOMState] = None,
    ) -> FunnelContext:
        """
        处理输入并返回更新后的上下文
        
        Args:
            context: 漏斗上下文
            dom_state: DOM 状态（某些层需要）
            
        Returns:
            更新后的上下文
        """
        pass
    
    def log_start(self):
        """记录层开始处理"""
        self.logger.info(f"🔍 {self.layer_name} 开始处理")
    
    def log_end(self, result_count: int = 0):
        """记录层处理完成"""
        self.logger.info(f"✅ {self.layer_name} 处理完成，找到 {result_count} 个候选")


@dataclass
class FunnelResult:
    """漏斗最终结果
    
    完整的五层漏斗处理结果
    
    Attributes:
        success: 是否成功找到元素
        result: 最终选择的匹配结果
        all_candidates: 所有层的候选结果
        context: 完整的处理上下文
        elapsed_time: 总耗时（秒）
    """
    
    success: bool
    result: Optional[MatchResult] = None
    all_candidates: dict[str, list[MatchResult]] = None
    context: Optional[FunnelContext] = None
    elapsed_time: float = 0.0
    
    def __post_init__(self):
        if self.all_candidates is None:
            self.all_candidates = {}
    
    def get_best_match(self) -> Optional[MatchResult]:
        """获取得分最高的匹配"""
        return self.result
    
    def get_layer_candidates(self, layer: str) -> list[MatchResult]:
        """获取指定层的候选结果"""
        return self.all_candidates.get(layer, [])
    
    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "success": self.success,
            "result": {
                "element_id": self.result.element.backend_node_id if self.result else None,
                "element_tag": self.result.element.tag_name if self.result else None,
                "score": self.result.score if self.result else 0.0,
                "layer": self.result.layer if self.result else None,
                "reasons": self.result.match_reasons if self.result else [],
            } if self.result else None,
            "candidates_count": {
                layer: len(candidates)
                for layer, candidates in self.all_candidates.items()
            },
            "elapsed_time": self.elapsed_time,
        }


class FunnelEngine:
    """漏斗引擎基类
    
    管理多个漏斗层的执行流程
    """
    
    def __init__(self, name: str):
        """
        初始化引擎
        
        Args:
            name: 引擎名称
        """
        self.name = name
        self.logger = get_logger(f"aerotest.funnel.{name}")
        self.layers: list[BaseFunnelLayer] = []
    
    def add_layer(self, layer: BaseFunnelLayer):
        """添加漏斗层"""
        self.layers.append(layer)
        self.logger.debug(f"添加层: {layer.layer_name}")
    
    async def run(
        self,
        instruction: str,
        dom_state: SerializedDOMState,
    ) -> FunnelResult:
        """
        执行漏斗流程
        
        Args:
            instruction: 自然语言指令
            dom_state: DOM 状态
            
        Returns:
            漏斗结果
        """
        import time
        
        start_time = time.time()
        
        # 创建初始上下文
        context = FunnelContext(instruction=instruction)
        
        # 依次执行各层
        for layer in self.layers:
            try:
                context = await layer.process(context, dom_state)
            except Exception as e:
                self.logger.error(f"{layer.layer_name} 处理失败: {e}")
                raise
        
        elapsed_time = time.time() - start_time
        
        # 构建结果
        result = FunnelResult(
            success=context.final_result is not None,
            result=context.final_result,
            all_candidates={
                "L2": context.l2_candidates,
                "L3": context.l3_candidates,
                "L4": context.l4_candidates,
            },
            context=context,
            elapsed_time=elapsed_time,
        )
        
        self.logger.info(
            f"✅ 漏斗处理完成: success={result.success}, "
            f"elapsed={elapsed_time*1000:.1f}ms"
        )
        
        return result
