#!/usr/bin/env python3
"""S158 — Test LIVE Sara multi-verticale COMPLETO.
Per ogni verticale: reset → set_vertical → greeting → booking → name → FAQ → close.
Output: log completo con timestamp, stato FSM, risposte Sara.
"""
import requests
import json
import time
import sys
from datetime import datetime

BASE = "http://127.0.0.1:3002"

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURAZIONE TEST PER VERTICALE
# ══════════════════════════════════════════════════════════════════════════════
TESTS = [
    {
        "vertical": "salone",
        "label": "SALONE PARRUCCHIERE",
        "steps": [
            ("Buongiorno, vorrei un appuntamento", "BOOKING"),
            ("Mi chiamo Marco Rossi", "NAME"),
            ("Un taglio uomo per favore", "SERVICE"),
            ("Quanto costa un taglio donna?", "FAQ_AFTER_RESET"),
            ("Che orari fate?", "FAQ2"),
        ]
    },
    {
        "vertical": "beauty",
        "label": "CENTRO ESTETICO",
        "steps": [
            ("Buongiorno, vorrei prenotare un trattamento viso", "BOOKING"),
            ("Mi chiamo Laura Bianchi", "NAME"),
            ("Quanto costa una ceretta?", "FAQ_AFTER_RESET"),
            ("Fate anche manicure?", "FAQ2"),
        ]
    },
    {
        "vertical": "palestra",
        "label": "PALESTRA / FITNESS",
        "steps": [
            ("Ciao, vorrei iscrivermi a un corso di yoga", "BOOKING"),
            ("Paolo Verdi", "NAME"),
            ("Quanto costa una lezione di pilates?", "FAQ_AFTER_RESET"),
            ("Avete personal trainer?", "FAQ2"),
        ]
    },
    {
        "vertical": "auto",
        "label": "OFFICINA MECCANICA",
        "steps": [
            ("Buongiorno, devo fare il tagliando alla macchina", "BOOKING"),
            ("Giuseppe Neri", "NAME"),
            ("Quanto costa un tagliando?", "FAQ_AFTER_RESET"),
            ("Fate anche la revisione?", "FAQ2"),
        ]
    },
    {
        "vertical": "gommista",
        "label": "GOMMISTA",
        "steps": [
            ("Buongiorno, devo cambiare le gomme invernali", "BOOKING"),
            ("Antonio Russo", "NAME"),
            ("Quanto costa il cambio gomme?", "FAQ_AFTER_RESET"),
            ("Fate anche l'equilibratura?", "FAQ2"),
        ]
    },
    {
        "vertical": "medical",
        "label": "STUDIO MEDICO",
        "steps": [
            ("Buongiorno, vorrei prenotare una visita medica", "BOOKING"),
            ("Maria Esposito", "NAME"),
            ("Quanto costa una visita generale?", "FAQ_AFTER_RESET"),
            ("Fate anche ecografie?", "FAQ2"),
        ]
    },
    {
        "vertical": "odontoiatra",
        "label": "STUDIO DENTISTICO",
        "steps": [
            ("Buongiorno, vorrei prenotare una pulizia dei denti", "BOOKING"),
            ("Franco Colombo", "NAME"),
            ("Quanto costa l'igiene dentale?", "FAQ_AFTER_RESET"),
            ("Fate lo sbiancamento?", "FAQ2"),
        ]
    },
    {
        "vertical": "fisioterapia",
        "label": "STUDIO FISIOTERAPIA",
        "steps": [
            ("Buongiorno, vorrei prenotare una seduta di fisioterapia", "BOOKING"),
            ("Elena Ricci", "NAME"),
            ("Quanto costa una seduta?", "FAQ_AFTER_RESET"),
            ("Fate anche massoterapia?", "FAQ2"),
        ]
    },
    {
        "vertical": "toelettatura",
        "label": "TOELETTATURA PET",
        "steps": [
            ("Buongiorno, vorrei prenotare un bagno per il mio cane", "BOOKING"),
            ("Sergio Moretti", "NAME"),
            ("Quanto costa il bagno per un cane di taglia media?", "FAQ_AFTER_RESET"),
            ("Fate anche la tosatura?", "FAQ2"),
        ]
    },
    {
        "vertical": "wellness",
        "label": "CENTRO BENESSERE / SPA",
        "steps": [
            ("Buongiorno, vorrei prenotare un massaggio rilassante", "BOOKING"),
            ("Chiara Ferrari", "NAME"),
            ("Quanto costa un massaggio?", "FAQ_AFTER_RESET"),
            ("Avete la sauna?", "FAQ2"),
        ]
    },
    {
        "vertical": "professionale",
        "label": "STUDIO PROFESSIONALE",
        "steps": [
            ("Buongiorno, vorrei fissare un appuntamento per una consulenza", "BOOKING"),
            ("Luca Gallo", "NAME"),
            ("Quanto costa una consulenza fiscale?", "FAQ_AFTER_RESET"),
            ("Fate anche consulenza legale?", "FAQ2"),
        ]
    },
]


def call_api(endpoint, payload=None, method="POST"):
    """Call Sara API with error handling."""
    url = f"{BASE}{endpoint}"
    try:
        if method == "POST":
            r = requests.post(url, json=payload, timeout=30)
        else:
            r = requests.get(url, timeout=10)
        return r.status_code, r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text
    except Exception as e:
        return 0, str(e)


