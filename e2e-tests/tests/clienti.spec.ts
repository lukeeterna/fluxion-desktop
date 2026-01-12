/**
 * Clienti (CRM) E2E Tests
 *
 * Enterprise Best Practices:
 * - Test complete CRUD operations
 * - Use data factories for test isolation
 * - Clean up after tests
 * - Use meaningful test names
 */

import { test, expect, TestDataFactory } from '../fixtures/test.fixtures';

test.describe('Clienti CRUD Operations @clienti', () => {
  test.beforeEach(async ({ clientiPage }) => {
    await clientiPage.navigate();
    await clientiPage.expectPageLoaded();
  });

  test('should display clienti list', async ({ page }) => {
    // Verify table or empty state is visible
    const table = page.getByRole('table');
    const emptyState = page.getByText(/nessun cliente|lista vuota/i);

    const isTableVisible = await table.isVisible().catch(() => false);
    const isEmptyStateVisible = await emptyState.isVisible().catch(() => false);

    expect(isTableVisible || isEmptyStateVisible).toBe(true);
  });

  test('should create new cliente', async ({ clientiPage, testCliente }) => {
    await clientiPage.createCliente(testCliente);
    await clientiPage.expectClienteInList(testCliente.nome);
  });

  test('should search for cliente by name', async ({ clientiPage, testCliente }) => {
    // First create a cliente
    await clientiPage.createCliente(testCliente);

    // Then search for it
    await clientiPage.searchCliente(testCliente.nome);
    await clientiPage.expectClienteInList(testCliente.nome);
  });

  test('should edit existing cliente', async ({ clientiPage, testCliente }) => {
    // Create cliente
    await clientiPage.createCliente(testCliente);

    // Edit it
    const newName = `Edited${Date.now()}`;
    await clientiPage.editCliente(testCliente.nome, { nome: newName });

    // Verify the edit
    await clientiPage.expectClienteInList(newName);
  });

  test('should delete cliente', async ({ clientiPage, testCliente }) => {
    // Create cliente
    await clientiPage.createCliente(testCliente);
    await clientiPage.expectClienteInList(testCliente.nome);

    // Delete it
    await clientiPage.deleteCliente(testCliente.nome);

    // Verify deletion
    await clientiPage.expectClienteNotInList(testCliente.nome);
  });

  test('should validate required fields', async ({ clientiPage, page }) => {
    await clientiPage.openNewClienteForm();

    // Try to submit empty form
    await clientiPage.submitForm();

    // Check for validation errors
    const validationError = page.getByText(/campo obbligatorio|required/i);
    await expect(validationError.first()).toBeVisible();
  });

  test('should validate email format', async ({ clientiPage, page }) => {
    await clientiPage.openNewClienteForm();

    // Fill with invalid email
    await clientiPage.fillClienteForm({
      nome: 'Test',
      cognome: 'User',
      email: 'invalid-email',
    });

    await clientiPage.submitForm();

    // Check for email validation error
    const emailError = page.getByText(/email.*valida|invalid.*email/i);
    await expect(emailError).toBeVisible();
  });

  test('should validate phone number format', async ({ clientiPage, page }) => {
    await clientiPage.openNewClienteForm();

    // Fill with invalid phone
    await clientiPage.fillClienteForm({
      nome: 'Test',
      cognome: 'User',
      telefono: 'abc',
    });

    await clientiPage.submitForm();

    // Check for phone validation error
    const phoneError = page.getByText(/telefono.*valido|invalid.*phone/i);
    await expect(phoneError).toBeVisible();
  });
});

test.describe('Clienti Search & Filter @clienti', () => {
  test.beforeEach(async ({ clientiPage }) => {
    await clientiPage.navigate();
    await clientiPage.expectPageLoaded();
  });

  test('should clear search results', async ({ clientiPage, testCliente }) => {
    // Create and search
    await clientiPage.createCliente(testCliente);
    await clientiPage.searchCliente(testCliente.nome);
    await clientiPage.expectClienteInList(testCliente.nome);

    // Clear search
    await clientiPage.clearSearch();

    // Should show all results (or at least not be filtered)
    // The test cliente should still be visible
    await clientiPage.expectClienteInList(testCliente.nome);
  });

  test('should show no results for non-existent cliente', async ({ clientiPage, page }) => {
    await clientiPage.searchCliente('NonExistentCliente12345XYZ');

    // Should show empty state or no results message
    const noResults = page.getByText(/nessun risultato|non trovato|no results/i);
    await expect(noResults).toBeVisible();
  });
});

test.describe('Clienti Bulk Operations @clienti @bulk', () => {
  test('should create multiple clienti', async ({ clientiPage }) => {
    const clienti = TestDataFactory.clienti(3);

    for (const cliente of clienti) {
      await clientiPage.createCliente(cliente);
    }

    // Verify all were created
    for (const cliente of clienti) {
      await clientiPage.expectClienteInList(cliente.nome);
    }
  });
});
