/**
 * Impostazioni Page Object
 * Covers the managed Sara receptionist and voice-quality controls.
 */

import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './BasePage';

export class ImpostazioniPage extends BasePage {
  readonly url = '/impostazioni';

  readonly voiceAgentHeading: Locator;
  readonly statusBadge: Locator;
  readonly managedNotice: Locator;
  readonly noCredentialNotice: Locator;
  readonly qualityHeading: Locator;
  readonly automaticRadio: Locator;
  readonly qualityRadio: Locator;
  readonly fastRadio: Locator;
  readonly saveModeButton: Locator;

  constructor(page: Page) {
    super(page);

    this.voiceAgentHeading = page
      .getByRole('heading', { name: /Sara — Receptionist AI/i, level: 2 })
      .last();
    this.statusBadge = page.getByText(/Attiva|Non disponibile|Verifica\.\.\./i).last();
    this.managedNotice = page.getByText('Gestita automaticamente da FLUXION AI');
    this.noCredentialNotice = page.getByText(/Nessuna chiave API da inserire/i);
    this.qualityHeading = page.getByRole('heading', { name: /Qualità Voce Sara/i });
    this.automaticRadio = page.getByRole('radio', { name: /Automatico \(consigliato\)/i });
    this.qualityRadio = page.getByRole('radio', { name: /Alta Qualità \(Qwen3-TTS\)/i });
    this.fastRadio = page.getByRole('radio', { name: /Veloce \(Piper\)/i });
    this.saveModeButton = page.getByRole('button', { name: /Salva modalità/i });
  }

  async scrollToVoiceAgentSection(): Promise<void> {
    await this.voiceAgentHeading.scrollIntoViewIfNeeded();
  }

  async selectQualityMode(): Promise<void> {
    await this.qualityRadio.check();
  }

  async saveVoiceMode(): Promise<void> {
    await this.saveModeButton.click();
  }

  async expectPageLoaded(): Promise<void> {
    await this.waitForPageLoad();
    await expect(this.page.getByRole('heading', { name: /Impostazioni/i, level: 1 })).toBeVisible();
  }

  async expectVoiceAgentSectionVisible(): Promise<void> {
    await this.scrollToVoiceAgentSection();
    await expect(this.voiceAgentHeading).toBeVisible();
  }

  async expectStatusBadge(): Promise<void> {
    await this.scrollToVoiceAgentSection();
    await expect(this.statusBadge).toBeVisible();
  }

  async expectManagedConfiguration(): Promise<void> {
    await this.scrollToVoiceAgentSection();
    await expect(this.managedNotice).toBeVisible();
    await expect(this.noCredentialNotice).toBeVisible();
  }

  async expectQualityControls(): Promise<void> {
    await this.qualityHeading.scrollIntoViewIfNeeded();
    await expect(this.automaticRadio).toBeVisible();
    await expect(this.qualityRadio).toBeVisible();
    await expect(this.fastRadio).toBeVisible();
    await expect(this.saveModeButton).toBeVisible();
  }

  async takeVoiceSettingsScreenshot(name = 'voice-agent-settings'): Promise<void> {
    await this.scrollToVoiceAgentSection();
    await this.takeScreenshot(name);
  }
}
