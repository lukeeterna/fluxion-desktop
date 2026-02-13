"""
E2E Tests - Verticale Salone
CoVe 2026 - Voice Agent Enterprise
Test end-to-end per flussi completi di prenotazione
"""

import pytest
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CONFIG
from intents import classify, IntentType
from entities import EXTRACTOR
from schema import create_customer, create_booking, BookingStatus

class TestSaloneE2E:
    """Test end-to-end per flussi completi"""
    
    def test_flusso_prenotazione_completo(self):
        """Test flusso completo di prenotazione"""
        # 1. Utente richiede prenotazione
        user_input = "Vorrei prenotare un taglio per domani alle 15:00"
        
        # 2. Classifica intent
        intent = classify(user_input)
        assert intent.type == IntentType.PRENOTAZIONE
        
        # 3. Estrai entità
        entities = EXTRACTOR.extract_all(user_input)
        assert entities["service"] == "taglio"
        assert entities["time"] == "15:00"
        
        # 4. Crea booking
        booking = create_booking(
            customer_id="cust_123",
            servizio=entities["service"],
            data=entities["date"] or "2026-02-14",
            ora=entities["time"],
            durata_minuti=45
        )
        assert booking.servizio == "taglio"
        assert booking.ora_inizio == "15:00"
        assert booking.stato == "pending"
    
    def test_flusso_cancellazione(self):
        """Test flusso di cancellazione"""
        # 1. Crea booking esistente
        booking = create_booking(
            customer_id="cust_123",
            servizio="taglio",
            data="2026-02-14",
            ora="15:00"
        )
        booking.conferma()
        
        # 2. Utente richiede cancellazione
        user_input = "Devo cancellare il mio appuntamento"
        intent = classify(user_input)
        assert intent.type == IntentType.CANCELLAZIONE
        
        # 3. Cancella
        booking.cancella(motivo="Impegno improvviso")
        assert booking.stato == "cancelled"
    
    def test_flusco_spostamento(self):
        """Test flusso di spostamento appuntamento"""
        # 1. Crea booking
        booking = create_booking(
            customer_id="cust_123",
            servizio="colore",
            data="2026-02-14",
            ora="10:00",
            durata_minuti=90
        )
        
        # 2. Utente richiede spostamento
        user_input = "Posso spostare l'appuntamento a venerdì?"
        intent = classify(user_input)
        assert intent.type == IntentType.SPOSTAMENTO
        
        # 3. Sposta
        booking.sposta(nuova_data="2026-02-16", nuova_ora="14:00")
        assert booking.data == "2026-02-16"
        assert booking.ora_inizio == "14:00"
    
    def test_verifica_configurazione(self):
        """Verifica che la configurazione sia corretta"""
        assert CONFIG.name == "salone"
        assert "taglio" in CONFIG.services
        assert "colore" in CONFIG.services
        assert len(CONFIG.required_slots) >= 3
        assert "service" in CONFIG.required_slots
    
    def test_flusso_info_prezzi(self):
        """Test richiesta informazioni prezzi"""
        user_input = "Quanto costa il colore?"
        intent = classify(user_input)
        assert intent.type == IntentType.PREZZI
        
        # Verifica che ci siano prezzi configurati
        assert "taglio_donna" in CONFIG.prices
        assert "colore" in CONFIG.prices
    
    def test_flusso_saluto_congedo(self):
        """Test saluto e congedo"""
        saluto = classify("Buongiorno")
        assert saluto.type == IntentType.SALUTO
        
        congedo = classify("Grazie, arrivederci")
        assert congedo.type == IntentType.CONGEDO
    
    def test_prenotazione_con_preferenze(self):
        """Test prenotazione con preferenze cliente"""
        # Crea cliente con preferenze
        customer = create_customer(
            nome="Anna",
            telefono="+39123456789",
            tipo_capelli="ricci",
            lunghezza_capelli="lunghi",
            preferenze_operatore="Maria",
            allergie_prodotti=["ammoniaca"]
        )
        
        assert customer.nome == "Anna"
        assert customer.preferenze_operatore == "Maria"
        assert "ammoniaca" in customer.allergie_prodotti

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
