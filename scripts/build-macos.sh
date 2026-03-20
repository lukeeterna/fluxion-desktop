#!/bin/bash
# FLUXION — macOS Build Script (iMac Intel x86_64)
# Builds: PyInstaller sidecar + Tauri app + ad-hoc codesign + PKG installer + DMG
#
# Usage: ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && bash scripts/build-macos.sh"
#
# Prerequisites:
#   - Python 3.9 with PyInstaller + all prod deps installed
#   - Node.js + npm
#   - Rust toolchain
#   - Xcode Command Line Tools (for codesign, pkgbuild, productbuild, hdiutil)
#
# Output (in releases/v$VERSION/):
#   - Fluxion_${VERSION}_macOS.pkg  (PRIMARY — zero-friction installer)
#   - Fluxion_${VERSION}_x64.dmg    (SECONDARY — drag-and-drop)
#   - Fluxion.app                    (raw app bundle)
#
# WHY PKG?
#   macOS Gatekeeper blocks ad-hoc signed .app when downloaded from internet.
#   A .pkg installer runs postinstall with root privileges, which strips the
#   com.apple.quarantine xattr. After install, the app opens with ZERO warnings.
#   The .pkg itself requires one right-click > "Open" on first launch (unavoidable
#   without Apple Developer ID $99/year).

set -euo pipefail

PYTHON="/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VOICE_DIR="$PROJECT_DIR/voice-agent"
BINARIES_DIR="$PROJECT_DIR/src-tauri/binaries"
ARCH="x86_64"
SIDECAR_NAME="voice-agent-${ARCH}-apple-darwin"
VERSION="1.0.0"
IDENTIFIER="com.fluxion.desktop"

# Output directories
RELEASE_DIR="$PROJECT_DIR/releases/v${VERSION}"
PKG_SCRIPTS_DIR="$PROJECT_DIR/scripts/pkg-scripts"
PKG_PAYLOAD_DIR="/tmp/fluxion-pkg-payload"

echo ""
echo "========================================================"
echo "  FLUXION macOS Build v${VERSION} (${ARCH})"
echo "========================================================"
echo ""

# ── Step 1: Build PyInstaller sidecar ─────────────────────────────
echo "[1/7] Building PyInstaller sidecar..."
cd "$VOICE_DIR"
"$PYTHON" -m PyInstaller --clean voice-agent.spec 2>&1 | tail -3

if [ ! -f "$VOICE_DIR/dist/voice-agent" ]; then
    echo "FAIL: PyInstaller build failed — no binary produced"
    exit 1
fi

SIDECAR_SIZE=$(du -h "$VOICE_DIR/dist/voice-agent" | cut -f1)
echo "  OK: Sidecar built: $SIDECAR_SIZE"

# ── Step 2: Copy sidecar to Tauri binaries ────────────────────────
echo ""
echo "[2/7] Installing sidecar..."
mkdir -p "$BINARIES_DIR"
cp "$VOICE_DIR/dist/voice-agent" "$BINARIES_DIR/$SIDECAR_NAME"
chmod +x "$BINARIES_DIR/$SIDECAR_NAME"
echo "  OK: Sidecar installed: $BINARIES_DIR/$SIDECAR_NAME"

# ── Step 3: Build frontend ────────────────────────────────────────
echo ""
echo "[3/7] Building frontend..."
cd "$PROJECT_DIR"
export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"
npm run build 2>&1 | tail -3
echo "  OK: Frontend built"

# ── Step 4: Build Tauri app ───────────────────────────────────────
echo ""
echo "[4/7] Building Tauri app..."
npm run tauri build 2>&1 | tail -10

# Find the .app bundle
APP_PATH=$(find "$PROJECT_DIR/src-tauri/target/release/bundle" -name "*.app" -maxdepth 3 2>/dev/null | head -1)

if [ -z "$APP_PATH" ]; then
    echo "FAIL: Tauri build failed — no .app bundle found"
    exit 1
fi
echo "  OK: Tauri app built: $APP_PATH"

# ── Step 5: Ad-hoc codesign (deep — signs all nested binaries) ───
echo ""
echo "[5/7] Ad-hoc code signing..."

# Sign inner binaries first (sidecar, frameworks), then the outer app
# --deep is convenient but signing inside-out is more reliable
find "$APP_PATH/Contents/MacOS" -type f -perm +111 | while read -r bin; do
    codesign --sign - --force --options runtime "$bin" 2>/dev/null || true
done

