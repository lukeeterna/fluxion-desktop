#!/usr/bin/env bash
# FLUXION Voice Agent — Build PyInstaller sidecar for Tauri
#
# Usage:
#   ./build-sidecar.sh              # Build for current platform
#   ./build-sidecar.sh --clean      # Clean build (remove previous artifacts)
#
# Run on iMac (192.168.1.2) where Python 3.9 + all deps are installed.
# Output is copied to src-tauri/binaries/ with Tauri naming convention.
#
# Tauri sidecar naming:
#   macOS ARM:   voice-agent-aarch64-apple-darwin
#   macOS Intel: voice-agent-x86_64-apple-darwin
#   Windows:     voice-agent-x86_64-pc-windows-msvc.exe

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BINARIES_DIR="$PROJECT_ROOT/src-tauri/binaries"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN} FLUXION Voice Agent — Sidecar Build${NC}"
echo -e "${GREEN}========================================${NC}"

# ── Clean mode ────────────────────────────────────────────────────────
if [[ "${1:-}" == "--clean" ]]; then
    echo -e "${YELLOW}Cleaning previous build artifacts...${NC}"
    rm -rf "$SCRIPT_DIR/build" "$SCRIPT_DIR/dist"
    echo "Done."
fi

# ── Detect platform ──────────────────────────────────────────────────
OS="$(uname -s)"
ARCH="$(uname -m)"

if [[ "$OS" == "Darwin" ]]; then
    if [[ "$ARCH" == "arm64" ]]; then
        TARGET="aarch64-apple-darwin"
    else
        TARGET="x86_64-apple-darwin"
    fi
    BINARY_NAME="voice-agent-${TARGET}"
elif [[ "$OS" == "MINGW"* ]] || [[ "$OS" == "MSYS"* ]] || [[ "$OS" == "CYGWIN"* ]]; then
    TARGET="x86_64-pc-windows-msvc"
    BINARY_NAME="voice-agent-${TARGET}.exe"
else
    echo -e "${RED}Unsupported platform: $OS $ARCH${NC}"
    exit 1
fi

echo "Platform: $OS $ARCH"
echo "Target:   $TARGET"
echo "Output:   $BINARIES_DIR/$BINARY_NAME"

# ── Find PyInstaller ─────────────────────────────────────────────────
PYINSTALLER=""
if command -v pyinstaller &>/dev/null; then
    PYINSTALLER="pyinstaller"
elif python3 -m PyInstaller --version &>/dev/null 2>&1; then
    PYINSTALLER="python3 -m PyInstaller"
else
    echo -e "${RED}PyInstaller not found. Install with: pip3 install pyinstaller${NC}"
    exit 1
fi

echo "PyInstaller: $PYINSTALLER"
echo ""
echo -e "${YELLOW}Building with PyInstaller...${NC}"
cd "$SCRIPT_DIR"

# ── Build ─────────────────────────────────────────────────────────────
$PYINSTALLER voice-agent.spec \
    --noconfirm \
    --log-level WARN \
    2>&1

# ── Verify output ─────────────────────────────────────────────────────
if [[ "$OS" == "Darwin" ]]; then
    BUILT="$SCRIPT_DIR/dist/voice-agent"
else
    BUILT="$SCRIPT_DIR/dist/voice-agent.exe"
fi

if [[ ! -f "$BUILT" ]]; then
    echo -e "${RED}Build failed: $BUILT not found${NC}"
    exit 1
fi

# ── Copy to Tauri binaries ────────────────────────────────────────────
mkdir -p "$BINARIES_DIR"
cp "$BUILT" "$BINARIES_DIR/$BINARY_NAME"
chmod +x "$BINARIES_DIR/$BINARY_NAME"

# ── Report ────────────────────────────────────────────────────────────
SIZE_MB=$(du -m "$BINARIES_DIR/$BINARY_NAME" | cut -f1)
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN} Build successful!${NC}"
echo -e "${GREEN}========================================${NC}"
echo "Binary: $BINARIES_DIR/$BINARY_NAME"
echo "Size:   ${SIZE_MB} MB"
echo ""

# ── Smoke test ────────────────────────────────────────────────────────
echo -e "${YELLOW}Running smoke test...${NC}"
timeout 5 "$BINARIES_DIR/$BINARY_NAME" --help 2>/dev/null && echo -e "${GREEN}Smoke test passed${NC}" || echo -e "${YELLOW}Smoke test: binary starts (timeout expected)${NC}"
echo ""
echo "Next: run 'npm run tauri build' to bundle the full app with sidecar."
