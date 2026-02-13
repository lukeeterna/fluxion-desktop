"""
Schema dati per verticale PALESTRA
CoVe 2026 - Voice Agent Enterprise
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class MemberSchema:
    id: Optional[str] = None
    nome: Optional[str] = None
    cognome: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    
    abbonamento_tipo: Optional[str] = None  # mensile, trimestrale, annuale
    data_inizio_abbonamento: Optional[str] = None
    data_scadenza_abbonamento: Optional[str] = None
    
    obiettivi: List[str] = field(default_factory=list)
    livello_fitness: Optional[str] = None
    corsi_preferiti: List[str] = field(default_factory=list)
    
    ingressi_totali: int = 0
    ultimo_ingresso: Optional[str] = None
    
    note: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemberSchema':
        return cls(**data)

@dataclass
class BookingSchema:
    id: Optional[str] = None
    member_id: Optional[str] = None
    
    servizio: str = "lezione"
    data: str = ""
    ora_inizio: str = ""
    ora_fine: Optional[str] = None
    durata_minuti: int = 60
    
    trainer: Optional[str] = None
    corso: Optional[str] = None
    
    stato: str = "pending"
    
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
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
        self.updated_at = datetime.now().isoformat()
    
    def cancella(self):
        self.stato = "cancelled"
        self.updated_at = datetime.now().isoformat()
    
    def sposta(self, nuova_data: str, nuova_ora: str):
        self.data = nuova_data
        self.ora_inizio = nuova_ora
        self._calcola_ora_fine()
        self.updated_at = datetime.now().isoformat()

def create_member(nome: str, telefono: str, **kwargs) -> MemberSchema:
    return MemberSchema(nome=nome, telefono=telefono, **kwargs)

def create_booking(member_id: str, servizio: str, data: str, ora: str, **kwargs) -> BookingSchema:
    return BookingSchema(
        member_id=member_id,
        servizio=servizio,
        data=data,
        ora_inizio=ora,
        **kwargs
    )
