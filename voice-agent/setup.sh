#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# FLUXION Voice Agent - Setup Script
# Installs Python dependencies for the voice pipeline
# ═══════════════════════════════════════════════════════════════════════════

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  FLUXION Voice Agent - Setup"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON="python3"
elif command -v python &> /dev/null; then
    PYTHON="python"
else
    echo "ERROR: Python not found!"
    echo "Please install Python 3.10 or later"
    exit 1
fi

echo "Python: $($PYTHON --version)"

# Check pip
if ! $PYTHON -m pip --version &> /dev/null; then
    echo "ERROR: pip not found!"
    echo "Please install pip"
    exit 1
fi

echo ""
echo "Installing dependencies..."
echo ""

# Install requirements
$PYTHON -m pip install -r requirements.txt --quiet

echo ""
echo "Verifying installation..."
echo ""

# Verify imports
$PYTHON -c "
import sys
try:
    from groq import Groq
    print('  [OK] groq')
except ImportError as e:
    print(f'  [FAIL] groq: {e}')
    sys.exit(1)

try:
    from aiohttp import web
    print('  [OK] aiohttp')
except ImportError as e:
    print(f'  [FAIL] aiohttp: {e}')
    sys.exit(1)

try:
    from dotenv import load_dotenv
    print('  [OK] python-dotenv')
except ImportError as e:
    print(f'  [FAIL] python-dotenv: {e}')
    sys.exit(1)

print('')
print('All dependencies installed successfully!')
"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Setup complete!"
echo ""
echo "  To test the voice agent:"
echo "    1. Set GROQ_API_KEY in ../.env"
echo "    2. Run: python3 main.py --test"
echo "═══════════════════════════════════════════════════════════════"
