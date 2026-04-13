"""
FLUXION Voice Agent - Vertical Customer Card Schemas
Tassonomie complete per settori verticali
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class CustomerTier(Enum):
    """Livelli cliente per priorità lista d'attesa"""
    STANDARD = "standard"
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    VIP = "vip"  # Priorità massima


@dataclass
class CustomerProfile:
    """Profilo base cliente (comune a tutti i verticali)"""
    customer_id: str
    phone: str
    name: str
    surname: str
    email: Optional[str] = None
    tier: CustomerTier = CustomerTier.STANDARD
    notes: str = ""
    allergies: List[str] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    # Storico
    total_bookings: int = 0
    no_show_count: int = 0
    last_visit: Optional[str] = None
    preferred_operator: Optional[str] = None


# =============================================================================
# 1. MEDICO / FISIOTERAPIA / ODONTOIATRIA - Schede Anamnestiche
# =============================================================================

@dataclass
class AnamnesiBase:
    """Anamnesi generale medica"""
    customer_id: str
    created_at: str
    updated_at: str
    
    # Dati anagrafici medici
    data_nascita: Optional[str] = None
    sesso: Optional[str] = None
    altezza: Optional[float] = None  # cm
    peso: Optional[float] = None  # kg
    gruppo_sanguigno: Optional[str] = None
    
    # Allergie e intolleranze
    allergie_farmaci: List[str] = field(default_factory=list)
    allergie_alimentari: List[str] = field(default_factory=list)
    allergie_ambientali: List[str] = field(default_factory=list)
    intolleranze: List[str] = field(default_factory=list)
    
    # Patologie
    patologie_croniche: List[str] = field(default_factory=list)
    patologie_precedenti: List[str] = field(default_factory=list)
    interventi_chirurgici: List[Dict] = field(default_factory=list)
    ospedalizzazioni: List[Dict] = field(default_factory=list)
    
    # Terapie in corso
    terapie_farmacologiche: List[Dict] = field(default_factory=list)
    integratori: List[str] = field(default_factory=list)
    
    # Familiarità
    familiarita_patologie: Dict[str, List[str]] = field(default_factory=dict)
    
    # Stili di vita
    fumatore: Optional[str] = None  # "si", "no", "ex"
    alcol: Optional[str] = None  # "mai", "occasionale", "regolare"
    attivita_fisica: Optional[str] = None
    lavoro: Optional[str] = None
    
    # Contatti emergenza
    contatto_emergenza_nome: Optional[str] = None
    contatto_emergenza_tel: Optional[str] = None
    medico_curante: Optional[str] = None


@dataclass
class SchedaFisioterapia:
    """Scheda specifica fisioterapia"""
    customer_id: str
    created_at: str
    
    # Motivo accesso
    motivo_primo_accesso: str = ""
    data_inizio_terapia: Optional[str] = None
    
    # Valutazione funzionale
    valutazione_iniziale: Dict = field(default_factory=dict)
    scale_valutazione: Dict = field(default_factory=dict)  # VAS, NRS, etc.
    
    # Zone trattate
    zona_principale: Optional[str] = None  # "colonna_lombare", "spalla_dx", etc.
    zone_secondarie: List[str] = field(default_factory=list)
    
    # Diagnosi
    diagnosi_medica: str = ""
    diagnosi_fisioterapica: str = ""
    
    # Trattamenti effettuati
    sedute: List[Dict] = field(default_factory=list)
    
    # Esiti
    esito_trattamento: Optional[str] = None  # "miglioramento", "stabile", "peggioramento"
    data_fine_terapia: Optional[str] = None
    
    # Prescrizione medica
    prescrizione_medica: Optional[Dict] = None  # scansione/dati
    numero_sedute_prescritte: int = 0
    sedute_effettuate: int = 0


