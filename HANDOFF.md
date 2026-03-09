# FLUXION — Handoff Sessione 37 → 38 (2026-03-09)

## ⚡ CTO MANDATE — NON NEGOZIABILE
> **"Non accetto mediocrità. Solo enterprise level."**
> Ogni feature risponde: *"quanti € risparmia o guadagna la PMI?"*

---

## ⚠️ GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`

---

## STATO GIT
```
Branch: master | HEAD: b9265f4 | CI: ✅ verde
Working tree: pulito
type-check: 0 errori
iMac: sincronizzato, pipeline UP porta 3002, license server UP porta 3010
```

---

## COMPLETATO SESSIONE 37

| Lavoro | Commit | Impatto PMI |
|--------|--------|-------------|
| **Gap #4** — WhatsApp Confirm/Cancel/Sposta | 3f097f1 | +5-10% confirmation rate, -no-show |
| **Gap #6A** — Birthday WA daily 9:00am | da197d1 | +8% return rate |
| **Gap #6B** — Milestones banner Clienti.tsx | da197d1 | Operatore vede chi incentivare |
| **F07** — Store LS creato + server live + test OK | 6350aec + b9265f4 | Monetizzazione attiva |

### Dettaglio Gap #4
- `RESCHEDULE_PATTERN` + `_handle_reschedule()` in `whatsapp_callback.py`
- `_send_reminder()` chiama `register_pending_appointment()` post-invio → reply attribuiti
- `start_reminder_scheduler()` riceve `callback_handler`; server creato prima del scheduler in `main.py`
- 40/40 test PASS Python 3.9 iMac

### Dettaglio Gap #6
- `reminder_scheduler.py`: `check_and_send_birthdays()` — query `strftime('%m-%d', data_nascita)` = oggi
- Job APScheduler `CronTrigger(hour=9)` — idempotente via `birthday_sent.json` {cliente_id: 'YYYY'}
- `Clienti.tsx`: `useLoyaltyMilestones(3)` → banner ambra "N clienti vicini al traguardo"

### Dettaglio F07 — License Delivery Server
- Store: https://fluxion.lemonsqueezy.com ✅
- server.py: `_resolve_tier()` con substring match + UUID variant fallback
- config.env su iMac: LS_WEBHOOK_SECRET + SMTP Gmail + keygen paths ✅
- ngrok tunnel attivo: `https://1c0b-151-45-144-241.ngrok-free.app`
- Test end-to-end ✅: webhook → DB order salvato → email inviata a fluxion.gestionale@gmail.com
- ⚠️ ngrok URL cambia al riavvio (piano free) → aggiornare webhook LS + ACTIVATE_URL_BASE in config.env

---

## INFRA F07 — Comandi manutenzione

```bash
# Avviare license server iMac
ssh imac "cd '/Volumes/MacSSD - Dati/FLUXION/scripts/license-delivery' && nohup /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python server.py > /tmp/license-server.log 2>&1 &"

# Avviare ngrok (porta 3010)
ssh imac "pkill -f 'ngrok http' 2>/dev/null; nohup ~/bin/ngrok http 3010 > /dev/null 2>&1 & sleep 3 && curl -s http://localhost:4040/api/tunnels | python3 -c \"import sys,json; t=json.load(sys.stdin)['tunnels']; print(t[0]['public_url'])\""

# Health check
ssh imac "curl -s http://localhost:3010/health"

# Log license server
ssh imac "tail -20 /tmp/license-server.log"

# Aggiornare config.env dopo cambio URL ngrok
# ssh imac "sed -i '' 's|ACTIVATE_URL_BASE=.*|ACTIVATE_URL_BASE=NUOVO_URL|' '/Volumes/MacSSD - Dati/FLUXION/scripts/license-delivery/config.env'"
```

---

## PROSSIMI GAP (ordine priorità)

| # | Gap | Pain | Revenue | Effort |
|---|-----|------|---------|--------|
| 5 | PDF import listino fornitori | 30min/giorno copiato a mano | risparmio tempo | L |
| 8 | Fattura 1-click da appuntamento | 5h/mese create manualmente | risparmio tempo | M |
| 9 | Analytics + report PDF mensile | PMI non sa cosa guadagna | decisioni migliori | L |
| 10 | WhatsApp bulk anti-churn | €500-1K/mese in FB ads evitabili | retention | L |

## F07 — PROSSIMI STEP (quando URL diventa permanente)
1. Cloudflare Tunnel permanente (sostituisce ngrok free)
2. Creare `activate.html` landing page per clienti
3. Collegare checkout URLs nella landing `fluxion-landing.pages.dev`

---

## SCHEMA WAITLIST DB REALE
```sql
servizio_id TEXT   -- FK servizi.id
data_richiesta     -- YYYY-MM-DD
ora_richiesta      -- HH:MM
stato = 'attivo'   -- non 'attesa'
notificato_il      -- timestamp notifica
scadenza_risposta  -- +2h da notifica
```
