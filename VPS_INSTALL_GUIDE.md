# VPS安装和使用指南

本指南将帮助您在VPS上安装和运行公交车线路规划系统。

## 系统要求

- 操作系统：Ubuntu 20.04+ / Debian 10+ / CentOS 7+
- Python 3.8 或更高版本
- 内存：至少 512MB
- 磁盘空间：至少 100MB

## 安装步骤

### 1. 连接到VPS

```bash
# 使用SSH连接到您的VPS
ssh username@your-vps-ip
```

### 2. 更新系统并安装Python

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y python3 python3-pip git
```

**CentOS/RHEL:**
```bash
sudo yum update -y
sudo yum install -y python3 python3-pip git
```

### 3. 验证Python版本

```bash
python3 --version
# 应该显示 Python 3.8 或更高版本
```

### 4. 克隆项目代码

```bash
# 克隆仓库
git clone https://github.com/weiruankeji2025/weiruan-bus.git

# 进入项目目录
cd weiruan-bus

# 切换到开发分支
git checkout claude/bus-route-planner-9rNXf
```

### 5. 安装Python依赖

```bash
# 安装依赖包
pip3 install -r requirements.txt

# 或者使用国内镜像加速（推荐）
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 使用方法

### 方法1：交互式模式（推荐）

```bash
# 运行主程序
python3 main.py
```

程序启动后会显示菜单：
```
1. 规划路线（最少换乘）
2. 规划路线（最短时间）
3. 查看线路信息
4. 查看网络统计
0. 退出
```

按照提示输入选项和站点名称即可。

### 方法2：运行测试

```bash
# 运行深圳南山区测试
python3 tests/test_nanshan.py
```

### 方法3：作为Python模块使用

创建自己的脚本：

```python
# my_script.py
import sys
sys.path.append('/path/to/weiruan-bus')

from src.data.shenzhen_nanshan import load_nanshan_data
from src.planner import PathFinder

# 加载数据
graph = load_nanshan_data()

# 创建路径规划器
pathfinder = PathFinder(graph)

# 查找路线
plan = pathfinder.find_path_bfs("SZ_NS_013", "SZ_NS_012")  # 世界之窗 -> 蛇口
print(plan)
```

## 后台运行（可选）

如果您想让程序在后台持续运行：

### 使用screen

```bash
# 安装screen
sudo apt install screen  # Ubuntu/Debian
sudo yum install screen  # CentOS

# 创建新会话
screen -S bus-planner

# 运行程序
python3 main.py

# 按 Ctrl+A，然后按 D 退出会话（程序继续运行）

# 重新连接到会话
screen -r bus-planner
```

### 使用nohup

```bash
# 后台运行（适合非交互式脚本）
nohup python3 tests/test_nanshan.py > output.log 2>&1 &

# 查看输出
tail -f output.log
```

### 使用systemd服务（生产环境推荐）

创建服务文件：

```bash
sudo nano /etc/systemd/system/bus-planner.service
```

添加以下内容：

```ini
[Unit]
Description=Bus Route Planner Service
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/weiruan-bus
ExecStart=/usr/bin/python3 /path/to/weiruan-bus/main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
# 重新加载systemd配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start bus-planner

# 设置开机自启动
sudo systemctl enable bus-planner

# 查看服务状态
sudo systemctl status bus-planner

# 查看日志
sudo journalctl -u bus-planner -f
```

## 添加更多城市数据

要添加其他城市的公交数据：

1. 在 `src/data/` 目录下创建新文件（例如 `beijing_chaoyang.py`）
2. 参考 `shenzhen_nanshan.py` 的格式添加站点和线路数据
3. 在主程序中加载新数据

示例：

