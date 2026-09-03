import sys
import os
import json
import urllib.request
import urllib.error
import datetime

STATE_PATH = os.path.expanduser("~/vicious-cli/vicious_context.md")
LOG_PATH = os.path.expanduser("~/vicious-cli/logs/api_errors.log")
CONFIG_PATH = os.path.expanduser("~/vicious-cli/config/paths.json")

def log_error(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")

def get_api_key():
    key = os.getenv("GEMINI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not key:
        print("[Vicious Error] No API key found. Run: export GEMINI_API_KEY='your_key'")
        sys.exit(1)
    return key

def query_ai_structured(prompt, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    system_instruction = (
        "You are an AI developer assistant communicating with another AI-driven CLI parser. "
        "You MUST output your answer strictly in valid JSON format with these exact four keys:\n"
        "{\n"
        '  "diagnosis": "Brief summary of what is happening or broken",\n'
        '  "instructions": "Step-by-step plain text guide on how to solve it",\n'
        '  "advice": "Best practices, edge cases, or optimizations",\n'
        '  "commands": ["command 1", "command 2"]\n'
        "}\n"
        "Do NOT write any markdown formatting outside the JSON object."
    )

    full_prompt = f"{system_instruction}\n\nUser Prompt: {prompt}"
    data = {"contents": [{"parts": [{"text": full_prompt}]}]}

    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode("utf-8"))
            raw_text = res["candidates"][0]["content"]["parts"][0]["text"]
            # Clean possible markdown wrapping around JSON
            raw_text = raw_text.strip().replace("```json", "").replace("```", "")
            return json.loads(raw_text)
    except Exception as e:
        log_error(str(e))
        print(f"[Vicious Error]: Failed to query AI or parse response. Check logs.")
        return None

def run_menu(parsed_data):
    while True:
        print("\n" + "="*40)
        print("       VICIOUS AI RESPONSE MENU       ")
        print("="*40)
        print(" 1) Show Diagnosis")
        print(" 2) Show Instructions")
        print(" 3) Show Advice")
        print(" 4) Show Recommended Commands")
        print(" 5) Execute All Commands")
        print(" 6) Exit")
        print("="*40)
        
        choice = input("Type an option (1-6): ").strip()

        if choice == "1":
            print("\n--- DIAGNOSIS ---")
            print(parsed_data.get("diagnosis", "No diagnosis provided."))
        elif choice == "2":
            print("\n--- INSTRUCTIONS ---")
            print(parsed_data.get("instructions", "No instructions provided."))
        elif choice == "3":
            print("\n--- ADVICE ---")
            print(parsed_data.get("advice", "No advice provided."))
        elif choice == "4":
            print("\n--- RECOMMENDED COMMANDS ---")
            cmds = parsed_data.get("commands", [])
            for i, c in enumerate(cmds, 1):
                print(f" [{i}] {c}")
        elif choice == "5":
            cmds = parsed_data.get("commands", [])
            if not cmds:
                print("\nNo commands to run.")
            else:
                print(f"\nExecuting {len(cmds)} command(s)...")
                for c in cmds:
                    print(f"➜ Running: {c}")
                    os.system(c)
        elif choice == "6":
            print("\nExiting Vicious Menu.")
            break
        else:
            print("\nInvalid choice. Type a number between 1 and 6.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("[Vicious Usage]: ask 'your question here'")
        sys.exit(0)

    prompt = " ".join(sys.argv[1:])
    key = get_api_key()
    
    print("[Vicious] Communicating with AI...")
    parsed_response = query_ai_structured(prompt, key)

    if parsed_response:
        # Append response to log
        with open(STATE_PATH, "a") as f:
            f.write(f"\n\n## USER: {prompt}\n## PARSED DATA:\n{json.dumps(parsed_response, indent=2)}\n")

        # Launch interactive option menu
        run_menu(parsed_response)
