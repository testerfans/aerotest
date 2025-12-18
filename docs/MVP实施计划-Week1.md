# AeroTest AI 2.0 - MVP Week 1 实施计划

**开始日期**: 2025-12-18  
**目标**: 核心补齐（事件监听器 + OODA 循环）  
**状态**: 🚀 进行中

---

## 📋 Week 1 总览

### 目标

```
Week 1: 核心补齐
═══════════════════════════════════════════════════
✅ Day 1-2: 事件监听器检测（L3 增强）
⏸️ Day 3-5: OODA 循环基础版

交付物：
  1. EventListenerDetector 模块
  2. L3 引擎增强
  3. OODA Engine 基础版
  4. 端到端用例执行能力
```

---

## 📅 Day 1-2: 事件监听器检测

### 目标

实现 CDP 事件监听器检测，增强 L3 层对非标控件的识别能力。

### 实现内容

#### 1. 创建 EventListenerDetector 模块

```python
# aerotest/browser/dom/event_listener_detector.py

class EventListenerDetector:
    """事件监听器检测器
    
    使用 CDP DOMDebugger.getEventListeners 检测元素的事件监听器
    """
    
    async def get_event_listeners(
        self,
        cdp_client,
        node_id: int,
        session_id: str
    ) -> list[EventListenerInfo]:
        """
        获取元素的事件监听器
        
        Args:
            cdp_client: CDP 客户端
            node_id: DOM 节点 ID
            session_id: CDP Session ID
            
        Returns:
            事件监听器列表
        """
        # 1. 将 node_id 转换为 Remote Object
        result = await cdp_client.send(
            "DOM.resolveNode",
            {"nodeId": node_id},
            session_id=session_id
        )
        
        object_id = result["object"]["objectId"]
        
        # 2. 获取事件监听器
        listeners_result = await cdp_client.send(
            "DOMDebugger.getEventListeners",
            {"objectId": object_id},
            session_id=session_id
        )
        
        # 3. 解析事件类型
        event_listeners = []
        for listener in listeners_result.get("listeners", []):
            event_listeners.append(
                EventListenerInfo(
                    type=listener["type"],
                    use_capture=listener.get("useCapture", False),
                    passive=listener.get("passive", False),
                    once=listener.get("once", False),
                )
            )
        
        return event_listeners
```

#### 2. 扩展 DomService

```python
# aerotest/browser/dom/dom_service.py

class DomService:
    """DOM 服务（增强版）"""
    
    def __init__(self, cdp_session):
        self.cdp_session = cdp_session
        self.event_detector = EventListenerDetector()
    
    async def get_enhanced_dom_tree_with_events(
        self,
        target_id: str
    ) -> EnhancedDOMTreeNode:
        """
        获取包含事件监听器信息的 DOM 树
        """
        # 1. 获取基础 DOM 树
        dom_tree = await self.get_dom_tree(target_id)
        
        # 2. 为每个节点添加事件监听器信息
        session_id = await self.cdp_session.get_session_id(target_id)
        await self._add_event_listeners_to_tree(
            dom_tree,
            session_id
        )
        
        return dom_tree
    
    async def _add_event_listeners_to_tree(
        self,
        node: EnhancedDOMTreeNode,
        session_id: str
    ):
        """递归添加事件监听器"""
        if node.backend_node_id:
            try:
                listeners = await self.event_detector.get_event_listeners(
                    self.cdp_session.cdp_client,
                    node.backend_node_id,
                    session_id
                )
                node.event_listeners = listeners
            except:
                node.event_listeners = []
        
        # 递归处理子节点
        for child in node.children:
            await self._add_event_listeners_to_tree(child, session_id)
```

#### 3. 更新 L3 引擎

```python
# aerotest/core/funnel/l3/l3_engine.py

class L3Engine:
    """L3 空间布局推理引擎（增强版）"""
    
    async def process(self, context, dom_state):
        """处理（增强版：支持事件监听器检测）"""
        
        # ... 现有逻辑 ...
        
        # 对于邻近的元素，检查事件监听器
        for element in nearby_elements:
            # 标准可交互元素
            if element.is_clickable:
                candidates.append(element)
            
            # 非标准元素：检查事件监听器
            elif element.event_listeners:
                has_click = any(
                    l.type in ["click", "mousedown", "mouseup"]
                    for l in element.event_listeners
                )
                if has_click:
                    candidates.append(element)
        
        return context
```

### 验收标准

```
✅ EventListenerDetector 创建完成
✅ DomService 支持事件监听器检测
✅ L3 引擎可检测非标控件
✅ 单元测试通过
✅ 集成测试通过
```

---

## 📅 Day 3-5: OODA 循环基础版

### 目标

实现 OODA 执行循环，提供端到端用例执行能力。

### 架构设计

