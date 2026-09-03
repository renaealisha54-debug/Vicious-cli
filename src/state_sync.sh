#!/bin/bash
OUT_FILE="$HOME/vicious-cli/vicious_context.md"
echo "# VICIOUS HANDOVER CONTEXT" > "$OUT_FILE"
echo "Timestamp: $(date)" >> "$OUT_FILE"
echo "Vicious context saved to: $OUT_FILE"
