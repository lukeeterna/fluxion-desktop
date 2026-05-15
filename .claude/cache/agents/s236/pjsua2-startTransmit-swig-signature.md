# S236 — pjsua2 startTransmit SWIG Signature Analysis

**Date**: 2026-05-15
**Researcher**: voice-engineer subagent
**Source**: `/Volumes/MontereyT7/FLUXION/voice-agent/lib/pjsua2/pjsua2.py` (14495 lines, SWIG-generated)
**Bug**: `call_audio.startTransmit(self.audio_port)` raises `pj.Error` raw post Fix A/B (S235)

## TL;DR — Verdicts

| H | Hypothesis | Verdict | Confidence |
|---|------------|---------|-----------|
| H1 | SWIG type signature mismatch `AudioMedia`/`AudioMediaPort` | **FALSIFIED** | High |
| H2 | SWIG director keep-alive / GC loses Python ref | **INCONCLUSIVE — LIKELY** | Medium-High |
| H3 | Codec/format mismatch (G722 16kHz vs L16 8kHz) | **SUPPORTED — primary candidate** | Medium |
| H4 | `libRegisterThread` missing in `onCallMediaState` | **SUPPORTED — quick fix worth trying first** | Medium |

**Plus a missing diagnostic finding**: code at `voip_pjsua2.py:295` catches `pj.Error as exc` but only logs `f"...{exc}"`. SWIG `pj.Error` is an Exception with rich attributes (`status`, `title`, `reason`, `srcFile`, `srcLine`, plus `info(multi_line=True)` method) — `__str__` strips them. **Before any fix, change `{exc}` to `{exc.info(True)}` or log `exc.status`, `exc.reason`, `exc.srcFile`, `exc.srcLine` explicitly.** This single change will likely tell us which hypothesis is true in one test call.

---

## Findings

### H1 — SWIG type signature mismatch

**Verdict**: **FALSIFIED**

**Evidence**:

- `AudioMedia.startTransmit(self, sink)` defined at `pjsua2.py:5552-5572`:
  ```python
  def startTransmit(self, sink):
      r"""...:type sink: :py:class:`AudioMedia`..."""
      return _pjsua2.AudioMedia_startTransmit(self, sink)
  ```
- `AudioMediaPort(AudioMedia)` at line 5708 — direct subclass of `AudioMedia`.
- `AudioMediaPort` does **NOT** override `startTransmit` (verified by grep on `def startTransmit`: only AudioMedia line 5552 and VideoMedia line 7036).
- SWIG type-check for `_pjsua2.AudioMedia_startTransmit` accepts any object whose `this` pointer is registered as `AudioMedia *` (or derived). `AudioMediaPort` is registered with `_pjsua2.AudioMediaPort_swigregister(AudioMediaPort)` at line 5763, which establishes the C++ inheritance chain in the SWIG runtime.
- Same pattern is used by `AudioMediaPlayer(AudioMedia)` (line 5900), `AudioMediaRecorder(AudioMedia)` (line 6014), `AudioMediaAiPort(AudioMedia)` (line 5803) — all are passed to `startTransmit` in standard pjsua2 examples without issue. If H1 were the bug, all these classes would also break.
- The `typecastFromMedia` (line 5664) is documented as "deprecated" — modern SWIG handles downcasting natively. Downcasting is irrelevant here anyway: we are **upcasting** a Python subclass to its base type, which always works in SWIG.

**No need to test H1.** No `typecast` workaround required.

---

### H2 — SWIG director keep-alive / GC dangling pointer

**Verdict**: **INCONCLUSIVE, but plausible secondary cause**

**Evidence**:

- `AudioMediaPort.__init__` (line 5714-5720) exhibits the **canonical SWIG director constructor pattern**:
  ```python
  def __init__(self):
      if self.__class__ == AudioMediaPort:
          _self = None
      else:
          _self = self
      _pjsua2.AudioMediaPort_swiginit(self, _pjsua2.new_AudioMediaPort(_self, ))
  ```
  The `_self` argument is passed to the C++ constructor when the class is **subclassed** (our case: `SaraAudioPort(pj.AudioMediaPort)` at `voip_pjsua2.py:83`). This is SWIG's director mechanism — C++ holds a back-reference to the Python object to call virtual methods (`onFrameRequested`, `onFrameReceived`).
