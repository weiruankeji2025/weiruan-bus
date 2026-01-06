#!/bin/bash

# 公交车线路规划系统 - VPS快速安装脚本
# 适用于 Ubuntu/Debian 系统

set -e  # 遇到错误立即退出

echo "================================================================"
echo "         公交车线路规划系统 - VPS自动安装脚本"
echo "================================================================"
echo ""

# 检测系统类型
if [ -f /etc/debian_version ]; then
    OS="debian"
    echo "✓ 检测到 Debian/Ubuntu 系统"
elif [ -f /etc/redhat-release ]; then
    OS="redhat"
    echo "✓ 检测到 CentOS/RHEL 系统"
else
    echo "✗ 不支持的操作系统"
    exit 1
fi

echo ""
echo "步骤 1/5: 更新系统包..."
if [ "$OS" = "debian" ]; then
    sudo apt update -y
else
    sudo yum update -y
fi

echo ""
echo "步骤 2/5: 安装Python3和必要工具..."
if [ "$OS" = "debian" ]; then
    sudo apt install -y python3 python3-pip git
else
    sudo yum install -y python3 python3-pip git
fi

# 检查Python版本
echo ""
echo "步骤 3/5: 检查Python版本..."
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Python版本: $PYTHON_VERSION"

if (( $(echo "$PYTHON_VERSION < 3.8" | bc -l) )); then
    echo "✗ Python版本过低，需要3.8或更高版本"
    exit 1
fi

echo "✓ Python版本符合要求"

echo ""
echo "步骤 4/5: 安装Python依赖包..."
if [ -f "requirements.txt" ]; then
    echo "使用国内镜像安装依赖..."
    pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
else
    echo "✗ 找不到 requirements.txt 文件"
    echo "请确保在项目根目录运行此脚本"
    exit 1
fi

echo ""
echo "步骤 5/5: 验证安装..."
python3 -c "import sys; sys.path.append('.'); from src.data.shenzhen_nanshan import load_nanshan_data; graph = load_nanshan_data(); print('✓ 数据加载成功，站点数:', len(graph.stations))" 2>/dev/null

if [ $? -eq 0 ]; then
    echo ""
    echo "================================================================"
    echo "                   安装成功！"
    echo "================================================================"
    echo ""
    echo "使用方法："
    echo ""
    echo "  1. 运行交互式程序："
    echo "     python3 main.py"
    echo ""
    echo "  2. 运行测试："
    echo "     python3 tests/test_nanshan.py"
    echo ""
    echo "  3. 查看详细使用指南："
    echo "     cat VPS_INSTALL_GUIDE.md"
    echo ""
    echo "================================================================"
else
    echo ""
    echo "✗ 验证失败，请检查错误信息"
    exit 1
fi