@dataclass
class SchedaOdontoiatrica:
    """Scheda dentista con odontogramma semplificato"""
    customer_id: str
    created_at: str
    
    # Odontogramma (stato denti)
    # Quadranti: 1=superiore dx, 2=superiore sx, 3=inferiore sx, 4=inferiore dx
    odontogramma: Dict[str, Dict] = field(default_factory=dict)
    # Esempio: "11": {"stato": "sano", "trattamenti": []}
    
    # Anamnesi odontoiatrica
    primo_accesso: Optional[str] = None
    ultima_visita: Optional[str] = None
    frequenza_controlli: Optional[str] = None  # "6mesi", "1anno"
    
    # Abitudini
    spazzolino: Optional[str] = None  # "manuale", "elettrico"
    filo_interdentale: bool = False
    collutorio: bool = False
    
    # Fattori di rischio
    fumatore: bool = False
    diabete: bool = False
    parafunzioni: List[str] = field(default_factory=list)  # "bruxismo", "unghie"
    
    # Trattamenti storici
    otturazioni: List[Dict] = field(default_factory=list)
    estrazioni: List[Dict] = field(default_factory=list)
    devitalizzazioni: List[Dict] = field(default_factory=list)
    corone: List[Dict] = field(default_factory=list)
    impianti: List[Dict] = field(default_factory=list)
    
    # Apparecchio ortodontico
    ortodonzia_in_corso: bool = False
    tipo_apparecchio: Optional[str] = None  # "fisso", "invisibile"
    data_inizio_ortodonzia: Optional[str] = None
    
    # Allergie specifiche
    allergia_lattice: bool = False
    allergia_anestesia: bool = False


# =============================================================================
# 2. ESTETICA - Schede Tecniche
# =============================================================================

@dataclass
class SchedaEstetica:
    """Scheda cliente estetica"""
    customer_id: str
    created_at: str
    
    # Fototipo
    fototipo: Optional[int] = None  # 1-6 scala Fitzpatrick
    tipo_pelle: Optional[str] = None  # "secca", "mista", "grassa", "sensibile"
    
    # Allergie cosmetiche
    allergie_prodotti: List[str] = field(default_factory=list)
    allergie_profumi: List[str] = field(default_factory=list)
    allergie_henné: bool = False
    
    # Trattamenti precedenti
    trattamenti_precedenti: List[Dict] = field(default_factory=list)
    
    # Esfoliazioni
    ultima_depilazione: Optional[str] = None
    ultima_ceretta: Optional[str] = None
    
    # Unghie
    unghie_naturali: bool = True
    problematiche_unghie: List[str] = field(default_factory=list)
    
    # Viso specifico
    problematiche_viso: List[str] = field(default_factory=list)  # "acne", "macchie"
    routine_skincare: List[str] = field(default_factory=list)
    
    # Corpo
    peso_attuale: Optional[float] = None
    obiettivo: Optional[str] = None  # "dimagrimento", "tonificazione"
    
    # Contraindicazioni
    gravidanza: bool = False
    allattamento: bool = False
    patologie_attive: List[str] = field(default_factory=list)


# =============================================================================
# 3. PARRUCCHIERE - Schede Tecniche Colore/Trattamenti
# =============================================================================

@dataclass
class SchedaParrucchiere:
    """Scheda tecnica parrucchiere"""
    customer_id: str
    created_at: str
    
    # Analisi capelli
    tipo_capello: Optional[str] = None  # "fino", "medio", "spesso"
    porosita: Optional[str] = None  # "bassa", "media", "alta"
    lunghezza_attuale: Optional[str] = None  # "corto", "medio", "lungo"
    
    # Storia colore
    base_naturale: Optional[str] = None  # livello 1-10
    colore_attuale: Optional[str] = None
    
    # Storia chimica
    colorazioni_precedenti: List[Dict] = field(default_factory=list)
    decolorazioni: int = 0
    permanente: bool = False
    stirature_chimiche: int = 0
    
    # Allergie
    allergia_tinta: bool = False
    allergia_ammoniaca: bool = False
    test_pelle_eseguito: bool = False
    data_test_pelle: Optional[str] = None
    
    # Trattamenti abituali
    servizi_abituali: List[str] = field(default_factory=list)
    frequenza_taglio: Optional[str] = None
    frequenza_colore: Optional[str] = None
    
    # Prodotti usati
    prodotti_casa: List[str] = field(default_factory=list)
    
    # Preferenze
    preferenze_colore: Optional[str] = None
    non_vuole: List[str] = field(default_factory=list)  # "rosso", "cortissimo"


# =============================================================================
# 4. AUTOMOTIVE - Schede Tecniche Veicolo
# =============================================================================

