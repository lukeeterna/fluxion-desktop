# S237 — Prompt ripartenza (handoff S236 → S237)

**Generato**: 2026-05-15 09:30 (chiusura S236 ORANGE — diagnostic patch landed, smoking gun catturato, root cause specifico isolato, fix richiede research nuova categoria)
**Branch**: master @ `db47cc5b` (MacBook + iMac sync)
**Pipeline iMac**: STOPPED clean (PID 57419 killed end S236)

## TL;DR S236 outcome

- ✅ **Diagnostic patch landed** (commit `db47cc5b`): structured `pj.Error` logging via `_pj_error_info()` helper + MRO/refcount/format introspection + `libRegisterThread` H4 mitigation
- ✅ **Pipeline UP**: VOIP_LOCAL_PORT=6080, SIP REGISTER 200 OK su sip.vivavox.it
- ✅ **Test live founder** 09:25:47 — smoking gun catturato per la prima volta in 3 sessioni (S234-S236)
- ❌ **Bug persiste**: founder sente "Vodafone telefono spento"
- 🎯 **Root cause isolato**: `pjsua_conf_connect(id, sink.id)` C-level rifiuta con `status=506784` (range pjsua errno 500000-509999)

## Smoking gun S236 (`/tmp/sara-live-s236-final.log` iMac, cache extract `.claude/cache/agents/s236/live-test-log-extract.txt`)

```
09:25:47  Incoming call from: <sip:3281536308@79.98.45.133>
09:25:47  S236 DIAG H1: call_audio=AudioMedia mro=['AudioMedia','Media','object'] |
          audio_port=SaraAudioPort mro=['SaraAudioPort','AudioMediaPort','AudioMedia','Media','object']
09:25:47  S236 DIAG H2: audio_port id=4590478576 refcount=2 _port_created=True
09:25:47  S236 DIAG H3: call.format clockRate=8000 ch=1 bits=16 frameUsec=20000 |
          sara.format clockRate=8000 ch=1 bits=16 frameUsec=20000
09:26:02  ERROR: S236: startTransmit failed structured |
          status=506784 title='pjsua_conf_connect(id, sink.id)'
          reason='Unknown error 506784'
          srcFile='../src/pjsua2/media.cpp' srcLine=235 |
          info=Title: pjsua_conf_connect(id, sink.id)
```

**Gap 15s** tra H3 log e error → `pjsua_conf_connect` blocca C-side ~14.5s prima di fallire. Vodafone timeout su no-answer.

## Discrimination 4 hypothesis S236 (definitiva)

| H | Verdict | Evidence |
|---|---------|----------|
| **H1** SWIG signature | FALSIFIED | MRO `[SaraAudioPort, AudioMediaPort, AudioMedia, Media, object]` — upcast OK |
| **H2** Director keep-alive | SUSPECT | refcount=2 (solo SaraCall.audio_port ref) — Python GC pressure possibile |
| **H3** Codec/format mismatch | FALSIFIED | call.format ≡ sara.format (8000/1/16/20000us perfect) |
| **H4** libRegisterThread | MITIGATO | aggiunto in onCallMediaState, ma bug persiste |

## Hypothesis nuove S237 (rank-ordered post-diagnostic)

### **N1 (TOP) — pjsua_conf_connect status 506784 lookup**
`status=506784` cade nel range **pjsua errno** (500000-509999) ma `reason='Unknown error 506784'` significa pjsua2 strerror table non ha mapping per questo specifico codice → custom Python AudioMediaPort path. Decodificare:
```bash
grep -rn "506784\|6784" /Volumes/MontereyT7/FLUXION/voice-agent/lib/pjsua2/ 2>/dev/null
# Source pjsip: cerca PJSUA_E* defines in pjsua-lib/pjsua_errno.h
# Possibili: PJSUA_E_NO_ACCESS, PJSUA_E_TOO_SMALL, PJSUA_E_PORT_NOT_FOUND etc.
```
Forse decode via `pj_strerror(506784, buf, sizeof(buf))` se pjsua2 espone — verificare.

### **N2 — pjmedia vs pjsua conf bridge namespace mismatch**
Custom `pj.AudioMediaPort.createPort()` chiama `pjmedia_conf_add_port()` (low-level pjmedia bridge). `AudioMedia.startTransmit(sink)` chiama `pjsua_conf_connect()` (high-level pjsua bridge). I due usano **port ID namespace diversi** → anche se `getPortId()` ritorna ID valido, pjsua_conf_connect non lo trova nella sua tabella → status=506784 = "port not in pjsua bridge".

