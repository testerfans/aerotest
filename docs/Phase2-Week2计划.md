# Phase 2 - Week 2 计划 (L2 属性匹配层)

**开始日期**: 2025-12-18  
**预计完成**: 2025-12-25  
**状态**: 🔄 进行中

---

## 🎯 Week 2 目标

实现 AeroTest AI 五层漏斗的**第二层 (L2): 启发式属性匹配**，基于 L1 提取的槽位信息，在 DOM 树中精确匹配目标元素。

### 核心功能

```
L1 槽位 + DOM 状态 ──> L2 属性匹配 ──> 候选元素列表

ActionSlot {                        MatchResult[] {
  keywords: ["提交", "submit"],        [
  target_type: BUTTON,                  {element: button#submit, score: 0.95},
}                                       {element: button.primary, score: 0.85},
                                      ]
+ DOM State                         }
```

---

## 📋 任务分解

### Day 1: 属性匹配器 (AttributeMatcher)

**功能**: 基于元素属性匹配关键词

**核心能力**:
```python
class AttributeMatcher:
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
        """按属性匹配元素"""
```

**交付物**:
- attribute_matcher.py
- test_attribute_matcher.py

### Day 2: 文本匹配器 (TextMatcher)

**功能**: 基于文本内容匹配（精确/模糊/包含）

**核心能力**:
```python
class TextMatcher:
    def exact_match(self, text: str, keyword: str) -> float:
        """精确匹配"""
    
    def fuzzy_match(self, text: str, keyword: str) -> float:
        """模糊匹配（rapidfuzz）"""
    
    def contains_match(self, text: str, keyword: str) -> float:
        """包含匹配"""
```

**交付物**:
- text_matcher.py
- test_text_matcher.py

### Day 3: 类型匹配器 (TypeMatcher)

**功能**: 基于元素类型筛选

**核心能力**:
```python
class TypeMatcher:
    def match_by_type(
        self,
        elements: list[EnhancedDOMTreeNode],
        target_type: str,
    ) -> list[EnhancedDOMTreeNode]:
        """按类型筛选元素"""
    
    def match_by_role(
        self,
        elements: list[EnhancedDOMTreeNode],
        role: str,
    ) -> list[EnhancedDOMTreeNode]:
        """按 ARIA role 筛选"""
```

**交付物**:
- type_matcher.py
- test_type_matcher.py

### Day 4: 评分器 (Scorer)

**功能**: 计算综合匹配得分

**核心能力**:
```python
@dataclass
class MatchResult:
    element: EnhancedDOMTreeNode
    score: float
    matched_attributes: dict[str, float]
    match_reasons: list[str]

class Scorer:
    def calculate_score(
        self,
        element: EnhancedDOMTreeNode,
        keywords: list[str],
        target_type: Optional[str],
    ) -> MatchResult:
        """计算综合得分"""
```

**交付物**:
- scorer.py
- match_result.py
- test_scorer.py

### Day 5-7: L2 引擎和集成

**功能**: 整合所有 L2 组件

**核心能力**:
```python
class L2Engine(BaseFunnelLayer):
    def match_elements(
        self,
        dom_state: SerializedDOMState,
        slot: ActionSlot,
    ) -> list[MatchResult]:
        """匹配元素"""
        # 1. 类型筛选
        # 2. 属性匹配
        # 3. 评分排序
        # 4. 返回 Top-N
```

**交付物**:
- l2_engine.py (更新)
- test_l2_engine.py
- l2_engine_usage.py
- Week2完成总结.md

---

## 🎯 Week 2 验收标准

| 标准 | 目标 | 当前 |
|------|------|------|
| **代码量** | > 1500 行 | 0 |
| **测试数** | > 40 个 | 0 |
| **测试覆盖率** | > 85% | - |
| **属性匹配准确率** | > 85% | - |
| **L2 处理时间** | < 100ms (500 元素) | - |
| **文档完整性** | 完整 | - |

---

## 📊 预期交付

```
aerotest/core/funnel/l2/
├── attribute_matcher.py      (~300 行)
├── text_matcher.py            (~200 行)
├── type_matcher.py            (~200 行)
├── scorer.py                  (~250 行)
├── match_result.py            (~100 行)
└── l2_engine.py               (~300 行)

tests/unit/funnel/
├── test_attribute_matcher.py  (~150 行)
├── test_text_matcher.py       (~150 行)
├── test_type_matcher.py       (~120 行)
├── test_scorer.py             (~150 行)
└── test_l2_engine.py          (~200 行)

examples/
└── l2_engine_usage.py         (~250 行)

总计: ~2500 行
```

---

**Week 2 开始！** 🚀

