# Phase 2: L1-L2 层实施计划

**目标**: 实现五层漏斗的前两层 - 规则槽位和启发式属性匹配  
**预计时间**: 2-3 周  
**优先级**: 🔴 高（核心定位能力）

---

## 🎯 总体目标

实现 AeroTest AI 的智能元素定位能力，通过规则和启发式方法快速准确地定位页面元素。

### 成功标准

1. ✅ L1 能够从自然语言中提取操作意图
2. ✅ L1 能够识别目标元素的关键特征
3. ✅ L2 能够通过多种属性匹配元素
4. ✅ L2 能够进行模糊匹配和相似度计算
5. ✅ 准确率 > 85%（简单场景）

---

## 📋 L1: 规则槽位 (Rule-based Slotting)

### 功能概述

从自然语言指令中提取结构化的操作信息：

```
输入: "点击提交按钮"
输出: {
    "action": "click",
    "target": "提交按钮",
    "target_type": "button",
    "keywords": ["提交", "按钮"]
}
```

### 核心组件

#### 1. 意图识别器 (IntentRecognizer)

**功能**: 识别用户操作意图

```python
class IntentRecognizer:
    """识别操作意图"""
    
    ACTIONS = {
        "click": ["点击", "按", "选择", "单击"],
        "input": ["输入", "填写", "录入", "键入"],
        "select": ["选择", "选中", "勾选"],
        "navigate": ["打开", "访问", "跳转"],
        "wait": ["等待", "暂停"],
    }
    
    def recognize(self, text: str) -> str:
        """识别动作类型"""
        ...
```

#### 2. 实体提取器 (EntityExtractor)

**功能**: 提取目标元素的关键信息

```python
class EntityExtractor:
    """提取目标实体"""
    
    ELEMENT_TYPES = {
        "button": ["按钮", "按键", "确认", "提交"],
        "input": ["输入框", "文本框", "输入", "框"],
        "link": ["链接", "超链接"],
        "checkbox": ["复选框", "多选框"],
        "radio": ["单选框", "单选"],
    }
    
    def extract(self, text: str) -> dict:
        """提取目标信息"""
        ...
```

#### 3. 槽位填充器 (SlotFiller)

**功能**: 将提取的信息填充到槽位

```python
@dataclass
class ActionSlot:
    """动作槽位"""
    action: str                    # 动作类型
    target: Optional[str]          # 目标描述
    target_type: Optional[str]     # 目标类型
    keywords: list[str]            # 关键词
    attributes: dict[str, str]     # 属性提示
    value: Optional[str]           # 输入值（如果是 input 动作）
    
class SlotFiller:
    """槽位填充"""
    
    def fill(self, text: str) -> ActionSlot:
        """填充槽位"""
        ...
```

#### 4. 同义词映射器 (SynonymMapper)

**功能**: 扩展关键词的同义词

```python
class SynonymMapper:
    """同义词映射"""
    
    SYNONYMS = {
        "提交": ["确认", "保存", "发送", "submit"],
        "取消": ["关闭", "退出", "cancel"],
        "搜索": ["查找", "检索", "search"],
    }
    
    def expand(self, keyword: str) -> list[str]:
        """扩展同义词"""
        ...
```

### 实施步骤

**Week 1: L1 基础**

```python
Day 1-2: 意图识别
├── intent_recognizer.py      # 意图识别器
├── action_patterns.py        # 动作模式库
└── tests/test_intent.py      # 单元测试

Day 3-4: 实体提取
├── entity_extractor.py       # 实体提取器
├── element_types.py          # 元素类型库
└── tests/test_entity.py      # 单元测试

Day 5-7: 槽位填充和集成
├── slot_filler.py            # 槽位填充器
├── synonym_mapper.py         # 同义词映射
├── l1_engine.py              # L1 引擎
└── tests/test_l1.py          # 集成测试
```

---

## 📋 L2: 启发式属性匹配 (Heuristic Attribute Match)

### 功能概述

使用启发式规则匹配 DOM 元素：

