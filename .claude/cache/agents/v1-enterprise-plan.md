# FLUXION v1.0 — Enterprise Execution Plan (CoVe 2026)
> Generato: 2026-03-02 | Agente: Plan | Analisi completa codebase

---

## Executive Summary

**Readiness Assessment: 78% toward v1.0**

FLUXION v0.9.2 ha i 3 pilastri fondamentali funzionanti. La strada verso v1.0 è chiara e a basso rischio: non richiede architetture nuove, ma polish su feature 80-90% complete + 2 nuove schede verticali (Parrucchiere + Fitness).

**Blockers critici v1.0:**
1. `window.prompt()` per Fattura24 API key — inaccettabile in produzione (security)
2. 5 schede verticali placeholder — landing vende 6 verticali
3. Voice Agent P95 1330ms vs 800ms target — KPI PRD fallisce
4. Screenshots landing obsoleti — non mostrano B2/B3/B4/C1/B5

---

## Feature Gap Analysis

### Implementato ma Non Polish (Polish Debt)

| Feature | Gap | Effort |
|---------|-----|--------|
| **SDI Fattura24** | `window.prompt()` cleartext ogni invocazione | 3h |
| **Landing Screenshots** | Obsoleti (pre-B2/B3/B4/SDI/B5) | 2h iMac |
| **Voice Latency** | 1330ms P95 vs 800ms target | 4-6h iMac Python |
| **WhatsApp Bulk** | `loyalty.rs:973` simulato, non HTTP reale | 2h |

### Nel PRD, Non Implementato

| Feature | Priorità v1.0 | Effort |
|---------|--------------|--------|
| **SchedaParrucchiere** | ✅ ALTA (primary vertical) | 8h |
| **SchedaFitness** | ✅ ALTA (second vertical) | 8h |
| **SchedaVeicoli** | 🔶 v1.1 placeholder OK | — |
| **SchedaCarrozzeria** | 🔶 v1.1 placeholder OK | — |
| **SchedaMedica** | 🔶 v1.1 placeholder OK | — |
| **Dashboard Operatori KPI Widget** | ✅ MEDIA (v_kpi_operatori già esiste) | 2h |
| **LemonSqueezy Payment** | 🔴 Post-video promo | — |
| **Multi-sede** | 🔴 Enterprise v2.0 | — |

### Test Coverage Gap

| Area | Stato |
|------|-------|
| Rust backend | ✅ 40+ tests (pre-commit hook) |
| Voice agent | ✅ 58/58 tests PASS |
| Frontend unit | 🔴 ZERO — package.json: `test:unit:frontend = "TODO: Install vitest"` |
| E2E Playwright | ⚠️ setup in e2e-tests/ ma coverage non verificata |

---

## Wave Execution Plan

### Wave 1 — Immediate Polish (Giorno 1, ~8h, MacBook + iMac)

Tutto polish su feature già 80-90% complete.

**W1-A: SDI API Key Persistence (3h, MacBook)**
- Migration `026_impostazioni_sdi_key.sql`: `ALTER TABLE impostazioni_fatturazione ADD COLUMN fattura24_api_key TEXT`
- `ImpostazioniFatturazione` struct Rust: aggiungi campo
- `Fatture.tsx`: sostituisci `window.prompt()` con read da settings; se null → redirect a `/impostazioni` con toast
- `Impostazioni.tsx`: aggiungi sezione "Integrazione SDI" con input masked per API key
- Commit: `fix(fatture): API key SDI persistita, rimosso window.prompt`

**W1-B: Dashboard Top Operatori KPI (2h, MacBook)**
- Nuovo comando Rust `get_top_operatori_mese` → query `v_kpi_operatori` WHERE current month LIMIT 3
- `Dashboard.tsx`: aggiungi `TopOperatoriCard` con nome, fatturato, appuntamenti_completati
- Commit: `feat(dashboard): Top Operatori KPI card mensile`

**W1-C: Landing Screenshots (2h, iMac required)**
- Cattura: `fx_operatori.png` (tab Statistiche KPI), `fx_fatture.png` (badge SDI verde), `fx_voice_agent.png` (NEW Sara), `fx_calendario.png` (refresh)
- Ottimizza: `pngquant --quality=70-85` + `sips -Z 1440`
- Deploy: ZIP `landing/` → Cloudflare Pages

