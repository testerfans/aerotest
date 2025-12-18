"""文本匹配�?

提供多种文本匹配策略：精确匹配、模糊匹配、包含匹�?
"""

from rapidfuzz import fuzz
from aerotest.utils import get_logger

logger = get_logger("aerotest.funnel.l2.text")


class TextMatcher:
    """文本匹配�?
    
    提供多种文本匹配策略，计算文本相似度�?
    1. 精确匹配 (exact_match): 完全相同 -> 1.0
    2. 模糊匹配 (fuzzy_match): 使用 rapidfuzz 计算相似�?
    3. 包含匹配 (contains_match): 关键词是否包含在文本�?
    4. 综合匹配 (match): 自动选择最佳策�?
    
    Example:
        ```python
        matcher = TextMatcher()
        
        # 精确匹配
        score = matcher.exact_match("submit", "submit")
        # 1.0
        
        # 模糊匹配
        score = matcher.fuzzy_match("submit", "sumit")
        # ~0.85
        
        # 包含匹配
        score = matcher.contains_match("submit-button", "submit")
        # ~0.7
        
        # 自动匹配
        score = matcher.match("submit", "submit-btn")
        # 综合得分
        ```
    """
    
    def __init__(
        self,
        fuzzy_threshold: float = 0.7,
        contains_bonus: float = 0.1,
    ):
        """
        初始化文本匹配器
        
        Args:
            fuzzy_threshold: 模糊匹配的最低阈�?
            contains_bonus: 包含匹配的奖励分�?
        """
        self.fuzzy_threshold = fuzzy_threshold
        self.contains_bonus = contains_bonus
        logger.debug("文本匹配器初始化完成")
    
    def exact_match(self, text: str, keyword: str) -> float:
        """
        精确匹配
        
        Args:
            text: 要匹配的文本
            keyword: 关键�?
            
        Returns:
            匹配得分 (1.0 �?0.0)
        """
        if not text or not keyword:
            return 0.0
        
        text_lower = text.lower().strip()
        keyword_lower = keyword.lower().strip()
        
        if text_lower == keyword_lower:
            logger.debug(f"精确匹配: '{text}' == '{keyword}'")
            return 1.0
        
        return 0.0
    
    def fuzzy_match(self, text: str, keyword: str) -> float:
        """
        模糊匹配（使�?rapidfuzz�?
        
        Args:
            text: 要匹配的文本
            keyword: 关键�?
            
        Returns:
            匹配得分 (0.0-1.0)
        """
        if not text or not keyword:
            return 0.0
        
        text_lower = text.lower().strip()
        keyword_lower = keyword.lower().strip()
        
        # 使用 token_sort_ratio (对单词顺序不敏感)
        score = fuzz.token_sort_ratio(text_lower, keyword_lower) / 100.0
        
        if score >= self.fuzzy_threshold:
            logger.debug(
                f"模糊匹配: '{text[:20]}...' ~ '{keyword[:20]}...' "
                f"score={score:.2f}"
            )
        
        return score
    
    def contains_match(self, text: str, keyword: str) -> float:
        """
        包含匹配（关键词是否在文本中�?
        
        Args:
            text: 要匹配的文本
            keyword: 关键�?
            
        Returns:
            匹配得分 (0.0-1.0)
        """
        if not text or not keyword:
            return 0.0
        
        text_lower = text.lower().strip()
        keyword_lower = keyword.lower().strip()
        
        if keyword_lower in text_lower:
            # 计算覆盖�?
            coverage = len(keyword_lower) / len(text_lower)
            # 基础�?0.6，覆盖度奖励最�?0.4
            score = 0.6 + coverage * 0.4
            
            logger.debug(
                f"包含匹配: '{keyword}' in '{text[:30]}...' "
                f"score={score:.2f}"
            )
            return score
        
        return 0.0
    
    def partial_ratio_match(self, text: str, keyword: str) -> float:
        """
        部分匹配（使�?partial_ratio�?
        
        适用于关键词是文本的一部分的情�?
        
        Args:
            text: 要匹配的文本
            keyword: 关键�?
            
        Returns:
            匹配得分 (0.0-1.0)
        """
        if not text or not keyword:
            return 0.0
        
        text_lower = text.lower().strip()
        keyword_lower = keyword.lower().strip()
        
        score = fuzz.partial_ratio(text_lower, keyword_lower) / 100.0
        
        return score
    
    def match(
        self,
        text: str,
        keyword: str,
        strategy: str = "auto",
    ) -> float:
        """
        综合匹配（自动选择最佳策略）
        
        Args:
            text: 要匹配的文本
            keyword: 关键�?
            strategy: 匹配策略
                - "auto": 自动选择最佳策�?
                - "exact": 仅精确匹�?
                - "fuzzy": 仅模糊匹�?
                - "contains": 仅包含匹�?
            
        Returns:
            匹配得分 (0.0-1.0)
        """
        if not text or not keyword:
            return 0.0
        
        # 1. 精确匹配（最高优先级�?
        exact_score = self.exact_match(text, keyword)
        if exact_score == 1.0:
            return 1.0
        
        if strategy == "exact":
            return exact_score
        
        # 2. 包含匹配
        contains_score = self.contains_match(text, keyword)
        
        if strategy == "contains":
            return contains_score
        
        # 3. 模糊匹配
        fuzzy_score = self.fuzzy_match(text, keyword)
        
        if strategy == "fuzzy":
            return fuzzy_score
        
        # 4. 自动策略：取最高分
        max_score = max(contains_score, fuzzy_score)
        
        # 如果同时有包含和模糊匹配，给一个小奖励
        if contains_score > 0.5 and fuzzy_score > self.fuzzy_threshold:
            max_score = min(1.0, max_score + self.contains_bonus)
        
        return max_score
    
    def match_any(
        self,
        text: str,
        keywords: list[str],
        strategy: str = "auto",
    ) -> float:
        """
        匹配任意关键词（返回最高得分）
        
        Args:
            text: 要匹配的文本
            keywords: 关键词列�?
            strategy: 匹配策略
            
        Returns:
            最高匹配得�?
        """
        if not text or not keywords:
            return 0.0
        
        max_score = 0.0
        
        for keyword in keywords:
            score = self.match(text, keyword, strategy)
            if score > max_score:
                max_score = score
            
            # 如果已经是完美匹配，直接返回
            if score == 1.0:
                return 1.0
        
        return max_score
    
    def match_all(
        self,
        text: str,
        keywords: list[str],
        strategy: str = "auto",
    ) -> float:
        """
        匹配所有关键词（返回平均得分）
        
        Args:
            text: 要匹配的文本
            keywords: 关键词列�?
            strategy: 匹配策略
            
        Returns:
            平均匹配得分
        """
        if not text or not keywords:
            return 0.0
        
        total_score = 0.0
        count = 0
        
        for keyword in keywords:
            score = self.match(text, keyword, strategy)
            total_score += score
            count += 1
        
        return total_score / count if count > 0 else 0.0
    
    def is_similar(
        self,
        text1: str,
        text2: str,
        threshold: float = 0.8,
    ) -> bool:
        """
        判断两个文本是否相似
        
        Args:
            text1: 文本 1
            text2: 文本 2
            threshold: 相似度阈�?
            
        Returns:
            是否相似
        """
        if not text1 or not text2:
            return False
        
        score = self.fuzzy_match(text1, text2)
        return score >= threshold

