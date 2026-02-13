"""
Tests per entity extraction - Verticale Salone
CoVe 2026 - Voice Agent Enterprise
"""

import pytest
import sys
import os
from datetime import datetime, timedelta

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from entities import SaloneEntityExtractor, BookingRequest, EXTRACTOR

class TestSaloneEntityExtractor:
    """Test suite per l'estrattore di entità"""
    
    @pytest.fixture
    def extractor(self):
        return SaloneEntityExtractor()
    
    # Test estrazione servizi
    def test_extract_service_taglio(self, extractor):
        text = "Vorrei un taglio"
        assert extractor.extract_service(text) == "taglio"
    
    def test_extract_service_colore(self, extractor):
        text = "Voglio fare il colore"
        assert extractor.extract_service(text) == "colore"
    
    def test_extract_service_taglio_colore(self, extractor):
        text = "Taglio e colore"
        assert extractor.extract_service(text) == "taglio_colore"
    
    def test_extract_service_barba(self, extractor):
        text = "Devo fare la barba"
        assert extractor.extract_service(text) == "barba"
    
    # Test estrazione date
    def test_extract_date_oggi(self, extractor):
        text = "Per oggi"
        result = extractor.extract_date(text)
        expected = datetime.now().strftime("%Y-%m-%d")
        assert result == expected
    
    def test_extract_date_domani(self, extractor):
        text = "Per domani"
        result = extractor.extract_date(text)
        expected = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        assert result == expected
    
    def test_extract_date_dopodomani(self, extractor):
        text = "Dopo domani"
        result = extractor.extract_date(text)
        expected = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
        assert result == expected
    
    def test_extract_date_numerical(self, extractor):
        text = "Per il 15/03"
        result = extractor.extract_date(text)
        assert result is not None
        assert "-03-15" in result
    
    # Test estrazione orari
    def test_extract_time_standard(self, extractor):
        text = "Alle 14:30"
        assert extractor.extract_time(text) == "14:30"
    
    def test_extract_time_e_format(self, extractor):
        text = "Alle 14 e 30"
        assert extractor.extract_time(text) == "14:30"
    
    def test_extract_time_mattina(self, extractor):
        text = "Di mattina"
        assert extractor.extract_time(text) == "09:00"
    
    def test_extract_time_pomeriggio(self, extractor):
        text = "Nel pomeriggio"
        assert extractor.extract_time(text) == "14:00"
    
    # Test estrazione operatore
    def test_extract_operator_con(self, extractor):
        text = "Vorrei prenotare con Maria"
        assert extractor.extract_operator(text) == "Maria"
    
    def test_extract_operator_da(self, extractor):
        text = "Da Giuseppe"
        assert extractor.extract_operator(text) == "Giuseppe"
    
    # Test calcolo durata
    def test_calculate_duration_taglio(self, extractor):
        assert extractor.calculate_duration("taglio") == 45
    
    def test_calculate_duration_colore(self, extractor):
        assert extractor.calculate_duration("colore") == 90
    
    def test_calculate_duration_default(self, extractor):
        assert extractor.calculate_duration("unknown") == 60
    
    # Test creazione booking request
    def test_create_booking_request(self, extractor):
        text = "Vorrei prenotare un taglio per domani alle 15:00"
        booking = extractor.create_booking_request(text)
        assert booking.service == "taglio"
        assert booking.time == "15:00"
        assert booking.durata_minuti == 45
    
    def test_create_booking_request_colore(self, extractor):
        text = "Colore per dopodomani"
        booking = extractor.create_booking_request(text)
        assert booking.service == "colore"
        assert booking.durata_minuti == 90
    
    # Test estrazione completa
    def test_extract_all(self, extractor):
        text = "Vorrei un taglio per domani alle 15 con Maria"
        result = extractor.extract_all(text)
        assert result["service"] == "taglio"
        assert result["time"] == "15:00"
        assert result["operator"] == "Maria"

# Test helper
def test_extract_helper():
    result = EXTRACTOR.extract_all("Taglio per domani")
    assert result["service"] == "taglio"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
