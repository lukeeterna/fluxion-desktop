// ═══════════════════════════════════════════════════════════════════
// FLUXION E2E - Servizi Validation Tests
// Test servizi form validation (BUG #3 regression tests)
// ═══════════════════════════════════════════════════════════════════

import { dashboardPage, serviziPage } from '../pages';
import { TestData } from '../fixtures/test-data';
import { waitForPageLoad, takeScreenshot } from '../utils/test-helpers';

describe('Servizi Validation Tests', () => {
  beforeEach(async () => {
    await waitForPageLoad();
    await dashboardPage.navigateToServizi();
    await waitForPageLoad();
  });

  it('should NOT allow creating servizio with only nome (BUG #3 regression)', async () => {
    await serviziPage.clickNuovoServizio();

    // Fill only nome, leave prezzo and durata empty
    await serviziPage.fillServizioForm({
      nome: 'Test Only Nome',
      // prezzo and durata intentionally missing
    });

    await serviziPage.saveServizio();

    // Form should NOT submit - dialog should stay open
    await browser.pause(1000);
    const dialogStillOpen = await serviziPage.isDialogOpen();
    expect(dialogStillOpen).toBe(true);

    // TODO: Check for validation error messages
    // const hasPrezzoError = await serviziPage.hasValidationError(serviziPage.selectors.prezzoError);
    // const hasDurataError = await serviziPage.hasValidationError(serviziPage.selectors.durataError);
    // expect(hasPrezzoError || hasDurataError).toBe(true);
  });

  it('should create servizio with all required fields', async () => {
    const servizio = TestData.servizi.taglioUomo;
    const initialCount = await serviziPage.getTableRowCount();

    await serviziPage.createServizio(servizio);

    // Wait for servizio to be created
    await serviziPage.waitUntil(
      async () => (await serviziPage.getTableRowCount()) === initialCount + 1,
      { timeout: 5000, timeoutMsg: 'Servizio not created' }
    );
  });

  it('should handle prezzo = 0 (free service)', async () => {
    const servizio = TestData.edgeCases.servizi.prezzoZero;

    await serviziPage.createServizio(servizio);
    await browser.pause(1000);

    // Should be created successfully
    const dialogClosed = !(await serviziPage.isDialogOpen());
    expect(dialogClosed).toBe(true);
  });

  it('should handle very high price (999.99)', async () => {
    const servizio = TestData.edgeCases.servizi.prezzoAlto;

    await serviziPage.createServizio(servizio);
    await browser.pause(1000);

    const dialogClosed = !(await serviziPage.isDialogOpen());
    expect(dialogClosed).toBe(true);
  });

  it('should reject negative price', async () => {
    await serviziPage.clickNuovoServizio();

    await serviziPage.fillServizioForm(TestData.edgeCases.servizi.prezzoNegativo);
    await serviziPage.saveServizio();

    await browser.pause(1000);

    // Should fail validation
    const dialogStillOpen = await serviziPage.isDialogOpen();
    expect(dialogStillOpen).toBe(true);
  });

  it('should reject duration = 0', async () => {
    await serviziPage.clickNuovoServizio();

    await serviziPage.fillServizioForm(TestData.edgeCases.servizi.durataZero);
    await serviziPage.saveServizio();

    await browser.pause(1000);

    // Should fail validation
    const dialogStillOpen = await serviziPage.isDialogOpen();
    expect(dialogStillOpen).toBe(true);
  });

  it('should handle nome with special characters', async () => {
    const servizio = TestData.edgeCases.servizi.nomeSpecialChars;

    await serviziPage.createServizio(servizio);
    await browser.pause(1000);

    const dialogClosed = !(await serviziPage.isDialogOpen());
    expect(dialogClosed).toBe(true);
  });

  it('should handle nome with emoji', async () => {
    const servizio = TestData.edgeCases.servizi.nomeEmoji;

    await serviziPage.createServizio(servizio);
    await browser.pause(1000);

    const dialogClosed = !(await serviziPage.isDialogOpen());
    expect(dialogClosed).toBe(true);
  });

  it('should handle very long nome', async () => {
    const servizio = TestData.edgeCases.servizi.nomeLungo;

    await serviziPage.createServizio(servizio);
    await browser.pause(1000);

    const dialogClosed = !(await serviziPage.isDialogOpen());
    expect(dialogClosed).toBe(true);
  });

  it('should handle 8-hour duration', async () => {
    const servizio = TestData.edgeCases.servizi.durataLunga;

    await serviziPage.createServizio(servizio);
    await browser.pause(1000);

    const dialogClosed = !(await serviziPage.isDialogOpen());
    expect(dialogClosed).toBe(true);
  });

  it('should reject nome < 2 characters', async () => {
    await serviziPage.clickNuovoServizio();

    await serviziPage.fillServizioForm(TestData.edgeCases.servizi.nomeCorto);
    await serviziPage.saveServizio();

    await browser.pause(1000);

    // Should fail validation
    const dialogStillOpen = await serviziPage.isDialogOpen();
    expect(dialogStillOpen).toBe(true);

    // TODO: Check for specific error message
    // const hasNomeError = await serviziPage.hasValidationError(serviziPage.selectors.nomeError);
    // expect(hasNomeError).toBe(true);
  });

  afterEach(async function () {
    if (this.currentTest?.state === 'failed') {
      await takeScreenshot(`servizi-validation-${this.currentTest.title}`);
    }
  });
});
