from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from visualization import plot_drawdown_curves, plot_equity_curves


BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"

STRATEGY_COLS = {
    "Buy and Hold": {
        "curve": "buy_hold_curve",
        "return": "buy_hold_return",
        "position": None,
        "color": "#4E79A7",
    },
    "Technical Only": {
        "curve": "technical_curve",
        "return": "technical_return",
        "position": "technical_position",
        "color": "#E15759",
    },
    "Technical + Sentiment": {
        "curve": "tech_sent_curve",
        "return": "tech_sent_return",
        "position": "tech_sent_position",
        "color": "#59A14F",
    },
    "Long-Biased Multi-Agent": {
        "curve": "multi_agent_curve",
        "return": "multi_agent_return",
        "position": "multi_agent_position",
        "color": "#F28E2B",
    },
}


def setup_style():
    font_candidates = [
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simhei.ttf"),
        Path("C:/Windows/Fonts/simsun.ttc"),
    ]
    for font in font_candidates:
        if font.exists():
            matplotlib.font_manager.fontManager.addfont(str(font))
            prop = matplotlib.font_manager.FontProperties(fname=str(font))
            plt.rcParams["font.family"] = prop.get_name()
            break
    plt.rcParams["axes.unicode_minus"] = False


def load_backtest():
    df = pd.read_csv(RESULTS_DIR / "backtest_results.csv")
    if "Date" not in df.columns:
        first = df.columns[0]
        df = df.rename(columns={first: "Date"})
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.set_index("Date")
    return df


def make_annual_returns(df):
    rows = []
    for year, group in df.groupby(df.index.year):
        row = {"Date": year}
        for name, cols in STRATEGY_COLS.items():
            out_name = "Buy & Hold" if name == "Buy and Hold" else (
                "Tech + Sentiment" if name == "Technical + Sentiment" else name
            )
            row[out_name] = (1 + group[cols["return"]]).prod() - 1
        rows.append(row)
    annual_df = pd.DataFrame(rows)
    annual_df.to_csv(RESULTS_DIR / "annual_returns.csv", index=False)
    return annual_df


def plot_annual_returns(annual_df):
    out = RESULTS_DIR / "annual_returns.png"
    cols = ["Buy & Hold", "Technical Only", "Tech + Sentiment", "Long-Biased Multi-Agent"]
    colors = ["#4E79A7", "#E15759", "#59A14F", "#F28E2B"]
    x = range(len(annual_df))
    width = 0.18

    fig, ax = plt.subplots(figsize=(11, 5.6))
    for i, (col, color) in enumerate(zip(cols, colors)):
        values = annual_df[col] * 100
        ax.bar([v + (i - 1.5) * width for v in x], values, width=width, label=col, color=color)

    ax.axhline(0, color="#333333", linewidth=1)
    ax.set_xticks(list(x))
    ax.set_xticklabels(annual_df["Date"].astype(str))
    ax.set_ylabel("Annual Return (%)")
    ax.set_title("Annual Returns by Strategy")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(ncol=2, frameon=False)
    fig.tight_layout()
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return out


def plot_metrics_comparison(metrics_df):
    out = RESULTS_DIR / "metrics_comparison.png"
    rows = list(STRATEGY_COLS)
    specs = [
        ("Cumulative Return", "Cumulative Return", lambda x: x * 100, "%"),
        ("Sharpe Ratio", "Sharpe Ratio", lambda x: x, ""),
        ("Max Drawdown", "Max Drawdown", lambda x: x * 100, "%"),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.8))
    for ax, (col, title, transform, suffix) in zip(axes, specs):
        values = [transform(metrics_df.loc[row, col]) for row in rows]
        colors = [STRATEGY_COLS[row]["color"] for row in rows]
        bars = ax.bar(rows, values, color=colors, width=0.62)
        ax.set_title(title)
        ax.grid(axis="y", alpha=0.25)
        ax.tick_params(axis="x", rotation=22)
        for bar, value in zip(bars, values):
            label = f"{value:.2f}{suffix}" if suffix else f"{value:.3f}"
            offset = max(abs(max(values) - min(values)), 1) * 0.025
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                value + (offset if value >= 0 else -offset),
                label,
                ha="center",
                va="bottom" if value >= 0 else "top",
                fontsize=9,
            )
    fig.suptitle("Core Metrics Comparison")
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return out


