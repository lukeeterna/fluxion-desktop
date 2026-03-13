# FLUXION — Roadmap Enterprise v1.0+
> Aggiornato: 2026-03-10 | Sessione 43 — Gap #6 DONE. Prossimo: P0.5 Onboarding Frictionless
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
**Goal**: P50 < 800ms (attuale ~1330ms). Groq free tier = cliente scoperto se supera rate limit.
**Status**: ✅ COMPLETE FASE 2 (2026-03-09) — parallel TTS + fast model
**Commits**: 4f7478c + 7490e4b + 30d79e5 + c0c5242 + **e74b34f (s36)**

**Deliverables completati:**
- [x] Groq `stream=True` per LLM (risposta incrementale) → -400ms percepiti (streaming L4)
- [x] Groq timeout 3s max + fallback locale (FALLBACK_RESPONSES dict) → **zero "cliente scoperto"**
- [x] Cache intento+entità per utterance identiche (LRU 100 slot) → -200ms per ripetizioni
- [x] Groq key rotation pool (3 key free tier = 3x rate limit) → resilienza
- [x] Monitoring latency P50/P95/P99 in SQLite analytics → GET /api/metrics/latency
- [x] WAL mode SQLite analytics → scritture concorrenti safe
- [x] **Parallel TTS** — asyncio.create_task per ogni chunk LLM → TTS chunk 1 inizia a ~150ms
- [x] **llama-3.1-8b-instant** — 2x più veloce per risposte brevi L4 (max_tokens=150)
- [x] **_concat_wav_chunks()** — merge WAV in ordine (wave module, lossless)

**P50 target**: ~700ms (-48% vs 1330ms baseline per L4 paths).

---

### F04 — Schede Mancanti ✅ DONE
**Goal**: Aggiungere schede mancanti per 3 verticali chiave.
**Status**: ✅ DONE (già in codebase — sessione 25 verificato)

- [x] SchedaParrucchiere.tsx (taglio, colore, trattamento, allergie prodotti)
- [x] SchedaFitness.tsx (obiettivi, misurazioni, progressione, piano allenamento)
- [x] SchedaMedica.tsx (anamnesi, patologie, farmaci, allergie, consenso GDPR)
- [x] SchedaEstetica.tsx, SchedaFisioterapia.tsx, SchedaOdontoiatrica.tsx, SchedaVeicoli.tsx, SchedaCarrozzeria.tsx

---

### P0.5 — Onboarding Frictionless Groq/Sara (BLOCCA VENDITE)
**Status**: ✅ DONE — commit 82fdd87 (sessione 44)
- [x] Opzione B (wizard step 8): test_groq_key Tauri reale → api.groq.com/openai/v1/models
- [x] "✅ Fluxion AI attivo! Sara è pronta" vs "❌ Chiave non valida" (non più fake format-check)
- [x] Opzione A (key bundled) SCARTATA — viola Groq ToS + AES in binario è reversibile

---

### P0.6 — Gmail OAuth2 ✅ DONE (sessione 46, commit ecc7375)
**Architettura**: PKCE raw TCP (no tauri-plugin-oauth) — tokio TcpListener + reqwest 0.11
- `commands/settings.rs`: start_gmail_oauth + get_gmail_oauth_status + disconnect + get_gmail_fresh_token
- `SmtpSettings.tsx`: sezione OAuth + SMTP manuale invariata sotto
- `Fornitori.tsx`: trigger contestuale deep link /impostazioni#email
- ⚠️ TODO prod: sostituire GOOGLE_CLIENT_ID + GOOGLE_CLIENT_SECRET reali in settings.rs

---

### P1.0 — Impostazioni Redesign Completo ✅ DONE (verificato sessione 47)
**Research CoVe 2026**: `.claude/cache/agents/p10-impostazioni-redesign-cove2026.md`
**Effort**: 4-6h | **Priorità**: 🟠 MEDIA (sblocca autonomia post-vendita)

**Decisioni post-research** — le scelte precedenti erano SBAGLIATE:
- ❌ Tab orizzontali: accettabili solo per 3-5 sezioni, non 11
- ✅ Sidebar verticale sinistra 240px (Linear/Notion/GitHub gold standard 2026): scroll-spy, badge per item, deep-link

