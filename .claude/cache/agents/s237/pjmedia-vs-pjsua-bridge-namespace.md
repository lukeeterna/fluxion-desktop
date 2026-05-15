# S237 — pjmedia vs pjsua bridge namespace mismatch (N2 hypothesis)

## TL;DR — verdict

**N2 FALSIFIED** (high confidence — direct evidence from pjsua2 wrapper sources).
Both `AudioMediaPort::createPort()` and `AudioMedia::startTransmit()` operate on the
**same pjsua conference bridge** (`pjsua_var.mconf`) via the same family of `pjsua_conf_*`
APIs. There is no namespace split.

**Actual root cause (high confidence)**: `pjsua_conf_connect2()` in `pjsua_aud.c`
implicitly tries to **open the local sound device** (Core Audio microphone/speaker on
iMac) the FIRST time it is invoked, because the pipeline never called
`Endpoint.audDevManager().setNullDev()` (or `setNoDev()`). On the headless iMac via SSH,
opening Core Audio blocks ~14.5 s (matches the observed 15 s gap), then returns a
device-layer error encoded outside the pjsua named ranges (value `506784` falls in the
"reserved" zone between `PJMEDIA_AUDIODEV_ERRNO_END=469999` and
`PJMEDIA_VIDEODEV_ERRNO_START=520000`, hence `reason='Unknown error 506784'` — the
pjsua2 strerror table has no mapping for it).

Confidence: **N2 falsification = 0.98**, **sound-device hypothesis = 0.85** (would need
the pipeline log line `Conf connect: SRC --> SINK` followed by an `open_snd_dev` /
`pjsua_set_snd_dev` failure trace to lock it to 1.0; this is the next diagnostic move).

---

## Evidence — pjsua2 wrapper (pjsip/src/pjsua2/media.cpp@master)

```cpp
// L233-L236  — startTransmit calls pjsua_conf_connect
void AudioMedia::startTransmit(const AudioMedia &sink) const PJSUA2_THROW(Error)
{
    PJSUA2_CHECK_EXPR( pjsua_conf_connect(id, sink.id) );
}

// L382-L424 — AudioMediaPort::createPort builds a pjmedia_port then registers via
// registerMediaPort2 (the SAME bridge used by startTransmit)
void AudioMediaPort::createPort(const string &name, MediaFormatAudio &fmt) ...
{
    ...
    pjmedia_port_info_init2(&port->info, &name_,
                            PJMEDIA_SIG_CLASS_APP ('A', 'M', 'P'),
                            PJMEDIA_DIR_ENCODING_DECODING, &fmt_);
    ...
    registerMediaPort2(port, pool);
}

// L175-L191 — registerMediaPort2 calls pjsua_conf_add_port (NOT pjmedia_conf_add_port).
// Same global pjsua conf bridge that pjsua_conf_connect targets.
void AudioMedia::registerMediaPort2(MediaPort port, pj_pool_t *pool) ...
{
    ...
    PJSUA2_CHECK_EXPR( pjsua_conf_add_port(pool,
                                           (pjmedia_port *)port,
                                           &id) );
    Endpoint::instance().mediaAdd(*this);
}
```

Both code paths (`createPort` and `startTransmit`) end up in the **pjsua** bridge layer.
There is no parallel registration in any pjmedia-only table. **N2 dies here.**

---

## Where `506784` actually comes from

`pjsua_conf_connect2` body (pjsua_aud.c@master, L966-L1118) — non-mswitch branch
(default):

```c
} else {
    /* The bridge version */

    /* Create sound port if none is instantiated */
    if (pjsua_var.snd_port==NULL && pjsua_var.null_snd==NULL &&
        !pjsua_var.no_snd)
    {
        status = pjsua_set_snd_dev(pjsua_var.cap_dev, pjsua_var.play_dev);
        if (status != PJ_SUCCESS) {
            pjsua_perror(THIS_FILE, "Error opening sound device", status);
            goto on_return;
        }
    }
    ...
}
```

`voip_pjsua2.py` initializes the endpoint at L576-L610 (`libCreate / libInit / libStart`),
but never calls `self._ep.audDevManager().setNullDev()`. So on first `startTransmit`:

1. `pjsua_var.snd_port == NULL` ✓
2. `pjsua_var.null_snd == NULL` ✓ (no `setNullDev`)
3. `pjsua_var.no_snd == 0` ✓ (no `setNoDev`)
4. → `pjsua_set_snd_dev` triggers Core Audio open on iMac via SSH (no aux input device,
   or audio HAL needs ~15 s to enumerate before failing).
5. → `status` set to a Core-Audio-derived value that lands at `506784` (above
   audiodev space, no string mapping → "Unknown error 506784").

Timing fits perfectly: the 15 s gap between `onCallMediaState` entry and exception is the
Core Audio open blocking before returning an error.

`getPortId()` returning a valid id is irrelevant — both ports ARE in the bridge; the
failure is the prerequisite snd-dev open.

---

## Errno-space mapping for status 506784

| Range | Symbol | Span |
|-------|--------|------|
| 70000–119999 | `PJ_ERRNO_START_STATUS` | pjlib pj_status |
| 120000–169999 | `PJ_ERRNO_START_SYS` | OS errno wrapped |
| 170000–219999 | `PJSIP_ERRNO_START` | SIP statuses + PJSIP |
| 220000–269999 | `PJMEDIA_ERRNO_START` | pjmedia core |
| 270000–319999 | `PJMEDIA_CODEC_ERRNO_START` | codecs |
| 370000–419999 | `PJNATH_ERRNO_START` | ICE/STUN/TURN |
| 420000–469999 | `PJMEDIA_AUDIODEV_ERRNO_START` | audiodev (incl. PortAudio @459999-469998) |
| **470000–519999** | **(unnamed gap)** | **← 506784 falls here** |
| 520000–569999 | `PJMEDIA_VIDEODEV_ERRNO_START` | viddev |

