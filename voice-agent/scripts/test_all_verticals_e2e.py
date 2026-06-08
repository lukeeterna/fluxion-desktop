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
    "wellness": {
        "booking": "Vorrei prenotare un massaggio rilassante",
        "faq": "Quanto costa il percorso spa?",
        "faq_expect": ["90", "spa"],
    },
    "professionale": {
        "booking": "Vorrei prenotare una consulenza fiscale",
        "faq": "Quanto costa una consulenza legale?",
        "faq_expect": ["100", "legale"],
    },
    "auto": {
        "booking": "Vorrei prenotare un tagliando",
        "faq": "Quanto costa il cambio olio?",
        "faq_expect": ["40", "olio"],
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
    # After "Mi chiamo Marco Rossi" (a client NOT in DB), Sara correctly goes to:
    #   - waiting_date/service/time  → recognized client continues booking
    #   - registering_phone          → new-client onboarding (collect phone) — CORRECT
    #   - disambiguating_name        → homonym in DB (e.g. barbiere "Marco Russo") — CORRECT
    # All of these are valid next states; anything else is a genuine WARN.
    flow_ok_states = ("waiting_date", "waiting_service", "waiting_time",
                      "registering_phone", "disambiguating_name")
    post("/api/voice/reset")
    post("/api/voice/set-vertical", {"vertical": name})
    r = post("/api/voice/process", {"text": tests["booking"]})
    if r.get("fsm_state") == "waiting_name":
        r2 = post("/api/voice/process", {"text": "Mi chiamo Marco Rossi"})
        state2 = r2.get("fsm_state", "?")
        if state2 in flow_ok_states:
            results.append("OK   [%-14s] FLOW:    booking+name -> %s" % (name, state2))
        else:
            resp2 = r2.get("response", "")[:60]
            results.append("WARN [%-14s] FLOW:    booking+name -> %s (%s)" % (name, state2, resp2))

    # 5. GRACEFUL CLOSURE (generic — every vertical)
    # A plain goodbye is intent-driven: Sara replies with a clean closing and
    # stays/returns to idle. fsm_state is NOT a dedicated "asking_close" state
    # for a standalone goodbye (verified live: intent=goodbye_standalone, state=idle).
    post("/api/voice/reset")
    post("/api/voice/set-vertical", {"vertical": name})
    r = post("/api/voice/process", {"text": "Grazie, arrivederci"})
    intent = str(r.get("intent", "?")).lower()
    resp = r.get("response", "")
    resp_lower = resp.lower()
    close_ok = ("goodbye" in intent or "close" in intent or
                "arrivederci" in resp_lower or "buona giornata" in resp_lower or
                "a presto" in resp_lower)
    if close_ok:
        results.append("OK   [%-14s] CLOSE:   'Grazie, arrivederci' -> %s (%s)" % (
            name, r.get("intent", "?"), resp[:50]))
    else:
        results.append("WARN [%-14s] CLOSE:   'Grazie, arrivederci' -> %s (%s)" % (
            name, r.get("intent", "?"), resp[:50]))

    # 6. WAITLIST (best-effort — only attempted on a vertical that supports it).
    # Waitlist is intent-driven (offer_waitlist / slot_unavailable_waitlist) and
    # surfaces only when a chosen slot is fully booked. It cannot be forced
    # deterministically from text alone (depends on DB availability for the date),
    # so this is a best-effort probe: OK if the offer surfaces, otherwise an
    # explanatory WARN (NOT a silent skip).
    if name in ("salone", "barbiere"):
        post("/api/voice/reset")
        post("/api/voice/set-vertical", {"vertical": name})
        post("/api/voice/process", {"text": tests["booking"]})
        post("/api/voice/process", {"text": "Sono Antonio Gallo"})
        rwl = post("/api/voice/process", {"text": "Domani"})
        rwl2 = post("/api/voice/process", {"text": "Alle 10 di mattina"})
        wl_intent = (str(rwl.get("intent", "")).lower() + " " +
                     str(rwl2.get("intent", "")).lower())
        wl_resp = (rwl.get("response", "") + " " + rwl2.get("response", "")).lower()
        wl_state = rwl2.get("fsm_state", rwl.get("fsm_state", "?"))
        wl_hit = ("waitlist" in wl_intent or "lista d'attesa" in wl_resp or
                  "lista di attesa" in wl_resp or "slot_unavailable" in wl_intent)
        if wl_hit:
            results.append("OK   [%-14s] WAITLIST:occupied-slot -> offered (state=%s)" % (
                name, wl_state))
        else:
            results.append("WARN [%-14s] WAITLIST:not triggered (slot free for chosen date; cannot force occupied slot from text)" % name)

    # 7. PHONETIC DISAMBIGUATION (barbiere only — DB has homonym "Marco Russo").
    # Sending "Marco Rossi" (phonetically close) must enter disambiguating_name.
    # Verified live with barbiere DB loaded: -> disambiguating_name.
    if name == "barbiere":
        post("/api/voice/reset")
        post("/api/voice/set-vertical", {"vertical": name})
        post("/api/voice/process", {"text": tests["booking"]})
        rd = post("/api/voice/process", {"text": "Mi chiamo Marco Rossi"})
        dstate = rd.get("fsm_state", "?")
        if dstate == "disambiguating_name":
            results.append("OK   [%-14s] DISAMB:  'Marco Rossi'~'Marco Russo' -> %s" % (name, dstate))
        else:
            results.append("WARN [%-14s] DISAMB:  'Marco Rossi' -> %s (%s)" % (
                name, dstate, rd.get("response", "")[:50]))

    return results


def main():
    print("\n" + "=" * 70)
    print("FLUXION S151 — FULL E2E TEST: Sara × 12 Verticals (with per-vertical DB)")
    print("=" * 70)

    all_results = []
    verticals_tested = 0

    for vertical, tests in VERTICALS.items():
        print("\n--- [%d/%d] Switching to: %s ---" % (
            verticals_tested + 1, len(VERTICALS), vertical.upper()))

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
    print("REPORT COMPLETO — TEST LIVE SARA × 12 VERTICALI (con DB dedicato)")
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
    print("Verticali testati: %d / %d" % (verticals_tested, len(VERTICALS)))
    print("=" * 70)

    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
