import os
import matplotlib.pyplot as plt

# 统一定义绝对路径
RESULTS_DIR = "/data/wanghl/xieyanbing/trading_agent_project(1)/trading_agent_project/results"

def plot_equity_curves(df):
    os.makedirs(RESULTS_DIR, exist_ok=True)

    plt.figure(figsize=(12, 6))

    plt.plot(df.index, df["buy_hold_curve"], label="Buy & Hold")
    plt.plot(df.index, df["technical_curve"], label="Technical Only")
    plt.plot(df.index, df["tech_sent_curve"], label="Technical + Sentiment")
    plt.plot(df.index, df["multi_agent_curve"], label="Full Multi-Agent")

    plt.title("Equity Curves")
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # 使用绝对路径保存
    plt.savefig(f"{RESULTS_DIR}/equity_curve.png", dpi=300)
    plt.show()


def plot_drawdown_curves(df):
    os.makedirs(RESULTS_DIR, exist_ok=True)

    def drawdown(curve):
        peak = curve.cummax()
        return (curve - peak) / peak

    plt.figure(figsize=(12, 6))

    plt.plot(df.index, drawdown(df["buy_hold_curve"]), label="Buy & Hold")
    plt.plot(df.index, drawdown(df["technical_curve"]), label="Technical Only")
    plt.plot(df.index, drawdown(df["tech_sent_curve"]), label="Technical + Sentiment")
    plt.plot(df.index, drawdown(df["multi_agent_curve"]), label="Full Multi-Agent")

    plt.title("Drawdown Curves")
    plt.xlabel("Date")
    plt.ylabel("Drawdown")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # 使用绝对路径保存
    plt.savefig(f"{RESULTS_DIR}/drawdown_curve.png", dpi=300)
    plt.show()