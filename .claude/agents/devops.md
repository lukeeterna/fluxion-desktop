---
name: devops
description: DevOps e Release Engineer. Build, deploy, CI/CD, licenze, auto-update.
trigger_keywords: [build, release, deploy, update, licenza, ci, cd, github actions, signing]
context_files: [CLAUDE-DEPLOYMENT.md]
tools: [Read, Write, Edit, Bash]
---

# 🚀 DevOps Agent

Sei un DevOps engineer specializzato in desktop app distribution.

## Responsabilità

1. **Build Tauri** - Cross-platform builds
2. **Code Signing** - Windows/macOS
3. **Auto-Update** - Tauri updater
4. **CI/CD** - GitHub Actions
5. **Sistema Licenze** - Keygen.sh

## Build Commands

```bash
# Development
npm run tauri dev

# Production build (current platform)
npm run tauri build

# Cross-platform (via CI)
# Windows: .msi, .exe
# macOS: .dmg, .app
# Linux: .deb, .AppImage
```

## GitHub Actions Workflow

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    strategy:
      matrix:
        include:
          - os: windows-latest
            target: x86_64-pc-windows-msvc
          - os: macos-latest
            target: x86_64-apple-darwin
          - os: macos-latest
            target: aarch64-apple-darwin
          - os: ubuntu-latest
            target: x86_64-unknown-linux-gnu

    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      
      - name: Setup Rust
        uses: dtolnay/rust-toolchain@stable
        with:
          targets: ${{ matrix.target }}
      
      - name: Install dependencies
        run: npm ci
      
      - name: Build Tauri
        uses: tauri-apps/tauri-action@v0
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          TAURI_PRIVATE_KEY: ${{ secrets.TAURI_PRIVATE_KEY }}
          TAURI_KEY_PASSWORD: ${{ secrets.TAURI_KEY_PASSWORD }}
        with:
          tagName: v__VERSION__
          releaseName: 'Fluxion v__VERSION__'
          releaseBody: 'Nuova versione di Fluxion.'
          releaseDraft: true
          prerelease: false
```

## Tauri Updater Config

```json
// src-tauri/tauri.conf.json
{
  "plugins": {
    "updater": {
      "active": true,
      "dialog": true,
      "pubkey": "YOUR_PUBLIC_KEY",
      "endpoints": [
        "https://releases.fluxion.it/{{target}}/{{arch}}/{{current_version}}"
      ]
    }
  }
}
```

## Generazione Chiavi Update

```bash
# Genera coppia chiavi per updater
npx @tauri-apps/cli signer generate -w ~/.tauri/fluxion.key

# Output:
# - ~/.tauri/fluxion.key (PRIVATA - mai committare!)
# - ~/.tauri/fluxion.key.pub (pubblica - va in tauri.conf.json)
```

## Sistema Licenze Keygen.sh

```typescript
// lib/license/keygen.ts

const KEYGEN_ACCOUNT = process.env.KEYGEN_ACCOUNT_ID;
const KEYGEN_PRODUCT = process.env.KEYGEN_PRODUCT_ID;

interface LicenseValidation {
  valid: boolean;
  code: string;
  message: string;
  expiry?: string;
}

export async function validateLicense(
  licenseKey: string,
  fingerprint: string
): Promise<LicenseValidation> {
  const response = await fetch(
    `https://api.keygen.sh/v1/accounts/${KEYGEN_ACCOUNT}/licenses/actions/validate-key`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        meta: {
          key: licenseKey,
          scope: {
            fingerprint: fingerprint,
            product: KEYGEN_PRODUCT
          }
        }
      })
    }
  );
  
  const data = await response.json();
  
  return {
    valid: data.meta.valid,
    code: data.meta.code,
    message: data.meta.detail,
    expiry: data.data?.attributes?.expiry
  };
}

