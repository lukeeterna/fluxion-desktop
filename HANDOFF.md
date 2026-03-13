# FLUXION — Handoff Sessione 63 → 64 (2026-03-13)

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
Branch: master | HEAD: 027401b
fix(voice): GAP-P1-3/P1-5/P1-6 — Sara Sprint 4 P1 (3 GAP chiusi)
Working tree: clean | type-check: 0 errori ✅ | lint: 0 errori ✅
MacBook pytest: 1424 PASS / 1 FAIL (groq not installed — pre-esistente) ✅
iMac: DA SINCRONIZZARE (git pull + pytest)
```

---

## COMPLETATO SESSIONE 63

### Sara Sprint 4 P1 — GAP-P1-3 + P1-5 + P1-6 (commit `027401b`)

#### GAP-P1-3 — check_first_available() in AvailabilityChecker
- `availability_checker.py`: nuovo metodo `check_first_available(service, days_ahead, exclude_days)`
- Itera i prossimi `days_ahead` giorni (da domani), salta `exclude_days` (nomi inglesi lowercase)
- Delega a `check_date()` per festività/orari — nessuna duplicazione logica
- Compatibile con chiamata in `orchestrator.py` riga 1381 (con `hasattr` guard rimossa in prod iMac)
- Return: `{"available": True, "date": "YYYY-MM-DD", "time": "HH:MM", "date_display": "lunedì 15 marzo"}`
- 9 test in `voice-agent/tests/test_first_available.py` — tutti PASS

#### GAP-P1-6 — Overlap detection + self-exclude in BookingManager
- `booking_manager.py` `_check_availability()`: aggiunto `duration_minutes` + `exclude_booking_id`
- Overlap detection: `new_start < old_end AND old_start < new_end` (non più point-in-time)
- Self-exclude: `reschedule_booking()` passa `exclude_booking_id=booking_id` al check
- Se reschedule non disponibile: restituisce alternative slots (top 3) via `_build_alternatives_message()`
- Fallback: se booking.time non parsabile usa confronto puntuale (retrocompat)
- 9 test in `voice-agent/tests/test_reschedule.py` — tutti PASS

#### GAP-P1-5 — Cancellation Window Validation
- `booking_manager.py`:
  - `_get_cancellation_window_hours()`: legge `faq_settings.ore_disdetta` via SQLite, default 24
  - `cancel_booking()`: nuovo param `bypass_window=False` — rifiuta se `hours_until < window_hours`
  - Return message: `"Disdetta non consentita: l'appuntamento e tra meno di N ore..."`
- `whatsapp_callback.py`:
  - `_get_cancellation_window_hours()`: stessa logica standalone (no import booking_manager)
  - `_cancel_appointment()`: check window prima di UPDATE — restituisce False se dentro finestra
  - `_handle_cancel()`: risposta WA dedicata: `"Disdetta ricevuta dopo la finestra di N ore..."`
- `orchestrator.py`:
  - `_get_cancellation_window_hours()`: legge da SQLite via `_find_db_path()`
  - `_check_cancellation_window(appointment_data)`: helper puro `(blocked, msg)` — fail-open su dati mancanti
  - `_handle_cancel_flow()`: check window prima di chiamare `_cancel_booking()`
- `test_booking_e2e_complete.py`: fix pre-esistente — aggiunto `bypass_window=True` per test con date passate
- 12 test in `voice-agent/tests/test_cancellation_window.py` — tutti PASS

**MacBook pytest S63**: 1424 PASS / 1 FAIL (pre-esistente groq) ✅ (+16 nuovi test vs S62)

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

## PROSSIMA SESSIONE S64

> **Skill**: `fluxion-voice-agent` (Sara Sprint 4 P1 restanti) o `fluxion-workflow` (F15 se EHIWEB arrivato)

### Priorità S64 (in ordine):
1. **SE EHIWEB arrivato** → F15 test SIP end-to-end
2. **Sara Sprint 4 P1 restanti** → GAP-P1-4 (operator gender preference), eventuale GAP-P1-7+ da research
3. **Sync iMac**: `git pull && pytest` → verificare 1424+ PASS su Python 3.9

### Al via sessione S64:
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
