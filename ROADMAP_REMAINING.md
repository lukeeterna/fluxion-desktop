# FLUXION — Roadmap Enterprise v1.0+
> Aggiornato: 2026-03-04 | CTO Audit sessione 18 — Enterprise Gap Analysis completa
> **Strategia**: Prima vendita → Qualità → Infrastruttura enterprise → Scale

---

## ✅ FOUNDATION COMPLETATA

| Feature | Status | Commit |
|---------|--------|--------|
| CRM + Calendario + Servizi + Operatori | ✅ | — |
| Fatturazione SDI + XML FatturaPA multi-provider | ✅ | c1ece40 |
| Voice Agent Sara — 1259 PASS / 0 FAIL | ✅ | c4bf3aa |
| F03 Latency Optimizer — 1263 PASS / 0 FAIL | ✅ | c0c5242 |
| F01 Click-to-sign contratto FES eIDAS | ✅ | cf56a0e |
| F02 Vertical system Sara (guardrails + entity extractor) | ✅ | bb98906 |
| F02.1 NLU Hardening — 7 P0 bug | ✅ | c4bf3aa |
| WhatsApp webhook post-booking | ✅ | 47ba161 |
| License system Ed25519 offline | ✅ | — |
| Feature gate Voice (Base tier) | ✅ | 391ddbf |
| B4 Exception handling narrowed | ✅ | 499f9da |
| Landing page live | ✅ | — |

---

## 🔴 CRITICO — BLOCKER VENDITA

### F03 — Latency Optimizer Sara
**Goal**: P95 < 800ms (attuale ~1330ms). Groq free tier = cliente scoperto se supera rate limit.
**Status**: ✅ COMPLETE (2026-03-04) — 1263 PASS / 0 FAIL
**Commits**: 4f7478c + 7490e4b + 30d79e5 + c0c5242

**Deliverables completati:**
- [x] Groq `stream=True` per LLM (risposta incrementale) → -400ms percepiti (streaming L4)
- [x] Groq timeout 3s max + fallback locale (FALLBACK_RESPONSES dict) → **zero "cliente scoperto"**
- [x] Cache intento+entità per utterance identiche (LRU 100 slot) → -200ms per ripetizioni
- [x] Groq key rotation pool (3 key free tier = 3x rate limit) → resilienza
- [x] Monitoring latency P50/P95/P99 in SQLite analytics → GET /api/metrics/latency
- [x] WAL mode SQLite analytics → scritture concorrenti safe

**P95 reale**: da misurare dopo sessioni live con LLM (target <800ms vs baseline ~1330ms).

---

### F04 — Schede Mancanti ✅ DONE
**Goal**: Aggiungere schede mancanti per 3 verticali chiave.
**Status**: ✅ DONE (già in codebase — sessione 25 verificato)

- [x] SchedaParrucchiere.tsx (taglio, colore, trattamento, allergie prodotti)
- [x] SchedaFitness.tsx (obiettivi, misurazioni, progressione, piano allenamento)
- [x] SchedaMedica.tsx (anamnesi, patologie, farmaci, allergie, consenso GDPR)
- [x] SchedaEstetica.tsx, SchedaFisioterapia.tsx, SchedaOdontoiatrica.tsx, SchedaVeicoli.tsx, SchedaCarrozzeria.tsx

---

### P0.5 — Onboarding Frictionless (BLOCCA VENDITE)
**Problema**: Utente PMI non tecnico deve configurare Groq API key + Gmail app code → abbandono garantito
**Effort**: 4-6h

- [ ] **Opzione A (raccomandata)**: Fluxion bundla sua Groq key (tier gratuito) → utente zero config
  - Implementazione: key cifrata in binario Tauri, rotazione automatica
  - Rischio: rate limit shared → risolvibile con pool di key
- [ ] **Opzione B (fallback)**: Setup wizard passo-passo con video/screenshot in-app
- [ ] Guida PDF attrattiva (non tecnica) per utente finale PMI
- [ ] Test: utente senza background tecnico completa setup in < 5 minuti

---

## 🟡 PRODUCT QUALITY (dopo prima vendita)

