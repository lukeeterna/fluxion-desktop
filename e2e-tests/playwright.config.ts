/**
 * FLUXION Enterprise Test Suite
 * Playwright Configuration - Enterprise Level
 *
 * Based on:
 * - https://playwright.dev/docs/best-practices
 * - https://github.com/mxschmitt/awesome-playwright
 * - https://betterstack.com/community/guides/testing/playwright-best-practices/
 */

import { defineConfig, devices } from '@playwright/test';
import path from 'path';

// Environment detection
const isCI = !!process.env.CI;
const baseURL = process.env.TAURI_DEV_URL || 'http://localhost:1420';

export default defineConfig({
  // =============================================================================
  // TEST DIRECTORY & PATTERNS
  // =============================================================================
  testDir: './tests',
  testMatch: '**/*.spec.ts',

  // =============================================================================
  // PARALLELIZATION - Enterprise Scale
  // =============================================================================
  fullyParallel: true,
  workers: isCI ? 4 : undefined, // Use 4 workers in CI, auto-detect locally

  // =============================================================================
  // RELIABILITY - Prevent Flaky Tests
  // =============================================================================
  retries: isCI ? 2 : 0, // Retry failed tests in CI only
  timeout: 30_000, // 30s per test
  expect: {
    timeout: 10_000, // 10s for assertions
  },

  // =============================================================================
  // REPORTING - Enterprise Grade
  // =============================================================================
  reporter: [
    // Console output
    ['list', { printSteps: true }],

    // HTML Report (local debugging)
    ['html', {
      outputFolder: 'reports/html',
      open: isCI ? 'never' : 'on-failure'
    }],

    // JUnit (CI/CD integration)
    ['junit', {
      outputFile: 'reports/junit/results.xml'
    }],

    // JSON (programmatic access)
    ['json', {
      outputFile: 'reports/json/results.json'
    }],

    // Allure (Enterprise reporting)
    ['allure-playwright', {
      outputFolder: '.allure-results',
      suiteTitle: 'FLUXION E2E Tests',
      environmentInfo: {
        'App': 'Fluxion Desktop',
        'Node': process.version,
        'Platform': process.platform,
      }
    }],
  ],

  // =============================================================================
  // ARTIFACTS - Debug Failures Fast
  // =============================================================================
  outputDir: 'reports/artifacts',

  use: {
    // Base URL for all tests
    baseURL,

    // Tracing - Capture everything for debugging
    trace: isCI ? 'on-first-retry' : 'retain-on-failure',

    // Screenshots on failure
    screenshot: 'only-on-failure',

    // Video recording
    video: isCI ? 'on-first-retry' : 'retain-on-failure',

    // Viewport consistency
    viewport: { width: 1280, height: 720 },

    // Locale for Italian app
    locale: 'it-IT',
    timezoneId: 'Europe/Rome',

    // Action timeouts
    actionTimeout: 10_000,
    navigationTimeout: 15_000,

    // Accessibility
    colorScheme: 'light',

    // Extra HTTP headers
    extraHTTPHeaders: {
      'Accept-Language': 'it-IT,it;q=0.9',
    },
  },

  // =============================================================================
  // BROWSER MATRIX - Cross-Platform
  // =============================================================================
  projects: [
    // Setup project - runs before all tests
    {
      name: 'setup',
      testMatch: /global\.setup\.ts/,
      teardown: 'teardown',
    },
    {
      name: 'teardown',
      testMatch: /global\.teardown\.ts/,
    },

    // Desktop browsers
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        channel: 'chrome', // Use stable Chrome
      },
      dependencies: ['setup'],
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
      dependencies: ['setup'],
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
      dependencies: ['setup'],
    },

    // Branded browsers (enterprise customers)
    {
      name: 'edge',
      use: {
        ...devices['Desktop Edge'],
        channel: 'msedge',
      },
      dependencies: ['setup'],
    },

    // Tauri WebView (primary target)
    {
      name: 'tauri-webview',
      use: {
        ...devices['Desktop Chrome'],
        // Tauri uses system WebView
        ignoreHTTPSErrors: true,
      },
      dependencies: ['setup'],
    },
  ],

  // =============================================================================
  // DEV SERVER - Auto-start Tauri
  // =============================================================================
  webServer: {
    command: 'npm run tauri dev',
    cwd: path.join(__dirname, '..'), // Run from project root
    url: baseURL,
    reuseExistingServer: !isCI,
    timeout: 120_000, // 2 min for Tauri startup
    stdout: 'pipe',
    stderr: 'pipe',
  },

  // =============================================================================
  // GLOBAL SETUP/TEARDOWN
  // =============================================================================
  globalSetup: path.join(__dirname, 'fixtures/global.setup.ts'),
  globalTeardown: path.join(__dirname, 'fixtures/global.teardown.ts'),

  // =============================================================================
  // METADATA
  // =============================================================================
  metadata: {
    project: 'FLUXION',
    version: process.env.npm_package_version || '0.1.0',
    environment: isCI ? 'ci' : 'local',
  },
});
