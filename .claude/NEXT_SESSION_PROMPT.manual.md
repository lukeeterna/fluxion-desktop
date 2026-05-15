# S236 — Prompt ripartenza (handoff S235 → S236)

**Generato**: 2026-05-15 (chiusura S235 ORANGE — Fix B+A applicato, guard discriminante, bug persiste con ipotesi nuova rank-ordered)
**Branch**: master @ `28ddbd03` (MacBook + iMac sync)
**Pipeline iMac**: STOPPED clean (PID 58312 killed end S235)

## TL;DR S235 outcome

- ✅ **Fix B (lazy createPort) + Fix A (getPortId guard)** applicati e validati syntactically (commit `28ddbd03`)
- ✅ **Pipeline UP** con VOIP_LOCAL_PORT=6080, SIP REGISTER 200 OK
- ✅ **Test live discriminate**: guard `getPortId` ha trovato slot READY (loop exit pre-timeout) → ipotesi race timing FALSIFICATA
- ❌ **`startTransmit` ancora fallisce** con `pj.Error` raw senza detail dopo che gli slot erano ready
- ❌ **Gap 16s identico a S234**: 08:33:18 INVITE → 08:33:34 error+DISCONNECTED → caller sente "Vodafone telefono spento"

## Smoking gun S235 (`/tmp/sara-live-s235.log` iMac)

```
08:33:18  Incoming call from 3281536308
08:33:34  ERROR: S235: startTransmit failed even after slot ready: (empty pj.Error)
08:33:34  Call state: CONNECTING → CONFIRMED → DISCONNECTED
08:33:34  Audio processing loop started (ma RTP NON flusha)
```

**Importante**: il log "Audio bridge established: call(slot=N) ↔ Sara(slot=M) after Xms" che indicava successo Fix A NON appare. Appare invece il branch `startTransmit failed even after slot ready` → significa che gli slot erano valid, ma `call_audio.startTransmit(self.audio_port)` ha tirato `pj.Error` raw vuoto.

## Hypothesis raffinate S236 (rank-ordered)

### **H1 (TOP) — SWIG type signature mismatch**
`pj.AudioMedia.startTransmit(sink: pj.AudioMedia)` accetta `AudioMedia` per il sink. `SaraAudioPort` deriva da `pj.AudioMediaPort` che deriva da `pj.AudioMedia`. SWIG director può non castare correttamente Python subclass→`AudioMedia` base type → `pj.Error` raw silente.

**Test discriminante**:
```python
# In onCallMediaState, prima di startTransmit:
logger.info(f"audio_port type: {type(self.audio_port).__mro__}")
# Verifica MRO contiene pj.AudioMedia
# Se non contiene → SWIG inheritance broken
```

**Fix candidato**: typecast esplicito o passare via registry helper.

### **H2 — SWIG director keep-alive**
`SaraAudioPort` Python subclass passa attraverso director pattern SWIG. Se Python GC libera reference prima che pjsua2 conf_bridge la usi → dangling pointer C++ → crash silente come `pj.Error`.

**Fix candidato**: tenere `self.audio_port` in una lista globale `_active_audio_ports` (vita garantita pari a pipeline).

### **H3 — Codec/format mismatch**
SaraAudioPort: 8kHz L16 mono (`0x2036314C`, 160 samples/20ms). Call_audio potrebbe arrivare in G722 (16kHz). Vivavox.it default codec da verificare.

**Test discriminante**:
```python
# log mi.format clock_rate, channel_count
# log codec negoziato
ci = self.getInfo()
for codec in ci.callInfo.callInfo.... # API exact
```

### **H4 — `ep.libRegisterThread()` mancante**
Anche `mainThreadOnly=True` non garantisce che `startTransmit` invocato Python-side sia su pjsua2 thread. Ma se Fix A guard `getPortId()` ha funzionato sullo stesso scope, H4 è meno probabile (entrambe chiamano native pjsua2).

## Plan S236

### Pre-flight
1. `ssh imac` verify pipeline DOWN: `lsof -ti:3002 || echo PIPELINE_DOWN_OK`
2. NO prune MEMORY (162 righe, già fatto S235)

### Step 1 — Research subagent paralleli
- **agent-1** `debugger`: WebSearch + WebFetch su `pjsua2 python AudioMediaPort startTransmit silent error director swig`. Cerca pattern GitHub Issues per object lifetime / director keep-alive. Output `.claude/cache/agents/s236/pjsua2-director-keepalive.md`
- **agent-2** `voice-engineer`: leggi `voice-agent/lib/pjsua2/pjsua2.py` SWIG bindings (~12000 righe, focus `class AudioMedia` + `class AudioMediaPort` + `def startTransmit`). Output `.claude/cache/agents/s236/pjsua2-startTransmit-swig-signature.md`

### Step 2 — Diagnostic logging (NON fix ancora, raccogli evidenza prima)
Edit `voip_pjsua2.py:onCallMediaState`, aggiungi PRIMA di startTransmit:
```python
logger.info(f"S236 DIAG: audio_port mro={type(self.audio_port).__mro__}")
logger.info(f"S236 DIAG: call_audio type={type(call_audio).__name__}, id={id(call_audio)}")
logger.info(f"S236 DIAG: sara_port id={id(self.audio_port)}, _port_created={self.audio_port._port_created}")
logger.info(f"S236 DIAG: media format clock_rate={mi.format.clock_rate if hasattr(mi, 'format') else 'N/A'}")
```
Commit "diag(S236)" → push → sync iMac → restart pipeline → founder ri-chiama 0972536918.

### Step 3 — Discriminazione
Analizza log per scegliere fix:
- MRO non contiene `pj.AudioMedia` → applica H1 fix (typecast)
- id audio_port cambia fra chiamate → applica H2 (registry globale)
- clock_rate != 8000 → applica H3 (audio resample dinamico)

### Step 4 — Apply fix + test
Atomic commit + push + sync + restart + founder retest.

### Step 5 — Se persiste
Fallback ctypes approccio diretto `pjsua_conf_connect()` o discutere con founder switch a engine SIP più semplice (PJSIP CLI Python wrapper vs SWIG bindings).

## File modificati S235

- `voice-agent/src/voip_pjsua2.py` (Fix B + Fix A applicati commit `28ddbd03`)
- `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md` (prune 1994→162 + S235 stato corrente)
- `.claude/cache/agents/s235/voip-audio-bridge-analysis.md` (Agent 1 report 380 righe)
- `.claude/cache/agents/s235/pjsua2-startTransmit-failures.md` (Agent 2 report ~330 righe, esiste su filesystem non committato)
- `.claude/NEXT_SESSION_PROMPT.manual.md` (questo file)

## Comando one-liner ripartenza S236

```
Sessione S236 FLUXION. Leggi MEMORY.md "Stato Corrente sessione 235" + .claude/NEXT_SESSION_PROMPT.manual.md. Bug pjsua2 audio bridge persiste dopo Fix B+A (S235): startTransmit fallisce dopo slot ready. 4 hypothesis raffinate (H1 SWIG typecast, H2 director keep-alive, H3 codec mismatch, H4 libRegisterThread). Plan: 2 subagent paralleli research SWIG bindings → diagnostic logging commit "diag(S236)" → test live discriminate → fix mirato.
```
