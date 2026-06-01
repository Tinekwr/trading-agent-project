import numpy as np
import pandas as pd


def calculate_metrics(returns: pd.Series) -> dict:
    returns = returns.dropna()

    cumulative_return = (1 + returns).prod() - 1
    annual_return = (1 + cumulative_return) ** (252 / len(returns)) - 1
    annual_volatility = returns.std() * np.sqrt(252)

    if annual_volatility == 0:
        sharpe_ratio = 0
    else:
        sharpe_ratio = annual_return / annual_volatility

    equity = (1 + returns).cumprod()
    peak = equity.cummax()
    drawdown = (equity - peak) / peak
    max_drawdown = drawdown.min()

    return {
        "Cumulative Return": cumulative_return,
        "Annual Return": annual_return,
        "Annual Volatility": annual_volatility,
        "Sharpe Ratio": sharpe_ratio,
        "Max Drawdown": max_drawdown
    }