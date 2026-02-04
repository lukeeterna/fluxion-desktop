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
    
    def add_to_waitlist(self, entry: WaitlistEntry) -> bool:
        """Aggiunge cliente alla lista d'attesa"""
        # Salva nel DB
        pass
    
    def get_priority_list(self, service_id: str, date: str) -> List[WaitlistEntry]:
        """
        Restituisce lista ordinata per priorità.
        I VIP sono sempre primi.
        """
        entries = self.db.get_waitlist_for_service(service_id, date)
        return sorted(entries, key=lambda x: x.priority_score, reverse=True)
    
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
# 6. FACTORY PER CREAZIONE SCHEDE
# =============================================================================

class CustomerCardFactory:
    """Factory per creare schede in base al vertical"""
    
    @staticmethod
    def create_card(vertical: str, customer_id: str) -> Any:
        """Crea scheda vuota per il vertical specifico"""
        from datetime import datetime
        
        now = datetime.now().isoformat()
        
        if vertical in ["fisioterapia", "fisio", "riabilitazione"]:
            return SchedaFisioterapia(customer_id=customer_id, created_at=now)
        
        elif vertical in ["dentista", "odontoiatria", "dental"]:
            return SchedaOdontoiatrica(customer_id=customer_id, created_at=now)
        
        elif vertical in ["estetica", "spa", "beauty"]:
            return SchedaEstetica(customer_id=customer_id, created_at=now)
        
        elif vertical in ["parrucchiere", "salone", "hair"]:
            return SchedaParrucchiere(customer_id=customer_id, created_at=now)
        
        elif vertical in ["auto", "officina", "meccanico"]:
            return SchedaVeicolo(customer_id=customer_id, veicolo_id="", created_at=now)
        
        elif vertical == "carrozzeria":
            return SchedaCarrozzeria(customer_id=customer_id, veicolo_id="", created_at=now)
        
        else:
            # Default: anamnesi base
            return AnamnesiBase(customer_id=customer_id, created_at=now, updated_at=now)


# Mappatura vertical → tipo scheda
VERTICAL_CARD_TYPES = {
    "fisioterapia": SchedaFisioterapia,
    "dentista": SchedaOdontoiatrica,
    "estetica": SchedaEstetica,
    "parrucchiere": SchedaParrucchiere,
    "automotive": SchedaVeicolo,
    "carrozzeria": SchedaCarrozzeria,
}
