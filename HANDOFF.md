# FLUXION — Handoff Sessione 62 → 63 (2026-03-12)

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
Branch: master | HEAD: c6e571c
chore(handoff): s62 — Sara Sprint 4 DONE (GAP-P0-1/2/3/4) — 1394 PASS
Working tree: clean | type-check: 0 errori ✅ | lint: 0 errori ✅
iMac: sincronizzato ✅ | pytest: 1408 PASS / 0 FAIL ✅ | cargo check: 0 errori ✅
```

---

## COMPLETATO SESSIONE 62

### F07 — Email Retry APScheduler (commit `a6f62a6`)
- `send_activation_email()` ora restituisce `bool` (successo/fallimento)
- Colonna `email_sent` (0=pending, 1=sent, -1=failed) + `email_retry_count` in tabella `orders`
- `_email_retry_loop()`: asyncio loop ogni 5min, max 3 tentativi, marca -1 su fallimento definitivo
- Lifecycle hooks `_start_background_tasks()` / `_stop_background_tasks()` in `create_app()`
- `?dark=1` già presente in `buildCheckoutUrl()` — nessuna modifica necessaria

### Sara Sprint 4 — GAP-P0-1/2/3/4 (commit `8c5b322`, `847021b`, `c6e571c`)

#### GAP-P0-1 — Phone Validation
- `entity_extractor.py`: helper `_is_valid_mobile()` in `extract_phone()`
- Rifiuta: numeri che iniziano con `0` (fisso), sequenze > 12 cifre (overflow)
- Pattern regex rinforzati con `(?<!\d)..(?!\d)` per bloccare partial match
- 6 test aggiunti in `TestPhoneValidation` (`test_entity_extractor.py`)

#### GAP-P0-2 — Email RFC5322 Compliance
- `entity_extractor.py` `extract_email()`: validazione post-match
- Rifiuta: consecutive dots, TLD < 2 chars, domain senza punto
- Normalizza sempre a lowercase
- 7 test aggiunti in `TestEmailValidation` (`test_entity_extractor.py`)

#### GAP-P0-3 — Festività caricate da DB
- `orchestrator.py` `_load_business_context()`: query `impostazioni.giorni_festivi` (JSON o CSV)
- Default: 10 festività nazionali italiane con anno relativo (Capodanno, Epifania, 25 Aprile, etc.)
- Propagazione immediata a `self.availability.config.holidays`
- 5 test in `test_holiday_handling.py`

#### GAP-P0-4 — Holiday messaging con 3 alternative
- `availability_checker.py`: `_suggest_alternative_dates()` → 3 alternative (era 2), skip festivi
- Template riformattato: "Mi dispiace, {data} siamo chiusi. Le propongo alt1, alt2 o alt3"
- 5 test in `test_holiday_handling.py`

**pytest iMac S62**: 1408 PASS / 0 FAIL ✅ (+23 vs S61)

---

## F15 VoIP — Stato Invariato

⚠️ **EHIWEB IN ATTESA** — email inviata s55, ancora nessuna risposta (2026-03-12)

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

## PROSSIMA SESSIONE S63

> **Skill**: `fluxion-voice-agent` (Sara Sprint 4 P1) o `fluxion-workflow` (F15 se EHIWEB arrivato)

### Priorità S63 (in ordine):
1. **SE EHIWEB arrivato** → F15 test SIP end-to-end
2. **Sara Sprint 4 P1** → GAP-P1-3 (exclude_days stub), GAP-P1-4 (operator gender), GAP-P1-5 (cancellation window), GAP-P1-6 (reschedule availability check)
3. **F07 config.env** → se Gianluca ha le credenziali LS + Gmail App Password

---

## Riavvio pipeline iMac:
```bash
ssh imac "kill \$(lsof -ti:3002) 2>/dev/null; sleep 2; cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python main.py --port 3002 > /tmp/voice-pipeline.log 2>&1 &"
```
