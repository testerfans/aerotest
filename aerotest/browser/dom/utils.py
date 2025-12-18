"""DOM 工具函数

来源: browser-use v0.11.2
"""

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aerotest.browser.dom.views import EnhancedDOMTreeNode


def cap_text_length(text: str, max_length: int) -> str:
    """
    截断文本长度用于显示
    
    Args:
        text: 原始文本
        max_length: 最大长�?
    
    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def generate_css_selector_for_element(enhanced_node: "EnhancedDOMTreeNode") -> str | None:
    """
    为元素生�?CSS 选择�?
    
    Args:
        enhanced_node: 增强�?DOM 树节�?
    
    Returns:
        CSS 选择器字符串�?None
    """
    if not enhanced_node or not hasattr(enhanced_node, "tag_name") or not enhanced_node.tag_name:
        return None

    # 获取基础选择�?
    tag_name = enhanced_node.tag_name.lower().strip()
    if not tag_name or not re.match(r"^[a-zA-Z][a-zA-Z0-9-]*$", tag_name):
        return None

    css_selector = tag_name

    # 添加 ID（最具体�?
    if enhanced_node.attributes and "id" in enhanced_node.attributes:
        element_id = enhanced_node.attributes["id"]
        if element_id and element_id.strip():
            element_id = element_id.strip()
            # 验证 ID 是否包含有效字符
            if re.match(r"^[a-zA-Z][a-zA-Z0-9_-]*$", element_id):
                return f"#{element_id}"
            else:
                # 对于带特殊字符的 ID，使用属性选择�?
                escaped_id = element_id.replace('"', '\\"')
                return f'{tag_name}[id="{escaped_id}"]'

    # 处理 class 属�?
    if enhanced_node.attributes and "class" in enhanced_node.attributes and enhanced_node.attributes["class"]:
        valid_class_name_pattern = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_-]*$")
        classes = enhanced_node.attributes["class"].split()
        
        for class_name in classes:
            if not class_name.strip():
                continue
            if valid_class_name_pattern.match(class_name):
                css_selector += f".{class_name}"

    # 安全属性列�?
    SAFE_ATTRIBUTES = {
        "id", "name", "type", "placeholder",
        "aria-label", "aria-labelledby", "aria-describedby", "role",
        "for", "autocomplete", "required", "readonly",
        "alt", "title", "src", "href", "target",
        "data-id", "data-qa", "data-cy", "data-testid",
    }

    # 处理其他属�?
    if enhanced_node.attributes:
        for attribute, value in enhanced_node.attributes.items():
            if attribute == "class":
                continue
            if not attribute.strip() or attribute not in SAFE_ATTRIBUTES:
                continue

            safe_attribute = attribute.replace(":", r"\:")

            if value == "":
                css_selector += f"[{safe_attribute}]"
            elif any(char in value for char in '"\'<>`\n\r\t'):
                if "\n" in value:
                    value = value.split("\n")[0]
                collapsed_value = re.sub(r"\s+", " ", value).strip()
                safe_value = collapsed_value.replace('"', '\\"')
                css_selector += f'[{safe_attribute}*="{safe_value}"]'
            else:
                css_selector += f'[{safe_attribute}="{value}"]'

    # 最终验�?
    if css_selector and not any(char in css_selector for char in ["\n", "\r", "\t"]):
        return css_selector

    return tag_name

