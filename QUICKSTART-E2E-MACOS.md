# 🚀 Quick Start: E2E Testing on macOS (iMac Monterey)

> **5-minute setup guide** for running E2E tests on macOS using CrabNebula WebDriver

---

## ⚠️ Prerequisites

Before starting, make sure you have:

1. **macOS 12 Monterey or later** (required for Tauri 2.x)
2. **Node.js 18+** installed (`node --version`)
3. **Git** configured with GitHub access
4. **CrabNebula API Key** (get it from [https://crabnebula.dev](https://crabnebula.dev))

---

## 📋 Step-by-Step Setup

### 1. Clone/Sync Repository

```bash
# Navigate to your working directory
cd "/Volumes/MacSSD - Dati/fluxion"

# Pull latest changes from GitHub
git pull

# Or clone from scratch if needed
# git clone https://github.com/lukeeterna/fluxion-desktop.git
# cd fluxion-desktop
```

### 2. Install Dependencies

```bash
# Install all npm dependencies (including CrabNebula drivers)
npm install
```

This installs:
- `@crabnebula/tauri-driver` - Enhanced tauri-driver with macOS support
- `@crabnebula/test-runner-backend` - Backend proxy for WKWebView automation
- `@wdio/cli` - WebdriverIO test runner
- All other project dependencies

### 3. Configure Environment

```bash
# Copy environment template
cp .env.e2e.example .env.e2e

# Edit .env.e2e and add your CN_API_KEY
nano .env.e2e
```

**Add this line to `.env.e2e`:**
```bash
CN_API_KEY=your-crabnebula-api-key-here
```

**Where to get your API key:**
1. Go to [https://crabnebula.dev](https://crabnebula.dev)
2. Sign up or log in
3. Copy your API key from the dashboard
4. Paste it in `.env.e2e`

### 4. Build Tauri App with E2E Features

```bash
# Build app with automation plugin enabled
npm run e2e:build:mac
```

This command:
- Builds Tauri app in release mode
- Enables the `e2e` feature (tauri-plugin-automation)
- Creates app bundle at: `src-tauri/target/release/bundle/macos/FLUXION.app`
- Takes ~30-60 seconds on Intel Macs

### 5. Run E2E Tests

```bash
# Run all E2E tests
npm run e2e:all

# Or run tests only (skip build if already built)
npm run e2e:run:mac

# Run in headed mode (see app window)
npm run e2e:headed:mac

# Run smoke test only
npm run e2e:smoke

# Debug single test
npm run e2e:debug:mac
```

---

## 🎯 Quick Command Reference

| Command | Description |
|---------|-------------|
| `npm run e2e:all` | Build app + run all tests (full suite) |
| `npm run e2e:build:mac` | Build app with E2E features enabled |
| `npm run e2e:run:mac` | Run tests (app must be built first) |
| `npm run e2e:headed:mac` | Run tests with visible app window |
| `npm run e2e:smoke` | Run smoke test only (fast) |
| `npm run e2e:debug:mac` | Debug mode (headed + single test) |

---

## 🔧 Troubleshooting

### CN_API_KEY Not Set

**Error:**
```
❌ ERROR: CN_API_KEY environment variable is not set!
```

**Fix:**
```bash
# Make sure .env.e2e exists and has CN_API_KEY
cat .env.e2e | grep CN_API_KEY

# If missing, add it:
echo "CN_API_KEY=your-api-key-here" >> .env.e2e
```

### tauri-driver Not Found

**Error:**
```
spawn ENOENT tauri-driver
```

**Fix:**
```bash
# Reinstall CrabNebula packages
npm install @crabnebula/tauri-driver @crabnebula/test-runner-backend

# Verify installation
ls -la node_modules/.bin/tauri-driver
```

### App Build Fails

**Error:**
```
Tauri build failed with exit code 1
```

**Fix:**
```bash
# Update Rust
rustup update

# Clean build cache
cd src-tauri && cargo clean && cd ..

# Try building manually to see detailed error
npm run tauri build -- -b none --features e2e
```

### test-runner-backend Not Starting

**Error:**
```
❌ test-runner-backend failed to start
```

**Fix:**
```bash
# Check if CN_API_KEY is valid
cat .env.e2e | grep CN_API_KEY

# Manually test backend
node_modules/.bin/test-runner-backend

# Kill stuck processes
pkill -f test-runner-backend
pkill -f tauri-driver
```

### Tests Timeout

**Error:**
```
Timeout waiting for element
```

**Fix:**
1. Increase timeout in `wdio.conf.ts` (already set to 60s)
2. Check if app actually launched: `ps aux | grep FLUXION`
3. Run in headed mode to see what's happening: `npm run e2e:headed:mac`
4. Check screenshots in `e2e/data/screenshots/`

---

## 🔄 Daily Workflow

### On MacBook (Development)

```bash
# Make code changes
# ...

# Commit and push
git add .
git commit -m "Your changes"
git push
```

### On iMac (Testing)

```bash
# 1. Pull latest changes
cd "/Volumes/MacSSD - Dati/fluxion"
git pull

# 2. Install dependencies if package.json changed
npm install

# 3. Run E2E tests
npm run e2e:all
```

---

## 📊 What Gets Tested

The E2E test suite covers:

- ✅ **Smoke tests** - App launch, basic navigation
- ✅ **Clienti CRUD** - Create, read, update, delete clients
- ✅ **Servizi validation** - Form validation, BUG #3 regression
- ✅ **Appuntamenti conflict** - Date/time conflicts, BUG #1 & #2 regression
- ✅ **Navigation** - All pages accessible

---

## 🆘 Getting Help

If you encounter issues:

1. Check `e2e/data/screenshots/` for failure screenshots
2. Review terminal output for error messages
3. Run single test with `--spec` flag for isolation
4. Enable headed mode to see what's happening
5. Read the full guide: `README-E2E.md`
6. Check documentation: `INTEGRATION-TAURI-AUTOMATION.md`

---

## 🔍 Understanding the Setup

### Why CrabNebula?

- Standard `tauri-driver` **doesn't support macOS** (no WKWebView driver)
- CrabNebula provides the missing macOS automation layer
- Requires API key + test-runner-backend service

### How It Works

1. `wdio.conf.ts` starts `test-runner-backend` (requires CN_API_KEY)
2. Backend listens on `http://127.0.0.1:3000`
3. `tauri-driver` connects to backend via `REMOTE_WEBDRIVER_URL`
4. Backend translates WebDriver commands → WKWebView automation
5. Your tests run normally through WebdriverIO

### Why the e2e Feature?

- `tauri-plugin-automation` is **REQUIRED** for macOS CrabNebula setup
- Enables test-runner-backend to inject automation hooks into app
- Built with `--features e2e` flag in `npm run e2e:build:mac`

---

## 📚 Additional Resources

- [Full E2E Guide](README-E2E.md) - Comprehensive documentation
- [Plugin Integration](INTEGRATION-TAURI-AUTOMATION.md) - Automation plugin details
- [WebdriverIO Docs](https://webdriver.io/docs/gettingstarted) - Testing framework
- [CrabNebula Tauri Driver](https://github.com/crabnebula-dev/tauri-driver) - macOS driver
- [CrabNebula Dashboard](https://crabnebula.dev) - Get your API key

---

**Happy Testing!** 🧪✨