`pjmedia-audiodev/errno.h` L44-L62 sets `PJMEDIA_AUDIODEV_ERRNO_START = PJ_ERRNO_START_USER + PJ_ERRNO_SPACE_SIZE*5 = 420000` with end at 469999. PortAudio mapping is
`PJMEDIA_AUDIODEV_ERRNO_END - 10000 = 459999` and `FROM_PORTAUDIO(err) = 459999 - err`
(PortAudio errors are non-positive). PortAudio's range therefore lands at 459999–469998.

`pjmedia-videodev/errno.h` L44-L45: `PJMEDIA_VIDEODEV_ERRNO_START = USER + SPACE*7 = 520000`.

`506784` is in neither named range — it is most likely a Core-Audio-specific encoding
produced by the macOS audio dev backend (or a wrapped negative OSStatus) that does not
have an entry in pjsua2's `errstr` table → `reason='Unknown error 506784'`.

This is fully consistent with a sound-device open failure path.

---

## Fix candidate (rank-ordered, surgical)

### F1 — Disable local audio device (RECOMMENDED, smallest patch)

In `voip_pjsua2.py`, immediately after `self._ep.libStart()` (L610), add:

```python
# Headless daemon: no local mic/speaker. Use pjsua null audio bridge so that
# pjsua_conf_connect() does NOT try to open Core Audio (causes 15s block + status
# 506784 on macOS via SSH). Pipeline produces/consumes audio via SaraAudioPort only.
try:
    self._ep.audDevManager().setNullDev()
    logger.info("pjsua2: null audio device set (headless mode)")
except pj.Error as e:
    logger.error(f"setNullDev failed: {_pj_error_info(e)}")
    raise
```

`setNullDev()` is the documented pjsua2 API to install a null master port (pjsua2
docstring L6902 of generated wrapper: "AudDevManager::setNullDev() … will act as a
master port"). After this, `pjsua_var.null_snd != NULL` → the `if` block at
`pjsua_aud.c` L1085 is skipped → no Core Audio open → `pjmedia_conf_connect_port` runs
directly → `startTransmit` returns synchronously in microseconds.

Alternative API: `setNoDev()` (L6313 wrapper). Difference: `setNullDev` installs a real
null port (clock ticks the bridge), `setNoDev` skips entirely. For a headless agent
processing call audio, `setNullDev` is safer — keeps the conference clock alive for
codec timing.

### F2 — Confirm with logs before patching

Run iMac pipeline with PJSIP log level ≥ 4 (default already) and look for:

```
Conf connect: <src_id> --> <sink_id>
Error opening sound device: ...
```

If those two lines appear before the `startTransmit failed` traceback, F1 is the right
fix. If not, fall back to F3.

### F3 — Alternative: use null transport explicitly via libInit

In `pj.EpConfig` set `medConfig.noVad`/`audioFramePtime` to defaults (already done) and
use `pj.MediaConfig` with `audio_frame_ptime=20` — no API there to skip snd dev at init,
so this reduces to F1.

### F4 — Last-resort ctypes bypass

If F1 fails (extremely unlikely): wrap a direct `ctypes` call to `pjmedia_conf_connect_port(pjsua_var.mconf, src_id, sink_id, 0)` bypassing `pjsua_conf_connect2` entirely. NOT recommended — F1 is the idiomatic pjsua2 path used by every headless pjsua2 example.

---

## Why earlier hypotheses missed this

- **H1 SWIG signature**: correctly falsified, port MRO is fine.
- **H2 director keep-alive**: red herring — refcount=2 is normal for a Python-held
  SWIG director.
- **H3 codec/format mismatch**: matched (8000/1/16/20000us) — was never the issue.
- **H4 libRegisterThread**: harmless safety net, didn't address the snd-dev open.

The 15 s gap was treated as "C-blocking on `pjsua_conf_connect`" — true, but the
*reason* it blocked is `pjsua_set_snd_dev` underneath, not the conf-connect logic itself.

---

## References (file:line, master branch unless noted)

- `pjproject/pjsip/src/pjsua2/media.cpp` L148-L207 (registerMediaPort, registerMediaPort2, unregisterMediaPort)
- `pjproject/pjsip/src/pjsua2/media.cpp` L233-L236 (`AudioMedia::startTransmit` → `pjsua_conf_connect`)
- `pjproject/pjsip/src/pjsua2/media.cpp` L382-L424 (`AudioMediaPort::createPort` → `registerMediaPort2`)
- `pjproject/pjsip/src/pjsua-lib/pjsua_aud.c` L966-L1118 (`pjsua_conf_connect2` body, sound-device open at L1085)
- `pjproject/pjmedia/include/pjmedia-audiodev/errno.h` L44-L62 (audiodev errno space 420000-469999, PortAudio 459999-469998)
- `pjproject/pjmedia/include/pjmedia-videodev/errno.h` L44-L45 (videodev errno space 520000-569999)
- `voice-agent/lib/pjsua2/pjsua2.py` L5516-L5691 (AudioMedia SWIG wrapper)
- `voice-agent/lib/pjsua2/pjsua2.py` L5708-L5763 (AudioMediaPort SWIG wrapper)
- `voice-agent/lib/pjsua2/pjsua2.py` L6305-L6311 (`AudDevManager.setNullDev`)
- `voice-agent/lib/pjsua2/pjsua2.py` L6313-L6323 (`AudDevManager.setNoDev`)
- `voice-agent/src/voip_pjsua2.py` L576-L611 (endpoint init, **missing setNullDev call**)
