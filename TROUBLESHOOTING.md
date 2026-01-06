# 故障排除指南

## 常见问题及解决方案

### 1. UnicodeEncodeError: 'latin-1' codec can't encode characters

**问题描述：**
```
UnicodeEncodeError: 'latin-1' codec can't encode characters in position 0-5: ordinal not in range(256)
```

**原因：** 系统默认编码不是UTF-8，无法显示中文。

**解决方案：**

#### 方案A：使用修复脚本（最简单）
```bash
./fix_encoding.sh
```
然后重新登录SSH或执行 `source ~/.bashrc`

#### 方案B：使用启动脚本（临时解决）
```bash
./run.sh  # 脚本已自动设置UTF-8编码
```

#### 方案C：手动临时设置
```bash
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
export PYTHONIOENCODING=utf-8
source venv/bin/activate
python main.py
```

#### 方案D：永久配置（手动）
```bash
# 安装语言包
sudo apt update
sudo apt install -y language-pack-zh-hans

# 生成locale
sudo locale-gen en_US.UTF-8
sudo locale-gen zh_CN.UTF-8

# 更新系统配置
sudo update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8

# 添加到用户配置
echo 'export LANG=en_US.UTF-8' >> ~/.bashrc
echo 'export LC_ALL=en_US.UTF-8' >> ~/.bashrc
echo 'export PYTHONIOENCODING=utf-8' >> ~/.bashrc

# 重新加载
source ~/.bashrc

# 验证
locale  # 应该显示 en_US.UTF-8
```

---

### 2. externally-managed-environment / PEP 668 错误

**问题描述：**
```
error: externally-managed-environment
This environment is externally managed
```

**解决方案：** 使用虚拟环境（推荐）

```bash
# 重新运行安装脚本（自动创建虚拟环境）
./install_vps.sh

# 或手动创建虚拟环境
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### 3. 找不到模块 (ModuleNotFoundError)

**问题描述：**
```
ModuleNotFoundError: No module named 'flask'
```

**原因：**
- 没有激活虚拟环境
- 依赖包没有安装

**解决方案：**
```bash
# 确保在虚拟环境中
source venv/bin/activate

# 重新安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 验证安装
pip list
```

---

### 4. Permission denied 权限错误

**问题描述：**
```
bash: ./run.sh: Permission denied
```

**解决方案：**
```bash
# 添加执行权限
chmod +x run.sh
chmod +x install_vps.sh
chmod +x fix_encoding.sh
chmod +x run_api.sh

# 然后重新运行
./run.sh
```

---

### 5. 端口已被占用

**问题描述：**
```
OSError: [Errno 98] Address already in use
```

**原因：** 5000端口已被其他程序占用

**解决方案：**

#### 方案A：更换端口
```bash
# 设置环境变量使用其他端口
export API_PORT=8080
python api_server.py
```

#### 方案B：停止占用端口的程序
```bash
# 查找占用5000端口的进程
sudo lsof -i :5000

# 或
sudo netstat -tulpn | grep :5000

# 停止进程（替换PID为实际进程ID）
kill -9 PID
```

---

### 6. 站点不存在错误

**问题描述：**
```
error: 起点站不存在: XXX
```

**解决方案：**

使用正确的站点ID或搜索站点：

```bash
# 方法1：查看所有站点
curl http://localhost:5000/api/stations

# 方法2：搜索站点
curl "http://localhost:5000/api/search?name=科技"

# 方法3：在程序中搜索
# 运行 python main.py
# 选择 "1. 规划路线"
# 输入站点名称（支持模糊匹配）
```

---

### 7. 虚拟环境激活后命令找不到

**问题描述：**
激活虚拟环境后运行 `python` 提示找不到命令

**解决方案：**
```bash
# 确保venv正确创建
python3 -m venv venv --clear

# 重新激活
source venv/bin/activate

# 验证Python路径
which python  # 应该显示 /path/to/weiruan-bus/venv/bin/python
```

---

### 8. Git拉取失败

**问题描述：**
```
fatal: unable to access 'https://github.com/...': Could not resolve host
```

**解决方案：**

#### 检查网络
```bash
ping github.com
```

#### 使用国内镜像（如果GitHub访问困难）
```bash
# 使用Gitee镜像（如果有）
git clone https://gitee.com/your-repo/weiruan-bus.git

# 或配置代理
git config --global http.proxy http://proxy-server:port
```

---

### 9. systemd服务启动失败

**问题描述：**
服务无法启动或立即退出

**解决方案：**

```bash
# 查看详细错误日志
sudo journalctl -u bus-planner -n 50 --no-pager

# 检查服务配置
sudo systemctl cat bus-planner

# 确保路径正确
# WorkingDirectory 和 ExecStart 必须是绝对路径
# ExecStart 必须使用虚拟环境中的python

# 测试命令是否能执行
/path/to/weiruan-bus/venv/bin/python /path/to/weiruan-bus/api_server.py

# 重新加载配置
sudo systemctl daemon-reload
sudo systemctl restart bus-planner
```

---

### 10. 数据加载失败

**问题描述：**
```
AttributeError: module has no attribute 'load_nanshan_data'
```

**解决方案：**

```bash
# 确保在项目根目录
cd /path/to/weiruan-bus

# 检查文件是否存在
ls -la src/data/shenzhen_nanshan.py

# 检查Python路径
python -c "import sys; print(sys.path)"

# 重新运行程序（确保在项目根目录）
source venv/bin/activate
python main.py
```

---

## 快速诊断命令

```bash
# 检查系统编码
locale

# 检查Python版本
python3 --version

# 检查虚拟环境
ls -la venv/bin/python

# 检查已安装的包
source venv/bin/activate
pip list

# 检查端口占用
sudo netstat -tulpn | grep :5000

# 检查服务状态
sudo systemctl status bus-planner

# 查看最近日志
sudo journalctl -u bus-planner -f
```

---

## 获取帮助

如果以上方案都无法解决问题：

1. 查看详细日志
2. 检查系统版本：`lsb_release -a`
3. 提供完整错误信息
4. 查看 GitHub Issues

---

## 完全重新安装

如果问题无法解决，可以完全重新安装：

```bash
# 1. 备份数据（如果有自定义数据）
cp -r src/data/custom_data.py ~/backup/

# 2. 删除项目
cd ~
rm -rf weiruan-bus

# 3. 重新克隆
git clone https://github.com/weiruankeji2025/weiruan-bus.git
cd weiruan-bus
git checkout claude/bus-route-planner-9rNXf

# 4. 修复编码
./fix_encoding.sh
source ~/.bashrc

# 5. 重新安装
./install_vps.sh

# 6. 测试
./run.sh
```
