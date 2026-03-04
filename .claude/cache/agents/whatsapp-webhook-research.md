# WhatsApp Webhook B2 Research — CoVe 2026
> Generato: 2026-03-04 | Agente: integration-specialist | Task B2

---

## WhatsApp esistente in FLUXION (analisi)

### Stack attuale — 3 componenti

**A. `/voice-agent/src/whatsapp.py`** (1189 righe, Python)

- `WhatsAppConfig` — path sessione, rate limits, NLU settings
- `WhatsAppClient` — low-level: invia via `subprocess.run([node, whatsapp-service.cjs, "send", phone, msg])`
- `WhatsAppManager` — high-level: polling loop `asyncio.sleep(2)` su `messages.jsonl` per ricezione
- `WhatsAppRateLimiter` — 3/min, 30/h, 200/day — già funzionante
- `WhatsAppTemplates` — conferma, reminder_24h, reminder_2h, cancellazione, benvenuto, compleanno, menu
- `WhatsAppMessage.from_dict()` — deserializza da JSON; `MessageDirection.INBOUND/OUTBOUND`

**Problema critico**: la ricezione attuale avviene tramite **polling del file** `~/.whatsapp-session/messages.jsonl` ogni 2 secondi. Non esiste nessun endpoint HTTP webhook per la ricezione push.

**B. `/scripts/whatsapp-service.cjs`** (Node.js, whatsapp-web.js)

Usa `whatsapp-web.js` + `LocalAuth`. Comandi CLI: `start`, `status`, `send <phone> <message>`. Scrive messaggi ricevuti nel file JSONL. Non espone nessun HTTP server — è puro filesystem/subprocess. **Questo è il punto di estensione chiave per B2.**

**C. `/voice-agent/src/orchestrator.py`** (integrazione WhatsApp)

```python
self._wa_client = WhatsAppClient()            # inizializzato se HAS_WHATSAPP
self._whatsapp_sent: bool = False             # flag anti-duplicato
self._last_booking_data: Optional[Dict]       # dati ultima prenotazione
await self._send_wa_booking_confirmation()    # fire-and-forget post-booking
await self._trigger_wa_escalation_call()      # notifica titolare su escalation
```

**D. `/voice-agent/src/session_manager.py`**

`SessionChannel.WHATSAPP` già definito. `VoiceSession.phone_number` già presente. API pronta senza modifiche.

### FSM — 23 stati in `BookingState`

```
IDLE, WAITING_NAME, WAITING_SERVICE, WAITING_DATE, WAITING_TIME,
WAITING_OPERATOR, CONFIRMING, COMPLETED, CANCELLED,
WAITING_SURNAME, CONFIRMING_PHONE,
PROPOSE_REGISTRATION, REGISTERING_SURNAME, REGISTERING_PHONE, REGISTERING_CONFIRM,
CHECKING_AVAILABILITY, SLOT_UNAVAILABLE, PROPOSING_WAITLIST,
CONFIRMING_WAITLIST, WAITLIST_SAVED,
ASKING_CLOSE_CONFIRMATION,
DISAMBIGUATING_NAME, DISAMBIGUATING_BIRTH_DATE
```

Il template `reminder_24h` già conclude con `Rispondi: OK per confermare / ANNULLA per disdire` — è il punto di ingresso principale per le risposte in arrivo.

---

## Architettura Proposta — `POST /api/voice/whatsapp/callback`

### Decisione architetturale chiave

FLUXION usa già `whatsapp-web.js` locale. **NON usare Twilio** (richiede HTTPS pubblico + costi per messaggio). Soluzione corretta:

1. Estendere `whatsapp-service.cjs` per pushare ogni messaggio ricevuto a `http://localhost:3002/api/voice/whatsapp/callback`
2. L'endpoint aiohttp Python gestisce il processing
3. Zero costi aggiuntivi, zero dipendenze cloud, funziona offline — coerente con modello FLUXION (NO SaaS)

### Flusso completo

