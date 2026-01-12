/**
 * Test Fixtures - Shared test context and utilities
 *
 * Enterprise Best Practices:
 * - Provide isolated test context
 * - Pre-configured page objects
 * - Test data factories
 */

import { test as base, expect } from '@playwright/test';
import { DashboardPage } from '../pages/DashboardPage';
import { ClientiPage, ClienteData } from '../pages/ClientiPage';

// =============================================================================
// FIXTURE TYPES
// =============================================================================

type TestFixtures = {
  dashboardPage: DashboardPage;
  clientiPage: ClientiPage;
  testCliente: ClienteData;
  uniqueId: string;
};

// =============================================================================
// EXTENDED TEST WITH FIXTURES
// =============================================================================

export const test = base.extend<TestFixtures>({
  // Dashboard Page Object
  dashboardPage: async ({ page }, use) => {
    const dashboardPage = new DashboardPage(page);
    await use(dashboardPage);
  },

  // Clienti Page Object
  clientiPage: async ({ page }, use) => {
    const clientiPage = new ClientiPage(page);
    await use(clientiPage);
  },

  // Generate unique test data for each test
  // eslint-disable-next-line no-empty-pattern
  testCliente: async ({}, use) => {
    const timestamp = Date.now();
    const testCliente: ClienteData = {
      nome: `Test${timestamp}`,
      cognome: `Cliente${timestamp}`,
      telefono: `333${timestamp.toString().slice(-7)}`,
      email: `test${timestamp}@example.com`,
      dataNascita: '1990-01-15',
      note: 'Cliente di test automatico',
    };
    await use(testCliente);
  },

  // Unique ID for test isolation
  // eslint-disable-next-line no-empty-pattern
  uniqueId: async ({}, use) => {
    const id = `test_${Date.now()}_${Math.random().toString(36).substring(7)}`;
    await use(id);
  },
});

// =============================================================================
// CUSTOM ASSERTIONS
// =============================================================================

export { expect };

// =============================================================================
// TEST DATA FACTORIES
// =============================================================================

export const TestDataFactory = {
  /**
   * Generate a random Italian phone number
   */
  phoneNumber(): string {
    const prefixes = ['333', '339', '347', '348', '349', '320', '328'];
    const prefix = prefixes[Math.floor(Math.random() * prefixes.length)];
    const number = Math.floor(Math.random() * 9000000) + 1000000;
    return `${prefix}${number}`;
  },

  /**
   * Generate a random Italian name
   */
  italianName(): { nome: string; cognome: string } {
    const nomi = ['Marco', 'Luca', 'Andrea', 'Francesco', 'Alessandro', 'Giulia', 'Sara', 'Chiara', 'Francesca', 'Elena'];
    const cognomi = ['Rossi', 'Russo', 'Ferrari', 'Esposito', 'Bianchi', 'Romano', 'Colombo', 'Ricci', 'Marino', 'Greco'];

    return {
      nome: nomi[Math.floor(Math.random() * nomi.length)],
      cognome: cognomi[Math.floor(Math.random() * cognomi.length)],
    };
  },

  /**
   * Generate a random email
   */
  email(name?: string): string {
    const domains = ['gmail.com', 'outlook.it', 'libero.it', 'yahoo.it'];
    const domain = domains[Math.floor(Math.random() * domains.length)];
    const baseName = name || `user${Date.now()}`;
    return `${baseName.toLowerCase().replace(/\s/g, '.')}@${domain}`;
  },

  /**
   * Generate a random date of birth (adult)
   */
  birthDate(): string {
    const year = 1960 + Math.floor(Math.random() * 40); // 1960-2000
    const month = String(Math.floor(Math.random() * 12) + 1).padStart(2, '0');
    const day = String(Math.floor(Math.random() * 28) + 1).padStart(2, '0');
    return `${year}-${month}-${day}`;
  },

  /**
   * Generate complete random cliente
   */
  cliente(): ClienteData {
    const { nome, cognome } = this.italianName();
    return {
      nome,
      cognome,
      telefono: this.phoneNumber(),
      email: this.email(`${nome}.${cognome}`),
      dataNascita: this.birthDate(),
      note: 'Generato automaticamente per test',
    };
  },

  /**
   * Generate multiple clienti
   */
  clienti(count: number): ClienteData[] {
    return Array.from({ length: count }, () => this.cliente());
  },
};

// =============================================================================
// TEST UTILITIES
// =============================================================================

export const TestUtils = {
  /**
   * Wait for specified milliseconds
   */
  async sleep(ms: number): Promise<void> {
    await new Promise((resolve) => setTimeout(resolve, ms));
  },

  /**
   * Retry a function with exponential backoff
   */
  async retry<T>(
    fn: () => Promise<T>,
    options: { maxRetries?: number; delay?: number } = {}
  ): Promise<T> {
    const { maxRetries = 3, delay = 1000 } = options;

    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await fn();
      } catch (error) {
        if (attempt === maxRetries) throw error;
        await this.sleep(delay * attempt);
      }
    }

    throw new Error('Max retries exceeded');
  },

  /**
   * Generate ISO date string for today
   */
  today(): string {
    return new Date().toISOString().split('T')[0];
  },

  /**
   * Generate ISO date string for N days from now
   */
  daysFromNow(days: number): string {
    const date = new Date();
    date.setDate(date.getDate() + days);
    return date.toISOString().split('T')[0];
  },
};
