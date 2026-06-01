import pandas as pd


def add_monthly_sentiment(df: pd.DataFrame, sentiment_file: str) -> pd.DataFrame:
    df = df.copy()

    # 读取情绪文件并建立映射字典
    sentiment_df = pd.read_csv(sentiment_file)
    sentiment_df["month"] = sentiment_df["month"].astype(str)

    sentiment_map = sentiment_df.set_index("month")[
        ["sentiment_score", "risk_score"]
    ]

    # 【核心修改】：获取当前日期的“上一个月”，消除未来函数
    df["prev_month"] = (df.index.to_period("M") - 1).astype(str)

    # 使用 prev_month 来匹配情绪分数
    df["sentiment_score"] = df["prev_month"].map(
        sentiment_map["sentiment_score"]
    )

    df["risk_score"] = df["prev_month"].map(
        sentiment_map["risk_score"]
    )

    # 填充缺失值（比如最开始的月份可能没有上个月的数据）
    df["sentiment_score"] = df["sentiment_score"].fillna(0.0)
    df["risk_score"] = df["risk_score"].fillna(0.5)
    
    # 删掉用完的辅助列，保持数据干净
    df.drop(columns=["prev_month"], inplace=True)

    return df