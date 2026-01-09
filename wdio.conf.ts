// ═══════════════════════════════════════════════════════════════════
// FLUXION - WebdriverIO Configuration for E2E Tests (macOS Monterey)
// Using CrabNebula Tauri Driver for macOS support
// ═══════════════════════════════════════════════════════════════════

import os from 'os';
import path from 'path';
import { spawn, spawnSync, ChildProcess } from 'child_process';
import type { Options } from '@wdio/types';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config({ path: '.env.e2e' });

// Import CrabNebula wait helpers (REQUIRED for macOS)
import { waitTauriDriverReady } from '@crabnebula/tauri-driver';
import { waitTestRunnerBackendReady } from '@crabnebula/test-runner-backend';

// Keep track of child processes
let tauriDriver: ChildProcess | null = null;
let testRunnerBackend: ChildProcess | null = null;

// Platform detection
const isMacOS = process.platform === 'darwin';
const isWindows = process.platform === 'win32';
const isLinux = process.platform === 'linux';

// Determine app path based on platform (using debug build for faster E2E)
function getAppPath(): string {
  const basePath = path.join(process.cwd(), 'src-tauri', 'target', 'debug');

  if (isMacOS) {
    return path.join(basePath, 'bundle', 'macos', 'Fluxion.app');
  } else if (isWindows) {
    return path.join(basePath, 'tauri-app.exe');
  } else {
    // Linux
    return path.join(basePath, 'tauri-app');
  }
}

