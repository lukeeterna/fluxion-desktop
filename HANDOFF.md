# FLUXION — Handoff Sessione 99 → 100 (2026-03-19)

## CTO MANDATE — NON NEGOZIABILE
> **"Basta polishing Sara — il prodotto è pronto. Ora PACKAGING e distribuzione. Zero supporto manuale, helpdesk online adeguato."**

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.2` | Voice pipeline: porta 3002 (127.0.0.1) | **iMac DISPONIBILE + PIPELINE ATTIVA**
**MacBook**: Playwright, Vite (1420), ffmpeg 8.0, Edge-TTS (pip), wrangler 3.22
**Tauri dev su iMac**: `bash -l -c 'cd "/Volumes/MacSSD - Dati/fluxion" && npm run tauri dev'`

---

## STATO GIT
```
Branch: master | HEAD: 0fa538b (da pushare)
iMac: da sincronizzare
type-check: 0 errori
```

---

## COMPLETATO SESSIONE 99

### 1. Enterprise Code Review — Full System Audit
- **Skill**: `fluxion-code-review` + 6 code-reviewer subagenti + 3 fix-agent specializzati
- **Scope**: 110+ file frontend, tutti i .rs backend, tutti i .py voice agent
- **Grade complessivo**: B (83/100) — 0 CRITICAL, 20 HIGH trovati

### 2. Fix 15/20 HIGH Issues (commit 0fa538b)

**Frontend (7/7 HIGH fixati):**
- `Fornitori.tsx`: `.find()!` → safe IIFE con lookup singolo
- `DiagnosticsPanel`: `window.open()` → `openUrl()`
- `WhatsAppQRKit`: `window.open()` fallback rimosso
- `SaraTrialBanner`, `SetupWizard`, `SdiProviderSettings`, `SmtpSettings`: `<a target="_blank">` → `openUrl()`
- `ImageAnnotator`: non-null assertion → null guard

**Rust Backend (5/5 HIGH fixati):**
- `http_bridge`: groq_api_key non più esposta via HTTP (ritorna boolean)
- `http_bridge`: smtp_password mascherata in risposta HTTP
- `voice_pipeline.rs`: `unwrap()` → `ok_or_else`
- `appuntamenti.rs`: 2x `unwrap()` → match guards
- `lib.rs`: migration runner refactored 1451 → 658 righe (-793 righe boilerplate)

**Voice Agent (3/8 HIGH fixati):**
- `orchestrator.py`: connection leak → context manager
- `orchestrator.py`: "il solito" 3x copy → `_apply_solito_to_context()` helper
- `Fornitori.tsx`: `.catch(() => {})` → `console.warn`

### 3. Audit Reports (in `.claude/cache/agents/`)
- `code-review-frontend-s99.md` — review diff-scoped S96-S98
- `code-review-rust-s99.md` — review diff-scoped S96-S98
- `code-review-voice-s99.md` — review diff-scoped S96-S98
- `full-audit-frontend-s99.md` — audit completo tutti i .tsx
- `full-audit-rust-s99.md` — audit completo tutti i .rs
- `full-audit-voice-s99.md` — audit completo tutti i .py

---

## DA FARE S100

### Priorità 0: Fix Voice Agent HIGH rimanenti (5 HIGH — sessione dedicata)
Da `full-audit-voice-s99.md`:
1. **H1**: Error response leakage in `main.py` — `str(e)` esposto ai client
2. **H3+H4**: Unbounded memory growth (`_rate_limit_store`, `_sales_sessions`)
3. **H6**: PII in logs (`whatsapp_callback.py` — numeri telefono)
4. **H7**: Shared mutable `_current_session_id` in `main.py`
5. **H8**: Blocking `time.sleep()` in `error_recovery.py`
- File già parzialmente modificati (main.py, vad_wrapper.py, whatsapp_callback.py) ma NON committati

### Priorità 1: F17 — Packaging/Distribuzione (BLOCKER VENDITA)
- PyInstaller sidecar build (voice agent → binario nativo)
- macOS: ad-hoc signing + Universal Binary (Intel + Apple Silicon)
- Windows: MSI (WiX)
- Pagina "Come installare FLUXION" (istruzioni step-by-step)

### Priorità 2: Audit UI/UX Completo (skill enterprise dedicata)
- CTO richiede audit completo UI con skill Claude Code enterprise
- Menu dropdown, layout sballati, UX issues
- Lanciare ui-designer subagent per scan tutte le pagine

### Priorità 3: Helpdesk Online
- Struttura self-service (FAQ, guide, troubleshooting)

---

## DIRETTIVE CTO (NON NEGOZIABILI)

1. **STOP POLISHING SARA** — il prodotto è pronto, ora packaging
2. **ZERO SUPPORTO MANUALE** — helpdesk online self-service obbligatorio
3. **F17 È IL BLOCKER** — senza installer, FLUXION non esiste per i clienti
4. **SEMPRE code reviewer** dopo ogni implementazione significativa
5. **Deep research CoVe 2026** — SEMPRE subagenti PRIMA di implementare
6. **SARA = SOLO DATI DB** — zero improvvisazione
7. **SEMPRE 1 nicchia** — una PMI = un'attività

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 100. S99: enterprise code review completa, 15/20 HIGH fixati.
Priorità S100: fix 5 voice agent HIGH rimanenti (sessione dedicata) + F17 packaging.
Pipeline iMac ATTIVA (127.0.0.1:3002). Sync iMac necessario.
File voice parzialmente modificati (main.py, vad_wrapper.py, whatsapp_callback.py) NON committati.
```
