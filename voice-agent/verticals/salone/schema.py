"""
Schema dati per verticale SALONE
CoVe 2026 - Voice Agent Enterprise
Dataclass per scheda cliente e prenotazione
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class HairType(Enum):
    """Tipologia di capelli"""
    LISCI = "lisci"
    RICCI = "ricci"
    MOSSI = "mossi"
    CRESPI = "crespi"
    ONDULATI = "ondulati"
    AFRO = "afro"

class HairLength(Enum):
    """Lunghezza capelli"""
    CORTISSIMI = "cortissimi"  # Undercut, rasati
    CORTI = "corti"  # Sopra le orecchie
    MEDI = "medi"  # Spalle
    LUNGHI = "lunghi"  # Sotto le spalle
    MOLTO_LUNGHI = "molto_lunghi"  # Vita

class BookingStatus(Enum):
    """Stato della prenotazione"""
    PENDING = "pending"  # In attesa di conferma
    CONFIRMED = "confirmed"  # Confermata
    CANCELLED = "cancelled"  # Cancellata
    COMPLETED = "completed"  # Completata
    NO_SHOW = "no_show"  # Non presentato

@dataclass
class CustomerSchema:
    """
    Schema dati cliente per salone
    Scheda completa con preferenze e storico
    """
    # Dati anagrafici
    id: Optional[str] = None
    nome: Optional[str] = None
    cognome: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    data_nascita: Optional[str] = None  # YYYY-MM-DD
    
    # Caratteristiche capelli
    tipo_capelli: Optional[str] = None  # lisci, ricci, mossi, ecc.
    lunghezza_capelli: Optional[str] = None  # corti, medi, lunghi
    colore_naturale: Optional[str] = None
    
    # Allergie e sensibilità
    allergie_prodotti: List[str] = field(default_factory=list)
    sensibilita_cuoi_capelluto: bool = False
    
    # Preferenze
    preferenze_operatore: Optional[str] = None
    preferenze_orario: List[str] = field(default_factory=list)  # ["mattina", "pomeriggio"]
    
    # Storico
    storico_trattamenti: List[Dict[str, Any]] = field(default_factory=list)
    data_ultima_visita: Optional[str] = None
    servizi_preferiti: List[str] = field(default_factory=list)
    
    # Fidelizzazione
    punti_fedelta: int = 0
    tessera_fedelta: Optional[str] = None
    
    # Note
    note_interne: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte in dizionario"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CustomerSchema':
        """Crea istanza da dizionario"""
        return cls(**data)
    
    def add_trattamento(self, data: str, servizio: str, operatore: str, 
                       note: Optional[str] = None):
        """Aggiunge un trattamento allo storico"""
        self.storico_trattamenti.append({
            "data": data,
            "servizio": servizio,
            "operatore": operatore,
            "note": note
        })
        self.data_ultima_visita = data
        
        # Aggiorna servizi preferiti
        if servizio not in self.servizi_preferiti:
            self.servizi_preferiti.append(servizio)
    
    def aggiungi_punti(self, punti: int):
        """Aggiunge punti fedeltà"""
        self.punti_fedelta += punti

@dataclass
class BookingSchema:
    """
    Schema dati prenotazione
    Rappresenta una prenotazione completa
    """
    # Identificazione
    id: Optional[str] = None
    customer_id: Optional[str] = None
    
    # Dettagli prenotazione
    servizio: str = "taglio"
    data: str = ""  # YYYY-MM-DD
    ora_inizio: str = ""  # HH:MM
    ora_fine: Optional[str] = None  # HH:MM (calcolata)
    durata_minuti: int = 45
    
    # Operatore
    operatore: Optional[str] = None
    operatore_assegnato: Optional[str] = None
    
    # Stato
    stato: str = "pending"  # pending, confirmed, cancelled, completed, no_show
    
    # Fonte
    canale: str = "voice"  # voice, whatsapp, phone, web
    
    # Timestamp
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    confirmed_at: Optional[str] = None
    
    # Comunicazioni
    reminder_inviato: bool = False
    conferma_inviata: bool = False
    
    # Note
    note_cliente: Optional[str] = None
    note_interne: Optional[str] = None
    
    def __post_init__(self):
        """Inizializza timestamp se non forniti"""
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at
        
        # Calcola ora fine se non fornita
        if not self.ora_fine and self.ora_inizio:
            self._calcola_ora_fine()
    
    def _calcola_ora_fine(self):
        """Calcola l'orario di fine in base alla durata"""
        try:
            h, m = map(int, self.ora_inizio.split(':'))
            fine_minuti = h * 60 + m + self.durata_minuti
            fine_h = fine_minuti // 60
            fine_m = fine_minuti % 60
            self.ora_fine = f"{fine_h:02d}:{fine_m:02d}"
        except (ValueError, AttributeError):
            self.ora_fine = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte in dizionario"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BookingSchema':
        """Crea istanza da dizionario"""
        return cls(**data)
    
    def conferma(self):
        """Conferma la prenotazione"""
        self.stato = "confirmed"
        self.confirmed_at = datetime.now().isoformat()
        self.updated_at = self.confirmed_at
    
    def cancella(self, motivo: Optional[str] = None):
        """Cancella la prenotazione"""
        self.stato = "cancelled"
        self.note_interne = f"Cancellata: {motivo}" if motivo else "Cancellata"
        self.updated_at = datetime.now().isoformat()
    
    def completa(self):
        """Marca come completata"""
        self.stato = "completed"
        self.updated_at = datetime.now().isoformat()
    
    def sposta(self, nuova_data: str, nuova_ora: str):
        """Sposta la prenotazione"""
        self.data = nuova_data
        self.ora_inizio = nuova_ora
        self._calcola_ora_fine()
        self.updated_at = datetime.now().isoformat()

@dataclass
class AvailabilitySlot:
    """Slot di disponibilità"""
    data: str
    ora: str
    disponibile: bool = True
    operatore: Optional[str] = None
    
@dataclass
class WaitlistEntry:
    """Entry per waitlist"""
    id: Optional[str] = None
    customer_id: Optional[str] = None
    servizio: str = ""
    data_preferita: Optional[str] = None
    fascia_oraria: Optional[str] = None  # "mattina", "pomeriggio", "sera"
    priorita: int = 0  # 0=normale, 1=alta, 2=urgente
    inserita_il: Optional[str] = None
    
    def __post_init__(self):
        if not self.inserita_il:
            self.inserita_il = datetime.now().isoformat()

# Helper functions
def create_customer(nome: str, telefono: str, **kwargs) -> CustomerSchema:
    """Crea un nuovo cliente"""
    return CustomerSchema(nome=nome, telefono=telefono, **kwargs)

def create_booking(customer_id: str, servizio: str, data: str, ora: str, 
                  **kwargs) -> BookingSchema:
    """Crea una nuova prenotazione"""
    return BookingSchema(
        customer_id=customer_id,
        servizio=servizio,
        data=data,
        ora_inizio=ora,
        **kwargs
    )
