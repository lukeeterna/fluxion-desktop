/**
 * FLUXION — Automated Screenshot Capture with Tauri Mock
 * Captures ALL app screens with realistic Italian PMI demo data.
 * Output: landing/screenshots/
 *
 * Run: cd e2e-tests && npx playwright test tests/screenshots.spec.ts --project=firefox
 */

import { test, expect } from '@playwright/test';
import path from 'path';
import fs from 'fs';

const SCREENSHOT_DIR = path.join(__dirname, '..', '..', 'landing', 'screenshots');
const MOCK_SCRIPT = path.join(__dirname, '..', 'fixtures', 'tauri-mock.js');

// Screenshot config per page
const PAGES = [
  { name: '01-dashboard',    path: '/',              title: 'Dashboard' },
  { name: '02-calendario',   path: '/calendario',    title: 'Calendario' },
  { name: '03-clienti',      path: '/clienti',       title: 'Clienti' },
  { name: '04-servizi',      path: '/servizi',       title: 'Servizi' },
  { name: '05-operatori',    path: '/operatori',     title: 'Operatori' },
  { name: '06-fatture',      path: '/fatture',       title: 'Fatture' },
  { name: '07-cassa',        path: '/cassa',         title: 'Cassa' },
  { name: '08-voice',        path: '/voice',         title: 'Sara AI' },
  { name: '09-fornitori',    path: '/fornitori',     title: 'Fornitori' },
  { name: '10-analytics',    path: '/analytics',     title: 'Analytics' },
  { name: '11-impostazioni', path: '/impostazioni',  title: 'Impostazioni' },
];

test.describe('FLUXION Screenshot Capture', () => {
  test.describe.configure({ mode: 'serial' });

  // Inject Tauri mock BEFORE every page load
  test.beforeEach(async ({ page }) => {
    await page.addInitScript({ path: MOCK_SCRIPT });
    await page.setViewportSize({ width: 1920, height: 1080 });
  });

  for (const pg of PAGES) {
    test(`Screenshot: ${pg.title}`, async ({ page }) => {
      await page.goto(pg.path, { waitUntil: 'domcontentloaded' });

      // Wait for data to render (mock has 50-150ms delay)
      await page.waitForTimeout(3000);

      // Verify NOT stuck on loading screen
      const body = await page.textContent('body');
      const isLoading = body?.includes('Caricamento...');
      if (isLoading) {
        // Extra wait if still loading
        await page.waitForTimeout(3000);
      }

      // Take screenshot
      await page.screenshot({
        path: path.join(SCREENSHOT_DIR, `${pg.name}.png`),
        fullPage: false,
      });

      // Validate screenshot file was created and has content
      const filePath = path.join(SCREENSHOT_DIR, `${pg.name}.png`);
      expect(fs.existsSync(filePath)).toBe(true);
      const stat = fs.statSync(filePath);
      expect(stat.size).toBeGreaterThan(10000); // >10KB = not blank
    });
  }
});
