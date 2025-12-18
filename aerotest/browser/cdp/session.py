"""CDP 会话管理

提供简化的 CDP 会话接口，用于获�?DOM 和执行页面操�?

来源: 简化并改造自 browser-use v0.11.2
核心算法: 复用 browser-use �?DOM 获取逻辑
"""

import asyncio
import time
from typing import Optional

from cdp_use.cdp.target import SessionID, TargetID

from aerotest.browser.cdp.connection import CDPConnection
from aerotest.browser.cdp.types import CDPConnectionConfig, PageInfo, TargetInfo
from aerotest.browser.dom.views import EnhancedDOMTreeNode, TargetAllTrees
from aerotest.browser.dom.enhanced_snapshot import (
    REQUIRED_COMPUTED_STYLES,
    build_snapshot_lookup,
)
from aerotest.utils import get_logger

logger = get_logger("aerotest.cdp.session")


class CDPSession:
    """简化的 CDP 会话
    
    提供�?
    - 页面导航
    - DOM 获取（复�?browser-use 核心算法�?
    - 基本页面操作
    
    不包含（相比 browser-use）：
    - EventBus
    - Cloud Browser
    - Watchdogs
    - 视频录制
    
    Example:
        ```python
        config = CDPConnectionConfig()
        async with CDPSession.connect(config) as session:
            await session.navigate("https://example.com")
            dom_tree = await session.get_dom_tree()
        ```
    """
    
    def __init__(
        self,
        connection: CDPConnection,
        target_info: Optional[TargetInfo] = None,
    ):
        """
        初始�?CDP 会话
        
        Args:
            connection: CDP 连接
            target_info: 目标信息（如果为 None，会自动选择第一个页面）
        """
        self.connection = connection
        self.target_info = target_info
        self.session_id: Optional[SessionID] = None
        self._page_info: Optional[PageInfo] = None
        
        logger.debug("初始�?CDP 会话")
    
    @classmethod
    async def connect(
        cls,
        config: Optional[CDPConnectionConfig] = None,
        target_info: Optional[TargetInfo] = None,
    ) -> "CDPSession":
        """
        创建并连�?CDP 会话
        
        Args:
            config: CDP 连接配置（如果为 None，使用默认配置）
            target_info: 目标信息（如果为 None，会自动选择第一个页面）
            
        Returns:
            CDP 会话实例
        """
        if config is None:
            config = CDPConnectionConfig()
        
        # 创建连接
        connection = CDPConnection(config)
        await connection.connect()
        
        # 如果没有指定目标，获取第一个页�?
        if target_info is None:
            target_info = await connection.get_first_page_target()
            
            if target_info is None:
                # 创建新页�?
                logger.info("没有可用页面，创建新页面...")
                target_info = await connection.create_new_page()
                
                if target_info is None:
                    raise RuntimeError("无法创建新页�?)
        
        # 创建会话
        session = cls(connection, target_info)
        await session._attach_to_target()
        
        logger.info(f"�?CDP 会话已创�? {target_info.title or target_info.url}")
        return session
    
    async def disconnect(self):
        """断开会话"""
        if self.session_id and self.connection.client:
            try:
                # 分离目标
                await self.connection.client.send.Target.detachFromTarget(
                    params={"sessionId": self.session_id}
                )
                logger.debug(f"已分离目�? {self.target_info.target_id}")
            except Exception as e:
                logger.debug(f"分离目标时出�? {e}")
        
        # 断开连接
        await self.connection.disconnect()
        logger.info("�?CDP 会话已断开")
    
    async def navigate(self, url: str, wait_until: str = "load") -> bool:
        """
        导航�?URL
        
        Args:
            url: 目标 URL
            wait_until: 等待条件（load, domcontentloaded, networkidle�?
            
        Returns:
            是否导航成功
        """
        try:
            logger.info(f"导航�? {url}")
            
            # 发送导航命�?
            result = await self.connection.client.send.Page.navigate(
                params={"url": url},
                session_id=self.session_id
            )
            
            # 等待页面加载
            if wait_until == "load":
                await self._wait_for_load()
            elif wait_until == "domcontentloaded":
                await self._wait_for_dom_content_loaded()
            elif wait_until == "networkidle":
                await self._wait_for_network_idle()
            
            # 更新页面信息
            await self._update_page_info()
            
            logger.info(f"�?导航完成: {url}")
            return True
            
        except Exception as e:
            logger.error(f"导航失败: {e}")
            return False
    
    async def get_dom_tree(self) -> EnhancedDOMTreeNode:
        """
        获取增强�?DOM �?
        
        完整实现：复�?browser-use �?DOM 获取算法
        
        Returns:
            增强�?DOM 树根节点
            
        Raises:
            RuntimeError: DOM 获取失败
        """
        try:
            logger.debug("开始获取完�?DOM �?..")
            
            # 获取所有树（Snapshot, DOM Tree, AX Tree�?
            all_trees = await self._get_all_trees()
            
            # 构建增强 DOM 树（完整版本�?
            root_node = await self._build_enhanced_dom_tree(
                all_trees,
                html_frames=None,
                total_frame_offset=None,
            )
            
            logger.info(f"�?完整 DOM 树获取成�?)
            return root_node
            
        except Exception as e:
            logger.error(f"获取 DOM 树失�? {e}")
            raise RuntimeError(f"获取 DOM 树失�? {e}") from e
    
    async def evaluate(self, expression: str) -> dict:
        """
        执行 JavaScript 代码
        
        Args:
            expression: JavaScript 表达�?
            
        Returns:
            执行结果
        """
        try:
            result = await self.connection.client.send.Runtime.evaluate(
                params={"expression": expression, "returnByValue": True},
                session_id=self.session_id
            )
            return result
        except Exception as e:
            logger.error(f"执行 JavaScript 失败: {e}")
            raise
    
    async def get_page_title(self) -> str:
        """获取页面标题"""
        try:
            result = await self.evaluate("document.title")
            return result.get("result", {}).get("value", "")
        except Exception:
            return ""
    
    async def get_page_url(self) -> str:
        """获取页面 URL"""
        try:
            result = await self.evaluate("window.location.href")
            return result.get("result", {}).get("value", "")
        except Exception:
            return ""
    
    async def screenshot(self, full_page: bool = False) -> bytes:
        """
        截取页面截图
        
        Args:
            full_page: 是否全页截图
            
        Returns:
            PNG 图片数据
        """
        try:
            import base64
            
            params = {"format": "png"}
            if full_page:
                params["captureBeyondViewport"] = True
            
            result = await self.connection.client.send.Page.captureScreenshot(
                params=params,
                session_id=self.session_id
            )
            
            # 解码 base64
            screenshot_data = base64.b64decode(result["data"])
            logger.info(f"�?截图完成: {len(screenshot_data)} 字节")
            return screenshot_data
            
        except Exception as e:
            logger.error(f"截图失败: {e}")
            raise
    
    # ========== 内部方法 ==========
    
    async def _attach_to_target(self):
        """附加到目�?""
        try:
            # 附加到目�?
            result = await self.connection.client.send.Target.attachToTarget(
                params={
                    "targetId": self.target_info.target_id,
                    "flatten": True
                }
            )
            
            self.session_id = result["sessionId"]
            logger.debug(f"已附加到目标: {self.target_info.target_id}")
            
            # 启用必要�?CDP �?
            await self._enable_cdp_domains()
            
        except Exception as e:
            raise RuntimeError(f"附加到目标失�? {e}") from e
    
    async def _enable_cdp_domains(self):
        """启用必要�?CDP �?""
        try:
            domains = ["Page", "DOM", "Runtime", "Accessibility", "DOMSnapshot"]
            
            for domain in domains:
                await self.connection.client.send(
                    f"{domain}.enable",
                    params={},
                    session_id=self.session_id
                )
            
            logger.debug(f"已启�?CDP �? {', '.join(domains)}")
            
        except Exception as e:
            logger.warning(f"启用 CDP 域时出错: {e}")
    
    async def _get_all_trees(self) -> TargetAllTrees:
        """
        获取所有树（Snapshot, DOM Tree, AX Tree�?
        
        复用 browser-use 的核心算�?
        
        Returns:
            TargetAllTrees 包含所有树数据
        """
        start_time = time.time()
        timing = {}
        
        try:
            # 1. 获取设备像素�?
            device_pixel_ratio = await self._get_viewport_ratio()
            
            # 2. 并行获取 Snapshot, DOM Tree, AX Tree
            snapshot_task = asyncio.create_task(
                self.connection.client.send.DOMSnapshot.captureSnapshot(
                    params={
                        "computedStyles": REQUIRED_COMPUTED_STYLES,
                        "includePaintOrder": True,
                        "includeDOMRects": True,
                        "includeBlendedBackgroundColors": False,
                        "includeTextColorOpacities": False,
                    },
                    session_id=self.session_id
                )
            )
            
            dom_tree_task = asyncio.create_task(
                self.connection.client.send.DOM.getDocument(
                    params={"depth": -1, "pierce": True},
                    session_id=self.session_id
                )
            )
            
            ax_tree_task = asyncio.create_task(
                self._get_ax_tree_for_all_frames()
            )
            
            # 等待所有任务完�?
            results = await asyncio.gather(
                snapshot_task,
                dom_tree_task,
                ax_tree_task,
                return_exceptions=True
            )
            
            snapshot, dom_tree, ax_tree = results
            
            # 检查错�?
            if isinstance(snapshot, Exception):
                raise snapshot
            if isinstance(dom_tree, Exception):
                raise dom_tree
            if isinstance(ax_tree, Exception):
                raise ax_tree
            
            # 记录时间
            timing["get_all_trees"] = time.time() - start_time
            timing["cdp_calls"] = timing["get_all_trees"]
            
            logger.debug(f"获取所有树完成，耗时: {timing['get_all_trees']*1000:.1f}ms")
            
            # 构建 TargetAllTrees
            return TargetAllTrees(
                snapshot=snapshot,
                dom_tree=dom_tree,
                ax_tree=ax_tree,
                device_pixel_ratio=device_pixel_ratio,
                cdp_timing=timing,
            )
            
        except Exception as e:
            logger.error(f"获取所有树失败: {e}")
            raise
    
    async def _get_ax_tree_for_all_frames(self) -> dict:
        """
        获取所有帧的辅助功能树
        
        复用 browser-use 的算�?
        """
        try:
            # 获取帧树
            frame_tree = await self.connection.client.send.Page.getFrameTree(
                session_id=self.session_id
            )
            
            # 收集所有帧 ID
            def collect_frame_ids(frame_tree_node) -> list[str]:
                frame_ids = [frame_tree_node["frame"]["id"]]
                if "childFrames" in frame_tree_node and frame_tree_node["childFrames"]:
                    for child_frame in frame_tree_node["childFrames"]:
                        frame_ids.extend(collect_frame_ids(child_frame))
                return frame_ids
            
            all_frame_ids = collect_frame_ids(frame_tree["frameTree"])
            
            # 为每个帧获取 AX �?
            ax_tree_tasks = []
            for frame_id in all_frame_ids:
                task = self.connection.client.send.Accessibility.getFullAXTree(
                    params={"frameId": frame_id},
                    session_id=self.session_id
                )
                ax_tree_tasks.append(task)
            
            # 等待所有任务完�?
            ax_trees = await asyncio.gather(*ax_tree_tasks, return_exceptions=True)
            
            # 合并所�?AX 节点
            merged_nodes = []
            for ax_tree in ax_trees:
                if not isinstance(ax_tree, Exception) and "nodes" in ax_tree:
                    merged_nodes.extend(ax_tree["nodes"])
            
            return {"nodes": merged_nodes}
            
        except Exception as e:
            logger.warning(f"获取 AX 树失�? {e}")
            return {"nodes": []}
    
    async def _get_viewport_ratio(self) -> float:
        """获取设备像素�?""
        try:
            metrics = await self.connection.client.send.Page.getLayoutMetrics(
                session_id=self.session_id
            )
            
            visual_viewport = metrics.get("visualViewport", {})
            css_visual_viewport = metrics.get("cssVisualViewport", {})
            css_layout_viewport = metrics.get("cssLayoutViewport", {})
            
            width = css_visual_viewport.get("clientWidth",
                                            css_layout_viewport.get("clientWidth", 1920.0))
            device_width = visual_viewport.get("clientWidth", width)
            css_width = css_visual_viewport.get("clientWidth", width)
            
            device_pixel_ratio = device_width / css_width if css_width > 0 else 1.0
            
            return float(device_pixel_ratio)
            
        except Exception as e:
            logger.debug(f"获取设备像素比失�? {e}")
            return 1.0
    
    async def _build_enhanced_dom_tree(
        self,
        all_trees: TargetAllTrees,
        html_frames: Optional[list] = None,
        total_frame_offset: Optional["DOMRect"] = None,
    ) -> EnhancedDOMTreeNode:
        """
        构建增强 DOM �?
        
        完整实现：复�?browser-use 的核心算�?
        
        Args:
            all_trees: 所有树数据
            html_frames: HTML 帧节点列�?
            total_frame_offset: 累积的帧偏移
            
        Returns:
            增强�?DOM 树根节点
        """
        import time
        from aerotest.browser.dom.cdp_types import DOMRect, EnhancedAXNode, EnhancedAXProperty
        from aerotest.browser.dom.views import EnhancedDOMTreeNode, NodeType
        
        start_time = time.time()
        
        # 构建 snapshot 查找�?
        snapshot_lookup = build_snapshot_lookup(
            all_trees.snapshot,
            all_trees.device_pixel_ratio
        )
        logger.debug(f"Snapshot 查找表构建完�? {len(snapshot_lookup)} 个节�?)
        
        # 构建 AX 树查找表
        ax_tree_lookup: dict[int, dict] = {}
        if all_trees.ax_tree and "nodes" in all_trees.ax_tree:
            for ax_node in all_trees.ax_tree["nodes"]:
                if "backendNodeId" in ax_node:
                    ax_tree_lookup[ax_node["backendNodeId"]] = ax_node
        logger.debug(f"AX 树查找表构建完成: {len(ax_tree_lookup)} 个节�?)
        
        # 记忆化查找表 (nodeId -> EnhancedDOMTreeNode)
        enhanced_dom_tree_node_lookup: dict[int, EnhancedDOMTreeNode] = {}
        
        # �?DOM 树根节点开始构�?
        dom_root = all_trees.dom_tree.get("root")
        if not dom_root:
            raise RuntimeError("DOM 树根节点为空")
        
        # 递归构建增强节点
        async def _construct_enhanced_node(
            node: dict,
            html_frames: Optional[list[EnhancedDOMTreeNode]],
            total_frame_offset: Optional[DOMRect],
        ) -> EnhancedDOMTreeNode:
            """递归构建增强 DOM 节点（复�?browser-use 核心算法�?""
            
            # 初始�?
            if html_frames is None:
                html_frames = []
            
            if total_frame_offset is None:
                total_frame_offset = DOMRect(x=0.0, y=0.0, width=0.0, height=0.0)
            else:
                # 复制以避免指针引�?
                total_frame_offset = DOMRect(
                    x=total_frame_offset.x,
                    y=total_frame_offset.y,
                    width=total_frame_offset.width,
                    height=total_frame_offset.height,
                )
            
            # 记忆化：避免重复构建
            node_id = node.get("nodeId")
            if node_id in enhanced_dom_tree_node_lookup:
                return enhanced_dom_tree_node_lookup[node_id]
            
            # 获取 backend_node_id
            backend_node_id = node.get("backendNodeId", 0)
            
            # �?AX 树获取辅助功能信�?
            enhanced_ax_node = None
            ax_node = ax_tree_lookup.get(backend_node_id)
            if ax_node:
                # 构建 EnhancedAXNode
                properties = []
                if "properties" in ax_node and ax_node["properties"]:
                    for prop in ax_node["properties"]:
                        try:
                            properties.append(
                                EnhancedAXProperty(
                                    name=prop.get("name", ""),
                                    value=prop.get("value", {}).get("value"),
                                )
                            )
                        except (ValueError, KeyError):
                            pass
                
                enhanced_ax_node = EnhancedAXNode(
                    ax_node_id=ax_node.get("nodeId", ""),
                    ignored=ax_node.get("ignored", False),
                    role=ax_node.get("role", {}).get("value"),
                    name=ax_node.get("name", {}).get("value"),
                    description=ax_node.get("description", {}).get("value"),
                    properties=properties if properties else None,
                    child_ids=ax_node.get("childIds"),
                )
            
            # 解析属�?
            attributes = {}
            if "attributes" in node and node["attributes"]:
                attrs_list = node["attributes"]
                for i in range(0, len(attrs_list), 2):
                    if i + 1 < len(attrs_list):
                        attributes[attrs_list[i]] = attrs_list[i + 1]
            
            # Shadow Root 类型
            shadow_root_type = None
            if "shadowRootType" in node and node["shadowRootType"]:
                shadow_root_type = node["shadowRootType"]
            
            # �?Snapshot 获取数据
            snapshot_data = snapshot_lookup.get(backend_node_id)
            
            # 计算绝对位置（考虑 iframe 偏移�?
            absolute_position = None
            if snapshot_data and snapshot_data.bounds:
                absolute_position = DOMRect(
                    x=snapshot_data.bounds.x + total_frame_offset.x,
                    y=snapshot_data.bounds.y + total_frame_offset.y,
                    width=snapshot_data.bounds.width,
                    height=snapshot_data.bounds.height,
                )
            
            # 创建增强节点
            dom_tree_node = EnhancedDOMTreeNode(
                node_id=node_id,
                backend_node_id=backend_node_id,
                node_type=NodeType(node.get("nodeType", 1)),
                node_name=node.get("nodeName", ""),
                node_value=node.get("nodeValue", ""),
                attributes=attributes,
                is_scrollable=node.get("isScrollable", False),
                is_visible=None,  # 稍后计算
                absolute_position=absolute_position,
                target_id=str(self.target_info.target_id),
                frame_id=node.get("frameId"),
                session_id=str(self.session_id),
                content_document=None,
                shadow_root_type=shadow_root_type,
                shadow_roots=None,
                parent_node=None,
                children_nodes=None,
                ax_node=enhanced_ax_node,
                snapshot_node=snapshot_data,
            )
            
            # 保存到查找表
            enhanced_dom_tree_node_lookup[node_id] = dom_tree_node
            
            # 设置父节�?
            if "parentId" in node and node["parentId"]:
                parent_id = node["parentId"]
                if parent_id in enhanced_dom_tree_node_lookup:
                    dom_tree_node.parent_node = enhanced_dom_tree_node_lookup[parent_id]
            
            # 更新 HTML frames 列表
            updated_html_frames = html_frames.copy()
            if (
                node.get("nodeType") == NodeType.ELEMENT_NODE.value
                and node.get("nodeName") == "HTML"
                and node.get("frameId") is not None
            ):
                updated_html_frames.append(dom_tree_node)
                
                # 调整帧偏移（考虑滚动�?
                if snapshot_data and snapshot_data.scrollRects:
                    total_frame_offset.x -= snapshot_data.scrollRects.x
                    total_frame_offset.y -= snapshot_data.scrollRects.y
            
            # 处理 iframe 偏移
            if (
                node.get("nodeName", "").upper() in ("IFRAME", "FRAME")
                and snapshot_data
                and snapshot_data.bounds
            ):
                updated_html_frames.append(dom_tree_node)
                total_frame_offset.x += snapshot_data.bounds.x
                total_frame_offset.y += snapshot_data.bounds.y
            
            # 递归处理 content_document
            if "contentDocument" in node and node["contentDocument"]:
                dom_tree_node.content_document = await _construct_enhanced_node(
                    node["contentDocument"],
                    updated_html_frames,
                    total_frame_offset,
                )
                dom_tree_node.content_document.parent_node = dom_tree_node
            
            # 递归处理 shadow_roots
            if "shadowRoots" in node and node["shadowRoots"]:
                dom_tree_node.shadow_roots = []
                for shadow_root in node["shadowRoots"]:
                    shadow_root_node = await _construct_enhanced_node(
                        shadow_root,
                        updated_html_frames,
                        total_frame_offset,
                    )
                    shadow_root_node.parent_node = dom_tree_node
                    dom_tree_node.shadow_roots.append(shadow_root_node)
            
            # 递归处理 children
            if "children" in node and node["children"]:
                dom_tree_node.children_nodes = []
                
                # 构建 shadow root node IDs 集合（避免重复）
                shadow_root_node_ids = set()
                if "shadowRoots" in node and node["shadowRoots"]:
                    for shadow_root in node["shadowRoots"]:
                        shadow_root_node_ids.add(shadow_root.get("nodeId"))
                
                for child in node["children"]:
                    # 跳过 shadow roots（已�?shadow_roots 列表中）
                    if child.get("nodeId") in shadow_root_node_ids:
                        continue
                    
                    child_node = await _construct_enhanced_node(
                        child,
                        updated_html_frames,
                        total_frame_offset,
                    )
                    dom_tree_node.children_nodes.append(child_node)
            
            # 计算可见性（简化版本：检查基本样式）
            dom_tree_node.is_visible = self._is_node_visible(dom_tree_node)
            
            return dom_tree_node
        
        # 开始递归构建
        root_node = await _construct_enhanced_node(
            dom_root,
            html_frames,
            total_frame_offset,
        )
        
        elapsed = time.time() - start_time
        logger.info(f"�?完整 DOM 树构建完�? {len(enhanced_dom_tree_node_lookup)} 个节�? 耗时 {elapsed*1000:.1f}ms")
        
        return root_node
    
    def _is_node_visible(self, node: EnhancedDOMTreeNode) -> bool:
        """
        检查节点是否可见（简化版本）
        
        Args:
            node: DOM 节点
            
        Returns:
            是否可见
        """
        if not node.snapshot_node:
            return True  # �?snapshot 数据，假设可�?
        
        # 检查计算样�?
        if node.snapshot_node.computed_styles:
            styles = node.snapshot_node.computed_styles
            
            display = styles.get("display", "").lower()
            visibility = styles.get("visibility", "").lower()
            opacity = styles.get("opacity", "1")
            
            if display == "none" or visibility == "hidden":
                return False
            
            try:
                if float(opacity) <= 0:
                    return False
            except (ValueError, TypeError):
                pass
        
        # 检查边界框
        if node.snapshot_node.bounds:
            bounds = node.snapshot_node.bounds
            if bounds.width <= 0 or bounds.height <= 0:
                return False
        
        return True
    
    
    async def _wait_for_load(self, timeout: float = 30.0):
        """等待页面加载完成"""
        try:
            result = await asyncio.wait_for(
                self.evaluate("document.readyState"),
                timeout=timeout
            )
            # 简化实现：只检查一�?
            await asyncio.sleep(0.5)  # 给一点时间让页面稳定
        except asyncio.TimeoutError:
            logger.warning("等待页面加载超时")
    
    async def _wait_for_dom_content_loaded(self, timeout: float = 30.0):
        """等待 DOM 内容加载"""
        await self._wait_for_load(timeout)
    
    async def _wait_for_network_idle(self, timeout: float = 30.0):
        """等待网络空闲"""
        # 简化实现：等待一段时�?
        await asyncio.sleep(1.0)
    
    async def _update_page_info(self):
        """更新页面信息"""
        try:
            title = await self.get_page_title()
            url = await self.get_page_url()
            
            self.target_info.title = title
            self.target_info.url = url
            
        except Exception as e:
            logger.debug(f"更新页面信息失败: {e}")
    
    @property
    def page_info(self) -> PageInfo:
        """获取页面信息"""
        if self._page_info is None:
            self._page_info = PageInfo(
                target_info=self.target_info,
                session_id=str(self.session_id) if self.session_id else None,
            )
        return self._page_info
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.disconnect()

