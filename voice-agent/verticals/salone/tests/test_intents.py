"""
Tests per intent classification - Verticale Salone
CoVe 2026 - Voice Agent Enterprise
"""

import pytest
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from intents import SaloneIntentClassifier, IntentType, classify

class TestSaloneIntentClassifier:
    """Test suite per il classificatore di intent"""
    
    @pytest.fixture
    def classifier(self):
        return SaloneIntentClassifier()
    
    # Test PRENOTAZIONE
    def test_prenotazione_basic(self, classifier):
        text = "Vorrei prenotare un taglio"
        intent = classifier.classify(text)
        assert intent.type == IntentType.PRENOTAZIONE
        assert intent.confidence > 0.5
    
    def test_prenotazione_fissare(self, classifier):
        text = "Posso fissare per domani?"
        intent = classifier.classify(text)
        assert intent.type == IntentType.PRENOTAZIONE
    
    def test_prenotazione_appuntamento(self, classifier):
        text = "Mi prenoto per una piega"
        intent = classifier.classify(text)
        assert intent.type == IntentType.PRENOTAZIONE
    
    # Test CANCELLAZIONE
    def test_cancellazione_basic(self, classifier):
        text = "Devo cancellare l'appuntamento"
        intent = classifier.classify(text)
        assert intent.type == IntentType.CANCELLAZIONE
    
    def test_cancellazione_non_posso(self, classifier):
        text = "Non posso venire domani"
        intent = classifier.classify(text)
        assert intent.type == IntentType.CANCELLAZIONE
    
    # Test SPOSTAMENTO
    def test_spostamento_spostare(self, classifier):
        text = "Posso spostare l'appuntamento?"
        intent = classifier.classify(text)
        assert intent.type == IntentType.SPOSTAMENTO
    
    def test_spostamento_cambiare(self, classifier):
        text = "Cambio orario"
        intent = classifier.classify(text)
        assert intent.type == IntentType.SPOSTAMENTO
    
    # Test PREZZI
    def test_prezzi_quanto(self, classifier):
        text = "Quanto costa un taglio?"
        intent = classifier.classify(text)
        assert intent.type == IntentType.PREZZI
    
    def test_prezzi_prezzo(self, classifier):
        text = "Il prezzo del colore?"
        intent = classifier.classify(text)
        assert intent.type == IntentType.PREZZI
    
    # Test ORARI
    def test_orari_apertura(self, classifier):
        text = "A che ora aprite?"
        intent = classifier.classify(text)
        assert intent.type == IntentType.ORARI
    
    def test_orari_domenica(self, classifier):
        text = "Siete aperti la domenica?"
        intent = classifier.classify(text)
        assert intent.type == IntentType.ORARI
    
    # Test SERVIZI
    def test_servizi_offrite(self, classifier):
        text = "Che servizi offrite?"
        intent = classifier.classify(text)
        assert intent.type == IntentType.SERVIZI
    
    # Test SALUTO
    def test_saluto_ciao(self, classifier):
        text = "Ciao"
        intent = classifier.classify(text)
        assert intent.type == IntentType.SALUTO
    
    def test_saluto_buongiorno(self, classifier):
        text = "Buongiorno"
        intent = classifier.classify(text)
        assert intent.type == IntentType.SALUTO
    
    # Test CONGEDO
    def test_congedo_grazie(self, classifier):
        text = "Grazie, arrivederci"
        intent = classifier.classify(text)
        assert intent.type == IntentType.CONGEDO
    
    # Test FALLBACK
    def test_fallback_nonsense(self, classifier):
        text = "Blah blah xyz123"
        intent = classifier.classify(text)
        assert intent.type == IntentType.FALLBACK
    
    # Test estrazione entità
    def test_entity_extraction_service(self, classifier):
        text = "Vorrei prenotare un taglio"
        intent = classifier.classify(text)
        assert "service" in intent.entities
        assert intent.entities["service"] == "taglio"
    
    def test_entity_extraction_operator(self, classifier):
        text = "Vorrei prenotare con Maria"
        intent = classifier.classify(text)
        assert "operator" in intent.entities
        assert intent.entities["operator"] == "Maria"

# Test helper function
def test_classify_helper():
    intent = classify("Vorrei un taglio")
    assert intent.type == IntentType.PRENOTAZIONE

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
