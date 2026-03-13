"""Dragon Judge 龙头评分系统"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from src.core.config import settings
from src.core.logger import logger


@dataclass
class StockScore:
    """股票评分结果"""
    code: str
    name: str
    height_score: float      # 连板高度得分 (40%)
    competition_score: float # 卡位竞争得分 (30%)
    sector_score: float      # 板块助攻得分 (20%)
    emotion_score: float     # 市场情绪得分 (5%)
    quality_score: float     # 封板质量得分 (5%)
    total_score: float       # 总分
    
    def to_dict(self) -> Dict:
        return {
            "code": self.code,
            "name": self.name,
            "height_score": round(self.height_score, 2),
            "competition_score": round(self.competition_score, 2),
            "sector_score": round(self.sector_score, 2),
            "emotion_score": round(self.emotion_score, 2),
            "quality_score": round(self.quality_score, 2),
            "total_score": round(self.total_score, 2),
        }


class DragonJudge:
    """
    Dragon Judge 龙头评分系统
    
    5维度评分:
    - 连板高度 (40%): 高度越高得分越高，但边际递减
    - 卡位竞争 (30%): 同身位竞争越少得分越高
    - 板块助攻 (20%): 板块内涨停股越多得分越高
    - 市场情绪 (5%): 与大盘情绪匹配度
    - 封板质量 (5%): 封单量/成交量比值
    """
    
    def __init__(self):
        self.weights = {
            "height": settings.WEIGHT_HEIGHT,
            "competition": settings.WEIGHT_COMPETITION,
            "sector": settings.WEIGHT_SECTOR,
            "emotion": settings.WEIGHT_EMOTION,
            "quality": settings.WEIGHT_QUALITY,
        }
    
    def calculate_height_score(self, limit_up_days: int) -> float:
        """
        计算连板高度得分
        
        评分规则:
        - 1板: 10分
        - 2板: 25分
        - 3板: 40分
        - 4板: 55分
        - 5板+: 65分（边际递减）
        """
        if limit_up_days <= 0:
            return 0
        
        score_map = {
            1: 10,
            2: 25,
            3: 40,
            4: 55,
        }
        
        if limit_up_days >= 5:
            # 5板以上边际递减
            base = 65
            extra = (limit_up_days - 5) * 2
            return min(base + extra, 100)
        
        return score_map.get(limit_up_days, 10)
    
    def calculate_competition_score(
        self, 
        current_height: int,
        competitors_count: int
    ) -> float:
        """
        计算卡位竞争得分
        
        评分规则:
        - 无竞争（独龙）: 100分
        - 1个竞争者: 70分
        - 2个竞争者: 50分
        - 3个+: 30分
        """
        if competitors_count == 0:
            return 100
        elif competitors_count == 1:
            return 70
        elif competitors_count == 2:
            return 50
        else:
            return max(30 - (competitors_count - 3) * 5, 10)
    
    def calculate_sector_score(
        self,
        sector_limit_up_count: int,
        sector_total_count: int
    ) -> float:
        """
        计算板块助攻得分
        
        评分规则:
        - 板块涨停数 1-2: 20分
        - 板块涨停数 3-5: 40分
        - 板块涨停数 6-10: 60分
        - 板块涨停数 11+: 80分
        - 板块内占比高: +20分
        """
        base_score = 0
        
        if sector_limit_up_count >= 11:
            base_score = 80
        elif sector_limit_up_count >= 6:
            base_score = 60
        elif sector_limit_up_count >= 3:
            base_score = 40
        elif sector_limit_up_count >= 1:
            base_score = 20
        
        # 板块内涨停占比加分
        if sector_total_count > 0:
            ratio = sector_limit_up_count / sector_total_count
            if ratio > 0.1:  # 板块内10%股票涨停
                base_score += 20
        
        return min(base_score, 100)
    
    def calculate_emotion_score(
        self,
        market_emotion: str,
        stock_type: str
    ) -> float:
        """
        计算市场情绪匹配得分
        
        逻辑:
        - 冰点期: 只给低位首板高分
        - 高潮期: 给高位龙头高分
        """
        emotion_scores = {
            "extreme_fear": {"low": 80, "high": 20},
            "fear": {"low": 70, "high": 30},
            "neutral": {"low": 50, "high": 50},
            "greed": {"low": 30, "high": 70},
            "extreme_greed": {"low": 20, "high": 80},
        }
        
        scores = emotion_scores.get(market_emotion, {"low": 50, "high": 50})
        return scores.get(stock_type, 50)
    
    def calculate_quality_score(
        self,
        seal_amount: float,  # 封单金额（万）
        turnover: float,      # 成交额（万）
        open_times: int       # 开板次数
    ) -> float:
        """
        计算封板质量得分
        
        评分规则:
        - 封单/成交 > 1: 100分
        - 封单/成交 0.5-1: 80分
        - 封单/成交 0.2-0.5: 60分
        - 封单/成交 < 0.2: 40分
        - 开板次数扣分: 每次-10分
        """
        if turnover <= 0:
            return 0
        
        ratio = seal_amount / turnover
        
        if ratio > 1:
            score = 100
        elif ratio > 0.5:
            score = 80
        elif ratio > 0.2:
            score = 60
        else:
            score = 40
        
        # 开板扣分
        score -= open_times * 10
        
        return max(score, 0)
    
    def calculate_total_score(self, stock_data: Dict) -> StockScore:
        """
        计算股票总分
        
        Args:
            stock_data: {
                "code": "000001",
                "name": "平安银行",
                "limit_up_days": 3,
                "competitors_count": 1,
                "sector_limit_up_count": 8,
                "sector_total_count": 50,
                "market_emotion": "neutral",
                "stock_type": "high",  # low/high
                "seal_amount": 5000,
                "turnover": 8000,
                "open_times": 0,
            }
        """
        try:
            height_score = self.calculate_height_score(
                stock_data.get("limit_up_days", 0)
            )
            
            competition_score = self.calculate_competition_score(
                stock_data.get("limit_up_days", 0),
                stock_data.get("competitors_count", 0)
            )
            
            sector_score = self.calculate_sector_score(
                stock_data.get("sector_limit_up_count", 0),
                stock_data.get("sector_total_count", 1)
            )
            
            emotion_score = self.calculate_emotion_score(
                stock_data.get("market_emotion", "neutral"),
                stock_data.get("stock_type", "low")
            )
            
            quality_score = self.calculate_quality_score(
                stock_data.get("seal_amount", 0),
                stock_data.get("turnover", 1),
                stock_data.get("open_times", 0)
            )
            
            # 加权总分
            total_score = (
                height_score * self.weights["height"] +
                competition_score * self.weights["competition"] +
                sector_score * self.weights["sector"] +
                emotion_score * self.weights["emotion"] +
                quality_score * self.weights["quality"]
            )
            
            return StockScore(
                code=stock_data["code"],
                name=stock_data["name"],
                height_score=height_score,
                competition_score=competition_score,
                sector_score=sector_score,
                emotion_score=emotion_score,
                quality_score=quality_score,
                total_score=total_score,
            )
            
        except Exception as e:
            logger.error(f"计算股票 {stock_data.get('code')} 评分失败: {e}")
            return StockScore(
                code=stock_data.get("code", ""),
                name=stock_data.get("name", ""),
                height_score=0,
                competition_score=0,
                sector_score=0,
                emotion_score=0,
                quality_score=0,
                total_score=0,
            )
    
    def rank_stocks(self, stocks_data: List[Dict]) -> List[StockScore]:
        """对多只股票进行评分排序"""
        scores = []
        for stock in stocks_data:
            score = self.calculate_total_score(stock)
            scores.append(score)
        
        # 按总分降序
        scores.sort(key=lambda x: x.total_score, reverse=True)
        return scores
