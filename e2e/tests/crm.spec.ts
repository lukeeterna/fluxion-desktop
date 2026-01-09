// ═══════════════════════════════════════════════════════════════════
// FLUXION E2E - CRM Module Tests
// ═══════════════════════════════════════════════════════════════════

describe('CRM Module - Clienti', () => {
  beforeEach(async () => {
    await browser.url('/');
    await browser.pause(1000);
  });

  it('should navigate to Clienti from sidebar', async () => {
    const clientiBtn = await $('[data-testid="sidebar-clienti"]');
    await expect(clientiBtn).toBeDisplayed();
    await clientiBtn.click();
    await browser.pause(500);

    const pageTitle = await $('h1');
    const text = await pageTitle.getText();
    expect(text).toContain('Clienti');
  });

  it('should open new client dialog', async () => {
    // Navigate to Clienti
    const clientiBtn = await $('[data-testid="sidebar-clienti"]');
    await clientiBtn.click();
    await browser.pause(500);

    // Click "Nuovo Cliente"
    const newBtn = await $('[data-testid="new-client"]');
    await expect(newBtn).toBeDisplayed();
    await newBtn.click();
    await browser.pause(500);

    // Verify form is visible
    const form = await $('[data-testid="client-form"]');
    await expect(form).toBeDisplayed();
  });

  it('should have all required form fields', async () => {
    // Navigate to Clienti
    const clientiBtn = await $('[data-testid="sidebar-clienti"]');
    await clientiBtn.click();
    await browser.pause(500);

    // Open new client dialog
    const newBtn = await $('[data-testid="new-client"]');
    await newBtn.click();
    await browser.pause(500);

    // Check form fields
    const nomeInput = await $('[data-testid="input-nome"]');
    const cognomeInput = await $('[data-testid="input-cognome"]');
    const telefonoInput = await $('[data-testid="input-telefono"]');
    const emailInput = await $('[data-testid="input-email"]');

    await expect(nomeInput).toBeDisplayed();
    await expect(cognomeInput).toBeDisplayed();
    await expect(telefonoInput).toBeDisplayed();
    await expect(emailInput).toBeDisplayed();
  });

  it('should fill client form fields', async () => {
    // Navigate to Clienti
    const clientiBtn = await $('[data-testid="sidebar-clienti"]');
    await clientiBtn.click();
    await browser.pause(500);

    // Open new client dialog
    const newBtn = await $('[data-testid="new-client"]');
    await newBtn.click();
    await browser.pause(500);

    // Fill form
    const nomeInput = await $('[data-testid="input-nome"]');
    await nomeInput.setValue('Mario');

    const cognomeInput = await $('[data-testid="input-cognome"]');
    await cognomeInput.setValue('Rossi');

    const telefonoInput = await $('[data-testid="input-telefono"]');
    await telefonoInput.setValue('3331234567');

    const emailInput = await $('[data-testid="input-email"]');
    await emailInput.setValue('mario.rossi@example.com');

    // Verify values are set
    await expect(nomeInput).toHaveValue('Mario');
    await expect(cognomeInput).toHaveValue('Rossi');
  });

  it('should have save button', async () => {
    // Navigate to Clienti
    const clientiBtn = await $('[data-testid="sidebar-clienti"]');
    await clientiBtn.click();
    await browser.pause(500);

    // Open dialog
    const newBtn = await $('[data-testid="new-client"]');
    await newBtn.click();
    await browser.pause(500);

    // Check save button
    const saveBtn = await $('[data-testid="btn-save-client"]');
    await expect(saveBtn).toBeDisplayed();
  });
});