export const config: Options.Testrunner = {
  // ───────────────────────────────────────────────────────────────────
  // Test Specs
  // ───────────────────────────────────────────────────────────────────
  specs: ['./e2e/tests/**/*.spec.ts'],
  // Exclude old spec files with import issues (use page objects)
  exclude: [
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
  reporters: ['spec'],

  mochaOpts: {
    ui: 'bdd',
    timeout: 60000,
  },

  // ───────────────────────────────────────────────────────────────────
  // Hooks
  // ───────────────────────────────────────────────────────────────────

  /**
   * Build Tauri app and start CrabNebula test-runner-backend (macOS only)
   */
  onPrepare: async function () {
    console.log('🔨 Building Tauri app for E2E tests...');

    // Build app (debug mode for faster builds, with e2e feature for automation plugin)
    const buildResult = spawnSync('npm', ['run', 'tauri', 'build', '--', '--debug', '--features', 'e2e'], {
      stdio: 'inherit',
      shell: true,
    });

    if (buildResult.error) {
      throw new Error(`Failed to build Tauri app: ${buildResult.error.message}`);
    }

    if (buildResult.status !== 0) {
      throw new Error(`Tauri build failed with exit code ${buildResult.status}`);
    }

    console.log('✅ Tauri app built successfully');

    // ───────────────────────────────────────────────────────────────────
    // macOS ONLY: Start CrabNebula test-runner-backend
    // ───────────────────────────────────────────────────────────────────
    if (isMacOS) {
      console.log('🍎 macOS detected: Starting CrabNebula test-runner-backend...');

      // Check CN_API_KEY is set (REQUIRED for macOS)
      if (!process.env.CN_API_KEY) {
        console.error('\n❌ ERROR: CN_API_KEY environment variable is not set!');
        console.error('');
        console.error('CrabNebula WebDriver is REQUIRED for macOS E2E testing.');
        console.error('Standard tauri-driver does NOT support macOS (no WKWebView driver).');
        console.error('');
        console.error('Steps to fix:');
        console.error('1. Get your API key from: https://crabnebula.dev');
        console.error('2. Copy .env.e2e.example to .env.e2e');
        console.error('3. Set CN_API_KEY=your-api-key in .env.e2e');
        console.error('');
        throw new Error('CN_API_KEY required for macOS E2E tests');
      }

      // Find test-runner-backend binary
      const backendBin = path.join(
        process.cwd(),
        'node_modules',
        '.bin',
        'test-runner-backend'
      );

      // Start test-runner-backend as child process
      testRunnerBackend = spawn(backendBin, [], {
        stdio: ['ignore', 'pipe', 'pipe'],
        env: {
          ...process.env,
          CN_API_KEY: process.env.CN_API_KEY,
        },
      });

      testRunnerBackend.stdout?.on('data', (data) => {
        console.log(`[test-runner-backend] ${data.toString().trim()}`);
      });

      testRunnerBackend.stderr?.on('data', (data) => {
        console.error(`[test-runner-backend ERROR] ${data.toString().trim()}`);
      });

      testRunnerBackend.on('error', (error) => {
        console.error('Failed to start test-runner-backend:', error);
      });

      // Wait for backend to be ready (with timeout)
      console.log('⏳ Waiting for test-runner-backend to be ready...');
      try {
        await waitTestRunnerBackendReady({ timeout: 30000 });
        console.log('✅ test-runner-backend is ready');
      } catch (error) {
        console.error('❌ test-runner-backend failed to start:', error);
        if (testRunnerBackend) {
          testRunnerBackend.kill();
        }
        throw error;
      }

      // Set REMOTE_WEBDRIVER_URL to point tauri-driver to the backend
      // Default backend port is 3000
      process.env.REMOTE_WEBDRIVER_URL = 'http://127.0.0.1:3000';
      console.log(`✅ REMOTE_WEBDRIVER_URL set to: ${process.env.REMOTE_WEBDRIVER_URL}`);
    } else {
      console.log(`ℹ️  Platform: ${process.platform} (test-runner-backend not needed)`);
    }

    // ───────────────────────────────────────────────────────────────────
    // Start tauri-driver ONCE (before all tests)
    // ───────────────────────────────────────────────────────────────────
    console.log('🚀 Starting tauri-driver...');

    // Find tauri-driver binary
    const driverBin = path.join(process.cwd(), 'node_modules', '.bin', 'tauri-driver');

    // Start tauri-driver as child process
    tauriDriver = spawn(driverBin, [], {
      stdio: ['ignore', 'pipe', 'pipe'],
      env: {
        ...process.env,
        // REMOTE_WEBDRIVER_URL is set above for macOS
      },
    });

    tauriDriver.stdout?.on('data', (data) => {
      console.log(`[tauri-driver] ${data.toString().trim()}`);
    });

    tauriDriver.stderr?.on('data', (data) => {
      // Filter out common warnings
      const msg = data.toString().trim();
      if (!msg.includes('WARN')) {
        console.error(`[tauri-driver ERROR] ${msg}`);
      }
    });

    tauriDriver.on('error', (error) => {
      console.error('Failed to start tauri-driver:', error);
    });

    // Wait for tauri-driver to be ready (with timeout)
    console.log('⏳ Waiting for tauri-driver to be ready...');
    try {
      await waitTauriDriverReady({ timeout: 30000 });
      console.log('✅ tauri-driver is ready');
    } catch (error) {
      console.error('❌ tauri-driver failed to start:', error);
      if (tauriDriver) {
        tauriDriver.kill();
      }
      throw error;
    }

    // Give extra time for connection to stabilize
    await new Promise((resolve) => setTimeout(resolve, 2000));
  },

  /**
   * Cleanup: Kill tauri-driver and test-runner-backend
   */
  onComplete: function () {
    if (tauriDriver) {
      console.log('🛑 Stopping tauri-driver...');
      tauriDriver.kill();
      tauriDriver = null;
    }
    if (testRunnerBackend) {
      console.log('🛑 Stopping test-runner-backend...');
      testRunnerBackend.kill();
      testRunnerBackend = null;
    }
  },

  /**
   * Before each test
   */
  beforeTest: function (test, context) {
    console.log(`\n📝 Running: ${test.parent} > ${test.title}`);
  },

  /**
   * After each test - capture screenshot on failure
   */
  afterTest: async function (test, context, { error, result, duration, passed, retries }) {
    if (error) {
      const timestamp = new Date().toISOString().replace(/:/g, '-');
      const testName = test.title.replace(/\s+/g, '-').toLowerCase();
      const screenshotPath = `./e2e/data/screenshots/failure-${testName}-${timestamp}.png`;

      try {
        await browser.saveScreenshot(screenshotPath);
        console.log(`📸 Screenshot saved: ${screenshotPath}`);
      } catch (screenshotError) {
        console.error('Failed to save screenshot:', screenshotError);
      }
    }
  },
};
