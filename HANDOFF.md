# FLUXION — Handoff Sessione 126 → 127 (2026-03-31)

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

## COMPLETATO SESSIONE 126 — 4 COMMIT

### 1. Bug fix: Name extractor troppo aggressivo
- "orari" was extracted as person name → blacklisted in NAME_BLACKLIST
- Extended _NON_NAMES_EX in _handle_waiting_name with articles, FAQ words, service words
- Changed _handle_idle to use `extracted.name is not None` instead of raw regex
- E2E verified: "orari" → not name, "prezzi" → FAQ, "Marco" → name ✅

### 2. Bug fix: Service from first message lost
- "Sono Alessia, vorrei un colore" — service was extracted but lost after registration
- Fixed orchestrator.py DB lookup (existing client): check context.service → skip to WAITING_DATE
- Fixed _handle_confirming_phone (new client): check service → skip to WAITING_DATE
- E2E verified:
  - Existing client: "Bentornato Federica! Colore, per quale giorno?" ✅
  - New client: Registration → "Colore, per quale giorno?" ✅

### 3. Tassonomia PMI italiane completa
- Deep research: 8 macro, 49 micro-categorie, ~467.000 attività appointment-based
- New macros: pet (toelettatura, veterinario, pensione, dog_sitter), formazione (5 sub)
- New micros: logopedista, dermatologo, makeup_artist, autolavaggio
- setup.ts: Zod schema + MACRO_CATEGORIE + MICRO_CATEGORIE updated (was 6/38, now 8/49)
- Research: `.claude/cache/agents/tassonomia-pmi-italiane-2026.md` (1247 lines)
- Competitor: `.claude/cache/agents/competitor-analysis-verticali-2026.md` (743 lines)

### 4. 6 new sub-vertical seeds + FAQs + infrastructure
- **Seeds** (all complete with 11 tables each):
  - `seed-sara-barbiere.sql` (287 lines)
  - `seed-sara-beauty.sql` (260 lines)
  - `seed-sara-odontoiatra.sql` (259 lines)
  - `seed-sara-fisioterapia.sql` (221 lines)
  - `seed-sara-gommista.sql` (256 lines)
  - `seed-sara-toelettatura.sql` (274 lines)
- **FAQs**: 6 files in both verticals/ and data/ directories (10 FAQs each)
- **Migration 035**: schede_pet table (animale dati, salute, toelettatura)
- **SchedaPet type**: Zod schema + union type + labels
- **vertical_loader.py**: VERTICAL_FAQ_MAP for all new sub-verticals
- **vertical_manager.py**: VerticalType enum expanded (6 new)
- **orchestrator.py**: VALID set for set_vertical() expanded
- E2E verified: barbiere seed loaded → booking + FAQ working ✅

---

## STATO GIT
```
Branch: master | HEAD: c9482b5
Commits S126:
  972e70c fix(S126): name extractor blacklist + service-from-first-message flow
  c9482b5 feat(S126): add Pet/Formazione macro-categories + 6 new sub-verticals
```

---

## GSD MILESTONE v1.0 Lancio
```
Phase 10d: Sara Verticali       ✅ FAQ + SEED + ALIAS + DISAMBIG + WELCOME-BACK + NEW-VERTICALS (S123-S126)
Phase 11:  Landing + Deploy     ⏳ (aggiornare per verticali + video per settore)
Phase 12:  Sales Agent WA       ⏳
Phase 13:  Post-Lancio          ⏳
```

---

## PROSSIMA SESSIONE 127 — PRIORITÀ

### A. FAQ Variable Substitution for new verticals
- The [PREZZO_BARBA] variables in new FAQ files aren't being substituted
- Need to extend S124 alias generator in orchestrator.py to cover new service names
- Test each vertical's FAQ with proper price substitution

### B. Remaining voice bugs
- [ ] Two-digit phone words (trentatre, ventuno)
- [ ] Spostamento appuntamenti non trova appuntamenti esistenti
- [ ] "Quali sono gli orari?" routes to L2 booking instead of L3 FAQ (intent routing issue)

### C. Sprint 1 tasks (ROADMAP_REMAINING.md)
- [ ] Allineare prezzi Rust 199/399 → 497/897
- [ ] Wire phone-home nell'app
- [ ] Seed dati demo su iMac con fatturato bello
- [ ] Screenshot perfetti

### D. Landing verticali
- Sezioni dedicate con copy per ogni macro-verticale
- Video dimostrativi per-settore

---

## FILE CHIAVE SESSIONE 126
- `voice-agent/src/entity_extractor.py:985-1065` — NAME_BLACKLIST (expanded S126)
- `voice-agent/src/booking_state_machine.py:1244-1250` — _handle_idle uses extracted.name
- `voice-agent/src/booking_state_machine.py:1446-1468` — _NON_NAMES_EX expanded
- `voice-agent/src/booking_state_machine.py:3777-3810` — _handle_confirming_phone service check
- `voice-agent/src/orchestrator.py:1616-1625` — DB lookup service skip to WAITING_DATE
- `src/types/setup.ts:35,65-120,115-180` — 8 macro, 49 micro categories
- `src/types/scheda-cliente.ts:480-520` — SchedaPet schema + union
- `scripts/seed-sara-{barbiere,beauty,odontoiatra,fisioterapia,gommista,toelettatura}.sql`
- `voice-agent/data/faq_{barbiere,beauty,odontoiatra,fisioterapia,gommista,toelettatura}.json`
- `voice-agent/src/vertical_loader.py:28-45` — VERTICAL_FAQ_MAP expanded
- `src-tauri/migrations/035_scheda_pet.sql` — Pet scheda table

---

## NOTE TECNICHE

### Pipeline riavvio (SEMPRE CON PYTHONUNBUFFERED)
```bash
ssh imac "kill \$(lsof -ti:3002) 2>/dev/null; sleep 2; cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && DYLD_LIBRARY_PATH=lib/pjsua2 PYTHONUNBUFFERED=1 nohup /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python main.py --port 3002 > /tmp/voice-pipeline.log 2>&1 &"
```

### Tassonomia PMI Italiane (S126)
```
8 Macro → 49 Micro → ~467.000 attività
Hair: 6 micro, ~135K (ALTISSIMA TAM)
Beauty: 7 micro, ~55K (ALTISSIMA)
Medico: 10 micro, ~95K (ALTA)
Auto: 7 micro, ~85K (ALTA)
Wellness: 6 micro, ~12K (MEDIA)
Pet: 4 micro, ~15K (MEDIA)
Formazione: 5 micro, ~15K (MEDIA)
Professionale: 5 micro, ~55K (BASSA)
```

### Seed files (10 total)
```
4 original: salone, wellness, medical, auto
6 new S126: barbiere, beauty, odontoiatra, fisioterapia, gommista, toelettatura
Each: 11 tables (impostazioni, servizi, operatori, orari_lavoro, clienti,
      appuntamenti, pacchetti, suppliers, fatture, fatture_righe, incassi)
```

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 127.
PRIORITÀ:
1. FAQ variable substitution per nuovi sotto-verticali
2. Fix intent routing: "orari" → FAQ non booking
3. Sprint 1 ROADMAP: prezzi Rust, phone-home, seed demo, screenshot
```
