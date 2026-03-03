# ZTools 部署验证脚本 (PowerShell)
# 用于验证部署后的环境是否正确配置

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "ZTools 部署验证脚本" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 检查计数器
$checksPassed = 0
$checksFailed = 0

# 检查函数
function Check-Condition {
    param(
        [bool]$Condition,
        [string]$Message
    )
    
    if ($Condition) {
        Write-Host "✓ $Message" -ForegroundColor Green
        $script:checksPassed++
    } else {
        Write-Host "✗ $Message" -ForegroundColor Red
        $script:checksFailed++
    }
}

# 获取项目根目录
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir

Write-Host ""
Write-Host "项目根目录: $projectRoot"

# 1. 检查 Python 版本
Write-Host ""
Write-Host "------------------------------------------" -ForegroundColor Cyan
Write-Host "1. 检查 Python 环境" -ForegroundColor Cyan
Write-Host "------------------------------------------" -ForegroundColor Cyan

try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python 版本: $pythonVersion"
    
    $versionMatch = $pythonVersion -match "Python (\d+)\.(\d+)"
    if ($versionMatch) {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]
        
        Check-Condition ($major -gt 3 -or ($major -eq 3 -and $minor -ge 13)) "Python 版本 >= 3.13"
    } else {
        Check-Condition $false "Python 版本 >= 3.13"
    }
} catch {
    Check-Condition $false "Python 3 已安装"
}

# 2. 检查项目结构
Write-Host ""
Write-Host "------------------------------------------" -ForegroundColor Cyan
Write-Host "2. 检查项目结构" -ForegroundColor Cyan
Write-Host "------------------------------------------" -ForegroundColor Cyan

$skillDir = Join-Path $projectRoot ".trae\skills\zentao-helper"
Check-Condition (Test-Path $skillDir) "zentao-helper Skill 目录存在"

Check-Condition (Test-Path (Join-Path $skillDir "skill.py")) "skill.py 文件存在"
Check-Condition (Test-Path (Join-Path $skillDir "SKILL.md")) "SKILL.md 文件存在"
Check-Condition (Test-Path (Join-Path $skillDir "requirements.txt")) "requirements.txt 文件存在"

Check-Condition (Test-Path (Join-Path $projectRoot "docs")) "docs 目录存在"
Check-Condition (Test-Path (Join-Path $projectRoot "README.md")) "README.md 文件存在"
Check-Condition (Test-Path (Join-Path $projectRoot "AGENTS.md")) "AGENTS.md 文件存在"

# 3. 检查配置文件
Write-Host ""
Write-Host "------------------------------------------" -ForegroundColor Cyan
Write-Host "3. 检查配置文件" -ForegroundColor Cyan
Write-Host "------------------------------------------" -ForegroundColor Cyan

$configFile = Join-Path $skillDir "config\settings.yaml"
if (Test-Path $configFile) {
    Check-Condition $true "settings.yaml 配置文件存在"
    
    # 检查关键配置项
    $configContent = Get-Content $configFile -Raw
    Check-Condition ($configContent -match "base_url:") "zentao.base_url 配置项存在"
    Check-Condition ($configContent -match "timeout:") "zentao.timeout 配置项存在"
} else {
    Check-Condition $false "settings.yaml 配置文件存在"
}

# 4. 检查依赖安装
Write-Host ""
Write-Host "------------------------------------------" -ForegroundColor Cyan
Write-Host "4. 检查 Python 依赖" -ForegroundColor Cyan
Write-Host "------------------------------------------" -ForegroundColor Cyan

# 检查关键依赖
try {
    python -c "import requests" 2>$null
    Check-Condition $true "requests 库已安装"
} catch {
    Check-Condition $false "requests 库已安装"
}

try {
    python -c "import yaml" 2>$null
    Check-Condition $true "PyYAML 库已安装"
} catch {
    Check-Condition $false "PyYAML 库已安装"
}

try {
    python -c "import keyring" 2>$null
    Check-Condition $true "keyring 库已安装"
} catch {
    Check-Condition $false "keyring 库已安装"
}

try {
    python -c "import cryptography" 2>$null
    Check-Condition $true "cryptography 库已安装"
} catch {
    Check-Condition $false "cryptography 库已安装"
}

# 5. 检查网络连接
Write-Host ""
Write-Host "------------------------------------------" -ForegroundColor Cyan
Write-Host "5. 检查网络连接" -ForegroundColor Cyan
Write-Host "------------------------------------------" -ForegroundColor Cyan

if (Test-Path $configFile) {
    $configContent = Get-Content $configFile -Raw
    if ($configContent -match 'base_url:\s*"([^"]+)"') {
        $zentaoUrl = $matches[1]
        Write-Host "禅道服务器地址: $zentaoUrl"
        
        try {
            $response = Invoke-WebRequest -Uri $zentaoUrl -TimeoutSec 5 -UseBasicParsing
            Check-Condition ($response.StatusCode -eq 200) "禅道服务器可访问"
        } catch {
            Check-Condition $false "禅道服务器可访问"
            Write-Host "  提示: 请检查网络连接或禅道服务器地址配置" -ForegroundColor Yellow
        }
    } else {
        Check-Condition $false "禅道服务器地址配置正确"
    }
}

# 6. 检查日志目录
Write-Host ""
Write-Host "------------------------------------------" -ForegroundColor Cyan
Write-Host "6. 检查日志目录" -ForegroundColor Cyan
Write-Host "------------------------------------------" -ForegroundColor Cyan

$logsDir = Join-Path $projectRoot "logs"
Check-Condition (Test-Path $logsDir) "logs 目录存在"

if (Test-Path $logsDir) {
    try {
        $testFile = Join-Path $logsDir ".write_test"
        "test" | Out-File $testFile -ErrorAction Stop
        Remove-Item $testFile
        Check-Condition $true "logs 目录可写"
    } catch {
        Check-Condition $false "logs 目录可写"
    }
}

# 总结
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "验证结果" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "通过: $checksPassed"
Write-Host "失败: $checksFailed"
Write-Host ""

if ($checksFailed -eq 0) {
    Write-Host "✓ 所有检查通过！部署验证成功。" -ForegroundColor Green
    Write-Host ""
    Write-Host "您现在可以在 Trae IDE 中使用 ZTools 了。"
    Write-Host "首次使用时会提示登录禅道。"
    exit 0
} else {
    Write-Host "⚠ 部分检查未通过，请查看上面的详细信息。" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "建议:"
    Write-Host "  1. 运行 .\scripts\setup.ps1 完成初始化"
    Write-Host "  2. 检查配置文件是否正确"
    Write-Host "  3. 确保网络连接正常"
    exit 1
}
