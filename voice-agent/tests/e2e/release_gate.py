#!/usr/bin/env python3
"""
FLUXION Sara — Release Gate (S200)
====================================
Test harness automatizzata multi-vertical multi-scenario per validare Sara
pre-release. Zero errori consentiti: exit code != 0 se qualunque test FAIL.

Tier 1 — Core deep:    salone, auto, medical, palestra, beauty, professionale
                       (full stress: booking multi-turn + disambig + cancel + latency)
Tier 2 — Extended smoke: barbiere, fisioterapia, gommista, odontoiatra, toelettatura
                       (greeting + booking intent + closing)
Tier 3 — DB verify:    schema integrity + recent activity post-test

Eseguire su iMac (pipeline bound 127.0.0.1:3002):

    ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && \\
        python3 tests/e2e/release_gate.py --release-gate"

Opzioni:
    --release-gate      Strict mode: exit 1 se R.fail > 0 (default: exit 0)
    --report=PATH       Path JSON report (default /tmp/sara-release-gate.json)
    --tier=N            Esegui solo Tier N (1, 2, 3) — default: tutti
    --verbose           Mostra risposte Sara per ogni turno
    --skip-extended     Skippa Tier 2 (utile per dev rapido)
    --skip-db           Skippa Tier 3 DB verify

Exit codes:
    0   PASS (zero FAIL)
    1   FAIL (almeno 1 FAIL → release bloccato)
    2   Pipeline non raggiungibile / errore infrastruttura
"""

import json
import os
import sqlite3
import sys
import time
from pathlib import Path

# Import framework esistente
THIS_DIR = Path(__file__).parent
sys.path.insert(0, str(THIS_DIR))

import test_sara_stress_per_verticale as base  # noqa: E402
from test_sara_stress_per_verticale import (  # noqa: E402
    R,
    VERTICALS,
    URL,
    api,
    health,
    process,
    reset,
    set_vertical,
    test_single_vertical,
)

# ============================================================================
# Config
# ============================================================================

# Verticals presenti in filesystem ma NON nel test stress -> smoke coverage
EXTENDED_VERTICALS = [
    "barbiere",
    "fisioterapia",
    "gommista",
    "odontoiatra",
    "toelettatura",
]

# DB path su iMac (fallback se env override)
DB_PATH = os.environ.get(
    "FLUXION_DB_PATH",
    "/Volumes/MacSSD - Dati/fluxion/voice-agent/data/fluxion.db",
)

# Soglie release gate (calibrate S200)
# Hard-fail su P50 (mediana = vera latenza user-facing tipica) + % sample lenti
# (regressione sistemica vs outlier). P95 mantenuto come WARN per monitoring.
LATENCY_P50_HARD_FAIL_MS = 1500   # Mediana > 1500ms = regressione user-facing reale
LATENCY_SLOW_SAMPLE_MS = 5000      # Soglia "sample lento"
LATENCY_SLOW_RATIO_HARD_FAIL = 0.30  # >30% sample > 5s = regressione sistemica
LATENCY_P95_WARN_MS = 2000         # Target SLO v1.1 (informativo)
LATENCY_P95_HARD_FAIL_MS = 12000   # Catastrofica only (pipeline completely broken)


# ============================================================================
# Tier 2 — Extended verticals smoke
# ============================================================================

