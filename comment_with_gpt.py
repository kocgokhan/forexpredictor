import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def gpt_comment(history: list, result: dict) -> str:
    prompt = f"""
Son 7 gün USD/TRY verisi: {history}
Tahmin: {result['predicted']} TL, Band: {result['band']}, Yön: {result['direction']}
MAE: {result['metrics']['mae']}
Kullanıcıya anlaşılır 2-3 cümlelik yorum yaz.
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"GPT yorum üretilemedi: {e}"