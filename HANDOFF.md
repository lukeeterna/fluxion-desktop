# FLUXION — Handoff Sessione 118 → 119 (2026-03-27)

## CTO MANDATE — NON NEGOZIABILE
> **"Tu sei il CTO. Il founder da la direzione, tu porti soluzioni."**
> **"A PROVA DI BAMBINO. L'utente PMI non sa fare nulla se non 2 click."**
> **"LASCIALI A BOCCA APERTA!"**
> **"Capire cosa ho → capire cosa è possibile → definire insieme cosa fare. MAI codice come secondo step."**

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.2` | Tauri dev porta 1420+3001 | Voice pipeline porta 3002

---

## COMPLETATO SESSIONE 118

### Sara: 2 nuove feature implementate + 4 gia' esistenti confermate
```
NUOVO:
1. DISDICI + RIPRENOTA — dopo cancel success, Sara propone rebook
   - "Appuntamento cancellato. Vuole che le trovi un altro orario?"
   - Si → booking con servizio pre-compilato (FSM in WAITING_DATE)
   - No → chiusura gentile
   - Fix: bypass cortesia/conferma durante cancel/rebook flow

2. PROPOSTA PACCHETTI — dopo booking confermato, Sara propone pacchetti
   - Query SQLite pacchetti attivi, check se cliente non li ha gia'
   - "A proposito, abbiamo il pacchetto Festa del Papa': 3 sedute a 89 euro..."
   - Si → registra in clienti_pacchetti come "proposto", operatore contatta
   - No → chiusura gentile
   - Regola fondatore: pacchetti CREATI da operatore, NON auto-proposti

GIA' ESISTENTI (verificato in S118):
3. RESCHEDULE — flusso completo L1+L2.5 (spostamento appuntamenti)
4. WAITLIST — FSM + scheduler 5min + WA notify (priorita' VIP)
5. PROMEMORIA WA — 24h/1h ogni 15min (reminder_scheduler.py)
6. AUGURI COMPLEANNO WA — daily 9:00am (check_and_send_birthdays)
```

### Fix tecnici S118
- cortesia/conferma/rifiuto L1 ora skippato quando cancel/reschedule/rebook/package flow attivo
- Booking SM skippato quando appointment management flow attivo
- Cancel flow: name resolution con nome+cognome (filtra client-side)

### Test
- 574 PASS / 1 FAIL pre-esistente (test_abbonamento palestra — bug NoneType)
- TypeScript: 0 errori
- Live test: 6 scenari su iMac (cancel+rebook accept, cancel+rebook decline, booking+package accept, booking+package decline)

### Memory salvata
- `feedback_pacchetti_operator_driven.md` — pacchetti CREATI da operatore, NON auto-proposti

---

## DA FARE S119

### Phase 11: Landing + Deploy (GSD Milestone v1.0)
- Embed video YouTube nella landing
- VideoObject JSON-LD schema
- Aggiornare screenshot landing con quelli nuovi
- Test flusso acquisto end-to-end
- Deploy CF Pages --branch=production
- Test mobile/tablet/desktop

### Oppure: Sales Agent WA (Phase 12)
- Scraping PagineGialle
- WhatsApp Web automation (Selenium)
- Dashboard leads

### Bug noto: test_abbonamento palestra
- `AttributeError: 'NoneType' object has no attribute 'is_solito'`
- booking_state_machine.py:2171

---

## STATO GIT
```
Branch: master | HEAD: 08ccd97
type-check: 0 errori
voice tests: 574 PASS / 1 FAIL (pre-existing)
```

---

## GSD MILESTONE v1.0 Lancio
```
Phase 9:  Screenshot Perfetti  ✅ COMPLETATO (S115)
Phase 10: Video V7             ✅ COMPLETATO (S117)
Phase 10b: Sara Features       ✅ COMPLETATO (S118) — cancel+rebook, pacchetti
Phase 11: Landing + Deploy     ⏳
Phase 12: Sales Agent WA       ⏳
Phase 13: Post-Lancio          ⏳
```

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 119.
PRIORITA': Phase 11 — Landing definitiva con video YouTube embeddato + deploy production.
Oppure: fix bug test_abbonamento palestra + push origin master.
Voice agent su iMac (192.168.1.2:3002).
```
