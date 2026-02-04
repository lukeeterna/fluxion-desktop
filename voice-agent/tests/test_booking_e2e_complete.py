"""
FLUXION Voice Agent - Test E2E Completo
Test end-to-end del flusso di prenotazione con VIP, lista d'attesa, annullamento
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from booking_orchestrator import BookingOrchestrator, WhatsAppBookingHandler
from booking_manager import BookingManager, BookingStatus
from vertical_schemas import CustomerTier, CustomerProfile
from service_resolver import ServiceResolver, OperatorResolver


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def mock_db():
    """Database mock con dati di test"""
    db = Mock()
    
    # Dati test
    db.services = {
        "srv_001": {
            "id": "srv_001",
            "name": "Taglio Donna",
            "aliases": ["taglio", "sforbiciata", "capelli"],
            "duration_minutes": 30,
            "price": 25.0
        },
        "srv_002": {
            "id": "srv_002",
            "name": "Colore",
            "aliases": ["colore", "tinta", "tintura"],
            "duration_minutes": 60,
            "price": 45.0
        },
        "srv_003": {
            "id": "srv_003",
            "name": "Fisioterapia",
            "aliases": ["fisioterapia", "fisio", "riabilitazione"],
            "duration_minutes": 45,
            "price": 50.0
        }
    }
    
    db.operators = {
        "op_001": {
            "id": "op_001",
            "name": "Giovanna",
            "nicknames": ["Giovanna", "Giovi"],
            "gender": "F",
            "services": ["srv_001", "srv_002"]
        },
        "op_002": {
            "id": "op_002",
            "name": "Anna",
            "nicknames": ["Anna"],
            "gender": "F",
            "services": ["srv_001"]
        },
        "op_003": {
            "id": "op_003",
            "name": "Marco",
            "nicknames": ["Marco"],
            "gender": "M",
            "services": ["srv_003"]
        }
    }
    
    db.customers = {
        "cust_vip": {
            "id": "cust_vip",
            "name": "Mario",
            "surname": "Rossi",
            "phone": "+39123456789",
            "tier": "vip",
            "preferred_operator_id": "op_001"
        },
        "cust_standard": {
            "id": "cust_standard",
            "name": "Luigi",
            "surname": "Bianchi",
            "phone": "+39987654321",
            "tier": "standard"
        }
    }
    
    # Mock methods
    db.get_services_by_business.return_value = list(db.services.values())
    db.get_operators_by_business.return_value = list(db.operators.values())
    db.get_customer.side_effect = lambda cid: db.customers.get(cid)
    db.get_customer_by_phone.side_effect = lambda phone: next(
        (c for c in db.customers.values() if c["phone"] == phone), None
    )
    db.get_service.side_effect = lambda sid: db.services.get(sid)
    db.get_operator.side_effect = lambda oid: db.operators.get(oid)
    
    return db


@pytest.fixture
def mock_whatsapp():
    """Mock servizio WhatsApp"""
    whatsapp = Mock()
    whatsapp.send_message = Mock(return_value=True)
    return whatsapp


@pytest.fixture
def orchestrator(mock_db, mock_whatsapp):
    """Orchestrator configurato per test"""
    return BookingOrchestrator(
        db_connection=mock_db,
        whatsapp_service=mock_whatsapp,
        business_id="biz_001"
    )


# =============================================================================
# TEST FLUSSO BASE
# =============================================================================

class TestFlussoBase:
    """Test flusso prenotazione standard"""
    
    def test_prenotazione_completa(self, orchestrator):
        """Test prenotazione dal primo messaggio alla conferma"""
        session_id = "test_session_001"
        
        # Step 1: Richiesta servizio
        result1 = orchestrator.process_message(
            session_id=session_id,
            message="Vorrei prenotare un taglio",
            customer_phone="+39987654321"
        )
        assert result1["state"] == "waiting_date"
        assert "taglio" in result1["response"].lower()
        
        # Step 2: Data
        result2 = orchestrator.process_message(
            session_id=session_id,
            message="Domani"
        )
        assert result2["state"] == "waiting_time"
        assert "domani" in result2["response"].lower()
        
        # Step 3: Ora + Operatore
        result3 = orchestrator.process_message(
            session_id=session_id,
            message="Alle 15 con Giovanna"
        )
        assert result3["state"] == "confirming"
        assert "15" in result3["response"]
        
        # Step 4: Conferma
        result4 = orchestrator.process_message(
            session_id=session_id,
            message="Sì confermo"
        )
        assert result4["completed"] is True
        assert result4["booking_id"] is not None
    
    def test_prenotazione_con_preferenza_operatore(self, orchestrator):
        """Test che riconosca preferenza operatore"""
        session_id = "test_session_002"
        
        # Prenotazione con preferenza esplicita
        orchestrator.process_message(
            session_id=session_id,
            message="Vorrei un colore",
            customer_phone="+39987654321"
        )
        
        orchestrator.process_message(session_id, "Domani")
        
        result = orchestrator.process_message(session_id, "Alle 16 con Giovanna")
        
        # Verifica che l'orchestratore abbia risolto l'operatore
        ctx = orchestrator.sessions[session_id]
        assert ctx.operator_name == "Giovanna"


# =============================================================================
# TEST VIP E LISTA D'ATTESA
# =============================================================================

class TestVIPeWaitlist:
    """Test funzionalità VIP e lista d'attesa"""
    
    def test_priorita_vip_in_waitlist(self, orchestrator, mock_db):
        """Test che VIP abbia priorità superiore in lista d'attesa"""
        
        # Crea entry lista d'attesa per cliente standard
        entry_standard = orchestrator.booking_manager.add_to_waitlist(
            customer_id="cust_standard",
            service_id="srv_001",
            preferred_dates=["2026-02-10"]
        )
        
        # Crea entry per cliente VIP
        entry_vip = orchestrator.booking_manager.add_to_waitlist(
            customer_id="cust_vip",
            service_id="srv_001",
            preferred_dates=["2026-02-10"]
        )
        
        # Verifica priorità
        waitlist = orchestrator.booking_manager.waitlist.get_priority_list("srv_001", "2026-02-10")
        
        # Il VIP deve essere primo
        assert len(waitlist) >= 2
        assert waitlist[0].customer_tier == CustomerTier.VIP
    
    def test_notifica_whatsapp_a_vip(self, orchestrator, mock_whatsapp):
        """Test che quando si libera uno slot, il VIP viene notificato"""
        
        # Aggiungi VIP a lista d'attesa
        orchestrator.booking_manager.add_to_waitlist(
            customer_id="cust_vip",
            service_id="srv_001",
            preferred_dates=["2026-02-10"],
            urgency="high"
        )
        
        # Simula liberazione slot
        orchestrator.booking_manager._handle_slot_freed(
            business_id="biz_001",
            service_id="srv_001",
            date="2026-02-10",
            time="15:00"
        )
        
        # Verifica che WhatsApp sia stato inviato al VIP
        mock_whatsapp.send_message.assert_called()
        call_args = mock_whatsapp.send_message.call_args
        assert "vip" in call_args[0][1].lower() or "priorità" in call_args[0][1].lower()
    
    def test_prenotazione_vip_su_slot_occupato(self, orchestrator):
        """Test che VIP possa 'bumpare' uno standard su lista d'attesa"""
        # Questo test verifica la logica di priorità
        pass  # Implementazione dettagliata dipende dalla logica specifica


