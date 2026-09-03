import sys
import re
import os
import json
import subprocess

CONFIG_PATH = os.path.expanduser("~/vicious-cli/config/paths.json")

def load_presets():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {}

def extract_and_expand(text, presets):
    pattern = r"```(?:bash|sh|shell)?\n(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    commands = []
    for match in matches:
        for line in match.strip().split("\n"):
            line = line.strip()
            if line and not line.startswith("#"):
                for key, val in presets.items():
                    line = line.replace(key, val)
                commands.append(line)
    return commands

def launch_fzf(commands):
    if not commands:
        print("[Vicious] No valid executable commands found in clipboard input.")
        return

    # Join extracted commands with newlines
    fzf_input = "\n".join(commands).encode("utf-8")
    
    try:
        # Pass -m / --multi flag to fzf to enable Tab selection
        process = subprocess.Popen(
            ["fzf", "-m", "--prompt=Vicious Batch Run (TAB to select, ENTER to execute) > "],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
        stdout, _ = process.communicate(input=fzf_input)
        selected = stdout.decode("utf-8").strip().splitlines()

        if selected:
            print(f"\n[Vicious] Executing {len(selected)} selected command(s)...\n")
            for cmd in selected:
                cmd = cmd.strip()
                if cmd:
                    print(f"➜ Running: {cmd}")
                    os.system(cmd)
                    print("-" * 40)
    except FileNotFoundError:
        print("[Vicious Error] fzf is not installed. Run: pkg install fzf")

if __name__ == "__main__":
    presets = load_presets()
    raw_input = sys.stdin.read() if not sys.stdin.isatty() else ""
    if raw_input:
        extracted = extract_and_expand(raw_input, presets)
        launch_fzf(extracted)
    else:
        print("[Vicious] Send input via pipe, e.g.: termux-clipboard-get | python src/main.py")
