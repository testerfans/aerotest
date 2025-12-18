# browser-use 快速集成指南

> 本文档提供 browser-use 集成的快速上手步骤

## 🚀 快速开始

### Step 1: Fork 项目（5 分钟）
```bash
# 1. 在 GitHub 上 Fork browser-use 项目
# 访问：https://github.com/browser-use/browser-use
# 点击右上角 "Fork" 按钮

# 2. Clone 到本地
cd d:/projects/OODA
git clone https://github.com/YOUR_ORG/browser-use.git
cd browser-use

# 3. 创建集成分支
git checkout -b aerotest-integration

# 4. 安装依赖
pip install -e .

# 5. 运行测试（确保原始功能正常）
pytest tests/ -v
```

---

### Step 2: 剔除不需要的代码（30 分钟）

#### 2.1 删除 AI Agent 模块
```bash
# 删除目录
rm -rf agent/
rm -rf examples/

# 删除相关测试
rm -rf tests/agent/
```

#### 2.2 清理依赖
编辑 `pyproject.toml` 或 `setup.py`：

```toml
# 删除这些依赖
[tool.poetry.dependencies]
# langchain = "^0.1.0"          # ❌ 删除
# langchain-openai = "^0.0.5"   # ❌ 删除
# openai = "^1.0.0"             # ❌ 删除

# 保留这些核心依赖
playwright = "^1.40.0"          # ✅ 保留
pydantic = "^2.0.0"            # ✅ 保留
loguru = "^0.7.0"              # ✅ 保留
```

#### 2.3 检查导入错误
```bash
# 查找所有对 agent 的引用
grep -r "from agent" . --include="*.py"
grep -r "import agent" . --include="*.py"

# 删除或注释这些导入
```

#### 2.4 重新安装依赖
```bash
pip install -e .
pytest tests/browser tests/dom -v  # 只测试核心模块
```

---

### Step 3: 集成到 AeroTest AI（1 小时）

#### 3.1 创建目录结构
```bash
cd d:/projects/OODA

# 创建项目结构
mkdir -p aerotest/browser_use
mkdir -p aerotest/core/funnel
mkdir -p aerotest/core/ooda
mkdir -p tests/integration
```

#### 3.2 复制 browser-use 核心代码
```bash
# 复制浏览器管理模块
cp -r ../browser-use/browser aerotest/browser_use/

# 复制 DOM 处理模块
cp -r ../browser-use/dom aerotest/browser_use/

# 复制控制器模块
cp -r ../browser-use/controller aerotest/browser_use/

# 复制工具模块
cp -r ../browser-use/utils aerotest/browser_use/

# 创建 __init__.py
touch aerotest/browser_use/__init__.py
```

#### 3.3 创建简单的集成示例
创建 `tests/integration/test_browser_use.py`：

```python
import pytest
from aerotest.browser_use.browser.service import BrowserService
from aerotest.browser_use.dom.service import DOMService

@pytest.mark.asyncio
async def test_basic_browser():
    """测试基本浏览器功能"""
    service = BrowserService()
    browser = await service.create_browser(headless=True)
    page = await browser.new_page()
    
    # 访问测试页面
    await page.goto('https://example.com')
    
    # 验证页面标题
    title = await page.title()
    assert 'Example Domain' in title
    
    await browser.close()
    print("✅ 浏览器管理测试通过")

@pytest.mark.asyncio
async def test_dom_extraction():
    """测试 DOM 提取"""
    service = BrowserService()
    browser = await service.create_browser(headless=True)
    page = await browser.new_page()
    
    await page.goto('https://example.com')
    
    # 提取 DOM
    dom_service = DOMService(page)
    dom_tree = await dom_service.extract_dom_tree()
    
    assert dom_tree is not None
    print(f"✅ DOM 提取测试通过，节点数：{len(dom_tree.get('children', []))}")
    
    await browser.close()

if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
```

#### 3.4 运行集成测试
```bash
cd d:/projects/OODA
pytest tests/integration/test_browser_use.py -v -s
```

---

### Step 4: 增强 L3 层空间布局（2 小时）

创建 `aerotest/browser_use/dom/spatial_layout.py`：

