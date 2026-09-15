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

const baseURL = process.env.BASE_URL || 'http://localhost:1420';
const storageState = path.join(__dirname, '.auth/user.json');

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
    baseURL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'on-first-retry',
    actionTimeout: 15_000,
    navigationTimeout: 30_000,
    locale: 'it-IT',
    timezoneId: 'Europe/Rome',
  },

  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        storageState,
      },
    },

    // WebKit is meaningful only on macOS runners.
    ...(process.platform === 'darwin'
      ? [
          {
            name: 'webkit',
            use: {
              ...devices['Desktop Safari'],
              storageState,
            },
          },
        ]
      : []),
  ],

  // Full CI runs against the built frontend. Playwright owns the preview
  // lifecycle so macOS and Windows use the same deterministic startup path.
  webServer: {
    command: 'npm run preview -- --host 127.0.0.1 --port 1420',
    cwd: path.join(__dirname, '..'),
    url: baseURL,
    timeout: 120_000,
    reuseExistingServer: false,
  },

  globalSetup: path.join(__dirname, 'fixtures/global.setup.ts'),
  globalTeardown: path.join(__dirname, 'fixtures/global.teardown.ts'),

  // Output directory for artifacts
  outputDir: 'test-results',
});
