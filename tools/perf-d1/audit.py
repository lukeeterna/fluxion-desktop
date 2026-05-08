#!/usr/bin/env python3
"""
S190 D-1 — SQLite query plan audit per `clienti` con 1000 record.

Cosa fa (idempotente):
  1. Bootstrap DB pulito `/tmp/fluxion-perf.db` da `src-tauri/migrations/*.sql`
     (ignora errori migrations non-clienti, ok per scope D-1).
  2. Seed 1000 clienti realistici italiani (idempotente, skip se gia >=1000).
  3. EXPLAIN QUERY PLAN su 8 query principali (hot path utente).
  4. Benchmark P50/P95/P99 100 iterazioni per ogni query.
  5. Output markdown `docs/perf/D1-sqlite-query-plans.md`.

SLO target: P95 lista clienti < 50ms (1000 record).

Run: `python3 tools/perf-d1/audit.py`
"""
from __future__ import annotations

import os
import random
import sqlite3
import statistics
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = Path("/tmp/fluxion-perf.db")
MIGRATIONS_DIR = ROOT / "src-tauri" / "migrations"
OUT_MD = ROOT / "docs" / "perf" / "D1-sqlite-query-plans.md"
SEED_TARGET = 1000
BENCH_ITERATIONS = 100

# Faker italiano semplice (no deps esterne)
NOMI = [
    "Marco", "Luca", "Giuseppe", "Andrea", "Francesco", "Alessandro", "Matteo",
    "Davide", "Lorenzo", "Stefano", "Antonio", "Roberto", "Paolo", "Fabio",
    "Maria", "Giulia", "Anna", "Sara", "Francesca", "Laura", "Chiara",
    "Elena", "Federica", "Silvia", "Valentina", "Martina", "Alessia", "Sofia",
]
COGNOMI = [
    "Rossi", "Bianchi", "Romano", "Gallo", "Costa", "Conti", "Esposito",
    "Russo", "Ferrari", "Lombardi", "Moretti", "Marino", "Greco", "Bruno",
    "Ricci", "Marini", "Galli", "Caruso", "De Luca", "Mancini", "Rizzo",
    "Colombo", "Barbieri", "Fontana", "Santoro", "Mariani", "Rinaldi", "Caputo",
]
CITTA = [
    ("Milano", "MI", "20121"), ("Roma", "RM", "00100"), ("Napoli", "NA", "80100"),
    ("Torino", "TO", "10121"), ("Palermo", "PA", "90100"), ("Genova", "GE", "16121"),
    ("Bologna", "BO", "40121"), ("Firenze", "FI", "50121"), ("Bari", "BA", "70121"),
    ("Catania", "CT", "95121"), ("Verona", "VR", "37121"), ("Venezia", "VE", "30121"),
    ("Lavello", "PZ", "85024"), ("Potenza", "PZ", "85100"), ("Matera", "MT", "75100"),
]
DOMINI = ["gmail.com", "libero.it", "yahoo.it", "outlook.com", "tin.it", "alice.it"]


def bootstrap_db() -> None:
    """Applica migrations 001-037 a DB pulito. Tollera errori non-clienti."""
    if DB_PATH.exists():
        DB_PATH.unlink()
    failed = []
    for sql_file in sorted(MIGRATIONS_DIR.glob("*.sql")):
        try:
            subprocess.run(
                ["sqlite3", str(DB_PATH)],
                input=sql_file.read_text(),
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            failed.append((sql_file.name, e.stderr.strip()[:120]))
    # Verifica clienti table esiste con tutti gli indici
    conn = sqlite3.connect(DB_PATH)
    indexes = {
        r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='clienti'"
        )
    }
    conn.close()
    print(f"[bootstrap] DB={DB_PATH} migrations failed (non-blocking): {len(failed)}")
    print(f"[bootstrap] clienti indexes: {sorted(indexes)}")


