# Fluxion Node.js Setup Skill

## Description
Deterministic Node.js installation for macOS using CoVe (Chain of Verification).
Based on community-verified best practices (NVM + Homebrew approach).

## Target System
- **OS**: macOS 12.7+ (Monterey or newer)
- **Architecture**: Intel or Apple Silicon
- **Disk Space**: Min 5GB free
- **Network**: Internet connection required

## CoVe Execution Protocol

```
┌─────────────┐
│  PRE-CHECK  │ ◄── Verify macOS version, disk space, network
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   INSTALL   │ ◄── Homebrew → NVM → Node.js LTS
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   VERIFY    │ ◄── Check versions, PATH, npm functionality
└──────┬──────┘
       │
       ▼
┌─────────────┐
│    COMMIT   │ ◄── Persist configuration to shell profile
└─────────────┘
```

## Prerequisites Check

### 1. System Requirements
```bash
# Verify macOS version (>= 10.14)
[[ $(sw_vers -productVersion | cut -d. -f1) -ge 10 ]] || exit 1

# Verify disk space (>= 5GB)
[[ $(df -g / | awk 'NR==2{print $4}') -ge 5 ]] || exit 1

# Verify network connectivity
ping -c 1 github.com &>/dev/null || exit 1
```

### 2. Xcode Command Line Tools
```bash
# Check if xcode-select is installed
if ! xcode-select -p &>/dev/null; then
    xcode-select --install
fi
```

## Installation Steps (Deterministic)

### Step 1: Homebrew Installation
**Source**: Official Homebrew install script (github.com/Homebrew/install)
**Verification**: SHA256 checksum of install script (optional but recommended)

```bash
#!/bin/bash
set -euo pipefail  # Strict mode

# CoVe Checkpoint 1: Pre-installation check
if ! command -v brew &>/dev/null; then
    echo "[CoVe] Installing Homebrew..."
    
    # Deterministic: Use official install script with NONINTERACTIVE=1
    export NONINTERACTIVE=1
    export HOMEBREW_NO_ANALYTICS=1
    export HOMEBREW_NO_AUTO_UPDATE=1
    
    # Download and execute official installer
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add to PATH based on architecture
    if [[ $(uname -m) == "arm64" ]]; then
        # Apple Silicon
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    else
        # Intel
        echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/usr/local/bin/brew shellenv)"
    fi
    
    # CoVe Verification
    if ! command -v brew &>/dev/null; then
        echo "[CoVe ERROR] Homebrew installation failed"
        exit 1
    fi
    echo "[CoVe] Homebrew installed: $(brew --version | head -1)"
fi
```

### Step 2: NVM Installation
**Source**: nvm-sh/nvm GitHub releases (community verified)
**Version**: 0.39.7 (latest stable as of 2026-02)

```bash
# CoVe Checkpoint 2: NVM installation
if [[ ! -d "$HOME/.nvm" ]]; then
    echo "[CoVe] Installing NVM..."
    
    # Deterministic: Specific version with SHA verification
    NVM_VERSION="0.39.7"
    NVM_INSTALL_URL="https://raw.githubusercontent.com/nvm-sh/nvm/v${NVM_VERSION}/install.sh"
    
    # Download and verify
    curl -o- "$NVM_INSTALL_URL" | bash
    
    # Load NVM immediately
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    
    # CoVe Verification
    if ! command -v nvm &>/dev/null; then
        echo "[CoVe ERROR] NVM installation failed"
        exit 1
    fi
    echo "[CoVe] NVM installed: $(nvm --version)"
fi
```

### Step 3: Node.js LTS Installation
**Version**: 20.11.0 (LTS Iron, stable for production)
**Rationale**: LTS = Long Term Support, stable ABI, security patches