```
┌─────────────────────────────────────────────────┐
│              OODA Engine                        │
├─────────────────────────────────────────────────┤
│                                                 │
│  Observe (观察)                                 │
│  ├─ 解析指令                                    │
│  ├─ 获取 DOM 状态                               │
│  └─ 检测阻挡物（基础版）                       │
│                                                 │
│  Orient (定向)                                  │
│  ├─ 查询知识库（预留接口）                     │
│  └─ 五层漏斗定位 ✅                             │
│                                                 │
│  Decide (决策)                                  │
│  ├─ 验证元素可见性                              │
│  └─ 生成执行指令                                │
│                                                 │
│  Act (执行)                                     │
│  ├─ 执行动作                                    │
│  ├─ 截图                                        │
│  └─ 回执验证（基础版）                         │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 实现内容

#### 1. 创建 OODA Engine

```python
# aerotest/core/ooda/engine.py

class OODAEngine:
    """OODA 执行循环引擎"""
    
    def __init__(
        self,
        cdp_session: CDPSession,
        knowledge_base: Optional[KnowledgeBase] = None
    ):
        self.cdp_session = cdp_session
        self.knowledge_base = knowledge_base
        
        # 初始化五层漏斗
        self.l1_engine = L1Engine()
        self.l2_engine = L2Engine()
        self.l3_engine = L3Engine()
        self.l4_engine = L4Engine()
        self.l5_engine = L5Engine()
        
        # 初始化其他组件
        self.dom_service = DomService(cdp_session)
    
    async def execute_step(
        self,
        instruction: str,
        target_id: str
    ) -> StepResult:
        """
        执行单个步骤
        
        Args:
            instruction: 用户指令
            target_id: CDP Target ID
            
        Returns:
            步骤执行结果
        """
        logger.info(f"执行步骤: {instruction}")
        
        # 1. Observe: 观察
        observation = await self._observe(instruction, target_id)
        
        # 2. Orient: 定向（通过五层漏斗）
        element = await self._orient(
            instruction,
            observation.dom_state,
            observation.url
        )
        
        if not element:
            return StepResult(
                success=False,
                error="未找到目标元素",
                instruction=instruction
            )
        
        # 3. Decide: 决策
        action = await self._decide(element, instruction)
        
        # 4. Act: 执行
        result = await self._act(action, target_id)
        
        return result
    
    async def _observe(
        self,
        instruction: str,
        target_id: str
    ) -> Observation:
        """观察阶段"""
        # 1. 获取当前 URL
        url = await self.cdp_session.get_url(target_id)
        
        # 2. 获取 DOM 状态
        dom_state = await self.dom_service.get_dom_tree(target_id)
        
        # 3. 检测阻挡物（基础版）
        # TODO: 实现阻挡物检测
        
        return Observation(
            instruction=instruction,
            url=url,
            dom_state=dom_state,
            has_obstacle=False
        )
    
    async def _orient(
        self,
        instruction: str,
        dom_state: SerializedDOMState,
        url: str
    ) -> Optional[EnhancedDOMTreeNode]:
        """定向阶段：通过五层漏斗定位元素"""
        
        # 0. 查询知识库（如果有）
        if self.knowledge_base:
            knowledge = await self.knowledge_base.query(url, instruction)
            if knowledge:
                logger.info("知识库命中")
                # TODO: 根据 selector 找到元素
                pass
        
        # 1. L1: 提取槽位
        slot = await self.l1_engine.extract_slot(instruction)
        if not slot:
            return None
        
        # 2. L2: 属性匹配
        l2_results = await self.l2_engine.match_elements(dom_state, slot)
        
        # 如果 L2 高置信度，直接返回
        if l2_results and l2_results[0].score > 0.9:
            return l2_results[0].element
        
        # 3. L3: 空间布局
        context = FunnelContext(
            instruction=instruction,
            action_slot=slot,
            l2_candidates=l2_results
        )
        context = await self.l3_engine.process(context, dom_state)
        
        if context.l3_candidates:
            return context.l3_candidates[0].element
        
        # 4. L4: AI 推理（如果需要）
        # TODO: 添加 L4 条件判断
        
        # 5. L5: 视觉识别（如果需要）
        # TODO: 添加 L5 条件判断
        
        # 返回最佳候选
        if l2_results:
            return l2_results[0].element
        
        return None
    
    async def _decide(
        self,
        element: EnhancedDOMTreeNode,
        instruction: str
    ) -> Action:
        """决策阶段：生成执行指令"""
        
        # 提取动作类型
        slot = await self.l1_engine.extract_slot(instruction)
        
        action = Action(
            type=slot.action_type,
            element=element,
            value=slot.value,
            instruction=instruction
        )
        
        return action
    
    async def _act(
        self,
        action: Action,
        target_id: str
    ) -> StepResult:
        """执行阶段：执行动作并验证"""
        
        try:
            # 1. 执行动作
            if action.type.value == "CLICK":
                await self._execute_click(action.element, target_id)
            elif action.type.value == "INPUT":
                await self._execute_input(
                    action.element,
                    action.value,
                    target_id
                )
            # ... 其他动作类型
            
            # 2. 截图
            screenshot_path = await self._take_screenshot(target_id)
            
            # 3. 回执验证（基础版）
            success = await self._verify_action(action, target_id)
            
            return StepResult(
                success=success,
                instruction=action.instruction,
                screenshot=screenshot_path,
                element_id=action.element.backend_node_id
            )
        
        except Exception as e:
            logger.error(f"执行失败: {str(e)}")
            return StepResult(
                success=False,
                error=str(e),
                instruction=action.instruction
            )
