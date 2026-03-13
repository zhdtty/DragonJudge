"""情绪周期分析模块"""
from typing import Dict, List
from enum import Enum
from dataclasses import dataclass
from src.core.config import settings
from src.core.logger import logger


class EmotionCycle(Enum):
    """情绪周期枚举"""
    EXTREME_FEAR = "extreme_fear"  # 冰点
    FEAR = "fear"                   # 恐惧
    START = "start"                 # 启动
    FERMENTATION = "fermentation"   # 发酵
    CLIMAX = "climax"               # 高潮
    DIVERGENCE = "divergence"       # 分化
    DECLINE = "decline"             # 退潮


@dataclass
class EmotionIndicators:
    """情绪指标数据"""
    # 涨停相关
    limit_up_count: int           # 涨停家数
    limit_down_count: int         # 跌停家数
    limit_up_ratio: float         # 涨停/跌停比
    
    # 高度相关
    max_height: int               # 最高连板
    height_4plus_count: int       # 4板以上数量
    
    # 晋级相关
    promotion_rate: float         # 昨日涨停今日晋级率
    break_rate: float             # 断板率
    
    # 市场数据
    market_index_change: float    # 大盘涨跌幅
    volume_ratio: float           # 量比
    
    # 情绪得分
    emotion_score: float          # 综合情绪得分 (0-100)


