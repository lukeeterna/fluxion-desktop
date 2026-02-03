"""Test suite per AuditClient.

Run: python -m pytest tests/test_audit_client.py -v
"""

import sys
import os
import sqlite3
import tempfile
import json
from datetime import datetime, timedelta

# Add parent dir to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from audit_client import (
    AuditClient, AuditAction, GdprCategory, UserType, AuditSource,
    audit_client
)


class TestAuditClient:
    """Test suite per AuditClient."""
    
    @classmethod
    def setup_class(cls):
        """Setup: create temp database."""
        cls.temp_dir = tempfile.mkdtemp()
        cls.db_path = os.path.join(cls.temp_dir, "test_audit.db")
        
        # Create DB with audit_log table
        conn = sqlite3.connect(cls.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                user_id TEXT,
                user_type TEXT,
                action TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                data_before TEXT,
                data_after TEXT,
                changed_fields TEXT,
                gdpr_category TEXT,
                source TEXT,
                legal_basis TEXT,
                retention_until TEXT,
                notes TEXT
            )
        """)
        conn.commit()
        conn.close()
        
        cls.client = AuditClient(db_path=cls.db_path)
    
    @classmethod
    def teardown_class(cls):
        """Cleanup: remove temp database."""
        import shutil
        shutil.rmtree(cls.temp_dir, ignore_errors=True)
    
    def test_log_client_creation(self):
        """Test logging client creation."""
        audit_id = self.client.log_client_creation(
            session_id="test-session-123",
            cliente_id="cust-456",
            cliente_data={
                "nome": "Mario",
                "cognome": "Rossi",
                "telefono": "+391234567890"
            }
        )
        
        assert audit_id is not None
        assert len(audit_id) == 36  # UUID format
        
        # Verify in DB
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM audit_log WHERE id = ?", (audit_id,)
        ).fetchone()
        conn.close()
        
        assert row is not None
        assert row["action"] == "CREATE"
        assert row["entity_type"] == "cliente"
        assert row["entity_id"] == "cust-456"
        assert row["gdpr_category"] == "personal_data"
        assert row["legal_basis"] == "consent"
        
        # Verify phone masking
        data_after = json.loads(row["data_after"])
        assert "******" in data_after["telefono"]
    
    def test_log_booking_creation(self):
        """Test logging booking creation."""
        audit_id = self.client.log_booking_creation(
            session_id="test-session-123",
            appuntamento_id="booking-789",
            booking_data={
                "cliente_id": "cust-456",
                "servizio": "Taglio",
                "data": "2025-03-15",
                "ora": "15:00"
            }
        )
        
        assert audit_id is not None
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM audit_log WHERE id = ?", (audit_id,)
        ).fetchone()
        conn.close()
        
        assert row["action"] == "CREATE"
        assert row["entity_type"] == "appuntamento"
        assert row["gdpr_category"] == "booking"
        assert row["legal_basis"] == "contract"
    
    def test_log_consent_update(self):
        """Test logging consent update."""
        audit_id = self.client.log_consent_update(
            session_id="test-session-123",
            cliente_id="cust-456",
            consenso_marketing=True,
            consenso_whatsapp=True,
            consenso_sms=False
        )
        
        assert audit_id is not None
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM audit_log WHERE id = ?", (audit_id,)
        ).fetchone()
        conn.close()
        
        assert row["action"] == "UPDATE"
        assert row["entity_type"] == "consenso"
        assert row["gdpr_category"] == "consent"
        
        data_after = json.loads(row["data_after"])
        assert data_after["consenso_marketing"] is True
        assert data_after["consenso_whatsapp"] is True
        assert data_after["consenso_sms"] is False
    
    def test_log_booking_cancellation(self):
        """Test logging booking cancellation."""
        audit_id = self.client.log_booking_cancellation(
            session_id="test-session-123",
            appuntamento_id="booking-789",
            booking_data={
                "servizio": "Taglio",
                "data": "2025-03-15",
                "ora": "15:00"
            }
        )
        
        assert audit_id is not None
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM audit_log WHERE id = ?", (audit_id,)
        ).fetchone()
        conn.close()
        
        assert row["action"] == "DELETE"
        assert row["entity_type"] == "appuntamento"
    
    def test_log_session_lifecycle(self):
        """Test logging session start and end."""
        session_id = "test-session-lifecycle"
        
        # Start session
        start_audit_id = self.client.log_session_start(
            session_id=session_id,
            phone_number="+391234567890",
            verticale_id="salone_test"
        )
        assert start_audit_id is not None
        
        # End session
        end_audit_id = self.client.log_session_end(
            session_id=session_id,
            outcome="completed",
            turns_count=12
        )
        assert end_audit_id is not None
        
        # Verify both in DB
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM audit_log WHERE entity_id = ? ORDER BY timestamp",
            (session_id,)
        ).fetchall()
        conn.close()
        
        assert len(rows) == 2
        assert rows[0]["action"] == "CREATE"  # Session start
        assert rows[1]["action"] == "UPDATE"  # Session end
        end_data = json.loads(rows[1]["data_after"])
        assert end_data["outcome"] == "completed"
    
    def test_retention_calculation(self):
        """Test retention days calculation."""
        # Test with no DB settings (should use defaults)
        days_personal = self.client._get_retention_days(GdprCategory.PERSONAL_DATA)
        days_consent = self.client._get_retention_days(GdprCategory.CONSENT)
        days_booking = self.client._get_retention_days(GdprCategory.BOOKING)
        
        assert days_personal == 2555  # 7 years
        assert days_consent == 1825   # 5 years
        assert days_booking == 1095   # 3 years
    
    def test_data_diff_calculation(self):
        """Test changed fields calculation."""
        before = {"nome": "Mario", "cognome": "Rossi", "telefono": "123"}
        after = {"nome": "Mario", "cognome": "Bianchi", "telefono": "456"}
        
        diff = self.client._calculate_diff(before, after)
        
        assert "cognome" in diff
        assert "telefono" in diff
        assert "nome" not in diff
    
    def test_phone_masking(self):
        """Test phone number masking."""
        phone1 = self.client._mask_phone("+391234567890")
        phone2 = self.client._mask_phone("1234567890")
        
        # Should mask all but last 4 digits
        assert phone1.endswith("7890")
        assert "*" in phone1
        assert phone2.endswith("7890")
    
    def test_email_masking(self):
        """Test email masking."""
        email1 = self.client._mask_email("mario.rossi@example.com")
        email2 = self.client._mask_email("a@test.org")
        
        assert email1 == "m***@example.com"
        assert email2 == "a***@test.org"
    
    def test_thread_safety(self):
        """Test thread-safe connection handling."""
        import threading
        
        results = []
        
        def log_in_thread():
            audit_id = self.client.log_operation(
                session_id="thread-test",
                action=AuditAction.VIEW,
                entity_type="test",
                entity_id="test-1"
            )
            results.append(audit_id)
        
        # Spawn multiple threads
        threads = [threading.Thread(target=log_in_thread) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All should succeed
        assert len(results) == 5
        assert all(r is not None for r in results)
    
    def test_singleton_instance(self):
        """Test singleton audit_client instance."""
        from audit_client import audit_client as singleton_client
        
        assert singleton_client is not None
        assert isinstance(singleton_client, AuditClient)


class TestAuditClientIntegration:
    """Integration tests with mock orchestrator context."""
    
    @classmethod
    def setup_class(cls):
        """Setup temp database."""
        cls.temp_dir = tempfile.mkdtemp()
        cls.db_path = os.path.join(cls.temp_dir, "test_integration.db")
        
        conn = sqlite3.connect(cls.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                user_id TEXT,
                user_type TEXT,
                action TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                data_before TEXT,
                data_after TEXT,
                changed_fields TEXT,
                gdpr_category TEXT,
                source TEXT,
                legal_basis TEXT,
                retention_until TEXT,
                notes TEXT
            )
        """)
        conn.commit()
        conn.close()
        
        cls.client = AuditClient(db_path=cls.db_path)
    
    @classmethod
    def teardown_class(cls):
        """Cleanup."""
        import shutil
        shutil.rmtree(cls.temp_dir, ignore_errors=True)
    
    def test_reschedule_audit(self):
        """Test complete reschedule flow audit."""
        old_data = {
            "data": "2025-03-15",
            "ora": "15:00",
            "servizio": "Taglio"
        }
        new_data = {
            "data": "2025-03-20",
            "ora": "16:00",
            "servizio": "Taglio"
        }
        
        audit_id = self.client.log_booking_reschedule(
            session_id="session-reschedule",
            appuntamento_id="booking-123",
            old_data=old_data,
            new_data=new_data
        )
        
        assert audit_id is not None
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM audit_log WHERE id = ?", (audit_id,)
        ).fetchone()
        conn.close()
        
        assert row["action"] == "UPDATE"
        assert row["entity_type"] == "appuntamento"
        
        data_before = json.loads(row["data_before"])
        data_after = json.loads(row["data_after"])
        
        assert data_before["data"] == "2025-03-15"
        assert data_after["data"] == "2025-03-20"
    
    def test_client_view_audit(self):
        """Test client view audit."""
        audit_id = self.client.log_client_view(
            session_id="session-view",
            cliente_id="cust-789",
            search_query="Rossi"
        )
        
        assert audit_id is not None
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM audit_log WHERE id = ?", (audit_id,)
        ).fetchone()
        conn.close()
        
        assert row["action"] == "VIEW"
        assert row["entity_type"] == "cliente"
        assert "Rossi" in row["notes"]


