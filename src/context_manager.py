import os

CONTEXT_FILE = "vicious_context.md"
MAX_LINES = 100  # Adjust based on average entry size

def append_and_truncate_context(new_entry: str, max_lines: int = MAX_LINES):
    """Appends new interaction history and caps the total line count."""
    if not os.path.exists(CONTEXT_FILE):
        lines = ["# Vicious CLI Context History\n\n"]
    else:
        with open(CONTEXT_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

    # Append new entry
    lines.append(f"\n{new_entry.strip()}\n")

    # Retain system header (first 2 lines) and keep only latest max_lines
    if len(lines) > max_lines:
        header = lines[:2]
        truncated_body = lines[-(max_lines - 2):]
        lines = header + truncated_body

    with open(CONTEXT_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)
