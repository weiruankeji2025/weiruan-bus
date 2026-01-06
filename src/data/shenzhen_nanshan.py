"""
深圳南山区公交线路数据
"""
from datetime import time
import sys
sys.path.append('/home/user/weiruan-bus')

from src.models import Station, BusRoute, Schedule
from src.planner import TransitGraph


def load_nanshan_data() -> TransitGraph:
    """
    加载深圳南山区公交数据

    Returns:
        TransitGraph对象，包含南山区的公交网络
    """
    graph = TransitGraph()

    # ========== 创建站点 ==========
    stations_data = [
        # M492路沿线站点
        ("SZ_NS_001", "科技园", 22.5428, 113.9493, "深圳市", "南山区"),
        ("SZ_NS_002", "深大北门", 22.5456, 113.9456, "深圳市", "南山区"),
        ("SZ_NS_003", "桂庙路口", 22.5389, 113.9389, "深圳市", "南山区"),
        ("SZ_NS_004", "大冲", 22.5367, 113.9367, "深圳市", "南山区"),
        ("SZ_NS_005", "科苑路", 22.5345, 113.9345, "深圳市", "南山区"),
        ("SZ_NS_006", "后海", 22.5312, 113.9312, "深圳市", "南山区"),

        # M475路沿线站点
        ("SZ_NS_007", "南山", 22.5289, 113.9289, "深圳市", "南山区"),
        ("SZ_NS_008", "南山医院", 22.5267, 113.9267, "深圳市", "南山区"),
        ("SZ_NS_009", "南新路", 22.5245, 113.9245, "深圳市", "南山区"),
        ("SZ_NS_010", "南油", 22.5223, 113.9223, "深圳市", "南山区"),
        ("SZ_NS_011", "海雅百货", 22.5201, 113.9201, "深圳市", "南山区"),
        ("SZ_NS_012", "蛇口", 22.5178, 113.9178, "深圳市", "南山区"),

        # 72路沿线站点
        ("SZ_NS_013", "世界之窗", 22.5456, 113.9567, "深圳市", "南山区"),
        ("SZ_NS_014", "白石洲", 22.5434, 113.9534, "深圳市", "南山区"),
        ("SZ_NS_015", "沙河东路", 22.5412, 113.9512, "深圳市", "南山区"),
        ("SZ_NS_016", "华侨城", 22.5390, 113.9490, "深圳市", "南山区"),
        ("SZ_NS_017", "欢乐海岸", 22.5368, 113.9468, "深圳市", "南山区"),
        ("SZ_NS_018", "海上世界", 22.5156, 113.9156, "深圳市", "南山区"),

        # B737路沿线站点
        ("SZ_NS_019", "高新园", 22.5501, 113.9501, "深圳市", "南山区"),
        ("SZ_NS_020", "深南科技路口", 22.5478, 113.9478, "深圳市", "南山区"),

        # M506路沿线站点
        ("SZ_NS_021", "车公庙", 22.5523, 113.9423, "深圳市", "南山区"),
        ("SZ_NS_022", "香蜜湖", 22.5489, 113.9389, "深圳市", "南山区"),
    ]

    for station_id, name, lat, lon, city, district in stations_data:
        station = Station(station_id, name, lat, lon, city, district)
        graph.add_station(station)

    # ========== 创建公交线路 ==========

    # M492路：科技园 -> 后海
    route_m492 = BusRoute(
        route_id="M492",
        route_name="M492路",
        city="深圳市",
        district="南山区",
        price=2.0,
        is_loop=False
    )
    route_m492.add_station("SZ_NS_001", 0, 0)   # 科技园
    route_m492.add_station("SZ_NS_002", 1, 3)   # 深大北门 (3分钟)
    route_m492.add_station("SZ_NS_003", 2, 6)   # 桂庙路口 (6分钟)
    route_m492.add_station("SZ_NS_004", 3, 10)  # 大冲 (10分钟)
    route_m492.add_station("SZ_NS_005", 4, 14)  # 科苑路 (14分钟)
    route_m492.add_station("SZ_NS_006", 5, 20)  # 后海 (20分钟)

    schedule_m492 = Schedule(
        route_id="M492",
        first_bus=time(6, 30),
        last_bus=time(22, 30),
        interval=8
    )
    graph.add_route(route_m492, schedule_m492)

    # M475路：南山 -> 蛇口
    route_m475 = BusRoute(
        route_id="M475",
        route_name="M475路",
        city="深圳市",
        district="南山区",
        price=2.0,
        is_loop=False
    )
    route_m475.add_station("SZ_NS_007", 0, 0)   # 南山
    route_m475.add_station("SZ_NS_008", 1, 4)   # 南山医院 (4分钟)
    route_m475.add_station("SZ_NS_004", 2, 8)   # 大冲 (8分钟) - 与M492交汇
    route_m475.add_station("SZ_NS_009", 3, 12)  # 南新路 (12分钟)
    route_m475.add_station("SZ_NS_010", 4, 16)  # 南油 (16分钟)
    route_m475.add_station("SZ_NS_011", 5, 20)  # 海雅百货 (20分钟)
    route_m475.add_station("SZ_NS_012", 6, 28)  # 蛇口 (28分钟)

    schedule_m475 = Schedule(
        route_id="M475",
        first_bus=time(6, 0),
        last_bus=time(23, 0),
        interval=10
    )
    graph.add_route(route_m475, schedule_m475)

    # 72路：世界之窗 -> 海上世界
    route_72 = BusRoute(
        route_id="72",
        route_name="72路",
        city="深圳市",
        district="南山区",
        price=2.5,
        is_loop=False
    )
    route_72.add_station("SZ_NS_013", 0, 0)   # 世界之窗
    route_72.add_station("SZ_NS_014", 1, 5)   # 白石洲 (5分钟)
    route_72.add_station("SZ_NS_015", 2, 9)   # 沙河东路 (9分钟)
    route_72.add_station("SZ_NS_016", 3, 13)  # 华侨城 (13分钟)
    route_72.add_station("SZ_NS_017", 4, 18)  # 欢乐海岸 (18分钟)
    route_72.add_station("SZ_NS_006", 5, 24)  # 后海 (24分钟) - 与M492交汇
    route_72.add_station("SZ_NS_011", 6, 30)  # 海雅百货 (30分钟) - 与M475交汇
    route_72.add_station("SZ_NS_018", 7, 38)  # 海上世界 (38分钟)

    schedule_72 = Schedule(
        route_id="72",
        first_bus=time(6, 15),
        last_bus=time(22, 45),
        interval=12
    )
    graph.add_route(route_72, schedule_72)

    # B737路：南山医院 -> 欢乐海岸
    route_b737 = BusRoute(
        route_id="B737",
        route_name="B737路",
        city="深圳市",
        district="南山区",
        price=2.0,
        is_loop=False
    )
    route_b737.add_station("SZ_NS_008", 0, 0)   # 南山医院
    route_b737.add_station("SZ_NS_019", 1, 6)   # 高新园 (6分钟)
    route_b737.add_station("SZ_NS_020", 2, 10)  # 深南科技路口 (10分钟)
    route_b737.add_station("SZ_NS_001", 3, 14)  # 科技园 (14分钟) - 与M492交汇
    route_b737.add_station("SZ_NS_016", 4, 20)  # 华侨城 (20分钟) - 与72路交汇
    route_b737.add_station("SZ_NS_017", 5, 25)  # 欢乐海岸 (25分钟)

    schedule_b737 = Schedule(
        route_id="B737",
        first_bus=time(6, 45),
        last_bus=time(22, 15),
        interval=15
    )
    graph.add_route(route_b737, schedule_b737)

    # M506路：车公庙 -> 大冲
    route_m506 = BusRoute(
        route_id="M506",
        route_name="M506路",
        city="深圳市",
        district="南山区",
        price=2.0,
        is_loop=False
    )
    route_m506.add_station("SZ_NS_021", 0, 0)   # 车公庙
    route_m506.add_station("SZ_NS_022", 1, 5)   # 香蜜湖 (5分钟)
    route_m506.add_station("SZ_NS_002", 2, 10)  # 深大北门 (10分钟) - 与M492交汇
    route_m506.add_station("SZ_NS_004", 3, 15)  # 大冲 (15分钟)
    route_m506.add_station("SZ_NS_011", 4, 25)  # 海雅百货 (25分钟)

    schedule_m506 = Schedule(
        route_id="M506",
        first_bus=time(6, 20),
        last_bus=time(23, 20),
        interval=10
    )
    graph.add_route(route_m506, schedule_m506)

    return graph


def get_test_cases():
    """
    获取测试用例

    Returns:
        测试用例列表 [(from_name, to_name, from_id, to_id, description)]
    """
    test_cases = [
        # 直达线路测试
        ("科技园", "后海", "SZ_NS_001", "SZ_NS_006", "M492路直达"),
        ("南山", "蛇口", "SZ_NS_007", "SZ_NS_012", "M475路直达"),
        ("世界之窗", "海上世界", "SZ_NS_013", "SZ_NS_018", "72路直达"),

        # 一次换乘测试
        ("科技园", "蛇口", "SZ_NS_001", "SZ_NS_012", "需要在大冲换乘"),
        ("南山医院", "后海", "SZ_NS_008", "SZ_NS_006", "需要在大冲或华侨城换乘"),
        ("世界之窗", "蛇口", "SZ_NS_013", "SZ_NS_012", "需要在后海或海雅百货换乘"),

        # 多次换乘测试
        ("车公庙", "海上世界", "SZ_NS_021", "SZ_NS_018", "需要多次换乘"),
        ("高新园", "南油", "SZ_NS_019", "SZ_NS_010", "需要多次换乘"),
    ]

    return test_cases