```python
槽位信息: {
    "action": "click",
    "target": "提交按钮",
    "keywords": ["提交", "按钮", "submit"]
}

匹配策略:
1. Placeholder 匹配 ⭐⭐⭐⭐⭐
2. ID 匹配 ⭐⭐⭐⭐
3. Name 匹配 ⭐⭐⭐⭐
4. InnerText 匹配 ⭐⭐⭐
5. Aria-label 匹配 ⭐⭐⭐
6. 标签类型匹配 ⭐⭐

结果: [
    {element: Button#submit, score: 0.95},
    {element: Button.primary, score: 0.85},
]
```

### 核心组件

#### 1. 属性匹配器 (AttributeMatcher)

**功能**: 基于属性匹配元素

```python
class AttributeMatcher:
    """属性匹配器"""
    
    # 属性权重
    ATTRIBUTE_WEIGHTS = {
        "placeholder": 1.0,
        "id": 0.9,
        "name": 0.9,
        "aria-label": 0.85,
        "title": 0.8,
        "value": 0.7,
        "innerText": 0.6,
        "class": 0.4,
    }
    
    def match_by_attribute(
        self,
        elements: list[EnhancedDOMTreeNode],
        keywords: list[str],
        attribute: str,
    ) -> list[MatchResult]:
        """按属性匹配"""
        ...
```

#### 2. 文本匹配器 (TextMatcher)

**功能**: 基于文本内容匹配

```python
class TextMatcher:
    """文本匹配器"""
    
    def exact_match(self, text: str, keyword: str) -> float:
        """精确匹配"""
        ...
    
    def fuzzy_match(self, text: str, keyword: str) -> float:
        """模糊匹配（使用 rapidfuzz）"""
        ...
    
    def contains_match(self, text: str, keyword: str) -> float:
        """包含匹配"""
        ...
```

#### 3. 类型匹配器 (TypeMatcher)

**功能**: 基于元素类型匹配

```python
class TypeMatcher:
    """类型匹配器"""
    
    def match_by_type(
        self,
        elements: list[EnhancedDOMTreeNode],
        target_type: str,
    ) -> list[EnhancedDOMTreeNode]:
        """按类型筛选元素"""
        ...
```

#### 4. 评分器 (Scorer)

**功能**: 计算匹配分数

```python
@dataclass
class MatchResult:
    """匹配结果"""
    element: EnhancedDOMTreeNode
    score: float
    matched_attributes: dict[str, float]
    match_reasons: list[str]

class Scorer:
    """评分器"""
    
    def calculate_score(
        self,
        element: EnhancedDOMTreeNode,
        keywords: list[str],
        target_type: Optional[str],
    ) -> MatchResult:
        """计算综合得分"""
        ...
```

### 实施步骤

**Week 2: L2 基础**

```python
Day 1-2: 属性匹配
├── attribute_matcher.py      # 属性匹配器
├── match_result.py           # 匹配结果
└── tests/test_attribute.py   # 单元测试

Day 3-4: 文本和类型匹配
├── text_matcher.py           # 文本匹配器
├── type_matcher.py           # 类型匹配器
└── tests/test_matcher.py     # 单元测试

Day 5-7: 评分和集成
├── scorer.py                 # 评分器
├── l2_engine.py              # L2 引擎
└── tests/test_l2.py          # 集成测试
```

---

## 📋 L1-L2 集成

### 完整工作流程

```python
class FunnelL1L2Engine:
    """L1-L2 层集成引擎"""
    
    def __init__(self):
        self.l1_engine = L1Engine()
        self.l2_engine = L2Engine()
    
    async def locate_element(
        self,
        instruction: str,
        dom_state: SerializedDOMState,
    ) -> list[MatchResult]:
        """
        定位元素
        
        Args:
            instruction: 自然语言指令，如 "点击提交按钮"
            dom_state: 序列化的 DOM 状态
            
        Returns:
            匹配结果列表（按得分排序）
        """
        # L1: 提取槽位信息
        slot = self.l1_engine.extract_slot(instruction)
        
        # L2: 属性匹配
        candidates = self.l2_engine.match_elements(
            dom_state=dom_state,
            slot=slot,
        )
        
        # 返回 Top-N 结果
        return sorted(candidates, key=lambda x: x.score, reverse=True)
```

