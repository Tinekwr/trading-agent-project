from agents.decision_agent import decision_agent


position = decision_agent(
    technical_signal=1,
    sentiment_score=0.8,
    risk_score=0.2
)

print(position)