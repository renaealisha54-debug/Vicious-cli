import sys
import os
from ai_chat import generate_ai_response
from context_manager import append_and_truncate_context
from logger import logger
from executor import execute_shell_command
from updater import run_self_update

def verify_environment():
    """Ensure at least one supported provider key is present."""
    keys = ["GROQ_API_KEY", "GEMINI_API_KEY", "OPENAI_API_KEY"]
    if not any(os.environ.get(k) for k in keys):
        print("\n[Error] No API keys found in environment.")
        print("Please export at least one of: GROQ_API_KEY, GEMINI_API_KEY, OPENAI_API_KEY\n")
        logger.error("Startup failed: missing API keys.")
        sys.exit(1)

def prompt_user_action():
    print("\nActions: [y] Execute | [n] Skip | [q] Quit")
    choice = input("Select an option: ").strip().lower()
    return choice

def main():
    if len(sys.argv) < 2:
        print("Usage: vicious <prompt> | vicious update")
        sys.exit(0)

    user_prompt = " ".join(sys.argv[1:])

    # Intercept self-update subcommand
    if user_prompt.strip().lower() == "update":
        run_self_update()

    verify_environment()
    logger.info(f"User Request: {user_prompt}")
    print(f"\n[vicious] Processing request: '{user_prompt}'...")

    system_instruction = (
        "You are Vicious CLI, an intelligent system administrator assistant. "
        "Return ONLY the exact single bash command necessary to fulfill the request. "
        "Do not wrap in markdown code blocks or add explanatory commentary."
    )

    try:
        cmd = generate_ai_response(user_prompt, system_instruction).strip()
        if cmd.startswith("```"):
            cmd = cmd.split("\n", 1)[-1].rsplit("```", 1)[0].strip()

        print(f"\n--- Suggested Command ---\n{cmd}\n-----------------------")
        
        action = prompt_user_action()
        if action == 'q':
            print("Exiting.")
            sys.exit(0)
        elif action == 'y':
            returncode, stdout, stderr = execute_shell_command(cmd)
            exec_summary = f"Exit Code: {returncode}"
            if stderr:
                exec_summary += f" | Stderr: {stderr.strip()}"
            append_and_truncate_context(
                f"### User: {user_prompt}\n- Executed: `{cmd}`\n- Result: {exec_summary}"
            )
        else:
            print("[Skipped execution.]")
            append_and_truncate_context(f"### User: {user_prompt}\n- Command (Skipped): `{cmd}`")

    except Exception as e:
        logger.error(f"Execution error: {e}")
        print(f"\n[Error] {e}")

if __name__ == "__main__":
    main()
