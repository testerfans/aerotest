# Phase 3: L3-L5 层实施计划

**开始日期**: 2025-12-18  
**预计完成**: 2026-01-10 (3 周)  
**状态**: 🔄 进行中

---

## 🎯 Phase 3 总体目标

实现 AeroTest AI 五层漏斗的**高级定位能力 (L3-L5)**，解决传统自动化无法处理的复杂场景：
- **L3**: 空间布局推理 - 解决非标准控件定位
- **L4**: AI 推理 - 处理模糊和复杂逻辑
- **L5**: 视觉识别 - 处理 Canvas 和极端非标准 UI

### 核心价值

```
L1-L2 覆盖: 85% 简单场景 ✅
L3 增强:    +10% 非标准控件 🎯
L4 增强:    +3% 复杂逻辑 🎯
L5 增强:    +2% 极端场景 🎯
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
总覆盖:     100% 全场景 🎉
```

---

## 📋 Week 1: L3 空间布局推理

### 目标

使用空间位置关系和锚点定位解决非标准控件问题。

### 核心功能

```python
# L3 典型场景
指令: "点击用户名输入框右边的清除按钮"

L1-L2 失败: 清除按钮没有明确的 ID/文本
L3 成功:    1. 找到 "用户名输入框" (锚点)
           2. 在其右侧搜索 (邻近检测)
           3. 检测事件监听器 (clickable)
           4. 返回清除按钮 ✅
```

### 核心组件

#### 1. 锚点定位器 (AnchorLocator)

**功能**: 识别并定位锚点元素

```python
class AnchorLocator:
    """锚点定位器
    
    从指令中识别锚点元素（参照物）
    """
    
    def extract_anchor(self, instruction: str) -> Optional[AnchorInfo]:
        """
        提取锚点信息
        
        Examples:
            "用户名输入框右边的按钮" -> 锚点: "用户名输入框"
            "搜索框下方的结果列表" -> 锚点: "搜索框"
        """
        
    def locate_anchor(
        self,
        anchor_info: AnchorInfo,
        dom_state: SerializedDOMState,
    ) -> Optional[EnhancedDOMTreeNode]:
        """定位锚点元素"""

@dataclass
class AnchorInfo:
    """锚点信息"""
    description: str        # 锚点描述
    direction: Direction    # 方向（上/下/左/右）
    distance: Optional[str] # 距离（近/远/N像素）
    target_description: str # 目标描述
```

#### 2. 邻近检测器 (ProximityDetector)

**功能**: 基于空间位置关系查找元素

```python
class ProximityDetector:
    """邻近检测器
    
    基于空间位置关系查找元素
    """
    
    def find_nearby_elements(
        self,
        anchor: EnhancedDOMTreeNode,
        direction: Direction,
        max_distance: float = 200.0,
    ) -> list[EnhancedDOMTreeNode]:
        """查找邻近元素"""
    
    def calculate_distance(
        self,
        elem1: EnhancedDOMTreeNode,
        elem2: EnhancedDOMTreeNode,
    ) -> float:
        """计算元素间距离"""
    
    def is_in_direction(
        self,
        anchor: EnhancedDOMTreeNode,
        element: EnhancedDOMTreeNode,
        direction: Direction,
    ) -> bool:
        """判断元素是否在指定方向"""

class Direction(Enum):
    """方向枚举"""
    LEFT = "left"
    RIGHT = "right"
    ABOVE = "above"
    BELOW = "below"
    INSIDE = "inside"
```

#### 3. 事件监听检测器 (EventListenerDetector)

**功能**: 检测动态事件监听器

```python
class EventListenerDetector:
    """事件监听检测器
    
    检测元素上的 JavaScript 事件监听器
    （利用 browser-use 的能力）
    """
    
    async def detect_listeners(
        self,
        element: EnhancedDOMTreeNode,
        cdp_session: CDPSession,
    ) -> list[str]:
        """检测事件监听器类型"""
    
    def has_click_listener(
        self,
        element: EnhancedDOMTreeNode,
    ) -> bool:
        """是否有点击监听器"""
```

#### 4. L3 引擎

```python
class L3Engine(BaseFunnelLayer):
    """L3 空间布局推理引擎"""
    
    def __init__(self):
        self.anchor_locator = AnchorLocator()
        self.proximity_detector = ProximityDetector()
        self.event_listener_detector = EventListenerDetector()
    
    async def process(
        self,
        context: FunnelContext,
        dom_state: SerializedDOMState,
    ) -> FunnelContext:
        """
        空间布局推理流程：
        1. 提取锚点信息
        2. 定位锚点元素
        3. 邻近搜索
        4. 事件监听验证
        5. 返回候选
        """
```

### 实施计划

**Day 1: 基础架构**
- 创建 L3 模块结构
- 定义数据类型（AnchorInfo, Direction, etc.）
- 基础工具函数

**Day 2: 锚点定位器**
- 实现锚点识别
- 实现锚点定位
- 单元测试

**Day 3: 邻近检测器**
- 实现距离计算
- 实现方向判断
- 实现邻近搜索
- 单元测试

**Day 4: 事件监听检测**
- 集成 CDP 事件监听查询
- 实现监听器检测
- 单元测试

