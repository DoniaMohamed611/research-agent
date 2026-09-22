import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

LLM_URL = "http://127.0.0.1:1234/v1/chat/completions"
MODEL_NAME = "qwen/qwen3-8b"


def ask_llm(prompt, temperature=0.7):
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature
    }
    response = requests.post(LLM_URL, json=payload)
    data = response.json()

    if "choices" not in data:
        print("Warning: LLM server returned an unexpected response:")
        print(data)
        return None

    return data["choices"][0]["message"]["content"]


def load_rules(filename):
    with open(f"config/{filename}", "r", encoding="utf-8") as f:
        return f.read()
        




OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "openrouter/free"


def ask_llm_cloud(prompt, temperature=0.7):
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        print("Warning: OPENROUTER_API_KEY not found in .env file.")
        return None

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    max_retries = 3
    for attempt in range(1, max_retries + 1):
        response = requests.post(OPENROUTER_URL, json=payload, headers=headers)
        data = response.json()

        if "choices" in data:
            return data["choices"][0]["message"]["content"]

        error_code = data.get("error", {}).get("code")
        if error_code == 429 and attempt < max_retries:
            wait_time = 10 * attempt
            print(f"Rate limited by OpenRouter. Retrying in {wait_time}s (attempt {attempt}/{max_retries})...")
            time.sleep(wait_time)
        else:
            print("Warning: OpenRouter returned an unexpected response:")
            print(data)
            return None

    return None