# ZTools 一键初始化脚本 (PowerShell)
# 用于设置开发环境和安装依赖

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "ZTools 初始化脚本" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 检查 Python 版本
Write-Host ""
Write-Host "检查 Python 版本..."

try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python 版本: $pythonVersion"
    
    # 提取版本号
    $versionMatch = $pythonVersion -match "Python (\d+)\.(\d+)"
    if ($versionMatch) {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        
        if ($major -gt 3 -or ($major -eq 3 -and $minor -ge 13)) {
            Write-Host "✓ Python 版本符合要求 (>= 3.13)" -ForegroundColor Green
        } else {
            Write-Host "✗ Python 版本过低，需要 3.13 或更高版本" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "✗ 无法解析 Python 版本" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ Python 未安装或不在 PATH 中" -ForegroundColor Red
    exit 1
}

# 检查 pip
Write-Host ""
Write-Host "检查 pip..."
try {
    $pipVersion = pip --version
    Write-Host "✓ pip 已安装" -ForegroundColor Green
} catch {
    Write-Host "✗ pip 未安装，请先安装 pip" -ForegroundColor Red
    exit 1
}

# 获取脚本所在目录
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir

Write-Host ""
Write-Host "项目根目录: $projectRoot"

# 安装 Skill 依赖
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "安装 Skill 依赖" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

$skillDir = Join-Path $projectRoot ".trae\skills\zentao-helper"
if (Test-Path $skillDir) {
    Write-Host ""
    Write-Host "安装 zentao-helper 依赖..."
    Set-Location $skillDir
    
    # 创建虚拟环境（如果不存在）
    $venvDir = Join-Path $skillDir "venv"
    if (-not (Test-Path $venvDir)) {
        Write-Host "创建虚拟环境..."
        python -m venv venv
    }
    
    # 激活虚拟环境
    $activateScript = Join-Path $venvDir "Scripts\Activate.ps1"
    if (Test-Path $activateScript) {
        & $activateScript
    }
    
    # 升级 pip
    pip install --upgrade pip
    
    # 安装依赖
    pip install -r requirements.txt
    
    Write-Host "✓ zentao-helper 依赖安装完成" -ForegroundColor Green
} else {
    Write-Host "⚠ zentao-helper 目录不存在，跳过" -ForegroundColor Yellow
}

# 创建必要的目录
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "创建项目目录结构" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

$logsDir = Join-Path $projectRoot "logs"
$tempDir = Join-Path $projectRoot "temp"

New-Item -ItemType Directory -Force -Path $logsDir | Out-Null
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null

Write-Host "✓ 目录创建完成" -ForegroundColor Green

# 检查配置文件
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "检查配置文件" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

$configFile = Join-Path $skillDir "config\settings.yaml"
if (Test-Path $configFile) {
    Write-Host "✓ 配置文件已存在: $configFile" -ForegroundColor Green
    
    # 提示用户检查配置
    Write-Host ""
    Write-Host "请检查配置文件中的以下项:" -ForegroundColor Yellow
    Write-Host "  - zentao.base_url: 禅道服务器地址"
    Write-Host "  - zentao.timeout: 请求超时时间"
    Write-Host "  - story_query.products: 要查询的产品列表"
    Write-Host ""
    Write-Host "配置文件路径: $configFile"
} else {
    Write-Host "✗ 配置文件不存在: $configFile" -ForegroundColor Red
    Write-Host "请从 settings.yaml.example 复制并修改"
}

# 完成
Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "初始化完成！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "下一步:"
Write-Host "  1. 检查并修改配置文件"
Write-Host "  2. 在 Trae IDE 中使用 Skill"
Write-Host "  3. 首次使用时会提示登录禅道"
Write-Host ""
Write-Host "常用命令:"
Write-Host "  查看需求: '查看我的需求'"
Write-Host "  查看任务: '查看我的任务'"
Write-Host "  任务拆解: '拆解任务#123'"
Write-Host "  任务分配: '把任务#456分配给张三'"
Write-Host ""

# 返回原目录
Set-Location $PSScriptRoot