```python
# src/data/beijing_chaoyang.py
from src.models import Station, BusRoute, Schedule
from src.planner import TransitGraph
from datetime import time

def load_beijing_data():
    graph = TransitGraph()

    # 添加站点
    station1 = Station("BJ_CY_001", "国贸", 39.9075, 116.4574, "北京市", "朝阳区")
    graph.add_station(station1)

    # 添加线路
    route = BusRoute("1", "1路", "北京市", "朝阳区", 2.0)
    route.add_station("BJ_CY_001", 0, 0)
    # ... 添加更多站点

    schedule = Schedule("1", time(6, 0), time(23, 0), 10)
    graph.add_route(route, schedule)

    return graph
```

## 常见问题

### Q: 提示找不到模块？
A: 确保在项目根目录运行程序，或者使用 `sys.path.append()` 添加路径。

### Q: 如何查看所有可用站点？
A: 运行程序后选择"4. 查看网络统计"，或者查看 `src/data/shenzhen_nanshan.py` 文件。

### Q: 如何修改票价？
A: 在数据文件中修改 `BusRoute` 的 `price` 参数。

### Q: 程序占用内存太多？
A: 当前深圳南山区数据很小，如果添加了大量城市数据导致内存占用高，可以考虑：
  - 使用数据库存储（如SQLite）
  - 按需加载城市数据
  - 优化数据结构

### Q: 如何从外部访问？
A: 当前是命令行程序，如需Web访问，可以：
  - 使用Flask/Django开发Web界面
  - 部署API服务供移动端调用

## Web API部署（进阶）

如果需要提供Web API服务，可以安装Flask：

```bash
pip3 install flask
```

创建简单的API服务（`api.py`）：

```python
from flask import Flask, request, jsonify
import sys
sys.path.append('/path/to/weiruan-bus')

from src.data.shenzhen_nanshan import load_nanshan_data
from src.planner import PathFinder

app = Flask(__name__)
graph = load_nanshan_data()
pathfinder = PathFinder(graph)

@app.route('/api/plan', methods=['GET'])
def plan_route():
    from_id = request.args.get('from')
    to_id = request.args.get('to')

    plan = pathfinder.find_path_bfs(from_id, to_id)

    if plan and plan.segments:
        return jsonify({
            'success': True,
            'transfer_count': plan.transfer_count,
            'total_time': plan.total_time,
            'total_price': plan.total_price,
            'segments': [
                {
                    'route': seg['route'].route_name,
                    'from': seg['from_station'].name,
                    'to': seg['to_station'].name,
                    'time': seg['travel_time']
                }
                for seg in plan.segments
            ]
        })
    else:
        return jsonify({'success': False, 'error': 'No route found'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

运行API服务：

```bash
python3 api.py
```

访问API：
```bash
curl "http://your-vps-ip:5000/api/plan?from=SZ_NS_013&to=SZ_NS_012"
```

## 安全建议

1. **防火墙配置**：只开放必要的端口
```bash
sudo ufw allow 22    # SSH
sudo ufw allow 5000  # API服务（如果需要）
sudo ufw enable
```

2. **使用反向代理**：使用Nginx作为反向代理
```bash
sudo apt install nginx
```

3. **定期更新**：定期更新系统和依赖包
```bash
sudo apt update && sudo apt upgrade
pip3 list --outdated
```

## 性能优化

1. **使用虚拟环境**（推荐）：
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **数据缓存**：对于频繁查询的路线，可以添加缓存机制

3. **并发处理**：如果部署Web服务，使用Gunicorn：
```bash
pip3 install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api:app
```

## 获取帮助

- 查看项目README：`cat README.md`
- 查看测试结果：`cat TEST_RESULTS.md`
- GitHub Issues: https://github.com/weiruankeji2025/weiruan-bus/issues

## 卸载

如需卸载：

```bash
# 停止服务（如果配置了）
sudo systemctl stop bus-planner
sudo systemctl disable bus-planner
sudo rm /etc/systemd/system/bus-planner.service

# 删除项目文件
cd ~
rm -rf weiruan-bus

# 卸载依赖（可选）
pip3 uninstall -r weiruan-bus/requirements.txt
```
