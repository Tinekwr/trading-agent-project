from agents.sentiment_agent import sentiment_agent


news = "Apple reports stronger-than-expected quarterly earnings and raises revenue guidance."

result = sentiment_agent(news)

print(result)