### F04 — Schede Mancanti ✅ DONE
(già completato — vedi sezione CRITICO sopra)

### F05 — LicenseManager UI
**Effort**: 1h
- [ ] Tab Impostazioni → sezione "La mia licenza" con tier attivo, scadenza trial, upgrade CTA

### F06 — Clinic Tier completo
**Effort**: 2h
- [ ] Clinic tier €1.497: verticali illimitate + export API + onboarding 1h
- [ ] Feature gate API export (JSON/CSV clienti, appuntamenti)

### F07 — LemonSqueezy Payment Integration
**Effort**: 3h (dopo approvazione account Kashish)
- [ ] Webhook LemonSqueezy → attivazione licenza Ed25519 offline
- [ ] In-app upgrade path (Base → Pro → Clinic)
- [ ] Ricevuta automatica + email conferma

---

## 🟠 INFRASTRUTTURA ENTERPRISE (parallelizzabile con F04-F07)

### F10 — CI/CD GitHub Actions
**Goal**: Eliminare il piano "iMac checkpoint" manuale da ogni fase GSD → -1 piano per fase.
**Effort**: 3-4h

- [ ] `.github/workflows/ci.yml`: type-check + pytest su ogni push
- [ ] Matrix: Python 3.9 (iMac runtime) + Python 3.13 (MacBook dev)
- [ ] Badge stato CI nel README
- [ ] Blocco merge se CI fallisce
- **ROI**: ogni fase GSD futura risparmia ~1h di verifica manuale

### F11 — Docker Voice Agent
**Goal**: Ambiente riproducibile. Elimina "funziona su iMac non su MacBook".
**Effort**: 3h

```dockerfile
FROM python:3.9-slim
# ONNX Runtime, aiohttp, sqlite3 — stessa versione MacBook e iMac
```

- [ ] `Dockerfile` + `docker-compose.yml` per voice agent
- [ ] Volume mount per SQLite DB locale
- [ ] CI usa container Docker → test identici ovunque
- **ROI**: onboarding nuovo dev in 10 minuti invece di 2h di setup

### F12 — File Index per Codebase Grossa
**Goal**: Ridurre token bruciati leggendo file da 2000+ righe interi.
**Effort**: 2h

- [ ] `voice-agent/src/_INDEX.md`: mappa metodo → righe per i 3 file > 1000 righe
  - `booking_state_machine.py` (~2600 righe) → indice 23 stati + metodi
  - `orchestrator.py` (~900 righe) → indice 5 layer + metodi chiave
  - `italian_regex.py` (~850 righe) → indice pattern groups
- [ ] Aggiornamento automatico indice via pre-commit hook
- **ROI**: -30-40% token per sessioni che toccano voice agent

### F13 — SQLite Backup & Auto-export
**Goal**: Dato locale = rischio totale se disco si guasta. PMI non fa backup.
**Effort**: 2h

- [ ] Backup automatico SQLite giornaliero in cartella `~/Fluxion_Backup/`
- [ ] Retention: ultimi 30 giorni
- [ ] Export CSV clienti/appuntamenti on-demand da UI
- [ ] Alert in-app se backup > 7gg fa

### F14 — Security Hardening
**Goal**: Produzione-ready per PMI con dati sensibili.
**Effort**: 2h

- [ ] Voice agent bind `0.0.0.0` → `127.0.0.1` (non esposto su rete locale)
- [ ] HTTP Bridge Tauri: validazione origin (solo localhost)
- [ ] Groq API key: non in .env ma in keychain macOS (SecureStorage Tauri)
- [ ] Rate limiting voice endpoint (max 100 req/min)

---

## 🟢 BUSINESS & SCALA (post-approvazione LemonSqueezy)

### F08 — Test Live Audio Sara T1-T5
**Effort**: 1h
- [ ] Scenari T1-T5 su iMac con microfono reale
- [ ] Documentazione audio + transcript

### F15 — VoIP Integration (EHIWEB + Telnyx)
**Prerequisito**: F03 Latency < 800ms P95
**Effort**: 8-12h

