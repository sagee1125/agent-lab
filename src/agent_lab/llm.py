import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

MODEL = "deepseek-flash"

client = AsyncOpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)


async def chat(user_text: str) -> str:
    messages = [
        {"role": "system", "content": "你是一個簡潔的助理，回答盡量精簡。"},
        {"role": "user", "content": user_text},
    ]
    resp = await client.chat.completions.create(model=MODEL, messages=messages)
    return resp.choices[0].message.content or ""
