# AeroTest AI - 虚拟环境使用指南

## 🚀 快速开始

### Windows 用户

**方法 1：使用激活脚本（推荐）**

```bash
# PowerShell
.\激活虚拟环境.ps1

# CMD
激活虚拟环境.bat
```

**方法 2：手动激活**

```bash
# PowerShell
.\venv\Scripts\Activate.ps1

# CMD
.\venv\Scripts\activate.bat
```

### Linux/macOS 用户

```bash
source venv/bin/activate
```

---

## 📦 已安装的依赖

### 核心框架
- ✅ **FastAPI 0.125.0** - Web 框架
- ✅ **Uvicorn 0.38.0** - ASGI 服务器
- ✅ **Pydantic 2.12.5** - 数据验证

### 日志和工具
- ✅ **Loguru 0.7.3** - 日志系统

### 测试框架
- ✅ **Pytest 9.0.2** - 测试框架
- ✅ **Pytest-asyncio 1.3.0** - 异步测试支持

---

## 🧪 运行测试

### 运行所有测试

```bash
pytest
```

### 运行特定目录的测试

```bash
# 单元测试
pytest tests/unit/

# 集成测试
pytest tests/integration/

# 端到端测试
pytest tests/e2e/
```

### 运行特定测试文件

```bash
pytest tests/integration/test_login_simple.py
```

### 详细输出

```bash
# 详细模式
pytest -v

# 显示 print 输出
pytest -s

# 详细 + print
pytest -vs
```

### 停止于第一个失败

```bash
pytest -x
```

### 运行匹配的测试

```bash
# 运行名称包含 "login" 的测试
pytest -k login
```

---

## 🔧 开发命令

### 启动 API 服务器

```bash
# 开发模式（自动重载）
uvicorn aerotest.api.main:app --reload

# 指定端口
uvicorn aerotest.api.main:app --reload --port 8080
```

### 安装新依赖

```bash
# 安装单个包
pip install <package-name>

# 安装多个包
pip install package1 package2 package3

# 更新 requirements.txt
pip freeze > requirements.txt
```

### 以可编辑模式安装项目

```bash
pip install -e .
```

这样可以直接导入 `aerotest` 模块，无需每次都安装。

---

## 📁 项目结构

```
d:\projects\OODA\
├── 激活虚拟环境.bat          # Windows CMD 激活脚本 ⭐
├── 激活虚拟环境.ps1           # PowerShell 激活脚本 ⭐
├── README.md                  # 项目说明
├── README-虚拟环境使用指南.md # 本文件 ⭐
├── requirements.txt           # 依赖列表
├── pyproject.toml            # 项目配置
│
├── venv/                     # Python 虚拟环境
│   ├── Scripts/              # Windows 脚本
│   ├── Lib/                  # Python 库
│   └── ...
│
├── aerotest/                 # 核心代码
│   ├── api/                  # API 模块
│   ├── browser/              # 浏览器控制
│   ├── core/                 # 核心引擎
│   │   ├── funnel/          # 五层漏斗
│   │   └── ooda/            # OODA 循环
│   ├── db/                   # 数据库
│   ├── config/               # 配置
│   ├── utils/                # 工具
│   └── ai/                   # AI 模块
│
├── tests/                    # 测试目录 ⭐
│   ├── unit/                 # 单元测试
│   │   ├── ooda/
│   │   ├── funnel/
│   │   └── dom/
│   ├── integration/          # 集成测试
│   │   ├── test_login_simple.py    # 登录测试 ⭐
│   │   ├── test_login_real.py
│   │   └── test_login_mock.py
│   └── e2e/                  # 端到端测试
│
├── docs/                     # 文档目录 ⭐
│   ├── requirement.md
│   ├── 测试报告-登录用例.md
│   └── ...
│
├── scripts/                  # 脚本目录 ⭐
│   ├── init_project.py
│   └── ...
│
└── examples/                 # 示例代码
    ├── cdp_session_usage.py
    └── ...
```

---

## 💡 常用工作流

### 开始工作

```bash
# 1. 激活虚拟环境
.\激活虚拟环境.ps1

# 2. 拉取最新代码
git pull

# 3. 安装/更新依赖
pip install -r requirements.txt
```

### 开发新功能

```bash
# 1. 创建新分支
git checkout -b feature/new-feature

# 2. 编写代码
# ...

# 3. 运行测试
pytest

# 4. 提交代码
git add .
git commit -m "feat: 添加新功能"
git push origin feature/new-feature
```

### 修复 Bug

```bash
# 1. 创建分支
git checkout -b fix/bug-description

# 2. 修复代码
# ...

# 3. 运行测试
pytest -v

# 4. 提交
git add .
git commit -m "fix: 修复某个 Bug"
git push origin fix/bug-description
```

### 结束工作

```bash
# 1. 确保测试通过
pytest

# 2. 提交并推送
git push

# 3. 退出虚拟环境
deactivate
```

---

## 🐛 故障排除

### 虚拟环境无法激活

**问题**：PowerShell 执行策略限制

```bash
# 查看当前策略
Get-ExecutionPolicy

# 临时允许脚本执行（仅当前会话）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# 然后再次激活
.\激活虚拟环境.ps1
```

### 依赖安装失败

```bash
# 清理 pip 缓存
pip cache purge

# 升级 pip
python -m pip install --upgrade pip

# 重新安装依赖
pip install -r requirements.txt
```

### 测试无法找到模块

```bash
# 确保在虚拟环境中
.\激活虚拟环境.ps1

# 以可编辑模式安装项目
pip install -e .

# 再次运行测试
pytest
```

### ImportError: No module named 'aerotest'

```bash
# 方法 1: 以可编辑模式安装
pip install -e .

# 方法 2: 设置 PYTHONPATH
$env:PYTHONPATH = "d:\projects\OODA"
pytest
```

---

## 📚 更多资源

### 项目文档
- 📄 [需求文档](docs/requirement.md)
- 📄 [技术架构](docs/AeroTest-技术架构设计.md)
- 📄 [快速开始](docs/快速开始指南.md)

### 测试文档
- 📄 [测试报告-登录用例](docs/测试报告-登录用例.md)
- 📄 [集成测试方案](docs/集成测试方案.md)

### Python 虚拟环境
- 🔗 [官方文档](https://docs.python.org/3/library/venv.html)
- 🔗 [Pytest 文档](https://docs.pytest.org/)
- 🔗 [FastAPI 文档](https://fastapi.tiangolo.com/)

---

## ✨ 最佳实践

### 1. 始终在虚拟环境中工作

❌ **不好的做法**：
```bash
python test.py
```

✅ **好的做法**：
```bash
.\激活虚拟环境.ps1
python test.py
```

### 2. 定期更新依赖

```bash
# 检查过期的包
pip list --outdated

# 升级特定包
pip install --upgrade <package-name>

# 更新 requirements.txt
pip freeze > requirements.txt
```

### 3. 运行测试后再提交

```bash
# 运行测试
pytest -v

# 确保通过后再提交
git commit -m "..."
```

### 4. 保持虚拟环境独立

- 每个项目使用独立的虚拟环境
- 不要在全局环境安装项目依赖
- 使用 `requirements.txt` 管理依赖

---

## 🎯 下一步

1. **熟悉项目结构** - 浏览 `aerotest/` 目录
2. **运行测试** - `pytest tests/integration/test_login_simple.py -v`
3. **阅读文档** - 查看 `docs/` 目录中的文档
4. **开始开发** - 根据需求添加新功能

---

**最后更新**: 2025-12-19  
**Python 版本**: 3.12.6  
**虚拟环境**: venv/