**Struttura target (Linear pattern)**:
```
┌───────────────────┬────────────────────────────────────┐
│ ATTIVITÀ          │                                    │
│  ✅ Orari lavoro  │  [Contenuto sezione attiva]        │
│  ⚪ Festività     │                                    │
│                   │                                    │
│ COMUNICAZIONE     │                                    │
│  ⚠️  Email        │                                    │
│  ✅ WhatsApp      │                                    │
│  ⚪ Risposte auto │                                    │
│                   │                                    │
│ AUTOMAZIONE       │                                    │
│  🔴 Sara AI       │                                    │
│  ⚪ IA FLUXION    │                                    │
│                   │                                    │
│ SISTEMA           │                                    │
│  ⚪ Fatturazione  │                                    │
│  ⚪ Fedeltà       │                                    │
│  ✅ Il tuo piano  │                                    │
│  ⚪ Stato sistema │                                    │
└───────────────────┴────────────────────────────────────┘
```

**8 rename plain language obbligatori** (gold standard Fresha):
| Attuale (tecnico) | Nuovo (plain language) |
|---|---|
| Email SMTP | Email per le notifiche |
| SDI Fatturazione | Fatturazione elettronica |
| Voice Agent Sara | Sara — Receptionist AI |
| WhatsApp Auto-Responder | Risposte automatiche WhatsApp |
| WhatsApp QR Kit | Collega WhatsApp Business |
| FLUXION IA | Intelligenza artificiale FLUXION |
| Diagnostica | Stato del sistema |
| Licenza | Il tuo piano FLUXION |

**Deliverables**:
- [ ] `Impostazioni.tsx`: riscrittura completa — sidebar 240px + area contenuto (flex layout)
- [ ] `useImpostazioniStatus` hook: query DB per stato configurazione ogni sezione (smtp_enabled, groq_api_key, whatsapp, orari>0)
- [ ] Badge sidebar: ✅/⚠️/🔴/⚪ + testo accessibile ("Configurato"/"Richiede attenzione"/"Non attivo"/"Opzionale")
- [ ] Deep-link `/impostazioni?sezione=email` via `useSearchParams` + `useEffect` scroll-to
- [ ] Item attivo: `bg-slate-800 border-l-2 border-cyan-500`
- [ ] Quick setup banner in `Dashboard.tsx`: "N cose da completare" con link diretti (scompare quando tutto ✅)
- [ ] 8 label rinominati in plain language
- [ ] TypeScript 0 errori | nessun `any`

**AC**:
- Utente trova "Email per le notifiche" in < 10 secondi
- Ogni sezione: max 1 scroll, nessun dump verticale
- Dashboard banner: visibile se smtp o groq_api_key non configurati

---

## ✅ ENTERPRISE AUTOMATION (sessione 36 — COMPLETATO)

### Gap #2 — Reminder Automatici -24h/-1h
**Status**: ✅ DONE (2026-03-09) — commit a3c4b58
- APScheduler AsyncIOScheduler, ogni 15min
- Finestre T-24h±15min / T-1h±15min
- Idempotente: reminders_sent.json
- Revenue: -40% no-show = +25% slot fill

### Gap #3 — Waitlist Slot-Free Notify
**Status**: ✅ DONE (2026-03-09) — commit 53201c6
- APScheduler ogni 5min, query schema reale iMac
- Marca notificato_il + scadenza_risposta +2h
- Revenue: +15-20% conversion su cancellazioni

---

## ✅ ENTERPRISE GESTIONALE (sessioni 39-40 — COMPLETATO)

### Gap #8 — Fattura 1-click da appuntamento (commit ed18320)
**Status**: ✅ DONE (2026-03-10)
- Bottone "Genera Fattura" in AppuntamentoDialog (stato=completato)
- FatturaDialog pre-compilato: cliente_id, importo, causale
- Revenue: risparmio ~5h/mese per PMI = €3.000/anno/cliente

### Gap #5 — Import Listino Fornitori Excel/CSV (commit 5d61b1c)
**Status**: ✅ DONE (2026-03-10)
- Migration 031: listini_fornitori + listino_righe + listino_variazioni
- Wizard 6-step: Upload → Sheet → Header (auto-detect) → Column Map (fuzzy-IT) → Validate → Import
- SheetJS + Levenshtein fuzzy-match colonne italiane
- Storico variazioni prezzi (differenziante vs TUTTI i competitor IT)
- Tab "Listini Prezzi" in Fornitori.tsx
- Revenue: 7.5h/anno risparmiate per PMI, 0 errori ricopiatura

