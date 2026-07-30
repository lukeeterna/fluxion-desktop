#!/usr/bin/env python3
"""FLUXION F3-SIP one-shot driver for the loopback Sara rig.

Speech-like STT-failure strategy
--------------------------------
The driver does not use white noise. It renders a real Italian voiced carrier
with the same macOS ``say``/``afconvert`` path already used by
``sara_audio_harness.py``, keeps only voiced 20 ms frames, mixes several
non-adjacent/reversed speech frames, and normalizes every frame just above the
Go turn-VAD threshold. The result retains speech formants and voiced envelopes
(which are accepted as speech by Silero/turn VAD) while destroying phoneme and
word continuity so STT returns an empty/rejected result and E6 strikes mature.
"""

from __future__ import annotations

import audioop
import math
import os
import queue
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import threading
import time
import wave
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, Iterable, List, Optional, Sequence, Tuple

LOOPBACK = "127.0.0.1"
SARA_HTTP_PORT = 3003       # rig identity only; this driver never calls HTTP
REGSTUB_PORT = 15062        # registration UAS used by the already-running rig
SARA_SIP_PORT = 15090       # direct INVITE target: Go engine SIP listener
BRIDGE_PORT = 8399          # Go engine <-> Python bridge used by the rig
LOCAL_SIP_PORTS = (15170, 15172, 15174, 15176)
LOCAL_RTP_PORTS = (15180, 15200, 15220, 15240)

LOG_PATH = Path("/tmp/rig_sara3003.log")
OUT_DIR = Path(__file__).resolve().parent
REPORT_PATH = OUT_DIR / "f3_sip_esiti.md"
SAMPLE_PATH = OUT_DIR / "f3_sip_sample.wav"

FRAME_BYTES = 320           # 20 ms, PCM16, 8 kHz, mono
SAMPLE_RATE = 8000
SAMPLE_WIDTH = 2
VAD_THRESHOLD = 400
PASS = "PASS"
FAIL = "FAIL"
ND = "ND"

REPO_ROOT = Path(__file__).resolve().parents[3]
PJSUA2_DIR = REPO_ROOT / "voice-agent" / "lib" / "pjsua2"
if PJSUA2_DIR.is_dir():
    sys.path.insert(0, str(PJSUA2_DIR))

_PJSUA2_IMPORT_ERROR: Optional[BaseException] = None
try:
    import pjsua2 as pj  # type: ignore
except BaseException as exc:  # runtime guard; report remains writable
    pj = None  # type: ignore
    _PJSUA2_IMPORT_ERROR = exc

E6_GREP = (
    r"CALL_START|greeting in coda|TTS done|risposta TTS|canned TTS|"
    r"fine-utterance|STT|Groq|trascri|rejected|strike|E6|"
    r"richiamar|collega|should_escalate|HANGUP|BYE|CALL_END|DISCONNECT"
)
IDLE_GREP = (
    r"CALL_START|greeting in coda|TTS done|GATE2R-PY-TX|"
    r"IDLE|reprompt|canned TTS|HANGUP|BYE|CALL_END|DISCONNECT"
)

TS_PATTERNS = (
    re.compile(
        r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:[.,]\d{1,6})?"
    ),
    re.compile(r"\b\d{2}:\d{2}:\d{2}(?:[.,]\d{1,6})?\b"),
)


@dataclass
class Evidence:
    verdict: str = FAIL
    reason: str = "scenario non eseguito"
    attempt: int = 0
    log_lines: List[str] = field(default_factory=list)
    timestamps: dict = field(default_factory=dict)
    metrics: dict = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)
    sample_temp: Optional[Path] = None


def iso_wall(value: Optional[float]) -> str:
    if value is None:
        return ND
    return datetime.fromtimestamp(value).astimezone().isoformat(
        timespec="milliseconds"
    )


def fmt_delta(value: Optional[float]) -> str:
    return ND if value is None else f"{value:.3f}s"


def extract_ts_text(line: Optional[str]) -> str:
    if not line:
        return ND
    for pattern in TS_PATTERNS:
        match = pattern.search(line)
        if match:
            return match.group(0)
    return ND


def log_epoch(
    line: Optional[str],
    reference_epoch: Optional[float],
) -> Optional[float]:
    if not line:
        return None
    text = extract_ts_text(line)
    if text == ND:
        return None
    text = text.replace(",", ".")
    try:
        if re.match(r"^\d{4}-", text):
            return datetime.fromisoformat(
                text.replace(" ", "T", 1)
            ).timestamp()

        parsed = datetime.strptime(
            text,
            "%H:%M:%S.%f" if "." in text else "%H:%M:%S",
        )
        ref = datetime.fromtimestamp(
            reference_epoch or time.time()
        ).astimezone()
        candidate = ref.replace(
            hour=parsed.hour,
            minute=parsed.minute,
            second=parsed.second,
            microsecond=parsed.microsecond,
        )
        if candidate.timestamp() - ref.timestamp() > 43200:
            candidate -= timedelta(days=1)
        elif ref.timestamp() - candidate.timestamp() > 43200:
            candidate += timedelta(days=1)
        return candidate.timestamp()
    except (ValueError, OverflowError, OSError):
        return None


def log_offset() -> int:
    try:
        return LOG_PATH.stat().st_size
    except OSError:
        return 0


