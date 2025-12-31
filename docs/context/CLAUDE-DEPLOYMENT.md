# 🚀 FLUXION Deployment - Build & Release

> Build cross-platform, auto-update, sistema licenze.

---

## Build Commands

```bash
# Development
npm run tauri dev

# Production (piattaforma corrente)
npm run tauri build

# Output
# Windows: .msi, .exe
# macOS: .dmg, .app
# Linux: .deb, .AppImage
```

---

## Sistema Licenze (Keygen.sh)

### Credenziali

```bash
KEYGEN_ACCOUNT_ID=b845d2ed-92a4-4048-b2d8-ee625206a5ae
```

### Validazione

```typescript
async function validateLicense(key: string, fingerprint: string) {
    const response = await fetch(
        `https://api.keygen.sh/v1/accounts/${ACCOUNT}/licenses/actions/validate-key`,
        {
            method: 'POST',
            body: JSON.stringify({ meta: { key, scope: { fingerprint } } })
        }
    );
    return response.json();
}
```

---

## Auto-Update

```json
// tauri.conf.json
{
    "plugins": {
        "updater": {
            "active": true,
            "endpoints": ["https://releases.fluxion.it/{{target}}/{{current_version}}"]
        }
    }
}
```

---

## Versioning

```bash
npm version patch  # 1.0.0 → 1.0.1
npm version minor  # 1.0.0 → 1.1.0  
npm version major  # 1.0.0 → 2.0.0
git push --tags    # Triggera release
```

---

*Ultimo aggiornamento: 2025-12-28*