```

#### 2. 创建数据类型

```python
# aerotest/core/ooda/types.py

@dataclass
class Observation:
    """观察结果"""
    instruction: str
    url: str
    dom_state: SerializedDOMState
    has_obstacle: bool = False

@dataclass
class Action:
    """执行动作"""
    type: ActionType
    element: EnhancedDOMTreeNode
    value: Optional[str] = None
    instruction: str = ""

@dataclass
class StepResult:
    """步骤结果"""
    success: bool
    instruction: str
    error: Optional[str] = None
    screenshot: Optional[str] = None
    element_id: Optional[int] = None
    duration: float = 0.0
```

#### 3. 创建完整用例执行器

```python
# aerotest/core/ooda/executor.py

class CaseExecutor:
    """用例执行器"""
    
    def __init__(self, cdp_session: CDPSession):
        self.ooda_engine = OODAEngine(cdp_session)
    
    async def execute_case(
        self,
        case: TestCase
    ) -> CaseResult:
        """
        执行完整测试用例
        
        Args:
            case: 测试用例
            
        Returns:
            用例执行结果
        """
        results = []
        
        for step in case.steps:
            result = await self.ooda_engine.execute_step(
                instruction=step.instruction,
                target_id=case.target_id
            )
            
            results.append(result)
            
            # 如果步骤失败，决定是否继续
            if not result.success:
                if not case.continue_on_failure:
                    break
        
        # 汇总结果
        success = all(r.success for r in results)
        
        return CaseResult(
            case_id=case.id,
            success=success,
            steps=results,
            total_duration=sum(r.duration for r in results)
        )
```

### 验收标准

```
✅ OODA Engine 创建完成
✅ 支持单步骤执行
✅ 支持完整用例执行
✅ 集成五层漏斗
✅ 基础回执验证
✅ E2E 测试通过
```

---

## 🧪 Week 1 测试计划

### 单元测试

```python
# tests/unit/ooda/test_ooda_engine.py

class TestOODAEngine:
    """OODA 引擎单元测试"""
    
    async def test_observe(self):
        """测试观察阶段"""
        pass
    
    async def test_orient(self):
        """测试定向阶段"""
        pass
    
    async def test_decide(self):
        """测试决策阶段"""
        pass
    
    async def test_act(self):
        """测试执行阶段"""
        pass
```

### 集成测试

```python
# tests/integration/test_ooda_e2e.py

async def test_login_flow():
    """测试完整登录流程"""
    
    # 初始化
    cdp_session = await create_cdp_session()
    executor = CaseExecutor(cdp_session)
    
    # 创建用例
    case = TestCase(
        id="login_test",
        steps=[
            Step("打开登录页 https://example.com/login"),
            Step("在用户名输入框输入 admin"),
            Step("在密码输入框输入 password123"),
            Step("点击登录按钮"),
            Step("验证页面显示'欢迎回来'")
        ]
    )
    
    # 执行
    result = await executor.execute_case(case)
    
    # 断言
    assert result.success == True
    assert len(result.steps) == 5
    assert all(s.success for s in result.steps)
```

---

## 📈 Week 1 进度跟踪

### Day 1-2 进度

```
事件监听器检测
├─ EventListenerDetector    [ 进行中 ]
├─ DomService 扩展          [ 待开始 ]
├─ L3 引擎集成              [ 待开始 ]
└─ 单元测试                 [ 待开始 ]
```

### Day 3-5 进度

```
OODA 循环
├─ OODA Engine              [ 待开始 ]
├─ Observation 阶段         [ 待开始 ]
├─ Orient 阶段              [ 待开始 ]
├─ Decide 阶段              [ 待开始 ]
├─ Act 阶段                 [ 待开始 ]
├─ CaseExecutor             [ 待开始 ]
└─ E2E 测试                 [ 待开始 ]
```

---

## ✅ Week 1 验收清单

### 功能验收

- [ ] 事件监听器检测工作正常
- [ ] L3 可识别非标控件
- [ ] OODA 循环可执行单步骤
- [ ] OODA 循环可执行完整用例
- [ ] 五层漏斗正确集成

### 测试验收

- [ ] 单元测试通过率 > 90%
- [ ] 集成测试通过
- [ ] E2E 测试通过（至少 1 个）

### 性能验收

- [ ] 单步骤执行时间 < 5s（不含 AI）
- [ ] 完整用例执行稳定

---

## 📚 参考资料

- CDP DOMDebugger Protocol: https://chromedevtools.github.io/devtools-protocol/tot/DOMDebugger/
- OODA Loop: https://en.wikipedia.org/wiki/OODA_loop

---

**计划创建时间**: 2025-12-18  
**预计完成时间**: 2025-12-25  
**当前状态**: 🚀 Day 1 进行中

