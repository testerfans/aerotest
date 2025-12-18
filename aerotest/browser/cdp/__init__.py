"""CDP (Chrome DevTools Protocol) 集成模块

提供轻量级的 CDP 连接和会话管理，�?AeroTest 能够�?
- 连接到本�?Chrome/Edge 浏览�?
- 获取页面 DOM �?
- 执行基本页面操作

这是 Week 3 的核心模块，采用智能复用策略�?
- 复用 browser-use 的核心算�?
- 简化架构，移除不需要的功能（EventBus, Cloud, Watchdogs等）

来源: 部分复用 browser-use v0.11.2
许可�? MIT
"""

from aerotest.browser.cdp.connection import CDPConnection, CDPConnectionConfig
from aerotest.browser.cdp.session import CDPSession
from aerotest.browser.cdp.types import PageInfo, TargetInfo

__all__ = [
    # 连接
    "CDPConnection",
    "CDPConnectionConfig",
    # 会话
    "CDPSession",
    # 类型
    "PageInfo",
    "TargetInfo",
]

