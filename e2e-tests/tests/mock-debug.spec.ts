import { test, expect } from '@playwright/test';
import path from 'path';

const MOCK_SCRIPT = path.join(__dirname, '..', 'fixtures', 'tauri-mock.js');

test('Verify Tauri mock is injected', async ({ page }) => {
  await page.addInitScript({ path: MOCK_SCRIPT });
  await page.goto('/', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(1000);

  // Check if mock exists
  const hasMock = await page.evaluate(() => {
    return typeof (window as any).__TAURI_INTERNALS__?.invoke === 'function';
  });
  console.log('Mock injected:', hasMock);
  expect(hasMock).toBe(true);

  // Try invoking a mock command
  const stats = await page.evaluate(async () => {
    try {
      const result = await (window as any).__TAURI_INTERNALS__.invoke('get_dashboard_stats');
      return result;
    } catch (e: any) {
      return { error: e.message };
    }
  });
  console.log('Dashboard stats:', JSON.stringify(stats));
  expect(stats).toHaveProperty('appuntamenti_oggi');

  // Check what the page shows
  await page.waitForTimeout(3000);
  const bodyText = await page.textContent('body');
  console.log('Body contains Buongiorno:', bodyText?.includes('Buongiorno'));
  console.log('Body contains Caricamento:', bodyText?.includes('Caricamento'));
  console.log('Body snippet:', bodyText?.substring(0, 500));
});
