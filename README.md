# 多智能体量化交易回测项目

本项目实现了一个面向股票交易策略研究的多智能体回测系统。系统以历史行情数据和新闻情绪数据为输入，结合技术分析、情绪分析、风险控制和交易决策模块，生成交易信号并完成回测评估，同时提供可视化结果和前端展示页面。

## 项目功能

- 读取本地股票历史行情数据和情绪数据
- 基于技术指标、情绪评分和风险约束生成交易决策
- 执行回测并输出资金曲线、回撤曲线、交易暴露和年度收益
- 对比不同情绪频率下的策略表现
- 生成可视化图片
- 提供 Streamlit 前端页面用于查看策略结果和图表
- 提供基础测试用例，覆盖情绪、风险、决策和环境配置等模块

## 目录结构

```text
.
├── agents/                         # 多智能体模块
│   ├── technical_agent.py           # 技术分析智能体
│   ├── sentiment_agent.py           # 情绪分析智能体
│   ├── risk_agent.py                # 风险控制智能体
│   └── decision_agent.py            # 交易决策智能体
├── data/                            # 输入数据
│   ├── AAPL.csv                     # 股票历史行情数据
│   ├── weekly_sentiment.csv         # 周度情绪数据
│   └── monthly_sentiment.csv        # 月度情绪数据
├── results/                         # 回测结果和可视化输出
├── test/                            # 测试用例
├── app.py                           # Streamlit 前端应用
├── main.py                          # 主回测入口
├── experiments.py                   # 策略实验与对比
├── backtest.py                      # 回测逻辑
├── data_loader.py                   # 行情数据读取
├── sentiment_loader.py              # 情绪数据读取
├── metrics.py                       # 指标计算
├── visualization.py                 # 回测图表生成
├── regenerate_visuals.py            # 重新生成报告可视化图片
├── generate_weekly_sentiment.py     # LLM推断周度情绪数据
├── generate_monthly_sentiment.py    # LLM推断月度情绪数据
└── plot_monthly_weekly_sentiment_comparison.py
```

## 环境准备

建议使用 Python 3.10 或以上版本。

安装常用依赖：

```bash
pip install pandas numpy matplotlib streamlit pytest
```

如果使用了大模型情绪分析或 DeepSeek 相关功能，还需要根据本地代码中的配置安装对应 SDK，并设置 API Key。

## 快速开始

1. 确认数据文件已放在 `data/` 目录下：

```text
data/AAPL.csv
data/weekly_sentiment.csv
data/monthly_sentiment.csv
```

2. 运行主回测：

```bash
python main.py
```

3. 运行实验对比：

```bash
python experiments.py
```

4. 启动前端页面：

```bash
streamlit run app.py
```

5. 重新生成报告图片：

```bash
python regenerate_visuals.py
```

生成的结果会保存到 `results/` 目录中。

## 输出结果

项目运行后通常会生成以下结果文件：

```text
results/backtest_results.csv
results/metrics.csv
results/annual_returns.csv
results/equity_curve.png
results/drawdown_curve.png
results/exposure_trades.png
results/annual_returns.png
results/metrics_comparison.png
results/monthly_weekly_sentiment_risk_comparison.png
results/sentiment_risk_scores.png
```

其中：

- `backtest_results.csv` 保存逐日回测结果
- `metrics.csv` 保存累计收益、年化收益、最大回撤等评价指标
- `annual_returns.csv` 保存年度收益统计
- `.png` 文件用于报告、论文和前端展示

## 测试

运行全部测试：

```bash
pytest
```

也可以运行单个测试文件：

```bash
pytest test/test_risk.py
pytest test/test_sentiment.py
pytest test/test_decision.py
```

## 核心思路

本项目将交易策略拆分为多个职责清晰的智能体：

- 技术分析智能体负责从价格和成交量数据中提取市场信号
- 情绪分析智能体负责读取或生成新闻情绪评分
- 风险控制智能体负责限制仓位、回撤和异常风险
- 决策智能体综合各类信号生成买入、卖出或持有动作

这种结构便于单独调整某一类信号，也便于在实验中比较不同数据频率、风险参数或决策规则对策略表现的影响。

## 注意事项

- 当前示例数据以 `AAPL` 为主，切换标的时需要同步替换行情数据和情绪数据。
- 运行前端前，请先执行回测或确认 `results/` 中已有结果文件。
- 生成情绪数据的脚本可能依赖外部 API，运行前需要确认网络和密钥配置。
- 回测结果仅用于课程实验和策略研究，不构成任何投资建议。
