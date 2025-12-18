"""Prompt 构建�?

构建高质量的 Qwen Prompt
"""

from typing import Any, Optional

from aerotest.browser.dom.views import EnhancedDOMTreeNode
from aerotest.core.funnel.types import ActionSlot, MatchResult
from aerotest.utils import get_logger

logger = get_logger("aerotest.funnel.l4.prompt")


class PromptBuilder:
    """Prompt 构建�?
    
    为不同的 L4 任务构建 Prompt�?
    - 元素选择：从候选中选择最佳匹�?
    - 信息提取：从元素中提取特定信�?
    - 逻辑推理：处理复杂的业务逻辑
    
    Example:
        ```python
        builder = PromptBuilder()
        
        messages = builder.build_element_selection_prompt(
            instruction="选择最便宜的商�?,
            candidates=[...],
        )
        ```
    """
    
    SYSTEM_PROMPT = """你是一个专业的 Web 自动化测试助手。你的任务是根据用户的指令，从给定的 DOM 元素中选择最合适的目标元素�?

你需要：
1. 仔细理解用户的指令意�?
2. 分析每个候选元素的属性和内容
3. 根据指令要求，选择最匹配的元�?
4. 返回选中元素的索引（�?0 开始）

注意�?
- 如果指令包含"第一�?�?最后一�?等序号，优先考虑位置
- 如果指令包含"最�?�?最便宜"等比较，需要比较数�?
- 如果指令包含"红色"�?大号"等描述，需要匹配属�?
- 如果无法确定，返回最可能的选项"""
    
    def __init__(self):
        """初始�?Prompt 构建�?""
        logger.debug("Prompt 构建器初始化完成")
    
    def build_element_selection_prompt(
        self,
        instruction: str,
        candidates: list[MatchResult],
        context: Optional[dict[str, Any]] = None,
    ) -> list[dict[str, str]]:
        """
        构建元素选择 Prompt
        
        Args:
            instruction: 用户指令
            candidates: 候选元素列�?
            context: 额外的上下文信息
            
        Returns:
            消息列表
        """
        # 构建候选元素描�?
        candidates_desc = []
        for i, result in enumerate(candidates):
            element = result.element
            desc = self._describe_element(element, index=i)
            candidates_desc.append(desc)
        
        candidates_text = "\n\n".join(candidates_desc)
        
        # 构建用户消息
        user_message = f"""用户指令：{instruction}

候选元素列表（�?{len(candidates)} 个）�?

{candidates_text}

请根据用户指令，选择最合适的元素�?

返回 JSON 格式�?
{{
    "selected_index": 选中的元素索引（0-{len(candidates)-1}），
    "reason": "选择原因的简短说�?
}}"""
        
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]
        
        return messages
    
    def build_information_extraction_prompt(
        self,
        instruction: str,
        elements: list[EnhancedDOMTreeNode],
        extract_type: str = "text",
    ) -> list[dict[str, str]]:
        """
        构建信息提取 Prompt
        
        Args:
            instruction: 用户指令
            elements: 元素列表
            extract_type: 提取类型（text, number, list�?
            
        Returns:
            消息列表
        """
        # 构建元素描述
        elements_desc = []
        for i, element in enumerate(elements):
            desc = self._describe_element(element, index=i)
            elements_desc.append(desc)
        
        elements_text = "\n\n".join(elements_desc)
        
        # 根据提取类型构建 prompt
        if extract_type == "number":
            task_desc = "从元素中提取数值信息（如价格、数量等�?
            return_format = """{{
    "values": [提取的数值列表],
    "unit": "单位（如果有�?
}}"""
        elif extract_type == "list":
            task_desc = "从元素中提取列表信息"
            return_format = """{{
    "items": [提取的项目列表]
}}"""
        else:
            task_desc = "从元素中提取文本信息"
            return_format = """{{
    "texts": [提取的文本列表]
}}"""
        
        user_message = f"""任务：{task_desc}

用户指令：{instruction}

元素列表（共 {len(elements)} 个）�?

{elements_text}

请{task_desc}，返�?JSON 格式�?
{return_format}"""
        
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]
        
        return messages
    
    def build_comparison_prompt(
        self,
        instruction: str,
        elements: list[EnhancedDOMTreeNode],
        comparison_type: str = "value",
    ) -> list[dict[str, str]]:
        """
        构建比较 Prompt
        
        Args:
            instruction: 用户指令
            elements: 元素列表
            comparison_type: 比较类型（value, text, attribute�?
            
        Returns:
            消息列表
        """
        # 构建元素描述
        elements_desc = []
        for i, element in enumerate(elements):
            desc = self._describe_element(element, index=i)
            elements_desc.append(desc)
        
        elements_text = "\n\n".join(elements_desc)
        
        user_message = f"""任务：比较元素并根据指令选择

用户指令：{instruction}

元素列表（共 {len(elements)} 个）�?

{elements_text}

请根据指令中的比较要求（�?最�?�?最便宜"�?最�?等），选择符合条件的元素�?

返回 JSON 格式�?
{{
    "selected_index": 选中的元素索�?
    "comparison_value": "比较的�?,
    "reason": "选择原因"
}}"""
        
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]
        
        return messages
    
    def _describe_element(
        self,
        element: EnhancedDOMTreeNode,
        index: Optional[int] = None,
    ) -> str:
        """
        描述一个元�?
        
        Args:
            element: DOM 元素
            index: 元素索引
            
        Returns:
            元素描述文本
        """
        lines = []
        
        # 索引
        if index is not None:
            lines.append(f"【元�?{index}�?)
        
        # 标签�?
        lines.append(f"标签: <{element.tag_name}>")
        
        # 重要属�?
        important_attrs = ["id", "name", "class", "type", "value", "placeholder", "aria-label", "title"]
        
        for attr in important_attrs:
            value = element.attributes.get(attr)
            if value:
                # 截断过长的�?
                if len(value) > 100:
                    value = value[:97] + "..."
                lines.append(f"{attr}: {value}")
        
        # 文本内容
        inner_text = element.attributes.get("innerText") or element.attributes.get("textContent")
        if inner_text:
            inner_text = inner_text.strip()
            if len(inner_text) > 200:
                inner_text = inner_text[:197] + "..."
            if inner_text:
                lines.append(f"文本: {inner_text}")
        
        # 位置信息
        if element.bounding_box:
            bbox = element.bounding_box
            lines.append(f"位置: ({bbox.x:.0f}, {bbox.y:.0f}), 大小: ({bbox.width:.0f}×{bbox.height:.0f})")
        
        return "\n".join(lines)

