import os
import json
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


def sentiment_agent(news_text: str) -> dict:
    prompt = f"""
You are a financial sentiment analysis agent.

Analyze the following financial news:

{news_text}

Return only JSON in this format:
{{
  "sentiment_score": 0.0,
  "risk_score": 0.0,
  "reason": "short explanation"
}}

Rules:
- sentiment_score ranges from -1 to 1
- -1 means very bearish
- 0 means neutral
- 1 means very bullish
- risk_score ranges from 0 to 1
- 0 means low risk
- 1 means high risk
"""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    content = response.choices[0].message.content

    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        result = {
            "sentiment_score": 0.0,
            "risk_score": 0.5,
            "reason": "Failed to parse LLM response."
        }

    return result