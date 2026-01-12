/**
 * Smoke Tests - Critical Health Checks
 *
 * Enterprise Best Practices:
 * - Run first in CI pipeline
 * - Fast execution (< 2 minutes)
 * - Verify core functionality works
 * - Block deployments if smoke tests fail
 */

import { test, expect } from '../fixtures/test.fixtures';

test.describe('Smoke Tests @smoke', () => {
  test.describe.configure({ mode: 'serial' });

  test('app loads successfully', async ({ dashboardPage }) => {
    await dashboardPage.navigate();
    await dashboardPage.expectPageLoaded();
  });

  test('main navigation is visible', async ({ dashboardPage }) => {
    await dashboardPage.navigate();
    await expect(dashboardPage['sidebar']).toBeVisible();
    await expect(dashboardPage['header']).toBeVisible();
  });

  test('can navigate to Clienti page', async ({ dashboardPage, page }) => {
    await dashboardPage.navigate();
    await dashboardPage.goToClienti();
    await expect(page).toHaveURL(/.*clienti/);
  });

  test('can navigate to Calendario page', async ({ dashboardPage, page }) => {
    await dashboardPage.navigate();
    await dashboardPage.goToCalendario();
    await expect(page).toHaveURL(/.*calendario/);
  });

  test('can navigate to Fatture page', async ({ dashboardPage, page }) => {
    await dashboardPage.navigate();
    await dashboardPage.goToFatture();
    await expect(page).toHaveURL(/.*fatture/);
  });

  test('can navigate to Impostazioni page', async ({ dashboardPage, page }) => {
    await dashboardPage.navigate();
    await dashboardPage.goToImpostazioni();
    await expect(page).toHaveURL(/.*impostazioni/);
  });

  test('no console errors on page load', async ({ page }) => {
    const consoleErrors: string[] = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Allow some known acceptable errors
    const criticalErrors = consoleErrors.filter(
      (error) =>
        !error.includes('favicon') &&
        !error.includes('404') &&
        !error.includes('ResizeObserver')
    );

    expect(criticalErrors).toHaveLength(0);
  });

  test('no JavaScript errors', async ({ page }) => {
    const jsErrors: Error[] = [];
    page.on('pageerror', (error) => {
      jsErrors.push(error);
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    expect(jsErrors).toHaveLength(0);
  });
});