```python
from typing import Optional, Literal

class SpatialLayoutLocator:
    """空间布局定位器（L3 层核心）"""
    
    def __init__(self, page):
        self.page = page
    
    async def find_by_spatial_layout(
        self,
        anchor_text: str,
        direction: Literal['right', 'below', 'left', 'above'] = 'right',
        proximity: int = 50
    ) -> Optional[dict]:
        """
        基于空间布局定位元素
        
        Args:
            anchor_text: 锚点文本（如："手机号"）
            direction: 搜索方向（right/below/left/above）
            proximity: 邻近阈值（像素）
        
        Returns:
            {
                'selector': '元素选择器',
                'element': '元素句柄',
                'distance': '距离（像素）'
            }
        """
        js_code = """
        (anchorText, direction, proximity) => {
            // 1. 查找锚点元素
            const allElements = Array.from(document.querySelectorAll('*'));
            const anchor = allElements.find(el => {
                const text = el.textContent?.trim();
                return text === anchorText || text?.includes(anchorText);
            });
            
            if (!anchor) {
                return { error: 'Anchor not found', anchorText };
            }
            
            const anchorRect = anchor.getBoundingClientRect();
            
            // 2. 查找可交互元素
            const interactiveSelectors = 
                'input, button, a, select, textarea, [role="button"], ' +
                '[onclick], [contenteditable], [tabindex]:not([tabindex="-1"])';
            
            const interactiveElements = document.querySelectorAll(interactiveSelectors);
            
            // 3. 计算距离并过滤
            const candidates = [];
            
            for (const el of interactiveElements) {
                const rect = el.getBoundingClientRect();
                let distance = null;
                let isMatch = false;
                
                // 判断相对位置
                switch(direction) {
                    case 'right':
                        // 右侧：rect.left > anchorRect.right 且垂直接近
                        if (rect.left > anchorRect.right && 
                            Math.abs(rect.top - anchorRect.top) < 50) {
                            distance = rect.left - anchorRect.right;
                            isMatch = distance <= proximity;
                        }
                        break;
                    
                    case 'below':
                        // 下方：rect.top > anchorRect.bottom 且水平接近
                        if (rect.top > anchorRect.bottom && 
                            Math.abs(rect.left - anchorRect.left) < 50) {
                            distance = rect.top - anchorRect.bottom;
                            isMatch = distance <= proximity;
                        }
                        break;
                    
                    case 'left':
                        // 左侧
                        if (rect.right < anchorRect.left && 
                            Math.abs(rect.top - anchorRect.top) < 50) {
                            distance = anchorRect.left - rect.right;
                            isMatch = distance <= proximity;
                        }
                        break;
                    
                    case 'above':
                        // 上方
                        if (rect.bottom < anchorRect.top && 
                            Math.abs(rect.left - anchorRect.left) < 50) {
                            distance = anchorRect.top - rect.bottom;
                            isMatch = distance <= proximity;
                        }
                        break;
                }
                
                if (isMatch) {
                    // 生成唯一选择器
                    let selector = el.tagName.toLowerCase();
                    if (el.id) selector += `#${el.id}`;
                    if (el.className) {
                        const classes = el.className.split(' ').filter(c => c);
                        if (classes.length > 0) {
                            selector += '.' + classes.join('.');
                        }
                    }
                    
                    candidates.push({
                        selector,
                        distance,
                        tagName: el.tagName,
                        id: el.id,
                        className: el.className,
                        rect: {
                            left: rect.left,
                            top: rect.top,
                            width: rect.width,
                            height: rect.height
                        }
                    });
                }
            }
            
            // 4. 返回最近的候选
            if (candidates.length > 0) {
                candidates.sort((a, b) => a.distance - b.distance);
                return { success: true, result: candidates[0], allCandidates: candidates };
            }
            
            return { success: false, reason: 'No candidates found' };
        }
        """
        
        result = await self.page.evaluate(js_code, anchor_text, direction, proximity)
        
        if result.get('success'):
            return result['result']
        else:
            return None

# 使用示例
"""
from aerotest.browser_use.dom.spatial_layout import SpatialLayoutLocator

# 在页面中使用
locator = SpatialLayoutLocator(page)
element = await locator.find_by_spatial_layout(
    anchor_text='手机号',
    direction='right',
    proximity=50
)

if element:
    print(f"找到元素：{element['selector']}，距离：{element['distance']}px")
    await page.click(element['selector'])
