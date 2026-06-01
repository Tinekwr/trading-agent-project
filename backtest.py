import pandas as pd

from agents.decision_agent import decision_agent
from agents.risk_agent import risk_agent


def run_backtest(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # 将第一天的 NaN 收益率填充为 0，防止后续相乘出现 NaN 导致计算中断
    df["daily_return"] = df["Close"].pct_change().fillna(0)

    positions = []
    strategy_returns = []
    equity_curve = []

    equity = 1.0
    peak = 1.0
    prev_position = 0  

    for i in range(len(df)):
        row = df.iloc[i]

        # 1. 先用【昨天】的仓位，计算【今天】的实际交易收益并更新资金曲线
        daily_return = row["daily_return"]
        strategy_return = prev_position * daily_return

        equity = equity * (1 + strategy_return)
        peak = max(peak, equity)

        # 2. 基于今天收盘更新后的资金曲线，计算最新的实时风险回撤
        current_drawdown = (equity - peak) / peak if peak > 0 else 0

        # 3. 根据今天的市场数据，由智能体决策出【明天】该使用的仓位
        raw_position = decision_agent(
            technical_signal=row["technical_signal"],
            sentiment_score=row["sentiment_score"],
            risk_score=row["risk_score"]
        )

        final_position = risk_agent(
            raw_position=raw_position,
            current_drawdown=current_drawdown
        )

        # 4. 记录当天的各项量化结果
        positions.append(final_position)
        strategy_returns.append(strategy_return)
        equity_curve.append(equity)

        # 5. 【核心步骤】将今天的仓位留存，作为明天的“昨日仓位”进下一轮循环
        prev_position = final_position

    df["position"] = positions
    df["strategy_return"] = strategy_returns
    df["equity_curve"] = equity_curve
    df["buy_hold_curve"] = (1 + df["daily_return"]).cumprod()

    return df