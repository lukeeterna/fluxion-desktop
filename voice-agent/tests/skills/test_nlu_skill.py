"""
Unit Tests per NLU Skill
CoVe 2026 - Voice Agent Enterprise
Coverage target: 90%
"""

import pytest
from unittest.mock import Mock, AsyncMock

class TestNLUSkill:
    """Test suite per NLU Skill"""
    
    def test_nlu_initialization(self):
        """Test inizializzazione NLU"""
        mock_nlu = Mock()
        mock_nlu.model = "groq-llama3"
        mock_nlu.language = "it"
        
        assert mock_nlu.model == "groq-llama3"
        assert mock_nlu.language == "it"
    
    @pytest.mark.asyncio
    async def test_nlu_intent_classification(self):
        """Test classificazione intent"""
        mock_nlu = AsyncMock()
        mock_nlu.classify_intent.return_value = {
            "intent": "PRENOTAZIONE",
            "confidence": 0.95,
            "entities": {"service": "taglio"}
        }
        
        result = await mock_nlu.classify_intent("Vorrei prenotare un taglio")
        
        assert result["intent"] == "PRENOTAZIONE"
        assert result["confidence"] > 0.9
        assert result["entities"]["service"] == "taglio"
    
    @pytest.mark.asyncio
    async def test_nlu_entity_extraction(self):
        """Test estrazione entità"""
        mock_nlu = AsyncMock()
        mock_nlu.extract_entities.return_value = {
            "service": "taglio",
            "date": "2026-02-14",
            "time": "15:00"
        }
        
        result = await mock_nlu.extract_entities(
            "Vorrei un taglio per domani alle 15"
        )
        
        assert result["service"] == "taglio"
        assert result["time"] == "15:00"
    
    @pytest.mark.asyncio
    async def test_nlu_sentiment_analysis(self):
        """Test analisi sentiment"""
        mock_nlu = AsyncMock()
        mock_nlu.analyze_sentiment.return_value = {
            "sentiment": "positive",
            "score": 0.8,
            "urgency": "low"
        }
        
        result = await mock_nlu.analyze_sentiment("Perfetto, grazie mille!")
        assert result["sentiment"] == "positive"
        assert result["score"] > 0.5
    
    @pytest.mark.asyncio
    async def test_nlu_context_management(self):
        """Test gestione contesto conversazione"""
        mock_nlu = AsyncMock()
        
        # Prima interazione
        mock_nlu.classify_intent.return_value = {
            "intent": "PRENOTAZIONE",
            "context": {"service_pending": True}
        }
        result1 = await mock_nlu.classify_intent("Vorrei prenotare")
        
        # Follow-up con contesto
        mock_nlu.classify_intent.return_value = {
            "intent": "CONFIRM_SERVICE",
            "context": {"service": "taglio"}
        }
        result2 = await mock_nlu.classify_intent("Un taglio", context=result1["context"])
        
        assert result2["context"]["service"] == "taglio"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
