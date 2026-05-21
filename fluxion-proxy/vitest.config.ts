import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: false,
    environment: 'node',
    include: ['tests/**/*.test.ts'],
    testTimeout: 10000,
    coverage: {
      provider: 'v8',
      include: ['src/routes/**/*.ts'],
      exclude: ['src/routes/admin-*.ts', 'src/routes/diagnostic-report.ts', 'src/routes/gdpr-download.ts', 'src/routes/lead-magnet.ts', 'src/routes/nlu-proxy.ts', 'src/routes/consent-log.ts', 'src/routes/health-monitor.ts'],
    },
  },
});