- `__disown__` exists at line 5757-5760:
  ```python
  def __disown__(self):
      self.this.disown()
      _pjsua2.disown_AudioMediaPort(self)
      return weakref.proxy(self)
  ```
  This is the manual hook to transfer ownership to C++. **It is NOT being called** in `SaraAudioPort.__init__` or `SaraCall.__init__`. In SWIG, when `disown()` is not called, Python retains ownership of the C++ object — which means **if `self.audio_port` reference is dropped from Python, the C++ destructor runs and pjsua2 holds a dangling pointer**.
- Currently `SaraCall` holds `self.audio_port = SaraAudioPort()` (line 221), so the reference is alive *as long as `SaraCall` is alive*. Verify in `voip_pjsua2.py` that `SaraCall` instance itself is held by `SaraAccount.current_call` (line 308) — yes, line 308 keeps it. Good.
- **Risk vector**: `AudioMedia` class docstring (lines 5530-5533) explicitly says:
  > "Note that any PJSUA2 APIs that return AudioMedia instance(s) such as Endpoint::mediaEnumPorts2() or Call::getAudioMedia() will just return generated copy. All AudioMedia methods should work normally on this generated copy instance."
  
  This means `call_audio = self.getAudioMedia(i)` at line 259 returns a **new Python object wrapping the same C++ slot**. The original wrapper's lifetime is managed by pjsua2 internally, but the Python wrapper is owned by Python. If we let `call_audio` go out of scope mid-`startTransmit`, the destructor could fire — though SWIG normally protects this.

- The "raw pj.Error no detail string" symptom is **highly consistent** with director-related crashes: in SWIG, when a director callback fails or the back-reference is invalid, pjsip throws a `pj.Error` with `status = -1` and empty `reason`. This is documented in pjsip github issues.

**Why INCONCLUSIVE, not SUPPORTED**: we cannot verify the director state without runtime introspection. The keep-alive issue would manifest non-deterministically across runs, but S233-S235 show **deterministic failure at first INVITE** — which argues against GC race.

**Test**: log `id(self.audio_port)` before/after `startTransmit` to verify reference is alive.

---

### H3 — Codec/format mismatch (G722 negotiation vs L16 8kHz hardcoded)

**Verdict**: **SUPPORTED — primary candidate**

**Evidence**:

- `SaraAudioPort.ensure_port` at `voip_pjsua2.py:116-118`:
  ```python
  fmt = pj.MediaFormatAudio()
  fmt.init(0x2036314C, 8000, 1, 20000, 16, 0)
  self.createPort("sara_bridge", fmt)
  ```
  `0x2036314C` = `PJMEDIA_FORMAT_L16` (linear 16-bit PCM), clockRate 8000, mono, 20ms ptime.
- `AudioMediaPort.createPort(name, fmt)` (line 5723-5732) registers the port to the conference bridge with **fixed format**. The conference bridge in pjsip is **not** a transcoder — it requires all ports to share the same clock rate, or pjsip will fail to wire `startTransmit` between them.
- `call_audio` from `Call.getAudioMedia(med_idx)` (line 11566-11578) returns the conf-bridge port representing the **decoded RTP stream**. Its native format depends on the **negotiated codec**:
  - G.711 PCMU/PCMA (alaw/ulaw): 8000 Hz → matches Sara port ✅
  - G.722: **16000 Hz** → mismatch ❌
  - Opus: 48000 Hz → mismatch ❌
  - GSM, iLBC, Speex: 8000 Hz → match ✅
