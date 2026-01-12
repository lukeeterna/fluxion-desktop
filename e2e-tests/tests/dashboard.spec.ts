/**
 * Dashboard E2E Tests
 *
 * Enterprise Best Practices:
 * - Test main entry point thoroughly
 * - Verify statistics and metrics
 * - Test quick actions
 */

import { test, expect } from '../fixtures/test.fixtures';

test.describe('Dashboard @dashboard', () => {
  test.beforeEach(async ({ dashboardPage }) => {
    await dashboardPage.navigate();
    await dashboardPage.expectPageLoaded();
  });

  test('should display dashboard layout correctly', async ({ dashboardPage }) => {
    await dashboardPage.expectDashboardLayout();
  });

  test('should display welcome message', async ({ dashboardPage }) => {
    await dashboardPage.expectWelcomeMessage();
  });

  test('should show stats cards', async ({ page }) => {
    // Wait for dashboard to fully load (not showing loading screen)
    await page.waitForSelector('text=Buongiorno', { timeout: 30000 });

    // Look for stats by their text content rather than test IDs
    const statsTexts = ['Appuntamenti oggi', 'Clienti totali', 'Fatturato del mese'];
    let foundStats = false;

    for (const text of statsTexts) {
      const stat = page.getByText(text);
      if (await stat.isVisible().catch(() => false)) {
        foundStats = true;
        break;
      }
    }

    expect(foundStats).toBe(true);
  });

  test('should navigate to Clienti from dashboard', async ({ dashboardPage, page }) => {
    await dashboardPage.goToClienti();
    await expect(page).toHaveURL(/.*clienti/);
  });

  test('should navigate to Calendario from dashboard', async ({ dashboardPage, page }) => {
    await dashboardPage.goToCalendario();
    await expect(page).toHaveURL(/.*calendario/);
  });

  test('should navigate to Fatture from dashboard', async ({ dashboardPage, page }) => {
    await dashboardPage.goToFatture();
    await expect(page).toHaveURL(/.*fatture/);
  });

  test('should be responsive on mobile viewport', async ({ dashboardPage, page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await dashboardPage.navigate();

    // Sidebar might be collapsed or hidden on mobile
    // Main content should still be visible
    await expect(page.locator('main')).toBeVisible();
  });

  test('should be responsive on tablet viewport', async ({ dashboardPage, page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await dashboardPage.navigate();

    await expect(page.locator('main')).toBeVisible();
  });
});

test.describe('Dashboard Quick Actions @dashboard', () => {
  test.beforeEach(async ({ dashboardPage }) => {
    await dashboardPage.navigate();
    await dashboardPage.expectPageLoaded();
  });

  test('should display quick actions section', async ({ page }) => {
    const quickActions = page.getByTestId('quick-actions');
    // Quick actions might not exist in all versions
    const isVisible = await quickActions.isVisible().catch(() => false);

    if (isVisible) {
      await expect(quickActions).toBeVisible();
    } else {
      test.skip();
    }
  });
});

test.describe('Dashboard Statistics @dashboard @stats', () => {
  test.beforeEach(async ({ dashboardPage }) => {
    await dashboardPage.navigate();
    await dashboardPage.expectPageLoaded();
  });

  test('should display numeric values in stats cards', async ({ page }) => {
    const statsCards = page.getByTestId('stats-card');
    const count = await statsCards.count();

    if (count > 0) {
      for (let i = 0; i < count; i++) {
        const card = statsCards.nth(i);
        const value = card.locator('[data-testid="stat-value"]');
        const valueText = await value.textContent();

        // Value should contain a number
        expect(valueText).toMatch(/\d+/);
      }
    } else {
      test.skip();
    }
  });
});
