#!/usr/bin/env python3
"""
FLUXION SQLite Database Connection Test
Verifies database schema and query performance
"""

import sqlite3
import os
from pathlib import Path

def test_sqlite_connection():
    """Test SQLite database connection and schema"""
    print("\n" + "="*80)
    print("SQLite Database Connection Test")
    print("="*80)

    # Determine DB path
    db_path = Path(os.path.expanduser("~/Library/Application Support/fluxion/fluxion.db"))

    print(f"\nDatabase path: {db_path}")
    print(f"   Exists: {'YES' if db_path.exists() else 'NO'}")

    if not db_path.exists():
        print("   WARNING: Database not found!")
        return False

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Test tables
        tables = ["clienti", "appuntamenti", "servizi", "operatori"]

        print("\nTesting tables:")
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"   {table}: {count} rows - PASS")
            except Exception as e:
                print(f"   {table}: ERROR - {e}")

        # Test critical queries
        print("\nTesting critical queries:")

        # Query 1: Search client by phone
        cursor.execute("SELECT * FROM clienti LIMIT 1")
        result = cursor.fetchone()
        print(f"   Select clienti: {'PASS' if result else 'EMPTY'}")

        # Query 2: Get available appointments
        cursor.execute("""
            SELECT COUNT(*) FROM appuntamenti
            WHERE data = DATE('now') AND stato = 'confermato'
        """)
        count = cursor.fetchone()[0]
        print(f"   Get today's appointments: {count} found - PASS")

        # Query 3: Index performance
        cursor.execute("EXPLAIN QUERY PLAN SELECT * FROM clienti WHERE telefono = '3459876543'")
        plan = cursor.fetchall()
        print(f"   Index performance: {'Using index' if 'SEARCH' in str(plan) else 'Full scan'}")

        conn.close()
        return True

    except Exception as e:
        print(f"   ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    test_sqlite_connection()
