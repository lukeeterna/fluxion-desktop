# Architettura Distribuzione FLUXION — Decisioni Definitive (S84)

## TTS 3-Tier
| Tier | Engine | Qualita | Latenza |
|------|--------|---------|---------|
| QUALITY | Edge-TTS IsabellaNeural | 9/10 | ~500ms |
| FAST/OFFLINE | Piper it_IT-paola-medium | 7/10 | ~50ms |
| LAST RESORT | SystemTTS (say/SAPI5) | 5/10 | ~400ms |

Auto-selection: Internet? Edge-TTS + Piper fallback. No internet? Piper + SystemTTS.

## LLM/NLU — Zero-Config
```
App → FLUXION Proxy (CF Workers) → Groq/Cerebras
Auth: Ed25519 license key | Rate: 200 NLU/giorno | Costo: €0
Fallback: Groq → Cerebras → Template NLU locale (offline)
```
Cliente NON crea account, NON gestisce API key, NON sa cosa e' un LLM.

## Pagamento — Stripe + Ed25519
```
Landing → Stripe Checkout → webhook CF Worker → Ed25519 license → email Resend → download
```
- Base €497: gestionale + WA + Sara 30gg trial
- Pro €897: 1 nicchia + Sara per sempre
- NON esiste download gratuito
- MAI blocco totale — solo Sara si blocca

## Compatibilita Minima
- Windows 10+ / macOS 12+ | 8GB RAM con Sara | 2GB disco
- Calendario/clienti/cassa funzionano OFFLINE

## Code Signing — ZERO COSTI
- macOS: ad-hoc signing + pagina istruzioni Gatekeeper
- Windows: MSI unsigned + pagina SmartScreen

## Python Voice Agent
- PyInstaller → binario nativo (sidecar Tauri)
- Utente NON installa Python
- Bundle ~520MB

## Self-Healing
- Health check ogni 30s su /health
- 3 fail → kill + restart + notifica

## Research Files
- `.claude/cache/agents/tts-crossplatform-install-research.md`
- `.claude/cache/agents/llm-api-onboarding-research.md`
- `.claude/cache/agents/install-compatibility-research.md`
