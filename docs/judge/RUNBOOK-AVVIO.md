# RUNBOOK AVVIO — Sara Voice Agent (:3002)

> Generato: 2026-07-30 | Task: T-B3-PROMOTE-r2 (#34v)
> Fonti: `restore.sh` (runtime catturato), `main.py` (verified), `launch_rig.sh` (rig analogy), `.env` (vars presenti)

---

## Comando esatto di avvio (VERIFICATO da restore.sh)

```bash
cd "/Volumes/MacSSD - Dati/fluxion/voice-agent"
set -a; . ".env"; set +a
# Per go engine (produzione con trunk):
VOICE_ENGINE=go \
nohup /Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python \
  main.py --port 3002 > /tmp/sara_3002.log 2>&1 &
echo "sara pid=$!"
```

**Python executable** (VERIFICATO in restore.sh, autogenerato da b3_open.sh):
`/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python`

**Working directory** (VERIFICATO in restore.sh):
`/Volumes/MacSSD - Dati/fluxion/voice-agent`

---

## Variabili d'ambiente richieste

Tutte caricate da `.env` nella working dir. Sovrascrivibili da shell.

| Variabile | Significato | Default | Fonte |
|-----------|-------------|---------|-------|
| `VOICE_ENGINE` | Selettore motore VoIP: `"pjsua2"` (default) o `"go"` | `pjsua2` | VERIFICATO main.py:1326 |
| `VOIP_SIP_USER` | Username SIP (es. numero EHIWEB). Se vuoto → VoIP disabilitato senza errori fatali | — | VERIFICATO main.py:1323 + .env |
| `VOIP_SIP_PASS` | Password SIP | — | VERIFICATO .env presente |
| `VOIP_SIP_SERVER` | Host SIP server (es. sip.ehiweb.it) | — | VERIFICATO .env presente |
| `VOIP_SIP_PORT` | Porta SIP (tipicamente 5060) | — | VERIFICATO .env presente |
| `VOIP_BRIDGE_PORT` | Porta bridge audio locale (go engine) | `8300` | VERIFICATO main.py:1334 |
| `VOIP_LOCAL_PORT` | Porta RTP locale (go engine) | DEDOTTO da launch_rig.sh (15090 su rig) | DEDOTTO |
| `VOIP_ENABLED` | Flag abilitazione VoIP (letto da .env) | — | VERIFICATO .env presente, uso in codice non esaminato |

**ATTENZIONE**: `VOIP_LOCAL_PORT` in produzione non è stata letta direttamente da `.env` produzione — il valore esatto è in `.env` su iMac, non verificato in questa sessione.

---

## Selettore VOICE_ENGINE (main.py:1326-1340, VERIFICATO)

```python
_voice_engine = os.getenv("VOICE_ENGINE", "pjsua2").strip().lower()
if _voice_engine == "go":
    from src.voip_goengine import GoEngineVoIPManager, SIPConfig
    voip_manager = GoEngineVoIPManager(voip_config, bridge_port=_bridge_port)
else:
    from src.voip_pjsua2 import VoIPManager, SIPConfig
    voip_manager = VoIPManager(voip_config)
```

`"go"` → `GoEngineVoIPManager` (motore esterno Go via bridge)
`"pjsua2"` (default) → `VoIPManager` pjsua2 (baseline storica, crash NDEBUG risolto S355)

---

## Porta e verifiche

| Cosa | Comando |
|------|---------|
| Health base | `curl -s http://127.0.0.1:3002/health` → JSON `{"status":"ok"}` |
| Status VoIP/SIP | `curl -s http://127.0.0.1:3002/api/voice/voip/status` → `{"registered":true,...}` |
| Greeting test | `curl -s -X POST http://127.0.0.1:3002/api/voice/process -H "Content-Type: application/json" -d '{"text":"Buongiorno"}'` |

---

## Spegnimento pulito

```bash
# Kill :3002
kill $(lsof -ti:3002 | head -1) 2>/dev/null || true
# Verifica DOWN
lsof -ti:3002 | wc -l   # deve essere 0
```

---

## Fix verificati nel codice corrente

| Fix | Descrizione | Evidenza (VERIFICATA) |
|-----|-------------|----------------------|
| FIX-A | Congedo senza «collega» | `escalation_manager.py:97`: "E6-FIX: congedo onesto — il salone richiamerà, Sara non promette un collega" |
| FIX-C | Conferma nome | `booking_state_machine.py:756`: `return "Mi conferma il nome corretto?"` |
| AI Disclosure | EU AI Act art.50 | `session_manager.py:743`: "AI-DISCLOSURE (founder GATE2): disclosure obbligatoria (EU AI Act art.50)" |

---

## Note operative

- **Dev MacBook** → non eseguire qui: nessun Python 3.9 compatibile, no venv voice-agent
- **Eseguire su iMac** via SSH: `ssh imac 'bash -s' < script.sh` oppure comandi diretti
- Il rig (`:3003`) usa regstub loopback e NON tocca il trunk EHIWEB — separato dalla produzione
- Produzione (`:3002`) legge `.env` con credenziali trunk reali → VOIP_SIP_SERVER punta a ehiweb
