// ═══════════════════════════════════════════════════════════════════
// FLUXION E2E - Voice Agent Module Tests
// ═══════════════════════════════════════════════════════════════════

describe('Voice Agent Module', () => {
  beforeEach(async () => {
    await browser.url('/');
    await browser.pause(1000);
  });

  it('should navigate to Voice Agent from sidebar', async () => {
    const voiceBtn = await $('[data-testid="sidebar-voice"]');
    await expect(voiceBtn).toBeDisplayed();
    await voiceBtn.click();
    await browser.pause(500);

    const pageTitle = await $('h1');
    const text = await pageTitle.getText();
    expect(text.toLowerCase()).toContain('voice');
  });

  it('should display start button when not running', async () => {
    // Navigate to Voice Agent
    const voiceBtn = await $('[data-testid="sidebar-voice"]');
    await voiceBtn.click();
    await browser.pause(500);

    // Check start button
    const startBtn = await $('[data-testid="btn-start-voice"]');
    await expect(startBtn).toBeDisplayed();
  });

  it('should display transcript area', async () => {
    // Navigate to Voice Agent
    const voiceBtn = await $('[data-testid="sidebar-voice"]');
    await voiceBtn.click();
    await browser.pause(500);

    // Check transcript area
    const transcript = await $('[data-testid="voice-transcript"]');
    await expect(transcript).toBeDisplayed();
  });

  it('should have text input for chat', async () => {
    // Navigate to Voice Agent
    const voiceBtn = await $('[data-testid="sidebar-voice"]');
    await voiceBtn.click();
    await browser.pause(500);

    // Check input
    const textInput = await $('[data-testid="input-voice-text"]');
    await expect(textInput).toBeDisplayed();
  });

  it('should have send button', async () => {
    // Navigate to Voice Agent
    const voiceBtn = await $('[data-testid="sidebar-voice"]');
    await voiceBtn.click();
    await browser.pause(500);

    // Check send button
    const sendBtn = await $('[data-testid="btn-send-voice"]');
    await expect(sendBtn).toBeDisplayed();
  });

  it('should have disabled input when not running', async () => {
    // Navigate to Voice Agent
    const voiceBtn = await $('[data-testid="sidebar-voice"]');
    await voiceBtn.click();
    await browser.pause(500);

    // Check input is disabled
    const textInput = await $('[data-testid="input-voice-text"]');
    const isDisabled = await textInput.getAttribute('disabled');
    expect(isDisabled).toBeTruthy();
  });
});
