// ═══════════════════════════════════════════════════════════════════
// FLUXION E2E - Cashier Module Tests
// ═══════════════════════════════════════════════════════════════════

describe('Cashier Module - Cassa', () => {
  beforeEach(async () => {
    await browser.url('/');
    await browser.pause(1000);
  });

  it('should navigate to Cassa from sidebar', async () => {
    const cassaBtn = await $('[data-testid="sidebar-cassa"]');
    await expect(cassaBtn).toBeDisplayed();
    await cassaBtn.click();
    await browser.pause(500);

    const pageTitle = await $('h1');
    const text = await pageTitle.getText();
    expect(text).toContain('Cassa');
  });

  it('should display balance card', async () => {
    // Navigate to Cassa
    const cassaBtn = await $('[data-testid="sidebar-cassa"]');
    await cassaBtn.click();
    await browser.pause(500);

    // Check balance card
    const balanceCard = await $('[data-testid="cashier-balance"]');
    await expect(balanceCard).toBeDisplayed();
  });

  it('should have cash-in button', async () => {
    // Navigate to Cassa
    const cassaBtn = await $('[data-testid="sidebar-cassa"]');
    await cassaBtn.click();
    await browser.pause(500);

    // Check cash-in button
    const cashInBtn = await $('[data-testid="btn-cash-in"]');
    await expect(cashInBtn).toBeDisplayed();
  });

  it('should open cash entry form', async () => {
    // Navigate to Cassa
    const cassaBtn = await $('[data-testid="sidebar-cassa"]');
    await cassaBtn.click();
    await browser.pause(500);

    // Click cash-in button
    const cashInBtn = await $('[data-testid="btn-cash-in"]');
    await cashInBtn.click();
    await browser.pause(500);

    // Check form is visible
    const form = await $('[data-testid="cashier-form"]');
    await expect(form).toBeDisplayed();
  });

  it('should have amount input in form', async () => {
    // Navigate to Cassa
    const cassaBtn = await $('[data-testid="sidebar-cassa"]');
    await cassaBtn.click();
    await browser.pause(500);

    // Open form
    const cashInBtn = await $('[data-testid="btn-cash-in"]');
    await cashInBtn.click();
    await browser.pause(500);

    // Check amount input
    const amountInput = await $('[data-testid="input-amount"]');
    await expect(amountInput).toBeDisplayed();
  });

  it('should fill amount and see save button', async () => {
    // Navigate to Cassa
    const cassaBtn = await $('[data-testid="sidebar-cassa"]');
    await cassaBtn.click();
    await browser.pause(500);

    // Open form
    const cashInBtn = await $('[data-testid="btn-cash-in"]');
    await cashInBtn.click();
    await browser.pause(500);

    // Fill amount
    const amountInput = await $('[data-testid="input-amount"]');
    await amountInput.setValue('50.00');

    // Check save button
    const saveBtn = await $('[data-testid="btn-save-cashier"]');
    await expect(saveBtn).toBeDisplayed();
  });
});
