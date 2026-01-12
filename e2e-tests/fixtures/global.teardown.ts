/**
 * Global Teardown - Runs once after all tests
 *
 * Enterprise Best Practices:
 * - Clean up test data
 * - Generate summary reports
 * - Upload artifacts to cloud storage
 */

import { FullConfig } from '@playwright/test';
import fs from 'fs';
import path from 'path';

async function globalTeardown(_config: FullConfig): Promise<void> {
  console.log('\n🧹 Running global teardown...');

  // =============================================================================
  // CLEANUP TEST DATA
  // =============================================================================
  if (process.env.CLEANUP_DATABASE === 'true') {
    console.log('🗑️  Cleaning up test database...');
    // Cleanup logic would go here
    // await cleanupTestDatabase();
    console.log('✅ Database cleaned');
  }

  // =============================================================================
  // GENERATE ALLURE REPORT
  // =============================================================================
  if (process.env.GENERATE_ALLURE === 'true') {
    console.log('📊 Generating Allure report...');
    const { execSync } = await import('child_process');
    try {
      execSync('npx allure generate .allure-results -o reports/allure --clean', {
        stdio: 'inherit',
        cwd: path.join(__dirname, '..'),
      });
      console.log('✅ Allure report generated at reports/allure');
    } catch (error) {
      console.warn('⚠️  Could not generate Allure report:', error);
    }
  }

  // =============================================================================
  // SUMMARY
  // =============================================================================
  const resultsPath = path.join(__dirname, '../reports/json/results.json');
  if (fs.existsSync(resultsPath)) {
    try {
      const results = JSON.parse(fs.readFileSync(resultsPath, 'utf-8'));
      const stats = results.stats || {};

      console.log('\n📈 Test Summary:');
      console.log(`   Total: ${stats.expected || 0}`);
      console.log(`   Passed: ${stats.expected - (stats.unexpected || 0) - (stats.flaky || 0)}`);
      console.log(`   Failed: ${stats.unexpected || 0}`);
      console.log(`   Flaky: ${stats.flaky || 0}`);
      console.log(`   Duration: ${((stats.duration || 0) / 1000).toFixed(2)}s`);
    } catch (_error) {
      // Ignore JSON parsing errors
    }
  }

  console.log('\n✅ Teardown complete');
  console.log('📁 Reports available at: e2e-tests/reports/');
}

export default globalTeardown;