**W1-D: Voice Latency Optimizer (4h, iMac)**
- Leggi `latency_optimizer.py` (FluxionLatencyOptimizer class)
- Integra in `main.py`: connection pooling (safe) → streaming LLM (higher risk)
- Misura P95 prima e dopo, confronta
- Fallback: se streaming causa regressioni T1-T5, ship solo connection pooling

### Wave 2 — Feature Completion (Giorni 2-3, ~18h, MacBook)

**W2-A: SchedaParrucchiere (8h)**
- Research: leggi `SchedaOdontoiatrica.tsx` (pattern) + `019_schede_clienti_verticali.sql` (schema esistente)
- Migration `027_scheda_parrucchiere.sql`: `schede_parrucchiere` (colore_capelli, lunghezza, tipo_trattamento, allergie_colorante, formulazione_attuale)
- Rust: `get_scheda_parrucchiere`, `update_scheda_parrucchiere`, `add_trattamento_parrucchiere` in `schede_cliente.rs`
- UI: sostituisce placeholder in `SchedaClienteDynamic.tsx` → form Caratteristiche + Colorazione + Storico

**W2-B: SchedaFitness (8h, parallelo con W2-A)**
- Migration `028_scheda_fitness.sql`: misurazioni_antropometriche (JSON), obiettivo, livello, schede_allenamento (JSON)
- Rust: `get_scheda_fitness`, `update_scheda_fitness`, `add_misurazione_fitness`
- UI: misurazioni (peso/altezza/BMI/% grasso), scheda allenamento giorni, progressi chart CSS

**W2-C: Frontend Unit Tests Bootstrap (2h)**
- Install Vitest + React Testing Library
- 10 smoke tests: OperatoreDettaglio tabs, Fatture SDI badge, Dashboard stats
- Aggiorna `package.json` script da "TODO" a test runner reale

### Wave 3 — Production Hardening (Giorni 4-5, ~12h)

**W3-A: Build v1.0 DMG (2h, iMac)**
- `npm run bump:version 1.0.0` (o manual `tauri.conf.json` + `package.json`)
- `npm run tauri build` su iMac
- `git tag v1.0.0 -a -m "FLUXION v1.0.0 - Release"`
- Verifica DMG installa su macOS pulito

**W3-B: Security Audit (3h, MacBook)**
- Zero API key nel repo: `git grep -r "fattura24\|groq\|lemon" -- '*.ts' '*.rs' '*.py'`
- Test license Ed25519 con hardware fingerprint diverso
- Verifica GDPR audit log (`018_gdpr_audit_logs.sql`) cattura operazioni sensitive

**W3-C: Fix window.confirm/alert residui (2h, MacBook)**
- Replace 12 `window.confirm()` → `AlertDialog` shadcn
- Replace 1 `window.alert()` → `sonner` toast
- Commit: `fix(ui): sostituiti window.confirm/alert con shadcn Dialog e sonner`

**W3-D: PRD + Documentation Update (1h)**
- `PRD-FLUXION-COMPLETE.md`: aggiorna pricing da €199/€399/€799 → €297/€497/€897
- `MEMORY.md`: aggiorna con v1.0 completion status
- `HANDOFF.md`: aggiorna Active Sprint a v1.0

---

## Risk Matrix

| # | Rischio | Prob | Impatto | Mitigazione |
|---|---------|------|---------|-------------|
| R1 | Voice Latency Optimizer rompe T1-T5 | Media | Alto | Backup main.py; integra incrementalmente; fallback connection-pooling only |
| R2 | SDI XML FatturaPA rifiutato da Fattura24 | Bassa | Alto | Test XML su validatore AdE; `download_xml` sempre disponibile per export manuale |
| R3 | 5 schede verticali = 40h lavoro | Media | Medio | v1.0 richiede SOLO Parrucchiere + Fitness; restanti "coming soon" con messaging esplicito |
| R4 | macOS Screenshot qualità Retina | Media | Medio | `sips -Z 2880` su display Retina iMac (non 1440); test preview su browser 1x |

