import sys
import os
import json
import urllib.request
import urllib.error
import datetime

STATE_PATH = os.path.expanduser("~/vicious-cli/vicious_context.md")
LOG_PATH = os.path.expanduser("~/vicious-cli/logs/api_errors.log")

def log_error(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")

def query_claude(prompt, context):
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        return None, "No Claude API key set."
    
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=key)
        
        system_instruction = (
            "You are an AI developer assistant communicating with a CLI parser. "
            "Output strictly valid JSON with keys: 'diagnosis', 'instructions', 'advice', 'commands' (array)."
        )
        full_prompt = f"System Context:\n{context}\n\nUser Question:\n{prompt}"
        
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=system_instruction,
            messages=[{"role": "user", "content": full_prompt}]
        )
        raw_text = message.content[0].text.strip().replace("```json", "").replace("```", "")
        return json.loads(raw_text), "Claude"
    except Exception as e:
        log_error(f"Claude Error: {e}")
        return None, f"Claude failed: {e}"

def query_gemini(prompt, context):
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        return None, "No Gemini API key set."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
    headers = {"Content-Type": "application/json"}
    
    system_instruction = (
        "You are an AI developer assistant communicating with a CLI parser. "
        "Output strictly valid JSON with keys: 'diagnosis', 'instructions', 'advice', 'commands' (array)."
    )
    full_prompt = f"{system_instruction}\n\nContext:\n{context}\n\nUser Question: {prompt}"
    data = {"contents": [{"parts": [{"text": full_prompt}]}]}

    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode("utf-8"))
            raw_text = res["candidates"][0]["content"]["parts"][0]["text"].strip().replace("```json", "").replace("```", "")
            return json.loads(raw_text), "Gemini"
    except Exception as e:
        log_error(f"Gemini Error: {e}")
        return None, f"Gemini failed: {e}"

def run_menu(parsed_data, provider_name):
    while True:
        print("\n" + "="*40)
        print(f"   VICIOUS AI MENU (Powered by {provider_name})   ")
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

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("[Vicious Usage]: ask 'your prompt here'")
        sys.exit(0)

    prompt = " ".join(sys.argv[1:])
    
    # Read workspace context
    context = ""
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, "r") as f:
            context = f.read()

    # Try Claude first
    print("[Vicious] Contacting Claude...")
    parsed_response, provider = query_claude(prompt, context)

    # Fallback to Gemini if Claude fails or hits rate limits
    if not parsed_response:
        print(f"[Vicious] Claude unavailable ({provider}). Falling back to Gemini...")
        parsed_response, provider = query_gemini(prompt, context)

    if parsed_response:
        with open(STATE_PATH, "a") as f:
            f.write(f"\n\n## [{provider}] USER: {prompt}\n## PARSED DATA:\n{json.dumps(parsed_response, indent=2)}\n")
        run_menu(parsed_response, provider)
    else:
        print("[Vicious Error] Both Claude and Gemini queries failed. Check ~/vicious-cli/logs/api_errors.log")
