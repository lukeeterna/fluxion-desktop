"""
FLUXION Voice Agent - Booking Orchestrator
Integra State Machine + Resolver + Booking Manager + VIP/Waitlist
"""

from typing import Optional, Dict, List, Tuple, Any
from datetime import datetime
import logging

from booking_state_machine import BookingStateMachine, BookingState, BookingContext, StateMachineResult
from booking_manager import BookingManager, BookingStatus
from service_resolver import ServiceResolver, OperatorResolver, EntityResolverPipeline
from vertical_schemas import CustomerProfile, CustomerTier, WaitlistEntry

logger = logging.getLogger(__name__)


class BookingOrchestrator:
    """
    Orchestratore completo per il flusso di prenotazione.
    
    Collega:
    1. State Machine (gestione stati conversazionali)
    2. Entity Resolver (testo → ID database)
    3. Booking Manager (CRUD prenotazioni + VIP)
    4. WhatsApp (notifiche)
    """
    
    def __init__(self, db_connection, whatsapp_service=None, business_id: str = None):
        self.db = db_connection
        self.whatsapp = whatsapp_service
        self.business_id = business_id
        
        # Componenti
        self.state_machine = BookingStateMachine()
        self.booking_manager = BookingManager(db_connection, whatsapp_service)
        self.resolver = EntityResolverPipeline(db_connection)
        
        # Cache contesto conversazione
        self.sessions: Dict[str, BookingContext] = {}
    
    # ========================================================================
    # FLUSSO PRINCIPALE
    # ========================================================================
    
    def process_message(
        self,
        session_id: str,
        message: str,
        customer_phone: Optional[str] = None,
        context_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Processa un messaggio nel flusso di prenotazione.
        
        Returns:
            {
                "response": str,
                "state": str,
                "booking_id": Optional[str],
                "completed": bool,
                "requires_action": Optional[str],
                "action_params": Dict
            }
        """
        # 1. Recupera o crea contesto
        ctx = self._get_or_create_context(session_id, customer_phone)
        
        # 2. Se è un comando speciale (annulla, sposta, etc.)
        action_result = self._check_special_commands(message, ctx)
        if action_result:
            return action_result
        
        # 3. Processa con state machine
        result = self.state_machine.process(message, ctx)
        
        # 4. Se state machine richiede lookup DB, risolvi entità
        if result.needs_db_lookup:
            self._resolve_entities(ctx, result.lookup_params)
        
        # 5. Se booking completo, salva nel DB
        if result.next_state == BookingState.COMPLETED:
            save_result = self._save_booking(ctx)
            result.response += f"\n{save_result['message']}"
            
            return {
                "response": result.response,
                "state": result.next_state.value,
                "booking_id": save_result.get("booking_id"),
                "completed": True,
                "requires_action": None
            }
        
        # 6. Salva contesto aggiornato
        self.sessions[session_id] = ctx
        
        return {
            "response": result.response,
            "state": result.next_state.value,
            "booking_id": None,
            "completed": False,
            "requires_action": result.lookup_type if result.needs_db_lookup else None,
            "action_params": result.lookup_params
        }
    
    # ========================================================================
    # GESTIONE COMANDI SPECIALI
    # ========================================================================
    
    def _check_special_commands(self, message: str, ctx: BookingContext) -> Optional[Dict]:
        """
        Controlla se il messaggio è un comando speciale
        (annullamento, spostamento, richiesta operatore).
        """
        msg_lower = message.lower()
        
        # Comando: Annulla prenotazione
        if any(kw in msg_lower for kw in ["annulla", "disdico", "cancella"]):
            return self._handle_cancel_request(ctx)
        
        # Comando: Sposta appuntamento
        if any(kw in msg_lower for kw in ["sposta", "cambio data", "cambio orario"]):
            return self._handle_reschedule_request(ctx, message)
        
        # Comando: Lista d'attesa
        if any(kw in msg_lower for kw in ["lista d'attesa", "mettimi in attesa", "aspetto"]):
            return self._handle_waitlist_request(ctx)
        
        return None
    
    def _handle_cancel_request(self, ctx: BookingContext) -> Dict:
        """Gestisce richiesta annullamento"""
        # Se c'è un booking attivo nel contesto
        if ctx.client_id and ctx.service:
            # Cerca booking futuri
            bookings = self.booking_manager.get_customer_bookings(
                ctx.client_id,
                from_date=datetime.now().isoformat()[:10]
            )
            
            if bookings:
                # Annulla il più recente
                last_booking = bookings[-1]
                success, msg = self.booking_manager.cancel_booking(
                    last_booking.booking_id,
                    reason="Richiesta cliente"
                )
                
                return {
                    "response": f"Ho annullato la sua prenotazione del {last_booking.date} alle {last_booking.time}. {msg}",
                    "state": BookingState.IDLE.value,
                    "booking_id": last_booking.booking_id,
                    "completed": True,
                    "action": "cancelled"
                }
        
        return {
            "response": "Non ho trovato prenotazioni attive da annullare. Posso aiutarla con una nuova prenotazione?",
            "state": BookingState.IDLE.value,
            "completed": False
        }
    
    def _handle_reschedule_request(self, ctx: BookingContext, message: str) -> Dict:
        """Gestisce richiesta spostamento"""
        # Estrai nuova data/ora dal messaggio
        from entity_extractor import extract_date, extract_time
        
        new_date = extract_date(message)
        new_time = extract_time(message)
        
        if not new_date or not new_time:
            return {
                "response": "Per spostare l'appuntamento mi servono la nuova data e ora. Per esempio: 'Sposta a domani alle 15'.",
                "state": ctx.state.value,
                "completed": False
            }
        
        # Cerca booking esistente
        if ctx.client_id:
            bookings = self.booking_manager.get_customer_bookings(
                ctx.client_id,
                status=BookingStatus.CONFIRMED
            )
            
            if bookings:
                last_booking = bookings[-1]
                success, new_booking, msg = self.booking_manager.reschedule_booking(
                    last_booking.booking_id,
                    new_date,
                    new_time
                )
                
                if success:
                    return {
                        "response": f"Appuntamento spostato! Nuovo orario: {new_date} alle {new_time}.",
                        "state": BookingState.IDLE.value,
                        "booking_id": new_booking.booking_id,
                        "completed": True,
                        "action": "rescheduled"
                    }
                else:
                    return {
                        "response": f"Non ho potuto spostare l'appuntamento: {msg}",
                        "state": ctx.state.value,
                        "completed": False
                    }
        
        return {
            "response": "Non ho trovato un appuntamento confermato da spostare. Vuole fare una nuova prenotazione?",
            "state": BookingState.IDLE.value,
            "completed": False
        }
    
    def _handle_waitlist_request(self, ctx: BookingContext) -> Dict:
        """Aggiunge cliente alla lista d'attesa con priorità"""
        if not ctx.service or not ctx.date:
            return {
                "response": "Per metterla in lista d'attesa ho bisogno di sapere che servizio desidera e per quale giorno.",
                "state": ctx.state.value,
                "completed": False
            }
        
        # Risolvi servizio in ID
        success, service_data, _ = self.resolver.service_resolver.resolve(
            ctx.service, self.business_id
        )
        
        if not success:
            return {
                "response": "Non ho capito bene che servizio desidera. Può ripetere?",
                "state": BookingState.WAITING_SERVICE.value,
                "completed": False
            }
        
        # Recupera profilo cliente (per tier VIP)
        customer = self._get_or_create_customer(ctx)
        
        # Aggiungi a lista d'attesa
        success, msg = self.booking_manager.add_to_waitlist(
            customer_id=customer.customer_id,
            service_id=service_data["id"],
            preferred_dates=[ctx.date],
            flexibility_days=7,
            urgency="normal",
            preferred_operator_id=ctx.operator_id
        )
        
        tier_msg = ""
        if customer.tier in [CustomerTier.VIP, CustomerTier.PLATINUM, CustomerTier.GOLD]:
            tier_msg = f" Ha priorità {customer.tier.value.upper()}."
        
        return {
            "response": f"L'ho aggiunto alla lista d'attesa.{tier_msg} La contatteremo appena si libera uno slot!",
            "state": BookingState.IDLE.value,
            "completed": True,
            "action": "waitlist_added"
        }
    
    # ========================================================================
    # RESOLVER INTEGRATION
    # ========================================================================
    
    def _resolve_entities(self, ctx: BookingContext, lookup_params: Dict):
        """Risolve entità testuali in ID database"""
        if not self.business_id:
            return
        
        # Risolvi servizio
        if ctx.service and not ctx.service.startswith("srv_"):  # Se non è già un ID
            success, data, msg = self.resolver.service_resolver.resolve(
                ctx.service, self.business_id
            )
            if success:
                ctx.service = data["id"]  # Salva ID nel contesto
                ctx.service_display = data["name"]
        
        # Risolvi operatore
        if ctx.operator_name and not ctx.operator_id:
            success, data, msg = self.resolver.operator_resolver.resolve(
                ctx.operator_name, self.business_id
            )
            if success:
                ctx.operator_id = data["id"]
                ctx.operator_name = data["name"]
    
    def _save_booking(self, ctx: BookingContext) -> Dict:
        """Salva prenotazione nel database"""
        if not self.business_id:
            return {"success": False, "message": "Business ID non configurato"}
        
        # Crea/recupera cliente
        customer = self._get_or_create_customer(ctx)
        
        # Se servizio è ancora testo, risolvi
        service_id = ctx.service
        if not service_id.startswith("srv_"):
            success, data, _ = self.resolver.service_resolver.resolve(
                service_id, self.business_id
            )
            if success:
                service_id = data["id"]
        
        # Crea booking
        success, booking, msg = self.booking_manager.create_booking(
            customer_id=customer.customer_id,
            business_id=self.business_id,
            service_id=service_id,
            date=ctx.date,
            time=ctx.time,
            operator_id=ctx.operator_id,
            notes=ctx.notes
        )
        
        if success:
            return {
                "success": True,
                "booking_id": booking.booking_id,
                "message": f"Prenotazione confermata! ID: {booking.booking_id}"
            }
        
        # Se fallisce per slot occupato, offri lista d'attesa
        if "non disponibile" in msg.lower():
            return {
                "success": False,
                "message": "Lo slot non è più disponibile. Posso metterla in lista d'attesa prioritaria?",
                "suggest_waitlist": True
            }
        
        return {"success": False, "message": msg}
    
    # ========================================================================
    # UTILITY
    # ========================================================================
    
    def _get_or_create_context(
        self,
        session_id: str,
        customer_phone: Optional[str] = None
    ) -> BookingContext:
        """Recupera o crea contesto sessione"""
        if session_id in self.sessions:
            return self.sessions[session_id]
        
        ctx = BookingContext()
        
        # Se c'è telefono, recupera cliente esistente
        if customer_phone:
            customer_data = self.db.get_customer_by_phone(customer_phone)
            if customer_data:
                ctx.client_id = customer_data["id"]
                ctx.client_name = customer_data["name"]
                ctx.client_phone = customer_phone
        
        self.sessions[session_id] = ctx
        return ctx
    
    def _get_or_create_customer(self, ctx: BookingContext) -> CustomerProfile:
        """Recupera o crea profilo cliente"""
        if ctx.client_id:
            data = self.db.get_customer(ctx.client_id)
            if data:
                return CustomerProfile(**data)
        
        # Crea nuovo cliente
        customer_id = f"cust_{datetime.now().timestamp()}"
        customer = CustomerProfile(
            customer_id=customer_id,
            phone=ctx.client_phone or "",
            name=ctx.client_name or "",
            surname=ctx.client_surname or "",
            tier=CustomerTier.STANDARD
        )
        
        # Salva nel DB
        self.db.save_customer({
            "id": customer_id,
            "phone": customer.phone,
            "name": customer.name,
            "surname": customer.surname,
            "tier": customer.tier.value
        })
        
        ctx.client_id = customer_id
        return customer
    
    def get_available_slots(
        self,
        service_id: str,
        date: str,
        operator_id: Optional[str] = None
    ) -> List[str]:
        """API pubblica per recuperare slot disponibili"""
        return self.booking_manager.get_available_slots(
            self.business_id, service_id, date, operator_id
        )
    
    def get_customer_bookings(self, customer_id: str) -> List[Dict]:
        """API pubblica per recuperare prenotazioni cliente"""
        bookings = self.booking_manager.get_customer_bookings(customer_id)
        return [b.to_dict() for b in bookings]
    
    def cancel_booking_by_id(self, booking_id: str, reason: str = "") -> Tuple[bool, str]:
        """API pubblica per annullamento"""
        return self.booking_manager.cancel_booking(booking_id, reason)


# =============================================================================
# HANDLER WHATSAPP INTEGRATION
# =============================================================================

class WhatsAppBookingHandler:
    """Handler per messaggi WhatsApp in entrata"""
    
    def __init__(self, orchestrator: BookingOrchestrator):
        self.orchestrator = orchestrator
    
    def handle_incoming_message(
        self,
        phone_number: str,
        message: str,
        message_id: str
    ) -> str:
        """
        Gestisce messaggio WhatsApp in entrata.
        Usa il numero di telefono come session_id.
        """
        # Usa phone come session_id per continuità
        result = self.orchestrator.process_message(
            session_id=phone_number,
            message=message,
            customer_phone=phone_number
        )
        
        return result["response"]
    
    def handle_reminder_response(self, phone_number: str, response: str) -> str:
        """
        Gestisce risposta a reminder 24h.
        """
        response_lower = response.lower()
        
        if any(kw in response_lower for kw in ["sì", "ok", "va bene", "confermo"]):
            # Trova booking e conferma
            bookings = self.orchestrator.get_customer_bookings(phone_number)
            for b in bookings:
                if b["status"] == "pending":
                    self.orchestrator.booking_manager.confirm_booking(b["booking_id"])
                    return "Grazie per la conferma! A domani! 👋"
        
        elif any(kw in response_lower for kw in ["no", "annulla", "disdico"]):
            # Annulla
            bookings = self.orchestrator.get_customer_bookings(phone_number)
            for b in bookings:
                if b["status"] in ["pending", "confirmed"]:
                    self.orchestrator.cancel_booking_by_id(b["booking_id"], "Disdetta cliente")
                    return "Prenotazione annullata. Posso aiutarla con una nuova data?"
        
        return "Non ho capito. Può ripetere? (Conferma/Annulla)"


# =============================================================================
# ESEMPI FLUSSO COMPLETO
# =============================================================================

"""
FLUSSO 1: Prenotazione Standard
-------------------------------
Utente: "Vorrei prenotare un taglio"
→ Orchestrator: resolver "taglio" → ID srv_123
→ Response: "Bene, Taglio! Per quale giorno?"

Utente: "Domani"
→ Orchestrator: extract_date → 2026-02-05
→ Response: "Domani, perfetto. A che ora?"

Utente: "Con Giovanna alle 15"
→ Orchestrator: 
  - resolver "Giovanna" → ID op_456
  - check availability: OK
→ Response: "Alle 15 con Giovanna. Confermo?"

Utente: "Sì"
→ Orchestrator: BookingManager.create_booking()
→ Response: "Prenotazione confermata! ID: bk_789"
→ WhatsApp: invia conferma

FLUSSO 2: VIP in Lista d'Attesa
-------------------------------
Utente: "Vorrei prenotare per domani ma sono occupato"
→ Orchestrator: check availability → Slot pieni
→ Response: "Non ho disponibilità. Posso metterla in lista d'attesa?"

Utente: "Sì"
→ Orchestrator: 
  - get customer tier → VIP
  - WaitlistManager.add_to_waitlist(priority=HIGH)
→ Response: "In lista d'attesa con priorità VIP. La contatteremo!"

[24h dopo si libera uno slot]
→ WhatsApp: "🌟 Ciao! Si è liberato uno slot per te..."
→ Utente risponde: "PRENOTA"
→ Orchestrator: crea booking automatico per VIP

FLUSSO 3: Annullamento
----------------------
Utente: "Devo disdire l'appuntamento"
→ Orchestrator: trova booking → cancel_booking()
→ WhatsApp: notifica annullamento
→ Check waitlist: trova VIP in attesa
→ WhatsApp a VIP: "Si è liberato uno slot!"
"""
