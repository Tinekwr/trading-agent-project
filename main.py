from data_loader import load_data
from agents.technical_agent import add_technical_indicators, technical_agent
from sentiment_loader import add_monthly_sentiment
from experiments import run_strategy_experiments
from metrics import calculate_metrics
from visualization import plot_equity_curves, plot_drawdown_curves
import pandas as pd


def main():

    df = load_data(
        "AAPL",
        "2020-01-01",
        "2024-12-31"
    )

    df = add_technical_indicators(df)

    df["technical_signal"] = df.apply(
        technical_agent,
        axis=1
    )

    df = add_monthly_sentiment(
        df,
        "/data/wanghl/xieyanbing/trading_agent_project(1)/trading_agent_project/data/monthly_sentiment.csv"
    )

    df = run_strategy_experiments(df)

    metrics_df = pd.DataFrame(
        [
            calculate_metrics(df["buy_hold_return"]),
            calculate_metrics(df["technical_return"]),
            calculate_metrics(df["tech_sent_return"]),
            calculate_metrics(df["multi_agent_return"])
        ],
        index=[
            "Buy and Hold",
            "Technical Only",
            "Technical + Sentiment",
            "Full Multi-Agent"
        ]
    )

    print(metrics_df)

    metrics_df.to_csv(
        "/data/wanghl/xieyanbing/trading_agent_project(1)/trading_agent_project/results/metrics.csv"
    )

    print()
    print("Metrics saved to results/metrics.csv")
    df.to_csv(
        "/data/wanghl/xieyanbing/trading_agent_project(1)/trading_agent_project/results/backtest_results.csv"
    )

    print()

    print(df[[
        "Close",
        "technical_signal",
        "sentiment_score",
        "risk_score",
        "technical_position",
        "tech_sent_position",
        "multi_agent_position"
    ]].tail())

    plot_equity_curves(df)
    plot_drawdown_curves(df)


if __name__ == "__main__":
    main()