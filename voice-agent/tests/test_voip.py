"""
Tests for FLUXION Voice Agent VoIP Module (Week 4).

Tests SIP client, RTP transport, and VoIP manager.
"""

import asyncio
import os
import pytest
import struct
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch

from src.voip import (
    SIPConfig,
    SIPClient,
    SIPMessage,
    RTPTransport,
    VoIPManager,
    CallSession,
    CallState,
    CallDirection,
)
from src.analytics import ConversationLogger


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def sip_config():
    """Create test SIP configuration."""
    return SIPConfig(
        server="test.sip.server",
        port=5060,
        username="testuser",
        password="testpass",
        local_ip="127.0.0.1",
        local_port=15060,
    )


@pytest.fixture
def sip_client(sip_config):
    """Create SIP client with test config."""
    return SIPClient(sip_config)


@pytest.fixture
def temp_db():
    """Create temporary database for analytics."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    yield db_path
    os.unlink(db_path)


@pytest.fixture
def logger(temp_db):
    """Create analytics logger with temp database."""
    return ConversationLogger(db_path=temp_db)


# =============================================================================
# SIPConfig Tests
# =============================================================================

class TestSIPConfig:
    """Tests for SIPConfig dataclass."""

    def test_default_values(self):
        """Test default configuration values."""
        config = SIPConfig()
        assert config.server == "sip.ehiweb.it"
        assert config.port == 5060
        assert config.transport == "udp"
        assert "PCMU" in config.codecs
        assert "PCMA" in config.codecs

    def test_custom_values(self):
        """Test custom configuration."""
        config = SIPConfig(
            server="custom.server",
            port=5080,
            username="user",
            password="pass"
        )
        assert config.server == "custom.server"
        assert config.port == 5080
        assert config.username == "user"

    def test_from_env(self):
        """Test loading from environment variables."""
        with patch.dict(os.environ, {
            "VOIP_SIP_SERVER": "env.server",
            "VOIP_SIP_PORT": "5070",
            "VOIP_SIP_USER": "envuser",
            "VOIP_SIP_PASSWORD": "envpass"
        }):
            config = SIPConfig.from_env()
            assert config.server == "env.server"
            assert config.port == 5070
            assert config.username == "envuser"
            assert config.password == "envpass"


# =============================================================================
# SIPMessage Tests
# =============================================================================

class TestSIPMessage:
    """Tests for SIP message parsing and building."""

    def test_parse_register_request(self):
        """Test parsing REGISTER request."""
        data = (
            b"REGISTER sip:test.server SIP/2.0\r\n"
            b"Via: SIP/2.0/UDP 192.168.1.1:5060;branch=z9hG4bK776\r\n"
            b"From: <sip:user@test.server>;tag=abc123\r\n"
            b"To: <sip:user@test.server>\r\n"
            b"Call-ID: 12345@192.168.1.1\r\n"
            b"CSeq: 1 REGISTER\r\n"
            b"Contact: <sip:user@192.168.1.1:5060>\r\n"
            b"Content-Length: 0\r\n"
            b"\r\n"
        )
        msg = SIPMessage.parse(data)

        assert msg.is_request
        assert msg.method == "REGISTER"
        assert msg.uri == "sip:test.server"
        assert "Via" in msg.headers
        assert "From" in msg.headers
        assert msg.body == ""

    def test_parse_200_ok_response(self):
        """Test parsing 200 OK response."""
        data = (
            b"SIP/2.0 200 OK\r\n"
            b"Via: SIP/2.0/UDP 192.168.1.1:5060;branch=z9hG4bK776\r\n"
            b"From: <sip:user@test.server>;tag=abc123\r\n"
            b"To: <sip:user@test.server>;tag=def456\r\n"
            b"Call-ID: 12345@192.168.1.1\r\n"
            b"CSeq: 1 REGISTER\r\n"
            b"Contact: <sip:user@192.168.1.1:5060>\r\n"
            b"Content-Length: 0\r\n"
            b"\r\n"
        )
        msg = SIPMessage.parse(data)

        assert not msg.is_request
        assert msg.status_code == 200
        assert msg.reason_phrase == "OK"
        assert msg.version == "SIP/2.0"

    def test_parse_401_unauthorized(self):
        """Test parsing 401 Unauthorized with WWW-Authenticate."""
        data = (
            b"SIP/2.0 401 Unauthorized\r\n"
            b"Via: SIP/2.0/UDP 192.168.1.1:5060\r\n"
            b'WWW-Authenticate: Digest realm="test.server", nonce="abc123xyz"\r\n'
            b"Content-Length: 0\r\n"
            b"\r\n"
        )
        msg = SIPMessage.parse(data)

        assert msg.status_code == 401
        assert "WWW-Authenticate" in msg.headers
        assert 'realm="test.server"' in msg.headers["WWW-Authenticate"]

    def test_parse_invite_with_sdp(self):
        """Test parsing INVITE with SDP body."""
        sdp = (
            "v=0\r\n"
            "o=- 123 1 IN IP4 192.168.1.100\r\n"
            "s=Session\r\n"
            "c=IN IP4 192.168.1.100\r\n"
            "t=0 0\r\n"
            "m=audio 10000 RTP/AVP 0\r\n"
        )
        data = (
            f"INVITE sip:user@test.server SIP/2.0\r\n"
            f"Via: SIP/2.0/UDP 192.168.1.1:5060\r\n"
            f"Content-Type: application/sdp\r\n"
            f"Content-Length: {len(sdp)}\r\n"
            f"\r\n"
            f"{sdp}"
        ).encode()

        msg = SIPMessage.parse(data)

        assert msg.method == "INVITE"
        assert "Content-Type" in msg.headers
        assert "v=0" in msg.body
        assert "m=audio 10000" in msg.body

    def test_build_request(self):
        """Test building SIP request."""
        msg = SIPMessage()
        msg.is_request = True
        msg.method = "REGISTER"
        msg.uri = "sip:test.server"
        msg.headers = {
            "Via": "SIP/2.0/UDP 192.168.1.1:5060",
            "From": "<sip:user@test.server>",
            "To": "<sip:user@test.server>",
            "Call-ID": "test123",
            "CSeq": "1 REGISTER"
        }

        data = msg.build()
        text = data.decode()

        assert text.startswith("REGISTER sip:test.server SIP/2.0")
        assert "Via: SIP/2.0/UDP" in text
        assert "Content-Length: 0" in text

    def test_build_response(self):
        """Test building SIP response."""
        msg = SIPMessage()
        msg.is_request = False
        msg.status_code = 200
        msg.reason_phrase = "OK"
        msg.headers = {
            "Via": "SIP/2.0/UDP 192.168.1.1:5060",
            "From": "<sip:user@test.server>",
            "To": "<sip:user@test.server>",
        }

        data = msg.build()
        text = data.decode()

        assert text.startswith("SIP/2.0 200 OK")


# =============================================================================
# CallSession Tests
# =============================================================================

class TestCallSession:
    """Tests for CallSession dataclass."""

    def test_default_values(self):
        """Test default call session values."""
        call = CallSession()
        assert call.state == CallState.IDLE
        assert call.direction == CallDirection.INBOUND
        assert call.call_id
        assert call.local_tag

    def test_duration_not_connected(self):
        """Test duration before connection."""
        call = CallSession()
        assert call.duration_seconds == 0

    def test_duration_connected(self):
        """Test duration after connection."""
        import time
        call = CallSession()
        call.connect_time = time.time() - 60  # 60 seconds ago
        call.end_time = time.time()
        assert call.duration_seconds == 60

    def test_duration_ongoing(self):
        """Test duration for ongoing call."""
        import time
        call = CallSession()
        call.connect_time = time.time() - 30  # 30 seconds ago
        # No end_time = still connected
        assert call.duration_seconds >= 29


# =============================================================================
# SIPClient Tests
# =============================================================================

class TestSIPClient:
    """Tests for SIP client."""

    def test_init_with_config(self, sip_config):
        """Test initialization with config."""
        client = SIPClient(sip_config)
        assert client.config.server == "test.sip.server"
        assert client.config.username == "testuser"
        assert not client._registered

    def test_init_without_credentials(self):
        """Test initialization without credentials."""
        config = SIPConfig(username="", password="")
        client = SIPClient(config)
        assert client.config.username == ""

    def test_get_local_ip(self, sip_client):
        """Test local IP detection."""
        ip = sip_client._get_local_ip()
        # Should return configured IP
        assert ip == "127.0.0.1"

    def test_build_via_header(self, sip_client):
        """Test Via header building."""
        via = sip_client._build_via_header()
        assert "SIP/2.0/UDP" in via
        assert "127.0.0.1:15060" in via
        assert "branch=z9hG4bK" in via

    def test_build_contact_header(self, sip_client):
        """Test Contact header building."""
        contact = sip_client._build_contact_header()
        assert "sip:testuser@127.0.0.1:15060" in contact

    def test_compute_digest_response(self, sip_client):
        """Test MD5 digest computation for auth."""
        sip_client._realm = "test.server"
        sip_client._nonce = "abc123"

        response = sip_client._compute_digest_response(
            method="REGISTER",
            uri="sip:test.server"
        )

        # Should be 32-char hex string (MD5)
        assert len(response) == 32
        assert all(c in '0123456789abcdef' for c in response)

    def test_get_status_not_registered(self, sip_client):
        """Test status when not registered."""
        status = sip_client.get_status()
        assert status["registered"] == False
        assert status["server"] == "test.sip.server"
        assert status["active_call"] is None

    def test_get_status_with_active_call(self, sip_client):
        """Test status with active call."""
        sip_client.active_call = CallSession(
            call_id="test123",
            direction=CallDirection.INBOUND,
            remote_number="+393331234567",
            state=CallState.CONNECTED
        )

        status = sip_client.get_status()
        assert status["active_call"] is not None
        assert status["active_call"]["call_id"] == "test123"
        assert status["active_call"]["direction"] == "inbound"
        assert status["active_call"]["state"] == "connected"


# =============================================================================
# RTPTransport Tests
# =============================================================================

class TestRTPTransport:
    """Tests for RTP audio transport."""

    def test_init(self):
        """Test RTP transport initialization."""
        rtp = RTPTransport(
            local_port=10000,
            remote_ip="192.168.1.100",
            remote_port=10002
        )
        assert rtp.local_port == 10000
        assert rtp.remote_ip == "192.168.1.100"
        assert rtp.remote_port == 10002

    def test_pcmu_encode_decode(self):
        """Test G.711 mu-law encoding/decoding data lengths."""
        rtp = RTPTransport(local_port=10000)

        # Create test PCM data (16-bit, 8 samples)
        samples = [0, 1000, 2000, 3000, -3000, -2000, -1000, 0]
        pcm = struct.pack('<8h', *samples)

        # Encode to mu-law
        encoded = rtp._encode_pcmu(pcm)
        assert len(encoded) == 8  # One byte per sample (compression ratio 2:1)

        # Decode back
        decoded = rtp._decode_pcmu(encoded)
        assert len(decoded) == 16  # Back to 16-bit (2 bytes per sample)

        # Verify we can unpack the decoded data
        decoded_samples = struct.unpack('<8h', decoded)
        assert len(decoded_samples) == 8

    def test_pcmu_silence(self):
        """Test encoding silence."""
        rtp = RTPTransport(local_port=10000)

        # Silence (zeros)
        silence = b'\x00' * 320  # 160 samples
        encoded = rtp._encode_pcmu(silence)

        # Should compress to ~160 bytes
        assert len(encoded) == 160


# =============================================================================
# VoIPManager Tests
# =============================================================================

class TestVoIPManager:
    """Tests for VoIP manager."""

    def test_init_default(self):
        """Test default initialization."""
        manager = VoIPManager()
        assert manager.sip is not None
        assert manager.rtp is None
        assert not manager._running

    def test_init_with_config(self, sip_config):
        """Test initialization with config."""
        manager = VoIPManager(sip_config)
        assert manager.config.server == "test.sip.server"

    def test_set_pipeline(self):
        """Test setting voice pipeline."""
        manager = VoIPManager()
        mock_pipeline = MagicMock()
        manager.set_pipeline(mock_pipeline)
        assert manager.pipeline == mock_pipeline

    def test_get_status_not_running(self):
        """Test status when not running."""
        manager = VoIPManager()
        status = manager.get_status()
        assert status["running"] == False
        assert status["rtp_active"] == False

    def test_audio_buffer_threshold(self):
        """Test audio buffer threshold."""
        manager = VoIPManager()
        # Default threshold should be ~500ms
        assert manager._buffer_threshold == 8000

    def test_upsample_audio(self):
        """Test upsampling from 8kHz to 16kHz."""
        manager = VoIPManager()

        # 4 samples at 8kHz
        samples_8k = struct.pack('<4h', 0, 1000, 2000, 1000)

        # Should become 8 samples at 16kHz
        samples_16k = manager._upsample_audio(samples_8k)
        assert len(samples_16k) == 16  # 8 samples * 2 bytes

        # Check interpolation
        result = struct.unpack('<8h', samples_16k)
        assert result[0] == 0
        assert result[2] == 1000
        assert result[4] == 2000

    def test_downsample_audio(self):
        """Test downsampling from 16kHz to 8kHz."""
        manager = VoIPManager()

        # 8 samples at 16kHz
        samples_16k = struct.pack('<8h', 0, 500, 1000, 1500, 2000, 1500, 1000, 500)

        # Should become 4 samples at 8kHz
        samples_8k = manager._downsample_audio(samples_16k)
        assert len(samples_8k) == 8  # 4 samples * 2 bytes

        # Check decimation (every other sample)
        result = struct.unpack('<4h', samples_8k)
        assert result[0] == 0
        assert result[1] == 1000
        assert result[2] == 2000


# =============================================================================
# Call Logging Tests (Analytics)
# =============================================================================

class TestCallLogging:
    """Tests for VoIP call logging in analytics."""

    def test_log_call_start(self, logger):
        """Test logging call start."""
        call_id = logger.log_call_start(
            call_id="call_001",
            direction="inbound",
            remote_number="+393331234567"
        )
        assert call_id == "call_001"

    def test_log_call_connected(self, logger):
        """Test logging call connection."""
        logger.log_call_start("call_002", "inbound", "+393331234567")
        logger.log_call_connected("call_002")

        # Verify in database
        import sqlite3
        conn = sqlite3.connect(logger.db_path)
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM voip_calls WHERE id = ?",
            ("call_002",)
        ).fetchone()
        conn.close()

        assert row["connect_time"] is not None

    def test_log_call_end(self, logger):
        """Test logging call end."""
        logger.log_call_start("call_003", "outbound", "+393339876543")
        logger.log_call_connected("call_003")
        logger.log_call_end(
            call_id="call_003",
            duration_seconds=120,
            outcome="completed",
            sip_status_code=200,
            rtp_packets_sent=6000,
            rtp_packets_received=5800,
            audio_quality_score=4.2
        )

        # Verify in database
        import sqlite3
        conn = sqlite3.connect(logger.db_path)
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM voip_calls WHERE id = ?",
            ("call_003",)
        ).fetchone()
        conn.close()

        assert row["duration_seconds"] == 120
        assert row["outcome"] == "completed"
        assert row["sip_status_code"] == 200
        assert row["rtp_packets_sent"] == 6000

    def test_get_call_metrics_empty(self, logger):
        """Test call metrics with no data."""
        metrics = logger.get_call_metrics()
        assert metrics["total_calls"] == 0
        assert metrics["answer_rate"] == 0

    def test_get_call_metrics_with_data(self, logger):
        """Test call metrics with data."""
        # Add some calls
        logger.log_call_start("call_m1", "inbound", "+39333111")
        logger.log_call_end("call_m1", 60, "completed")

        logger.log_call_start("call_m2", "inbound", "+39333222")
        logger.log_call_end("call_m2", 0, "missed")

        logger.log_call_start("call_m3", "outbound", "+39333333")
        logger.log_call_end("call_m3", 120, "completed")

        metrics = logger.get_call_metrics()

        assert metrics["total_calls"] == 3
        assert metrics["inbound_calls"] == 2
        assert metrics["outbound_calls"] == 1
        assert metrics["completed_calls"] == 2
        assert metrics["missed_calls"] == 1
        assert metrics["avg_duration_seconds"] == 60  # (60+0+120)/3
        assert metrics["answer_rate"] == pytest.approx(2/3, rel=0.01)

    def test_call_with_conversation(self, logger):
        """Test linking call to conversation session."""
        # Start conversation session (returns session ID string)
        session_id = logger.start_session("test_verticale")

        # Log call linked to session
        logger.log_call_start(
            call_id="call_conv1",
            direction="inbound",
            remote_number="+39333444",
            conversation_id=session_id
        )

        # Verify link
        import sqlite3
        conn = sqlite3.connect(logger.db_path)
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT conversation_id FROM voip_calls WHERE id = ?",
            ("call_conv1",)
        ).fetchone()
        conn.close()

        assert row["conversation_id"] == session_id


# =============================================================================
# Integration Tests
# =============================================================================

class TestVoIPIntegration:
    """Integration tests for VoIP system."""

    def test_call_state_flow(self):
        """Test call state transitions."""
        call = CallSession()
        assert call.state == CallState.IDLE

        # Simulate inbound call flow
        call.state = CallState.RINGING
        assert call.state == CallState.RINGING

        call.state = CallState.CONNECTED
        import time
        call.connect_time = time.time()
        assert call.state == CallState.CONNECTED

        call.state = CallState.ENDED
        call.end_time = time.time()
        assert call.state == CallState.ENDED
        assert call.duration_seconds >= 0

    def test_outbound_call_state_flow(self):
        """Test outbound call state transitions."""
        call = CallSession(direction=CallDirection.OUTBOUND)
        assert call.direction == CallDirection.OUTBOUND

        # Simulate outbound call flow
        call.state = CallState.INVITING
        call.state = CallState.RINGING
        call.state = CallState.CONNECTED
        call.state = CallState.ENDED

        assert call.state == CallState.ENDED


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