- [ ] Telnyx SIP trunk setup
- [ ] EHIWEB numero italiano
- [ ] Bridge SIP → WebSocket → voice pipeline
- [ ] Test latenza end-to-end (SIP + STT + LLM + TTS + SIP) target < 2s percepiti
- **HW Note**: Intel iMac limita. Per VoIP produzione seria: valutare Mac Mini M2 (~€600)

### F16 — Landing Page Upgrade
**Effort**: 3h
- [ ] Foto verticali reali (screenshot dall'app)
- [ ] Benchmark competitor (prezzo/feature)
- [ ] Linguaggio piano per PMI (no tech jargon)
- [ ] CTA A/B test

### F09 — Multi-sede (RIMANDATO)
**Status**: 🚫 Dopo P.IVA forfettaria

---

## 📐 Hardware Assessment CTO

| Macchina | Specs | Ruolo | Limite |
|----------|-------|-------|--------|
| MacBook | Dev machine | TypeScript, Python unit test, Claude Code | No Rust build |
| iMac Intel 16GB | Build + voice pipeline | Rust build, full pytest, Sara pipeline | STT locale impraticabile |

**Bottleneck**: STT. Con Intel iMac, Whisper.cpp medium = ~1.5s → sopra target.
**Soluzione attuale**: Groq STT cloud (~200ms) + timeout 3s + fallback.
**Soluzione futura (VoIP)**: Mac Mini M2 Pro (~€800) → Whisper.cpp con Core ML ~150ms.

**Disco iMac**: 931GB totale, 554GB liberi → nessun problema. Docker, modelli ONNX, SQLite backup tutto gestibile.

---

## 📋 Priorità Esecuzione CTO (ordine consigliato)

```
SPRINT 1 (questa settimana):
  F03 → Latency + Groq resilienza     [BLOCKER revenue]
  P0.5 → Onboarding frictionless      [BLOCKER vendite]

SPRINT 2 (prossima settimana):
  F04 → Schede mancanti               [product complete]
  F10 → CI/CD GitHub Actions          [infra — sblocca velocità sviluppo]
  F07 → LemonSqueezy                  [revenue]

SPRINT 3 (dopo prima vendita):
  F05, F06 → License UI + Clinic tier
  F11 → Docker voice agent
  F12 → File index (riduce token Claude)
  F13 → SQLite backup
  F14 → Security hardening

SPRINT 4 (maturità enterprise):
  F08 → Test live audio
  F15 → VoIP (valuta upgrade HW)
  F16 → Landing upgrade
```

---

## 📐 Architettura Pricing Definitiva

| Tier | Nome | Prezzo | Features chiave |
|------|------|--------|----------------|
| Trial | Trial 30gg | €0 | Tutto incluso |
| Base | FLUXION Base | €497 | 1 verticale, no Voice |
| Pro | FLUXION Pro | €897 | 3 verticali + Voice + WhatsApp AI |
| Clinic | FLUXION Clinic | €1.497 | Verticali illimitate + API + onboarding |

---

## ⚖️ Note Legali

- **Venditore**: Privato senza P.IVA → Prestazione Occasionale max €5.000/anno
- **Documento vendita**: Ricevuta P.O. con ritenuta d'acconto 20%
- **Contratto**: Concessione Licenza Software (FES click-to-sign in-app)
- **GDPR**: Dati locali, no cloud, conservazione 10 anni + export PDF
- **P.IVA**: Aprire regime forfettario prima dei €5.000 (tassa effettiva ~12%)
- **Multi-sede**: Rimandato a dopo apertura P.IVA

---

## 🛠️ Workflow CTO — Claude Code 2026

```
Ogni sessione:
1. Leggi HANDOFF.md + ROADMAP_REMAINING.md
2. Prendi la prima fase NON completata in Sprint corrente
3. CoVe 2026: Research → Plan → Implement → Verify → Deploy
4. Aggiorna status in questo file
5. Aggiorna HANDOFF.md + MEMORY.md
6. /compact a 70% context

Subagenti in parallelo dove possibile:
- Research in background mentre leggi file
- Type-check sempre prima del commit
- Wave execution per piani indipendenti
```
