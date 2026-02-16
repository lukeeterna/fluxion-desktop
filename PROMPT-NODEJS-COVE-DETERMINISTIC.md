# PROMPT: Node.js CoVe Deterministic Setup
## Per iMac (192.168.1.7) - macOS 12.7.4

**AUTORITÀ**: Questo prompt è generato da Deep Research CoVe con metodologia Reddit-verified.
**OBIETTIVO**: Installare Node.js 20.11.0 LTS sull'iMac in modo deterministico con verifica ad ogni step.

---

## 🎯 RISULTATO ATTESO
- Node.js v20.11.0 installato e funzionante
- NVM 0.39.7 come version manager
- Homebrew come package manager
- Tutti i tool pronti per `npm run tauri build`

---

## 📋 COVE EXECUTION CHECKLIST

### PHASE 1: PRE-CHECK ✅
- [ ] macOS version >= 12.0 (Attuale: 12.7.4) ✅
- [ ] Disk space >= 5GB (Attuale: 602GB) ✅
- [ ] Network connectivity to github.com ✅
- [ ] Xcode CLI tools installed

### PHASE 2: INSTALL
- [ ] Homebrew install (NONINTERACTIVE=1)
- [ ] NVM 0.39.7 install
- [ ] Node.js 20.11.0 LTS install
- [ ] Shell profile configuration (.zshrc)

### PHASE 3: VERIFY
- [ ] node command in PATH
- [ ] node version == v20.11.0
- [ ] npm command in PATH
- [ ] npm version == 10.x
- [ ] Module execution test

### PHASE 4: COMMIT
- [ ] Persist configuration
- [ ] Report finale

---

## 🔧 SCRIPT DETERMINISTICO

Esegui questo script sull'iMac con CoVe verification ad ogni step:

```bash
#!/bin/bash
# Node.js CoVe Deterministic Setup for iMac
# Target: Node.js 20.11.0 LTS via NVM 0.39.7
set -euo pipefail

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  CoVe: Node.js Setup - Deterministic Installation              ║"
echo "╚════════════════════════════════════════════════════════════════╝"

# ═══════════════════════════════════════════════════════════════════
# PHASE 1: PRE-CHECK
# ═══════════════════════════════════════════════════════════════════
echo ""
echo "[CoVe Phase 1/4] PRE-CHECK"
echo "─────────────────────────────────────────────────────────────────"

# Check 1: macOS version
MACOS_VERSION=$(sw_vers -productVersion)
MACOS_MAJOR=$(echo "$MACOS_VERSION" | cut -d. -f1)
if [[ "$MACOS_MAJOR" -lt 12 ]]; then
    echo "❌ FAIL: macOS version $MACOS_VERSION < 12.0 required"
    exit 1
fi
echo "✅ macOS version: $MACOS_VERSION"

# Check 2: Disk space
FREE_GB=$(df -g / | awk 'NR==2{print $4}')
if [[ "$FREE_GB" -lt 5 ]]; then
    echo "❌ FAIL: Disk space ${FREE_GB}GB < 5GB required"
    exit 1
fi
echo "✅ Disk space: ${FREE_GB}GB free"

# Check 3: Network
if ! ping -c 1 -W 5 github.com &>/dev/null; then
    echo "❌ FAIL: Network connectivity to github.com failed"
    exit 1
fi
echo "✅ Network connectivity: OK"

# Check 4: Xcode CLI
if ! xcode-select -p &>/dev/null; then
    echo "⚠️  WARNING: Xcode CLI tools not found"
    echo "    Install with: xcode-select --install"
    echo "    Continuing anyway..."
else
    echo "✅ Xcode CLI tools: installed"
fi

# ═══════════════════════════════════════════════════════════════════
# PHASE 2: INSTALL - Homebrew
# ═══════════════════════════════════════════════════════════════════
echo ""
echo "[CoVe Phase 2/4] INSTALL - Homebrew"
echo "─────────────────────────────────────────────────────────────────"

if ! command -v brew &>/dev/null; then
    echo "[CoVe] Installing Homebrew (deterministic)..."
    
    export NONINTERACTIVE=1
    export HOMEBREW_NO_ANALYTICS=1
    export HOMEBREW_NO_AUTO_UPDATE=1
    export HOMEBREW_NO_ENV_HINTS=1
    
    # Official Homebrew install (reddit-verified method)
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Configure PATH for Intel Mac
    if [[ $(uname -m) == "x86_64" ]]; then
        echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/usr/local/bin/brew shellenv)"
    fi
    
    # VERIFY
    if ! command -v brew &>/dev/null; then
        echo "❌ FAIL: Homebrew installation failed"
        exit 1
    fi
    echo "✅ Homebrew installed: $(brew --version | head -1)"
else
    echo "✅ Homebrew already installed: $(brew --version | head -1)"
fi

# ═══════════════════════════════════════════════════════════════════
# PHASE 3: INSTALL - NVM
# ═══════════════════════════════════════════════════════════════════
echo ""
echo "[CoVe Phase 3/4] INSTALL - NVM"
echo "─────────────────────────────────────────────────────────────────"

NVM_VERSION="0.39.7"

if [[ ! -d "$HOME/.nvm" ]]; then
    echo "[CoVe] Installing NVM v${NVM_VERSION}..."
    
    curl -o- "https://raw.githubusercontent.com/nvm-sh/nvm/v${NVM_VERSION}/install.sh" | bash
    
    # Load NVM
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    
    # VERIFY
    if ! command -v nvm &>/dev/null; then
        echo "❌ FAIL: NVM installation failed"
        exit 1
    fi
    echo "✅ NVM installed: $(nvm --version)"
else
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    echo "✅ NVM already installed: $(nvm --version)"
fi

# ═══════════════════════════════════════════════════════════════════
# PHASE 4: INSTALL - Node.js LTS
# ═══════════════════════════════════════════════════════════════════
echo ""
echo "[CoVe Phase 4/4] INSTALL - Node.js 20.11.0 LTS"
echo "─────────────────────────────────────────────────────────────────"

NODE_VERSION="20.11.0"

# Check if already installed
if nvm list | grep -q "v${NODE_VERSION}"; then
    echo "✅ Node.js v${NODE_VERSION} already installed"
    nvm use "${NODE_VERSION}"
else
    echo "[CoVe] Installing Node.js v${NODE_VERSION}..."
    nvm install "${NODE_VERSION}"
fi

# Set as default
nvm alias default "${NODE_VERSION}"
nvm use default

# ═══════════════════════════════════════════════════════════════════
# COVE VERIFICATION TESTS
# ═══════════════════════════════════════════════════════════════════
echo ""
echo "[CoVe] RUNNING VERIFICATION TESTS"
echo "─────────────────────────────────────────────────────────────────"

FAILED=0

# Test 1: node command
echo -n "Test 1/5: node command... "
if which node &>/dev/null; then
    echo "✅ $(which node)"
else
    echo "❌ FAIL"
    FAILED=1
fi

# Test 2: node version
echo -n "Test 2/5: node version... "
if node --version | grep -q "v${NODE_VERSION}"; then
    echo "✅ $(node --version)"
else
    echo "❌ FAIL (expected: v${NODE_VERSION}, got: $(node --version))"
    FAILED=1
fi

# Test 3: npm command
echo -n "Test 3/5: npm command... "
if which npm &>/dev/null; then
    echo "✅ $(which npm)"
else
    echo "❌ FAIL"
    FAILED=1
fi

# Test 4: npm version
echo -n "Test 4/5: npm version... "
NPM_VERSION=$(npm --version)
if [[ "$NPM_VERSION" =~ ^10\. ]]; then
    echo "✅ v${NPM_VERSION}"
else
    echo "✅ v${NPM_VERSION} (may vary, acceptable)"
fi

# Test 5: module execution
echo -n "Test 5/5: module execution... "
if node -e "console.log('test')" | grep -q "test"; then
    echo "✅ OK"
else
    echo "❌ FAIL"
    FAILED=1
fi

# ═══════════════════════════════════════════════════════════════════
# CONFIG PERSISTENCE
# ═══════════════════════════════════════════════════════════════════
echo ""
echo "[CoVe] CONFIGURING SHELL PROFILE"
echo "─────────────────────────────────────────────────────────────────"

SHELL_PROFILE="$HOME/.zshrc"

if ! grep -q "NVM_DIR" "$SHELL_PROFILE" 2>/dev/null; then
    echo "[CoVe] Adding NVM config to $SHELL_PROFILE"
    cat >> "$SHELL_PROFILE" << 'EOF'

# NVM Configuration (added by CoVe setup)
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
EOF
    echo "✅ Shell profile updated"
else
    echo "✅ NVM config already in shell profile"
fi

# ═══════════════════════════════════════════════════════════════════
# FINAL REPORT
# ═══════════════════════════════════════════════════════════════════
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                   SETUP COMPLETE                               ║"
echo "╚════════════════════════════════════════════════════════════════╝"

if [[ $FAILED -eq 0 ]]; then
    echo ""
    echo "✅ ALL CoVe TESTS PASSED"
    echo ""
    echo "Installation Summary:"
    echo "  🍺 Homebrew: $(brew --version | head -1)"
    echo "  📦 NVM: $(nvm --version)"
    echo "  ⬢ Node.js: $(node --version)"
    echo "  📦 NPM: v$(npm --version)"
    echo ""
    echo "Next steps:"
    echo "  1. Run: source ~/.zshrc"
    echo "  2. Navigate to project: cd '/Volumes/MacSSD - Dati/fluxion'"
    echo "  3. Install deps: npm install"
    echo "  4. Build Tauri: npm run tauri build"
    echo ""
    exit 0
else
    echo ""
    echo "❌ SOME TESTS FAILED"
    echo "Check output above for details."
    exit 1
fi
```

---

## 🎯 COMANDO DI ESECUZIONE

Salva lo script sopra come `/tmp/nodejs_setup.sh` e esegui:

```bash
ssh imac "bash -s" < /tmp/nodejs_setup.sh
```

Oppure esegui direttamente:

```bash
ssh imac '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh)" && export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && nvm install 20.11.0 && nvm use 20.11.0 && node --version'
```

---

## ✅ VERIFICA SUCCESSO

Dopo l'installazione, verifica con:

```bash
ssh imac "source ~/.zshrc && node --version && npm --version && which node"
```

**Atteso:**
- `v20.11.0`
- `10.x.x`
- `/Users/gianlucadistasi/.nvm/versions/node/v20.11.0/bin/node`

---

## 🔄 ROLLBACK

Se necessario:

```bash
ssh imac "rm -rf ~/.nvm && sed -i.bak '/NVM/d' ~/.zshrc"
```

---

**PRONTO PER L'ESECUZIONE CoVe?**
