// ═══════════════════════════════════════════════════════════════════
// FLUXION E2E - Smoke Tests
// Basic app startup and navigation smoke tests
// ═══════════════════════════════════════════════════════════════════

import { dashboardPage } from '../pages';
import { waitForPageLoad } from '../utils/test-helpers';

describe('Smoke Tests', () => {
  it('should launch app successfully', async () => {
    // Wait for app to fully load
    await waitForPageLoad();

    // Check if dashboard is visible
    const isLoaded = await dashboardPage.isLoaded();
    expect(isLoaded).toBe(true);
  });

  it('should display sidebar navigation', async () => {
    const sidebarVisible = await dashboardPage.isVisible(dashboardPage.selectors.sidebar);
    expect(sidebarVisible).toBe(true);
  });

  it('should have all navigation links', async () => {
    // Check if all main navigation items exist
    const clientiExists = await dashboardPage.exists(dashboardPage.selectors.sidebarClienti);
    const calendarioExists = await dashboardPage.exists(dashboardPage.selectors.sidebarCalendario);
    const serviziExists = await dashboardPage.exists(dashboardPage.selectors.sidebarServizi);

    expect(clientiExists).toBe(true);
    expect(calendarioExists).toBe(true);
    expect(serviziExists).toBe(true);
  });

  it('should not have console errors on startup', async () => {
    const logs = await browser.getLogs('browser');
    const errors = logs.filter((log) => log.level === 'SEVERE');

    expect(errors).toHaveLength(0);
  });
});
