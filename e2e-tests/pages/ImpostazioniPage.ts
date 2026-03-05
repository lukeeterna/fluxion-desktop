/**
 * Impostazioni Page Object
 * Includes VoiceAgentSettings section locators
 */

import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './BasePage';

export class ImpostazioniPage extends BasePage {
  readonly url = '/impostazioni';

  readonly voiceAgentHeading: Locator;
  readonly statusBadge: Locator;
  readonly groqKeyInput: Locator;
  // data-testid on buttons for reliable cross-page scoping
  readonly testButton: Locator;
  readonly saveButton: Locator;
  // Eye toggle scoped to the input wrapper div
  readonly eyeToggle: Locator;

  constructor(page: Page) {
    super(page);

    this.voiceAgentHeading = page.getByRole('heading', { name: /Assistente Vocale Sara/i });
    this.statusBadge = page.locator('span').filter({ hasText: /Attivo|Non configurata/ }).first();
    this.groqKeyInput = page.locator('#groq-api-key');
    this.testButton = page.getByTestId('voice-settings-testa');
    this.saveButton = page.getByTestId('voice-settings-salva');
    // Ghost button inside the relative div that wraps the password input
    this.eyeToggle = page.locator('div.relative').filter({ has: page.locator('#groq-api-key') }).getByRole('button');
  }

  // =============================================================================
  // ACTIONS
  // =============================================================================

  async fillGroqKey(key: string): Promise<void> {
    await this.groqKeyInput.fill(key);
  }

  async clickTesta(): Promise<void> {
    await this.testButton.click();
  }

  async clickSalva(): Promise<void> {
    await this.saveButton.click();
  }

  async scrollToVoiceAgentSection(): Promise<void> {
    await this.voiceAgentHeading.scrollIntoViewIfNeeded();
  }

  async toggleKeyVisibility(): Promise<void> {
    await this.eyeToggle.click();
  }

  // =============================================================================
  // ASSERTIONS
  // =============================================================================

  async expectPageLoaded(): Promise<void> {
    await this.waitForPageLoad();
    await expect(this.page.getByRole('heading', { name: /Impostazioni/i, level: 1 })).toBeVisible();
  }

  async expectVoiceAgentSectionVisible(): Promise<void> {
    await this.scrollToVoiceAgentSection();
    await expect(this.voiceAgentHeading).toBeVisible();
  }

  async expectStatusBadge(status?: 'Attivo' | 'Non configurata'): Promise<void> {
    if (status) {
      await expect(this.page.locator('span').filter({ hasText: status }).first()).toBeVisible();
    } else {
      await expect(this.statusBadge).toBeVisible();
    }
  }

  async expectGroqInputVisible(): Promise<void> {
    await expect(this.groqKeyInput).toBeVisible();
    await expect(this.groqKeyInput).toHaveAttribute('type', 'password');
  }

  async expectActionButtonsVisible(): Promise<void> {
    await expect(this.testButton).toBeVisible();
    await expect(this.saveButton).toBeVisible();
  }

  async takeVoiceSettingsScreenshot(name = 'voice-agent-settings'): Promise<void> {
    await this.scrollToVoiceAgentSection();
    await this.takeScreenshot(name);
  }
}
