"""
命令行用户界面
"""
import sys
sys.path.append('/home/user/weiruan-bus')

from src.planner import TransitGraph, PathFinder
from datetime import datetime


class BusRouteCLI:
    """公交线路规划命令行界面"""

    def __init__(self, graph: TransitGraph):
        self.graph = graph
        self.pathfinder = PathFinder(graph)

    def show_welcome(self):
        """显示欢迎信息"""
        print("\n" + "=" * 60)
        print(" " * 15 + "公交线路规划系统")
        print("=" * 60)
        stats = self.graph.get_statistics()
        print(f"当前数据：{stats['total_stations']}个站点，{stats['total_routes']}条线路")
        print(f"覆盖城市：{stats['cities']}个，区县：{stats['districts']}个")
        print("=" * 60 + "\n")

    def search_station(self, name: str):
        """搜索站点"""
        stations = self.graph.find_station_by_name(name)

        if not stations:
            print(f"未找到站点：{name}")
            return None

        if len(stations) == 1:
            return stations[0]

        # 多个匹配结果
        print(f"\n找到 {len(stations)} 个匹配的站点：")
        for i, station in enumerate(stations, 1):
            routes = ", ".join([self.graph.get_route(rid).route_name for rid in station.routes[:3]])
            if len(station.routes) > 3:
                routes += f" 等{len(station.routes)}条线路"
            print(f"{i}. {station.name} ({station.district}) - 途经线路: {routes}")

        while True:
            try:
                choice = input("\n请选择站点编号 (输入0取消): ")
                choice_num = int(choice)

                if choice_num == 0:
                    return None
                if 1 <= choice_num <= len(stations):
                    return stations[choice_num - 1]
                else:
                    print("无效的选择，请重新输入")
            except ValueError:
                print("请输入数字")

    def plan_route(self, from_name: str, to_name: str, algorithm: str = "bfs"):
        """
        规划路线

        Args:
            from_name: 起点站名称
            to_name: 终点站名称
            algorithm: 算法类型 ("bfs" 或 "dijkstra")
        """
        print(f"\n正在查找从 '{from_name}' 到 '{to_name}' 的路线...\n")

        # 搜索起点站
        from_station = self.search_station(from_name)
        if not from_station:
            return

        # 搜索终点站
        to_station = self.search_station(to_name)
        if not to_station:
            return

        # 检查起点和终点是否相同
        if from_station.station_id == to_station.station_id:
            print("起点和终点相同，无需乘车")
            return

        print(f"\n起点：{from_station.name} ({from_station.district})")
        print(f"终点：{to_station.name} ({to_station.district})")
        print("\n正在计算最优路线...\n")

        # 规划路径
        if algorithm == "dijkstra":
            plan = self.pathfinder.find_path_dijkstra(from_station.station_id, to_station.station_id)
        else:
            plan = self.pathfinder.find_path_bfs(from_station.station_id, to_station.station_id)

        # 显示结果
        if plan and plan.segments:
            print(plan)
        else:
            print("未找到可行路线，请检查起点和终点是否正确")

    def show_route_info(self, route_name: str):
        """显示线路信息"""
        # 查找线路
        route = None
        for r in self.graph.routes.values():
            if route_name.upper() in r.route_name.upper():
                route = r
                break

        if not route:
            print(f"未找到线路：{route_name}")
            return

        print("\n" + "=" * 60)
        print(f"线路信息：{route.route_name}")
        print("=" * 60)
        print(f"所属区域：{route.city} {route.district}")
        print(f"票价：{route.price}元")
        print(f"站点数：{len(route.stations)}站")

        schedule = self.graph.get_schedule(route.route_id)
        if schedule:
            print(f"首班车：{schedule.first_bus.strftime('%H:%M')}")
            print(f"末班车：{schedule.last_bus.strftime('%H:%M')}")
            print(f"发车间隔：{schedule.interval}分钟")

            # 计算下一班车
            next_bus = schedule.get_next_bus()
            if next_bus:
                waiting = schedule.get_waiting_time()
                print(f"下一班车：{next_bus.strftime('%H:%M')} (等待{waiting}分钟)")
            else:
                print("当前已无班次")

        print("\n站点列表：")
        for i, rs in enumerate(route.stations, 1):
            station = self.graph.get_station(rs.station_id)
            if station:
                time_info = f" ({rs.arrival_time_offset}分钟)" if rs.arrival_time_offset > 0 else ""
                print(f"{i:2}. {station.name}{time_info}")

        print("=" * 60)

    def interactive_mode(self):
        """交互模式"""
        self.show_welcome()

        while True:
            print("\n请选择功能：")
            print("1. 规划路线（最少换乘）")
            print("2. 规划路线（最短时间）")
            print("3. 查看线路信息")
            print("4. 查看网络统计")
            print("0. 退出")

            choice = input("\n请输入选项: ").strip()

            if choice == "0":
                print("\n感谢使用公交线路规划系统！")
                break
            elif choice == "1":
                from_name = input("请输入起点站名称: ").strip()
                to_name = input("请输入终点站名称: ").strip()
                if from_name and to_name:
                    self.plan_route(from_name, to_name, "bfs")
            elif choice == "2":
                from_name = input("请输入起点站名称: ").strip()
                to_name = input("请输入终点站名称: ").strip()
                if from_name and to_name:
                    self.plan_route(from_name, to_name, "dijkstra")
            elif choice == "3":
                route_name = input("请输入线路名称: ").strip()
                if route_name:
                    self.show_route_info(route_name)
            elif choice == "4":
                stats = self.graph.get_statistics()
                print("\n" + "=" * 60)
                print("网络统计信息")
                print("=" * 60)
                print(f"站点总数：{stats['total_stations']}")
                print(f"线路总数：{stats['total_routes']}")
                print(f"连接总数：{stats['total_edges']}")
                print(f"覆盖城市：{stats['cities']}")
                print(f"覆盖区县：{stats['districts']}")
                print("=" * 60)
            else:
                print("无效的选项，请重新输入")