# Sign any frameworks/dylibs
find "$APP_PATH/Contents/Frameworks" -type f \( -name "*.dylib" -o -name "*.so" \) 2>/dev/null | while read -r lib; do
    codesign --sign - --force "$lib" 2>/dev/null || true
done

# Sign the app bundle itself
codesign --sign - --force --deep "$APP_PATH" 2>&1
echo "  OK: App signed (ad-hoc)"

# Verify signature
codesign --verify --verbose=2 "$APP_PATH" 2>&1 | tail -3 || true

# ── Step 6: Create PKG installer (PRIMARY distribution) ──────────
echo ""
echo "[6/7] Creating PKG installer..."

mkdir -p "$RELEASE_DIR"
mkdir -p "$PKG_SCRIPTS_DIR"

# Create the postinstall script that strips quarantine + fixes permissions
cat > "$PKG_SCRIPTS_DIR/postinstall" << 'POSTINSTALL_EOF'
#!/bin/bash
# FLUXION PKG postinstall — runs as root after installation
#
# This script removes the com.apple.quarantine extended attribute
# that macOS adds to files downloaded from the internet.
# Without this, Gatekeeper would block the app on launch.

APP_INSTALL_PATH="/Applications/Fluxion.app"

# Strip quarantine xattr from the entire app bundle (recursive)
xattr -cr "$APP_INSTALL_PATH" 2>/dev/null || true

# Ensure all executables have proper permissions
chmod -R 755 "$APP_INSTALL_PATH/Contents/MacOS/" 2>/dev/null || true

# Ensure the main binary is executable
if [ -f "$APP_INSTALL_PATH/Contents/MacOS/tauri-app" ]; then
    chmod 755 "$APP_INSTALL_PATH/Contents/MacOS/tauri-app"
fi

# Ensure voice agent sidecar is executable
find "$APP_INSTALL_PATH/Contents/MacOS/" -name "voice-agent*" -exec chmod 755 {} \; 2>/dev/null || true

# Register with Launch Services so the app appears in Spotlight/Launchpad
/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "$APP_INSTALL_PATH" 2>/dev/null || true

exit 0
POSTINSTALL_EOF

chmod +x "$PKG_SCRIPTS_DIR/postinstall"

# Prepare payload: copy .app to a temp directory mimicking /Applications/
rm -rf "$PKG_PAYLOAD_DIR"
mkdir -p "$PKG_PAYLOAD_DIR"
cp -R "$APP_PATH" "$PKG_PAYLOAD_DIR/Fluxion.app"

# Strip quarantine from the payload too (belt and suspenders)
xattr -cr "$PKG_PAYLOAD_DIR/Fluxion.app" 2>/dev/null || true

# Build the component package
PKG_COMPONENT="/tmp/fluxion-component.pkg"
pkgbuild \
    --root "$PKG_PAYLOAD_DIR" \
    --identifier "$IDENTIFIER" \
    --version "$VERSION" \
    --install-location "/Applications" \
    --scripts "$PKG_SCRIPTS_DIR" \
    "$PKG_COMPONENT" 2>&1

# Create distribution XML for productbuild (adds welcome/license/readme support)
DIST_XML="/tmp/fluxion-distribution.xml"
cat > "$DIST_XML" << DIST_EOF
<?xml version="1.0" encoding="utf-8"?>
<installer-gui-script minSpecVersion="2">
    <title>Fluxion</title>
    <organization>${IDENTIFIER}</organization>
    <domains enable_localSystem="true" enable_currentUserHome="false"/>
    <options customize="never" require-scripts="false" hostArchitectures="x86_64,arm64"/>

    <!-- Minimum macOS 12 Monterey -->
    <volume-check>
        <allowed-os-versions>
            <os-version min="12.0"/>
        </allowed-os-versions>
    </volume-check>

    <!-- System requirements check -->
    <installation-check script="installCheck()"/>
    <script>
        function installCheck() {
            var mem = system.sysctl('hw.memsize');
            // Warn if less than 4GB but don't block
            return true;
        }
    </script>

    <choices-outline>
        <line choice="default">
            <line choice="${IDENTIFIER}"/>
        </line>
    </choices-outline>

    <choice id="default"/>
    <choice id="${IDENTIFIER}" visible="false">
        <pkg-ref id="${IDENTIFIER}"/>
    </choice>

    <pkg-ref id="${IDENTIFIER}" version="${VERSION}" onConclusion="none">fluxion-component.pkg</pkg-ref>
</installer-gui-script>
DIST_EOF

