// ═══════════════════════════════════════════════════════════════════
// FLUXION E2E - Navigation Tests
// Test navigation between pages
// ═══════════════════════════════════════════════════════════════════

import { dashboardPage, clientiPage, serviziPage, calendarioPage } from '../pages';
import { waitForPageLoad } from '../utils/test-helpers';

describe('Navigation Tests', () => {
  beforeEach(async () => {
    // Ensure we start from dashboard
    await waitForPageLoad();
  });

  it('should navigate to Clienti page', async () => {
    await dashboardPage.navigateToClienti();
    await waitForPageLoad();

    const isLoaded = await clientiPage.isLoaded();
    expect(isLoaded).toBe(true);
  });

  it('should navigate to Servizi page', async () => {
    await dashboardPage.navigateToServizi();
    await waitForPageLoad();

    const isLoaded = await serviziPage.isLoaded();
    expect(isLoaded).toBe(true);
  });

  it('should navigate to Calendario page', async () => {
    await dashboardPage.navigateToCalendario();
    await waitForPageLoad();

    const isLoaded = await calendarioPage.isLoaded();
    expect(isLoaded).toBe(true);
  });

  it('should navigate between pages without crashes', async () => {
    // Navigate through all pages
    await dashboardPage.navigateToClienti();
    await waitForPageLoad();

    await dashboardPage.navigateToServizi();
    await waitForPageLoad();

    await dashboardPage.navigateToCalendario();
    await waitForPageLoad();

    // Go back to dashboard
    const dashboardLoaded = await dashboardPage.isLoaded();
    expect(dashboardLoaded).toBe(true);

    // Check no console errors
    const logs = await browser.getLogs('browser');
    const errors = logs.filter((log) => log.level === 'SEVERE');
    expect(errors).toHaveLength(0);
  });

  it('should preserve data when navigating back and forth', async () => {
    // TODO: Create a cliente, navigate away, come back, verify it's still there
    // This test requires implementing actual CRUD operations first
  });
});
