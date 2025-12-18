# Week 3: Session 管理 - 实施计划

**目标**: 创建轻量级 CDP 集成，让 DomService 能够从真实浏览器获取 DOM

**预计时间**: 3-4 天  
**复杂度**: ⭐⭐⭐⭐ (高)

---

## 🎯 核心目标

让 AeroTest 能够：
1. ✅ 连接到 Chrome/Edge（通过 CDP）
2. ✅ 获取当前页面的 DOM 树
3. ✅ 使用 DomService 处理 DOM
4. ✅ 执行基本的页面操作

---

## 📊 browser-use 分析

### 文件大小

| 文件 | 行数 | 复杂度 | 复用策略 |
|------|------|--------|---------|
| `session.py` | 3542 | 超高 ⭐⭐⭐⭐⭐ | ❌ **不直接复用** |
| `session_manager.py` | 895 | 高 ⭐⭐⭐⭐ | ⚠️ 简化版本 |
| `profile.py` | ~200 | 低 ⭐⭐ | ✅ 部分复用 |
| `views.py` | ~150 | 低 ⭐ | ✅ 直接复用 |

### 为什么不直接复用 session.py？

**问题**:
1. **太庞大**: 3542 行代码
2. **依赖太多**: EventBus, CloudBrowser, Watchdogs, VideoRecorder...
3. **功能过载**: 包含很多我们暂时不需要的功能
   - Cloud Browser 集成 (~500 行)
   - 视频录制 (~300 行)
   - Demo 模式 (~200 行)
   - 10+ 个 Watchdogs

**我们真正需要的** (Week 3):
- CDP 连接管理 (~200 行)
- 页面导航 (~100 行)
- DOM 获取 (~300 行)
- 基本操作（点击、输入）(~200 行)

**总计**: ~800 行（只需要原文件的 22%）

---

## 🏗️ Week 3 架构设计

### 方案选择

我们采用 **轻量级改造方案**：

```
AeroTest Week 3 架构
═══════════════════════════════════════════════════

aerotest/browser/cdp/          (新模块)
├── connection.py              # CDP WebSocket 连接
├── session.py                 # 简化的 CDP 会话
├── page.py                    # 页面操作
└── types.py                   # CDP 类型定义

集成点:
aerotest/browser/dom/
└── dom_service.py             # 扩展：添加 from_cdp_session()
```

### 与 browser-use 的对比

| 功能模块 | browser-use | AeroTest Week 3 | 说明 |
|---------|------------|----------------|------|
| **CDP 连接** | ✅ 完整 | ✅ 简化版 | 只保留核心连接 |
| **会话管理** | ✅ 复杂（多会话池） | ✅ 简单（单会话） | 暂不需要会话池 |
| **DOM 获取** | ✅ 完整 | ✅ 完整 | 复用核心算法 |
| **页面操作** | ✅ 全面 | ✅ 基础 | 点击、输入、导航 |
| **EventBus** | ✅ 复杂事件系统 | ❌ 不需要 | 使用简单回调 |
| **Cloud Browser** | ✅ 完整集成 | ❌ 不需要 | 只连接本地浏览器 |
| **视频录制** | ✅ 支持 | ❌ 不需要 | 后续添加 |
| **Watchdogs** | ✅ 10+ 个 | ❌ 不需要 | 后续添加 |

---

## 📋 实施步骤

### Step 1: CDP 类型定义 (~50 行)

```python
# aerotest/browser/cdp/types.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class CDPConnectionConfig:
    """CDP 连接配置"""
    host: str = "localhost"
    port: int = 9222
    timeout: float = 30.0
    
@dataclass
class PageInfo:
    """页面信息"""
    url: str
    title: str
    target_id: str
    session_id: str
```

### Step 2: CDP 连接管理 (~200 行)

```python
# aerotest/browser/cdp/connection.py
import asyncio
from cdp_use import CDPClient

class CDPConnection:
    """简化的 CDP WebSocket 连接"""
    
    def __init__(self, config: CDPConnectionConfig):
        self.config = config
        self.client: Optional[CDPClient] = None
    
    async def connect(self) -> CDPClient:
        """连接到 Chrome DevTools Protocol"""
        ...
    
    async def disconnect(self):
        """断开连接"""
        ...
```

### Step 3: CDP 会话 (~300 行)

