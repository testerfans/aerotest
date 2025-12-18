"""CDP 连接管理

管理�?Chrome DevTools Protocol �?WebSocket 连接

来源: 简化自 browser-use v0.11.2
"""

import asyncio
import json
from typing import Optional

import httpx
from cdp_use import CDPClient

from aerotest.browser.cdp.types import CDPConnectionConfig, TargetInfo
from aerotest.utils import get_logger

logger = get_logger("aerotest.cdp.connection")


class CDPConnection:
    """CDP WebSocket 连接管理�?
    
    负责�?
    - 连接�?Chrome DevTools Protocol
    - 管理 WebSocket 生命周期
    - 获取可用的浏览器目标（页面）
    
    Example:
        ```python
        config = CDPConnectionConfig(host="localhost", port=9222)
        connection = CDPConnection(config)
        
        await connection.connect()
        targets = await connection.get_targets()
        await connection.disconnect()
        ```
    """
    
    def __init__(self, config: CDPConnectionConfig):
        """
        初始�?CDP 连接
        
        Args:
            config: CDP 连接配置
        """
        self.config = config
        self.client: Optional[CDPClient] = None
        self._connected = False
        
        logger.debug(f"初始�?CDP 连接: {config.http_url}")
    
    async def connect(self) -> CDPClient:
        """
        连接�?Chrome DevTools Protocol
        
        Returns:
            CDPClient 实例
            
        Raises:
            ConnectionError: 连接失败
        """
        if self._connected and self.client:
            logger.debug("CDP 已连接，复用现有连接")
            return self.client
        
        try:
            logger.info(f"正在连接 CDP: {self.config.http_url}")
            
            # 检�?CDP 是否可用
            await self._check_cdp_availability()
            
            # 获取浏览�?WebSocket URL
            ws_url = await self._get_browser_ws_url()
            
            # 创建 CDP 客户�?
            self.client = CDPClient()
            
            # 连接到浏览器
            await asyncio.wait_for(
                self.client.connect(ws_url),
                timeout=self.config.timeout
            )
            
            self._connected = True
            logger.info("�?CDP 连接成功")
            
            return self.client
            
        except asyncio.TimeoutError as e:
            logger.error(f"CDP 连接超时: {e}")
            raise ConnectionError(f"连接超时: {self.config.timeout}�?) from e
        except Exception as e:
            logger.error(f"CDP 连接失败: {e}")
            raise ConnectionError(f"无法连接�?CDP: {e}") from e
    
    async def disconnect(self):
        """断开 CDP 连接"""
        if not self._connected or not self.client:
            logger.debug("CDP 未连接，无需断开")
            return
        
        try:
            logger.info("正在断开 CDP 连接...")
            await self.client.disconnect()
            self._connected = False
            self.client = None
            logger.info("�?CDP 已断开")
            
        except Exception as e:
            logger.error(f"断开 CDP 连接时出�? {e}")
            self._connected = False
            self.client = None
    
    async def get_targets(self, target_type: str = "page") -> list[TargetInfo]:
        """
        获取可用的浏览器目标
        
        Args:
            target_type: 目标类型（page, iframe, worker等）
            
        Returns:
            目标信息列表
        """
        try:
            url = f"{self.config.http_url}/json/list"
            
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                targets_data = response.json()
            
            targets = []
            for target_data in targets_data:
                # 过滤目标类型
                if target_data.get("type") == target_type:
                    target = TargetInfo(
                        target_id=target_data["id"],
                        target_type=target_data["type"],
                        url=target_data.get("url", "about:blank"),
                        title=target_data.get("title", ""),
                        attached="webSocketDebuggerUrl" in target_data,
                    )
                    targets.append(target)
            
            logger.debug(f"找到 {len(targets)} �?{target_type} 类型的目�?)
            return targets
            
        except Exception as e:
            logger.error(f"获取目标列表失败: {e}")
            return []
    
    async def get_first_page_target(self) -> Optional[TargetInfo]:
        """
        获取第一个可用的页面目标
        
        Returns:
            页面目标信息，如果没有则返回 None
        """
        targets = await self.get_targets(target_type="page")
        
        if not targets:
            logger.warning("没有找到可用的页面目�?)
            return None
        
        # 优先选择�?about:blank 的页�?
        for target in targets:
            if target.url != "about:blank":
                logger.debug(f"选择目标: {target.title} ({target.url})")
                return target
        
        # 如果都是 about:blank，返回第一�?
        logger.debug(f"选择目标: {targets[0].title} (默认)")
        return targets[0]
    
    async def create_new_page(self, url: str = "about:blank") -> Optional[TargetInfo]:
        """
        创建新的页面目标
        
        Args:
            url: 初始 URL
            
        Returns:
            新创建的页面目标信息
        """
        try:
            create_url = f"{self.config.http_url}/json/new?{url}"
            
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                response = await client.get(create_url)
                response.raise_for_status()
                target_data = response.json()
            
            target = TargetInfo(
                target_id=target_data["id"],
                target_type=target_data["type"],
                url=target_data.get("url", url),
                title=target_data.get("title", ""),
                attached=True,
            )
            
            logger.info(f"�?创建新页�? {target.target_id}")
            return target
            
        except Exception as e:
            logger.error(f"创建新页面失�? {e}")
            return None
    
    async def close_target(self, target_id: str) -> bool:
        """
        关闭指定的目�?
        
        Args:
            target_id: 目标 ID
            
        Returns:
            是否成功关闭
        """
        try:
            close_url = f"{self.config.http_url}/json/close/{target_id}"
            
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                response = await client.get(close_url)
                response.raise_for_status()
            
            logger.info(f"�?关闭目标: {target_id}")
            return True
            
        except Exception as e:
            logger.error(f"关闭目标失败: {e}")
            return False
    
    async def _check_cdp_availability(self):
        """检�?CDP 是否可用"""
        try:
            url = f"{self.config.http_url}/json/version"
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                version_info = response.json()
            
            browser = version_info.get("Browser", "Unknown")
            protocol_version = version_info.get("Protocol-Version", "Unknown")
            
            logger.debug(f"CDP 可用: {browser}, 协议版本: {protocol_version}")
            
        except Exception as e:
            raise ConnectionError(
                f"CDP 不可用。请确保：\n"
                f"1. Chrome/Edge 已启动\n"
                f"2. 使用 --remote-debugging-port={self.config.port} 参数启动\n"
                f"3. 地址 {self.config.http_url} 可访问\n"
                f"错误: {e}"
            ) from e
    
    async def _get_browser_ws_url(self) -> str:
        """获取浏览器的 WebSocket URL"""
        try:
            url = f"{self.config.http_url}/json/version"
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                version_info = response.json()
            
            ws_url = version_info.get("webSocketDebuggerUrl")
            
            if not ws_url:
                raise ValueError("无法获取 WebSocket URL")
            
            logger.debug(f"浏览�?WebSocket URL: {ws_url}")
            return ws_url
            
        except Exception as e:
            raise ConnectionError(f"无法获取 WebSocket URL: {e}") from e
    
    @property
    def is_connected(self) -> bool:
        """是否已连�?""
        return self._connected and self.client is not None
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.disconnect()

