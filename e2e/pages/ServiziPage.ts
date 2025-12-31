// ═══════════════════════════════════════════════════════════════════
// FLUXION E2E - Servizi Page Object
// ═══════════════════════════════════════════════════════════════════

import { BasePage } from './BasePage';

export class ServiziPage extends BasePage {
  get selectors() {
    return {
      header: 'h1:has-text("Servizi")',
      searchInput: 'input[placeholder*="Cerca"]',
      nuovoServizioButton: 'button:has-text("Nuovo Servizio")',

      // Table
      table: 'table',
      tableRows: 'table tbody tr',

      // Dialog form
      dialog: '[role="dialog"]',
      dialogNomeInput: '[name="nome"]',
      dialogCategoriaInput: '[name="categoria"]',
      dialogDescrizioneInput: '[name="descrizione"]',
      dialogPrezzoInput: '[name="prezzo"]',
      dialogIvaInput: '[name="iva_percentuale"]',
      dialogDurataInput: '[name="durata_minuti"]',
      dialogBufferInput: '[name="buffer_minuti"]',
      dialogColoreInput: '[name="colore"]',
      dialogOrdineInput: '[name="ordine"]',
      dialogSaveButton: 'button[type="submit"]:has-text("Crea Servizio"), button[type="submit"]:has-text("Aggiorna Servizio")',
      dialogCancelButton: 'button:has-text("Annulla")',

      // Validation errors
      nomeError: 'text="Nome richiesto"',
      prezzoError: 'text="Prezzo deve essere"',
      durataError: 'text="Durata"',

      emptyState: 'text="Nessun servizio trovato"',
    };
  }

  async isLoaded(): Promise<boolean> {
    try {
      await this.waitForDisplayed(this.selectors.header, 5000);
      return true;
    } catch {
      return false;
    }
  }

  async clickNuovoServizio(): Promise<void> {
    await this.click(this.selectors.nuovoServizioButton);
  }

  async fillServizioForm(data: {
    nome: string;
    categoria?: string;
    descrizione?: string;
    prezzo?: number;
    iva?: number;
    durata?: number;
    buffer?: number;
    colore?: string;
    ordine?: number;
  }): Promise<void> {
    await this.clearAndSetValue(this.selectors.dialogNomeInput, data.nome);

    if (data.categoria) {
      await this.clearAndSetValue(this.selectors.dialogCategoriaInput, data.categoria);
    }

    if (data.descrizione) {
      await this.clearAndSetValue(this.selectors.dialogDescrizioneInput, data.descrizione);
    }

    if (data.prezzo !== undefined) {
      await this.clearAndSetValue(this.selectors.dialogPrezzoInput, data.prezzo);
    }

    if (data.iva !== undefined) {
      await this.clearAndSetValue(this.selectors.dialogIvaInput, data.iva);
    }

    if (data.durata !== undefined) {
      await this.clearAndSetValue(this.selectors.dialogDurataInput, data.durata);
    }

    if (data.buffer !== undefined) {
      await this.clearAndSetValue(this.selectors.dialogBufferInput, data.buffer);
    }

    if (data.colore) {
      await this.clearAndSetValue(this.selectors.dialogColoreInput, data.colore);
    }

    if (data.ordine !== undefined) {
      await this.clearAndSetValue(this.selectors.dialogOrdineInput, data.ordine);
    }
  }

  async saveServizio(): Promise<void> {
    await this.click(this.selectors.dialogSaveButton);
  }

  async createServizio(data: {
    nome: string;
    categoria?: string;
    descrizione?: string;
    prezzo?: number;
    iva?: number;
    durata?: number;
    buffer?: number;
    colore?: string;
    ordine?: number;
  }): Promise<void> {
    await this.clickNuovoServizio();
    await this.fillServizioForm(data);
    await this.saveServizio();

    // Wait for dialog to close or error to appear
    await this.pause(1000);
  }

  async getTableRowCount(): Promise<number> {
    return await this.getElementCount(this.selectors.tableRows);
  }

  async isDialogOpen(): Promise<boolean> {
    return await this.exists(this.selectors.dialog);
  }

  async hasValidationError(errorSelector: string): Promise<boolean> {
    return await this.exists(errorSelector);
  }
}

export const serviziPage = new ServiziPage();
