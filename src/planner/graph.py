"""
公交网络图构建模块
"""
from typing import Dict, List, Set
from collections import defaultdict
import sys
sys.path.append('/home/user/weiruan-bus')

from src.models import Station, BusRoute, Schedule


class TransitGraph:
    """公交网络图类"""

    def __init__(self):
        self.stations: Dict[str, Station] = {}  # station_id -> Station
        self.routes: Dict[str, BusRoute] = {}   # route_id -> BusRoute
        self.schedules: Dict[str, Schedule] = {}  # route_id -> Schedule

        # 图结构：站点之间的连接
        # station_id -> [(next_station_id, route_id, travel_time)]
        self.graph: Dict[str, List[tuple]] = defaultdict(list)

        # 站点到线路的映射
        # station_id -> [route_id]
        self.station_routes: Dict[str, Set[str]] = defaultdict(set)

    def add_station(self, station: Station):
        """添加站点"""
        self.stations[station.station_id] = station

    def add_route(self, route: BusRoute, schedule: Schedule = None):
        """
        添加线路

        Args:
            route: 公交线路对象
            schedule: 时刻表对象（可选）
        """
        self.routes[route.route_id] = route

        if schedule:
            self.schedules[route.route_id] = schedule

        # 构建图的边
        stations = route.stations
        for i in range(len(stations) - 1):
            from_station = stations[i]
            to_station = stations[i + 1]

            # 计算行驶时间
            travel_time = to_station.arrival_time_offset - from_station.arrival_time_offset

            # 添加边
            self.graph[from_station.station_id].append(
                (to_station.station_id, route.route_id, travel_time)
            )

            # 记录站点到线路的映射
            self.station_routes[from_station.station_id].add(route.route_id)
            self.station_routes[to_station.station_id].add(route.route_id)

            # 更新站点的线路列表
            if from_station.station_id in self.stations:
                self.stations[from_station.station_id].add_route(route.route_id)
            if to_station.station_id in self.stations:
                self.stations[to_station.station_id].add_route(route.route_id)

        # 如果是环线，连接最后一站到第一站
        if route.is_loop and len(stations) > 1:
            last_station = stations[-1]
            first_station = stations[0]
            travel_time = route.interval  # 使用发车间隔作为估计

            self.graph[last_station.station_id].append(
                (first_station.station_id, route.route_id, travel_time)
            )

    def get_station(self, station_id: str) -> Station:
        """获取站点对象"""
        return self.stations.get(station_id)

    def get_route(self, route_id: str) -> BusRoute:
        """获取线路对象"""
        return self.routes.get(route_id)

    def get_schedule(self, route_id: str) -> Schedule:
        """获取时刻表对象"""
        return self.schedules.get(route_id)

    def get_common_routes(self, station1_id: str, station2_id: str) -> Set[str]:
        """
        获取两个站点的共同线路

        Args:
            station1_id: 站点1 ID
            station2_id: 站点2 ID

        Returns:
            共同线路ID集合
        """
        routes1 = self.station_routes.get(station1_id, set())
        routes2 = self.station_routes.get(station2_id, set())
        return routes1 & routes2

    def get_neighbors(self, station_id: str) -> List[tuple]:
        """
        获取站点的所有邻居站点

        Args:
            station_id: 站点ID

        Returns:
            [(next_station_id, route_id, travel_time), ...]
        """
        return self.graph.get(station_id, [])

    def find_station_by_name(self, name: str) -> List[Station]:
        """
        根据名称查找站点（支持模糊匹配）

        Args:
            name: 站点名称

        Returns:
            匹配的站点列表
        """
        results = []
        for station in self.stations.values():
            if name.lower() in station.name.lower():
                results.append(station)
        return results

    def get_statistics(self) -> Dict:
        """获取网络统计信息"""
        return {
            'total_stations': len(self.stations),
            'total_routes': len(self.routes),
            'total_edges': sum(len(neighbors) for neighbors in self.graph.values()),
            'cities': len(set(s.city for s in self.stations.values())),
            'districts': len(set(s.district for s in self.stations.values()))
        }

    def __str__(self):
        stats = self.get_statistics()
        return f"TransitGraph(stations={stats['total_stations']}, routes={stats['total_routes']}, edges={stats['total_edges']})"