"""
```

---

### Step 5: 创建简单的五层漏斗示例（1 小时）

创建 `aerotest/core/funnel/simple_funnel.py`：

```python
from aerotest.browser_use.browser.service import BrowserService
from aerotest.browser_use.dom.service import DOMService
from aerotest.browser_use.dom.spatial_layout import SpatialLayoutLocator

class SimpleFunnelEngine:
    """简化的五层漏斗引擎（演示用）"""
    
    def __init__(self):
        self.browser_service = BrowserService()
    
    async def locate_element(self, page, instruction: str):
        """
        通过五层漏斗定位元素
        
        Args:
            page: Playwright Page 对象
            instruction: 用户指令（如："点击提交按钮"）
        
        Returns:
            定位结果字典
        """
        # 提取目标文本（简化版，实际应使用 NLP）
        target = self._extract_target(instruction)
        
        print(f"🔍 开始定位：{instruction}")
        print(f"   目标文本：{target}")
        
        # L1: 规则层（简化）
        result = await self._l1_rule_match(instruction)
        if result:
            print(f"✅ L1 层命中")
            return result
        
        # L2: 属性匹配
        result = await self._l2_attribute_match(page, target)
        if result:
            print(f"✅ L2 层命中：{result['selector']}")
            return result
        
        # L3: 空间布局
        result = await self._l3_spatial_layout(page, target)
        if result:
            print(f"✅ L3 层命中：{result['selector']}，距离：{result['distance']}px")
            return result
        
        print(f"❌ L1-L3 层均未命中，需要 L4/L5 层处理")
        return None
    
    def _extract_target(self, instruction: str) -> str:
        """提取目标文本（简化版）"""
        # 移除动作词
        for action in ['点击', '输入', '选择', '滚动到', '等待']:
            instruction = instruction.replace(action, '')
        return instruction.strip()
    
    async def _l1_rule_match(self, instruction: str):
        """L1: 规则匹配（简化）"""
        # 硬编码规则示例
        rules = {
            '点击登录': {'selector': 'button.login-btn'},
            '点击提交': {'selector': 'button[type="submit"]'},
        }
        return rules.get(instruction)
    
    async def _l2_attribute_match(self, page, target: str):
        """L2: 属性匹配"""
        # 尝试多种属性匹配
        selectors = [
            f'button:has-text("{target}")',
            f'[aria-label="{target}"]',
            f'[placeholder="{target}"]',
            f'input[name*="{target.lower()}"]',
        ]
        
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element and await element.is_visible():
                    return {
                        'selector': selector,
                        'confidence': 0.95,
                        'method': 'l2_attribute'
                    }
            except:
                continue
        
        return None
    
    async def _l3_spatial_layout(self, page, target: str):
        """L3: 空间布局"""
        locator = SpatialLayoutLocator(page)
        
        # 尝试右侧
        result = await locator.find_by_spatial_layout(target, 'right', 50)
        if result:
            return {
                'selector': result['selector'],
                'confidence': 0.88,
                'method': 'l3_spatial',
                'distance': result['distance']
            }
        
        # 尝试下方
        result = await locator.find_by_spatial_layout(target, 'below', 50)
        if result:
            return {
                'selector': result['selector'],
                'confidence': 0.85,
                'method': 'l3_spatial',
                'distance': result['distance']
            }
        
        return None


# 测试代码
async def demo():
    """演示五层漏斗"""
    from playwright.async_api import async_playwright
    
    engine = SimpleFunnelEngine()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # 加载测试页面
        await page.set_content("""
        <html>
        <body>
            <h1>测试页面</h1>
            
            <!-- L2 层测试：标准按钮 -->
            <button type="submit">提交</button>
            
            <!-- L3 层测试：非标控件 -->
            <div style="margin: 20px 0;">
                <label style="display: inline-block; width: 100px;">手机号</label>
                <div class="custom-input" onclick="alert('clicked')" 
                     style="display: inline-block; width: 200px; height: 30px; 
                            border: 1px solid #ccc; cursor: pointer;">
                    点击输入
                </div>
            </div>
            
            <div style="margin: 20px 0;">
                <label style="display: block; margin-bottom: 10px;">验证码</label>
                <input type="text" style="width: 200px;" />
            </div>
        </body>
        </html>
        """)
        
        # 测试 L2 层
        print("\n=== 测试 L2 层：属性匹配 ===")
        result = await engine.locate_element(page, "点击提交按钮")
        if result:
            await page.click(result['selector'])
        
        # 测试 L3 层（水平）
        print("\n=== 测试 L3 层：空间布局（右侧） ===")
        result = await engine.locate_element(page, "点击手机号输入框")
        if result:
            await page.click(result['selector'])
        
        # 测试 L3 层（垂直）
        print("\n=== 测试 L3 层：空间布局（下方） ===")
        result = await engine.locate_element(page, "点击验证码输入框")
        if result:
            await page.click(result['selector'])
        
        await page.wait_for_timeout(3000)
        await browser.close()

if __name__ == '__main__':
    import asyncio
    asyncio.run(demo())
```

运行演示：
```bash
cd d:/projects/OODA
python aerotest/core/funnel/simple_funnel.py
```

---

## ✅ 验证清单

完成以上步骤后，检查以下项目：

- [ ] browser-use 项目已 Fork 并 Clone 到本地
- [ ] 已删除 agent/ 模块
- [ ] 已清理 LangChain 等不需要的依赖
- [ ] browser-use 核心模块已复制到 aerotest/browser_use/
- [ ] 基础集成测试通过
- [ ] L3 层空间布局定位器已实现
- [ ] 简单的五层漏斗演示成功运行

---

## 🎯 下一步

完成快速集成后，可以继续：

1. **完善 L1-L3 层**：
   - L1：规则引擎（NLP 正则）
   - L2：模糊匹配算法优化
   - L3：更复杂的空间布局场景

2. **实现 L4-L5 层**：
   - L4：集成阿里百炼 API（Qwen-Max）
   - L5：集成视觉识别（Qwen2-VL）

3. **构建 OODA 引擎**：
   - 完整的观察-调整-决定-执行循环
   - 回执验证
   - 异常处理

4. **平台化开发**：
   - FastAPI 后端接口
   - React 前端界面
   - 数据库设计

---

## 📚 参考文档

- [browser-use 可行性分析](./browser-use-feasibility-analysis.md)
- [AeroTest AI 需求文档](./requirement.md)
- [Playwright 官方文档](https://playwright.dev/python/)

---

## 💬 问题反馈

如遇到问题，请检查：
1. Python 版本是否 >= 3.11
2. Playwright 是否正确安装：`playwright install`
3. 依赖是否完整：`pip list`

---

**祝集成顺利！** 🚀

