// ═══════════════════════════════════════════════════════════════════
// FLUXION E2E - Booking Module Tests
// ═══════════════════════════════════════════════════════════════════

describe('Booking Module - Calendario', () => {
  beforeEach(async () => {
    // Navigate to app root
    await browser.url('/');
    await browser.pause(1000);
  });

  it('should navigate to Calendario from sidebar', async () => {
    const calendarBtn = await $('[data-testid="sidebar-calendario"]');
    await expect(calendarBtn).toBeDisplayed();
    await calendarBtn.click();
    await browser.pause(500);

    const pageTitle = await $('h1');
    const text = await pageTitle.getText();
    expect(text).toContain('Calendario');
  });

  it('should open new appointment dialog', async () => {
    // Navigate to Calendario
    const calendarBtn = await $('[data-testid="sidebar-calendario"]');
    await calendarBtn.click();
    await browser.pause(500);

    // Click "Nuovo Appuntamento"
    const newBtn = await $('[data-testid="new-appointment"]');
    await expect(newBtn).toBeDisplayed();
    await newBtn.click();
    await browser.pause(500);

    // Verify form is visible
    const form = await $('[data-testid="appointment-form"]');
    await expect(form).toBeDisplayed();
  });

  it('should have date/time input in appointment form', async () => {
    // Navigate to Calendario
    const calendarBtn = await $('[data-testid="sidebar-calendario"]');
    await calendarBtn.click();
    await browser.pause(500);

    // Open new appointment dialog
    const newBtn = await $('[data-testid="new-appointment"]');
    await newBtn.click();
    await browser.pause(500);

    // Check datetime input exists
    const datetimeInput = await $('[data-testid="input-data-ora"]');
    await expect(datetimeInput).toBeDisplayed();
  });

  it('should have submit and cancel buttons', async () => {
    // Navigate to Calendario
    const calendarBtn = await $('[data-testid="sidebar-calendario"]');
    await calendarBtn.click();
    await browser.pause(500);

    // Open dialog
    const newBtn = await $('[data-testid="new-appointment"]');
    await newBtn.click();
    await browser.pause(500);

    // Check buttons
    const submitBtn = await $('[data-testid="btn-submit"]');
    const cancelBtn = await $('[data-testid="btn-cancel"]');

    await expect(submitBtn).toBeDisplayed();
    await expect(cancelBtn).toBeDisplayed();
  });

  it('should close dialog on cancel', async () => {
    // Navigate to Calendario
    const calendarBtn = await $('[data-testid="sidebar-calendario"]');
    await calendarBtn.click();
    await browser.pause(500);

    // Open dialog
    const newBtn = await $('[data-testid="new-appointment"]');
    await newBtn.click();
    await browser.pause(500);

    // Cancel
    const cancelBtn = await $('[data-testid="btn-cancel"]');
    await cancelBtn.click();
    await browser.pause(500);

    // Form should not be visible
    const form = await $('[data-testid="appointment-form"]');
    const isDisplayed = await form.isDisplayed().catch(() => false);
    expect(isDisplayed).toBe(false);
  });
});
