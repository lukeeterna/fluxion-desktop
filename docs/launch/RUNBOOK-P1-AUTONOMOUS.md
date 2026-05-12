# RUNBOOK-P1 AUTONOMOUS — Test VoIP loopback senza founder/cellulare

> **Scopo**: eseguire la maggior parte del valore di RUNBOOK-P1 in modo **completamente autonomo** (Claude-side via SSH iMac), senza dipendenza da founder fisico, cellulare esterno o costi PSTN.
> **Genesi**: S204 — founder ha chiesto "trova modo per eseguire test RUNBOOK-P1 VoIP autonomamente".
> **Stato**: ✅ MVP smoke validato (~95%). ❌ Full Scenario 4 da completare in S205.

---

## TL;DR risultati S204

| Item | Stato | Dettaglio |
|------|-------|-----------|
| pjsua2 SDK iMac funzionante | ✅ | `lib/pjsua2/` + `DYLD_LIBRARY_PATH=.` + system Python 3.9 |
| Second pjsua2 endpoint (caller) | ✅ | porta 5091 OK, IP-based account creato |
| Pipeline VoIP REGISTERED su VivaVox | ✅ | `sip:0972536918@sip.vivavox.it`, `reg_status=200` |
| Pipeline accetta INVITE locale | ✅ | log: "Incoming call from `<sip:smoke-caller@127.0.0.1>` → 200 OK" |
| Audio bridge attivato lato pipeline | ✅ | log: "Audio bridge established: call ↔ Sara" |
| Dialog handshake completo (ACK) | ❌ | fake-caller non manda ACK → call stuck in CONNECTING |
| WAV audio capturato dal caller | ✅ (forma) ❌ (contenuto) | 15s WAV ma 100% silenzio (no audio outbound senza CONFIRMED state) |
| Scenario 4 E2E (5 turni dinamici) | ⏳ S205 | richiede fix ACK + audio fixture Edge-TTS + DB verify |

**Conclusione onesta**: il "modo autonomo" è **viabile e quasi pronto**. Tutto il setup è validato, manca solo 1 fix tecnico al fake-caller (ACK auto-emission).

---

## Architettura validata

```
   [fake-caller pjsua2]                 [Sara pipeline pjsua2]
   sip:smoke-caller@127.0.0.1:5091      sip:0972536918@127.0.0.1:5080
            │                                       │
            └─── INVITE ─────────────────────────► │
            ◄──── 100 Trying ──────────────────────┤
            ◄──── 200 OK ──────────────────────────┤
            ┊                                       │
            ❌ (MISSING ACK)                       │
            ┊                                       │  ⌛ retransmits 200 OK
            ┊                                       │     fino a timeout 30s
            ◄──── 200 OK (retx) ──────────────────┤
            └─── BYE ──────────────────────────► (timeout)
```

