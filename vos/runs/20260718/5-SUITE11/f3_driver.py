#!/usr/bin/env python3
"""Run FLUXION F3 audio scenarios once against Sara on 127.0.0.1:3003."""

import json
import os
import random
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import wave
from datetime import datetime
from pathlib import Path

BASE = "http://127.0.0.1:3003"
LOG = Path("/tmp/rig_sara3003.log")
OUT = Path(__file__).resolve().parent
REPORT = OUT / "f3_esiti.md"
WAV = OUT / "f3_audio_sample.wav"
PASS, FAIL, ND = "PASS", "FAIL", "ND"

GREP08 = (
    r"strike|stt[_ -]?failure|speech.to.text|STT|VAD|rms|E6|escalat|"
    r"richiamar|collega|goodbye|TTS|BYE"
)
GREP09 = (
    r"reprompt|silence|silenz|timeout|greeting|salut|TTS|ripet|"
    r"non ho sentito|non la sento|mi sente"
)


def post(path, payload, timeout):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            try:
                body = json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                body = {"_raw": raw[:500]}
            return resp.status, body if isinstance(body, dict) else {"_body": body}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            body = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            body = {"_raw": raw[:500]}
        return exc.code, body if isinstance(body, dict) else {"_body": body}
    except Exception as exc:
        return 0, {"_error": f"{type(exc).__name__}: {exc}"}


def session_id(*bodies):
    for body in bodies:
        if not isinstance(body, dict):
            continue
        for source in (body, body.get("data")):
            if not isinstance(source, dict):
                continue
            for key in ("session_id", "sessionId", "session"):
                value = source.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
    return None


def log_offset():
    try:
        return LOG.stat().st_size
    except OSError:
        return 0


