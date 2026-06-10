from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = BASE_DIR / "results"
OUT = RESULTS_DIR / "monthly_weekly_sentiment_risk_comparison.png"


def setup_font():
    for path in [
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simhei.ttf"),
        Path("C:/Windows/Fonts/simsun.ttc"),
    ]:
        if path.exists():
            matplotlib.font_manager.fontManager.addfont(str(path))
            prop = matplotlib.font_manager.FontProperties(fname=str(path))
            plt.rcParams["font.family"] = prop.get_name()
            break
    plt.rcParams["axes.unicode_minus"] = False


def load_data():
    monthly = pd.read_csv(DATA_DIR / "monthly_sentiment.csv")
    monthly["date"] = pd.to_datetime(monthly["month"] + "-01")

    weekly = pd.read_csv(DATA_DIR / "weekly_sentiment.csv")
    weekly["date"] = pd.to_datetime(weekly["week_start"])

    start = pd.Timestamp("2021-08-01")
    end = pd.Timestamp("2024-12-31")
    monthly = monthly[(monthly["date"] >= start) & (monthly["date"] <= end)]
    weekly = weekly[(weekly["date"] >= start) & (weekly["date"] <= end)]
    return monthly, weekly


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    setup_font()
    monthly, weekly = load_data()

    fig, axes = plt.subplots(2, 1, figsize=(14, 7.6), sharex=True)

    axes[0].plot(
        weekly["date"],
        weekly["sentiment_score"],
        color="#2F5597",
        linewidth=1.25,
        alpha=0.78,
        label="周度 sentiment_score",
    )
    axes[0].step(
        monthly["date"],
        monthly["sentiment_score"],
        where="post",
        color="#F28E2B",
        linewidth=2.2,
        label="月度 sentiment_score",
    )
    axes[0].axhline(0, color="#333333", linewidth=0.9)
    axes[0].set_ylabel("情绪分数")
    axes[0].set_title("月度与周度情绪评分对比")
    axes[0].grid(axis="y", alpha=0.25)
    axes[0].legend(frameon=False, ncol=2, loc="upper left")

    axes[1].plot(
        weekly["date"],
        weekly["risk_score"],
        color="#2F5597",
        linewidth=1.25,
        alpha=0.78,
        label="周度 risk_score",
    )
    axes[1].step(
        monthly["date"],
        monthly["risk_score"],
        where="post",
        color="#F28E2B",
        linewidth=2.2,
        label="月度 risk_score",
    )
    axes[1].axhline(0.75, color="#B42318", linestyle="--", linewidth=1.2, label="风险阈值 0.75")
    axes[1].set_ylabel("风险分数")
    axes[1].set_title("月度与周度风险评分对比")
    axes[1].grid(axis="y", alpha=0.25)
    axes[1].legend(frameon=False, ncol=3, loc="upper left")

    fig.suptitle("月度情绪/风险评分与周度情绪/风险评分对比（2021-08 至 2024-12）", fontsize=16, fontweight="bold")
    axes[1].set_xlabel("日期")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(OUT, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(OUT)


if __name__ == "__main__":
    main()
