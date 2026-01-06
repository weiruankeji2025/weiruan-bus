#!/bin/bash

# API服务启动脚本 - 自动处理编码并后台运行

# 设置UTF-8编码
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
export PYTHONIOENCODING=utf-8

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "错误：虚拟环境不存在"
    echo "请先运行安装脚本： ./install_vps.sh"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 启动API服务
echo "================================================================"
echo "         启动公交车线路规划系统 Web API 服务"
echo "================================================================"
echo ""
echo "访问地址: http://0.0.0.0:5000"
echo "API文档: http://0.0.0.0:5000/"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

python api_server.py

# 退出虚拟环境
deactivate
