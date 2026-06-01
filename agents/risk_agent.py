def risk_agent(
    raw_position: int,
    current_drawdown: float,
    max_drawdown_limit: float = -0.10
) -> int:
    """
    Return:
    1 = hold stock
    0 = stay in cash

    If drawdown is lower than max_drawdown_limit,
    force position to 0.
    """

    if current_drawdown <= max_drawdown_limit:
        return 0

    return raw_position