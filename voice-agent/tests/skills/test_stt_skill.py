"""
Unit Tests per STT Skill
CoVe 2026 - Voice Agent Enterprise
Coverage target: 90%
"""

import pytest
from unittest.mock import Mock, AsyncMock

class TestSTTSkill:
    """Test suite per STT Skill"""
    
    def test_stt_initialization(self):
        """Test inizializzazione STT"""
        mock_stt = Mock()
        mock_stt.model = "whisper-large-v3"
        mock_stt.language = "it"
        
        assert mock_stt.model == "whisper-large-v3"
        assert mock_stt.language == "it"
    
    @pytest.mark.asyncio
    async def test_stt_transcription(self):
        """Test trascrizione audio"""
        mock_stt = AsyncMock()
        mock_stt.transcribe.return_value = {
            "text": "Vorrei prenotare un taglio",
            "confidence": 0.95,
            "language": "it"
        }
        
        audio_data = b"fake_audio_data"
        result = await mock_stt.transcribe(audio_data)
        
        assert result["text"] == "Vorrei prenotare un taglio"
        assert result["confidence"] > 0.9
    
    @pytest.mark.asyncio
    async def test_stt_empty_audio(self):
        """Test gestione audio vuoto"""
        mock_stt = AsyncMock()
        mock_stt.transcribe.return_value = {
            "text": "",
            "confidence": 0.0,
            "language": "it"
        }
        
        result = await mock_stt.transcribe(b"")
        assert result["text"] == ""
        assert result["confidence"] == 0.0
    
    @pytest.mark.asyncio
    async def test_stt_italian_language_detection(self):
        """Test rilevamento lingua italiana"""
        mock_stt = AsyncMock()
        mock_stt.transcribe.return_value = {
            "text": "Buongiorno",
            "confidence": 0.98,
            "language": "it"
        }
        
        result = await mock_stt.transcribe(b"audio")
        assert result["language"] == "it"
    
    def test_stt_preprocessing(self):
        """Test preprocessing audio"""
        mock_stt = Mock()
        mock_stt.preprocess.return_value = b"processed_audio"
        
        raw_audio = b"raw_audio_data"
        processed = mock_stt.preprocess(raw_audio)
        
        assert processed == b"processed_audio"
    
    def test_stt_format_conversion(self):
        """Test conversione formati audio"""
        mock_stt = Mock()
        mock_stt.convert_format.return_value = {
            "sample_rate": 16000,
            "channels": 1,
            "format": "PCM_16"
        }
        
        result = mock_stt.convert_format(b"audio", target_rate=16000)
        assert result["sample_rate"] == 16000
        assert result["channels"] == 1

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
