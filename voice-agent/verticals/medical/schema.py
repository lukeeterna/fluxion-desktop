"""
Schema dati per verticale MEDICAL
CoVe 2026 - Voice Agent Enterprise
Dataclass per scheda paziente e prenotazione
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class BookingStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"

@dataclass
class PatientSchema:
    """Schema dati paziente per medical"""
    
    # Dati anagrafici
    id: Optional[str] = None
    nome: Optional[str] = None
    cognome: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    data_nascita: Optional[str] = None
    codice_fiscale: Optional[str] = None
    
    # Anamnesi
    patologie_croniche: List[str] = field(default_factory=list)
    allergie: List[str] = field(default_factory=list)
    terapie_in_corso: List[str] = field(default_factory=list)
    interventi_precedenti: List[str] = field(default_factory=list)
    
    # Contatti emergenza
    contatto_emergenza_nome: Optional[str] = None
    contatto_emergenza_telefono: Optional[str] = None
    
    # Storico visite
    storico_visite: List[Dict[str, Any]] = field(default_factory=list)
    data_ultima_visita: Optional[str] = None
    
    # Note
    note_mediche: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PatientSchema':
        return cls(**data)
    
    def add_visita(self, data: str, tipo: str, dottore: str, note: Optional[str] = None):
        self.storico_visite.append({
            "data": data,
            "tipo": tipo,
            "dottore": dottore,
            "note": note
        })
        self.data_ultima_visita = data

@dataclass
class BookingSchema:
    """Schema dati prenotazione medical"""
    
    id: Optional[str] = None
    patient_id: Optional[str] = None
    
    servizio: str = "visita"
    data: str = ""
    ora_inizio: str = ""
    ora_fine: Optional[str] = None
    durata_minuti: int = 30
    
    dottore: Optional[str] = None
    
    stato: str = "pending"
    priorita: str = "normale"  # normale, alta, urgente
    
    canale: str = "voice"
    
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    confirmed_at: Optional[str] = None
    
    reminder_inviato: bool = False
    conferma_inviata: bool = False
    
    note_cliente: Optional[str] = None
    note_interne: Optional[str] = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at
        if not self.ora_fine and self.ora_inizio:
            self._calcola_ora_fine()
    
    def _calcola_ora_fine(self):
        try:
            h, m = map(int, self.ora_inizio.split(':'))
            fine_minuti = h * 60 + m + self.durata_minuti
            fine_h = fine_minuti // 60
            fine_m = fine_minuti % 60
            self.ora_fine = f"{fine_h:02d}:{fine_m:02d}"
        except (ValueError, AttributeError):
            self.ora_fine = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BookingSchema':
        return cls(**data)
    
    def conferma(self):
        self.stato = "confirmed"
        self.confirmed_at = datetime.now().isoformat()
        self.updated_at = self.confirmed_at
    
    def cancella(self, motivo: Optional[str] = None):
        self.stato = "cancelled"
        self.note_interne = f"Cancellata: {motivo}" if motivo else "Cancellata"
        self.updated_at = datetime.now().isoformat()
    
    def completa(self):
        self.stato = "completed"
        self.updated_at = datetime.now().isoformat()
    
    def sposta(self, nuova_data: str, nuova_ora: str):
        self.data = nuova_data
        self.ora_inizio = nuova_ora
        self._calcola_ora_fine()
        self.updated_at = datetime.now().isoformat()

@dataclass
class WaitlistEntry:
    """Entry per waitlist"""
    id: Optional[str] = None
    patient_id: Optional[str] = None
    servizio: str = ""
    data_preferita: Optional[str] = None
    fascia_oraria: Optional[str] = None
    priorita: int = 0
    inserita_il: Optional[str] = None
    
    def __post_init__(self):
        if not self.inserita_il:
            self.inserita_il = datetime.now().isoformat()

def create_patient(nome: str, cognome: str, telefono: str, **kwargs) -> PatientSchema:
    return PatientSchema(nome=nome, cognome=cognome, telefono=telefono, **kwargs)

def create_booking(patient_id: str, servizio: str, data: str, ora: str, **kwargs) -> BookingSchema:
    return BookingSchema(
        patient_id=patient_id,
        servizio=servizio,
        data=data,
        ora_inizio=ora,
        **kwargs
    )
