"""锚点定位器

从自然语言指令中识别并定位锚点元素（参照物）
"""

import re
from typing import Optional

import jieba

from aerotest.browser.dom.views import EnhancedDOMTreeNode
from aerotest.browser.dom.views import SerializedDOMState
from aerotest.core.funnel.l3.types import AnchorInfo, Direction, DistanceUnit
from aerotest.core.funnel.l2.attribute_matcher import AttributeMatcher
from aerotest.core.funnel.l2.text_matcher import TextMatcher
from aerotest.utils import get_logger

logger = get_logger("aerotest.funnel.l3.anchor")


class AnchorLocator:
    """锚点定位器
    
    从自然语言指令中识别锚点（参照物）并定位对应的元素：
    1. 识别锚点描述（如 "用户名输入框"）
    2. 识别方向（如 "右边"、"下方"）
    3. 识别距离（如 "旁边"、"远处"）
    4. 定位锚点元素
    
    Example:
        ```python
        locator = AnchorLocator()
        
        # 提取锚点信息
        anchor_info = locator.extract_anchor("点击用户名输入框右边的按钮")
        # AnchorInfo {
        #     description: "用户名输入框",
        #     direction: Direction.RIGHT,
        #     target_description: "按钮"
        # }
        
        # 定位锚点元素
        anchor_element = locator.locate_anchor(anchor_info, dom_state)
        ```
    """
    
    # 方向关键词映射
    DIRECTION_KEYWORDS = {
        Direction.LEFT: ["左边", "左侧", "左面", "左", "left"],
        Direction.RIGHT: ["右边", "右侧", "右面", "右", "right"],
        Direction.ABOVE: ["上边", "上方", "上面", "上", "above", "top"],
        Direction.BELOW: ["下边", "下方", "下面", "下", "below", "bottom"],
        Direction.INSIDE: ["里面", "内部", "中", "inside", "within"],
        Direction.NEAR: ["旁边", "附近", "邻近", "near", "nearby"],
    }
    
    # 距离关键词
    DISTANCE_KEYWORDS = {
        "近": (50, DistanceUnit.PIXEL),
        "远": (200, DistanceUnit.PIXEL),
        "旁边": (100, DistanceUnit.PIXEL),
        "附近": (150, DistanceUnit.PIXEL),
    }
    
    # 空间关系模式（用于识别锚点结构）
    SPATIAL_PATTERNS = [
        # "XXX 右边的 YYY"
        r"(.+?)(左边|右边|上边|下边|上方|下方|左侧|右侧|里面|旁边|附近)的(.+)",
        # "XXX 的右边的 YYY"
        r"(.+?)的(左边|右边|上边|下边|上方|下方|左侧|右侧|里面|旁边|附近)的(.+)",
        # "在 XXX 右边的 YYY"
        r"在(.+?)(左边|右边|上边|下边|上方|下方|左侧|右侧|里面|旁边|附近)的(.+)",
    ]
    
    def __init__(self):
        """初始化锚点定位器"""
        self.attribute_matcher = AttributeMatcher()
        self.text_matcher = TextMatcher()
        self._load_keywords()
        logger.debug("锚点定位器初始化完成")
    
    def _load_keywords(self):
        """加载关键词到 jieba 词典"""
        for keywords in self.DIRECTION_KEYWORDS.values():
            for keyword in keywords:
                jieba.add_word(keyword, freq=1000)
    
    def extract_anchor(self, instruction: str) -> Optional[AnchorInfo]:
        """
        从指令中提取锚点信息
        
        Args:
            instruction: 自然语言指令
            
        Returns:
            锚点信息，如果没有锚点则返回 None
        """
        instruction = instruction.strip()
        
        # 尝试匹配空间关系模式
        for pattern in self.SPATIAL_PATTERNS:
            match = re.search(pattern, instruction)
            if match:
                anchor_desc = match.group(1).strip()
                direction_word = match.group(2).strip()
                target_desc = match.group(3).strip()
                
                # 识别方向
                direction = self._recognize_direction(direction_word)
                
                # 识别距离
                distance, distance_unit = self._recognize_distance(instruction)
                
                anchor_info = AnchorInfo(
                    description=anchor_desc,
                    direction=direction,
                    distance=distance,
                    distance_unit=distance_unit,
                    target_description=target_desc,
                    confidence=0.9,
                )
                
                logger.info(
                    f"提取锚点: '{anchor_desc}' {direction.value if direction else ''} -> '{target_desc}'"
                )
                
                return anchor_info
        
        logger.debug(f"未检测到空间关系: '{instruction}'")
        return None
    
    def _recognize_direction(self, direction_word: str) -> Optional[Direction]:
        """
        识别方向词
        
        Args:
            direction_word: 方向词
            
        Returns:
            方向枚举
        """
        direction_word_lower = direction_word.lower()
        
        for direction, keywords in self.DIRECTION_KEYWORDS.items():
            if any(keyword in direction_word_lower for keyword in keywords):
                return direction
        
        return Direction.NEAR  # 默认为附近
    
    def _recognize_distance(self, text: str) -> tuple[Optional[float], DistanceUnit]:
        """
        识别距离
        
        Args:
            text: 文本
            
        Returns:
            (距离, 单位)
        """
        for keyword, (distance, unit) in self.DISTANCE_KEYWORDS.items():
            if keyword in text:
                return distance, unit
        
        # 尝试提取数字距离（如 "10像素"）
        pixel_match = re.search(r"(\d+)\s*(像素|px|pixel)", text)
        if pixel_match:
            distance = float(pixel_match.group(1))
            return distance, DistanceUnit.PIXEL
        
        return None, DistanceUnit.RELATIVE
    
    def locate_anchor(
        self,
        anchor_info: AnchorInfo,
        dom_state: SerializedDOMState,
    ) -> Optional[EnhancedDOMTreeNode]:
        """
        定位锚点元素
        
        Args:
            anchor_info: 锚点信息
            dom_state: DOM 状态
            
        Returns:
            锚点元素，如果找不到则返回 None
        """
        # 使用 L2 的能力匹配锚点元素
        anchor_keywords = self._extract_keywords(anchor_info.description)
        
        logger.debug(f"搜索锚点元素: {anchor_keywords}")
        
        # 获取所有可交互元素
        candidates = self._get_interactive_elements(dom_state)
        
        # 使用属性匹配器查找最佳匹配
        results = self.attribute_matcher.get_best_matches(
            elements=candidates,
            keywords=anchor_keywords,
            top_n=1,
        )
        
        if results:
            anchor_element = results[0].element
            logger.info(
                f"找到锚点元素: {anchor_element.tag_name} "
                f"(得分: {results[0].score:.2f})"
            )
            return anchor_element
        
        logger.warning(f"未找到锚点元素: '{anchor_info.description}'")
        return None
    
    def _extract_keywords(self, description: str) -> list[str]:
        """
        从描述中提取关键词
        
        Args:
            description: 元素描述
            
        Returns:
            关键词列表
        """
        # 分词
        words = list(jieba.cut(description))
        
        # 过滤停用词
        stop_words = ["的", "了", "在", "是", "上", "个", "中"]
        keywords = [w for w in words if w not in stop_words and len(w) > 0]
        
        # 添加原始描述（如果不太长）
        if len(description) <= 20:
            keywords.append(description)
        
        return keywords
    
    def _get_interactive_elements(
        self,
        dom_state: SerializedDOMState,
    ) -> list[EnhancedDOMTreeNode]:
        """
        获取所有可交互元素
        
        Args:
            dom_state: DOM 状态
            
        Returns:
            可交互元素列表
        """
        interactive_elements = []
        
        for node in dom_state.simplified_nodes:
            # 保留可点击的元素或表单元素
            if node.is_clickable:
                interactive_elements.append(node)
            elif node.tag_name and node.tag_name.lower() in ["input", "textarea", "select", "button"]:
                interactive_elements.append(node)
        
        return interactive_elements
    
    def has_spatial_relation(self, instruction: str) -> bool:
        """
        判断指令是否包含空间关系
        
        Args:
            instruction: 自然语言指令
            
        Returns:
            是否包含空间关系
        """
        # 检查是否匹配任何空间关系模式
        for pattern in self.SPATIAL_PATTERNS:
            if re.search(pattern, instruction):
                return True
        
        # 检查是否包含方向关键词
        instruction_lower = instruction.lower()
        for keywords in self.DIRECTION_KEYWORDS.values():
            if any(keyword in instruction_lower for keyword in keywords):
                return True
        
        return False