def test_with_real_db_path():
    """Test that default DB path works (if DB exists)."""
    # This test only verifies the client can be instantiated
    # It doesn't require the actual DB to exist
    client = AuditClient(db_path="/tmp/nonexistent_test.db")
    assert client.db_path == "/tmp/nonexistent_test.db"


if __name__ == "__main__":
    # Run tests with pytest if available, else basic runner
    try:
        import pytest
        pytest.main([__file__, "-v"])
    except ImportError:
        print("Running basic test runner...")
        
        test = TestAuditClient()
        test.setup_class()
        
        tests = [
            test.test_log_client_creation,
            test.test_log_booking_creation,
            test.test_log_consent_update,
            test.test_log_booking_cancellation,
            test.test_log_session_lifecycle,
            test.test_retention_calculation,
            test.test_data_diff_calculation,
            test.test_phone_masking,
            test.test_email_masking,
            test.test_thread_safety,
            test.test_singleton_instance,
        ]
        
        passed = 0
        failed = 0
        
        for t in tests:
            try:
                t()
                print(f"✓ {t.__name__}")
                passed += 1
            except Exception as e:
                print(f"✗ {t.__name__}: {e}")
                failed += 1
        
        test.teardown_class()
        
        print(f"\nResults: {passed} passed, {failed} failed")