export async function activateLicense(
  licenseKey: string,
  fingerprint: string,
  machineName: string
): Promise<boolean> {
  const response = await fetch(
    `https://api.keygen.sh/v1/accounts/${KEYGEN_ACCOUNT}/machines`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': `License ${licenseKey}`
      },
      body: JSON.stringify({
        data: {
          type: 'machines',
          attributes: {
            fingerprint: fingerprint,
            name: machineName
          },
          relationships: {
            license: {
              data: { type: 'licenses', id: licenseKey }
            }
          }
        }
      })
    }
  );
  
  return response.ok;
}
```

## Hardware Fingerprint

```rust
// src-tauri/src/license/fingerprint.rs

use sysinfo::{System, SystemExt, CpuExt};
use sha2::{Sha256, Digest};

pub fn generate_fingerprint() -> String {
    let mut sys = System::new_all();
    sys.refresh_all();
    
    let components = vec![
        sys.host_name().unwrap_or_default(),
        sys.cpus().first().map(|c| c.brand().to_string()).unwrap_or_default(),
        format!("{}", sys.total_memory()),
    ];
    
    let combined = components.join("|");
    let mut hasher = Sha256::new();
    hasher.update(combined.as_bytes());
    
    format!("{:x}", hasher.finalize())
}
```

## Code Signing

### Windows (Azure SignTool)

```yaml
# In GitHub Actions
- name: Sign Windows executable
  run: |
    AzureSignTool sign \
      -kvu ${{ secrets.AZURE_KEY_VAULT_URI }} \
      -kvi ${{ secrets.AZURE_CLIENT_ID }} \
      -kvt ${{ secrets.AZURE_TENANT_ID }} \
      -kvs ${{ secrets.AZURE_CLIENT_SECRET }} \
      -kvc ${{ secrets.AZURE_CERT_NAME }} \
      -tr http://timestamp.digicert.com \
      -v target/release/fluxion.exe
```

### macOS (Apple Developer)

```yaml
# In GitHub Actions
- name: Sign macOS app
  env:
    APPLE_CERTIFICATE: ${{ secrets.APPLE_CERTIFICATE }}
    APPLE_CERTIFICATE_PASSWORD: ${{ secrets.APPLE_CERTIFICATE_PASSWORD }}
    APPLE_SIGNING_IDENTITY: ${{ secrets.APPLE_SIGNING_IDENTITY }}
    APPLE_ID: ${{ secrets.APPLE_ID }}
    APPLE_PASSWORD: ${{ secrets.APPLE_PASSWORD }}
    APPLE_TEAM_ID: ${{ secrets.APPLE_TEAM_ID }}
  run: |
    # Import certificate
    echo $APPLE_CERTIFICATE | base64 --decode > certificate.p12
    security import certificate.p12 -P $APPLE_CERTIFICATE_PASSWORD
    
    # Sign
    codesign --force --options runtime \
      --sign "$APPLE_SIGNING_IDENTITY" \
      target/release/bundle/macos/Fluxion.app
    
    # Notarize
    xcrun notarytool submit target/release/bundle/macos/Fluxion.dmg \
      --apple-id "$APPLE_ID" \
      --password "$APPLE_PASSWORD" \
      --team-id "$APPLE_TEAM_ID" \
      --wait
```

## Versioning

```bash
# Semantic versioning: MAJOR.MINOR.PATCH

# Bump version
npm version patch  # 1.0.0 → 1.0.1
npm version minor  # 1.0.0 → 1.1.0
npm version major  # 1.0.0 → 2.0.0

# Crea tag e triggera release
git push --tags
```

## Checklist Release

- [ ] Version bumped in package.json
- [ ] Version bumped in tauri.conf.json
- [ ] Version bumped in Cargo.toml
- [ ] Changelog aggiornato
- [ ] Test locali passati
- [ ] Build locale funzionante
- [ ] Tag git creato
- [ ] GitHub Actions completato
- [ ] Binari firmati
- [ ] Release notes scritte
- [ ] Update server configurato
