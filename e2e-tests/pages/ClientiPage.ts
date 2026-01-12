/**
 * Clienti (Customers) Page Object
 * CRM functionality testing
 */

import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './BasePage';

export interface ClienteData {
  nome: string;
  cognome: string;
  telefono?: string;
  email?: string;
  dataNascita?: string;
  note?: string;
}

export class ClientiPage extends BasePage {
  readonly url = '/clienti';

  // Page-specific locators
  private readonly searchInput: Locator;
  private readonly addButton: Locator;
  private readonly clientiTable: Locator;
  private readonly clienteForm: Locator;
  private readonly filterDropdown: Locator;
  private readonly exportButton: Locator;

  constructor(page: Page) {
    super(page);

    this.searchInput = page.getByRole('searchbox', { name: /cerca/i });
    this.addButton = page.getByRole('button', { name: /nuovo cliente|aggiungi/i });
    this.clientiTable = page.getByRole('table');
    this.clienteForm = page.getByRole('form', { name: /cliente/i });
    this.filterDropdown = page.getByRole('combobox', { name: /filtra/i });
    this.exportButton = page.getByRole('button', { name: /esporta/i });
  }

  // =============================================================================
  // SEARCH & FILTER
  // =============================================================================

  async searchCliente(query: string): Promise<void> {
    await this.searchInput.fill(query);
    await this.searchInput.press('Enter');
    await this.waitForPageLoad();
  }

  async clearSearch(): Promise<void> {
    await this.searchInput.clear();
    await this.waitForPageLoad();
  }

  async filterBy(filter: string): Promise<void> {
    await this.filterDropdown.selectOption(filter);
    await this.waitForPageLoad();
  }

  // =============================================================================
  // CRUD OPERATIONS
  // =============================================================================

  async openNewClienteForm(): Promise<void> {
    await this.addButton.click();
    await this.expectModalOpen();
  }

  async fillClienteForm(data: ClienteData): Promise<void> {
    await this.fillInput('Nome', data.nome);
    await this.fillInput('Cognome', data.cognome);

    if (data.telefono) {
      await this.fillInput('Telefono', data.telefono);
    }
    if (data.email) {
      await this.fillInput('Email', data.email);
    }
    if (data.dataNascita) {
      await this.fillInput('Data di nascita', data.dataNascita);
    }
    if (data.note) {
      await this.page.getByLabel('Note').fill(data.note);
    }
  }

  async saveCliente(): Promise<void> {
    await this.submitForm();
    await this.expectToast(/cliente.*salvato|creato/i);
  }

  async createCliente(data: ClienteData): Promise<void> {
    await this.openNewClienteForm();
    await this.fillClienteForm(data);
    await this.saveCliente();
  }

  async openClienteDetails(nome: string): Promise<void> {
    await this.clickTableRowAction(nome, 'Visualizza');
    await this.expectModalOpen();
  }

  async editCliente(nome: string, newData: Partial<ClienteData>): Promise<void> {
    await this.clickTableRowAction(nome, 'Modifica');
    await this.expectModalOpen();

    if (newData.nome) await this.fillInput('Nome', newData.nome);
    if (newData.cognome) await this.fillInput('Cognome', newData.cognome);
    if (newData.telefono) await this.fillInput('Telefono', newData.telefono);
    if (newData.email) await this.fillInput('Email', newData.email);

    await this.saveCliente();
  }

  async deleteCliente(nome: string): Promise<void> {
    await this.clickTableRowAction(nome, 'Elimina');

    // Confirm deletion
    const confirmButton = this.modal.getByRole('button', { name: /conferma|elimina/i });
    await confirmButton.click();

    await this.expectToast(/cliente.*eliminato/i);
  }

  // =============================================================================
  // ASSERTIONS
  // =============================================================================

  async expectClienteInList(nome: string): Promise<void> {
    await expect(this.clientiTable.getByRole('cell', { name: nome })).toBeVisible();
  }

  async expectClienteNotInList(nome: string): Promise<void> {
    await expect(this.clientiTable.getByRole('cell', { name: nome })).toBeHidden();
  }

  async expectClientiCount(count: number): Promise<void> {
    const rows = this.clientiTable.getByRole('row');
    // +1 for header row
    await expect(rows).toHaveCount(count + 1);
  }

  async expectEmptyState(): Promise<void> {
    await expect(this.page.getByText(/nessun cliente|lista vuota/i)).toBeVisible();
  }

  // =============================================================================
  // EXPORT
  // =============================================================================

  async exportClienti(): Promise<void> {
    await this.exportButton.click();
    // Wait for download to start
    const download = await this.page.waitForEvent('download');
    expect(download.suggestedFilename()).toMatch(/clienti.*\.(csv|xlsx)/i);
  }
}
