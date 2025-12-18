"""可点击元素检测器

来源: browser-use v0.11.2
改�? 移除�?browser_use 的依赖，适配 AeroTest 架构
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aerotest.browser.dom.views import EnhancedDOMTreeNode, NodeType


class ClickableElementDetector:
    """可点击元素检测器"""

    @staticmethod
    def is_interactive(node: "EnhancedDOMTreeNode") -> bool:
        """
        检查节点是否可交互/可点�?
        
        Args:
            node: 增强�?DOM 树节�?
        
        Returns:
            是否可交�?
        """
        from aerotest.browser.dom.views import NodeType

        # 跳过非元素节�?
        if node.node_type != NodeType.ELEMENT_NODE:
            return False

        # 移除 html �?body 节点
        if node.tag_name in {"html", "body"}:
            return False

        # IFRAME 元素应该是可交互的，如果它们足够大可能需要滚�?
        if node.tag_name and node.tag_name.upper() in ("IFRAME", "FRAME"):
            if node.snapshot_node and node.snapshot_node.bounds:
                width = node.snapshot_node.bounds.width
                height = node.snapshot_node.bounds.height
                # 只包含大�?100x100px �?iframe
                if width > 100 and height > 100:
                    return True

        # 搜索元素检�?
        if node.attributes:
            search_indicators = {
                "search", "magnify", "glass", "lookup", "find", "query",
                "search-icon", "search-btn", "search-button", "searchbox",
            }

            # 检�?class 名称
            class_list = node.attributes.get("class", "").lower().split()
            if any(indicator in " ".join(class_list) for indicator in search_indicators):
                return True

            # 检�?id
            element_id = node.attributes.get("id", "").lower()
            if any(indicator in element_id for indicator in search_indicators):
                return True

            # 检�?data 属�?
            for attr_name, attr_value in node.attributes.items():
                if attr_name.startswith("data-") and any(
                    indicator in attr_value.lower() for indicator in search_indicators
                ):
                    return True

        # 增强的可访问性属性检�?
        if node.ax_node and node.ax_node.properties:
            for prop in node.ax_node.properties:
                try:
                    # aria disabled
                    if prop.name == "disabled" and prop.value:
                        return False

                    # aria hidden
                    if prop.name == "hidden" and prop.value:
                        return False

                    # 直接交互性指示器
                    if prop.name in ["focusable", "editable", "settable"] and prop.value:
                        return True

                    # 交互状态属�?
                    if prop.name in ["checked", "expanded", "pressed", "selected"]:
                        return True

                    # 表单相关交互�?
                    if prop.name in ["required", "autocomplete"] and prop.value:
                        return True

                    # 具有键盘快捷键的元素是可交互�?
                    if prop.name == "keyshortcuts" and prop.value:
                        return True
                except (AttributeError, ValueError):
                    continue

        # 增强的标签检�?
        interactive_tags = {
            "button", "input", "select", "textarea", "a",
            "details", "summary", "option", "optgroup",
        }
        if node.tag_name and node.tag_name.lower() in interactive_tags:
            return True

        # 具有交互属性的元素
        if node.attributes:
            interactive_attributes = {
                "onclick", "onmousedown", "onmouseup",
                "onkeydown", "onkeyup", "tabindex"
            }
            if any(attr in node.attributes for attr in interactive_attributes):
                return True

            # 检查交�?ARIA 角色
            if "role" in node.attributes:
                interactive_roles = {
                    "button", "link", "menuitem", "option", "radio", "checkbox",
                    "tab", "textbox", "combobox", "slider", "spinbutton",
                    "search", "searchbox",
                }
                if node.attributes["role"] in interactive_roles:
                    return True

        # 可访问性树角色
        if node.ax_node and node.ax_node.role:
            interactive_ax_roles = {
                "button", "link", "menuitem", "option", "radio", "checkbox",
                "tab", "textbox", "combobox", "slider", "spinbutton",
                "listbox", "search", "searchbox",
            }
            if node.ax_node.role in interactive_ax_roles:
                return True

        # 图标和小元素检�?
        if (
            node.snapshot_node
            and node.snapshot_node.bounds
            and 10 <= node.snapshot_node.bounds.width <= 50
            and 10 <= node.snapshot_node.bounds.height <= 50
        ):
            if node.attributes:
                icon_attributes = {"class", "role", "onclick", "data-action", "aria-label"}
                if any(attr in node.attributes for attr in icon_attributes):
                    return True

        # 最后的后备方案：光标样式表示交互�?
        if (
            node.snapshot_node
            and node.snapshot_node.cursor_style
            and node.snapshot_node.cursor_style == "pointer"
        ):
            return True

        return False

