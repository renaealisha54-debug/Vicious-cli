import os
import json
from openai import OpenAI

# Path to persistent local settings
CONFIG_FILE = os.path.expanduser("~/vicious-cli/config/settings.json")
HISTORY_FILE = os.path.expanduser("~/vicious-cli/config/history.json")

def load_settings():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"provider": "groq", "model": "openai/gpt-oss-120b"}

def load_history(limit=5):
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            data = json.load(f)
            return data[-limit:]
    return []

def save_history(user_prompt, response_text):
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            try:
                history = json.load(f)
            except Exception:
                history = []
    history.append({"user": user_prompt, "assistant": response_text})
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def generate_ai_response(prompt):
    settings = load_settings()
    provider = settings.get("provider", "groq")
    history = load_history(limit=5)

    # Build conversation context stack
    messages = [
        {
            "role": "system",
            "content": (
                "You are VICIOUS, an automated CLI terminal bridge. "
                "You retain strict awareness of previous code and context."
            )
        }
    ]

    # Inject historical context
    for entry in history:
        messages.append({"role": "user", "content": entry["user"]})
        messages.append({"role": "assistant", "content": entry["assistant"]})

    messages.append({"role": "user", "content": prompt})

    try:
        if provider == "groq":
            client = OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=os.environ.get("GROQ_API_KEY")
            )
            model_name = settings.get("model", "openai/gpt-oss-120b")
        elif provider == "gemini":
            client = OpenAI(
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                api_key=os.environ.get("GEMINI_API_KEY")
            )
            model_name = settings.get("model", "gemini-2.5-flash")
        else:
            return None, f"Unsupported provider: {provider}"

        completion = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.2
        )
        response = completion.choices[0].message.content
        save_history(prompt, response)
        return response, None
    except Exception as e:
        return None, str(e)