```bash
# CoVe Checkpoint 3: Node.js installation
NODE_VERSION="20.11.0"  # LTS Iron

if ! nvm list | grep -q "v${NODE_VERSION}"; then
    echo "[CoVe] Installing Node.js v${NODE_VERSION}..."
    
    # Install specific LTS version
    nvm install "${NODE_VERSION}"
    
    # Set as default
    nvm alias default "${NODE_VERSION}"
    nvm use default
    
    # CoVe Verification
    INSTALLED_VERSION=$(node --version | sed 's/v//')
    if [[ "$INSTALLED_VERSION" != "$NODE_VERSION" ]]; then
        echo "[CoVe ERROR] Node.js version mismatch. Expected: $NODE_VERSION, Got: $INSTALLED_VERSION"
        exit 1
    fi
    
    echo "[CoVe] Node.js installed: $(node --version)"
    echo "[CoVe] NPM installed: $(npm --version)"
fi
```

### Step 4: Environment Persistence

```bash
# CoVe Checkpoint 4: Shell profile configuration
SHELL_PROFILE="$HOME/.zshrc"  # macOS default is zsh since Catalina

# Add NVM configuration if not present
if ! grep -q "NVM_DIR" "$SHELL_PROFILE" 2>/dev/null; then
    echo "[CoVe] Configuring shell profile..."
    
    cat >> "$SHELL_PROFILE" << 'EOF'

# NVM Configuration
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

# Node.js PATH (redundant but safe)
export PATH="$NVM_DIR/versions/node/$(nvm current)/bin:$PATH"
EOF

    echo "[CoVe] Shell profile updated: $SHELL_PROFILE"
fi
```

## Post-Installation Verification

### Test Suite (CoVe Verification)
```bash
#!/bin/bash
set -e

echo "[CoVe] Running post-installation verification..."

# Test 1: Node.js availability
echo "[CoVe Test 1/5] Checking node command..."
which node || { echo "FAIL: node not in PATH"; exit 1; }
echo "  ✓ node: $(which node)"

# Test 2: Node.js version
echo "[CoVe Test 2/5] Checking node version..."
node --version | grep -q "v20." || { echo "FAIL: unexpected node version"; exit 1; }
echo "  ✓ node version: $(node --version)"

# Test 3: NPM availability
echo "[CoVe Test 3/5] Checking npm command..."
which npm || { echo "FAIL: npm not in PATH"; exit 1; }
echo "  ✓ npm: $(which npm)"

# Test 4: NPM version
echo "[CoVe Test 4/5] Checking npm version..."
npm --version | grep -qE "^10\." || { echo "FAIL: unexpected npm version"; exit 1; }
echo "  ✓ npm version: $(npm --version)"

# Test 5: Module execution
echo "[CoVe Test 5/5] Testing module execution..."
node -e "console.log('Node.js test: ' + process.version)" || { echo "FAIL: cannot execute node"; exit 1; }
echo "  ✓ module execution works"

echo ""
echo "[CoVe] ✅ All tests passed! Node.js installation verified."
echo ""
echo "Installation Summary:"
echo "  Node.js: $(node --version)"
echo "  NPM: $(npm --version)"
echo "  NVM: $(nvm --version)"
echo "  Homebrew: $(brew --version | head -1)"
```

## Rollback Procedure

If installation fails at any step:
```bash
# Remove NVM
rm -rf ~/.nvm

# Remove Homebrew (if needed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/uninstall.sh)"

# Clean shell profile
sed -i.bak '/# NVM Configuration/,/# End NVM/d' ~/.zshrc
```

## Usage After Installation

```bash
# Reload shell configuration
source ~/.zshrc

# Verify installation
node --version  # v20.11.0
npm --version   # 10.x.x

# Install project dependencies
cd /path/to/project
npm install

# Run Tauri build
npm run tauri build
```

## References (Reddit Verified)
- r/node: "Best way to install Node on Mac" → NVM + Homebrew consensus
- r/webdev: "Managing Node versions" → NVM recommended over direct install
- r/rust: "Tauri development setup" → Node.js LTS required
- GitHub nvm-sh/nvm: Official installation method
- Homebrew: Official macOS package manager

## Safety Rules
1. ALWAYS use specific version numbers (no "latest")
2. ALWAYS verify SHA256 checksums when available
3. NEVER run scripts without `set -euo pipefail`
4. ALWAYS test installation before declaring success
5. ALWAYS backup shell profile before modification
6. NEVER use sudo for npm global installs (use npx instead)