---

## Definition of Done v1.0

Tutti i criteri devono essere verificati simultaneamente:

### Functional Criteria
- [ ] F1: `npm run type-check` → 0 errori TypeScript
- [ ] F2: `npm run lint` → 0 errori ESLint
- [ ] F3: `cargo test --lib` → tutti i test Rust passano
- [ ] F4: Voice agent T1-T5 → 5/5 PASS
- [ ] F5: SDI API key: persistita in `impostazioni_fatturazione`, mai `window.prompt()` a runtime
- [ ] F6: SDI badge visibile in lista fatture con color coding (grey/giallo/verde/rosso)
- [ ] F7: SchedaParrucchiere funzionale (no placeholder): colorazione + storico CRUD
- [ ] F8: SchedaFitness funzionale: misurazioni + scheda allenamento CRUD
- [ ] F9: Dashboard mostra Top Operatori KPI card con dati mese corrente
- [ ] F10: Tutti e 6 tab OperatoreDettaglio (Anagrafica, Statistiche, Servizi, Orari, Assenze, Commissioni) renderizzano senza errori

### Performance Criteria
- [ ] P1: Voice Agent P95 latency documentata; target <1000ms (v1.0 OK), <800ms (ideale)
- [ ] P2: App cold start su iMac: <3 secondi a Dashboard render
- [ ] P3: SQLite Calendario (1 mese appuntamenti): <200ms

### Quality Criteria
- [ ] Q1: Zero `window.prompt()` nel codice UI produzione
- [ ] Q2: Zero API key hardcodate in file committati
- [ ] Q3: Landing `fluxion-landing.pages.dev` mostra screenshots post-B2/B3/B4/C1/B5
- [ ] Q4: `fx_voice_agent.png` esiste ed è referenziato in landing HTML
- [ ] Q5: `Fluxion_1.0.0_x64.dmg` prodotto e verificato installabile

### Documentation Criteria
- [ ] D1: `PRD-FLUXION-COMPLETE.md` pricing corretto (€297/€497/€897)
- [ ] D2: `MEMORY.md` aggiornato con milestone v1.0
- [ ] D3: `HANDOFF.md` aggiornato con note v1.0 e next milestone

---

## Immediate Actions (Prossime 2 Ore, MacBook)

### Azione 1 — Fix SDI API Key UX (90min, Priority 1 URGENTE)
```
FASE 1: Research già in sdi-fatturapa-research.md
FASE 2: Migration 026 DDL + Rust struct + acceptance criteria
FASE 3: Implement (migration + Rust + Fatture.tsx + Impostazioni.tsx)
FASE 4: npm run type-check + test manuale (imposta key, clicca Invia SDI → no prompt)
FASE 5: git commit + git push
```

### Azione 2 — Dashboard KPI Widget (60min, parallelo con A1)
```
FASE 3: Rust command get_top_operatori_mese + Dashboard.tsx TopOperatoriCard
FASE 4: npm run type-check + review visiva
```

### Azione 3 — Research Schede Verticali (30min, subagente)
```
Lancia subagente: leggi SchedaOdontoiatrica.tsx + migration 019 + schede_cliente.rs
Scrivi: .claude/cache/agents/schede-verticali-research.md
Sblocca Wave 2 immediatamente
```

---

## Critical Files per Implementation

| File | Rilevanza | Azione |
|------|-----------|--------|
| `src/pages/Fatture.tsx:147` | W1-A SDI key fix | Sostituisci `window.prompt()` |
| `src-tauri/src/commands/fatture.rs` | W1-A Rust struct | Aggiungi `fattura24_api_key` |
| `src/pages/Dashboard.tsx` | W1-B KPI widget | Aggiungi `TopOperatoriCard` |
| `src/components/schede-cliente/SchedaClienteDynamic.tsx` | W2-A/B | Replace 5 placeholder con implementazioni |
| `voice-agent/src/latency_optimizer.py` | W1-D voice | Integra in main.py |
| `src-tauri/src/commands/appuntamenti.rs` | W3-B safety | Fix 21 bare `unwrap()` |

---

*Fonte: Plan agent — analisi completa codebase FLUXION v0.9.2 + PRD alignment*
