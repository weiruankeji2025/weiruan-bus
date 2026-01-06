#!/usr/bin/env python3
"""
公交车线路规划系统 - Web API服务
可以通过HTTP接口调用路径规划功能
"""
import sys
sys.path.append('/home/user/weiruan-bus')

from flask import Flask, request, jsonify
from src.data.shenzhen_nanshan import load_nanshan_data
from src.planner import PathFinder

app = Flask(__name__)

# 加载数据
print("正在加载公交数据...")
graph = load_nanshan_data()
pathfinder = PathFinder(graph)
print(f"数据加载完成：{graph}")


@app.route('/')
def index():
    """首页"""
    return """
    <h1>公交车线路规划系统 API</h1>
    <h2>可用接口：</h2>
    <ul>
        <li><a href="/api/stations">/api/stations</a> - 查询所有站点</li>
        <li><a href="/api/routes">/api/routes</a> - 查询所有线路</li>
        <li>/api/plan?from=站点ID&to=站点ID&algorithm=bfs - 规划路线</li>
        <li>/api/search?name=站点名称 - 搜索站点</li>
    </ul>
    <h2>示例：</h2>
    <ul>
        <li><a href="/api/plan?from=SZ_NS_013&to=SZ_NS_012&algorithm=bfs">世界之窗到蛇口（BFS）</a></li>
        <li><a href="/api/plan?from=SZ_NS_008&to=SZ_NS_006&algorithm=dijkstra">南山医院到后海（Dijkstra）</a></li>
        <li><a href="/api/search?name=科技">搜索"科技"</a></li>
    </ul>
    """


@app.route('/api/stations')
def get_stations():
    """获取所有站点"""
    stations = []
    for station in graph.stations.values():
        stations.append({
            'id': station.station_id,
            'name': station.name,
            'district': station.district,
            'routes': [graph.get_route(rid).route_name for rid in station.routes]
        })

    return jsonify({
        'success': True,
        'count': len(stations),
        'stations': stations
    })


@app.route('/api/routes')
def get_routes():
    """获取所有线路"""
    routes = []
    for route in graph.routes.values():
        schedule = graph.get_schedule(route.route_id)
        routes.append({
            'id': route.route_id,
            'name': route.route_name,
            'price': route.price,
            'station_count': len(route.stations),
            'first_bus': schedule.first_bus.strftime('%H:%M') if schedule else None,
            'last_bus': schedule.last_bus.strftime('%H:%M') if schedule else None,
            'interval': schedule.interval if schedule else None
        })

    return jsonify({
        'success': True,
        'count': len(routes),
        'routes': routes
    })


@app.route('/api/search')
def search_station():
    """搜索站点"""
    name = request.args.get('name', '')

    if not name:
        return jsonify({
            'success': False,
            'error': '请提供站点名称参数 name'
        }), 400

    stations = graph.find_station_by_name(name)

    return jsonify({
        'success': True,
        'count': len(stations),
        'stations': [
            {
                'id': s.station_id,
                'name': s.name,
                'district': s.district,
                'routes': [graph.get_route(rid).route_name for rid in s.routes]
            }
            for s in stations
        ]
    })


@app.route('/api/plan')
def plan_route():
    """规划路线"""
    from_id = request.args.get('from')
    to_id = request.args.get('to')
    algorithm = request.args.get('algorithm', 'bfs').lower()

    if not from_id or not to_id:
        return jsonify({
            'success': False,
            'error': '请提供起点和终点参数 from 和 to'
        }), 400

    # 检查站点是否存在
    from_station = graph.get_station(from_id)
    to_station = graph.get_station(to_id)

    if not from_station:
        return jsonify({
            'success': False,
            'error': f'起点站不存在: {from_id}'
        }), 404

    if not to_station:
        return jsonify({
            'success': False,
            'error': f'终点站不存在: {to_id}'
        }), 404

    # 规划路径
    if algorithm == 'dijkstra':
        plan = pathfinder.find_path_dijkstra(from_id, to_id)
    else:
        plan = pathfinder.find_path_bfs(from_id, to_id)

    if plan and plan.segments:
        return jsonify({
            'success': True,
            'from': {
                'id': from_id,
                'name': from_station.name
            },
            'to': {
                'id': to_id,
                'name': to_station.name
            },
            'algorithm': algorithm,
            'transfer_count': plan.transfer_count,
            'total_time': plan.total_time,
            'total_price': plan.total_price,
            'total_stations': plan.total_stations,
            'segments': [
                {
                    'route_id': seg['route'].route_id,
                    'route_name': seg['route'].route_name,
                    'from_station': seg['from_station'].name,
                    'to_station': seg['to_station'].name,
                    'travel_time': seg['travel_time'],
                    'waiting_time': seg['waiting_time'],
                    'station_count': seg['station_count'],
                    'price': seg['route'].price
                }
                for seg in plan.segments
            ]
        })
    else:
        return jsonify({
            'success': False,
            'error': '未找到可行路线'
        }), 404


@app.route('/api/route/<route_id>')
def get_route_detail(route_id):
    """获取线路详情"""
    route = graph.get_route(route_id)

    if not route:
        return jsonify({
            'success': False,
            'error': f'线路不存在: {route_id}'
        }), 404

    schedule = graph.get_schedule(route_id)

    stations = []
    for rs in route.stations:
        station = graph.get_station(rs.station_id)
        if station:
            stations.append({
                'sequence': rs.sequence,
                'id': station.station_id,
                'name': station.name,
                'arrival_time_offset': rs.arrival_time_offset
            })

    return jsonify({
        'success': True,
        'route': {
            'id': route.route_id,
            'name': route.route_name,
            'city': route.city,
            'district': route.district,
            'price': route.price,
            'is_loop': route.is_loop,
            'station_count': len(stations),
            'first_bus': schedule.first_bus.strftime('%H:%M') if schedule else None,
            'last_bus': schedule.last_bus.strftime('%H:%M') if schedule else None,
            'interval': schedule.interval if schedule else None,
            'stations': stations
        }
    })


if __name__ == '__main__':
    import os

    # 从环境变量读取配置，或使用默认值
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', 5000))
    debug = os.getenv('API_DEBUG', 'False').lower() == 'true'

    print(f"\n启动API服务...")
    print(f"地址: http://{host}:{port}")
    print(f"文档: http://{host}:{port}/")
    print(f"\n按 Ctrl+C 停止服务\n")

    app.run(host=host, port=port, debug=debug)