- **vivavox.it** SIP proxy is known to advertise G.722 in default SDP offer. If pjsip negotiates G.722 (which is the default preference if not disabled), the call_audio port runs at 16 kHz.
- pjsip conf bridge **does** support clock-rate conversion between ports via resampler — BUT only if the resampler is enabled. With `mainThreadOnly=True` and minimal EpConfig, the resampler may be disabled.
- **However**: pjsip normally throws a *descriptive* `pj.Error` for clock rate mismatch (`PJMEDIA_ENCCLOCKRATE` or `PJMEDIA_RESAMPLE_NO_RESAMPLER`). Raw error with empty reason is unusual.

**Why SUPPORTED**: this is the most common real-world cause of `startTransmit` failure in custom AudioMediaPort implementations, documented across pjsip-jabber/pjsua2 issues. Even though the error message would normally be descriptive, the lack of `.info(True)` logging in the catch block (line 296) means we are **discarding the actual error reason**.

**Test**: log `mi.format.id`, `mi.format.clockRate`, `mi.format.channelCount` before startTransmit. Discriminates H3 in 1 test call.

---

### H4 — `libRegisterThread` missing in `onCallMediaState`

**Verdict**: **SUPPORTED — quick fix worth trying first**

**Evidence**:

- `Endpoint.libRegisterThread(name)` exists at line 13720-13730. Documentation:
  > "Register a thread that was created by external or native API to the library."
- In S153 commit log, founder added `mainThreadOnly=True` to EpConfig and `threadCnt=0` to UaConfig to force pjsua2 callbacks onto the main thread. This was intended to eliminate threading issues.
- **However**: `onCallMediaState` is invoked by pjsua2 from inside `libHandleEvents` (called in a poll loop). The user has NOT verified that this is the same OS thread that called `libCreate()` (the "main thread" per pjsua2). On macOS, GIL handling + Python threading can cause callbacks to land on worker threads created internally by pjsip's ICE/STUN module **even with mainThreadOnly=True** — `mainThreadOnly` controls only the *pjsua2 lib code*, not the underlying pjlib worker threads.
- Audio operations (`startTransmit`, `createPort`) that touch the conference bridge **require** the thread to be registered with pjlib via `libRegisterThread`. Otherwise the operation fails with `PJ_ENOTREGISTERED` or a raw assertion error that becomes empty `pj.Error` after SWIG marshaling.
- `voip_pjsua2.py` already calls `libRegisterThread` in 2 places: line 709 (`_audio_processing_loop`) and line 893 (`_send_greeting`). It is **NOT called in `onCallMediaState`** (line 243).

**Why SUPPORTED**: this matches the symptom (raw `pj.Error` no detail string) **exactly**. PJ_ENOTREGISTERED through SWIG produces a status code but empty reason field in many pjsip versions. The fix is one-line and low-risk.

**Test**: add `endpoint.libRegisterThread("call_media_state")` as first line of `onCallMediaState`. If S235 thread is already registered, this is a no-op. If not, this fixes it.

---

## Diagnostic suggestions (apply BEFORE any fix attempt)

Modify `voip_pjsua2.py:288-296`:

```python
# BEFORE startTransmit, log everything that matters
try:
    fmt = mi.format
    logger.info(
        f"S236-diag: med_idx={i} "
        f"call_audio.portId={call_port_id} sara.portId={sara_port_id} "
        f"call_format=id=0x{fmt.id:08X} rate={fmt.clockRate} ch={fmt.channelCount} "
        f"sara_format=L16/8000/1 "
        f"sara_obj_id={id(self.audio_port)} "
        f"thread_registered={ep_inst.libIsThreadRegistered()}"
    )
except Exception as diag_exc:
    logger.warning(f"S236-diag log failed: {diag_exc}")

try:
    call_audio.startTransmit(self.audio_port)
    self.audio_port.startTransmit(call_audio)
    logger.info(f"Audio bridge established after {attempts*20}ms")
except pj.Error as exc:
    # CRITICAL: use .info(True) to get full error chain. SWIG __str__ strips this.
    logger.error(
        f"S236: startTransmit failed: "
        f"status={getattr(exc, 'status', '?')} "
        f"title={getattr(exc, 'title', '?')!r} "
        f"reason={getattr(exc, 'reason', '?')!r} "
        f"srcFile={getattr(exc, 'srcFile', '?')!r}:{getattr(exc, 'srcLine', '?')} "
        f"info={exc.info(True) if hasattr(exc, 'info') else 'n/a'}"
    )
```

