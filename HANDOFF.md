# FLUXION — Handoff Sessione 98 → 99 (2026-03-19)

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
Branch: master | HEAD: 0b56682 (pushato ✅) + 1 fix locale non committato
iMac: sincronizzato ✅ | Pipeline: ATTIVA ✅ (127.0.0.1:3002)
type-check: 0 errori ✅
Test: 1998 PASS / 8 FAIL pre-esistenti / 31 skipped
```

---

## COMPLETATO SESSIONE 98

### 1. Fix Fornitori crash "Ricarica Applicazione"
- **Bug**: `Fornitori.tsx:542` — `.find()!` non-null assertion su fornitore potenzialmente undefined
- **Causa**: quando SendConfirmDialog si apriva con un fornitore non trovato nell'array → crash → ErrorBoundary
- **Fix**: guard clause `&& fornitori.find(...)` nel conditional render — dialog non si apre se fornitore non esiste
- **Stato**: type-check 0 errori, non ancora committato

### 2. Decisione strategica CTO
- **STOP** polishing Sara features (1998 test PASS, è pronta)
- **FOCUS** su F17 — Packaging/Distribuzione (blocker vendita assoluto)
- **Helpdesk online** — zero supporto manuale, struttura self-service da creare

### 3. Audit crash ErrorBoundary (IN CORSO)
- Subagente sta scansionando tutte le pagine per pattern pericolosi (`.find()!`, unsafe access, etc.)
- Risultati da integrare in S99

---

## DA FARE S99

### Priorità 0: Commit fix Fornitori + audit crash results
- Committare il fix Fornitori.tsx
- Applicare fix da audit crash (se trovati altri pattern pericolosi)

### Priorità 1: Code Review Enterprise (skill fluxion-code-review)
- CTO ha richiesto code review completa in S99
- Usare skill `fluxion-code-review` sulle pagine principali

### Priorità 2: F17 — Packaging/Distribuzione (BLOCKER VENDITA)
- PyInstaller sidecar build (voice agent → binario nativo)
- macOS: ad-hoc signing + Universal Binary (Intel + Apple Silicon)
- Windows: MSI (WiX)
- Pagina "Come installare FLUXION" (istruzioni step-by-step)
- **Prerequisito completato**: PyInstaller spec già pronto (S93), `voice_pipeline.rs` gestisce sidecar

### Priorità 3: Helpdesk Online
- CTO non darà assistenza personale
- Creare struttura helpdesk self-service (FAQ, guide, troubleshooting)
- Pattern: pagina web statica + email auto-reply (Support Agent F18-A)

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
Leggi HANDOFF.md. Sessione 99. S98: fix crash Fornitori, decisione strategica packaging.
Priorità S99: commit fix + code review + F17 packaging (blocker vendita).
Pipeline iMac ATTIVA (127.0.0.1:3002).
DIRETTIVE: STOP polishing Sara, FOCUS packaging, zero supporto manuale, code review prima.
```
