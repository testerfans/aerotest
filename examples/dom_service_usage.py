"""DOM Service 使用示例

演示如何使用 AeroTest 的 DOM Service 进行 DOM 处理

Note: 这是一个简化示例，完整的 CDP 集成将在 Week 3 实现
"""

from aerotest.browser.dom import (
    DomService,
    EnhancedDOMTreeNode,
    NodeType,
    create_dom_service,
)
from aerotest.browser.dom.cdp_types import TargetID, SessionID
from aerotest.browser.dom.views import (
    DOMRect,
    EnhancedAXNode,
    EnhancedSnapshotNode,
)


def create_mock_dom_tree() -> EnhancedDOMTreeNode:
    """
    创建一个模拟的 DOM 树用于演示
    
    在实际使用中，这会从浏览器的 CDP 接口获取
    """
    # 创建根节点（HTML）
    root = EnhancedDOMTreeNode(
        node_id=1,
        backend_node_id=1,
        node_type=NodeType.ELEMENT_NODE,
        node_name="HTML",
        node_value="",
        attributes={},
        is_scrollable=False,
        is_visible=True,
        absolute_position=None,
        target_id="target-1",
        frame_id="frame-1",
        session_id="session-1",
        content_document=None,
        shadow_root_type=None,
        shadow_roots=None,
        parent_node=None,
        children_nodes=[],
        ax_node=None,
        snapshot_node=None,
    )
    
    # 创建 body 节点
    body = EnhancedDOMTreeNode(
        node_id=2,
        backend_node_id=2,
        node_type=NodeType.ELEMENT_NODE,
        node_name="BODY",
        node_value="",
        attributes={},
        is_scrollable=False,
        is_visible=True,
        absolute_position=None,
        target_id="target-1",
        frame_id="frame-1",
        session_id="session-1",
        content_document=None,
        shadow_root_type=None,
        shadow_roots=None,
        parent_node=root,
        children_nodes=[],
        ax_node=None,
        snapshot_node=None,
    )
    
    # 创建一个按钮元素
    button = EnhancedDOMTreeNode(
        node_id=3,
        backend_node_id=3,
        node_type=NodeType.ELEMENT_NODE,
        node_name="BUTTON",
        node_value="",
        attributes={
            "id": "submit-btn",
            "class": "btn btn-primary",
            "aria-label": "Submit form",
        },
        is_scrollable=False,
        is_visible=True,
        absolute_position=DOMRect(x=100, y=200, width=120, height=40),
        target_id="target-1",
        frame_id="frame-1",
        session_id="session-1",
        content_document=None,
        shadow_root_type=None,
        shadow_roots=None,
        parent_node=body,
        children_nodes=[],
        ax_node=EnhancedAXNode(
            ax_node_id="ax-3",
            ignored=False,
            role="button",
            name="Submit",
            description=None,
            properties=[],
            child_ids=None,
        ),
        snapshot_node=EnhancedSnapshotNode(
            is_clickable=True,
            cursor_style="pointer",
            bounds=DOMRect(x=100, y=200, width=120, height=40),
            clientRects=DOMRect(x=100, y=200, width=120, height=40),
            scrollRects=None,
            computed_styles={"display": "block", "visibility": "visible", "opacity": "1"},
            paint_order=1,
            stacking_contexts=0,
        ),
    )
    
    # 创建按钮的文本节点
    button_text = EnhancedDOMTreeNode(
        node_id=4,
        backend_node_id=4,
        node_type=NodeType.TEXT_NODE,
        node_name="#text",
        node_value="Submit",
        attributes={},
        is_scrollable=False,
        is_visible=True,
        absolute_position=None,
        target_id="target-1",
        frame_id="frame-1",
        session_id="session-1",
        content_document=None,
        shadow_root_type=None,
        shadow_roots=None,
        parent_node=button,
        children_nodes=None,
        ax_node=None,
        snapshot_node=EnhancedSnapshotNode(
            is_clickable=False,
            cursor_style=None,
            bounds=None,
            clientRects=None,
            scrollRects=None,
            computed_styles=None,
            paint_order=None,
            stacking_contexts=None,
        ),
    )
    
    # 建立关系
    button.children_nodes = [button_text]
    body.children_nodes = [button]
    root.children_nodes = [body]
    
    return root


