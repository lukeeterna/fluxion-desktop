---
title: "Network & Firewall"
type: entity
slug: network-firewall
sources_consumed:
  - raw/install/win10-fresh-compat.md
last_ingest: 2026-05-04
status: stable
related:
  - win10-installation
  - sara-voice-agent
  - gdpr-compliance
verticals: [all]
---

# Network & Firewall

> Configurazione rete necessaria per FLUXION. Porte locali loopback + FQDN outbound API. Setup `setup-win.bat` automatizza firewall rules su Win.

## TL;DR
- **Porte locali**: 3001 (HTTP bridge Tauri) + 3002 (Sara voice) — **loopback only** (127.0.0.1), no inbound
- **FQDN outbound**: Groq, Stripe, Resend, Sentry DE, GitHub Releases, FLUXION proxy CF Worker
- **Whitelist firewall corporate**: vedi tabella sez. "FQDN whitelist"
- Tool diagnostico: `tools/network-test.sh` (S184 α.4) — probe 9 endpoint, output JSON CI-friendly

## Porte locali (loopback)

| Porta | Servizio | Direzione | Note |
|-------|---------|-----------|------|
| **3001** | HTTP Bridge Tauri | inbound localhost | Frontend React → backend Rust IPC |
| **3002** | Sara Voice Pipeline | inbound localhost | Python FastAPI ([[sara-voice-agent]]) |

**Setup automatico Win**: `setup-win.bat` aggiunge regole firewall localhost-only. NO admin richiesto.
**Setup macOS**: `setup-mac.command` rimuove xattr quarantine. Firewall macOS gestito automaticamente.

## FQDN whitelist (corporate firewall / proxy)

| Endpoint | Categoria | Scopo | Bloccante? |
|----------|----------|-------|-----------|
| `fluxion-proxy.gianlucanewtech.workers.dev` | CRITICAL | LLM proxy zero-config (Groq/Cerebras routing) | SÌ — Sara non funziona |
| `api.github.com` | CRITICAL | Auto-update check + release assets | SÌ — no update |
| `github.com/lukeeterna/fluxion-desktop/releases` | CRITICAL | Download installer + asset | SÌ — no install/update |
| `o*.ingest.de.sentry.io` | IMPORTANT | Diagnostic error reporting (region DE GDPR-safe) | NO — solo telemetry |
| `api.stripe.com`, `js.stripe.com` | IMPORTANT | Checkout post-acquisto (browser-side) | SÌ — no acquisto |
| `fluxion-landing.pages.dev` | IMPORTANT | Landing page checkout | SÌ — no acquisto |
| `api.resend.com` | OPTIONAL | Email transazionali (license post-acquisto) | NO — fallback Gmail manuale |
| `*.tts.speech.microsoft.com` | OPTIONAL | Edge-TTS premium voice ([[sara-voice-agent]]) | NO — fallback Piper offline |
| `api.groq.com` | OPTIONAL | Direct Groq (se proxy CF down) | NO — fallback Cerebras / template |

> **Endpoint NON richiesti** (compliance positivo):
> - Nessun tracker (Google Analytics, Facebook Pixel, etc.)
> - Nessun cloud per dati cliente (SQLite locale, no transit PII)
> - Nessun backup automatico esterno (founder controlla)

## Esempi configurazione firewall

### Squid (proxy aziendale)
```
acl fluxion_endpoints dstdomain .workers.dev .pages.dev api.github.com github.com api.stripe.com js.stripe.com
http_access allow fluxion_endpoints
```

### FortiGate / pfSense / Sophos
Aggiungere FQDN tabella sopra a Web Filter Allow List, categoria "Business — productivity tool".

## Test diagnostico

```bash
# Tool ufficiale (cross-platform bash)
bash tools/network-test.sh           # human-readable IT colored
bash tools/network-test.sh --quiet   # silent (exit code only)
bash tools/network-test.sh --json    # CI-friendly JSON
```

**Exit code**:
- `0` — tutti CRITICAL OK
- `1` — almeno un CRITICAL FAIL
- `2` — solo IMPORTANT/OPTIONAL warn (CRITICAL OK)

**Tempo target**: ~10s per probe completa 9 endpoint.

## Errori comuni

| Sintomo | Causa | Fix |
|---------|-------|-----|
| "Sara offline" all'avvio | Porta 3002 bloccata da AV / port in use | `lsof -i :3002` per processo conflitto. Whitelist FLUXION in AV. |
| "Update check failed" | `api.github.com` bloccato firewall corporate | Whitelist FQDN. Manual update: download MSI da link email. |
| "Pipeline not responding" 3001 | HTTP bridge Tauri non avviato | Restart app. Verifica processo `fluxion.exe` in Task Manager. |
| Groq API 503 sporadico | Throttle Groq free tier | Auto-fallback Cerebras → template NLU. NO action utente. |
| Sentry "non raggiungibile" | Region DE bloccata firewall | Sentry è OPTIONAL (telemetry). FLUXION funziona senza. |
| Edge-TTS lenta / fallita | `*.tts.speech.microsoft.com` bloccato | Auto-fallback Piper offline (~50ms latency). Voice quality 7/10 vs 9/10. |
| Corporate proxy + auth richiesta | Proxy NTLM/Kerberos non supportato | TODO gap docs. Workaround: bypass proxy per FQDN whitelist. |

## Privacy & data residency

- **Dati cliente**: SQLite locale crittografato AES-256-GCM. **Mai in transit**.
- **License key**: Ed25519 offline-verifiable. Nessuna phone-home.
- **Sara voice**: audio buffer locale, transcript via STT locale (Whisper.cpp) o Groq (US). LLM via FLUXION proxy CF Worker (stateless edge, no PII storage).
- **Sentry telemetry**: region DE (GDPR-safe), no PII, solo error stack + system metrics.

Vedi [[gdpr-compliance]] per dettagli.

## Cross-references
- [[win10-installation]] — `setup-win.bat` configura firewall localhost
- [[sara-voice-agent]] — pipeline 3002 dettagli
- [[gdpr-compliance]] — privacy posture FLUXION

## Sources
- `tools/network-test.sh` — tool diagnostico autoritativo
- `scripts/install/docs/NETWORK-REQUIREMENTS.md` — doc IT manager whitelist (S184 α.4)
- `scripts/install/setup-win.bat` — firewall rules localhost
- [raw/install/win10-fresh-compat.md](../../raw/install/win10-fresh-compat.md) — setup-win.bat reference
