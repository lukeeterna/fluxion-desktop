# FLUXION — Handoff Sessione 151 → 152 (2026-04-13)

## CTO MANDATE — NON NEGOZIABILE
> **"Tu sei il CTO. Il founder da la direzione, tu porti soluzioni."**
> **"A PROVA DI BAMBINO. L'utente PMI non sa fare nulla se non 2 click."**
> **"LASCIALI A BOCCA APERTA!"**

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.2` | Voice pipeline porta 3002 | SIP: 0972536918

---

## COMPLETATO SESSIONE 151

### 1. Sub-Vertical Support (3 file modificati)
- **`SUB_VERTICAL_TO_MACRO` mapping** — 11 sub-verticali → 5 macro-verticali
- **Triage medico** — ora funziona per odontoiatra/fisioterapia (non solo "medical")
- **Pattern urgenza sintomatici** — mal di denti, dolore forte, dolore al petto, sangue, emorragia
- **Guardrail sub-verticali** — risposte personalizzate per 7 sub-verticali
- **VERTICAL_SERVICES fallback** — sub-verticali usano servizi macro-verticale
- **Entity extraction** — urgency/plate detection per tutti sub-verticali

### 2. 9 Vertical Test DB + Infrastructure (3 nuovi script)
- **`create_vertical_dbs.py`** — genera 9 SQLite DB completi (35 tabelle, servizi realistici, operatori, orari, clienti)
- **`switch_vertical.sh`** — switch DB + restart pipeline su iMac (usage: `./switch_vertical.sh salone`)
- **`test_all_verticals_e2e.py`** — E2E test completo: switch DB → booking → FAQ → triage → name flow

### 3. E2E Results
```
TOTALE: 21 OK / 8 WARN / 0 FAIL (29 test, 9 verticali)
- BOOKING: 8/9 OK (gommista: service name mismatch — known issue)
- FAQ:     9/9 OK (prezzi corretti da DB per ogni verticale!)
- TRIAGE:  3/3 OK (odontoiatra + fisioterapia + medical)
- FLOW:    1/8 OK (7 registering_phone = expected for new clients)
```

---

## STATO GIT
```
Branch: master | HEAD: da8c7cb pushed
Commits S151:
  87ee604 fix(S151): sub-vertical support — guardrails, triage, entity extraction
  da8c7cb feat(S151): 9 vertical test DBs + switch script + full E2E test suite
```

---

## KNOWN ISSUES (da S151)

### Gommista Booking WARN
Service "Cambio gomme stagionale" nel DB non matcha key "gomme" di VERTICAL_SERVICES["auto"]. 
L'entity_extractor trova "cambio gomme" ma il FSM non lo abbina al servizio DB.
Fix: allineare nomi servizi DB con sinonimi VERTICAL_SERVICES, o aggiungere fuzzy match.

### FAQ Content per Verticali Non-Salone
Groq risponde con prezzi corretti dal DB ma a volte menziona "salone" o servizi non pertinenti (hallucination dal training data). In produzione il system prompt sarà più specifico per verticale.

---

## SARA WORLD-CLASS PLAN — STATO
```
PHASE A-H: COMPLETE (94h/94h)
S151 Test: 9 verticali E2E testati con DB dedicati — PASS
```

---

## PROSSIMA SESSIONE (152)

### Opzione A: Sprint 5 — Sales Agent WA
Scraping PMI italiane + outreach automatico WhatsApp

### Opzione B: Fix gommista + miglioramenti FAQ
- Fix service name matching per auto/gommista
- System prompt Groq più vertical-aware
- Test live audio con microfono iMac

### Opzione C: Sprint 3 — Video V6
Aggiornamento video con scene pacchetti/fedeltà

---

## Comandi Utili S151
```bash
# Switch verticale su iMac
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && voice-agent/scripts/switch_vertical.sh salone"

# Rigenera DB verticali
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && python3 voice-agent/scripts/create_vertical_dbs.py"

# Test E2E tutti i verticali
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && python3 voice-agent/scripts/test_all_verticals_e2e.py"

# Test singolo verticale rapido
ssh imac "curl -s -X POST http://127.0.0.1:3002/api/voice/set-vertical -H 'Content-Type: application/json' -d '{\"vertical\":\"salone\"}'"
ssh imac "curl -s -X POST http://127.0.0.1:3002/api/voice/reset"
ssh imac "curl -s -X POST http://127.0.0.1:3002/api/voice/process -H 'Content-Type: application/json' -d '{\"text\":\"Vorrei prenotare un taglio\"}' | python3 -c 'import sys,json; r=json.load(sys.stdin); print(r[\"fsm_state\"], r[\"response\"][:80])'"
```

---

## CONTINUA CON
```
/clear
Leggi HANDOFF.md. Sessione 152.
DECIDERE: Sprint 5 Sales Agent WA | Fix gommista | Sprint 3 Video V6 | F1-3b VAD hookup
```