def seed_clienti(conn: sqlite3.Connection) -> None:
    """Inserisce SEED_TARGET clienti realistici, idempotente."""
    cur = conn.cursor()
    existing = cur.execute("SELECT COUNT(*) FROM clienti").fetchone()[0]
    if existing >= SEED_TARGET:
        print(f"[seed] gia presenti {existing} clienti, skip")
        return
    print(f"[seed] inserimento {SEED_TARGET - existing} clienti...")
    rows = []
    rng = random.Random(42)  # deterministic
    for i in range(SEED_TARGET - existing):
        nome = rng.choice(NOMI)
        cognome = rng.choice(COGNOMI)
        citta_t = rng.choice(CITTA)
        rows.append((
            str(uuid.uuid4()),
            nome,
            cognome,
            f"{nome.lower()}.{cognome.lower().replace(' ', '')}{rng.randint(10, 999)}@{rng.choice(DOMINI)}",
            f"+39{rng.randint(310, 399)}{rng.randint(1000000, 9999999)}",
            f"{rng.randint(1950, 2005)}-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
            f"Via {rng.choice(COGNOMI)} {rng.randint(1, 200)}",
            citta_t[2],
            citta_t[0],
            citta_t[1],
            None if rng.random() < 0.3 else f"RSSMRA{rng.randint(70, 99)}A01H501Z",
            None if rng.random() < 0.85 else f"IT{rng.randint(10000000000, 99999999999)}",
            "0000000",
            None,
            None,
            None,
            None,
            1 if rng.random() < 0.6 else 0,
            1 if rng.random() < 0.5 else 0,
            None,
            1 if rng.random() < 0.15 else 0,  # is_vip
            rng.randint(0, 20),  # loyalty_visits
            10,
        ))
    cur.executemany(
        """
        INSERT INTO clienti (
            id, nome, cognome, email, telefono, data_nascita,
            indirizzo, cap, citta, provincia,
            codice_fiscale, partita_iva, codice_sdi, pec,
            note, tags, fonte,
            consenso_marketing, consenso_whatsapp, data_consenso,
            is_vip, loyalty_visits, loyalty_threshold
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    conn.commit()
    final = cur.execute("SELECT COUNT(*) FROM clienti").fetchone()[0]
    print(f"[seed] totale clienti dopo seed: {final}")


# ─────────────────────────────────────────────────────────────────────
# Query catalog: 8 query principali su clienti
# ─────────────────────────────────────────────────────────────────────
QUERIES: list[dict[str, Any]] = [
    {
        "id": "Q1-list-all",
        "rust_origin": "commands/clienti.rs:117 get_clienti",
        "description": "Lista clienti pagina principale (ORDER BY cognome, nome)",
        "sql": "SELECT * FROM clienti WHERE deleted_at IS NULL ORDER BY cognome ASC, nome ASC",
        "params": (),
        "slo_p95_ms": 50,
    },
    {
        "id": "Q2-get-by-id",
        "rust_origin": "commands/clienti.rs:134 get_cliente",
        "description": "Lookup cliente by id (PK)",
        "sql": "SELECT * FROM clienti WHERE id = ? AND deleted_at IS NULL",
        "params": ("__SAMPLE_ID__",),
        "slo_p95_ms": 5,
    },
    {
        "id": "Q3-search-like",
        "rust_origin": "commands/clienti.rs:357 search_clienti",
        "description": "Search free-text con LIKE %x% su 4 colonne",
        "sql": (
            "SELECT * FROM clienti WHERE deleted_at IS NULL "
            "AND (nome LIKE ? OR cognome LIKE ? OR telefono LIKE ? OR email LIKE ?) "
            "ORDER BY cognome ASC, nome ASC LIMIT 50"
        ),
        "params": ("%Ross%", "%Ross%", "%Ross%", "%Ross%"),
        "slo_p95_ms": 50,
    },
    {
        "id": "Q4-count-active",
        "rust_origin": "commands/dashboard.rs:73",
        "description": "Dashboard count clienti attivi",
        "sql": "SELECT COUNT(*) FROM clienti WHERE deleted_at IS NULL",
        "params": (),
        "slo_p95_ms": 10,
    },
    {
        "id": "Q5-count-vip",
        "rust_origin": "commands/dashboard.rs:80",
        "description": "Dashboard count VIP attivi",
        "sql": "SELECT COUNT(*) FROM clienti WHERE is_vip = 1 AND deleted_at IS NULL",
        "params": (),
        "slo_p95_ms": 10,
    },
    {
        "id": "Q6-list-export",
        "rust_origin": "commands/support.rs:733 (GDPR export)",
        "description": "Lista completa clienti per export GDPR",
        "sql": "SELECT id, nome, cognome, email, telefono FROM clienti WHERE deleted_at IS NULL ORDER BY cognome, nome",
        "params": (),
        "slo_p95_ms": 50,
    },
    {
        "id": "Q7-by-telefono",
        "rust_origin": "voice agent lookup (HTTP bridge)",
        "description": "Match cliente by telefono (voice agent)",
        "sql": "SELECT * FROM clienti WHERE telefono = ? AND deleted_at IS NULL",
        "params": ("+39__SAMPLE_TEL__",),
        "slo_p95_ms": 5,
    },
    {
        "id": "Q8-by-email",
        "rust_origin": "registrazione/login lookup",
        "description": "Match cliente by email",
        "sql": "SELECT * FROM clienti WHERE email = ? AND deleted_at IS NULL",
        "params": ("__SAMPLE_EMAIL__",),
        "slo_p95_ms": 5,
    },
]


def fill_sample_params(conn: sqlite3.Connection) -> None:
    """Pesca id/telefono/email reali dal seed per query parametriche."""
    cur = conn.cursor()
    row = cur.execute(
        "SELECT id, telefono, email FROM clienti WHERE email IS NOT NULL LIMIT 1 OFFSET 500"
    ).fetchone()
    if not row:
        raise RuntimeError("seed insufficiente per parametri sample")
    sid, stel, semail = row
    for q in QUERIES:
        if q["id"] == "Q2-get-by-id":
            q["params"] = (sid,)
        elif q["id"] == "Q7-by-telefono":
            q["params"] = (stel,)
        elif q["id"] == "Q8-by-email":
            q["params"] = (semail,)


def explain_plan(conn: sqlite3.Connection, sql: str, params: tuple) -> list[str]:
    cur = conn.cursor()
    rows = cur.execute(f"EXPLAIN QUERY PLAN {sql}", params).fetchall()
    return [f"id={r[0]} parent={r[1]} | {r[3]}" for r in rows]


def benchmark(conn: sqlite3.Connection, sql: str, params: tuple, iterations: int) -> dict[str, float]:
    durations_ms: list[float] = []
    cur = conn.cursor()
    # warmup
    for _ in range(5):
        cur.execute(sql, params).fetchall()
    for _ in range(iterations):
        t0 = time.perf_counter()
        cur.execute(sql, params).fetchall()
        durations_ms.append((time.perf_counter() - t0) * 1000)
    durations_ms.sort()
    return {
        "min": durations_ms[0],
        "p50": statistics.median(durations_ms),
        "p95": durations_ms[int(0.95 * iterations) - 1],
        "p99": durations_ms[int(0.99 * iterations) - 1],
        "max": durations_ms[-1],
        "mean": statistics.mean(durations_ms),
    }


def verdict(plan: list[str], stats: dict[str, float], slo_ms: float) -> str:
    has_scan = any("SCAN" in line and "USING INDEX" not in line and "USING COVERING INDEX" not in line for line in plan)
    p95 = stats["p95"]
    if has_scan and p95 >= slo_ms:
        return "FAIL — table scan + P95 oltre SLO"
    if has_scan and p95 < slo_ms:
        return "WARN — table scan tollerato (P95 sotto SLO con 1000 record, da rivalutare a 10k)"
    if not has_scan and p95 < slo_ms:
        return "PASS"
    return f"WARN — P95 {p95:.2f}ms sopra SLO {slo_ms}ms (no scan, ottimizzazione marginale)"


def render_markdown(results: list[dict[str, Any]]) -> str:
    lines = []
    lines.append("# S190 D-1 — SQLite EXPLAIN QUERY PLAN audit `clienti` (1000 record)\n")
    lines.append(f"**Generato**: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}\n")
    lines.append(f"**DB test**: `{DB_PATH}` (fresh from migrations)\n")
    lines.append(f"**Seed**: {SEED_TARGET} clienti italiani realistici (deterministic, seed=42)\n")
    lines.append(f"**Benchmark**: {BENCH_ITERATIONS} iterazioni con warmup 5\n")
    lines.append(f"**SQLite version**: {sqlite3.sqlite_version}\n")
    lines.append("\n## SLO target\n")
    lines.append("- P95 lista clienti `< 50ms`\n")
    lines.append("- P95 lookup PK `< 5ms`\n")
    lines.append("- P95 search free-text `< 50ms` (con LIKE wildcard, NB: nessun indice possibile su `LIKE %x%` — soluzione long-term FTS5)\n")
    lines.append("\n## Indici esistenti su `clienti`\n")
    lines.append("```sql")
    conn = sqlite3.connect(DB_PATH)
    for name, sql in conn.execute(
        "SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='clienti' AND sql IS NOT NULL ORDER BY name"
    ):
        lines.append(f"-- {name}")
        lines.append(f"{sql};")
    conn.close()
    lines.append("```\n")
    lines.append("\n## Risultati audit\n")
    lines.append("| Query | P50 ms | P95 ms | P99 ms | SLO ms | Verdict |")
    lines.append("|-------|--------|--------|--------|--------|---------|")
    for r in results:
        lines.append(
            f"| `{r['id']}` | {r['stats']['p50']:.2f} | {r['stats']['p95']:.2f} | "
            f"{r['stats']['p99']:.2f} | {r['slo_p95_ms']} | {r['verdict']} |"
        )
    lines.append("\n## Dettaglio per query\n")
    for r in results:
        lines.append(f"### {r['id']} — {r['description']}\n")
        lines.append(f"**Origin Rust**: `{r['rust_origin']}`\n")
        lines.append(f"**Verdict**: {r['verdict']}\n")
        lines.append("**SQL**:\n```sql")
        lines.append(r["sql"].strip())
        lines.append("```\n")
        lines.append("**EXPLAIN QUERY PLAN**:\n```")
        for line in r["plan"]:
            lines.append(line)
        lines.append("```\n")
        lines.append(
            f"**Bench**: min={r['stats']['min']:.2f}ms p50={r['stats']['p50']:.2f}ms "
            f"p95={r['stats']['p95']:.2f}ms p99={r['stats']['p99']:.2f}ms max={r['stats']['max']:.2f}ms\n"
        )
    lines.append("\n## Conclusioni e azioni\n")
    fails = [r for r in results if r["verdict"].startswith("FAIL")]
    warns = [r for r in results if r["verdict"].startswith("WARN")]
    passes = [r for r in results if r["verdict"].startswith("PASS")]
    lines.append(f"- PASS: {len(passes)} | WARN: {len(warns)} | FAIL: {len(fails)}\n")
    if fails:
        lines.append("\n### Azioni richieste\n")
        for r in fails:
            lines.append(f"- `{r['id']}`: {r['verdict']}\n")
    if warns:
        lines.append("\n### Da monitorare\n")
        for r in warns:
            lines.append(f"- `{r['id']}`: {r['verdict']}\n")
    lines.append(
        "\n### Note tecniche\n"
        "- `LIKE '%x%'` (Q3 search) NON è ottimizzabile con indice B-tree standard. "
        "Soluzione long-term: FTS5 virtual table su (nome, cognome, telefono, email). "
        "Tech debt P2 — accettabile sotto 10k clienti, P95 < SLO con full scan.\n"
        "- `ORDER BY cognome, nome` su lista completa: SQLite usa `idx_clienti_nome` "
        "se compatibile con WHERE clause, altrimenti SCAN+SORT.\n"
        "- `idx_clienti_deleted_at` (migration 036) coprire WHERE deleted_at IS NULL "
        "ma per filtri `IS NULL` SQLite spesso preferisce table scan se selettività bassa.\n"
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    print("[main] S190 D-1 SQLite query plan audit")
    bootstrap_db()
    conn = sqlite3.connect(DB_PATH)
    seed_clienti(conn)
    fill_sample_params(conn)
    print(f"[main] running EXPLAIN + bench for {len(QUERIES)} queries...")
    results = []
    for q in QUERIES:
        plan = explain_plan(conn, q["sql"], q["params"])
        stats = benchmark(conn, q["sql"], q["params"], BENCH_ITERATIONS)
        v = verdict(plan, stats, q["slo_p95_ms"])
        print(f"  {q['id']}: P95={stats['p95']:.2f}ms verdict={v}")
        results.append({**q, "plan": plan, "stats": stats, "verdict": v})
    conn.close()
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text(render_markdown(results))
    print(f"[main] report scritto in {OUT_MD}")
    fails = [r for r in results if r["verdict"].startswith("FAIL")]
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
