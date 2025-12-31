// ═══════════════════════════════════════════════════════════════════
// FLUXION E2E - Test Helpers
// Utility functions for E2E tests
// ═══════════════════════════════════════════════════════════════════

/**
 * Generate unique test data with timestamp
 */
export function generateUniqueData(prefix: string): string {
  const timestamp = Date.now();
  return `${prefix}_${timestamp}`;
}

/**
 * Generate random email
 */
export function generateEmail(name: string): string {
  const timestamp = Date.now();
  return `${name.toLowerCase()}_${timestamp}@test.fluxion.local`;
}

/**
 * Generate random phone number (Italian format)
 */
export function generatePhone(): string {
  const random = Math.floor(Math.random() * 900000000) + 100000000;
  return `+39 ${random}`;
}

/**
 * Wait for a condition with custom retry logic
 */
export async function waitForCondition(
  condition: () => Promise<boolean>,
  options: { timeout?: number; interval?: number; errorMessage?: string } = {}
): Promise<void> {
  const timeout = options.timeout || 10000;
  const interval = options.interval || 500;
  const startTime = Date.now();

  while (Date.now() - startTime < timeout) {
    if (await condition()) {
      return;
    }
    await browser.pause(interval);
  }

  throw new Error(options.errorMessage || 'Condition not met within timeout');
}

/**
 * Retry an action multiple times on failure
 */
export async function retryAction<T>(
  action: () => Promise<T>,
  retries = 3,
  delayMs = 1000
): Promise<T> {
  for (let i = 0; i < retries; i++) {
    try {
      return await action();
    } catch (error) {
      if (i === retries - 1) {
        throw error;
      }
      console.log(`Retry ${i + 1}/${retries} after error:`, error);
      await browser.pause(delayMs);
    }
  }
  throw new Error('Retry action failed');
}

/**
 * Take screenshot with custom name
 */
export async function takeScreenshot(name: string): Promise<void> {
  const timestamp = new Date().toISOString().replace(/:/g, '-');
  const filename = `${name}-${timestamp}.png`;
  await browser.saveScreenshot(`./e2e/data/screenshots/${filename}`);
  console.log(`📸 Screenshot saved: ${filename}`);
}

/**
 * Format date for datetime-local input (YYYY-MM-DDTHH:mm)
 */
export function formatDateTimeLocal(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');

  return `${year}-${month}-${day}T${hours}:${minutes}`;
}

/**
 * Get date for N days from now
 */
export function getDateInFuture(daysFromNow: number): Date {
  const date = new Date();
  date.setDate(date.getDate() + daysFromNow);
  return date;
}

/**
 * Generate appointment datetime (next available slot)
 */
export function generateAppointmentDateTime(daysFromNow = 1, hour = 10): string {
  const date = getDateInFuture(daysFromNow);
  date.setHours(hour, 0, 0, 0);
  return formatDateTimeLocal(date);
}

/**
 * Clean test database (if needed)
 * NOTE: This should be implemented based on your backend API
 */
export async function cleanTestData(): Promise<void> {
  // TODO: Implement database cleanup
  // This could call a Tauri command or use direct SQL
  console.log('⚠️  cleanTestData not implemented yet');
}

/**
 * Seed test data
 */
export async function seedTestData(): Promise<void> {
  // TODO: Implement test data seeding
  console.log('⚠️  seedTestData not implemented yet');
}

/**
 * Assert no console errors in app
 */
export async function assertNoConsoleErrors(): Promise<void> {
  const logs = await browser.getLogs('browser');
  const errors = logs.filter((log) => log.level === 'SEVERE');

  if (errors.length > 0) {
    console.error('Console errors found:', errors);
    throw new Error(`Found ${errors.length} console errors`);
  }
}

/**
 * Wait for page to be fully loaded (no spinners)
 */
export async function waitForPageLoad(timeout = 10000): Promise<void> {
  // Wait for common loading indicators to disappear
  const loadingSelector = '[data-testid="loading"], [data-testid="spinner"]';

  try {
    const loadingElement = await $(loadingSelector);
    await loadingElement.waitForDisplayed({ reverse: true, timeout });
  } catch {
    // Element not found or already disappeared, which is fine
  }

  await browser.pause(500); // Small buffer for UI to settle
}

/**
 * Get current route/page name
 */
export async function getCurrentRoute(): Promise<string> {
  const url = await browser.getUrl();
  return url;
}

/**
 * Random number in range
 */
export function randomInt(min: number, max: number): number {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

/**
 * Random item from array
 */
export function randomItem<T>(array: T[]): T {
  return array[Math.floor(Math.random() * array.length)];
}
