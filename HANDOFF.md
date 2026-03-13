# FLUXION — Handoff Sessione 64 → 65 (2026-03-13)

## CTO MANDATE — NON NEGOZIABILE
> **"Non accetto mediocrità. Solo enterprise level."**
> Ogni feature risponde: *"quanti € risparmia o guadagna la PMI?"*

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.12` | Voice pipeline: porta 3002 (bind 127.0.0.1) | Test via SSH

---

## STATO GIT
```
Branch: master | HEAD: 1ec1831
feat(voice): GAP-P1-4 operator gender preference
Working tree: clean | type-check: 0 errori ✅ | lint: 0 errori ✅
MacBook pytest: 1449 PASS / 1 FAIL (groq not installed — pre-esistente) ✅
iMac pytest: 1463 PASS / 0 FAIL ✅ (+25 vs S63)
```

---

## COMPLETATO SESSIONE 64

### Sara Sprint 4 P1 — GAP-P1-4 (commit `1ec1831`)

#### GAP-P1-4 — Operator Gender Preference

**Migration 033** (`033_operatori_genere.sql`):
- `ALTER TABLE operatori ADD COLUMN genere TEXT` — valori: 'M', 'F', NULL
- `lib.rs`: runner block 033 con duplicate-column guard

**HTTP Bridge** (`http_bridge.rs`):
- `OperatoreRow` struct: aggiunto `genere: Option<String>`
- `handle_operatori_list`: SELECT + JSON includono `genere`
- `get_alternative_operators`: SELECT aggiornato

**Python** (`operator_gender.py` + `orchestrator.py`):
- `operator_gender.py`: modulo standalone `extract_operator_gender_preference()` — 8 pattern femminili + 8 maschili, regex precompilate
- `orchestrator.py`: import + rilevamento in L0-PRE (sticky, si setta una volta sola) + filtro operatori per `genere` con fallback a tutti se nessuno matcha
- `test_operator_gender.py`: 25 test (20 extraction + 5 filtering) — tutti PASS

---

## F15 VoIP — Stato Invariato

⚠️ **EHIWEB IN ATTESA** — email inviata s55, ancora nessuna risposta (2026-03-13)

Quando arrivano le credenziali:
1. `config.env iMac` → `VOIP_SIP_USER`, `VOIP_SIP_PASSWORD`, `VOIP_LOCAL_IP=192.168.1.12`
2. Port forward router: 5060 UDP → 192.168.1.12
3. Test: `curl http://192.168.1.12:3002/api/voice/voip/status` → `{"registered": true}`
4. Test chiamata end-to-end — latenza P95 < 2s

---

## F07 — Config.env iMac (BLOCKERS mancanti)

Server già funzionante, mancano credenziali reali in `config.env` iMac:
```bash
LS_WEBHOOK_SECRET=<preso da LemonSqueezy webhook settings>
SMTP_USER=<email@gmail.com>
SMTP_PASS=<16-char app password da myaccount.google.com/apppasswords>
ACTIVATE_URL_BASE=https://<dominio-cloudflare> (tunnel già attivo)
FLUXION_KEYGEN_PATH=/Users/gianlucadistasi/fluxion-keygen
KEYPAIR_PATH=/Users/gianlucadistasi/fluxion-keypair.json
```

---

## PROSSIMA SESSIONE S65

> **Skill**: `fluxion-voice-agent` (Sara Sprint 4 P1 restanti) o `fluxion-workflow` (F15 se EHIWEB arrivato)

### Priorità S65 (in ordine):
1. **SE EHIWEB arrivato** → F15 test SIP end-to-end
2. **Sara Sprint 4 P1 restanti** → eventuali GAP da research (P1-7+?)
3. **UI operatori genere** → aggiungere campo genere (M/F/NULL) nella scheda operatore in Impostazioni → `src/components/settings/OperatoriSettings.tsx` o equivalente
4. **F07 go-live** → se credenziali config.env disponibili

### Al via sessione S65:
```bash
# 1. Sync iMac
git push origin master && ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && git pull"

# 2. Test iMac
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && \
  /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python \
  -m pytest tests/ -v --tb=short 2>&1 | tail -20"

# 3. Riavvio pipeline se necessario
ssh imac "kill \$(lsof -ti:3002); sleep 2; \
  cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && \
  /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python \
  main.py --port 3002 > /tmp/voice-pipeline.log 2>&1 &"
```

---