def grep_since(offset: int, pattern: str) -> List[str]:
    """Return targeted matches appended after offset; never read the full log."""
    if not LOG_PATH.is_file():
        return []

    try:
        size = LOG_PATH.stat().st_size
        start = 1 if size < offset else offset + 1
        tail = subprocess.Popen(
            ["tail", "-c", f"+{start}", str(LOG_PATH)],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        grep = subprocess.run(
            ["grep", "-E", "-i", pattern],
            stdin=tail.stdout,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=8,
            check=False,
        )

        if tail.stdout is not None:
            tail.stdout.close()

        try:
            tail.wait(timeout=2)
        except subprocess.TimeoutExpired:
            tail.kill()
            tail.wait(timeout=2)

        if grep.returncode not in (0, 1):
            return []

        lines = grep.stdout.decode(
            "utf-8",
            errors="replace",
        ).splitlines()

        seen = set()
        ordered = []
        for line in lines:
            if line not in seen:
                seen.add(line)
                ordered.append(line)
        return ordered
    except (OSError, subprocess.SubprocessError):
        return []


def ordered_subset(
    lines: Sequence[str],
    selected: Iterable[Optional[str]],
) -> List[str]:
    wanted = {line for line in selected if line}
    return [line for line in lines if line in wanted]


def find_strike(
    lines: Sequence[str],
    number: int,
) -> Optional[str]:
    patterns = (
        rf"\bstrike(?:s)?\b[^0-9]{{0,40}}{number}\s*(?:/|of)\s*3\b",
        rf"\bstrike(?:s)?\b[^0-9]{{0,40}}(?:=|:|#)\s*{number}\b",
        rf"\bstt[_ -]?failure\b[^0-9]{{0,40}}{number}"
        rf"\s*(?:/\s*3)?\b",
        rf"\bfailure[_ -]?(?:count|strike)\b[^0-9]{{0,40}}"
        rf"{number}\b",
        rf"\b{number}\s*/\s*3\b[^\n]*"
        rf"\b(?:strike|stt[_ -]?failure)\b",
    )
    for line in lines:
        low = line.lower()
        if "3-strike escalation" in low and number == 3:
            continue
        if any(
            re.search(candidate, line, re.IGNORECASE)
            for candidate in patterns
        ):
            return line
    return None


def find_e6(
    lines: Sequence[str],
    after: int = -1,
) -> Optional[str]:
    candidates = lines[after + 1:] if after >= 0 else lines

    for line in candidates:
        if re.search(
            r"\[?E6\]?.*(?:trigger|scatt|escalat|threshold)",
            line,
            re.IGNORECASE,
        ):
            return line

    return next(
        (
            line
            for line in candidates
            if re.search(r"\bE6\b", line, re.IGNORECASE)
        ),
        None,
    )


def find_goodbye(
    lines: Sequence[str],
    after: int = -1,
) -> Optional[str]:
    candidates = lines[after + 1:] if after >= 0 else lines
    for line in candidates:
        low = line.lower()
        if "richiamar" in low or "collega" in low:
            return line
    return None


def find_bye(
    lines: Sequence[str],
    after: int = -1,
) -> Optional[str]:
    candidates = lines[after + 1:] if after >= 0 else lines
    return next(
        (
            line
            for line in candidates
            if re.search(r"\bBYE\b", line, re.IGNORECASE)
        ),
        None,
    )


def find_identity_evidence(
    lines: Sequence[str],
) -> Optional[str]:
    patterns = (
        r"Marco Rossi",
        r"cliente nuovo",
        r"numero di telefono",
        r"registrar",
        r"WAITING_PHONE|REGISTERING_PHONE",
    )
    for line in lines:
        if any(
            re.search(pattern, line, re.IGNORECASE)
            for pattern in patterns
        ):
            return line
    return None


def find_idle_arming(
    lines: Sequence[str],
) -> Optional[str]:
    for line in lines:
        if re.search(
            r"reprompt[_ -]?timer.*(?:arm|start)|"
            r"IDLE.*(?:arm|start)",
            line,
            re.IGNORECASE,
        ):
            return line

    return next(
        (line for line in lines if "CALL_START" in line),
        None,
    )


def find_idle_trigger(
    lines: Sequence[str],
) -> Optional[str]:
    for line in lines:
        if re.search(
            r"IDLE:\s*2[12-4]s.*reprompt",
            line,
            re.IGNORECASE,
        ):
            return line

    for line in lines:
        if re.search(
            r"(?:reprompt).*?(?:trigger|fire|scatt|silenz)",
            line,
            re.IGNORECASE,
        ):
            return line
    return None


def find_reprompt_tts(
    lines: Sequence[str],
    after: int = -1,
) -> Optional[str]:
    candidates = lines[after + 1:] if after >= 0 else lines

    for line in candidates:
        low = line.lower()
        if (
            "canned tts" in low
            and re.search(
                r"linea|sente|pronto|presente|reprompt",
                low,
            )
        ):
            return line

    return next(
        (
            line
            for line in candidates
            if "canned tts" in line.lower()
        ),
        None,
    )


def write_wav(path: Path, pcm: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(SAMPLE_WIDTH)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(pcm)


def read_wav(path: Path) -> bytes:
    with wave.open(str(path), "rb") as wav_file:
        shape = (
            wav_file.getframerate(),
            wav_file.getnchannels(),
            wav_file.getsampwidth(),
        )
        pcm = wav_file.readframes(wav_file.getnframes())

    if shape != (SAMPLE_RATE, 1, SAMPLE_WIDTH):
        raise ValueError(f"WAV non RTP-ready: {shape!r}")
    return pcm


def render_speech(text: str, out_path: Path) -> bytes:
    aiff = out_path.with_suffix(out_path.suffix + ".aiff")
    try:
        subprocess.run(
            ["say", "-o", str(aiff), text],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=30,
            check=True,
        )
        subprocess.run(
            [
                "afconvert",
                "-f",
                "WAVE",
                "-d",
                "LEI16@8000",
                "-c",
                "1",
                str(aiff),
                str(out_path),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=30,
            check=True,
        )
        return read_wav(out_path)
    finally:
        try:
            aiff.unlink()
        except OSError:
            pass


def pcm_rms(pcm: bytes) -> float:
    return (
        float(audioop.rms(pcm, SAMPLE_WIDTH))
        if len(pcm) >= SAMPLE_WIDTH
        else 0.0
    )


def _samples(pcm: bytes) -> List[int]:
    usable = len(pcm) - (len(pcm) % SAMPLE_WIDTH)
    if not usable:
        return []
    return list(
        struct.unpack(
            "<" + "h" * (usable // SAMPLE_WIDTH),
            pcm[:usable],
        )
    )


def _pack(samples: Sequence[int]) -> bytes:
    clipped = [
        max(-32768, min(32767, int(value)))
        for value in samples
    ]
    return struct.pack(
        "<" + "h" * len(clipped),
        *clipped,
    )


def normalize_frame(
    frame: Sequence[int],
    target_rms: float,
) -> List[int]:
    if not frame:
        return []

    current = math.sqrt(
        sum(value * value for value in frame) / len(frame)
    )
    if current < 1.0:
        return [0] * len(frame)

    gain = min(12.0, target_rms / current)
    return [
        max(-12000, min(12000, int(value * gain)))
        for value in frame
    ]


def speech_like_babble(
    carrier_pcm: bytes,
    seed: int,
    profile: int,
) -> bytes:
    """Create low-level, formant-preserving, non-transcribable voiced babble."""
    source = _samples(carrier_pcm)
    frame_samples = FRAME_BYTES // SAMPLE_WIDTH
    frames = [
        source[index:index + frame_samples]
        for index in range(
            0,
            len(source) - frame_samples + 1,
            frame_samples,
        )
    ]

    voiced = []
    for frame in frames:
        raw = _pack(frame)
        if pcm_rms(raw) >= 650:
            voiced.append(frame)

    if len(voiced) < 12:
        raise ValueError(
            "carrier speech insufficiente per costruire babble"
        )

    target_frames = 72 if profile == 0 else 68
    target_rms = 920.0 if profile == 0 else 760.0
    output: List[int] = []
    count = len(voiced)

    for index in range(target_frames):
        first_index = (
            seed + index * (17 if profile == 0 else 23)
        ) % count
        second_index = (
            seed * 3 + index * 29 + 7
        ) % count
        third_index = (
            seed * 5 + index * 37 + 11
        ) % count

        first = voiced[first_index]
        second = list(reversed(voiced[second_index]))
        third = voiced[third_index]

        shift = (
            index * (19 + profile * 13)
        ) % frame_samples
        third = third[shift:] + third[:shift]

        mixed = []
        for sample_index in range(frame_samples):
            value = (
                0.52 * first[sample_index]
                + 0.31 * second[sample_index]
                + 0.27 * third[sample_index]
            )
            micro = 20 if profile == 0 else 10
            if ((sample_index // micro) + index) & 1:
                value = -value
            mixed.append(int(value))

        mixed = normalize_frame(mixed, target_rms)

        if index < 3:
            gain = 0.72 + 0.09 * index
            mixed = [
                int(value * gain)
                for value in mixed
            ]
        elif index >= target_frames - 3:
            gain = (
                0.90
                - 0.12 * (index - (target_frames - 3))
            )
            mixed = [
                int(value * gain)
                for value in mixed
            ]

        output.extend(mixed)

    pcm = _pack(output)
    if pcm_rms(pcm) < 650:
        raise ValueError(
            "babble RMS sotto il margine VAD"
        )
    return pcm


if pj is not None:

    class DriverAudioPort(pj.AudioMediaPort):
        def __init__(self) -> None:
            super().__init__()
            self.tx_queue: "queue.Queue[bytes]" = queue.Queue()
            self.rx_chunks: List[bytes] = []
            self._silence = b"\x00" * FRAME_BYTES
            self._thread_local = threading.local()
            self._created = False
            self._pending = 0
            self._pending_lock = threading.Lock()
            self.tx_idle = threading.Event()
            self.tx_idle.set()

            self.rx_starts: List[float] = []
            self.rx_segments: List[Tuple[float, float]] = []
            self._rx_candidate_start: Optional[float] = None
            self._rx_hot_frames = 0
            self._rx_active = False
            self._rx_active_start: Optional[float] = None
            self._rx_silent_frames = 0

        def _register_thread(self) -> None:
            if getattr(
                self._thread_local,
                "registered",
                False,
            ):
                return

            try:
                pj.Endpoint.instance().libRegisterThread(
                    f"f3_audio_{threading.get_ident()}"
                )
            except pj.Error:
                pass

            self._thread_local.registered = True

        def ensure_port(self) -> None:
            if self._created:
                return

            audio_format = pj.MediaFormatAudio()
            audio_format.init(
                0x2036314C,
                SAMPLE_RATE,
                1,
                20000,
                16,
                0,
            )
            self.createPort(
                "f3_sip_bridge",
                audio_format,
            )
            self._created = True

        def enqueue(
            self,
            pcm: bytes,
            tail_silence: float = 1.10,
        ) -> None:
            chunks = []

            for index in range(0, len(pcm), FRAME_BYTES):
                chunk = pcm[index:index + FRAME_BYTES]
                if len(chunk) < FRAME_BYTES:
                    chunk += b"\x00" * (
                        FRAME_BYTES - len(chunk)
                    )
                chunks.append(chunk)

            chunks.extend(
                [self._silence]
                * max(
                    0,
                    int(round(tail_silence / 0.020)),
                )
            )

            with self._pending_lock:
                self._pending += len(chunks)
                if chunks:
                    self.tx_idle.clear()

            for chunk in chunks:
                self.tx_queue.put(chunk)

        def onFrameRequested(self, frame) -> None:
            self._register_thread()
            try:
                chunk = self.tx_queue.get_nowait()
                with self._pending_lock:
                    self._pending = max(
                        0,
                        self._pending - 1,
                    )
                    if self._pending == 0:
                        self.tx_idle.set()
            except queue.Empty:
                chunk = self._silence
                with self._pending_lock:
                    if self._pending == 0:
                        self.tx_idle.set()

            frame.type = pj.PJMEDIA_FRAME_TYPE_AUDIO
            frame.buf = pj.ByteVector(chunk)

        def onFrameReceived(self, frame) -> None:
            self._register_thread()
            if frame.type != pj.PJMEDIA_FRAME_TYPE_AUDIO:
                return

            chunk = bytes(frame.buf)
            self.rx_chunks.append(chunk)
            now = time.time()
            rms = pcm_rms(chunk)
            hot = rms >= 220.0

            if hot:
                if self._rx_candidate_start is None:
                    self._rx_candidate_start = now
                    self._rx_hot_frames = 1
                else:
                    self._rx_hot_frames += 1

                self._rx_silent_frames = 0

                if (
                    not self._rx_active
                    and self._rx_hot_frames >= 5
                ):
                    self._rx_active = True
                    self._rx_active_start = (
                        self._rx_candidate_start
                    )
                    self.rx_starts.append(
                        self._rx_active_start
                    )
            else:
                if not self._rx_active:
                    self._rx_candidate_start = None
                    self._rx_hot_frames = 0
                    return

                self._rx_silent_frames += 1
                if self._rx_silent_frames >= 30:
                    end = now - 0.600
                    start = (
                        self._rx_active_start or end
                    )
                    self.rx_segments.append(
                        (start, max(start, end))
                    )
                    self._rx_candidate_start = None
                    self._rx_hot_frames = 0
                    self._rx_active = False
                    self._rx_active_start = None
                    self._rx_silent_frames = 0

        def flush_segment(
            self,
            wall: Optional[float] = None,
        ) -> None:
            if self._rx_active:
                end = wall or time.time()
                start = self._rx_active_start or end
                self.rx_segments.append(
                    (start, max(start, end))
                )

            self._rx_candidate_start = None
            self._rx_hot_frames = 0
            self._rx_active = False
            self._rx_active_start = None
            self._rx_silent_frames = 0

        def write_capture(self, path: Path) -> int:
            pcm = b"".join(self.rx_chunks)
            write_wav(path, pcm)
            return len(pcm)


    class DriverCall(pj.Call):
        def __init__(self, account) -> None:
            super().__init__(
                account,
                pj.PJSUA_INVALID_ID,
            )
            self.audio_port = DriverAudioPort()
            self.connected = False
            self.media_pending = False
            self.media_bridged = False
            self.done = threading.Event()
            self.connected_wall: Optional[float] = None
            self.disconnected_wall: Optional[float] = None
            self.last_status = ND

        def onCallState(self, prm) -> None:
            try:
                info = self.getInfo()
                self.last_status = (
                    f"{info.lastStatusCode} "
                    f"{info.lastReason}"
                ).strip()

                if (
                    info.state
                    == pj.PJSIP_INV_STATE_CONFIRMED
                ):
                    self.connected = True
                    if self.connected_wall is None:
                        self.connected_wall = time.time()

                elif (
                    info.state
                    == pj.PJSIP_INV_STATE_DISCONNECTED
                ):
                    self.connected = False
                    self.disconnected_wall = time.time()
                    self.audio_port.flush_segment(
                        self.disconnected_wall
                    )
                    self.done.set()
            except pj.Error:
                self.disconnected_wall = time.time()
                self.audio_port.flush_segment(
                    self.disconnected_wall
                )
                self.done.set()

        def onCallMediaState(self, prm) -> None:
            self.media_pending = True

        def bridge_media(self) -> None:
            if (
                not self.media_pending
                or self.media_bridged
            ):
                return

            info = self.getInfo()
            for media in info.media:
                if (
                    media.type == pj.PJMEDIA_TYPE_AUDIO
                    and media.status
                    == pj.PJSUA_CALL_MEDIA_ACTIVE
                ):
                    self.audio_port.ensure_port()
                    call_audio = self.getAudioMedia(
                        media.index
                    )
                    call_audio.startTransmit(
                        self.audio_port
                    )
                    self.audio_port.startTransmit(
                        call_audio
                    )
                    self.media_bridged = True
                    self.media_pending = False
                    return


    class DriverAccount(pj.Account):
        def onRegState(self, prm) -> None:
            return


class ScenarioStop(RuntimeError):
    pass


class SipLeg:
    def __init__(
        self,
        local_sip_port: int,
        local_rtp_port: int,
    ) -> None:
        if pj is None:
            raise RuntimeError(
                "pjsua2 non importabile: "
                f"{_PJSUA2_IMPORT_ERROR}"
            )

        self.local_sip_port = local_sip_port
        self.local_rtp_port = local_rtp_port
        self.endpoint = None
        self.account = None
        self.call = None
        self._destroyed = False

    def start(self) -> None:
        endpoint = pj.Endpoint()
        endpoint.libCreate()
        self.endpoint = endpoint

        config = pj.EpConfig()
        config.uaConfig.userAgent = (
            "FLUXION-F3-SIP/1.0"
        )
        config.uaConfig.threadCnt = 0
        config.uaConfig.mainThreadOnly = True
        config.medConfig.noVad = True
        config.medConfig.srtpUse = 0

        try:
            config.medConfig.port = self.local_rtp_port
        except Exception:
            pass

        try:
            config.logConfig.level = 0
            config.logConfig.consoleLevel = 0
            config.logConfig.msgLogging = 0
        except Exception:
            pass

        endpoint.libInit(config)

        transport = pj.TransportConfig()
        transport.port = self.local_sip_port

        try:
            transport.boundAddress = LOOPBACK
            transport.publicAddress = LOOPBACK
        except Exception:
            pass

        endpoint.transportCreate(
            pj.PJSIP_TRANSPORT_UDP,
            transport,
        )
        endpoint.libStart()
        endpoint.audDevManager().setNullDev()

        account_config = pj.AccountConfig()
        account_config.idUri = (
            f"sip:f3driver@{LOOPBACK}:"
            f"{self.local_sip_port}"
        )

        account = DriverAccount()
        account.create(account_config)
        self.account = account

        call = DriverCall(account)
        self.call = call

        user = (
            os.getenv(
                "VOIP_SIP_USER",
                "0972536918",
            ).strip()
            or "0972536918"
        )
        target = (
            f"sip:{user}@{LOOPBACK}:"
            f"{SARA_SIP_PORT};transport=udp"
        )
        call.makeCall(
            target,
            pj.CallOpParam(True),
        )

    @property
    def port(self):
        return self.call.audio_port

    def pump_once(
        self,
        milliseconds: int = 20,
    ) -> None:
        if self.endpoint is None:
            return

        self.endpoint.libHandleEvents(milliseconds)

        if (
            self.call is not None
            and self.call.media_pending
            and not self.call.media_bridged
        ):
            try:
                self.call.bridge_media()
            except pj.Error:
                pass

    def wait_for(
        self,
        predicate: Callable[[], bool],
        timeout: float,
        poll: float = 0.04,
    ) -> bool:
        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:
            self.pump_once(20)
            if predicate():
                return True
            time.sleep(poll)

        self.pump_once(0)
        return predicate()

    def wait_connected(
        self,
        timeout: float = 10.0,
    ) -> bool:
        return self.wait_for(
            lambda: bool(
                self.call
                and self.call.connected
                and self.call.media_bridged
            ),
            timeout,
        )

    def wait_tx_idle(
        self,
        timeout: float,
    ) -> bool:
        return self.wait_for(
            lambda: self.port.tx_idle.is_set(),
            timeout,
        )

    def wait_segment(
        self,
        index: int,
        timeout: float,
    ) -> Optional[Tuple[float, float]]:
        ready = self.wait_for(
            lambda: (
                len(self.port.rx_segments) > index
                or self.call.done.is_set()
            ),
            timeout,
        )
        if (
            ready
            and len(self.port.rx_segments) > index
        ):
            return self.port.rx_segments[index]
        return None

    def wait_rx_start(
        self,
        index: int,
        timeout: float,
    ) -> Optional[float]:
        ready = self.wait_for(
            lambda: (
                len(self.port.rx_starts) > index
                or self.call.done.is_set()
            ),
            timeout,
        )
        if (
            ready
            and len(self.port.rx_starts) > index
        ):
            return self.port.rx_starts[index]
        return None

    def wait_log(
        self,
        offset: int,
        pattern: str,
        predicate: Callable[[Sequence[str]], bool],
        timeout: float,
    ) -> List[str]:
        deadline = time.monotonic() + timeout
        lines: List[str] = []
        next_grep = 0.0

        while time.monotonic() < deadline:
            self.pump_once(20)
            now = time.monotonic()

            if now >= next_grep:
                lines = grep_since(offset, pattern)
                if predicate(lines):
                    return lines
                next_grep = now + 0.45

            if (
                self.call.done.is_set()
                and predicate(lines)
            ):
                return lines

            time.sleep(0.04)

        return grep_since(offset, pattern)

    def close(
        self,
        capture_path: Optional[Path] = None,
    ) -> int:
        captured = 0

        if self.call is not None:
            try:
                if not self.call.done.is_set():
                    self.call.hangup(
                        pj.CallOpParam(True)
                    )
                    self.wait_for(
                        lambda: self.call.done.is_set(),
                        2.0,
                    )
            except Exception:
                pass

            self.call.audio_port.flush_segment(
                self.call.disconnected_wall
                or time.time()
            )

            if capture_path is not None:
                try:
                    captured = (
                        self.call.audio_port.write_capture(
                            capture_path
                        )
                    )
                except Exception:
                    captured = 0

        if (
            self.endpoint is not None
            and not self._destroyed
        ):
            try:
                self.endpoint.libDestroy()
            except Exception:
                pass
            self._destroyed = True

        return captured


def run_scn08_attempt(
    attempt: int,
    local_index: int,
    identity_pcm: bytes,
    bad_clips: Sequence[bytes],
    sample_temp: Path,
) -> Evidence:
    result = Evidence(
        attempt=attempt,
        sample_temp=sample_temp,
    )
    offset = log_offset()
    capture_temp = sample_temp.with_name(
        f"scn08_capture_a{attempt}.wav"
    )
    leg: Optional[SipLeg] = None
    greeting: Optional[Tuple[float, float]] = None
    identity_reply: Optional[Tuple[float, float]] = None
    final_segments: List[Tuple[float, float]] = []

    try:
        leg = SipLeg(
            LOCAL_SIP_PORTS[local_index],
            LOCAL_RTP_PORTS[local_index],
        )
        leg.start()

        if not leg.wait_connected(12.0):
            raise ScenarioStop(
                "INVITE/media non confermati "
                f"({leg.call.last_status})"
            )

        greeting = leg.wait_segment(0, 22.0)
        if greeting is None:
            raise ScenarioStop(
                "fine greeting RTP non rilevata"
            )

        leg.port.enqueue(
            identity_pcm,
            tail_silence=1.15,
        )
        leg.wait_tx_idle(
            max(
                8.0,
                len(identity_pcm) / 16000.0 + 3.0,
            )
        )
        identity_reply = leg.wait_segment(
            1,
            25.0,
        )

        for number, pcm in enumerate(
            bad_clips,
            1,
        ):
            if leg.call.done.is_set():
                break

            baseline_segments = len(
                leg.port.rx_segments
            )
            leg.port.enqueue(
                pcm,
                tail_silence=1.15,
            )
            leg.wait_tx_idle(
                max(
                    7.0,
                    len(pcm) / 16000.0 + 3.0,
                )
            )
            leg.wait_log(
                offset,
                E6_GREP,
                lambda current, wanted=number: (
                    find_strike(
                        current,
                        wanted,
                    )
                    is not None
                ),
                18.0,
            )

            if (
                number < 3
                and not leg.call.done.is_set()
            ):
                leg.wait_segment(
                    baseline_segments,
                    18.0,
                )
                leg.wait_for(
                    lambda: False,
                    0.30,
                )

        leg.wait_for(
            lambda: leg.call.done.is_set(),
            25.0,
        )

        final_segments = list(
            leg.port.rx_segments
        )
        if leg.call.audio_port._rx_active:
            leg.call.audio_port.flush_segment(
                time.time()
            )
            final_segments = list(
                leg.port.rx_segments
            )

    except ScenarioStop as exc:
        result.reason = str(exc)
    except Exception as exc:
        result.reason = (
            f"eccezione {type(exc).__name__}: {exc}"
        )
    finally:
        if leg is not None:
            leg.close(capture_temp)
            final_segments = list(
                leg.port.rx_segments
            )

    lines = grep_since(offset, E6_GREP)
    strikes = [
        find_strike(lines, number)
        for number in (1, 2, 3)
    ]
    indices = [
        lines.index(line) if line in lines else -1
        for line in strikes
    ]
    ordered_strikes = (
        all(index >= 0 for index in indices)
        and indices[0] < indices[1] < indices[2]
    )

    e6 = find_e6(
        lines,
        indices[2] if indices[2] >= 0 else -1,
    )
    e6_index = (
        lines.index(e6)
        if e6 in lines
        else -1
    )
    goodbye = find_goodbye(
        lines,
        e6_index,
    )
    goodbye_index = (
        lines.index(goodbye)
        if goodbye in lines
        else -1
    )
    bye = find_bye(
        lines,
        goodbye_index
        if goodbye_index >= 0
        else e6_index,
    )
    identity_line = find_identity_evidence(lines)

    goodbye_low = (
        goodbye.lower()
        if goodbye
        else ""
    )
    honest = (
        "richiamar" in goodbye_low
        and "collega" not in goodbye_low
    )
    goodbye_end = (
        final_segments[-1][1]
        if final_segments
        else None
    )
    bye_wall = log_epoch(
        bye,
        goodbye_end,
    )
    disconnected = (
        leg.call.disconnected_wall
        if (
            leg is not None
            and leg.call is not None
        )
        else None
    )

    # The log is required evidence that BYE was emitted. The local call-state
    # timestamp is the precise edge for the <=2 s measurement because the
    # server log may expose only second-resolution timestamps.
    if (
        bye is not None
        and disconnected is not None
    ):
        bye_wall = disconnected

    bye_delta = (
        None
        if goodbye_end is None or bye_wall is None
        else bye_wall - goodbye_end
    )
    bye_ok = (
        bye is not None
        and bye_delta is not None
        and -0.10 <= bye_delta <= 2.0
    )
    identity_ok = (
        identity_reply is not None
        or identity_line is not None
    )

    selected = [
        identity_line,
        *strikes,
        e6,
        goodbye,
        bye,
    ]
    diagnostics = [
        line
        for line in lines
        if re.search(
            r"STT|Groq|trascri|rejected|fine-utterance",
            line,
            re.IGNORECASE,
        )
    ][:18]

    result.log_lines = ordered_subset(
        lines,
        [*selected, *diagnostics],
    )
    result.timestamps = {
        "call_connected": iso_wall(
            leg.call.connected_wall
            if leg and leg.call
            else None
        ),
        "greeting_end_rtp": iso_wall(
            greeting[1] if greeting else None
        ),
        "identity_reply_end_rtp": iso_wall(
            identity_reply[1]
            if identity_reply
            else None
        ),
        "strike_1": extract_ts_text(strikes[0]),
        "strike_2": extract_ts_text(strikes[1]),
        "strike_3": extract_ts_text(strikes[2]),
        "e6": extract_ts_text(e6),
        "goodbye_text": extract_ts_text(goodbye),
        "goodbye_end_rtp": iso_wall(goodbye_end),
        "bye": extract_ts_text(bye),
    }
    result.metrics = {
        "identity_ok": identity_ok,
        "ordered_strikes": ordered_strikes,
        "honest_goodbye": honest,
        "bye_delta": bye_delta,
        "bye_log_present": bye is not None,
    }

    failed = []
    if not identity_ok:
        failed.append("FSM oltre identità")
    if not ordered_strikes:
        failed.append("strike 1→2→3")
    if e6 is None:
        failed.append("E6")
    if not honest:
        failed.append(
            "congedo richiamar/no-collega"
        )
    if not bye_ok:
        failed.append("BYE≤2s")

    if failed:
        prior = (
            result.reason
            if result.reason != "scenario non eseguito"
            else ""
        )
        result.verdict = FAIL
        result.reason = (
            (prior + "; " if prior else "")
            + "criteri non maturati: "
            + ", ".join(failed)
        )
    else:
        result.verdict = PASS
        result.reason = (
            "strike 1→2→3, E6, congedo onesto "
            "e BYE entro 2s"
        )

    return result


def run_scn09_attempt(
    attempt: int,
    local_index: int,
    sample_temp: Path,
) -> Evidence:
    result = Evidence(
        attempt=attempt,
        sample_temp=sample_temp,
    )
    offset = log_offset()
    capture_temp = sample_temp.with_name(
        f"scn09_capture_a{attempt}.wav"
    )
    leg: Optional[SipLeg] = None
    greeting: Optional[Tuple[float, float]] = None
    reprompt_start: Optional[float] = None

    try:
        leg = SipLeg(
            LOCAL_SIP_PORTS[local_index],
            LOCAL_RTP_PORTS[local_index],
        )
        leg.start()

        if not leg.wait_connected(12.0):
            raise ScenarioStop(
                "INVITE/media non confermati "
                f"({leg.call.last_status})"
            )

        greeting = leg.wait_segment(0, 22.0)
        if greeting is None:
            raise ScenarioStop(
                "fine greeting RTP non rilevata"
            )

        # No caller audio is enqueued after the greeting. Pump the SIP leg
        # while the Go engine's 22.0 s idle timer arms from its last TX frame
        # and fires.
        target_deadline = greeting[1] + 27.0
        next_grep = 0.0

        while (
            time.time() < target_deadline
            and not leg.call.done.is_set()
        ):
            leg.pump_once(20)
            now_monotonic = time.monotonic()

            if now_monotonic >= next_grep:
                lines = grep_since(
                    offset,
                    IDLE_GREP,
                )
                trigger = find_idle_trigger(lines)
                if (
                    trigger is not None
                    and len(leg.port.rx_starts) > 1
                ):
                    reprompt_start = (
                        leg.port.rx_starts[1]
                    )
                    break
                next_grep = now_monotonic + 0.45

            time.sleep(0.04)

        if reprompt_start is None:
            reprompt_start = leg.wait_rx_start(
                1,
                5.0,
            )

    except ScenarioStop as exc:
        result.reason = str(exc)
    except Exception as exc:
        result.reason = (
            f"eccezione {type(exc).__name__}: {exc}"
        )
    finally:
        if leg is not None:
            leg.close(capture_temp)

    lines = grep_since(offset, IDLE_GREP)
    arming = find_idle_arming(lines)
    trigger = find_idle_trigger(lines)
    trigger_index = (
        lines.index(trigger)
        if trigger in lines
        else -1
    )
    reprompt_tts = find_reprompt_tts(
        lines,
        trigger_index,
    )
    greeting_end = (
        greeting[1]
        if greeting
        else None
    )
    delta_audio = (
        None
        if (
            greeting_end is None
            or reprompt_start is None
        )
        else reprompt_start - greeting_end
    )
    trigger_wall = log_epoch(
        trigger,
        greeting_end,
    )
    delta_trigger = (
        None
        if (
            greeting_end is None
            or trigger_wall is None
        )
        else trigger_wall - greeting_end
    )

    trigger_ok = (
        trigger is not None
        and delta_trigger is not None
        and -0.10 <= delta_trigger <= 25.0
    )
    audio_ok = (
        reprompt_start is not None
        and delta_audio is not None
        and 0.0 <= delta_audio <= 25.5
    )

    diagnostics = [
        line
        for line in lines
        if re.search(
            r"IDLE|reprompt|canned TTS|GATE2R-PY-TX",
            line,
            re.IGNORECASE,
        )
    ][:20]

    result.log_lines = ordered_subset(
        lines,
        [
            arming,
            trigger,
            reprompt_tts,
            *diagnostics,
        ],
    )
    result.timestamps = {
        "call_connected": iso_wall(
            leg.call.connected_wall
            if leg and leg.call
            else None
        ),
        "arming": extract_ts_text(arming),
        "greeting_end_rtp": iso_wall(greeting_end),
        "trigger": extract_ts_text(trigger),
        "reprompt_start_rtp": iso_wall(
            reprompt_start
        ),
    }
    result.metrics = {
        "trigger_delta": delta_trigger,
        "reprompt_audio_delta": delta_audio,
        "arming_present": arming is not None,
        "trigger_present": trigger is not None,
        "reprompt_tts_present": (
            reprompt_tts is not None
        ),
    }

    failed = []
    if trigger is None:
        failed.append("scatto reprompt_timer")
    if not trigger_ok:
        failed.append("trigger entro 25s")
    if not (
        audio_ok
        or reprompt_tts is not None
    ):
        failed.append("reprompt presente")

    if failed:
        prior = (
            result.reason
            if result.reason != "scenario non eseguito"
            else ""
        )
        result.verdict = FAIL
        result.reason = (
            (prior + "; " if prior else "")
            + "criteri non maturati: "
            + ", ".join(failed)
        )
    else:
        result.verdict = PASS
        result.reason = (
            "reprompt_timer scattato e reprompt presente "
            "entro 25s dalla fine greeting"
        )

    return result


def evidence_block(
    lines: Sequence[str],
) -> str:
    if not lines:
        return ND
    return (
        "```text\n"
        + "\n".join(lines)
        + "\n```"
    )


def build_report(
    scn08: Evidence,
    scn09: Evidence,
    sample_ok: bool,
) -> str:
    timestamps_08 = scn08.timestamps
    metrics_08 = scn08.metrics
    timestamps_09 = scn09.timestamps
    metrics_09 = scn09.metrics

    lines = [
        "## Esiti F3-SIP",
        "",
        (
            "**Data:** "
            + datetime.now()
            .astimezone()
            .isoformat(timespec="seconds")
        ),
        (
            "**Rig:** loopback Sara "
            f"HTTP :{SARA_HTTP_PORT} · "
            f"regstub :{REGSTUB_PORT} · "
            f"SIP :{SARA_SIP_PORT} · "
            f"bridge :{BRIDGE_PORT}"
        ),
        (
            f"**WAV campione:** `{SAMPLE_PATH}`"
            if sample_ok
            else "**WAV campione:** ND"
        ),
        "",
        "### SCN-08 — E6 sulla gamba SIP",
        f"**Verdetto:** {scn08.verdict}",
        (
            "**Tentativo usato:** "
            f"{scn08.attempt or ND}"
        ),
        f"**Motivo:** {scn08.reason}",
        (
            "**Chiamata connessa:** "
            f"{timestamps_08.get('call_connected', ND)}"
        ),
        (
            "**Fine greeting RTP:** "
            f"{timestamps_08.get('greeting_end_rtp', ND)}"
        ),
        (
            "**Fine risposta identità RTP:** "
            f"{timestamps_08.get('identity_reply_end_rtp', ND)}"
        ),
        (
            "**Strike 1 timestamp:** "
            f"{timestamps_08.get('strike_1', ND)}"
        ),
        (
            "**Strike 2 timestamp:** "
            f"{timestamps_08.get('strike_2', ND)}"
        ),
        (
            "**Strike 3 timestamp:** "
            f"{timestamps_08.get('strike_3', ND)}"
        ),
        (
            "**E6 timestamp:** "
            f"{timestamps_08.get('e6', ND)}"
        ),
        (
            "**Goodbye-TTS testo timestamp:** "
            f"{timestamps_08.get('goodbye_text', ND)}"
        ),
        (
            "**Fine goodbye-TTS RTP:** "
            f"{timestamps_08.get('goodbye_end_rtp', ND)}"
        ),
        (
            "**BYE timestamp:** "
            f"{timestamps_08.get('bye', ND)}"
        ),
        (
            "**BYE dalla fine goodbye-TTS:** "
            f"{fmt_delta(metrics_08.get('bye_delta'))}"
        ),
        (
            "**Congedo contiene «richiamar» "
            "e non «collega»:** "
            + (
                "SÌ"
                if metrics_08.get("honest_goodbye")
                else "NO"
            )
        ),
        "**Evidenza log VERBATIM:**",
        evidence_block(scn08.log_lines),
        "",
        "### SCN-09 — silenzio → reprompt",
        f"**Verdetto:** {scn09.verdict}",
        (
            "**Tentativo usato:** "
            f"{scn09.attempt or ND}"
        ),
        f"**Motivo:** {scn09.reason}",
        (
            "**Chiamata connessa:** "
            f"{timestamps_09.get('call_connected', ND)}"
        ),
        (
            "**Arming reprompt_timer timestamp:** "
            f"{timestamps_09.get('arming', ND)}"
        ),
        (
            "**Fine greeting-TTS RTP:** "
            f"{timestamps_09.get('greeting_end_rtp', ND)}"
        ),
        (
            "**Scatto reprompt_timer timestamp:** "
            f"{timestamps_09.get('trigger', ND)}"
        ),
        (
            "**Inizio reprompt RTP:** "
            f"{timestamps_09.get('reprompt_start_rtp', ND)}"
        ),
        (
            "**Delta trigger dalla fine greeting:** "
            f"{fmt_delta(metrics_09.get('trigger_delta'))}"
        ),
        (
            "**Delta audio reprompt dalla fine greeting:** "
            f"{fmt_delta(metrics_09.get('reprompt_audio_delta'))}"
        ),
        "**Evidenza log VERBATIM:**",
        evidence_block(scn09.log_lines),
        "",
    ]
    return "\n".join(lines)


def atomic_write(
    path: Path,
    text: str,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    temp = path.with_name(
        f".{path.name}.{os.getpid()}.tmp"
    )

    try:
        temp.write_text(
            text,
            encoding="utf-8",
        )
        os.replace(temp, path)
    finally:
        try:
            temp.unlink()
        except OSError:
            pass


def choose_result(
    attempts: Sequence[Evidence],
) -> Evidence:
    for result in attempts:
        if result.verdict == PASS:
            return result

    return (
        attempts[-1]
        if attempts
        else Evidence()
    )


def main() -> int:
    OUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )
    scn08_attempts: List[Evidence] = []
    scn09_attempts: List[Evidence] = []
    sample_ok = False

    with tempfile.TemporaryDirectory(
        prefix="fluxion_f3_sip_"
    ) as temp_name:
        temp_dir = Path(temp_name)

        try:
            identity_pcm = render_speech(
                "Sono Marco Rossi, cliente nuovo",
                temp_dir / "identity.wav",
            )
            carrier_pcm = render_speech(
                (
                    "Marco desidera informazioni per una nuova "
                    "registrazione e vorrebbe parlare con Sara "
                    "domani mattina"
                ),
                temp_dir / "carrier.wav",
            )

            profiles = []
            for profile in (0, 1):
                clips = [
                    speech_like_babble(
                        carrier_pcm,
                        (
                            760230
                            + profile * 101
                            + index * 17
                        ),
                        profile,
                    )
                    for index in range(3)
                ]
                profiles.append(clips)
                write_wav(
                    temp_dir
                    / f"babble_profile_{profile}.wav",
                    clips[0],
                )

            for attempt in (1, 2):
                result = run_scn08_attempt(
                    attempt,
                    attempt - 1,
                    identity_pcm,
                    profiles[attempt - 1],
                    temp_dir
                    / f"scn08_a{attempt}_sample.wav",
                )
                scn08_attempts.append(result)

                if result.verdict == PASS:
                    break

            for attempt in (1, 2):
                result = run_scn09_attempt(
                    attempt,
                    1 + attempt,
                    temp_dir
                    / f"scn09_a{attempt}_sample.wav",
                )
                scn09_attempts.append(result)

                if result.verdict == PASS:
                    break

            scn08 = choose_result(
                scn08_attempts
            )
            scn09 = choose_result(
                scn09_attempts
            )

            # Copy one actual run WAV to the run root. Prefer captured RTP;
            # if capture is unavailable, copy the exact injected babble sample.
            capture_candidates = (
                sorted(
                    temp_dir.glob(
                        "scn08_capture_a*.wav"
                    )
                )
                + sorted(
                    temp_dir.glob(
                        "scn09_capture_a*.wav"
                    )
                )
            )
            source = next(
                (
                    path
                    for path in capture_candidates
                    if (
                        path.is_file()
                        and path.stat().st_size > 44
                    )
                ),
                None,
            )

            if source is None:
                source = (
                    temp_dir
                    / "babble_profile_0.wav"
                )

            if source.is_file():
                shutil.copy2(
                    source,
                    SAMPLE_PATH,
                )
                sample_ok = (
                    SAMPLE_PATH.is_file()
                    and SAMPLE_PATH.stat().st_size > 44
                )

        except Exception as exc:
            message = (
                "preparazione/runtime fallita: "
                f"{type(exc).__name__}: {exc}"
            )
            scn08 = Evidence(
                verdict=FAIL,
                reason=message,
            )
            scn09 = Evidence(
                verdict=FAIL,
                reason=message,
            )

        try:
            atomic_write(
                REPORT_PATH,
                build_report(
                    scn08,
                    scn09,
                    sample_ok,
                ),
            )
            report_ok = True
        except Exception:
            report_ok = False

    print(f"SCN-08: {scn08.verdict}")
    print(f"SCN-08: {scn08.reason}")
    print(f"SCN-09: {scn09.verdict}")
    print(f"SCN-09: {scn09.reason}")

    return (
        0
        if (
            scn08.verdict == PASS
            and scn09.verdict == PASS
            and sample_ok
            and report_ok
        )
        else 1
    )


if __name__ == "__main__":
    sys.exit(main())
