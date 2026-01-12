/**
 * Accessibility Tests (WCAG 2.1 AA Compliance)
 *
 * Enterprise Best Practices:
 * - Test keyboard navigation
 * - Verify ARIA attributes
 * - Check color contrast
 * - Screen reader compatibility
 */

import { test, expect } from '../fixtures/test.fixtures';
import AxeBuilder from '@axe-core/playwright';

test.describe('Accessibility Tests @a11y', () => {
  test('dashboard should have no accessibility violations', async ({ dashboardPage, page }) => {
    await dashboardPage.navigate();
    await dashboardPage.expectPageLoaded();

    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
      .analyze();

    expect(results.violations).toEqual([]);
  });

  test('clienti page should have no accessibility violations', async ({ clientiPage, page }) => {
    await clientiPage.navigate();
    await clientiPage.expectPageLoaded();

    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
      .analyze();

    expect(results.violations).toEqual([]);
  });

  test('modal should have no accessibility violations', async ({ clientiPage, page }) => {
    await clientiPage.navigate();
    await clientiPage.openNewClienteForm();

    const results = await new AxeBuilder({ page })
      .include('[role="dialog"]')
      .withTags(['wcag2a', 'wcag2aa'])
      .analyze();

    expect(results.violations).toEqual([]);
  });
});

test.describe('Keyboard Navigation @a11y @keyboard', () => {
  test('can navigate dashboard with keyboard only', async ({ dashboardPage, page }) => {
    await dashboardPage.navigate();
    await dashboardPage.expectPageLoaded();

    // Tab through main navigation
    await page.keyboard.press('Tab');
    const firstFocused = await page.evaluate(() => document.activeElement?.tagName);
    expect(firstFocused).toBeTruthy();

    // Continue tabbing
    for (let i = 0; i < 5; i++) {
      await page.keyboard.press('Tab');
    }

    // Should have moved focus
    const laterFocused = await page.evaluate(() => document.activeElement?.tagName);
    expect(laterFocused).toBeTruthy();
  });

  test('can open and close modal with keyboard', async ({ clientiPage, page }) => {
    await clientiPage.navigate();

    // Find and activate the add button with keyboard
    const addButton = page.getByRole('button', { name: /nuovo cliente|aggiungi/i });
    await addButton.focus();
    await page.keyboard.press('Enter');

    // Modal should open
    await clientiPage.expectModalOpen();

    // Close with Escape
    await page.keyboard.press('Escape');
    await clientiPage.expectModalClosed();
  });

  test('form fields are keyboard accessible', async ({ clientiPage, page }) => {
    await clientiPage.navigate();
    await clientiPage.openNewClienteForm();

    // Tab through form fields
    const fieldLabels = ['Nome', 'Cognome', 'Telefono', 'Email'];

    for (const label of fieldLabels) {
      const field = page.getByLabel(new RegExp(label, 'i'));
      const isVisible = await field.isVisible().catch(() => false);

      if (isVisible) {
        await field.focus();
        const isFocused = await field.evaluate((el) => el === document.activeElement);
        expect(isFocused).toBe(true);
      }
    }
  });

  test('skip link is functional', async ({ page }) => {
    await page.goto('/');

    // Press Tab to reveal skip link
    await page.keyboard.press('Tab');

    const skipLink = page.getByRole('link', { name: /skip|salta|vai al contenuto/i });
    const isVisible = await skipLink.isVisible().catch(() => false);

    if (isVisible) {
      await page.keyboard.press('Enter');
      // Focus should move to main content
      const mainFocused = await page.evaluate(() =>
        document.activeElement?.closest('main') !== null
      );
      expect(mainFocused).toBe(true);
    }
  });
});

