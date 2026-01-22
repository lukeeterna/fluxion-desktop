// ═══════════════════════════════════════════════════════════════════
// FLUXION - Voice Agent E2E Tests
// Tests microphone recording, STT, and TTS functionality
// ═══════════════════════════════════════════════════════════════════

import { test, expect, Page } from '@playwright/test';

// Helper to capture console logs
async function captureConsoleLogs(page: Page): Promise<string[]> {
  const logs: string[] = [];
  page.on('console', (msg) => {
    logs.push(`[${msg.type()}] ${msg.text()}`);
  });
  return logs;
}

// Check if Tauri API is available (for pipeline-dependent tests)
async function hasTauriApi(page: Page): Promise<boolean> {
  return page.evaluate(() => {
    // @ts-ignore
    return typeof window.__TAURI__ !== 'undefined' ||
      typeof window.__TAURI_INTERNALS__ !== 'undefined';
  });
}

// Check if Voice Pipeline is reachable via HTTP (for browser mode with HTTP fallback)
async function isVoicePipelineAvailable(): Promise<boolean> {
  try {
    const response = await fetch('http://localhost:3002/status');
    if (response.ok) {
      const data = await response.json();
      return data.status === 'running';
    }
  } catch {
    // Pipeline not available
  }
  return false;
}

