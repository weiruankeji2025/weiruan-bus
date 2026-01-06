"""
公交线路模型
"""
from typing import List, Optional
from datetime import time


class RouteStation:
    """线路站点关联类（线路上的某一站）"""

    def __init__(self, station_id: str, sequence: int, arrival_time_offset: int = 0):
        """
        初始化线路站点

        Args:
            station_id: 站点ID
            sequence: 站点在线路中的顺序（从0开始）
            arrival_time_offset: 从起点到此站的时间偏移（分钟）
        """
        self.station_id = station_id
        self.sequence = sequence
        self.arrival_time_offset = arrival_time_offset


class BusRoute:
    """公交线路类"""

    def __init__(self, route_id: str, route_name: str, city: str = "",
                 district: str = "", price: float = 2.0, is_loop: bool = False):
        """
        初始化公交线路

        Args:
            route_id: 线路唯一ID
            route_name: 线路名称（如"M492路"）
            city: 所属城市
            district: 所属区县
            price: 票价（元）
            is_loop: 是否为环线
        """
        self.route_id = route_id
        self.route_name = route_name
        self.city = city
        self.district = district
        self.price = price
        self.is_loop = is_loop
        self.stations: List[RouteStation] = []  # 站点列表（按顺序）
        self.first_bus_time: Optional[time] = None  # 首班车时间
        self.last_bus_time: Optional[time] = None   # 末班车时间
        self.interval: int = 10  # 发车间隔（分钟）
        self.avg_speed: float = 20.0  # 平均速度（km/h）

    def add_station(self, station_id: str, sequence: int = None,
                   arrival_time_offset: int = 0):
        """
        添加站点到线路

        Args:
            station_id: 站点ID
            sequence: 站点顺序（如果为None，则添加到末尾）
            arrival_time_offset: 到达时间偏移
        """
        if sequence is None:
            sequence = len(self.stations)

        route_station = RouteStation(station_id, sequence, arrival_time_offset)
        self.stations.append(route_station)
        self.stations.sort(key=lambda x: x.sequence)

    def get_station_ids(self) -> List[str]:
        """获取线路上所有站点ID列表"""
        return [rs.station_id for rs in self.stations]

    def get_travel_time(self, from_seq: int, to_seq: int) -> int:
        """
        计算两站之间的行驶时间

        Args:
            from_seq: 起始站点序号
            to_seq: 终点站点序号

        Returns:
            行驶时间（分钟）
        """
        if from_seq >= len(self.stations) or to_seq >= len(self.stations):
            return 0

        from_station = self.stations[from_seq]
        to_station = self.stations[to_seq]

        return abs(to_station.arrival_time_offset - from_station.arrival_time_offset)

    def get_station_sequence(self, station_id: str) -> Optional[int]:
        """获取站点在线路中的序号"""
        for rs in self.stations:
            if rs.station_id == station_id:
                return rs.sequence
        return None

    def __str__(self):
        return f"{self.route_name} ({len(self.stations)}站)"

    def __repr__(self):
        return f"BusRoute(id={self.route_id}, name={self.route_name}, stations={len(self.stations)})"
