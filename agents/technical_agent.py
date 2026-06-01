import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD


def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["MA20"] = df["Close"].rolling(window=20).mean()
    df["MA60"] = df["Close"].rolling(window=60).mean()

    df["RSI"] = RSIIndicator(
        close=df["Close"],
        window=14
    ).rsi()

    macd = MACD(close=df["Close"])
    df["MACD"] = macd.macd()
    df["MACD_signal"] = macd.macd_signal()

    df.dropna(inplace=True)

    return df


def technical_agent(row) -> int:
    score = 0

    if row["MA20"] > row["MA60"]:
        score += 1
    else:
        score -= 1

    if row["RSI"] < 30:
        score += 1
    elif row["RSI"] > 70:
        score -= 1

    if row["MACD"] > row["MACD_signal"]:
        score += 1
    else:
        score -= 1

    if score > 0:
        return 1
    elif score < 0:
        return -1
    else:
        return 0