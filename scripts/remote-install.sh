#!/bin/bash

# ═══════════════════════════════════════════════════════════════════
# FLUXION - Remote Installation Script
# Installazione remota su macOS/Windows via SSH
# ═══════════════════════════════════════════════════════════════════

set -e

# ========== CONFIGURATION ==========
REMOTE_USER="${1:-}"
REMOTE_HOST="${2:-}"
REMOTE_ADDR="${REMOTE_USER}@${REMOTE_HOST}"
REMOTE_PATH="/Applications/Fluxion.app"
BUILD_TYPE="${3:-release}"

if [ -z "$REMOTE_USER" ] || [ -z "$REMOTE_HOST" ]; then
    echo "Usage: $0 <remote_user> <remote_host> [release|debug]"
    echo "Example: $0 admin 192.168.1.100 release"
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "  FLUXION Remote Installation"
echo "═══════════════════════════════════════════════════════════════════"
echo "  Target: $REMOTE_ADDR"
echo "  Type: $BUILD_TYPE"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# ========== PHASE 1: BUILD ==========
echo "🔨 Phase 1: Building Fluxion..."
if [ "$BUILD_TYPE" = "release" ]; then
    npm run tauri build
    LOCAL_APP="src-tauri/target/release/bundle/macos/Fluxion.app"
else
    npm run tauri build -- --debug
    LOCAL_APP="src-tauri/target/debug/bundle/macos/Fluxion.app"
fi

if [ ! -d "$LOCAL_APP" ]; then
    echo "❌ Build failed: $LOCAL_APP not found"
    exit 1
fi

echo "✅ Build complete: $LOCAL_APP"

# ========== PHASE 2: PREPARE REMOTE ==========
echo ""
echo "📦 Phase 2: Preparing remote system..."

# Check if remote is macOS or Windows
OS_TYPE=$(ssh "$REMOTE_ADDR" "uname -s 2>/dev/null || echo 'Windows'")

if [[ "$OS_TYPE" == *"Darwin"* ]]; then
    echo "  Target OS: macOS"
    REMOTE_APP_PATH="/Applications/Fluxion.app"
    
    # Close app if running
    ssh "$REMOTE_ADDR" "pkill -f 'Fluxion' 2>/dev/null || true; sleep 1"
    
    # Backup existing installation
    ssh "$REMOTE_ADDR" "if [ -d '$REMOTE_APP_PATH' ]; then \
        mv '$REMOTE_APP_PATH' '${REMOTE_APP_PATH}.backup.$(date +%Y%m%d_%H%M%S)'; \
    fi"
    
    # Create temp directory
    ssh "$REMOTE_ADDR" "mkdir -p /tmp/fluxion-install"
    
    # Copy app
    echo ""
    echo "📤 Phase 3: Copying application..."
    scp -r "$LOCAL_APP" "$REMOTE_ADDR:/tmp/fluxion-install/Fluxion.app"
    
    # Move to Applications
    ssh "$REMOTE_ADDR" "sudo mv /tmp/fluxion-install/Fluxion.app /Applications/ && \
        rm -rf /tmp/fluxion-install && \
        sudo chmod -R 755 '$REMOTE_APP_PATH' && \
        sudo xattr -rd com.apple.quarantine '$REMOTE_APP_PATH' 2>/dev/null || true"
    
    # Create Desktop shortcut
    ssh "$REMOTE_ADDR" "osascript -e 'tell application \"Finder\" to make alias file to POSIX file \"/Applications/Fluxion.app\" at POSIX file \"$HOME/Desktop/\"' 2>/dev/null || true"
    
elif [[ "$OS_TYPE" == *"Linux"* ]]; then
    echo "  Target OS: Linux"
    # Linux installation (AppImage or deb)
    REMOTE_APP_PATH="/opt/fluxion"
    
    # Find built AppImage
    LOCAL_APPIMAGE=$(find src-tauri/target -name "*.AppImage" -type f | head -1)
    
    if [ -n "$LOCAL_APPIMAGE" ]; then
        scp "$LOCAL_APPIMAGE" "$REMOTE_ADDR:/tmp/fluxion.AppImage"
        ssh "$REMOTE_ADDR" "sudo mkdir -p /opt/fluxion && \
            sudo mv /tmp/fluxion.AppImage /opt/fluxion/ && \
            sudo chmod +x /opt/fluxion/fluxion.AppImage && \
            sudo ln -sf /opt/fluxion/fluxion.AppImage /usr/local/bin/fluxion"
    fi
    
else
    echo "  Target OS: Windows"
    REMOTE_APP_PATH="C:\\Program Files\\Fluxion"
    
    # Windows MSI installation
    LOCAL_MSI=$(find src-tauri/target -name "*.msi" -type f | head -1)
    
    if [ -n "$LOCAL_MSI" ]; then
        echo "  Copying MSI installer..."
        scp "$LOCAL_MSI" "$REMOTE_ADDR:/tmp/FluxionSetup.msi"
        
        echo "  Installing on Windows..."
        ssh "$REMOTE_ADDR" "msiexec /i C:\\tmp\\FluxionSetup.msi /qn /norestart"
    fi
fi

# ========== PHASE 4: VERIFY ==========
echo ""
echo "✅ Phase 4: Verifying installation..."

if [[ "$OS_TYPE" == *"Darwin"* ]]; then
    if ssh "$REMOTE_ADDR" "[ -d '$REMOTE_APP_PATH' ]"; then
        VERSION=$(ssh "$REMOTE_ADDR" "/usr/libexec/PlistBuddy -c 'Print CFBundleShortVersionString' '$REMOTE_APP_PATH/Contents/Info.plist' 2>/dev/null || echo 'unknown'")
        echo "  Version: $VERSION"
        echo "  Path: $REMOTE_APP_PATH"
        echo "  Status: ✅ Installed successfully"
    else
        echo "  Status: ❌ Installation failed"
        exit 1
    fi
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "  Installation Complete"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "  Next steps on remote machine:"
echo "  1. Open Fluxion from Applications folder"
echo "  2. Complete the Setup Wizard"
echo "  3. Activate your license"
echo ""
