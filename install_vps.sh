#!/bin/bash

# 公交车线路规划系统 - VPS快速安装脚本（虚拟环境版本）
# 适用于 Ubuntu/Debian 系统

set -e

echo "================================================================"
echo "         公交车线路规划系统 - VPS自动安装脚本"
echo "                   (使用Python虚拟环境)"
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
echo "步骤 1/6: 更新系统包..."
if [ "$OS" = "debian" ]; then
    sudo apt update -y
else
    sudo yum update -y
fi

echo ""
echo "步骤 2/6: 安装Python3、pip、git和虚拟环境工具..."
if [ "$OS" = "debian" ]; then
    sudo apt install -y python3 python3-pip python3-venv git
else
    sudo yum install -y python3 python3-pip git
fi

# 检查Python版本
echo ""
echo "步骤 3/6: 检查Python版本..."
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Python版本: $PYTHON_VERSION"

if command -v bc &> /dev/null; then
    if (( $(echo "$PYTHON_VERSION < 3.8" | bc -l) )); then
        echo "✗ Python版本过低，需要3.8或更高版本"
        exit 1
    fi
fi

echo "✓ Python版本符合要求"

echo ""
echo "步骤 4/6: 创建Python虚拟环境..."
if [ -d "venv" ]; then
    echo "虚拟环境已存在，跳过创建"
else
    python3 -m venv venv
    echo "✓ 虚拟环境创建成功"
fi

echo ""
echo "步骤 5/6: 激活虚拟环境并安装依赖..."
source venv/bin/activate

if [ -f "requirements.txt" ]; then
    echo "使用国内镜像安装依赖..."
    pip install --upgrade pip
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    echo "✓ 依赖安装完成"
else
    echo "✗ 找不到 requirements.txt 文件"
    echo "请确保在项目根目录运行此脚本"
    exit 1
fi

echo ""
echo "步骤 6/6: 验证安装..."
python -c "import sys; sys.path.append('.'); from src.data.shenzhen_nanshan import load_nanshan_data; graph = load_nanshan_data(); print('✓ 数据加载成功，站点数:', len(graph.stations))" 2>/dev/null

if [ $? -eq 0 ]; then
    echo ""
    echo "================================================================"
    echo "                   安装成功！"
    echo "================================================================"
    echo ""
    echo "虚拟环境已创建在: ./venv"
    echo ""
    echo "使用方法："
    echo ""
    echo "  1. 激活虚拟环境："
    echo "     source venv/bin/activate"
    echo ""
    echo "  2. 运行交互式程序："
    echo "     python main.py"
    echo ""
    echo "  3. 运行API服务："
    echo "     python api_server.py"
    echo ""
    echo "  4. 运行测试："
    echo "     python tests/test_nanshan.py"
    echo ""
    echo "  5. 退出虚拟环境："
    echo "     deactivate"
    echo ""
    echo "  6. 查看详细使用指南："
    echo "     cat VPS_INSTALL_GUIDE.md"
    echo ""
    echo "================================================================"
    echo ""
    echo "快速启动（自动激活虚拟环境）："
    echo "  ./run.sh"
    echo ""
    echo "================================================================"

    deactivate
else
    echo ""
    echo "✗ 验证失败，请检查错误信息"
    deactivate
    exit 1
fi
