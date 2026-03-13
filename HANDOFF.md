# FLUXION — Handoff Sessione 65 → 66 (2026-03-13)

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
Branch: master | HEAD: a17ba90
fix(tests): VoiceOrchestrator class name in waitlist trigger tests
Working tree: clean | type-check: 0 errori ✅ | lint: 0 errori ✅
MacBook pytest: 1449+2=1451 PASS / 1 FAIL (groq not installed — pre-esistente) ✅
iMac pytest: 1467 PASS / 0 FAIL ✅ (+4 vs S64)
```

---

## COMPLETATO SESSIONE 65

### 1. UI Genere Operatore (commit `01b8b26`)
Campo `genere` M/F/NULL nel `OperatoreDialog` — completa il ciclo iniziato in S64 (DB + API già fatti).

- `src/types/operatore.ts`: `genere: string | null` in interface + Zod schema `enum('M','F').nullable().optional()`
- `OperatoreDialog.tsx`: Select "Uomo/Donna/Non specificato" con label `(per preferenze clienti Sara)`
- `src-tauri/src/commands/operatori.rs`: `genere: Option<String>` in struct + INSERT + UPDATE SQL

### 2. GAP-P1-7: Waitlist Trigger Immediato su Cancellazione (commit `815cde4` + `a17ba90`)
Quando un appuntamento viene cancellato via voice, il check waitlist viene triggerato immediatamente (fire-and-forget) invece di aspettare il ciclo da 5min.

- `orchestrator.py`: `asyncio.create_task(check_and_notify_waitlist(self._wa_client))` dopo cancel success
- `main.py`: `server.wa_client = wa_client` + endpoint `POST /api/waitlist/trigger` (per UI future)
- `test_waitlist_trigger.py`: 4 test (2 MacBook-safe + 2 iMac integration) — **4/4 PASS iMac** ✅

### 3. CLAUDE.md aggiornato
- FASE 0 skill identification: aggiunta regola "OGNI task deve avere skill assegnata" + "crea skill custom con docs Anthropic se non trovata"

---

## F15 VoIP — Stato Invariato

⚠️ **EHIWEB IN ATTESA** — email inviata s55, ancora nessuna risposta (2026-03-13)

---

## F07 — Config.env iMac (BLOCKERS mancanti)

```bash
LS_WEBHOOK_SECRET=<preso da LemonSqueezy webhook settings>
SMTP_USER=<email@gmail.com>
SMTP_PASS=<16-char app password da myaccount.google.com/apppasswords>
ACTIVATE_URL_BASE=https://<dominio-cloudflare> (tunnel già attivo)
FLUXION_KEYGEN_PATH=/Users/gianlucadistasi/fluxion-keygen
KEYPAIR_PATH=/Users/gianlucadistasi/fluxion-keypair.json
```

---

## PROSSIMA SESSIONE S66

> **Skill**: `fluxion-voice-agent` (GAP-P1-1/P1-2/P1-8 restanti) o `fluxion-tauri-architecture` (F07 se credenziali disponibili)

### Priorità S66 (in ordine):
1. **SE EHIWEB arrivato** → F15 test SIP end-to-end
2. **GAP-P1-1** → Intl phone formats (0039, varianti spazi) — normalize → "39XXXXXXXXX"
3. **GAP-P1-2** → Email extraction da testo complesso — prioritize post keyword "email"
4. **GAP-P1-8** → Multi-operator selection (`extract_operators()` plural)
5. **F07 go-live** → se credenziali config.env disponibili

### GAP P1 Restanti (Sprint 5):
| GAP | Stato | Descrizione |
|-----|-------|-------------|
| P1-1 | ⏳ | Intl phone formats |
| P1-2 | ⏳ | Email extraction keyword |
| P1-7 | ✅ S65 | Waitlist trigger su cancellazione |
| P1-8 | ⏳ | Multi-operator selection |

### Al via sessione S66:
```bash
# 1. Sync iMac (se non fatto)
git push origin master && ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && git pull"

# 2. Verifica pytest iMac
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && \
  /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python \
  -m pytest tests/ --tb=short 2>&1 | tail -5"
```

---