```
Cliente risponde "OK" su WhatsApp
        |
        v
whatsapp-service.cjs (Node.js, whatsapp-web.js)
  client.on('message', msg => {
    axios.post('http://localhost:3002/api/voice/whatsapp/callback', {
      from: msg.from.replace('@c.us',''),
      name: contact.pushname,
      body: msg.body,
      timestamp: msg.timestamp,
      message_id: msg.id._serialized
    })
  })
        |
        | HTTP POST JSON
        v
POST /api/voice/whatsapp/callback  (aiohttp, main.py)
        |
        v
WhatsAppCallbackHandler.handle(request)
  1. Parse payload JSON custom
  2. Verifica message_id non già processato (dedup set)
  3. Normalizza phone via WhatsAppClient.normalize_phone()
  4. Lookup WAPhoneSession per phone
  5. Routing intent:
     a. CONFIRM_PATTERNS (ok/si/confermo) -> mark_confirmed(appointment_id)
     b. CANCEL_PATTERNS (annulla/no/disdico) -> cancel_appointment(appointment_id)
     c. Testo libero -> orchestrator.process(text, session_id=wa_session_id)
  6. Genera risposta testuale da template
  7. wa_client.send_message_async(phone, response)
  8. Log analytics whatsapp_messages
  9. Return web.Response(status=200)
```

---

## Payload formato atteso

### Formato custom JSON (whatsapp-web.js locale — raccomandato)

```json
{
  "from": "393281536308",
  "name": "Mario Rossi",
  "body": "OK",
  "timestamp": "2026-03-04T10:00:00.000Z",
  "message_id": "msg_abc123"
}
```

### Formato Twilio (supporto secondario, `application/x-www-form-urlencoded`)

```
MessageSid=SMxxx
From=whatsapp:+393281536308
Body=OK
ProfileName=Mario Rossi
```

Il `From` Twilio ha prefisso `whatsapp:` da strippare. `normalize_phone()` esistente gestisce il resto.
**Il parser deve auto-rilevare** il formato dal `Content-Type` header.

---

## Integrazione FSM

### Problema core

La risposta "OK" del cliente arriva DOPO che la sessione voice originale è già chiusa (`BookingState.COMPLETED` + `SessionState.COMPLETED`). Non si può ripristinare la sessione precedente.

### Strategia per intent semplici (OK/ANNULLA) — NON usare FSM

```python
CONFIRM_PATTERNS = re.compile(
    r"^(ok|okk|si|si'|sii|confermo|confermato|va bene|certo|esatto|perfetto|ci sono|a domani)\s*[!.]*$",
    re.IGNORECASE
)
CANCEL_PATTERNS = re.compile(
    r"^(annulla|cancella|disdico|disdetto|no|non vengo|non posso|impossibile|purtroppo)\s*[!.]*$",
    re.IGNORECASE
)
```

Azioni dirette senza FSM:
- CONFIRM: aggiorna DB `stato='confermato'` + invia template `reminder_confirmed` (nuovo template)
- CANCEL: cancella appuntamento + invia template `cancellazione` (già esistente)

### Strategia per testo libero — FSM completo

```python
# Lookup o crea sessione WhatsApp per questo phone
session_id = self._phone_sessions.get(phone, {}).get("session_id")
if not session_id or session_is_expired(session_id):
    result = await self.orchestrator.start_session(
        channel=SessionChannel.WHATSAPP,
        phone_number=phone
    )
    session_id = result.session_id

result = await self.orchestrator.process(
    user_input=message_body,
    session_id=session_id
)
```

### Mapping phone -> appointment_id

```python
@dataclass
class WAPhoneSession:
    phone: str
    session_id: Optional[str]
    pending_appointment_id: Optional[str]  # popolato quando si invia reminder
    client_name: str
    last_activity: datetime
    fsm_state: str = "idle"
```

Fallback se phone non registrato: query DB per appuntamento più recente con `telefono={phone}` e `stato=in_attesa_conferma`.

---

## File da creare/modificare

### File NUOVI

```
voice-agent/src/whatsapp_callback.py         # Handler logica callback
voice-agent/tests/test_whatsapp_callback.py  # pytest suite (12 test cases)
```

### File MODIFICATI

