"""报告生成模块"""
from typing import Dict, List
from datetime import datetime
from src.analysis.dragon_judge import DragonJudge, StockScore
from src.analysis.emotion import EmotionAnalyzer
from src.core.logger import logger


class ReportGenerator:
    """
    每日复盘报告生成器
    
    生成格式:
    - Markdown 格式
    - 适合 Telegram/Discord 推送
    - 包含表情符号增强可读性
    """
    
    def __init__(self):
        self.dragon_judge = DragonJudge()
        self.emotion_analyzer = EmotionAnalyzer()
    
    def generate_daily_report(self, data: Dict) -> str:
        """
        生成每日复盘报告
        
        Args:
            data: fetch_all_data() 返回的完整数据
        """
        try:
            report = []
            
            # 标题
            report.append(self._generate_header())
            
            # 情绪周期
            report.append(self._generate_emotion_section(data))
            
            # 涨停梯队
            report.append(self._generate_zt_ladder_section(data))
            
            # 龙头评分
            report.append(self._generate_dragon_section(data))
            
            # 策略建议
            report.append(self._generate_strategy_section(data))
            
            return "\n\n".join(report)
            
        except Exception as e:
            logger.error(f"生成报告失败: {e}")
            return f"❌ 报告生成失败: {e}"
    
    def _generate_header(self) -> str:
        """生成报告头部"""
        date_str = datetime.now().strftime("%Y年%m月%d日")
        return f"""📊 **A股情绪复盘报告**
📅 {date_str}

---"""
    
    def _generate_emotion_section(self, data: Dict) -> str:
        """生成情绪周期部分"""
        summary = data.get("summary", {})
        market_index = data.get("market_index", {})
        
        # 构建情绪指标
        emotion_data = {
            "limit_up_count": summary.get("limit_up_count", 0),
            "limit_down_count": data.get("dt_count", 0),
            "max_height": summary.get("max_height", 0),
            "promotion_rate": 0.35,  # 简化，实际应计算
            "break_rate": 0.25,
            "market_index_change": market_index.get("上证指数", {}).get("change_pct", 0),
            "volume_ratio": 1.0,
        }
        
        # 分析情绪
        emotion_result = self.emotion_analyzer.analyze(emotion_data)
        
        # 情绪表情
        emotion_emoji = {
            "extreme_fear": "❄️",
            "fear": "😰",
            "start": "🌱",
            "fermentation": "🔥",
            "climax": "🚀",
            "divergence": "⚠️",
            "decline": "📉",
        }
        
        emoji = emotion_emoji.get(emotion_result["cycle"], "😐")
        
        section = f"""## {emoji} 情绪周期: {emotion_result['cycle_name']}

**情绪得分**: {emotion_result['emotion_score']}/100

**状态描述**: {emotion_result['description']}

**策略建议**: {emotion_result['strategy']}

**建议仓位**: {emotion_result['suggested_position']}

**关键数据**:
- 涨停: {summary.get('limit_up_count', 0)} 只
- 跌停: {data.get('dt_count', 0)} 只  
- 最高连板: {summary.get('max_height', 0)} 板
- 上证涨跌: {market_index.get('上证指数', {}).get('change_pct', 0):.2f}%"""
        
        return section
    
    def _generate_zt_ladder_section(self, data: Dict) -> str:
        """生成涨停梯队部分"""
        zt_data = data.get("zt_data", {})
        height_dist = zt_data.get("height_distribution", {})
        sector_dist = zt_data.get("sector_distribution", {})
        
        # 梯队分布
        ladder_text = []
        for height, count in height_dist.items():
            if count > 0:
                ladder_text.append(f"- {height}: {count} 只")
        
        # 板块分布（Top 5）
        top_sectors = sorted(sector_dist.items(), key=lambda x: x[1], reverse=True)[:5]
        sector_text = [f"- {name}: {count} 只" for name, count in top_sectors]
        
        section = f"""## 📈 涨停梯队

**高度分布**:
{chr(10).join(ladder_text)}

**板块热度 Top 5**:
{chr(10).join(sector_text)}"""
        
        return section
    
    def _generate_dragon_section(self, data: Dict) -> str:
        """生成龙头评分部分"""
        zt_data = data.get("zt_data", {})
        stocks = zt_data.get("stocks", [])
        
        if not stocks:
            return "## 🐉 龙头评分\n\n暂无涨停股票数据"
        
        # 筛选有竞争力的股票（3板以上）
        candidates = [s for s in stocks if s.get("limit_up_days", 0) >= 3]
        
        if not candidates:
            candidates = stocks[:10]  # 取前10个
        
        # 计算评分
        scored_stocks = []
        for stock in candidates:
            # 补充分析所需字段
            stock_data = {
                **stock,
                "competitors_count": 0,  # 简化
                "sector_limit_up_count": zt_data.get("sector_distribution", {}).get(stock.get("sector", ""), 0),
                "sector_total_count": 50,
                "market_emotion": "neutral",
                "stock_type": "high" if stock.get("limit_up_days", 0) >= 3 else "low",
            }
            
            score = self.dragon_judge.calculate_total_score(stock_data)
            scored_stocks.append(score)
        
        # 排序取前5
        scored_stocks.sort(key=lambda x: x.total_score, reverse=True)
        top5 = scored_stocks[:5]
        
        # 生成表格
        dragon_lines = []
        dragon_lines.append("| 排名 | 代码 | 名称 | 连板 | 总分 | 评分 |")
        dragon_lines.append("|------|------|------|------|------|------|")
        
        for i, stock in enumerate(top5, 1):
            rating = "🔥" if stock.total_score >= 80 else "⭐" if stock.total_score >= 60 else "📊"
            dragon_lines.append(
                f"| {i} | {stock.code} | {stock.name} | {stock.height_score/15:.0f}板 | "
                f"{stock.total_score:.1f} | {rating} |"
            )
        
        section = f"""## 🐉 龙头评分 Top 5

{chr(10).join(dragon_lines)}

**评分维度**: 高度40% | 竞争30% | 板块20% | 情绪5% | 质量5%"""
        
        return section
    
    def _generate_strategy_section(self, data: Dict) -> str:
        """生成策略建议部分"""
        summary = data.get("summary", {})
        max_height = summary.get("max_height", 0)
        limit_up_count = summary.get("limit_up_count", 0)
        
        # 根据数据生成建议
        if max_height >= 5 and limit_up_count > 60:
            strategy = "高潮期，去弱留强，只保留最强龙头"
            watchlist = "观察高标是否断板，准备撤退"
        elif max_height >= 3 and limit_up_count > 40:
            strategy = "发酵期，积极试错主线龙头"
            watchlist = "关注3进4，板块持续性"
        elif limit_up_count > 20:
            strategy = "启动期，小仓位试错首板"
            watchlist = "观察新题材，寻找潜力龙头"
        else:
            strategy = "冰点期，空仓观望为主"
            watchlist = "等待情绪回暖信号"
        
        section = f"""## 🎯 明日策略

**操作建议**: {strategy}

**重点关注**:
- {watchlist}
- 竞价观察一字板数量
- 观察北向资金流向
- 关注晚间消息面

---
*报告生成时间: {datetime.now().strftime("%H:%M:%S")}*
*免责声明: 仅供参考，不构成投资建议* ⚠️"""
        
        return section
    
    def generate_short_report(self, data: Dict) -> str:
        """生成简短报告（用于推送）"""
        summary = data.get("summary", {})
        
        emotion_data = {
            "limit_up_count": summary.get("limit_up_count", 0),
            "limit_down_count": data.get("dt_count", 0),
            "max_height": summary.get("max_height", 0),
            "promotion_rate": 0.35,
            "break_rate": 0.25,
            "market_index_change": 0,
            "volume_ratio": 1.0,
        }
        
        emotion = self.emotion_analyzer.analyze(emotion_data)
        
        return f"""📊 复盘速报

{emotion['cycle_name']} | 得分: {emotion['emotion_score']}
涨停: {summary.get('limit_up_count', 0)} | 跌停: {data.get('dt_count', 0)}
最高: {summary.get('max_height', 0)}板

策略: {emotion['strategy']}
仓位: {emotion['suggested_position']}"""
