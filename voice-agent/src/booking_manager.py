"""
FLUXION Voice Agent - Booking Manager
Gestisce prenotazioni, annullamenti, spostamenti e lista d'attesa VIP
"""

from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid

from vertical_schemas import (
    CustomerTier, WaitlistEntry, WaitlistManager, 
    CustomerProfile, CustomerCardFactory
)


class BookingStatus(Enum):
    PENDING = "pending"           # Appena creata, non confermata
    CONFIRMED = "confirmed"       # Confermata
    COMPLETED = "completed"       # Effettuata
    CANCELLED = "cancelled"       # Annullata
    NO_SHOW = "no_show"          # Non presentato
    RESCHEDULED = "rescheduled"  # Spostata


@dataclass
class Booking:
    """Modello prenotazione completo"""
    booking_id: str
    customer_id: str
    customer_tier: CustomerTier
    business_id: str
    
    # Servizio
    service_id: str
    service_name: str
    duration_minutes: int
    
    # Data/Orario
    date: str  # YYYY-MM-DD
    time: str  # HH:MM
    end_time: str  # HH:MM calcolato
    
    # Operatore (opzionale)
    operator_id: Optional[str] = None
    operator_name: Optional[str] = None
    
    # Stato
    status: BookingStatus = BookingStatus.PENDING
    created_at: str = ""
    updated_at: str = ""
    
    # Note
    notes: str = ""
    source: str = "voice"  # "voice", "whatsapp", "web"
    
    # Cronologia modifiche
    history: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "booking_id": self.booking_id,
            "customer_id": self.customer_id,
            "customer_tier": self.customer_tier.value,
            "service_id": self.service_id,
            "service_name": self.service_name,
            "date": self.date,
            "time": self.time,
            "operator_id": self.operator_id,
            "operator_name": self.operator_name,
            "status": self.status.value,
            "notes": self.notes
        }


