"""情绪分析测试"""
import pytest
from src.analysis.emotion import EmotionAnalyzer, EmotionCycle, EmotionIndicators


class TestEmotionAnalyzer:
    """情绪分析器测试"""
    
    @pytest.fixture
    def analyzer(self):
        return EmotionAnalyzer()
    
    def test_calculate_emotion_score(self, analyzer):
        """测试情绪得分计算"""
        indicators = EmotionIndicators(
            limit_up_count=60,
            limit_down_count=5,
            limit_up_ratio=12.0,
            max_height=5,
            height_4plus_count=3,
            promotion_rate=0.40,
            break_rate=0.20,
            market_index_change=1.0,
            volume_ratio=1.2,
            emotion_score=0,
        )
        
        score = analyzer.calculate_emotion_score(indicators)
        
        assert 0 <= score <= 100
        # 60涨停 + 40%晋级率 + 5板高度 + 大盘涨1% + 量1.2倍，应该得分较高
        assert score > 50
    
    def test_judge_cycle_extreme_fear(self, analyzer):
        """测试冰点判断"""
        indicators = EmotionIndicators(
            limit_up_count=15,
            limit_down_count=20,
            limit_up_ratio=0.75,
            max_height=2,
            height_4plus_count=0,
            promotion_rate=0.15,
            break_rate=0.50,
            market_index_change=-1.5,
            volume_ratio=0.8,
            emotion_score=15,
        )
        
        cycle = analyzer.judge_cycle(indicators)
        assert cycle == EmotionCycle.EXTREME_FEAR
    
    def test_judge_cycle_climax(self, analyzer):
        """测试高潮判断"""
        indicators = EmotionIndicators(
            limit_up_count=80,
            limit_down_count=2,
            limit_up_ratio=40.0,
            max_height=7,
            height_4plus_count=5,
            promotion_rate=0.60,
            break_rate=0.10,
            market_index_change=2.0,
            volume_ratio=1.5,
            emotion_score=75,
        )
        
        cycle = analyzer.judge_cycle(indicators)
        assert cycle == EmotionCycle.CLIMAX
    
    def test_get_cycle_description(self, analyzer):
        """测试周期描述"""
        desc = analyzer.get_cycle_description(EmotionCycle.CLIMAX)
        
        assert desc["name"] == "高潮"
        assert "策略" in desc["strategy"]
        assert "仓位" in desc["position"]
    
    def test_analyze_integration(self, analyzer):
        """测试完整分析流程"""
        market_data = {
            "limit_up_count": 45,
            "limit_down_count": 5,
            "max_height": 5,
            "height_4plus_count": 3,
            "promotion_rate": 0.35,
            "break_rate": 0.25,
            "market_index_change": 0.5,
            "volume_ratio": 1.2,
        }
        
        result = analyzer.analyze(market_data)
        
        assert "cycle" in result
        assert "emotion_score" in result
        assert "strategy" in result
        assert "suggested_position" in result
        assert 0 <= result["emotion_score"] <= 100
