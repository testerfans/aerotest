"""事件监听器检测器

使用 CDP DOMDebugger.getEventListeners 检测元素绑定的事件监听�?
"""

from dataclasses import dataclass
from typing import Any, Optional

from aerotest.utils import get_logger

logger = get_logger("aerotest.dom.event_listener")


@dataclass
class EventListenerInfo:
    """事件监听器信�?""
    
    type: str  # 事件类型（click, input, change, etc.�?
    use_capture: bool = False  # 是否捕获阶段
    passive: bool = False  # 是否被动监听
    once: bool = False  # 是否只触发一�?
    handler_body: Optional[str] = None  # 处理函数代码（可选）
    
    def __repr__(self) -> str:
        flags = []
        if self.use_capture:
            flags.append("capture")
        if self.passive:
            flags.append("passive")
        if self.once:
            flags.append("once")
        
        flag_str = f" ({', '.join(flags)})" if flags else ""
        return f"<EventListener: {self.type}{flag_str}>"


class EventListenerDetector:
    """事件监听器检测器
    
    核心能力�?
    - 检测元素绑定的事件监听�?
    - 支持所有事件类型（click, input, change, mousedown, etc.�?
    - 识别非标准交互元�?
    
    使用场景�?
    - L3 层检测非标控件（�?div 绑定�?click 事件�?
    - 验证元素是否可交�?
    - 调试和分析页面交�?
    
    Example:
        ```python
        detector = EventListenerDetector()
        
        listeners = await detector.get_event_listeners(
            cdp_client=cdp_client,
            node_id=123,
            session_id="session_abc"
        )
        
        has_click = any(l.type == "click" for l in listeners)
        if has_click:
            print("元素可点�?)
        ```
    """
    
    # 常见的交互事件类�?
    INTERACTIVE_EVENTS = {
        "click", "dblclick", "mousedown", "mouseup",
        "input", "change", "keydown", "keyup", "keypress",
        "submit", "focus", "blur",
        "touchstart", "touchend", "touchmove",
        "pointerdown", "pointerup",
    }
    
    def __init__(self):
        """初始化事件监听器检测器"""
        logger.debug("事件监听器检测器初始化完�?)
    
    async def get_event_listeners(
        self,
        cdp_client: Any,
        node_id: int,
        session_id: str,
        depth: int = 1
    ) -> list[EventListenerInfo]:
        """
        获取元素的事件监听器
        
        Args:
            cdp_client: CDP 客户�?
            node_id: DOM 节点 ID (backend_node_id)
            session_id: CDP Session ID
            depth: 递归深度（默�?1，只检测当前元素）
            
        Returns:
            事件监听器列�?
        """
        try:
            # 1. �?backend_node_id 转换�?Remote Object
            # 注意：CDP 需要先 resolveNode 才能获取 objectId
            resolve_result = await cdp_client.send(
                "DOM.resolveNode",
                {"backendNodeId": node_id},
                session_id=session_id
            )
            
            if "object" not in resolve_result:
                logger.warning(f"无法解析节点 {node_id}")
                return []
            
            object_id = resolve_result["object"]["objectId"]
            
            # 2. 获取事件监听�?
            listeners_result = await cdp_client.send(
                "DOMDebugger.getEventListeners",
                {
                    "objectId": object_id,
                    "depth": depth,  # 递归深度
                    "pierce": True,  # 穿�?Shadow DOM
                },
                session_id=session_id
            )
            
            # 3. 解析事件监听�?
            event_listeners = []
            for listener in listeners_result.get("listeners", []):
                event_info = EventListenerInfo(
                    type=listener["type"],
                    use_capture=listener.get("useCapture", False),
                    passive=listener.get("passive", False),
                    once=listener.get("once", False),
                )
                event_listeners.append(event_info)
            
            if event_listeners:
                logger.debug(
                    f"节点 {node_id} �?{len(event_listeners)} 个事件监听器: "
                    f"{[l.type for l in event_listeners]}"
                )
            
            return event_listeners
        
        except Exception as e:
            logger.warning(f"获取事件监听器失�?(node_id={node_id}): {str(e)}")
            return []
    
    def has_interactive_events(
        self,
        listeners: list[EventListenerInfo]
    ) -> bool:
        """
        判断是否有交互事件监听器
        
        Args:
            listeners: 事件监听器列�?
            
        Returns:
            是否有交互事�?
        """
        return any(
            l.type in self.INTERACTIVE_EVENTS
            for l in listeners
        )
    
    def has_event_type(
        self,
        listeners: list[EventListenerInfo],
        event_type: str
    ) -> bool:
        """
        判断是否有特定类型的事件监听�?
        
        Args:
            listeners: 事件监听器列�?
            event_type: 事件类型（如 "click"�?
            
        Returns:
            是否有该类型的事�?
        """
        return any(l.type == event_type for l in listeners)
    
    def filter_by_type(
        self,
        listeners: list[EventListenerInfo],
        event_types: list[str]
    ) -> list[EventListenerInfo]:
        """
        按事件类型过�?
        
        Args:
            listeners: 事件监听器列�?
            event_types: 事件类型列表
            
        Returns:
            过滤后的监听器列�?
        """
        return [
            l for l in listeners
            if l.type in event_types
        ]

