/**
 * Playwright CI Configuration
 *
 * Optimized for CI/CD pipelines:
 * - Reduced parallelism to prevent resource exhaustion
 * - Increased timeouts for slower CI environments
 * - Artifacts for debugging failures
 */

import { defineConfig, devices } from '@playwright/test';
import path from 'path';

export default defineConfig({
  testDir: './tests',
  fullyParallel: false, // Sequential in CI to reduce flakiness
  forbidOnly: true, // Fail if test.only is left in code
  retries: 2, // Retry failed tests twice
  workers: 2, // Limited workers in CI

  reporter: [
    ['github'], // GitHub Actions annotations
    ['html', { outputFolder: 'reports/html', open: 'never' }],
    ['junit', { outputFile: 'reports/junit/results.xml' }],
    ['json', { outputFile: 'reports/json/results.json' }],
    ['allure-playwright', { outputFolder: '.allure-results' }],
  ],

  timeout: 60_000, // 60 seconds per test
  expect: {
    timeout: 10_000,
  },

  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:1420',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'on-first-retry',
    actionTimeout: 15_000,
    navigationTimeout: 30_000,
    locale: 'it-IT',
    timezoneId: 'Europe/Rome',
  },

  projects: [
    // Run setup first
    {
      name: 'setup',
      testMatch: /global\.setup\.ts/,
    },

    // Main browser tests
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
      },
      dependencies: ['setup'],
    },

    // Only run webkit on macOS
    ...(process.platform === 'darwin'
      ? [
          {
            name: 'webkit',
            use: {
              ...devices['Desktop Safari'],
            },
            dependencies: ['setup'],
          },
        ]
      : []),

    // Teardown after all tests
    {
      name: 'teardown',
      testMatch: /global\.teardown\.ts/,
      dependencies: ['chromium'],
    },
  ],

  // No auto-start webServer in CI (app should already be running)
  webServer: process.env.CI
    ? undefined
    : {
        command: 'npm run tauri dev',
        cwd: path.join(__dirname, '..'), // Run from project root
        url: 'http://localhost:1420',
        timeout: 120_000,
        reuseExistingServer: true,
      },

  // Output directory for artifacts
  outputDir: 'test-results',
});