**Test**: cercare in pjsua2 docs/source se esiste `pjsua_conf_add_port()` API esplicita o se `AudioMediaPort` deve essere passato a `Endpoint.audDevManager().getConferenceBridge()` per registrarsi nel pjsua-level bridge.

### **N3 — pjsua_conf_connect blocking 15s**
Gap 14.5s tra entry e error → `pjsua_conf_connect` blocca C-level. Possibile motivo: pjsua bridge in attesa di clock sync con call leg che non arriva mai (clock mismatch invisible). Connesso a N2.

### **N4 — H2 lifetime + community pattern**
Move `self.audio_port` da `SaraCall` (transient) a `SaraAccount.active_ports` list (long-lived). Pattern Agent 2 Example A. Anche se non risolve N2, riduce GC pressure.

## Plan S237

### Pre-flight
1. `ssh imac "lsof -ti:3002 || echo PIPELINE_DOWN_OK"`
2. Verificare commit `db47cc5b` MacBook + iMac sync

### Step 1 — Decode status 506784 (5 min)
- Grep pjsua2.py + lib/pjsua2/include/ per PJSUA_E* defines numerici (se headers presenti)
- WebFetch GitHub pjsip `pjsua-lib/pjsua_errno.h` raw + grep `PJSUA_E` → trovare mapping 506784
- Output: `.claude/cache/agents/s237/pjsua-errno-506784-mapping.md`

### Step 2 — Verificare pjmedia vs pjsua bridge (subagent voice-engineer)
Cerca in `voice-agent/lib/pjsua2/pjsua2.py` (14495 righe) e pjsua2 C++ wrapper sources se disponibili:
- `class AudioMediaPort`: cosa fa `createPort()` esattamente? Chiama `pjmedia_conf_add_port` o `pjsua_conf_add_port`?
- `class AudioMedia`: cosa fa `startTransmit()`? `pjmedia_conf_connect_port` o `pjsua_conf_connect`?
- Se mismatch confermato → cercare API corretta per registrare custom port in pjsua bridge

Output: `.claude/cache/agents/s237/pjmedia-vs-pjsua-bridge-namespace.md`

### Step 3 — Fix candidato rank-ordered
- **F1 (se N2 confermato)**: usare `Endpoint.instance().audDevManager()` per registrare port. O usare `AudioMediaPlayer`/`AudioMediaRecorder` built-in instead of custom subclass.
- **F2 (se N4)**: spostare `self.audio_port` su `SaraAccount.active_ports` list
- **F3 (escape hatch)**: ctypes diretto a `pjsua_conf_connect(src_pjmedia_id, sink_pjsua_id)` bypassando SWIG — ~30 righe codice. Discutere founder cost/benefit.

### Step 4 — Apply + test
Atomic commit + push + sync + restart + founder retest. Verificare log `S236 DIAG` cambia (no più error structured).

### Step 5 — Escape hatch se nessun fix funziona
Considerare switch engine SIP:
- **opzione A**: `python-pjsip` (legacy v1) — pattern noto stabile per custom audio
- **opzione B**: SIP server esterno (Asterisk/FreeSWITCH) + Sara come WebSocket client — più affidabile, costo zero
- **opzione C**: SIP via `pjsua2 + AudioMediaPlayer/Recorder` (built-in, no director pattern) + bridge audio out-of-band

## File modificati S236

- `voice-agent/src/voip_pjsua2.py` — diagnostic patch (commit `db47cc5b`)
- `.claude/cache/agents/s236/pjsua2-startTransmit-swig-signature.md` — report Agent 1 voice-engineer (300+ righe)
- `.claude/cache/agents/s236/live-test-log-extract.txt` — log eventi diagnostici (6 righe)
- `.claude/NEXT_SESSION_PROMPT.manual.md` — questo file

## Comando one-liner ripartenza S237

```
Sessione S237 FLUXION. Leggi MEMORY.md "Stato Corrente S236" + .claude/NEXT_SESSION_PROMPT.manual.md + .claude/cache/agents/s236/live-test-log-extract.txt. Smoking gun: pjsua_conf_connect status=506784 a media.cpp:235 (range pjsua errno 500000-509999), gap 15s C-blocking. H1/H3 falsified, H2 suspect (refcount=2), H4 mitigato. Plan S237: (1) decode 506784 via grep pjsua_errno.h sources, (2) verificare pjmedia vs pjsua bridge namespace mismatch (subagent voice-engineer), (3) fix rank-ordered F1/F2/F3 con escape hatch ctypes o switch python-pjsip.
```
