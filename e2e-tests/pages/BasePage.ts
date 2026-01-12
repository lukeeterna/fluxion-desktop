/**
 * FLUXION Enterprise Test Suite
 * Base Page Object - All pages inherit from this
 *
 * Best Practices:
 * - Use role locators (getByRole) as primary
 * - Fallback to data-testid for complex elements
 * - Never use CSS selectors or XPath
 */

import { Page, Locator, expect } from '@playwright/test';

export abstract class BasePage {
  protected readonly page: Page;

  // Common UI elements
  protected readonly sidebar: Locator;
  protected readonly header: Locator;
  protected readonly loadingSpinner: Locator;
  protected readonly toast: Locator;
  protected readonly modal: Locator;

  constructor(page: Page) {
    this.page = page;

    // Initialize common locators - flexible selectors for FLUXION UI
    // Sidebar: look for nav element or common sidebar patterns
    this.sidebar = page.locator('nav, [data-testid="sidebar"], aside').first();
    this.header = page.locator('header, [data-testid="header"]').first();
    this.loadingSpinner = page.getByRole('progressbar');
    this.toast = page.locator('[data-sonner-toast], [role="alert"], .toast').first();
    this.modal = page.getByRole('dialog');
  }

  // =============================================================================
  // NAVIGATION
  // =============================================================================

  abstract readonly url: string;

  async goto(): Promise<void> {
    await this.page.goto(this.url);
    await this.waitForPageLoad();
  }

  // Alias for goto
  async navigate(): Promise<void> {
    await this.goto();
  }

  async expectPageLoaded(): Promise<void> {
    await this.waitForPageLoad();
  }

  async expectModalClosed(): Promise<void> {
    await expect(this.modal).toBeHidden();
  }

  async waitForPageLoad(): Promise<void> {
    // Wait for loading spinner to disappear
    await this.loadingSpinner.waitFor({ state: 'hidden', timeout: 10_000 }).catch(() => {});

    // Wait for network to be idle
    await this.page.waitForLoadState('networkidle');
  }

  // =============================================================================
  // COMMON ACTIONS
  // =============================================================================

  async clickNavLink(name: string): Promise<void> {
    // Try multiple strategies to find navigation links
    const link = this.page.locator(`nav a:has-text("${name}"), a:has-text("${name}")`).first();
    await link.click();
    await this.waitForPageLoad();
  }

  async expectToast(message: string | RegExp): Promise<void> {
    await expect(this.toast).toContainText(message);
  }

  async dismissToast(): Promise<void> {
    const closeButton = this.toast.getByRole('button', { name: /close|chiudi|×/i });
    if (await closeButton.isVisible()) {
      await closeButton.click();
    }
  }

  async expectModalOpen(): Promise<void> {
    await expect(this.modal).toBeVisible();
  }

  async closeModal(): Promise<void> {
    const closeButton = this.modal.getByRole('button', { name: /close|chiudi|annulla|×/i });
    await closeButton.click();
    await expect(this.modal).toBeHidden();
  }

  // =============================================================================
  // FORM HELPERS
  // =============================================================================

  async fillInput(label: string, value: string): Promise<void> {
    await this.page.getByLabel(label).fill(value);
  }

  async selectOption(label: string, value: string): Promise<void> {
    await this.page.getByLabel(label).selectOption(value);
  }

  async checkCheckbox(label: string): Promise<void> {
    await this.page.getByRole('checkbox', { name: label }).check();
  }

  async uncheckCheckbox(label: string): Promise<void> {
    await this.page.getByRole('checkbox', { name: label }).uncheck();
  }

  async clickButton(name: string): Promise<void> {
    await this.page.getByRole('button', { name }).click();
  }

  async submitForm(): Promise<void> {
    await this.page.getByRole('button', { name: /salva|conferma|invia|submit/i }).click();
  }

  // =============================================================================
  // ASSERTIONS
  // =============================================================================

  async expectTitle(title: string | RegExp): Promise<void> {
    await expect(this.page).toHaveTitle(title);
  }

  async expectURL(url: string | RegExp): Promise<void> {
    await expect(this.page).toHaveURL(url);
  }

  async expectHeading(text: string | RegExp, level?: 1 | 2 | 3 | 4 | 5 | 6): Promise<void> {
    const heading = level
      ? this.page.getByRole('heading', { level, name: text })
      : this.page.getByRole('heading', { name: text });
    await expect(heading).toBeVisible();
  }

  // =============================================================================
  // TABLE HELPERS
  // =============================================================================

  async getTableRowCount(): Promise<number> {
    const rows = this.page.getByRole('row');
    return await rows.count() - 1; // Exclude header row
  }

  async clickTableRowAction(rowText: string, actionName: string): Promise<void> {
    const row = this.page.getByRole('row').filter({ hasText: rowText });
    await row.getByRole('button', { name: actionName }).click();
  }

  async expectTableContains(text: string): Promise<void> {
    await expect(this.page.getByRole('cell', { name: text })).toBeVisible();
  }

  // =============================================================================
  // SCREENSHOTS & VISUAL REGRESSION
  // =============================================================================

  async takeScreenshot(name: string): Promise<void> {
    await this.page.screenshot({
      path: `reports/screenshots/${name}.png`,
      fullPage: true,
    });
  }

  async expectScreenshotMatch(name: string): Promise<void> {
    await expect(this.page).toHaveScreenshot(`${name}.png`, {
      maxDiffPixels: 100,
      threshold: 0.2,
    });
  }

  // =============================================================================
  // ACCESSIBILITY
  // =============================================================================

  async checkAccessibility(): Promise<void> {
    // This would use axe-playwright in real implementation
    // For now, check basic accessibility
    await expect(this.page.getByRole('main')).toBeVisible();
  }

  // =============================================================================
  // TAURI-SPECIFIC
  // =============================================================================

  async invokeTauriCommand<T>(command: string, args?: Record<string, unknown>): Promise<T> {
    return await this.page.evaluate(
      async ({ cmd, cmdArgs }) => {
        // @ts-expect-error - Tauri API
        const { invoke } = window.__TAURI__.core;
        return await invoke(cmd, cmdArgs);
      },
      { cmd: command, cmdArgs: args }
    );
  }

  async mockTauriCommand(command: string, response: unknown): Promise<void> {
    await this.page.evaluate(
      ({ cmd, resp }) => {
        // @ts-expect-error - Tauri mocks
        window.__TAURI_IPC__ = window.__TAURI_IPC__ || {};
        window.__TAURI_IPC__[cmd] = () => Promise.resolve(resp);
      },
      { cmd: command, resp: response }
    );
  }
}
