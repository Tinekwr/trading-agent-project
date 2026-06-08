def decision_agent(
    technical_signal: int,
    sentiment_score: float,
    risk_score: float
) -> int:
    """
    Long-biased multi-agent risk-filter decision.

    Return:
    1 = buy / hold stock
    0 = stay in cash
    """

    # Risk Agent veto: high risk means no trading.
    if risk_score >= 0.75:
        return 0

    # For a long-term stock like AAPL, use sentiment as a confirmation filter:
    # stay invested by default and exit only when price trend and monthly
    # sentiment both turn negative.
    if technical_signal == -1 and sentiment_score <= -0.3:
        return 0

    return 1
