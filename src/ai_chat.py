import sys
import os
import json
import datetime
from groq import Groq

STATE_PATH = os.path.expanduser("~/vicious-cli/vicious_context.md")
LOG_PATH = os.path.expanduser("~/vicious-cli/logs/api_errors.log")

def log_error(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(f"[{timestamp}] {msg}\n")

def get_active_model(client):
    try:
        models_page = client.models.list()
        available_ids = [m.id for m in models_page.data]

        for preferred in ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile", "llama3-70b-8192", "llama-3.1-8b-instant", "qwen/qwen3.8-27b"]:
            if preferred in available_ids:
                return preferred

        if available_ids:
            return available_ids[0]
    except Exception as e:
        log_error(f"Failed to fetch models list: {e}")

    return "llama3-8b-8192"

def query_groq(prompt, context):
    key = os.getenv("GROQ_API_KEY")
    if not key:
        return None, "No GROQ_API_KEY set in environment."

    try:
        client = Groq(api_key=key)
        target_model = get_active_model(client)

        system_instruction = (
            "You are an AI developer assistant communicating with a CLI parser. "
            "Output strictly valid JSON with keys: 'diagnosis', 'instructions', 'advice', 'commands' (array)."
        )

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": f"System Context:\n{context}\n\nUser Question:\n{prompt}"}
            ],
            model=target_model,
            response_format={"type": "json_object"}
        )

        raw_text = chat_completion.choices[0].message.content
        return json.loads(raw_text), f"Groq ({target_model})"
    except Exception as e:
        log_error(f"Groq Error: {e}")
        return None, f"Groq failed: {e}"

def run_menu(parsed_data, provider_name):
    while True:
        options = {}
        idx = 1

        print("\n" + "="*40)
        print(f"   VICIOUS AI MENU ({provider_name})   ")
        print("="*40)

        options[str(idx)] = ("Display Full Response", "full")
        print(f" {idx}) Display Full Response")
        idx += 1

        if parsed_data.get("diagnosis"):
            options[str(idx)] = ("Show Diagnosis", "diagnosis")
            print(f" {idx}) Show Diagnosis")
            idx += 1

        if parsed_data.get("instructions"):
            options[str(idx)] = ("Show Instructions", "instructions")
            print(f" {idx}) Show Instructions")
            idx += 1

        if parsed_data.get("advice"):
            options[str(idx)] = ("Show Advice", "advice")
            print(f" {idx}) Show Advice")
            idx += 1

        cmds = parsed_data.get("commands", [])
        if cmds:
            options[str(idx)] = ("Show Recommended Commands", "show_cmds")
            print(f" {idx}) Show Recommended Commands")
            idx += 1

            options[str(idx)] = ("Execute Commands (asks before each)", "exec_cmds")
            print(f" {idx}) Execute Commands (asks before each)")
            idx += 1

        options[str(idx)] = ("Exit", "exit")
        print(f" {idx}) Exit")
        print("="*40)

        choice = input(f"Type an option (1-{idx}): ").strip()

        if choice in options:
            action = options[choice][1]
            if action == "full":
                print("\n--- FULL RESPONSE ---")
                for k, v in parsed_data.items():
                    print(f"\n[{k.upper()}]:\n{v if isinstance(v, str) else json.dumps(v, indent=2)}")
            elif action == "diagnosis":
                print("\n--- DIAGNOSIS ---")
                print(parsed_data.get("diagnosis"))
            elif action == "instructions":
                print("\n--- INSTRUCTIONS ---")
                print(parsed_data.get("instructions"))
            elif action == "advice":
                print("\n--- ADVICE ---")
                print(parsed_data.get("advice"))
            elif action == "show_cmds":
                print("\n--- RECOMMENDED COMMANDS ---")
                for i, c in enumerate(cmds, 1):
                    print(f" [{i}] {c}")
            elif action == "exec_cmds":
                print(f"\n{len(cmds)} command(s) suggested by the AI — NOT reviewed for safety.")
                run_rest = False
                for c in cmds:
                    if not run_rest:
                        answer = input(
                            f"\nRun this command?\n  {c}\n(y)es / (n)o / (a)ll remaining / (q)uit: "
                        ).strip().lower()
                        if answer == 'q':
                            print("Stopped — no further commands will run.")
                            break
                        elif answer == 'a':
                            run_rest = True
                        elif answer != 'y':
                            print(f"Skipped: {c}")
                            continue
                    print(f"➜ Running: {c}")
                    os.system(c)
            elif action == "exit":
                print("\nExiting Vicious Menu.")
                break
        else:
            print("\nInvalid choice, try again.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("[Vicious Usage]: ask 'your prompt here'")
        sys.exit(0)

    prompt = " ".join(sys.argv[1:])

    context = ""
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, "r") as f:
            context = f.read()

    print("[Vicious] Contacting Groq...")
    parsed_response, provider = query_groq(prompt, context)

    if parsed_response:
        with open(STATE_PATH, "a") as f:
            f.write(f"\n\n## [{provider}] USER: {prompt}\n## PARSED DATA:\n{json.dumps(parsed_response, indent=2)}\n")
        run_menu(parsed_response, provider)
    else:
        print(f"[Vicious Error] Request failed ({provider}). Check ~/vicious-cli/logs/api_errors.log")
