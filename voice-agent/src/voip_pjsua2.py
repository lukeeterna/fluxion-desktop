"""
FLUXION Voice Agent - VoIP Module (pjsua2)

Production-grade SIP/VoIP using pjsua2 (pjsip SWIG bindings).
Replaces the hand-rolled voip.py with industry-standard NAT traversal,
codec negotiation, jitter buffer, and RTP transport.

Architecture:
  Phone → EHIWEB SIP → pjsua2 (ICE/STUN/RTP) → SaraAudioPort → Sara Pipeline
  Sara Pipeline → SaraAudioPort → pjsua2 RTP → EHIWEB → Phone
"""

import asyncio
import audioop
import concurrent.futures
import faulthandler
import io
import logging
import os
import queue
import struct
import sys
import threading
import time
import wave
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)

# S238 FIX F2: dump backtrace of ALL Python threads on SIGABRT.
# The pjlib grp_lock_unset_owner_thread assertion (lock.c:279) fires from a
# C-side abort() before Python can raise. Without all_threads=True, the
# traceback only shows the aborting thread; we need every thread's stack to
# identify which Python thread did the cross-thread lock release.
if not faulthandler.is_enabled():
    faulthandler.enable(file=sys.stderr, all_threads=True)


def _run_with_pjlib_registration(name: str, target: Callable, *args, **kwargs):
    """S238 FIX F2: thread entrypoint that registers itself with pjlib before
    invoking the real callback.

    Root cause S237 post-F1: SaraCall.onCallState spawns Python daemon threads
    on CONFIRMED / DISCONNECTED that immediately touch self.audio_port (via
    queue_tts_audio, clear_tx, getInfo). Any pjsua2 SWIG director call into
    C can take a pj_grp_lock; if released from a non-registered thread,
    pj_thread_this() returns NULL → grp_lock_unset_owner_thread assertion
    → SIGABRT (S237 smoking gun).

    libRegisterThread is idempotent in pjlib (returns PJ_SUCCESS or already-
    registered status). Safe to call once per thread lifetime.

    S352: routed through _register_thread_if_needed so a thread pjlib already
    tracks (media/clock threads) is NOT re-registered (TLS desc overwrite →
    grp_lock owner corruption → lock.c:279 SIGABRT).
    """
    _register_thread_if_needed(name)
    target(*args, **kwargs)


def _pjlib_thread_initializer():
    """S239 FIX F3: ThreadPoolExecutor `initializer=` hook.

    Registers every TPE worker thread with pjlib once at spawn time so that
    any subsequent pjsua2 SWIG-director call from that worker (TTS chunk
    enqueue, STT post-processing, groq calls, whatsapp helpers, etc.) does
    not produce a cross-thread `pj_grp_lock` release assertion.

    Root cause S238 (faulthandler dump,
    .claude/cache/agents/s238/faulthandler-analysis.md):
    `_pjsua2_thread` aborts inside `libHandleEvents` because two unregistered
    `concurrent.futures.thread._worker` threads previously acquired
    `pj_grp_lock` via SWIG director paths. When `_pjsua2_thread` (registered)
    attempts the release, `pj_thread_this()` returns a value that does not
    match the C-side owner identity -> `grp_lock_unset_owner_thread`
    assertion (lock.c:279) -> SIGABRT.

    `libRegisterThread` is idempotent in pjlib. Safe even if called before
    `Endpoint` exists (the inner exception is swallowed and the worker still
    runs; it just remains unregistered until next spawn).
    """
    # S352: skip re-registration if pjlib already tracks this thread.
    _register_thread_if_needed(f"sara_tpe_{threading.get_ident()}")


def _install_pjlib_aware_default_executor(loop: asyncio.AbstractEventLoop) -> None:
    """S239 FIX F3: replace asyncio's default ThreadPoolExecutor with one
    whose worker threads self-register with pjlib at spawn time.

    Why: every call site in voice-agent/src/ that uses
    `loop.run_in_executor(None, ...)` or `asyncio.to_thread(...)` shares the
    same default executor (audit S239 step 1). Without an initializer, those
    workers touch pjsua2 SWIG director objects (TTS audio chunk enqueue,
    STT post-processing into call media, etc.) without `pj_thread_register`,
    causing the cross-thread group-lock assertion observed in S238.

    Must be called AFTER `Endpoint.libCreate()` + `libStart()` so the
    initializer's `Endpoint.instance()` resolves successfully. Old default
    executor (if any) is shut down `wait=False` so in-flight non-pjsua2
    tasks (Edge-TTS pre-warm HTTP) complete naturally.
    """
    new_executor = concurrent.futures.ThreadPoolExecutor(
        max_workers=32,  # matches asyncio 3.9 default ceiling
        thread_name_prefix="asyncio-pjlib",
        initializer=_pjlib_thread_initializer,
    )
    old_executor = getattr(loop, "_default_executor", None)
    loop.set_default_executor(new_executor)
    if old_executor is not None:
        try:
            old_executor.shutdown(wait=False)
        except Exception as exc:
            logger.debug(f"S239 F3: old default executor shutdown raised (non-fatal): {exc!r}")
    logger.info("S239 F3: asyncio default executor replaced with pjlib-registered TPE")


# Add pjsua2 lib path
_PJSUA2_LIB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "lib", "pjsua2")
if _PJSUA2_LIB_DIR not in sys.path:
    sys.path.insert(0, _PJSUA2_LIB_DIR)

# Set DYLD_LIBRARY_PATH for macOS dynamic libraries
if sys.platform == "darwin":
    existing = os.environ.get("DYLD_LIBRARY_PATH", "")
    if _PJSUA2_LIB_DIR not in existing:
        os.environ["DYLD_LIBRARY_PATH"] = _PJSUA2_LIB_DIR + (":" + existing if existing else "")

import pjsua2 as pj


def _register_thread_if_needed(name: str) -> None:
    """S352: register the calling thread with pjlib ONLY if not already
    registered. Calling libRegisterThread on a thread pjlib already knows
    (e.g. pjmedia-internal clock/media threads like `onCallMediaS`) overwrites
    its pj_thread_desc in TLS, corrupting group-lock owner identity →
    grp_lock_unset_owner_thread assertion (lock.c:279) → SIGABRT. The smoking
    gun was the pjlib log line "possibly re-registering existing thread".
    libIsThreadRegistered() lets us register ONLY genuine Python threads that
    pjlib does not yet track, and skip the already-registered media threads."""
    try:
        ep = pj.Endpoint.instance()
        if not ep.libIsThreadRegistered():
            ep.libRegisterThread(name)
    except pj.Error:
        pass
    except Exception:
        pass


