def decision_agent(
    technical_signal: int,
    sentiment_score: float,
    risk_score: float
) -> int:
    """
    Multi-agent voting decision.

    Return:
    1 = buy / hold stock
    0 = stay in cash
    """

    # Risk Agent veto: high risk means no trading
    if risk_score >= 0.75:
        return 0

    votes = 0

    # Technical Analyst vote
    if technical_signal == 1:
        votes += 1
    elif technical_signal == -1:
        votes -= 1

    # Sentiment Analyst vote
    if sentiment_score >= 0.3:
        votes += 1
    elif sentiment_score <= -0.3:
        votes -= 1

    # Risk Analyst vote
    if risk_score <= 0.35:
        votes += 1
    elif risk_score >= 0.6:
        votes -= 1

    if votes >= 1:
        return 1
    else:
        return 0
    
#risk_score >= 0.75，直接空仓，风控一票否决。