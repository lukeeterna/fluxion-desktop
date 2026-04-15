"""
FLUXION Sales Agent WA — CLI principale.
Uso: python3 agent.py [init|scrape|send|dashboard|stats|pause|resume|next-week]
"""
from __future__ import annotations

import argparse
import logging
import sqlite3
import sys
from pathlib import Path

from config import DB_PATH, WA_SESSION_DIR, LOG_DIR, DEFAULT_DAILY_LIMIT

# Setup logging
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(str(LOG_DIR / "agent.log")),
    ],
)
logger = logging.getLogger(__name__)


def init_db():
    """Crea le tabelle SQLite se non esistono."""
    WA_SESSION_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))

    schema = """
    CREATE TABLE IF NOT EXISTS leads (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        business_name   TEXT NOT NULL,
        phone           TEXT,
        phone_raw       TEXT,
        address         TEXT,
        city            TEXT,
        province        TEXT,
        category        TEXT NOT NULL,
        source          TEXT NOT NULL,
        source_id       TEXT,
        website         TEXT,
        google_rating   REAL,
        google_reviews  INTEGER,
        wa_registered   INTEGER DEFAULT NULL,
        scraped_at      TEXT NOT NULL DEFAULT (datetime('now')),
        notes           TEXT,
        UNIQUE(phone_raw)
    );
    CREATE TABLE IF NOT EXISTS messages (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        lead_id         INTEGER NOT NULL REFERENCES leads(id),
        campaign_id     INTEGER,
        template_key    TEXT NOT NULL,
        message_text    TEXT NOT NULL,
        utm_url         TEXT NOT NULL,
        status          TEXT NOT NULL DEFAULT 'pending',
        sent_at         TEXT,
        delivered_at    TEXT,
        read_at         TEXT,
        replied_at      TEXT,
        reply_text      TEXT,
        error_msg       TEXT,
        created_at      TEXT NOT NULL DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS campaigns (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        name            TEXT NOT NULL,
        category        TEXT NOT NULL,
        city            TEXT,
        status          TEXT NOT NULL DEFAULT 'active',
        daily_limit     INTEGER NOT NULL DEFAULT 10,
        delay_min_s     INTEGER NOT NULL DEFAULT 60,
        delay_max_s     INTEGER NOT NULL DEFAULT 180,
        started_at      TEXT NOT NULL DEFAULT (datetime('now')),
        paused_at       TEXT,
        notes           TEXT
    );
    CREATE TABLE IF NOT EXISTS daily_stats (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        date            TEXT NOT NULL,
        sent            INTEGER NOT NULL DEFAULT 0,
        delivered       INTEGER NOT NULL DEFAULT 0,
        read_count      INTEGER NOT NULL DEFAULT 0,
        replied         INTEGER NOT NULL DEFAULT 0,
        failed          INTEGER NOT NULL DEFAULT 0,
        blocked         INTEGER NOT NULL DEFAULT 0,
        UNIQUE(date)
    );
    CREATE TABLE IF NOT EXISTS agent_state (
        key             TEXT PRIMARY KEY,
        value           TEXT NOT NULL,
        updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
    );
    CREATE INDEX IF NOT EXISTS idx_messages_status  ON messages(status);
    CREATE INDEX IF NOT EXISTS idx_messages_sent_at ON messages(sent_at);
    CREATE INDEX IF NOT EXISTS idx_leads_category   ON leads(category);
    CREATE INDEX IF NOT EXISTS idx_leads_city       ON leads(city);
    CREATE INDEX IF NOT EXISTS idx_leads_wa         ON leads(wa_registered);
    """

    conn.executescript(schema)

    conn.execute("""
        INSERT OR IGNORE INTO agent_state (key, value) VALUES
        ('status', 'active')
    """)
    conn.execute("""
        INSERT OR IGNORE INTO agent_state (key, value) VALUES
        ('daily_limit', ?)
    """, (str(DEFAULT_DAILY_LIMIT),))
    conn.execute("""
        INSERT OR IGNORE INTO agent_state (key, value) VALUES
        ('week_number', '1')
    """)
    conn.execute("""
        INSERT OR IGNORE INTO agent_state (key, value) VALUES
        ('total_sent_ever', '0')
    """)
    conn.commit()
    conn.close()
    logger.info("DB inizializzato: %s", DB_PATH)