def _pj_error_info(exc: "pj.Error") -> str:
    """S236: safely extract structured detail from pj.Error.

    pj.Error has .info(multi_line) method returning full diagnostic string
    (status code + title + reason + srcFile + srcLine + stack). Default
    f"{exc}" calls SWIG _swig_repr which drops these fields, producing the
    "empty pj.Error" symptom observed in S234 + S235.
    """
    try:
        return exc.info(True)
    except Exception as e:
        return f"<info() unavailable: {e!r} | repr={exc!r}>"


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class SIPConfig:
    """EHIWEB SIP configuration."""
    server: str = "sip.vivavox.it"
    port: int = 5060
    username: str = ""
    password: str = ""
    local_port: int = 5090  # 5060=Traccar, 5080=old voip.py
    stun_server: str = "stun.voip.vivavox.it:3478"
    user_agent: str = "FLUXION-Sara/1.0"
    # D4: TURN server for CGNAT traversal (~20% of Italian PMI behind CGNAT)
    turn_server: str = ""      # e.g. "turn:turn.example.com:3478"
    turn_username: str = ""
    turn_password: str = ""
    # E7: UDP keepalive interval (seconds) for CGNAT NAT binding refresh
    keepalive_interval: int = 15

    @classmethod
    def from_env(cls) -> "SIPConfig":
        return cls(
            server=os.getenv("VOIP_SIP_SERVER", os.getenv("EHIWEB_SIP_SERVER", "sip.vivavox.it")),
            port=int(os.getenv("VOIP_SIP_PORT", os.getenv("EHIWEB_SIP_PORT", "5060"))),
            username=os.getenv("VOIP_SIP_USER", os.getenv("EHIWEB_SIP_USER", "")),
            password=os.getenv("VOIP_SIP_PASS", os.getenv("EHIWEB_SIP_PASS", "")),
            local_port=int(os.getenv("VOIP_LOCAL_PORT", "5080")),
            turn_server=os.getenv("VOIP_TURN_SERVER", ""),
            turn_username=os.getenv("VOIP_TURN_USER", ""),
            turn_password=os.getenv("VOIP_TURN_PASS", ""),
            keepalive_interval=int(os.getenv("VOIP_KEEPALIVE_INTERVAL", "15")),
        )


# =============================================================================
# Audio Bridge: pjsua2 ↔ Sara Pipeline
# =============================================================================

class SaraAudioPort(pj.AudioMediaPort):
    """Bridges pjsua2 conference bridge with Sara voice pipeline.

    - onFrameReceived: caller audio → rx_queue → Sara STT
    - onFrameRequested: Sara TTS → tx_queue → caller
    """

    def __init__(self):
        super().__init__()
        self.rx_queue = queue.Queue(maxsize=500)   # Caller speech → Sara (10s)
        self.tx_queue = queue.Queue(maxsize=3000)  # Sara speech → caller (60s)
        self._silence_frame = b'\x00' * 320        # 20ms silence at 8kHz 16-bit mono
        self._current_tx_rms = 0.0                 # S142: RMS of current TX frame for barge-in
        self._port_created = False                 # S235 FIX B: lazy createPort
        # S237 FIX F1-bis: pjlib group lock owner thread tracking.
        # onFrameRequested/onFrameReceived are invoked at 50Hz by a pjlib audio worker
        # thread (created C-side when conf bridge starts pulling frames). That thread is
        # NOT registered with pjlib by default → pj_thread_this() returns NULL →
        # grp_lock_unset_owner_thread assertion fires (lock.c:279) → SIGABRT.
        # Pre-F1 this was masked because Core Audio open blocked startTransmit. Post-F1
        # the bridge starts, callbacks fire, assertion explodes on first frame.
        self._thread_local = threading.local()

    def _ensure_thread_registered(self):
        """Idempotent thread registration with pjlib. Called from audio callbacks.
        Uses threading.local() to register exactly once per worker thread."""
        if getattr(self._thread_local, "registered", False):
            return
        # S352: register only if pjlib does not already track this thread
        # (audio callbacks may run on a pjmedia-internal thread). threading.local
        # guard avoids the libIsThreadRegistered round-trip at 50Hz once handled.
        _register_thread_if_needed(f"sara_audio_cb_{threading.get_ident()}")
        self._thread_local.registered = True

    def ensure_port(self):
        """S235 FIX B: lazy createPort, invoked from onCallMediaState only.

        Calling createPort() inside __init__ registers the port with the
        pjsua2 conference bridge before SDP O/A negotiation has completed.
        This creates a timing window where onCallMediaState fires but the
        port's bridge slot is still PJSUA_INVALID_ID, causing startTransmit
        to raise raw pjsua2.Error with no detail (SWIG strips status text).

        Deferring registration to onCallMediaState ensures the call leg has
        active media before we touch the conference bridge.
        """
        if self._port_created:
            return
        # 8kHz, mono, 160 samples/frame (20ms), 16-bit
        # Format ID 0x2036314C = PJMEDIA_FORMAT_L16 (linear 16-bit PCM)
        # Use init() to properly initialize all internal fields (type, detail_type)
        # Manual field assignment leaves detail_type unset, causing assertion crash
        fmt = pj.MediaFormatAudio()
        fmt.init(0x2036314C, 8000, 1, 20000, 16, 0)
        self.createPort("sara_bridge", fmt)
        self._port_created = True

    def onFrameReceived(self, frame):
        """Called by pjsua2 when audio arrives from the phone call."""
        self._ensure_thread_registered()  # S237 F1-bis: register pjlib worker thread once
        if frame.type == pj.PJMEDIA_FRAME_TYPE_AUDIO:
            try:
                self.rx_queue.put_nowait(bytes(frame.buf))
            except queue.Full:
                pass  # Drop oldest if full (real-time priority)

    def onFrameRequested(self, frame):
        """Called by pjsua2 when it needs audio to send to the caller."""
        self._ensure_thread_registered()  # S237 F1-bis: register pjlib worker thread once
        try:
            audio_data = self.tx_queue.get_nowait()
            frame.type = pj.PJMEDIA_FRAME_TYPE_AUDIO
            frame.buf = pj.ByteVector(audio_data)
            # S142: Track TX RMS for barge-in detection
            self._current_tx_rms = self._calc_frame_rms(audio_data)
        except queue.Empty:
            # Send silence when Sara has nothing to say
            frame.type = pj.PJMEDIA_FRAME_TYPE_AUDIO
            frame.buf = pj.ByteVector(self._silence_frame)
            self._current_tx_rms = 0.0

    @staticmethod
    def _calc_frame_rms(pcm_data: bytes) -> float:
        """Calculate RMS of a single PCM frame (fast, used in audio callback)."""
        if len(pcm_data) < 2:
            return 0.0
        n = len(pcm_data) // 2
        total = 0
        for i in range(n):
            s = struct.unpack_from('<h', pcm_data, i * 2)[0]
            total += s * s
        return (total / n) ** 0.5

    def queue_tts_audio(self, audio_data: bytes, src_rate: int = 16000):
        """Queue TTS audio for playback to caller.

        Handles WAV parsing, resampling to 8kHz, and chunking into 20ms frames.
        """
        pcm_data = audio_data

        # Parse WAV header if present
        if audio_data[:4] == b"RIFF":
            try:
                wav_io = io.BytesIO(audio_data)
                with wave.open(wav_io, 'rb') as wf:
                    src_rate = wf.getframerate()
                    pcm_data = wf.readframes(wf.getnframes())
            except Exception as exc:
                logger.warning(f"WAV parse failed: {exc}, using raw at {src_rate}Hz")

        # Resample to 8kHz if needed
        if src_rate != 8000:
            pcm_data, _ = audioop.ratecv(pcm_data, 2, 1, src_rate, 8000, None)

        # Chunk into 20ms frames (320 bytes = 160 samples * 2 bytes)
        chunk_size = 320
        for i in range(0, len(pcm_data), chunk_size):
            chunk = pcm_data[i:i + chunk_size]
            if len(chunk) < chunk_size:
                chunk = chunk + b'\x00' * (chunk_size - len(chunk))
            try:
                self.tx_queue.put_nowait(chunk)
            except queue.Full:
                break  # Don't block, skip remaining

    def get_caller_audio(self, timeout: float = 0.5) -> Optional[bytes]:
        """Get accumulated caller audio (for STT processing).

        Returns PCM 8kHz 16-bit mono, or None if no audio available.
        """
        chunks = []
        try:
            while True:
                chunks.append(self.rx_queue.get_nowait())
        except queue.Empty:
            pass

        if chunks:
            return b''.join(chunks)
        return None

    def clear_tx(self):
        """Clear pending TTS audio (e.g., when caller interrupts)."""
        while not self.tx_queue.empty():
            try:
                self.tx_queue.get_nowait()
            except queue.Empty:
                break


