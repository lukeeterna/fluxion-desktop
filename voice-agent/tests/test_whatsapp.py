"""
Tests for WhatsApp Integration Module.

Week 5: VOICE-AGENT-RAG.md implementation
Tests WhatsApp client, rate limiting, templates, and analytics.
"""

import asyncio
import json
import os
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.whatsapp import (
    WhatsAppConfig,
    WhatsAppClient,
    WhatsAppManager,
    WhatsAppMessage,
    WhatsAppRateLimiter,
    WhatsAppTemplates,
    ConnectionStatus,
    MessageDirection,
    PendingQuestion,
)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def whatsapp_config(temp_dir):
    """Create WhatsApp config for testing."""
    return WhatsAppConfig(
        fluxion_root=temp_dir,
        session_dir=temp_dir / ".whatsapp-session",
        rate_limit_per_minute=3,
        rate_limit_per_hour=30,
        rate_limit_per_day=200,
    )


@pytest.fixture
def whatsapp_client(whatsapp_config):
    """Create WhatsApp client for testing."""
    return WhatsAppClient(whatsapp_config)


@pytest.fixture
def rate_limiter():
    """Create rate limiter for testing."""
    return WhatsAppRateLimiter(per_minute=3, per_hour=30, per_day=200)


# =============================================================================
# WhatsAppConfig Tests
# =============================================================================

