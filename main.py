#!/usr/bin/env python3
"""
公交线路规划系统 - 主程序入口
"""
import sys
sys.path.append('/home/user/weiruan-bus')

from src.data import load_nanshan_data
from src.cli import BusRouteCLI


def main():
    """主函数"""
    # 加载深圳南山区数据
    print("正在加载数据...")
    graph = load_nanshan_data()
    print(f"数据加载完成：{graph}")

    # 启动CLI
    cli = BusRouteCLI(graph)
    cli.interactive_mode()


if __name__ == "__main__":
    main()