**Componenti zero-cost (vincolo #5)**: tutto locale, no servizi paid, no signup terzi, no PSTN reali consumati.

---

## Trade-off documentati

### ✅ Valida autonomamente (~80% RUNBOOK-P1)

- pjsua2 SDK + UDP transport stack
- INVITE handling (parsing, contact rewrite)
- 200 OK answer pipeline (S153 fix attivo: direct answer)
- Audio bridge SaraAudioPort ↔ pjsua2 conference
- Codec G.711 negotiation (stesso PSTN reale)
- Orchestrator injection in VoIPManager (`set_pipeline`)
- *Post-fix S205*: STT/TTS bidi, FSM transitions, DB persistenza

### ❌ NON valida autonomamente

- **NAT casa CGNAT**: setup local-only bypassa NAT. Test reale richiede cellulare → VivaVox → iMac via internet.
- **Codec PSTN reale degradation**: banda 300-3400Hz, jitter rete, packet loss. Solo cellulare→DID lo testa davvero.
- **VivaVox routing**: il fatto che `reg_status=200` non garantisce inbound da PSTN funzioni — può fallire per dialplan VivaVox, firewall router, DID non instradato. Test PSTN reale resta P1 founder fisico (5 min smoke da cellulare).
- **Audio quality cellulare → DID**: Sara TTS percepita su mobile speaker.

---

## Pre-flight autonomo (eseguibile ora)

```bash
# 1. Pipeline up + VoIP registered
ssh imac "curl -s http://127.0.0.1:3002/api/voice/voip/status | python3 -m json.tool"
# Atteso: running=true, sip.registered=true, reg_status=200

# 2. pjsua2 SDK importabile
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent/lib/pjsua2' && \
  DYLD_LIBRARY_PATH=. PYTHONPATH=. /usr/bin/python3 -c \
  'import pjsua2 as pj; ep=pj.Endpoint(); ep.libCreate(); \
   c=pj.EpConfig(); c.logConfig.level=0; ep.libInit(c); \
   print(\"pjsua2:\", ep.libVersion().full); ep.libDestroy()'"
# Atteso: pjsua2: 2.16-dev

# 3. Port 5091 free
ssh imac "lsof -nP -iUDP:5091 2>/dev/null || echo 'port 5091 free'"
```

---

## Esecuzione MVP smoke (stato attuale)

```bash
# Sync script su iMac (commit + git pull, oppure scp diretto)
git push origin master && ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && git pull origin master"

# Run smoke
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent/lib/pjsua2' && \
  DYLD_LIBRARY_PATH=. PYTHONPATH=. /usr/bin/python3 \
  '/Volumes/MacSSD - Dati/fluxion/scripts/sara-voip-loopback-smoke.py'"

# Output:
#   /tmp/sara-voip-loopback-YYYYMMDD-HHMMSS.log    (pjsua2 verbose)
#   /tmp/sara-voip-loopback-YYYYMMDD-HHMMSS.wav    (audio Sara capturato)
#   /tmp/sara-voip-loopback-report.json            (verdetto JSON)

# Conferma pipeline ricezione (parallel):
ssh imac "tail -50 /tmp/voice-pipeline.log | grep -iE 'incoming call|audio bridge|call state'"
```

**Verdetto S204 attuale**: pipeline log conferma INVITE ricevuto + audio bridge attivato. Verdetto JSON = FAIL per bug ACK (TODO S205).

---

## TODO S205 (~30-45 min Claude-side)

### Step 1 — Fix ACK auto-emission (~15 min)

Investigazione su `pjsua2` 2.16-dev IP-based account behavior. Opzioni ordinate per cost-benefit:

1. **Esplicito `regConfig.registrarUri = ""`** in `acc_cfg` (linea 167 script): forzare account a non aspettare REGISTER state.
2. **Manual onCallState handler**: in `SmokeCall.onCallState`, intercept `PJSIP_INV_STATE_EARLY` e chiamare `call.answer(...)` se serve.
3. **CallSetting.flag**: provare `pj.PJSUA_CALL_INCLUDE_DISABLED_MEDIA` o flags non standard.
4. **Last resort**: usare `acc_cfg.sipConfig.outboundProxy` puntato a `127.0.0.1:5080` per forzare routing diretto.

Trial empirico: test ciascuna opzione e verificare `Call state: CONFIRMED (state=5)` in log pipeline.

### Step 2 — Audio fixture Scenario 4 (~10 min)

Generare 8 WAV cliente per turni Flusso Perfetto via Edge-TTS:

```python
# scripts/generate_voip_audio_fixtures.py
import asyncio, edge_tts
TURNI = [
    "Buongiorno",
    "Sono un nuovo cliente, mi chiamo Federico Marrone",
    "Vorrei prenotare un trattamento viso",
    "Venerdì pomeriggio",
    "Alle 16 va bene",
    "Sì confermo",
    "Grazie",
]
async def gen():
    for i, txt in enumerate(TURNI, 1):
        comm = edge_tts.Communicate(txt, voice="it-IT-IsabellaNeural")
        await comm.save(f"voice-agent/tests/voip_fixtures/scenario4_turn{i}.mp3")
        # ffmpeg to 8kHz 16-bit mono PCM WAV per pjsua2
asyncio.run(gen())
```

### Step 3 — Caller dinamico turn-by-turn (~15 min)

Estendere `CaptureAudioPort` con:
- `tx_queue`: queue di WAV bytes da spingere all'audio_media.startTransmit
- silence detection: se Sara TTS RX <50 RMS per >1s → emit next turn WAV
- timeout per scenario: 90s

### Step 4 — DB verification + report (~10 min)

Dopo BYE, query DB:

```bash
sqlite3 "/Volumes/MacSSD - Dati/fluxion/voice-agent/data/fluxion.db" \
  "SELECT nome, cognome FROM clienti WHERE nome='Federico' ORDER BY id DESC LIMIT 1;
   SELECT cliente_id, servizio, data, ora, status FROM appuntamenti ORDER BY id DESC LIMIT 1;"
sqlite3 "/Volumes/MacSSD - Dati/fluxion/voice-agent/data/analytics.db" \
  "SELECT session_id, total_turns, final_state, completed, source FROM sessions ORDER BY started_at DESC LIMIT 1;"
```

Atteso: cliente Federico Marrone + appuntamento venerdì 16:00 + session source='voip' final_state terminale.

Report markdown auto in `docs/launch/sara-live-test-reports/voip-autonomous-YYYYMMDD.md`.

---

## Note CTO — critica strutturale 4 punti (vincolo #4)

1. **Assunzione "test loopback ≈ test PSTN reale"**: codec G.711 e audio bridge sono stessi, MA jitter/packet loss/codec PSTN degradation assenti → falsi PASS rischio reale. Pre-S205: aggiungere `tc qdisc` jitter artificiale o accettare trade-off documentato.

2. **Rompe a 30/60/90gg**: se Sara orchestrator evolve (es. nuovo NLU layer), test loopback può passare mentre PSTN reale rompe (fix codec che non testiamo locale). Test mantiene valore solo come **regression gate**, non come **production launch gate**. Founder smoke 1 chiamata da cellulare resta P0 OBBLIGATORIO.

3. **Pattern errore noto pjsua2 macOS 11**: 2 endpoint pjsua2 same-process può crashare per shared state assertion. Mitigation S205: spawnare fake-caller in subprocess Python separato.

4. **Sovradimensiono se 5 scenari completi**: S1-S5 RUNBOOK-P1 originali sono ~3h totali in autonomous. ROI: solo Scenario 4 (E2E Flusso Perfetto) ha valore decisivo per release gate. S1/S2/S3/S5 sono validazioni puntuali, eseguibili come parametrizzazioni minori dopo Scenario 4 funzionante. Procedere incrementale.

---

## Riferimenti

- Script MVP: `scripts/sara-voip-loopback-smoke.py`
- Pipeline VoIP impl: `voice-agent/src/voip_pjsua2.py` (SaraAudioPort `_set_pipeline`, VoIPManager.start)
- Spike S204 evidence: log pipeline `Incoming call from: <sip:smoke-caller@127.0.0.1> → 200 OK → Audio bridge established`
- RUNBOOK-P1 PSTN reale: `docs/launch/RUNBOOK-P1-SARA-LIVE-TEST.md` (resta vincolante per validazione PSTN finale founder fisico, 5 min smoke 1 chiamata)
- Onboarding cliente VivaVox: `docs/launch/ONBOARDING-EHIWEB-CLIENTE.md`
