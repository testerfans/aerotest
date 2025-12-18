"""DOM 视图数据结构

核心数据类型和类定义，用于表示增强的 DOM �?

来源: browser-use v0.11.2
改�? 移除外部依赖，适配 AeroTest 架构
"""

import hashlib
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from aerotest.browser.dom.cdp_types import AXPropertyName, ShadowRootType, SessionID, TargetID
from aerotest.browser.dom.utils import cap_text_length

# 序列化器默认包含的属�?
DEFAULT_INCLUDE_ATTRIBUTES = [
    'title', 'type', 'checked', 'id', 'name', 'role', 'value', 'placeholder',
    'data-date-format', 'alt', 'aria-label', 'aria-expanded', 'data-state',
    'aria-checked', 'aria-valuemin', 'aria-valuemax', 'aria-valuenow',
    'aria-placeholder', 'pattern', 'min', 'max', 'minlength', 'maxlength',
    'step', 'accept', 'multiple', 'inputmode', 'autocomplete', 'data-mask',
    'data-inputmask', 'data-datepicker', 'format', 'expected_format',
    'contenteditable', 'pseudo', 'disabled', 'invalid', 'required',
    'valuetext', 'level', 'busy', 'live', 'ax_name',
]

# 静态属性（用于哈希计算�?
STATIC_ATTRIBUTES = {
    'class', 'id', 'name', 'type', 'placeholder', 'aria-label', 'title',
    'role', 'data-testid', 'data-test', 'data-cy', 'data-selenium',
    'for', 'required', 'disabled', 'readonly', 'checked', 'selected',
    'multiple', 'accept', 'href', 'target', 'rel', 'aria-describedby',
    'aria-labelledby', 'aria-controls', 'aria-owns', 'tabindex', 'alt',
    'src', 'lang', 'pseudo', 'aria-valuemin', 'aria-valuemax', 'aria-valuenow',
}

# 动态类模式（排除在稳定哈希之外�?
DYNAMIC_CLASS_PATTERNS = frozenset({
    'focus', 'hover', 'active', 'selected', 'disabled', 'animation',
    'transition', 'loading', 'open', 'closed', 'expanded', 'collapsed',
    'visible', 'hidden', 'pressed', 'checked', 'highlighted', 'current',
    'entering', 'leaving',
})


class MatchLevel(Enum):
    """元素匹配严格程度级别"""
    EXACT = 1      # 完整哈希，包含所有属�?
    STABLE = 2     # 过滤动态类的哈�?
    XPATH = 3      # XPath 字符串比�?


def filter_dynamic_classes(class_str: str | None) -> str:
    """
    移除动态状态类，保留语�?识别�?
    
    Args:
        class_str: class 属性字符串
    
    Returns:
        过滤后的类字符串（已排序�?
    """
    if not class_str:
        return ''
    classes = class_str.split()
    stable = [c for c in classes if not any(pattern in c.lower() for pattern in DYNAMIC_CLASS_PATTERNS)]
    return ' '.join(sorted(stable))


class NodeType(int, Enum):
    """DOM 节点类型（基�?DOM 规范�?""
    ELEMENT_NODE = 1
    ATTRIBUTE_NODE = 2
    TEXT_NODE = 3
    CDATA_SECTION_NODE = 4
    ENTITY_REFERENCE_NODE = 5
    ENTITY_NODE = 6
    PROCESSING_INSTRUCTION_NODE = 7
    COMMENT_NODE = 8
    DOCUMENT_NODE = 9
    DOCUMENT_TYPE_NODE = 10
    DOCUMENT_FRAGMENT_NODE = 11
    NOTATION_NODE = 12


@dataclass(slots=True)
class DOMRect:
    """DOM 矩形"""
    x: float
    y: float
    width: float
    height: float

    def to_dict(self) -> dict[str, Any]:
        """转换为字�?""
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
        }

    def __json__(self) -> dict:
        """JSON 序列�?""
        return self.to_dict()


@dataclass(slots=True)
class PropagatingBounds:
    """跟踪从父元素传播的边界以过滤子元�?""
    tag: str              # 开始传播的标签�?a' �?'button'�?
    bounds: DOMRect       # 边界�?
    node_id: int          # 节点 ID（用于调试）
    depth: int            # 树中的深度（用于调试�?


