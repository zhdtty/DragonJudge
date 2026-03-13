"""Dragon Judge 测试"""
import pytest
from src.analysis.dragon_judge import DragonJudge, StockScore


class TestDragonJudge:
    """Dragon Judge 评分系统测试"""
    
    @pytest.fixture
    def judge(self):
        return DragonJudge()
    
    def test_calculate_height_score(self, judge):
        """测试连板高度得分"""
        assert judge.calculate_height_score(1) == 10
        assert judge.calculate_height_score(2) == 25
        assert judge.calculate_height_score(3) == 40
        assert judge.calculate_height_score(4) == 55
        assert judge.calculate_height_score(5) == 65
        assert judge.calculate_height_score(6) == 67  # 边际递减
        assert judge.calculate_height_score(0) == 0
    
    def test_calculate_competition_score(self, judge):
        """测试卡位竞争得分"""
        assert judge.calculate_competition_score(3, 0) == 100  # 独龙
        assert judge.calculate_competition_score(3, 1) == 70
        assert judge.calculate_competition_score(3, 2) == 50
        assert judge.calculate_competition_score(3, 3) == 30
        assert judge.calculate_competition_score(3, 5) == 20  # 最低10分保底
    
    def test_calculate_sector_score(self, judge):
        """测试板块助攻得分"""
        assert judge.calculate_sector_score(1, 50) == 20
        assert judge.calculate_sector_score(4, 50) == 40
        assert judge.calculate_sector_score(8, 50) == 60
        assert judge.calculate_sector_score(12, 50) == 80
        # 板块占比高加分
        assert judge.calculate_sector_score(6, 30) == 80  # 20%涨停，+20分
    
    def test_calculate_emotion_score(self, judge):
        """测试市场情绪得分"""
        # 冰点期，低位股应该高分
        assert judge.calculate_emotion_score("extreme_fear", "low") == 80
        assert judge.calculate_emotion_score("extreme_fear", "high") == 20
        # 高潮期，高位股应该高分
        assert judge.calculate_emotion_score("extreme_greed", "low") == 20
        assert judge.calculate_emotion_score("extreme_greed", "high") == 80
    
    def test_calculate_quality_score(self, judge):
        """测试封板质量得分"""
        # 封单/成交 > 1
        assert judge.calculate_quality_score(10000, 5000, 0) == 100
        # 封单/成交 0.5-1
        assert judge.calculate_quality_score(5000, 8000, 0) == 80
        # 开板扣分
        assert judge.calculate_quality_score(10000, 5000, 2) == 80  # 扣20分
    
    def test_calculate_total_score(self, judge):
        """测试总分计算"""
        stock_data = {
            "code": "000001",
            "name": "测试股票",
            "limit_up_days": 3,
            "competitors_count": 1,
            "sector_limit_up_count": 8,
            "sector_total_count": 50,
            "market_emotion": "neutral",
            "stock_type": "high",
            "seal_amount": 5000,
            "turnover": 8000,
            "open_times": 0,
        }
        
        result = judge.calculate_total_score(stock_data)
        
        assert isinstance(result, StockScore)
        assert result.code == "000001"
        assert result.name == "测试股票"
        assert result.total_score > 0
        assert result.height_score == 40  # 3板
        assert result.competition_score == 70  # 1个竞争者
    
    def test_rank_stocks(self, judge):
        """测试股票排序"""
        stocks = [
            {
                "code": "000001",
                "name": "股票A",
                "limit_up_days": 2,
                "competitors_count": 0,
                "sector_limit_up_count": 5,
                "sector_total_count": 50,
                "market_emotion": "neutral",
                "stock_type": "low",
                "seal_amount": 10000,
                "turnover": 5000,
                "open_times": 0,
            },
            {
                "code": "000002",
                "name": "股票B",
                "limit_up_days": 5,
                "competitors_count": 0,
                "sector_limit_up_count": 10,
                "sector_total_count": 50,
                "market_emotion": "neutral",
                "stock_type": "high",
                "seal_amount": 20000,
                "turnover": 8000,
                "open_times": 0,
            },
        ]
        
        ranked = judge.rank_stocks(stocks)
        
        assert len(ranked) == 2
        # 股票B应该排第一（5板+板块强）
        assert ranked[0].code == "000002"
        assert ranked[0].total_score > ranked[1].total_score