def plot_exposure_trades(df):
    out = RESULTS_DIR / "exposure_trades.png"
    rows = ["Technical Only", "Technical + Sentiment", "Long-Biased Multi-Agent"]
    exposures = []
    trades = []
    for name in rows:
        pos = df[STRATEGY_COLS[name]["position"]]
        exposures.append(pos.mean() * 100)
        trades.append(int((pos.diff().fillna(0) != 0).sum()))

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    colors = [STRATEGY_COLS[row]["color"] for row in rows]
    axes[0].bar(rows, exposures, color=colors)
    axes[0].set_title("Average Exposure")
    axes[0].set_ylabel("Exposure (%)")
    axes[0].set_ylim(0, 100)
    axes[0].grid(axis="y", alpha=0.25)
    axes[1].bar(rows, trades, color=colors)
    axes[1].set_title("Number of Position Changes")
    axes[1].grid(axis="y", alpha=0.25)
    for ax in axes:
        ax.tick_params(axis="x", rotation=18)
    for ax, values in zip(axes, [exposures, trades]):
        for patch, value in zip(ax.patches, values):
            label = f"{value:.1f}%" if ax is axes[0] else f"{value}"
            ax.text(patch.get_x() + patch.get_width() / 2, patch.get_height(), label, ha="center", va="bottom")
    fig.tight_layout()
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return out


def plot_sentiment_risk(df):
    out = RESULTS_DIR / "sentiment_risk_scores.png"
    weekly = df[["sentiment_score", "risk_score"]].resample("W-FRI").last().dropna(how="all")
    colors = ["#59A14F" if value >= 0 else "#E15759" for value in weekly["sentiment_score"]]

    fig, axes = plt.subplots(2, 1, figsize=(12, 6.5), sharex=True)
    axes[0].bar(weekly.index, weekly["sentiment_score"], color=colors, width=5)
    axes[0].axhline(0, color="#333333", linewidth=0.9)
    axes[0].set_title("Weekly Sentiment Score")
    axes[0].grid(axis="y", alpha=0.25)

    axes[1].fill_between(weekly.index, weekly["risk_score"], color="#4E79A7", alpha=0.35)
    axes[1].plot(weekly.index, weekly["risk_score"], color="#4E79A7")
    axes[1].axhline(0.75, color="#B42318", linestyle="--", linewidth=1.2, label="Risk threshold 0.75")
    axes[1].set_title("Weekly Risk Score")
    axes[1].grid(axis="y", alpha=0.25)
    axes[1].legend(frameon=False)

    fig.tight_layout()
    fig.savefig(out, dpi=300)
    plt.close(fig)
    return out


def regenerate_report_assets():
    import build_report

    _metrics_df, _annual_df, assets = build_report.make_assets()
    return list(assets.values())


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    setup_style()
    df = load_backtest()
    metrics_df = pd.read_csv(RESULTS_DIR / "metrics.csv", index_col=0)

    plot_equity_curves(df)
    plot_drawdown_curves(df)
    annual_df = make_annual_returns(df)

    outputs = [
        plot_annual_returns(annual_df),
        plot_metrics_comparison(metrics_df),
        plot_exposure_trades(df),
        plot_sentiment_risk(df),
    ]
    outputs.extend(regenerate_report_assets())

    print("Regenerated visuals:")
    for path in [
        RESULTS_DIR / "equity_curve.png",
        RESULTS_DIR / "drawdown_curve.png",
        *outputs,
    ]:
        print(path)


if __name__ == "__main__":
    main()
