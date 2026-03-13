#!/usr/bin/env python3
"""DragonJudge CLI"""
import asyncio
import argparse
from src.main import main


def cli():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="A股情绪龙头助手")
    parser.add_argument(
        "--version", 
        action="version", 
        version="%(prog)s 0.1.0"
    )
    parser.add_argument(
        "--fetch", 
        action="store_true",
        help="立即抓取数据并生成报告"
    )
    
    args = parser.parse_args()
    
    if args.fetch:
        asyncio.run(main())
    else:
        print("DragonJudge v0.1.0")
        print("Use --fetch to run data fetch and report generation")


if __name__ == "__main__":
    cli()
