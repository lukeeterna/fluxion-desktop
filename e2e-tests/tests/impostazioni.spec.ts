/**
 * Impostazioni E2E Tests — managed Sara receptionist.
 *
 * Verifies the production UI contract: no customer API credential, observable
 * runtime state, and selectable TTS quality with fail-visible offline saving.
 */

import { test, expect } from '../fixtures/test.fixtures';

test.describe('Impostazioni Page @smoke @impostazioni', () => {
  test.beforeEach(async ({ impostazioniPage }) => {
    await impostazioniPage.goto();
    await impostazioniPage.expectPageLoaded();
  });

  test('impostazioni page loads with heading', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /Impostazioni/i, level: 1 })).toBeVisible();
  });

  test('impostazioni page has no critical console errors', async ({ page }) => {
    const jsErrors: Error[] = [];
    page.on('pageerror', (error) => jsErrors.push(error));

    await page.goto('/#/impostazioni');
    await page.waitForLoadState('domcontentloaded');

    expect(jsErrors).toHaveLength(0);
  });
});

test.describe('Managed Sara Section @impostazioni @voice-settings', () => {
  test.beforeEach(async ({ impostazioniPage }) => {
    await impostazioniPage.goto();
    await impostazioniPage.expectPageLoaded();
  });

  test('Sara receptionist section is visible', async ({ impostazioniPage }) => {
    await impostazioniPage.expectVoiceAgentSectionVisible();
  });

  test('runtime status is observable', async ({ impostazioniPage }) => {
    await impostazioniPage.expectStatusBadge();
  });

  test('managed FLUXION AI configuration is explicit', async ({ impostazioniPage }) => {
    await impostazioniPage.expectManagedConfiguration();
  });

  test('customer API credential input is absent', async ({ page }) => {
    await expect(page.locator('#groq-api-key')).toHaveCount(0);
    await expect(page.getByText(/Nessuna chiave API da inserire/i)).toBeVisible();
  });

  test('voice-quality controls are present', async ({ impostazioniPage }) => {
    await impostazioniPage.expectQualityControls();
  });

  test('screenshot: managed Sara settings section', async ({ impostazioniPage }) => {
    await impostazioniPage.takeVoiceSettingsScreenshot('voice-agent-settings');
  });
});

test.describe('Sara Voice Quality Interactions @voice-settings', () => {
  test.beforeEach(async ({ impostazioniPage }) => {
    await impostazioniPage.goto();
    await impostazioniPage.expectPageLoaded();
    await impostazioniPage.expectQualityControls();
  });

  test('automatic quality is selected by default', async ({ impostazioniPage }) => {
    await expect(impostazioniPage.automaticRadio).toBeChecked();
  });

  test('quality mode can be selected', async ({ impostazioniPage }) => {
    await impostazioniPage.selectQualityMode();
    await expect(impostazioniPage.qualityRadio).toBeChecked();
  });

  test('offline save reports that Sara is unreachable', async ({ impostazioniPage, page }) => {
    await impostazioniPage.selectQualityMode();
    await impostazioniPage.saveVoiceMode();
    await expect(page.getByText(/Sara non raggiungibile/i)).toBeVisible({ timeout: 6000 });
  });
});