class EmotionAnalyzer:
    """
    A股市场情绪周期分析器
    
    情绪周期判断逻辑:
    - 冰点: 涨停<20家，高度≤2板，情绪分<20
    - 启动: 涨停20-40家，出现3板，情绪分20-40
    - 发酵: 涨停40-60家，4板出现，情绪分40-60
    - 高潮: 涨停60-100家，5板+出现，晋级率>50%，情绪分60-80
    - 分化: 涨停减少，断板增加，高度滞涨，情绪分下降
    - 退潮: 涨停<30家，高度下降，大面股增加，情绪分<40
    """
    
    def __init__(self):
        self.thresholds = {
            "extreme_fear": {"limit_up": 20, "emotion": 20},
            "fear": {"limit_up": 40, "emotion": 40},
            "neutral": {"limit_up": 60, "emotion": 60},
            "greed": {"limit_up": 100, "emotion": 80},
        }
    
    def calculate_emotion_score(self, indicators: EmotionIndicators) -> float:
        """
        计算综合情绪得分 (0-100)
        
        权重:
        - 涨停家数: 30%
        - 晋级率: 25%
        - 高度: 20%
        - 大盘: 15%
        - 量能: 10%
        """
        # 涨停得分 (0-100)
        limit_up_score = min(indicators.limit_up_count, 100)
        
        # 晋级率得分
        promotion_score = indicators.promotion_rate * 100
        
        # 高度得分
        height_score = min(indicators.max_height * 15, 100)
        
        # 大盘得分
        if indicators.market_index_change >= 0:
            market_score = 50 + min(indicators.market_index_change * 10, 50)
        else:
            market_score = max(50 + indicators.market_index_change * 10, 0)
        
        # 量能得分
        volume_score = min(indicators.volume_ratio * 50, 100)
        
        # 加权
        total_score = (
            limit_up_score * 0.30 +
            promotion_score * 0.25 +
            height_score * 0.20 +
            market_score * 0.15 +
            volume_score * 0.10
        )
        
        return min(max(total_score, 0), 100)
    
    def judge_cycle(self, indicators: EmotionIndicators) -> EmotionCycle:
        """
        判断当前情绪周期
        """
        score = self.calculate_emotion_score(indicators)
        
        # 基础判断
        if score < 20:
            return EmotionCycle.EXTREME_FEAR
        elif score < 40:
            if indicators.promotion_rate < 0.3:
                return EmotionCycle.FEAR
            else:
                return EmotionCycle.START
        elif score < 60:
            if indicators.max_height >= 4:
                return EmotionCycle.FERMENTATION
            else:
                return EmotionCycle.START
        elif score < 80:
            if indicators.break_rate > 0.3:
                return EmotionCycle.DIVERGENCE
            else:
                return EmotionCycle.CLIMAX
        else:
            if indicators.limit_up_count < indicators.limit_up_count * 0.8:
                return EmotionCycle.DECLINE
            else:
                return EmotionCycle.CLIMAX
    
    def get_cycle_description(self, cycle: EmotionCycle) -> Dict:
        """获取周期描述和建议"""
        descriptions = {
            EmotionCycle.EXTREME_FEAR: {
                "name": "冰点",
                "description": "市场极度恐慌，涨停极少，高度压制",
                "strategy": "空仓观望，等待新题材启动",
                "position": "0-1成",
                "risk": "高",
            },
            EmotionCycle.FEAR: {
                "name": "恐惧",
                "description": "市场情绪低落，资金谨慎",
                "strategy": "小仓位试错首板",
                "position": "1-2成",
                "risk": "中高",
            },
            EmotionCycle.START: {
                "name": "启动",
                "description": "新题材出现，资金开始进场",
                "strategy": "积极试错新题材龙头",
                "position": "3-4成",
                "risk": "中",
            },
            EmotionCycle.FERMENTATION: {
                "name": "发酵",
                "description": "题材扩散，板块效应明显",
                "strategy": "重仓主线龙头",
                "position": "5-6成",
                "risk": "中低",
            },
            EmotionCycle.CLIMAX: {
                "name": "高潮",
                "description": "市场情绪高涨，全民狂欢",
                "strategy": "去弱留强，准备撤退",
                "position": "4-5成",
                "risk": "中",
            },
            EmotionCycle.DIVERGENCE: {
                "name": "分化",
                "description": "龙头分歧，跟风股掉队",
                "strategy": "只留最强龙头，其他卖出",
                "position": "2-3成",
                "risk": "中高",
            },
            EmotionCycle.DECLINE: {
                "name": "退潮",
                "description": "大面积杀跌，跌停增加",
                "strategy": "空仓或极小仓位",
                "position": "0-1成",
                "risk": "高",
            },
        }
        
        return descriptions.get(cycle, descriptions[EmotionCycle.NEUTRAL])
    
    def analyze(self, market_data: Dict) -> Dict:
        """
        综合分析市场情绪
        
        Args:
            market_data: {
                "limit_up_count": 45,
                "limit_down_count": 5,
                "max_height": 5,
                "height_4plus_count": 3,
                "promotion_rate": 0.35,
                "break_rate": 0.25,
                "market_index_change": 0.5,
                "volume_ratio": 1.2,
            }
        """
        try:
            indicators = EmotionIndicators(
                limit_up_count=market_data.get("limit_up_count", 0),
                limit_down_count=market_data.get("limit_down_count", 0),
                limit_up_ratio=market_data.get("limit_up_ratio", 0),
                max_height=market_data.get("max_height", 0),
                height_4plus_count=market_data.get("height_4plus_count", 0),
                promotion_rate=market_data.get("promotion_rate", 0),
                break_rate=market_data.get("break_rate", 0),
                market_index_change=market_data.get("market_index_change", 0),
                volume_ratio=market_data.get("volume_ratio", 1.0),
                emotion_score=0,  # 稍后计算
            )
            
            # 计算情绪得分
            indicators.emotion_score = self.calculate_emotion_score(indicators)
            
            # 判断周期
            cycle = self.judge_cycle(indicators)
            
            # 获取描述
            description = self.get_cycle_description(cycle)
            
            return {
                "cycle": cycle.value,
                "cycle_name": description["name"],
                "emotion_score": round(indicators.emotion_score, 2),
                "description": description["description"],
                "strategy": description["strategy"],
                "suggested_position": description["position"],
                "risk_level": description["risk"],
                "indicators": {
                    "limit_up_count": indicators.limit_up_count,
                    "max_height": indicators.max_height,
                    "promotion_rate": round(indicators.promotion_rate * 100, 2),
                },
            }
            
        except Exception as e:
            logger.error(f"情绪分析失败: {e}")
            return {
                "cycle": "unknown",
                "emotion_score": 0,
                "description": "分析失败",
                "strategy": "观望",
            }