@dataclass
class SchedaVeicolo:
    """Scheda veicolo cliente"""
    customer_id: str
    veicolo_id: str
    created_at: str
    
    # Dati veicolo
    targa: str = ""
    marca: str = ""
    modello: str = ""
    anno: Optional[int] = None
    alimentazione: Optional[str] = None  # "benzina", "diesel", "gpl", "metano", "elettrico"
    cilindrata: Optional[str] = None
    kw: Optional[int] = None
    
    # Dati tecnici
    telaio: Optional[str] = None  # VIN
    ultima_revisione: Optional[str] = None
    scadenza_revisione: Optional[str] = None
    
    # Storico interventi
    interventi: List[Dict] = field(default_factory=list)
    
    # Tagliandi
    ultimo_tagliando: Optional[str] = None
    km_ultimo_tagliando: Optional[int] = None
    km_attuali: Optional[int] = None
    
    # Gomme
    misura_gomme: Optional[str] = None
    tipo_gomme: Optional[str] = None  # "estive", "invernali", "allseason"
    
    # Preferenze
    preferenza_ricambi: Optional[str] = None  # "originali", "compatibili"
    garanzia_attiva: bool = False


@dataclass
class SchedaCarrozzeria:
    """Scheda interventi carrozzeria"""
    customer_id: str
    veicolo_id: str
    created_at: str
    
    # Danno riportato
    tipo_danno: Optional[str] = None  # "ammaccatura", "graffio", "urto"
    posizione_danno: Optional[str] = None  # "paraurti_ant", "porta_dx", etc.
    entita_danno: Optional[str] = None  # "lieve", "media", "grave"
    
    # Foto
    foto_pre: List[str] = field(default_factory=list)
    foto_post: List[str] = field(default_factory=list)
    
    # Preventivo
    preventivo_numero: Optional[str] = None
    importo_preventivo: Optional[float] = None
    approvato: bool = False
    
    # Intervento
    data_ingresso: Optional[str] = None
    data_consegna_prevista: Optional[str] = None
    data_consegna_effettiva: Optional[str] = None
    
    # Dettagli lavorazione
    lavorazioni: List[Dict] = field(default_factory=list)
    verniciatura: bool = False
    codice_colore: Optional[str] = None
    
    # Assicurazione
    sinistro_assicurativo: bool = False
    compagnia: Optional[str] = None
    numero_sinistro: Optional[str] = None


# =============================================================================
# 5. LISTA D'ATTESA CON PRIORITÀ VIP
# =============================================================================

@dataclass
class WaitlistEntry:
    """Singola entry lista d'attesa"""
    entry_id: str
    customer_id: str
    customer_tier: CustomerTier
    service_id: str
    preferred_operator_id: Optional[str] = None
    preferred_dates: List[str] = field(default_factory=list)  # date preferite
    flexibility_days: int = 7  # quanti giorni flessibilità
    urgency: str = "normal"  # "low", "normal", "high", "urgent"
    notes: str = ""
    created_at: str = ""
    
    # Calcolo priorità (più alto = più priorità)
    @property
    def priority_score(self) -> int:
        """
        Algoritmo priorità lista d'attesa:
        - Tier VIP: +1000
        - Tier Platinum: +500
        - Tier Gold: +250
        - Tier Silver: +100
        - Tier Bronze: +50
        - Standard: +0
        
        - Urgency urgent: +200
        - Urgency high: +100
        - Urgency normal: +0
        - Urgency low: -50
        
        - Attesa > 7 giorni: +10 per giorno aggiuntivo
        """
        tier_scores = {
            CustomerTier.VIP: 1000,
            CustomerTier.PLATINUM: 500,
            CustomerTier.GOLD: 250,
            CustomerTier.SILVER: 100,
            CustomerTier.BRONZE: 50,
            CustomerTier.STANDARD: 0
        }
        
        urgency_scores = {
            "urgent": 200,
            "high": 100,
            "normal": 0,
            "low": -50
        }
        
        base_score = tier_scores.get(self.customer_tier, 0)
        urgency_score = urgency_scores.get(self.urgency, 0)
        
        # TODO: aggiungere calcolo giorni attesa
        return base_score + urgency_score