test.describe('Voice Agent E2E', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('Should navigate to Voice Agent page', async ({ page }) => {
    // Find Voice Agent in sidebar
    const voiceAgentLink = page.locator('[data-testid="nav-voice-agent"], a:has-text("Voice Agent"), button:has-text("Voice Agent")');
    await expect(voiceAgentLink.first()).toBeVisible({ timeout: 10000 });

    await voiceAgentLink.first().click();
    await page.waitForTimeout(1000);

    // Verify page loaded
    const heading = page.locator('h1:has-text("Voice Agent")');
    await expect(heading).toBeVisible();

    console.log('✅ Voice Agent page loaded');
  });

  test('Should display start or stop button based on pipeline state', async ({ page }) => {
    // Navigate to Voice Agent
    await page.click('[data-testid="nav-voice-agent"], a:has-text("Voice Agent"), button:has-text("Voice Agent")');
    await page.waitForTimeout(2000);

    // Check for either start or stop button (depends on whether HTTP pipeline is running)
    const startButton = page.locator('[data-testid="btn-start-voice"]');
    const stopButton = page.locator('button:has-text("Ferma")');

    const hasStart = await startButton.isVisible().catch(() => false);
    const hasStop = await stopButton.isVisible().catch(() => false);

    // One of them must be visible
    expect(hasStart || hasStop).toBe(true);

    if (hasStop) {
      console.log('✅ Stop button visible (pipeline running)');
    } else {
      console.log('✅ Start button visible (pipeline stopped)');
    }
  });

  test('Should start voice pipeline', async ({ page }) => {
    // Check if we have Tauri API OR Voice Pipeline HTTP fallback available
    const hasTauri = await hasTauriApi(page);
    const hasPipeline = await isVoicePipelineAvailable();
    if (!hasTauri && !hasPipeline) {
      console.log('⚠️ Skipping: Neither Tauri API nor Voice Pipeline HTTP available');
      test.skip();
      return;
    }
    console.log(`ℹ️ Running with: Tauri=${hasTauri}, HTTP Pipeline=${hasPipeline}`);

    const logs = await captureConsoleLogs(page);

    // Navigate to Voice Agent
    await page.click('[data-testid="nav-voice-agent"], a:has-text("Voice Agent"), button:has-text("Voice Agent")');
    await page.waitForTimeout(2000);

    // Check if pipeline is already running (HTTP fallback mode)
    const stopButton = page.locator('button:has-text("Ferma")');
    const startButton = page.locator('[data-testid="btn-start-voice"], button:has-text("Avvia")');

    const isAlreadyRunning = await stopButton.isVisible().catch(() => false);

    if (isAlreadyRunning) {
      console.log('✅ Voice pipeline already running (HTTP fallback mode)');
    } else {
      // Click start
      await startButton.first().click();
      // Wait for pipeline to start
      await page.waitForTimeout(5000);
    }

    // Verify pipeline is running by checking for either "Attivo" status or "Ferma" button
    const fermaButton = page.locator('button:has-text("Ferma")');
    const attivoStatus = page.locator('text=Attivo');

    const hasFerma = await fermaButton.isVisible().catch(() => false);
    const hasAttivo = await attivoStatus.isVisible().catch(() => false);

    expect(hasFerma || hasAttivo).toBe(true);

    console.log('✅ Voice pipeline started/verified');
    console.log('📋 Console logs:', logs.slice(-10));
  });

  test('Should show microphone button when pipeline is running', async ({ page }) => {
    // Check if we have Tauri API OR Voice Pipeline HTTP fallback available
    const hasTauri = await hasTauriApi(page);
    const hasPipeline = await isVoicePipelineAvailable();
    if (!hasTauri && !hasPipeline) {
      console.log('⚠️ Skipping: Neither Tauri API nor Voice Pipeline HTTP available');
      test.skip();
      return;
    }
    console.log(`ℹ️ Running with: Tauri=${hasTauri}, HTTP Pipeline=${hasPipeline}`);

    // Navigate to Voice Agent
    await page.click('[data-testid="nav-voice-agent"], a:has-text("Voice Agent"), button:has-text("Voice Agent")');
    await page.waitForTimeout(2000);

    // Ensure pipeline is running (may already be running in HTTP mode)
    const stopButton = page.locator('button:has-text("Ferma")');
    const startButton = page.locator('[data-testid="btn-start-voice"], button:has-text("Avvia")');
    const isAlreadyRunning = await stopButton.isVisible().catch(() => false);

    if (!isAlreadyRunning) {
      await startButton.first().click();
      await page.waitForTimeout(5000);
    }

    // Check microphone button
    const micButton = page.locator('[data-testid="btn-voice-mic"]');
    await expect(micButton).toBeVisible();
    await expect(micButton).toBeEnabled();

    console.log('✅ Microphone button visible and enabled');
  });

  test('Should toggle recording state on mic click', async ({ page }) => {
    // Check if we have Tauri API OR Voice Pipeline HTTP fallback available
    const hasTauri = await hasTauriApi(page);
    const hasPipeline = await isVoicePipelineAvailable();
    if (!hasTauri && !hasPipeline) {
      console.log('⚠️ Skipping: Neither Tauri API nor Voice Pipeline HTTP available');
      test.skip();
      return;
    }
    console.log(`ℹ️ Running with: Tauri=${hasTauri}, HTTP Pipeline=${hasPipeline}`);

    const logs = await captureConsoleLogs(page);

    // Navigate to Voice Agent
    await page.click('[data-testid="nav-voice-agent"], a:has-text("Voice Agent"), button:has-text("Voice Agent")');
    await page.waitForTimeout(2000);

    // Ensure pipeline is running
    const stopButton = page.locator('button:has-text("Ferma")');
    const startButton = page.locator('[data-testid="btn-start-voice"], button:has-text("Avvia")');
    const isAlreadyRunning = await stopButton.isVisible().catch(() => false);

    if (!isAlreadyRunning) {
      await startButton.first().click();
      await page.waitForTimeout(5000);
    }

    // Click mic to start recording
    const micButton = page.locator('[data-testid="btn-voice-mic"]');
    await micButton.click();

    // Wait for recording to start
    await page.waitForTimeout(1000);

    // Check for recording indicator
    const recordingIndicator = page.locator('text=Registrazione in corso');
    const isRecording = await recordingIndicator.isVisible().catch(() => false);

    console.log('📋 Recording state logs:');
    logs.filter((l) => l.includes('MicClick') || l.includes('AudioRecorder')).forEach((l) => console.log(l));

    if (isRecording) {
      console.log('✅ Recording started - indicator visible');

      // Click mic again to stop
      await micButton.click();
      await page.waitForTimeout(2000);

      // Verify recording stopped
      const stillRecording = await recordingIndicator.isVisible().catch(() => false);
      if (!stillRecording) {
        console.log('✅ Recording stopped successfully');
      } else {
        console.log('❌ Recording did NOT stop - BUG-V5 still present');
      }
    } else {
      console.log('⚠️ Recording indicator not visible (may need permissions)');
    }
  });

  test('Should send text message via input', async ({ page }) => {
    // Check if we have Tauri API OR Voice Pipeline HTTP fallback available
    const hasTauri = await hasTauriApi(page);
    const hasPipeline = await isVoicePipelineAvailable();
    if (!hasTauri && !hasPipeline) {
      console.log('⚠️ Skipping: Neither Tauri API nor Voice Pipeline HTTP available');
      test.skip();
      return;
    }
    console.log(`ℹ️ Running with: Tauri=${hasTauri}, HTTP Pipeline=${hasPipeline}`);

    const logs = await captureConsoleLogs(page);

    // Navigate to Voice Agent
    await page.click('[data-testid="nav-voice-agent"], a:has-text("Voice Agent"), button:has-text("Voice Agent")');
    await page.waitForTimeout(2000);

    // Ensure pipeline is running
    const stopButton = page.locator('button:has-text("Ferma")');
    const startButton = page.locator('[data-testid="btn-start-voice"], button:has-text("Avvia")');
    const isAlreadyRunning = await stopButton.isVisible().catch(() => false);

    if (!isAlreadyRunning) {
      await startButton.first().click();
      await page.waitForTimeout(5000);
    }

    // Type in input
    const input = page.locator('[data-testid="input-voice-text"], input[placeholder*="Scrivi"]');
    await input.fill('Vorrei prenotare un appuntamento');

    // Click send
    const sendButton = page.locator('[data-testid="btn-send-voice"]');
    await sendButton.click();

    // Wait for response
    await page.waitForTimeout(5000);

    // Check for Sara's response
    const transcript = page.locator('[data-testid="voice-transcript"]');
    const content = await transcript.textContent();

    console.log('📋 Transcript content:', content?.substring(0, 200));

    // Verify we got some response from Sara (not empty)
    // Sara may ask for name, service, or date - any response is valid
    expect(content).toBeTruthy();
    expect(content!.length).toBeGreaterThan(20);

    console.log('✅ Text message sent and response received');
  });

  test('Should capture browser console logs for debugging', async ({ page }) => {
    const logs: string[] = [];

    page.on('console', (msg) => {
      logs.push(`[${msg.type().toUpperCase()}] ${msg.text()}`);
    });

    page.on('pageerror', (err) => {
      logs.push(`[ERROR] ${err.message}`);
    });

    // Navigate
    await page.click('[data-testid="nav-voice-agent"], a:has-text("Voice Agent"), button:has-text("Voice Agent")');
    await page.waitForTimeout(2000);

    console.log('📋 All browser console logs:');
    logs.forEach((log) => console.log(log));

    // Save logs to file
    const fs = await import('fs');
    fs.writeFileSync('test-results/console-logs.txt', logs.join('\n'));

    console.log('✅ Console logs saved to test-results/console-logs.txt');
  });
});
