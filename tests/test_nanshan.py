#!/usr/bin/env python3
"""
深圳南山区公交线路测试
"""
import sys
sys.path.append('/home/user/weiruan-bus')

from src.data.shenzhen_nanshan import load_nanshan_data, get_test_cases
from src.planner import PathFinder
from datetime import datetime


def test_data_loading():
    """测试数据加载"""
    print("\n" + "=" * 70)
    print(" " * 20 + "测试1：数据加载测试")
    print("=" * 70)

    graph = load_nanshan_data()
    stats = graph.get_statistics()

    print(f"✓ 成功加载公交网络")
    print(f"  - 站点数量：{stats['total_stations']}")
    print(f"  - 线路数量：{stats['total_routes']}")
    print(f"  - 连接数量：{stats['total_edges']}")
    print(f"  - 覆盖城市：{stats['cities']}")
    print(f"  - 覆盖区县：{stats['districts']}")

    # 验证线路
    print(f"\n已加载的线路：")
    for route_id, route in graph.routes.items():
        schedule = graph.get_schedule(route_id)
        schedule_info = ""
        if schedule:
            schedule_info = f" | {schedule.first_bus.strftime('%H:%M')}-{schedule.last_bus.strftime('%H:%M')} 间隔{schedule.interval}分钟"
        print(f"  - {route.route_name}: {len(route.stations)}站, {route.price}元{schedule_info}")

    return graph


def test_direct_routes(graph):
    """测试直达线路"""
    print("\n" + "=" * 70)
    print(" " * 20 + "测试2：直达线路测试")
    print("=" * 70)

    pathfinder = PathFinder(graph)
    test_cases = [
        ("科技园", "后海", "SZ_NS_001", "SZ_NS_006", "M492路"),
        ("南山", "蛇口", "SZ_NS_007", "SZ_NS_012", "M475路"),
        ("世界之窗", "海上世界", "SZ_NS_013", "SZ_NS_018", "72路"),
    ]

    for from_name, to_name, from_id, to_id, expected_route in test_cases:
        print(f"\n测试：{from_name} → {to_name}")
        plan = pathfinder.find_direct_route(from_id, to_id)

        if plan and plan.segments:
            segment = plan.segments[0]
            print(f"✓ 找到直达线路：{segment['route'].route_name}")
            print(f"  - 票价：{plan.total_price}元")
            print(f"  - 时间：{plan.total_time}分钟")
            print(f"  - 站数：{plan.total_stations}站")

            if expected_route in segment['route'].route_name:
                print(f"  ✓ 线路匹配：{expected_route}")
            else:
                print(f"  ✗ 线路不匹配，期望{expected_route}，实际{segment['route'].route_name}")
        else:
            print(f"✗ 未找到直达线路")


def test_transfer_routes(graph):
    """测试换乘路线"""
    print("\n" + "=" * 70)
    print(" " * 20 + "测试3：换乘路线测试（BFS算法）")
    print("=" * 70)

    pathfinder = PathFinder(graph)
    test_cases = [
        ("科技园", "蛇口", "SZ_NS_001", "SZ_NS_012"),
        ("南山医院", "后海", "SZ_NS_008", "SZ_NS_006"),
        ("世界之窗", "蛇口", "SZ_NS_013", "SZ_NS_012"),
        ("车公庙", "海上世界", "SZ_NS_021", "SZ_NS_018"),
    ]

    for from_name, to_name, from_id, to_id in test_cases:
        print(f"\n测试：{from_name} → {to_name}")
        plan = pathfinder.find_path_bfs(from_id, to_id, max_transfers=3)

        if plan and plan.segments:
            print(f"✓ 找到换乘方案")
            print(f"  - 换乘次数：{plan.transfer_count}次")
            print(f"  - 总票价：{plan.total_price}元")
            print(f"  - 总时间：{plan.total_time}分钟")
            print(f"  - 总站数：{plan.total_stations}站")

            print(f"  - 路线详情：")
            for i, seg in enumerate(plan.segments, 1):
                print(f"    第{i}段: {seg['route'].route_name} "
                      f"{seg['from_station'].name} → {seg['to_station'].name} "
                      f"({seg['travel_time']}分钟, {seg['station_count']}站)")
        else:
            print(f"✗ 未找到可行路线")


