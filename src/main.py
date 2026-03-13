"""DragonJudge 主入口"""
import asyncio
import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.data.fetcher import DataFetcher
from src.analysis.report import ReportGenerator
from src.core.logger import logger


async def main():
    """主函数"""
    logger.info("🚀 DragonJudge 启动...")
    
    async with DataFetcher() as fetcher:
        # 抓取数据
        logger.info("📊 正在抓取市场数据...")
        data = await fetcher.fetch_all_data()
        
        if not data or not data.get("zt_data"):
            logger.error("❌ 数据抓取失败")
            return
        
        # 生成报告
        logger.info("📝 正在生成报告...")
        generator = ReportGenerator()
        
        # 完整报告
        full_report = generator.generate_daily_report(data)
        print("\n" + "="*60)
        print(full_report)
        print("="*60 + "\n")
        
        # 简短报告
        short_report = generator.generate_short_report(data)
        print("\n" + "-"*60)
        print(short_report)
        print("-"*60 + "\n")
        
        logger.info("✅ 报告生成完成!")


if __name__ == "__main__":
    asyncio.run(main())