```python
# aerotest/browser/cdp/session.py
from aerotest.browser.cdp.connection import CDPConnection

class CDPSession:
    """简化的 CDP 会话
    
    功能：
    - 连接管理
    - 页面导航
    - DOM 获取
    """
    
    def __init__(self, connection: CDPConnection):
        self.connection = connection
        self.target_id: Optional[str] = None
        self.session_id: Optional[str] = None
    
    async def navigate(self, url: str):
        """导航到 URL"""
        ...
    
    async def get_dom_tree(self) -> EnhancedDOMTreeNode:
        """获取 DOM 树（复用 browser-use 核心算法）"""
        ...
```

### Step 4: 页面操作 (~250 行)

```python
# aerotest/browser/cdp/page.py
class CDPPage:
    """页面操作接口"""
    
    def __init__(self, session: CDPSession):
        self.session = session
    
    async def click(self, selector: str):
        """点击元素"""
        ...
    
    async def type(self, selector: str, text: str):
        """输入文本"""
        ...
    
    async def screenshot(self) -> bytes:
        """截图"""
        ...
```

### Step 5: 集成到 DomService (~100 行)

```python
# 扩展 aerotest/browser/dom/dom_service.py
class DomService:
    # ... 现有方法 ...
    
    @classmethod
    async def from_cdp_session(
        cls,
        session: CDPSession,
        **kwargs
    ) -> tuple["DomService", SerializedDOMState]:
        """从 CDP 会话创建 DomService 并获取 DOM
        
        这是 Week 3 的核心集成方法
        """
        service = cls(**kwargs)
        root_node = await session.get_dom_tree()
        state, timing = service.serialize_dom_tree(root_node)
        return service, state
```

---

## 🎯 Week 3 交付标准

### 必须完成 ✅

1. ✅ CDP 连接（本地 Chrome/Edge）
2. ✅ 获取 DOM 树
3. ✅ 基础页面操作（导航、点击、输入）
4. ✅ 与 DomService 集成
5. ✅ 完整使用示例

### 可选功能 ⚠️

- ⚠️ 会话池管理（后续添加）
- ⚠️ 多标签页支持（后续添加）
- ⚠️ Cookie 管理（后续添加）
- ⚠️ 代理设置（后续添加）

### 不实现 ❌

- ❌ EventBus
- ❌ Cloud Browser
- ❌ 视频录制
- ❌ Watchdogs
- ❌ Demo 模式

---

## 📊 预计代码量

| 模块 | 预计行数 | 状态 |
|------|---------|------|
| `types.py` | 50 | 待开发 |
| `connection.py` | 200 | 待开发 |
| `session.py` | 300 | 待开发 |
| `page.py` | 250 | 待开发 |
| `dom_service.py` (扩展) | 100 | 待开发 |
| 示例代码 | 200 | 待开发 |
| **总计** | **~1100 行** | 0% |

---

## 🔑 关键代码复用点

### 从 browser-use 复用的核心算法

1. **DOM 树构建** (session.py 中)
   - `_get_all_trees()` - 获取 DOM/AX/Snapshot 树
   - `_get_ax_tree_for_all_frames()` - 获取辅助功能树
   - `get_dom_tree()` - 构建增强 DOM 树

2. **元素定位** (session.py 中)
   - `_resolve_object_id_for_backend_node_id()` - 解析对象 ID
   - `get_element_offset()` - 获取元素偏移

3. **页面操作** (session.py 中)
   - `_execute_cdp_click()` - CDP 点击
   - `_execute_cdp_input()` - CDP 输入

---

## 📝 使用示例（目标）

### 示例 1: 基础使用

```python
from aerotest.browser.cdp import CDPSession, CDPConnectionConfig
from aerotest.browser.dom import DomService

# 1. 创建连接配置
config = CDPConnectionConfig(
    host="localhost",
    port=9222,
)

# 2. 创建会话
async with CDPSession.connect(config) as session:
    # 3. 导航到页面
    await session.navigate("https://example.com")
    
    # 4. 获取 DOM 并处理
    service, state = await DomService.from_cdp_session(session)
    
    # 5. 使用 DomService
    llm_repr = service.get_llm_representation(state)
    print(f"找到 {len(state.selector_map)} 个可交互元素")
```

### 示例 2: 页面操作

```python
async with CDPSession.connect(config) as session:
    page = session.page
    
    # 导航
    await page.navigate("https://example.com")
    
    # 点击
    await page.click("#submit-button")
    
    # 输入
    await page.type("#search-input", "AeroTest AI")
    
    # 截图
    screenshot = await page.screenshot()
```

