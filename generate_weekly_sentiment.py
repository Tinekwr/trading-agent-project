import os
import json
import time
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


def ask_deepseek_for_week(symbol: str, week_start: str, week_end: str) -> dict:
    prompt = f"""
You are a financial market analyst.

For the stock {symbol}, summarize the major company-specific and macroeconomic events
that likely affected its stock price during this week:

Week start: {week_start}
Week end: {week_end}

Then analyze market sentiment and risk.

Return only valid JSON in this format:

{{
  "week_start": "{week_start}",
  "week_end": "{week_end}",
  "summary": "short summary of important events",
  "sentiment_score": 0.0,
  "risk_score": 0.0
}}

Rules:
- sentiment_score ranges from -1 to 1
- -1 means very bearish
- 0 means neutral
- 1 means very bullish
- risk_score ranges from 0 to 1
- 0 means very low risk
- 1 means very high risk
- Do not include markdown
- Do not include explanation outside JSON
"""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    content = response.choices[0].message.content

    if content is None:
        return {
            "week_start": week_start,
            "week_end": week_end,
            "summary": "Empty response from DeepSeek.",
            "sentiment_score": 0.0,
            "risk_score": 0.5
        }

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "week_start": week_start,
            "week_end": week_end,
            "summary": "Failed to parse DeepSeek response.",
            "sentiment_score": 0.0,
            "risk_score": 0.5
        }


def main():
    symbol = "AAPL"

    weeks = pd.date_range(
        start="2020-01-01",
        end="2024-12-31",
        freq="W-MON"
    )

    results = []

    for week_start in weeks:
        week_end = week_start + pd.Timedelta(days=6)

        week_start_str = week_start.strftime("%Y-%m-%d")
        week_end_str = week_end.strftime("%Y-%m-%d")

        print(f"Processing {week_start_str} to {week_end_str}...")

        result = ask_deepseek_for_week(
            symbol=symbol,
            week_start=week_start_str,
            week_end=week_end_str
        )

        results.append(result)

        time.sleep(1)

    df = pd.DataFrame(results)

    output_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, "weekly_sentiment.csv")
    df.to_csv(output_path, index=False)

    print(f"Saved to {output_path}")
    print(df.head())


if __name__ == "__main__":
    main()