### 使用示例

```python
# 完整流程示例
async def example_usage():
    # 1. 连接浏览器并获取 DOM
    async with CDPSession.connect() as session:
        await session.navigate("https://example.com")
        dom_tree = await session.get_dom_tree()
        
        # 2. 序列化 DOM
        service = DomService()
        state, _ = service.serialize_dom_tree(dom_tree)
        
        # 3. L1-L2 定位
        engine = FunnelL1L2Engine()
        results = await engine.locate_element(
            instruction="点击提交按钮",
            dom_state=state,
        )
        
        # 4. 获取最佳匹配
        if results:
            best_match = results[0]
            print(f"找到元素: {best_match.element.tag_name}")
            print(f"得分: {best_match.score:.2f}")
            print(f"匹配原因: {best_match.match_reasons}")
```

---

## 📊 预期性能指标

### 准确率目标

| 场景 | L1 准确率 | L2 准确率 | 综合准确率 |
|------|----------|----------|-----------|
| **简单场景** | 95% | 90% | 85% |
| **中等场景** | 85% | 75% | 65% |
| **复杂场景** | 70% | 60% | 45% |

**说明**:
- 简单场景：标准 HTML，清晰的 ID/Name
- 中等场景：动态生成的 ID，需要文本匹配
- 复杂场景：非标准控件，需要 L3-L5

### 性能目标

| 指标 | 目标 |
|------|------|
| **L1 处理时间** | < 10ms |
| **L2 匹配时间** | < 100ms (500 元素) |
| **综合时间** | < 150ms |
| **内存占用** | < 50MB |

---

## 🏗️ 项目结构

```
aerotest/core/funnel/
├── __init__.py
├── base.py                      # 基础类和接口
├── types.py                     # 数据类型定义
│
├── l1/                          # L1 规则槽位
│   ├── __init__.py
│   ├── intent_recognizer.py    # 意图识别
│   ├── entity_extractor.py     # 实体提取
│   ├── slot_filler.py           # 槽位填充
│   ├── synonym_mapper.py        # 同义词映射
│   ├── action_patterns.py       # 动作模式库
│   ├── element_types.py         # 元素类型库
│   └── l1_engine.py             # L1 引擎
│
├── l2/                          # L2 属性匹配
│   ├── __init__.py
│   ├── attribute_matcher.py    # 属性匹配
│   ├── text_matcher.py          # 文本匹配
│   ├── type_matcher.py          # 类型匹配
│   ├── scorer.py                # 评分器
│   ├── match_result.py          # 匹配结果
│   └── l2_engine.py             # L2 引擎
│
└── engine.py                    # L1-L2 集成引擎

tests/unit/funnel/
├── test_l1_intent.py
├── test_l1_entity.py
├── test_l2_attribute.py
├── test_l2_text.py
└── test_integration.py

examples/
└── funnel_l1_l2_usage.py       # 使用示例
```

---

## 🧪 测试策略

### 单元测试

**L1 测试**:
```python
def test_intent_recognition():
    recognizer = IntentRecognizer()
    assert recognizer.recognize("点击按钮") == "click"
    assert recognizer.recognize("输入用户名") == "input"
    assert recognizer.recognize("选择选项") == "select"

def test_entity_extraction():
    extractor = EntityExtractor()
    result = extractor.extract("提交按钮")
    assert result["target_type"] == "button"
    assert "提交" in result["keywords"]
```

**L2 测试**:
```python
def test_attribute_matching():
    matcher = AttributeMatcher()
    # 创建测试元素
    element = create_test_element(id="submit-btn", text="提交")
    # 测试匹配
    score = matcher.match_attribute(element, "提交", "id")
    assert score > 0.8
```

### 集成测试

