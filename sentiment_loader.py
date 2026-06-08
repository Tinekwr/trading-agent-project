import pandas as pd


def add_weekly_sentiment(df: pd.DataFrame, sentiment_file: str) -> pd.DataFrame:
    df = df.copy()

    sentiment_df = pd.read_csv(sentiment_file)

    sentiment_df["week_start"] = pd.to_datetime(sentiment_df["week_start"])

    sentiment_map = sentiment_df.set_index("week_start")[
        ["sentiment_score", "risk_score"]
    ]

    # 当前交易日所在周的周一
    cdate_index = pd.DatetimeIndex(df.index)
    current_week_start = (
        cdate_index.to_period("W")
        .to_timestamp()
    )
    # 使用上一周情绪，避免未来函数
    df["prev_week_start"] = current_week_start - pd.Timedelta(days=7)

    df["sentiment_score"] = df["prev_week_start"].map(
        sentiment_map["sentiment_score"]
    )

    df["risk_score"] = df["prev_week_start"].map(
        sentiment_map["risk_score"]
    )

    df["sentiment_score"] = df["sentiment_score"].fillna(0.0)
    df["risk_score"] = df["risk_score"].fillna(0.5)

    df.drop(columns=["prev_week_start"], inplace=True)

    return df