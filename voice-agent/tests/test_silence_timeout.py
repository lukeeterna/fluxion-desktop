"""
Tests for A3: Silence timeout reduction (S143).

Validates that _vad_silence_timeout is 50 frames (1000ms)
and that turn detection triggers correctly.
"""

import sys
import pytest
from unittest.mock import MagicMock

# Mock native dependencies not available on MacBook (Python 3.13)
# pjsua2: SIP library only on iMac
# audioop: removed in Python 3.13
for _mod in ("pjsua2", "audioop"):
    if _mod not in sys.modules:
        sys.modules[_mod] = MagicMock()


from src.voip_pjsua2 import VoIPManager, SIPConfig


# =============================================================================
# Test VAD Silence Timeout Value
# =============================================================================

class TestSilenceTimeoutValue:
    """Test that the silence timeout is correctly set to 50 frames (1000ms)."""

    def test_vad_silence_timeout_is_50(self):
        """_vad_silence_timeout must be 50 (1000ms at 20ms/frame)."""
        config = SIPConfig()
        service = VoIPManager(config)
        assert service._vad_silence_timeout == 50

    def test_vad_silence_timeout_ms(self):
        """50 frames * 20ms/frame = 1000ms total silence."""
        config = SIPConfig()
        service = VoIPManager(config)
        ms = service._vad_silence_timeout * 20
        assert ms == 1000

    def test_vad_speech_threshold_unchanged(self):
        """Speech threshold should remain at 600 (not affected by A3)."""
        config = SIPConfig()
        service = VoIPManager(config)
        assert service._vad_speech_threshold == 600


# =============================================================================
# Test VAD Turn Detection Logic
# =============================================================================

class TestVADTurnDetection:
    """Test that turn detection triggers after correct number of silence frames."""

    def test_turn_triggers_after_50_silence_frames(self):
        """Turn should be detected after 15+ speech frames and 50 silence frames."""
        config = SIPConfig()
        service = VoIPManager(config)

        service._vad_speech_frames = 15
        service._vad_silence_frames = 50

        # The condition from voip_pjsua2.py line 664:
        turn_complete = (
            service._vad_speech_frames >= 15
            and service._vad_silence_frames >= service._vad_silence_timeout
        )
        assert turn_complete is True

    def test_short_pause_does_not_trigger(self):
        """30 frames (600ms) of silence should NOT trigger turn detection."""
        config = SIPConfig()
        service = VoIPManager(config)

        service._vad_speech_frames = 20
        service._vad_silence_frames = 30  # 600ms -- too short

        turn_complete = (
            service._vad_speech_frames >= 15
            and service._vad_silence_frames >= service._vad_silence_timeout
        )
        assert turn_complete is False

    def test_49_frames_does_not_trigger(self):
        """49 frames (980ms) should NOT trigger -- must be >= 50."""
        config = SIPConfig()
        service = VoIPManager(config)

        service._vad_speech_frames = 20
        service._vad_silence_frames = 49

        turn_complete = (
            service._vad_speech_frames >= 15
            and service._vad_silence_frames >= service._vad_silence_timeout
        )
        assert turn_complete is False

    def test_insufficient_speech_does_not_trigger(self):
        """Even with enough silence, insufficient speech (< 15 frames) should not trigger."""
        config = SIPConfig()
        service = VoIPManager(config)

        service._vad_speech_frames = 10  # Only 200ms speech
        service._vad_silence_frames = 50

        turn_complete = (
            service._vad_speech_frames >= 15
            and service._vad_silence_frames >= service._vad_silence_timeout
        )
        assert turn_complete is False

    def test_excess_silence_still_triggers(self):
        """75 frames (old value, 1500ms) should still trigger since >= 50."""
        config = SIPConfig()
        service = VoIPManager(config)

        service._vad_speech_frames = 20
        service._vad_silence_frames = 75

        turn_complete = (
            service._vad_speech_frames >= 15
            and service._vad_silence_frames >= service._vad_silence_timeout
        )
        assert turn_complete is True