---

## 🔴 ENTERPRISE AUTOMATION — NEXT

### Gap #4 — WhatsApp Interactive Confirm/Cancel [M]
**Goal**: WA message con bottoni "Confermo / Cancello / Sposto" su appuntamento
**Status**: ✅ DONE — commit 6410b93 (sessione 41)
**Revenue**: +5-10% confirmation rate → -no-show → +€200-400/mese per PMI tipica
**Deliverables**:
- [x] booking_confirm_interactive() template (CONFERMO/CANCELLO/SPOSTO CTA)
- [x] POST /api/voice/whatsapp/send_confirmation + /register_pending endpoints
- [x] send_booking_confirm_wa Tauri command (fire-and-forget, non-blocca booking)
- [x] AppuntamentoDialog.tsx: invoke su create success
- [x] Bug fix: stato lowercase→CamelCase (Confermato/Cancellato)
- [x] Bug fix: tabella prenotazioni→appuntamenti + JOIN clienti

### Gap #6 — Tessera Fedeltà UI + Birthday WA [M]
**Goal**: Wire loyalty UI + APScheduler birthday WA (-7 giorni)
**Status**: ✅ DONE — commit bf044cb (sessione 43)
**Revenue**: +8% return rate = Pro differentiator
- LoyaltyProgress: "+ Timbro" manuale + soglia configurabile inline
- Dashboard: widget "Compleanni questa settimana" (7 gg, età, VIP, highlight oggi)
- Rust: set_loyalty_threshold + get_clienti_compleanno_settimana
- Birthday WA: APScheduler daily 9:00am già attivo in reminder_scheduler.py

---

## 🟡 PRODUCT QUALITY (dopo prima vendita)

### F04 — Schede Mancanti ✅ DONE
(già completato — vedi sezione CRITICO sopra)

### F05 — LicenseManager UI ✅ DONE (verificato sessione 49)
**Effort**: 1h
- [x] Tab Impostazioni → sezione "La mia licenza" con tier attivo, scadenza trial, upgrade CTA
- `src/components/license/LicenseManager.tsx`: 3 tab (Stato / Attiva / Piani), hooks Ed25519, TypeScript 0 errori

### F06 — Media Upload Schede Cliente
**Effort**: ~16h totale (Sprint A+B completati, Sprint C rimasto)
- [x] **Sprint A** ✅ commit 7601ca3 — Migration 030, Rust commands, MediaUploadZone/Gallery/Lightbox/ConsentModal
- [x] **Sprint B** ✅ commit 3fdd19a — BeforeAfterSlider, ProgressTimeline, VideoThumbnail, SchedaFitness+Estetica
- [x] **Sprint C** ✅ commit 847fcbe — ImageAnnotator (SVG overlay + annotation), SchedaCarrozzeria Foto tab, PDF export

### F07 — LemonSqueezy Payment Integration ✅ DONE (S62-S68)
- [x] Webhook LemonSqueezy → attivazione licenza Ed25519 offline
- [x] In-app upgrade path (Base → Pro → Clinic)
- [x] Ricevuta automatica + email conferma
- [x] E2E test 22/22 PASS | LaunchAgent boot automatico

---

## 🟠 INFRASTRUTTURA ENTERPRISE (parallelizzabile con F04-F07)

### F10 — CI/CD GitHub Actions ✅ DONE (commit e8e0072)
**Goal**: Eliminare il piano "iMac checkpoint" manuale da ogni fase GSD → -1 piano per fase.

- [x] `.github/workflows/ci.yml`: type-check + lint + pytest su ogni push/PR
- [x] Matrix: Python 3.9 (iMac runtime) + Python 3.13 (MacBook dev)
- [x] Badge stato CI nel README (punta a ci.yml)
- [x] Blocco merge: branch protection "CI Pass" job obbligatorio
- [x] `voice-agent/requirements-ci.txt`: deps slim senza torch/faiss
- **ROI**: ogni fase GSD futura risparmia ~1h di verifica manuale

### F11 — Docker Voice Agent ✅ DONE (sessione 48, commit ea24ea7)
**Goal**: Ambiente riproducibile. Elimina "funziona su iMac non su MacBook".

