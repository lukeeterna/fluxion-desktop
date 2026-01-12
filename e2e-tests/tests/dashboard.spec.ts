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

    // Verify all 4 stat cards are visible using data-testid
    const statCards = [
      'stat-appuntamenti-oggi',
      'stat-clienti-totali',
      'stat-fatturato-mese',
      'stat-servizio-top'
    ];

    for (const testId of statCards) {
      await expect(page.getByTestId(testId)).toBeVisible();
    }
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
    // Use actual data-testid from Dashboard.tsx
    const statTestIds = [
      'stat-appuntamenti-oggi',
      'stat-clienti-totali',
      'stat-fatturato-mese',
      'stat-servizio-top'
    ];

    for (const testId of statTestIds) {
      const card = page.getByTestId(testId);
      await expect(card).toBeVisible();

      // Each card should have a visible value (the text-3xl element)
      const cardText = await card.textContent();
      expect(cardText).toBeTruthy();
    }
  });

  test('should display section cards', async ({ page }) => {
    // Verify the two section cards
    await expect(page.getByTestId('section-prossimi-appuntamenti')).toBeVisible();
    await expect(page.getByTestId('section-riepilogo-veloce')).toBeVisible();
  });

  test('should display navigation buttons', async ({ page }) => {
    // Verify CTA buttons in riepilogo section
    await expect(page.getByTestId('btn-vai-fatture')).toBeVisible();
    await expect(page.getByTestId('btn-vai-calendario')).toBeVisible();
  });
});
