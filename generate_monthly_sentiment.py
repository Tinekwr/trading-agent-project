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


def ask_deepseek_for_month(symbol: str, month: str) -> dict:
    prompt = f"""
You are a financial market analyst.

For the stock {symbol}, summarize the major company-specific and macroeconomic events
that likely affected its stock price during {month}.

Then analyze market sentiment and risk.

Return only valid JSON in this format:

{{
  "month": "{month}",
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

    content = response.choices[0].message.content

    if content is None:
        return {
            "month": month,
            "summary": "Empty response from DeepSeek.",
            "sentiment_score": 0.0,
            "risk_score": 0.5
        }

    try:
        return json.loads(content)

    except json.JSONDecodeError:
        return {
            "month": month,
            "summary": "Failed to parse DeepSeek response.",
            "sentiment_score": 0.0,
            "risk_score": 0.5
        }


def main():
    symbol = "AAPL"

    months = pd.period_range(
        start="2020-01",
        end="2024-12",
        freq="M"
    ).astype(str)

    results = []

    for month in months:
        print(f"Processing {month}...")

        result = ask_deepseek_for_month(symbol, month)
        results.append(result)

        time.sleep(1)

    df = pd.DataFrame(results)
    
   
    import os
    # 设置绝对路径
    target_dir = "/data/wanghl/xieyanbing/trading_agent_project(1)/trading_agent_project/data"
    # 确保文件夹存在，如果不存在会自动创建
    os.makedirs(target_dir, exist_ok=True)
    
    output_path = os.path.join(target_dir, "monthly_sentiment.csv")
    df.to_csv(output_path, index=False)


    print(f"Saved to {output_path}")
    print(df.head())


if __name__ == "__main__":
    main()