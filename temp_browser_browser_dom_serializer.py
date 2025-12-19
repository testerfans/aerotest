"""DOM 树序列化�?

将增强的 DOM 树序列化为字符串格式�?LLM 使用

来源: browser-use v0.11.2  
改�? 精简版本，保留核心序列化逻辑
"""

import time
from typing import Any

from aerotest.browser.dom.clickable_detector import ClickableElementDetector
from aerotest.browser.dom.paint_order import PaintOrderRemover
from aerotest.browser.dom.utils import cap_text_length
from aerotest.browser.dom.views import (
    DEFAULT_INCLUDE_ATTRIBUTES,
    DOMRect,
    DOMSelectorMap,
    EnhancedDOMTreeNode,
    NodeType,
    PropagatingBounds,
    SerializedDOMState,
    SimplifiedNode,
)

# 禁用的元�?
DISABLED_ELEMENTS = {'style', 'script', 'head', 'meta', 'link', 'title'}

# SVG 子元素跳�?
SVG_ELEMENTS = {
    'path', 'rect', 'g', 'circle', 'ellipse', 'line', 'polyline',
    'polygon', 'use', 'defs', 'clipPath', 'mask', 'pattern',
    'image', 'text', 'tspan',
}


class DOMTreeSerializer:
    """DOM 树序列化�?""

    # 传播边界的元素配�?
    PROPAGATING_ELEMENTS = [
        {'tag': 'a', 'role': None},
        {'tag': 'button', 'role': None},
        {'tag': 'div', 'role': 'button'},
        {'tag': 'div', 'role': 'combobox'},
        {'tag': 'span', 'role': 'button'},
        {'tag': 'span', 'role': 'combobox'},
        {'tag': 'input', 'role': 'combobox'},
    ]
    DEFAULT_CONTAINMENT_THRESHOLD = 0.99

    def __init__(
        self,
        root_node: EnhancedDOMTreeNode,
        previous_cached_state: SerializedDOMState | None = None,
        enable_bbox_filtering: bool = True,
        containment_threshold: float | None = None,
        paint_order_filtering: bool = True,
        session_id: str | None = None,
    ):
        self.root_node = root_node
        self._interactive_counter = 1
        self._selector_map: DOMSelectorMap = {}
        self._previous_cached_selector_map = (
            previous_cached_state.selector_map if previous_cached_state else None
        )
        self.timing_info: dict[str, float] = {}
        self._clickable_cache: dict[int, bool] = {}
        self.enable_bbox_filtering = enable_bbox_filtering
        self.containment_threshold = containment_threshold or self.DEFAULT_CONTAINMENT_THRESHOLD
        self.paint_order_filtering = paint_order_filtering
        self.session_id = session_id

    def serialize_accessible_elements(self) -> tuple[SerializedDOMState, dict[str, float]]:
        """序列化可访问元素"""
        start_total = time.time()

        # 重置状�?
        self._interactive_counter = 1
        self._selector_map = {}
        self._clickable_cache = {}

        # 步骤 1: 创建简化树
        start_step1 = time.time()
        simplified_tree = self._create_simplified_tree(self.root_node)
        self.timing_info['create_simplified_tree'] = time.time() - start_step1

        # 步骤 2: 移除基于绘制顺序的元�?
        start_step2 = time.time()
        if self.paint_order_filtering and simplified_tree:
            PaintOrderRemover(simplified_tree).calculate_paint_order()
        self.timing_info['calculate_paint_order'] = time.time() - start_step2

        # 步骤 3: 优化�?
        start_step3 = time.time()
        optimized_tree = self._optimize_tree(simplified_tree)
        self.timing_info['optimize_tree'] = time.time() - start_step3

        # 步骤 4: 应用边界框过�?
        if self.enable_bbox_filtering and optimized_tree:
            start_step4 = time.time()
            filtered_tree = self._apply_bounding_box_filtering(optimized_tree)
            self.timing_info['bbox_filtering'] = time.time() - start_step4
        else:
            filtered_tree = optimized_tree

        # 步骤 5: 分配交互索引
        start_step5 = time.time()
        self._assign_interactive_indices(filtered_tree)
        self.timing_info['assign_interactive_indices'] = time.time() - start_step5

        self.timing_info['serialize_accessible_elements_total'] = time.time() - start_total

        return SerializedDOMState(_root=filtered_tree, selector_map=self._selector_map), self.timing_info

    def _is_interactive_cached(self, node: EnhancedDOMTreeNode) -> bool:
        """缓存版本的可点击元素检�?""
        if node.node_id not in self._clickable_cache:
            start_time = time.time()
            result = ClickableElementDetector.is_interactive(node)
            
            if 'clickable_detection_time' not in self.timing_info:
                self.timing_info['clickable_detection_time'] = 0
            self.timing_info['clickable_detection_time'] += time.time() - start_time
            
            self._clickable_cache[node.node_id] = result

        return self._clickable_cache[node.node_id]

    def _create_simplified_tree(
        self, node: EnhancedDOMTreeNode, depth: int = 0
    ) -> SimplifiedNode | None:
        """创建简化树"""
        if node.node_type == NodeType.DOCUMENT_NODE:
            for child in node.children_and_shadow_roots:
                simplified_child = self._create_simplified_tree(child, depth + 1)
                if simplified_child:
                    return simplified_child
            return None

        if node.node_type == NodeType.DOCUMENT_FRAGMENT_NODE:
            # Shadow DOM 处理
            simplified = SimplifiedNode(original_node=node, children=[])
            for child in node.children_and_shadow_roots:
                simplified_child = self._create_simplified_tree(child, depth + 1)
                if simplified_child:
                    simplified.children.append(simplified_child)
            return simplified if simplified.children else SimplifiedNode(original_node=node, children=[])

        elif node.node_type == NodeType.ELEMENT_NODE:
            # 跳过非内容元�?
            if node.node_name.lower() in DISABLED_ELEMENTS:
                return None

            # 跳过 SVG 子元�?
            if node.node_name.lower() in SVG_ELEMENTS:
                return None

            # 检查排除属�?
            attributes = node.attributes or {}
            exclude_attr = None
            if self.session_id:
                session_specific_attr = f'data-browser-use-exclude-{self.session_id}'
                exclude_attr = attributes.get(session_specific_attr)
            if not exclude_attr:
                exclude_attr = attributes.get('data-browser-use-exclude')
            if isinstance(exclude_attr, str) and exclude_attr.lower() == 'true':
                return None

            # IFRAME 处理
            if node.node_name in ('IFRAME', 'FRAME'):
                if node.content_document:
                    simplified = SimplifiedNode(original_node=node, children=[])
                    for child in node.content_document.children_nodes or []:
                        simplified_child = self._create_simplified_tree(child, depth + 1)
                        if simplified_child is not None:
                            simplified.children.append(simplified_child)
                    return simplified

            is_visible = node.is_visible
            is_scrollable = node.is_actually_scrollable
            has_shadow_content = bool(node.children_and_shadow_roots)
            is_shadow_host = any(
                child.node_type == NodeType.DOCUMENT_FRAGMENT_NODE 
                for child in node.children_and_shadow_roots
            )

            # 文件输入特殊处理
            is_file_input = (
                node.tag_name and node.tag_name.lower() == 'input'
                and node.attributes and node.attributes.get('type') == 'file'
            )
            if not is_visible and is_file_input:
                is_visible = True

            # 包含可见、可滚动、有子节点或�?shadow host 的元�?
            if is_visible or is_scrollable or has_shadow_content or is_shadow_host:
                simplified = SimplifiedNode(
                    original_node=node, children=[], is_shadow_host=is_shadow_host
                )

                # 处理所有子节点包括 shadow roots
                for child in node.children_and_shadow_roots:
                    simplified_child = self._create_simplified_tree(child, depth + 1)
                    if simplified_child:
                        simplified.children.append(simplified_child)

                if is_shadow_host and simplified.children:
                    return simplified

                if is_visible or is_scrollable or simplified.children:
                    return simplified

        elif node.node_type == NodeType.TEXT_NODE:
            # 包含有意义的文本节点
            is_visible = node.snapshot_node and node.is_visible
            if is_visible and node.node_value and node.node_value.strip() and len(node.node_value.strip()) > 1:
                return SimplifiedNode(original_node=node, children=[])

        return None

    def _optimize_tree(self, node: SimplifiedNode | None) -> SimplifiedNode | None:
        """优化树结�?""
        if not node:
            return None

        # 处理子节�?
        optimized_children = []
        for child in node.children:
            optimized_child = self._optimize_tree(child)
            if optimized_child:
                optimized_children.append(optimized_child)

        node.children = optimized_children

        # 保留有意义的节点
        is_visible = node.original_node.snapshot_node and node.original_node.is_visible
        is_file_input = (
            node.original_node.tag_name
            and node.original_node.tag_name.lower() == 'input'
            and node.original_node.attributes
            and node.original_node.attributes.get('type') == 'file'
        )

        if (
            is_visible
            or node.original_node.is_actually_scrollable
            or node.original_node.node_type == NodeType.TEXT_NODE
            or node.children
            or is_file_input
        ):
            return node

        return None

    def _apply_bounding_box_filtering(self, node: SimplifiedNode | None) -> SimplifiedNode | None:
        """应用边界框过�?""
        if not node:
            return None

        self._filter_tree_recursive(node, active_bounds=None, depth=0)
        return node

    def _filter_tree_recursive(
        self, node: SimplifiedNode, active_bounds: PropagatingBounds | None = None, depth: int = 0
    ) -> None:
        """递归过滤�?""
        # 检查是否应该被激活边界排�?
        if active_bounds and self._should_exclude_child(node, active_bounds):
            node.excluded_by_parent = True

        # 检查这个节点是否开始新的传�?
        new_bounds = None
        tag = node.original_node.tag_name.lower()
        role = node.original_node.attributes.get('role') if node.original_node.attributes else None
        
        if self._is_propagating_element({'tag': tag, 'role': role}):
            if node.original_node.snapshot_node and node.original_node.snapshot_node.bounds:
                new_bounds = PropagatingBounds(
                    tag=tag,
                    bounds=node.original_node.snapshot_node.bounds,
                    node_id=node.original_node.node_id,
                    depth=depth,
                )

        # 传播到所有子节点
        propagate_bounds = new_bounds if new_bounds else active_bounds

        for child in node.children:
            self._filter_tree_recursive(child, propagate_bounds, depth + 1)

    def _should_exclude_child(self, node: SimplifiedNode, active_bounds: PropagatingBounds) -> bool:
        """判断是否应该排除子节�?""
        # 永远不排除文本节�?
        if node.original_node.node_type == NodeType.TEXT_NODE:
            return False

        # 获取子节点边�?
        if not node.original_node.snapshot_node or not node.original_node.snapshot_node.bounds:
            return False

        child_bounds = node.original_node.snapshot_node.bounds

        # 检查包含关�?
        if not self._is_contained(child_bounds, active_bounds.bounds, self.containment_threshold):
            return False

        # 异常规则
        child_tag = node.original_node.tag_name.lower()
        child_role = node.original_node.attributes.get('role') if node.original_node.attributes else None

        # 不排除表单元�?
        if child_tag in ['input', 'select', 'textarea', 'label']:
            return False

        # 保留传播元素
        if self._is_propagating_element({'tag': child_tag, 'role': child_role}):
            return False

        # 保留有明�?onclick 处理器的元素
        if node.original_node.attributes and 'onclick' in node.original_node.attributes:
            return False

        return True

    def _is_contained(self, child: DOMRect, parent: DOMRect, threshold: float) -> bool:
        """检查子元素是否被父元素包含"""
        x_overlap = max(0, min(child.x + child.width, parent.x + parent.width) - max(child.x, parent.x))
        y_overlap = max(0, min(child.y + child.height, parent.y + parent.height) - max(child.y, parent.y))

        intersection_area = x_overlap * y_overlap
        child_area = child.width * child.height

        if child_area == 0:
            return False

        containment_ratio = intersection_area / child_area
        return containment_ratio >= threshold

    def _is_propagating_element(self, attributes: dict[str, str | None]) -> bool:
        """检查元素是否应该传播边�?""
        for pattern in self.PROPAGATING_ELEMENTS:
            check = [
                pattern.get(key) is None or pattern.get(key) == attributes.get(key)
                for key in ['tag', 'role']
            ]
            if all(check):
                return True
        return False

    def _assign_interactive_indices(self, node: SimplifiedNode | None) -> None:
        """分配交互索引"""
        if not node:
            return

        if not node.excluded_by_parent and not node.ignored_by_paint_order:
            is_interactive = self._is_interactive_cached(node.original_node)
            is_visible = node.original_node.snapshot_node and node.original_node.is_visible
            is_scrollable = node.original_node.is_actually_scrollable

            is_file_input = (
                node.original_node.tag_name
                and node.original_node.tag_name.lower() == 'input'
                and node.original_node.attributes
                and node.original_node.attributes.get('type') == 'file'
            )

            should_make_interactive = False
            if is_scrollable:
                # 只有没有交互子元素的可滚动容器才标记为交�?
                if not self._has_interactive_descendants(node):
                    should_make_interactive = True
            elif is_interactive and (is_visible or is_file_input):
                should_make_interactive = True

            if should_make_interactive:
                node.is_interactive = True
                self._selector_map[node.original_node.backend_node_id] = node.original_node
                self._interactive_counter += 1

                if self._previous_cached_selector_map:
                    previous_ids = {n.backend_node_id for n in self._previous_cached_selector_map.values()}
                    if node.original_node.backend_node_id not in previous_ids:
                        node.is_new = True

        # 处理子节�?
        for child in node.children:
            self._assign_interactive_indices(child)

    def _has_interactive_descendants(self, node: SimplifiedNode) -> bool:
        """检查节点是否有交互后代"""
        for child in node.children:
            if self._is_interactive_cached(child.original_node):
                return True
            if self._has_interactive_descendants(child):
                return True
        return False

    @staticmethod
    def serialize_tree(node: SimplifiedNode | None, include_attributes: list[str], depth: int = 0) -> str:
        """将优化后的树序列化为字符串格�?""
        if not node:
            return ''

        # 跳过被排除的节点，但处理其子节点
        if hasattr(node, 'excluded_by_parent') and node.excluded_by_parent:
            formatted_text = []
            for child in node.children:
                child_text = DOMTreeSerializer.serialize_tree(child, include_attributes, depth)
                if child_text:
                    formatted_text.append(child_text)
            return '\n'.join(formatted_text)

        formatted_text = []
        depth_str = depth * '\t'
        next_depth = depth

        if node.original_node.node_type == NodeType.ELEMENT_NODE:
            if not node.should_display:
                for child in node.children:
                    child_text = DOMTreeSerializer.serialize_tree(child, include_attributes, depth)
                    if child_text:
                        formatted_text.append(child_text)
                return '\n'.join(formatted_text)

            # SVG 特殊处理
            if node.original_node.tag_name.lower() == 'svg':
                line = f'{depth_str}'
                if node.is_interactive:
                    new_prefix = '*' if node.is_new else ''
                    line += f'{new_prefix}[{node.original_node.backend_node_id}]'
                line += '<svg'
                attrs = DOMTreeSerializer._build_attributes_string(node.original_node, include_attributes, '')
                if attrs:
                    line += f' {attrs}'
                line += ' /> <!-- SVG content collapsed -->'
                formatted_text.append(line)
                return '\n'.join(formatted_text)

            # 添加可点击、可滚动�?iframe 元素
            is_any_scrollable = node.original_node.is_actually_scrollable or node.original_node.is_scrollable
            should_show_scroll = node.original_node.should_show_scroll_info
            
            if (
                node.is_interactive
                or is_any_scrollable
                or node.original_node.tag_name.upper() in ('IFRAME', 'FRAME')
            ):
                next_depth += 1

                text_content = ''
                attrs = DOMTreeSerializer._build_attributes_string(
                    node.original_node, include_attributes, text_content
                )

                if should_show_scroll and not node.is_interactive:
                    line = f'{depth_str}|SCROLL|<{node.original_node.tag_name}'
                elif node.is_interactive:
                    new_prefix = '*' if node.is_new else ''
                    scroll_prefix = '|SCROLL[' if should_show_scroll else '['
                    line = f'{depth_str}{new_prefix}{scroll_prefix}{node.original_node.backend_node_id}]<{node.original_node.tag_name}'
                elif node.original_node.tag_name.upper() == 'IFRAME':
                    line = f'{depth_str}|IFRAME|<{node.original_node.tag_name}'
                else:
                    line = f'{depth_str}<{node.original_node.tag_name}'

                if attrs:
                    line += f' {attrs}'
                line += ' />'

                if should_show_scroll:
                    scroll_info_text = node.original_node.get_scroll_info_text()
                    if scroll_info_text:
                        line += f' ({scroll_info_text})'

                formatted_text.append(line)

        elif node.original_node.node_type == NodeType.TEXT_NODE:
            is_visible = node.original_node.snapshot_node and node.original_node.is_visible
            if (
                is_visible
                and node.original_node.node_value
                and node.original_node.node_value.strip()
                and len(node.original_node.node_value.strip()) > 1
            ):
                clean_text = node.original_node.node_value.strip()
                formatted_text.append(f'{depth_str}{clean_text}')

        # 处理子节�?
        for child in node.children:
            child_text = DOMTreeSerializer.serialize_tree(child, include_attributes, next_depth)
            if child_text:
                formatted_text.append(child_text)

        return '\n'.join(formatted_text)

    @staticmethod
    def _build_attributes_string(node: EnhancedDOMTreeNode, include_attributes: list[str], text: str) -> str:
        """构建属性字符串"""
        attributes_to_include = {}

        # 包含 HTML 属�?
        if node.attributes:
            attributes_to_include.update({
                key: str(value).strip()
                for key, value in node.attributes.items()
                if key in include_attributes and str(value).strip() != ''
            })

        # 包含可访问性属�?
        if node.ax_node and node.ax_node.properties:
            for prop in node.ax_node.properties:
                try:
                    if prop.name in include_attributes and prop.value is not None:
                        if isinstance(prop.value, bool):
                            attributes_to_include[prop.name] = str(prop.value).lower()
                        else:
                            prop_value_str = str(prop.value).strip()
                            if prop_value_str:
                                attributes_to_include[prop.name] = prop_value_str
                except (AttributeError, ValueError):
                    continue

        if not attributes_to_include:
            return ''

        # 格式化属�?
        formatted_attrs = []
        for key, value in attributes_to_include.items():
            capped_value = cap_text_length(value, 100)
            if not capped_value:
                formatted_attrs.append(f"{key}=''")
            else:
                formatted_attrs.append(f'{key}={capped_value}')

        return ' '.join(formatted_attrs)

