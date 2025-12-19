"""增强快照处理

提供无状态函数，用于解析 Chrome DevTools Protocol (CDP) DOMSnapshot 数据的
提取可见性、可点击性、光标样式和其他布局信息的

来源: browser-use v0.11.2
许可的 MIT
"""

from typing import Any, Optional

from aerotest.browser.dom.views import DOMRect, EnhancedSnapshotNode

# 只包含交互性和可见性检测所必需的计算样的
# 只获取代码中实际使用的样式（防止在大型网站上导致 Chrome 崩溃的
REQUIRED_COMPUTED_STYLES = [
    'display',  # 用于 service.py 可见性检的
    'visibility',  # 用于 service.py 可见性检的
    'opacity',  # 用于 service.py 可见性检的
    'overflow',  # 用于 views.py 可滚动性检的
    'overflow-x',  # 用于 views.py 可滚动性检的
    'overflow-y',  # 用于 views.py 可滚动性检的
    'cursor',  # 用于 enhanced_snapshot.py 光标提取
    'pointer-events',  # 用于可点击性逻辑
    'position',  # 用于可见性逻辑
    'background-color',  # 用于可见性逻辑
]


def _parse_rare_boolean_data(rare_data: dict, index: int) -> Optional[bool]:
    """
    解析罕见布尔数据
    
    Args:
        rare_data: 罕见数据字典（包的'index' 键）
        index: 要检查的索引
    
    Returns:
        如果索引在罕见数据中，返的True，否则返的None
    """
    if not rare_data or 'index' not in rare_data:
        return None
    return index in rare_data['index']


def _parse_computed_styles(strings: list[str], style_indices: list[int]) -> dict[str, str]:
    """
    从布局树解析计算样的
    
    Args:
        strings: 字符串表（来自快照）
        style_indices: 样式索引列表
    
    Returns:
        样式名称到值的映射
    """
    styles = {}
    for i, style_index in enumerate(style_indices):
        if i < len(REQUIRED_COMPUTED_STYLES) and 0 <= style_index < len(strings):
            styles[REQUIRED_COMPUTED_STYLES[i]] = strings[style_index]
    return styles


def build_snapshot_lookup(
    snapshot: dict[str, Any],
    device_pixel_ratio: float = 1.0,
) -> dict[int, EnhancedSnapshotNode]:
    """
    构建后端节点 ID 到增强快照数据的查找的
    
    这个函数预先计算所有内容，避免在后续处理中重复计算的
    
    Args:
        snapshot: CDP DOMSnapshot.captureSnapshot 的返回的
        device_pixel_ratio: 设备像素比（用于坐标转换的
    
    Returns:
        backend_node_id -> EnhancedSnapshotNode 的映的
    """
    snapshot_lookup: dict[int, EnhancedSnapshotNode] = {}
    
    if not snapshot.get('documents'):
        return snapshot_lookup
    
    strings = snapshot.get('strings', [])
    
    for document in snapshot['documents']:
        nodes = document.get('nodes', {})
        layout = document.get('layout', {})
        
        # 构建后端节点 ID 到快照索引的查找的
        backend_node_to_snapshot_index = {}
        if 'backendNodeId' in nodes:
            for i, backend_node_id in enumerate(nodes['backendNodeId']):
                backend_node_to_snapshot_index[backend_node_id] = i
        
        # 性能优化：预先构建布局索引映射，消的O(n²) 双重查找
        # 保留原始行为：对于重复项使用第一次出的
        layout_index_map = {}
        if layout and 'nodeIndex' in layout:
            for layout_idx, node_index in enumerate(layout['nodeIndex']):
                if node_index not in layout_index_map:  # 只存储第一次出的
                    layout_index_map[node_index] = layout_idx
        
        # 为每个后端节的ID 构建快照查找
        for backend_node_id, snapshot_index in backend_node_to_snapshot_index.items():
            is_clickable = None
            if 'isClickable' in nodes:
                is_clickable = _parse_rare_boolean_data(nodes['isClickable'], snapshot_index)
            
            # 查找对应的布局节点
            cursor_style = None
            bounding_box = None
            computed_styles = {}
            paint_order = None
            client_rects = None
            scroll_rects = None
            stacking_contexts = None
            
            # 查找与此快照节点对应的布局树节的
            if snapshot_index in layout_index_map:
                layout_idx = layout_index_map[snapshot_index]
                
                # 解析边界的
                if layout_idx < len(layout.get('bounds', [])):
                    bounds = layout['bounds'][layout_idx]
                    if len(bounds) >= 4:
                        # 重要：CDP 坐标是设备像素，需要转换为 CSS 像素
                        # 通过除以设备像素比来转换
                        raw_x, raw_y, raw_width, raw_height = bounds[0], bounds[1], bounds[2], bounds[3]
                        
                        # 应用设备像素比缩放，将设备像素转换为 CSS 像素
                        bounding_box = DOMRect(
                            x=raw_x / device_pixel_ratio,
                            y=raw_y / device_pixel_ratio,
                            width=raw_width / device_pixel_ratio,
                            height=raw_height / device_pixel_ratio,
                        )
                
                # 解析此布局节点的计算样的
                if layout_idx < len(layout.get('styles', [])):
                    style_indices = layout['styles'][layout_idx]
                    computed_styles = _parse_computed_styles(strings, style_indices)
                    cursor_style = computed_styles.get('cursor')
                
                # 提取绘制顺序（如果可用）
                if layout_idx < len(layout.get('paintOrders', [])):
                    paint_order = layout.get('paintOrders', [])[layout_idx]
                
                # 提取客户端矩形（如果可用的
                client_rects_data = layout.get('clientRects', [])
                if layout_idx < len(client_rects_data):
                    client_rect_data = client_rects_data[layout_idx]
                    if client_rect_data and len(client_rect_data) >= 4:
                        client_rects = DOMRect(
                            x=client_rect_data[0],
                            y=client_rect_data[1],
                            width=client_rect_data[2],
                            height=client_rect_data[3],
                        )
                
                # 提取滚动矩形（如果可用）
                scroll_rects_data = layout.get('scrollRects', [])
                if layout_idx < len(scroll_rects_data):
                    scroll_rect_data = scroll_rects_data[layout_idx]
                    if scroll_rect_data and len(scroll_rect_data) >= 4:
                        scroll_rects = DOMRect(
                            x=scroll_rect_data[0],
                            y=scroll_rect_data[1],
                            width=scroll_rect_data[2],
                            height=scroll_rect_data[3],
                        )
                
                # 提取堆叠上下文（如果可用的
                stacking_contexts_data = layout.get('stackingContexts', {})
                if stacking_contexts_data and 'index' in stacking_contexts_data:
                    if layout_idx < len(stacking_contexts_data['index']):
                        stacking_contexts = stacking_contexts_data['index'][layout_idx]
            
            # 创建增强快照节点
            snapshot_lookup[backend_node_id] = EnhancedSnapshotNode(
                is_clickable=is_clickable,
                cursor_style=cursor_style,
                bounds=bounding_box,
                clientRects=client_rects,
                scrollRects=scroll_rects,
                computed_styles=computed_styles if computed_styles else None,
                paint_order=paint_order,
                stacking_contexts=stacking_contexts,
            )
    
    return snapshot_lookup