class BookingManager:
    """Gestore centrale prenotazioni"""
    
    def __init__(self, db_connection, whatsapp_service=None):
        self.db = db_connection
        self.whatsapp = whatsapp_service
        self.waitlist = WaitlistManager(db_connection)
    
    # ========================================================================
    # OPERAZIONI CRUD
    # ========================================================================
    
    def create_booking(
        self,
        customer_id: str,
        business_id: str,
        service_id: str,
        date: str,
        time: str,
        operator_id: Optional[str] = None,
        notes: str = ""
    ) -> Tuple[bool, Booking, str]:
        """
        Crea nuova prenotazione.
        
        Returns:
            (success, booking_object, message)
        """
        # 1. Recupera profilo cliente (per tier VIP)
        customer = self._get_customer_profile(customer_id)
        if not customer:
            return False, None, "Cliente non trovato"
        
        # 2. Verifica disponibilità
        available, conflict = self._check_availability(
            business_id, service_id, date, time, operator_id
        )
        
        if not available:
            # Slot non disponibile → trova alternative
            alternatives = self._find_alternative_slots(
                business_id, service_id, date, time, operator_id
            )
            
            # Costruisci risposta con alternative e opzione waitlist
            return False, None, {
                "error": "Slot non disponibile",
                "alternatives": alternatives,
                "can_waitlist": True,
                "message": self._build_alternatives_message(alternatives, date, time)
            }
        
        # 3. Crea booking
        booking_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        # Recupera info servizio
        service_info = self._get_service_info(service_id)
        operator_info = self._get_operator_info(operator_id) if operator_id else None
        
        # Calcola orario fine
        end_time = self._calculate_end_time(time, service_info["duration"])
        
        booking = Booking(
            booking_id=booking_id,
            customer_id=customer_id,
            customer_tier=customer.tier,
            business_id=business_id,
            service_id=service_id,
            service_name=service_info["name"],
            duration_minutes=service_info["duration"],
            date=date,
            time=time,
            end_time=end_time,
            operator_id=operator_id,
            operator_name=operator_info["name"] if operator_info else None,
            status=BookingStatus.PENDING,
            created_at=now,
            updated_at=now,
            notes=notes,
            history=[{"action": "created", "timestamp": now}]
        )
        
        # 4. Salva nel DB
        self.db.save_booking(booking)
        
        # 5. Invia conferma WhatsApp (se configurato)
        if self.whatsapp:
            self._send_booking_confirmation(booking, customer)
        
        return True, booking, "Prenotazione creata con successo"
    
    def cancel_booking(
        self, 
        booking_id: str, 
        reason: str = "",
        cancelled_by: str = "customer"  # "customer", "operator", "system"
    ) -> Tuple[bool, str]:
        """
        Annulla prenotazione esistente.
        Se c'è lista d'attesa, notifica il prossimo VIP.
        """
        booking = self.db.get_booking(booking_id)
        if not booking:
            return False, "Prenotazione non trovata"
        
        if booking.status == BookingStatus.CANCELLED:
            return False, "Prenotazione già annullata"
        
        # Aggiorna stato
        now = datetime.now().isoformat()
        booking.status = BookingStatus.CANCELLED
        booking.updated_at = now
        booking.history.append({
            "action": "cancelled",
            "timestamp": now,
            "reason": reason,
            "by": cancelled_by
        })
        
        self.db.update_booking(booking)
        
        # Libera slot e controlla lista d'attesa
        self._handle_slot_freed(
            booking.business_id,
            booking.service_id,
            booking.date,
            booking.time
        )
        
        # Notifica annullamento
        customer = self._get_customer_profile(booking.customer_id)
        if self.whatsapp and customer:
            self._send_cancellation_notice(booking, customer)
        
        return True, "Prenotazione annullata"
    
    def reschedule_booking(
        self,
        booking_id: str,
        new_date: str,
        new_time: str,
        new_operator_id: Optional[str] = None
    ) -> Tuple[bool, Booking, str]:
        """
        Sposta prenotazione a nuovo slot.
        Mantiene lo stesso ID ma aggiorna data/ora.
        """
        booking = self.db.get_booking(booking_id)
        if not booking:
            return False, None, "Prenotazione non trovata"
        
        # Salva vecchi dati
        old_date = booking.date
        old_time = booking.time
        
        # Verifica disponibilità nuovo slot
        available, _ = self._check_availability(
            booking.business_id,
            booking.service_id,
            new_date,
            new_time,
            new_operator_id or booking.operator_id
        )
        
        if not available:
            return False, None, "Nuovo slot non disponibile"
        
        # Aggiorna booking
        now = datetime.now().isoformat()
        booking.date = new_date
        booking.time = new_time
        booking.end_time = self._calculate_end_time(new_time, booking.duration_minutes)
        
        if new_operator_id:
            op_info = self._get_operator_info(new_operator_id)
            booking.operator_id = new_operator_id
            booking.operator_name = op_info["name"] if op_info else None
        
        booking.status = BookingStatus.RESCHEDULED
        booking.updated_at = now
        booking.history.append({
            "action": "rescheduled",
            "timestamp": now,
            "from": {"date": old_date, "time": old_time},
            "to": {"date": new_date, "time": new_time}
        })
        
        self.db.update_booking(booking)
        
        # Libera vecchio slot → lista d'attesa
        self._handle_slot_freed(
            booking.business_id,
            booking.service_id,
            old_date,
            old_time
        )
        
        # Notifica
        customer = self._get_customer_profile(booking.customer_id)
        if self.whatsapp and customer:
            self._send_reschedule_notice(booking, customer, old_date, old_time)
        
        return True, booking, "Appuntamento spostato"
    
    def confirm_booking(self, booking_id: str) -> Tuple[bool, str]:
        """Conferma prenotazione pending (es: dopo reminder 24h)"""
        booking = self.db.get_booking(booking_id)
        if not booking:
            return False, "Prenotazione non trovata"
        
        booking.status = BookingStatus.CONFIRMED
        booking.updated_at = datetime.now().isoformat()
        self.db.update_booking(booking)
        
        return True, "Prenotazione confermata"
    
    # ========================================================================
    # LISTA D'ATTESA
    # ========================================================================
    
    def add_to_waitlist(
        self,
        customer_id: str,
        service_id: str,
        preferred_dates: List[str],
        flexibility_days: int = 7,
        urgency: str = "normal",
        preferred_operator_id: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Aggiunge cliente alla lista d'attesa con priorità VIP"""
        
        customer = self._get_customer_profile(customer_id)
        if not customer:
            return False, "Cliente non trovato"
        
        entry = WaitlistEntry(
            entry_id=str(uuid.uuid4()),
            customer_id=customer_id,
            customer_tier=customer.tier,
            service_id=service_id,
            preferred_operator_id=preferred_operator_id,
            preferred_dates=preferred_dates,
            flexibility_days=flexibility_days,
            urgency=urgency,
            created_at=datetime.now().isoformat()
        )
        
        success = self.waitlist.add_to_waitlist(entry)
        
        if success:
            # Notifica al cliente
            msg = f"Hai sido aggiunto alla lista d'attesa con priorità {customer.tier.value}"
            return True, msg
        
        return False, "Errore aggiunta lista d'attesa"
    
    def check_waitlist_priority(
        self,
        service_id: str,
        date: str,
        time: str
    ) -> Optional[str]:
        """
        Verifica se c'è un VIP in lista d'attesa per questo slot.
        Se sì, riserva lo slot per lui prima di offrirlo ad altri.
        """
        priority_customer = self.waitlist.notify_slot_available(service_id, date, time)
        return priority_customer
    
    # ========================================================================
    # UTILITY
    # ========================================================================
    
    def get_customer_bookings(
        self,
        customer_id: str,
        status: Optional[BookingStatus] = None,
        from_date: Optional[str] = None
    ) -> List[Booking]:
        """Recupera prenotazioni cliente"""
        return self.db.get_customer_bookings(customer_id, status, from_date)
    
    def get_available_slots(
        self,
        business_id: str,
        service_id: str,
        date: str,
        operator_id: Optional[str] = None
    ) -> List[str]:
        """
        Restituisce slot disponibili per data/servizio.
        Tiene conto della durata del servizio.
        """
        # Recupera durata servizio
        service = self._get_service_info(service_id)
        duration = service["duration"]
        
        # Recupera orari apertura
        business_hours = self.db.get_business_hours(business_id, date)
        
        # Recupera booking esistenti
        existing = self.db.get_bookings_for_date(business_id, date, operator_id)
        
        # Calcola slot liberi
        slots = self._calculate_available_slots(
            business_hours,
            existing,
            duration
        )
        
        return slots
    
    def get_preferred_operator_availability(
        self,
        operator_id: str,
        date: str
    ) -> List[str]:
        """Disponibilità operatore specifico"""
        return self.db.get_operator_schedule(operator_id, date)
    
    # ========================================================================
    # METODI PRIVATI
    # ========================================================================
    
    def _get_customer_profile(self, customer_id: str) -> Optional[CustomerProfile]:
        """Recupera profilo cliente dal DB"""
        data = self.db.get_customer(customer_id)
        if data:
            return CustomerProfile(**data)
        return None
    
    def _get_service_info(self, service_id: str) -> Dict:
        """Recupera info servizio"""
        return self.db.get_service(service_id) or {
            "name": "Servizio",
            "duration": 30
        }
    
    def _get_operator_info(self, operator_id: str) -> Optional[Dict]:
        """Recupera info operatore"""
        return self.db.get_operator(operator_id)
    
    def _check_availability(
        self,
        business_id: str,
        service_id: str,
        date: str,
        time: str,
        operator_id: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """Verifica se slot è disponibile"""
        # Verifica sovrapposizioni
        existing = self.db.get_bookings_for_date(business_id, date, operator_id)
        
        for booking in existing:
            if booking.time == time:
                return False, booking.booking_id
        
        return True, None
    
    def _calculate_end_time(self, start_time: str, duration_minutes: int) -> str:
        """Calcola orario fine"""
        start = datetime.strptime(start_time, "%H:%M")
        end = start + timedelta(minutes=duration_minutes)
        return end.strftime("%H:%M")
    
    def _calculate_available_slots(
        self,
        business_hours: Dict,
        existing_bookings: List[Booking],
        service_duration: int
    ) -> List[str]:
        """Calcola slot liberi"""
        # Implementazione base
        open_time = datetime.strptime(business_hours["open"], "%H:%M")
        close_time = datetime.strptime(business_hours["close"], "%H:%M")
        
        slots = []
        current = open_time
        
        while current + timedelta(minutes=service_duration) <= close_time:
            slot_str = current.strftime("%H:%M")
            
            # Verifica se slot è occupato
            occupied = any(b.time == slot_str for b in existing_bookings)
            
            if not occupied:
                slots.append(slot_str)
            
            current += timedelta(minutes=30)  # Slot ogni 30 min
        
        return slots
    
    def _find_alternative_slots(
        self,
        business_id: str,
        service_id: str,
        preferred_date: str,
        preferred_time: str,
        operator_id: Optional[str] = None,
        max_alternatives: int = 3
    ) -> List[Dict]:
        """
        Trova slot alternativi quando quello preferito è occupato.
        Cerca nello stesso giorno prima, poi nei giorni successivi.
        """
        alternatives = []
        service_info = self._get_service_info(service_id)
        duration = service_info["duration"]
        
        # 1. Cerca nello stesso giorno (prima prima, poi dopo)
        same_day_slots = self.get_available_slots(business_id, service_id, preferred_date, operator_id)
        
        preferred_dt = datetime.strptime(preferred_time, "%H:%M")
        
        # Slot precedenti (più vicini all'orario richiesto)
        earlier_slots = [s for s in same_day_slots if datetime.strptime(s, "%H:%M") < preferred_dt]
        earlier_slots.sort(key=lambda s: preferred_dt - datetime.strptime(s, "%H:%M"))
        
        # Slot successivi
        later_slots = [s for s in same_day_slots if datetime.strptime(s, "%H:%M") > preferred_dt]
        later_slots.sort(key=lambda s: datetime.strptime(s, "%H:%M") - preferred_dt)
        
        # Alterna precedenti e successivi
        for i in range(max(len(earlier_slots), len(later_slots))):
            if i < len(earlier_slots) and len(alternatives) < max_alternatives:
                alternatives.append({
                    "date": preferred_date,
                    "time": earlier_slots[i],
                    "type": "earlier"
                })
            if i < len(later_slots) and len(alternatives) < max_alternatives:
                alternatives.append({
                    "date": preferred_date,
                    "time": later_slots[i],
                    "type": "later"
                })
        
        # 2. Se non abbastanza alternative, cerca nei giorni successivi
        if len(alternatives) < max_alternatives:
            for day_offset in range(1, 4):  # Prossimi 3 giorni
                if len(alternatives) >= max_alternatives:
                    break
                    
                next_date = (datetime.strptime(preferred_date, "%Y-%m-%d") + timedelta(days=day_offset)).strftime("%Y-%m-%d")
                next_slots = self.get_available_slots(business_id, service_id, next_date, operator_id)
                
                for slot in next_slots[:2]:  # Max 2 slot per giorno
                    if len(alternatives) >= max_alternatives:
                        break
                    alternatives.append({
                        "date": next_date,
                        "time": slot,
                        "type": f"next_day_{day_offset}"
                    })
        
        return alternatives
    
    def _build_alternatives_message(
        self,
        alternatives: List[Dict],
        requested_date: str,
        requested_time: str
    ) -> str:
        """
        Costruisce messaggio con alternative per il cliente.
        Usato dal Voice Agent per proporre altri slot.
        """
        if not alternatives:
            return (
                f"Mi dispiace, lo slot delle {requested_time} è occupato e "
                f"non ho altre disponibilità per quella giornata. "
                f"Posso metterla in lista d'attesa e avvisarla via WhatsApp "
                f"appena si libera uno slot?"
            )
        
        # Costruisci lista alternative
        alt_texts = []
        for i, alt in enumerate(alternatives[:3], 1):
            date_obj = datetime.strptime(alt["date"], "%Y-%m-%d")
            date_str = date_obj.strftime("%d/%m")
            
            if alt["type"] == "earlier":
                alt_texts.append(f"{i}) Alle {alt['time']} (prima)")
            elif alt["type"] == "later":
                alt_texts.append(f"{i}) Alle {alt['time']} (dopo)")
            else:
                day_name = date_obj.strftime("%A").lower()
                day_names_it = {
                    "monday": "lunedì", "tuesday": "martedì", "wednesday": "mercoledì",
                    "thursday": "giovedì", "friday": "venerdì", "saturday": "sabato", "sunday": "domenica"
                }
                alt_texts.append(f"{i}) {day_names_it.get(day_name, day_name)} {date_str} alle {alt['time']}")
        
        return (
            f"Lo slot delle {requested_time} è occupato, ma ho queste alternative:\n"
            + "\n".join(alt_texts) +
            f"\n\nQuale preferisce? Oppure posso metterla in lista d'attesa per il {requested_time} "
            f"e avvisarla via WhatsApp quando si libera."
        )
    
    def _handle_slot_freed(
        self,
        business_id: str,
        service_id: str,
        date: str,
        time: str
    ):
        """
        Gestisce liberazione slot (lista d'attesa).
        Notifica i clienti in attesa via WhatsApp.
        """
        # 1. Trova clienti in waitlist per questo servizio/data
        from vertical_schemas import CustomerTier
        
        waitlist_entries = self.waitlist.find_entries_for_slot(
            service_id=service_id,
            date=date,
            time=time,
            business_id=business_id
        )
        
        if not waitlist_entries:
            return
        
        # 2. Ordina per priorità (VIP prima, poi FIFO)
        waitlist_entries.sort(key=lambda e: (
            0 if e.customer_tier == CustomerTier.PLATINUM else
            1 if e.customer_tier == CustomerTier.GOLD else
            2 if e.customer_tier == CustomerTier.SILVER else 3,
            e.created_at
        ))
        
        # 3. Notifica il primo cliente (VIP o più vecchio)
        top_entry = waitlist_entries[0]
        customer = self._get_customer_profile(top_entry.customer_id)
        
        if customer and self.whatsapp:
            # Invia notifica WhatsApp con proposta immediata
            self._send_waitlist_notification(customer, service_id, date, time, top_entry.entry_id)
            
            # Marca come "notificato" in attesa di risposta
            self.waitlist.mark_as_notified(
                entry_id=top_entry.entry_id,
                slot_date=date,
                slot_time=time
            )
    
    def _send_waitlist_notification(
        self,
        customer: CustomerProfile,
        service_id: str,
        date: str,
        time: str,
        waitlist_entry_id: str
    ):
        """
        Invia notifica WhatsApp a cliente in lista d'attesa.
        Include link diretto per confermare prenotazione.
        """
        service_info = self._get_service_info(service_id)
        service_name = service_info.get("name", "il servizio richiesto")
        
        # Formatta data in italiano
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        date_str = date_obj.strftime("%d/%m/%Y")
        
        message = (
            f"🎉 Buone notizie {customer.name}!\n\n"
            f"Si è liberato uno slot per {service_name}:\n"
            f"📅 {date_str}\n"
            f"🕐 {time}\n\n"
            f"Rispondi *SI* per confermare la prenotazione entro 2 ore, "
            f"oppure *NO* se non ti serve più.\n\n"
            f"_Questo messaggio scade alle {(datetime.now() + timedelta(hours=2)).strftime('%H:%M')}_"
        )
        
        self.whatsapp.send_message(customer.phone, message)
        
        # Log per tracking
        logger.info(f"Waitlist notification sent to {customer.phone} for {date} {time}")
    
    # ========================================================================
    # NOTIFICHE WHATSAPP
    # ========================================================================
    
    def _send_booking_confirmation(self, booking: Booking, customer: CustomerProfile):
        """Invia conferma WhatsApp"""
        if not self.whatsapp:
            return
        
        message = (
            f"Ciao {customer.name}! ✂️\n\n"
            f"Appuntamento confermato:\n"
            f"📅 {booking.date}\n"
            f"🕐 {booking.time}\n"
            f"💇 {booking.service_name}\n"
        )
        
        if booking.operator_name:
            message += f"👤 Con {booking.operator_name}\n"
        
        message += "\nTi ricorderemo l'appuntamento 24h prima! 👋"
        
        self.whatsapp.send_message(customer.phone, message)
        
        # Schedula reminder 24h
        self._schedule_reminder(booking, customer)
    
    def _schedule_reminder(self, booking: Booking, customer: CustomerProfile):
        """Schedula reminder 24h prima"""
        # Calcola data reminder
        booking_datetime = datetime.strptime(f"{booking.date} {booking.time}", "%Y-%m-%d %H:%M")
        reminder_datetime = booking_datetime - timedelta(hours=24)
        
        # Salva job (usando scheduler)
        if reminder_datetime > datetime.now():
            self.db.schedule_reminder(
                booking_id=booking.booking_id,
                send_at=reminder_datetime.isoformat(),
                phone=customer.phone,
                message_template="reminder_24h"
            )
    
    def _send_cancellation_notice(self, booking: Booking, customer: CustomerProfile):
        """Invia notifica annullamento"""
        message = (
            f"Ciao {customer.name},\n\n"
            f"La tua prenotazione del {booking.date} alle {booking.time} "
            f"è stata annullata.\n\n"
            f"Per riprendere l'appuntamento, rispondi a questo messaggio!"
        )
        self.whatsapp.send_message(customer.phone, message)
    
    def _send_reschedule_notice(
        self,
        booking: Booking,
        customer: CustomerProfile,
        old_date: str,
        old_time: str
    ):
        """Invia notifica spostamento"""
        message = (
            f"Ciao {customer.name}! 📝\n\n"
            f"Appuntamento spostato:\n"
            f"Da: {old_date} {old_time}\n"
            f"A: {booking.date} {booking.time}\n"
            f"💇 {booking.service_name}\n\n"
            f"Confermi il nuovo orario?"
        )
        self.whatsapp.send_message(customer.phone, message)
    
    def _send_priority_notification(self, entry: WaitlistEntry, date: str, time: str):
        """Invia notifica prioritaria VIP"""
        customer = self._get_customer_profile(entry.customer_id)
        if not customer or not self.whatsapp:
            return
        
        message = (
            f"🌟 Ciao {customer.name}!\n\n"
            f"Uno slot si è liberato per te (priorità VIP):\n"
            f"📅 {date} alle {time}\n\n"
            f"Vuoi prenotarlo? Rispondi PRENOTA entro 1 ora!"
        )
        self.whatsapp.send_message(customer.phone, message)
