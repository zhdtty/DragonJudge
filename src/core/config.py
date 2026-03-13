"""核心配置模块"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用信息
    APP_NAME: str = "DragonJudge"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # 数据更新间隔（秒）
    DATA_FETCH_INTERVAL: int = 300  # 5分钟
    
    # 数据库
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/dragonjudge.db")
    
    # 日志
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = "./logs/dragonjudge.log"
    
    # Dragon Judge 评分权重
    WEIGHT_HEIGHT: float = 0.40        # 连板高度
    WEIGHT_COMPETITION: float = 0.30   # 卡位竞争
    WEIGHT_SECTOR: float = 0.20        # 板块助攻
    WEIGHT_EMOTION: float = 0.05       # 市场情绪
    WEIGHT_QUALITY: float = 0.05       # 封板质量
    
    # 情绪周期阈值
    EMOTION_EXTREME_FEAR: float = 20   # 冰点
    EMOTION_FEAR: float = 40           # 恐惧
    EMOTION_NEUTRAL: float = 60        # 中性
    EMOTION_GREED: float = 80          # 贪婪
    EMOTION_EXTREME_GREED: float = 100 # 极度贪婪
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 全局配置实例
settings = Settings()