class TestWhatsAppConfig:
    """Tests for WhatsAppConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = WhatsAppConfig()
        assert config.auto_responder_enabled is True
        assert config.faq_category == "salone"
        assert config.rate_limit_per_minute == 3
        assert config.confidence_threshold == 0.5

    def test_config_paths(self, temp_dir):
        """Test path resolution."""
        config = WhatsAppConfig(
            fluxion_root=temp_dir,
            session_dir=temp_dir / ".whatsapp-session",
        )
        assert config.status_file == temp_dir / ".whatsapp-session" / "status.json"
        assert config.messages_log == temp_dir / ".whatsapp-session" / "messages.jsonl"
        assert config.pending_questions_file == temp_dir / ".whatsapp-session" / "pending_questions.jsonl"

    def test_service_path(self, temp_dir):
        """Test service path calculation."""
        config = WhatsAppConfig(fluxion_root=temp_dir)
        assert config.service_path == temp_dir / "scripts" / "whatsapp-service.cjs"


# =============================================================================
# WhatsAppMessage Tests
# =============================================================================

class TestWhatsAppMessage:
    """Tests for WhatsAppMessage dataclass."""

    def test_message_creation(self):
        """Test message creation."""
        msg = WhatsAppMessage(
            id="msg_123",
            phone="393281234567",
            name="Mario Rossi",
            body="Ciao, vorrei prenotare",
            direction=MessageDirection.INBOUND,
        )
        assert msg.id == "msg_123"
        assert msg.phone == "393281234567"
        assert msg.name == "Mario Rossi"
        assert msg.body == "Ciao, vorrei prenotare"
        assert msg.direction == MessageDirection.INBOUND

    def test_message_to_dict(self):
        """Test message serialization."""
        msg = WhatsAppMessage(
            id="msg_123",
            phone="393281234567",
            body="Test message",
        )
        data = msg.to_dict()
        assert data["id"] == "msg_123"
        assert data["phone"] == "393281234567"
        assert data["body"] == "Test message"
        assert "timestamp" in data

    def test_message_from_dict_inbound(self):
        """Test message deserialization for inbound."""
        data = {
            "from": "393281234567",
            "name": "Test User",
            "body": "Hello",
            "timestamp": "2025-01-10T10:00:00",
            "type": "received",
        }
        msg = WhatsAppMessage.from_dict(data)
        assert msg.phone == "393281234567"
        assert msg.name == "Test User"
        assert msg.body == "Hello"
        assert msg.direction == MessageDirection.INBOUND

    def test_message_from_dict_outbound(self):
        """Test message deserialization for outbound."""
        data = {
            "to": "393281234567",
            "body": "Response",
            "timestamp": "2025-01-10T10:00:00",
            "type": "sent",
            "confidence": 0.85,
        }
        msg = WhatsAppMessage.from_dict(data)
        assert msg.phone == "393281234567"
        assert msg.body == "Response"
        assert msg.direction == MessageDirection.OUTBOUND
        assert msg.confidence == 0.85


# =============================================================================
# PendingQuestion Tests
# =============================================================================

class TestPendingQuestion:
    """Tests for PendingQuestion dataclass."""

    def test_pending_question_from_dict(self):
        """Test pending question deserialization."""
        data = {
            "id": "pq_123",
            "question": "Quanto costa un taglio?",
            "fromPhone": "393281234567",
            "fromName": "Mario",
            "category": "salone",
            "timestamp": "2025-01-10T10:00:00",
            "status": "pending",
        }
        question = PendingQuestion.from_dict(data)
        assert question.id == "pq_123"
        assert question.question == "Quanto costa un taglio?"
        assert question.from_phone == "393281234567"
        assert question.status == "pending"

    def test_pending_question_with_response(self):
        """Test pending question with operator response."""
        data = {
            "id": "pq_456",
            "question": "Test question",
            "fromPhone": "393281234567",
            "fromName": "Test",
            "category": "salone",
            "timestamp": "2025-01-10T10:00:00",
            "status": "answered",
            "operatorResponse": "Test response",
            "responseTimestamp": "2025-01-10T10:30:00",
        }
        question = PendingQuestion.from_dict(data)
        assert question.status == "answered"
        assert question.operator_response == "Test response"


# =============================================================================
# WhatsAppRateLimiter Tests
# =============================================================================

class TestWhatsAppRateLimiter:
    """Tests for WhatsAppRateLimiter."""

    def test_initial_state(self, rate_limiter):
        """Test initial state allows sending."""
        assert rate_limiter.can_send() is True
        status = rate_limiter.get_status()
        assert status["can_send"] is True
        assert status["remaining"]["minute"] == 3

    def test_rate_limiting_per_minute(self, rate_limiter):
        """Test per-minute rate limiting."""
        # Send 3 messages (limit)
        for _ in range(3):
            assert rate_limiter.can_send() is True
            rate_limiter.record_sent()

        # 4th should be blocked
        assert rate_limiter.can_send() is False
        status = rate_limiter.get_status()
        assert status["remaining"]["minute"] == 0

    def test_rate_limiting_per_hour(self):
        """Test per-hour rate limiting."""
        limiter = WhatsAppRateLimiter(per_minute=100, per_hour=5, per_day=200)

        # Send 5 messages (hourly limit)
        for _ in range(5):
            assert limiter.can_send() is True
            limiter.record_sent()

        # 6th should be blocked
        assert limiter.can_send() is False
        status = limiter.get_status()
        assert status["remaining"]["hour"] == 0

    def test_rate_limit_reset(self, rate_limiter):
        """Test rate limit reset after time window."""
        # Exhaust minute limit
        for _ in range(3):
            rate_limiter.record_sent()

        assert rate_limiter.can_send() is False

        # Simulate time passing (reset minute counter)
        rate_limiter.reset_times["minute"] = time.time() - 61

        assert rate_limiter.can_send() is True

    def test_status_includes_all_periods(self, rate_limiter):
        """Test status includes all rate limit periods."""
        rate_limiter.record_sent()
        status = rate_limiter.get_status()

        assert "minute" in status["remaining"]
        assert "hour" in status["remaining"]
        assert "day" in status["remaining"]
        assert "minute" in status["next_reset"]


# =============================================================================
# WhatsAppTemplates Tests
# =============================================================================

class TestWhatsAppTemplates:
    """Tests for WhatsAppTemplates."""

    def test_conferma_template(self):
        """Test appointment confirmation template."""
        msg = WhatsAppTemplates.conferma(
            nome="Mario",
            servizio="Taglio",
            data="lunedì 15 gennaio",
            ora="10:00",
        )
        assert "Prenotazione Confermata" in msg
        assert "Mario" in msg
        assert "Taglio" in msg
        assert "lunedì 15 gennaio" in msg
        assert "10:00" in msg

    def test_conferma_with_operator(self):
        """Test confirmation with operator."""
        msg = WhatsAppTemplates.conferma(
            nome="Mario",
            servizio="Taglio",
            data="lunedì",
            ora="10:00",
            operatore="Laura",
        )
        assert "Laura" in msg
        assert "Con:" in msg

    def test_reminder_24h_template(self):
        """Test 24-hour reminder template."""
        msg = WhatsAppTemplates.reminder_24h(
            nome="Maria",
            servizio="Colore",
            data="martedì",
            ora="14:00",
        )
        assert "Promemoria" in msg
        assert "Maria" in msg
        assert "domani" in msg
        assert "OK" in msg
        assert "ANNULLA" in msg

    def test_reminder_2h_template(self):
        """Test 2-hour reminder template."""
        msg = WhatsAppTemplates.reminder_2h(nome="Paolo", ora="16:30")
        assert "tra poco" in msg
        assert "Paolo" in msg
        assert "16:30" in msg

    def test_cancellazione_template(self):
        """Test cancellation template."""
        msg = WhatsAppTemplates.cancellazione(
            nome="Anna",
            data="mercoledì 17 gennaio",
            ora="11:00",
        )
        assert "Cancellato" in msg
        assert "Anna" in msg
        assert "mercoledì 17 gennaio" in msg

    def test_benvenuto_template(self):
        """Test welcome template."""
        msg = WhatsAppTemplates.benvenuto(
            nome="Giuseppe",
            nome_attivita="Salone Bella",
        )
        assert "Benvenuto" in msg
        assert "Giuseppe" in msg
        assert "Salone Bella" in msg
        assert "PRENOTA" in msg

    def test_compleanno_template(self):
        """Test birthday template."""
        msg = WhatsAppTemplates.compleanno(nome="Lucia")
        assert "Auguri" in msg
        assert "Lucia" in msg

    def test_compleanno_with_discount(self):
        """Test birthday with discount."""
        msg = WhatsAppTemplates.compleanno(nome="Marco", sconto=15)
        assert "15%" in msg
        assert "sconto" in msg

    def test_menu_template(self):
        """Test menu template."""
        msg = WhatsAppTemplates.menu(nome="Sara")
        assert "Sara" in msg
        assert "PRENOTA" in msg
        assert "ANNULLA" in msg
        assert "ORARI" in msg
        assert "SERVIZI" in msg

    def test_no_info_template(self):
        """Test no information template."""
        msg = WhatsAppTemplates.no_info()
        assert "Non ho informazioni" in msg
        assert "team" in msg.lower()

    def test_error_template(self):
        """Test error template."""
        msg = WhatsAppTemplates.error()
        assert "problema tecnico" in msg


# =============================================================================
# WhatsAppClient Tests
# =============================================================================

class TestWhatsAppClient:
    """Tests for WhatsAppClient."""

    def test_client_initialization(self, whatsapp_client, whatsapp_config):
        """Test client initialization."""
        assert whatsapp_client.config == whatsapp_config
        assert whatsapp_client.templates is not None
        assert whatsapp_client.rate_limiter is not None

    def test_normalize_phone_with_prefix(self, whatsapp_client):
        """Test phone normalization with country prefix."""
        assert whatsapp_client.normalize_phone("+393281234567") == "393281234567"
        assert whatsapp_client.normalize_phone("393281234567") == "393281234567"

    def test_normalize_phone_without_prefix(self, whatsapp_client):
        """Test phone normalization without country prefix."""
        assert whatsapp_client.normalize_phone("3281234567") == "393281234567"
        assert whatsapp_client.normalize_phone("0281234567") == "39281234567"

    def test_normalize_phone_with_formatting(self, whatsapp_client):
        """Test phone normalization with formatting characters."""
        assert whatsapp_client.normalize_phone("+39 328 123 4567") == "393281234567"
        assert whatsapp_client.normalize_phone("328-123-4567") == "393281234567"

    def test_get_status_not_initialized(self, whatsapp_client):
        """Test status when not initialized."""
        status = whatsapp_client.get_status()
        assert status["status"] == ConnectionStatus.NOT_INITIALIZED.value

    def test_get_status_from_file(self, whatsapp_client, whatsapp_config):
        """Test reading status from file."""
        # Create status file
        whatsapp_config.session_dir.mkdir(parents=True, exist_ok=True)
        status_data = {
            "status": "ready",
            "phone": "393281234567",
            "timestamp": datetime.now().isoformat(),
        }
        with open(whatsapp_config.status_file, "w") as f:
            json.dump(status_data, f)

        status = whatsapp_client.get_status()
        assert status["status"] == "ready"
        assert status["phone"] == "393281234567"

    def test_is_connected(self, whatsapp_client, whatsapp_config):
        """Test connection check."""
        # Not connected initially
        assert whatsapp_client.is_connected() is False

        # Create ready status
        whatsapp_config.session_dir.mkdir(parents=True, exist_ok=True)
        with open(whatsapp_config.status_file, "w") as f:
            json.dump({"status": "ready"}, f)

        assert whatsapp_client.is_connected() is True

    def test_get_messages_empty(self, whatsapp_client):
        """Test getting messages when log is empty."""
        messages = whatsapp_client.get_messages()
        assert messages == []

    def test_get_messages_from_file(self, whatsapp_client, whatsapp_config):
        """Test reading messages from log file."""
        whatsapp_config.session_dir.mkdir(parents=True, exist_ok=True)

        # Create message log
        messages_data = [
            {"from": "393281111111", "name": "User1", "body": "Hello", "timestamp": "2025-01-10T10:00:00", "type": "received"},
            {"to": "393281111111", "body": "Hi!", "timestamp": "2025-01-10T10:01:00", "type": "sent"},
            {"from": "393282222222", "name": "User2", "body": "Test", "timestamp": "2025-01-10T10:02:00", "type": "received"},
        ]

        with open(whatsapp_config.messages_log, "w") as f:
            for msg in messages_data:
                f.write(json.dumps(msg) + "\n")

        messages = whatsapp_client.get_messages()
        assert len(messages) == 3

    def test_get_messages_with_since_filter(self, whatsapp_client, whatsapp_config):
        """Test filtering messages by time."""
        whatsapp_config.session_dir.mkdir(parents=True, exist_ok=True)

        messages_data = [
            {"from": "393281111111", "body": "Old", "timestamp": "2025-01-09T10:00:00", "type": "received"},
            {"from": "393281111111", "body": "New", "timestamp": "2025-01-11T10:00:00", "type": "received"},
        ]

        with open(whatsapp_config.messages_log, "w") as f:
            for msg in messages_data:
                f.write(json.dumps(msg) + "\n")

        since = datetime(2025, 1, 10)
        messages = whatsapp_client.get_messages(since=since)
        assert len(messages) == 1
        assert messages[0].body == "New"

    def test_get_pending_questions(self, whatsapp_client, whatsapp_config):
        """Test getting pending questions."""
        whatsapp_config.session_dir.mkdir(parents=True, exist_ok=True)

        questions = [
            {"id": "pq_1", "question": "Q1", "fromPhone": "123", "fromName": "User", "category": "test", "timestamp": "2025-01-10T10:00:00", "status": "pending"},
            {"id": "pq_2", "question": "Q2", "fromPhone": "456", "fromName": "User2", "category": "test", "timestamp": "2025-01-10T11:00:00", "status": "answered"},
            {"id": "pq_3", "question": "Q3", "fromPhone": "789", "fromName": "User3", "category": "test", "timestamp": "2025-01-10T12:00:00", "status": "pending"},
        ]

        with open(whatsapp_config.pending_questions_file, "w") as f:
            for q in questions:
                f.write(json.dumps(q) + "\n")

        pending = whatsapp_client.get_pending_questions()
        assert len(pending) == 2  # Only pending status

    def test_send_message_rate_limited(self, whatsapp_client, whatsapp_config):
        """Test send message when rate limited."""
        # Exhaust rate limit
        for _ in range(3):
            whatsapp_client.rate_limiter.record_sent()

        result = whatsapp_client.send_message("393281234567", "Test")
        assert result["success"] is False
        assert "Rate limit" in result["error"]

    def test_send_message_not_connected(self, whatsapp_client):
        """Test send message when not connected."""
        result = whatsapp_client.send_message("393281234567", "Test")
        assert result["success"] is False
        assert "not connected" in result["error"]

    def test_get_config_empty(self, whatsapp_client):
        """Test getting config when file doesn't exist."""
        config = whatsapp_client.get_config()
        assert config == {}

    def test_update_config(self, whatsapp_client, whatsapp_config):
        """Test updating config."""
        whatsapp_config.session_dir.mkdir(parents=True, exist_ok=True)

        whatsapp_client.update_config(faqCategory="medical", maxResponsesPerHour=100)

        config = whatsapp_client.get_config()
        assert config["faqCategory"] == "medical"
        assert config["maxResponsesPerHour"] == 100

    def test_enable_disable_auto_responder(self, whatsapp_client, whatsapp_config):
        """Test enabling/disabling auto-responder."""
        whatsapp_config.session_dir.mkdir(parents=True, exist_ok=True)

        whatsapp_client.enable_auto_responder()
        assert whatsapp_client.get_config()["autoResponderEnabled"] is True

        whatsapp_client.disable_auto_responder()
        assert whatsapp_client.get_config()["autoResponderEnabled"] is False

    def test_set_faq_category(self, whatsapp_client, whatsapp_config):
        """Test setting FAQ category."""
        whatsapp_config.session_dir.mkdir(parents=True, exist_ok=True)

        whatsapp_client.set_faq_category("wellness")

        assert whatsapp_client.get_config()["faqCategory"] == "wellness"
        assert whatsapp_client.config.faq_category == "wellness"