def cmd_init(args):
    init_db()
    print("Database inizializzato: {}".format(DB_PATH))
    print("Sessione WA directory: {}".format(WA_SESSION_DIR))
    print("\nProssimi passi:")
    print("  1. python3 agent.py scrape --category parrucchiere --city milano")
    print("  2. python3 agent.py send --dry-run  (testa senza inviare)")
    print("  3. python3 agent.py send            (invia messaggi reali)")


def cmd_scrape(args):
    init_db()
    from scraper import scrape_all_sources

    categories = args.category.split(",") if args.category else ["parrucchiere"]
    cities = args.city.split(",") if args.city else ["milano"]

    total = 0
    for cat in categories:
        for city in cities:
            n = scrape_all_sources(cat.strip(), city.strip())
            total += n
            print("  {}/{}: {} nuovi lead".format(cat, city, n))

    print("\nTotale nuovi lead aggiunti: {}".format(total))
    print("DB: {}".format(DB_PATH))


def cmd_send(args):
    init_db()
    from sender import run_sender

    conn = sqlite3.connect(str(DB_PATH))
    state = conn.execute(
        "SELECT value FROM agent_state WHERE key = 'status'"
    ).fetchone()
    conn.close()

    if state and state[0] == "paused":
        print("Agent in PAUSA. Usa 'resume' per ripartire.")
        return

    conn = sqlite3.connect(str(DB_PATH))
    week_row = conn.execute(
        "SELECT value FROM agent_state WHERE key = 'week_number'"
    ).fetchone()
    conn.close()

    from config import WARMUP_SCHEDULE
    week_num = int(week_row[0]) if week_row else 1
    limit = args.limit or WARMUP_SCHEDULE.get(week_num, DEFAULT_DAILY_LIMIT)

    print("Invio messaggi - settimana {}, limite {}/giorno".format(week_num, limit))
    run_sender(
        daily_limit=limit,
        category=args.category,
        dry_run=args.dry_run,
    )


def cmd_dashboard(args):
    from dashboard import run_dashboard
    run_dashboard()


def cmd_stats(args):
    init_db()
    conn = sqlite3.connect(str(DB_PATH))

    print("\n=== FLUXION Sales Agent - Stats ===\n")

    total_leads = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
    total_with_phone = conn.execute(
        "SELECT COUNT(*) FROM leads WHERE phone IS NOT NULL"
    ).fetchone()[0]
    total_sent = conn.execute(
        "SELECT COUNT(*) FROM messages WHERE status NOT IN ('pending', 'failed')"
    ).fetchone()[0]
    total_replied = conn.execute(
        "SELECT COUNT(*) FROM messages WHERE status = 'replied'"
    ).fetchone()[0]
    total_failed = conn.execute(
        "SELECT COUNT(*) FROM messages WHERE status = 'failed'"
    ).fetchone()[0]

    print("Lead totali:          {}".format(total_leads))
    print("  con telefono:       {}".format(total_with_phone))
    print("Messaggi inviati:     {}".format(total_sent))
    print("Risposte ricevute:    {}".format(total_replied))
    print("Falliti (no WA):      {}".format(total_failed))

    if total_sent > 0:
        print("\nReply rate:           {:.1f}%".format(total_replied / total_sent * 100))

    print("\n--- Per categoria ---")
    rows = conn.execute("""
        SELECT category, COUNT(*) as n
        FROM leads GROUP BY category ORDER BY n DESC
    """).fetchall()
    for r in rows:
        print("  {:20s}: {} lead".format(r[0], r[1]))

    print("\n--- Ultimi 7 giorni ---")
    rows = conn.execute("""
        SELECT date, sent, replied, blocked
        FROM daily_stats
        ORDER BY date DESC LIMIT 7
    """).fetchall()
    for r in rows:
        print("  {}: {} inviati, {} risposte, {} blocked".format(r[0], r[1], r[2], r[3]))

    conn.close()