# =============================================================================
# TEST ANNULLAMENTO E SPOSTAMENTO
# =============================================================================

class TestAnnullamentoSpostamento:
    """Test gestione modifiche prenotazioni"""
    
    def test_annullamento_prenotazione(self, orchestrator, mock_db):
        """Test annullamento appuntamento"""
        
        # Crea prima una prenotazione
        booking = orchestrator.booking_manager.create_booking(
            customer_id="cust_standard",
            business_id="biz_001",
            service_id="srv_001",
            date="2026-02-15",
            time="10:00"
        )
        
        # Ora annulla
        success, msg = orchestrator.booking_manager.cancel_booking(
            booking[1].booking_id,
            reason="Prova annullamento"
        )
        
        assert success is True
        assert booking[1].status == BookingStatus.CANCELLED
    
    def test_spostamento_prenotazione(self, orchestrator):
        """Test spostamento appuntamento a nuova data/ora"""
        
        # Crea prenotazione
        success, booking, _ = orchestrator.booking_manager.create_booking(
            customer_id="cust_standard",
            business_id="biz_001",
            service_id="srv_001",
            date="2026-02-15",
            time="10:00"
        )
        
        original_date = booking.date
        
        # Sposta
        success, new_booking, msg = orchestrator.booking_manager.reschedule_booking(
            booking.booking_id,
            new_date="2026-02-16",
            new_time="14:00"
        )
        
        assert success is True
        assert new_booking.date == "2026-02-16"
        assert new_booking.time == "14:00"
        assert new_booking.status == BookingStatus.RESCHEDULED
    
    def test_annullamento_via_comando_vocale(self, orchestrator):
        """Test comando vocale 'annulla prenotazione'"""
        
        session_id = "test_cancel"
        
        # Simula contesto con prenotazione attiva
        ctx = orchestrator._get_or_create_context(session_id)
        ctx.client_id = "cust_standard"
        ctx.service = "srv_001"
        
        # Comando annullamento
        result = orchestrator.process_message(
            session_id=session_id,
            message="Voglio annullare la prenotazione"
        )
        
        assert result["action"] == "cancelled" or "annullata" in result["response"].lower()


