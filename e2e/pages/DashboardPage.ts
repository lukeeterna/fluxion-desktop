// ═══════════════════════════════════════════════════════════════════
// FLUXION E2E - Dashboard Page Object
// ═══════════════════════════════════════════════════════════════════

import { BasePage } from './BasePage';

export class DashboardPage extends BasePage {
  // ───────────────────────────────────────────────────────────────────
  // Selectors
  // ───────────────────────────────────────────────────────────────────

  get selectors() {
    return {
      // TODO: Replace with actual data-testid selectors from your app
      header: '[data-testid="dashboard-header"]',
      sidebar: '[data-testid="sidebar"]',
      sidebarDashboard: '[data-testid="sidebar-dashboard"]',
      sidebarClienti: '[data-testid="sidebar-clienti"]',
      sidebarCalendario: '[data-testid="sidebar-calendario"]',
      sidebarServizi: '[data-testid="sidebar-servizi"]',
      sidebarOperatori: '[data-testid="sidebar-operatori"]',
      sidebarFatture: '[data-testid="sidebar-fatture"]',
      sidebarImpostazioni: '[data-testid="sidebar-impostazioni"]',

      // Stats cards
      statsClienti: '[data-testid="stats-clienti"]',
      statsAppuntamenti: '[data-testid="stats-appuntamenti"]',
      statsFatturato: '[data-testid="stats-fatturato"]',

      // Generic fallback selectors (if data-testid not available)
      pageTitle: 'h1',
      navLink: (text: string) => `nav a:has-text("${text}")`,
    };
  }

  // ───────────────────────────────────────────────────────────────────
  // Actions
  // ───────────────────────────────────────────────────────────────────

  async isLoaded(): Promise<boolean> {
    try {
      await this.waitForDisplayed(this.selectors.sidebar, 5000);
      return true;
    } catch {
      return false;
    }
  }

  async navigateToClienti(): Promise<void> {
    await this.click(this.selectors.sidebarClienti);
  }

  async navigateToCalendario(): Promise<void> {
    await this.click(this.selectors.sidebarCalendario);
  }

  async navigateToServizi(): Promise<void> {
    await this.click(this.selectors.sidebarServizi);
  }

  async navigateToOperatori(): Promise<void> {
    await this.click(this.selectors.sidebarOperatori);
  }

  async navigateToFatture(): Promise<void> {
    await this.click(this.selectors.sidebarFatture);
  }

  async navigateToImpostazioni(): Promise<void> {
    await this.click(this.selectors.sidebarImpostazioni);
  }

  async getStatsClientiCount(): Promise<string> {
    return await this.getText(this.selectors.statsClienti);
  }

  async getStatsAppuntamentiCount(): Promise<string> {
    return await this.getText(this.selectors.statsAppuntamenti);
  }

  async getStatsFatturatoValue(): Promise<string> {
    return await this.getText(this.selectors.statsFatturato);
  }

  async isSidebarCollapsed(): Promise<boolean> {
    const sidebar = await $(this.selectors.sidebar);
    const width = await sidebar.getSize('width');
    return width < 100; // Sidebar collapsed width is 60px
  }

  async toggleSidebar(): Promise<void> {
    // TODO: Add sidebar toggle button selector
    await this.click('[data-testid="sidebar-toggle"]');
  }
}

export const dashboardPage = new DashboardPage();