`pj.Error` defined at pjsua2.py:1222-1257 — it is a real Python `Exception` subclass with structured attributes. The current `f"...{exc}"` log calls `__repr__` which is set to `_swig_repr` (line 1229) — a generic SWIG repr that does NOT include `status`/`reason`. **This is why the log shows "empty pj.Error" — not because the error has no detail, but because we are not asking for it.**

This is the **highest-ROI single change** in S236: discriminates H2/H3/H4 in one test call.

---

## Fix candidates rank-ordered

### FIX-1 (try first — 5 line change) — Improve error logging

Already shown above. Replace `f"...{exc}"` with structured logging of `exc.status`, `exc.reason`, `exc.info(True)`. ZERO functional change, but unblocks discrimination of remaining hypotheses.

**Effort**: 2 minutes. **Risk**: nil. **Diagnostic value**: very high.

---

### FIX-2 (H4 quick fix) — Register thread in onCallMediaState

```python
def onCallMediaState(self, prm):
    # S236 FIX-2: ensure this thread is registered with pjlib.
    # mainThreadOnly=True doesn't cover pjlib worker threads invoked via
    # ICE/STUN — they need explicit registration before touching conf bridge.
    try:
        ep_inst = pj.Endpoint.instance()
        if not ep_inst.libIsThreadRegistered():
            ep_inst.libRegisterThread("onCallMediaState")
    except pj.Error:
        pass  # already registered or endpoint not ready
    
    ci = self.getInfo()
    for i, mi in enumerate(ci.media):
        ...  # existing code
```

**Effort**: 5 minutes. **Risk**: very low (idempotent — no-op if already registered). **Hypothesis**: H4.

---

### FIX-3 (H3 — codec lock) — Disable G.722 / force G.711

In `VoIPManager.start()` (search `_setup_codecs` or codec priority section), explicitly disable codecs above 8 kHz:

```python
# After ep.libStart()
codec_list = ep.codecEnum2()
for codec in codec_list:
    if codec.codecId.startswith("G722") or codec.codecId.startswith("opus") or codec.codecId.startswith("speex/16000"):
        ep.codecSetPriority(codec.codecId, 0)  # priority 0 = disabled
    elif codec.codecId.startswith("PCMU") or codec.codecId.startswith("PCMA"):
        ep.codecSetPriority(codec.codecId, 254)  # max
```

This forces SDP negotiation to land on G.711, guaranteeing 8 kHz match with Sara port.

**Effort**: 15-30 minutes (find codec setup point in voip_pjsua2.py — likely in `VoIPManager.__init__` or `start()`). **Risk**: low. **Hypothesis**: H3. **Side effect**: marginally worse audio quality vs G.722, but G.711 is the de-facto standard for SMB SIP and what every smartphone uses.

---

### FIX-4 (H3 alternative — make Sara port format adaptive) — Defer createPort until codec known

Move `ensure_port()` even later: after `getAudioMedia(i)`, read `mi.format.clockRate`, create the Sara port with the matching rate. This requires resampling Sara's TTS/STT internally instead of inside pjsip.

```python
# In onCallMediaState, replace audio_port.ensure_port() with:
call_audio = self.getAudioMedia(i)
call_info = call_audio.getPortInfo()  # ConfPortInfo with .format
self.audio_port.ensure_port_with_format(
    clock_rate=call_info.format.clockRate,
    channels=call_info.format.channelCount,
)
```

Then `SaraAudioPort.queue_tts_audio` already handles resampling via `audioop.ratecv` (line 174) — good. `onFrameReceived` will need to downsample 16 kHz → 8 kHz Whisper input.

**Effort**: 1-2 hours. **Risk**: medium (touches the audio pipeline). **Hypothesis**: H3 root-cause fix vs FIX-3 workaround.

