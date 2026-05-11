# FLUXION — Handoff Sessione 197 (PRE-LAUNCH-AUDIT + cleanup) (2026-05-11)

## SESSIONE 197 — ✅ CHIUSA Claude-side priorities (P1+P2). Founder action P3+P4 pending.

**Esito**: PRIORITY 1 (PRE-LAUNCH-AUDIT.md aggregato Gate 3) e PRIORITY 2 (cleanup orphan setup-piper) completate Claude-side. Commit `65dfc97`. PRIORITY 3 (deploy CF F-3+F-4) e PRIORITY 4 (ROTATE 2 CF tokens) restano founder action ~15 min totali.

### Lavoro completato S197

1. ✅ **NEW `docs/launch/PRE-LAUNCH-AUDIT.md`** (242 righe, 6 categorie CTO checklist S181):
   - **1. Build/Distribution** ⚠️ PARTIAL — macOS PKG ✅, sidecar 208MB ✅, **Win MSI ❌ P0 BLOCKER** (~80% mercato IT desktop), Universal Binary arm64 + Linux deferred milestone.
   - **2. Functional E2E** ⚠️ PARTIAL — calendario/clienti/cassa offline ✅, **test live audio Sara ❌ P0**, Stripe test mode ⚠️ TBD, 5 scenari Sara live ❌.
   - **3. Security** ✅ PASS post-rotate — git history pulita S192 ✅, settings.local.json pulito ✅, Ed25519 ✅, **2 CF token ROTATE ❌ P0 founder ~3 min**.
   - **4. Performance** ✅ PASS PRO Gate 3 COMPLETO:
     - D-1 SQLite 8/8 query PASS (Q1-list P95 24.5ms vs SLO 50ms)
     - D-2 IPC `get_clienti` P95 36.9ms vs SLO 100ms (margine -63%)
     - D-3 Voice TTS Piper sidecar P95 **404ms** vs SLO 800ms (**margine -49.5%**)
   - **5. Compliance** ⚠️ PARTIAL — privacy policy + ToS ❌ P0 GDPR, fatturazione XML FatturaPA non implementata (TBD post-prima vendita), disclaimer voice agent ❌ P0.
   - **6. Customer Success** ⚠️ PARTIAL — F-3 email sequence ✅ CODE COMPLETE, F-4 health monitor ✅ CODE COMPLETE, **deploy CF + Discord secret ❌ P0 founder ~10 min**, FAQ pubblica TBD P1.
   - Tempo stimato Gate 3 GREEN end-to-end pre-launch: **~2h** (~15 min founder hands-on, resto Claude-side post-sblocco).

2. ✅ **Cleanup orphan `scripts/setup-piper.js`**:
   - Rimosso file (path mismatch confermato S193+S195+S196 in `docs/perf/D3-voice-latency.md`)
   - Rimossa entry `package.json:41` `"setup:piper": "node scripts/setup-piper.js"`
   - Verificato: nessun riferimento attivo, solo storici in docs/perf + HANDOFF previous.

### Files modificati S197

- A `docs/launch/PRE-LAUNCH-AUDIT.md` (NEW 242 righe)
- M `package.json` (-1 riga setup:piper script)
- D `scripts/setup-piper.js` (-220 righe orphan)
- Commit: `65dfc97 docs(S197): PRE-LAUNCH-AUDIT.md + cleanup setup-piper orphan`
- Pre-commit hook: 17 ESLint warning pre-esistenti, 0 error → ✅ PASSED.

### Stato Gate 3 — ✅ COMPLETO BLINDATO (invariato S196)

- F-1 ✅ | F-2 ✅ | F-3 ✅ CODE COMPLETE | F-4 ✅ CODE COMPLETE
- D-1 ✅ | D-2 ✅ (P95 36.9ms) | D-3 ✅ PASS PRO (P95 404ms vs SLO 800ms)
- **Pre-launch readiness aggregato**: vedi `docs/launch/PRE-LAUNCH-AUDIT.md`.

### Founder action P0 (~15 min totali) — S198 prerequisite

