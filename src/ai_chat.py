import sys
import os
import json
import urllib.request
import urllib.error
import subprocess
import datetime

CONFIG_PATH = os.path.expanduser("~/vicious-cli/config/paths.json")
STATE_PATH = os.path.expanduser("~/vicious-cli/vicious_context.md")
LOG_PATH = os.path.expanduser("~/vicious-cli/logs/api_errors.log")

def log_error(error_message):
    """Appends API failures with timestamps to the error log."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_PATH, "a") as f:
        f.write(f"[{timestamp}] {error_message}\n")
    print(f"[Vicious Error Logged]: Check ~/vicious-cli/logs/api_errors.log")

def get_api_key():
    key = os.getenv("GEMINI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not key:
        err = "No API key found in environment variables (GEMINI_API_KEY)."
        print(f"[Vicious Error] {err}")
        log_error(err)
        sys.exit(1)
    return key

def query_gemini(prompt, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    context = ""
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, "r") as f:
            context = f.read()

    full_prompt = f"System Context:\n{context}\n\nUser Question:\n{prompt}" if context else prompt
    data = {"contents": [{"parts": [{"text": full_prompt}]}]}

    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode("utf-8"))
            return res["candidates"][0]["content"]["parts"][0]["text"]
    except urllib.error.HTTPError as e:
        err_msg = f"HTTP Error {e.code}: {e.reason}"
        log_error(err_msg)
        return None
    except urllib.error.URLError as e:
        err_msg = f"Network Connection Error: {e.reason}"
        log_error(err_msg)
        return None
    except Exception as e:
        err_msg = f"Unexpected Error: {str(e)}"
        log_error(err_msg)
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("[Vicious Usage]: ask 'your prompt here'")
        sys.exit(0)

    user_prompt = " ".join(sys.argv[1:])
    key = get_api_key()
    
    print("[Vicious] Querying AI...")
    response_text = query_gemini(user_prompt, key)

    if response_text:
        with open(STATE_PATH, "a") as f:
            f.write(f"\n\n## USER: {user_prompt}\n## AI:\n{response_text}\n")

        process = subprocess.Popen(["python", os.path.expanduser("~/vicious-cli/src/main.py")], stdin=subprocess.PIPE)
        process.communicate(input=response_text.encode("utf-8"))
