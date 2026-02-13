"""
Schema dati per verticale AUTO
CoVe 2026 - Voice Agent Enterprise
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class VehicleSchema:
    id: Optional[str] = None
    targa: str = ""
    modello: Optional[str] = None
    marca: Optional[str] = None
    anno: Optional[int] = None
    km_attuali: Optional[int] = None
    
    ultimo_tagliando: Optional[str] = None
    km_ultimo_tagliando: Optional[int] = None
    
    storico_interventi: List[Dict[str, Any]] = field(default_factory=list)
    
    note: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VehicleSchema':
        return cls(**data)
    
    def add_intervento(self, data: str, tipo: str, costo: Optional[float] = None, note: Optional[str] = None):
        self.storico_interventi.append({
            "data": data,
            "tipo": tipo,
            "costo": costo,
            "note": note
        })
        if tipo == "tagliando":
            self.ultimo_tagliando = data

@dataclass
class BookingSchema:
    id: Optional[str] = None
    vehicle_id: Optional[str] = None
    
    servizio: str = "tagliando"
    data: str = ""
    ora_inizio: str = ""
    ora_fine: Optional[str] = None
    
    targa: Optional[str] = None
    urgenza: str = "pianificata"  # pianificata, entro_3_giorni, entro_24h, immediata
    
    stato: str = "pending"
    
    preventivo_approvato: bool = False
    preventivo_importo: Optional[float] = None
    
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    note_cliente: Optional[str] = None
    note_interne: Optional[str] = None
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = self.created_at
    
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
        self.updated_at = datetime.now().isoformat()

def create_vehicle(targa: str, **kwargs) -> VehicleSchema:
    return VehicleSchema(targa=targa, **kwargs)

def create_booking(vehicle_id: str, servizio: str, data: str, ora: str, **kwargs) -> BookingSchema:
    return BookingSchema(
        vehicle_id=vehicle_id,
        servizio=servizio,
        data=data,
        ora_inizio=ora,
        **kwargs
    )
