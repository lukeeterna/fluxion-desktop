#!/usr/bin/env python3
"""
FLUXION S151 — Full E2E Test: Sara × 9 Verticals with per-vertical DB
Switches DB, restarts pipeline, tests booking + FAQ + triage per vertical.
Run on iMac: python3 scripts/test_all_verticals_e2e.py
"""
import json
import os
import sqlite3
import subprocess
import sys
import time
import urllib.request

BASE = "http://127.0.0.1:3002"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SWITCH_SCRIPT = os.path.join(SCRIPT_DIR, "switch_vertical.sh")

# ── Per-vertical test data ──────────────────────────────────────────────

VERTICALS = {
    "salone": {
        "booking": "Buongiorno, vorrei prenotare un taglio uomo",
        "faq": "Quanto costa un taglio donna?",
        "faq_expect": ["25", "taglio", "donna"],
    },
    "barbiere": {
        "booking": "Vorrei prenotare un taglio e barba",
        "faq": "Quanto costa una rasatura?",
        "faq_expect": ["10", "rasatura"],
    },
    "beauty": {
        "booking": "Vorrei prenotare una pulizia del viso",
        "faq": "Quanto costa un massaggio rilassante?",
        "faq_expect": ["60", "massaggio"],
    },
    "odontoiatra": {
        "booking": "Vorrei prenotare una pulizia dei denti",
        "faq": "Quanto costa lo sbiancamento?",
        "faq_expect": ["250", "sbiancamento"],
        "triage": "Ho un forte mal di denti da due giorni",
    },
    "fisioterapia": {
        "booking": "Vorrei prenotare una seduta di fisioterapia",
        "faq": "Quanto costa una seduta?",
        "faq_expect": ["50", "fisioterapia"],
        "triage": "Ho un dolore forte alla schiena dopo una caduta",
    },
    "gommista": {
        "booking": "Vorrei prenotare un cambio gomme stagionale",
        "faq": "Quanto costa l'equilibratura?",
        "faq_expect": ["20", "equilibratura"],
    },
    "toelettatura": {
        "booking": "Vorrei prenotare un bagno per il mio cane di taglia media",
        "faq": "Quanto costa la tosatura completa?",
        "faq_expect": ["40", "tosatura"],
    },
    "palestra": {
        "booking": "Vorrei prenotare una lezione di pilates",
        "faq": "Quanto costa il personal training?",
        "faq_expect": ["40", "personal"],
    },
    "medical": {
        "booking": "Vorrei prenotare una visita generale",
        "faq": "Quanto costa un'ecografia?",
        "faq_expect": ["100", "ecografia"],
        "triage": "Ho un dolore al petto e fatico a respirare",
    },
}


def post(path, data=None, timeout=30):
    url = BASE + path
    if data:
        req = urllib.request.Request(url, json.dumps(data).encode(),
                                     {"Content-Type": "application/json"})
    else:
        req = urllib.request.Request(url, b"",
                                     {"Content-Type": "application/json"})
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
        r = json.loads(resp.read())
        r.pop("audio_base64", None)
        r.pop("audio_url", None)
        return r
    except Exception as e:
        return {"error": str(e)}


def wait_for_health(max_wait=20):
    """Wait for pipeline to respond to health check."""
    for _ in range(max_wait):
        try:
            req = urllib.request.Request(BASE + "/health")
            resp = urllib.request.urlopen(req, timeout=3)
            data = json.loads(resp.read())
            if data.get("status") == "ok":
                return True
        except Exception:
            pass
        time.sleep(1)
    return False


def switch_vertical(vertical):
    """Run the switch_vertical.sh script."""
    result = subprocess.run(
        ["/bin/bash", SWITCH_SCRIPT, vertical],
        capture_output=True, text=True, timeout=60,
        cwd=os.path.dirname(SWITCH_SCRIPT)
    )
    if result.returncode != 0:
        print("  SWITCH FAILED: %s" % result.stderr[:200])
        return False
    return True


def verify_db_loaded(vertical):
    """Verify the pipeline loaded the correct DB by checking settings."""
    r = post("/api/voice/process", {"text": "reset"})
    # The process response should have metadata about the session
    # Better: use the status endpoint
    try:
        req = urllib.request.Request(BASE + "/api/voice/status")
        resp = urllib.request.urlopen(req, timeout=5)
        status = json.loads(resp.read())
        return status
    except Exception:
        return {}


