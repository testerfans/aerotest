# AeroTest AI - Week 3 快速开始指南

**版本**: v0.1.0-alpha  
**更新**: 2025-12-18  
**状态**: Week 3 基础版已完成 (85%)

---

## 🎯 Week 3 能做什么？

AeroTest AI 现在可以：

1. ✅ 连接到本地 Chrome/Edge 浏览器
2. ✅ 导航到任意网页
3. ✅ 获取页面的完整 DOM 树
4. ✅ 智能过滤可交互元素
5. ✅ 生成 LLM 友好的页面表示
6. ✅ 执行截图、JavaScript 等基本操作

---

## 📦 安装

### 1. 安装依赖

```bash
# 使用 Poetry (推荐)
poetry install

# 或者使用 pip
pip install cdp-use httpx uuid-extensions pydantic loguru
```

### 2. 启动浏览器（重要！）

**必须** 先启动浏览器并开启远程调试：

```bash
# Windows - Chrome
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222

# Windows - Edge  
"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9222

# macOS - Chrome
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222

# Linux - Chrome
google-chrome --remote-debugging-port=9222

# 无头模式（不显示窗口）
chrome --remote-debugging-port=9222 --headless=new
```

**验证浏览器已启动**:

访问 http://localhost:9222/json 应该能看到 JSON 数据。

---

## 🚀 快速开始

### 最简示例 (3 行代码)

```python
from aerotest.browser.cdp import CDPSession

async def main():
    # 连接浏览器并获取 DOM
    async with CDPSession.connect() as session:
        await session.navigate("https://example.com")
        dom_tree = await session.get_dom_tree()
    
    print(f"✅ 获取到 DOM 树: {dom_tree.node_name}")

# 运行
import asyncio
asyncio.run(main())
```

### 完整示例 (使用 DomService)

```python
from aerotest.browser.cdp import CDPSession, CDPConnectionConfig
from aerotest.browser.dom import DomService

async def main():
    # 1. 配置连接
    config = CDPConnectionConfig(
        host="localhost",
        port=9222,
    )
    
    # 2. 创建会话
    async with CDPSession.connect(config) as session:
        # 3. 导航到目标页面
        await session.navigate("https://example.com")
        
        # 4. 获取 DOM 树
        dom_tree = await session.get_dom_tree()
        
        # 5. 使用 DomService 处理
        service = DomService()
        state, timing = service.serialize_dom_tree(dom_tree)
        
        # 6. 获取 LLM 表示
        llm_repr = service.get_llm_representation(state)
        
        # 7. 查找元素
        elements = service.find_elements_by_text(state, "Example")
        
        # 8. 获取统计信息
        stats = service.get_statistics(state)
        
        # 输出结果
        print(f"✅ 找到 {len(state.selector_map)} 个可交互元素")
        print(f"⏱️ 处理耗时: {timing['serialize_accessible_elements_total']*1000:.1f}ms")
        print(f"📊 统计: {stats}")
        print(f"\n📝 LLM 表示 (前 500 字符):\n{llm_repr[:500]}")

import asyncio
asyncio.run(main())
```

---

## 📖 核心 API

### 1. CDPConnection - 连接管理

```python
from aerotest.browser.cdp import CDPConnection, CDPConnectionConfig

config = CDPConnectionConfig(
    host="localhost",
    port=9222,
    timeout=30.0,
)

async with CDPConnection(config) as connection:
    # 获取所有页面
    targets = await connection.get_targets()
    
    # 获取第一个页面
    target = await connection.get_first_page_target()
    
    # 创建新页面
    new_target = await connection.create_new_page("https://example.com")
    
    # 关闭页面
    await connection.close_target(target_id)
```

### 2. CDPSession - 会话操作

```python
from aerotest.browser.cdp import CDPSession

async with CDPSession.connect() as session:
    # 页面导航
    await session.navigate("https://example.com")
    
    # 获取 DOM 树 (核心功能)
    dom_tree = await session.get_dom_tree()
    
    # 执行 JavaScript
    result = await session.evaluate("document.title")
    
    # 截图
    screenshot = await session.screenshot()
    with open("screenshot.png", "wb") as f:
        f.write(screenshot)
    
    # 获取页面信息
    title = await session.get_page_title()
    url = await session.get_page_url()
```

### 3. DomService - DOM 处理

```python
from aerotest.browser.dom import DomService

service = DomService()

# 序列化 DOM 树
state, timing = service.serialize_dom_tree(dom_tree)

# 获取 LLM 表示
llm_repr = service.get_llm_representation(state)

# 查找元素
elements = service.find_elements_by_text(state, "搜索")
element = service.find_element_by_backend_node_id(state, 123)

# 获取可交互元素
clickable = service.get_clickable_elements(state)

# 获取统计信息
stats = service.get_statistics(state)
```

---

## 🎯 常见用例

### 用例 1: 获取页面所有链接

```python
async with CDPSession.connect() as session:
    await session.navigate("https://example.com")
    dom_tree = await session.get_dom_tree()
    
    service = DomService()
    state, _ = service.serialize_dom_tree(dom_tree)
    
    # 找到所有 <a> 标签
    links = []
    for element in state.selector_map.values():
        if element.tag_name.lower() == "a":
            href = element.attributes.get("href", "")
            text = element.get_all_children_text()
            links.append({"text": text, "href": href})
    
    print(f"找到 {len(links)} 个链接")
```

### 用例 2: 页面截图

