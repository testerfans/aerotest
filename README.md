# AeroTest AI

**智能 UI 自动化测试平台**

AeroTest AI 是一款基于 OODA 循环和五层漏斗过滤机制的智能 UI 自动化测试平台，旨在解决传统 UI 自动化测试的痛点，提高测试效率和稳定性。

## ✨ 核心特性

### 🔄 OODA 循环
- **Observe (观察)**: 智能观察页面状态
- **Orient (定向)**: 五层漏斗精准定位元素
- **Decide (决策)**: 智能决策执行策略
- **Act (行动)**: 可靠执行并验证结果

### 🎯 五层漏斗过滤机制
1. **L1 - 规则槽位层**: NLP 意图识别和实体提取
2. **L2 - 启发式属性匹配**: DOM 属性智能匹配
3. **L3 - 空间布局推理**: 锚点定位 + 邻近检测 + 事件监听器
4. **L4 - AI 推理**: Qwen-Max/Plus 智能推理
5. **L5 - 视觉识别**: Qwen2-VL 多模态视觉感知

### 🔥 技术亮点
- ✅ 完整的 OODA 循环实现
- ✅ 五层漏斗深度集成
- ✅ CDP 事件监听器检测（非标控件识别）
- ✅ 灵活的重试和降级策略
- ✅ 完善的数据追踪和可观测性

## 📦 安装

### 环境要求
- Python 3.12+
- Chrome/Chromium 浏览器

### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/testerfans/aerotest.git
cd aerotest

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

## 🚀 快速开始

### 基础用法

```python
from aerotest.core.ooda import (
    OODAEngine,
    TestStep,
    ActionType,
    ExecutionContext,
)

# 创建 OODA 引擎
engine = OODAEngine(use_l3=True, use_l4=False, use_l5=False)

# 创建测试步骤
step = TestStep(
    step_id="1",
    description="点击登录按钮",
    action_type=ActionType.CLICK,
)

# 创建执行上下文
context = ExecutionContext(target_id="page_1")

# 执行步骤
result = await engine.execute_step(step, context)

print(f"执行结果: {result.success}")
print(f"策略: {step.orientation.strategy}")
print(f"置信度: {step.orientation.confidence}")
```

### 完整用例

```python
from aerotest.core.ooda import CaseExecutor, TestCase, TestStep, ActionType

# 创建用例执行器
executor = CaseExecutor(max_retries=2)

# 创建测试用例
case = TestCase(
    case_id="TC001",
    name="登录测试",
    steps=[
        TestStep(step_id="1", description="输入用户名", action_type=ActionType.INPUT),
        TestStep(step_id="2", description="输入密码", action_type=ActionType.INPUT),
        TestStep(step_id="3", description="点击登录按钮", action_type=ActionType.CLICK),
    ],
)

# 执行用例
result = await executor.execute_case(case, context)

print(f"用例结果: {result.success}")
print(f"统计: {result.stats}")
```

## 📚 文档

- [需求文档](docs/requirement.md)
- [技术架构设计](docs/AeroTest-技术架构设计.md)
- [快速开始指南](docs/快速开始指南.md)
- [工程架构说明](docs/工程架构说明.md)

## 🏗️ 项目结构

```
aerotest/
├── aerotest/
│   ├── core/
│   │   ├── ooda/           # OODA 循环实现
│   │   │   ├── types.py    # 数据类型定义
│   │   │   ├── ooda_engine.py  # OODA 引擎
│   │   │   └── case_executor.py  # 用例执行器
│   │   └── funnel/         # 五层漏斗
│   │       ├── l1/         # L1 规则槽位层
│   │       ├── l2/         # L2 启发式匹配
│   │       ├── l3/         # L3 空间布局推理
│   │       ├── l4/         # L4 AI 推理
│   │       └── l5/         # L5 视觉识别
│   ├── browser/
│   │   ├── cdp/            # CDP 集成
│   │   └── dom/            # DOM 处理
│   ├── config/             # 配置管理
│   ├── utils/              # 工具函数
│   ├── api/                # API 接口
│   └── db/                 # 数据库模型
├── tests/
│   ├── unit/               # 单元测试
│   ├── integration/        # 集成测试
│   └── e2e/                # 端到端测试
├── docs/                   # 文档
└── examples/               # 示例代码
```

## 📊 项目状态

### ✅ 已完成

#### Phase 1: browser-use 集成
- ✅ DOM 提取和序列化
- ✅ CDP Session 管理
- ✅ 增强快照处理

#### Phase 2: L1-L2 层
- ✅ L1 规则槽位层（意图识别、实体提取、槽位填充）
- ✅ L2 启发式属性匹配（属性匹配、文本匹配、类型匹配）

#### Phase 3: L3-L5 层
- ✅ L3 空间布局推理（锚点定位、邻近检测）
- ✅ L4 AI 推理（Qwen-Max/Plus）
- ✅ L5 视觉识别（Qwen2-VL）

#### MVP Week 1: 核心补齐
- ✅ 事件监听器检测（CDP）
- ✅ OODA 循环基础版

### 🔄 进行中

#### MVP Week 2: 稳定性增强
- ⏳ 回执验证
- ⏳ 阻挡物清除

#### MVP Week 3: 知识库和测试
- ⏳ 自愈知识库基础版
- ⏳ 集成测试和文档

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

## 📄 许可证

MIT License

## 👥 作者

AeroTest AI Team

## 📧 联系方式

- GitHub: https://github.com/testerfans/aerotest
- Issues: https://github.com/testerfans/aerotest/issues

---

**注意**: 本项目目前处于 MVP 阶段，部分功能仍在开发中。
