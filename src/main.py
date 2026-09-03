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

if __name__ == "__main__":
    presets = load_presets()
    raw_input = sys.stdin.read() if not sys.stdin.isatty() else ""
    if raw_input:
        extracted = extract_and_expand(raw_input, presets)
        print(f"[Vicious] Extracted {len(extracted)} executable commands.")