# =============================================================================
# WhatsAppManager Tests
# =============================================================================

class TestWhatsAppManager:
    """Tests for WhatsAppManager."""

    def test_manager_initialization(self, whatsapp_config):
        """Test manager initialization."""
        manager = WhatsAppManager(whatsapp_config)
        assert manager.client is not None
        assert manager._running is False

    def test_set_pipeline(self, whatsapp_config):
        """Test setting pipeline."""
        manager = WhatsAppManager(whatsapp_config)
        mock_pipeline = MagicMock()

        manager.set_pipeline(mock_pipeline)

        assert manager.client._pipeline == mock_pipeline

    @pytest.mark.asyncio
    async def test_start_not_connected(self, whatsapp_config):
        """Test start fails when not connected."""
        manager = WhatsAppManager(whatsapp_config)

        result = await manager.start()

        assert result is False
        assert manager._running is False

    @pytest.mark.asyncio
    async def test_start_connected(self, whatsapp_config):
        """Test start succeeds when connected."""
        whatsapp_config.session_dir.mkdir(parents=True, exist_ok=True)
        with open(whatsapp_config.status_file, "w") as f:
            json.dump({"status": "ready"}, f)

        manager = WhatsAppManager(whatsapp_config)

        result = await manager.start()

        assert result is True
        assert manager._running is True

        await manager.stop()

    @pytest.mark.asyncio
    async def test_stop(self, whatsapp_config):
        """Test stop."""
        whatsapp_config.session_dir.mkdir(parents=True, exist_ok=True)
        with open(whatsapp_config.status_file, "w") as f:
            json.dump({"status": "ready"}, f)

        manager = WhatsAppManager(whatsapp_config)
        await manager.start()

        await manager.stop()

        assert manager._running is False

    def test_get_status(self, whatsapp_config):
        """Test get status."""
        whatsapp_config.session_dir.mkdir(parents=True, exist_ok=True)

        # Write pending question
        with open(whatsapp_config.pending_questions_file, "w") as f:
            f.write(json.dumps({"id": "1", "question": "Q", "fromPhone": "123", "fromName": "U", "category": "t", "timestamp": "2025-01-01T00:00:00", "status": "pending"}) + "\n")

        manager = WhatsAppManager(whatsapp_config)
        status = manager.get_status()

        assert "connected" in status
        assert "running" in status
        assert "rate_limit" in status
        assert status["pending_questions"] == 1