class WaitlistManager:
    """Gestore lista d'attesa con priorità"""

    def __init__(self, db_connection):
        self.db = db_connection
        self._entries: List["WaitlistEntry"] = []  # in-memory store

    def add_to_waitlist(self, entry: "WaitlistEntry") -> bool:
        """Aggiunge cliente alla lista d'attesa"""
        self._entries.append(entry)
        return True

    def _get_entries(self, service_id: str, date: str) -> List["WaitlistEntry"]:
        """Recupera entry da DB o store in-memory come fallback."""
        entries = self.db.get_waitlist_for_service(service_id, date)
        if not entries:
            entries = [
                e for e in self._entries
                if e.service_id == service_id and date in (e.preferred_dates or [])
            ]
        return list(entries)

    def get_priority_list(self, service_id: str, date: str) -> List["WaitlistEntry"]:
        """Restituisce lista ordinata per priorità. I VIP sono sempre primi."""
        entries = self._get_entries(service_id, date)
        return sorted(entries, key=lambda x: x.priority_score, reverse=True)

    def find_entries_for_slot(self, service_id: str, date: str, time: str = None, business_id: str = None) -> List["WaitlistEntry"]:
        """Trova entry in lista d'attesa per uno slot specifico."""
        return self.get_priority_list(service_id, date)

    def mark_as_notified(self, entry_id: str, slot_date: str, slot_time: str) -> None:
        """Marca entry come notificata (in attesa di risposta cliente)."""
        for entry in self._entries:
            if entry.entry_id == entry_id:
                entry.notified_at = f"{slot_date} {slot_time}"
                break

    def notify_slot_available(self, service_id: str, date: str, time: str) -> Optional[str]:
        """
        Quando si libera uno slot, notifica il primo VIP in lista.
        Se nessun VIP, il primo standard.
        """
        entries = self.get_priority_list(service_id, date)
        
        if not entries:
            return None
        
        # Prendi il primo (più alta priorità)
        top_entry = entries[0]
        
        # Invia notifica WhatsApp/SMS
        self._send_priority_notification(top_entry, date, time)
        
        return top_entry.customer_id
    
    def _send_priority_notification(self, entry: WaitlistEntry, date: str, time: str):
        """Invia notifica prioritaria al cliente"""
        # Implementazione notifica
        pass


# =============================================================================
# 6. COMPOSITE CUSTOMER CARD (multi-vertical clinics)
# =============================================================================

@dataclass
class CompositeCustomerCard:
    """
    Scheda composita per clienti che usano servizi di più verticali.
    Es: clinica che fa odontoiatria + fisioterapia + estetica.
    Ogni verticale ha la sua scheda specifica, il composito le aggrega.
    """
    customer_id: str
    profile: Optional[CustomerProfile] = None
    cards: Dict[str, Any] = field(default_factory=dict)  # vertical → card
    created_at: str = ""
    updated_at: str = ""

    def add_card(self, vertical: str, card: Any) -> None:
        """Aggiunge una scheda verticale al composito."""
        self.cards[vertical] = card
        from datetime import datetime
        self.updated_at = datetime.now().isoformat()

    def get_card(self, vertical: str) -> Optional[Any]:
        """Recupera la scheda per un verticale specifico."""
        return self.cards.get(vertical)

    def get_verticals(self) -> List[str]:
        """Lista dei verticali attivi per questo cliente."""
        return list(self.cards.keys())

    def has_vertical(self, vertical: str) -> bool:
        """Verifica se il cliente ha una scheda per il verticale."""
        return vertical in self.cards

    def get_all_allergies(self) -> List[str]:
        """Aggrega tutte le allergie da tutti i verticali."""
        all_allergies = set()
        if self.profile and self.profile.allergies:
            all_allergies.update(self.profile.allergies)
        for card in self.cards.values():
            if hasattr(card, 'allergie_farmaci'):
                all_allergies.update(card.allergie_farmaci)
            if hasattr(card, 'allergie_prodotti'):
                all_allergies.update(card.allergie_prodotti)
            if hasattr(card, 'allergie_profumi'):
                all_allergies.update(card.allergie_profumi)
            if hasattr(card, 'allergia_tinta') and card.allergia_tinta:
                all_allergies.add("tinta capelli")
            if hasattr(card, 'allergia_lattice') and card.allergia_lattice:
                all_allergies.add("lattice")
            if hasattr(card, 'allergia_anestesia') and card.allergia_anestesia:
                all_allergies.add("anestesia locale")
        return sorted(all_allergies)

    def get_medical_warnings(self) -> List[str]:
        """Raccoglie avvertenze mediche cross-vertical."""
        warnings = []
        for vertical, card in self.cards.items():
            if hasattr(card, 'patologie_croniche') and card.patologie_croniche:
                warnings.append(f"[{vertical}] Patologie: {', '.join(card.patologie_croniche)}")
            if hasattr(card, 'terapie_farmacologiche') and card.terapie_farmacologiche:
                warnings.append(f"[{vertical}] Terapie in corso: {len(card.terapie_farmacologiche)} farmaci")
            if hasattr(card, 'gravidanza') and card.gravidanza:
                warnings.append(f"[{vertical}] GRAVIDANZA IN CORSO")
            if hasattr(card, 'patologie_attive') and card.patologie_attive:
                warnings.append(f"[{vertical}] Patologie attive: {', '.join(card.patologie_attive)}")
        return warnings

    def to_dict(self) -> Dict[str, Any]:
        """Serializza in dizionario."""
        from dataclasses import asdict
        result = {
            "customer_id": self.customer_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "verticals": self.get_verticals(),
            "all_allergies": self.get_all_allergies(),
            "medical_warnings": self.get_medical_warnings(),
            "cards": {},
        }
        if self.profile:
            result["profile"] = asdict(self.profile)
        for vertical, card in self.cards.items():
            result["cards"][vertical] = asdict(card)
        return result


