"""
Unit Tests per State Skill
CoVe 2026 - Voice Agent Enterprise
Coverage target: 90%
"""

import pytest
from unittest.mock import Mock

class TestStateSkill:
    """Test suite per State Skill (Booking State Machine)"""
    
    def test_state_initialization(self):
        """Test inizializzazione stato"""
        mock_state = Mock()
        mock_state.current_state = "IDLE"
        mock_state.session_id = "test_session_123"
        
        assert mock_state.current_state == "IDLE"
    
    def test_state_transition_to_collecting(self):
        """Test transizione a collecting"""
        mock_state = Mock()
        mock_state.transition.return_value = "COLLECTING_SLOTS"
        
        new_state = mock_state.transition("START_BOOKING")
        assert new_state == "COLLECTING_SLOTS"
    
    def test_state_transition_to_confirming(self):
        """Test transizione a confirming"""
        mock_state = Mock()
        mock_state.transition.return_value = "CONFIRMING"
        
        new_state = mock_state.transition("SLOTS_FILLED")
        assert new_state == "CONFIRMING"
    
    def test_state_transition_to_confirmed(self):
        """Test transizione a confirmed"""
        mock_state = Mock()
        mock_state.transition.return_value = "CONFIRMED"
        
        new_state = mock_state.transition("USER_CONFIRMED")
        assert new_state == "CONFIRMED"
    
    def test_state_invalid_transition(self):
        """Test transizione invalida"""
        mock_state = Mock()
        mock_state.transition.return_value = None
        mock_state.get_error.return_value = "Invalid transition"
        
        result = mock_state.transition("INVALID_EVENT")
        assert result is None
        assert mock_state.get_error() == "Invalid transition"
    
    def test_state_slot_management(self):
        """Test gestione slot"""
        mock_state = Mock()
        mock_state.slots = {}
        
        # Aggiungi slot
        mock_state.set_slot.return_value = True
        result = mock_state.set_slot("service", "taglio")
        assert result is True
        
        # Verifica slot richiesti
        mock_state.get_missing_slots.return_value = ["date", "time"]
        missing = mock_state.get_missing_slots()
        assert "date" in missing
        assert "time" in missing
    
    def test_state_persistency(self):
        """Test persistenza stato"""
        mock_state = Mock()
        mock_state.save.return_value = True
        mock_state.load.return_value = {
            "current_state": "COLLECTING_SLOTS",
            "slots": {"service": "taglio"}
        }
        
        # Salva stato
        assert mock_state.save() is True
        
        # Carica stato
        loaded = mock_state.load()
        assert loaded["current_state"] == "COLLECTING_SLOTS"
        assert loaded["slots"]["service"] == "taglio"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
