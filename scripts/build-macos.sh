#!/bin/bash
# FLUXION — macOS Build Script (iMac Intel x86_64)
# Builds: PyInstaller sidecar + Tauri app + ad-hoc codesign
#
# Usage: ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && bash scripts/build-macos.sh"
#
# Prerequisites:
#   - Python 3.9 with PyInstaller + all prod deps installed
#   - Node.js + npm
#   - Rust toolchain
#   - Xcode Command Line Tools (for codesign)

set -euo pipefail

PYTHON="/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VOICE_DIR="$PROJECT_DIR/voice-agent"
BINARIES_DIR="$PROJECT_DIR/src-tauri/binaries"
ARCH="x86_64"
SIDECAR_NAME="voice-agent-${ARCH}-apple-darwin"

echo "═══════════════════════════════════════════"
echo "  FLUXION macOS Build (${ARCH})"
echo "═══════════════════════════════════════════"
echo ""

# ── Step 1: Build PyInstaller sidecar ─────────────────────────────
echo "▶ Step 1/5: Building PyInstaller sidecar..."
cd "$VOICE_DIR"
"$PYTHON" -m PyInstaller --clean voice-agent.spec 2>&1 | tail -3

if [ ! -f "$VOICE_DIR/dist/voice-agent" ]; then
    echo "❌ PyInstaller build failed — no binary produced"
    exit 1
fi

SIDECAR_SIZE=$(du -h "$VOICE_DIR/dist/voice-agent" | cut -f1)
echo "✅ Sidecar built: $SIDECAR_SIZE"

# ── Step 2: Copy sidecar to Tauri binaries ────────────────────────
echo ""
echo "▶ Step 2/5: Installing sidecar..."
mkdir -p "$BINARIES_DIR"
cp "$VOICE_DIR/dist/voice-agent" "$BINARIES_DIR/$SIDECAR_NAME"
chmod +x "$BINARIES_DIR/$SIDECAR_NAME"
echo "✅ Sidecar installed: $BINARIES_DIR/$SIDECAR_NAME"

# ── Step 3: Build frontend ────────────────────────────────────────
echo ""
echo "▶ Step 3/5: Building frontend..."
cd "$PROJECT_DIR"
export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"
npm run build 2>&1 | tail -3
echo "✅ Frontend built"

# ── Step 4: Build Tauri app ───────────────────────────────────────
echo ""
echo "▶ Step 4/5: Building Tauri app..."
npm run tauri build 2>&1 | tail -10

# Find the .app bundle
APP_PATH=$(find "$PROJECT_DIR/src-tauri/target/release/bundle" -name "*.app" -maxdepth 3 2>/dev/null | head -1)
DMG_PATH=$(find "$PROJECT_DIR/src-tauri/target/release/bundle" -name "*.dmg" -maxdepth 3 2>/dev/null | head -1)

if [ -z "$APP_PATH" ]; then
    echo "❌ Tauri build failed — no .app bundle found"
    exit 1
fi
echo "✅ Tauri app built: $APP_PATH"

# ── Step 5: Ad-hoc codesign ───────────────────────────────────────
echo ""
echo "▶ Step 5/5: Ad-hoc code signing..."
codesign --sign - --force --deep "$APP_PATH" 2>&1
echo "✅ App signed (ad-hoc)"

# ── Summary ───────────────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════"
echo "  BUILD COMPLETE"
echo "═══════════════════════════════════════════"
echo ""
echo "  App:     $APP_PATH"
[ -n "${DMG_PATH:-}" ] && echo "  DMG:     $DMG_PATH"
echo "  Sidecar: $SIDECAR_SIZE"
echo ""
APP_SIZE=$(du -sh "$APP_PATH" | cut -f1)
echo "  Total app size: $APP_SIZE"
echo ""
echo "  To test: open '$APP_PATH'"
echo ""
