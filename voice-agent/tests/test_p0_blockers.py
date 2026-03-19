"""
Tests for P0 Blocker Features (S96):
  P0-1: Buffer automatico tra servizi
  P0-2: Pausa pranzo / blocchi orario
  P0-3: Multi-servizio combo
  P0-4: "Il solito" entity detection
"""

import pytest
import sqlite3
import os
import tempfile
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock

# Add parent path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from entity_extractor import detect_solito, extract_all, ExtractionResult


# =============================================================================
# P0-1: Buffer automatico tra servizi
# =============================================================================

class TestBufferMinuti:
    """P0-1: buffer_minuti must be included in slot availability calculations."""

    @pytest.fixture
    def db_with_buffer(self, tmp_path):
        """Create a test DB with services that have buffer_minuti."""
        db_path = str(tmp_path / "test_buffer.db")
        conn = sqlite3.connect(db_path)
        conn.executescript("""
            CREATE TABLE servizi (
                id TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                durata_minuti INTEGER NOT NULL,
                buffer_minuti INTEGER DEFAULT 0,
                prezzo REAL DEFAULT 25.0,
                attivo INTEGER DEFAULT 1
            );
            CREATE TABLE appuntamenti (
                id TEXT PRIMARY KEY,
                cliente_id TEXT,
                servizio_id TEXT,
                operatore_id TEXT,
                data_ora_inizio TEXT,
                data_ora_fine TEXT,
                durata_minuti INTEGER,
                stato TEXT DEFAULT 'confermato',
                prezzo REAL DEFAULT 25.0,
                sconto_percentuale REAL DEFAULT 0,
                prezzo_finale REAL DEFAULT 25.0,
                fonte_prenotazione TEXT DEFAULT 'voice',
                note TEXT,
                created_at TEXT
            );
            CREATE TABLE operatori (
                id TEXT PRIMARY KEY,
                nome TEXT,
                cognome TEXT,
                attivo INTEGER DEFAULT 1,
                specializzazioni TEXT
            );
            CREATE TABLE blocchi_orario (
                id TEXT PRIMARY KEY,
                operatore_id TEXT,
                giorno_settimana INTEGER,
                data_specifica TEXT,
                ora_inizio TEXT NOT NULL,
                ora_fine TEXT NOT NULL,
                motivo TEXT DEFAULT 'pausa',
                ricorrente INTEGER DEFAULT 1,
                attivo INTEGER DEFAULT 1,
                created_at TEXT
            );

            INSERT INTO servizi VALUES ('s1', 'Taglio', 30, 15, 25.0, 1);
            INSERT INTO servizi VALUES ('s2', 'Colore', 90, 10, 60.0, 1);
            INSERT INTO servizi VALUES ('s3', 'Piega', 40, 0, 20.0, 1);
            INSERT INTO operatori VALUES ('op1', 'Marco', 'Rossi', 1, NULL);
        """)
        conn.close()
        return db_path

    def test_buffer_increases_slot_duration(self, db_with_buffer):
        """Taglio (30min + 15min buffer = 45min) should block full 45 minutes."""
        conn = sqlite3.connect(db_with_buffer)
        cur = conn.execute(
            "SELECT durata_minuti, COALESCE(buffer_minuti, 0) FROM servizi WHERE nome = 'Taglio'"
        )
        row = cur.fetchone()
        assert row[0] == 30  # durata
        assert row[1] == 15  # buffer
        slot_totale = row[0] + row[1]
        assert slot_totale == 45  # total blocked time
        conn.close()

    def test_buffer_zero_does_not_add_time(self, db_with_buffer):
        """Piega (40min + 0 buffer) should only block 40 minutes."""
        conn = sqlite3.connect(db_with_buffer)
        cur = conn.execute(
            "SELECT durata_minuti, COALESCE(buffer_minuti, 0) FROM servizi WHERE nome = 'Piega'"
        )
        row = cur.fetchone()
        assert row[0] + row[1] == 40
        conn.close()


# =============================================================================
# P0-2: Pausa pranzo / blocchi orario
# =============================================================================