# =============================================================================
# Deferred bridge wiring (S243 T1)
# =============================================================================

@dataclass
class _PendingBridge:
    """Bridge-wiring work item produced by onCallMediaState, consumed by
    _pjsua2_thread's main poll loop OUTSIDE pjsip callback dispatch context.

    Why a dataclass instead of a tuple: makes the drain loop self-documenting
    and allows future fields (retry_count, deadline) without refactor.
    """
    call: "SaraCall"
    call_audio: "pj.AudioMedia"
    media_index: int
    enqueued_at: float
    attempts: int = 0
    MAX_ATTEMPTS: int = 25       # 25 * 20ms tick = 500ms total slot wait
    completed: bool = False


# =============================================================================
# SIP Call Handler
# =============================================================================

class SaraCall(pj.Call):
    """Handles an incoming SIP call, bridging audio to Sara."""

    def __init__(self, acc, call_id=pj.PJSUA_INVALID_ID):
        super().__init__(acc, call_id)
        self.account = acc                # S243 T2: explicit back-reference for cleanup
        self.audio_port = SaraAudioPort()
        self.connected = False
        self.on_connected = None   # Callback: call connected
        self.on_disconnected = None  # Callback: call ended

    def onCallState(self, prm):
        ci = self.getInfo()
        state = ci.state
        logger.info(f"Call state: {ci.stateText} (state={state})")

        if state == pj.PJSIP_INV_STATE_CONFIRMED:
            self.connected = True
            if self.on_connected:
                # S153: With mainThreadOnly=True, callbacks run on pjsua2 thread.
                # Still use separate thread for on_connected because it starts
                # long-running audio processing that would block libHandleEvents.
                # S238 FIX F2: wrap with pjlib thread registration. The on_connected
                # callback touches self.audio_port via SWIG director proxies that
                # take pj_grp_lock internally; an unregistered thread releasing
                # those locks triggers lock.c:279 SIGABRT (S237 blocker).
                threading.Thread(
                    target=_run_with_pjlib_registration,
                    args=("sara_audio_processor", self.on_connected, self),
                    daemon=True,
                ).start()
        elif state == pj.PJSIP_INV_STATE_DISCONNECTED:
            self.connected = False
            # S243 T2: release long-lived account references AFTER C-side teardown.
            # We schedule the removal one tick later via the account's drain queue
            # so any in-flight conf bridge teardown can complete first.
            try:
                self.account._schedule_call_release(self)
            except Exception as exc:
                logger.warning(f"S243 T2: _schedule_call_release raised: {exc!r}")
            if self.on_disconnected:
                # S238 FIX F2: same registration wrapper as on_connected above.
                threading.Thread(
                    target=_run_with_pjlib_registration,
                    args=("sara_disconnect_handler", self.on_disconnected, self),
                    daemon=True,
                ).start()

    def onCallMediaState(self, prm):
        # S352: onCallMediaState runs on the pjmedia thread (`onCallMediaS`)
        # which pjlib ALREADY registered. Re-registering it here was the root
        # cause of the lock.c:279 SIGABRT (TLS pj_thread_desc overwrite). Skip
        # if already tracked.
        _register_thread_if_needed("onCallMediaState")

        # S243 T1: NO startTransmit here. Stash the work and let
        # _pjsua2_thread.drain_pending_bridges() execute it outside the
        # pjsip callback dispatch (which holds upstream call/dialog locks).
        # This breaks the lock inversion that produces the cross-thread
        # grp_lock release assertion at the next libHandleEvents tick.
        #
        # S243 T1.5: NO blocking sleep loop here either. The slot-readiness
        # poll moves into the drainer so we don't starve libHandleEvents
        # for up to 500ms inside a callback.
        ci = self.getInfo()
        for i, mi in enumerate(ci.media):
            if mi.type == pj.PJMEDIA_TYPE_AUDIO and \
               mi.status == pj.PJSUA_CALL_MEDIA_ACTIVE:
                # S235 FIX B: lazy createPort on pjsua2 main thread.
                try:
                    self.audio_port.ensure_port()
                except pj.Error as exc:
                    logger.error(
                        f"S236: ensure_port failed | "
                        f"info={_pj_error_info(exc)}"
                    )
                    continue

                try:
                    call_audio = self.getAudioMedia(i)
                except pj.Error as exc:
                    logger.warning(
                        f"S236: getAudioMedia({i}) failed | "
                        f"info={_pj_error_info(exc)}"
                    )
                    continue

                # S236 DIAG H1/H2/H3: introspection (kept for forensic logging).
                try:
                    import sys as _sys
                    call_mro = [c.__name__ for c in type(call_audio).__mro__][:5]
                    port_mro = [c.__name__ for c in type(self.audio_port).__mro__][:5]
                    logger.info(
                        f"S236 DIAG H1: call_audio={type(call_audio).__name__} "
                        f"mro={call_mro} | "
                        f"audio_port={type(self.audio_port).__name__} mro={port_mro}"
                    )
                    logger.info(
                        f"S236 DIAG H2: audio_port id={id(self.audio_port)} "
                        f"refcount={_sys.getrefcount(self.audio_port)} "
                        f"_port_created={self.audio_port._port_created}"
                    )
                    call_pinfo = call_audio.getPortInfo()
                    sara_pinfo = self.audio_port.getPortInfo()
                    cf = call_pinfo.format
                    sf = sara_pinfo.format
                    logger.info(
                        f"S236 DIAG H3: call.format clockRate={cf.clockRate} "
                        f"ch={cf.channelCount} bits={cf.bitsPerSample} "
                        f"frameUsec={cf.frameTimeUsec} | "
                        f"sara.format clockRate={sf.clockRate} ch={sf.channelCount} "
                        f"bits={sf.bitsPerSample} frameUsec={sf.frameTimeUsec}"
                    )
                except Exception as _diag_exc:
                    logger.warning(f"S236 DIAG introspection failed: {_diag_exc}")

                # S243 T1: enqueue deferred bridge wiring on the account.
                # _pjsua2_thread.drain_pending_bridges() will pick this up
                # at the next tick and execute startTransmit there.
                pending = _PendingBridge(
                    call=self,
                    call_audio=call_audio,
                    media_index=i,
                    enqueued_at=time.time(),
                )
                self.account._pending_bridges.append(pending)
                logger.info(
                    f"S243 T1: bridge wiring enqueued (media_idx={i}, "
                    f"queue_depth={len(self.account._pending_bridges)})"
                )


