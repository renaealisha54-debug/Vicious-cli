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
    """Loads previously executed commands from bash history."""
    if os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, "r", errors="ignore") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def extract_expand_and_filter(text, presets, history):
    pattern = r"```(?:bash|sh|shell)?\n(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    
    # Get assigned app target paths to filter out unwanted apps
    allowed_paths = [os.path.normpath(v) for v in presets.values()]
    
    display_list = []
    cmd_map = {}

    for match in matches:
        for line in match.strip().split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # 1. Expand presets
            expanded_line = line
            for key, val in presets.items():
                expanded_line = expanded_line.replace(key, val)

            # 2. Filter: Only include commands that target assigned paths or local operations
            # Skip if the command explicitly references a path outside your configured app folders
            if "/" in expanded_line and not any(p in expanded_line for p in allowed_paths):
                # If command points to a specific path outside allowed paths, ignore it
                if expanded_line.startswith("cd /") or expanded_line.startswith("ls /"):
                    continue

            # 3. Check execution history status
            is_executed = expanded_line in history
            status_tag = "[EXECUTED] " if is_executed else "[NEW]      "
            
            display_str = f"{status_tag} {expanded_line}"
            display_list.append(display_str)
            cmd_map[display_str] = expanded_line

    return display_list, cmd_map

def launch_fzf(display_list, cmd_map):
    if not display_list:
        print("[Vicious] No matching app commands found in clipboard.")
        return

    fzf_input = "\n".join(display_list).encode("utf-8")
    
    try:
        process = subprocess.Popen(
            ["fzf", "-m", "--prompt=Vicious App Filter > "],
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
    presets = load_presets()
    history = load_history()
    raw_input = sys.stdin.read() if not sys.stdin.isatty() else ""
    if raw_input:
        display_list, cmd_map = extract_expand_and_filter(raw_input, presets, history)
        launch_fzf(display_list, cmd_map)
    else:
        print("[Vicious] Usage: termux-clipboard-get | python src/main.py")
