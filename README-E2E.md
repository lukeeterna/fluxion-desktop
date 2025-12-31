# 🧪 FLUXION - E2E Testing Guide (macOS Monterey)

End-to-End testing setup for FLUXION using **WebdriverIO** + **CrabNebula Tauri Driver** for macOS support.

---

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
- [Troubleshooting](#troubleshooting)
- [macOS Monterey Specific Notes](#macos-monterey-specific-notes)
- [CI/CD Integration](#cicd-integration)

---

## 🔧 Prerequisites

### System Requirements

- **macOS**: 12 Monterey or later (Intel or Apple Silicon)
- **Node.js**: 18+ or 20+
- **Rust**: Latest stable (via `rustup`)
- **Cargo**: Latest stable
- **Tauri CLI**: v2.x

### ⚠️ macOS Prerequisites - CrabNebula WebDriver REQUIRED

**IMPORTANT**: The standard Tauri WebDriver **does NOT support macOS** because there is no native WKWebView driver available.

On macOS, you **MUST** use CrabNebula's enhanced WebDriver with the test-runner-backend:

1. **Get CrabNebula API Key**:
   - Sign up at [https://crabnebula.dev](https://crabnebula.dev)
   - Copy your API key from the dashboard

2. **Configure Environment**:
   ```bash
   # Copy .env.e2e.example to .env.e2e
   cp .env.e2e.example .env.e2e

   # Edit .env.e2e and add your CN_API_KEY
   nano .env.e2e
   ```

   Add this line to `.env.e2e`:
   ```bash
   CN_API_KEY=your-api-key-here
   ```

3. **Install Dependencies** (includes CrabNebula drivers):
   ```bash
   npm install
   ```

   This installs:
   - `@crabnebula/tauri-driver` - Enhanced tauri-driver with macOS support
   - `@crabnebula/test-runner-backend` - Backend service for macOS WebDriver proxy

**Why CrabNebula?**
- Standard `tauri-driver` lacks WKWebView automation support
- CrabNebula provides the missing macOS WebDriver layer
- Enables full E2E testing on macOS Monterey and later

---

## 📦 Installation

### 1. Install Dependencies

```bash
# Install all dependencies including E2E tools
npm install
```

This will install:
- `@wdio/cli` - WebdriverIO test runner
- `@wdio/mocha-framework` - Mocha test framework
- `@wdio/local-runner` - Local test execution
- `@wdio/spec-reporter` - Test result reporter
- `@crabnebula/tauri-driver` - CrabNebula tauri-driver (macOS support)
- `@crabnebula/test-runner-backend` - Backend proxy for macOS
- `ts-node` - TypeScript execution
- `tsconfig-paths` - Path mapping support

### 2. Configure Environment (Already done in Prerequisites)

If you haven't already:
```bash
# Copy environment template
cp .env.e2e.example .env.e2e

# Add your CN_API_KEY
nano .env.e2e
```

### 3. Build Tauri App for Testing

```bash
# Build app without creating installer (faster)
npm run e2e:build:mac
```

This creates the test app at:
```
src-tauri/target/release/bundle/macos/FLUXION.app
```

---

## 🚀 Running Tests

### Quick Commands

```bash
# Run all E2E tests
npm run e2e:all

# Run tests only (skip build if already built)
npm run e2e:run:mac

# Run in headed mode (see browser window)
npm run e2e:headed:mac

# Run single test file for debugging
npm run e2e:debug:mac

# Run smoke test only
npm run e2e:smoke
```

### Detailed Commands

#### Full Test Suite
```bash
npm run e2e:build:mac   # Build app
npm run e2e:run:mac     # Run all tests
```

#### Run Specific Test
```bash
wdio run wdio.conf.ts --spec e2e/tests/03-clienti-crud.spec.ts
```

#### Debug Mode (headed + single test)
```bash
HEADLESS=false wdio run wdio.conf.ts --spec e2e/tests/01-smoke.spec.ts
```

---

## ✍️ Writing Tests

### Project Structure

```
e2e/
├── tests/                  # Test specs
│   ├── 01-smoke.spec.ts
│   ├── 02-navigation.spec.ts
│   ├── 03-clienti-crud.spec.ts
│   ├── 04-servizi-validation.spec.ts
│   └── 05-appuntamenti-conflict.spec.ts
├── pages/                  # Page Object Models
│   ├── BasePage.ts
│   ├── DashboardPage.ts
│   ├── ClientiPage.ts
│   ├── ServiziPage.ts
│   └── CalendarioPage.ts
├── fixtures/               # Test data
│   └── test-data.ts
├── utils/                  # Helper functions
│   └── test-helpers.ts
└── data/                   # Test artifacts
    └── screenshots/        # Failure screenshots
```

### Page Object Model Example

```typescript
import { BasePage } from './BasePage';

export class MyPage extends BasePage {
  get selectors() {
    return {
      button: '[data-testid="my-button"]',
      input: '[name="myInput"]',
    };
  }

  async clickButton(): Promise<void> {
    await this.click(this.selectors.button);
  }

  async fillInput(value: string): Promise<void> {
    await this.setValue(this.selectors.input, value);
  }
}

export const myPage = new MyPage();
```

### Writing a Test

```typescript
import { dashboardPage, clientiPage } from '../pages';
import { TestData } from '../fixtures/test-data';

describe('My Feature', () => {
  beforeEach(async () => {
    await dashboardPage.navigateToClienti();
  });

  it('should create a cliente', async () => {
    const cliente = TestData.clienti.getUnique();

    await clientiPage.createCliente(cliente);

    // Assertions
    const count = await clientiPage.getTableRowCount();
    expect(count).toBeGreaterThan(0);
  });
});
```

### Best Practices

1. **Use data-testid attributes** for stable selectors
2. **Use Page Objects** - Never use selectors directly in tests
3. **Avoid sleep/pause** - Use `waitFor*` methods instead
4. **Isolate tests** - Each test should be independent
5. **Clean up** - Use `afterEach`/`after` hooks to cleanup test data
6. **Take screenshots** on failure (done automatically)
7. **Use fixtures** for test data to avoid hardcoding

---

## 🐛 Troubleshooting

### Common Issues

#### 1. `tauri-driver` not found

**Error**: `spawn ENOENT tauri-driver`

**Solution**:
```bash
# Make sure you ran npm install
npm install

# Verify node_modules/.bin has the driver
ls -la node_modules/.bin/tauri-driver

# If missing, reinstall CrabNebula packages
npm install @crabnebula/tauri-driver @crabnebula/test-runner-backend
```

**Note**: On macOS, tauri-driver is installed via npm (not cargo). The driver is located in `node_modules/.bin/tauri-driver`.

#### 2. App build fails

**Error**: `Tauri build failed with exit code 1`

**Solution**:
```bash
# Build manually to see detailed error
npm run tauri build -- -b none

# Common fixes:
# - Update Rust: rustup update
# - Clean build: cd src-tauri && cargo clean
# - Update Tauri: cargo update -p tauri
```

#### 3. Tests timeout

**Error**: `Timeout waiting for element`

**Solution**:
- Increase timeout in `wdio.conf.ts` (`waitforTimeout`)
- Check if app is actually running: `ps aux | grep FLUXION`
- Check console logs in `e2e/data/screenshots/`

#### 4. WebDriver connection refused

**Error**: `connect ECONNREFUSED 127.0.0.1:4444`

**Solution**:
```bash
# Ensure tauri-driver is running
ps aux | grep tauri-driver

# If not running, check beforeSession hook in wdio.conf.ts
# Try manual start:
tauri-driver
```

#### 5. macOS Accessibility Permissions

**Error**: `Failed to connect to WebDriver`

**Solution**:
1. Open **System Preferences** → **Security & Privacy** → **Privacy** → **Accessibility**
2. Add **Terminal** (or your IDE) to the list
3. Restart Terminal and try again

#### 6. CN_API_KEY not set (macOS)

**Error**: `CN_API_KEY environment variable is not set!`

**Solution**:
```bash
# Copy environment template if you haven't
cp .env.e2e.example .env.e2e

# Edit .env.e2e and add your CrabNebula API key
nano .env.e2e

# Add this line:
# CN_API_KEY=your-api-key-from-crabnebula-dashboard

# Get your key from: https://crabnebula.dev
```

**Note**: CN_API_KEY is REQUIRED on macOS. Without it, the test-runner-backend cannot start.

#### 7. Screenshots not saved

**Error**: Screenshots directory not found

**Solution**:
```bash
mkdir -p e2e/data/screenshots
```

---

## 🍎 macOS Monterey Specific Notes

### Why CrabNebula Driver?

- Standard `tauri-driver` **doesn't support macOS** (no WKWebView automation layer)
- CrabNebula provides `@crabnebula/tauri-driver` + `test-runner-backend` to bridge this gap
- The `test-runner-backend` acts as a proxy that translates WebDriver commands to macOS-compatible WKWebView automation
- **REQUIRED** for running E2E tests on iMac Monterey (or any macOS machine)

### How it Works on macOS

1. **wdio.conf.ts** starts `test-runner-backend` (requires CN_API_KEY)
2. Backend listens on `http://127.0.0.1:3000`
3. **tauri-driver** connects to backend via `REMOTE_WEBDRIVER_URL`
4. Backend translates WebDriver commands → WKWebView automation
5. Your tests run normally through WebdriverIO

### iMac Intel AVX1 Considerations

- **No performance issues** with WebdriverIO
- **Headless mode** may be slower on older Macs → use headed mode for debugging
- **Build times**: 30-60 seconds for test builds (normal)

### Multi-Machine Workflow

**Development (MacBook)**:
```bash
# Write code and tests
git add e2e/
git commit -m "Add E2E tests"
git push
```

**Testing (iMac Monterey)**:
```bash
cd "/Volumes/MacSSD - Dati/fluxion"
git pull
npm install  # If dependencies changed

# Make sure .env.e2e exists with CN_API_KEY
# (You only need to do this once)
cp .env.e2e.example .env.e2e
nano .env.e2e  # Add CN_API_KEY=your-key

# Run tests
npm run e2e:all
```

### Monterey-Specific Commands

```bash
# Check macOS version
sw_vers

# Check if Tauri app can run
open src-tauri/target/release/bundle/macos/FLUXION.app

# Kill stuck processes
pkill -f tauri-driver
pkill -f test-runner-backend
pkill -f FLUXION

# Check if test-runner-backend is running
ps aux | grep test-runner-backend

# Manually test backend connection
curl http://127.0.0.1:3000/status
```

---

## 🔄 CI/CD Integration

### GitHub Actions (Future)

```yaml
# .github/workflows/e2e-macos.yml
name: E2E Tests macOS

on: [push, pull_request]

jobs:
  e2e:
    runs-on: macos-12  # Monterey
    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-node@v3
        with:
          node-version: '20'

      - name: Install Rust
        uses: actions-rs/toolchain@v1
        with:
          toolchain: stable

      - name: Install dependencies
        run: npm install

      - name: Setup E2E environment
        run: |
          cp .env.e2e.example .env.e2e
          echo "CN_API_KEY=${{ secrets.CN_API_KEY }}" >> .env.e2e

      - name: Run E2E tests
        run: npm run e2e:all
        env:
          CN_API_KEY: ${{ secrets.CN_API_KEY }}

      - name: Upload screenshots
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: e2e-screenshots
          path: e2e/data/screenshots/
```

**Note**: Add `CN_API_KEY` to your GitHub repository secrets:
1. Go to repository **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `CN_API_KEY`
4. Value: Your CrabNebula API key

---

## 📊 Test Coverage Goals

- [x] Smoke tests (app launch, navigation)
- [x] CRUD operations (Clienti, Servizi, Operatori)
- [x] Form validation (Servizi BUG #3 regression)
- [x] Conflict detection (Appuntamenti BUG #1, #2 regression)
- [ ] Calendar navigation and display
- [ ] Date/time edge cases
- [ ] Multi-user scenarios
- [ ] Performance tests (1000+ records)
- [ ] Error recovery
- [ ] Network failure handling

---

## 🎯 Next Steps

1. **Add data-testid attributes** to UI components
2. **Implement database cleanup** for isolated tests
3. **Add visual regression** testing (optional)
4. **Setup CI/CD** pipeline
5. **Add accessibility** tests
6. **Measure test coverage** metrics

---

## 📝 Useful Links

- [WebdriverIO Docs](https://webdriver.io/docs/gettingstarted)
- [Tauri Testing Guide](https://tauri.app/v1/guides/testing/webdriver/introduction)
- [CrabNebula Tauri Driver](https://github.com/crabnebula-dev/tauri-driver)
- [Page Object Model Pattern](https://webdriver.io/docs/pageobjects)

---

## 🆘 Getting Help

If you encounter issues:

1. Check `e2e/data/screenshots/` for failure screenshots
2. Review logs in terminal output
3. Try running a single test with `--spec`
4. Enable headed mode with `e2e:headed:mac`
5. Check this README's Troubleshooting section

---

**Happy Testing!** 🧪✨
