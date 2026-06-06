# FLUXION — ROADMAP AUTORITATIVO (unico)

> **Questo è l'UNICO roadmap valido.** Supersede: `ROADMAP_S183_S190.md` (piano aprile, stale) e la versione precedente di questo file (backup: `ROADMAP_REMAINING.md.bak-PRE-S344-20260606-184921`).
> Prodotto in S344 (2026-06-06) per mandato founder S343. Allineato allo stato reale verificato sul terreno (gh/git/Glob/Grep, non da handoff).
> **REGOLA #29**: si lavora SOLO da questo file. Ogni task deve puntare a una voce qui sotto. Vietato freelancing/speculazione.
> **Obiettivo nord**: primo €497. Il percorso revenue NON passa da Sara (voce), passa dal **Sales Agent WA → checkout €497**.

---

## ✅ PRONTO (verificato, non rifare)
- **Payment rail prod** — worker `fluxion-proxy`, smoke €1 LIVE end-to-end + revocation anti-refund (S331, commit `d5c330f`).
- **Email deliverability** — `fluxion-app.com` Resend verified + smoke pass da `noreply@fluxion-app.com` (S342).
- **Custom domain** — `https://fluxion-app.com/health` 200 HTTPS su worker prod (S342).
- **Gestionale core** — app Tauri funzionante.
- **Sara Layer 1 (testo)** — `voice-agent/scripts/test_all_verticals_e2e.py` 50 OK/3 WARN su 12 verticali (S333).
- **License client-side** — `src/lib/phone-home.ts` + `src/components/license/SaraTrialBanner.tsx` IMPLEMENTATI (rami offline-grace/clock-rollback/banner non behavior-verified, gated GUI iMac Keychain — REGOLA #12).

---

## 🎯 PERCORSO REVENUE — ordine ROI verso primo €497 (tutto CTO-actionable, zero-dep-esterne)

### R1 — SALES AGENT: strato conversazione→checkout  `[il vero gap revenue]`
**Stato**: `tools/SalesAgentWA/` ha scraper+sender+monitor+template+LaunchAgent (girato live 15 apr: 205 lead, reply 60%). MANCA la chiusura.
**Componenti GIÀ presenti/definiti** (tutti ~14 apr): `scraper.py`, `sender.py`, `monitor.py`, `agent.py`, `templates.py`, `config.py`, `utm.py`, `dashboard.py`, `test_send.py`, `com.fluxion.salesagent.plist` (LaunchAgent), `SALES-AGENT-BLUEPRINT.md`, `wa_session/` (sessione Chrome WA persistita).
**Gap verificati (cosa MANCA)**:
- `config.py:19-27` → CTA/`LANDING_URL` puntano a `https://fluxion-landing.pages.dev`, **non** a `fluxion-app.com` né a link Stripe checkout €497.
- `monitor.py` logga le risposte ma **nessuno strato conversazione→checkout/handoff** (nessun "497"/"stripe"/"checkout" nei .py).
- LaunchAgent `com.fluxion.salesagent.plist` non caricato.
**Done-condition (TERMINAL_FACT)**: una conversazione WA reale di test → l'agente propone link checkout €497 funzionante → Stripe checkout si apre col prezzo corretto. E2E PASS.
**Sub-task**: (a) cablare link checkout reale €497 (Stripe payment link su prezzo €497, NON €1 smoke); (b) aggiornare CTA a dominio/landing corretto; (c) strato risposta→handoff nel monitor; (d) caricare LaunchAgent.

### R2 — DISTRIBUZIONE: release sana multi-OS  `[~10h, secondo blocker]`
**Stato**: distribuibile OGGI **solo macOS Intel x64** (DMG+PKG su `v1.0.0`).
**Gap verificati**:
- `v1.0.1` è "Latest" ma ha **0 asset** → l'auto-updater (`tauri.conf.json` → `github.com/lukeeterna/fluxion-desktop/releases/latest`) punta a una latest **senza binari** = BUG bloccante update.
- Windows NSIS `.exe` esiste in `v0.0.0-dev` **(draft, non pubblico)** — vicino, va pubblicato+testato.
- No arm64/Universal Binary (solo Intel x64).
**Done-condition (TERMINAL_FACT)**: una release pubblica "Latest" con asset funzionanti per macOS + Windows installabili e testati (install → app parte).
**Sub-task**: (a) FIX release latest vuota (allegare asset o ripubblicare); (b) pubblicare+testare Windows MSI/NSIS; (c) valutare arm64 (mercato secondario, può slittare).

### R3 — COMPLIANCE P0  `[rischio AGCM/legale, gate go-live pubblico]`
**Stato item (evidenza S344)**:
- **E-3** `STRIPE_SECRET_KEY` Worker — no leak committato (CLEAN), MA `refund.ts:202-212` torna 503 se manca → garanzia 30gg non operativa. **Azione**: `wrangler secret put STRIPE_SECRET_KEY` su worker prod + verifica refund path. `[QUICK WIN]`
- **E-2** disclaimer testimonial — probabile gap sulla landing di vendita principale (disclaimer presente solo in `termini.html`/`guida-gdpr-pmi.html`). **Azione**: aggiungere disclaimer ai testimonial sulla landing vendita.
- **C-1** admin auth — 0 match in `src/`+`src-tauri/` → assente. **Azione**: verificare se serve per il modello desktop-locale; se sì, implementare.
- **B-3** fatturazione SDI — solo schema DB (`migrations/007_fatturazione_elettronica.sql`), integrazione SDI INCERTA. **Azione**: verificare scope reale (è P0 per il primo €497?).
- **B-2** WhatsApp Cloud API — non implementato in source. **Azione**: verificare se necessario per il primo €497 o deferribile (il Sales Agent usa WA web automation, non Cloud API).
**Done-condition**: per ciascun item P0 confermato in-scope → CHIUSO con evidenza, oppure declassato fuori-P0 con motivazione.

---

## 🔒 BLOCKED-ON ESTERNO (NON lavoro autonomo)
- **Sara Layer 2 (audio reale via SIP)** — `reg_status:403` da EHIWEB/MOR Softswitch su `0972536918@sip.vivavox.it` (confermato S344 pre-flight). Gate vendita PREMIUM (REGOLA #21), **NON** product-core per il primo €497.
  - **Azione Luke (unica leva)**: inoltrare a EHIWEB il messaggio pronto (vedi `.claude/NEXT_SESSION_PROMPT.manual.md` righe 40-42): account registrava 200 OK il 3 giugno, ora MOR accetta Digest ma risponde 403 → verificare flag abilitazione registrazione SIP + lockout anti-frode + saldo.
  - **Verifica sblocco**: `ssh imac "curl -s http://127.0.0.1:3002/api/voice/voip/status"` → `reg_status:200`.
  - Diagnosi locale CHIUSA (S341-bis: locale 100% sano, è policy provider). **NON ri-diagnosticare.**
- **Rami license client-side** (offline-grace/clock-rollback/banner) — gated GUI iMac Keychain (REGOLA #12), live-verify in finestra founder-presente.

---

## SEQUENZA OPERATIVA
1. **R1** (Sales Agent checkout) — apre il primo €497.
2. **R2** (distribuzione Windows + fix release) — il cliente Windows deve poter installare.
3. **R3** (compliance, partendo da E-3 quick win) — gate go-live pubblico.
4. Sara Layer 2 → SOLO quando EHIWEB sblocca (parcheggiato).