def run_vertical_test(test_config):
    """Run complete test for one vertical."""
    vert = test_config["vertical"]
    label = test_config["label"]
    steps = test_config["steps"]
    results = []

    ts = datetime.now().strftime("%H:%M:%S")
    results.append(f"\n{'='*90}")
    results.append(f"  {label} (vertical={vert}) — {ts}")
    results.append(f"{'='*90}")

    # Reset + Set vertical
    call_api("/api/voice/reset")
    time.sleep(0.3)
    code, data = call_api("/api/voice/set-vertical", {"vertical": vert})
    if code != 200:
        results.append(f"  FAIL  set_vertical: {data}")
        return results, 0, 0, 1

    # Extract greeting from set_vertical response
    if isinstance(data, dict):
        greeting = data.get("greeting", data.get("response", ""))
        if greeting:
            results.append(f"  SARA (greeting): {greeting[:150]}")
    results.append("")

    time.sleep(0.5)

    ok = 0
    warn = 0
    fail = 0
    did_reset_for_faq = False

    for user_msg, step_type in steps:
        # FAQ steps after booking: reset session first
        if step_type == "FAQ_AFTER_RESET" and not did_reset_for_faq:
            call_api("/api/voice/reset")
            time.sleep(0.3)
            call_api("/api/voice/set-vertical", {"vertical": vert})
            time.sleep(0.5)
            did_reset_for_faq = True

        code, data = call_api("/api/voice/process", {"text": user_msg})
        if code != 200:
            results.append(f"  FAIL  [{step_type:20s}] {user_msg}")
            results.append(f"        Error: {data}")
            fail += 1
            continue

        fsm = data.get("fsm_state", "?")
        resp = data.get("response", "")
        intent = data.get("intent", "?")
        layer = data.get("layer", "?")

        # Determine OK/WARN/FAIL
        status = "OK  "
        if step_type == "BOOKING":
            if "chiami" in resp.lower() or "waiting_name" in fsm:
                status = "OK  "
            elif "servizio" in resp.lower() or "waiting_service" in fsm:
                status = "OK  "  # disambiguation is OK
            else:
                status = "WARN"
        elif step_type == "NAME":
            if "waiting" in fsm or "registering" in fsm or "confirm" in fsm:
                status = "OK  "
            else:
                status = "WARN"
        elif step_type.startswith("FAQ"):
            # Check for cross-contamination
            wrong_vertical_words = []
            if vert not in ("auto", "gommista"):
                wrong_vertical_words = ["cambio gomme", "equilibratura", "convergenza", "foratura"]
            if vert not in ("salone", "barbiere"):
                wrong_vertical_words += ["taglio uomo", "taglio donna"]
            resp_lower = resp.lower()
            if any(w in resp_lower for w in wrong_vertical_words):
                status = "FAIL"  # Cross-contamination!
            elif len(resp) < 15:
                status = "WARN"
            else:
                status = "OK  "

        if status == "OK  ":
            ok += 1
        elif status == "WARN":
            warn += 1
        else:
            fail += 1

        results.append(f"  {status} [{step_type:20s}] fsm={fsm:20s} intent={intent}")
        results.append(f"        USER: {user_msg}")
        results.append(f"        SARA: {resp[:200]}")
        results.append("")

    return results, ok, warn, fail


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    start = datetime.now()
    print(f"""
╔══════════════════════════════════════════════════════════════════════════════════════════╗
║  FLUXION — TEST LIVE SARA MULTI-VERTICALE                                              ║
║  S158 — {start.strftime('%Y-%m-%d %H:%M:%S')}                                                              ║
║  11 verticali × 4-5 step = ~50 interazioni                                             ║
╚══════════════════════════════════════════════════════════════════════════════════════════╝""")

    total_ok = 0
    total_warn = 0
    total_fail = 0
    vertical_results = []

    for test in TESTS:
        lines, ok, warn, fail = run_vertical_test(test)
        for line in lines:
            print(line)
        total_ok += ok
        total_warn += warn
        total_fail += fail
        tag = "PASS" if fail == 0 and warn == 0 else ("WARN" if fail == 0 else "FAIL")
        vertical_results.append((test["label"], test["vertical"], ok, warn, fail, tag))

    elapsed = (datetime.now() - start).total_seconds()

    print(f"""
╔══════════════════════════════════════════════════════════════════════════════════════════╗
║  RIEPILOGO FINALE                                                                      ║
╠══════════════════════════════════════════════════════════════════════════════════════════╣""")
    for label, vert, ok, warn, fail, tag in vertical_results:
        indicator = "✅" if tag == "PASS" else ("⚠️ " if tag == "WARN" else "❌")
        print(f"║  {indicator} {label:30s} ({vert:15s}) OK={ok} WARN={warn} FAIL={fail}")
    print(f"""╠══════════════════════════════════════════════════════════════════════════════════════════╣
║  TOTALE: {total_ok + total_warn + total_fail:3d} interazioni | OK: {total_ok:2d} | WARN: {total_warn:2d} | FAIL: {total_fail:2d} | Tempo: {elapsed:.0f}s          ║
╚══════════════════════════════════════════════════════════════════════════════════════════╝""")

    if total_fail > 0:
        sys.exit(1)
