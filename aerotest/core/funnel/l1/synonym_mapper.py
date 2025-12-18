"""同义词映射器

扩展关键词的同义词，提高匹配的召回率
"""

from typing import Optional

from aerotest.utils import get_logger

logger = get_logger("aerotest.funnel.l1.synonym")


# 同义词词�?
SYNONYM_DICT = {
    # 提交相关
    "提交": ["确认", "保存", "发�?, "submit", "save", "send", "ok", "提交"],
    "确认": ["提交", "保存", "发�?, "confirm", "ok", "确认"],
    "保存": ["提交", "确认", "存储", "save", "store", "保存"],
    
    # 取消相关
    "取消": ["关闭", "退�?, "返回", "cancel", "close", "exit", "back", "取消"],
    "关闭": ["取消", "退�?, "close", "exit", "关闭"],
    
    # 登录相关
    "登录": ["登陆", "signin", "login", "sign in", "登录"],
    "注册": ["注冊", "signup", "register", "sign up", "注册"],
    
    # 搜索相关
    "搜索": ["查找", "检�?, "查询", "search", "find", "query", "搜索"],
    "查找": ["搜索", "检�?, "查询", "search", "find", "查找"],
    
    # 输入相关
    "输入": ["填写", "录入", "键入", "input", "enter", "type", "输入"],
    "填写": ["输入", "录入", "fill", "input", "填写"],
    
    # 选择相关
    "选择": ["选中", "勾�?, "�?, "select", "choose", "pick", "选择"],
    "勾�?: ["选择", "选中", "check", "勾�?],
    
    # 删除相关
    "删除": ["移除", "清除", "delete", "remove", "clear", "删除"],
    "移除": ["删除", "清除", "remove", "delete", "移除"],
    
    # 编辑相关
    "编辑": ["修改", "更改", "edit", "modify", "change", "编辑"],
    "修改": ["编辑", "更改", "modify", "edit", "修改"],
    
    # 查看相关
    "查看": ["浏览", "查阅", "view", "browse", "see", "查看"],
    "浏览": ["查看", "查阅", "browse", "view", "浏览"],
    
    # 下一�?上一�?
    "下一�?: ["next", "下一�?, "继续", "next step", "下一�?],
    "上一�?: ["previous", "上一�?, "返回", "prev", "back", "上一�?],
    
    # 按钮相关
    "按钮": ["button", "btn", "按键", "按钮"],
    "链接": ["link", "超链�?, "href", "链接"],
    
    # 输入框相�?
    "输入�?: ["文本�?, "input", "输入�?],
    "文本�?: ["输入�?, "input box", "文本�?],
    
    # 用户相关
    "用户�?: ["账号", "账户", "username", "account", "user", "用户�?],
    "密码": ["口令", "password", "密码"],
    "邮箱": ["email", "电子邮件", "mail", "邮箱"],
    "手机": ["电话", "手机�?, "phone", "mobile", "tel", "手机"],
    
    # 操作相关
    "点击": ["�?, "单击", "click", "tap", "点击"],
    "双击": ["double click", "dblclick", "双击"],
    
    # 其他常用�?
    "打开": ["开�?, "启动", "open", "start", "打开"],
    "跳转": ["进入", "访问", "navigate", "go to", "跳转"],
    "等待": ["暂停", "wait", "pause", "sleep", "等待"],
}

# 英文到中文的映射
ENGLISH_TO_CHINESE = {
    "submit": "提交",
    "confirm": "确认",
    "cancel": "取消",
    "save": "保存",
    "delete": "删除",
    "edit": "编辑",
    "view": "查看",
    "search": "搜索",
    "login": "登录",
    "register": "注册",
    "button": "按钮",
    "input": "输入�?,
    "link": "链接",
    "next": "下一�?,
    "previous": "上一�?,
    "username": "用户�?,
    "password": "密码",
    "email": "邮箱",
    "phone": "手机",
    "click": "点击",
}


class SynonymMapper:
    """同义词映射器
    
    为关键词扩展同义词，提高元素匹配的召回率
    
    功能�?
    1. 同义词扩展：为每个关键词添加同义�?
    2. 去重：移除重复的同义�?
    3. 中英文互译：支持中英文同义词
    4. 权重计算：原词权重高于同义词
    
    Example:
        ```python
        mapper = SynonymMapper()
        
        # 基本扩展
        synonyms = mapper.expand(["提交"])
        # ["提交", "确认", "保存", "发�?, "submit"]
        
        # 批量扩展
        expanded = mapper.expand_keywords(["提交", "按钮"])
        # {
        #     "提交": ["提交", "确认", "保存", "submit"],
        #     "按钮": ["按钮", "button", "btn"],
        # }
        ```
    """
    
    def __init__(self, max_synonyms: int = 10):
        """
        初始化同义词映射�?
        
        Args:
            max_synonyms: 每个关键词最多扩展的同义词数�?
        """
        self.max_synonyms = max_synonyms
        self.synonym_dict = SYNONYM_DICT
        self.en_to_zh = ENGLISH_TO_CHINESE
        logger.debug(f"同义词映射器初始化完成，词典大小: {len(self.synonym_dict)}")
    
    def expand(self, keyword: str) -> list[str]:
        """
        扩展单个关键词的同义�?
        
        Args:
            keyword: 关键�?
            
        Returns:
            包含原词和同义词的列表（原词在最前面�?
        """
        keyword = keyword.strip().lower()
        
        if not keyword:
            return []
        
        # 结果列表，原词放在第一�?
        result = [keyword]
        
        # 查找同义�?
        synonyms = self.synonym_dict.get(keyword, [])
        
        # 添加同义词（去重�?
        for syn in synonyms:
            syn_lower = syn.lower()
            if syn_lower not in result and len(result) < self.max_synonyms + 1:
                result.append(syn_lower)
        
        # 如果是英文词，尝试添加中文翻�?
        if keyword in self.en_to_zh:
            zh_word = self.en_to_zh[keyword]
            if zh_word.lower() not in result:
                result.append(zh_word.lower())
        
        logger.debug(f"同义词扩�? '{keyword}' -> {result}")
        return result
    
    def expand_keywords(self, keywords: list[str]) -> dict[str, list[str]]:
        """
        批量扩展关键�?
        
        Args:
            keywords: 关键词列�?
            
        Returns:
            关键词到同义词列表的映射
        """
        result = {}
        
        for keyword in keywords:
            if keyword:
                result[keyword] = self.expand(keyword)
        
        return result
    
    def get_all_synonyms(self, keywords: list[str]) -> list[str]:
        """
        获取所有关键词的所有同义词（扁平化�?
        
        Args:
            keywords: 关键词列�?
            
        Returns:
            所有同义词的扁平列表（去重�?
        """
        all_synonyms = []
        seen = set()
        
        for keyword in keywords:
            expanded = self.expand(keyword)
            for syn in expanded:
                if syn not in seen:
                    seen.add(syn)
                    all_synonyms.append(syn)
        
        return all_synonyms
    
    def add_synonym(self, word: str, synonyms: list[str]):
        """
        动态添加同义词
        
        Args:
            word: 单词
            synonyms: 同义词列�?
        """
        word_lower = word.lower()
        
        if word_lower not in self.synonym_dict:
            self.synonym_dict[word_lower] = []
        
        for syn in synonyms:
            syn_lower = syn.lower()
            if syn_lower not in self.synonym_dict[word_lower]:
                self.synonym_dict[word_lower].append(syn_lower)
        
        logger.debug(f"添加同义�? '{word}' -> {synonyms}")
    
    def get_weight(self, keyword: str, matched_word: str) -> float:
        """
        获取匹配词的权重
        
        原词权重�?1.0，同义词权重递减
        
        Args:
            keyword: 原关键词
            matched_word: 匹配到的�?
            
        Returns:
            权重�?.0-1.0�?
        """
        keyword_lower = keyword.lower()
        matched_lower = matched_word.lower()
        
        # 如果是原词，权重�?1.0
        if keyword_lower == matched_lower:
            return 1.0
        
        # 查找同义�?
        synonyms = self.expand(keyword)
        
        if matched_lower not in synonyms:
            return 0.0
        
        # 同义词的权重递减
        # 第一个同义词 0.9，第二个 0.8，以此类�?
        try:
            index = synonyms.index(matched_lower)
            weight = max(0.5, 1.0 - index * 0.1)
            return weight
        except ValueError:
            return 0.5
    
    def find_best_match(
        self,
        keyword: str,
        candidates: list[str],
    ) -> Optional[tuple[str, float]]:
        """
        在候选词中找到最佳匹�?
        
        Args:
            keyword: 关键�?
            candidates: 候选词列表
            
        Returns:
            (最佳匹配词, 权重) �?None
        """
        expanded = self.expand(keyword)
        
        best_match = None
        best_weight = 0.0
        
        for candidate in candidates:
            candidate_lower = candidate.lower()
            
            # 检查是否在扩展列表�?
            if candidate_lower in expanded:
                weight = self.get_weight(keyword, candidate_lower)
                
                if weight > best_weight:
                    best_weight = weight
                    best_match = candidate
        
        if best_match:
            return (best_match, best_weight)
        
        return None

