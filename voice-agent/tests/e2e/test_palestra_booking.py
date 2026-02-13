"""
E2E Test - Prenotazione Palestra
CoVe 2026 - Voice Agent Enterprise
"""

import pytest
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(BASE_DIR, 'verticals', 'palestra'))

from verticals.palestra.intents import classify, IntentType
from verticals.palestra.entities import EXTRACTOR
from verticals.palestra.schema import create_booking, create_member

class TestPalestraBookingE2E:
    """Test E2E prenotazione palestra"""
    
    def test_e2e_prenotazione_pt(self):
        """E2E: Prenotazione personal trainer"""
        user_input = "Vorrei prenotare un PT per domani alle 18"
        
        intent = classify(user_input)
        assert intent.type == IntentType.PRENOTAZIONE
        
        entities = EXTRACTOR.extract_all(user_input)
        assert entities["service"] == "pt"
        
        member = create_member(
            nome="Luca",
            telefono="+39123456789"
        )
        
        booking = create_booking(
            member_id=member.id or "mem_123",
            servizio=entities["service"],
            data=entities["date"] or "2026-02-14",
            ora=entities["time"] or "18:00",
            durata_minuti=60
        )
        
        assert booking.durata_minuti == 60
    
    def test_e2e_prenotazione_corso(self):
        """E2E: Prenotazione corso yoga"""
        user_input = "Vorrei prenotare una lezione di yoga"
        
        intent = classify(user_input)
        assert intent.type == IntentType.PRENOTAZIONE
        
        entities = EXTRACTOR.extract_all(user_input)
        assert entities["service"] == "yoga"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
