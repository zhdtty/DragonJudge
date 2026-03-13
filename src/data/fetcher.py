"""A股数据获取模块"""
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
import aiohttp
import pandas as pd
from src.core.config import settings
from src.core.logger import logger


class DataFetcher:
    """
    A股数据抓取器
    
    数据来源:
    - akshare: 主要数据源 (免费)
    - 东方财富: 备选
    - Tushare: 专业数据 (需要token)
    """
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.base_url = "https://push2ex.eastmoney.com"
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_limit_up_stocks(self, date: Optional[str] = None) -> List[Dict]:
        """
        抓取涨停股票列表
        
        返回格式:
        [
            {
                "code": "000001",
                "name": "平安银行",
                "price": 12.50,
                "limit_up_days": 3,
                "sector": "银行",
                "seal_amount": 5000,  # 封单金额(万)
                "turnover": 8000,      # 成交额(万)
                "open_times": 0,       # 开板次数
            }
        ]
        """
        try:
            # 使用东方财富API
            url = f"{self.base_url}/getTopicZTPool"
            params = {
                "ut": "7eea3edcaed734bea9cbfc24409ed989",
                "dpt": "wz.ztzt",
                "Pageindex": "0",
                "pagesize": "500",
                "sort": "fbt:asc",
                "date": date or datetime.now().strftime("%Y%m%d"),
            }
            
            async with self.session.get(url, params=params) as resp:
                if resp.status != 200:
                    logger.error(f"获取涨停数据失败: HTTP {resp.status}")
                    return []
                
                data = await resp.json()
                stocks = []
                
                for item in data.get("data", {}).get("pool", []):
                    stock = {
                        "code": item.get("c"),           # 代码
                        "name": item.get("n"),           # 名称
                        "price": float(item.get("p", 0)) / 1000,  # 价格
                        "limit_up_days": int(item.get("zttz", 1)),  # 连板天数
                        "sector": item.get("hybk", ""),  # 行业板块
                        "seal_amount": float(item.get("fbt", 0)) / 10000,  # 封单金额(万)
                        "turnover": float(item.get("amount", 0)) / 10000,  # 成交额(万)
                        "open_times": int(item.get("opentimes", 0)),  # 开板次数
                        "first_time": item.get("t", ""),  # 首次涨停时间
                        "last_time": item.get("l", ""),  # 最后涨停时间
                    }
                    stocks.append(stock)
                
                logger.info(f"获取涨停股票: {len(stocks)} 只")
                return stocks
                
        except Exception as e:
            logger.error(f"抓取涨停数据失败: {e}")
            return []
    
    async def fetch_limit_down_stocks(self, date: Optional[str] = None) -> List[Dict]:
        """抓取跌停股票列表"""
        try:
            url = f"{self.base_url}/getTopicDTPool"
            params = {
                "ut": "7eea3edcaed734bea9cbfc24409ed989",
                "dpt": "wz.dtzt",
                "Pageindex": "0",
                "pagesize": "500",
                "sort": "fbt:asc",
                "date": date or datetime.now().strftime("%Y%m%d"),
            }
            
            async with self.session.get(url, params=params) as resp:
                if resp.status != 200:
                    return []
                
                data = await resp.json()
                stocks = []
                
                for item in data.get("data", {}).get("pool", []):
                    stock = {
                        "code": item.get("c"),
                        "name": item.get("n"),
                        "price": float(item.get("p", 0)) / 1000,
                        "limit_down_days": int(item.get("dttz", 1)),
                        "sector": item.get("hybk", ""),
                    }
                    stocks.append(stock)
                
                return stocks
                
        except Exception as e:
            logger.error(f"抓取跌停数据失败: {e}")
            return []
    
    async def fetch_zt_trends(self) -> Dict:
        """
        抓取涨停梯队数据
        
        返回:
        {
            "max_height": 5,
            "height_distribution": {
                "1板": 30,
                "2板": 15,
                "3板": 8,
                "4板": 3,
                "5板+": 2,
            },
            "sector_distribution": {
                "能源": 12,
                "科技": 8,
                ...
            },
        }
        """
        try:
            limit_up_stocks = await self.fetch_limit_up_stocks()
            
            if not limit_up_stocks:
                return {}
            
            # 计算高度分布
            height_dist = {"1板": 0, "2板": 0, "3板": 0, "4板": 0, "5板+": 0}
            sector_dist = {}
            max_height = 0
            
            for stock in limit_up_stocks:
                days = stock["limit_up_days"]
                max_height = max(max_height, days)
                
                if days == 1:
                    height_dist["1板"] += 1
                elif days == 2:
                    height_dist["2板"] += 1
                elif days == 3:
                    height_dist["3板"] += 1
                elif days == 4:
                    height_dist["4板"] += 1
                else:
                    height_dist["5板+"] += 1
                
                # 板块分布
                sector = stock.get("sector", "其他")
                sector_dist[sector] = sector_dist.get(sector, 0) + 1
            
            return {
                "max_height": max_height,
                "total_limit_up": len(limit_up_stocks),
                "height_distribution": height_dist,
                "sector_distribution": sector_dist,
                "stocks": limit_up_stocks,
            }
            
        except Exception as e:
            logger.error(f"抓取涨停梯队失败: {e}")
            return {}
    
    async def fetch_market_index(self) -> Dict:
        """
        抓取大盘指数数据
        
        返回:
        {
            "上证指数": {"price": 3000.50, "change": 0.5, "change_pct": 0.02},
            "深证成指": {"price": 9500.30, "change": -10.2, "change_pct": -0.11},
            "创业板指": {"price": 1800.20, "change": 5.8, "change_pct": 0.32},
        }
        """
        try:
            url = "https://push2.eastmoney.com/api/qt/ulist.np/get"
            params = {
                "ut": "7eea3edcaed734bea9cbfc24409ed989",
                "fltt": "2",
                "invt": "2",
                "fields": "f2,f3,f4,f12,f14",
                "secids": "1.000001,0.399001,0.399006",  # 上证、深证、创业板
            }
            
            async with self.session.get(url, params=params) as resp:
                if resp.status != 200:
                    return {}
                
                data = await resp.json()
                indices = {}
                
                name_map = {
                    "000001": "上证指数",
                    "399001": "深证成指",
                    "399006": "创业板指",
                }
                
                for item in data.get("data", {}).get("diff", []):
                    code = item.get("f12")
                    name = name_map.get(code, code)
                    
                    indices[name] = {
                        "price": float(item.get("f2", 0)),
                        "change": float(item.get("f4", 0)),
                        "change_pct": float(item.get("f3", 0)),
                    }
                
                return indices
                
        except Exception as e:
            logger.error(f"抓取大盘数据失败: {e}")
            return {}
    
    async def fetch_all_data(self) -> Dict:
        """抓取所有必要数据"""
        logger.info("开始抓取全市场数据...")
        
        # 并发抓取
        tasks = [
            self.fetch_zt_trends(),
            self.fetch_limit_down_stocks(),
            self.fetch_market_index(),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        zt_data = results[0] if not isinstance(results[0], Exception) else {}
        dt_stocks = results[1] if not isinstance(results[1], Exception) else []
        market_index = results[2] if not isinstance(results[2], Exception) else {}
        
        # 构建完整数据
        all_data = {
            "timestamp": datetime.now().isoformat(),
            "zt_data": zt_data,
            "dt_count": len(dt_stocks),
            "dt_stocks": dt_stocks[:10],  # 只保留前10个
            "market_index": market_index,
            "summary": {
                "limit_up_count": zt_data.get("total_limit_up", 0),
                "limit_down_count": len(dt_stocks),
                "max_height": zt_data.get("max_height", 0),
            },
        }
        
        logger.info(f"数据抓取完成: 涨停 {all_data['summary']['limit_up_count']} 只, "
                   f"跌停 {all_data['summary']['limit_down_count']} 只, "
                   f"最高 {all_data['summary']['max_height']} 板")
        
        return all_data
