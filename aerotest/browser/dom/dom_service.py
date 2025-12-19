"""DOM 服务

提供高层 DOM 操作接口，封装底层的 DOM 序列化和处理逻辑

来源: browser-use v0.11.2
改动: 简化版本，暂时移除 CDP 集成（Week 3 完成）
"""

import logging
from typing import Any, Optional

from aerotest.browser.dom.serializer import DOMTreeSerializer
from aerotest.browser.dom.views import (
    DEFAULT_INCLUDE_ATTRIBUTES,
    DOMSelectorMap,
    EnhancedDOMTreeNode,
    NodeType,
    SerializedDOMState,
)
from aerotest.utils import get_logger

logger = get_logger("aerotest.dom.service")


class DomService:
    """
    DOM 服务，用于获取 DOM 树和其他 DOM 相关信息
    
    这是一个高层接口，封装了 DOM 序列化和处理的复杂性。
    
    Note: 完整的 CDP 集成将在 Week 3 实现
    """

    def __init__(
        self,
        paint_order_filtering: bool = True,
        bbox_filtering: bool = True,
        containment_threshold: float = 0.99,
        logger: Optional[logging.Logger] = None,
    ):
        """
        初始化 DOM 服务
        
        Args:
            paint_order_filtering: 是否启用绘制顺序过滤
            bbox_filtering: 是否启用边界框过滤
            containment_threshold: 包含阈值（0.0-1.0）
            logger: 可选的日志记录器
        """
        self.paint_order_filtering = paint_order_filtering
        self.bbox_filtering = bbox_filtering
        self.containment_threshold = containment_threshold
        self.logger = logger or get_logger("aerotest.dom.service")

    def serialize_dom_tree(
        self,
        root_node: EnhancedDOMTreeNode,
        previous_state: Optional[SerializedDOMState] = None,
        include_attributes: Optional[list[str]] = None,
        session_id: Optional[str] = None,
    ) -> tuple[SerializedDOMState, dict[str, float]]:
        """
        序列化 DOM 树为可访问元素
        
        Args:
            root_node: DOM 树的根节点
            previous_state: 可选的之前的状态（用于检测新元素）
            include_attributes: 要包含的属性列表
            session_id: 可选的会话 ID
        
        Returns:
            (SerializedDOMState, timing_info) 元组
        """
        try:
            self.logger.debug("开始序列化 DOM 树")
            
            # 创建序列化器
            serializer = DOMTreeSerializer(
                root_node=root_node,
                previous_cached_state=previous_state,
                enable_bbox_filtering=self.bbox_filtering,
                containment_threshold=self.containment_threshold,
                paint_order_filtering=self.paint_order_filtering,
                session_id=session_id,
            )
            
            # 执行序列化
            state, timing = serializer.serialize_accessible_elements()
            
            self.logger.debug(
                f"DOM 序列化完成: {len(state.selector_map)} 个可交互元素, "
                f"耗时 {timing.get('serialize_accessible_elements_total', 0)*1000:.1f}ms"
            )
            
            return state, timing
            
        except Exception as e:
            self.logger.error(f"DOM 序列化失败: {e}")
            raise

    def get_llm_representation(
        self,
        state: SerializedDOMState,
        include_attributes: Optional[list[str]] = None,
    ) -> str:
        """
        获取适合 LLM 使用的 DOM 表示
        
        Args:
            state: 序列化的 DOM 状态
            include_attributes: 要包含的属性列表
        
        Returns:
            格式化的 DOM 字符串
        """
        try:
            attributes = include_attributes or DEFAULT_INCLUDE_ATTRIBUTES
            return state.llm_representation(attributes)
        except Exception as e:
            self.logger.error(f"获取 LLM 表示失败: {e}")
            raise

    def find_element_by_backend_node_id(
        self,
        state: SerializedDOMState,
        backend_node_id: int,
    ) -> Optional[EnhancedDOMTreeNode]:
        """
        通过 backend_node_id 查找元素
        
        Args:
            state: 序列化的 DOM 状态
            backend_node_id: 后端节点 ID
        
        Returns:
            找到的元素或 None
        """
        try:
            return state.selector_map.get(backend_node_id)
        except Exception as e:
            self.logger.error(f"查找元素失败: {e}")
            return None

    def get_clickable_elements(
        self,
        state: SerializedDOMState,
    ) -> list[EnhancedDOMTreeNode]:
        """
        获取所有可点击元素
        
        Args:
            state: 序列化的 DOM 状态
        
        Returns:
            可点击元素列表
        """
        try:
            return list(state.selector_map.values())
        except Exception as e:
            self.logger.error(f"获取可点击元素失败: {e}")
            return []

    def get_clickable_elements_summary(
        self,
        state: SerializedDOMState,
    ) -> list[dict[str, Any]]:
        """
        获取可点击元素的摘要信息
        
        Args:
            state: 序列化的 DOM 状态
        
        Returns:
            元素摘要列表
        """
        try:
            summaries = []
            for backend_node_id, element in state.selector_map.items():
                summary = {
                    "backend_node_id": backend_node_id,
                    "tag_name": element.tag_name,
                    "attributes": element.attributes,
                    "xpath": element.xpath,
                    "text": element.get_all_children_text()[:100],  # 限制文本长度
                    "is_visible": element.is_visible,
                    "is_scrollable": element.is_actually_scrollable,
                }
                
                # 添加位置信息
                if element.snapshot_node and element.snapshot_node.bounds:
                    summary["bounds"] = {
                        "x": element.snapshot_node.bounds.x,
                        "y": element.snapshot_node.bounds.y,
                        "width": element.snapshot_node.bounds.width,
                        "height": element.snapshot_node.bounds.height,
                    }
                
                summaries.append(summary)
            
            return summaries
            
        except Exception as e:
            self.logger.error(f"获取元素摘要失败: {e}")
            return []

    @staticmethod
    def is_element_visible(
        node: EnhancedDOMTreeNode,
        check_parents: bool = False,
    ) -> bool:
        """
        检查元素是否可见
        
        Args:
            node: DOM 节点
            check_parents: 是否检查父节点（简化版本暂不实现）
        
        Returns:
            元素是否可见
        """
        if not node.snapshot_node:
            return False

        # 检查基本可见性
        if node.is_visible is False:
            return False

        # 检查计算样式
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

        return True

    @staticmethod
    def find_elements_by_text(
        state: SerializedDOMState,
        text: str,
        exact_match: bool = False,
    ) -> list[EnhancedDOMTreeNode]:
        """
        通过文本内容查找元素
        
        Args:
            state: 序列化的 DOM 状态
            text: 要搜索的文本
            exact_match: 是否精确匹配
        
        Returns:
            匹配的元素列表
        """
        matching_elements = []
        
        for element in state.selector_map.values():
            element_text = element.get_all_children_text()
            
            if exact_match:
                if element_text == text:
                    matching_elements.append(element)
            else:
                if text.lower() in element_text.lower():
                    matching_elements.append(element)
        
        return matching_elements

    @staticmethod
    def find_elements_by_xpath(
        state: SerializedDOMState,
        xpath: str,
    ) -> list[EnhancedDOMTreeNode]:
        """
        通过 XPath 查找元素
        
        Args:
            state: 序列化的 DOM 状态
            xpath: XPath 表达式
        
        Returns:
            匹配的元素列表
        """
        matching_elements = []
        
        for element in state.selector_map.values():
            if element.xpath == xpath:
                matching_elements.append(element)
        
        return matching_elements

    @staticmethod
    def get_element_hierarchy(
        element: EnhancedDOMTreeNode,
    ) -> list[EnhancedDOMTreeNode]:
        """
        获取元素的完整层级结构（从根到元素）
        
        Args:
            element: DOM 元素
        
        Returns:
            从根到元素的路径
        """
        hierarchy = []
        current = element
        
        while current is not None:
            hierarchy.insert(0, current)
            current = current.parent_node
        
        return hierarchy

    def get_statistics(
        self,
        state: SerializedDOMState,
    ) -> dict[str, Any]:
        """
        获取 DOM 统计信息
        
        Args:
            state: 序列化的 DOM 状态
        
        Returns:
            统计信息字典
        """
        stats = {
            "total_interactive_elements": len(state.selector_map),
            "elements_by_tag": {},
            "visible_elements": 0,
            "scrollable_elements": 0,
            "has_iframes": False,
            "has_shadow_dom": False,
        }
        
        for element in state.selector_map.values():
            # 按标签统计
            tag = element.tag_name
            stats["elements_by_tag"][tag] = stats["elements_by_tag"].get(tag, 0) + 1
            
            # 可见元素
            if element.is_visible:
                stats["visible_elements"] += 1
            
            # 可滚动元素
            if element.is_actually_scrollable:
                stats["scrollable_elements"] += 1
            
            # iframe 检测
            if tag.upper() in ("IFRAME", "FRAME"):
                stats["has_iframes"] = True
            
            # Shadow DOM 检测
            if element.shadow_roots:
                stats["has_shadow_dom"] = True
        
        return stats


