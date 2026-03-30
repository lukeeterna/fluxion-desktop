# FLUXION — Handoff Sessione 124 → 125 (2026-03-30)

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

## COMPLETATO SESSIONE 124 — 3 COMMIT, 3 FIX CRITICI

### Fix applicati
1. **FAQ alias generator** — DB service "Visita Medica Generale" genera chiave `PREZZO_VISITA_MEDICA_GENERALE`, ma FAQ usa `PREZZO_VISITA_GENERALE`. Alias generator crea varianti corte (strip modifiers, first+last word, first word only). Funziona per medical, auto, salone.
2. **Seed SQL genere column** — Rimosso `genere` da tutti e 4 i seed scripts (colonna non esiste in DB schema)
3. **Service matching greedy fix** — Phase 2 fuzzy matching re-aggiungeva servizi che condividevano sinonimi single-word con servizi già matchati. "taglio donna" → 1 servizio (era 4), "pulizia denti" → 1 (era 3)

### Test matrix S124
```
✅ Medical FAQ "quanto costa visita?" → "€80" (PREZZO_VISITA_GENERALE resolved)
✅ Medical FAQ "quanto costa ecografia?" → "€70" (PREZZO_ECOGRAFIA resolved)
✅ Auto FAQ "quanto costa revisione?" → "€79" (PREZZO_REVISIONE resolved)
✅ Auto FAQ "quanto costa tagliando?" → "Base €120 / Completo €220"
✅ Salone FAQ "taglio donna?" → "€35"
✅ Salone service match "taglio donna" → 1 servizio (FIX: era 4)
✅ Salone booking E2E: nome→servizio→data→ora→conferma (FSM completo)
✅ Medical booking E2E: nome→servizio→data→ora→conferma (FSM completo)
⚠️ Slots non disponibili al momento conferma (seed data non ha schedule aperti per date future)
```

---

## STATO GIT
```
Branch: master | HEAD: 4792a25
type-check: 0 errori
voice pipeline: ATTIVO con VoIP
Commits S124: 3 fix (alias generator + seed genere + service match)
```

---

## GSD MILESTONE v1.0 Lancio
```
Phase 9:    Screenshot Perfetti  ✅ COMPLETATO (S115)
Phase 10:   Video V7             ✅ COMPLETATO (S117)
Phase 10b:  Sara Features        ✅ COMPLETATO (S118)
Phase 10c:  Sara VoIP EHIWEB    ✅ BRIDGE + FSM FIX (S121-S122)
Phase 10d:  Sara Verticali       ✅ FAQ + SEED + ALIAS (S123-S124)
Phase 11:   Landing + Deploy     ⏳ (video YT non caricato, landing da aggiornare per verticali)
Phase 12:   Sales Agent WA       ⏳
Phase 13:   Post-Lancio          ⏳
```

---

## PROSSIMA SESSIONE 125 — PRIORITÀ

### A. Deep research KB settoriale per sotto-verticali
CoVe 2026 per FAQ specifiche:
- Barbiere vs parrucchiera (gergo diverso)
- Gommista vs meccanico (servizi diversi)
- Fisioterapista vs odontoiatra (terminologia medica)
- Estetista vs nail artist (trattamenti specifici)
Creare FAQ files per almeno 4-6 sotto-verticali aggiuntivi.

### B. Bug rimasti
- [ ] Bare "taglio" matcha 3 servizi (ambiguo → Sara dovrebbe chiedere "donna, uomo o bambino?")
- [ ] Name extractor troppo aggressivo ("orari" interpretato come nome cliente)
- [ ] Servizio dal primo messaggio non estratto ("Sono Alessia, vorrei un colore")
- [ ] Spostamento appuntamenti non trova appuntamenti esistenti
- [ ] Two-digit phone words (trentatre, ventuno)

### C. Operatori schedule per booking E2E completo
I seed scripts hanno operatori ma NON hanno turni/disponibilità. Per completare il booking serve:
- Inserire `orari_lavoro` per ogni operatore nei seed
- O creare slot di disponibilità aperti per date future

### D. Aggiornamento Landing + Video per settore (da S123)
- Landing page: aggiungere sezioni per verticali con screenshot + copy settoriale
- Video dimostrativi per-settore (parrucchiere, officina, studio medico, palestra)

---

## FILE CHIAVE SESSIONE
- `voice-agent/src/orchestrator.py:2288-2320` — alias generator per FAQ variables
- `voice-agent/src/entity_extractor.py:1549-1575` — consumed words in service matching
- `voice-agent/src/vertical_loader.py:68-76` — unresolved variable logging
- `scripts/seed-sara-*.sql` — seed scripts senza colonna genere

---

## NOTE TECNICHE

### DB Path iMac
- **Tauri app DB**: `/Users/gianlucadistasi/Library/Application Support/com.fluxion.desktop/fluxion.db`
- **Dev DB**: `/Volumes/MacSSD - Dati/FLUXION/src-tauri/fluxion.db`
- Pipeline usa HTTP Bridge (porta 3001) prima, poi fallback SQLite
- Per forzare DB specifico: `FLUXION_DB_PATH=... python main.py`

### Alias generator strategy
Per ogni servizio DB, genera:
1. Full key: `PREZZO_VISITA_MEDICA_GENERALE`
2. Strip modifiers (medico/a, generale, ministeriale, base, etc.): `PREZZO_VISITA`
3. First+last word (3+ words): `PREZZO_VISITA_GENERALE`
4. First word only: `PREZZO_VISITA`
Non sovrascrive chiavi esistenti (first-come wins).

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 125.
PRIORITÀ:
1. Deep research KB settoriale (barbiere, gommista, estetista, fisioterapista, odontoiatra)
2. Fix bare-word service disambiguation ("taglio" → chiedi quale tipo)
3. Operatori schedule nei seed per booking E2E completo
4. Aggiornamento landing per verticali + video per-settore
```