# =============================================================================
# Analytics Integration Tests
# =============================================================================

class TestWhatsAppAnalytics:
    """Tests for WhatsApp analytics integration."""

    def test_analytics_logger_has_whatsapp_methods(self):
        """Test that analytics logger has WhatsApp methods."""
        from src.analytics import ConversationLogger

        assert hasattr(ConversationLogger, "log_whatsapp_message")
        assert hasattr(ConversationLogger, "get_whatsapp_metrics")

    def test_log_whatsapp_message(self, temp_dir):
        """Test logging WhatsApp message."""
        from src.analytics import ConversationLogger

        logger = ConversationLogger(db_path=str(temp_dir / "test.db"))

        msg_id = logger.log_whatsapp_message(
            phone="393281234567",
            body="Test message",
            direction="inbound",
            name="Mario Rossi",
        )

        assert msg_id is not None

    def test_get_whatsapp_metrics(self, temp_dir):
        """Test getting WhatsApp metrics."""
        from src.analytics import ConversationLogger

        logger = ConversationLogger(db_path=str(temp_dir / "test.db"))

        # Log some messages
        logger.log_whatsapp_message(phone="123", body="In1", direction="inbound")
        logger.log_whatsapp_message(phone="123", body="Out1", direction="outbound")
        logger.log_whatsapp_message(phone="456", body="In2", direction="inbound", passed_to_operator=True)

        metrics = logger.get_whatsapp_metrics()

        assert metrics["total_messages"] == 3
        assert metrics["inbound_messages"] == 2
        assert metrics["outbound_messages"] == 1
        assert metrics["escalated_messages"] == 1
        assert metrics["unique_contacts"] == 2


