import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai_chat import generate_ai_response

def main():
    # If arguments are passed, run once
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
        process_prompt(prompt)
        return

    # Interactive loop mode
    print("=== Vicious CLI Interactive Mode (type 'exit' or 'quit' to stop) ===")
    while True:
        try:
            prompt = input("\nEnter prompt for Vicious CLI: ").strip()
            if prompt.lower() in ["exit", "quit"]:
                print("Exiting Vicious CLI.")
                break
            if not prompt:
                continue
            process_prompt(prompt)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting Vicious CLI.")
            break

def process_prompt(prompt):
    print(f"\n[vicious] Processing request: '{prompt}'...")
    result = generate_ai_response(prompt)
    
    if isinstance(result, tuple):
        response = result[0]
        error = result[1] if len(result) > 1 else None
    else:
        response, error = result, None

    if error:
        print(f"\n[Error] {error}")
    else:
        print(f"\n{response}")

if __name__ == "__main__":
    main()