def example_basic_usage():
    """示例 1: 基础使用"""
    print("=" * 60)
    print("示例 1: 基础使用")
    print("=" * 60)
    
    # 创建 DOM Service
    service = create_dom_service(
        paint_order_filtering=True,
        bbox_filtering=True,
    )
    
    # 创建模拟 DOM 树
    root_node = create_mock_dom_tree()
    
    # 序列化 DOM 树
    state, timing = service.serialize_dom_tree(root_node)
    
    print(f"\n✅ DOM 序列化完成")
    print(f"   - 可交互元素数量: {len(state.selector_map)}")
    print(f"   - 总耗时: {timing.get('serialize_accessible_elements_total', 0)*1000:.1f}ms")
    
    # 获取 LLM 表示
    llm_repr = service.get_llm_representation(state)
    print(f"\n📝 LLM 表示:\n{llm_repr}\n")


def example_find_elements():
    """示例 2: 查找元素"""
    print("=" * 60)
    print("示例 2: 查找元素")
    print("=" * 60)
    
    service = create_dom_service()
    root_node = create_mock_dom_tree()
    state, _ = service.serialize_dom_tree(root_node)
    
    # 获取所有可点击元素
    clickable = service.get_clickable_elements(state)
    print(f"\n✅ 找到 {len(clickable)} 个可点击元素")
    
    for element in clickable:
        print(f"   - {element.tag_name}: {element.attributes.get('id', 'no-id')}")
    
    # 通过文本查找
    elements_by_text = service.find_elements_by_text(state, "Submit", exact_match=True)
    print(f"\n✅ 通过文本 'Submit' 找到 {len(elements_by_text)} 个元素")
    
    # 通过 backend_node_id 查找
    element = service.find_element_by_backend_node_id(state, 3)
    if element:
        print(f"\n✅ 找到元素:")
        print(f"   - 标签: {element.tag_name}")
        print(f"   - XPath: {element.xpath}")
        print(f"   - 文本: {element.get_all_children_text()}")


def example_element_summary():
    """示例 3: 元素摘要"""
    print("=" * 60)
    print("示例 3: 元素摘要")
    print("=" * 60)
    
    service = create_dom_service()
    root_node = create_mock_dom_tree()
    state, _ = service.serialize_dom_tree(root_node)
    
    # 获取元素摘要
    summaries = service.get_clickable_elements_summary(state)
    print(f"\n✅ 元素摘要 ({len(summaries)} 个元素):\n")
    
    for summary in summaries:
        print(f"   ID: {summary['backend_node_id']}")
        print(f"   标签: {summary['tag_name']}")
        print(f"   可见: {summary['is_visible']}")
        print(f"   XPath: {summary['xpath']}")
        if summary.get('bounds'):
            bounds = summary['bounds']
            print(f"   位置: ({bounds['x']}, {bounds['y']}) "
                  f"大小: {bounds['width']}x{bounds['height']}")
        print()


def example_statistics():
    """示例 4: 统计信息"""
    print("=" * 60)
    print("示例 4: 统计信息")
    print("=" * 60)
    
    service = create_dom_service()
    root_node = create_mock_dom_tree()
    state, _ = service.serialize_dom_tree(root_node)
    
    # 获取统计信息
    stats = service.get_statistics(state)
    
    print("\n📊 DOM 统计信息:")
    print(f"   - 总交互元素: {stats['total_interactive_elements']}")
    print(f"   - 可见元素: {stats['visible_elements']}")
    print(f"   - 可滚动元素: {stats['scrollable_elements']}")
    print(f"   - 包含 iframe: {stats['has_iframes']}")
    print(f"   - 包含 Shadow DOM: {stats['has_shadow_dom']}")
    
    print("\n   元素按标签分布:")
    for tag, count in stats['elements_by_tag'].items():
        print(f"      - {tag}: {count}")


def main():
    """运行所有示例"""
    print("\n" + "=" * 60)
    print("AeroTest DOM Service 使用示例")
    print("=" * 60 + "\n")
    
    try:
        example_basic_usage()
        print("\n")
        
        example_find_elements()
        print("\n")
        
        example_element_summary()
        print("\n")
        example_statistics()
        
        print("\n" + "=" * 60)
        print("✅ 所有示例运行完成！")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

