"""漏斗引擎核心逻辑"""

from typing import Any, Dict, List, Optional

from aerotest.config import get_settings
from aerotest.core.types import ElementLocatorStrategy
from aerotest.utils import get_logger

logger = get_logger("aerotest.funnel.engine")


class FunnelResult:
    """漏斗查询结果"""

    def __init__(
        self,
        strategy: ElementLocatorStrategy,
        element: Optional[Any] = None,
        confidence: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.strategy = strategy
        self.element = element
        self.confidence = confidence
        self.metadata = metadata or {}

    def is_success(self) -> bool:
        """判断是否成功找到元素"""
        return self.element is not None

    def __repr__(self) -> str:
        return f"<FunnelResult strategy={self.strategy} confidence={self.confidence:.2f}>"


class FunnelEngine:
    """五层漏斗决策引擎"""

    def __init__(self, dom_adapter: Any):
        """
        初始化漏斗引�?

        Args:
            dom_adapter: DOM 适配器实�?
        """
        self.settings = get_settings()
        self.dom_adapter = dom_adapter

        # 初始化各�?
        self.layers: List[Any] = []
        self._init_layers()

        logger.info("漏斗引擎初始化完�?)

    def _init_layers(self) -> None:
        """初始化各层处理器"""
        # TODO: 根据配置初始化各�?
        # if self.settings.l1_enabled:
        #     from aerotest.core.funnel.l1_rule import L1RuleLayer
        #     self.layers.append(L1RuleLayer())

        # if self.settings.l2_enabled:
        #     from aerotest.core.funnel.l2_attribute import L2AttributeLayer
        #     self.layers.append(L2AttributeLayer())

        # ... 其他�?

        logger.info(f"已启�?{len(self.layers)} 个漏斗层")

    async def locate_element(self, selector: str, context: Optional[Dict[str, Any]] = None) -> FunnelResult:
        """
        通过漏斗机制定位元素

        Args:
            selector: 元素选择器（支持自然语言�?
            context: 可选的上下文信�?

        Returns:
            FunnelResult: 漏斗查询结果
        """
        logger.info(f"开始漏斗定�? selector='{selector}'")
        context = context or {}

        # 依次尝试各层
        for layer in self.layers:
            try:
                logger.debug(f"尝试 {layer.__class__.__name__}")
                result = await layer.locate(selector, context, self.dom_adapter)

                if result and result.is_success():
                    logger.info(f"定位成功: {result}")
                    return result

            except Exception as e:
                logger.warning(f"{layer.__class__.__name__} 处理失败: {e}")
                continue

        # 所有层都失�?
        logger.error(f"所有漏斗层都未能定位元�? '{selector}'")
        return FunnelResult(
            strategy=ElementLocatorStrategy.FALLBACK,
            element=None,
            confidence=0.0,
            metadata={"error": "All layers failed"},
        )