- [x] `Dockerfile`: python:3.9-slim, utente non-root, healthcheck, libgomp1 per ONNX
- [x] `docker-compose.yml`: bind 127.0.0.1:3002, volume mount DB Tauri, host-gateway
- [x] `requirements-docker.txt`: deps leggere (no torch/faiss/TTS/spacy)
- [x] `.dockerignore`: esclude venv, modelli, test, .env
- [x] README: sezione Docker setup 10min
- **ROI**: onboarding nuovo dev da 2h → 10min

### F12 — File Index per Codebase Grossa ✅ DONE (sessione 47, commit a59e37f)
**Goal**: Ridurre token bruciati leggendo file da 2000+ righe interi.

- [x] `voice-agent/src/_INDEX.md`: 226 righe — mappa completa metodo→riga per 3 file (7229 righe totali)
  - `booking_state_machine.py` (3506 righe) → 23 stati + tutti i _handle_* + helper
  - `orchestrator.py` (2831 righe) → 5-layer pipeline range + tutti i metodi
  - `italian_regex.py` (892 righe) → 12 gruppi pattern + costanti + classi
- [x] `scripts/update_voice_index.py`: auto-update header + conteggi righe (--check mode per CI)
- [x] `.husky/pre-commit`: step 4 — ri-genera index se voice-agent/src/*.py staged
- **ROI**: -30-40% token per sessioni che toccano voice agent

### F13 — SQLite Backup & Auto-export ✅ DONE (sessione 47, commit 63d09ba)
**Goal**: Dato locale = rischio totale se disco si guasta. PMI non fa backup.

- [x] Auto-backup giornaliero su startup (VACUUM INTO, backups/ in app_data_dir)
- [x] Retention 30 giorni: prune_old_backups() eseguito ad ogni startup
- [x] Export CSV clienti + appuntamenti on-demand (save-dialog, JOIN completo)
- [x] Alert ⚠️ in DiagnosticsPanel se backup > 7gg o assente
- [x] diagnostica badge: warning se backup > 7gg (useImpostazioniStatus)

### F14 — Security Hardening ✅ DONE (sessione 47)
**Goal**: Produzione-ready per PMI con dati sensibili.
**Effort**: 2h

- [x] Voice agent bind `0.0.0.0` → `127.0.0.1` (non esposto su rete locale)
- [x] HTTP Bridge Tauri: CorsLayer restricted to localhost origins only
- [x] Rate limiting voice endpoint (max 100 req/min sliding window per IP)
- ⚠️ Groq API key in keychain macOS: rimandato — tauri-plugin-stronghold ancora beta; chiave è in SQLite locale (accettabile per v1)

---

## 🟢 BUSINESS & SCALA (post-approvazione LemonSqueezy)

### F08 — Test Live Audio Sara T1-T5 ✅ DONE (S69)
**Effort**: 1h
- [x] T1: Gino vs Gigio — disambiguazione fonetica (fsm=disambiguating_name) ✅
- [x] T2: Soprannome VIP Gigi → waiting_surname ✅
- [x] T3: Chiusura graceful arrivederci — L1_exact ✅
- [x] T4: Flusso perfetto nuovo cliente end-to-end ✅
- [x] T5: Waitlist slot occupato ✅
- [x] Full t1_live_test.py 11/11 PASS ✅

### F15 — VoIP Integration (EHIWEB + Telnyx)
**Prerequisito**: F03 Latency < 800ms P95
**Effort**: 8-12h

- [ ] Telnyx SIP trunk setup
- [ ] EHIWEB numero italiano
- [ ] Bridge SIP → WebSocket → voice pipeline
- [ ] Test latenza end-to-end (SIP + STT + LLM + TTS + SIP) target < 2s percepiti
- **HW Note**: Intel iMac limita. Per VoIP produzione seria: valutare Mac Mini M2 (~€600)

### F16 — Landing Page Upgrade ✅ DONE (S51, commit 94d180c)
- [x] Pricing corretto: Base €497 / Pro €897 / Clinic €1.497
- [x] LemonSqueezy checkout URLs wired (8 CTA) — funnel revenue completo
- [x] Piano Enterprise → Clinic (allineato con license system)
- [x] Copy PMI-friendly: "P95 < 800ms" → "Risponde in meno di 1 secondo"
- [x] Comparison table, testimonial, ROI calc aggiornati
- [ ] TODO iMac: catturare fx_voice_agent.png (Sara UI) → .claude/cache/agents/landing-screenshots-research.md

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
  F16 → Landing upgrade ✅ DONE S51
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
