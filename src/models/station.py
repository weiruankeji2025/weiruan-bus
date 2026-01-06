"""
公交站点模型
"""
from typing import Optional, List


class Station:
    """公交站点类"""

    def __init__(self, station_id: str, name: str, latitude: float = 0.0,
                 longitude: float = 0.0, city: str = "", district: str = ""):
        """
        初始化站点

        Args:
            station_id: 站点唯一ID
            name: 站点名称
            latitude: 纬度
            longitude: 经度
            city: 所属城市
            district: 所属区县
        """
        self.station_id = station_id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.city = city
        self.district = district
        self.routes: List[str] = []  # 经过此站点的线路ID列表

    def add_route(self, route_id: str):
        """添加经过此站点的线路"""
        if route_id not in self.routes:
            self.routes.append(route_id)

    def __str__(self):
        return f"{self.name} ({self.district})"

    def __repr__(self):
        return f"Station(id={self.station_id}, name={self.name}, city={self.city}, district={self.district})"

    def __eq__(self, other):
        if isinstance(other, Station):
            return self.station_id == other.station_id
        return False

    def __hash__(self):
        return hash(self.station_id)
