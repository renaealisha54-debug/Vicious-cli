import sys
import re
import os
import json
import subprocess

CONFIG_PATH = os.path.expanduser("~/vicious-cli/config/paths.json")
HISTORY_PATH = os.path.expanduser("~/.bash_history")

def load_presets():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {}

def load_history():
    if os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, "r", errors="ignore") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def display_full_response(text):
    """Pipes the full raw AI response into less so you can read explanations."""
    try:
        process = subprocess.Popen(["less", "-R"], stdin=subprocess.PIPE)
        process.communicate(input=text.encode("utf-8"))
    except Exception as e:
        print(f"[Vicious Warning] Could not render full text: {e}")

def extract_and_filter(text, presets, history):
    pattern = r"```(?:bash|sh|shell)?\n(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    
    allowed_paths = [os.path.normpath(v) for v in presets.values()]
    display_list = []
    cmd_map = {}

    for match in matches:
        for line in match.strip().split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            expanded_line = line
            for key, val in presets.items():
                expanded_line = expanded_line.replace(key, val)

            if "/" in expanded_line and not any(p in expanded_line for p in allowed_paths):
                if expanded_line.startswith("cd /") or expanded_line.startswith("ls /"):
                    continue

            is_executed = expanded_line in history
            status_tag = "[EXECUTED] " if is_executed else "[NEW]      "
            
            display_str = f"{status_tag} {expanded_line}"
            display_list.append(display_str)
            cmd_map[display_str] = expanded_line

    return display_list, cmd_map

def launch_fzf(display_list, cmd_map):
    if not display_list:
        print("\n[Vicious] No executable commands found in this response.")
        return

    fzf_input = "\n".join(display_list).encode("utf-8")
    
    try:
        process = subprocess.Popen(
            ["fzf", "-m", "--prompt=Select Command to Execute (TAB=multi-select, ENTER=run) > "],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
        stdout, _ = process.communicate(input=fzf_input)
        selected_displays = stdout.decode("utf-8").strip().splitlines()

        if selected_displays:
            print(f"\n[Vicious] Executing {len(selected_displays)} selected command(s)...\n")
            for item in selected_displays:
                cmd = cmd_map.get(item.strip())
                if cmd:
                    print(f"➜ Running: {cmd}")
                    os.system(cmd)
                    print("-" * 40)
    except FileNotFoundError:
        print("[Vicious Error] fzf is not installed. Run: pkg install fzf")

if __name__ == "__main__":
    raw_input = sys.stdin.read() if not sys.stdin.isatty() else ""
    if raw_input:
        # Phase 1: Read full AI text explanation in terminal
        display_full_response(raw_input)
        
        # Phase 2: Select and run commands
        presets = load_presets()
        history = load_history()
        display_list, cmd_map = extract_and_filter(raw_input, presets, history)
        launch_fzf(display_list, cmd_map)
    else:
        print("[Vicious] Usage: termux-clipboard-get | python src/main.py")