# Build the final product archive (the .pkg the user downloads)
PKG_PATH="$RELEASE_DIR/Fluxion_${VERSION}_macOS.pkg"
productbuild \
    --distribution "$DIST_XML" \
    --package-path "/tmp" \
    --version "$VERSION" \
    "$PKG_PATH" 2>&1

PKG_SIZE=$(du -h "$PKG_PATH" | cut -f1)
echo "  OK: PKG installer created: $PKG_PATH ($PKG_SIZE)"

# Cleanup temp files
rm -rf "$PKG_PAYLOAD_DIR" "$PKG_COMPONENT" "$DIST_XML"

# ── Step 7: Create DMG (SECONDARY distribution) ──────────────────
echo ""
echo "[7/7] Creating DMG..."

DMG_STAGING="/tmp/fluxion-dmg-staging"
DMG_PATH="$RELEASE_DIR/Fluxion_${VERSION}_x64.dmg"

rm -rf "$DMG_STAGING"
mkdir -p "$DMG_STAGING"
cp -R "$APP_PATH" "$DMG_STAGING/Fluxion.app"

# Strip quarantine from DMG contents
xattr -cr "$DMG_STAGING/Fluxion.app" 2>/dev/null || true

# Create symlink to /Applications for drag-and-drop install
ln -s /Applications "$DMG_STAGING/Applications"

# Create a README for DMG users
cat > "$DMG_STAGING/LEGGIMI - Come Installare.txt" << 'README_EOF'
INSTALLAZIONE FLUXION
=====================

1. Trascina "Fluxion" nella cartella "Applications"

2. Apri il Terminale (Applicazioni > Utility > Terminale) e incolla:

   xattr -cr /Applications/Fluxion.app

3. Apri Fluxion da Launchpad o dalla cartella Applicazioni

NOTA: Il comando al punto 2 rimuove il blocco di sicurezza macOS
per le app scaricate da internet. E' necessario farlo solo la prima volta.

In alternativa, usa il file .pkg per un'installazione automatica
che non richiede il Terminale.

Supporto: fluxion.gestionale@gmail.com
README_EOF

# Create the DMG
hdiutil create \
    -volname "Fluxion ${VERSION}" \
    -srcfolder "$DMG_STAGING" \
    -ov \
    -format UDZO \
    "$DMG_PATH" 2>&1 | tail -2

DMG_SIZE=$(du -h "$DMG_PATH" | cut -f1)
echo "  OK: DMG created: $DMG_PATH ($DMG_SIZE)"

# Cleanup
rm -rf "$DMG_STAGING"

# ── Generate checksums ───────────────────────────────────────────
echo ""
echo "Generating checksums..."
cd "$RELEASE_DIR"
shasum -a 256 "Fluxion_${VERSION}_macOS.pkg" "Fluxion_${VERSION}_x64.dmg" > "checksums-sha256.txt"
echo "  OK: Checksums written to checksums-sha256.txt"

# ── Summary ───────────────────────────────────────────────────────
APP_SIZE=$(du -sh "$APP_PATH" | cut -f1)

echo ""
echo "========================================================"
echo "  BUILD COMPLETE — FLUXION v${VERSION}"
echo "========================================================"
echo ""
echo "  PRIMARY (recommended):"
echo "    PKG:  $PKG_PATH ($PKG_SIZE)"
echo "    Install: right-click > Open > enter password > done"
echo "    After install: app opens with ZERO warnings"
echo ""
echo "  SECONDARY (advanced users):"
echo "    DMG:  $DMG_PATH ($DMG_SIZE)"
echo "    Requires: xattr -cr /Applications/Fluxion.app"
echo ""
echo "  Raw app:  $APP_PATH ($APP_SIZE)"
echo "  Sidecar:  $SIDECAR_SIZE"
echo ""
echo "  Checksums: $RELEASE_DIR/checksums-sha256.txt"
echo ""
echo "  DISTRIBUTION INSTRUCTIONS:"
echo "  - Upload PKG + DMG to GitHub Releases"
echo "  - Landing page: link PKG as primary download"
echo "  - DMG as secondary 'advanced' download"
echo ""
echo "  USER FLOW (PKG):"
echo "    1. Download Fluxion_${VERSION}_macOS.pkg"
echo "    2. Right-click > Open (bypasses Gatekeeper for .pkg)"
echo "    3. Click Install > enter Mac password"
echo "    4. Open Fluxion from Launchpad — no warnings!"
echo ""