# 便捷函数

def create_dom_service(
    paint_order_filtering: bool = True,
    bbox_filtering: bool = True,
) -> DomService:
    """
    创建 DOM 服务实例的便捷函数
    
    Args:
        paint_order_filtering: 是否启用绘制顺序过滤
        bbox_filtering: 是否启用边界框过滤
    
    Returns:
        DomService 实例
    """
    return DomService(
        paint_order_filtering=paint_order_filtering,
        bbox_filtering=bbox_filtering,
    )


def serialize_and_get_llm_representation(
    root_node: EnhancedDOMTreeNode,
    paint_order_filtering: bool = True,
    bbox_filtering: bool = True,
) -> tuple[str, SerializedDOMState, dict[str, float]]:
    """
    一步完成序列化和获取 LLM 表示的便捷函数
    
    Args:
        root_node: DOM 树的根节点
        paint_order_filtering: 是否启用绘制顺序过滤
        bbox_filtering: 是否启用边界框过滤
    
    Returns:
        (llm_representation, state, timing_info) 元组
    """
    service = create_dom_service(
        paint_order_filtering=paint_order_filtering,
        bbox_filtering=bbox_filtering,
    )
    
    state, timing = service.serialize_dom_tree(root_node)
    llm_repr = service.get_llm_representation(state)
    
    return llm_repr, state, timing
