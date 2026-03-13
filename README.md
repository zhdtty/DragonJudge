# DragonJudge 🐉

A股情绪龙头助手 - 智能分析系统

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://img.shields.io/badge/tests-13%20passed-green.svg)]()

## 核心功能

- 📊 情绪周期判断（冰点/启动/发酵/高潮/分化/退潮）
- 📈 涨停梯队追踪（连板高度、晋级率）
- 🎯 Dragon Judge 评分系统（5维度评分）
- 📋 每日复盘报告（情绪+梯队+明日策略）
- 🔔 实时预警（龙头断板、新主线启动）

## 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/zhdtty/DragonJudge.git
cd DragonJudge

# 2. 安装依赖
poetry install

# 3. 运行
poetry run python dragonjudge.py --fetch

# 或使用 Docker
docker-compose up
```

## 项目结构

```
DragonJudge/
├── src/
│   ├── core/          # 配置、日志
│   ├── data/          # 数据抓取
│   ├── analysis/      # 分析算法
│   └── main.py        # 入口
├── tests/             # 单元测试
├── docker-compose.yml # Docker部署
└── README.md
```

## 技术栈

- **Python 3.11+** - 核心语言
- **Poetry** - 依赖管理
- **aiohttp** - 异步HTTP
- **pytest** - 测试框架
- **Docker** - 容器化部署

## 开发进度

- [x] 项目初始化
- [x] Dragon Judge 评分算法
- [x] 情绪周期分析
- [x] 数据抓取模块
- [x] 报告生成
- [x] Docker部署
- [x] 单元测试
- [ ] Telegram Bot推送
- [ ] 定时任务
- [ ] 历史数据存储

## 团队

- 📈 @交易策略 - 产品负责人+核心算法
- 🐱👤 @数据采集 - 数据工程师  
- 🫡 @工程助理 - 技术架构师
- 🪙 @数据货币 - 项目经理+商业化
- 🦞 @代码检查 - 质量保障

## 许可证

MIT
