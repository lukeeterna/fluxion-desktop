// ═══════════════════════════════════════════════════════════════════
// FLUXION E2E - Appuntamenti Conflict Detection Tests
// Test appointment creation and conflict detection (BUG #1, #2 regression)
// ═══════════════════════════════════════════════════════════════════

import { dashboardPage, clientiPage, serviziPage, calendarioPage } from '../pages';
import { TestData } from '../fixtures/test-data';
import { waitForPageLoad, generateAppointmentDateTime, takeScreenshot } from '../utils/test-helpers';

describe('Appuntamenti Conflict Detection Tests', () => {
  let clienteId: string;
  let servizioId: string;
  let operatoreId: string;

  before(async () => {
    await waitForPageLoad();

    // Setup: Create test cliente, servizio, operatore
    // TODO: Implement these after we have IDs returned from create operations
    // For now, we'll use placeholder IDs and assume data exists
    clienteId = 'test-cliente-id'; // TODO: Get from created cliente
    servizioId = 'test-servizio-id'; // TODO: Get from created servizio
    operatoreId = 'test-operatore-id'; // TODO: Get from created operatore
  });

  beforeEach(async () => {
    await waitForPageLoad();
    await dashboardPage.navigateToCalendario();
    await waitForPageLoad();
  });

  it('should create an appointment successfully (BUG #1 regression)', async () => {
    const appointmentDateTime = generateAppointmentDateTime(1, 10); // Tomorrow at 10:00

    await calendarioPage.createAppuntamento({
      clienteId,
      servizioId,
      operatoreId,
      dataOraInizio: appointmentDateTime,
      durata: 30,
      prezzo: 25.0,
    });

    // Wait for dialog to close (success)
    await calendarioPage.waitUntil(
      async () => !(await calendarioPage.isDialogOpen()),
      {
        timeout: 5000,
        timeoutMsg: 'Dialog did not close after creating appointment (BUG #1 may have regressed)',
      }
    );

    // Verify no conflict error appeared
    const hasConflict = await calendarioPage.hasConflictError();
    expect(hasConflict).toBe(false);
  });

  it('should detect conflict when same operator same time (BUG #2 error handling)', async () => {
    const appointmentDateTime = generateAppointmentDateTime(2, 11); // 2 days from now at 11:00

    // Create first appointment
    await calendarioPage.createAppuntamento({
      clienteId,
      servizioId,
      operatoreId,
      dataOraInizio: appointmentDateTime,
      durata: 30,
    });

    // Wait for first to complete
    await browser.pause(2000);

    // Try to create second with SAME operator SAME time
    await calendarioPage.createAppuntamento({
      clienteId,
      servizioId,
      operatore: operatoreId, // SAME operator!
      dataOraInizio: appointmentDateTime, // SAME time!
      durata: 30,
    });

    await browser.pause(1000);

    // Should show conflict error
    const hasConflict = await calendarioPage.hasConflictError();
    expect(hasConflict).toBe(true);

    // Dialog should stay open
    const dialogOpen = await calendarioPage.isDialogOpen();
    expect(dialogOpen).toBe(true);
  });

  it('should allow same time with different operators', async () => {
    const appointmentDateTime = generateAppointmentDateTime(3, 14); // 3 days from now at 14:00

    // Create first appointment with operatore 1
    await calendarioPage.createAppuntamento({
      clienteId,
      servizioId,
      operatoreId: operatoreId,
      dataOraInizio: appointmentDateTime,
      durata: 30,
    });

    await browser.pause(2000);

    // Create second with DIFFERENT operator, SAME time
    const otherOperatoreId = 'other-operatore-id'; // TODO: Use real ID
    await calendarioPage.createAppuntamento({
      clienteId,
      servizioId,
      operatoreId: otherOperatoreId, // DIFFERENT operator!
      dataOraInizio: appointmentDateTime, // SAME time - should be OK!
      durata: 30,
    });

    await browser.pause(1000);

    // Should NOT show conflict
    const hasConflict = await calendarioPage.hasConflictError();
    expect(hasConflict).toBe(false);
  });

  it('should allow back-to-back appointments (no conflict)', async () => {
    const appointmentDateTime1 = generateAppointmentDateTime(4, 9); // 4 days from now at 09:00

    // Create first appointment 09:00-09:30
    await calendarioPage.createAppuntamento({
      clienteId,
      servizioId,
      operatoreId,
      dataOraInizio: appointmentDateTime1,
      durata: 30,
    });

    await browser.pause(2000);

    // Create second appointment starting EXACTLY when first ends (09:30)
    const appointmentDateTime2 = generateAppointmentDateTime(4, 9.5); // 09:30
    await calendarioPage.createAppuntamento({
      clienteId,
      servizioId,
      operatoreId, // SAME operator
      dataOraInizio: appointmentDateTime2, // Starts exactly when previous ends
      durata: 30,
    });

    await browser.pause(1000);

    // Should NOT conflict (back-to-back is OK)
    const hasConflict = await calendarioPage.hasConflictError();
    expect(hasConflict).toBe(false);
  });

  it('should handle datetime format correctly (RFC3339 conversion)', async () => {
    // This test verifies BUG #1 fix: datetime-local → RFC3339 conversion

    const appointmentDateTime = generateAppointmentDateTime(5, 15);

    await calendarioPage.createAppuntamento({
      clienteId,
      servizioId,
      operatoreId,
      dataOraInizio: appointmentDateTime, // Format: YYYY-MM-DDTHH:mm
      durata: 45,
      prezzo: 30.0,
    });

    // Should succeed without "Invalid start datetime" error
    await calendarioPage.waitUntil(
      async () => !(await calendarioPage.isDialogOpen()),
      {
        timeout: 5000,
        timeoutMsg: 'Datetime format conversion failed (BUG #1 regression)',
      }
    );
  });

  afterEach(async function () {
    if (this.currentTest?.state === 'failed') {
      await takeScreenshot(`appuntamenti-conflict-${this.currentTest.title}`);
    }
  });

  after(async () => {
    // TODO: Cleanup test data
  });
});
