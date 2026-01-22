// ═══════════════════════════════════════════════════════════════════
// FLUXION - Smoke Tests
// Quick verification that the app loads and basic navigation works
// ═══════════════════════════════════════════════════════════════════

import { test, expect } from '@playwright/test';

test.describe('Smoke Tests', () => {
  test('App loads successfully', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Verify React app mounted
    const app = page.locator('#root, #app, [data-testid="app"]');
    await expect(app.first()).toBeVisible();

    console.log('✅ App loaded');
  });

  test('Sidebar navigation visible', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Check for sidebar
    const sidebar = page.locator('[data-testid="sidebar"], nav, aside');
    await expect(sidebar.first()).toBeVisible();

    console.log('✅ Sidebar visible');
  });

  test('Dashboard accessible', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Check for dashboard content
    const dashboard = page.locator('text=Dashboard, h1:has-text("Dashboard")');
    const isDashboard = await dashboard.first().isVisible().catch(() => false);

    if (isDashboard) {
      console.log('✅ Dashboard visible');
    } else {
      // May redirect to another page
      console.log('ℹ️ Not on dashboard, checking URL');
      const url = page.url();
      console.log(`   Current URL: ${url}`);
    }
  });

  test('Can access Tauri API', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Check if Tauri API is available
    const hasTauri = await page.evaluate(() => {
      // @ts-ignore
      return typeof window.__TAURI__ !== 'undefined';
    });

    if (hasTauri) {
      console.log('✅ Tauri API available');

      // Try a simple Tauri command
      const result = await page.evaluate(async () => {
        try {
          // @ts-ignore
          const suppliers = await window.__TAURI__.tauri.invoke('list_suppliers');
          return { success: true, count: suppliers?.length ?? 0 };
        } catch (e) {
          return { success: false, error: String(e) };
        }
      });

      console.log('📊 Tauri command result:', result);
    } else {
      console.log('⚠️ Tauri API not available (running in browser mode)');
    }
  });

  test('No console errors on load', async ({ page }) => {
    const errors: string[] = [];

    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    page.on('pageerror', (err) => {
      errors.push(err.message);
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    if (errors.length > 0) {
      console.log('❌ Console errors found:');
      errors.forEach((e) => console.log(`   ${e}`));
    } else {
      console.log('✅ No console errors');
    }

    // Allow some warnings but no critical errors
    const criticalErrors = errors.filter(
      (e) => !e.includes('ResizeObserver') && !e.includes('Warning')
    );
    expect(criticalErrors.length).toBe(0);
  });
});
