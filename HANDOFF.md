# FLUXION — Handoff Sessione 125 → 126 (2026-03-31)

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

## COMPLETATO SESSIONE 125 — 6 COMMIT

### 1. Operator schedules in ALL 4 seed scripts
- Turni per-operatore realistici per salone (5 op), wellness (5), medical (5), auto (5)
- 8 clienti + 20 appuntamenti settimana nel salone seed
- Giovedì 3 aprile pieno (test waitlist)

### 2. Bare-word service disambiguation
- "taglio" → "Abbiamo diverse opzioni: Taglio Donna, Taglio Uomo o Taglio Bambino. Quale preferisce?"
- confidence -1.0 per match ambigui, propagato via ExtractionResult.ambiguous_services
- FSM _handle_idle intercetta ambiguità prima del nome

### 3. Welcome-back preserva servizio
- Tutti i 4 path welcome-back (exact, nickname, disambiguation) ora controllano se servizio è nel context
- "Bentornato Anna! Taglio Donna, per quale giorno?" (skip WAITING_SERVICE)

### 4. DB path priority fix
- File vuoto `./fluxion.db` nel voice-agent dir veniva trovato prima del vero Tauri DB
- Riordinato: env var → macOS App Support → Windows → project root → cwd
- Aggiunto check `os.path.getsize() > 0`

### 5. KB settoriale research (subagenti completati, file in scrittura)
- Barbiere: servizi+prezzi+gergo+FAQ
- Gommista: servizi stagionali+FAQ
- Estetista/Nail: 24 servizi+FAQ
- Fisioterapista: terminologia medica+prescrizioni+FAQ
- Odontoiatra: urgenze+prezzi+FAQ
- Palestra: gap analysis vs seed esistente

### Test E2E verificati (flusso 6 step)
```
✅ "Vorrei un taglio" → disambiguation (3 opzioni)
✅ "Taglio donna" → "Mi dice il suo nome?"
✅ "Anna Colombo" → "Bentornato Anna! Taglio Donna, per quale giorno?" (VIP + servizio preservato)
✅ "Mercoledì" → slot disponibilità (09:00, 09:30, 10:00...)
✅ "Alle 10" → "Riepilogo: Taglio Donna, mercoledì 1 aprile, alle 10:00. Conferma?"
✅ "Sì" → rileva conflitto (slot occupato da seed) → propone alternative
✅ Servizi specifici ("colore", "barba") → no disambiguation, flusso diretto
✅ type-check: 0 errori
```

---

## STATO GIT
```
Branch: master | HEAD: 127ca52
Commits S125:
  fb69c9a feat(S125): add operator schedules to seeds + bare-word service disambiguation
  3145aca fix(S125): propagate bare-word ambiguity through extraction pipeline
  9cd6881 fix(S125): add _ambiguous_services field to BookingContext dataclass
  6e41fc2 docs(S125): update HANDOFF for session 126 handoff
  446b878 fix(S125): preserve service context through welcome-back flow
  127ca52 fix(S125): fix DB path priority — Tauri DB before empty relative file
```

---

## GSD MILESTONE v1.0 Lancio
```
Phase 10d: Sara Verticali       ✅ FAQ + SEED + ALIAS + DISAMBIG + WELCOME-BACK (S123-S125)
Phase 11:  Landing + Deploy     ⏳ (aggiornare per verticali + video per settore)
Phase 12:  Sales Agent WA       ⏳
Phase 13:  Post-Lancio          ⏳
```

---

## PROSSIMA SESSIONE 126 — PRIORITÀ

### A. KB settoriale sotto-verticali
- File research in `.claude/cache/agents/kb-settoriale-*.md` (subagenti completati S125)
- Creare seed SQL per nuovi sotto-verticali (barbiere, gommista, estetista, fisioterapista, odontoiatra)
- Creare FAQ JSON per nuovi sotto-verticali
- Aggiungere sinonimi in VERTICAL_SERVICES per i nuovi servizi

### B. Bug rimasti voce
- [ ] Name extractor troppo aggressivo ("orari" interpretato come nome)
- [ ] "Sono Alessia, vorrei un colore" — service extractable dal primo messaggio non usato in IDLE
- [ ] Two-digit phone words (trentatre, ventuno)
- [ ] Spostamento appuntamenti non trova appuntamenti esistenti

### C. Aggiornamento Landing + Video per settore
- Landing page: sezioni per verticali con screenshot + copy settoriale
- Video dimostrativi per-settore (parrucchiere, palestra, studio medico, officina)

---

## FILE CHIAVE SESSIONE 125
- `voice-agent/src/entity_extractor.py:1549-1570` — bare-word ambiguity detection
- `voice-agent/src/entity_extractor.py:1841` — ambiguous_services field
- `voice-agent/src/booking_state_machine.py:185` — _ambiguous_services context field
- `voice-agent/src/booking_state_machine.py:1221-1231` — _handle_idle disambiguation
- `voice-agent/src/booking_state_machine.py:1522-1535` — welcome-back preserva servizio (4 path)
- `voice-agent/src/booking_state_machine.py:1846-1858` — DB path priority fix
- `scripts/seed-sara-*.sql` — orari_lavoro per-operatore + appuntamenti

---

## NOTE TECNICHE

### Pipeline riavvio (SEMPRE CON PYTHONUNBUFFERED)
```bash
ssh imac "kill \$(lsof -ti:3002) 2>/dev/null; sleep 2; cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && DYLD_LIBRARY_PATH=lib/pjsua2 PYTHONUNBUFFERED=1 nohup /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python main.py --port 3002 > /tmp/voice-pipeline.log 2>&1 &"
```

### Disambiguation trigger conditions
- `extract_services()` returns confidence=-1.0 when:
  - Multiple services match the same bare word
  - User input has only 1 content word (after filtering filler)
- `extract_all()` routes to `ambiguous_services` instead of `services`
- FSM `_handle_idle` checks ambiguity before name
- Welcome-back: se servizio già nel context → skip WAITING_SERVICE

### DB path discovery (FSM)
- Priority: FLUXION_DB_PATH env → macOS App Support → Windows AppData → project root → cwd
- Skip files with size == 0
- **NOTA**: file vuoto `voice-agent/fluxion.db` esiste su iMac, NON eliminare ma non usare

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 126.
PRIORITÀ:
1. KB settoriale: creare seed SQL + FAQ JSON per nuovi sotto-verticali
2. Fix: name extractor troppo aggressivo ("orari" → nome)
3. Fix: service dal primo messaggio ("Sono Alessia, vorrei un colore")
4. Aggiornamento landing per verticali
```