# =============================================================================
# 7. FACTORY PER CREAZIONE SCHEDE
# =============================================================================

# Mapping sub-verticals to card types
_VERTICAL_TO_CARD = {
    # Medical sub-verticals
    "fisioterapia": "fisioterapia",
    "fisio": "fisioterapia",
    "riabilitazione": "fisioterapia",
    "odontoiatra": "odontoiatrica",
    "dentista": "odontoiatrica",
    "odontoiatria": "odontoiatrica",
    "dental": "odontoiatrica",
    "medical": "anamnesi",
    # Beauty/hair sub-verticals
    "estetica": "estetica",
    "spa": "estetica",
    "beauty": "estetica",
    "parrucchiere": "parrucchiere",
    "salone": "parrucchiere",
    "hair": "parrucchiere",
    "barbiere": "parrucchiere",
    # Auto sub-verticals
    "auto": "veicolo",
    "officina": "veicolo",
    "meccanico": "veicolo",
    "gommista": "veicolo",
    "carrozzeria": "carrozzeria",
    # Standalone
    "palestra": "anamnesi",
    "toelettatura": "anamnesi",
}


class CustomerCardFactory:
    """Factory per creare schede in base al vertical"""

    @staticmethod
    def create_card(vertical: str, customer_id: str) -> Any:
        """Crea scheda vuota per il vertical specifico."""
        from datetime import datetime
        now = datetime.now().isoformat()

        card_type = _VERTICAL_TO_CARD.get(vertical, "anamnesi")

        if card_type == "fisioterapia":
            return SchedaFisioterapia(customer_id=customer_id, created_at=now)
        elif card_type == "odontoiatrica":
            return SchedaOdontoiatrica(customer_id=customer_id, created_at=now)
        elif card_type == "estetica":
            return SchedaEstetica(customer_id=customer_id, created_at=now)
        elif card_type == "parrucchiere":
            return SchedaParrucchiere(customer_id=customer_id, created_at=now)
        elif card_type == "veicolo":
            return SchedaVeicolo(customer_id=customer_id, veicolo_id="", created_at=now)
        elif card_type == "carrozzeria":
            return SchedaCarrozzeria(customer_id=customer_id, veicolo_id="", created_at=now)
        else:
            return AnamnesiBase(customer_id=customer_id, created_at=now, updated_at=now)

    @staticmethod
    def create_composite(customer_id: str, verticals: List[str],
                         profile: Optional[CustomerProfile] = None) -> CompositeCustomerCard:
        """Crea una scheda composita per cliniche multi-servizio."""
        from datetime import datetime
        now = datetime.now().isoformat()
        composite = CompositeCustomerCard(
            customer_id=customer_id,
            profile=profile,
            created_at=now,
            updated_at=now,
        )
        for vertical in verticals:
            card = CustomerCardFactory.create_card(vertical, customer_id)
            composite.add_card(vertical, card)
        return composite


# Mappatura vertical → tipo scheda
VERTICAL_CARD_TYPES = {
    "fisioterapia": SchedaFisioterapia,
    "odontoiatra": SchedaOdontoiatrica,
    "dentista": SchedaOdontoiatrica,
    "estetica": SchedaEstetica,
    "beauty": SchedaEstetica,
    "parrucchiere": SchedaParrucchiere,
    "barbiere": SchedaParrucchiere,
    "salone": SchedaParrucchiere,
    "automotive": SchedaVeicolo,
    "auto": SchedaVeicolo,
    "gommista": SchedaVeicolo,
    "carrozzeria": SchedaCarrozzeria,
}
