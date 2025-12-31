// ═══════════════════════════════════════════════════════════════════
// FLUXION - WebdriverIO Configuration for E2E Tests (macOS Monterey)
// Using CrabNebula Tauri Driver for macOS support
// ═══════════════════════════════════════════════════════════════════

import os from 'os';
import path from 'path';
import { spawn, spawnSync, ChildProcess } from 'child_process';
import type { Options } from '@wdio/types';

// Keep track of the tauri-driver child process
let tauriDriver: ChildProcess | null = null;

export const config: Options.Testrunner = {
  // ───────────────────────────────────────────────────────────────────
  // Test Specs
  // ───────────────────────────────────────────────────────────────────
  specs: ['./e2e/tests/**/*.spec.ts'],
  exclude: [
    // 'path/to/excluded/files'
  ],

  // ───────────────────────────────────────────────────────────────────
  // Capabilities
  // ───────────────────────────────────────────────────────────────────
  maxInstances: 1, // Run tests serially (Tauri limitation)
  capabilities: [
    {
      maxInstances: 1,
      'tauri:options': {
        // Path to built Tauri app (macOS .app bundle)
        application: path.join(
          process.cwd(),
          'src-tauri',
          'target',
          'release',
          'bundle',
          'macos',
          'FLUXION.app'
        ),
      },
    },
  ],

  // ───────────────────────────────────────────────────────────────────
  // Test Configuration
  // ───────────────────────────────────────────────────────────────────
  logLevel: 'info',
  bail: 0, // Run all tests even if some fail
  baseUrl: 'tauri://localhost', // Tauri app URL
  waitforTimeout: 10000, // Default timeout for wait* commands
  connectionRetryTimeout: 120000,
  connectionRetryCount: 3,

  // Test runner services
  services: [], // CrabNebula driver doesn't need services, we spawn manually

  // ───────────────────────────────────────────────────────────────────
  // Framework
  // ───────────────────────────────────────────────────────────────────
  framework: 'mocha',
  reporters: ['spec'],

  mochaOpts: {
    ui: 'bdd',
    timeout: 60000, // 60 seconds per test
    require: ['tsconfig-paths/register'],
  },

  // ───────────────────────────────────────────────────────────────────
  // Hooks
  // ───────────────────────────────────────────────────────────────────

  /**
   * Build Tauri app before tests run
   * Uses 'none' bundler to just compile without creating installers
   */
  onPrepare: function () {
    console.log('🔨 Building Tauri app for E2E tests...');

    const result = spawnSync('npm', ['run', 'tauri', 'build', '--', '-b', 'none'], {
      stdio: 'inherit',
      shell: true,
    });

    if (result.error) {
      throw new Error(`Failed to build Tauri app: ${result.error.message}`);
    }

    if (result.status !== 0) {
      throw new Error(`Tauri build failed with exit code ${result.status}`);
    }

    console.log('✅ Tauri app built successfully');
  },

  /**
   * Start CrabNebula tauri-driver before session starts
   * This driver proxies WebDriver requests to Tauri app
   */
  beforeSession: function () {
    console.log('🚀 Starting CrabNebula tauri-driver...');

    const driverPath = path.resolve(os.homedir(), '.cargo', 'bin', 'tauri-driver');

    tauriDriver = spawn(driverPath, [], {
      stdio: [null, process.stdout, process.stderr],
    });

    // Give driver time to start
    return new Promise((resolve) => setTimeout(resolve, 2000));
  },

  /**
   * Kill tauri-driver after session ends
   */
  afterSession: function () {
    if (tauriDriver) {
      console.log('🛑 Stopping tauri-driver...');
      tauriDriver.kill();
      tauriDriver = null;
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