def run_extended_smoke(vert):
    """Smoke test per verticali extended (config-only, no Python differenziato).

    3 check minimi: greeting, booking intent, closing graceful.
    """
    tag = vert.upper()
    scenario = "T2_SMOKE"

    # Reset + set vertical
    reset()
    r = set_vertical(vert)
    if not r.get("success", True) and "error" in r:
        # Vertical non riconosciuto dalla pipeline (config-only filesystem)
        R.WARN(tag, scenario, "set-vertical not supported: %s" % r.get("error", "")[:60])
        # Continuiamo con vertical default — testiamo che pipeline non crashi
    else:
        R.OK(tag, scenario, "set-vertical accepted")

    # Greeting
    r = process("Buongiorno")
    resp = r.get("response", "").lower()
    ms = r.get("_ms", 0)
    success = r.get("success", False)
    if not success:
        R.FAIL(tag, scenario, "Greeting -> errore: %s" % r.get("error", "")[:60], ms)
        return
    if any(kw in resp for kw in ["buongiorno", "sara", "posso", "aiut", "salv"]):
        R.OK(tag, scenario, "Greeting OK", ms)
    else:
        R.FAIL(tag, scenario, "Greeting -> resp='%s'" % resp[:60], ms)

    # Booking intent
    r = process("Vorrei prenotare un appuntamento")
    resp = r.get("response", "").lower()
    fsm = r.get("fsm_state", "")
    ms = r.get("_ms", 0)
    fsm_valid = fsm in (
        "waiting_service", "waiting_name", "waiting_date", "waiting_time",
        "propose_registration", "registering_name", "registering_surname",
        "asking_service", "asking_date", "asking_name", "collecting_info",
    )
    if fsm_valid:
        R.OK(tag, scenario, "Booking intent -> fsm=%s" % fsm, ms)
    elif any(kw in resp for kw in ["servizio", "quale", "che cosa", "prenot", "appuntamento", "nome"]):
        R.OK(tag, scenario, "Booking intent -> resp keyword match", ms)
    else:
        R.FAIL(tag, scenario, "Booking intent -> fsm=%s resp='%s'" % (fsm, resp[:60]), ms)

    # Closing graceful
    r = process("Grazie, arrivederci")
    resp = r.get("response", "").lower()
    ms = r.get("_ms", 0)
    if any(kw in resp for kw in ["arrivederci", "buona giornata", "presto", "risentir", "ciao"]):
        R.OK(tag, scenario, "Closing OK", ms)
    else:
        R.WARN(tag, scenario, "Closing -> resp='%s'" % resp[:60], ms)


# ============================================================================
# Tier 3 — DB integrity post-test
# ============================================================================

def verify_db_state():
    """Verifica DB SQLite integrita' schema + attivita' recente."""
    tag = "DB"
    if not os.path.exists(DB_PATH):
        R.WARN(tag, "VERIFY", "DB path non trovato: %s (skip)" % DB_PATH)
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Schema: tabelle critiche presenti
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row["name"] for row in cur.fetchall()}
        required = {"clients", "appointments"}
        missing = required - tables
        if missing:
            R.FAIL(tag, "SCHEMA", "Tabelle critiche mancanti: %s" % missing)
        else:
            R.OK(tag, "SCHEMA", "Tabelle critiche presenti: %s" % required)

        # Clienti totali
        cur.execute("SELECT COUNT(*) AS n FROM clients")
        n_clients = cur.fetchone()["n"]
        R.OK(tag, "CLIENTS_COUNT", "clienti=%d" % n_clients)

        # Appointments recenti (ultima ora)
        try:
            cur.execute(
                "SELECT COUNT(*) AS n FROM appointments "
                "WHERE created_at > datetime('now', '-1 hour')"
            )
            n_recent = cur.fetchone()["n"]
            R.OK(tag, "RECENT_APPT", "appuntamenti ultima ora=%d" % n_recent)
        except sqlite3.OperationalError as e:
            R.WARN(tag, "RECENT_APPT", "query failed: %s" % str(e)[:80])

        # Waitlist presente (se tabella esiste)
        if "waitlist" in tables:
            cur.execute("SELECT COUNT(*) AS n FROM waitlist")
            n_wait = cur.fetchone()["n"]
            R.OK(tag, "WAITLIST", "waitlist entries=%d" % n_wait)

        # Foreign key integrity (assert appointments.cliente_id resolvable)
        try:
            cur.execute(
                "SELECT COUNT(*) AS n FROM appointments a "
                "LEFT JOIN clients c ON a.cliente_id = c.id "
                "WHERE c.id IS NULL AND a.cliente_id IS NOT NULL"
            )
            orphans = cur.fetchone()["n"]
            if orphans == 0:
                R.OK(tag, "FK_INTEGRITY", "zero appointments orfani")
            else:
                R.FAIL(tag, "FK_INTEGRITY", "%d appointments con cliente_id non risolvibile" % orphans)
        except sqlite3.OperationalError as e:
            R.WARN(tag, "FK_INTEGRITY", "query failed: %s" % str(e)[:80])

        conn.close()
    except Exception as e:
        R.FAIL(tag, "VERIFY", "DB error: %s" % str(e)[:120])


# ============================================================================
# Argparse minimale (no dipendenze)
# ============================================================================

