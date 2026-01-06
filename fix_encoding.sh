#!/bin/bash

# 修复系统编码问题的脚本

echo "================================================================"
echo "         修复系统UTF-8编码配置"
echo "================================================================"
echo ""

echo "步骤 1/4: 安装语言包..."
sudo apt update
sudo apt install -y language-pack-zh-hans locales

echo ""
echo "步骤 2/4: 生成locale..."
sudo locale-gen en_US.UTF-8
sudo locale-gen zh_CN.UTF-8

echo ""
echo "步骤 3/4: 更新系统locale..."
sudo update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8

echo ""
echo "步骤 4/4: 配置用户环境..."
if ! grep -q "export LANG=en_US.UTF-8" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "# UTF-8 编码配置" >> ~/.bashrc
    echo "export LANG=en_US.UTF-8" >> ~/.bashrc
    echo "export LC_ALL=en_US.UTF-8" >> ~/.bashrc
    echo "export PYTHONIOENCODING=utf-8" >> ~/.bashrc
    echo "✓ 已添加到 ~/.bashrc"
else
    echo "✓ 环境变量已存在于 ~/.bashrc"
fi

echo ""
echo "================================================================"
echo "                   配置完成！"
echo "================================================================"
echo ""
echo "请执行以下操作之一："
echo ""
echo "  方法1（推荐）：重新登录SSH"
echo "    exit"
echo "    ssh username@your-server"
echo ""
echo "  方法2：重新加载配置"
echo "    source ~/.bashrc"
echo ""
echo "  方法3：直接使用启动脚本（已自动设置编码）"
echo "    ./run.sh"
echo ""
echo "验证编码："
echo "    locale"
echo ""
echo "================================================================"