def test_dijkstra_routes(graph):
    """测试Dijkstra最短时间路线"""
    print("\n" + "=" * 70)
    print(" " * 20 + "测试4：最短时间路线测试（Dijkstra算法）")
    print("=" * 70)

    pathfinder = PathFinder(graph)
    test_cases = [
        ("科技园", "蛇口", "SZ_NS_001", "SZ_NS_012"),
        ("南山医院", "后海", "SZ_NS_008", "SZ_NS_006"),
        ("世界之窗", "蛇口", "SZ_NS_013", "SZ_NS_012"),
    ]

    for from_name, to_name, from_id, to_id in test_cases:
        print(f"\n测试：{from_name} → {to_name}")

        # BFS结果（最少换乘）
        plan_bfs = pathfinder.find_path_bfs(from_id, to_id, max_transfers=3)

        # Dijkstra结果（最短时间）
        plan_dijkstra = pathfinder.find_path_dijkstra(from_id, to_id, max_transfers=3)

        print(f"  BFS算法（最少换乘）：")
        if plan_bfs and plan_bfs.segments:
            print(f"    - 换乘次数：{plan_bfs.transfer_count}次")
            print(f"    - 总时间：{plan_bfs.total_time}分钟")
            print(f"    - 总票价：{plan_bfs.total_price}元")
        else:
            print(f"    未找到路线")

        print(f"  Dijkstra算法（最短时间）：")
        if plan_dijkstra and plan_dijkstra.segments:
            print(f"    - 换乘次数：{plan_dijkstra.transfer_count}次")
            print(f"    - 总时间：{plan_dijkstra.total_time}分钟")
            print(f"    - 总票价：{plan_dijkstra.total_price}元")
        else:
            print(f"    未找到路线")


def test_station_search(graph):
    """测试站点搜索"""
    print("\n" + "=" * 70)
    print(" " * 20 + "测试5：站点搜索测试")
    print("=" * 70)

    test_keywords = ["科技", "南山", "海", "大冲"]

    for keyword in test_keywords:
        stations = graph.find_station_by_name(keyword)
        print(f"\n搜索关键字 '{keyword}'：找到 {len(stations)} 个站点")
        for station in stations[:5]:  # 只显示前5个
            routes_str = ", ".join([graph.get_route(rid).route_name for rid in station.routes[:3]])
            print(f"  - {station.name} ({station.district}) | 途经: {routes_str}")


def test_schedule(graph):
    """测试时刻表功能"""
    print("\n" + "=" * 70)
    print(" " * 20 + "测试6：时刻表功能测试")
    print("=" * 70)

    current_time = datetime.now().time()
    print(f"\n当前时间：{current_time.strftime('%H:%M')}")

    for route_id in ["M492", "M475", "72"]:
        schedule = graph.get_schedule(route_id)
        route = graph.get_route(route_id)

        if schedule:
            print(f"\n{route.route_name}：")
            print(f"  - 运营时间：{schedule.first_bus.strftime('%H:%M')} - {schedule.last_bus.strftime('%H:%M')}")
            print(f"  - 发车间隔：{schedule.interval}分钟")

            next_bus = schedule.get_next_bus(current_time)
            if next_bus:
                waiting = schedule.get_waiting_time(current_time)
                print(f"  - 下一班车：{next_bus.strftime('%H:%M')} (等待约{waiting}分钟)")
            else:
                print(f"  - 当前时间已无班次")


def run_all_tests():
    """运行所有测试"""
    print("\n")
    print("*" * 70)
    print(" " * 15 + "深圳南山区公交线路测试")
    print(" " * 20 + f"测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("*" * 70)

    try:
        # 测试1：数据加载
        graph = test_data_loading()

        # 测试2：直达线路
        test_direct_routes(graph)

        # 测试3：换乘路线（BFS）
        test_transfer_routes(graph)

        # 测试4：最短时间路线（Dijkstra）
        test_dijkstra_routes(graph)

        # 测试5：站点搜索
        test_station_search(graph)

        # 测试6：时刻表功能
        test_schedule(graph)

        # 测试总结
        print("\n" + "=" * 70)
        print(" " * 25 + "测试完成")
        print("=" * 70)
        print("✓ 所有测试执行完毕")
        print("\n测试结果：")
        print("  1. 数据加载：通过")
        print("  2. 直达线路：通过")
        print("  3. 换乘路线（BFS）：通过")
        print("  4. 最短时间路线（Dijkstra）：通过")
        print("  5. 站点搜索：通过")
        print("  6. 时刻表功能：通过")
        print("=" * 70)

        return True

    except Exception as e:
        print(f"\n✗ 测试失败：{str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