1. **CF token ROTATE** (~3 min) — procedura HANDOFF S192 PRIORITY 1:
   - Dashboard CF → API Tokens → Trova 2 token leakati S189-B → "Roll" → Confirm.
   - Nuovo token aggiornare in `.env` MacBook e/o iMac (storage gitignored).

2. **Deploy CF F-3+F-4** (~10 min):
   ```bash
   cd fluxion-proxy
   npx wrangler secret put DISCORD_HEALTH_WEBHOOK_URL
   # incolla URL da chat history S189-A (Discord channel personale founder)
   npx wrangler deploy
   ```
   Post-deploy Claude S198 esegue E2E:
   - Email sequence preview 5 templates (`/admin/email-sequence/preview`)
   - Health monitor manual trigger (`curl /admin/health/run-now`)
   - Verifica Gmail inbox 5 email arrivate
   - Verifica Discord webhook embed health status

### Prompt ripartenza S198

```
S197 ✅ CHIUSA Claude-side (PRE-LAUNCH-AUDIT.md + cleanup setup-piper, commit 65dfc97).

PRE-REQUISITE FOUNDER (~15 min) prima di iniziare S198:
1. ROTATE 2 CF API tokens dashboard CF (S192 procedura).
2. cd fluxion-proxy && npx wrangler secret put DISCORD_HEALTH_WEBHOOK_URL (URL chat S189-A)
   && npx wrangler deploy.

S198 START (post-founder-action):
PRIORITY 1 (~15 min): E2E F-3 email sequence (5 email Gmail preview) + F-4 health (curl /admin/health/run-now + verifica Discord webhook).
PRIORITY 2 (~30 min): privacy policy + ToS draft via agent legal-compliance-checker → pubblicare landing CF Pages.
PRIORITY 3 (~60 min): test live audio Sara iMac (5 scenari voice-agent-details.md § Test Live Scenari).
PRIORITY 4 (TBD schedule founder): build Win MSI rule architecture-distribution.md (P0 ~80% mercato).
PRIORITY 5 (deferred): FAQ pubblica via documentation-writer agent (P1).
```

---

## SESSIONE 196 — ✅ CHIUSA Gate 3 D-3 RICONFERMATO con margine -49.5%

**Esito**: Bundle PyInstaller sidecar S195 (199MB, espeak-ng-data + paola onnx + piper module Python API) validato E2E HTTP `/api/voice/say`. Bench 10 frasi italiane production-realistic: **P95 404ms vs SLO 800ms** (margine -49.5%, miglioramento +32% vs S193 P95 590ms direct API). Sidecar self-contained, zero deps esterne runtime.

### Lavoro completato S196

1. ✅ **Bundle inspection** (`pyi-archive_viewer -l -r dist/voice-agent`):
   - `models/tts/it_IT-paola-medium.onnx` 58MB ✅
   - `models/tts/it_IT-paola-medium.onnx.json` ✅
   - `piper/espeak-ng-data/it_dict` 95KB + 100+ altri lang dict ✅
   - `piper/espeakbridge.so` ✅
   - PYZ modules: `piper.voice`, `piper.config`, `piper.phonemize_espeak` ✅
   - **Conclusione**: spec S195 (`collect_data_files('piper')` + `collect_submodules('piper')`) ha funzionato correttamente.

2. ✅ **Sidecar standalone E2E**:
   - Avviato `dist/voice-agent --port 3099 --host 127.0.0.1` (non disturba pipeline 3002)
   - `.tts_mode = fast` scritto in `~/Library/Application Support/Fluxion/voice-agent/.tts_mode`
   - Log conferma: `[TTSEngineSelector] PiperTTSEngine selected (fast mode)` + `PiperTTS: Python API voice loaded (model=_MEIPASS.../paola-medium.onnx)`
   - POST `/api/voice/say` ritorna `success=true` + `audio_base64` 112KB con header `RIFF...WAVEfmt` valido.

3. ✅ **Bench latency 10 frasi production-realistic**:
   | Metrica | Valore |
   |---------|--------|
   | P50 | **278.0 ms** |
   | **P95** | **404.1 ms** |
   | P99/MAX | 404.1 ms |
   | MIN | 209.7 ms |
   | AVG | 296.4 ms |
   | STDEV | 73.6 ms |

   Tutte 10 < 405ms, nessun outlier. WAV 64KB-129KB per utterance.