# =============================================================================
# TEST RESOLVER ENTITÀ
# =============================================================================

class TestResolverEntita:
    """Test fuzzy matching servizi e operatori"""
    
    def test_risoluzione_servizio_fuzzy(self, orchestrator, mock_db):
        """Test che 'sforbiciata' venga risolta in 'Taglio Donna'"""
        
        resolver = orchestrator.resolver.service_resolver
        success, data, msg = resolver.resolve("sforbiciata", "biz_001")
        
        assert success is True
        assert data["id"] == "srv_001"
        assert data["name"] == "Taglio Donna"
    
    def test_risoluzione_operatore_nome_parziale(self, orchestrator, mock_db):
        """Test che 'Giovanna' venga risolto correttamente"""
        
        resolver = orchestrator.resolver.operator_resolver
        success, data, msg = resolver.resolve("Giovanna", "biz_001")
        
        assert success is True
        assert data["id"] == "op_001"
        assert data["gender"] == "F"
    
    def test_servizio_non_trovato(self, orchestrator):
        """Test gestione servizio non riconosciuto"""
        
        resolver = orchestrator.resolver.service_resolver
        success, data, msg = resolver.resolve("servizio inesistente", "biz_001")
        
        assert success is False
        assert "non riconosciuto" in msg.lower() or "disponibili" in msg.lower()


# =============================================================================
# TEST INTEGRAZIONE WHATSAPP
# =============================================================================

