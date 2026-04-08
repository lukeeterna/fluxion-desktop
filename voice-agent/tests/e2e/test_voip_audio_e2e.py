"""
VoIP Audio E2E Test — S135
==========================
Tests the FULL voice pipeline (STT → NLU → FSM → TTS) using Edge-TTS
generated Italian audio sent via audio_hex to /api/voice/process.

Equivalent to a live VoIP call but fully autonomous.
Covers: STT accuracy on compressed audio, disambiguation, NameCorrector,
multi-service handling, NLU timeout resilience.

Usage:
    python -m pytest tests/e2e/test_voip_audio_e2e.py -v --tb=short
    # Or standalone:
    python tests/e2e/test_voip_audio_e2e.py
"""

import asyncio
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request
from typing import Dict, Optional, Tuple

# Pipeline endpoint (iMac local)
PIPELINE_URL = os.environ.get("PIPELINE_URL", "http://127.0.0.1:3002")

# Edge-TTS voice (male Italian — simulates caller)
CALLER_VOICE = "it-IT-DiegoNeural"


def generate_audio(text: str, output_path: str) -> bool:
    """Generate Italian WAV audio using Edge-TTS."""
    try:
        result = subprocess.run(
            ["edge-tts", "--voice", CALLER_VOICE, "--text", text, "--write-media", output_path],
            capture_output=True, text=True, timeout=15
        )
        return result.returncode == 0 and os.path.exists(output_path)
    except Exception as e:
        print(f"  [TTS-GEN] Failed: {e}")
        return False


def send_audio(wav_path: str, session_id: Optional[str] = None) -> Dict:
    """Send WAV file as audio_hex to pipeline."""
    with open(wav_path, "rb") as f:
        audio_hex = f.read().hex()

    payload = {"audio_hex": audio_hex}
    if session_id:
        payload["session_id"] = session_id

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{PIPELINE_URL}/api/voice/process",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    resp = urllib.request.urlopen(req, timeout=30)
    return json.loads(resp.read())


def send_text(text: str, session_id: Optional[str] = None) -> Dict:
    """Send text input to pipeline (for comparison/setup)."""
    payload = {"text": text}
    if session_id:
        payload["session_id"] = session_id

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{PIPELINE_URL}/api/voice/process",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    resp = urllib.request.urlopen(req, timeout=30)
    return json.loads(resp.read())


