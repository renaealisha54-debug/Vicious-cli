import sys
import os
from ai_chat import generate_ai_response
from context_manager import append_and_truncate_context
from logger import logger

def verify_environment():
    """Ensure at least one supported provider key is present."""
    keys = ["GROQ_API_KEY", "GEMINI_API_KEY", "OPENAI_API_KEY"]
    if not any(os.environ.get(k) for k in keys):
        print("\n[Error] No API keys found in environment.")
        print("Please export at least one of: GROQ_API_KEY, GEMINI_API_KEY, OPENAI_API_KEY\n")
        logger.error("Startup failed: missing API keys.")
        sys.exit(1)

def prompt_user_action():
    print("\nActions: [y] Execute | [n] Skip | [a] Always Allow | [q] Quit")
    choice = input("Select an option: ").strip().lower()
    return choice

def main():
    verify_environment()
    
    if len(sys.argv) < 2:
        print("Usage: vicious <prompt>")
        sys.exit(0)

    user_prompt = " ".join(sys.argv[1:])
    logger.info(f"User Request: {user_prompt}")
    print(f"\n[vicious] Processing request: '{user_prompt}'...")

    system_instruction = (
        "You are Vicious CLI, an intelligent system administrator assistant. "
        "Return short, clear responses or executable shell commands."
    )

    try:
        response = generate_ai_response(user_prompt, system_instruction)
        print(f"\n--- AI Output ---\n{response}\n-----------------")
        
        # Log and update history
        logger.info(f"AI Output: {response}")
        append_and_truncate_context(f"### User: {user_prompt}\n- Response: {response}")

        action = prompt_user_action()
        if action == 'q':
            print("Exiting.")
            sys.exit(0)
        elif action == 'y':
            print("[Executing command...]")
            # Place shell execution logic here
        else:
            print("[Skipped execution.]")

    except Exception as e:
        logger.error(f"Execution error: {e}")
        print(f"\n[Error] {e}")

if __name__ == "__main__":
    main()
