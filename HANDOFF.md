# FLUXION — Handoff Sessione 96 → 97 (2026-03-19)

## CTO MANDATE — NON NEGOZIABILE
> **"Sara deve essere un sistema di prenotazioni PROFESSIONALE world-class. Le feature indicate sono il MINIMO — DEEP RESEARCH CoVe 2026 per trovare TUTTO ciò che serve e implementarlo. ZERO improvvisazione, SOLO dati DB."**

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
Branch: master | HEAD: c20e001 (pushato ✅)
iMac: sincronizzato ✅ | Pipeline: ATTIVA ✅ (127.0.0.1:3002)
type-check: 0 errori
Test: 1975 PASS / 16 FAIL pre-esistenti / 46 skipped
```

---

## COMPLETATO SESSIONE 96

### Commit c20e001 — 4 P0 Blocker Sistema Prenotazioni
| # | Feature | Stato |
|---|---------|-------|
| P0-1 | buffer_minuti in slot availability + booking creation | ✅ Verificato iMac |
| P0-2 | Blocchi orario operatore (migration 034 + availability check) | ✅ 28 test |
| P0-3 | Multi-servizio combo (somma durate, gruppo_id) | ✅ Verificato iMac |
| P0-4 | "Il solito" — detect_solito() + lookup storico cliente | ✅ 15 pattern test |

### Dettagli Tecnici
- **P0-1**: `orchestrator.py` — query `SELECT durata_minuti, COALESCE(buffer_minuti, 0)` sia in availability check che in booking creation. Slot totale = durata + buffer.
- **P0-2**: `034_blocchi_orario.sql` — tabella con ricorrente/one-shot, giorno_settimana/data_specifica. Check in `_check_slot_availability_sqlite_fallback()` e alternatives. Fail-open se tabella non esiste.
- **P0-3**: `_check_slot_availability_sqlite_fallback()` accetta `services: List[str]`, somma tutte le durate+buffer. `_create_booking_sqlite_fallback()` crea N appuntamenti contigui con `note='gruppo:{id}'`.
- **P0-4**: `entity_extractor.py` — `detect_solito()` regex 12+ pattern. `ExtractionResult.is_solito`. FSM `WAITING_SERVICE` intercetta e richiede `lookup_type="solito"`. Orchestrator `_lookup_solito()` query ultimi 5 appuntamenti, pre-fill context.

---

## DA FARE S97

### Priorità 1: Test Live Voce Reale
- Testare tutti i P0 con voce reale su iMac
- Verificare flow: "il solito" → lookup → proposta → conferma
- Verificare: slot bloccato da pausa pranzo → slot alternativo
- Verificare: "taglio e piega" → durata sommata → slot corretto

### Priorità 2: Sprint P1 (post-lancio)
Deep research completata (`.claude/cache/agents/f19-booking-system-deep-research-2026.md`):
1. Smart gap elimination (2-3gg)
2. Appuntamenti ricorrenti (4-5gg)
3. Operatore preferito (2gg)
4. No-show tracking + penalità (3gg)
5. Waitlist notifica automatica (3-4gg)

### Cleanup
- [ ] OpenRouter cleanup (3x empty response)
- [ ] Test voce reale con P0 features

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
Leggi HANDOFF.md. Sessione 97. P0 blocker completati (S96).
Priorità: test live voce reale dei 4 P0 su iMac + inizio sprint P1.
Pipeline iMac ATTIVA (127.0.0.1:3002).
DIRETTIVE: SOLO dati DB, deep research PRIMA, code reviewer dopo.
```
