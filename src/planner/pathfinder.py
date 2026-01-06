"""
路径规划算法模块
"""
from typing import List, Optional, Dict, Tuple
from collections import deque
from datetime import time
import heapq
import sys
sys.path.append('/home/user/weiruan-bus')

from src.planner.graph import TransitGraph
from src.models import Station, BusRoute


class TransferPlan:
    """换乘方案类"""

    def __init__(self):
        self.segments: List[Dict] = []  # 行程段列表
        self.total_time: int = 0        # 总时间（分钟）
        self.total_price: float = 0.0   # 总票价（元）
        self.transfer_count: int = 0    # 换乘次数
        self.total_stations: int = 0    # 总站数

    def add_segment(self, route: BusRoute, from_station: Station,
                   to_station: Station, travel_time: int, waiting_time: int = 0):
        """
        添加行程段

        Args:
            route: 公交线路
            from_station: 起始站点
            to_station: 终点站点
            travel_time: 行驶时间（分钟）
            waiting_time: 等待时间（分钟）
        """
        # 计算站数
        from_seq = route.get_station_sequence(from_station.station_id)
        to_seq = route.get_station_sequence(to_station.station_id)
        station_count = abs(to_seq - from_seq) if from_seq is not None and to_seq is not None else 0

        segment = {
            'route': route,
            'from_station': from_station,
            'to_station': to_station,
            'travel_time': travel_time,
            'waiting_time': waiting_time,
            'station_count': station_count
        }

        self.segments.append(segment)
        self.total_time += travel_time + waiting_time
        self.total_price += route.price
        self.total_stations += station_count

        # 如果不是第一段，则增加换乘次数
        if len(self.segments) > 1:
            self.transfer_count += 1

    def get_summary(self) -> str:
        """获取方案摘要"""
        if not self.segments:
            return "无可用方案"

        lines = []
        lines.append("=" * 60)
        lines.append("换乘方案：")
        lines.append(f"总时间：{self.total_time}分钟 | 总票价：{self.total_price:.1f}元 | 换乘次数：{self.transfer_count}次 | 总站数：{self.total_stations}站")
        lines.append("=" * 60)

        for i, seg in enumerate(self.segments, 1):
            route = seg['route']
            from_st = seg['from_station']
            to_st = seg['to_station']
            travel_time = seg['travel_time']
            waiting_time = seg['waiting_time']
            station_count = seg['station_count']

            lines.append(f"\n第{i}段：")
            lines.append(f"  线路：{route.route_name}")
            lines.append(f"  上车站：{from_st.name}")
            lines.append(f"  下车站：{to_st.name}")
            lines.append(f"  行驶时间：{travel_time}分钟 ({station_count}站)")
            if waiting_time > 0:
                lines.append(f"  等待时间：{waiting_time}分钟")
            lines.append(f"  票价：{route.price:.1f}元")

        lines.append("=" * 60)
        return "\n".join(lines)

    def __str__(self):
        return self.get_summary()


