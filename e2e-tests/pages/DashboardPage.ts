/**
 * Dashboard Page Object
 * Main entry point of the application
 */

import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './BasePage';

export class DashboardPage extends BasePage {
  readonly url = '/';

  // Dashboard-specific locators
  private readonly welcomeMessage: Locator;
  private readonly statsCards: Locator;
  private readonly quickActions: Locator;
  private readonly recentActivity: Locator;
  private readonly upcomingAppointments: Locator;

  constructor(page: Page) {
    super(page);

    this.welcomeMessage = page.getByRole('heading', { level: 1 });
    this.statsCards = page.getByTestId('stats-card');
    this.quickActions = page.getByTestId('quick-actions');
    this.recentActivity = page.getByTestId('recent-activity');
    this.upcomingAppointments = page.getByTestId('upcoming-appointments');
  }

  // =============================================================================
  // DASHBOARD ACTIONS
  // =============================================================================

  async expectWelcomeMessage(name?: string): Promise<void> {
    if (name) {
      await expect(this.welcomeMessage).toContainText(name);
    } else {
      await expect(this.welcomeMessage).toBeVisible();
    }
  }

  async getStatsCardValue(cardName: string): Promise<string> {
    const card = this.statsCards.filter({ hasText: cardName });
    const value = card.locator('[data-testid="stat-value"]');
    return await value.textContent() || '';
  }

  async clickQuickAction(actionName: string): Promise<void> {
    await this.quickActions.getByRole('button', { name: actionName }).click();
  }

  async expectRecentActivityCount(minCount: number): Promise<void> {
    const items = this.recentActivity.getByRole('listitem');
    await expect(items).toHaveCount(minCount, { timeout: 5000 });
  }

  async getUpcomingAppointmentsCount(): Promise<number> {
    const items = this.upcomingAppointments.getByRole('listitem');
    return await items.count();
  }

  // =============================================================================
  // NAVIGATION FROM DASHBOARD
  // =============================================================================

  async goToClienti(): Promise<void> {
    await this.clickNavLink('Clienti');
  }

  async goToCalendario(): Promise<void> {
    await this.clickNavLink('Calendario');
  }

  async goToFatture(): Promise<void> {
    await this.clickNavLink('Fatture');
  }

  async goToImpostazioni(): Promise<void> {
    await this.clickNavLink('Impostazioni');
  }

  // =============================================================================
  // VISUAL CHECKS
  // =============================================================================

  async expectDashboardLayout(): Promise<void> {
    await expect(this.sidebar).toBeVisible();
    await expect(this.header).toBeVisible();
    await expect(this.statsCards.first()).toBeVisible();
  }
}