def reset_session() -> Dict:
    """Reset conversation state."""
    req = urllib.request.Request(
        f"{PIPELINE_URL}/api/voice/reset",
        data=b"{}",
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    resp = urllib.request.urlopen(req, timeout=10)
    return json.loads(resp.read())


def set_vertical(vertical: str) -> Dict:
    """Set business vertical."""
    data = json.dumps({"vertical": vertical}).encode("utf-8")
    req = urllib.request.Request(
        f"{PIPELINE_URL}/api/voice/set-vertical",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    resp = urllib.request.urlopen(req, timeout=10)
    return json.loads(resp.read())


def check_health() -> bool:
    """Check pipeline health."""
    try:
        req = urllib.request.Request(f"{PIPELINE_URL}/health")
        resp = urllib.request.urlopen(req, timeout=5)
        data = json.loads(resp.read())
        return data.get("status") == "ok"
    except Exception:
        return False


# ============================================================================
# TEST SCENARIOS
# ============================================================================

class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0
        self.results = []

    def ok(self, tag: str, scenario: str, detail: str):
        self.passed += 1
        msg = f"OK   [{tag}] {scenario}: {detail}"
        self.results.append(msg)
        print(msg)

    def fail(self, tag: str, scenario: str, detail: str):
        self.failed += 1
        msg = f"FAIL [{tag}] {scenario}: {detail}"
        self.results.append(msg)
        print(msg)

    def warn(self, tag: str, scenario: str, detail: str):
        self.warnings += 1
        msg = f"WARN [{tag}] {scenario}: {detail}"
        self.results.append(msg)
        print(msg)

    def summary(self):
        total = self.passed + self.failed + self.warnings
        print(f"\n{'='*60}")
        print(f"RESULTS: {self.passed} OK / {self.warnings} WARN / {self.failed} FAIL (total {total})")
        print(f"{'='*60}")
        return self.failed == 0


def run_tests():
    """Run all VoIP-equivalent E2E tests."""
    tr = TestResult()
    tmpdir = tempfile.mkdtemp(prefix="fluxion_voip_test_")
    print(f"\n{'='*60}")
    print(f"FLUXION VoIP Audio E2E Test — S135")
    print(f"Pipeline: {PIPELINE_URL}")
    print(f"Temp dir: {tmpdir}")
    print(f"{'='*60}\n")

    # Pre-check
    if not check_health():
        print("FATAL: Pipeline not reachable")
        return False

    # ── TEST 1: STT accuracy on synthetic Italian ──
    print("\n--- Test 1: STT Accuracy (Edge-TTS → Groq Whisper) ---")
    reset_session()
    wav1 = os.path.join(tmpdir, "t1_greeting.wav")
    if generate_audio("Buongiorno, sono Marco Rossi e vorrei prenotare", wav1):
        t0 = time.time()
        r = send_audio(wav1)
        elapsed = (time.time() - t0) * 1000
        trans = r.get("transcription", "").lower()
        if r.get("success"):
            if "marco" in trans and "rossi" in trans:
                tr.ok("STT", "Name transcription", f"'{trans}' ({elapsed:.0f}ms)")
            elif "marco" in trans or "rossi" in trans:
                tr.warn("STT", "Partial name", f"'{trans}' ({elapsed:.0f}ms)")
            else:
                tr.fail("STT", "Name not detected", f"'{trans}' ({elapsed:.0f}ms)")
        else:
            tr.fail("STT", "API error", str(r.get("error", "unknown")))
    else:
        tr.fail("STT", "Audio generation", "Edge-TTS failed")

    # ── TEST 2: Bare-word disambiguation "taglio" ──
    print("\n--- Test 2: Taglio Disambiguation (S125) ---")
    reset_session()
    set_vertical("salone")
    wav2 = os.path.join(tmpdir, "t2_taglio.wav")
    if generate_audio("Vorrei un taglio", wav2):
        r = send_audio(wav2)
        resp = r.get("response", "").lower()
        fsm = r.get("fsm_state", "")
        if "opzioni" in resp or "quale" in resp or "preferisce" in resp:
            tr.ok("DISAMB", "Bare-word taglio", f"Sara asks disambiguation → '{resp[:80]}'")
        elif fsm == "waiting_service":
            tr.warn("DISAMB", "Taglio — waiting but no question", f"'{resp[:80]}'")
        else:
            tr.fail("DISAMB", "No disambiguation", f"fsm={fsm}, resp='{resp[:80]}'")
    else:
        tr.fail("DISAMB", "Audio generation", "Edge-TTS failed")

    # ── TEST 3: Multi-service max 3 (S135) ──
    print("\n--- Test 3: Multi-Service Limit (S135) ---")
    reset_session()
    set_vertical("salone")
    wav3 = os.path.join(tmpdir, "t3_multi.wav")
    if generate_audio("Vorrei taglio barba e colore", wav3):
        r = send_audio(wav3)
        resp = r.get("response", "").lower()
        fsm = r.get("fsm_state", "")
        # Should NOT list 6 variants
        all_variants = ["taglio donna", "taglio uomo", "taglio bambino"]
        listed_count = sum(1 for v in all_variants if v in resp)
        if listed_count >= 3:
            tr.fail("MULTI", "Lists all taglio variants", f"Found {listed_count} variants in '{resp[:100]}'")
        elif fsm in ("waiting_name", "waiting_date"):
            tr.ok("MULTI", "Services accepted cleanly", f"fsm={fsm}, resp='{resp[:80]}'")
        elif "quale" in resp or "tipo" in resp:
            tr.ok("MULTI", "Asks taglio type (mixed disamb)", f"resp='{resp[:80]}'")
        else:
            tr.warn("MULTI", "Unexpected state", f"fsm={fsm}, resp='{resp[:80]}'")
    else:
        tr.fail("MULTI", "Audio generation", "Edge-TTS failed")

    # ── TEST 4: Full booking flow via audio ──
    print("\n--- Test 4: Full Booking Flow (Audio) ---")
    reset_session()
    set_vertical("salone")
    steps = [
        ("Vorrei prenotare un taglio uomo", "waiting_name", ["nome", "cortesia"]),
        ("Mi chiamo Marco Rossi", "waiting_date", ["quando", "giorno", "data"]),
        ("Domani alle dieci", "confirming", ["riepilogo", "conferma", "taglio"]),
    ]
    booking_ok = True
    for i, (phrase, expected_fsm, expected_words) in enumerate(steps):
        wav = os.path.join(tmpdir, f"t4_step{i}.wav")
        if not generate_audio(phrase, wav):
            tr.fail("BOOKING", f"Step {i} audio gen", "Edge-TTS failed")
            booking_ok = False
            break
        r = send_audio(wav)
        fsm = r.get("fsm_state", "")
        resp = r.get("response", "").lower()
        trans = r.get("transcription", "")

        # Check FSM state
        if fsm == expected_fsm:
            tr.ok("BOOKING", f"Step {i}: '{phrase[:40]}'",
                   f"fsm={fsm} ✓ | STT='{trans[:50]}' | Sara='{resp[:60]}'")
        else:
            # Some flexibility — STT may garble the phrase
            has_keywords = any(w in resp for w in expected_words)
            if has_keywords:
                tr.warn("BOOKING", f"Step {i}: fsm={fsm}≠{expected_fsm}",
                        f"But keywords present. STT='{trans[:50]}'")
            else:
                tr.fail("BOOKING", f"Step {i}: '{phrase[:40]}'",
                        f"fsm={fsm}≠{expected_fsm} | STT='{trans[:50]}' | Sara='{resp[:60]}'")
                booking_ok = False
                break

    # ── TEST 5: NLU Timing (no timeout) ──
    print("\n--- Test 5: NLU Timing ---")
    reset_session()
    wav5 = os.path.join(tmpdir, "t5_timing.wav")
    if generate_audio("Buongiorno, vorrei informazioni sui prezzi", wav5):
        t0 = time.time()
        r = send_audio(wav5)
        elapsed = (time.time() - t0) * 1000
        if r.get("success") and elapsed < 8000:
            tr.ok("NLU", "Response time", f"{elapsed:.0f}ms (target <8000ms)")
        elif r.get("success"):
            tr.warn("NLU", "Slow response", f"{elapsed:.0f}ms")
        else:
            tr.fail("NLU", "Pipeline error", str(r.get("error", "unknown")))
    else:
        tr.fail("NLU", "Audio generation", "Edge-TTS failed")

    # ── TEST 6: TTS audio response present ──
    print("\n--- Test 6: TTS Audio Response ---")
    reset_session()
    wav6 = os.path.join(tmpdir, "t6_tts.wav")
    if generate_audio("Buongiorno", wav6):
        r = send_audio(wav6)
        audio_b64 = r.get("audio_base64", "")
        if audio_b64 and len(audio_b64) > 1000:
            audio_kb = len(audio_b64) / 1024
            tr.ok("TTS", "Audio response present", f"{audio_kb:.0f}KB base64")
        elif audio_b64:
            tr.warn("TTS", "Audio response small", f"{len(audio_b64)} chars")
        else:
            tr.fail("TTS", "No audio response", "audio_base64 empty")
    else:
        tr.fail("TTS", "Audio generation", "Edge-TTS failed")

    # ── TEST 7: Audio vs Text consistency ──
    print("\n--- Test 7: Audio vs Text Consistency ---")
    reset_session()
    set_vertical("salone")
    r_text = send_text("Vorrei prenotare un taglio uomo")
    text_fsm = r_text.get("fsm_state", "")

    reset_session()
    set_vertical("salone")
    wav7 = os.path.join(tmpdir, "t7_consist.wav")
    if generate_audio("Vorrei prenotare un taglio uomo", wav7):
        r_audio = send_audio(wav7)
        audio_fsm = r_audio.get("fsm_state", "")
        if text_fsm == audio_fsm:
            tr.ok("CONSIST", "Text vs Audio same FSM", f"both={text_fsm}")
        else:
            tr.warn("CONSIST", "Different FSM states",
                    f"text={text_fsm}, audio={audio_fsm} (STT may differ)")
    else:
        tr.fail("CONSIST", "Audio generation", "Edge-TTS failed")

    # ── Summary ──
    return tr.summary()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
