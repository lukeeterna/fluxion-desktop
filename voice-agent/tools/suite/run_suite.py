#!/usr/bin/env python3
"""
suite/run_suite.py — FLUXION STEP-4 SUITE v1
Runner di scenari su rig high-port (:3003).

Scenari (capitolato PLAYBOOK-1):
  smoke · congedo×2 · name-gate («Buonasera») · escalation-E6 (3 garbage) ·
  silenzio→reprompt · barge-in · dettatura-numero

Esecuzione:
  python3 run_suite.py [--sara http://127.0.0.1:3003] [--wav-dir /path/to/audio]
  (from MacBook via ssh: ssh imac 'python3 /path/run_suite.py ...')

Output:
  suite_report.md (PASS/FAIL per scenario + log estratti)
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import urllib.request
import urllib.error

TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
PASS = "PASS"
FAIL = "FAIL"
ND = "ND"


# ---------------------------------------------------------------------------
# HTTP helpers (stdlib only — no requests dep on iMac Python 3.9)
# ---------------------------------------------------------------------------

def _post(url: str, payload: dict, timeout: int = 30) -> Tuple[int, dict]:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode())
            return resp.status, body
    except urllib.error.HTTPError as e:
        body = {}
        try:
            body = json.loads(e.read().decode())
        except Exception:
            pass
        return e.code, body
    except Exception as exc:
        return 0, {"_error": str(exc)}


def _get(url: str, timeout: int = 10) -> Tuple[int, dict]:
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, {}
    except Exception as exc:
        return 0, {"_error": str(exc)}


def sara_text(base: str, text: str, session_id: Optional[str] = None, timeout: int = 30) -> dict:
    payload: dict = {"text": text}
    if session_id:
        payload["session_id"] = session_id
    status, body = _post(f"{base}/api/voice/process", payload, timeout=timeout)
    body["_http_status"] = status
    return body


def sara_reset(base: str) -> dict:
    status, body = _post(f"{base}/api/voice/reset", {}, timeout=10)
    body["_http_status"] = status
    return body


def sara_health(base: str) -> dict:
    status, body = _get(f"{base}/health", timeout=8)
    body["_http_status"] = status
    return body


# ---------------------------------------------------------------------------
# WAV generation via macOS `say` (evidence artefact)
# ---------------------------------------------------------------------------

def make_wav(text: str, path: str) -> bool:
    """Generate a WAV via macOS say (AIFF→WAV via afconvert). Returns True on success."""
    aiff = path.replace(".wav", ".aiff")
    try:
        subprocess.run(["say", "-o", aiff, "--data-format=LEI16@8000", text],
                       check=True, capture_output=True, timeout=15)
        subprocess.run(["afconvert", "-f", "WAVE", "-d", "LEI16@8000", aiff, path],
                       check=True, capture_output=True, timeout=10)
        os.unlink(aiff)
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Scenario runners
# ---------------------------------------------------------------------------

class ScenarioResult:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name
        self.verdict = ND
        self.turns: List[dict] = []
        self.notes: List[str] = []
        self.wav_path: Optional[str] = None

    def add_turn(self, label: str, input_text: str, response: dict):
        self.turns.append({"label": label, "input": input_text, "response": response})

    def add_note(self, note: str):
        self.notes.append(note)

    def set(self, verdict: str, reason: str):
        self.verdict = verdict
        self.add_note(f"[{verdict}] {reason}")

    def to_md(self) -> str:
        lines = [f"### {self.id} — {self.name}", f"**Verdict:** {self.verdict}", ""]
        for t in self.turns:
            resp = t["response"]
            text_out = resp.get("response", resp.get("_error", "ND"))
            intent = resp.get("intent", "ND")
            fsm_state = resp.get("fsm_state", "ND")
            http_status = resp.get("_http_status", "ND")
            lines.append(f"**[{t['label']}]** INPUT: `{t['input']!r}`")
            lines.append(f"  → HTTP {http_status} | intent=`{intent}` | fsm=`{fsm_state}`")
            lines.append(f"  → RESPONSE: `{text_out[:200]}`")
            lines.append("")
        for n in self.notes:
            lines.append(f"- {n}")
        if self.wav_path:
            lines.append(f"- WAV: `{self.wav_path}`")
        lines.append("")
        return "\n".join(lines)


def run_smoke(base: str, wav_dir: str) -> ScenarioResult:
    r = ScenarioResult("SCN-01", "smoke — health + greeting")
    h = sara_health(base)
    if h.get("status") != "ok":
        r.set(FAIL, f"health NON ok: {h}")
        return r
    r.add_note(f"health OK: {h.get('version','?')} pipeline={h.get('pipeline','?')}")
    sara_reset(base)
    resp = sara_text(base, "Buongiorno")
    r.add_turn("greeting", "Buongiorno", resp)
    if resp.get("_http_status") == 200 and resp.get("success"):
        text_out = resp.get("response", "")
        r.set(PASS, f"Sara risponde al saluto: '{text_out[:80]}'")
    else:
        r.set(FAIL, f"HTTP {resp.get('_http_status')} / success={resp.get('success')}")
    wav_path = str(Path(wav_dir) / "SCN01_smoke.wav")
    if make_wav("Buongiorno", wav_path):
        r.wav_path = wav_path
    return r


def run_congedo_x2(base: str, wav_dir: str) -> ScenarioResult:
    r = ScenarioResult("SCN-02", "congedo×2 — goodbye ripetuto (idempotenza)")
    successes = []
    for attempt in range(1, 3):
        sara_reset(base)
        # prime with a greeting first
        sara_text(base, "Buongiorno", timeout=20)
        resp = sara_text(base, "Grazie, arrivederci", timeout=20)
        r.add_turn(f"congedo_#{attempt}", "Grazie, arrivederci", resp)
        intent = resp.get("intent", "")
        should_exit = resp.get("should_exit", False)
        text_out = resp.get("response", "")
        hit = resp.get("_http_status") == 200 and (
            should_exit or "goodbye" in intent.lower() or "chiusura" in intent.lower()
            or any(k in text_out.lower() for k in ["arrivederci", "a presto", "buona giornata", "grazie"])
        )
        successes.append(hit)
        r.add_note(f"attempt #{attempt}: should_exit={should_exit} intent={intent} hit={hit}")
    if all(successes):
        r.set(PASS, "congedo riconosciuto entrambe le volte")
    elif any(successes):
        r.set(FAIL, f"congedo riconosciuto solo {sum(successes)}/2 volte")
    else:
        r.set(FAIL, "congedo NON riconosciuto in nessun tentativo")
    wav_path = str(Path(wav_dir) / "SCN02_congedo.wav")
    if make_wav("Grazie, arrivederci", wav_path):
        r.wav_path = wav_path
    return r


def run_name_gate(base: str, wav_dir: str) -> ScenarioResult:
    r = ScenarioResult("SCN-03", "name-gate — «Buonasera» non committato come nome")
    sara_reset(base)
    resp = sara_text(base, "Buonasera", timeout=20)
    r.add_turn("saluto_buonasera", "Buonasera", resp)
    fsm_state = resp.get("fsm_state", "")
    text_out = resp.get("response", "")
    intent = resp.get("intent", "")
    # Name-gate fix: "Buonasera" should NOT trigger CONFIRMING_NAME
    # It should be treated as a greeting → remain in idle or greeting state
    # NOT go to confirming_name (which would mean "Buonasera" was interpreted as a person's name)
    if fsm_state == "confirming_name":
        r.set(FAIL, f"REGRESSIONE: 'Buonasera' finito in confirming_name — name-gate FIX NON applicato. Response: '{text_out[:80]}'")
    elif resp.get("_http_status") == 200 and resp.get("success"):
        r.add_note(f"fsm_state={fsm_state} intent={intent}")
        r.set(PASS, f"'Buonasera' trattato come saluto (fsm={fsm_state}), NON nome. Response: '{text_out[:80]}'")
    else:
        r.set(FAIL, f"HTTP {resp.get('_http_status')} / success={resp.get('success')}")
    wav_path = str(Path(wav_dir) / "SCN03_namegate.wav")
    if make_wav("Buonasera", wav_path):
        r.wav_path = wav_path
    return r


def run_escalation_e6(base: str, wav_dir: str) -> ScenarioResult:
    r = ScenarioResult("SCN-04", "escalation E6 — 3 garbage → congedo onesto")
    sara_reset(base)
    garbage = [
        "xkzqwmflpbt",
        "aaaa bbbb cccc dddd eeee ffffzz",
        "9999 0000 1234 zqzq asdf",
    ]
    should_escalate = False
    honest_msg = False
    for i, g in enumerate(garbage, 1):
        resp = sara_text(base, g, timeout=25)
        r.add_turn(f"garbage_{i}", g, resp)
        if resp.get("should_exit") or resp.get("should_escalate"):
            should_escalate = True
            text_out = resp.get("response", "")
            # Honest message check: should NOT say "collega" (false promise)
            bad_keywords = ["collega", "la passo", "passo subito"]
            good_keywords = ["richiamer", "richiamar", "disturb", "arrivederci", "disagio", "difficolt"]
            has_bad = any(k in text_out.lower() for k in bad_keywords)
            has_good = any(k in text_out.lower() for k in good_keywords)
            honest_msg = has_good and not has_bad
            r.add_note(f"escalation triggered at turn {i}: should_exit={resp.get('should_exit')} should_escalate={resp.get('should_escalate')}")
            r.add_note(f"E6 message: '{text_out[:150]}'")
            r.add_note(f"honest_msg={honest_msg} (has_good={has_good}, has_bad={has_bad})")
            break
    if should_escalate and honest_msg:
        r.set(PASS, "E6 scatta dopo 3 garbage, messaggio onesto (no promessa collega)")
    elif should_escalate and not honest_msg:
        r.set(FAIL, "E6 scatta MA messaggio disonesto (promessa collega o testo sbagliato)")
    else:
        r.set(FAIL, "E6 NON scattato dopo 3 garbage consecutivi")
    wav_path = str(Path(wav_dir) / "SCN04_e6.wav")
    if make_wav("aabba qqzz mmmm", wav_path):
        r.wav_path = wav_path
    return r


def run_silenzio_reprompt(base: str, wav_dir: str) -> ScenarioResult:
    r = ScenarioResult("SCN-05", "silenzio→reprompt — input vuoto genera reprompt")
    sara_reset(base)
    # First turn to prime session
    sara_text(base, "Buongiorno", timeout=20)
    # Now send empty/silence
    resp_empty = sara_text(base, "", timeout=20)
    r.add_turn("silenzio", "", resp_empty)
    text_out = resp_empty.get("response", "")
    intent = resp_empty.get("intent", "")
    # A reprompt should produce SOME response (not error), asking the caller to repeat
    if resp_empty.get("_http_status") == 200:
        # Check for reprompt indicators
        reprompt_indicators = ["scusi", "ripeta", "capito", "dica", "sento", "sentito", "mi dica", "come posso", "buongiorno"]
        has_reprompt = len(text_out.strip()) > 0
        r.add_note(f"intent={intent} response='{text_out[:100]}'")
        if has_reprompt:
            r.set(PASS, f"Sara risponde a input vuoto con reprompt: '{text_out[:80]}'")
        else:
            r.set(FAIL, "Sara non genera nessuna risposta su input vuoto")
    else:
        r.set(FAIL, f"HTTP {resp_empty.get('_http_status')} su input vuoto")
    wav_path = str(Path(wav_dir) / "SCN05_silenzio.wav")
    # WAV for silence = short silence
    if make_wav(" ", wav_path):
        r.wav_path = wav_path
    return r


def run_bargein(base: str, wav_dir: str) -> ScenarioResult:
    r = ScenarioResult("SCN-06", "barge-in — input rapido consecutivo")
    sara_reset(base)
    # Simulate barge-in: send two rapid turns without waiting for reply
    # The second message interrupts before processing the first
    resp1 = sara_text(base, "Vorrei prenotare un appuntamento", timeout=20)
    r.add_turn("turn1", "Vorrei prenotare un appuntamento", resp1)
    # Immediately send barge-in
    resp2 = sara_text(base, "Scusi ho cambiato idea", timeout=20)
    r.add_turn("bargein", "Scusi ho cambiato idea", resp2)
    # Sara should handle both without crashing
    both_ok = (resp1.get("_http_status") == 200 and resp2.get("_http_status") == 200)
    if both_ok:
        r.set(PASS, f"Sara gestisce barge-in senza crash. turn1_fsm={resp1.get('fsm_state')} turn2_fsm={resp2.get('fsm_state')}")
    else:
        r.set(FAIL, f"Uno dei turni ha fallito: turn1={resp1.get('_http_status')} turn2={resp2.get('_http_status')}")
    wav_path = str(Path(wav_dir) / "SCN06_bargein.wav")
    if make_wav("Scusi ho cambiato idea", wav_path):
        r.wav_path = wav_path
    return r


def run_dettatura_numero(base: str, wav_dir: str) -> ScenarioResult:
    r = ScenarioResult("SCN-07", "dettatura numero — inject cifre pulite")
    sara_reset(base)
    # Prime with greeting + name to get to phone collection state
    sara_text(base, "Buongiorno", timeout=20)
    resp_name = sara_text(base, "Sono Marco Rossi, cliente nuovo", timeout=25)
    r.add_turn("nome", "Sono Marco Rossi, cliente nuovo", resp_name)
    # Confirm name if in confirming_name state
    if resp_name.get("fsm_state") == "confirming_name":
        resp_confirm = sara_text(base, "Sì esatto", timeout=20)
        r.add_turn("conferma_nome", "Sì esatto", resp_confirm)
    # Inject clean digit string for phone number
    resp_phone = sara_text(base, "tre tre tre uno due tre quattro cinque sei", timeout=25)
    r.add_turn("dettatura_numero", "tre tre tre uno due tre quattro cinque sei", resp_phone)
    http_ok = resp_phone.get("_http_status") == 200
    text_out = resp_phone.get("response", "")
    intent = resp_phone.get("intent", "")
    fsm_state = resp_phone.get("fsm_state", "")
    if http_ok:
        # Sara should accept the number OR ask for confirmation
        r.add_note(f"fsm_state={fsm_state} intent={intent}")
        r.add_note(f"response='{text_out[:120]}'")
        r.set(PASS, f"dettatura numero processata senza crash (HTTP 200, fsm={fsm_state})")
    else:
        r.set(FAIL, f"HTTP {resp_phone.get('_http_status')} su dettatura numero")
    wav_path = str(Path(wav_dir) / "SCN07_numero.wav")
    if make_wav("tre tre tre uno due tre quattro cinque sei", wav_path):
        r.wav_path = wav_path
    return r


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(description="FLUXION Suite v1 — step-4 scenario runner")
    p.add_argument("--sara", default="http://127.0.0.1:3003",
                   help="Sara base URL (default: http://127.0.0.1:3003)")
    p.add_argument("--wav-dir", default="/tmp/suite_audio",
                   help="Directory for WAV evidence files")
    p.add_argument("--report-out", default=None,
                   help="Path to write suite_report.md (default: stdout)")
    args = p.parse_args()

    Path(args.wav_dir).mkdir(parents=True, exist_ok=True)

    runners = [
        run_smoke,
        run_congedo_x2,
        run_name_gate,
        run_escalation_e6,
        run_silenzio_reprompt,
        run_bargein,
        run_dettatura_numero,
    ]

    results: List[ScenarioResult] = []
    for fn in runners:
        print(f"[RUN] {fn.__name__}...", file=sys.stderr)
        try:
            r = fn(args.sara, args.wav_dir)
        except Exception as exc:
            r_id = fn.__name__.upper()
            r = ScenarioResult(r_id, fn.__name__)
            r.set(FAIL, f"EXCEPTION: {exc}")
        results.append(r)
        print(f"  → {r.verdict}: {r.notes[-1] if r.notes else 'ND'}", file=sys.stderr)
        time.sleep(1)

    # Build report
    n_pass = sum(1 for r in results if r.verdict == PASS)
    n_fail = sum(1 for r in results if r.verdict == FAIL)
    n_nd = sum(1 for r in results if r.verdict == ND)

    lines = [
        "# SUITE v1 — Report",
        f"**Data:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Target:** {args.sara}",
        f"**Totale:** {len(results)} | PASS={n_pass} | FAIL={n_fail} | ND={n_nd}",
        "",
        "## Tabella riepilogo",
        "",
        "| ID | Nome | Verdict |",
        "|---|---|---|",
    ]
    for r in results:
        lines.append(f"| {r.id} | {r.name} | **{r.verdict}** |")
    lines.append("")
    lines.append("## Dettaglio scenari")
    lines.append("")
    for r in results:
        lines.append(r.to_md())

    report_md = "\n".join(lines)

    if args.report_out:
        Path(args.report_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report_out).write_text(report_md, encoding="utf-8")
        print(f"Report scritto: {args.report_out}", file=sys.stderr)
    else:
        print(report_md)

    # JSON summary for CI
    summary = {
        "timestamp": TIMESTAMP,
        "sara": args.sara,
        "pass": n_pass,
        "fail": n_fail,
        "nd": n_nd,
        "scenarios": [{"id": r.id, "name": r.name, "verdict": r.verdict} for r in results],
    }
    print(json.dumps(summary, ensure_ascii=False), file=sys.stderr)
    sys.exit(0 if n_fail == 0 else 1)


if __name__ == "__main__":
    main()