def cmd_pause(args):
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        INSERT OR REPLACE INTO agent_state (key, value, updated_at)
        VALUES ('status', 'paused', datetime('now'))
    """)
    conn.commit()
    conn.close()
    print("Agent in PAUSA. Usa 'resume' per ripartire.")


def cmd_resume(args):
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        INSERT OR REPLACE INTO agent_state (key, value, updated_at)
        VALUES ('status', 'active', datetime('now'))
    """)
    conn.commit()
    conn.close()
    print("Agent ATTIVO. Prossima esecuzione al prossimo orario operativo.")


def cmd_monitor(args):
    init_db()
    from monitor import run_monitor
    run_monitor(loop=args.loop)


def cmd_advance_week(args):
    """Avanza la settimana di warm-up (aumenta limite giornaliero)."""
    conn = sqlite3.connect(str(DB_PATH))
    row = conn.execute(
        "SELECT value FROM agent_state WHERE key = 'week_number'"
    ).fetchone()
    current = int(row[0]) if row else 1
    new_week = min(current + 1, 6)

    from config import WARMUP_SCHEDULE
    new_limit = WARMUP_SCHEDULE.get(new_week, DEFAULT_DAILY_LIMIT)

    conn.execute("""
        INSERT OR REPLACE INTO agent_state (key, value, updated_at)
        VALUES ('week_number', ?, datetime('now'))
    """, (str(new_week),))
    conn.execute("""
        INSERT OR REPLACE INTO agent_state (key, value, updated_at)
        VALUES ('daily_limit', ?, datetime('now'))
    """, (str(new_limit),))
    conn.commit()
    conn.close()
    print("Settimana avanzata a {} - limite giornaliero: {} msg/giorno".format(
        new_week, new_limit))


def main():
    parser = argparse.ArgumentParser(
        description="FLUXION Sales Agent WhatsApp",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Comandi disponibili:
  init          Inizializza database e directory
  scrape        Scarica lead dalle directory italiane
  send          Invia messaggi WhatsApp ai lead
  monitor       Scansiona WA per risposte ricevute
  dashboard     Avvia dashboard web (http://127.0.0.1:5050)
  stats         Mostra statistiche da terminale
  pause         Mette in pausa l'invio
  resume        Riprende l'invio
  next-week     Avanza settimana di warm-up (aumenta limite)

Esempi:
  python3 agent.py init
  python3 agent.py scrape --category parrucchiere --city milano,torino,roma
  python3 agent.py scrape --category officina,estetico --city roma,napoli,torino
  python3 agent.py send --dry-run
  python3 agent.py send --limit 5
  python3 agent.py monitor
  python3 agent.py monitor --loop
  python3 agent.py dashboard
  python3 agent.py stats
        """,
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("init", help="Inizializza database")

    p_scrape = subparsers.add_parser("scrape", help="Scraping lead")
    p_scrape.add_argument("--category", default="parrucchiere",
        help="Categoria: parrucchiere,officina,estetico,palestra,dentista,generico")
    p_scrape.add_argument("--city", default="milano",
        help="Citta (virgola-separated): milano,roma,torino")

    p_send = subparsers.add_parser("send", help="Invia messaggi WA")
    p_send.add_argument("--category", default=None, help="Filtra per categoria")
    p_send.add_argument("--limit", type=int, default=None, help="Override limite giornaliero")
    p_send.add_argument("--dry-run", action="store_true", help="Test senza inviare")

    p_monitor = subparsers.add_parser("monitor", help="Scansiona WA per risposte")
    p_monitor.add_argument("--loop", action="store_true",
        help="Ripeti ogni 15 minuti (daemon)")

    subparsers.add_parser("dashboard", help="Avvia dashboard web")
    subparsers.add_parser("stats", help="Statistiche da terminale")
    subparsers.add_parser("pause", help="Pausa invio")
    subparsers.add_parser("resume", help="Riprendi invio")
    subparsers.add_parser("next-week", help="Avanza settimana warm-up")

    args = parser.parse_args()

    if args.command == "init":         cmd_init(args)
    elif args.command == "scrape":     cmd_scrape(args)
    elif args.command == "send":       cmd_send(args)
    elif args.command == "monitor":    cmd_monitor(args)
    elif args.command == "dashboard":  cmd_dashboard(args)
    elif args.command == "stats":      cmd_stats(args)
    elif args.command == "pause":      cmd_pause(args)
    elif args.command == "resume":     cmd_resume(args)
    elif args.command == "next-week":  cmd_advance_week(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
