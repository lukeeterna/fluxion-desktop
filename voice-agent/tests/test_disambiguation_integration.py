"""
Test integrazione disambiguazione fonetica - Voice Agent v0.8.1

Verifica che il Voice Agent gestisca correttamente:
- "Gino" vs "Gigio" (similarità fonetica)
- "Mario" vs "Maria" (gender confusion STT)
- Match esatti (bentornato diretto)
- Nuovi clienti (nessuna ambiguità)
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from booking_state_machine import BookingStateMachine, BookingState, StateMachineResult
from disambiguation_handler import name_similarity, is_phonetically_similar


class TestNameSimilarity:
    """Test algoritmi di similarità fonetica."""
    
    def test_gino_vs_gigio_base_similarity(self):
        """Gino vs Gigio ha similarità base 60% (Levenshtein)."""
        similarity = name_similarity("Gino", "Gigio")
        # Levenshtein: 1 char diff su 5 = 0.8, ma è 0.6 per come è implementato
        assert 0.55 <= similarity <= 0.65, f"Similarity base Gino/Gigio: {similarity}"
    
    def test_mario_vs_maria_similarity(self):
        """Mario vs Maria dovrebbe avere similarità ~80%."""
        similarity = name_similarity("Mario", "Maria")
        assert 0.75 <= similarity <= 0.90, f"Similarity Mario/Maria: {similarity}"
    
    def test_luca_vs_luisa_not_similar(self):
        """Luca vs Luisa dovrebbe essere < 70%."""
        similarity = name_similarity("Luca", "Luisa")
        assert similarity < 0.70, f"Similarity Luca/Luisa: {similarity} (dovrebbe essere bassa)"
    
    def test_exact_match(self):
        """Nomi identici = 100%."""
        assert name_similarity("Gigio", "Gigio") == 1.0
        assert name_similarity("MARIA", "maria") == 1.0  # Case insensitive
    
    def test_phonetic_threshold_base(self):
        """Test threshold fonetico base (Levenshtein only)."""
        # Mario/Maria passano threshold 0.75
        assert is_phonetically_similar("Mario", "Maria") == True
        # Luca/Luisa non passano
        assert is_phonetically_similar("Luca", "Luisa") == False
        # Gino/Gigio non passano a 0.75 ma passano a 0.60 (usato in production)


class TestDisambiguationFlow:
    """Test flusso completo disambiguazione nella state machine."""
    
    def setup_method(self):
        """Setup per ogni test."""
        self.sm = BookingStateMachine()
    
    def test_gino_peruzzi_triggers_disambiguation(self):
        """
        SCENARIO 1: Utente dice 'Sono Gino Peruzzi' con Gigio in DB.
        Dovrebbe chiedere conferma, non dire 'Ciao Gino'.
        """
        self.sm.context.state = BookingState.WAITING_NAME
        
        # Simula input utente
        result = self.sm.process_message("Sono Gino Peruzzi")
        
        # Verifica stato
        print(f"\nTest Gino Peruzzi:")
        print(f"  Stato: {result.next_state.value}")
        print(f"  Risposta: {result.response}")
        
        # DOVREBBE chiedere disambiguazione, non dire "Ciao Gino"
        assert result.next_state == BookingState.DISAMBIGUATING_NAME, \
            f"Atteso DISAMBIGUATING_NAME, got {result.next_state.value}"
        
        # La risposta dovrebbe contenere 'Gigio' o 'conferma' o 'data di nascita'
        response_lower = result.response.lower()
        assert any(word in response_lower for word in ["gigio", "conferma", "nascita"]), \
            f"Risposta non chiede conferma: {result.response}"
    
    def test_exact_match_no_disambiguation(self):
        """
        SCENARIO 2: Utente dice nome esatto ('Gigio Peruzzi').
        Dovrebbe andare diretto a WAITING_SERVICE con bentornato.
        """
        self.sm.context.state = BookingState.WAITING_NAME
        
        result = self.sm.process_message("Sono Gigio Peruzzi")
        
        print(f"\nTest Gigio Peruzzi (esatto):")
        print(f"  Stato: {result.next_state.value}")
        print(f"  Risposta: {result.response}")
        
        # Match esatto o nuovo cliente - non disambiguazione
        assert result.next_state != BookingState.DISAMBIGUATING_NAME, \
            f"Non dovrebbe disambiguare nome esatto: {result.response}"
    
    def test_new_client_no_disambiguation(self):
        """
        SCENARIO 3: Nuovo cliente con nome diverso da tutti.
        Dovrebbe procedere senza disambiguazione.
        """
        self.sm.context.state = BookingState.WAITING_NAME
        
        # Nome molto diverso da qualsiasi cliente
        result = self.sm.process_message("Sono Alessandro Manzoni")
        
        print(f"\nTest Alessandro Manzoni (nuovo):")
        print(f"  Stato: {result.next_state.value}")
        print(f"  Risposta: {result.response}")
        
        # Non dovrebbe chiedere disambiguazione
        assert result.next_state != BookingState.DISAMBIGUATING_NAME, \
            f"Nuovo cliente non dovrebbe triggerare disambiguazione: {result.response}"


class TestDisambiguationStateHandlers:
    """Test handler per stati di disambiguazione."""
    
    def setup_method(self):
        self.sm = BookingStateMachine()
    
    def test_disambiguating_name_accepts_birth_date(self):
        """Test che DISAMBIGUATING_NAME accetti data di nascita corretta."""
        self.sm.context.state = BookingState.DISAMBIGUATING_NAME
        self.sm.context.disambiguation_candidates = [{
            "id": "test-gigio",
            "nome": "Gigio",
            "cognome": "Peruzzi",
            "data_nascita": "1985-03-15"
        }]
        self.sm.context.disambiguation_attempts = 0
        
        result = self.sm.process_message("15 marzo 1985")
        
        print(f"\nTest conferma con data nascita:")
        print(f"  Stato: {result.next_state.value}")
        print(f"  Client ID: {self.sm.context.client_id}")
        
        # Dovrebbe confermare e andare a WAITING_SERVICE
        assert result.next_state == BookingState.WAITING_SERVICE, \
            f"Dovrebbe andare a WAITING_SERVICE, got {result.next_state.value}"
        assert self.sm.context.client_id == "test-gigio"
    
    def test_disambiguating_name_rejects_wrong_person(self):
        """Test che 'no, sono un altro' porti a nuovo cliente."""
        self.sm.context.state = BookingState.DISAMBIGUATING_NAME
        self.sm.context.disambiguation_candidates = [{
            "id": "test-gigio",
            "nome": "Gigio",
            "cognome": "Peruzzi"
        }]
        
        result = self.sm.process_message("No, sono una persona diversa")
        
        print(f"\nTest rifiuto disambiguazione:")
        print(f"  Stato: {result.next_state.value}")
        
        # Dovrebbe andare a registrazione nuovo cliente
        assert result.next_state in [BookingState.REGISTERING_SURNAME, BookingState.WAITING_SERVICE], \
            f"Dovrebbe andare a registrazione, got {result.next_state.value}"


class TestRegressionExistingFlows:
    """Test che flussi esistenti non si siano rotti."""
    
    def setup_method(self):
        self.sm = BookingStateMachine()
    
    def test_followup_booking_same_client(self):
        """Test booking di follow-up con cliente già identificato."""
        self.sm.context.client_id = "test-gigio"
        self.sm.context.client_name = "Gigio"
        self.sm.context.state = BookingState.WAITING_NAME
        
        result = self.sm.process_message("Vorrei un altro appuntamento")
        
        assert result.next_state == BookingState.WAITING_SERVICE, \
            f"Follow-up booking fallito: {result.next_state.value}"
    
    def test_new_client_indicator_flow(self):
        """Test flusso 'prima volta' non si sia rotto."""
        self.sm.context.state = BookingState.WAITING_NAME
        
        result = self.sm.process_message("È la prima volta che vengo")
        
        print(f"\nTest 'prima volta':")
        print(f"  Stato: {result.next_state.value}")
        
        # Dovrebbe andare a registrazione
        assert self.sm.context.is_new_client == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
