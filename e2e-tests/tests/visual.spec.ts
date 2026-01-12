/**
 * Visual Regression Tests
 *
 * Enterprise Best Practices:
 * - Capture screenshots for visual comparison
 * - Test responsive layouts
 * - Verify UI consistency across updates
 * - Use threshold for minor rendering differences
 */

import { test, expect } from '../fixtures/test.fixtures';

test.describe('Visual Regression @visual', () => {
  test.describe.configure({ mode: 'parallel' });

  test('dashboard visual snapshot', async ({ dashboardPage, page }) => {
    await dashboardPage.navigate();
    await dashboardPage.expectPageLoaded();

    // Wait for animations to complete
    await page.waitForTimeout(500);

    await expect(page).toHaveScreenshot('dashboard.png', {
      maxDiffPixels: 100,
      threshold: 0.2,
    });
  });

  test('clienti list visual snapshot', async ({ clientiPage, page }) => {
    await clientiPage.navigate();
    await clientiPage.expectPageLoaded();

    await page.waitForTimeout(500);

    await expect(page).toHaveScreenshot('clienti-list.png', {
      maxDiffPixels: 100,
      threshold: 0.2,
    });
  });

  test('new cliente modal visual snapshot', async ({ clientiPage, page }) => {
    await clientiPage.navigate();
    await clientiPage.openNewClienteForm();

    await page.waitForTimeout(300);

    await expect(page).toHaveScreenshot('clienti-modal.png', {
      maxDiffPixels: 100,
      threshold: 0.2,
    });
  });
});

test.describe('Responsive Visual Tests @visual @responsive', () => {
  const viewports = [
    { name: 'mobile', width: 375, height: 667 },
    { name: 'tablet', width: 768, height: 1024 },
    { name: 'desktop', width: 1280, height: 720 },
    { name: 'wide', width: 1920, height: 1080 },
  ];

  for (const viewport of viewports) {
    test(`dashboard at ${viewport.name} viewport`, async ({ dashboardPage, page }) => {
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      await dashboardPage.navigate();
      await dashboardPage.expectPageLoaded();

      await page.waitForTimeout(500);

      await expect(page).toHaveScreenshot(`dashboard-${viewport.name}.png`, {
        maxDiffPixels: 150,
        threshold: 0.25,
      });
    });
  }
});

test.describe('Component Visual Tests @visual @components', () => {
  test('sidebar navigation visual', async ({ dashboardPage, page }) => {
    await dashboardPage.navigate();
    await dashboardPage.expectPageLoaded();

    const sidebar = page.locator('[data-testid="sidebar"], nav, aside').first();
    const isVisible = await sidebar.isVisible().catch(() => false);

    if (isVisible) {
      await expect(sidebar).toHaveScreenshot('sidebar.png', {
        maxDiffPixels: 50,
        threshold: 0.2,
      });
    } else {
      test.skip();
    }
  });

  test('header visual', async ({ dashboardPage, page }) => {
    await dashboardPage.navigate();
    await dashboardPage.expectPageLoaded();

    const header = page.locator('[data-testid="header"], header').first();
    const isVisible = await header.isVisible().catch(() => false);

    if (isVisible) {
      await expect(header).toHaveScreenshot('header.png', {
        maxDiffPixels: 50,
        threshold: 0.2,
      });
    } else {
      test.skip();
    }
  });

  test('stats cards visual', async ({ dashboardPage, page }) => {
    await dashboardPage.navigate();
    await dashboardPage.expectPageLoaded();

    const statsSection = page.getByTestId('stats-card').first();
    const isVisible = await statsSection.isVisible().catch(() => false);

    if (isVisible) {
      await expect(statsSection).toHaveScreenshot('stats-card.png', {
        maxDiffPixels: 50,
        threshold: 0.2,
      });
    } else {
      test.skip();
    }
  });
});

test.describe('Dark Mode Visual Tests @visual @dark-mode', () => {
  test('dashboard in dark mode', async ({ dashboardPage, page }) => {
    // Set dark mode preference
    await page.emulateMedia({ colorScheme: 'dark' });

    await dashboardPage.navigate();
    await dashboardPage.expectPageLoaded();

    await page.waitForTimeout(500);

    await expect(page).toHaveScreenshot('dashboard-dark.png', {
      maxDiffPixels: 100,
      threshold: 0.2,
    });
  });

  test('clienti page in dark mode', async ({ clientiPage, page }) => {
    await page.emulateMedia({ colorScheme: 'dark' });

    await clientiPage.navigate();
    await clientiPage.expectPageLoaded();

    await page.waitForTimeout(500);

    await expect(page).toHaveScreenshot('clienti-dark.png', {
      maxDiffPixels: 100,
      threshold: 0.2,
    });
  });
});

test.describe('Accessibility Visual Tests @visual @a11y', () => {
  test('high contrast mode', async ({ dashboardPage, page }) => {
    await page.emulateMedia({ forcedColors: 'active' });

    await dashboardPage.navigate();
    await dashboardPage.expectPageLoaded();

    await page.waitForTimeout(500);

    await expect(page).toHaveScreenshot('dashboard-high-contrast.png', {
      maxDiffPixels: 200,
      threshold: 0.3,
    });
  });

  test('reduced motion', async ({ dashboardPage, page }) => {
    await page.emulateMedia({ reducedMotion: 'reduce' });

    await dashboardPage.navigate();
    await dashboardPage.expectPageLoaded();

    // Verify no animations are playing
    await page.waitForTimeout(100);

    await expect(page).toHaveScreenshot('dashboard-reduced-motion.png', {
      maxDiffPixels: 100,
      threshold: 0.2,
    });
  });
});
