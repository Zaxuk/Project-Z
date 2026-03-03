#!/bin/bash

# ZTools 一键初始化脚本
# 用于设置开发环境和安装依赖

set -e

echo "=========================================="
echo "ZTools 初始化脚本"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查 Python 版本
echo ""
echo "检查 Python 版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python 版本: $python_version"

# 检查是否为 3.13+
if python3 -c "import sys; exit(0 if sys.version_info >= (3, 13) else 1)"; then
    echo -e "${GREEN}✓ Python 版本符合要求 (>= 3.13)${NC}"
else
    echo -e "${RED}✗ Python 版本过低，需要 3.13 或更高版本${NC}"
    exit 1
fi

# 检查 pip
echo ""
echo "检查 pip..."
if command -v pip3 &> /dev/null; then
    echo -e "${GREEN}✓ pip 已安装${NC}"
else
    echo -e "${RED}✗ pip 未安装，请先安装 pip${NC}"
    exit 1
fi

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo ""
echo "项目根目录: $PROJECT_ROOT"

# 安装 Skill 依赖
echo ""
echo "=========================================="
echo "安装 Skill 依赖"
echo "=========================================="

SKILL_DIR="$PROJECT_ROOT/.trae/skills/zentao-helper"
if [ -d "$SKILL_DIR" ]; then
    echo ""
    echo "安装 zentao-helper 依赖..."
    cd "$SKILL_DIR"
    
    # 创建虚拟环境（如果不存在）
    if [ ! -d "venv" ]; then
        echo "创建虚拟环境..."
        python3 -m venv venv
    fi
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 升级 pip
    pip install --upgrade pip
    
    # 安装依赖
    pip install -r requirements.txt
    
    echo -e "${GREEN}✓ zentao-helper 依赖安装完成${NC}"
else
    echo -e "${YELLOW}⚠ zentao-helper 目录不存在，跳过${NC}"
fi

# 创建必要的目录
echo ""
echo "=========================================="
echo "创建项目目录结构"
echo "=========================================="

mkdir -p "$PROJECT_ROOT/logs"
mkdir -p "$PROJECT_ROOT/temp"

echo -e "${GREEN}✓ 目录创建完成${NC}"

# 检查配置文件
echo ""
echo "=========================================="
echo "检查配置文件"
echo "=========================================="

CONFIG_FILE="$SKILL_DIR/config/settings.yaml"
if [ -f "$CONFIG_FILE" ]; then
    echo -e "${GREEN}✓ 配置文件已存在: $CONFIG_FILE${NC}"
    
    # 提示用户检查配置
    echo ""
    echo -e "${YELLOW}请检查配置文件中的以下项:${NC}"
    echo "  - zentao.base_url: 禅道服务器地址"
    echo "  - zentao.timeout: 请求超时时间"
    echo "  - story_query.products: 要查询的产品列表"
    echo ""
    echo "配置文件路径: $CONFIG_FILE"
else
    echo -e "${RED}✗ 配置文件不存在: $CONFIG_FILE${NC}"
    echo "请从 settings.yaml.example 复制并修改"
fi

# 完成
echo ""
echo "=========================================="
echo -e "${GREEN}初始化完成！${NC}"
echo "=========================================="
echo ""
echo "下一步:"
echo "  1. 检查并修改配置文件"
echo "  2. 在 Trae IDE 中使用 Skill"
echo "  3. 首次使用时会提示登录禅道"
echo ""
echo "常用命令:"
echo "  查看需求: '查看我的需求'"
echo "  查看任务: '查看我的任务'"
echo "  任务拆解: '拆解任务#123'"
echo "  任务分配: '把任务#456分配给张三'"
echo ""
