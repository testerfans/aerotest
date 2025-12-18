"""DOM 处理模块

复用 browser-use 的 DOM 提取和序列化能力
"""

from aerotest.browser.dom.dom_service import DomService
from aerotest.browser.dom.event_listener_detector import (
    EventListenerDetector,
    EventListenerInfo,
)
from aerotest.browser.dom import enhanced_snapshot

__all__ = [
    "DomService",
    "EventListenerDetector",
    "EventListenerInfo",
    "enhanced_snapshot",
]
