import pandas as pd
from pathlib import Path


def load_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    file_path = Path("data") / f"{symbol}.csv"

    if not file_path.exists():
        raise FileNotFoundError(f"Cannot find file: {file_path}")

    df = pd.read_csv(file_path)

    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)


    df.sort_index(inplace=True)

    for col in ["Close/Last", "Open", "High", "Low"]:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace("$", "", regex=False)
            .astype(float)
        )

    df.rename(columns={"Close/Last": "Close"}, inplace=True)

    df = df.loc[start_date:end_date]

    df = df[["Open", "High", "Low", "Close", "Volume"]]

    df["Volume"] = pd.to_numeric(df["Volume"], errors="coerce")
    df.dropna(inplace=True)

    return df