def grep_since(offset, pattern):
    """Targeted grep over bytes appended after offset; never load the whole log."""
    if not LOG.is_file():
        return []
    try:
        start = 1 if LOG.stat().st_size < offset else offset + 1
        tail = subprocess.Popen(
            ["tail", "-c", f"+{start}", str(LOG)],
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
            tail.wait(timeout=3)
        except subprocess.TimeoutExpired:
            tail.kill()
            tail.wait(timeout=2)
        if grep.returncode not in (0, 1):
            return []
        return grep.stdout.decode("utf-8", errors="replace").splitlines()
    except Exception:
        return []


def poll(offset, pattern, ready, timeout):
    deadline = time.monotonic() + timeout
    while True:
        lines = grep_since(offset, pattern)
        if ready(lines) or time.monotonic() >= deadline:
            return lines
        time.sleep(0.5)


def make_noise(seed):
    rng = random.Random(seed)
    pcm = bytearray(16000 * 3)  # 1.5 s, mono, int16
    pos = 0
    for _ in range(24000):
        magnitude = rng.randint(3000, 6000)
        sample = -magnitude if rng.getrandbits(1) else magnitude
        struct.pack_into("<h", pcm, pos, sample)
        pos += 2
    return bytes(pcm)


def copy_wav(pcm):
    OUT.mkdir(parents=True, exist_ok=True)
    temp = None
    try:
        with tempfile.NamedTemporaryFile(
            prefix="fluxion_f3_",
            suffix=".wav",
            delete=False,
        ) as fh:
            temp = Path(fh.name)
        with wave.open(str(temp), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(16000)
            wav.writeframes(pcm)
        shutil.copy2(temp, WAV)
        return True
    except Exception:
        return False
    finally:
        if temp is not None:
            try:
                temp.unlink()
            except OSError:
                pass


def timestamp_text(line):
    if not line:
        return ND
    for pattern in (
        r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:[.,]\d{1,6})?",
        r"\d{2}:\d{2}:\d{2}(?:[.,]\d{1,6})?",
    ):
        match = re.search(pattern, line)
        if match:
            return match.group(0)
    return ND


def timestamp_value(line):
    text = timestamp_text(line)
    if text == ND:
        return None
    text = text.replace(",", ".")
    try:
        if re.match(r"^\d{4}-", text):
            return datetime.fromisoformat(
                text.replace(" ", "T", 1)
            ).timestamp()
        whole, dot, frac = text.partition(".")
        parsed = datetime.strptime(whole, "%H:%M:%S")
        fraction = float("0." + frac) if dot else 0.0
        return (
            parsed.hour * 3600
            + parsed.minute * 60
            + parsed.second
            + fraction
        )
    except (ValueError, OverflowError):
        return None


def delta_seconds(start_line, end_line):
    start = timestamp_value(start_line)
    end = timestamp_value(end_line)
    if start is None or end is None:
        return None
    delta = end - start
    return delta + 86400 if delta < -43200 else delta


def index_of(lines, line):
    try:
        return lines.index(line)
    except (ValueError, AttributeError):
        return -1


def find_strike(lines, number):
    patterns = (
        rf"\bstrike(?:s)?\b[^0-9]{{0,32}}{number}\s*(?:/|of)\s*3\b",
        rf"\bstrike(?:s)?\b[^0-9]{{0,32}}(?:=|:)\s*{number}\b",
        rf"\b{number}\s*/\s*3\b.*\bstrike(?:s)?\b",
        rf"\bstrike(?:s)?\s+{number}\b",
        rf"stt[_ -]?failure.*\b{number}\s*/\s*3\b",
    )
    for line in lines:
        if any(
            re.search(pattern, line, re.IGNORECASE)
            for pattern in patterns
        ):
            return line
    return None


def find_e6(lines, after):
    candidates = lines[after + 1 :] if after >= 0 else lines
    for line in candidates:
        low = line.lower()
        if "e6" in low and re.search(
            r"trigger|scatt|threshold|escalat|attiv|goodbye",
            low,
        ):
            return line
    return next(
        (line for line in candidates if "e6" in line.lower()),
        None,
    )


def is_tts_end(line):
    low = line.lower()
    return "tts" in low and bool(
        re.search(
            r"\bend\b|\bdone\b|complet|finish|terminat|fine[-_ ]?tts|"
            r"playback.*(?:end|done|complet)|"
            r"audio.*(?:end|done|complet)",
            low,
        )
    )


def find_reprompt(lines, after=-1):
    configured = re.compile(
        r"arm(?:ed|ing)?|schedul|config|set for|timer started|"
        r"starting timer|cancel",
        re.IGNORECASE,
    )
    activated = re.compile(
        r"fir(?:e|ed|ing)|trigger|expir|elapsed|inactiv|"
        r"silence.*(?:22|timeout)|"
        r"timeout.*(?:reach|elapsed|expir)|send|synth|play|tts",
        re.IGNORECASE,
    )
    candidates = lines[after + 1 :] if after >= 0 else lines
    for line in candidates:
        low = line.lower()
        if (
            "reprompt" in low
            and activated.search(low)
            and not configured.search(low)
        ):
            return line
    for line in candidates:
        low = line.lower()
        if "tts" in low and re.search(
            r"ripet|non ho sentito|non la sento|mi sente",
            low,
        ):
            return line
    return None


def diagnostics(lines, limit=18):
    out = []
    for line in lines:
        if re.search(
            r"\bVAD\b|\bSTT\b|stt[_ -]?failure|rms|speech|audio",
            line,
            re.IGNORECASE,
        ):
            if line not in out:
                out.append(line)
            if len(out) >= limit:
                break
    return out


def ordered_evidence(lines, selected, extra=()):
    wanted = {
        line
        for line in (*selected, *extra)
        if line
    }
    return [line for line in lines if line in wanted]


def blank_result(scenario, reason):
    return {
        "scenario": scenario,
        "verdict": FAIL,
        "reason": reason,
        "http": [],
        "timestamps": {},
        "metrics": {},
        "evidence": [],
    }


def run_scn08():
    result = blank_result("SCN-08", "scenario non completato")
    offset = log_offset()
    http = []

    reset_status, reset_body = post("/api/voice/reset", {}, 10)
    http.append(("reset", reset_status))
    sid = session_id(reset_body)

    payload = {"text": "Sono Marco Rossi, cliente nuovo"}
    if sid:
        payload["session_id"] = sid
    text_status, text_body = post(
        "/api/voice/process",
        payload,
        30,
    )
    http.append(("text", text_status))
    sid = session_id(text_body, reset_body)

    noises = [
        make_noise(515126),
        make_noise(515127),
        make_noise(515128),
    ]
    for number, pcm in enumerate(noises, 1):
        payload = {"audio_hex": pcm.hex()}
        if sid:
            payload["session_id"] = sid
        status, _ = post(
            "/api/voice/process-with-vad",
            payload,
            35,
        )
        http.append((f"audio_{number}", status))

    lines = poll(
        offset,
        GREP08,
        lambda current: any(
            re.search(r"\bBYE\b", line, re.IGNORECASE)
            for line in current
        ),
        15.0,
    )

    strikes = [
        find_strike(lines, number)
        for number in (1, 2, 3)
    ]
    strike_idx = [
        index_of(lines, line)
        for line in strikes
    ]
    strikes_ok = (
        all(index >= 0 for index in strike_idx)
        and strike_idx[0] < strike_idx[1] < strike_idx[2]
    )

    e6 = find_e6(
        lines,
        strike_idx[2] if strike_idx[2] >= 0 else -1,
    )
    e6_idx = index_of(lines, e6)

    goodbye = next(
        (
            line
            for line in lines[e6_idx if e6_idx >= 0 else 0 :]
            if (
                "richiamar" in line.lower()
                or "collega" in line.lower()
            )
        ),
        None,
    )
    goodbye_idx = index_of(lines, goodbye)
    goodbye_low = goodbye.lower() if goodbye else ""
    honest = (
        "richiamar" in goodbye_low
        and "collega" not in goodbye_low
    )

    bye = next(
        (
            line
            for line in lines[
                goodbye_idx + 1 if goodbye_idx >= 0 else 0 :
            ]
            if re.search(r"\bBYE\b", line, re.IGNORECASE)
        ),
        None,
    )
    bye_idx = index_of(lines, bye)

    tts_end = None
    start = goodbye_idx if goodbye_idx >= 0 else max(e6_idx, 0)
    stop = bye_idx if bye_idx >= 0 else len(lines)
    for line in lines[start:stop]:
        if is_tts_end(line):
            tts_end = line
    if tts_end is None and goodbye and is_tts_end(goodbye):
        tts_end = goodbye

    bye_delta = delta_seconds(tts_end, bye)
    bye_ok = (
        bye_delta is not None
        and 0.0 <= bye_delta <= 2.0
    )
    http_ok = all(
        status == 200
        for _, status in http
    )
    e6_ok = e6 is not None

    selected = [
        *strikes,
        e6,
        goodbye,
        tts_end,
        bye,
    ]
    evidence = ordered_evidence(lines, selected)
    if not (
        strikes_ok
        and e6_ok
        and honest
        and bye_ok
    ):
        evidence = ordered_evidence(
            lines,
            selected,
            diagnostics(lines),
        )

    result.update(
        http=http,
        timestamps={
            "strike_1": timestamp_text(strikes[0]),
            "strike_2": timestamp_text(strikes[1]),
            "strike_3": timestamp_text(strikes[2]),
            "e6": timestamp_text(e6),
            "goodbye_text": timestamp_text(goodbye),
            "goodbye_end": timestamp_text(tts_end),
            "bye": timestamp_text(bye),
        },
        metrics={
            "honest": honest,
            "bye_delta": bye_delta,
        },
        evidence=evidence,
    )

    failed = []
    if not http_ok:
        failed.append("HTTP")
    if not strikes_ok:
        failed.append("strike 1→2→3")
    if not e6_ok:
        failed.append("E6")
    if not honest:
        failed.append("congedo richiamar/no-collega")
    if not bye_ok:
        failed.append("BYE≤2s")

    if not failed:
        result["verdict"] = PASS
        result["reason"] = (
            "strike 1→2→3, E6, congedo onesto "
            "e BYE entro 2s"
        )
    else:
        result["reason"] = (
            "criteri non maturati: "
            + ", ".join(failed)
        )

    return result, noises[0]


def run_scn09():
    result = blank_result("SCN-09", "scenario non completato")
    offset = log_offset()
    http = []

    reset_status, reset_body = post("/api/voice/reset", {}, 10)
    http.append(("reset", reset_status))
    sid = session_id(reset_body)

    payload = {"text": "Buongiorno"}
    if sid:
        payload["session_id"] = sid
    greeting_status, _ = post(
        "/api/voice/process",
        payload,
        30,
    )
    http.append(("greeting", greeting_status))

    time.sleep(30.0)
    lines = grep_since(offset, GREP09)

    greeting_end = next(
        (line for line in lines if is_tts_end(line)),
        None,
    )
    greeting_end_idx = index_of(lines, greeting_end)
    reprompt = find_reprompt(lines, greeting_end_idx)

    reprompt_delta = delta_seconds(
        greeting_end,
        reprompt,
    )
    timing_ok = (
        reprompt_delta is not None
        and 0.0 <= reprompt_delta <= 25.0
    )
    http_ok = all(
        status == 200
        for _, status in http
    )
    reprompt_ok = reprompt is not None

    selected = [greeting_end, reprompt]
    extra = []
    if not (reprompt_ok and timing_ok):
        extra.extend(diagnostics(lines))
        extra.extend(
            line
            for line in lines
            if re.search(
                r"reprompt|silence|silenz|timeout",
                line,
                re.IGNORECASE,
            )
        )
    evidence = ordered_evidence(
        lines,
        selected,
        extra[:22],
    )

    result.update(
        http=http,
        timestamps={
            "greeting_end": timestamp_text(greeting_end),
            "reprompt_start": timestamp_text(reprompt),
        },
        metrics={
            "reprompt_delta": reprompt_delta,
        },
        evidence=evidence,
    )

    failed = []
    if not http_ok:
        failed.append("HTTP")
    if not reprompt_ok:
        failed.append("reprompt assente")
    if not timing_ok:
        failed.append("timestamp/delta >25s")

    if not failed:
        result["verdict"] = PASS
        result["reason"] = (
            "reprompt presente entro 25s "
            "dalla fine del greeting-TTS"
        )
    else:
        result["reason"] = (
            "criteri non maturati: "
            + ", ".join(failed)
        )

    return result


def fmt_http(events):
    if not events:
        return ND
    return " · ".join(
        f"{name}=HTTP {status if status else ND}"
        for name, status in events
    )


def fmt_delta(value):
    return f"{value:.3f}s" if value is not None else ND


def evidence_block(lines):
    if not lines:
        return ND
    return (
        "```text\n"
        + "\n".join(lines)
        + "\n```"
    )


def build_report(scn08, scn09, wav_ok):
    t8 = scn08["timestamps"]
    m8 = scn08["metrics"]
    t9 = scn09["timestamps"]
    m9 = scn09["metrics"]

    return "\n".join(
        [
            "## Esiti F3",
            "",
            (
                "**Data:** "
                + datetime.now()
                .astimezone()
                .isoformat(timespec="seconds")
            ),
            f"**Rig:** {BASE}",
            (
                f"**WAV campione:** `{WAV}`"
                if wav_ok
                else "**WAV campione:** ND"
            ),
            "",
            "### SCN-08 — E6 sul path AUDIO",
            f"**Verdetto:** {scn08['verdict']}",
            f"**Motivo:** {scn08['reason']}",
            f"**HTTP:** {fmt_http(scn08['http'])}",
            (
                "**Strike 1 timestamp:** "
                + t8.get("strike_1", ND)
            ),
            (
                "**Strike 2 timestamp:** "
                + t8.get("strike_2", ND)
            ),
            (
                "**Strike 3 timestamp:** "
                + t8.get("strike_3", ND)
            ),
            f"**E6 timestamp:** {t8.get('e6', ND)}",
            (
                "**Goodbye-TTS testo timestamp:** "
                + t8.get("goodbye_text", ND)
            ),
            (
                "**Goodbye-TTS fine timestamp:** "
                + t8.get("goodbye_end", ND)
            ),
            f"**BYE timestamp:** {t8.get('bye', ND)}",
            (
                "**BYE dalla fine goodbye-TTS:** "
                + fmt_delta(m8.get("bye_delta"))
            ),
            (
                "**Congedo contiene «richiamar» "
                "e non «collega»:** "
                + ("SÌ" if m8.get("honest") else "NO")
            ),
            "**Evidenza log VERBATIM:**",
            evidence_block(scn08["evidence"]),
            "",
            "### SCN-09 — silenzio → reprompt",
            f"**Verdetto:** {scn09['verdict']}",
            f"**Motivo:** {scn09['reason']}",
            f"**HTTP:** {fmt_http(scn09['http'])}",
            (
                "**Fine greeting-TTS timestamp:** "
                + t9.get("greeting_end", ND)
            ),
            (
                "**Inizio reprompt timestamp:** "
                + t9.get("reprompt_start", ND)
            ),
            (
                "**Delta reprompt:** "
                + fmt_delta(m9.get("reprompt_delta"))
            ),
            "**Evidenza log VERBATIM:**",
            evidence_block(scn09["evidence"]),
            "",
        ]
    )


def atomic_write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(
        f".{path.name}.{os.getpid()}.tmp"
    )
    try:
        temp.write_text(text, encoding="utf-8")
        os.replace(temp, path)
    finally:
        try:
            temp.unlink()
        except OSError:
            pass


def main():
    try:
        scn08, sample = run_scn08()
    except Exception as exc:
        scn08 = blank_result(
            "SCN-08",
            f"eccezione: {type(exc).__name__}: {exc}",
        )
        sample = make_noise(515126)

    try:
        scn09 = run_scn09()
    except Exception as exc:
        scn09 = blank_result(
            "SCN-09",
            f"eccezione: {type(exc).__name__}: {exc}",
        )

    wav_ok = copy_wav(sample)
    report_ok = True
    try:
        atomic_write(
            REPORT,
            build_report(scn08, scn09, wav_ok),
        )
    except Exception:
        report_ok = False

    print(f"SCN-08: {scn08['verdict']}")
    print(f"SCN-09: {scn09['verdict']}")

    return (
        0
        if (
            scn08["verdict"] == PASS
            and scn09["verdict"] == PASS
            and wav_ok
            and report_ok
        )
        else 1
    )


if __name__ == "__main__":
    sys.exit(main())
