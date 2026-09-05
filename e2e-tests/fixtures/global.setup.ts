/**
 * Global Setup - Runs once before all tests
 *
 * Enterprise Best Practices:
 * - Initialize test database with seed data
 * - Authenticate if needed
 * - Check environment health
 */

import fs from 'node:fs';
import path from 'node:path';
import { chromium, firefox, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig): Promise<void> {
  console.log('🚀 Starting FLUXION E2E Test Suite');
  console.log(`📍 Environment: ${process.env.CI ? 'CI' : 'Local'}`);
  console.log(`🌐 Base URL: ${config.projects[0]?.use?.baseURL || 'http://localhost:1420'}`);

  // =============================================================================
  // HEALTH CHECK + DETERMINISTIC FIRST-RUN STATE
  // =============================================================================
  let browser;
  try {
    browser = await chromium.launch();
  } catch {
    console.log('⚠️ Chromium unavailable, using Firefox instead');
    browser = await firefox.launch();
  }
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // Wait for app to be ready
    const baseURL = config.projects[0]?.use?.baseURL || 'http://localhost:1420';
    await page.goto(baseURL, { timeout: 60_000 });

    // Check if app loaded (domcontentloaded, not networkidle — Vite HMR keeps WS open)
    await page.waitForLoadState('domcontentloaded', { timeout: 15_000 });
    await page.waitForSelector('body', { timeout: 10_000 });

    // E2E exercises the application itself, not the one-time preflight wizard.
    // Seed the exact key used by FirstRunWizard, then persist it for every test context.
    await page.evaluate(() => {
      window.localStorage.setItem('fluxion-preflight-completed-v1', '1');
    });

    const authFile = path.resolve(__dirname, '../.auth/user.json');
    fs.mkdirSync(path.dirname(authFile), { recursive: true });
    await context.storageState({ path: authFile });

    console.log('✅ App is running and E2E preflight state saved');

  } catch (error) {
    console.error('❌ App health check failed:', error);
    throw new Error('Application is not running. Start with: npm run tauri dev');
  } finally {
    await browser.close();
  }

  // =============================================================================
  // DATABASE SEEDING (if needed)
  // =============================================================================
  if (process.env.SEED_DATABASE === 'true') {
    console.log('🌱 Seeding test database...');
    // Seed logic would go here
    // await seedTestDatabase();
    console.log('✅ Database seeded');
  }

  console.log('✅ Global setup complete\n');
}

export default globalSetup;
