#!/bin/bash

# 快速启动脚本 - 自动激活虚拟环境并运行程序

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "错误：虚拟环境不存在"
    echo "请先运行安装脚本： ./install_vps.sh"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 显示菜单
echo "================================================================"
echo "         公交车线路规划系统"
echo "================================================================"
echo ""
echo "请选择要运行的程序："
echo ""
echo "  1. 交互式路线规划程序"
echo "  2. Web API服务"
echo "  3. 运行测试"
echo "  4. 退出"
echo ""
read -p "请输入选项 (1-4): " choice

case $choice in
    1)
        echo ""
        echo "启动交互式程序..."
        python main.py
        ;;
    2)
        echo ""
        echo "启动Web API服务..."
        echo "访问地址: http://localhost:5000"
        echo "按 Ctrl+C 停止服务"
        echo ""
        python api_server.py
        ;;
    3)
        echo ""
        echo "运行测试..."
        python tests/test_nanshan.py
        ;;
    4)
        echo "退出"
        ;;
    *)
        echo "无效选项"
        ;;
esac

# 退出虚拟环境
deactivate