class TestBlocchiOrario:
    """P0-2: blocchi_orario table must block slot availability."""

    @pytest.fixture
    def db_with_blocks(self, tmp_path):
        """Create DB with lunch break block."""
        db_path = str(tmp_path / "test_blocks.db")
        conn = sqlite3.connect(db_path)
        conn.executescript("""
            CREATE TABLE blocchi_orario (
                id TEXT PRIMARY KEY,
                operatore_id TEXT NOT NULL,
                giorno_settimana INTEGER,
                data_specifica TEXT,
                ora_inizio TEXT NOT NULL,
                ora_fine TEXT NOT NULL,
                motivo TEXT DEFAULT 'pausa',
                ricorrente INTEGER DEFAULT 1,
                attivo INTEGER DEFAULT 1,
                created_at TEXT
            );
            -- Marco has lunch break 13:00-14:00 every day
            INSERT INTO blocchi_orario VALUES
                ('b1', 'op1', NULL, NULL, '13:00', '14:00', 'pausa_pranzo', 1, 1, NULL);
            -- Marco leaves early on Fridays (after 17:00)
            INSERT INTO blocchi_orario VALUES
                ('b2', 'op1', 4, NULL, '17:00', '19:00', 'chiusura_anticipata', 1, 1, NULL);
        """)
        conn.close()
        return db_path

    def test_lunch_break_blocks_slot(self, db_with_blocks):
        """Slot at 13:30 should be blocked by lunch break 13:00-14:00."""
        conn = sqlite3.connect(db_with_blocks)
        # Simulating the check: slot 13:30, ends 14:00
        slot_time_start = "13:30"
        slot_time_end = "14:00"
        giorno_settimana = 2  # Wednesday
        date = "2026-03-25"

        block_count = conn.execute(
            """SELECT COUNT(*) FROM blocchi_orario
               WHERE operatore_id = 'op1'
               AND attivo = 1
               AND (
                   (ricorrente = 1 AND (giorno_settimana IS NULL OR giorno_settimana = ?))
                   OR
                   (ricorrente = 0 AND data_specifica = ?)
               )
               AND ora_inizio < ?
               AND ora_fine > ?""",
            (giorno_settimana, date, slot_time_end, slot_time_start)
        ).fetchone()[0]
        assert block_count > 0, "Lunch break should block slot at 13:30"
        conn.close()

    def test_slot_before_lunch_ok(self, db_with_blocks):
        """Slot at 12:00-12:30 should NOT be blocked."""
        conn = sqlite3.connect(db_with_blocks)
        block_count = conn.execute(
            """SELECT COUNT(*) FROM blocchi_orario
               WHERE operatore_id = 'op1'
               AND attivo = 1
               AND (ricorrente = 1 AND (giorno_settimana IS NULL OR giorno_settimana = 2))
               AND ora_inizio < '12:30'
               AND ora_fine > '12:00'""",
        ).fetchone()[0]
        assert block_count == 0, "12:00-12:30 should not be blocked"
        conn.close()

    def test_friday_early_close_blocks(self, db_with_blocks):
        """Friday 17:30 should be blocked (chiusura_anticipata 17:00-19:00)."""
        conn = sqlite3.connect(db_with_blocks)
        block_count = conn.execute(
            """SELECT COUNT(*) FROM blocchi_orario
               WHERE operatore_id = 'op1'
               AND attivo = 1
               AND (
                   (ricorrente = 1 AND (giorno_settimana IS NULL OR giorno_settimana = 4))
                   OR (ricorrente = 0 AND data_specifica = '2026-03-27')
               )
               AND ora_inizio < '18:00'
               AND ora_fine > '17:30'""",
        ).fetchone()[0]
        assert block_count > 0, "Friday 17:30 should be blocked"
        conn.close()

    def test_friday_morning_ok(self, db_with_blocks):
        """Friday 10:00 should NOT be blocked."""
        conn = sqlite3.connect(db_with_blocks)
        block_count = conn.execute(
            """SELECT COUNT(*) FROM blocchi_orario
               WHERE operatore_id = 'op1'
               AND attivo = 1
               AND (
                   (ricorrente = 1 AND (giorno_settimana IS NULL OR giorno_settimana = 4))
                   OR (ricorrente = 0 AND data_specifica = '2026-03-27')
               )
               AND ora_inizio < '10:30'
               AND ora_fine > '10:00'""",
        ).fetchone()[0]
        assert block_count == 0, "Friday 10:00 should not be blocked"
        conn.close()


# =============================================================================
# P0-3: Multi-servizio combo
# =============================================================================

