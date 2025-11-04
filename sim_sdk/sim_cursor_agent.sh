#!/bin/bash

# sim_sdk.py 执行脚本
# 用于运行 Cursor CLI SDK 模拟器

# 设置脚本目录
SCRIPT_DIR="/data/auto-coder/sim_sdk"
PYTHON_SCRIPT="${SCRIPT_DIR}/sim_sdk.py"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印错误信息
print_error() {
    echo -e "${RED}[错误]${NC} $1" >&2
}

# 打印成功信息
print_success() {
    echo -e "${GREEN}[成功]${NC} $1"
}

# 打印警告信息
print_warning() {
    echo -e "${YELLOW}[警告]${NC} $1"
}

# 检查 Python 是否安装
check_python() {
    if ! command -v python3 &> /dev/null; then
        if ! command -v python &> /dev/null; then
            print_error "未找到 Python。请先安装 Python 3。"
            exit 1
        else
            PYTHON_CMD="python"
        fi
    else
        PYTHON_CMD="python3"
    fi
    
    # 检查 Python 版本
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
    print_success "找到 Python: $PYTHON_VERSION"
}

# 检查必要的依赖
check_dependencies() {
    print_warning "检查依赖包..."
    
    # 检查 requests 库
    if ! $PYTHON_CMD -c "import requests" 2>/dev/null; then
        print_warning "requests 库未安装，正在安装..."
        $PYTHON_CMD -m pip install requests --quiet
        if [ $? -eq 0 ]; then
            print_success "requests 库安装成功"
        else
            print_error "无法安装 requests 库。请手动运行: pip install requests"
            exit 1
        fi
    else
        print_success "依赖检查通过"
    fi
}

# 检查 API Key
check_api_key() {
    if [ -z "$CURSOR_API_KEY" ]; then
        print_warning "未设置 CURSOR_API_KEY 环境变量"
        read -p "请输入 Cursor API Key (或按 Enter 跳过，将在脚本中设置): " api_key
        if [ -n "$api_key" ]; then
            export CURSOR_API_KEY="$api_key"
            print_success "API Key 已设置"
        else
            print_warning "未设置 API Key，脚本运行可能会失败"
        fi
    else
        print_success "API Key 已设置"
    fi
}

# 主函数
main() {
    echo "=========================================="
    echo "  Cursor CLI SDK 模拟器执行脚本"
    echo "=========================================="
    echo ""
    
    # 检查 Python
    check_python
    
    # 检查依赖
    check_dependencies
    
    # 检查 API Key
    check_api_key
    
    # 检查 Python 脚本是否存在
    if [ ! -f "$PYTHON_SCRIPT" ]; then
        print_error "找不到脚本文件: $PYTHON_SCRIPT"
        exit 1
    fi
    
    echo ""
    echo "=========================================="
    print_success "开始执行 sim_sdk.py"
    echo "=========================================="
    echo ""
    
    # 执行 Python 脚本
    cd "$SCRIPT_DIR"
    $PYTHON_CMD "$PYTHON_SCRIPT"
    EXIT_CODE=$?
    
    echo ""
    echo "=========================================="
    if [ $EXIT_CODE -eq 0 ]; then
        print_success "脚本执行完成"
    else
        print_error "脚本执行失败，退出码: $EXIT_CODE"
    fi
    echo "=========================================="
    
    exit $EXIT_CODE
}

# 运行主函数
main "$@"

