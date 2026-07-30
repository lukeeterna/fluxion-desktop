# Setup SIP preso da voice-agent/scripts/sara_audio_harness.py, senza ricostruire INVITE o SDP.
# Quel percorso crea una sola media audio predefinita e collega HarnessAudioPort solo dopo la negoziazione.
# SCN-08 usa parlato TTS reale scomposto, invertito e rimiscelato in babble formantico non trascrivibile.
from __future__ import annotations

import importlib.util
import math
import os
import random
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import wave
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, Iterable, List, Optional, Sequence, Tuple

LOOPBACK = "127.0.0.1"
SARA_SIP_PORT = 15090
LOCAL_SIP_PORTS = (15082, 15083, 15084, 15085)
SARA_USER = os.getenv("VOIP_SIP_USER", "0972536918").strip() or "0972536918"

LOG_PATH = Path("/tmp/rig_sara3003.log")
OUT_DIR = Path(__file__).resolve().parent
REPORT_PATH = OUT_DIR / "f3_sip_esiti_v2.md"
SAMPLE_PATH = OUT_DIR / "f3_sip_v2_sample.wav"

REPO_ROOT = Path(__file__).resolve().parents[3]
HARNESS_PATH = (
    REPO_ROOT
    / "voice-agent"
    / "scripts"
    / "sara_audio_harness.py"
)

FRAME_BYTES = 320
FRAME_SECONDS = 0.020
RATE = 8000

PASS = "PASS"
FAIL = "FAIL"
ND = "ND"

CONNECTION_GREP = (
    r"INVITE|480|temporar|unavailable|more than 1 media line|"
    r"SDP|reject|rifiut"
)
E6_GREP = (
    r"CALL_START|greeting|TTS done|fine-utterance|VAD|Silero|"
    r"STT|Groq|trascri|empty|vuot|reject|strike|E6|richiamar|"
    r"collega|HANGUP|BYE|CALL_END"
)
REPROMPT_GREP = (
    r"CALL_START|greeting|TTS done|reprompt|idle|silence|silenz|"
    r"timer|canned TTS|HANGUP|BYE|CALL_END"
)
TIMESTAMP_PATTERNS = (
    re.compile(
        r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}"
        r"(?:[.,]\d{1,6})?"
    ),
    re.compile(
        r"\b\d{2}:\d{2}:\d{2}(?:[.,]\d{1,6})?\b"
    ),
)


@dataclass
class Result:
    scenario: str
    verdict: str = FAIL
    reason: str = "scenario non eseguito"
    attempt: int = 0
    evidence: List[str] = field(default_factory=list)
    timestamps: dict = field(default_factory=dict)
    metrics: dict = field(default_factory=dict)


@dataclass
class GateFailure(Exception):
    code: int
    reason: str
    log_line: str

    def __str__(self) -> str:
        return (
            f"SIP {self.code or ND} "
            f"{self.reason or ND}"
        ).strip()


@contextmanager
def muted_native_output():
    """Impedisce ai log nativi pjsua2 di contaminare stdout."""
    sys.stdout.flush()
    sys.stderr.flush()

    saved_out = os.dup(1)
    saved_err = os.dup(2)

    try:
        with open(os.devnull, "wb", buffering=0) as sink:
            os.dup2(sink.fileno(), 1)
            os.dup2(sink.fileno(), 2)
            yield
    finally:
        os.dup2(saved_out, 1)
        os.dup2(saved_err, 2)
        os.close(saved_out)
        os.close(saved_err)


