// ═══════════════════════════════════════════════════════════════════
// FLUXION E2E - Clienti CRUD Tests
// Test cliente creation, read, update, delete
// ═══════════════════════════════════════════════════════════════════

import { dashboardPage, clientiPage } from '../pages';
import { TestData } from '../fixtures/test-data';
import { waitForPageLoad, takeScreenshot } from '../utils/test-helpers';

describe('Clienti CRUD Tests', () => {
  beforeEach(async () => {
    await waitForPageLoad();
    await dashboardPage.navigateToClienti();
    await waitForPageLoad();
  });

  it('should create a new cliente', async () => {
    const cliente = TestData.clienti.getUnique();
    const initialCount = await clientiPage.getTableRowCount();

    await clientiPage.createCliente(cliente);

    // Verify cliente was created
    await clientiPage.waitUntil(
      async () => (await clientiPage.getTableRowCount()) === initialCount + 1,
      { timeout: 5000, timeoutMsg: 'Cliente not created' }
    );

    // Search for the created cliente
    await clientiPage.searchCliente(cliente.nome);
    await browser.pause(500);

    const searchResults = await clientiPage.getTableRowCount();
    expect(searchResults).toBeGreaterThan(0);
  });

  it('should display empty state when no clienti', async () => {
    // TODO: This requires database cleanup functionality
    // await cleanTestData();
    // const emptyStateVisible = await clientiPage.isEmptyStateVisible();
    // expect(emptyStateVisible).toBe(true);
  });

  it('should search clienti by name', async () => {
    // Create a unique cliente
    const cliente = TestData.clienti.getUnique();
    await clientiPage.createCliente(cliente);

    // Search for it
    await clientiPage.searchCliente(cliente.nome);
    await browser.pause(500);

    const results = await clientiPage.getTableRowCount();
    expect(results).toBeGreaterThan(0);

    // Clear search
    await clientiPage.searchCliente('');
    await browser.pause(500);
  });

  it('should delete a cliente (soft delete)', async () => {
    // Create a cliente to delete
    const cliente = TestData.clienti.getUnique();
    await clientiPage.createCliente(cliente);

    // Get initial count
    const initialCount = await clientiPage.getTableRowCount();

    // Delete first row
    await clientiPage.deleteClienteByRow(1);

    // Verify count decreased
    await clientiPage.waitUntil(
      async () => (await clientiPage.getTableRowCount()) === initialCount - 1,
      { timeout: 5000, timeoutMsg: 'Cliente not deleted' }
    );
  });

  it('should validate required fields', async () => {
    await clientiPage.clickNuovoCliente();

    // Try to save without filling anything
    await clientiPage.saveCliente();

    // Dialog should still be open (validation failed)
    const dialogOpen = await clientiPage.isDialogOpen();
    expect(dialogOpen).toBe(true);

    // Cancel dialog
    await clientiPage.cancelDialog();
  });

  it('should handle special characters in name', async () => {
    const cliente = {
      nome: "O'Connor",
      cognome: 'Müller-Schmidt',
      email: 'test@example.com',
      telefono: '+39 333 1234567',
    };

    await clientiPage.createCliente(cliente);

    // Search and verify
    await clientiPage.searchCliente("O'Connor");
    await browser.pause(500);

    const results = await clientiPage.getTableRowCount();
    expect(results).toBeGreaterThan(0);
  });

  afterEach(async function () {
    // Take screenshot on failure
    if (this.currentTest?.state === 'failed') {
      await takeScreenshot(`clienti-crud-${this.currentTest.title}`);
    }
  });
});
