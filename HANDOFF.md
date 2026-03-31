# FLUXION — Handoff Sessione 127 → 128 (2026-03-31)

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

## COMPLETATO SESSIONE 127 — 3 COMMIT

### 1. Fix FAQ variable substitution for new verticals
- `substitute_variables()` in `vertical_loader.py` now handles both `{{VAR}}` (old) and `[VAR]` (S126) formats
- S126 FAQ files used `[PREZZO_*]` which was silently unsubstituted — now fixed
- Also fixed Python 3.9 positional arg issue with `re.sub()`
- E2E verified:
  - barbiere: `[PREZZO_BARBA]` → `15`, `[PREZZO_RIFINITURA]` → `10` ✅
  - odontoiatra: `[PREZZO_IGIENE]` → `80` ✅

### 2. Fix intent routing: "orari" → FAQ not booking
- Added explicit INFO keyword guard in `orchestrator.py` before `should_process_booking`
- Keywords: orario, prezzi, costi, quanto cost, listino, accettate, pagamenti
- `_is_info` now blocks ALL booking conditions (not just first-turn)
- `should_process_booking` rewritten: `not _is_info` guard on every condition
- E2E verified:
  - "Quali sono gli orari?" → L3_faq ✅
  - "Quanto costa la barba?" → L3_faq with price ✅
  - "Vorrei prenotare" → L2_slot booking (not broken) ✅
  - "Accettate carte?" → L3_faq ✅

### 3. Demo seed for screenshots (Sprint 1.3)
- `scripts/seed-demo-screenshot.sql` — comprehensive demo data
- 48 clienti (5 VIP: Valeria 14/10, Francesca 18/10, Silvia 22/10, Roberto 12/10, Alessandra 16/10)
- 112 completati marzo + 9 confermati oggi + 16 settimana
- **Fatturato: €4.850 esatto** (servizi €4.441 + prodotti €409)
- 3 pacchetti attivi (Festa Papà, Estate, Natale)
- 4 fornitori, incassi mix contanti/carta/satispay
- Loaded on iMac DB ✅

### Sprint 1 tasks already done (found during research)
- **Prezzi Rust**: Already aligned 497/897 in `license_ed25519.rs` (Base/Pro/Enterprise)
- **Phone-home**: Fully implemented — Rust Ed25519 + CF Worker + React hooks + SaraTrialBanner

---

## STATO GIT
```
Branch: master | HEAD: 74fe9e7
Commits S127:
  6e69e1e fix(S127): FAQ variable [VAR] format + intent routing INFO guard
  a0ea240 fix(S127): Python 3.9 re.sub positional arg
  74fe9e7 feat(S127): add demo seed for screenshots — €4.850 fatturato, 48 clients
```

---

## GSD MILESTONE v1.0 Lancio
```
Phase 10d: Sara Verticali       ✅ FAQ + SEED + ALIAS + DISAMBIG + WELCOME-BACK + NEW-VERTICALS (S123-S126)
Phase 10e: Sara Bug Fixes       ✅ FAQ vars + intent routing (S127)
Sprint 1:  Product Ready        ✅ Prezzi OK + Phone-home OK + Demo seed loaded (S127)
Sprint 2:  Screenshot Perfetti  ⏳ NEXT — catturare da iMac con dati demo belli
Sprint 3:  Video che Spacca     ⏳
Sprint 4:  Landing Definitiva   ⏳
Sprint 5:  Sales Agent WA       ⏳
```

---

## PROSSIMA SESSIONE 128 — PRIORITÀ

### A. Sprint 2: Screenshot Perfetti
- **Prerequisito completato**: Demo seed caricato su iMac con €4.850 fatturato
- Catturare 18+ screenshot via SSH (CGEvent + CGWindowListCreateImage)
- Dashboard, Calendario, Clienti, Servizi, Operatori, Fatture, Cassa, Voice, Fornitori, Analytics, Impostazioni, Pacchetti, Fedeltà, 5 schede verticali
- Verificare: ogni screenshot 1280x720+, dati realistici, zero glitch

### B. Remaining voice bugs (lower priority)
- [ ] Two-digit phone words (trentatre, ventuno)
- [ ] Spostamento appuntamenti non trova appuntamenti esistenti

### C. Sprint 1.4 — Remove "non configurato" warning
- [ ] Verify dashboard shows no warnings with demo seed

---

## FILE CHIAVE SESSIONE 127
- `voice-agent/src/vertical_loader.py:70-96` — substitute_variables() dual format
- `voice-agent/src/orchestrator.py:1265-1270` — S127 INFO keyword guard
- `voice-agent/src/orchestrator.py:1301-1312` — S127 _is_info blocks booking
- `scripts/seed-demo-screenshot.sql` — 538 lines, complete demo data

---

## NOTE TECNICHE

### Pipeline riavvio (SEMPRE CON PYTHONUNBUFFERED)
```bash
ssh imac "kill \$(lsof -ti:3002) 2>/dev/null; sleep 2; cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && DYLD_LIBRARY_PATH=lib/pjsua2 PYTHONUNBUFFERED=1 nohup /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python main.py --port 3002 > /tmp/voice-pipeline.log 2>&1 &"
```

### Demo DB su iMac
```
Seed: scripts/seed-demo-screenshot.sql
Path: /Users/gianlucadistasi/Library/Application Support/com.fluxion.desktop/fluxion.db
Vertical: salone | Nome: Salone Elegance di Giulia
Clienti: 48 (5 VIP) | Fatturato: €4.850 | Oggi: 9 apt | Settimana: 25 apt
Top servizio: Taglio + Barba (25x)
```

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 128.
PRIORITÀ:
1. Sprint 2: Screenshot perfetti da iMac (18+ screenshot con dati demo)
2. Sprint 1.4: Verificare zero warning dashboard
3. Sprint 3: Video aggiornato con nuovi screenshot
```
