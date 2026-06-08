import pandas as pd
from agents.decision_agent import decision_agent
from agents.risk_agent import risk_agent


def run_strategy_experiments(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["daily_return"] = df["Close"].pct_change().fillna(0)

    # 1. Buy & Hold
    df["buy_hold_return"] = df["daily_return"]

    # 2. Technical Only
    df["technical_position"] = df["technical_signal"].apply(
        lambda x: 1 if x == 1 else 0
    )
    df["technical_return"] = (
        df["technical_position"].shift(1).fillna(0)
        * df["daily_return"]
    )

    # 3. Technical + Sentiment
    df["tech_sent_position"] = df.apply(
        lambda row: 1
        if row["technical_signal"] == 1 and row["sentiment_score"] >= 0
        else 0,
        axis=1
    )
    df["tech_sent_return"] = (
        df["tech_sent_position"].shift(1).fillna(0)
        * df["daily_return"]
    )

    # 4. Long-Biased Multi-Agent
    positions = []
    equity = 1.0
    prev_position = 0
    equity_history = []

    for i in range(len(df)):
        row = df.iloc[i]

        # Use yesterday's position to calculate today's realizable return.
        strategy_return = prev_position * row["daily_return"]
        equity = equity * (1 + strategy_return)
        equity_history.append(equity)

        # Calculate rolling drawdown from the recent 60-day equity peak.
        rolling_window = 60
        recent_peak = max(equity_history[-rolling_window:])
        current_drawdown = (equity - recent_peak) / recent_peak if recent_peak > 0 else 0

        # Use today's close-based signals to decide tomorrow's position.
        raw_position = decision_agent(
            technical_signal=row["technical_signal"],
            sentiment_score=row["sentiment_score"],
            risk_score=row["risk_score"]
        )

        if row["risk_score"] > 0.8 and row["technical_signal"] == -1:
            final_position = 0
        else:
            final_position = risk_agent(
                raw_position=raw_position,
                current_drawdown=current_drawdown
            )

        positions.append(final_position)
        prev_position = final_position

    df["multi_agent_position"] = positions
    df["multi_agent_return"] = (
        df["multi_agent_position"].shift(1).fillna(0)
        * df["daily_return"]
    )

    df["buy_hold_curve"] = (1 + df["buy_hold_return"]).cumprod()
    df["technical_curve"] = (1 + df["technical_return"]).cumprod()
    df["tech_sent_curve"] = (1 + df["tech_sent_return"]).cumprod()
    df["multi_agent_curve"] = (1 + df["multi_agent_return"]).cumprod()

    return df
