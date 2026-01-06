"""
时刻表模型
"""
from datetime import time, datetime, timedelta
from typing import List, Optional


class Schedule:
    """时刻表类"""

    def __init__(self, route_id: str, first_bus: time, last_bus: time,
                 interval: int = 10):
        """
        初始化时刻表

        Args:
            route_id: 线路ID
            first_bus: 首班车时间
            last_bus: 末班车时间
            interval: 发车间隔（分钟）
        """
        self.route_id = route_id
        self.first_bus = first_bus
        self.last_bus = last_bus
        self.interval = interval

    def get_next_bus(self, current_time: time = None) -> Optional[time]:
        """
        获取下一班车时间

        Args:
            current_time: 当前时间（如果为None，使用系统时间）

        Returns:
            下一班车时间，如果没有则返回None
        """
        if current_time is None:
            current_time = datetime.now().time()

        # 转换为datetime以便计算
        today = datetime.now().date()
        current_dt = datetime.combine(today, current_time)
        first_dt = datetime.combine(today, self.first_bus)
        last_dt = datetime.combine(today, self.last_bus)

        # 如果当前时间早于首班车
        if current_dt < first_dt:
            return self.first_bus

        # 如果当前时间晚于末班车
        if current_dt > last_dt:
            return None

        # 计算下一班车
        elapsed = (current_dt - first_dt).total_seconds() / 60
        next_interval = ((elapsed // self.interval) + 1) * self.interval
        next_dt = first_dt + timedelta(minutes=next_interval)

        if next_dt > last_dt:
            return None

        return next_dt.time()

    def get_waiting_time(self, current_time: time = None) -> Optional[int]:
        """
        获取等待时间（分钟）

        Args:
            current_time: 当前时间

        Returns:
            等待时间（分钟），如果没有下一班车则返回None
        """
        next_bus = self.get_next_bus(current_time)
        if next_bus is None:
            return None

        if current_time is None:
            current_time = datetime.now().time()

        today = datetime.now().date()
        current_dt = datetime.combine(today, current_time)
        next_dt = datetime.combine(today, next_bus)

        waiting = (next_dt - current_dt).total_seconds() / 60
        return int(waiting)

    def __str__(self):
        return f"Schedule(route={self.route_id}, {self.first_bus}-{self.last_bus}, interval={self.interval}min)"
