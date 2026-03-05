/**
 * Impostazioni E2E Tests — VoiceAgentSettings section
 *
 * Layer 2 autonomous verification per CoVe 2026.
 * Verifies DOM presence and basic interactions — no DB state required.
 * Screenshots saved to reports/screenshots/ as P0.5 evidence.
 */

import { test, expect } from '../fixtures/test.fixtures';

test.describe('Impostazioni Page @smoke @impostazioni', () => {
  test.beforeEach(async ({ impostazioniPage }) => {
    await impostazioniPage.goto();
    await impostazioniPage.expectPageLoaded();
  });

  test('impostazioni page loads with heading', async ({ impostazioniPage, page }) => {
    await expect(page.getByRole('heading', { name: /Impostazioni/i, level: 1 })).toBeVisible();
  });

  test('impostazioni page has no critical console errors', async ({ page }) => {
    const jsErrors: Error[] = [];
    page.on('pageerror', (e) => jsErrors.push(e));

    await page.goto('/#/impostazioni');
    await page.waitForLoadState('domcontentloaded');

    expect(jsErrors).toHaveLength(0);
  });
});

test.describe('VoiceAgentSettings Section @impostazioni @voice-settings', () => {
  test.beforeEach(async ({ impostazioniPage }) => {
    await impostazioniPage.goto();
    await impostazioniPage.expectPageLoaded();
  });

  test('voice agent section is visible with heading', async ({ impostazioniPage }) => {
    await impostazioniPage.expectVoiceAgentSectionVisible();
  });

  test('status badge is present (Attivo or Non configurata)', async ({ impostazioniPage }) => {
    await impostazioniPage.scrollToVoiceAgentSection();
    await impostazioniPage.expectStatusBadge();
  });

  test('groq key input is type=password', async ({ impostazioniPage }) => {
    await impostazioniPage.scrollToVoiceAgentSection();
    await impostazioniPage.expectGroqInputVisible();
  });

  test('Testa and Salva buttons are present', async ({ impostazioniPage }) => {
    await impostazioniPage.scrollToVoiceAgentSection();
    await impostazioniPage.expectActionButtonsVisible();
  });

  test('screenshot: voice agent settings section', async ({ impostazioniPage }) => {
    await impostazioniPage.scrollToVoiceAgentSection();
    await impostazioniPage.takeVoiceSettingsScreenshot('voice-agent-settings');
  });
});

test.describe('VoiceAgentSettings Interactions @voice-settings', () => {
  test.beforeEach(async ({ impostazioniPage }) => {
    await impostazioniPage.goto();
    await impostazioniPage.expectPageLoaded();
    await impostazioniPage.scrollToVoiceAgentSection();
  });

  test('empty key → Testa button is disabled', async ({ impostazioniPage }) => {
    // Component disables Testa when localKey is empty (disabled={!localKey})
    await impostazioniPage.groqKeyInput.clear();
    await expect(impostazioniPage.testButton).toBeDisabled();
  });

  test('invalid key format → Testa shows format error', async ({ impostazioniPage, page }) => {
    await impostazioniPage.fillGroqKey('invalid_key_format');
    await impostazioniPage.clickTesta();
    await expect(
      page.getByText(/Formato non valido|deve iniziare con gsk_/i)
    ).toBeVisible();
  });

  test('valid key prefix → Testa shows format valid or reachable', async ({ impostazioniPage, page }) => {
    await impostazioniPage.fillGroqKey('gsk_testkey1234567890abcdef');
    await impostazioniPage.clickTesta();
    // Wait for async test to complete (fetch to localhost:3002 will fail in test env)
    await expect(
      page.getByText(/Formato valido|raggiungibile/i)
    ).toBeVisible({ timeout: 6000 });
  });

  test('show/hide key toggle changes input type', async ({ impostazioniPage }) => {
    await impostazioniPage.fillGroqKey('gsk_somekey123');
    // Input starts as password
    await expect(impostazioniPage.groqKeyInput).toHaveAttribute('type', 'password');
    // Click the eye toggle button (scoped to the input wrapper div)
    await impostazioniPage.toggleKeyVisibility();
    await expect(impostazioniPage.groqKeyInput).toHaveAttribute('type', 'text');
  });
});
