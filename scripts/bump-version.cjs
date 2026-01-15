#!/usr/bin/env node

/**
 * FLUXION Version Bump Script
 *
 * Synchronizes version across:
 * - package.json
 * - src-tauri/tauri.conf.json
 * - src-tauri/Cargo.toml
 *
 * Usage:
 *   node scripts/bump-version.js <version>
 *   node scripts/bump-version.js patch|minor|major
 *
 * Examples:
 *   node scripts/bump-version.js 1.2.3
 *   node scripts/bump-version.js patch     # 0.1.0 -> 0.1.1
 *   node scripts/bump-version.js minor     # 0.1.0 -> 0.2.0
 *   node scripts/bump-version.js major     # 0.1.0 -> 1.0.0
 */

const fs = require('fs');
const path = require('path');

const ROOT_DIR = path.resolve(__dirname, '..');

const FILES = {
  packageJson: path.join(ROOT_DIR, 'package.json'),
  tauriConf: path.join(ROOT_DIR, 'src-tauri', 'tauri.conf.json'),
  cargoToml: path.join(ROOT_DIR, 'src-tauri', 'Cargo.toml'),
};

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf-8'));
}

function writeJson(filePath, data) {
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2) + '\n');
}

function readToml(filePath) {
  return fs.readFileSync(filePath, 'utf-8');
}

function writeToml(filePath, content) {
  fs.writeFileSync(filePath, content);
}

function getCurrentVersion() {
  const pkg = readJson(FILES.packageJson);
  return pkg.version;
}

function parseVersion(version) {
  const match = version.match(/^(\d+)\.(\d+)\.(\d+)$/);
  if (!match) {
    throw new Error(`Invalid version format: ${version}. Expected X.Y.Z`);
  }
  return {
    major: parseInt(match[1], 10),
    minor: parseInt(match[2], 10),
    patch: parseInt(match[3], 10),
  };
}

function bumpVersion(current, type) {
  const v = parseVersion(current);

  switch (type) {
    case 'major':
      return `${v.major + 1}.0.0`;
    case 'minor':
      return `${v.major}.${v.minor + 1}.0`;
    case 'patch':
      return `${v.major}.${v.minor}.${v.patch + 1}`;
    default:
      // Assume it's a specific version
      parseVersion(type); // Validate format
      return type;
  }
}

function updatePackageJson(version) {
  const pkg = readJson(FILES.packageJson);
  pkg.version = version;
  writeJson(FILES.packageJson, pkg);
  console.log(`  ✓ package.json: ${version}`);
}

function updateTauriConf(version) {
  const conf = readJson(FILES.tauriConf);
  conf.version = version;
  writeJson(FILES.tauriConf, conf);
  console.log(`  ✓ tauri.conf.json: ${version}`);
}

function updateCargoToml(version) {
  let content = readToml(FILES.cargoToml);

  // Update version in [package] section
  // Match: version = "X.Y.Z" in the first occurrence
  const versionRegex = /^(version\s*=\s*")[^"]+(")/m;

  if (!versionRegex.test(content)) {
    throw new Error('Could not find version in Cargo.toml');
  }

  content = content.replace(versionRegex, `$1${version}$2`);
  writeToml(FILES.cargoToml, content);
  console.log(`  ✓ Cargo.toml: ${version}`);
}

function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log('FLUXION Version Manager');
    console.log('');
    console.log(`Current version: ${getCurrentVersion()}`);
    console.log('');
    console.log('Usage:');
    console.log('  node scripts/bump-version.js <version>');
    console.log('  node scripts/bump-version.js patch|minor|major');
    console.log('');
    console.log('Examples:');
    console.log('  node scripts/bump-version.js 1.0.0');
    console.log('  node scripts/bump-version.js patch');
    process.exit(0);
  }

  const input = args[0];
  const currentVersion = getCurrentVersion();
  const newVersion = bumpVersion(currentVersion, input);

  console.log(`Bumping version: ${currentVersion} -> ${newVersion}`);
  console.log('');

  try {
    updatePackageJson(newVersion);
    updateTauriConf(newVersion);
    updateCargoToml(newVersion);

    console.log('');
    console.log(`✅ Version updated to ${newVersion}`);
    console.log('');
    console.log('Next steps:');
    console.log('  1. git add -A');
    console.log(`  2. git commit -m "chore: bump version to ${newVersion}"`);
    console.log(`  3. git tag v${newVersion}`);
    console.log('  4. git push origin main --tags');
  } catch (error) {
    console.error(`❌ Error: ${error.message}`);
    process.exit(1);
  }
}

main();