def load_harness():
    if not HARNESS_PATH.is_file():
        raise RuntimeError(
            f"harness assente: {HARNESS_PATH}"
        )

    spec = importlib.util.spec_from_file_location(
        "fluxion_sara_audio_harness",
        HARNESS_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(
            "impossibile caricare sara_audio_harness.py"
        )

    module = importlib.util.module_from_spec(spec)

    try:
        spec.loader.exec_module(module)
    except SystemExit as exc:
        raise RuntimeError(
            "import harness terminato con "
            f"SystemExit({exc.code})"
        ) from exc

    return module


def log_offset() -> int:
    try:
        return LOG_PATH.stat().st_size
    except OSError:
        return 0


def grep_since(
    offset: int,
    pattern: str,
) -> List[str]:
    """Esegue grep solo sui byte aggiunti dopo offset."""
    if not LOG_PATH.is_file():
        return []

    try:
        size = LOG_PATH.stat().st_size
        start = 1 if size < offset else offset + 1

        tail = subprocess.Popen(
            [
                "tail",
                "-c",
                f"+{start}",
                str(LOG_PATH),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )

        grep = subprocess.run(
            [
                "grep",
                "-E",
                "-i",
                pattern,
            ],
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
        return [
            line
            for line in lines
            if not (
                line in seen
                or seen.add(line)
            )
        ]

    except (
        OSError,
        subprocess.SubprocessError,
    ):
        return []


def first_match(
    lines: Sequence[str],
    patterns: Sequence[str],
    start: int = 0,
) -> Optional[str]:
    for line in lines[max(0, start):]:
        if any(
            re.search(
                pattern,
                line,
                re.IGNORECASE,
            )
            for pattern in patterns
        ):
            return line

    return None


def line_index(
    lines: Sequence[str],
    line: Optional[str],
) -> int:
    if line is None:
        return -1

    try:
        return lines.index(line)
    except ValueError:
        return -1


def ordered_evidence(
    lines: Sequence[str],
    selected: Iterable[Optional[str]],
) -> List[str]:
    wanted = {
        line
        for line in selected
        if line
    }

    return [
        line
        for line in lines
        if line in wanted
    ]


def timestamp_text(
    line: Optional[str],
) -> str:
    if not line:
        return ND

    for pattern in TIMESTAMP_PATTERNS:
        match = pattern.search(line)
        if match:
            return match.group(0)

    return ND


def timestamp_epoch(
    line: Optional[str],
    reference: Optional[float],
) -> Optional[float]:
    text = timestamp_text(line)

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
            (
                "%H:%M:%S.%f"
                if "." in text
                else "%H:%M:%S"
            ),
        )

        ref = datetime.fromtimestamp(
            reference or time.time()
        ).astimezone()

        value = ref.replace(
            hour=parsed.hour,
            minute=parsed.minute,
            second=parsed.second,
            microsecond=parsed.microsecond,
        )

        if (
            value.timestamp()
            - ref.timestamp()
            > 43200
        ):
            value -= timedelta(days=1)
        elif (
            ref.timestamp()
            - value.timestamp()
            > 43200
        ):
            value += timedelta(days=1)

        return value.timestamp()

    except (
        ValueError,
        OverflowError,
        OSError,
    ):
        return None


def iso_wall(
    value: Optional[float],
) -> str:
    if value is None:
        return ND

    return datetime.fromtimestamp(
        value
    ).astimezone().isoformat(
        timespec="milliseconds"
    )


def fmt_delta(
    value: Optional[float],
) -> str:
    if value is None:
        return ND

    return f"{value:.3f}s"


def rms16(pcm: bytes) -> float:
    usable = len(pcm) - len(pcm) % 2

    if usable == 0:
        return 0.0

    values = struct.unpack(
        "<" + "h" * (usable // 2),
        pcm[:usable],
    )

    return math.sqrt(
        sum(
            value * value
            for value in values
        )
        / len(values)
    )


def write_wav(
    path: Path,
    pcm: bytes,
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with wave.open(
        str(path),
        "wb",
    ) as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(RATE)
        wav_file.writeframes(pcm)


def build_babble(
    carrier: bytes,
    seed: int,
    profile: int,
) -> bytes:
    """Mantiene formanti vocali, distruggendo la continuità fonetica."""
    frames = [
        carrier[
            index:index + FRAME_BYTES
        ]
        for index in range(
            0,
            len(carrier) - FRAME_BYTES + 1,
            FRAME_BYTES,
        )
    ]

    voiced = [
        frame
        for frame in frames
        if rms16(frame) >= 550.0
    ]

    if len(voiced) < 18:
        raise RuntimeError(
            "carrier insufficiente per generare "
            "babble speech-like"
        )

    rng = random.Random(seed)
    output = bytearray()
    target_rms = (
        1150.0
        if profile == 0
        else 900.0
    )
    frame_count = (
        76
        if profile == 0
        else 70
    )

    for index in range(frame_count):
        chosen = rng.sample(
            voiced,
            3,
        )

        first = struct.unpack(
            "<160h",
            chosen[0],
        )
        second = list(
            reversed(
                struct.unpack(
                    "<160h",
                    chosen[1],
                )
            )
        )
        third = list(
            struct.unpack(
                "<160h",
                chosen[2],
            )
        )

        shift = (
            index
            * (
                23
                if profile == 0
                else 31
            )
        ) % 160

        third = (
            third[shift:]
            + third[:shift]
        )

        mixed = []

        for sample_index in range(160):
            value = (
                0.55 * first[sample_index]
                + 0.34 * second[sample_index]
                + 0.27 * third[sample_index]
            )

            microblock = (
                20
                if profile == 0
                else 10
            )

            if (
                (
                    sample_index
                    // microblock
                )
                + index
            ) & 1:
                value = -value

            mixed.append(value)

        current = math.sqrt(
            sum(
                value * value
                for value in mixed
            )
            / len(mixed)
        ) or 1.0

        gain = min(
            8.0,
            target_rms / current,
        )

        envelope = min(
            1.0,
            (index + 1) / 4.0,
            (frame_count - index) / 4.0,
        )

        packed = [
            max(
                -14000,
                min(
                    14000,
                    int(
                        value
                        * gain
                        * envelope
                    ),
                ),
            )
            for value in mixed
        ]

        output.extend(
            struct.pack(
                "<160h",
                *packed,
            )
        )

    pcm = bytes(output)

    if rms16(pcm) < 700.0:
        raise RuntimeError(
            "babble sotto il margine speech-like"
        )

    return pcm


class RxTracker:
    def __init__(self, call) -> None:
        self.call = call
        self.processed = 0
        self.base_wall: Optional[float] = None
        self.hot_run = 0
        self.candidate_start: Optional[float] = None
        self.active = False
        self.active_start: Optional[float] = None
        self.last_hot_end: Optional[float] = None
        self.quiet_run = 0
        self.starts: List[float] = []
        self.segments: List[
            Tuple[float, float]
        ] = []

    def update(self) -> None:
        chunks = (
            self.call
            .audio_port
            .rx_chunks
        )

        if (
            self.base_wall is None
            and chunks
        ):
            self.base_wall = (
                time.time()
                - len(chunks)
                * FRAME_SECONDS
            )

        while self.processed < len(chunks):
            chunk = chunks[self.processed]

            frame_start = (
                self.base_wall
                or time.time()
            ) + (
                self.processed
                * FRAME_SECONDS
            )

            self.processed += 1
            hot = rms16(chunk) >= 220.0

            if hot:
                self.last_hot_end = (
                    frame_start
                    + FRAME_SECONDS
                )
                self.quiet_run = 0

                if not self.active:
                    if self.hot_run == 0:
                        self.candidate_start = (
                            frame_start
                        )

                    self.hot_run += 1

                    if self.hot_run >= 5:
                        self.active = True
                        self.active_start = (
                            self.candidate_start
                        )
                        self.starts.append(
                            self.active_start
                            or frame_start
                        )
            else:
                if self.active:
                    self.quiet_run += 1

                    if self.quiet_run >= 30:
                        self._finish(
                            self.last_hot_end
                            or frame_start
                        )
                else:
                    self.hot_run = 0
                    self.candidate_start = None

    def _finish(
        self,
        end: float,
    ) -> None:
        start = (
            self.active_start
            or end
        )

        self.segments.append(
            (
                start,
                max(
                    start,
                    end,
                ),
            )
        )

        self.hot_run = 0
        self.candidate_start = None
        self.active = False
        self.active_start = None
        self.last_hot_end = None
        self.quiet_run = 0

    def flush(
        self,
        wall: Optional[float] = None,
    ) -> None:
        self.update()

        if self.active:
            self._finish(
                self.last_hot_end
                or wall
                or time.time()
            )

    def latest_end(self) -> Optional[float]:
        self.update()

        if not self.segments:
            return None

        return self.segments[-1][1]

    def first_start_after(
        self,
        wall: float,
    ) -> Optional[float]:
        self.update()

        return next(
            (
                value
                for value in self.starts
                if value > wall
            ),
            None,
        )


class HarnessLeg:
    """Setup fino a makeCall copiato dall'harness di giugno."""

    def __init__(
        self,
        harness,
        local_port: int,
        offset: int,
    ) -> None:
        self.h = harness
        self.pj = harness.pj
        self.local_port = local_port
        self.offset = offset

        self.ep = None
        self.acc = None
        self.call = None
        self.tracker = None

        self.confirmed_at: Optional[float] = None
        self.disconnected_at: Optional[float] = None

        self.status_code = 0
        self.status_reason = ND

    def open(self) -> None:
        pj = self.pj

        ep = pj.Endpoint()
        ep.libCreate()

        ep_cfg = pj.EpConfig()
        ep_cfg.uaConfig.userAgent = (
            "FLUXION-Harness/1.0"
        )
        ep_cfg.uaConfig.threadCnt = 0
        ep_cfg.uaConfig.mainThreadOnly = True
        ep_cfg.medConfig.noVad = True
        ep_cfg.medConfig.srtpUse = 0
        ep.libInit(ep_cfg)

        tp_cfg = pj.TransportConfig()
        tp_cfg.port = self.local_port

        ep.transportCreate(
            pj.PJSIP_TRANSPORT_UDP,
            tp_cfg,
        )
        ep.libStart()
        ep.audDevManager().setNullDev()

        acc_cfg = pj.AccountConfig()
        acc_cfg.idUri = (
            f"sip:harness@"
            f"{LOOPBACK}:"
            f"{self.local_port}"
        )

        acc = self.h.HarnessAccount()
        acc.create(acc_cfg)

        target = (
            f"sip:{SARA_USER}@"
            f"{LOOPBACK}:"
            f"{SARA_SIP_PORT}"
        )

        call = self.h.HarnessCall(acc)
        call_prm = pj.CallOpParam(True)
        call.makeCall(
            target,
            call_prm,
        )

        self.ep = ep
        self.acc = acc
        self.call = call
        self.tracker = RxTracker(call)

    def pump(
        self,
        milliseconds: int = 20,
    ) -> None:
        if (
            self.ep is None
            or self.call is None
        ):
            return

        self.ep.libHandleEvents(
            milliseconds
        )

        try:
            info = self.call.getInfo()

            self.status_code = int(
                info.lastStatusCode
            )
            self.status_reason = str(
                info.lastReason
                or ND
            )

            if (
                info.state
                == self.pj.PJSIP_INV_STATE_CONFIRMED
                and self.confirmed_at is None
            ):
                self.confirmed_at = time.time()

            if (
                info.state
                == self.pj.PJSIP_INV_STATE_DISCONNECTED
                and self.disconnected_at is None
            ):
                self.disconnected_at = time.time()

        except self.pj.Error:
            pass

        self.tracker.update()

    def wait(
        self,
        predicate: Callable[[], bool],
        timeout: float,
    ) -> bool:
        deadline = (
            time.monotonic()
            + timeout
        )

        while time.monotonic() < deadline:
            self.pump(20)

            if predicate():
                return True

            time.sleep(0.02)

        self.pump(0)
        return predicate()

    def gate(
        self,
        timeout: float = 12.0,
    ) -> None:
        confirmed = (
            self.wait(
                lambda: (
                    bool(self.call.connected)
                    or self.call.done.is_set()
                ),
                timeout,
            )
            and bool(self.call.connected)
        )

        if confirmed:
            self.confirmed_at = (
                self.confirmed_at
                or time.time()
            )
            return

        refusal = None
        deadline = (
            time.monotonic()
            + 1.5
        )

        while (
            time.monotonic() < deadline
            and refusal is None
        ):
            refusal = first_match(
                grep_since(
                    self.offset,
                    CONNECTION_GREP,
                ),
                (
                    r"more than 1 media line",
                    r"\b480\b",
                    r"temporar",
                    r"reject",
                    r"INVITE",
                    r"SDP",
                ),
            )

            if refusal is None:
                time.sleep(0.10)

        raise GateFailure(
            self.status_code,
            self.status_reason,
            refusal or ND,
        )

    def media_ready(
        self,
        timeout: float = 4.0,
    ) -> bool:
        return self.wait(
            lambda: bool(
                self.call
                .audio_port
                ._port_created
            ),
            timeout,
        )

    def send(
        self,
        pcm: bytes,
        tail_silence: float = 1.20,
    ) -> bool:
        port = self.call.audio_port
        port._tx_done.clear()
        port.load_wav(pcm)

        duration = (
            len(pcm)
            / 16000.0
        )
        started = time.monotonic()

        emptied = self.wait(
            lambda: (
                port.tx_queue.empty()
                and (
                    time.monotonic()
                    - started
                )
                >= duration * 0.80
            ),
            duration + 5.0,
        )

        self.wait(
            lambda: False,
            tail_silence,
        )

        return emptied

    def wait_audio_idle(
        self,
        timeout: float,
        quiet: float = 1.15,
        after: Optional[float] = None,
    ) -> Optional[float]:
        deadline = (
            time.monotonic()
            + timeout
        )

        while (
            time.monotonic() < deadline
            and not self.call.done.is_set()
        ):
            self.pump(20)
            end = self.tracker.latest_end()

            if (
                end is not None
                and (
                    after is None
                    or end > after
                )
                and not self.tracker.active
                and (
                    time.time()
                    - end
                    >= quiet
                )
            ):
                return end

            time.sleep(0.02)

        end = self.tracker.latest_end()

        if (
            end is not None
            and (
                after is None
                or end > after
            )
        ):
            return end

        return None

    def wait_log(
        self,
        pattern: str,
        predicate: Callable[
            [Sequence[str]],
            bool,
        ],
        timeout: float,
    ) -> List[str]:
        deadline = (
            time.monotonic()
            + timeout
        )
        lines: List[str] = []
        next_grep = 0.0

        while time.monotonic() < deadline:
            self.pump(20)
            now = time.monotonic()

            if now >= next_grep:
                lines = grep_since(
                    self.offset,
                    pattern,
                )

                if predicate(lines):
                    return lines

                next_grep = now + 0.40

            if (
                self.call.done.is_set()
                and predicate(lines)
            ):
                return lines

            time.sleep(0.02)

        return grep_since(
            self.offset,
            pattern,
        )

    def close(
        self,
        capture: Optional[Path] = None,
    ) -> None:
        if self.call is not None:
            try:
                if not self.call.done.is_set():
                    self.call.hangup(
                        self.pj.CallOpParam(True)
                    )
                    self.wait(
                        self.call.done.is_set,
                        2.0,
                    )
            except Exception:
                pass

            self.disconnected_at = (
                self.disconnected_at
                or (
                    time.time()
                    if self.call.done.is_set()
                    else None
                )
            )

            self.tracker.flush(
                self.disconnected_at
            )

            if capture is not None:
                try:
                    self.call.audio_port.write_capture(
                        str(capture)
                    )
                except Exception:
                    pass

        if self.ep is not None:
            try:
                self.ep.libDestroy()
            except Exception:
                pass


def find_strike(
    lines: Sequence[str],
    number: int,
) -> Optional[str]:
    patterns = (
        rf"\bstrike(?:s)?\b"
        rf"[^0-9]{{0,40}}"
        rf"{number}\s*(?:/|of)\s*3\b",

        rf"\bstrike(?:s)?\b"
        rf"[^0-9]{{0,40}}"
        rf"(?:=|:|#)\s*{number}\b",

        rf"\bstt[_ -]?"
        rf"(?:failure|failures)\b"
        rf"[^0-9]{{0,40}}"
        rf"{number}\s*(?:/\s*3)?\b",

        rf"\b{number}\s*/\s*3\b"
        rf".*\b(?:strike|stt[_ -]?failure)\b",
    )

    return first_match(
        lines,
        patterns,
    )


def find_e6(
    lines: Sequence[str],
    start: int,
) -> Optional[str]:
    return first_match(
        lines,
        (
            r"\bE6\b.*"
            r"(?:trigger|scatt|escalat|threshold)",

            r"3-strike escalation",

            r"\bE6\b",
        ),
        start,
    )


def find_goodbye(
    lines: Sequence[str],
    start: int,
) -> Optional[str]:
    return first_match(
        lines,
        (
            r"richiamar",
            r"collega",
        ),
        start,
    )


def find_bye(
    lines: Sequence[str],
    start: int,
) -> Optional[str]:
    return first_match(
        lines,
        (r"\bBYE\b",),
        start,
    )


def diagnostic_lines(
    lines: Sequence[str],
    limit: int = 18,
) -> List[str]:
    selected = []

    for line in lines:
        if re.search(
            r"VAD|Silero|STT|Groq|trascri|"
            r"empty|vuot|reject|fine-utterance",
            line,
            re.IGNORECASE,
        ):
            selected.append(line)

            if len(selected) >= limit:
                break

    return selected


def _run_scn08_attempt(
    harness,
    attempt: int,
    port: int,
    identity: bytes,
    clips: Sequence[bytes],
    temp: Path,
) -> Result:
    result = Result(
        "SCN-08",
        attempt=attempt,
    )

    offset = log_offset()
    leg = HarnessLeg(
        harness,
        port,
        offset,
    )

    greeting_end = None
    identity_reply_end = None
    runtime_error = None

    try:
        leg.open()
        leg.gate()

        if not leg.media_ready():
            raise RuntimeError(
                "chiamata CONFIRMED ma media "
                "audio non attiva"
            )

        greeting_end = leg.wait_audio_idle(
            24.0
        )

        if greeting_end is None:
            raise RuntimeError(
                "fine greeting RTP non rilevata"
            )

        identity_sent_at = time.time()

        leg.send(identity)

        identity_reply_end = (
            leg.wait_audio_idle(
                22.0,
                after=identity_sent_at,
            )
        )

        for number, clip in enumerate(
            clips,
            1,
        ):
            if leg.call.done.is_set():
                break

            leg.send(clip)

            leg.wait_log(
                E6_GREP,
                lambda lines, n=number: (
                    find_strike(
                        lines,
                        n,
                    )
                    is not None
                ),
                18.0,
            )

        leg.wait_log(
            E6_GREP,
            lambda lines: (
                find_bye(
                    lines,
                    0,
                )
                is not None
                or leg.call.done.is_set()
            ),
            25.0,
        )

    except GateFailure:
        raise

    except Exception as exc:
        runtime_error = (
            f"{type(exc).__name__}: {exc}"
        )

    finally:
        leg.close(
            temp
            / f"scn08_capture_a{attempt}.wav"
        )

    lines = grep_since(
        offset,
        E6_GREP,
    )

    strikes = [
        find_strike(
            lines,
            number,
        )
        for number in (1, 2, 3)
    ]

    strike_indices = [
        line_index(
            lines,
            line,
        )
        for line in strikes
    ]

    ordered = (
        all(
            index >= 0
            for index in strike_indices
        )
        and (
            strike_indices[0]
            < strike_indices[1]
            < strike_indices[2]
        )
    )

    e6 = find_e6(
        lines,
        (
            strike_indices[2] + 1
            if strike_indices[2] >= 0
            else 0
        ),
    )

    e6_index = line_index(
        lines,
        e6,
    )

    goodbye = find_goodbye(
        lines,
        (
            e6_index + 1
            if e6_index >= 0
            else 0
        ),
    )

    goodbye_index = line_index(
        lines,
        goodbye,
    )

    bye = find_bye(
        lines,
        (
            goodbye_index + 1
            if goodbye_index >= 0
            else 0
        ),
    )

    honest = bool(
        goodbye
        and "richiamar" in goodbye.lower()
        and "collega" not in goodbye.lower()
    )

    goodbye_end = (
        leg.tracker.segments[-1][1]
        if leg.tracker.segments
        else None
    )

    bye_wall = (
        leg.disconnected_at
        if bye is not None
        else timestamp_epoch(
            bye,
            goodbye_end,
        )
    )

    bye_delta = (
        None
        if (
            goodbye_end is None
            or bye_wall is None
        )
        else bye_wall - goodbye_end
    )

    bye_ok = (
        bye is not None
        and bye_delta is not None
        and -0.10 <= bye_delta <= 2.0
    )

    identity_ok = (
        identity_reply_end is not None
        and greeting_end is not None
        and identity_reply_end > greeting_end
    )

    selected = [
        *strikes,
        e6,
        goodbye,
        bye,
    ]

    if not (
        identity_ok
        and ordered
        and e6
        and honest
        and bye_ok
    ):
        selected.extend(
            diagnostic_lines(lines)
        )

    result.evidence = ordered_evidence(
        lines,
        selected,
    )

    result.timestamps = {
        "confirmed": iso_wall(
            leg.confirmed_at
        ),
        "greeting_end": iso_wall(
            greeting_end
        ),
        "identity_reply_end": iso_wall(
            identity_reply_end
        ),
        "strike_1": timestamp_text(
            strikes[0]
        ),
        "strike_2": timestamp_text(
            strikes[1]
        ),
        "strike_3": timestamp_text(
            strikes[2]
        ),
        "e6": timestamp_text(e6),
        "goodbye": timestamp_text(
            goodbye
        ),
        "goodbye_end": iso_wall(
            goodbye_end
        ),
        "bye": timestamp_text(bye),
    }

    result.metrics = {
        "bye_delta": bye_delta,
        "honest": honest,
    }

    failed = []

    if not identity_ok:
        failed.append(
            "FSM oltre identità"
        )

    if not ordered:
        failed.append(
            "strike 1→2→3"
        )

    if e6 is None:
        failed.append("E6")

    if not honest:
        failed.append(
            "congedo richiamar/no-collega"
        )

    if not bye_ok:
        failed.append("BYE≤2s")

    if failed:
        prefix = (
            f"{runtime_error}; "
            if runtime_error
            else ""
        )

        result.reason = (
            prefix
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


def run_scn08_attempt(
    harness,
    attempt: int,
    port: int,
    identity: bytes,
    clips: Sequence[bytes],
    temp: Path,
) -> Result:
    with muted_native_output():
        return _run_scn08_attempt(
            harness,
            attempt,
            port,
            identity,
            clips,
            temp,
        )


def find_arm(
    lines: Sequence[str],
) -> Optional[str]:
    return first_match(
        lines,
        (
            r"reprompt[_ -]?timer.*"
            r"(?:arm|start)",

            r"timer.*22(?:\.0)?s",

            r"CALL_START",
        ),
    )


def find_reprompt_trigger(
    lines: Sequence[str],
) -> Optional[str]:
    return first_match(
        lines,
        (
            r"reprompt.*"
            r"(?:trigger|fire|scatt|expir)",

            r"IDLE.*2[12-5]"
            r"(?:\.\d+)?s.*reprompt",

            r"reprompt.*2[12-5]"
            r"(?:\.\d+)?s",

            r"silenz.*reprompt",
        ),
    )


def find_reprompt_tts(
    lines: Sequence[str],
    start: int,
) -> Optional[str]:
    return first_match(
        lines,
        (
            r"canned TTS.*"
            r"(?:linea|sente|pronto|presente|reprompt)",

            r"reprompt.*TTS",

            r"TTS.*reprompt",
        ),
        start,
    )


def _run_scn09_attempt(
    harness,
    attempt: int,
    port: int,
    temp: Path,
) -> Result:
    result = Result(
        "SCN-09",
        attempt=attempt,
    )

    offset = log_offset()

    leg = HarnessLeg(
        harness,
        port,
        offset,
    )

    greeting_end = None
    reprompt_start = None
    runtime_error = None

    try:
        leg.open()
        leg.gate()

        if not leg.media_ready():
            raise RuntimeError(
                "chiamata CONFIRMED ma media "
                "audio non attiva"
            )

        greeting_end = leg.wait_audio_idle(
            24.0
        )

        if greeting_end is None:
            raise RuntimeError(
                "fine greeting RTP non rilevata"
            )

        deadline = greeting_end + 27.0

        while (
            time.time() < deadline
            and not leg.call.done.is_set()
        ):
            leg.pump(20)

            reprompt_start = (
                leg.tracker.first_start_after(
                    greeting_end + 0.80
                )
            )

            lines = grep_since(
                offset,
                REPROMPT_GREP,
            )

            if (
                reprompt_start is not None
                and find_reprompt_trigger(
                    lines
                )
                is not None
            ):
                break

            time.sleep(0.02)

    except GateFailure:
        raise

    except Exception as exc:
        runtime_error = (
            f"{type(exc).__name__}: {exc}"
        )

    finally:
        leg.close(
            temp
            / f"scn09_capture_a{attempt}.wav"
        )

    lines = grep_since(
        offset,
        REPROMPT_GREP,
    )

    arm = find_arm(lines)
    trigger = find_reprompt_trigger(lines)

    trigger_index = line_index(
        lines,
        trigger,
    )

    reprompt_tts = find_reprompt_tts(
        lines,
        (
            trigger_index + 1
            if trigger_index >= 0
            else 0
        ),
    )

    trigger_wall = timestamp_epoch(
        trigger,
        greeting_end,
    )

    trigger_delta = (
        None
        if (
            greeting_end is None
            or trigger_wall is None
        )
        else trigger_wall - greeting_end
    )

    audio_delta = (
        None
        if (
            greeting_end is None
            or reprompt_start is None
        )
        else reprompt_start - greeting_end
    )

    within_25 = (
        audio_delta is not None
        and 0.0 <= audio_delta <= 25.5
    )

    selected = [
        arm,
        trigger,
        reprompt_tts,
    ]

    if not (
        trigger
        and within_25
        and (
            reprompt_tts
            or reprompt_start
        )
    ):
        selected.extend(
            line
            for line in lines
            if re.search(
                r"reprompt|IDLE|silence|silenz|"
                r"timer|canned TTS",
                line,
                re.IGNORECASE,
            )
        )

    result.evidence = ordered_evidence(
        lines,
        selected[:24],
    )

    result.timestamps = {
        "confirmed": iso_wall(
            leg.confirmed_at
        ),
        "arming": timestamp_text(
            arm
        ),
        "greeting_end": iso_wall(
            greeting_end
        ),
        "trigger": timestamp_text(
            trigger
        ),
        "reprompt_start": iso_wall(
            reprompt_start
        ),
    }

    result.metrics = {
        "trigger_delta": trigger_delta,
        "audio_delta": audio_delta,
    }

    failed = []

    if trigger is None:
        failed.append(
            "scatto reprompt_timer"
        )

    if (
        reprompt_start is None
        and reprompt_tts is None
    ):
        failed.append(
            "reprompt assente"
        )

    if not within_25:
        failed.append(
            "reprompt entro 25s"
        )

    if failed:
        prefix = (
            f"{runtime_error}; "
            if runtime_error
            else ""
        )

        result.reason = (
            prefix
            + "criteri non maturati: "
            + ", ".join(failed)
        )
    else:
        result.verdict = PASS
        result.reason = (
            "reprompt presente entro 25s "
            "dalla fine del greeting-TTS"
        )

    return result


def run_scn09_attempt(
    harness,
    attempt: int,
    port: int,
    temp: Path,
) -> Result:
    with muted_native_output():
        return _run_scn09_attempt(
            harness,
            attempt,
            port,
            temp,
        )


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


def report_text(
    scn08: Result,
    scn09: Result,
    sample_ok: bool,
) -> str:
    timestamps_08 = scn08.timestamps
    metrics_08 = scn08.metrics
    timestamps_09 = scn09.timestamps
    metrics_09 = scn09.metrics

    return "\n".join(
        [
            "## Esiti F3-SIP v2",
            "",
            (
                "**Data:** "
                + datetime.now()
                .astimezone()
                .isoformat(
                    timespec="seconds"
                )
            ),
            (
                "**Rig:** loopback Sara "
                "HTTP :3003 · "
                "regstub :15062 · "
                "SIP :15090 · "
                "bridge :8399"
            ),
            (
                f"**WAV campione:** "
                f"`{SAMPLE_PATH}`"
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
                "**Chiamata CONFIRMED:** "
                f"{timestamps_08.get('confirmed', ND)}"
            ),
            (
                "**Fine greeting-TTS RTP:** "
                f"{timestamps_08.get('greeting_end', ND)}"
            ),
            (
                "**Fine risposta identità RTP:** "
                f"{timestamps_08.get('identity_reply_end', ND)}"
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
                "**Goodbye-TTS timestamp:** "
                f"{timestamps_08.get('goodbye', ND)}"
            ),
            (
                "**Fine goodbye-TTS RTP:** "
                f"{timestamps_08.get('goodbye_end', ND)}"
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
                    if metrics_08.get("honest")
                    else "NO"
                )
            ),
            "**Evidenza log VERBATIM:**",
            evidence_block(
                scn08.evidence
            ),
            "",
            "### SCN-09 — silenzio → reprompt",
            f"**Verdetto:** {scn09.verdict}",
            (
                "**Tentativo usato:** "
                f"{scn09.attempt or ND}"
            ),
            f"**Motivo:** {scn09.reason}",
            (
                "**Chiamata CONFIRMED:** "
                f"{timestamps_09.get('confirmed', ND)}"
            ),
            (
                "**Arming reprompt_timer timestamp:** "
                f"{timestamps_09.get('arming', ND)}"
            ),
            (
                "**Fine greeting-TTS RTP:** "
                f"{timestamps_09.get('greeting_end', ND)}"
            ),
            (
                "**Scatto reprompt_timer timestamp:** "
                f"{timestamps_09.get('trigger', ND)}"
            ),
            (
                "**Inizio reprompt RTP:** "
                f"{timestamps_09.get('reprompt_start', ND)}"
            ),
            (
                "**Delta trigger:** "
                f"{fmt_delta(metrics_09.get('trigger_delta'))}"
            ),
            (
                "**Delta audio reprompt:** "
                f"{fmt_delta(metrics_09.get('audio_delta'))}"
            ),
            "**Evidenza log VERBATIM:**",
            evidence_block(
                scn09.evidence
            ),
            "",
        ]
    )


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
        os.replace(
            temp,
            path,
        )
    finally:
        try:
            temp.unlink()
        except OSError:
            pass


def gate_results(
    scenario: str,
    gate: GateFailure,
) -> Tuple[Result, Result]:
    line = gate.log_line or ND

    current = Result(
        scenario,
        verdict=FAIL,
        reason=(
            "gate connessione fallita: "
            f"SIP {gate.code or ND} "
            f"{gate.reason or ND}"
        ),
        evidence=(
            []
            if line == ND
            else [line]
        ),
        timestamps={
            "confirmed": ND,
        },
    )

    other_name = (
        "SCN-09"
        if scenario == "SCN-08"
        else "SCN-08"
    )

    other = Result(
        other_name,
        verdict=FAIL,
        reason=(
            "non eseguito: "
            "gate connessione fallita"
        ),
        timestamps={
            "confirmed": ND,
        },
    )

    if scenario == "SCN-08":
        return current, other

    return other, current


def choose(
    attempts: Sequence[Result],
) -> Result:
    return next(
        (
            item
            for item in attempts
            if item.verdict == PASS
        ),
        attempts[-1],
    )


def print_verdicts(
    scn08: Result,
    scn09: Result,
) -> None:
    print(
        f"SCN-08: {scn08.verdict}"
    )
    print(
        f"SCN-08: {scn08.reason}"
    )
    print(
        f"SCN-09: {scn09.verdict}"
    )
    print(
        f"SCN-09: {scn09.reason}"
    )


def print_gate_verdicts(
    scn08: Result,
    scn09: Result,
    gate_scenario: str,
    gate: GateFailure,
) -> None:
    if gate_scenario == "SCN-08":
        print(
            "SCN-08: FAIL — "
            f"SIP {gate.code or ND} "
            f"{gate.reason or ND}"
        )
        print(
            f"SCN-08: {gate.log_line or ND}"
        )
        print("SCN-09: FAIL")
        print(
            "SCN-09: non eseguito — "
            "gate connessione fallita"
        )
        return

    print(
        f"SCN-08: {scn08.verdict}"
    )
    print(
        f"SCN-08: {scn08.reason}"
    )
    print(
        "SCN-09: FAIL — "
        f"SIP {gate.code or ND} "
        f"{gate.reason or ND}"
    )
    print(
        f"SCN-09: {gate.log_line or ND}"
    )


def main() -> int:
    OUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    sample_ok = False
    report_ok = False

    scn08 = Result("SCN-08")
    scn09 = Result("SCN-09")

    with tempfile.TemporaryDirectory(
        prefix="fluxion_f3_sip_v2_"
    ) as temp_name:
        temp = Path(temp_name)

        try:
            harness = load_harness()

            identity_path = (
                temp
                / "identity.wav"
            )
            carrier_path = (
                temp
                / "carrier.wav"
            )

            harness.generate_wav_from_text(
                "Sono Marco Rossi, cliente nuovo",
                str(identity_path),
            )

            harness.generate_wav_from_text(
                (
                    "Sara registra una nuova richiesta "
                    "domani mattina, verifica il nominativo "
                    "e richiama il cliente"
                ),
                str(carrier_path),
            )

            identity, _, _, _ = (
                harness.read_wav_pcm(
                    str(identity_path)
                )
            )

            carrier, _, _, _ = (
                harness.read_wav_pcm(
                    str(carrier_path)
                )
            )

            profiles = [
                [
                    build_babble(
                        carrier,
                        (
                            935780
                            + profile * 101
                            + index * 17
                        ),
                        profile,
                    )
                    for index in range(3)
                ]
                for profile in (0, 1)
            ]

            sample_temp = (
                temp
                / "f3_sip_v2_sample.wav"
            )

            write_wav(
                sample_temp,
                profiles[0][0],
            )

            shutil.copy2(
                sample_temp,
                SAMPLE_PATH,
            )

            sample_ok = (
                SAMPLE_PATH.is_file()
                and SAMPLE_PATH.stat().st_size > 44
            )

            attempts_08 = []

            try:
                for attempt in (1, 2):
                    result = run_scn08_attempt(
                        harness,
                        attempt,
                        LOCAL_SIP_PORTS[
                            attempt - 1
                        ],
                        identity,
                        profiles[
                            attempt - 1
                        ],
                        temp,
                    )

                    attempts_08.append(
                        result
                    )

                    if result.verdict == PASS:
                        break

                scn08 = choose(
                    attempts_08
                )

            except GateFailure as gate:
                scn08, scn09 = gate_results(
                    "SCN-08",
                    gate,
                )

                atomic_write(
                    REPORT_PATH,
                    report_text(
                        scn08,
                        scn09,
                        sample_ok,
                    ),
                )

                print_gate_verdicts(
                    scn08,
                    scn09,
                    "SCN-08",
                    gate,
                )

                return 1

            attempts_09 = []

            try:
                for attempt in (1, 2):
                    result = run_scn09_attempt(
                        harness,
                        attempt,
                        LOCAL_SIP_PORTS[
                            1 + attempt
                        ],
                        temp,
                    )

                    attempts_09.append(
                        result
                    )

                    if result.verdict == PASS:
                        break

                scn09 = choose(
                    attempts_09
                )

            except GateFailure as gate:
                scn09 = gate_results(
                    "SCN-09",
                    gate,
                )[1]

                atomic_write(
                    REPORT_PATH,
                    report_text(
                        scn08,
                        scn09,
                        sample_ok,
                    ),
                )

                print_gate_verdicts(
                    scn08,
                    scn09,
                    "SCN-09",
                    gate,
                )

                return 1

        except Exception as exc:
            message = (
                "errore runtime: "
                f"{type(exc).__name__}: {exc}"
            )

            if (
                scn08.reason
                == "scenario non eseguito"
            ):
                scn08.reason = message

            if (
                scn09.reason
                == "scenario non eseguito"
            ):
                scn09.reason = message

        try:
            atomic_write(
                REPORT_PATH,
                report_text(
                    scn08,
                    scn09,
                    sample_ok,
                ),
            )
            report_ok = True
        except Exception:
            report_ok = False

    print_verdicts(
        scn08,
        scn09,
    )

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