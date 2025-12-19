# AeroTest AI - 虚拟环境激活脚本 (PowerShell)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AeroTest AI - 虚拟环境激活脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $projectRoot

if (-not (Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "[错误] 虚拟环境不存在！" -ForegroundColor Red
    Write-Host "请先运行: python -m venv venv" -ForegroundColor Yellow
    Read-Host "按任意键退出"
    exit 1
}

Write-Host "[激活] 正在激活虚拟环境..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✅ 虚拟环境已激活！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📦 可用命令：" -ForegroundColor Cyan
Write-Host "  - pytest              运行所有测试" -ForegroundColor White
Write-Host "  - pytest -v           详细输出" -ForegroundColor White
Write-Host "  - pytest -s           显示 print 输出" -ForegroundColor White
Write-Host "  - python              启动 Python" -ForegroundColor White
Write-Host "  - deactivate          退出虚拟环境" -ForegroundColor White
Write-Host ""
Write-Host "🐍 Python 版本:" -ForegroundColor Cyan
python --version
Write-Host ""
Write-Host "📚 已安装的主要包：" -ForegroundColor Cyan
pip list | Select-String -Pattern "pytest|fastapi|pydantic|loguru"
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "开始工作吧！🚀" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
