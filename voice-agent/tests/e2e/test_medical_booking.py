"""
E2E Test - Prenotazione Medical
CoVe 2026 - Voice Agent Enterprise
"""

import pytest
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(BASE_DIR, 'verticals', 'medical'))

from verticals.medical.intents import classify, IntentType
from verticals.medical.entities import EXTRACTOR
from verticals.medical.schema import create_booking, create_patient

class TestMedicalBookingE2E:
    """Test E2E prenotazione medical"""
    
    def test_e2e_prenotazione_visita(self):
        """E2E: Prenotazione visita"""
        user_input = "Vorrei prenotare una visita per dopodomani"
        
        intent = classify(user_input)
        assert intent.type == IntentType.PRENOTAZIONE
        
        entities = EXTRACTOR.extract_all(user_input)
        assert entities["service"] == "visita"
        
        patient = create_patient(
            nome="Giulia",
            cognome="Rossi",
            telefono="+39123456789"
        )
        
        booking = create_booking(
            patient_id=patient.id or "pat_123",
            servizio=entities["service"],
            data=entities["date"] or "2026-02-15",
            ora=entities["time"] or "10:00",
            durata_minuti=30
        )
        
        booking.conferma()
        assert booking.stato == "confirmed"
    
    def test_e2e_urgenza(self):
        """E2E: Gestione urgenza"""
        user_input = "Ho un dolore forte, ho bisogno di un appuntamento urgente"
        
        intent = classify(user_input)
        assert intent.type == IntentType.URGENTE
        
        urgenza = EXTRACTOR.extract_urgency(user_input)
        assert urgenza in ["alta", "critica"]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