# =============================================================================
# Connection Status Tests
# =============================================================================

class TestConnectionStatus:
    """Tests for ConnectionStatus enum."""

    def test_all_statuses(self):
        """Test all connection statuses."""
        assert ConnectionStatus.NOT_INITIALIZED.value == "not_initialized"
        assert ConnectionStatus.READY.value == "ready"
        assert ConnectionStatus.WAITING_QR.value == "waiting_qr"
        assert ConnectionStatus.DISCONNECTED.value == "disconnected"
        assert ConnectionStatus.ERROR.value == "error"


# =============================================================================
# Message Direction Tests
# =============================================================================

class TestMessageDirection:
    """Tests for MessageDirection enum."""

    def test_directions(self):
        """Test message directions."""
        assert MessageDirection.INBOUND.value == "inbound"
        assert MessageDirection.OUTBOUND.value == "outbound"


# =============================================================================
# Integration Test
# =============================================================================

class TestWhatsAppIntegration:
    """Integration tests for WhatsApp module."""

    @pytest.mark.asyncio
    async def test_full_flow_with_mock_pipeline(self, whatsapp_config, temp_dir):
        """Test full message flow with mocked pipeline."""
        whatsapp_config.session_dir.mkdir(parents=True, exist_ok=True)

        # Setup connected status
        with open(whatsapp_config.status_file, "w") as f:
            json.dump({"status": "ready"}, f)

        # Create client
        client = WhatsAppClient(whatsapp_config)

        # Mock pipeline
        mock_pipeline = MagicMock()
        mock_pipeline.process_input = AsyncMock(return_value="Ciao! Come posso aiutarti?")
        mock_pipeline.last_intent_result = MagicMock(
            confidence=0.85,
            intent="greeting",
            layer_used="L1_exact",
        )
        client.set_pipeline(mock_pipeline)

        # Create incoming message
        msg = WhatsAppMessage(
            phone="393281234567",
            name="Mario",
            body="Ciao",
            direction=MessageDirection.INBOUND,
        )

        # Process message
        response = await client.process_message(msg, verticale_id="test")

        assert response == "Ciao! Come posso aiutarti?"
        mock_pipeline.process_input.assert_called_once()

    def test_template_send_flow(self, whatsapp_config):
        """Test template send flow."""
        whatsapp_config.session_dir.mkdir(parents=True, exist_ok=True)

        client = WhatsAppClient(whatsapp_config)

        # Template generation works even without connection
        result = client.send_template(
            "393281234567",
            "conferma",
            nome="Mario",
            servizio="Taglio",
            data="lunedì",
            ora="10:00",
        )

        # Will fail because not connected, but template was generated
        assert result["success"] is False
        assert "not connected" in result["error"]

    def test_unknown_template(self, whatsapp_config):
        """Test unknown template error."""
        client = WhatsAppClient(whatsapp_config)

        result = client.send_template("393281234567", "nonexistent_template")

        assert result["success"] is False
        assert "Unknown template" in result["error"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