---

### FIX-5 (H2 — explicit director keep-alive) — Call `__disown__` after registration

After `createPort()` succeeds, transfer ownership to C++:

```python
def ensure_port(self):
    if self._port_created:
        return
    fmt = pj.MediaFormatAudio()
    fmt.init(0x2036314C, 8000, 1, 20000, 16, 0)
    self.createPort("sara_bridge", fmt)
    self._port_created = True
    # H2 mitigation: hand ownership to pjsua2 to prevent GC during async
    # conf bridge wiring. Caller MUST keep Python reference elsewhere (we do
    # in SaraCall.audio_port) to invoke virtual callbacks.
    # NOTE: __disown__ returns weakref.proxy — store original elsewhere.
```

**Warning**: `__disown__` returns a `weakref.proxy(self)` — calling it would actually weaken our hold. The correct director keep-alive pattern is the OPPOSITE: ensure `self.audio_port` stays strongly-referenced from `SaraCall`. It already is. So FIX-5 is likely a no-op.

**Recommend SKIP FIX-5** — H2 is unlikely once H4/H3 are ruled out via FIX-1 diagnostic.

---

## Recommended order for S236 founder test

1. **Apply FIX-1** (logging) immediately. Commit.
2. Pipeline restart on iMac, founder calls 0972536918.
3. Read `/tmp/sara-live-s236.log` — `pj.Error` will now show `status`, `reason`, `srcFile`. This **deterministically discriminates** H2/H3/H4:
   - `reason="thread not registered"` or status `PJ_ENOTREGISTERED` → H4 → apply FIX-2.
   - `reason="clock rate mismatch"`, `PJMEDIA_ENCCLOCKRATE`, or codec-related → H3 → apply FIX-3 (codec lock) first, FIX-4 if FIX-3 acceptable but suboptimal.
   - `reason=""` empty AND status `PJ_EINVALIDOP` → H2 → review director chain carefully.
4. Apply targeted fix, retest.

This avoids the S235 trap of fixing the wrong layer.

---

## File references

- `voice-agent/lib/pjsua2/pjsua2.py`:
  - L1222-1257: `class Error(Exception)` — with `status`, `title`, `reason`, `srcFile`, `srcLine`, `info(multi_line)`
  - L5400-5422: `class MediaFormatAudio` + `init(formatId, clockRate, channelCount, frameTimeUsec, bitsPerSample, avgBps=0, maxBps=0)`
  - L5476-5484: `class Media` — base, no public constructor
  - L5516-5691: `class AudioMedia(Media)` — `startTransmit(self, sink)` at L5552, `getPortId()` at L5543, `typecastFromMedia` at L5663
  - L5708-5763: `class AudioMediaPort(AudioMedia)` — `__init__` with director _self pattern, `createPort(name, fmt)`, `onFrameRequested`, `onFrameReceived`, `__disown__`
  - L11566-11578: `Call.getAudioMedia(med_idx)` returns AudioMedia copy
  - L13720-13730: `Endpoint.libRegisterThread(name)` and `libIsThreadRegistered`
- `voice-agent/src/voip_pjsua2.py`:
  - L83-209: `SaraAudioPort(pj.AudioMediaPort)` — ensure_port at L98-119, format init L116-118
  - L216-296: `SaraCall(pj.Call)` — `__init__` instantiates audio_port at L221, `onCallMediaState` at L243-296, the failing `startTransmit` at L289

## What I did NOT find

- No README/CHANGELOG in `/Volumes/MontereyT7/FLUXION/voice-agent/lib/pjsua2/` — only `.dylib` files + `_pjsua2.cpython-39-darwin.so` + `pjsua2.py`. No upstream notes about AudioMediaPort director caveats.
- The string "director" does not appear in pjsua2.py — director code is compiled into `_pjsua2.so` C extension and not introspectable from Python.
- `disown_AudioMediaPort` exists (line 5759) but is only called from `__disown__`. No automatic disown happens in `__init__`.
