# FLUXION — Handoff Sessione 95 → 96 (2026-03-19)

## CTO MANDATE — NON NEGOZIABILE
> **"Sara deve essere un sistema di prenotazioni PROFESSIONALE world-class. Le feature indicate sono il MINIMO — DEEP RESEARCH CoVe 2026 per trovare TUTTO ciò che serve e implementarlo. ZERO improvvisazione, SOLO dati DB."**

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.2` | Voice pipeline: porta 3002 | **iMac DISPONIBILE + PIPELINE ATTIVA**
**MacBook**: Playwright, Vite (1420), ffmpeg 8.0, Edge-TTS (pip), wrangler 3.22
**Tauri dev su iMac**: `bash -l -c 'cd "/Volumes/MacSSD - Dati/fluxion" && npm run tauri dev'`

---

## STATO GIT
```
Branch: master | HEAD: 9d6dad9 (pushato ✅)
iMac: sincronizzato ✅ | Pipeline: ATTIVA ✅
type-check: 0 errori
Test: 1949 PASS / 3 FAIL pre-esistenti / 46 skipped
```

---

## COMPLETATO SESSIONE 95

### Commit e9d6a83 — F19 Sara DB-Grounded (9 fix P0/P1)
| # | Fix | Stato |
|---|-----|-------|
| 1 | Servizi dinamici dal DB (non più hardcodati) | ✅ Verificato iMac |
| 2 | Operatori dal DB + SQLite fallback + validazione entity | ✅ |
| 3 | Cancellazione protetta in CONFIRMING | ✅ Verificato iMac |
| 4 | FSM Backtracking (correzioni cliente) | ✅ |
| 5 | Waitlist SQLite fallback + VIP priority | ✅ |
| 6 | Orari apertura dal DB (non 9-18 hardcodato) | ✅ |
| 7 | Copy elegante (pool varianti) | ✅ |
| 8 | STT anti-allucinazione | ✅ |
| 9 | Barge-in backend (VAD event) | ✅ |

### Deep Research CoVe 2026 — 19 Feature Mancanti Identificate
**File**: `.claude/cache/agents/f19-booking-system-deep-research-2026.md`
**Competitor analizzati**: Fresha, Mindbody, Jane App, Vagaro, Acuity, Square, Retell AI, Vapi, BookingBee AI, SpaVoices, +6 altri

---

## 🔴 DA FARE S96 — 4 P0 BLOCKER

### Sprint P0 (8-10 giorni totali)

#### P0-1: Buffer automatico tra servizi (1 giorno)
- `buffer_minuti` esiste in tabella `servizi` ma Sara NON lo usa nel calcolo slot
- **Fix**: sommare `durata_minuti + buffer_minuti` nella query disponibilità
- **File**: `orchestrator.py` → `_check_slot_availability_sqlite_fallback()`
- **AC**: Servizio con buffer 15min → slot proposto include il buffer

#### P0-2: Pausa pranzo / blocco fasce operatore (2 giorni)
- Nessun concetto di fasce bloccate intra-giornaliere per singolo operatore
- **Implementazione**: migration `blocchi_orario` (operatore_id, giorno, ora_inizio, ora_fine, ricorrente)
- Sara verifica blocchi PRIMA di proporre slot
- **AC**: Operatore con pausa 13-14 → Sara non propone slot in quella fascia

#### P0-3: Multi-servizio combo con durata sommata (3-4 giorni)
- Regex `extract_multi_services` esiste ma FSM gestisce 1 servizio alla volta
- "Taglio e piega" deve calcolare durata totale (30+40=70min) e trovare slot unico
- **Implementazione**: FSM `WAITING_SERVICE` → somma durate + buffers, cerca slot contiguo
- **AC**: "Taglio e piega" → propone slot da 70min con buffer

#### P0-4: "Il solito" — servizio abituale da storico (2-3 giorni)
- Nessun competitor vocale in italiano lo fa → differenziante WOW
- Entity extractor: "il solito", "come l'ultima volta", "come sempre"
- Query: ultimi 3 appuntamenti → estrai servizio, operatore, giorno/ora più frequente
- Sara: "L'ultima volta ha fatto taglio con Marco il giovedì alle 15. Confermo?"
- **AC**: Cliente abituale dice "il solito" → Sara propone correttamente

---

## DIRETTIVE CTO (NON NEGOZIABILI)

1. **SARA = SISTEMA PRENOTAZIONI PROFESSIONALE** — deep research per TUTTO
2. **SARA = SOLO DATI DB** — zero improvvisazione, zero entità inventate
3. **SEMPRE code reviewer** dopo ogni implementazione significativa
4. **ZERO COSTI** per licensing, protezione, infra
5. **SEMPRE 1 nicchia** — una PMI = un'attività
6. **Deep research CoVe 2026** — SEMPRE subagenti PRIMA di implementare
7. **Le feature indicate sono il MINIMO** — ricercare e implementare TUTTO il gold standard

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 96. PRIORITÀ: 4 P0 blocker sistema prenotazioni Sara.
Deep research COMPLETATA (S95): `.claude/cache/agents/f19-booking-system-deep-research-2026.md`
4 P0: (1) buffer_minuti nei slot, (2) pausa pranzo operatore con migration DB,
(3) multi-servizio combo durata sommata, (4) "il solito" da storico cliente.
Pipeline iMac ATTIVA. Implementa in ordine, commit atomici, test su iMac.
DIRETTIVE: SOLO dati DB, deep research PRIMA, code reviewer dopo.
```
