# AeroTest AI 2.0 技术架构设计

## 文档信息
- **版本**：v1.0
- **创建日期**：2025-12-18
- **架构策略**：基于 browser-use 全面复用 + AeroTest 五层漏斗扩展
- **技术选型**：CDP (Chrome DevTools Protocol)

---

## 目录
1. [架构决策](#1-架构决策)
2. [整体架构](#2-整体架构)
3. [browser-use 复用方案](#3-browser-use-复用方案)
4. [五层漏斗引擎设计](#4-五层漏斗引擎设计)
5. [核心模块设计](#5-核心模块设计)
6. [数据流设计](#6-数据流设计)
7. [接口设计](#7-接口设计)
8. [部署架构](#8-部署架构)

---

## 1. 架构决策

### 1.1 为什么选择 browser-use + CDP？

#### 决策对比

| 方案 | 开发时间 | 性能 | 功能完整性 | 维护成本 | 决策 |
|------|---------|------|-----------|---------|------|
| Playwright | 6-9周 | ⭐⭐⭐⭐ | 90% (L3缺陷) | 低 | ❌ |
| 纯 CDP 自研 | 13-20周 | ⭐⭐⭐⭐⭐ | 100% | 极高 | ❌ |
| **browser-use + CDP** | **3-4周** | **⭐⭐⭐⭐⭐** | **100%** | **中** | **✅ 采用** |

#### 核心优势

```python
✅ 开发效率最高
   - 复用 browser-use 7000+ 行生产级代码
   - 节省 10-16 周开发时间
   - 专注于五层漏斗和 OODA 引擎

✅ 性能最优
   - CDP 原生性能（比 Playwright 快 20-50%）
   - 事件响应 < 1ms（Playwright 5-10ms）
   - 启动速度快 3-10 倍

✅ 功能完整
   - 支持事件监听器检测（L3 层关键能力）
   - 完整的 DOM 提取和分析能力
   - 成熟的 Browser Session 管理

✅ 生产验证
   - browser-use 已有 5000+ Stars
   - 经过大量真实场景验证
   - 社区活跃，bug 修复及时
```

---

## 2. 整体架构

### 2.1 系统分层架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      应用层 (Application)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Web 前端     │  │ CLI 工具     │  │ CI/CD 插件   │         │
│  │ (React)      │  │ (Python CLI) │  │ (Jenkins等)  │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                             │ HTTP/WebSocket
┌─────────────────────────────▼─────────────────────────────────┐
│                     业务层 (Business)                          │
│  ┌────────────────────────────────────────────────────────┐  │
│  │            FastAPI 服务                                 │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │  │
│  │  │ 用例服务     │  │ 执行调度     │  │ 报告服务     │ │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘ │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │  │
│  │  │ 知识库服务   │  │ 配置服务     │  │ 权限服务     │ │  │
│  │  └──────────────┘  └──────────────┘  └──────────────┘ │  │
│  └────────────────────────────────────────────────────────┘  │
└────────────┬──────────────────────────┬───────────────────────┘
             │                          │
     ┌───────▼────────┐         ┌───────▼────────┐
     │  PostgreSQL    │         │     Redis      │
     │ (持久化存储)   │         │  (缓存/队列)   │
     └────────────────┘         └────────────────┘
             │
             │
┌────────────▼──────────────────────────────────────────────────┐
│                   引擎层 (Engine)                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │         AeroTest 五层漏斗引擎 (自研扩展)                 │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐             │ │
│  │  │ L1: 规则 │→ │ L2: 属性 │→ │ L3: 空间 │→ L4/L5      │ │
│  │  └──────────┘  └──────────┘  └──────────┘             │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │  OODA 执行循环                                    │  │ │
│  │  │  Observe → Orient → Decide → Act                 │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────┘ │
│                             │                                 │
│  ┌─────────────────────────▼─────────────────────────────┐  │
│  │      browser-use 核心层 (复用)                         │  │
│  │  ┌──────────────────┐  ┌──────────────────┐          │  │
│  │  │ BrowserSession   │  │ DomService       │          │  │
│  │  │ (会话管理)       │  │ (DOM 提取)       │          │  │
│  │  └──────────────────┘  └──────────────────┘          │  │
│  │  ┌──────────────────┐  ┌──────────────────┐          │  │
│  │  │ DOM Serializer   │  │ Actor Layer      │          │  │
│  │  │ (元素序列化)     │  │ (元素交互)       │          │  │
│  │  └──────────────────┘  └──────────────────┘          │  │
│  └─────────────────────────┬─────────────────────────────┘  │
└────────────────────────────┼────────────────────────────────┘
                             │ CDP Protocol (WebSocket)
                             │
┌────────────────────────────▼────────────────────────────────┐
│                    驱动层 (Driver)                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              cdp-use (CDP 客户端)                     │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │  CDP Domains:                                   │  │  │
│  │  │  - Page: 页面控制                               │  │  │
│  │  │  - DOM: DOM 操作                                │  │  │
│  │  │  - Runtime: JavaScript 执行                     │  │  │
│  │  │  - Network: 网络拦截                            │  │  │
│  │  │  - DOMDebugger: 事件监听器检测                  │  │  │
│  │  │  - Accessibility: 可访问性树                    │  │  │
│  │  │  - Input: 输入模拟                              │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────┘
                             │ WebSocket
                             │
┌────────────────────────────▼────────────────────────────────┐
│                 浏览器层 (Browser)                           │
│              Chrome / Chromium                              │
└─────────────────────────────────────────────────────────────┘


外部服务：
┌──────────────────┐
│  阿里百炼 API     │  ← L4/L5 层调用
│  - Qwen-Max      │
│  - Qwen2-VL      │
└──────────────────┘
```

---

## 3. browser-use 复用方案

### 3.1 完全复用的模块（无需修改）

#### ✅ 1. BrowserSession (browser/session.py)

```python
复用内容：
=========
- CDP 连接管理
- Target 管理（多标签）
- Session 缓存
- 网络拦截
- Cookie 管理
- 事件订阅机制
- Watchdog 监控

复用方式：
=========
直接继承或包装使用：

from browser_use.browser import BrowserSession

class AeroTestBrowserSession(BrowserSession):
    """AeroTest 扩展的浏览器会话"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 添加 AeroTest 特定配置
        self.aerotest_config = {...}
    
    async def navigate_with_wait(self, url: str):
        """增强的导航（带智能等待）"""
        await self.navigate_to_url(url)
        # 添加 AeroTest 的智能等待逻辑
        await self._wait_for_page_stable()

价值：
=====
- 节省 3-4 周开发时间
- 获得生产级 Session 管理
- 完善的错误处理和重试机制
```

#### ✅ 2. DomService (dom/service.py)

```python
复用内容：
=========
- Accessibility Tree 提取
- DOM Tree 提取
- 计算样式批量获取
- 边界框批量获取
- iframe 递归处理
- 跨域检测

复用方式：
=========
直接使用或轻度包装：

from browser_use.dom import DomService

class AeroTestDomExtractor:
    def __init__(self, browser_session: BrowserSession):
        self.dom_service = DomService(
            browser_session=browser_session,
            cross_origin_iframes=True,  # 支持跨域 iframe
            paint_order_filtering=True,  # 过滤被遮挡元素
            max_iframes=100,
            max_iframe_depth=5
        )
    
    async def extract_for_l2(self, target_id: str):
        """为 L2 层提取 DOM"""
        enhanced_dom = await self.dom_service.get_enhanced_dom_tree(
            target_id=target_id
        )
        return enhanced_dom
    
    async def extract_for_l3(self, target_id: str):
        """为 L3 层提取 DOM（包含位置信息）"""
        enhanced_dom = await self.dom_service.get_enhanced_dom_tree(
            target_id=target_id
        )
        # enhanced_dom 包含完整的边界框和可见性信息
        return enhanced_dom

价值：
=====
- 节省 2-3 周开发时间
- 完善的 DOM 提取算法
- 支持复杂的 iframe 场景
```

#### ✅ 3. DOM Serializer (dom/serializer/)

```python
复用内容：
=========
- DOMTreeSerializer: 元素序列化和过滤
- ClickableElementDetector: 可交互元素检测
- PaintOrderRemover: 绘制顺序过滤

复用方式：
=========
直接使用（这是最有价值的部分）：

from browser_use.dom.serializer import DOMTreeSerializer
from browser_use.dom.serializer.clickable_elements import ClickableElementDetector

# L2 层使用
class L2AttributeMatcher:
    def __init__(self):
        self.detector = ClickableElementDetector()
    
    async def match(self, dom_tree, target: str):
        # 1. 序列化 DOM
        serializer = DOMTreeSerializer(
            root_node=dom_tree,
            enable_bbox_filtering=True,
            paint_order_filtering=True
        )
        serialized_state, timing = serializer.serialize_accessible_elements()
        
        # 2. 使用 browser-use 的可交互元素检测
        for node in self._traverse(dom_tree):
            if self.detector.is_clickable(node):
                # 检查属性匹配
                score = self._calculate_match_score(node, target)
                if score > 0.95:
                    return node
        
        return None

# L3 层使用
class L3SpatialLayout:
    async def find_by_spatial_layout(self, dom_tree, anchor_text: str):
        # 使用 browser-use 的边界框信息
        # dom_tree 已包含完整的位置信息
        anchor = self._find_anchor(dom_tree, anchor_text)
        
        # 使用 ClickableElementDetector 检测可交互元素
        detector = ClickableElementDetector()
        nearby = self._find_nearby_elements(anchor, 50)  # 50px 范围
        
        for element in nearby:
            if detector.is_clickable(element):
                return element

价值：
=====
- 节省 2-3 周开发时间
- 获得业界最佳的元素检测算法
- 30+ 个交互标签定义
- 20+ 个交互 role 定义
```

#### ✅ 4. Actor Layer (actor/)

```python
复用内容：
=========
- Page: 页面级操作
- Element: 元素级操作
- Mouse: 鼠标操作

复用方式：
=========
直接使用或包装：

from browser_use.actor import Page, Element

class AeroTestExecutor:
    """AeroTest 执行器"""
    
    def __init__(self, browser_session: BrowserSession):
        self.browser_session = browser_session
    
    async def execute_action(self, action: dict, target_id: str):
        """执行动作"""
        page = Page(
            browser_session=self.browser_session,
            target_id=target_id
        )
        
        if action['type'] == 'click':
            selector = action['selector']
            element = await page.query_selector(selector)
            await element.click()
        
        elif action['type'] == 'input':
            selector = action['selector']
            text = action['text']
            element = await page.query_selector(selector)
            await element.type(text)
        
        elif action['type'] == 'coordinate_click':
            # L5 层坐标点击
            mouse = await page.mouse
            await mouse.click(action['x'], action['y'])

价值：
=====
- 节省 1-2 周开发时间
- 完善的元素交互封装
- 支持坐标级操作
```

---

### 3.2 需要扩展的模块

#### ⚠️ 1. 事件监听器检测（L3 层关键能力）

```python
扩展原因：
=========
L3 层需要检测元素是否绑定了事件监听器
browser-use 没有直接暴露这个功能

扩展方式：
=========
在 DomService 基础上扩展：

from browser_use.dom import DomService

class AeroTestDomExtractor(DomService):
    """扩展的 DOM 提取器"""
    
    async def get_event_listeners(
        self,
        node_id: int,
        session_id: str
    ) -> list[str]:
        """
        获取元素的事件监听器（CDP 独有能力）
        
        使用 CDP DOMDebugger.getEventListeners
        """
        # 1. 获取 Remote Object
        result = await self.browser_session.cdp_client.send.DOM.resolveNode({
            'nodeId': node_id
        }, session_id=session_id)
        
        object_id = result['object']['objectId']
        
        # 2. 获取事件监听器
        listeners_result = await self.browser_session.cdp_client.send.DOMDebugger.getEventListeners({
            'objectId': object_id
        }, session_id=session_id)
        
        # 3. 提取事件类型
        event_types = [
            listener['type'] 
            for listener in listeners_result['listeners']
        ]
        
        return event_types
    
    async def get_enhanced_dom_tree_with_events(
        self,
        target_id: str
    ) -> EnhancedDOMTreeNode:
        """
        提取包含事件监听器信息的 DOM 树
        """
        # 1. 调用 browser-use 的基础方法
        dom_tree = await super().get_enhanced_dom_tree(target_id)
        
        # 2. 为每个元素添加事件监听器信息
        session_id = await self.browser_session.get_or_create_cdp_session(target_id)
        await self._add_event_listeners_to_tree(dom_tree, session_id)
        
        return dom_tree
    
    async def _add_event_listeners_to_tree(
        self,
        node: EnhancedDOMTreeNode,
        session_id: str
    ):
        """递归添加事件监听器信息"""
        if node.backend_node_id:
            try:
                listeners = await self.get_event_listeners(
                    node.backend_node_id,
                    session_id
                )
                node.event_listeners = listeners  # 扩展字段
            except:
                node.event_listeners = []
        
        # 递归处理子节点
        for child in node.children:
            await self._add_event_listeners_to_tree(child, session_id)

工作量：
=======
- 1-2 天开发
- 这是 L3 层的核心能力
```

#### ⚠️ 2. 自愈知识库（AeroTest 特有）

```python
扩展原因：
=========
browser-use 没有知识库功能
这是 AeroTest 的差异化能力

扩展方式：
=========
在 browser-use 基础上构建：

from browser_use.dom.serializer import DOMTreeSerializer

class SelfHealingKnowledgeBase:
    """自愈知识库"""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    async def learn_from_success(
        self,
        url_pattern: str,
        instruction: str,
        selector: str,
        dom_tree_hash: str,
        confidence: float,
        method: str  # 'l2', 'l3', 'l4', 'l5'
    ):
        """从成功的定位中学习"""
        knowledge = {
            'url_pattern': url_pattern,
            'instruction': instruction,
            'selector': selector,
            'dom_tree_hash': dom_tree_hash,
            'confidence': confidence,
            'method': method,
            'created_at': datetime.now(),
            'success_count': 1,
            'fail_count': 0,
            'status': 'pending_review'  # 待审核
        }
        
        await self.db.insert('knowledge_base', knowledge)
    
    async def query_knowledge(
        self,
        url: str,
        instruction: str,
        dom_tree: EnhancedDOMTreeNode
    ) -> dict | None:
        """查询知识库"""
        # 1. 计算当前页面的 DOM 树哈希
        dom_hash = self._calculate_dom_hash(dom_tree)
        
        # 2. 查询匹配的知识
        results = await self.db.query(
            'knowledge_base',
            filters={
                'url_pattern': self._match_url_pattern(url),
                'instruction': instruction,
                'dom_tree_hash': dom_hash,
                'status': 'approved'
            }
        )
        
        if results:
            # 返回置信度最高的
            return max(results, key=lambda x: x['confidence'])
        
        return None
    
    def _calculate_dom_hash(self, dom_tree: EnhancedDOMTreeNode) -> str:
        """
        计算 DOM 树结构哈希
        
        复用 browser-use 的 DOM Serializer
        """
        serializer = DOMTreeSerializer(
            root_node=dom_tree,
            enable_bbox_filtering=False,
            paint_order_filtering=False
        )
        
        # 提取结构特征
        structure = self._extract_structure(dom_tree)
        return hashlib.md5(structure.encode()).hexdigest()

工作量：
=======
- 1 周开发
- 这是 AeroTest 的核心差异化功能
```

---

### 3.3 browser-use 复用清单

| browser-use 模块 | 复用方式 | 工作量 | 价值 | 优先级 |
|-----------------|---------|--------|------|--------|
| **BrowserSession** | 直接复用/继承 | 0-1天 | ⭐⭐⭐⭐⭐ | P0 |
| **DomService** | 直接复用/扩展 | 1-2天 | ⭐⭐⭐⭐⭐ | P0 |
| **DOM Serializer** | 直接复用 | 0天 | ⭐⭐⭐⭐⭐ | P0 |
| **ClickableDetector** | 直接复用 | 0天 | ⭐⭐⭐⭐⭐ | P0 |
| **PaintOrderRemover** | 直接复用 | 0天 | ⭐⭐⭐⭐ | P1 |
| **Actor Layer** | 直接复用 | 0-1天 | ⭐⭐⭐⭐ | P0 |
| **Watchdog** | 选择性复用 | 1-2天 | ⭐⭐⭐ | P2 |
| **事件监听器检测** | 需要扩展 | 1-2天 | ⭐⭐⭐⭐⭐ | P0 |

**总工作量**：3-9 天（vs 完全自研的 13-20 周）

---

## 4. 五层漏斗引擎设计

### 4.1 五层漏斗与 browser-use 的集成

```python
┌────────────────────────────────────────────────────────────┐
│              五层漏斗引擎 (AeroTest 自研)                   │
└────────────────────────────────────────────────────────────┘

L1: 语义槽规则层
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
输入：用户指令（"点击提交按钮"）
处理：NLP 正则 + 同义词映射
输出：{action: "Click", target: "提交按钮", confidence: 1.0}

使用 browser-use：无（纯规则处理）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

L2: 结构化属性硬匹配
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
输入：target="提交按钮", target_id
处理：
  1. 调用 browser-use DomService 提取 DOM 树
  2. 调用 browser-use DOMTreeSerializer 序列化
  3. 调用 browser-use ClickableElementDetector 检测
  4. AeroTest 属性匹配和打分

核心代码：
┌─────────────────────────────────────────────────────┐
│ from browser_use.dom import DomService              │
│ from browser_use.dom.serializer import (            │
│     DOMTreeSerializer,                              │
│     ClickableElementDetector                        │
│ )                                                   │
│                                                     │
│ class L2AttributeMatcher:                           │
│     async def match(self, target, target_id):       │
│         # 1. 提取 DOM (browser-use)                 │
│         dom_tree = await self.dom_service.\         │
│             get_enhanced_dom_tree(target_id)        │
│                                                     │
│         # 2. 序列化 (browser-use)                   │
│         serializer = DOMTreeSerializer(dom_tree)    │
│         state, _ = serializer.serialize()           │
│                                                     │
│         # 3. 检测可交互 (browser-use)               │
│         detector = ClickableElementDetector()       │
│                                                     │
│         # 4. 属性匹配 (AeroTest 自研)              │
│         candidates = []                             │
│         for element in self._traverse(dom_tree):    │
│             if detector.is_clickable(element):      │
│                 score = self._match_score(          │
│                     element, target                 │
│                 )                                   │
│                 if score > 0.7:                     │
│                     candidates.append(...)          │
│                                                     │
│         # 5. 返回最佳候选                           │
│         if candidates:                              │
│             best = max(candidates,                  │
│                       key=lambda x: x['score'])     │
│             if best['score'] > 0.95:                │
│                 return best                         │
│         return None                                 │
└─────────────────────────────────────────────────────┘

使用 browser-use：
  ✅ DomService.get_enhanced_dom_tree()
  ✅ DOMTreeSerializer.serialize_accessible_elements()
  ✅ ClickableElementDetector.is_clickable()
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

L3: 空间布局锚点层
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
输入：target="手机号", target_id
处理：
  1. 调用 browser-use DomService 提取 DOM（含位置）
  2. AeroTest 查找锚点元素
  3. AeroTest 邻近探测
  4. 调用 AeroTestDomExtractor.get_event_listeners()
     检测事件监听器 ⭐ 关键能力
  5. 调用 browser-use ClickableElementDetector 验证

核心代码：
┌─────────────────────────────────────────────────────┐
│ from browser_use.dom import DomService              │
│ from browser_use.dom.serializer import \            │
│     ClickableElementDetector                        │
│ from aerotest.dom import AeroTestDomExtractor       │
│                                                     │
│ class L3SpatialLayout:                              │
│     async def find_by_spatial_layout(               │
│         self, target, target_id                     │
│     ):                                              │
│         # 1. 提取 DOM (browser-use + 扩展)          │
│         dom_tree = await self.dom_extractor.\       │
│             get_enhanced_dom_tree_with_events(      │
│                 target_id                           │
│             )                                       │
│                                                     │
│         # 2. 查找锚点 (AeroTest)                    │
│         anchor = self._find_anchor(                 │
│             dom_tree, target                        │
│         )                                           │
│                                                     │
│         # 3. 邻近探测 (AeroTest)                    │
│         nearby = self._find_nearby_elements(        │
│             anchor, proximity=50                    │
│         )                                           │
│                                                     │
│         # 4. 检测事件监听器 (扩展功能 ⭐)           │
│         detector = ClickableElementDetector()       │
│         for element in nearby:                      │
│             # 先检测标准可交互元素                  │
│             if detector.is_clickable(element):      │
│                 return element                      │
│                                                     │
│             # 再检测事件监听器（非标控件）          │
│             if element.event_listeners and \        │
│                ('click' in element.event_listeners  │
│                 or 'input' in ...):                 │
│                 return element                      │
│                                                     │
│         return None                                 │
└─────────────────────────────────────────────────────┘

使用 browser-use：
  ✅ DomService.get_enhanced_dom_tree()
  ✅ ClickableElementDetector.is_clickable()
  ✅ 扩展：AeroTestDomExtractor.get_event_listeners()
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

L4: 意图推理层
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
输入：target="删除第二条订单", target_id
处理：
  1. 调用 browser-use DomService 提取 DOM
  2. AeroTest 构建上下文（精简 DOM）
  3. AeroTest 调用阿里百炼 API
  4. AeroTest 解析 LLM 响应

使用 browser-use：
  ✅ DomService.get_enhanced_dom_tree()
  ✅ DOMTreeSerializer（用于精简 DOM）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

L5: 多模态视觉感知层
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
输入：target="关闭图标", target_id
处理：
  1. 调用 browser-use Page.screenshot() 截图
  2. AeroTest 调用 OmniParser 标识热区
  3. AeroTest 调用 Qwen2-VL 识别
  4. 调用 browser-use Mouse.click(x, y) 坐标点击

使用 browser-use：
  ✅ Page.screenshot()
  ✅ Mouse.click(x, y)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 4.2 五层漏斗完整代码示例

```python
# aerotest/core/funnel/engine.py

from browser_use.browser import BrowserSession
from browser_use.dom import DomService
from browser_use.dom.serializer import DOMTreeSerializer, ClickableElementDetector
from browser_use.actor import Page

from aerotest.dom import AeroTestDomExtractor
from aerotest.core.funnel.l1_rule import L1RuleMatcher
from aerotest.core.funnel.l2_attribute import L2AttributeMatcher
from aerotest.core.funnel.l3_spatial import L3SpatialLayoutMatcher
from aerotest.core.funnel.l4_reasoning import L4ReasoningMatcher
from aerotest.core.funnel.l5_vision import L5VisionMatcher
from aerotest.knowledge import SelfHealingKnowledgeBase

class FunnelEngine:
    """五层漏斗引擎"""
    
    def __init__(
        self,
        browser_session: BrowserSession,
        knowledge_base: SelfHealingKnowledgeBase
    ):
        self.browser_session = browser_session
        self.knowledge_base = knowledge_base
        
        # 初始化各层
        self.l1 = L1RuleMatcher()
        self.l2 = L2AttributeMatcher(browser_session)
        self.l3 = L3SpatialLayoutMatcher(browser_session)
        self.l4 = L4ReasoningMatcher(browser_session)
        self.l5 = L5VisionMatcher(browser_session)
    
    async def locate_element(
        self,
        instruction: str,
        target_id: str,
        url: str
    ) -> dict:
        """
        通过五层漏斗定位元素
        
        Args:
            instruction: 用户指令（如："点击提交按钮"）
            target_id: 目标 Target ID
            url: 当前 URL
        
        Returns:
            {
                'selector': 'button#submit',
                'confidence': 0.96,
                'method': 'l2',
                'time': 0.15
            }
        """
        import time
        
        # 0. 先查询知识库
        knowledge = await self.knowledge_base.query_knowledge(
            url=url,
            instruction=instruction
        )
        if knowledge:
            print(f"💡 知识库命中：{knowledge['selector']}")
            return {
                'selector': knowledge['selector'],
                'confidence': knowledge['confidence'],
                'method': 'knowledge_base',
                'time': 0.01
            }
        
        # 1. L1: 规则层
        start = time.time()
        result = await self.l1.match(instruction)
        if result:
            elapsed = time.time() - start
            print(f"✅ L1 层命中，耗时：{elapsed*1000:.0f}ms")
            result['time'] = elapsed
            return result
        
        # 2. L2: 属性匹配层
        start = time.time()
        result = await self.l2.match(instruction, target_id)
        if result:
            elapsed = time.time() - start
            print(f"✅ L2 层命中，耗时：{elapsed*1000:.0f}ms")
            result['time'] = elapsed
            
            # 学习到知识库
            await self._learn_to_knowledge_base(
                url, instruction, result
            )
            return result
        
        # 3. L3: 空间布局层
        start = time.time()
        result = await self.l3.match(instruction, target_id)
        if result:
            elapsed = time.time() - start
            print(f"✅ L3 层命中，耗时：{elapsed*1000:.0f}ms")
            result['time'] = elapsed
            
            # 学习到知识库
            await self._learn_to_knowledge_base(
                url, instruction, result
            )
            return result
        
        # 4. L4: AI 推理层
        start = time.time()
        result = await self.l4.match(instruction, target_id)
        if result:
            elapsed = time.time() - start
            print(f"✅ L4 层命中，耗时：{elapsed*1000:.0f}ms，Token：{result.get('tokens_used')}")
            result['time'] = elapsed
            
            # 学习到知识库（重要！）
            await self._learn_to_knowledge_base(
                url, instruction, result
            )
            return result
        
        # 5. L5: 视觉感知层
        start = time.time()
        result = await self.l5.match(instruction, target_id)
        if result:
            elapsed = time.time() - start
            print(f"✅ L5 层命中，耗时：{elapsed*1000:.0f}ms")
            result['time'] = elapsed
            
            # 视觉识别的结果也要学习
            await self._learn_to_knowledge_base(
                url, instruction, result
            )
            return result
        
        # 6. 全部失败
        print(f"❌ 五层漏斗全部失败")
        return None
    
    async def _learn_to_knowledge_base(
        self,
        url: str,
        instruction: str,
        result: dict
    ):
        """学习到知识库"""
        # 只学习 L2-L5 的成功结果
        if result['method'] in ['l2', 'l3', 'l4', 'l5']:
            # 获取当前 DOM 树（计算哈希）
            dom_tree = await self.l2.dom_extractor.get_enhanced_dom_tree(
                target_id=result.get('target_id')
            )
            
            await self.knowledge_base.learn_from_success(
                url_pattern=self._extract_url_pattern(url),
                instruction=instruction,
                selector=result.get('selector'),
                dom_tree_hash=self._calculate_dom_hash(dom_tree),
                confidence=result['confidence'],
                method=result['method']
            )
```

---

## 5. 核心模块设计

### 5.1 模块依赖关系

```
┌──────────────────────────────────────────────────────┐
│             AeroTest 自研模块                         │
├──────────────────────────────────────────────────────┤
│  ┌────────────────┐  ┌────────────────┐             │
│  │ OODA Engine    │  │ Funnel Engine  │             │
│  │ (执行循环)     │  │ (五层漏斗)     │             │
│  └────────┬───────┘  └────────┬───────┘             │
│           │                   │                      │
│  ┌────────▼───────────────────▼───────┐             │
│  │  Knowledge Base (自愈知识库)       │             │
│  └────────────────────────────────────┘             │
└───────────────────┬──────────────────────────────────┘
                    │ 依赖
┌───────────────────▼──────────────────────────────────┐
│          browser-use 复用模块                         │
├──────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  │
│  │BrowserSession│  │  DomService  │  │DOM Serial.│  │
│  └──────────────┘  └──────────────┘  └───────────┘  │
│  ┌──────────────┐  ┌──────────────┐                 │
│  │ Actor Layer  │  │Clickable Det.│                 │
│  └──────────────┘  └──────────────┘                 │
└───────────────────┬──────────────────────────────────┘
                    │
┌───────────────────▼──────────────────────────────────┐
│                cdp-use (CDP 客户端)                   │
└──────────────────────────────────────────────────────┘
                    │
┌───────────────────▼──────────────────────────────────┐
│               Chrome Browser                          │
└──────────────────────────────────────────────────────┘
```

### 5.2 目录结构设计

```
aerotest/
├── __init__.py
├── browser/                      # 浏览器管理（基于 browser-use）
│   ├── __init__.py
│   ├── session_manager.py       # Session 管理器（包装 BrowserSession）
│   └── pool.py                  # Browser Pool（多实例管理）
│
├── dom/                          # DOM 处理（扩展 browser-use）
│   ├── __init__.py
│   ├── extractor.py             # AeroTestDomExtractor（扩展 DomService）
│   └── event_detector.py        # 事件监听器检测（新增）
│
├── core/                         # 核心引擎（AeroTest 自研）
│   ├── __init__.py
│   ├── ooda/                    # OODA 执行循环
│   │   ├── __init__.py
│   │   ├── engine.py            # OODA Engine
│   │   └── observer.py          # 观察器
│   │
│   ├── funnel/                  # 五层漏斗
│   │   ├── __init__.py
│   │   ├── engine.py            # 漏斗引擎
│   │   ├── l1_rule.py           # L1 规则层
│   │   ├── l2_attribute.py      # L2 属性层
│   │   ├── l3_spatial.py        # L3 空间层
│   │   ├── l4_reasoning.py      # L4 推理层
│   │   └── l5_vision.py         # L5 视觉层
│   │
│   └── executor/                # 执行器
│       ├── __init__.py
│       ├── action_executor.py   # 动作执行（包装 Actor Layer）
│       └── validator.py         # 回执验证
│
├── knowledge/                    # 知识库（AeroTest 自研）
│   ├── __init__.py
│   ├── database.py              # 知识库存储
│   ├── matcher.py               # 知识匹配
│   └── learner.py               # 自愈学习
│
├── ai/                           # AI 集成（AeroTest 自研）
│   ├── __init__.py
│   ├── qwen_max.py              # Qwen-Max（L4）
│   ├── qwen_vl.py               # Qwen2-VL（L5）
│   └── prompt_builder.py        # Prompt 构建器
│
├── recovery/                     # 异常恢复（AeroTest 自研）
│   ├── __init__.py
│   ├── obstacle_cleaner.py      # 阻挡物清除
│   └── page_monitor.py          # 页面监控
│
└── utils/                        # 工具函数
    ├── __init__.py
    ├── dom_hash.py              # DOM 哈希计算
    └── matcher.py               # 字符串匹配

# 依赖 browser-use（作为第三方库）
# 安装：pip install browser-use
# 或者将 browser-use 作为 Git submodule
```

---

## 6. 数据流设计

### 6.1 用例执行完整数据流

```
1. 用户提交用例
   │
   ▼
2. FastAPI 接收请求
   │
   ▼
3. 任务入队（Redis Queue）
   │
   ▼
4. OODA Engine 取出任务
   │
   ▼
5. Observe (观察)
   ├─ 解析用例步骤："点击提交按钮"
   ├─ 获取当前页面状态
   │  └─ browser-use BrowserSession.get_state()
   └─ 检测阻挡物
      └─ AeroTest ObstacleCleaner
   │
   ▼
6. Orient (调整) - 五层漏斗定位
   │
   ├─ L1: 规则匹配
   │  └─ AeroTest L1RuleMatcher
   │
   ├─ L2: 属性匹配
   │  ├─ browser-use DomService.get_enhanced_dom_tree()
   │  ├─ browser-use DOMTreeSerializer.serialize()
   │  ├─ browser-use ClickableElementDetector.is_clickable()
   │  └─ AeroTest 属性打分和匹配
   │
   ├─ L3: 空间布局
   │  ├─ browser-use DomService.get_enhanced_dom_tree()
   │  ├─ AeroTest 查找锚点
   │  ├─ AeroTest 邻近探测
   │  ├─ AeroTest DomExtractor.get_event_listeners() ⭐
   │  └─ browser-use ClickableElementDetector.is_clickable()
   │
   ├─ L4: AI 推理
   │  ├─ browser-use DomService.get_enhanced_dom_tree()
   │  ├─ AeroTest 构建上下文（精简 DOM）
   │  ├─ AeroTest 调用阿里百炼 API (Qwen-Max)
   │  └─ AeroTest 解析响应
   │
   └─ L5: 视觉识别
      ├─ browser-use Page.screenshot()
      ├─ AeroTest 调用 OmniParser
      ├─ AeroTest 调用 Qwen2-VL
      └─ 返回坐标
   │
   ▼
7. Decide (决定)
   ├─ 验证定位结果
   ├─ 生成执行指令
   └─ 准备回执验证逻辑
   │
   ▼
8. Act (执行)
   ├─ 执行动作
   │  ├─ browser-use Page.query_selector()
   │  ├─ browser-use Element.click()
   │  └─ 或 browser-use Mouse.click(x, y)
   │
   ├─ 截图
   │  └─ browser-use Page.screenshot()
   │
   ├─ 验证回执
   │  └─ browser-use DomService.get_enhanced_dom_tree()
   │  └─ AeroTest 验证 DOM 变化
   │
   └─ 记录日志
      ├─ 步骤信息
      ├─ 漏斗层级
      ├─ 耗时
      ├─ Token 消耗（L4/L5）
      └─ 截图路径
   │
   ▼
9. 学习到知识库
   └─ AeroTest SelfHealingKnowledgeBase.learn()
   │
   ▼
10. 生成报告
    └─ HTML 报告 + CDP Trace
```

---

## 7. 接口设计

### 7.1 核心接口

#### 1. 用例执行接口

```python
POST /api/v1/cases/{case_id}/execute

Request:
{
    "environment": "test",           # 环境
    "browser_config": {
        "headless": true,
        "viewport": {"width": 1920, "height": 1080}
    },
    "ai_config": {
        "model": "qwen-max",
        "token_budget": 5000
    }
}

Response:
{
    "execution_id": "exec_xxx",
    "status": "running",
    "started_at": "2025-12-18T10:00:00Z"
}
```

#### 2. 执行状态查询

```python
GET /api/v1/executions/{execution_id}

Response:
{
    "execution_id": "exec_xxx",
    "status": "completed",  # running/completed/failed
    "progress": {
        "total_steps": 10,
        "completed_steps": 10,
        "current_step": "验证页面显示'欢迎回来'"
    },
    "result": {
        "success": true,
        "duration": 15.3,  # 秒
        "steps": [
            {
                "step": 1,
                "instruction": "点击提交按钮",
                "method": "l2",  # L2 层命中
                "confidence": 0.96,
                "time": 0.15,
                "screenshot": "screenshots/step_1.png"
            },
            ...
        ],
        "ai_cost": {
            "tokens_used": 1234,
            "estimated_cost": 0.05  # 元
        }
    }
}
```

#### 3. 知识库查询

```python
GET /api/v1/knowledge?url_pattern=/product/\d+&instruction=点击购买按钮

Response:
{
    "matches": [
        {
            "selector": "button.buy-btn",
            "confidence": 0.95,
            "success_rate": 0.98,
            "last_used": "2025-12-18T09:00:00Z",
            "created_at": "2025-12-15T10:00:00Z"
        }
    ]
}
```

---

## 8. 部署架构

### 8.1 单机部署（MVP）

```
┌──────────────────────────────────────────────────┐
│           单机服务器 (8C16G)                      │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │  Docker Compose                            │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐ │ │
│  │  │ FastAPI  │  │PostgreSQL│  │  Redis   │ │ │
│  │  │ (AeroTest)│  │          │  │          │ │ │
│  │  └──────────┘  └──────────┘  └──────────┘ │ │
│  │  ┌──────────┐  ┌──────────┐               │ │
│  │  │  Nginx   │  │  Chrome  │               │ │
│  │  │ (前端)   │  │(Headless)│               │ │
│  │  └──────────┘  └──────────┘               │ │
│  └────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────┘

并发能力：10 个浏览器实例
适用场景：个人/小团队
```

### 8.2 分布式部署（生产）

```
┌─────────────────────────────────────────────────────┐
│                 负载均衡 (Nginx)                     │
└─────────────┬───────────────────────────────────────┘
              │
     ┌────────┴────────┐
     │                 │
┌────▼─────┐      ┌────▼─────┐
│ API 节点1 │      │ API 节点2 │
│ (FastAPI) │      │ (FastAPI) │
└─────┬─────┘      └─────┬─────┘
      │                  │
      └──────────┬───────┘
                 │
        ┌────────▼────────┐
        │   PostgreSQL    │
        │ (主从复制)       │
        └─────────────────┘
                 │
        ┌────────▼────────┐
        │   Redis Cluster │
        │ (队列/缓存)      │
        └─────────────────┘
                 │
     ┌───────────┴───────────┐
     │                       │
┌────▼─────┐  ┌──────┐  ┌────▼─────┐
│执行节点 1 │  │ ...  │  │执行节点 N │
│ (8C16G)  │  │      │  │ (8C16G)  │
│ 10并发   │  │      │  │ 10并发   │
└──────────┘  └──────┘  └──────────┘

总并发能力：N * 10
适用场景：企业级
```

---

## 9. 开发计划

### 9.1 MVP 开发（3-4 周）

#### Week 1: 基础集成
```
□ 集成 browser-use (安装和配置)
□ 包装 BrowserSession
□ 包装 DomService
□ 实现 L1 规则层
□ 实现 L2 属性层（使用 browser-use）
```

#### Week 2: 核心功能
```
□ 扩展事件监听器检测
□ 实现 L3 空间层
□ 实现简单的 OODA 循环
□ 实现动作执行器（使用 browser-use Actor）
```

#### Week 3: AI 集成
```
□ 集成阿里百炼 API
□ 实现 L4 推理层
□ 实现 L5 视觉层
□ 实现知识库（基础版）
```

#### Week 4: 测试和报告
```
□ 集成测试
□ 性能优化
□ 实现 HTML 报告
□ 编写文档
```

### 9.2 完整开发（4-6 个月）

见需求文档的实施路线图。

---

## 10. 附录

### 10.1 依赖清单

```toml
[project.dependencies]
# browser-use 及其依赖
browser-use = ">=0.11.2"
cdp-use = ">=1.4.4"
pydantic = ">=2.11.5"

# AeroTest 特有依赖
fastapi = ">=0.104.0"
uvicorn = ">=0.24.0"
sqlalchemy = ">=2.0.0"
alembic = ">=1.12.0"
asyncpg = ">=0.29.0"
redis = ">=5.0.0"
alibabacloud-sdk = ">=1.0.0"  # 阿里百炼

# 前端
# (另外的 Node.js 项目)
```

### 10.2 参考资料

- [browser-use GitHub](https://github.com/browser-use/browser-use)
- [CDP Protocol](https://chromedevtools.github.io/devtools-protocol/)
- [阿里百炼平台](https://www.aliyun.com/product/bailian)

---

**文档结束**