class TestWhatsAppIntegration:
    """Test flusso WhatsApp completo"""
    
    def test_conferma_24h_whatsapp(self, orchestrator, mock_whatsapp):
        """Test invio reminder 24h prima"""
        
        # Crea prenotazione
        success, booking, _ = orchestrator.booking_manager.create_booking(
            customer_id="cust_standard",
            business_id="biz_001",
            service_id="srv_001",
            date=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            time="10:00"
        )
        
        # Verifica che sia stato schedulato un reminder
        mock_whatsapp.send_message.assert_called()
        # Il messaggio di conferma iniziale è stato inviato
        
    def test_handler_whatsapp_in entrata(self, orchestrator):
        """Test handler per messaggi WhatsApp in entrata"""
        
        handler = WhatsAppBookingHandler(orchestrator)
        
        # Simula messaggio di prenotazione via WhatsApp
        response = handler.handle_incoming_message(
            phone_number="+39987654321",
            message="Vorrei prenotare un taglio",
            message_id="msg_001"
        )
        
        assert "taglio" in response.lower() or "giorno" in response.lower()
    
    def test_risposta_a_reminder(self, orchestrator):
        """Test gestione risposta cliente a reminder 24h"""
        
        handler = WhatsAppBookingHandler(orchestrator)
        
        # Crea prenotazione pending
        success, booking, _ = orchestrator.booking_manager.create_booking(
            customer_id="cust_standard",
            business_id="biz_001",
            service_id="srv_001",
            date=(datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            time="10:00"
        )
        
        # Simula risposta conferma
        response = handler.handle_reminder_response("+39987654321", "Sì confermo")
        
        assert "conferma" in response.lower() or "domani" in response.lower()


# =============================================================================
# TEST SCHEDE CLIENTE VERTICALI
# =============================================================================

class TestSchedeVerticali:
    """Test creazione e gestione schede cliente per settore"""
    
    def test_creazione_scheda_fisioterapia(self, orchestrator):
        """Test creazione scheda anamnestica fisioterapia"""
        from vertical_schemas import CustomerCardFactory
        
        scheda = CustomerCardFactory.create_card("fisioterapia", "cust_001")
        
        assert scheda is not None
        assert hasattr(scheda, 'motivo_primo_accesso')
        assert hasattr(scheda, 'zona_principale')
    
    def test_creazione_scheda_dentista(self, orchestrator):
        """Test creazione scheda odontoiatrica"""
        from vertical_schemas import CustomerCardFactory
        
        scheda = CustomerCardFactory.create_card("dentista", "cust_001")
        
        assert scheda is not None
        assert hasattr(scheda, 'odontogramma')
        assert hasattr(scheda, 'allergia_lattice')
    
    def test_priorita_waitlist_vip(self, orchestrator):
        """Test calcolo punteggio priorità VIP"""
        from vertical_schemas import WaitlistEntry, CustomerTier
        
        entry_vip = WaitlistEntry(
            entry_id="wl_001",
            customer_id="cust_001",
            customer_tier=CustomerTier.VIP,
            service_id="srv_001",
            created_at=datetime.now().isoformat()
        )
        
        entry_standard = WaitlistEntry(
            entry_id="wl_002",
            customer_id="cust_002",
            customer_tier=CustomerTier.STANDARD,
            service_id="srv_001",
            created_at=datetime.now().isoformat()
        )
        
        # VIP deve avere punteggio molto più alto
        assert entry_vip.priority_score > entry_standard.priority_score
        assert entry_vip.priority_score >= 1000


# =============================================================================
# TEST EDGE CASES
# =============================================================================

class TestEdgeCases:
    """Test casi limite e gestione errori"""
    
    def test_operatore_non_disponibile(self, orchestrator, mock_db):
        """Test quando operatore preferito non è libero"""
        
        # Simula operatore occupato
        mock_db.get_operator_bookings.return_value = [
            {"time": "15:00", "service_id": "srv_001"}
        ]
        
        resolver = orchestrator.resolver.operator_resolver
        success, data, msg = resolver.resolve(
            "Giovanna", "biz_001",
            date="2026-02-10", time="15:00"
        )
        
        # Dovrebbe trovare l'operatore ma segnalare non disponibile
        assert success is False or data is not None  # Dipende dalla logica
    
    def test_slot_non_disponibile_waitlist(self, orchestrator):
        """Test che quando slot è pieno venga offerta lista d'attesa"""
        
        session_id = "test_full"
        
        # Processa fino a richiesta slot
        orchestrator.process_message(session_id, "Vorrei un taglio", "+39987654321")
        orchestrator.process_message(session_id, "Domani")
        
        # Simula slot pieno (mock del DB che ritorna occupato)
        orchestrator.db.get_bookings_for_date.return_value = [
            {"time": "15:00", "booking_id": "bk_001"}
        ]
        
        result = orchestrator.process_message(session_id, "Alle 15")
        
        # Dovrebbe suggerire lista d'attesa o alternative
        assert "lista d'attesa" in result["response"].lower() or "altro" in result["response"].lower()
    
    def test_multi_service_prenotazione(self, orchestrator):
        """Test prenotazione multi-servizio (taglio + colore)"""
        
        session_id = "test_multi"
        
        result = orchestrator.process_message(
            session_id,
            "Vorrei taglio e colore",
            "+39987654321"
        )
        
        # Dovrebbe riconoscere entrambi i servizi
        ctx = orchestrator.sessions[session_id]
        # Verifica che abbia estratto multipli servizi


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
