import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
# Assumes GROQ_API_KEY is loaded in your environment variables
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
LLM_MODEL = "qwen/qwen3.8-27b"

def generate_answer(prompt: str) -> str:
    print("\n========== LLM RECEIVED ==========")
    print(prompt)
    print("==================================\n")
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content