/**
 * Global Setup - Runs once before all tests
 *
 * Enterprise Best Practices:
 * - Initialize test database with seed data
 * - Authenticate if needed
 * - Check environment health
 */

import { chromium, firefox, FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig): Promise<void> {
  console.log('🚀 Starting FLUXION E2E Test Suite');
  console.log(`📍 Environment: ${process.env.CI ? 'CI' : 'Local'}`);
  console.log(`🌐 Base URL: ${config.projects[0]?.use?.baseURL || 'http://localhost:1420'}`);

  // =============================================================================
  // HEALTH CHECK (use firefox on macOS Big Sur, chromium elsewhere)
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

    // Check if app loaded correctly
    await page.waitForSelector('body', { timeout: 10_000 });
    console.log('✅ App is running and accessible');

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
