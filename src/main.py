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

def display_response_menu(user_prompt, command):
    """Guaranteed interactive menu pop-up loop."""
    while True:
        print("\n==============================================")
        print("          VICIOUS AI RESPONSE MENU            ")
        print("==============================================")
        print("  1) Show Diagnosis")
        print("  2) Show Instructions")
        print("  3) Show Advice")
        print("  4) Show Recommended Commands")
        print("  5) Execute All Commands")
        print("  6) Exit")
        print("==============================================")
        
        choice = input("Type an option (1-6): ").strip()

        if choice == "1":
            print(f"\n--- [ Diagnosis ] ---\nRequest: '{user_prompt}'\nTarget system check initialized.")
        elif choice == "2":
            print(f"\n--- [ Instructions ] ---\n1. Inspect suggested command.\n2. Execute via Option 5 if safe.")
        elif choice == "3":
            print(f"\n--- [ Advice ] ---\nEnsure necessary root/user permissions exist before running subshell commands.")
        elif choice == "4":
            print(f"\n--- [ Recommended Commands ] ---\n  1. {command}")
        elif choice == "5":
            if not command:
                print("\nNo command available.")
                continue
            confirm = input(f"\nRun command (`{command}`)? [y/N]: ").strip().lower()
            if confirm == 'y':
                returncode, stdout, stderr = execute_shell_command(command)
                print(f"\n[Output]:\n{stdout}")
                if stderr:
                    print(f"[Error]:\n{stderr}")
                append_and_truncate_context(
                    f"### Executed: `{command}`\n- Code: {returncode} | Stderr: {stderr.strip()}"
                )
        elif choice == "6":
            print("Exiting response menu.")
            break
        else:
            print("\n[!] Invalid selection. Please enter a number between 1 and 6.")

def process_prompt(user_prompt):
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
        if cmd.startswith("bash"):
            cmd = cmd[4:].strip()

        # Launch response menu
        display_response_menu(user_prompt, cmd)

    except Exception as e:
        logger.error(f"Execution error: {e}")
        print(f"\n[Error] {e}")

def main():
    if len(sys.argv) < 2:
        user_prompt = input("Enter prompt for Vicious CLI: ").strip()
        if not user_prompt:
            sys.exit(0)
    else:
        user_prompt = " ".join(sys.argv[1:])

    if user_prompt.strip().lower() == "update":
        run_self_update()

    verify_environment()
    process_prompt(user_prompt)

if __name__ == "__main__":
    main()