---

## 🎓 设计原则

### 1. 简单优先

- ✅ 只实现核心功能
- ✅ 避免过度设计
- ✅ 代码清晰易懂

### 2. 智能复用

- ✅ 复用 browser-use 的核心算法
- ✅ 不复用复杂的框架代码
- ✅ 适配到 AeroTest 的架构

### 3. 渐进式开发

- ✅ Week 3: 基础 CDP 集成
- ⏸️ Week 4: 测试和优化
- ⏸️ 未来: 高级功能（会话池、多标签等）

---

## 📈 对比：browser-use vs AeroTest Week 3

### browser-use (全功能)

```
browser_use/browser/session.py (3542 行)
├── BrowserSession (超级类)
│   ├── CDP 基础 (~500 行)
│   ├── EventBus 集成 (~300 行)
│   ├── Cloud Browser (~500 行)
│   ├── 视频录制 (~300 行)
│   ├── Watchdogs (~10 个, ~800 行)
│   ├── Demo 模式 (~200 行)
│   └── 其他功能 (~900 行)
└── 3 个辅助类 (~40 行)

总复杂度: ⭐⭐⭐⭐⭐ (极高)
维护难度: ⭐⭐⭐⭐⭐ (极高)
```

### AeroTest Week 3 (精简版)

```
aerotest/browser/cdp/ (~900 行)
├── types.py (~50 行)
├── connection.py (~200 行)
├── session.py (~300 行)
└── page.py (~250 行)

总复杂度: ⭐⭐⭐ (中等)
维护难度: ⭐⭐ (简单)
```

**减少复杂度**: 从 3542 行 → 900 行（减少 75%）

---

## 🚧 风险和挑战

### 高风险 ⚠️

1. **CDP API 复杂性**
   - 风险: CDP 协议很复杂
   - 缓解: 只使用核心 API，复用 browser-use 经验

2. **异步编程**
   - 风险: 大量异步代码，容易出错
   - 缓解: 参考 browser-use 的异步模式

### 中风险 ⚠️

3. **浏览器兼容性**
   - 风险: Chrome/Edge 可能有细微差异
   - 缓解: 先支持 Chrome，后续添加 Edge

4. **错误处理**
   - 风险: 网络、超时、浏览器崩溃
   - 缓解: 完善的异常处理和重试机制

---

## 📅 时间规划

### Day 1: 基础设施 (4-6 小时)
- ✅ types.py
- ✅ connection.py
- ✅ 基础测试

### Day 2: 会话管理 (6-8 小时)
- ✅ session.py
- ✅ get_dom_tree() 集成
- ✅ 导航功能

### Day 3: 页面操作 (4-6 小时)
- ✅ page.py
- ✅ 点击、输入功能
- ✅ 截图功能

### Day 4: 集成和示例 (4-6 小时)
- ✅ DomService 扩展
- ✅ 完整示例
- ✅ 文档编写

**总计**: 18-26 小时（3-4 个工作日）

---

## ✅ 验收标准

### 功能验收

```python
# 这段代码必须能够运行
async def test_week3_complete():
    config = CDPConnectionConfig(host="localhost", port=9222)
    
    async with CDPSession.connect(config) as session:
        # 1. 导航
        await session.navigate("https://example.com")
        
        # 2. 获取 DOM
        service, state = await DomService.from_cdp_session(session)
        
        # 3. 验证
        assert len(state.selector_map) > 0
        assert state.llm_representation()
        
        # 4. 页面操作
        page = session.page
        await page.click("button")
        await page.type("input", "test")
        screenshot = await page.screenshot()
        
    print("✅ Week 3 验收通过！")
```

---

## 📚 参考资料

1. **browser-use 源码**
   - `browser_use/browser/session.py` - 会话管理
   - `browser_use/dom/service.py` - DOM 服务

2. **CDP 文档**
   - [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/)
   - [cdp_use 文档](https://github.com/HMaker/python-cdp)

3. **AeroTest 已完成模块**
   - Week 1: DOM Serializer
   - Week 2: DomService

---

**计划制定**: 2025-12-18  
**预计开始**: 立即  
**预计完成**: 2025-12-21

---

**准备好了吗？让我们开始 Week 3 的开发！** 🚀