# =============================================================================
# SIP Account
# =============================================================================

class SaraAccount(pj.Account):
    """SIP account that handles incoming calls for Sara."""

    def __init__(self):
        super().__init__()
        self.current_call: Optional[SaraCall] = None
        self.on_incoming_call = None  # Callback for VoIPManager
        self.on_reg_state = None      # Callback for registration state
        # S243 T1: deferred bridge wiring queue, drained by _pjsua2_thread.
        # NOT a threading.Queue — single producer (pjsua callback thread)
        # and single consumer (_pjsua2_thread main loop); a plain list
        # under the GIL is sufficient and avoids needless contention.
        self._pending_bridges: list = []
        # S243 T2: long-lived references to prevent premature GC of SaraCall
        # and SaraAudioPort SWIG director objects. Removed on
        # PJSIP_INV_STATE_DISCONNECTED via _schedule_call_release().
        self.active_calls: list = []
        self._released_calls: list = []   # awaiting next-tick removal

    def onRegState(self, prm):
        info = self.getInfo()
        is_registered = info.regIsActive
        logger.info(f"Registration: active={is_registered}, status={info.regStatus} {info.regStatusText}")
        if self.on_reg_state:
            self.on_reg_state(is_registered, info.regStatus)

    def onIncomingCall(self, prm):
        call = SaraCall(self, prm.callId)
        ci = call.getInfo()
        logger.info(f"Incoming call from: {ci.remoteUri}")

        # Only handle one call at a time
        if self.current_call and self.current_call.connected:
            logger.warning("Already in a call, rejecting new call")
            call_prm = pj.CallOpParam()
            call_prm.statusCode = 486  # Busy Here
            call.answer(call_prm)
            return

        self.current_call = call
        # S243 T2: long-lived reference, prevents SWIG director GC during call.
        self.active_calls.append(call)

        if self.on_incoming_call:
            self.on_incoming_call(call)

    # =========================================================================
    # S243 T2 helpers
    # =========================================================================

    def _schedule_call_release(self, call: "SaraCall") -> None:
        """Queue a SaraCall for removal from active_calls. The actual list
        mutation happens in drain_call_releases() on _pjsua2_thread, AFTER
        the next libHandleEvents tick so any pending C-side teardown
        (conf bridge port unregister, transport unref) completes first."""
        if call not in self._released_calls:
            self._released_calls.append(call)

    def drain_call_releases(self) -> None:
        """Called once per _pjsua2_thread tick. Idempotent."""
        if not self._released_calls:
            return
        to_release = self._released_calls
        self._released_calls = []
        for call in to_release:
            try:
                if call in self.active_calls:
                    self.active_calls.remove(call)
            except ValueError:
                pass
        # Drop dangling current_call reference if it matches a released one.
        if self.current_call is not None and self.current_call not in self.active_calls:
            self.current_call = None

    def drain_pending_bridges(self) -> None:
        """S243 T1 + T1.5: execute startTransmit() OUTSIDE callback dispatch.
        Called once per _pjsua2_thread tick (every 20ms). Each pending entry
        waits up to MAX_ATTEMPTS ticks for slot assignment, then wires the
        bridge bidirectionally. Removed when completed or expired."""
        if not self._pending_bridges:
            return
        remaining: list = []
        for pending in self._pending_bridges:
            if pending.completed:
                continue
            try:
                call = pending.call
                if not call or not getattr(call, "audio_port", None):
                    continue
                # If call already torn down, skip silently.
                try:
                    ci = call.getInfo()
                    if ci.state == pj.PJSIP_INV_STATE_DISCONNECTED:
                        logger.info("S243 T1: bridge wiring skipped — call disconnected")
                        continue
                except pj.Error:
                    continue

                call_audio = pending.call_audio
                audio_port = call.audio_port
                call_slot = call_audio.getPortId()
                sara_slot = audio_port.getPortId()

                if call_slot == pj.PJSUA_INVALID_ID or sara_slot == pj.PJSUA_INVALID_ID:
                    pending.attempts += 1
                    if pending.attempts >= pending.MAX_ATTEMPTS:
                        logger.error(
                            f"S243 T1: bridge slot not assigned after "
                            f"{pending.attempts * 20}ms "
                            f"(call={call_slot}, sara={sara_slot}) — dropping"
                        )
                        continue
                    remaining.append(pending)
                    continue

                # Slots ready — wire the bridge bidirectionally.
                # This is the critical operation that previously fired the
                # grp_lock_unset_owner_thread assertion when invoked from
                # onCallMediaState callback context. Now executed in
                # _pjsua2_thread's main loop, OUTSIDE callback dispatch.
                try:
                    call_audio.startTransmit(audio_port)
                    audio_port.startTransmit(call_audio)
                    pending.completed = True
                    wait_ms = pending.attempts * 20
                    logger.info(
                        f"S243 T1: Audio bridge established (deferred): "
                        f"call(slot={call_slot}) ↔ Sara(slot={sara_slot}) "
                        f"after {wait_ms}ms wait"
                    )
                except pj.Error as exc:
                    logger.error(
                        f"S243 T1: deferred startTransmit failed | "
                        f"info={_pj_error_info(exc)}"
                    )
            except Exception as exc:
                logger.error(f"S243 T1: drain iteration raised: {exc!r}", exc_info=True)
        self._pending_bridges = remaining


# =============================================================================
# VoIPManager — Drop-in replacement for voip.py VoIPManager
# =============================================================================