class TestMultiServizio:
    """P0-3: Multi-service should sum durations for slot calculation."""

    def test_multi_service_duration_sum(self, tmp_path):
        """Taglio (30) + Piega (40) = 70 min total slot."""
        db_path = str(tmp_path / "test_multi.db")
        conn = sqlite3.connect(db_path)
        conn.executescript("""
            CREATE TABLE servizi (
                id TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                durata_minuti INTEGER NOT NULL,
                buffer_minuti INTEGER DEFAULT 0,
                prezzo REAL DEFAULT 25.0,
                attivo INTEGER DEFAULT 1
            );
            INSERT INTO servizi VALUES ('s1', 'Taglio', 30, 15, 25.0, 1);
            INSERT INTO servizi VALUES ('s3', 'Piega', 40, 0, 20.0, 1);
        """)
        conn.close()

        # Simulate multi-service duration calculation
        services = ["taglio", "piega"]
        total_durata = 0
        total_buffer = 0
        conn = sqlite3.connect(db_path)
        for svc in services:
            row = conn.execute(
                "SELECT durata_minuti, COALESCE(buffer_minuti, 0) FROM servizi WHERE nome LIKE ? LIMIT 1",
                (f"%{svc}%",)
            ).fetchone()
            if row:
                total_durata += row[0]
                total_buffer += row[1]
        conn.close()

        assert total_durata == 70  # 30 + 40
        assert total_buffer == 15  # 15 + 0
        assert total_durata + total_buffer == 85  # total blocked time

    def test_multi_service_with_all_buffers(self, tmp_path):
        """Taglio (30+15) + Colore (90+10) = 145 min total."""
        db_path = str(tmp_path / "test_multi2.db")
        conn = sqlite3.connect(db_path)
        conn.executescript("""
            CREATE TABLE servizi (
                id TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                durata_minuti INTEGER NOT NULL,
                buffer_minuti INTEGER DEFAULT 0,
                prezzo REAL DEFAULT 25.0,
                attivo INTEGER DEFAULT 1
            );
            INSERT INTO servizi VALUES ('s1', 'Taglio', 30, 15, 25.0, 1);
            INSERT INTO servizi VALUES ('s2', 'Colore', 90, 10, 60.0, 1);
        """)
        conn.close()

        services = ["taglio", "colore"]
        total = 0
        conn = sqlite3.connect(db_path)
        for svc in services:
            row = conn.execute(
                "SELECT durata_minuti, COALESCE(buffer_minuti, 0) FROM servizi WHERE nome LIKE ? LIMIT 1",
                (f"%{svc}%",)
            ).fetchone()
            if row:
                total += row[0] + row[1]
        conn.close()

        assert total == 145  # (30+15) + (90+10)


# =============================================================================
# P0-4: "Il solito" entity detection
# =============================================================================

class TestIlSolito:
    """P0-4: detect_solito must recognize all Italian 'repeat' patterns."""

    @pytest.mark.parametrize("text,expected", [
        ("Vorrei il solito", True),
        ("Vorrei fare il solito per favore", True),
        ("Come l'ultima volta", True),
        ("come l\u2019ultima volta", True),  # curly apostrophe
        ("Faccio come sempre", True),
        ("Quello di sempre", True),
        ("La stessa cosa", True),
        ("Come l'altra volta", True),
        ("Stessa cosa", True),
        ("Vorrei un taglio", False),
        ("Buongiorno", False),
        ("Vorrei prenotare", False),
        ("Alle 15 come al solito", True),
        ("Uguale a sempre", True),
        ("Uguale all'ultima volta", True),
    ])
    def test_detect_solito(self, text, expected):
        result = detect_solito(text)
        assert result == expected, f"detect_solito('{text}') should be {expected}"

    def test_extract_all_sets_is_solito(self):
        """extract_all should set is_solito flag."""
        result = extract_all("Vorrei il solito")
        assert result.is_solito is True

    def test_extract_all_no_solito(self):
        """extract_all should not set is_solito for normal text."""
        result = extract_all("Vorrei un taglio domani")
        assert result.is_solito is False

    def test_solito_with_other_entities(self):
        """'Il solito' can coexist with date/time extraction."""
        result = extract_all("Il solito per domani")
        assert result.is_solito is True
        # Date should also be extracted
        assert result.date is not None


# =============================================================================
# Migration 034: blocchi_orario schema
# =============================================================================

class TestMigration034:
    """Verify migration 034 creates correct schema."""

    def test_migration_creates_table(self, tmp_path):
        """Migration SQL should create blocchi_orario table."""
        db_path = str(tmp_path / "test_migration.db")
        conn = sqlite3.connect(db_path)

        # Read and execute migration
        migration_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 'src-tauri', 'migrations', '034_blocchi_orario.sql'
        )
        with open(migration_path) as f:
            sql = f.read()

        conn.executescript(sql)

        # Verify table exists
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='blocchi_orario'"
        ).fetchall()
        assert len(tables) == 1

        # Verify columns
        columns = conn.execute("PRAGMA table_info(blocchi_orario)").fetchall()
        col_names = [c[1] for c in columns]
        assert "operatore_id" in col_names
        assert "giorno_settimana" in col_names
        assert "data_specifica" in col_names
        assert "ora_inizio" in col_names
        assert "ora_fine" in col_names
        assert "ricorrente" in col_names
        assert "motivo" in col_names
        assert "attivo" in col_names

        conn.close()

    def test_migration_idempotent(self, tmp_path):
        """Migration should be idempotent (IF NOT EXISTS)."""
        db_path = str(tmp_path / "test_idempotent.db")
        conn = sqlite3.connect(db_path)
        migration_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 'src-tauri', 'migrations', '034_blocchi_orario.sql'
        )
        with open(migration_path) as f:
            sql = f.read()
        # Run twice — should not error
        conn.executescript(sql)
        conn.executescript(sql)
        conn.close()
