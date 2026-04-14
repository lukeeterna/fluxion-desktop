#!/usr/bin/env python3
"""S158 — Test Sara multi-verticale: set_vertical + booking flow per ogni verticale."""
import requests
import json
import time
import sys

BASE = "http://127.0.0.1:3002"

VERTICALS = {
    "salone": ("Vorrei prenotare un taglio", "Marco Rossi"),
    "beauty": ("Vorrei un trattamento viso", "Laura Bianchi"),
    "palestra": ("Vorrei iscrivermi a un corso", "Paolo Verdi"),
    "auto": ("Devo fare il tagliando", "Giuseppe Neri"),
    "gommista": ("Devo cambiare le gomme", "Antonio Russo"),
    "medical": ("Vorrei prenotare una visita", "Maria Esposito"),
    "odontoiatra": ("Pulizia dei denti", "Franco Colombo"),
    "fisioterapia": ("Seduta di fisioterapia", "Elena Ricci"),
    "toelettatura": ("Bagno per il mio cane", "Sergio Moretti"),
    "wellness": ("Vorrei un massaggio", "Chiara Ferrari"),
    "professionale": ("Vorrei un appuntamento", "Luca Gallo"),
}

FAQ_QUESTIONS = {
    "salone": "Quanto costa un taglio?",
    "beauty": "Quali trattamenti fate?",
    "palestra": "Quanto costa un abbonamento?",
    "auto": "Quanto costa un tagliando?",
    "gommista": "Quanto costa il cambio gomme?",
    "medical": "Quali visite fate?",
    "odontoiatra": "Quanto costa una pulizia dentale?",
    "fisioterapia": "Quanto costa una seduta?",
    "toelettatura": "Quanto costa il bagno per un cane?",
    "wellness": "Quanto costa un massaggio?",
    "professionale": "Quali servizi offrite?",
}

results = []

def test_vertical(vert, booking_q, name):
    """Test a single vertical: set_vertical, booking flow, FAQ."""
    tag = f"[{vert:15s}]"
    sub_results = []

    # Reset
    try:
        requests.post(f"{BASE}/api/voice/reset", timeout=5)
    except Exception:
        pass
    time.sleep(0.3)

    # Set vertical
    try:
        r = requests.post(f"{BASE}/api/voice/set-vertical", json={"vertical": vert}, timeout=10)
        if r.status_code != 200:
            sub_results.append(f"FAIL {tag} set_vertical failed: {r.text[:80]}")
            return sub_results
        sub_results.append(f"OK   {tag} set_vertical OK")
    except Exception as e:
        sub_results.append(f"FAIL {tag} set_vertical error: {e}")
        return sub_results

    time.sleep(0.5)

    # Step 1: Booking request
    try:
        r1 = requests.post(f"{BASE}/api/voice/process", json={"text": booking_q}, timeout=30)
        d1 = r1.json()
        s1 = d1.get("fsm_state", d1.get("state", "?"))
        a1 = d1.get("response", "")[:100]
        if "waiting_name" in s1 or "chiami" in a1.lower():
            sub_results.append(f"OK   {tag} BOOKING: state={s1} | Sara: {a1}")
        else:
            sub_results.append(f"WARN {tag} BOOKING: state={s1} | Sara: {a1}")
    except Exception as e:
        sub_results.append(f"FAIL {tag} BOOKING error: {e}")
        return sub_results

    # Step 2: Give name
    time.sleep(0.3)
    try:
        r2 = requests.post(f"{BASE}/api/voice/process", json={"text": f"Mi chiamo {name}"}, timeout=30)
        d2 = r2.json()
        s2 = d2.get("fsm_state", d2.get("state", "?"))
        a2 = d2.get("response", "")[:120]
        if "waiting" in s2 or "confirm" in s2:
            sub_results.append(f"OK   {tag} NAME:    state={s2} | Sara: {a2}")
        else:
            sub_results.append(f"WARN {tag} NAME:    state={s2} | Sara: {a2}")
    except Exception as e:
        sub_results.append(f"FAIL {tag} NAME error: {e}")

    # Step 3: FAQ test (separate session)
    try:
        requests.post(f"{BASE}/api/voice/reset", timeout=5)
    except Exception:
        pass
    time.sleep(0.3)
    try:
        requests.post(f"{BASE}/api/voice/set-vertical", json={"vertical": vert}, timeout=10)
    except Exception:
        pass
    time.sleep(0.5)

    faq_q = FAQ_QUESTIONS.get(vert, "Quali servizi offrite?")
    try:
        r3 = requests.post(f"{BASE}/api/voice/process", json={"text": faq_q}, timeout=30)
        d3 = r3.json()
        s3 = d3.get("fsm_state", d3.get("state", "?"))
        a3 = d3.get("response", "")[:150]
        # Check for unresolved variables like [PREZZO_X]
        has_unresolved = "[" in a3 and "]" in a3 and "PREZZO" in a3.upper()
        if has_unresolved:
            sub_results.append(f"WARN {tag} FAQ:     UNRESOLVED VARS | state={s3} | Sara: {a3}")
        elif len(a3) > 10:
            sub_results.append(f"OK   {tag} FAQ:     state={s3} | Sara: {a3}")
        else:
            sub_results.append(f"WARN {tag} FAQ:     short response | state={s3} | Sara: {a3}")
    except Exception as e:
        sub_results.append(f"FAIL {tag} FAQ error: {e}")

    return sub_results


# Run all tests
print("=" * 100)
print("SARA S158 MULTI-VERTICAL TEST")
print("=" * 100)

ok_count = 0
warn_count = 0
fail_count = 0

for vert, (booking_q, name) in VERTICALS.items():
    print(f"\n--- {vert.upper()} ---")
    sub = test_vertical(vert, booking_q, name)
    for line in sub:
        print(line)
        if line.startswith("OK"):
            ok_count += 1
        elif line.startswith("WARN"):
            warn_count += 1
        elif line.startswith("FAIL"):
            fail_count += 1
    results.extend(sub)

print("\n" + "=" * 100)
print(f"TOTALE: {ok_count + warn_count + fail_count} | OK: {ok_count} | WARN: {warn_count} | FAIL: {fail_count}")
print("=" * 100)

# Exit with error if any FAIL
if fail_count > 0:
    sys.exit(1)
