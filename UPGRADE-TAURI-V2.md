# Upgrade Tauri 1.x → 2.x - Documentazione

## Data Upgrade
2026-02-19 14:16:36

## Files Backup
- Location: backup-tauri-v1-20260219_141610/
- Checksum: backup-tauri-v1-20260219_141610/checksums.md5

## Modifiche Principali

### 1. Struttura Configurazione

#### VECCHIO (v1)
```json
{
  "build": {
    "devPath": "http://localhost:5173",
    "distDir": "../dist"
  },
  "tauri": {
    "allowlist": { ... }
  }
}
```

#### NUOVO (v2)
```json
{
  "build": {
    "devUrl": "http://localhost:5173",
    "frontendDist": "../dist"
  },
  "app": {
    "windows": [ ... ],
    "security": { ... }
  },
  "bundle": { ... },
  "capabilities": [ ... ]
}
```

### 2. Cambiamenti Chiave

| Componente | V1 | V2 |
|------------|----|----|
| Root key | tauri | app |
| Dev path | devPath | devUrl |
| Dist dir | distDir | frontendDist |
| Permessi | allowlist | capabilities |
| Window config | tauri.windows | app.windows |
| Security | - | app.security (obbligatorio) |

### 3. Capabilities (Nuovo sistema permessi)

In v2 i permessi si definiscono in  come file JSON separati,
on inline in tauri.conf.json.

Permessi migrati:
- shell:all → shell:allow-execute, shell:allow-open
- http:all → http:default

## Comandi per Ripristino
```bash
cd /Volumes/MacSSD\ -\ Dati/fluxion
cp backup-tauri-v1-*/tauri.conf.json src-tauri/
cargo clean
npm run tauri build
```

## Note Tecniche
- Tauri 2.0 richiede capabilities esplicite
- Il campo allowlist è deprecato
- Security CSP deve essere definito
