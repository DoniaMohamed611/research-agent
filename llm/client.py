import requests

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