```python
async def test_l1_l2_integration():
    """测试 L1-L2 完整流程"""
    engine = FunnelL1L2Engine()
    
    # 准备测试数据
    dom_state = create_test_dom_state()
    
    # 执行定位
    results = await engine.locate_element(
        instruction="点击提交按钮",
        dom_state=dom_state,
    )
    
    # 验证结果
    assert len(results) > 0
    assert results[0].score > 0.7
    assert results[0].element.tag_name == "button"
```

### 端到端测试

```python
async def test_e2e_locate_and_click():
    """端到端测试：定位并点击"""
    async with CDPSession.connect() as session:
        await session.navigate("https://example.com")
        
        # 获取 DOM
        dom_tree = await session.get_dom_tree()
        service = DomService()
        state, _ = service.serialize_dom_tree(dom_tree)
        
        # L1-L2 定位
        engine = FunnelL1L2Engine()
        results = await engine.locate_element(
            instruction="点击提交按钮",
            dom_state=state,
        )
        
        # 执行点击
        assert len(results) > 0
        # TODO: 实现点击操作
```

---

## 📚 依赖库

### 新增依赖

```toml
[tool.poetry.dependencies]
# NLP 和文本处理
jieba = "^0.42.1"           # 中文分词（已有）
rapidfuzz = "^3.5.2"        # 模糊匹配（已有）
zhon = "^2.0.2"             # 中文字符处理（新增）

# 可选: 更高级的 NLP
# pypinyin = "^0.50.0"      # 拼音转换
# snownlp = "^0.12.3"       # 中文自然语言处理
```

---

## 🎯 里程碑

### Week 1: L1 实现

- [x] Day 1: 项目结构和基础类
- [ ] Day 2: 意图识别器
- [ ] Day 3: 实体提取器
- [ ] Day 4: 槽位填充器
- [ ] Day 5: 同义词映射
- [ ] Day 6-7: L1 引擎和测试

### Week 2: L2 实现

- [ ] Day 1: 属性匹配器
- [ ] Day 2: 文本匹配器
- [ ] Day 3: 类型匹配器
- [ ] Day 4: 评分器
- [ ] Day 5-7: L2 引擎和测试

### Week 3: 集成和优化

- [ ] Day 1-2: L1-L2 集成引擎
- [ ] Day 3-4: 端到端测试
- [ ] Day 5: 性能优化
- [ ] Day 6-7: 文档和示例

---

## 🚀 快速开始

### 第一步：创建基础结构

```bash
# 创建目录
mkdir -p aerotest/core/funnel/{l1,l2}
mkdir -p tests/unit/funnel

# 创建 __init__.py
touch aerotest/core/funnel/{__init__,base,types}.py
touch aerotest/core/funnel/l1/__init__.py
touch aerotest/core/funnel/l2/__init__.py
```

### 第二步：实现基础类

```python
# aerotest/core/funnel/base.py
from abc import ABC, abstractmethod

class BaseFunnelLayer(ABC):
    """漏斗层基类"""
    
    @abstractmethod
    async def process(self, input_data):
        """处理输入数据"""
        pass
```

### 第三步：运行示例

```python
from aerotest.core.funnel import FunnelL1L2Engine

engine = FunnelL1L2Engine()
results = await engine.locate_element(
    instruction="点击提交按钮",
    dom_state=dom_state,
)
```

---

## 📝 注意事项

### 中文处理

1. **分词**: 使用 jieba 进行中文分词
2. **同义词**: 建立中文同义词库
3. **繁简转换**: 支持繁体中文
4. **拼音匹配**: 支持拼音输入（可选）

### 性能优化

1. **缓存**: 缓存分词结果和同义词映射
2. **索引**: 为常用属性建立索引
3. **并行**: 并行处理多个候选元素
4. **裁剪**: 只处理可见和可交互的元素

### 可扩展性

1. **插件化**: 支持自定义匹配器
2. **配置化**: 支持权重和阈值配置
3. **学习能力**: 记录成功的匹配模式（L4 自愈）

---

**计划制定**: 2025-12-18  
**预计开始**: 立即  
**预计完成**: 2026-01-10 (3 周)

**准备开始 Phase 2 的开发！** 🚀

