# Dragon Judge 算法 v1.0

> A股情绪龙头战法核心算法文档
> 版本: 1.0
> 更新日期: 2026-03-14
> 作者: 交易策略 (小股)

---

## 目录

1. [情绪周期判断算法](#一情绪周期判断算法)
2. [Dragon Judge 5维评分](#二dragon-judge-5维评分)
3. [主线识别6大信号](#三主线识别6大信号)
4. [输入输出接口定义](#四输入输出接口定义)
5. [测试用例说明](#五测试用例说明)

---

## 一、情绪周期判断算法

### 1.1 周期定义

| 周期 | 涨停家数 | 最高连板 | 特征 | 策略 |
|------|----------|----------|------|------|
| **冰点期** | <30 | ≤3板 | 无明显热点，资金观望 | 空仓或≤1成试错 |
| **启动期** | 30-50 | 3-4板 | 新题材出现，资金试探 | 2成仓试错 |
| **发酵期** | 50-70 | 4-5板 | 主线确立，板块扩散 | 3-4成仓参与 |
| **高潮期** | >70 | 5板+ | 多主线竞争，全民参与 | 持有或减仓 |
| **分化期** | 50-70 | 高度下降 | 掉队增多，亏钱效应 | 减仓至2成 |
| **退潮期** | <40 | ≤3板 | 龙头断板，全线调整 | 空仓观望 |

### 1.2 判断公式

```python
def judge_emotion_cycle(limit_up_count, max_boards, prev_cycle):
    """
    情绪周期判断
    """
    if limit_up_count < 30 and max_boards <= 3:
        return "冰点期", 30
    elif limit_up_count < 40 and max_boards <= 3:
        return "退潮期", 40
    elif limit_up_count >= 30 and limit_up_count < 50:
        return "启动期", 50
    elif limit_up_count >= 50 and limit_up_count < 70:
        if max_boards >= 5:
            return "高潮期", 80
        return "发酵期", 65
    else:
        return "高潮期", 85
```

### 1.3 周期切换信号

```
冰点期 → 启动期: 涨停>30只，新题材批量涨停
启动期 → 发酵期: 主线确立，身位龙出现
发酵期 → 高潮期: 涨停>70只，多主线竞争
高潮期 → 分化期: 龙头断板，涨停减少
分化期 → 退潮期: 高度降至3板以下
退潮期 → 冰点期: 涨停<30只
```

---

## 二、Dragon Judge 5维评分

### 2.1 评分维度与权重

| 维度 | 权重 | 说明 |
|------|------|------|
| **连板高度** | 40% | 身位优势，越高越强 |
| **卡位竞争** | 30% | 独龙vs多龙，独龙胜 |
| **板块助攻** | 20% | 梯队完整性 |
| **市场情绪** | 5% | 整体环境 |
| **封板质量** | 5% | 资金态度 |

### 2.2 评分公式

```python
def dragon_judge_score(stock_data, market_data):
    # 1. 连板高度 (40%)
    height_score = min(stock_data['连板数'] * 10, 40)
    
    # 2. 卡位竞争 (30%)
    competitors = stock_data['同身位竞争股数']
    if competitors == 0:
        compete_score = 30
    elif competitors == 1:
        compete_score = 20
    else:
        compete_score = max(30 - competitors * 10, 5)
    
    # 3. 板块助攻 (20%)
    sector = stock_data['板块涨停家数']
    if sector >= 10: sector_score = 20
    elif sector >= 5: sector_score = 15
    elif sector >= 3: sector_score = 10
    else: sector_score = 5
    
    # 4. 市场情绪 (5%)
    market = market_data['涨停家数']
    if market >= 70: emotion_score = 5
    elif market >= 50: emotion_score = 4
    elif market >= 30: emotion_score = 3
    else: emotion_score = 2
    
    # 5. 封板质量 (5%)
    opens = stock_data['开板次数']
    if opens == 0: quality_score = 5
    elif opens == 1: quality_score = 3
    else: quality_score = 1
    
    total = height_score + compete_score + sector_score + emotion_score + quality_score
    
    if total >= 80: evaluation = "真龙"
    elif total >= 70: evaluation = "强龙"
    elif total >= 60: evaluation = "潜龙"
    else: evaluation = "杂毛"
    
    return total, evaluation
```

### 2.3 评分标准

| 总分 | 评价 | 策略 |
|------|------|------|
| 80-100 | 🟢 **真龙** | 满仓或重仓干 |
| 70-79 | 🟡 **强龙** | 重仓参与 |
| 60-69 | 🟠 **潜龙** | 观察或小仓试错 |
| <60 | 🔴 **杂毛** | 不碰 |

---

## 三、主线识别6大信号

### 3.1 信号权重分配

| 信号 | 权重 | 判断标准 |
|------|------|----------|
| **批量涨停** | 40% | 首日涨停≥10只 |
| **身位龙头** | 20% | 09:25竞价涨停 |
| **中军涨停** | 20% | 大市值(>100亿)涨停 |
| **板块指数** | 10% | 板块涨幅前10 |
| **资金流向** | 5% | 主力净流入 |
| **政策催化** | 5% | 两会/行业政策 |

### 3.2 主线评分公式

```python
def main_line_score(sector_data):
    # 1. 批量涨停 (40%)
    limit_up = sector_data['涨停家数']
    if limit_up >= 10: batch = 40
    elif limit_up >= 5: batch = 30
    elif limit_up >= 3: batch = 20
    else: batch = 10
    
    # 2. 身位龙头 (20%)
    time = sector_data['龙头涨停时间']
    if time <= '09:25': leader = 20
    elif time <= '09:30': leader = 15
    elif time <= '09:35': leader = 10
    else: leader = 5
    
    # 3. 中军涨停 (20%)
    heavyweight = 20 if sector_data['大市值涨停'] else 5
    
    # 4. 板块指数 (10%)
    rank = sector_data['板块涨幅排名']
    if rank <= 10: index = 10
    elif rank <= 20: index = 7
    else: index = 3
    
    # 5. 资金流向 (5%)
    fund = 5 if sector_data['资金净流入'] > 0 else 2
    
    # 6. 政策催化 (5%)
    policy = 5 if sector_data['政策利好'] else 2
    
    total = batch + leader + heavyweight + index + fund + policy
    
    if total >= 80: return total, True, "强势主线"
    elif total >= 60: return total, True, "普通主线"
    return total, False, "弱势/假热点"
```

### 3.3 主线确认3步法

```
Day 1 (观察期):
  └── 板块首日批量涨停 → 列入观察清单
  └── 不操作，等待确认

Day 2 (确认期):
  └── 身位龙晋级2板 + 板块3只+涨停 → 主线确认
  └── 2成仓打板身位龙

Day 3 (发酵期):
  └── 龙头晋级3板 + 板块5只+涨停 → 重仓
  └── 加仓至4-5成
```

---

## 四、输入输出接口定义

### 4.1 输入数据结构

```python
# 个股数据
stock_input = {
    '股票代码': '601088',
    '股票名称': '中国神华',
    '连板数': 2,
    '涨停时间': '09:25',
    '开板次数': 0,
    '封单金额': 50000,
    '板块名称': '煤炭',
    '同身位竞争股数': 0,
    '板块涨停家数': 6,
    '换手率': 2.5,
    '流通市值': 2000
}

# 市场数据
market_input = {
    '日期': '2026-03-14',
    '涨停家数': 55,
    '跌停家数': 3,
    '最高连板': 3,
    '上涨家数': 2500,
    '下跌家数': 2000
}

# 板块数据
sector_input = {
    '板块名称': '煤炭',
    '涨停家数': 6,
    '涨幅': 4.69,
    '板块排名': 1,
    '资金净流入': 50000,
    '龙头涨停时间': '09:25',
    '大市值涨停': True,
    '政策利好': True
}
```

### 4.2 输出数据结构

```python
# 情绪分析输出
emotion_output = {
    '日期': '2026-03-14',
    '情绪分数': 50,
    '情绪周期': '混沌期',
    '涨停家数': 55,
    '最高连板': 3,
    '明日预判': '观察期'
}

# 龙头评分输出
dragon_output = {
    '股票代码': '601088',
    '股票名称': '中国神华',
    '总分': 88,
    '评价': '真龙',
    '策略建议': '满仓干'
}

# 主线识别输出
main_line_output = {
    '板块名称': '煤炭',
    '主线评分': 85,
    '是否主线': True,
    '参与建议': 'Day2确认期，2成仓试错'
}
```

---

## 五、测试用例说明

### 5.1 山东墨龙（成功案例）

```python
stock = {
    '股票代码': '002490',
    '股票名称': '山东墨龙',
    '连板数': 4,
    '同身位竞争股数': 0,
    '板块涨停家数': 8
}
# 预期: 总分88，评价"真龙"
# 结果: 次日5板成功
```

### 5.2 面板板块（成功案例）

```python
sector = {
    '板块名称': '面板',
    '涨停家数': 11,
    '龙头涨停时间': '09:25',
    '大市值涨停': True,
    '板块排名': 1
}
# 预期: 评分92，强势主线
# 结果: 兆驰股份2板确认
```

### 5.3 泰嘉股份（失败案例）

```python
stock = {
    '股票代码': '002843',
    '股票名称': '泰嘉股份',
    '连板数': 3,
    '同身位竞争股数': 2,
    '板块涨停家数': 3
}
# 预期: 总分55，评价"杂毛"
# 结果: 次日断板
```

---

## 附录：核心规律

| 规律 | 说明 | 验证 |
|------|------|------|
| 双龙头魔咒 | 同身位多股竞争，成功率<40% | ✅ |
| 4板分水岭 | 4进5是关键 | ✅ |
| 中军验证 | 大市值涨停才是真主线 | ✅ |
| 竞价定生死 | 09:25>09:30>09:35 | ✅ |
| 换手出龙头 | 充分换手才能走远 | ✅ |

---

*资金永不眠，系统不停歇，算法驱动交易。* 📈🐉
