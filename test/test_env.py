from dotenv import load_dotenv
import os

load_dotenv()

print("API Key:")
print(os.getenv("DEEPSEEK_API_KEY"))