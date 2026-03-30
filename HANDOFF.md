# FLUXION — Handoff Sessione 123 → 124 (2026-03-30)

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

## COMPLETATO SESSIONE 123 — 5 COMMIT, 6 BUG FIX CRITICO

### Bug fix applicati
1. **FAQ prezzi routing** — `_has_booking_words` non overrida più `_is_info`. "Quanto costa un taglio?" → risponde con prezzi
2. **Special command word boundaries** — "persona" non matcha più "personal" (regex `\bpersona\b`)
3. **INFO regex always-check** — LLM che classifica FAQ come PRENOTAZIONE corretto dal regex (`quanto costa` = INFO)
4. **Vertical config loading** — `categoria_attivita` + `micro_categoria` letti da DB (HTTP Bridge + SQLite)
5. **FAQ variable substitution** — Prezzi servizi popolati dinamicamente dal DB (`_service_prices` dict)
6. **set_vertical reload** — Cambio verticale ricarica servizi dal DB e ricostruisce FAQ con variabili

### Seed scripts creati (4 verticali)
- `scripts/seed-sara-salone.sql` — 14 servizi, 5 operatori, 3 pacchetti
- `scripts/seed-sara-wellness.sql` — 16 servizi, 5 operatori, 8 clienti, 23 appuntamenti, 4 pacchetti
- `scripts/seed-sara-medical.sql` — 17 servizi, 5 medici, 8 pazienti, 20 appuntamenti, 4 pacchetti
- `scripts/seed-sara-auto.sql` — 15 servizi, 5 meccanici, 8 clienti, 20 appuntamenti, 4 pacchetti

### Test matrix S123 (9/10 PASS)
```
✅ Salone FAQ taglio → "€35 donna, €18 uomo" (da DB)
✅ Salone FAQ orari → "Lun-Sab 9:00-19:00"
✅ Salone booking → chiede nome
✅ Salone cliente esistente → "Bentornato Anna!"
✅ Wellness FAQ PT → "€45 per 60 minuti"
✅ Wellness booking → chiede nome
✅ Auto FAQ tagliando → "Tagliando Base €120 / Completo €220"
✅ Auto booking → chiede nome
✅ Medical booking → chiede nome
⚠️ Medical FAQ visita → variabili {{PREZZO_VISITA_GENERALE}} non sostituite (mismatch chiave)
```

---

## STATO GIT
```
Branch: master | HEAD: cb1a835
type-check: 0 errori
voice pipeline: ATTIVO con VoIP
Commits S123: 5 fix Sara FAQ routing + vertical config + seed scripts
```

---

## GSD MILESTONE v1.0 Lancio
```
Phase 9:    Screenshot Perfetti  ✅ COMPLETATO (S115)
Phase 10:   Video V7             ✅ COMPLETATO (S117)
Phase 10b:  Sara Features        ✅ COMPLETATO (S118)
Phase 10c:  Sara VoIP EHIWEB    ✅ BRIDGE + FSM FIX (S121-S122)
Phase 10d:  Sara Verticali       ✅ FAQ ROUTING + SEED (S123)
Phase 11:   Landing + Deploy     ⏳ (video YT non caricato, landing da aggiornare per verticali)
Phase 12:   Sales Agent WA       ⏳
Phase 13:   Post-Lancio          ⏳
```

---

## PROSSIMA SESSIONE 124 — PRIORITÀ

### A. Fix sostituzione variabili FAQ (CRITICO)
La chiave auto-generata dal DB (`PREZZO_VISITA_MEDICA_GENERALE`) non matcha la chiave nel file FAQ (`PREZZO_VISITA_GENERALE`). Serve:
- Alias generator: per ogni servizio, generare anche varianti corte (prima+ultima parola, prima parola sola)
- Oppure: aggiornare i file FAQ per usare le chiavi generate automaticamente

### B. Test booking end-to-end per ogni verticale
1 booking COMPLETO per ogni verticale (nome→cognome→telefono→servizio→data→ora→conferma→chiusura):
- Salone: taglio donna
- Wellness: lezione yoga
- Medical: visita dentista
- Auto: tagliando

### C. Arricchimento KB settoriale + sotto-verticali
Deep research CoVe 2026 per:
- FAQ specifiche per sotto-verticale (odontoiatra, gommista, fisioterapista, barbiere, estetista, etc.)
- Gergo settoriale (terminologia specifica che Sara deve capire)
- Risposte naturali e informate per ogni sotto-settore

### D. Aggiornamento Landing + Video per settore (NUOVA DIREZIONE)
- Landing page: aggiungere sezioni per verticali (ogni settore con screenshot + copy specifico)
- Video: creare video dimostrativi per-settore (parrucchiere, officina, studio medico, palestra)
- Tassonomia verticali: 6 macro × 33 micro già in `setup.ts` (MICRO_CATEGORIE)

### E. Bug rimasti da S122
- [ ] Spostamento non trova appuntamenti
- [ ] Two-digit phone words (trentatre, ventuno)
- [ ] Servizio dal primo messaggio non estratto ("Sono Alessia, vorrei un colore")

---

## FILE CHIAVE SESSIONE
- `voice-agent/src/orchestrator.py` — FAQ routing, INFO regex, set_vertical, service_prices
- `voice-agent/main.py` — config loading (categoria_attivita, micro_categoria)
- `scripts/seed-sara-*.sql` — seed scripts per 4 verticali
- `voice-agent/data/faq_*.json` — FAQ per verticale (25 entry ciascuno)
- `src/types/setup.ts` — tassonomia MICRO_CATEGORIE (6 macro × 33 micro)

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 124.
PRIORITÀ:
1. Fix sostituzione variabili FAQ (alias generator per chiavi servizi)
2. Test booking end-to-end per ogni verticale (nome→servizio→data→ora→conferma)
3. Deep research CoVe 2026: KB settoriale per ogni sotto-verticale
4. Aggiornamento landing per verticali + video per-settore
```
