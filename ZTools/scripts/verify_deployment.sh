#!/bin/bash

# ZTools 部署验证脚本
# 用于验证部署后的环境是否正确配置

set -e

echo "=========================================="
echo "ZTools 部署验证脚本"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查计数器
checks_passed=0
checks_failed=0

# 检查函数
check() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ $2${NC}"
        ((checks_passed++))
    else
        echo -e "${RED}✗ $2${NC}"
        ((checks_failed++))
    fi
}

# 获取项目根目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo ""
echo "项目根目录: $PROJECT_ROOT"

# 1. 检查 Python 版本
echo ""
echo "------------------------------------------"
echo "1. 检查 Python 环境"
echo "------------------------------------------"

if command -v python3 &> /dev/null; then
    python_version=$(python3 --version 2>&1)
    echo "Python 版本: $python_version"
    
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 13) else 1)"; then
        check 0 "Python 版本 >= 3.13"
    else
        check 1 "Python 版本 >= 3.13"
    fi
else
    check 1 "Python 3 已安装"
fi

# 2. 检查项目结构
echo ""
echo "------------------------------------------"
echo "2. 检查项目结构"
echo "------------------------------------------"

[ -d "$PROJECT_ROOT/.trae/skills/zentao-helper" ]
check $? "zentao-helper Skill 目录存在"

[ -f "$PROJECT_ROOT/.trae/skills/zentao-helper/skill.py" ]
check $? "skill.py 文件存在"

[ -f "$PROJECT_ROOT/.trae/skills/zentao-helper/SKILL.md" ]
check $? "SKILL.md 文件存在"

[ -f "$PROJECT_ROOT/.trae/skills/zentao-helper/requirements.txt" ]
check $? "requirements.txt 文件存在"

[ -d "$PROJECT_ROOT/docs" ]
check $? "docs 目录存在"

[ -f "$PROJECT_ROOT/README.md" ]
check $? "README.md 文件存在"

[ -f "$PROJECT_ROOT/AGENTS.md" ]
check $? "AGENTS.md 文件存在"

# 3. 检查配置文件
echo ""
echo "------------------------------------------"
echo "3. 检查配置文件"
echo "------------------------------------------"

CONFIG_FILE="$PROJECT_ROOT/.trae/skills/zentao-helper/config/settings.yaml"
if [ -f "$CONFIG_FILE" ]; then
    check 0 "settings.yaml 配置文件存在"
    
    # 检查关键配置项
    if grep -q "base_url:" "$CONFIG_FILE"; then
        check 0 "zentao.base_url 配置项存在"
    else
        check 1 "zentao.base_url 配置项存在"
    fi
    
    if grep -q "timeout:" "$CONFIG_FILE"; then
        check 0 "zentao.timeout 配置项存在"
    else
        check 1 "zentao.timeout 配置项存在"
    fi
else
    check 1 "settings.yaml 配置文件存在"
fi

# 4. 检查依赖安装
echo ""
echo "------------------------------------------"
echo "4. 检查 Python 依赖"
echo "------------------------------------------"

# 检查关键依赖
python3 -c "import requests" 2>/dev/null
check $? "requests 库已安装"

python3 -c "import yaml" 2>/dev/null
check $? "PyYAML 库已安装"

python3 -c "import keyring" 2>/dev/null
check $? "keyring 库已安装"

python3 -c "import cryptography" 2>/dev/null
check $? "cryptography 库已安装"

# 5. 检查网络连接
echo ""
echo "------------------------------------------"
echo "5. 检查网络连接"
echo "------------------------------------------"

# 从配置文件中读取禅道服务器地址
if [ -f "$CONFIG_FILE" ]; then
    zentao_url=$(grep "base_url:" "$CONFIG_FILE" | sed 's/.*base_url: *"\?\([^"]*\)"\?.*/\1/')
    
    if [ -n "$zentao_url" ]; then
        echo "禅道服务器地址: $zentao_url"
        
        # 尝试连接（仅检查网络连通性，不验证登录）
        if curl -s --max-time 5 "$zentao_url" > /dev/null 2>&1; then
            check 0 "禅道服务器可访问"
        else
            check 1 "禅道服务器可访问"
            echo -e "${YELLOW}  提示: 请检查网络连接或禅道服务器地址配置${NC}"
        fi
    else
        check 1 "禅道服务器地址配置正确"
    fi
fi

# 6. 检查日志目录
echo ""
echo "------------------------------------------"
echo "6. 检查日志目录"
echo "------------------------------------------"

if [ -d "$PROJECT_ROOT/logs" ]; then
    check 0 "logs 目录存在"
    
    # 检查写入权限
    if [ -w "$PROJECT_ROOT/logs" ]; then
        check 0 "logs 目录可写"
    else
        check 1 "logs 目录可写"
    fi
else
    check 1 "logs 目录存在"
fi

# 总结
echo ""
echo "=========================================="
echo "验证结果"
echo "=========================================="
echo ""
echo "通过: $checks_passed"
echo "失败: $checks_failed"
echo ""

if [ $checks_failed -eq 0 ]; then
    echo -e "${GREEN}✓ 所有检查通过！部署验证成功。${NC}"
    echo ""
    echo "您现在可以在 Trae IDE 中使用 ZTools 了。"
    echo "首次使用时会提示登录禅道。"
    exit 0
else
    echo -e "${YELLOW}⚠ 部分检查未通过，请查看上面的详细信息。${NC}"
    echo ""
    echo "建议:"
    echo "  1. 运行 ./scripts/setup.sh 完成初始化"
    echo "  2. 检查配置文件是否正确"
    echo "  3. 确保网络连接正常"
    exit 1
fi
