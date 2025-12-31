// ═══════════════════════════════════════════════════════════════════
// FLUXION E2E - Clienti Page Object
// ═══════════════════════════════════════════════════════════════════

import { BasePage } from './BasePage';

export class ClientiPage extends BasePage {
  // ───────────────────────────────────────────────────────────────────
  // Selectors
  // ───────────────────────────────────────────────────────────────────

  get selectors() {
    return {
      // Page elements
      header: 'h1:has-text("Clienti")',
      searchInput: 'input[placeholder*="Cerca"]',
      nuovoClienteButton: 'button:has-text("Nuovo Cliente")',

      // Table
      table: 'table',
      tableRows: 'table tbody tr',
      tableRowByIndex: (index: number) => `table tbody tr:nth-child(${index})`,

      // Row actions
      editButton: (row: number) => `table tbody tr:nth-child(${row}) button[data-testid="edit-cliente"]`,
      deleteButton: (row: number) => `table tbody tr:nth-child(${row}) button[data-testid="delete-cliente"]`,

      // Dialog
      dialog: '[role="dialog"]',
      dialogTitle: '[role="dialog"] h2',
      dialogNomeInput: '[name="nome"]',
      dialogCognomeInput: '[name="cognome"]',
      dialogEmailInput: '[name="email"]',
      dialogTelefonoInput: '[name="telefono"]',
      dialogIndirizzoInput: '[name="indirizzo"]',
      dialogNoteInput: '[name="note"]',
      dialogSaveButton: 'button[type="submit"]:has-text("Crea Cliente"), button[type="submit"]:has-text("Aggiorna Cliente")',
      dialogCancelButton: 'button:has-text("Annulla")',

      // Delete confirmation
      deleteConfirmDialog: '[role="alertdialog"]',
      deleteConfirmButton: 'button:has-text("Elimina")',
      deleteCancelButton: 'button:has-text("Annulla")',

      // Empty state
      emptyState: 'text="Nessun cliente trovato"',

      // Error/Success messages
      errorMessage: '[data-testid="error-message"]',
      successMessage: '[data-testid="success-message"]',
    };
  }

  // ───────────────────────────────────────────────────────────────────
  // Actions
  // ───────────────────────────────────────────────────────────────────

  async isLoaded(): Promise<boolean> {
    try {
      await this.waitForDisplayed(this.selectors.header, 5000);
      return true;
    } catch {
      return false;
    }
  }

  async clickNuovoCliente(): Promise<void> {
    await this.click(this.selectors.nuovoClienteButton);
  }

  async searchCliente(query: string): Promise<void> {
    await this.clearAndSetValue(this.selectors.searchInput, query);
    await this.pause(500); // Wait for debounce
  }

  async getTableRowCount(): Promise<number> {
    return await this.getElementCount(this.selectors.tableRows);
  }

  async clickEditCliente(rowIndex: number): Promise<void> {
    await this.click(this.selectors.editButton(rowIndex));
  }

  async clickDeleteCliente(rowIndex: number): Promise<void> {
    await this.click(this.selectors.deleteButton(rowIndex));
  }

  async confirmDelete(): Promise<void> {
    await this.click(this.selectors.deleteConfirmButton);
  }

  async cancelDelete(): Promise<void> {
    await this.click(this.selectors.deleteCancelButton);
  }

  async fillClienteForm(data: {
    nome: string;
    cognome: string;
    email?: string;
    telefono?: string;
    indirizzo?: string;
    note?: string;
  }): Promise<void> {
    await this.clearAndSetValue(this.selectors.dialogNomeInput, data.nome);
    await this.clearAndSetValue(this.selectors.dialogCognomeInput, data.cognome);

    if (data.email) {
      await this.clearAndSetValue(this.selectors.dialogEmailInput, data.email);
    }

    if (data.telefono) {
      await this.clearAndSetValue(this.selectors.dialogTelefonoInput, data.telefono);
    }

    if (data.indirizzo) {
      await this.clearAndSetValue(this.selectors.dialogIndirizzoInput, data.indirizzo);
    }

    if (data.note) {
      await this.clearAndSetValue(this.selectors.dialogNoteInput, data.note);
    }
  }

  async saveCliente(): Promise<void> {
    await this.click(this.selectors.dialogSaveButton);
  }

  async cancelDialog(): Promise<void> {
    await this.click(this.selectors.dialogCancelButton);
  }

  async isDialogOpen(): Promise<boolean> {
    return await this.exists(this.selectors.dialog);
  }

  async isEmptyStateVisible(): Promise<boolean> {
    return await this.exists(this.selectors.emptyState);
  }

  async getClienteNameByRow(rowIndex: number): Promise<string> {
    const row = await $(this.selectors.tableRowByIndex(rowIndex));
    const nameCell = await row.$('td:nth-child(1)'); // Adjust column index
    return await nameCell.getText();
  }

  async createCliente(data: {
    nome: string;
    cognome: string;
    email?: string;
    telefono?: string;
    indirizzo?: string;
    note?: string;
  }): Promise<void> {
    await this.clickNuovoCliente();
    await this.fillClienteForm(data);
    await this.saveCliente();

    // Wait for dialog to close
    await this.waitUntil(
      async () => !(await this.isDialogOpen()),
      { timeout: 5000, timeoutMsg: 'Dialog did not close after creating cliente' }
    );
  }

  async deleteClienteByRow(rowIndex: number): Promise<void> {
    await this.clickDeleteCliente(rowIndex);
    await this.confirmDelete();

    // Wait for deletion to complete
    await this.pause(1000);
  }
}

export const clientiPage = new ClientiPage();