4. ✅ **Sync bundle**: `cp dist/voice-agent → src-tauri/binaries/voice-agent-x86_64-apple-darwin` (208MB, da S195 build) per Tauri sidecar packaging.

5. ✅ **Artefatto perf**: `docs/perf/D3-voice-latency.md` aggiornato con sezione "S196 RESULT" (tabella metriche + confronto progressivo S191→S193→S196 + reproduce instructions).

### Confronto progressivo Gate 3 D-3

| Run | Setup | P95 | Stato |
|-----|-------|-----|-------|
| S191 | Edge-TTS cloud fallback | 867 ms | ❌ FAIL |
| S193 | Piper subprocess `--user` install (direct API) | 590.8 ms | ✅ PASS |
| **S196** | **Piper Python API via sidecar bundle** (HTTP) | **404.1 ms** | **✅ PASS PRO** |

**Perché S196 outperform S193**:
1. PiperVoice eager-loaded in `__init__` → no cold-load (~200ms) primo synthesize
2. No subprocess fork/exec → Python API in-process zero IPC penalty
3. `asyncio.to_thread` non-blocking → server può servire concurrent

### Files modificati S196

- M `docs/perf/D3-voice-latency.md` (+60 righe sezione S196)
- M `HANDOFF.md` (questo file, ricreato post auto-close commit 42ef289)
- iMac side: bundle copiato `dist/voice-agent` → `src-tauri/binaries/voice-agent-x86_64-apple-darwin` (208MB)

### Stato Gate 3 — ✅ COMPLETO BLINDATO

- F-1 ✅ | F-2 ✅ | F-3 ✅ CODE COMPLETE | F-4 ✅ CODE COMPLETE
- D-1 ✅ | D-2 ✅ (P95 36.9ms) | **D-3 ✅ PASS PRO** (P95 404ms vs SLO 800ms)
- Bundle PyInstaller sidecar self-contained → distribuibile a end-user senza deps esterne.

### Tech debt residuo S197 (P2)

- `scripts/setup-piper.js` orphan — rimuovere (path mismatch confermato S193+S195+S196)
- `docs/launch/PRE-LAUNCH-AUDIT.md` NEW — Gate 3 readiness summary aggregato (D-1+D-2+D-3 + F-1..F-4)
- Deploy CF Worker F-3 + F-4 (S189-A still pending: founder action 2 cmd terminale per `wrangler secret put` + `wrangler deploy`)
- Founder action: rotate 2 CF tokens (S192 procedure)

### Tech debt P3 (deferred milestone)

- Bundle Linux/Windows sidecar (PyInstaller cross-compile). Questa S196 solo macOS x86_64.
- Universal Binary macOS arm64 (Apple Silicon native).

### Prompt ripartenza S197

```
S196 ✅ CHIUSA — Gate 3 D-3 PASS PRO P95 404ms (margine -49.5% vs SLO 800ms).
Bundle sidecar 208MB self-contained validato E2E.

PRIORITY 1 — PRE-LAUNCH-AUDIT.md NEW (~15 min):
  Aggregare Gate 3 readiness: F-1..F-4 + D-1+D-2+D-3 con metriche misurate.
  Format: tabella checklist 6 categorie (Build/Functional/Security/Perf/Compliance/CS) + sign-off.

PRIORITY 2 — Cleanup orphan scripts (~5 min):
  rm scripts/setup-piper.js (path mismatch S193+S195+S196).
  Verifica package.json non lo referenzia più.

PRIORITY 3 — Deploy CF F-3 + F-4 (founder action ~10 min):
  cd fluxion-proxy && npx wrangler secret put DISCORD_HEALTH_WEBHOOK_URL && npx wrangler deploy
  Then E2E: 5 email Gmail (sequence preview) + curl /admin/health/run-now

PRIORITY 4 — Founder ROTATE 2 CF tokens (S192 procedure, ~3 min dashboard).

PRIORITY 5 (deferred) — Bundle Win/Linux sidecar (cross-compile PyInstaller).
```
