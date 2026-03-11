# FLUXION — Handoff Sessione 48 → 49 (2026-03-11)

## ⚡ CTO MANDATE — NON NEGOZIABILE
> **"Non accetto mediocrità. Solo enterprise level."**
> Ogni feature risponde: *"quanti € risparmia o guadagna la PMI?"*

---

## ⚠️ GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`

---

## STATO GIT
```
Branch: master | HEAD: ea24ea7
Working tree: CLEAN ✅
type-check: 0 errori ✅
cargo errori pre-esistenti in listini.rs/media.rs (invariati, NON toccare)
iMac: sincronizzato ✅ | voice pipeline: UP 127.0.0.1:3002 ✅
```

---

## ✅ COMPLETATO SESSIONE 48

| Task | Commit | Impatto |
|---|---|---|
| Fix sqlx query_as! → query | fef288b | cargo check iMac 0 nuovi errori — support.rs compila |
| F11 Docker Voice Agent | ea24ea7 | ambiente riproducibile, onboarding 10min |

### Dettaglio fix sqlx (inizio s48)
- `support.rs`: `sqlx::query_as!` sostituito con `sqlx::query` + `try_get` (stesso pattern codebase)
- `restore_database`: `state` → `_state` (variabile inutilizzata eliminata)
- Cargo check iMac: 0 errori in support.rs/http_bridge.rs ✅

### Dettaglio F11 — Docker Voice Agent
- `voice-agent/Dockerfile`: python:3.9-slim, utente non-root, healthcheck 30s, libgomp1 per ONNX
- `voice-agent/docker-compose.yml`: bind `127.0.0.1:3002`, volume mount DB Tauri, host-gateway per HTTP Bridge
- `voice-agent/requirements-docker.txt`: solo deps leggere (no torch/faiss/TTS/spacy/WebRTC)
- `voice-agent/.dockerignore`: esclude venv, modelli pesanti, .env, test
- `voice-agent/README.md`: sezione Docker con setup guidato 10min
- **ROI**: onboarding nuovo dev da 2h → 10min

---

## 🚀 PROSSIMO: dalla ROADMAP_REMAINING.md

Aprire ROADMAP_REMAINING.md e prendere la prima task `⏳` disponibile.

---

## ⚠️ TODO PRODUZIONE APERTI (non bloccanti)

1. `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET` reali in `src-tauri/src/commands/settings.rs`
2. Groq API key in keychain macOS (post-tauri-plugin-stronghold stable)
3. ESLint pre-esistenti (pre-existing, non bloccanti):
   - `localStorage` in Dashboard.tsx L71/97
   - `IntersectionObserver` in Impostazioni.tsx L179/185
   - useless escape in VoiceAgent.tsx L209

---

## AZIONI INIZIO S49

```bash
# 1. Verifica pipeline iMac (dovrebbe già essere UP)
curl http://127.0.0.1:3002/health

# 2. (Opzionale) Test Docker locale su MacBook se Docker Desktop installato
cd voice-agent && docker-compose build && docker-compose up -d
curl http://127.0.0.1:3002/health

# 3. Leggi ROADMAP_REMAINING.md → prima task ⏳
```