class PathFinder:
    """路径规划器"""

    def __init__(self, graph: TransitGraph):
        self.graph = graph

    def find_direct_route(self, from_station_id: str, to_station_id: str) -> Optional[TransferPlan]:
        """
        查找直达线路（无需换乘）

        Args:
            from_station_id: 起点站ID
            to_station_id: 终点站ID

        Returns:
            换乘方案，如果没有直达则返回None
        """
        common_routes = self.graph.get_common_routes(from_station_id, to_station_id)

        if not common_routes:
            return None

        # 找到最快的直达线路
        best_plan = None
        min_time = float('inf')

        for route_id in common_routes:
            route = self.graph.get_route(route_id)
            from_seq = route.get_station_sequence(from_station_id)
            to_seq = route.get_station_sequence(to_station_id)

            if from_seq is not None and to_seq is not None and from_seq < to_seq:
                travel_time = route.get_travel_time(from_seq, to_seq)

                # 获取等待时间
                waiting_time = 0
                schedule = self.graph.get_schedule(route_id)
                if schedule:
                    wt = schedule.get_waiting_time()
                    waiting_time = wt if wt is not None else 0

                total_time = travel_time + waiting_time

                if total_time < min_time:
                    min_time = total_time
                    plan = TransferPlan()
                    plan.add_segment(
                        route,
                        self.graph.get_station(from_station_id),
                        self.graph.get_station(to_station_id),
                        travel_time,
                        waiting_time
                    )
                    best_plan = plan

        return best_plan

    def find_path_bfs(self, from_station_id: str, to_station_id: str,
                     max_transfers: int = 3) -> Optional[TransferPlan]:
        """
        使用BFS查找最少换乘方案

        Args:
            from_station_id: 起点站ID
            to_station_id: 终点站ID
            max_transfers: 最大换乘次数

        Returns:
            换乘方案，如果无法到达则返回None
        """
        # 首先尝试直达
        direct_plan = self.find_direct_route(from_station_id, to_station_id)
        if direct_plan:
            return direct_plan

        # BFS搜索
        # 状态：(current_station_id, current_route_id, path)
        # path: [(station_id, route_id, travel_time)]
        queue = deque()

        # 初始化：从起点站所有可乘坐的线路开始
        for next_station_id, route_id, travel_time in self.graph.get_neighbors(from_station_id):
            queue.append((next_station_id, route_id, [(from_station_id, route_id, 0), (next_station_id, route_id, travel_time)]))

        visited = set()  # (station_id, route_id)

        while queue:
            current_station, current_route, path = queue.popleft()

            # 到达目标
            if current_station == to_station_id:
                return self._build_plan_from_path(path)

            # 检查换乘次数
            transfers = self._count_transfers(path)
            if transfers > max_transfers:
                continue

            # 状态标记
            state = (current_station, current_route)
            if state in visited:
                continue
            visited.add(state)

            # 尝试继续乘坐当前线路
            route = self.graph.get_route(current_route)
            current_seq = route.get_station_sequence(current_station)

            if current_seq is not None and current_seq < len(route.stations) - 1:
                next_route_station = route.stations[current_seq + 1]
                next_station_id = next_route_station.station_id
                travel_time = next_route_station.arrival_time_offset - route.stations[current_seq].arrival_time_offset

                new_path = path + [(next_station_id, current_route, travel_time)]
                queue.append((next_station_id, current_route, new_path))

            # 尝试换乘到其他线路（在当前站点换乘）
            if current_station in self.graph.station_routes:
                for other_route_id in self.graph.station_routes[current_station]:
                    if other_route_id != current_route:  # 换乘到不同线路
                        other_route = self.graph.get_route(other_route_id)
                        other_seq = other_route.get_station_sequence(current_station)

                        # 确保可以继续前进
                        if other_seq is not None and other_seq < len(other_route.stations) - 1:
                            next_route_station = other_route.stations[other_seq + 1]
                            next_station_id = next_route_station.station_id
                            travel_time = next_route_station.arrival_time_offset - other_route.stations[other_seq].arrival_time_offset

                            # 在路径中添加换乘点和下一站
                            new_path = path + [(current_station, other_route_id, 0), (next_station_id, other_route_id, travel_time)]
                            queue.append((next_station_id, other_route_id, new_path))

        return None

    def find_path_dijkstra(self, from_station_id: str, to_station_id: str,
                          max_transfers: int = 3) -> Optional[TransferPlan]:
        """
        使用Dijkstra算法查找最短时间方案

        Args:
            from_station_id: 起点站ID
            to_station_id: 终点站ID
            max_transfers: 最大换乘次数

        Returns:
            换乘方案，如果无法到达则返回None
        """
        # 首先尝试直达
        direct_plan = self.find_direct_route(from_station_id, to_station_id)
        if direct_plan:
            return direct_plan

        # 优先队列：(total_time, current_station, current_route, path, transfers)
        heap = []

        # 初始化
        for next_station_id, route_id, travel_time in self.graph.get_neighbors(from_station_id):
            schedule = self.graph.get_schedule(route_id)
            waiting_time = 0
            if schedule:
                wt = schedule.get_waiting_time()
                waiting_time = wt if wt is not None else 0

            total_time = travel_time + waiting_time
            path = [(from_station_id, route_id, 0, 0), (next_station_id, route_id, travel_time, waiting_time)]
            heapq.heappush(heap, (total_time, next_station_id, route_id, path, 0))

        visited = {}  # (station, route) -> min_time
        best_plan = None
        min_time = float('inf')

        while heap:
            total_time, current_station, current_route, path, transfers = heapq.heappop(heap)

            # 到达目标
            if current_station == to_station_id:
                if total_time < min_time:
                    min_time = total_time
                    best_plan = self._build_plan_from_path_with_waiting(path)
                continue

            # 检查换乘次数
            if transfers > max_transfers:
                continue

            # 状态检查
            state = (current_station, current_route)
            if state in visited and visited[state] <= total_time:
                continue
            visited[state] = total_time

            # 继续乘坐当前线路
            route = self.graph.get_route(current_route)
            current_seq = route.get_station_sequence(current_station)

            if current_seq is not None and current_seq < len(route.stations) - 1:
                next_route_station = route.stations[current_seq + 1]
                next_station_id = next_route_station.station_id
                travel_time = next_route_station.arrival_time_offset - route.stations[current_seq].arrival_time_offset

                new_total_time = total_time + travel_time
                new_path = path + [(next_station_id, current_route, travel_time, 0)]
                heapq.heappush(heap, (new_total_time, next_station_id, current_route, new_path, transfers))

            # 换乘到其他线路（在当前站点换乘）
            if current_station in self.graph.station_routes:
                for other_route_id in self.graph.station_routes[current_station]:
                    if other_route_id != current_route:  # 换乘到不同线路
                        other_route = self.graph.get_route(other_route_id)
                        other_seq = other_route.get_station_sequence(current_station)

                        # 确保可以继续前进
                        if other_seq is not None and other_seq < len(other_route.stations) - 1:
                            next_route_station = other_route.stations[other_seq + 1]
                            next_station_id = next_route_station.station_id
                            travel_time = next_route_station.arrival_time_offset - other_route.stations[other_seq].arrival_time_offset

                            schedule = self.graph.get_schedule(other_route_id)
                            waiting_time = 0
                            if schedule:
                                wt = schedule.get_waiting_time()
                                waiting_time = wt if wt is not None else 0

                            new_total_time = total_time + travel_time + waiting_time + 2  # 加2分钟换乘时间
                            # 在路径中添加换乘点和下一站
                            new_path = path + [(current_station, other_route_id, 0, waiting_time), (next_station_id, other_route_id, travel_time, 0)]
                            heapq.heappush(heap, (new_total_time, next_station_id, other_route_id, new_path, transfers + 1))

        return best_plan

    def _count_transfers(self, path: List[Tuple]) -> int:
        """计算路径中的换乘次数"""
        if len(path) <= 1:
            return 0

        transfers = 0
        prev_route = path[0][1]

        for _, route_id, _ in path[1:]:
            if route_id != prev_route:
                transfers += 1
                prev_route = route_id

        return transfers

    def _build_plan_from_path(self, path: List[Tuple]) -> TransferPlan:
        """从路径构建换乘方案"""
        plan = TransferPlan()

        if not path:
            return plan

        # 按线路分段
        segments = []
        current_segment = [path[0]]

        for i in range(1, len(path)):
            station_id, route_id, travel_time = path[i]
            prev_route_id = path[i-1][1]

            if route_id == prev_route_id:
                current_segment.append(path[i])
            else:
                segments.append(current_segment)
                current_segment = [path[i]]

        segments.append(current_segment)

        # 构建方案
        for segment in segments:
            if len(segment) < 2:
                continue

            route_id = segment[0][1]
            route = self.graph.get_route(route_id)

            from_station_id = segment[0][0]
            to_station_id = segment[-1][0]

            from_station = self.graph.get_station(from_station_id)
            to_station = self.graph.get_station(to_station_id)

            # 计算总行驶时间
            travel_time = sum(item[2] for item in segment[1:])

            # 获取等待时间
            waiting_time = 0
            schedule = self.graph.get_schedule(route_id)
            if schedule and len(plan.segments) == 0:  # 只有第一段需要等待
                wt = schedule.get_waiting_time()
                waiting_time = wt if wt is not None else 0

            plan.add_segment(route, from_station, to_station, travel_time, waiting_time)

        return plan

    def _build_plan_from_path_with_waiting(self, path: List[Tuple]) -> TransferPlan:
        """从带等待时间的路径构建换乘方案"""
        plan = TransferPlan()

        if not path:
            return plan

        # 按线路分段
        segments = []
        current_segment = [path[0]]

        for i in range(1, len(path)):
            station_id, route_id, travel_time, waiting_time = path[i]
            prev_route_id = path[i-1][1]

            if route_id == prev_route_id:
                current_segment.append(path[i])
            else:
                segments.append(current_segment)
                current_segment = [path[i]]

        segments.append(current_segment)

        # 构建方案
        for segment in segments:
            if len(segment) < 2:
                continue

            route_id = segment[0][1]
            route = self.graph.get_route(route_id)

            from_station_id = segment[0][0]
            to_station_id = segment[-1][0]

            from_station = self.graph.get_station(from_station_id)
            to_station = self.graph.get_station(to_station_id)

            # 计算总行驶时间和等待时间
            travel_time = sum(item[2] for item in segment[1:])
            waiting_time = segment[0][3] if len(segment[0]) > 3 else 0

            plan.add_segment(route, from_station, to_station, travel_time, waiting_time)

        return plan