**Day 5-7: L3 引擎**
- 整合所有组件
- 完整流程实现
- 集成测试
- 使用示例

---

## 📋 Week 2: L4 AI 推理

### 目标

使用 Qwen-Max/Plus 进行语义理解和复杂逻辑推理。

### 核心功能

```python
# L4 典型场景
指令: "选择最便宜的商品"

L1-L2-L3 失败: 需要比较价格逻辑
L4 成功:       1. 提取所有商品元素
               2. Qwen 提取价格信息
               3. Qwen 比较并选择最便宜
               4. 返回目标元素 ✅
```

### 核心组件

#### 1. Qwen 客户端

```python
class QwenClient:
    """Qwen API 客户端"""
    
    async def chat(
        self,
        messages: list[dict],
        model: str = "qwen-max",
    ) -> str:
        """调用 Qwen API"""

class QwenPromptBuilder:
    """Qwen Prompt 构建器"""
    
    def build_element_selection_prompt(
        self,
        instruction: str,
        candidates: list[EnhancedDOMTreeNode],
    ) -> list[dict]:
        """构建元素选择 prompt"""
```

#### 2. 上下文提取器

```python
class ContextExtractor:
    """上下文提取器
    
    从 DOM 中提取相关上下文信息
    """
    
    def extract_context(
        self,
        elements: list[EnhancedDOMTreeNode],
        instruction: str,
    ) -> dict:
        """提取上下文"""
```

#### 3. L4 引擎

```python
class L4Engine(BaseFunnelLayer):
    """L4 AI 推理引擎"""
    
    async def process(
        self,
        context: FunnelContext,
        dom_state: SerializedDOMState,
    ) -> FunnelContext:
        """
        AI 推理流程：
        1. 获取 L2/L3 候选
        2. 提取上下文
        3. 构建 prompt
        4. 调用 Qwen
        5. 解析结果
        """
```

---

## 📋 Week 3: L5 视觉识别

### 目标

使用 Qwen2-VL 进行视觉识别，处理 Canvas 和图像元素。

### 核心功能

```python
# L5 典型场景
指令: "点击红色的购物车图标"

L1-L2-L3-L4 失败: 图标在 Canvas 中，无 DOM 信息
L5 成功:          1. 截取页面截图
                  2. Qwen2-VL 识别红色购物车图标
                  3. 返回坐标位置
                  4. 点击坐标 ✅
```

### 核心组件

#### 1. 截图服务

```python
class ScreenshotService:
    """截图服务"""
    
    async def capture_screenshot(
        self,
        cdp_session: CDPSession,
    ) -> bytes:
        """截取页面截图"""
    
    async def capture_element(
        self,
        element: EnhancedDOMTreeNode,
        cdp_session: CDPSession,
    ) -> bytes:
        """截取元素截图"""
```

#### 2. Qwen2-VL 客户端

```python
class Qwen2VLClient:
    """Qwen2-VL 视觉模型客户端"""
    
    async def identify_element(
        self,
        image: bytes,
        description: str,
    ) -> Optional[BoundingBox]:
        """识别元素位置"""

@dataclass
class BoundingBox:
    """边界框"""
    x: float
    y: float
    width: float
    height: float
```

#### 3. L5 引擎

```python
class L5Engine(BaseFunnelLayer):
    """L5 视觉识别引擎"""
    
    async def process(
        self,
        context: FunnelContext,
        dom_state: SerializedDOMState,
    ) -> FunnelContext:
        """
        视觉识别流程：
        1. 截取截图
        2. 调用 Qwen2-VL
        3. 解析坐标
        4. 返回结果
        """
```

---

## 📊 Phase 3 预期交付

### 代码统计

```
aerotest/core/funnel/l3/
├── anchor_locator.py         (~300 行)
├── proximity_detector.py     (~250 行)
├── event_listener.py         (~200 行)
└── l3_engine.py              (~300 行)

aerotest/core/funnel/l4/
├── qwen_client.py            (~250 行)
├── context_extractor.py      (~200 行)
├── prompt_builder.py         (~200 行)
└── l4_engine.py              (~250 行)

aerotest/core/funnel/l5/
├── screenshot_service.py     (~200 行)
├── qwen2vl_client.py         (~250 行)
└── l5_engine.py              (~200 行)

tests/unit/funnel/
├── test_l3_*.py              (~500 行)
├── test_l4_*.py              (~400 行)
└── test_l5_*.py              (~300 行)

总计: ~3500 行
```

### 测试覆盖

- L3: 30+ 单元测试
- L4: 20+ 单元测试
- L5: 15+ 单元测试
- **总计**: 65+ 测试

---

## 🎯 Phase 3 验收标准

| 标准 | 目标 |
|------|------|
| **代码量** | > 3000 行 |
| **测试数** | > 60 个 |
| **测试覆盖率** | > 80% |
| **L3 准确率** | > 75% (非标准场景) |
| **L4 准确率** | > 70% (复杂逻辑) |
| **L5 准确率** | > 60% (视觉识别) |
| **L1-L5 综合覆盖** | > 95% (所有场景) |

---

## 🚀 Phase 3 开始！

**Week 1 Day 1: 立即开始 L3 基础架构！** 🎯

