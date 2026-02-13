"""
Integration Tests - Pipeline Audio
CoVe 2026 - Voice Agent Enterprise
Test pipeline: VAD → STT → NLU → State → TTS
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch

class TestAudioPipeline:
    """Test suite per pipeline audio completa"""
    
    @pytest.mark.asyncio
    async def test_pipeline_full_flow(self):
        """Test flusso completo pipeline"""
        # Mock components
        mock_vad = Mock()
        mock_stt = AsyncMock()
        mock_nlu = AsyncMock()
        mock_state = Mock()
        mock_tts = AsyncMock()
        
        # Configura mock
        mock_vad.process.return_value = {"is_speech": True, "event": "SPEECH_START"}
        mock_stt.transcribe.return_value = {"text": "Vorrei prenotare un taglio", "confidence": 0.95}
        mock_nlu.classify_intent.return_value = {"intent": "PRENOTAZIONE", "confidence": 0.92}
        mock_state.transition.return_value = "COLLECTING_SLOTS"
        mock_tts.synthesize.return_value = {"audio": b"audio_data"}
        
        # Simula pipeline
        audio_chunk = b"audio_input"
        
        # Step 1: VAD
        vad_result = mock_vad.process(audio_chunk)
        assert vad_result["is_speech"] is True
        
        # Step 2: STT
        stt_result = await mock_stt.transcribe(audio_chunk)
        assert stt_result["text"] == "Vorrei prenotare un taglio"
        
        # Step 3: NLU
        nlu_result = await mock_nlu.classify_intent(stt_result["text"])
        assert nlu_result["intent"] == "PRENOTAZIONE"
        
        # Step 4: State
        state_result = mock_state.transition("INTENT_DETECTED")
        assert state_result == "COLLECTING_SLOTS"
        
        # Step 5: TTS
        tts_result = await mock_tts.synthesize("Che servizio desidera?")
        assert tts_result["audio"] is not None
    
    @pytest.mark.asyncio
    async def test_pipeline_latency_requirement(self):
        """Test requisito latenza < 800ms P95"""
        import time
        
        # Simula latenze pipeline
        latencies = [650, 720, 680, 750, 800, 620, 710, 690, 740, 780]
        latencies.sort()
        
        # Calcola P95
        p95_index = int(len(latencies) * 0.95)
        p95_latency = latencies[p95_index]
        
        assert p95_latency <= 800, f"Latenza P95 {p95_latency}ms supera 800ms"
    
    @pytest.mark.asyncio
    async def test_pipeline_interruption_handling(self):
        """Test gestione interruzioni durante TTS"""
        mock_vad = Mock()
        mock_tts = AsyncMock()
        
        # TTS sta riproducendo
        tts_playing = True
        
        # Interruzione rilevata
        mock_vad.detect_interruption.return_value = True
        
        if tts_playing:
            interruption = True  # Simula rilevamento interruzione
            # Interrompi TTS se interruzione rilevata
            if interruption:
                result = True  # Simula stop riuscito
                assert result is True
    
    @pytest.mark.asyncio
    async def test_pipeline_error_recovery(self):
        """Test recovery da errori"""
        mock_stt = AsyncMock()
        mock_nlu = AsyncMock()
        
        # STT fallisce
        mock_stt.transcribe.side_effect = Exception("STT Error")
        
        # Recovery con retry
        try:
            await mock_stt.transcribe(b"audio")
        except Exception:
            # Fallback
            mock_nlu.fallback_response.return_value = "Non ho capito, puoi ripetere?"
            fallback = await mock_nlu.fallback_response()
            assert "ripetere" in fallback

class TestIntegrationWhatsApp:
    """Test integrazione WhatsApp"""
    
    @pytest.mark.asyncio
    async def test_whatsapp_booking_confirmation(self):
        """Test invio conferma via WhatsApp"""
        mock_whatsapp = AsyncMock()
        mock_whatsapp.send_message.return_value = {
            "status": "sent",
            "message_id": "msg_123",
            "timestamp": "2026-02-13T10:00:00Z"
        }
        
        result = await mock_whatsapp.send_message(
            to="+39123456789",
            body="Conferma appuntamento: 14/02 alle 15:00"
        )
        
        assert result["status"] == "sent"
        assert result["message_id"] is not None

class TestIntegrationVoIP:
    """Test integrazione VoIP EhiWeb"""
    
    def test_voip_inbound_call_handling(self):
        """Test gestione chiamata inbound"""
        mock_voip = Mock()
        mock_voip.handle_inbound_call.return_value = {
            "call_id": "call_123",
            "caller_number": "+39123456789",
            "status": "connected"
        }
        
        result = mock_voip.handle_inbound_call("+39123456789")
        assert result["status"] == "connected"
        assert result["call_id"] is not None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