def parse_args(argv):
    opts = {
        "strict": False,
        "report_path": "/tmp/sara-release-gate.json",
        "tier": None,
        "skip_extended": False,
        "skip_db": False,
    }
    for a in argv[1:]:
        if a == "--release-gate":
            opts["strict"] = True
        elif a.startswith("--report="):
            opts["report_path"] = a.split("=", 1)[1]
        elif a.startswith("--tier="):
            opts["tier"] = int(a.split("=", 1)[1])
        elif a == "--verbose":
            base.VERBOSE = True
        elif a == "--skip-extended":
            opts["skip_extended"] = True
        elif a == "--skip-db":
            opts["skip_db"] = True
        elif a in ("-h", "--help"):
            print(__doc__)
            sys.exit(0)
        else:
            print("Opzione sconosciuta: %s (--help per uso)" % a)
            sys.exit(2)
    return opts


# ============================================================================
# MAIN
# ============================================================================

def main():
    opts = parse_args(sys.argv)

    print("=" * 80)
    print("FLUXION Sara — RELEASE GATE")
    print("Pipeline: %s" % URL)
    print("Strict mode: %s" % opts["strict"])
    print("Report: %s" % opts["report_path"])
    print("=" * 80)

    # Pre-flight: health
    h = health()
    if not h or h.get("status") != "ok":
        print("FATAL: pipeline non raggiungibile a %s" % URL)
        sys.exit(2)
    print("Pipeline UP: %s | STT=%s | TTS=%s" % (
        h.get("version", "?"),
        h.get("features", {}).get("stt", "?"),
        h.get("features", {}).get("tts", "?"),
    ))

    # ── Pre-warm: scalda pipeline + tutti i verticals (latencies scartate) ──
    # Root cause cold-start outliers (S200): primo turn dopo set_vertical
    # carica config/cache vertical-specifici. Pre-warming elimina la varianza
    # cold-start dai sample misurati. Le latencies pre-warm NON vengono incluse
    # in R.latencies (resettato dopo).
    all_verticals_to_warm = sorted(VERTICALS.keys()) + EXTENDED_VERTICALS
    print("\n[PREWARM] Scaldo pipeline + %d verticals..." % len(all_verticals_to_warm))
    for vert in all_verticals_to_warm:
        try:
            reset()
            set_vertical(vert)
            # Una chiamata greeting per scaldare ogni vertical
            api("/api/voice/process", {"text": "Buongiorno"})
        except Exception as e:
            print("  [PREWARM] %s WARN: %s" % (vert, str(e)[:60]))
    # Scarta latencies del pre-warm
    R.latencies = []
    print("[PREWARM] Done. Latencies reset.")

    t_start = time.time()

    # ── Tier 1: Core verticals deep ──────────────────────────────────
    if opts["tier"] is None or opts["tier"] == 1:
        print("\n" + "#" * 80)
        print("# TIER 1 — Core deep (%d verticals)" % len(VERTICALS))
        print("#" * 80)
        for vert in sorted(VERTICALS.keys()):
            try:
                test_single_vertical(vert)
            except Exception as e:
                R.FAIL(vert.upper(), "T1_CRASH", "exception: %s" % str(e)[:120])

    # ── Tier 2: Extended verticals smoke ─────────────────────────────
    if (opts["tier"] is None or opts["tier"] == 2) and not opts["skip_extended"]:
        print("\n" + "#" * 80)
        print("# TIER 2 — Extended smoke (%d verticals)" % len(EXTENDED_VERTICALS))
        print("#" * 80)
        for vert in EXTENDED_VERTICALS:
            print("\n--- %s ---" % vert.upper())
            try:
                run_extended_smoke(vert)
            except Exception as e:
                R.FAIL(vert.upper(), "T2_CRASH", "exception: %s" % str(e)[:120])

    # ── Tier 3: DB verify ────────────────────────────────────────────
    if (opts["tier"] is None or opts["tier"] == 3) and not opts["skip_db"]:
        print("\n" + "#" * 80)
        print("# TIER 3 — DB integrity")
        print("#" * 80)
        verify_db_state()

    elapsed = time.time() - t_start

    # Summary console
    summary_ok = R.summary()
    print("\nDurata totale: %.1fs" % elapsed)

    # Latency gates (calibrate S200):
    # - P50 hard-fail: mediana sopra 1500ms = vera regressione user-facing
    # - Slow-ratio hard-fail: >30% sample > 5000ms = regressione sistemica
    # - P95 catastrofico: >12000ms = pipeline completely broken
    # - P95 > 2000ms = WARN-only (monitoring SLO, non release-blocker)
    warmup_skipped = 0
    effective_latencies = list(R.latencies)
    p50_val = 0
    p95_val = 0
    slow_ratio = 0.0
    if R.latencies:
        s_lat = sorted(R.latencies)
        p50_val = s_lat[len(s_lat) // 2]
        p95_val = s_lat[int(len(s_lat) * 0.95)]
        n_slow = sum(1 for x in R.latencies if x > LATENCY_SLOW_SAMPLE_MS)
        slow_ratio = n_slow / len(R.latencies)

        # Hard-fail 1: P50 mediana
        if p50_val > LATENCY_P50_HARD_FAIL_MS:
            R.FAIL("LATENCY", "P50", "P50=%dms > %dms hard-fail (regressione user-facing)" % (p50_val, LATENCY_P50_HARD_FAIL_MS))
            summary_ok = False

        # Hard-fail 2: slow-ratio
        if slow_ratio > LATENCY_SLOW_RATIO_HARD_FAIL:
            R.FAIL("LATENCY", "SLOW_RATIO", "%.0f%% sample > %dms (regressione sistemica)" % (slow_ratio * 100, LATENCY_SLOW_SAMPLE_MS))
            summary_ok = False

        # Hard-fail 3: P95 catastrofico (pipeline broken)
        if p95_val > LATENCY_P95_HARD_FAIL_MS:
            R.FAIL("LATENCY", "P95_CATASTROFICA", "P95=%dms > %dms (pipeline broken)" % (p95_val, LATENCY_P95_HARD_FAIL_MS))
            summary_ok = False

        # WARN-only: P95 sopra SLO target
        if p95_val > LATENCY_P95_WARN_MS and p95_val <= LATENCY_P95_HARD_FAIL_MS:
            R.WARN("LATENCY", "P95_SLO", "P95=%dms > target %dms (monitoring only)" % (p95_val, LATENCY_P95_WARN_MS))

    # JSON report machine-readable
    report = {
        "verdict": "PASS" if (summary_ok and R.fail == 0) else "FAIL",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "pipeline_url": URL,
        "pipeline_version": h.get("version", "?"),
        "duration_sec": round(elapsed, 1),
        "totals": {
            "ok": R.ok,
            "warn": R.warn,
            "fail": R.fail,
        },
        "by_vertical": dict(R.by_vertical),
        "latency": {},
        "tier1_verticals_core": sorted(VERTICALS.keys()),
        "tier2_verticals_extended": EXTENDED_VERTICALS,
    }
    if R.latencies:
        s_lat = sorted(R.latencies)
        report["latency"] = {
            "samples": len(s_lat),
            "avg_ms": round(sum(s_lat) / len(s_lat)),
            "p50_ms": round(s_lat[len(s_lat) // 2]),
            "p95_ms": round(s_lat[int(len(s_lat) * 0.95)]),
            "p99_ms": round(s_lat[int(len(s_lat) * 0.99)]),
            "max_ms": round(s_lat[-1]),
            "slow_sample_ratio": round(slow_ratio, 3),
            "slow_sample_threshold_ms": LATENCY_SLOW_SAMPLE_MS,
            "gates": {
                "p50_hard_fail_ms": LATENCY_P50_HARD_FAIL_MS,
                "slow_ratio_hard_fail": LATENCY_SLOW_RATIO_HARD_FAIL,
                "p95_catastrophic_ms": LATENCY_P95_HARD_FAIL_MS,
                "p95_slo_target_ms": LATENCY_P95_WARN_MS,
            },
        }

    # Failures detail
    report["failures"] = [
        line for line in R.log if line.startswith("FAIL")
    ]

    try:
        with open(opts["report_path"], "w") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print("\nReport JSON: %s" % opts["report_path"])
    except Exception as e:
        print("WARN: impossibile scrivere report: %s" % e)

    # Verdict + exit code
    print("\n" + "=" * 80)
    if report["verdict"] == "PASS":
        print("RELEASE GATE: ✅ PASS — Sara pronta per release")
        print("=" * 80)
        sys.exit(0)
    else:
        print("RELEASE GATE: ❌ FAIL — %d failure(s) — release BLOCCATA" % R.fail)
        print("=" * 80)
        sys.exit(1 if opts["strict"] else 0)


if __name__ == "__main__":
    main()