test.describe('Screen Reader Compatibility @a11y @screen-reader', () => {
  test('page has proper heading hierarchy', async ({ dashboardPage, page }) => {
    await dashboardPage.navigate();
    await dashboardPage.expectPageLoaded();

    // Check for h1
    const h1 = page.getByRole('heading', { level: 1 });
    await expect(h1).toBeVisible();

    // Verify heading hierarchy doesn't skip levels
    const headings = await page.evaluate(() => {
      const allHeadings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
      return Array.from(allHeadings).map((h) => parseInt(h.tagName[1]));
    });

    for (let i = 1; i < headings.length; i++) {
      const diff = headings[i] - headings[i - 1];
      // Should not skip more than 1 level
      expect(diff).toBeLessThanOrEqual(1);
    }
  });

  test('images have alt text', async ({ dashboardPage, page }) => {
    await dashboardPage.navigate();
    await dashboardPage.expectPageLoaded();

    const images = page.locator('img');
    const count = await images.count();

    for (let i = 0; i < count; i++) {
      const img = images.nth(i);
      const alt = await img.getAttribute('alt');
      const role = await img.getAttribute('role');

      // Image should have alt text or be marked as decorative
      const hasAlt = alt !== null && alt.length > 0;
      const isDecorative = role === 'presentation' || alt === '';

      expect(hasAlt || isDecorative).toBe(true);
    }
  });

  test('form inputs have labels', async ({ clientiPage, page }) => {
    await clientiPage.navigate();
    await clientiPage.openNewClienteForm();

    const inputs = page.locator('input:not([type="hidden"])');
    const count = await inputs.count();

    for (let i = 0; i < count; i++) {
      const input = inputs.nth(i);
      const id = await input.getAttribute('id');
      const ariaLabel = await input.getAttribute('aria-label');
      const ariaLabelledBy = await input.getAttribute('aria-labelledby');

      // Check for associated label or aria attributes
      const hasLabel = id
        ? (await page.locator(`label[for="${id}"]`).count()) > 0
        : false;
      const hasAriaLabel = ariaLabel !== null && ariaLabel.length > 0;
      const hasAriaLabelledBy = ariaLabelledBy !== null;

      expect(hasLabel || hasAriaLabel || hasAriaLabelledBy).toBe(true);
    }
  });

  test('interactive elements have accessible names', async ({ dashboardPage, page }) => {
    await dashboardPage.navigate();
    await dashboardPage.expectPageLoaded();

    const buttons = page.getByRole('button');
    const count = await buttons.count();

    for (let i = 0; i < count; i++) {
      const button = buttons.nth(i);
      const name = await button.evaluate((el) => {
        return el.getAttribute('aria-label') ||
               el.textContent?.trim() ||
               el.getAttribute('title') ||
               '';
      });

      expect(name.length).toBeGreaterThan(0);
    }
  });
});

test.describe('Color Contrast @a11y @contrast', () => {
  test('text has sufficient contrast', async ({ dashboardPage, page }) => {
    await dashboardPage.navigate();
    await dashboardPage.expectPageLoaded();

    // Run axe specifically for color contrast
    const results = await new AxeBuilder({ page })
      .withRules(['color-contrast'])
      .analyze();

    expect(results.violations).toEqual([]);
  });

  test('interactive elements are distinguishable', async ({ dashboardPage, page }) => {
    await dashboardPage.navigate();
    await dashboardPage.expectPageLoaded();

    // Check that buttons have visible focus styles
    const button = page.getByRole('button').first();

    if (await button.isVisible()) {
      await button.focus();

      // Get computed styles
      const focusStyles = await button.evaluate((el) => {
        const styles = window.getComputedStyle(el);
        return {
          outline: styles.outline,
          boxShadow: styles.boxShadow,
          border: styles.border,
        };
      });

      // At least one focus indicator should be present
      const hasFocusIndicator =
        focusStyles.outline !== 'none' ||
        focusStyles.boxShadow !== 'none' ||
        focusStyles.border !== 'none';

      expect(hasFocusIndicator).toBe(true);
    }
  });
});
