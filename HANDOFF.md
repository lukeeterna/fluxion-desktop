# FLUXION — Handoff Sessione 125 → 126 (2026-03-30)

## CTO MANDATE — NON NEGOZIABILE
> **"Tu sei il CTO. Il founder da la direzione, tu porti soluzioni."**
> **"A PROVA DI BAMBINO. L'utente PMI non sa fare nulla se non 2 click."**
> **"LASCIALI A BOCCA APERTA!"**

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.2` | Tauri dev porta 1420+3001 | Voice pipeline porta 3002

---

## COMPLETATO SESSIONE 125 — 4 COMMIT

### 1. Operator schedules in ALL 4 seed scripts
- `seed-sara-salone.sql`: 5 operatori con turni diversi (Giulia lun-sab, Marco mar-sab, Laura part-time, Luca 10-20 no sab, Paola full)
- `seed-sara-wellness.sql`: 5 operatori (Marco PT split, Elena yoga, Davide crossfit, Sara nuoto, Luca direttore)
- `seed-sara-medical.sql`: 5 medici (Rossi lun-sab, Bianchi lun/mar/gio, Verdi lun/mer/ven, Neri mar/gio/sab, Giulia inf lun-ven)
- `seed-sara-auto.sql`: 5 meccanici con turni officina (Giuseppe titolare, Andrea, Paolo gommista, Daniele elettrauto, Marta reception)

### 2. Salone clients + appointments
- 8 clienti realistici (VIP, allergie, matrimonio)
- 20 appuntamenti settimana 31 Mar - 4 Apr 2026
- Giovedì 3 aprile pieno (per test waitlist)

### 3. Bare-word service disambiguation
- **Bug**: "taglio" matchava 3 servizi (donna, uomo, bambino) e Sara li trattava come combo booking
- **Fix**: `extract_services()` rileva single-content-word con match multipli → confidence -1.0
- `ExtractionResult.ambiguous_services` propagato attraverso pipeline
- `_handle_idle()` e `_handle_waiting_service()` intercettano ambiguità → prompt "Quale preferisce?"
- WAITING_SERVICE → chiede nome prima della data se non ancora raccolto

### Test E2E verificati
```
✅ Salone "taglio" (bare word) → "Abbiamo diverse opzioni: Taglio Donna, Taglio Uomo o Taglio Bambino. Quale preferisce?"
✅ Salone "taglio donna" → diretto (no disambiguation)
✅ Salone "colore" → diretto (no disambiguation)
✅ Salone "barba" → diretto (no disambiguation)
✅ Booking E2E: disambig → servizio → nome → data → slot disponibilità → ora → conferma
✅ Slot disponibilità: orari reali dal seed (09:00, 09:30, 10:00...)
✅ type-check: 0 errori
```

---

## STATO GIT
```
Branch: master | HEAD: 9cd6881
Commits S125:
  fb69c9a feat(S125): add operator schedules to seeds + bare-word service disambiguation
  3145aca fix(S125): propagate bare-word ambiguity through extraction pipeline
  9cd6881 fix(S125): add _ambiguous_services field to BookingContext dataclass
```

---

## GSD MILESTONE v1.0 Lancio
```
Phase 9:    Screenshot Perfetti  ✅ COMPLETATO (S115)
Phase 10:   Video V7             ✅ COMPLETATO (S117)
Phase 10b:  Sara Features        ✅ COMPLETATO (S118)
Phase 10c:  Sara VoIP EHIWEB    ✅ BRIDGE + FSM FIX (S121-S122)
Phase 10d:  Sara Verticali       ✅ FAQ + SEED + ALIAS + DISAMBIG (S123-S125)
Phase 11:   Landing + Deploy     ⏳ (video YT non caricato, landing da aggiornare per verticali)
Phase 12:   Sales Agent WA       ⏳
Phase 13:   Post-Lancio          ⏳
```

---

## PROSSIMA SESSIONE 126 — PRIORITÀ

### A. KB settoriale sotto-verticali (research lanciata S125, non ancora completata)
Creare FAQ files per sotto-verticali aggiuntivi:
- Barbiere (gergo diverso da parrucchiera)
- Gommista (servizi diversi da meccanico)
- Estetista + Nail artist
- Fisioterapista
- Odontoiatra (terminologia medica)
- Palestra (abbonamenti vs sessioni)

### B. Bug rimasti
- [ ] Name extractor troppo aggressivo ("orari" interpretato come nome cliente)
- [ ] Servizio dal primo messaggio non estratto ("Sono Alessia, vorrei un colore") — service context perso dopo welcome-back
- [ ] Spostamento appuntamenti non trova appuntamenti esistenti
- [ ] Two-digit phone words (trentatre, ventuno)
- [ ] Welcome-back perde il servizio selezionato nel context (Anna → "Cosa desidera?" invece di ricordare "taglio donna")

### C. Aggiornamento Landing + Video per settore
- Landing page: aggiungere sezioni per verticali con screenshot + copy settoriale
- Video dimostrativi per-settore

### D. iMac pipeline buffering
- Riavvio pipeline DEVE usare `PYTHONUNBUFFERED=1` per vedere i print nei log
- Aggiornato nel riavvio command

---

## FILE CHIAVE SESSIONE
- `voice-agent/src/entity_extractor.py:1549-1570` — S125 bare-word ambiguity detection
- `voice-agent/src/entity_extractor.py:1841` — ambiguous_services field
- `voice-agent/src/entity_extractor.py:1968-1974` — extract_all ambiguity routing
- `voice-agent/src/booking_state_machine.py:185` — _ambiguous_services context field
- `voice-agent/src/booking_state_machine.py:1107-1118` — _update_context_from_extraction ambiguity storage
- `voice-agent/src/booking_state_machine.py:1221-1231` — _handle_idle disambiguation check
- `voice-agent/src/booking_state_machine.py:2342-2355` — _handle_waiting_service name-before-date
- `scripts/seed-sara-*.sql` — orari_lavoro per-operatore + appuntamenti

---

## NOTE TECNICHE

### Pipeline riavvio CON PYTHONUNBUFFERED
```bash
ssh imac "kill \$(lsof -ti:3002) 2>/dev/null; sleep 2; cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && DYLD_LIBRARY_PATH=lib/pjsua2 PYTHONUNBUFFERED=1 nohup /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python main.py --port 3002 > /tmp/voice-pipeline.log 2>&1 &"
```

### Disambiguation trigger conditions
- `extract_services()` returns confidence=-1.0 when:
  - Multiple services match the same bare word
  - User input has only 1 content word (after filtering filler)
- `extract_all()` routes to `ambiguous_services` instead of `services`
- FSM `_handle_idle` checks ambiguity before name
- FSM `_handle_waiting_service` checks ambiguity on service text

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 126.
PRIORITÀ:
1. KB settoriale sotto-verticali (completare research barbiere/gommista/estetista/fisioterapista)
2. Fix: welcome-back perde servizio selezionato
3. Fix: name extractor troppo aggressivo
4. Aggiornamento landing per verticali
```
