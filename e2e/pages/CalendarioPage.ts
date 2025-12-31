// ═══════════════════════════════════════════════════════════════════
// FLUXION E2E - Calendario Page Object
// ═══════════════════════════════════════════════════════════════════

import { BasePage } from './BasePage';

export class CalendarioPage extends BasePage {
  get selectors() {
    return {
      header: 'h1:has-text("Calendario")',
      nuovoAppuntamentoButton: 'button:has-text("Nuovo Appuntamento")',

      // Calendar navigation
      prevMonthButton: 'button[aria-label="Previous month"], button:has-text("←")',
      nextMonthButton: 'button[aria-label="Next month"], button:has-text("→")',
      todayButton: 'button:has-text("Oggi")',
      currentMonth: '[data-testid="current-month"]', // TODO: Add to CalendarioPage

      // Calendar grid
      calendarGrid: '[data-testid="calendar-grid"]',
      dayCell: (date: string) => `[data-date="${date}"]`,
      appointmentInDay: (date: string) => `[data-date="${date}"] [data-testid="appointment-item"]`,

      // Dialog
      dialog: '[role="dialog"]',
      dialogClienteSelect: '[name="cliente_id"]',
      dialogServizioSelect: '[name="servizio_id"]',
      dialogOperatoreSelect: '[name="operatore_id"]',
      dialogDataOraInput: '[name="data_ora_inizio"]',
      dialogDurataInput: '[name="durata_minuti"]',
      dialogPrezzoInput: '[name="prezzo"]',
      dialogScontoInput: '[name="sconto_percentuale"]',
      dialogNoteInput: '[name="note"]',
      dialogNoteInterneInput: '[name="note_interne"]',
      dialogSaveButton: 'button[type="submit"]:has-text("Crea Appuntamento")',
      dialogCancelButton: 'button:has-text("Annulla")',

      // Error messages
      conflictError: 'text="Conflitto: operatore già impegnato"',
      validationError: '[data-testid="validation-error"]',

      // Stats footer
      statsFooter: '[data-testid="calendar-stats"]',
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

  async clickNuovoAppuntamento(): Promise<void> {
    await this.click(this.selectors.nuovoAppuntamentoButton);
  }

  async goToPreviousMonth(): Promise<void> {
    await this.click(this.selectors.prevMonthButton);
  }

  async goToNextMonth(): Promise<void> {
    await this.click(this.selectors.nextMonthButton);
  }

  async goToToday(): Promise<void> {
    await this.click(this.selectors.todayButton);
  }

  async fillAppuntamentoForm(data: {
    clienteId: string;
    servizioId: string;
    operatoreId?: string;
    dataOraInizio: string; // YYYY-MM-DDTHH:mm
    durata?: number;
    prezzo?: number;
    sconto?: number;
    note?: string;
    noteInterne?: string;
  }): Promise<void> {
    // Select cliente
    await this.selectByValue(this.selectors.dialogClienteSelect, data.clienteId);

    // Select servizio (this should auto-fill prezzo and durata)
    await this.selectByValue(this.selectors.dialogServizioSelect, data.servizioId);

    // Wait for auto-fill to complete
    await this.pause(500);

    // Select operatore if provided
    if (data.operatoreId) {
      await this.selectByValue(this.selectors.dialogOperatoreSelect, data.operatoreId);
    }

    // Set date/time
    await this.clearAndSetValue(this.selectors.dialogDataOraInput, data.dataOraInizio);

    // Override durata if provided (otherwise uses auto-filled value)
    if (data.durata !== undefined) {
      await this.clearAndSetValue(this.selectors.dialogDurataInput, data.durata);
    }

    // Override prezzo if provided
    if (data.prezzo !== undefined) {
      await this.clearAndSetValue(this.selectors.dialogPrezzoInput, data.prezzo);
    }

    // Set sconto if provided
    if (data.sconto !== undefined) {
      await this.clearAndSetValue(this.selectors.dialogScontoInput, data.sconto);
    }

    // Set notes
    if (data.note) {
      await this.clearAndSetValue(this.selectors.dialogNoteInput, data.note);
    }

    if (data.noteInterne) {
      await this.clearAndSetValue(this.selectors.dialogNoteInterneInput, data.noteInterne);
    }
  }

  async saveAppuntamento(): Promise<void> {
    await this.click(this.selectors.dialogSaveButton);
  }

  async createAppuntamento(data: {
    clienteId: string;
    servizioId: string;
    operatoreId?: string;
    dataOraInizio: string;
    durata?: number;
    prezzo?: number;
    sconto?: number;
    note?: string;
    noteInterne?: string;
  }): Promise<void> {
    await this.clickNuovoAppuntamento();
    await this.fillAppuntamentoForm(data);
    await this.saveAppuntamento();

    // Wait for either success (dialog closes) or error (conflict message appears)
    await this.pause(1000);
  }

  async hasConflictError(): Promise<boolean> {
    return await this.exists(this.selectors.conflictError);
  }

  async isDialogOpen(): Promise<boolean> {
    return await this.exists(this.selectors.dialog);
  }

  async getAppointmentCountForDate(date: string): Promise<number> {
    return await this.getElementCount(this.selectors.appointmentInDay(date));
  }

  async clickAppointmentInDay(date: string, appointmentIndex = 0): Promise<void> {
    const appointments = await $$(this.selectors.appointmentInDay(date));
    if (appointments[appointmentIndex]) {
      await appointments[appointmentIndex].click();
    }
  }
}

export const calendarioPage = new CalendarioPage();
