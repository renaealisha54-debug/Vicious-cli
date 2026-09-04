#!/usr/bin/env bash
set -e

INSTALL_DIR="$HOME/.local/bin"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"

echo "=========================================="
echo "  Installing Vicious CLI..."
echo "=========================================="

# 1. Create virtual environment if missing
if [ ! -d "$VENV_DIR" ]; then
    echo "[1/4] Creating virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
else
    echo "[1/4] Virtual environment already exists."
fi

# 2. Upgrade pip and install dependencies
echo "[2/4] Installing dependencies..."
"$VENV_DIR/bin/pip" install --upgrade pip
if [ -f "$PROJECT_DIR/requirements.txt" ]; then
    "$VENV_DIR/bin/pip" install -r "$PROJECT_DIR/requirements.txt"
fi

# 3. Create target bin directory if missing
mkdir -p "$INSTALL_DIR"

# 4. Create wrapper executable script
EXECUTABLE="$INSTALL_DIR/vicious"
echo "[3/4] Creating executable binary wrapper at $EXECUTABLE..."

cat << LAUNCHER > "$EXECUTABLE"
#!/usr/bin/env bash
export PYTHONPATH="$PROJECT_DIR/src:\$PYTHONPATH"
exec "$VENV_DIR/bin/python" "$PROJECT_DIR/src/main.py" "\$@"
LAUNCHER

chmod +x "$EXECUTABLE"

# 5. Check PATH environment variable
echo "[4/4] Verifying PATH installation..."
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo ""
    echo "⚠️  $INSTALL_DIR is not in your current PATH variable!"
    echo "Add this line to your ~/.bashrc or ~/.zshrc file:"
    echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
else
    echo "SUCCESS: $INSTALL_DIR is already in your PATH."
fi

echo "=========================================="
echo "  Vicious CLI installed successfully! 🎉"
echo "  Try running: vicious 'check free system memory'"
echo "=========================================="