| File | Modifica |
|------|----------|
| `voice-agent/main.py` | +route `POST /api/voice/whatsapp/callback` + istanza handler (~15 righe) |
| `scripts/whatsapp-service.cjs` | +HTTP push axios su `client.on('message')` (~20 righe) |
| `voice-agent/src/whatsapp.py` | +`register_pending_reminder()` method (~30 righe) |

Dipendenze Python nuove: nessuna (`aiohttp`, `re`, `hmac`, `hashlib` già disponibili).
Dipendenze Node.js nuove: `axios` oppure `http` stdlib Node (zero deps aggiuntivi).

---

## Acceptance Criteria MISURABILI

| # | Criterio | Verifica |
|---|----------|---------|
| AC1 | `POST /api/voice/whatsapp/callback` risponde 200 entro 500ms | `curl -w '%{http_code}' -X POST ...` |
| AC2 | Payload `{"from":"393...", "body":"OK"}` → DB `stato='confermato'` | SQLite query dopo chiamata |
| AC3 | Payload `{"from":"393...", "body":"ANNULLA"}` → appointment cancellato + WA `cancellazione` inviato | Verifica DB + log |
| AC4 | Testo libero "Vorrei prenotare" → FSM attivo `WAITING_NAME` o `WAITING_SERVICE` | Check fsm_state in log |
| AC5 | Phone non in `_phone_sessions` → nuova sessione `SessionChannel.WHATSAPP` creata | Check `voice_sessions.db` |
| AC6 | Payload Twilio form-urlencoded parsed correttamente | pytest unit test |
| AC7 | Payload JSON custom parsed correttamente | pytest unit test |
| AC8 | Rate limiter: >3 risposte/min → warning loggato, non crash | pytest + log check |
| AC9 | message_id duplicato → ignorato silenziosamente (dedup) | pytest unit test |
| AC10 | Media message (immagine) → risposta "Solo testo" senza crash | pytest unit test |
| AC11 | `pytest tests/test_whatsapp_callback.py -v` → tutti PASS | pytest output |
| AC12 | `npm run type-check` → 0 errori (TypeScript non impattato) | npm output |

---

## Rischi e Edge Case

| # | Rischio | Severità | Mitigazione |
|---|---------|-----------|-------------|
| R1 | Nessuna mappatura phone→appointment_id (restart server) | ALTO | Persistere `_phone_sessions` su SQLite; fallback query DB |
| R2 | `_phone_sessions` perso dopo restart | MEDIO | Persistenza SQLite + recovery all'avvio |
| R3 | whatsapp-web.js non supporta HTTP push nativamente | MEDIO | Estendere `whatsapp-service.cjs` con axios (già nel piano) |
| R4 | Race condition rate limiter con più clienti simultanei | MEDIO | `asyncio.Queue` per serializzare risposte in uscita |
| R5 | Doppio processing stesso message_id (retry) | BASSO | `_processed_message_ids: Set[str]` con TTL 24h |
| R6 | Dialetto/errori: "okk", "si si", "disdico" non matchano | BASSO | Regex già include varianti; fallback orchestrator.process() |
| R7 | Sintassi Python 3.10+ non compatibile con iMac 3.9 | BASSO | Usare solo sintassi 3.9 (no walrus, no match/case) |
| EC1 | Messaggio media (foto/audio) | — | Check `type != "text"` → risposta standard |
| EC2 | Messaggio vuoto o whitespace | — | `body.strip() == ""` → skip silenzioso |
| EC3 | Sessione scaduta >30min | — | `get_session()` ritorna None → crea nuova sessione |

---

## Effort stimato

| Attività | Ore |
|-----------|-----|
| Estensione `whatsapp-service.cjs` (HTTP push) | 1h |
| `whatsapp_callback.py` classe completa + routing | 2h |
| Payload parsing dual-format | 1h |
| FSM integration + WAPhoneSession + SQLite persist | 2h |
| `test_whatsapp_callback.py` (12 test cases) | 2h |
| Integrazione `main.py` route | 0.5h |
| Verifica iMac Python 3.9 + type-check | 0.5h |
| **TOTALE** | **~9h** |

---

*Fonte: integration-specialist agent — analisi codebase reale FLUXION 2026-03-04*