```python
async with CDPSession.connect() as session:
    await session.navigate("https://example.com")
    
    # 等待页面加载
    await asyncio.sleep(2)
    
    # 截图
    screenshot = await session.screenshot()
    
    # 保存
    from pathlib import Path
    Path("screenshot.png").write_bytes(screenshot)
    print("✅ 截图已保存")
```

### 用例 3: 获取页面所有表单

```python
async with CDPSession.connect() as session:
    await session.navigate("https://example.com")
    dom_tree = await session.get_dom_tree()
    
    service = DomService()
    state, _ = service.serialize_dom_tree(dom_tree)
    
    # 找到所有 <form> 和 <input>
    forms = []
    inputs = []
    for element in state.selector_map.values():
        if element.tag_name.lower() == "form":
            forms.append(element)
        elif element.tag_name.lower() == "input":
            inputs.append(element)
    
    print(f"找到 {len(forms)} 个表单, {len(inputs)} 个输入框")
```

### 用例 4: 执行 JavaScript 并获取结果

```python
async with CDPSession.connect() as session:
    await session.navigate("https://example.com")
    
    # 获取页面所有图片
    result = await session.evaluate("""
        Array.from(document.images).map(img => ({
            src: img.src,
            alt: img.alt,
            width: img.width,
            height: img.height,
        }))
    """)
    
    images = result.get("result", {}).get("value", [])
    print(f"找到 {len(images)} 张图片")
```

---

## 🔧 配置选项

### CDPConnectionConfig

```python
from aerotest.browser.cdp import CDPConnectionConfig

config = CDPConnectionConfig(
    host="localhost",      # CDP 服务器地址
    port=9222,             # CDP 端口
    timeout=30.0,          # 连接超时（秒）
    max_retries=3,         # 最大重试次数
)
```

### DomService 选项

```python
from aerotest.browser.dom import DomService

service = DomService(
    paint_order_filtering=True,   # 启用绘制顺序过滤
    bbox_filtering=True,           # 启用边界框过滤
    containment_threshold=0.99,    # 包含阈值
)
```

---

## ⚠️ 常见问题

### 1. ConnectionError: CDP 不可用

**问题**: 连接时报错 "CDP 不可用"

**解决**:
1. 确保浏览器已启动并开启远程调试
2. 检查端口是否正确（默认 9222）
3. 访问 http://localhost:9222/json 验证

### 2. 没有找到页面目标

**问题**: `get_first_page_target()` 返回 None

**解决**:
1. 在浏览器中打开一个页面（不要只有空白标签）
2. 或者使用 `create_new_page()` 创建新页面

### 3. DOM 获取超时

**问题**: `get_dom_tree()` 超时

**解决**:
1. 增加超时时间：`config.timeout = 60.0`
2. 检查页面是否过于复杂（大量 iframe）
3. 尝试等待页面完全加载后再获取

### 4. asyncio.run() 报错

**问题**: Windows 上运行 asyncio 报错

**解决**:
```python
# Windows 上需要设置事件循环策略
import asyncio
import sys

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

asyncio.run(main())
```

---

## 📊 性能指标

### 典型页面 (中等复杂度)

- **CDP 连接**: ~100ms
- **页面导航**: 500-2000ms (取决于网络)
- **DOM 获取**: ~300ms (并行)
- **DOM 序列化**: ~100ms
- **总计**: 1-3 秒

### 大型页面 (复杂)

- **DOM 获取**: ~500ms
- **DOM 序列化**: ~200ms
- **可交互元素**: 500-1000 个

---

## 🔗 相关资源

### 文档

- [Week3-Session管理计划.md](Week3-Session管理计划.md) - 实施计划
- [Week3-完成总结.md](Week3-完成总结.md) - 完成总结
- [项目状态更新-Week3完成.md](项目状态更新-Week3完成.md) - 状态更新

### 示例

- [examples/cdp_session_usage.py](../examples/cdp_session_usage.py) - 完整示例
- [examples/dom_service_usage.py](../examples/dom_service_usage.py) - DOM 服务示例

### API 文档

查看源码中的 docstring，所有方法都有详细注释。

---

## 🚧 当前限制

### 已知问题

1. ⚠️ **DOM 树构建简化**
   - 当前是简化版本
   - 不影响基本使用
   - 完整版本开发中

2. ⚠️ **iframe 支持有限**
   - 基础 iframe 可以处理
   - 深度嵌套和跨域 iframe 待完善

3. ⚠️ **页面等待策略简化**
   - 当前使用简单的延迟等待
   - 事件监听版本开发中

### 未实现功能

- ❌ EventBus (不计划实现)
- ❌ Cloud Browser (不计划实现)
- ❌ Watchdogs (后续版本)
- ❌ 视频录制 (后续版本)
- ❌ 多标签页管理 (后续版本)

---

## 🎯 下一步

### Week 3 完善 (进行中)

- [ ] 完整 DOM 树构建
- [ ] iframe 深度支持
- [ ] 页面等待优化

### Week 4 集成测试 (计划中)

- [ ] 端到端测试
- [ ] 性能测试
- [ ] 文档完善

---

## 💬 反馈

如有问题或建议，请：
1. 查看文档
2. 检查示例代码
3. 查看源码注释

---

**更新日期**: 2025-12-18  
**版本**: v0.1.0-alpha  
**状态**: Week 3 基础版完成 (85%)

**AeroTest AI 团队** 🚀

