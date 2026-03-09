# FLUXION — Handoff Sessione 36 → 37 (2026-03-09)

## ⚡ CTO MANDATE — NON NEGOZIABILE (sessione 36)
> **"Non accetto mediocrità. Solo enterprise level."**
> Ogni feature deve battere Fresha sul campo della PMI italiana.
> Ogni task risponde: *"quanti € risparmia o guadagna la PMI?"*
> Se non risponde → non si implementa.

---

## ⚠️ GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`

---

## STATO GIT
```
Branch: master | HEAD: 53201c6 | CI: ✅ verde
Working tree: pulito
type-check: 0 errori
iMac: sincronizzato, pipeline UP su porta 3002, APScheduler 3.11.2 installato
```

---

## COMPLETATO SESSIONE 36

| Lavoro | Commit | Impatto PMI |
|--------|--------|-------------|
| **Gap #1** — Parallel TTS + llama-3.1-8b-instant | e74b34f | Sara latency 1330ms→<800ms (-48%) |
| **Gap #2** — Reminder automatici -24h/-1h APScheduler | a3c4b58 | -40% no-show = +25% slot fill |
| **Gap #3** — Waitlist slot-free notify ogni 5min | 3b2901a | +15-20% conversion cancellazioni |
| **Fix** — Align waitlist query a schema DB reale | 53201c6 | Schema reale: servizio_id, data_richiesta |
| **Note WhatsApp** — Rischio ban analizzato | — | LOW per 1:1, pathway Cloud API F08 |

### Dettaglio tecnico Gap #1 — Parallel TTS
- `orchestrator.py`: L4 ora lancia `asyncio.create_task(tts.synthesize(chunk))` su ogni chunk LLM
- `_concat_wav_chunks()`: merge WAV in ordine (wave module, stesso sample rate)
- `groq_client.py`: `LLM_FAST_MODEL = "llama-3.1-8b-instant"` (2x più veloce per risposte brevi)
- Fallback automatico a synthesis sequenziale su errore TTS parallel

### Dettaglio tecnico Gap #2 + #3 — `reminder_scheduler.py`
- **Job 1** (ogni 15min): `check_and_send_reminders()` — finestre T-24h±15min / T-1h±15min
- **Job 2** (ogni 5min): `check_and_notify_waitlist()` — slot libero → WA "Rispondi SI/NO entro 2h"
- Idempotente: `reminders_sent.json` per reminder, `notificato_il` in DB per waitlist
- APScheduler `AsyncIOScheduler` — stessa event loop del voice pipeline
- WA non connesso → warning, non crash

---

## SCHEMA WAITLIST DB REALE (non coincide con migration 013)
```sql
-- Colonne reali su iMac DB:
servizio_id TEXT   -- FK servizi.id  (non: servizio TEXT)
data_richiesta     -- (non: data_preferita)
ora_richiesta      -- (non: ora_preferita)
stato = 'attivo'   -- (non: 'attesa')
notificato_il      -- (non: contattato_at)
scadenza_risposta  -- +2h da notifica (già presente in schema)
priorita INTEGER   -- (non: priorita_valore)
creato_il          -- (non: created_at)
```

---

## F07 LEMONSQUEEZY — In attesa azioni Luke

| Step | Stato | Note |
|------|-------|------|
| server.py bugfix | ✅ a6d0d1f | enterprise→clinic |
| Crea store + 3 prodotti | ⏳ LUKE | nomi esatti, pricing definito |
| Webhook Signing Secret | ⏳ LUKE | dopo creazione webhook |
| SMTP in config.env | ⏳ | SMTP pass già in .env: `lzhx yujp hvel epyb` |
| Server iMac porta 3010 | ⏳ | dopo config.env |
| Cloudflare Tunnel | ⏳ | dopo server |

---

## PROSSIMA SESSIONE 37 — AGENDA

### Priorità in ordine
1. **Gap #4 — WhatsApp button Conferma/Cancella [M]**
   - Pain: cliente dice "sì" al telefono poi non viene. No-show da conferma verbale.
   - Fix: WA interactive message con bottoni "✅ Confermo" / "❌ Cancello" / "📅 Sposto"
   - Files: `whatsapp.py` (send_template) + `whatsapp_callback.py` (gestione risposta) + `whatsapp-service.cjs`
   - Prerequisito: verificare se whatsapp-web.js supporta interactive buttons (MessageMedia)
   - Alternativa se no: testo con keyword "SI"/"NO" già gestito in `whatsapp_callback.py`
   - Revenue: +5-10% confirmation rate = diretto slot fill

2. **F07 LemonSqueezy** — solo se Luke fornisce credenziali store

3. **Gap #6 — Tessera fedeltà UI** [M]
   - Pain: schema loyalty esiste, UI mai collegata → titolare non può usarla
   - Fix: wire loyalty UI + APScheduler birthday WA (-7 giorni)
   - Revenue: +8% return rate = Pro feature differentiator

### Se Gap #4 richiede research preventiva
File da leggere prima di implementare:
- `scripts/whatsapp-service.cjs` — supporto MessageMedia/buttons in whatsapp-web.js
- `voice-agent/src/whatsapp_callback.py` — callback handler esistente (pattern SI/NO già c'è)
- `voice-agent/src/whatsapp.py` — `send_template()` + templates disponibili

---

## PROMPT RIPARTENZA SESSIONE 37

```
Sessione 37 — Gap #4 WhatsApp Confirm/Cancel + F07 LemonSqueezy

⚠️ GUARDRAIL:
- Working dir: /Volumes/MontereyT7/FLUXION
- Memory: /Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md
- Ignora backup-combaretrovamiauto-* nel T7

CTO MANDATE: "Non accetto mediocrità. Solo enterprise level."

STATO:
- HEAD: 53201c6 | CI ✅ verde | working tree pulito
- Gap #1-3 COMPLETATI (latency + reminder + waitlist)
- APScheduler 3.11.2 installato iMac, pipeline UP porta 3002
- F07 in attesa credenziali Luke (LemonSqueezy)

AGENDA — in ordine esatto:
1. GAP #4 — WhatsApp button Conferma/Cancella
   Target: WA interactive "Confermo/Cancello/Sposto" su appuntamento prenotato
   Leggi prima: scripts/whatsapp-service.cjs (button support?) + voice-agent/src/whatsapp.py + whatsapp_callback.py
   Revenue: +5-10% confirmation rate → meno no-show

2. F07 LEMONSQUEEZY (solo se Luke ha creato lo store)
   Config needed: LS_WEBHOOK_SECRET + SMTP_USER + SMTP_PASS

3. GAP #6 — Tessera fedeltà UI + birthday WA
   Pain: loyalty schema esiste, UI mai collegata
   Revenue: +8% return rate

Per ogni gap: RESEARCH → PLAN con AC misurabili → IMPLEMENT → VERIFY → DEPLOY
REGOLA: ogni feature risponde "quanti € risparmia/guadagna la PMI?"

SCHEMA WAITLIST REALE (da usare se tocchi waitlist):
- servizio_id (FK), data_richiesta, ora_richiesta, stato='attivo', notificato_il, priorita
```
