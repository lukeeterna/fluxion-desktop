# CARRY MAGAZZINO S360 (2026-06-09) — PREREQUISITO FASE 6 COMPLETO: app Magazzino LIVE su iMac. Resta SOLO E2E S1-S7 (HITL Luke@iMac).

## Stato Verificato (sessione S360, tutto live trust-but-verify)

**Azioni completate:**
- ✅ Reset iMac → `93cc1db` (era 97 commit dietro; base `95d21cc` + fix migration 042). 4 condizioni de-risk validate. Stash salvato `PRE-FASE6-safety-20260609`.
- ✅ File FASE 4 frontend presenti (Magazzino.tsx 42KB / use-magazzino.ts / types/magazzino.ts). `.so` NDEBUG Sara 8.6MB intatto.
- ✅ **BUG #1 FIXATO — node_modules corrotto** (NON path-con-spazi): symlink dangling `.bin/vite`→`vite/bin/vite.js` inesistente → `vite/tauri: command not found`. Fix: `npm ci`.
- ✅ **BUG #2 FIXATO (commit `93cc1db`) — migration 042 mai cablata**: `042_magazzino.sql` esisteva ma NON registrata in `lib.rs` (runner fermo a 041) → tabelle `articoli`/`movimenti_magazzino` MAI create sul DB live. Unit test 4/4 passavano (schema autonomo) → REGOLA #24 (il claim "FASI 1-5 VERIFICATE" era falso sul DB live). Fix: `run_migration("042", ...)`.
- ✅ **APP LIVE**: `cargo tauri dev` → `✓ [042] ready` + `🚀 Application ready` + `🌉 HTTP Bridge 3001`. Tabelle magazzino confermate nel DB. Istanze stale killate (3001 pulito).

**LANCIO APP (rilancio E2E):** `ssh imac` → `cd '/Volumes/MacSSD - Dati/fluxion' && cargo tauri dev` (login shell per PATH). NON `npm run tauri`. Log: `/tmp/fluxion-dev.log`.
**OSSERVAZIONE E2E (CC read-only):** DB `/Users/gianlucadistasi/Library/Application Support/com.fluxion.desktop/fluxion.db` → `sqlite3 "$DB" "SELECT id,nome,giacenza,soglia_minima,alert_notificato FROM articoli;"` + `"SELECT * FROM movimenti_magazzino;"`. Magazzino è SOLO IPC (no HTTP bridge) → E2E richiede la GUI (Luke clicca).
**PROSSIMA AZIONE = E2E FASE 6 S1-S7 (HITL).** Poi → Windows R2 → Sara.

## Blocco Tecnico Identificato

**Root cause:** npm 10.9.2 non quota correttamente il path con spazi quando invoca script shell. Puppeteer (dependency) tenta di eseguire un comando e npm non riesce a risolvere:
```
npm error path /Volumes/MacSSD - Dati/FLUXION
npm error errno -2 ENOENT spawn sh
```

Symlink `/tmp/fluxion-build` → `/Volumes/MacSSD - Dati/fluxion` non risolve perché npm legge il path originale dai moduli installati.

## Prossima Azione — Build Alternativo

**Opzione A (CONSIGLIATA):** Cargo diretto (salta npm script shell)
```bash
cd /tmp/fluxion-build
export PATH='/usr/local/bin:/opt/homebrew/bin:$PATH'
cargo build --release
# Poi: cargo tauri build (o equiv)
```

**Opzione B:** Disabilitare Puppeteer in package.json se non essenziale per build Tauri
```bash
npm ci --omit=dev --ignore-scripts
# oppure editare package.json: rimuovere puppeteer dalle devDependencies
```

**Opzione C (se niente funziona):** Build su MacBook (path senza spazi) e sincronizzare binary su iMac
```bash
# MacBook: npm run tauri build
# iMac: scp MacBook:... → /Volumes/MacSSD - Dati/fluxion/src-tauri/target/release/
```

## Requisiti per Ripartenza

1. Risolvi build (A/B/C sopra)
2. Verifica eseguibile Tauri pronto: `file src-tauri/target/release/fluxion-desktop`
3. Lancia app per FASE 6 E2E HITL (vai a riga sotto)

## FASE 6 E2E — SCENARI S1-S7 (HITL col founder Luke)

Quando app è lanciata e visibile. **Luke clicca, CTO osserva e guida il test.**

| S | Scenario | Input | Expected | Gate |
|---|----------|-------|----------|------|
| S1 | Crea articolo | nome="Cuscino", giacenza=10, soglia=5 | alert badge=0 | ✅ nessun alert |
| S2 | Badge OK sopra soglia | apri pagina Magazzino | badge nascosto | ✅ badge=0 visivo |
| S3 | Scarico sotto soglia | scarico 6 pezzi (giacenza→4) | alert badge=1, count=1 | ✅ count esatto |
| S4 | Badge sale senza apertura | osserva badge app (no reload) | badge mostra 1 | ✅ realtime |
| S5 | Pagina evidenzia sottoscorta | apri pagina Magazzino | riga Cuscino rossa/destacata | ✅ highlight visivo |
| S6 | Anti-spam + recupero | scarico nuovo (rifiutato), carico 6 (giacenza→10) | alert=0, badge sparisce | ✅ no duplicate, reset |
| S7 | Gate licenza Base | tenta azione (es. export) senza Base | dialog "serve licenza Pro" | ✅ gating corretto |

**Output atteso:** tabella risultati in `MAGAZZINO_BUILD_2026-06-0X.md` + verdetto: `VERDE PRONTO VENDITA` o `ROSSO BLOCCO PRE-VENDITA`.

## Ordine Prioritario (Luke)

1. **FASE 6 Magazzino** (1h, HITL) ← prossimo step
2. **Windows R2 CI** (2h, `release-full.yml` rotto)
3. **Sara test vocale** (tutti verticali, `reg_status:200` prerequisito)

## Carry tecnici residui (NON bloccanti)

- **R2**: CI `release-full.yml` FAIL (5 run failures). Pre-flight: `gh run view 25328286560 --log-failed` (SSH MacBook, non iMac)
- **R3**: E-3 `sk_live` Stripe live key per go-live production
- **Custom domain**: `fluxion-app.com` attach worker + Resend verify (S342 lasciato verde, pronto)

## Note per CTO S361

- NON riaprire diagnosi npm — è quirk macOS 11 Big Sur + npm 10.9.2 con path spazi. Build Rust diretto (opzione A) funziona sempre.
- FASE 6 è HITL puro: Luke clicca, tu osservi console/log e raccogli output. NON test automatici (già fatto FASE 5 su frontend).
- Magazzino è fuori dal revenue path. Il blocco reale è R1 Sales Agent (vedi ROADMAP_REMAINING.md), ma Luke ha ordinato FASE 6 prima.
- Se build diretto Rust fallisce: escalate e chiedi a Luke se riprendere R1 oppure Sara test vocale (più high-ROI).
