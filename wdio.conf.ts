// ═══════════════════════════════════════════════════════════════════
// FLUXION - WebdriverIO Configuration for E2E Tests
// Using native tauri-driver (NO CrabNebula dependency)
// ═══════════════════════════════════════════════════════════════════

import path from 'path';
import { spawn, spawnSync, ChildProcess } from 'child_process';
import type { Options } from '@wdio/types';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Keep track of tauri-driver process
let tauriDriver: ChildProcess | null = null;

// Platform detection
const isMacOS = process.platform === 'darwin';
const isWindows = process.platform === 'win32';

// Determine app path based on platform
// Uses debug build for faster iteration, release for CI
function getAppPath(): string {
  const isCI = process.env.CI === 'true';
  const buildType = isCI ? 'release' : 'debug';
  const basePath = path.join(__dirname, 'src-tauri', 'target', buildType);

  if (isMacOS) {
    // macOS: bundle/macos/AppName.app/Contents/MacOS/AppName
    return path.join(basePath, 'bundle', 'macos', 'Fluxion.app', 'Contents', 'MacOS', 'Fluxion');
  } else if (isWindows) {
    // Windows: direct executable
    return path.join(basePath, 'Fluxion.exe');
  } else {
    // Linux: direct executable
    return path.join(basePath, 'fluxion');
  }
}

// Wait for tauri-driver to be ready by polling the WebDriver endpoint
async function waitForTauriDriver(timeout = 30000): Promise<void> {
  const startTime = Date.now();
  const checkUrl = 'http://127.0.0.1:4444/status';

  while (Date.now() - startTime < timeout) {
    try {
      const response = await fetch(checkUrl);
      if (response.ok) {
        return;
      }
    } catch {
      // Not ready yet, continue waiting
    }
    await new Promise((resolve) => setTimeout(resolve, 500));
  }

  throw new Error(`tauri-driver not ready after ${timeout}ms`);
}

export const config: Options.Testrunner = {
  // ───────────────────────────────────────────────────────────────────
  // Test Specs
  // ───────────────────────────────────────────────────────────────────
  specs: ['./e2e/tests/**/*.spec.ts'],
  exclude: [
    // Exclude old spec files with import issues
    './e2e/tests/01-smoke.spec.ts',
    './e2e/tests/02-navigation.spec.ts',
    './e2e/tests/03-clienti-crud.spec.ts',
    './e2e/tests/04-servizi-validation.spec.ts',
    './e2e/tests/05-appuntamenti-conflict.spec.ts',
  ],

  // ───────────────────────────────────────────────────────────────────
  // Capabilities
  // ───────────────────────────────────────────────────────────────────
  maxInstances: 1, // Run tests serially (Tauri limitation)

  // Connect to tauri-driver on port 4444
  hostname: '127.0.0.1',
  port: 4444,

  capabilities: [
    {
      maxInstances: 1,
      browserName: 'wry', // Tauri WebView engine
      'tauri:options': {
        application: getAppPath(),
      },
    },
  ],

  // ───────────────────────────────────────────────────────────────────
  // Test Configuration
  // ───────────────────────────────────────────────────────────────────
  logLevel: 'info',
  bail: 0,
  baseUrl: 'tauri://localhost',
  waitforTimeout: 10000,
  connectionRetryTimeout: 120000,
  connectionRetryCount: 3,

  services: [],

  // ───────────────────────────────────────────────────────────────────
  // Framework
  // ───────────────────────────────────────────────────────────────────
  framework: 'mocha',
  reporters: [
    'spec',
    ['json', {
      outputDir: './e2e/reports',
      outputFileFormat: () => `results-${Date.now()}.json`,
    }],
  ],

  mochaOpts: {
    ui: 'bdd',
    timeout: 60000,
  },

  // ───────────────────────────────────────────────────────────────────
  // Hooks
  // ───────────────────────────────────────────────────────────────────

  /**
   * Start tauri-driver before all tests
   * tauri-driver is installed via: cargo install tauri-driver
   */
  onPrepare: async function () {
    console.log('🚀 Starting tauri-driver for E2E tests...');
    console.log(`📱 Platform: ${process.platform}`);
    console.log(`📂 App path: ${getAppPath()}`);

    // Verify app exists
    const appPath = getAppPath();
    try {
      const fs = await import('fs');
      if (!fs.existsSync(appPath)) {
        console.error(`❌ App not found at: ${appPath}`);
        console.error('💡 Run: npm run tauri build -- --debug');
        throw new Error(`Tauri app not found at ${appPath}`);
      }
      console.log('✅ App binary found');
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
        throw new Error(`Tauri app not found at ${appPath}. Build it first with: npm run tauri build -- --debug`);
      }
      throw error;
    }

    // Start tauri-driver (must be installed globally via cargo install tauri-driver)
    tauriDriver = spawn('tauri-driver', [], {
      stdio: ['ignore', 'pipe', 'pipe'],
    });

    tauriDriver.stdout?.on('data', (data) => {
      const msg = data.toString().trim();
      if (msg) console.log(`[tauri-driver] ${msg}`);
    });

    tauriDriver.stderr?.on('data', (data) => {
      const msg = data.toString().trim();
      // Filter out common warnings
      if (!msg.includes('WARN') && msg) {
        console.error(`[tauri-driver] ${msg}`);
      }
    });

    tauriDriver.on('error', (error) => {
      console.error('❌ Failed to start tauri-driver:', error);
      console.error('💡 Install it with: cargo install tauri-driver');
    });

    tauriDriver.on('exit', (code) => {
      if (code !== 0 && code !== null) {
        console.error(`⚠️ tauri-driver exited with code ${code}`);
      }
    });

    // Wait for tauri-driver to be ready
    console.log('⏳ Waiting for tauri-driver to be ready...');
    try {
      await waitForTauriDriver(30000);
      console.log('✅ tauri-driver is ready on port 4444');
    } catch (error) {
      console.error('❌ tauri-driver failed to start');
      if (tauriDriver) {
        tauriDriver.kill();
      }
      throw error;
    }

    // Give extra time for connection to stabilize
    await new Promise((resolve) => setTimeout(resolve, 1000));
  },

  /**
   * Cleanup: Kill tauri-driver
   */
  onComplete: function () {
    if (tauriDriver) {
      console.log('🛑 Stopping tauri-driver...');
      tauriDriver.kill();
      tauriDriver = null;
    }
    console.log('✅ E2E tests complete');
  },

  /**
   * Before each test
   */
  beforeTest: function (test) {
    console.log(`\n📝 Running: ${test.parent} > ${test.title}`);
  },

  /**
   * After each test - capture screenshot on failure
   */
  afterTest: async function (test, context, { error }) {
    if (error) {
      const timestamp = new Date().toISOString().replace(/:/g, '-');
      const testName = test.title.replace(/\s+/g, '-').toLowerCase();
      const screenshotDir = './e2e/reports/screenshots';
      const screenshotPath = `${screenshotDir}/failure-${testName}-${timestamp}.png`;

      try {
        // Ensure directory exists
        const fs = await import('fs');
        if (!fs.existsSync(screenshotDir)) {
          fs.mkdirSync(screenshotDir, { recursive: true });
        }

        await browser.saveScreenshot(screenshotPath);
        console.log(`📸 Screenshot saved: ${screenshotPath}`);
      } catch (screenshotError) {
        console.error('Failed to save screenshot:', screenshotError);
      }
    }
  },
};
