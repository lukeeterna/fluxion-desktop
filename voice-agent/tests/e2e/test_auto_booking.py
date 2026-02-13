"""
E2E Test - Prenotazione Auto/Officina
CoVe 2026 - Voice Agent Enterprise
"""

import pytest
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(BASE_DIR, 'verticals', 'auto'))

from verticals.auto.intents import classify, IntentType
from verticals.auto.entities import EXTRACTOR
from verticals.auto.schema import create_booking, create_vehicle

class TestAutoBookingE2E:
    """Test E2E prenotazione officina"""
    
    def test_e2e_prenotazione_tagliando(self):
        """E2E: Prenotazione tagliando"""
        user_input = "Vorrei prenotare un tagliando per domani mattina, targa AB123CD"
        
        intent = classify(user_input)
        assert intent.type == IntentType.PRENOTAZIONE
        
        entities = EXTRACTOR.extract_all(user_input)
        assert entities["service"] == "tagliando"
        assert entities["targa"] == "AB123CD"
        
        vehicle = create_vehicle(
            targa="AB123CD",
            modello="Fiat Panda"
        )
        
        booking = create_booking(
            vehicle_id=vehicle.id or "veh_123",
            servizio=entities["service"],
            data=entities["date"] or "2026-02-14",
            ora=entities["time"] or "08:00",
            targa=entities["targa"]
        )
        
        assert booking.targa == "AB123CD"
    
    def test_e2e_urgenza_riparazione(self):
        """E2E: Urgenza riparazione"""
        user_input = "Non parte l'auto, ho bisogno di aiuto subito"
        
        intent = classify(user_input)
        assert intent.type == IntentType.URGENTE
        
        urgenza = EXTRACTOR.extract_urgenza(user_input)
        assert urgenza == "immediata"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
