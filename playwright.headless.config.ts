// ═══════════════════════════════════════════════════════════════════
// FLUXION - Playwright Headless Config for SSH Remote Testing
// Optimized for macOS Monterey via SSH (no display server needed)
// ═══════════════════════════════════════════════════════════════════

import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  testMatch: '**/*.test.ts',

  // Serial execution for stability on macOS
  fullyParallel: false,
  workers: 1,

  // Retry on CI only
  retries: process.env.CI ? 2 : 0,
  timeout: 60000,

  expect: {
    timeout: 10000,
  },

  reporter: [
    ['list'],
    ['html', { outputFolder: 'test-results/html', open: 'never' }],
    ['junit', { outputFile: 'test-results/junit.xml' }],
    ['json', { outputFile: 'test-results/results.json' }],
  ],

  outputDir: 'test-results/artifacts',

  use: {
    baseURL: 'http://localhost:1420',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    viewport: { width: 1280, height: 720 },
    locale: 'it-IT',
    timezoneId: 'Europe/Rome',
    actionTimeout: 10000,
    navigationTimeout: 15000,
    // Headless mode (native on WebKit)
    headless: true,
  },

  // Use Chromium for macOS 12 compatibility (WebKit has issues on Monterey)
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  // Auto-start Vite dev server (NOT tauri dev - faster startup)
  webServer: {
    command: 'npm run dev',
    port: 1420,
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
});