class VoIPManager:
    """Production-grade VoIP manager using pjsua2.

    Same interface as the old voip.py VoIPManager:
    - start() / stop()
    - set_pipeline(pipeline)
    - get_status() / hangup()
    """

    def __init__(self, config: Optional[SIPConfig] = None):
        self.config = config or SIPConfig.from_env()
        self.pipeline = None
        self._running = False
        self._registered = False
        self._reg_status = 0
        self._main_loop: Optional[asyncio.AbstractEventLoop] = None  # Main aiohttp event loop

        # pjsua2 objects (created in _pj_thread)
        self._ep: Optional[pj.Endpoint] = None
        self._account: Optional[SaraAccount] = None
        self._transport_id = -1

        # pjsua2 runs in its own thread (it has its own event loop)
        self._pj_thread: Optional[threading.Thread] = None
        self._pj_started = threading.Event()
        self._pj_stop = threading.Event()

        # Audio processing
        self._audio_thread: Optional[threading.Thread] = None
        self._hangup_pending = False  # L5: Prevent multiple hangup threads
        self._current_call: Optional[SaraCall] = None

        # Simple energy-based VAD for caller speech detection
        # S140: Tuned for Italian telephony turn-taking (research: vad-barge-in-research.md)
        self._vad_speech_frames = 0
        self._vad_silence_frames = 0
        self._vad_speech_threshold = 600   # S140: 500→600 — rejects phone line noise (200-400 RMS)
        self._vad_silence_timeout = 50     # S143: 75→50 — 50 frames * 20ms = 1000ms silence
                                           # 1500ms was too slow for natural Italian turn-taking

    def set_pipeline(self, pipeline):
        """Set voice pipeline for processing incoming calls."""
        self.pipeline = pipeline

    async def start(self) -> bool:
        """Start VoIP service (SIP registration + listen for calls)."""
        if self._running:
            return True

        if not self.config.username or not self.config.password:
            logger.error("VoIP: SIP credentials not configured")
            return False

        # Capture the main event loop — coroutines must run here (httpx, groq, etc.)
        self._main_loop = asyncio.get_running_loop()

        # Start pjsua2 in background thread
        self._pj_thread = threading.Thread(target=self._pjsua2_thread, daemon=True)
        self._pj_thread.start()

        # Wait for initialization (max 10s)
        if not self._pj_started.wait(timeout=10):
            logger.error("VoIP: pjsua2 initialization timeout")
            return False

        # S239 FIX F3: Endpoint is up (libCreate + libStart completed inside
        # `_pjsua2_thread`); now replace the asyncio default executor with a
        # pjlib-aware one so every subsequent run_in_executor / to_thread
        # worker registers with pjlib at spawn time. This closes the S238
        # `grp_lock_unset_owner_thread` SIGABRT root cause (faulthandler dump
        # showed unregistered concurrent.futures _worker threads holding
        # pj_grp_lock at the moment _pjsua2_thread attempted release).
        _install_pjlib_aware_default_executor(self._main_loop)

        # Wait a bit for registration
        await asyncio.sleep(3)

        if self._registered:
            self._running = True
            logger.info(f"VoIP started: {self.config.username}@{self.config.server}")
            return True
        else:
            logger.warning(f"VoIP: SIP registration pending (status={self._reg_status})")
            # Still consider it started — registration may complete later
            self._running = True
            return True

    async def stop(self):
        """Stop VoIP service."""
        if not self._running:
            return

        self._pj_stop.set()
        self._running = False

        if self._pj_thread:
            self._pj_thread.join(timeout=5)
            self._pj_thread = None

        logger.info("VoIP service stopped")

    async def hangup(self) -> bool:
        """End current call."""
        if self._current_call and self._current_call.connected:
            try:
                call_prm = pj.CallOpParam()
                self._current_call.hangup(call_prm)
                return True
            except Exception as exc:
                logger.error(f"Hangup error: {exc}")
                return False
        return False

    def get_status(self) -> Dict[str, Any]:
        """Get VoIP status."""
        return {
            "running": self._running,
            "sip": {
                "registered": self._registered,
                "reg_status": self._reg_status,
                "username": self.config.username,
                "server": self.config.server,
            },
            "rtp_active": self._current_call is not None and self._current_call.connected,
            "engine": "pjsua2",
        }

    # =========================================================================
    # pjsua2 Thread (runs pjsip event loop)
    # =========================================================================

    def _pjsua2_thread(self):
        """Background thread running pjsua2 endpoint."""
        try:
            # S244 DIAG: redirect stderr to /tmp/sara-pjsip-s244.log so
            # pjsip C-side assertion dumps + buffered stderr flush land
            # in the same file as pjsua logConfig output. Without dup2,
            # Python stderr buffer drops the last events on SIGABRT.
            import os as _os, sys as _sys
            try:
                _s244_fd = _os.open("/tmp/sara-pjsip-s244.log",
                                    _os.O_WRONLY | _os.O_CREAT | _os.O_APPEND,
                                    0o644)
                _os.dup2(_s244_fd, _sys.stderr.fileno())
                _os.close(_s244_fd)
            except Exception as _e:
                logger.warning(f"S244 stderr dup2 failed: {_e}")
            self._init_pjsua2()
            self._pj_started.set()

            # Event loop — poll pjsua2 every 20ms
            while not self._pj_stop.is_set():
                self._ep.libHandleEvents(20)
                # S243 T1/T2: drain deferred work OUTSIDE callback dispatch.
                if self._account is not None:
                    self._account.drain_pending_bridges()
                    self._account.drain_call_releases()

            # Cleanup
            self._cleanup_pjsua2()

        except Exception as exc:
            logger.error(f"pjsua2 thread error: {exc}", exc_info=True)
            self._running = False  # E2: Don't leave VoIP in zombie state
            self._pj_started.set()  # Unblock start() even on failure

    def _init_pjsua2(self):
        """Initialize pjsua2 endpoint, transport, and account."""
        # Create endpoint
        self._ep = pj.Endpoint()
        self._ep.libCreate()

        # Endpoint config
        ep_cfg = pj.EpConfig()
        ep_cfg.uaConfig.userAgent = self.config.user_agent
        ep_cfg.uaConfig.stunServer.append(self.config.stun_server)
        # S244 FIX T3: revert threadCnt=1 (S240 T0) → threadCnt=0 retry.
        #
        # Smoking gun S244 (.claude/cache/agents/s244/sara-pjsip-s244.log,
        # decor=0xFFFF + level=5):
        #
        #   pjsua_0       Add port 1 (sip:...@79.98.45.133) queued    [19:33:06.309]
        #   pjsua_0       Info: possibly re-registering existing thread [19:33:06.309]
        #   onCallMediaS  Add port 2 (sara_bridge) queued              [19:33:06.311]
        #   *** Assertion failed: (glock->owner == pj_thread_this()),
        #       function grp_lock_unset_owner_thread, file lock.c, line 279 ***
        #
        # Diagnosi: due thread (pjsua_0 worker C-side + _pjsua2_thread/
        # onCallMediaState Python) operano sullo stesso pjmedia_conf op queue
        # refactorato in 2.16-dev (`Add port N queued` invece di sync
        # `Conf add port N` di 2.15.1). Group lock owner mismatch al queue
        # processing → assertion → SIGABRT. Il log esplicito 'possibly
        # re-registering existing thread' su os_core_unix.c PRIMA del crash
        # conferma double-register su stesso pthread_self() tra pjsua_0
        # nativo e libRegisterThread Python.
        #
        # Eliminare pjsua_0 (threadCnt=0 + mainThreadOnly=True) chiude il race
        # per costruzione: tutto il dispatch pjsua avviene su _pjsua2_thread
        # via libHandleEvents(20). Niente cross-thread su pjmedia_conf.
        #
        # S153 deadlock (reinv_timer_cb) NON ricomparirà — era causato da TPE
        # workers Python non registrati con pjlib che acquisivano grp_lock
        # via SWIG director. F1-bis (audio callbacks SaraAudioPort), F2
        # (on_connected/on_disconnected _run_with_pjlib_registration wrap),
        # F3 (asyncio default TPE pjlib-aware initializer), F1-S237 (setNullDev
        # pre-startTransmit), T1/T1.5/T2 (bridge wiring deferred fuori
        # onCallMediaState) chiudono ogni Python thread che possa ricevere
        # callback pjsua2 o toccare pjmedia objects.
        #
        # Falsificazione attesa nel log post-T3:
        #   - Sparisce thread name `pjsua_0` dai decor=0xFFFF
        #   - "Add port 1" e "Add port 2" entrambi su `_pjsua2_thread`
        #     (o `onCallMediaS` che sotto mainThreadOnly=True è lo stesso)
        #   - Sparisce "possibly re-registering existing thread"
        #   - Bridge wiring completato, audio bidirezionale funzionante
        #
        # Se T3 fallisce stesso pattern (assertion lock.c:279 ricompare):
        #   → significa che il refactor 2.16-dev pjmedia_conf op_queue è rotto
        #     a livello strutturale anche single-thread (pjmedia clock thread
        #     C-side fire callback indipendentemente da uaConfig.threadCnt)
        #   → procedere con B1 downgrade pjsip 2.15.1 (runbook in
        #     .claude/NEXT_SESSION_PROMPT.manual.md)
        #   → NO retry C (ctypes thread_local_get) o D (Asterisk ARI) stasera,
        #     anti-pattern S159 vale: nessun switch architetturale a fine
        #     sessione esausta
        ep_cfg.uaConfig.threadCnt = 0
        ep_cfg.uaConfig.mainThreadOnly = True
        # S244 DIAG: pjsip log level 5 (verbose) + filename to capture
        # last pjmedia event before SIGABRT grp_lock_unset_owner_thread.
        # Discriminates N1 (pjmedia clock master) vs N2 (conf event) vs
        # other surfaces. decor=0xFFFF prints thread name + microseconds.
        ep_cfg.logConfig.level = 5
        ep_cfg.logConfig.consoleLevel = 5
        try:
            ep_cfg.logConfig.filename = "/tmp/sara-pjsip-s244.log"
            ep_cfg.logConfig.fileFlags = 0  # truncate on each run
            # Decor bitmask: year+month+day+time+micro+thread_name+thread_id
            ep_cfg.logConfig.decor = 0xFFFF
        except Exception as _e:
            logger.warning(f"S244 logConfig optional fields unavailable: {_e}")

        # No sound device needed — we use AudioMediaPort for Sara bridge
        ep_cfg.medConfig.noVad = True
        # Disable SRTP — not needed for EHIWEB VoIP, avoids SRTP self-test
        # failure when running as headless daemon
        ep_cfg.medConfig.srtpUse = 0  # PJMEDIA_SRTP_DISABLED

        try:
            self._ep.libInit(ep_cfg)
        except pj.Error as e:
            logger.error(f"pjsua2 libInit failed: {e.info()}")
            raise

        # Create UDP transport
        tp_cfg = pj.TransportConfig()
        tp_cfg.port = self.config.local_port
        self._transport_id = self._ep.transportCreate(pj.PJSIP_TRANSPORT_UDP, tp_cfg)

        # Start library
        self._ep.libStart()
        logger.info(f"pjsua2 started on port {self.config.local_port}")

        # S237 FIX F1: install null audio device BEFORE first startTransmit.
        # Without this, pjsua_conf_connect() implicitly calls pjsua_set_snd_dev() to
        # open Core Audio on the first audio bridge wiring (see pjsua_aud.c:1085).
        # On headless iMac via SSH, Core Audio open blocks ~14.5s and returns an
        # OSStatus-encoded value in the unnamed errno gap 470000-519999 → status=506784
        # 'Unknown error 506784' (S236 smoking gun). Sara is a pure SIP↔in-memory
        # bridge, never uses local mic/speaker → setNullDev is the idiomatic path.
        try:
            self._ep.audDevManager().setNullDev()
            logger.info("pjsua2: null audio device installed (headless mode, S237 F1)")
        except pj.Error as exc:
            logger.error(f"S237: setNullDev failed | {_pj_error_info(exc)}")
            raise

        # Create and register SIP account
        acc_cfg = pj.AccountConfig()
        acc_cfg.idUri = f"sip:{self.config.username}@{self.config.server}"
        acc_cfg.regConfig.registrarUri = f"sip:{self.config.server}:{self.config.port}"
        acc_cfg.regConfig.timeoutSec = 300

        # Auth credentials
        cred = pj.AuthCredInfo()
        cred.scheme = "digest"
        cred.realm = "*"
        cred.username = self.config.username
        cred.dataType = 0  # Plain text password
        cred.data = self.config.password
        acc_cfg.sipConfig.authCreds.append(cred)

        # NAT config — use STUN for mapped address
        acc_cfg.natConfig.iceEnabled = True
        acc_cfg.natConfig.sdpNatRewriteUse = 1
        acc_cfg.natConfig.sipOutboundUse = 1
        acc_cfg.natConfig.contactRewriteUse = 1

        # D4: TURN server for CGNAT traversal
        if self.config.turn_server:
            acc_cfg.natConfig.turnEnabled = True
            acc_cfg.natConfig.turnServer = self.config.turn_server
            acc_cfg.natConfig.turnConnType = pj.PJ_TURN_TP_UDP
            if self.config.turn_username:
                acc_cfg.natConfig.turnUserName = self.config.turn_username
                acc_cfg.natConfig.turnPasswordType = 0  # Plain text
                acc_cfg.natConfig.turnPassword = self.config.turn_password
            logger.info(f"TURN enabled: {self.config.turn_server}")
        else:
            logger.info("TURN not configured (STUN only — CGNAT users may have issues)")

        # S152: Disable session timers (RFC 4028 keepalive re-INVITEs)
        acc_cfg.callConfig.timerUse = pj.PJSUA_SIP_TIMER_INACTIVE
        acc_cfg.callConfig.timerMinSESec = 90
        acc_cfg.callConfig.timerSessExpiresSec = 1800

        # S153: Disable codec lock — THIS is the actual reinv_timer_cb trigger
        # The codec lock timer fires 200ms after call establishment to send a
        # re-INVITE narrowing the codec list to a single codec. This timer is
        # what causes "Timed-out trying to acquire PJSUA mutex in reinv_timer_cb()".
        # Disabling it prevents the timer from firing entirely.
        # Safe for EHIWEB: G.711 is the only codec, no renegotiation needed.
        acc_cfg.mediaConfig.lockCodecEnabled = False

        # E7: UDP keepalive for CGNAT NAT binding refresh
        # Sends CRLF keepalive to keep NAT pinhole open (aggressive NATs close after 30-120s)
        if self.config.keepalive_interval > 0:
            acc_cfg.natConfig.udpKaIntervalSec = self.config.keepalive_interval
            # Also set SIP-level keepalive via re-registration at shorter interval
            acc_cfg.regConfig.timeoutSec = min(300, self.config.keepalive_interval * 10)
            logger.info(f"E7: UDP keepalive enabled every {self.config.keepalive_interval}s")

        # Create account
        self._account = SaraAccount()
        self._account.on_incoming_call = self._on_incoming_call
        self._account.on_reg_state = self._on_reg_state
        self._account.create(acc_cfg)

        logger.info(f"SIP account created: {self.config.username}@{self.config.server}")

    def _cleanup_pjsua2(self):
        """Clean up pjsua2 resources."""
        try:
            if self._current_call and self._current_call.connected:
                call_prm = pj.CallOpParam()
                self._current_call.hangup(call_prm)

            if self._account:
                self._account.shutdown()
                self._account = None

            if self._ep:
                self._ep.libDestroy()
                self._ep = None

        except Exception as exc:
            logger.error(f"pjsua2 cleanup error: {exc}")

    # =========================================================================
    # Callbacks (called from pjsua2 thread)
    # =========================================================================

    def _on_reg_state(self, is_registered: bool, status: int):
        """SIP registration state changed."""
        self._registered = is_registered
        self._reg_status = status
        if is_registered:
            logger.info("SIP REGISTERED successfully")
        else:
            logger.warning(f"SIP registration failed: status={status}")

    def _on_incoming_call(self, call: SaraCall):
        """Incoming call — answer with 200 OK directly.

        S153: With threadCnt=0 + mainThreadOnly=True + lockCodecEnabled=False,
        all callbacks run on our single pjsua2 thread. The codec lock timer
        (reinv_timer_cb) is disabled entirely. No cross-thread mutex contention
        is possible, so we can answer directly without delay hacks.
        """
        # C2: Extract caller phone number from SIP URI
        try:
            ci = call.getInfo()
            self._caller_phone = self._extract_phone_from_uri(ci.remoteUri)
            logger.info(f"Incoming call from: {ci.remoteUri} → phone: {self._caller_phone}")
        except Exception as e:
            self._caller_phone = ""
            logger.warning(f"Could not extract caller phone: {e}")

        self._current_call = call
        call.on_connected = self._on_call_connected
        call.on_disconnected = self._on_call_disconnected

        # S153: Answer directly with 200 OK — no 180 Ringing needed
        # mainThreadOnly=True ensures this runs on pjsua2 event loop thread
        # lockCodecEnabled=False prevents reinv_timer_cb from ever firing
        logger.info("Answering call with 200 OK (direct — S153 fix)")
        try:
            call_prm = pj.CallOpParam()
            call_prm.statusCode = 200
            call.answer(call_prm)
        except Exception as exc:
            logger.error(f"Failed to answer call: {exc}")

    def _on_call_connected(self, call: SaraCall):
        """Call connected — start audio processing thread."""
        logger.info("Call connected, starting audio processing")

        # Start audio processing thread
        self._audio_thread = threading.Thread(
            target=self._audio_processing_loop,
            args=(call,),
            daemon=True
        )
        self._audio_thread.start()

        # Send greeting (C2: pass caller phone number)
        if self.pipeline:
            threading.Thread(
                target=self._send_greeting,
                args=(call, getattr(self, '_caller_phone', '')),
                daemon=True
            ).start()

    def _on_call_disconnected(self, call: SaraCall):
        """Call ended — cleanup."""
        logger.info("Call disconnected")
        self._current_call = None
        self._caller_phone = ""
        self._vad_speech_frames = 0
        self._vad_silence_frames = 0

    @staticmethod
    def _extract_phone_from_uri(sip_uri: str) -> str:
        """Extract phone number from SIP URI.

        Examples:
            'sip:+390972536918@sip.vivavox.it' → '+390972536918'
            '<sip:0972536918@sip.vivavox.it>'   → '0972536918'
            '"Mario" <sip:+39333@host>'         → '+39333'
        """
        if not sip_uri:
            return ""
        # Strip display name and angle brackets
        uri = sip_uri
        if "<" in uri:
            uri = uri.split("<")[-1].split(">")[0]
        # Remove sip: prefix
        if uri.lower().startswith("sip:"):
            uri = uri[4:]
        # Take user part (before @)
        user = uri.split("@")[0] if "@" in uri else uri
        # Keep only digits and leading +
        if user.startswith("+"):
            return "+" + "".join(c for c in user[1:] if c.isdigit())
        return "".join(c for c in user if c.isdigit())

    # =========================================================================
    # Audio Processing (runs in dedicated thread)
    # =========================================================================

    def _audio_processing_loop(self, call: SaraCall):
        """Continuously reads caller audio, detects speech turns, processes via Sara."""
        # S352: register only if pjlib does not already track this thread.
        _register_thread_if_needed("audio_processing")
        logger.info("Audio processing loop started")
        audio_buffer = bytearray()
        speech_audio = bytearray()  # Accumulates actual speech frames for STT
        is_speaking = False  # Anti-echo: track if Sara TTS is playing
        barge_in_frames = 0  # S142: Counter for sustained caller speech during TTS
        BARGE_IN_MARGIN = 500  # RMS above expected echo to trigger barge-in
        BARGE_IN_THRESHOLD = 4  # 80ms of sustained speech = real barge-in
        ECHO_ATTENUATION = 0.5  # Echo is ~50% of TX energy through phone speaker

        while call.connected and self._running:
            # S142: Barge-in detection replaces binary anti-echo
            # Instead of dropping ALL caller audio during TTS, detect if caller
            # is actually speaking (energy significantly above expected echo)
            sara_speaking = not call.audio_port.tx_queue.empty() or call.audio_port._current_tx_rms > 0
            if sara_speaking:
                audio = call.audio_port.get_caller_audio(timeout=0.01)
                if audio:
                    caller_rms = self._calculate_rms(audio)
                    expected_echo = call.audio_port._current_tx_rms * ECHO_ATTENUATION
                    if caller_rms > expected_echo + BARGE_IN_MARGIN:
                        barge_in_frames += 1
                        if barge_in_frames >= BARGE_IN_THRESHOLD:
                            # Real barge-in detected! Stop Sara and process caller speech
                            logger.info(f"BARGE-IN detected! caller_rms={caller_rms:.0f} vs echo={expected_echo:.0f}")
                            call.audio_port.clear_tx()  # Stop Sara immediately
                            speech_audio.extend(audio)
                            is_speaking = False
                            barge_in_frames = 0
                            self._vad_speech_frames = len(audio) // 320
                            self._vad_silence_frames = 0
                            # B1 FIX: Do NOT continue — fall through to VAD below
                            # (old code fell to is_speaking=True → continue → grace period → clear)
                        else:
                            time.sleep(0.02)
                            continue
                    else:
                        barge_in_frames = 0  # Reset: just echo
                        is_speaking = True
                        time.sleep(0.02)
                        continue
                else:
                    is_speaking = True
                    time.sleep(0.02)
                    continue
            elif is_speaking:
                # Grace period after TTS ends — B5: reduced from 0.3s to 0.15s
                # to avoid clipping short "sì"/"no" responses (~150ms)
                is_speaking = False
                time.sleep(0.15)
                call.audio_port.get_caller_audio(timeout=0.01)  # Drain echo tail
                speech_audio.clear()
                audio_buffer.clear()
                self._vad_speech_frames = 0
                self._vad_silence_frames = 0
                continue

            # Get caller audio from the bridge
            audio = call.audio_port.get_caller_audio(timeout=0.1)
            if not audio:
                time.sleep(0.02)
                continue

            audio_buffer.extend(audio)

            # Simple energy-based VAD on 20ms frames
            frame_size = 320  # 20ms at 8kHz 16-bit mono
            while len(audio_buffer) >= frame_size:
                frame = bytes(audio_buffer[:frame_size])
                del audio_buffer[:frame_size]

                # Calculate RMS energy
                rms = self._calculate_rms(frame)

                if rms > self._vad_speech_threshold:
                    self._vad_speech_frames += 1
                    self._vad_silence_frames = 0
                    speech_audio.extend(frame)  # Keep speech frame for STT
                else:
                    if self._vad_speech_frames > 0:
                        self._vad_silence_frames += 1
                        speech_audio.extend(frame)  # Keep trailing silence too

                # S143: Turn complete: had enough speech (300ms min), then 1000ms silence
                # Was: speech >= 3 (60ms) — too short, triggered on coughs/echo
                if self._vad_speech_frames >= 15 and self._vad_silence_frames >= self._vad_silence_timeout:
                    full_audio = bytes(speech_audio)
                    speech_audio.clear()
                    audio_buffer.clear()
                    self._vad_speech_frames = 0
                    self._vad_silence_frames = 0

                    if full_audio and self.pipeline:
                        dur_ms = len(full_audio) / 16  # 8kHz 16-bit = 16 bytes/ms
                        # S140: Audio quality gate — reject too-short or too-quiet turns
                        if dur_ms < 300:
                            logger.debug(f"Turn too short ({dur_ms:.0f}ms), skipping")
                            continue
                        turn_rms = self._calculate_rms(full_audio)
                        if turn_rms < 400:
                            logger.debug(f"Turn too quiet (RMS={turn_rms:.0f}), skipping")
                            continue
                        logger.info(f"Speech turn detected: {dur_ms:.0f}ms audio (RMS={turn_rms:.0f}), sending to Sara")
                        self._process_caller_audio(call, full_audio)

        logger.info("Audio processing loop ended")

    def _calculate_rms(self, pcm_data: bytes) -> float:
        """Calculate RMS energy of PCM audio frame (C-optimized via audioop)."""
        if len(pcm_data) < 2:
            return 0.0
        return float(audioop.rms(pcm_data, 2))

    def _process_caller_audio(self, call: SaraCall, audio_8k: bytes):
        """Process caller audio through Sara pipeline."""
        try:
            # Upsample 8kHz → 16kHz for Whisper STT
            audio_16k, _ = audioop.ratecv(audio_8k, 2, 1, 8000, 16000, None)

            # Schedule on main event loop (where httpx/groq clients live)
            t0 = time.time()
            future = asyncio.run_coroutine_threadsafe(
                self.pipeline.process_audio(audio_16k), self._main_loop
            )
            result = future.result(timeout=15)  # L2/L4: 15s max (was 30s — too long for live call)
            elapsed = (time.time() - t0) * 1000

            if result:
                text = result.get("text", "")
                transcription = result.get("transcription", "")
                has_audio = result.get("audio_response") is not None
                audio_len = len(result["audio_response"]) if has_audio else 0
                logger.info(f"Pipeline result ({elapsed:.0f}ms): STT='{transcription}' → response='{text[:80]}' audio={audio_len}B")

                # Queue TTS response
                if has_audio:
                    call.audio_port.queue_tts_audio(result["audio_response"])
                    logger.info("TTS audio queued for playback")
                else:
                    logger.warning("No audio_response from pipeline")

                # S142: Hangup after goodbye TTS finishes
                if result.get("should_exit") and not self._hangup_pending:
                    self._hangup_pending = True  # L5: prevent multiple hangup threads
                    logger.info("should_exit=True — will hangup after TTS playback")
                    _hangup_call = call  # L1: capture reference to THIS call
                    def _hangup_after_tts():
                        # Wait for TTS to finish playing
                        while not _hangup_call.audio_port.tx_queue.empty():
                            if not _hangup_call.connected:
                                return  # L1: caller already hung up
                            time.sleep(0.1)
                        time.sleep(0.5)  # Brief pause after last word
                        # L1: Don't hang up if a new call arrived
                        if self._current_call is not _hangup_call:
                            logger.warning("Hangup skipped — different call active")
                            return
                        if not _hangup_call.connected:
                            return
                        # S352: skip if pjlib already tracks this thread.
                        _register_thread_if_needed("hangup")
                        try:
                            call_prm = pj.CallOpParam()
                            _hangup_call.hangup(call_prm)
                            logger.info("Call hung up after goodbye")
                        except Exception as exc:
                            logger.error(f"Hangup error: {exc}")
                        finally:
                            self._hangup_pending = False
                    threading.Thread(target=_hangup_after_tts, daemon=True).start()
            else:
                logger.warning(f"Pipeline returned None ({elapsed:.0f}ms)")

        except Exception as exc:
            logger.error(f"Audio processing error: {exc}", exc_info=True)

    def _send_greeting(self, call: SaraCall, phone_number: str = ""):
        """Send Sara greeting when call connects."""
        # S352: register only if pjlib does not already track this thread.
        _register_thread_if_needed("send_greeting")
        try:
            # Brief delay for media to stabilize
            time.sleep(0.5)

            if not self.pipeline:
                return

            # Schedule on main event loop (where TTS/httpx clients live)
            # C2: Pass caller phone for personalized greeting
            future = asyncio.run_coroutine_threadsafe(
                self.pipeline.greet(phone_number=phone_number), self._main_loop
            )
            greeting = future.result(timeout=15)

            if greeting and greeting.get("audio_response"):
                call.audio_port.queue_tts_audio(greeting["audio_response"])
                logger.info("Greeting queued for playback")

        except Exception as exc:
            logger.error(f"Greeting error: {exc}", exc_info=True)


# =============================================================================
# Test
# =============================================================================

async def test_voip():
    """Test pjsua2 VoIP — register and wait for calls."""
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.env"))

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(name)s %(levelname)s %(message)s'
    )

    config = SIPConfig.from_env()
    print(f"SIP: {config.username}@{config.server}:{config.port}")
    print(f"STUN: {config.stun_server}")
    print(f"TURN: {config.turn_server or 'disabled'}")
    print(f"Local port: {config.local_port}")

    manager = VoIPManager(config)

    print("\nStarting VoIP (pjsua2)...")
    if await manager.start():
        print(f"✅ VoIP started — registered={manager._registered}")
        print(f"Status: {manager.get_status()}")
        print("\nWaiting for incoming calls... (Ctrl+C to stop)")
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            pass
    else:
        print("❌ VoIP start failed")

    await manager.stop()
    print("VoIP stopped")


if __name__ == "__main__":
    asyncio.run(test_voip())
