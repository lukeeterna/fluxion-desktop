# CARRY MAGAZZINO S360 — RESET COMPLETO, BUILD BLOCCATO SU NPM PATH

## Stato Verificato (2026-06-09 sessione S360)

**Azioni completate:**
- ✅ Reset HEAD a `95d21cc` (commit di handoff Magazzino FASI 1-5 complete)
- ✅ File FASE 4 frontend verificati presenti su iMac:
  - `/Volumes/MacSSD - Dati/fluxion/src/pages/Magazzino.tsx` (42KB)
  - `/Volumes/MacSSD - Dati/fluxion/src/hooks/use-magazzino.ts` (6.5KB)
  - `/Volumes/MacSSD - Dati/fluxion/src/types/magazzino.ts` (2.6KB)
- ✅ `.so` NDEBUG Sara presente e corretto: `/Volumes/MacSSD - Dati/fluxion/voice-agent/lib/pjsua2/_pjsua2.cpython-39-darwin.so` → 8.6MB ✅
- ❌ Build Tauri bloccato: `npm run tauri build` fallisce con `spawn sh ENOENT`

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
