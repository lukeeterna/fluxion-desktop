#!/usr/bin/env python3
"""
Seed Stress Fixtures (S216-P1)
==============================
Inserisce i clienti usati da test_sara_stress_per_verticale.py nel DB FLUXION
prima dello stress run, in modo che il booking flow procede lineare (cliente
gia' noto) invece di entrare in registering_phone / disambiguating_name.

Pattern identificato S214: BEAUTY/MEDICAL/PALESTRA WARN dominati da
`booking_keyword_miss` su `layer=L2_slot` quando fsm=registering_phone.

Idempotente: skip se (nome, cognome) gia' presente.
"""

import os
import sqlite3
import sys

# 13 clienti dal test stress (nome, cognome, telefono dummy unique, vertical_tag)
STRESS_CLIENTI = [
    # SALONE
    ("Marco",       "Rossi",     "3339000001", "stress:salone"),
    ("Luca",        "Verdi",     "3339000002", "stress:salone"),
    # AUTO
    ("Giuseppe",    "Ferrari",   "3339000003", "stress:auto"),
    ("Paolo",       "Neri",      "3339000004", "stress:auto"),
    ("Roberto",     "Colombo",   "3339000005", "stress:auto"),
    # MEDICAL
    ("Francesca",   "Russo",     "3339000006", "stress:medical"),
    ("Davide",      "Esposito",  "3339000007", "stress:medical"),
    # PALESTRA
    ("Simone",      "Conti",     "3339000008", "stress:palestra"),
    ("Chiara",      "Mancini",   "3339000009", "stress:palestra"),
    # BEAUTY
    ("Elena",       "Moretti",   "3339000010", "stress:beauty"),
    ("Sara",        "Romano",    "3339000011", "stress:beauty"),
    # STUDIO PROFESSIONALE
    ("Alessandro",  "Gentile",   "3339000012", "stress:studio"),
    ("Maria",       "Fontana",   "3339000013", "stress:studio"),
]


def resolve_db_path():
    # type: () -> str
    """Stessa logica di orchestrator.py:2879-2886."""
    db_path = os.environ.get("FLUXION_DB_PATH")
    if db_path and os.path.exists(db_path):
        return db_path
    home = os.path.expanduser("~")
    candidates = [
        os.path.join(home, "Library", "Application Support", "com.fluxion.desktop", "fluxion.db"),
        os.path.join(home, "Library", "Application Support", "fluxion", "fluxion.db"),
        "fluxion.db",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    raise RuntimeError("fluxion.db non trovato in %s" % candidates)


def seed_stress_clienti(verbose=False):
    # type: (bool) -> dict
    """
    Inserisce i clienti stress in fluxion.db, skip se gia' presenti (match
    case-insensitive su nome+cognome). Restituisce dict {inserted, skipped, errors}.
    """
    db_path = resolve_db_path()
    inserted = 0
    skipped = 0
    errors = []

    conn = sqlite3.connect(db_path, timeout=5)
    try:
        cur = conn.cursor()
        for nome, cognome, tel, tag in STRESS_CLIENTI:
            try:
                cur.execute(
                    "SELECT id FROM clienti WHERE LOWER(nome)=? AND LOWER(cognome)=? LIMIT 1",
                    (nome.lower(), cognome.lower()),
                )
                row = cur.fetchone()
                if row is not None:
                    skipped += 1
                    if verbose:
                        print("  [skip] %s %s (id=%s)" % (nome, cognome, row[0]))
                    continue
                cur.execute(
                    "INSERT INTO clienti (nome, cognome, telefono, note, fonte) VALUES (?, ?, ?, ?, ?)",
                    (nome, cognome, tel, tag, "stress-fixture"),
                )
                inserted += 1
                if verbose:
                    print("  [ins ] %s %s (tel=%s, tag=%s)" % (nome, cognome, tel, tag))
            except Exception as e:
                errors.append("%s %s: %s" % (nome, cognome, e))
        conn.commit()
    finally:
        conn.close()

    return {"db": db_path, "inserted": inserted, "skipped": skipped, "errors": errors,
            "total": len(STRESS_CLIENTI)}


if __name__ == "__main__":
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    print("=" * 70)
    print("Seed Stress Fixtures (S216-P1)")
    print("=" * 70)
    res = seed_stress_clienti(verbose=verbose)
    print("DB:       %s" % res["db"])
    print("Total:    %d clienti" % res["total"])
    print("Inserted: %d" % res["inserted"])
    print("Skipped:  %d (gia' presenti)" % res["skipped"])
    if res["errors"]:
        print("Errors:   %d" % len(res["errors"]))
        for e in res["errors"]:
            print("  - %s" % e)
        sys.exit(1)
    print("OK")