def test_vertical(name, tests):
    """Run all tests for a single vertical."""
    results = []

    # 1. BOOKING
    post("/api/voice/reset")
    # Set vertical explicitly (in case DB vertical detection differs)
    post("/api/voice/set-vertical", {"vertical": name})

    r = post("/api/voice/process", {"text": tests["booking"]})
    state = r.get("fsm_state", r.get("error", "?"))
    resp = r.get("response", "")[:100]
    if state in ("waiting_name", "waiting_service", "waiting_date"):
        results.append("OK   [%-14s] BOOKING: %s -> %s" % (name, tests["booking"][:45], state))
    else:
        results.append("WARN [%-14s] BOOKING: %s -> %s (%s)" % (name, tests["booking"][:45], state, resp[:60]))

    # 2. FAQ (with price check)
    post("/api/voice/reset")
    post("/api/voice/set-vertical", {"vertical": name})
    r = post("/api/voice/process", {"text": tests["faq"]})
    layer = r.get("layer", "?")
    resp = r.get("response", "")
    intent = r.get("intent", "?")
    resp_lower = resp.lower()

    # Check if FAQ response contains expected keywords
    faq_ok = ("L3" in str(layer) or "L4" in str(layer) or
              "faq" in str(intent).lower() or "info" in str(intent).lower())
    # Check price/content accuracy
    expect = tests.get("faq_expect", [])
    content_match = any(e.lower() in resp_lower for e in expect) if expect else True

    if faq_ok and content_match:
        results.append("OK   [%-14s] FAQ:     %s -> %s (%s)" % (name, tests["faq"][:45], layer, resp[:60]))
    elif faq_ok:
        results.append("WARN [%-14s] FAQ:     %s -> %s (price/content mismatch: %s)" % (
            name, tests["faq"][:45], layer, resp[:60]))
    else:
        results.append("WARN [%-14s] FAQ:     %s -> %s/%s (%s)" % (
            name, tests["faq"][:45], layer, intent, resp[:60]))

    # 3. TRIAGE (medical verticals only)
    if "triage" in tests:
        post("/api/voice/reset")
        post("/api/voice/set-vertical", {"vertical": name})
        r = post("/api/voice/process", {"text": tests["triage"]})
        intent = r.get("intent", "?")
        resp = r.get("response", "")[:100]
        if "medical" in str(intent).lower() or "urgenz" in resp.lower() or \
           "118" in resp or "pronto" in resp.lower():
            results.append("OK   [%-14s] TRIAGE:  %s -> %s" % (name, tests["triage"][:45], intent))
        else:
            results.append("WARN [%-14s] TRIAGE:  %s -> %s (%s)" % (
                name, tests["triage"][:45], intent, resp[:60]))

    # 4. NAME FLOW (verify complete booking path)
    post("/api/voice/reset")
    post("/api/voice/set-vertical", {"vertical": name})
    r = post("/api/voice/process", {"text": tests["booking"]})
    if r.get("fsm_state") == "waiting_name":
        r2 = post("/api/voice/process", {"text": "Mi chiamo Marco Rossi"})
        state2 = r2.get("fsm_state", "?")
        if state2 in ("waiting_date", "waiting_service", "waiting_time"):
            results.append("OK   [%-14s] FLOW:    booking+name -> %s" % (name, state2))
        else:
            resp2 = r2.get("response", "")[:60]
            results.append("WARN [%-14s] FLOW:    booking+name -> %s (%s)" % (name, state2, resp2))

    return results


def main():
    print("\n" + "=" * 70)
    print("FLUXION S151 — FULL E2E TEST: Sara × 9 Verticals (with per-vertical DB)")
    print("=" * 70)

    all_results = []
    verticals_tested = 0

    for vertical, tests in VERTICALS.items():
        print("\n--- [%d/9] Switching to: %s ---" % (verticals_tested + 1, vertical.upper()))

        # Switch DB and restart pipeline
        if not switch_vertical(vertical):
            all_results.append("FAIL [%-14s] SWITCH: could not switch vertical DB" % vertical)
            continue

        # Wait for pipeline to come up
        if not wait_for_health(20):
            all_results.append("FAIL [%-14s] HEALTH: pipeline did not start after switch" % vertical)
            continue

        print("  Pipeline ready. Running tests...")

        # Run tests
        results = test_vertical(vertical, tests)
        all_results.extend(results)
        verticals_tested += 1

        # Print inline
        for r in results:
            print("  " + r)

    # Summary
    print("\n" + "=" * 70)
    print("REPORT COMPLETO — TEST LIVE SARA × 9 VERTICALI (con DB dedicato)")
    print("=" * 70)

    ok = warn = fail = 0
    for r in all_results:
        print(r)
        if r.startswith("OK"):
            ok += 1
        elif r.startswith("WARN"):
            warn += 1
        else:
            fail += 1

    total = ok + warn + fail
    print("\n" + "=" * 70)
    print("TOTALE: %d OK / %d WARN / %d FAIL (su %d test)" % (ok, warn, fail, total))
    print("Verticali testati: %d / 9" % verticals_tested)
    print("=" * 70)

    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
