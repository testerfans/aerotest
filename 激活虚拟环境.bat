@echo off
echo ========================================
echo   AeroTest AI - 虚拟环境激活脚本
echo ========================================
echo.

cd /d "%~dp0"

if not exist "venv\Scripts\activate.bat" (
    echo [错误] 虚拟环境不存在！
    echo 请先运行: python -m venv venv
    pause
    exit /b 1
)

echo [激活] 正在激活虚拟环境...
call venv\Scripts\activate.bat

echo.
echo ========================================
echo   ✅ 虚拟环境已激活！
echo ========================================
echo.
echo 📦 可用命令：
echo   - pytest              运行所有测试
echo   - pytest -v           详细输出
echo   - python              启动 Python
echo   - deactivate          退出虚拟环境
echo.
echo 🐍 Python 版本:
python --version
echo.
echo ========================================
