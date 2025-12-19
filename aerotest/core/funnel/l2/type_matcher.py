"""类型匹配器

基于元素类型和角色筛选元素
"""

from typing import Optional

from aerotest.browser.dom.views import EnhancedDOMTreeNode
from aerotest.core.funnel.types import ElementType
from aerotest.utils import get_logger

logger = get_logger("aerotest.funnel.l2.type")


class TypeMatcher:
    """类型匹配器
    
    基于元素类型筛选，包括：
    - 标签名(tag_name)
    - 元素类型 (ElementType)
    - ARIA role
    - input type 属性
    
    Example:
        ```python
        matcher = TypeMatcher()
        
        # 按标签名筛选
        buttons = matcher.match_by_tag(elements, "button")
        
        # 按元素类型筛选
        buttons = matcher.match_by_type(elements, ElementType.BUTTON)
        
        # 按 role 筛选
        buttons = matcher.match_by_role(elements, "button")
        ```
    """
    
    # 元素类型到标签名的映射
    TYPE_TO_TAGS = {
        ElementType.BUTTON: ["button", "input"],
        ElementType.INPUT: ["input", "textarea"],
        ElementType.TEXTAREA: ["textarea"],
        ElementType.SELECT: ["select"],
        ElementType.CHECKBOX: ["input"],
        ElementType.RADIO: ["input"],
        ElementType.LINK: ["a"],
        ElementType.DIV: ["div"],
        ElementType.SPAN: ["span"],
        ElementType.LABEL: ["label"],
    }
    
    # input 类型筛选条件
    INPUT_TYPE_CONDITIONS = {
        ElementType.BUTTON: ["button", "submit", "reset"],
        ElementType.INPUT: ["text", "password", "email", "tel", "url", "search"],
        ElementType.CHECKBOX: ["checkbox"],
        ElementType.RADIO: ["radio"],
    }
    
    def __init__(self):
        """初始化类型匹配器"""
        logger.debug("类型匹配器初始化完成")
    
    def match_by_tag(
        self,
        elements: list[EnhancedDOMTreeNode],
        tag_name: str,
    ) -> list[EnhancedDOMTreeNode]:
        """
        按标签名筛选
        
        Args:
            elements: 元素列表
            tag_name: 标签名
            
        Returns:
            匹配的元素列表
        """
        tag_lower = tag_name.lower()
        matched = [
            elem for elem in elements
            if elem.tag_name and elem.tag_name.lower() == tag_lower
        ]
        
        logger.debug(f"标签筛选: {tag_name} -> {len(matched)} 个元素")
        return matched
    
    def match_by_type(
        self,
        elements: list[EnhancedDOMTreeNode],
        element_type: ElementType,
    ) -> list[EnhancedDOMTreeNode]:
        """
        按元素类型筛选
        
        Args:
            elements: 元素列表
            element_type: 元素类型
            
        Returns:
            匹配的元素列表
        """
        # 获取可能的标签名
        possible_tags = self.TYPE_TO_TAGS.get(element_type, [])
        
        if not possible_tags:
            return []
        
        matched = []
        
        for elem in elements:
            if not elem.tag_name:
                continue
            
            tag_lower = elem.tag_name.lower()
            
            # 检查标签名
            if tag_lower not in possible_tags:
                continue
            
            # 对于 input 元素，需要检查 type 属性
            if tag_lower == "input":
                input_type = elem.attributes.get("type", "text").lower()
                type_conditions = self.INPUT_TYPE_CONDITIONS.get(element_type, [])
                
                if type_conditions and input_type not in type_conditions:
                    continue
            
            matched.append(elem)
        
        logger.debug(f"类型筛选: {element_type.value} -> {len(matched)} 个元素")
        return matched
    
    def match_by_role(
        self,
        elements: list[EnhancedDOMTreeNode],
        role: str,
    ) -> list[EnhancedDOMTreeNode]:
        """
        按 ARIA role 筛选
        
        Args:
            elements: 元素列表
            role: ARIA role
            
        Returns:
            匹配的元素列表
        """
        role_lower = role.lower()
        matched = [
            elem for elem in elements
            if elem.attributes.get("role", "").lower() == role_lower
        ]
        
        logger.debug(f"role 筛选: {role} -> {len(matched)} 个元素")
        return matched
    
    def is_type_match(
        self,
        element: EnhancedDOMTreeNode,
        element_type: Optional[ElementType],
    ) -> bool:
        """
        判断元素是否匹配指定类型
        
        Args:
            element: 元素
            element_type: 元素类型
            
        Returns:
            是否匹配
        """
        if not element_type:
            return True
        
        matched_elements = self.match_by_type([element], element_type)
        return len(matched_elements) > 0


# 导出单例
_type_matcher = None

def get_type_matcher() -> TypeMatcher:
    """获取类型匹配器单例"""
    global _type_matcher
    if _type_matcher is None:
        _type_matcher = TypeMatcher()
    return _type_matcher