@dataclass(slots=True)
class EnhancedAXProperty:
    """增强的可访问性属�?""
    name: AXPropertyName
    value: str | bool | None


@dataclass(slots=True)
class EnhancedAXNode:
    """增强的可访问性节�?""
    ax_node_id: str
    ignored: bool
    role: str | None
    name: str | None
    description: str | None
    properties: list[EnhancedAXProperty] | None
    child_ids: list[str] | None


@dataclass(slots=True)
class EnhancedSnapshotNode:
    """�?DOMSnapshot 提取的快照数�?""
    is_clickable: bool | None
    cursor_style: str | None
    bounds: DOMRect | None
    """文档坐标（原�?= 页面左上角，忽略当前滚动�?""
    
    clientRects: DOMRect | None
    """视口坐标（原�?= 可见滚动端口左上角）"""
    
    scrollRects: DOMRect | None
    """元素的可滚动区域"""
    
    computed_styles: dict[str, str] | None
    """从布局树计算的样式"""
    
    paint_order: int | None
    """绘制顺序"""
    
    stacking_contexts: int | None
    """堆叠上下�?""


@dataclass(slots=True)
class EnhancedDOMTreeNode:
    """
    增强�?DOM 树节点，包含来自 AX、DOM �?Snapshot 树的信息
    
    主要基于 DOM 节点类型，增强了 AX �?Snapshot 树的数据
    """
    
    # ===== DOM 节点数据 =====
    node_id: int
    backend_node_id: int
    node_type: NodeType
    node_name: str
    node_value: str
    attributes: dict[str, str]
    is_scrollable: bool | None
    is_visible: bool | None
    absolute_position: DOMRect | None
    
    # 框架相关
    target_id: TargetID
    frame_id: str | None
    session_id: SessionID | None
    content_document: 'EnhancedDOMTreeNode | None'
    
    # Shadow DOM
    shadow_root_type: ShadowRootType | None
    shadow_roots: list['EnhancedDOMTreeNode'] | None
    
    # 导航
    parent_node: 'EnhancedDOMTreeNode | None'
    children_nodes: list['EnhancedDOMTreeNode'] | None
    
    # ===== AX 节点数据 =====
    ax_node: EnhancedAXNode | None
    
    # ===== Snapshot 节点数据 =====
    snapshot_node: EnhancedSnapshotNode | None
    
    # 复合控件子组件信�?
    _compound_children: list[dict[str, Any]] = field(default_factory=list)
    
    uuid: str = field(default_factory=lambda: str(uuid4()))

    @property
    def parent(self) -> 'EnhancedDOMTreeNode | None':
        """父节�?""
        return self.parent_node

    @property
    def children(self) -> list['EnhancedDOMTreeNode']:
        """子节�?""
        return self.children_nodes or []

    @property
    def children_and_shadow_roots(self) -> list['EnhancedDOMTreeNode']:
        """返回所有子节点，包�?shadow roots"""
        children = list(self.children_nodes) if self.children_nodes else []
        if self.shadow_roots:
            children.extend(self.shadow_roots)
        return children

    @property
    def tag_name(self) -> str:
        """标签名（小写�?""
        return self.node_name.lower()

    @property
    def xpath(self) -> str:
        """生成�?DOM 节点�?XPath，在 shadow 边界�?iframe 处停�?""
        segments = []
        current_element = self

        while current_element and (
            current_element.node_type == NodeType.ELEMENT_NODE
            or current_element.node_type == NodeType.DOCUMENT_FRAGMENT_NODE
        ):
            # 只是通过 shadow roots
            if current_element.node_type == NodeType.DOCUMENT_FRAGMENT_NODE:
                current_element = current_element.parent_node
                continue

            # 只在遇到 iframe 时停�?
            if current_element.parent_node and current_element.parent_node.node_name.lower() == 'iframe':
                break

            position = self._get_element_position(current_element)
            tag_name = current_element.node_name.lower()
            xpath_index = f'[{position}]' if position > 0 else ''
            segments.insert(0, f'{tag_name}{xpath_index}')

            current_element = current_element.parent_node

        return '/'.join(segments)

    def _get_element_position(self, element: 'EnhancedDOMTreeNode') -> int:
        """获取元素在具有相同标签名的兄弟元素中的位�?""
        if not element.parent_node or not element.parent_node.children_nodes:
            return 0

        same_tag_siblings = [
            child for child in element.parent_node.children_nodes
            if child.node_type == NodeType.ELEMENT_NODE and child.node_name.lower() == element.node_name.lower()
        ]

        if len(same_tag_siblings) <= 1:
            return 0

        try:
            return same_tag_siblings.index(element) + 1  # XPath �?1 索引�?
        except ValueError:
            return 0

    def get_all_children_text(self, max_depth: int = -1) -> str:
        """获取所有子节点的文本内�?""
        text_parts = []

        def collect_text(node: EnhancedDOMTreeNode, current_depth: int) -> None:
            if max_depth != -1 and current_depth > max_depth:
                return

            if node.node_type == NodeType.TEXT_NODE:
                text_parts.append(node.node_value)
            elif node.node_type == NodeType.ELEMENT_NODE:
                for child in node.children:
                    collect_text(child, current_depth + 1)

        collect_text(self, 0)
        return '\n'.join(text_parts).strip()

    def get_meaningful_text_for_llm(self) -> str:
        """获取 LLM 实际看到的有意义的文本内�?""
        meaningful_text = ''
        if hasattr(self, 'attributes') and self.attributes:
            # 优先级顺序：value, aria-label, title, placeholder, alt, 文本内容
            for attr in ['value', 'aria-label', 'title', 'placeholder', 'alt']:
                if attr in self.attributes and self.attributes[attr]:
                    meaningful_text = self.attributes[attr]
                    break

        # 回退到文本内�?
        if not meaningful_text:
            meaningful_text = self.get_all_children_text()

        return meaningful_text.strip()

    @property
    def is_actually_scrollable(self) -> bool:
        """
        增强的滚动检测，结合 CDP 检测和 CSS 分析
        
        这可以检�?Chrome CDP 可能遗漏的可滚动元素
        """
        if self.is_scrollable:
            return True

        if not self.snapshot_node:
            return False

        scroll_rects = self.snapshot_node.scrollRects
        client_rects = self.snapshot_node.clientRects

        if scroll_rects and client_rects:
            has_vertical_scroll = scroll_rects.height > client_rects.height + 1
            has_horizontal_scroll = scroll_rects.width > client_rects.width + 1

            if has_vertical_scroll or has_horizontal_scroll:
                if self.snapshot_node.computed_styles:
                    styles = self.snapshot_node.computed_styles
                    overflow = styles.get('overflow', 'visible').lower()
                    overflow_x = styles.get('overflow-x', overflow).lower()
                    overflow_y = styles.get('overflow-y', overflow).lower()

                    allows_scroll = (
                        overflow in ['auto', 'scroll', 'overlay']
                        or overflow_x in ['auto', 'scroll', 'overlay']
                        or overflow_y in ['auto', 'scroll', 'overlay']
                    )
                    return allows_scroll
                else:
                    scrollable_tags = {'div', 'main', 'section', 'article', 'aside', 'body', 'html'}
                    return self.tag_name.lower() in scrollable_tags

        return False

    @property
    def should_show_scroll_info(self) -> bool:
        """是否应该显示滚动信息"""
        if self.tag_name.lower() == 'iframe':
            return True

        if not (self.is_scrollable or self.is_actually_scrollable):
            return False

        if self.tag_name.lower() in {'body', 'html'}:
            return True

        if self.parent_node and (self.parent_node.is_scrollable or self.parent_node.is_actually_scrollable):
            return False

        return True

    @property
    def scroll_info(self) -> dict[str, Any] | None:
        """计算此元素的滚动信息（如果可滚动�?""
        if not self.is_actually_scrollable or not self.snapshot_node:
            return None

        scroll_rects = self.snapshot_node.scrollRects
        client_rects = self.snapshot_node.clientRects

        if not scroll_rects or not client_rects:
            return None

        scroll_top = scroll_rects.y
        scroll_left = scroll_rects.x
        scrollable_height = scroll_rects.height
        scrollable_width = scroll_rects.width
        visible_height = client_rects.height
        visible_width = client_rects.width

        content_above = max(0, scroll_top)
        content_below = max(0, scrollable_height - visible_height - scroll_top)
        content_left = max(0, scroll_left)
        content_right = max(0, scrollable_width - visible_width - scroll_left)

        vertical_scroll_percentage = 0
        horizontal_scroll_percentage = 0

        if scrollable_height > visible_height:
            max_scroll_top = scrollable_height - visible_height
            vertical_scroll_percentage = (scroll_top / max_scroll_top) * 100 if max_scroll_top > 0 else 0

        if scrollable_width > visible_width:
            max_scroll_left = scrollable_width - visible_width
            horizontal_scroll_percentage = (scroll_left / max_scroll_left) * 100 if max_scroll_left > 0 else 0

        pages_above = content_above / visible_height if visible_height > 0 else 0
        pages_below = content_below / visible_height if visible_height > 0 else 0
        total_pages = scrollable_height / visible_height if visible_height > 0 else 1

        return {
            'scroll_top': scroll_top,
            'scroll_left': scroll_left,
            'scrollable_height': scrollable_height,
            'scrollable_width': scrollable_width,
            'visible_height': visible_height,
            'visible_width': visible_width,
            'content_above': content_above,
            'content_below': content_below,
            'content_left': content_left,
            'content_right': content_right,
            'vertical_scroll_percentage': round(vertical_scroll_percentage, 1),
            'horizontal_scroll_percentage': round(horizontal_scroll_percentage, 1),
            'pages_above': round(pages_above, 1),
            'pages_below': round(pages_below, 1),
            'total_pages': round(total_pages, 1),
            'can_scroll_up': content_above > 0,
            'can_scroll_down': content_below > 0,
            'can_scroll_left': content_left > 0,
            'can_scroll_right': content_right > 0,
        }

    def get_scroll_info_text(self) -> str:
        """获取人类可读的滚动信息文�?""
        if self.tag_name.lower() == 'iframe':
            if self.content_document:
                html_element = self._find_html_in_content_document()
                if html_element and html_element.scroll_info:
                    info = html_element.scroll_info
                    pages_below = info.get('pages_below', 0)
                    pages_above = info.get('pages_above', 0)
                    v_pct = int(info.get('vertical_scroll_percentage', 0))

                    if pages_below > 0 or pages_above > 0:
                        return f'scroll: {pages_above:.1f}�?{pages_below:.1f}�?{v_pct}%'
            return 'scroll'

        scroll_info = self.scroll_info
        if not scroll_info:
            return ''

        parts = []
        if scroll_info['scrollable_height'] > scroll_info['visible_height']:
            parts.append(f'{scroll_info["pages_above"]:.1f} pages above, {scroll_info["pages_below"]:.1f} pages below')

        if scroll_info['scrollable_width'] > scroll_info['visible_width']:
            parts.append(f'horizontal {scroll_info["horizontal_scroll_percentage"]:.0f}%')

        return ' '.join(parts)

    def _find_html_in_content_document(self) -> 'EnhancedDOMTreeNode | None':
        """�?iframe 内容文档中查�?HTML 元素"""
        if not self.content_document:
            return None

        if self.content_document.tag_name.lower() == 'html':
            return self.content_document

        if self.content_document.children_nodes:
            for child in self.content_document.children_nodes:
                if child.tag_name.lower() == 'html':
                    return child

        return None

    @property
    def element_hash(self) -> int:
        """元素哈希�?""
        return hash(self)

    def compute_stable_hash(self) -> int:
        """计算过滤动态类后的稳定哈希"""
        parent_branch_path = self._get_parent_branch_path()
        parent_branch_path_string = '/'.join(parent_branch_path)

        filtered_attrs: dict[str, str] = {}
        for k, v in self.attributes.items():
            if k not in STATIC_ATTRIBUTES:
                continue
            if k == 'class':
                v = filter_dynamic_classes(v)
                if not v:
                    continue
            filtered_attrs[k] = v

        attributes_string = ''.join(f'{k}={v}' for k, v in sorted(filtered_attrs.items()))

        ax_name = ''
        if self.ax_node and self.ax_node.name:
            ax_name = f'|ax_name={self.ax_node.name}'

        combined_string = f'{parent_branch_path_string}|{attributes_string}{ax_name}'
        hash_hex = hashlib.sha256(combined_string.encode()).hexdigest()
        return int(hash_hex[:16], 16)

    def __hash__(self) -> int:
        """基于父分支路径、属性和可访问性名称对元素进行哈希"""
        parent_branch_path = self._get_parent_branch_path()
        parent_branch_path_string = '/'.join(parent_branch_path)

        attributes_string = ''.join(
            f'{k}={v}' for k, v in sorted((k, v) for k, v in self.attributes.items() if k in STATIC_ATTRIBUTES)
        )

        ax_name = ''
        if self.ax_node and self.ax_node.name:
            ax_name = f'|ax_name={self.ax_node.name}'

        combined_string = f'{parent_branch_path_string}|{attributes_string}{ax_name}'
        element_hash = hashlib.sha256(combined_string.encode()).hexdigest()

        return int(element_hash[:16], 16)

    def _get_parent_branch_path(self) -> list[str]:
        """获取从根到当前元素的父分支路�?""
        parents: list[EnhancedDOMTreeNode] = []
        current_element: EnhancedDOMTreeNode | None = self

        while current_element is not None:
            if current_element.node_type == NodeType.ELEMENT_NODE:
                parents.append(current_element)
            current_element = current_element.parent_node

        parents.reverse()
        return [parent.tag_name for parent in parents]

    def __repr__(self) -> str:
        """字符串表�?""
        attributes = ', '.join([f'{k}={v}' for k, v in self.attributes.items()])
        is_scrollable = getattr(self, 'is_scrollable', False)
        num_children = len(self.children_nodes or [])
        return (
            f'<{self.tag_name} {attributes} is_scrollable={is_scrollable} '
            f'num_children={num_children} >{self.node_value}</{self.tag_name}>'
        )

    def __str__(self) -> str:
        """简短字符串表示"""
        return f'[<{self.tag_name}>#{self.frame_id[-4:] if self.frame_id else "?"}:{self.backend_node_id}]'

    def __json__(self) -> dict:
        """序列化节点及其后代为字典"""
        return {
            'node_id': self.node_id,
            'backend_node_id': self.backend_node_id,
            'node_type': self.node_type.name,
            'node_name': self.node_name,
            'node_value': self.node_value,
            'is_visible': self.is_visible,
            'attributes': self.attributes,
            'is_scrollable': self.is_scrollable,
            'session_id': self.session_id,
            'target_id': self.target_id,
            'frame_id': self.frame_id,
            'content_document': self.content_document.__json__() if self.content_document else None,
            'shadow_root_type': self.shadow_root_type,
            'ax_node': asdict(self.ax_node) if self.ax_node else None,
            'snapshot_node': asdict(self.snapshot_node) if self.snapshot_node else None,
            'shadow_roots': [r.__json__() for r in self.shadow_roots] if self.shadow_roots else [],
            'children_nodes': [c.__json__() for c in self.children_nodes] if self.children_nodes else [],
        }


@dataclass(slots=True)
class SimplifiedNode:
    """简化的树节点用于优�?""
    original_node: EnhancedDOMTreeNode
    children: list['SimplifiedNode']
    should_display: bool = True
    is_interactive: bool = False
    is_new: bool = False
    ignored_by_paint_order: bool = False
    excluded_by_parent: bool = False
    is_shadow_host: bool = False
    is_compound_component: bool = False

    def __json__(self) -> dict:
        """JSON 序列�?""
        original_node_json = self.original_node.__json__()
        # 移除重复字段
        if 'children_nodes' in original_node_json:
            del original_node_json['children_nodes']
        if 'shadow_roots' in original_node_json:
            del original_node_json['shadow_roots']

        return {
            'should_display': self.should_display,
            'is_interactive': self.is_interactive,
            'ignored_by_paint_order': self.ignored_by_paint_order,
            'excluded_by_parent': self.excluded_by_parent,
            'original_node': original_node_json,
            'children': [c.__json__() for c in self.children],
        }


# 类型别名
DOMSelectorMap = dict[int, EnhancedDOMTreeNode]


@dataclass
class SerializedDOMState:
    """序列化的 DOM 状�?""
    _root: SimplifiedNode | None
    selector_map: DOMSelectorMap

    def llm_representation(self, include_attributes: list[str] | None = None) -> str:
        """LLM 友好的表示形�?""
        # 延迟导入避免循环依赖
        from aerotest.browser.dom.serializer import DOMTreeSerializer

        if not self._root:
            return 'Empty DOM tree (you might have to wait for the page to load)'

        include_attributes = include_attributes or DEFAULT_INCLUDE_ATTRIBUTES
        return DOMTreeSerializer.serialize_tree(self._root, include_attributes)


@dataclass
class DOMInteractedElement:
    """表示已交互的 DOM 元素"""
    node_id: int
    backend_node_id: int
    frame_id: str | None
    node_type: NodeType
    node_value: str
    node_name: str
    attributes: dict[str, str] | None
    bounds: DOMRect | None
    x_path: str
    element_hash: int
    stable_hash: int | None = None
    ax_name: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """转换为字�?""
        return {
            'node_id': self.node_id,
            'backend_node_id': self.backend_node_id,
            'frame_id': self.frame_id,
            'node_type': self.node_type.value,
            'node_value': self.node_value,
            'node_name': self.node_name,
            'attributes': self.attributes,
            'x_path': self.x_path,
            'element_hash': self.element_hash,
            'stable_hash': self.stable_hash,
            'bounds': self.bounds.to_dict() if self.bounds else None,
            'ax_name': self.ax_name,
        }

    @classmethod
    def load_from_enhanced_dom_tree(cls, enhanced_dom_tree: EnhancedDOMTreeNode) -> 'DOMInteractedElement':
        """从增强的 DOM 树加�?""
        ax_name = None
        if enhanced_dom_tree.ax_node and enhanced_dom_tree.ax_node.name:
            ax_name = enhanced_dom_tree.ax_node.name

        return cls(
            node_id=enhanced_dom_tree.node_id,
            backend_node_id=enhanced_dom_tree.backend_node_id,
            frame_id=enhanced_dom_tree.frame_id,
            node_type=enhanced_dom_tree.node_type,
            node_value=enhanced_dom_tree.node_value,
            node_name=enhanced_dom_tree.node_name,
            attributes=enhanced_dom_tree.attributes,
            bounds=enhanced_dom_tree.snapshot_node.bounds if enhanced_dom_tree.snapshot_node else None,
            x_path=enhanced_dom_tree.xpath,
            element_hash=hash(enhanced_dom_tree),
            stable_hash=enhanced_dom_tree.compute_stable_hash(),
            ax_name=ax_name,
        )

