# voice-agent/guided_dialog.py
"""
Sara Voice Agent - Guided Dialog Engine
Production-ready per FLUXION

Paradigma: Guided-First, NLU-Validation
- Proponiamo opzioni numerate
- Validare input con fuzzy matching italiano
- Escalate dopo 3 fallback

Stack: Python 3.13, SQLite, FastAPI bridge
Author: FLUXION Dev | License: MIT
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import re
from pathlib import Path


# ============================================================
# ENUMS E DATACLASSES
# ============================================================

class DialogState(str, Enum):
    """Stati della conversazione"""
    IDLE = "idle"
    GREETING = "greeting"
    COLLECTING_SERVIZIO = "collecting_servizio"
    COLLECTING_OPERATORE = "collecting_operatore"
    COLLECTING_DATA = "collecting_data"
    COLLECTING_ORA = "collecting_ora"
    COLLECTING_CLIENTE_NOME = "collecting_cliente_nome"
    COLLECTING_CLIENTE_TEL = "collecting_cliente_tel"
    FALLBACK_1 = "fallback_1"
    FALLBACK_2 = "fallback_2"
    FALLBACK_3_ESCALATION = "fallback_3_escalation"
    CONFIRMING = "confirming"
    SAVING = "saving"
    SUCCESS = "success"
    ERROR = "error"


# Mapping slot_id -> DialogState
SLOT_TO_STATE = {
    "servizio": DialogState.COLLECTING_SERVIZIO,
    "operatore": DialogState.COLLECTING_OPERATORE,
    "data": DialogState.COLLECTING_DATA,
    "ora": DialogState.COLLECTING_ORA,
    "cliente_nome": DialogState.COLLECTING_CLIENTE_NOME,
    "cliente_tel": DialogState.COLLECTING_CLIENTE_TEL,
}


@dataclass
class DialogContext:
    """Contesto di una conversazione"""
    vertical_id: str
    user_phone: Optional[str] = None
    state: DialogState = DialogState.IDLE
    slot_values: Dict[str, Any] = field(default_factory=dict)
    fallback_count: Dict[str, int] = field(default_factory=dict)
    conversation_history: List[Dict] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    db_client_id: Optional[int] = None
    error_messages: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Serializza contesto"""
        return {
            "vertical_id": self.vertical_id,
            "state": self.state.value,
            "slots": self.slot_values,
            "fallback_count": self.fallback_count,
            "db_client_id": self.db_client_id,
            "duration_sec": (datetime.now() - self.start_time).total_seconds()
        }


# ============================================================
# FUZZY MATCHING ITALIANO (CRITICO)
# ============================================================

class ItalianFuzzyMatcher:
    """Fuzzy matching per input italiano naturale"""

    RULES = {
        # Numeri ordinali -> indice 0-based
        "ordinali": {
            "1": 0, "uno": 0, "primo": 0, "il primo": 0, "la prima": 0,
            "2": 1, "due": 1, "secondo": 1, "il secondo": 1, "la seconda": 1,
            "3": 2, "tre": 2, "terzo": 2, "il terzo": 2, "la terza": 2,
            "4": 3, "quattro": 3, "quarto": 3, "il quarto": 3, "la quarta": 3,
            "5": 4, "cinque": 4, "quinto": 4, "il quinto": 4, "la quinta": 4,
            "6": 5, "sei": 5, "sesto": 5, "il sesto": 5, "la sesta": 5,
            "7": 6, "sette": 6, "settimo": 6, "il settimo": 6, "la settima": 6,
            "8": 7, "otto": 7, "ottavo": 7, "l'ottavo": 7, "l'ottava": 7,
            "9": 8, "nove": 8, "nono": 8, "il nono": 8, "la nona": 8,
            "10": 9, "dieci": 9, "decimo": 9, "il decimo": 9, "la decima": 9,
        },

        # Conferme
        "conferma_si": [
            "sì", "si", "yes", "ok", "okay", "va bene", "perfetto",
            "certo", "certamente", "assolutamente", "confermo", "esatto",
            "giusto", "d'accordo", "procedi", "vai", "ok perfetto", "sì perfetto"
        ],
        "conferma_no": [
            "no", "non", "nope", "annulla", "cancella", "stop", "aspetta",
            "momento", "ferma", "indietro", "torna", "no grazie", "no no"
        ],

        # Date relative (ordered by length - longest first to avoid partial matches)
        "date_relative": {
            "dopodomani": 2,  # Must be before "domani"
            "oggi": 0,
            "domani": 1,
            "fra due giorni": 2,
            "tra due giorni": 2,
            "questa settimana": "this_week",
            "la prossima settimana": "next_week",
            "settimana prossima": "next_week",
            "lunedì": "weekday_0",
            "lunedi": "weekday_0",
            "martedì": "weekday_1",
            "martedi": "weekday_1",
            "mercoledì": "weekday_2",
            "mercoledi": "weekday_2",
            "giovedì": "weekday_3",
            "giovedi": "weekday_3",
            "venerdì": "weekday_4",
            "venerdi": "weekday_4",
            "sabato": "weekday_5",
            "domenica": "weekday_6",
        },

        # Ore relative
        "ore_relative": {
            "mattina": ("09:00", "12:00"),
            "mattino": ("09:00", "12:00"),
            "pranzo": ("12:00", "14:00"),
            "pomeriggio": ("14:00", "18:00"),
            "sera": ("18:00", "21:00"),
            "subito": "first_available",
            "prima possibile": "first_available",
            "quando c'è posto": "first_available",
            "quando c'è": "first_available",
            "qualsiasi": "first_available",
            "indifferente": "first_available",
        },

        # Operatore default (normalized - no accents)
        "operatore_default": [
            "chiunque", "chi c'e", "chi e disponibile", "non importa",
            "indifferente", "qualsiasi", "il primo libero", "boh", "chi volete",
            "fate voi", "decidete voi"
        ],

        # Nuovo cliente triggers
        "nuovo_cliente": [
            "è la prima volta", "prima volta", "non sono mai stato",
            "non sono mai venuto", "non mi conosci", "non mi conoscete",
            "sono nuovo", "sono nuova", "cliente nuovo", "nuova cliente",
            "mai stato", "mai venuto", "mai venuta"
        ],
    }

    # Sinonimi servizi salone
    SINONIMI_SERVIZI = {
        "taglio": ["tagliare", "accorciare", "spuntare", "sfoltire", "capelli"],
        "taglio uomo": ["taglio maschile", "uomo", "maschile"],
        "taglio donna": ["taglio femminile", "donna", "femminile"],
        "piega": ["messa in piega", "asciugatura", "styling", "acconciatura"],
        "colore": ["tinta", "colorazione", "tintura", "colpi di sole", "meches", "balayage"],
        "barba": ["rasatura", "rifinitura barba", "barba e baffi"],
        "trattamento": ["cheratina", "maschera", "ristrutturante", "cura"],
    }

    @staticmethod
    def normalize(text: str) -> str:
        """Normalizza testo italiano"""
        text = text.lower().strip()
        # Normalizza apostrofi e accenti comuni
        text = text.replace("'", "'").replace("'", "'").replace("`", "'")
        text = text.replace("è", "e").replace("é", "e")
        text = text.replace("à", "a").replace("ì", "i").replace("ò", "o").replace("ù", "u")
        # Rimuovi punteggiatura finale
        text = re.sub(r'[!?.,;:]$', '', text)
        # Pulisci spazi multipli
        text = re.sub(r'\s+', ' ', text)
        return text

    @classmethod
    def match_ordinal(cls, text: str) -> Optional[int]:
        """Estrai numero ordinale da testo"""
        text = cls.normalize(text)
        return cls.RULES["ordinali"].get(text)

    @classmethod
    def is_conferma_si(cls, text: str) -> bool:
        """Verifica conferma positiva"""
        text = cls.normalize(text)
        return text in cls.RULES["conferma_si"] or any(
            c in text for c in cls.RULES["conferma_si"]
        )

    @classmethod
    def is_conferma_no(cls, text: str) -> bool:
        """Verifica conferma negativa"""
        text = cls.normalize(text)
        return text in cls.RULES["conferma_no"] or any(
            c in text for c in cls.RULES["conferma_no"]
        )

    @classmethod
    def is_nuovo_cliente(cls, text: str) -> bool:
        """Verifica se utente indica essere nuovo cliente"""
        text = cls.normalize(text)
        return any(trigger in text for trigger in cls.RULES["nuovo_cliente"])

    @classmethod
    def is_operatore_default(cls, text: str) -> bool:
        """Verifica se utente vuole qualsiasi operatore"""
        text = cls.normalize(text)
        return any(trigger in text for trigger in cls.RULES["operatore_default"])

    @classmethod
    def match_servizio_sinonimo(cls, text: str, services: List[str]) -> Optional[str]:
        """Match servizio tramite sinonimi"""
        text = cls.normalize(text)

        # Prima prova match diretto
        for svc in services:
            if svc.lower() in text or text in svc.lower():
                return svc

        # Poi prova sinonimi
        for servizio, sinonimi in cls.SINONIMI_SERVIZI.items():
            if text in sinonimi or any(s in text for s in sinonimi):
                # Trova servizio corrispondente
                for svc in services:
                    if servizio in svc.lower():
                        return svc

        return None

    @classmethod
    def extract_date(cls, text: str) -> Optional[str]:
        """Estrai data relativa e ritorna ISO string (YYYY-MM-DD)"""
        text = cls.normalize(text)

        # Check date relative
        for key, relative in cls.RULES["date_relative"].items():
            if key in text:
                if isinstance(relative, int):
                    # Giorni offset
                    target_date = datetime.now() + timedelta(days=relative)
                    return target_date.strftime("%Y-%m-%d")

                elif relative == "this_week":
                    # Prossimo giorno lavorativo questa settimana
                    today = datetime.now()
                    days_until_monday = (7 - today.weekday()) % 7
                    if days_until_monday == 0:
                        days_until_monday = 1  # Almeno domani
                    target_date = today + timedelta(days=days_until_monday)
                    return target_date.strftime("%Y-%m-%d")

                elif relative == "next_week":
                    # Lunedi della prossima settimana
                    today = datetime.now()
                    days_until_monday = 7 - today.weekday()
                    if days_until_monday <= 0:
                        days_until_monday += 7
                    target_date = today + timedelta(days=days_until_monday)
                    return target_date.strftime("%Y-%m-%d")

                elif relative.startswith("weekday_"):
                    # Giorno della settimana specifico
                    weekday = int(relative.split("_")[1])
                    today = datetime.now()
                    current_weekday = today.weekday()
                    days_offset = (weekday - current_weekday) % 7
                    if days_offset == 0:
                        days_offset = 7  # Prossima settimana se oggi
                    target_date = today + timedelta(days=days_offset)
                    return target_date.strftime("%Y-%m-%d")

        # Prova pattern GG/MM o GG-MM
        match = re.search(r'(\d{1,2})[/\-](\d{1,2})', text)
        if match:
            day, month = int(match.group(1)), int(match.group(2))
            year = datetime.now().year
            try:
                target_date = datetime(year, month, day)
                if target_date < datetime.now():
                    target_date = datetime(year + 1, month, day)
                return target_date.strftime("%Y-%m-%d")
            except ValueError:
                pass

        return None

    @classmethod
    def extract_time(cls, text: str) -> Optional[str]:
        """Estrai ora da testo"""
        text = cls.normalize(text)

        # Check fasce orarie
        for fascia, value in cls.RULES["ore_relative"].items():
            if fascia in text:
                if value == "first_available":
                    return "first_available"
                elif isinstance(value, tuple):
                    return value[0]  # Prima ora del range

        # Prova pattern HH:MM o HH.MM
        match = re.search(r'(\d{1,2})[:.](\d{2})', text)
        if match:
            hour, minute = int(match.group(1)), int(match.group(2))
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return f"{hour:02d}:{minute:02d}"

        # Prova "alle X" o "le X"
        match = re.search(r'(?:alle|le)\s*(\d{1,2})', text)
        if match:
            hour = int(match.group(1))
            if 7 <= hour <= 21:
                return f"{hour:02d}:00"

        # Solo numero (es: "10")
        match = re.search(r'^(\d{1,2})$', text)
        if match:
            hour = int(match.group(1))
            if 7 <= hour <= 21:
                return f"{hour:02d}:00"

        return None

    @classmethod
    def extract_time_range(cls, text: str) -> Optional[Tuple[str, str]]:
        """Estrai fascia oraria (mattina/pomeriggio) -> (HH:MM, HH:MM)"""
        text = cls.normalize(text)
        result = cls.RULES["ore_relative"].get(text)
        if isinstance(result, tuple):
            return result
        return None


# ============================================================
# VERTICAL CONFIG LOADER
# ============================================================

class VerticalConfigLoader:
    """Carica JSON config per verticale"""

    def __init__(self, vertical_id: str, data_path: Optional[Path] = None):
        self.vertical_id = vertical_id

        # Default path relativo a questo file
        if data_path is None:
            data_path = Path(__file__).parent / "data"
        self.data_path = Path(data_path)

        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Carica JSON config"""
        config_file = self.data_path / "verticals" / f"{self.vertical_id}.json"

        if not config_file.exists():
            # Prova config default
            config_file = self.data_path / "verticals" / "default.json"
            if not config_file.exists():
                # Config minima di emergenza
                return self._get_default_config()

        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _get_default_config(self) -> Dict:
        """Config minima di emergenza"""
        return {
            "vertical_id": self.vertical_id,
            "vertical_name": "Attivita",
            "slots_order": ["servizio", "operatore", "data", "ora", "cliente_nome", "cliente_tel"],
            "prompts": {
                "greeting_standard": "Buongiorno! Sono Sara. Come posso aiutarvi?",
                "greeting_cliente_noto": "Ciao {nome_cliente}! Bentornato!",
                "ask_servizio": "Quale servizio vi interessa?",
                "ask_operatore": "Con chi preferite?",
                "ask_data": "Quando vi va bene?",
                "ask_ora": "A che ora?",
                "ask_cliente_nome": "A che nome prenoto?",
                "ask_cliente_tel": "Mi lascia un numero per conferma?",
                "recap": "Ricapitolo: {servizio} con {operatore}, {data} alle {ora}.",
                "success": "Perfetto! Prenotato. A presto!",
                "escalation_message": "Vi passo a un collega. Un momento...",
            },
            "faq_inline": []
        }

    def get_prompt(self, prompt_key: str, **kwargs) -> str:
        """Ottieni prompt template e formatta"""
        prompts = self.config.get("prompts", {})
        template = prompts.get(prompt_key, f"[MISSING: {prompt_key}]")

        # Sostituisci placeholder {key} e {{key}}
        for key, value in kwargs.items():
            template = template.replace(f"{{{key}}}", str(value) if value else "")
            template = template.replace(f"{{{{{key}}}}}", str(value) if value else "")

        return template

    def get_slots_order(self) -> List[str]:
        """Ordine di raccolta slot"""
        return self.config.get("slots_order", [
            "servizio", "operatore", "data", "ora", "cliente_nome", "cliente_tel"
        ])

    def get_services(self, db_path: str, limit: int = 10) -> List[Dict]:
        """Ottieni lista servizi da DB"""
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id, nome, prezzo FROM servizi WHERE attivo=1 ORDER BY nome LIMIT ?",
                (limit,)
            )

            services = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return services
        except Exception as e:
            print(f"[CONFIG] Error loading services: {e}")
            return []

    def get_operatori(self, db_path: str, limit: int = 10) -> List[Dict]:
        """Ottieni lista operatori da DB"""
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id, nome, cognome FROM operatori WHERE attivo=1 ORDER BY nome LIMIT ?",
                (limit,)
            )

            operatori = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return operatori
        except Exception as e:
            print(f"[CONFIG] Error loading operatori: {e}")
            return []

    def get_faq_inline(self) -> List[Dict]:
        """Ottieni FAQ inline dal config"""
        return self.config.get("faq_inline", [])


# ============================================================
# GUIDED DIALOG ENGINE (CORE)
# ============================================================

class GuidedDialogEngine:
    """Motore principale Sara - Guided Dialog"""

    MAX_FALLBACK_ATTEMPTS = 3

    def __init__(
        self,
        vertical_id: str,
        db_path: str,
        config_path: Optional[Path] = None
    ):
        self.vertical_id = vertical_id
        self.db_path = db_path
        self.config_loader = VerticalConfigLoader(vertical_id, config_path)
        self.fuzzy = ItalianFuzzyMatcher()
        self.context: Optional[DialogContext] = None

    def start_dialog(self, user_phone: Optional[str] = None) -> Tuple[str, DialogContext]:
        """Inizia nuovo dialogo"""
        self.context = DialogContext(
            vertical_id=self.vertical_id,
            user_phone=user_phone
        )

        # Lookup cliente se esiste
        if user_phone:
            self._lookup_cliente(user_phone)

        # Greeting
        if self.context.db_client_id:
            # Cliente noto
            client_name = self._get_client_name()
            greeting = self.config_loader.get_prompt(
                "greeting_cliente_noto",
                nome_cliente=client_name
            )
        else:
            # Nuovo cliente
            greeting = self.config_loader.get_prompt("greeting_standard")

        # Aggiungi prima domanda (servizio)
        first_slot = self.config_loader.get_slots_order()[0]
        first_prompt = self._get_slot_prompt(first_slot)
        greeting = f"{greeting} {first_prompt}"

        self.context.state = SLOT_TO_STATE.get(first_slot, DialogState.COLLECTING_SERVIZIO)
        self._log_turn("assistant", greeting)

        return greeting, self.context

    def process_user_input(self, user_input: str) -> Tuple[str, DialogState]:
        """Processo input utente - core logic"""

        if not self.context:
            greeting, _ = self.start_dialog()
            return greeting, DialogState.GREETING

        # Log turn
        self._log_turn("user", user_input)

        # Check nuovo cliente trigger
        if self.fuzzy.is_nuovo_cliente(user_input):
            self.context.db_client_id = None
            self.context.slot_values.pop("cliente_nome", None)

        # Check FAQ inline (prezzi, orari, etc.)
        faq_response = self._match_faq_inline(user_input)
        if faq_response:
            # Rispondi FAQ ma rimani nello stato corrente
            current_prompt = self._get_current_slot_prompt()
            response = f"{faq_response} {current_prompt}"
            self._log_turn("assistant", response)
            return response, self.context.state

        # State machine
        if self.context.state == DialogState.CONFIRMING:
            return self._handle_confirmation(user_input)

        elif self.context.state == DialogState.FALLBACK_3_ESCALATION:
            response = self.config_loader.get_prompt("escalation_message")
            self.context.state = DialogState.ERROR
            self._log_turn("assistant", response)
            return response, DialogState.ERROR

        elif self.context.state.value.startswith("collecting_"):
            slot_id = self._get_current_slot_id()
            return self._handle_slot_input(slot_id, user_input)

        elif self.context.state in [DialogState.FALLBACK_1, DialogState.FALLBACK_2]:
            # Still collecting the same slot after a fallback
            slot_id = self._get_fallback_slot_id()
            return self._handle_slot_input(slot_id, user_input)

        else:
            response = "Scusate, c'e stato un errore. Riproviamo."
            self.context.state = DialogState.ERROR
            self._log_turn("assistant", response)
            return response, DialogState.ERROR

    def _get_current_slot_id(self) -> str:
        """Ottieni slot_id dallo stato corrente"""
        state_value = self.context.state.value
        if state_value.startswith("collecting_"):
            return state_value.replace("collecting_", "")
        return "servizio"

    def _get_fallback_slot_id(self) -> str:
        """Ottieni slot_id dal fallback (ultimo slot con fallback count > 0)"""
        # Find which slot we were collecting based on fallback_count
        for slot_id, count in self.context.fallback_count.items():
            if count > 0:
                return slot_id
        # Fallback to first incomplete slot
        for slot_id in self.config_loader.get_slots_order():
            if slot_id not in self.context.slot_values:
                return slot_id
        return "servizio"

    def _get_current_slot_prompt(self) -> str:
        """Ottieni prompt per slot corrente"""
        slot_id = self._get_current_slot_id()
        return self._get_slot_prompt(slot_id)

    def _handle_slot_input(self, slot_id: str, user_input: str) -> Tuple[str, DialogState]:
        """Gestisci input per slot specifico"""

        # Validare input
        is_valid, normalized_value = self._validate_slot(slot_id, user_input)

        if is_valid:
            # Slot valido
            self.context.slot_values[slot_id] = normalized_value
            self.context.fallback_count[slot_id] = 0

            # Conferma implicita + avanza a prossimo slot
            confirm = self._get_implicit_confirm(slot_id, normalized_value)
            next_response = self._advance_to_next_slot()

            response = f"{confirm} {next_response}"
            self._log_turn("assistant", response)
            return response, self.context.state

        else:
            # Slot non valido - incrementa fallback
            return self._handle_fallback(slot_id, user_input)

    def _validate_slot(self, slot_id: str, user_input: str) -> Tuple[bool, Any]:
        """Validare input per slot"""

        if slot_id == "servizio":
            # Prova ordinale
            idx = self.fuzzy.match_ordinal(user_input)
            if idx is not None:
                services = self.config_loader.get_services(self.db_path)
                if idx < len(services):
                    return True, services[idx]["nome"]

            # Prova sinonimo
            services = self.config_loader.get_services(self.db_path)
            service_names = [s["nome"] for s in services]
            match = self.fuzzy.match_servizio_sinonimo(user_input, service_names)
            if match:
                return True, match

            return False, None

        elif slot_id == "operatore":
            # Check operatore default
            if self.fuzzy.is_operatore_default(user_input):
                return True, "primo disponibile"

            # Prova ordinale
            idx = self.fuzzy.match_ordinal(user_input)
            if idx is not None:
                operatori = self.config_loader.get_operatori(self.db_path)
                if idx < len(operatori):
                    op = operatori[idx]
                    nome = f"{op['nome']} {op.get('cognome', '')}".strip()
                    return True, nome

            # Prova match nome diretto
            operatori = self.config_loader.get_operatori(self.db_path)
            user_lower = user_input.lower()
            for op in operatori:
                if op['nome'].lower() in user_lower:
                    nome = f"{op['nome']} {op.get('cognome', '')}".strip()
                    return True, nome

            return False, None

        elif slot_id == "data":
            # Prova date relative
            date_str = self.fuzzy.extract_date(user_input)
            if date_str:
                return True, date_str

            # Prova ordinale (se proposte date)
            idx = self.fuzzy.match_ordinal(user_input)
            if idx is not None:
                dates = self._get_available_dates()
                if idx < len(dates):
                    return True, dates[idx]

            return False, None

        elif slot_id == "ora":
            # Prova ora esplicita o fascia
            time_str = self.fuzzy.extract_time(user_input)
            if time_str:
                return True, time_str

            # Prova ordinale (se proposte ore)
            idx = self.fuzzy.match_ordinal(user_input)
            if idx is not None:
                times = self._get_available_times()
                if idx < len(times):
                    return True, times[idx]

            return False, None

        elif slot_id == "cliente_nome":
            # Accetta qualsiasi testo non vuoto >= 2 caratteri
            name = user_input.strip()
            if len(name) >= 2:
                # Capitalizza
                return True, name.title()
            return False, None

        elif slot_id == "cliente_tel":
            # Valida numero telefonico italiano
            phone = re.sub(r'\D', '', user_input)
            if len(phone) >= 9:
                return True, phone
            return False, None

        return False, None

    def _get_implicit_confirm(self, slot_id: str, value: Any) -> str:
        """Genera conferma implicita per slot"""
        confirms = {
            "servizio": f"{value}, perfetto!",
            "operatore": f"Con {value}, ottimo!" if value != "primo disponibile" else "Ok, vedo chi e' libero!",
            "data": f"{self._format_date_italian(value)}, trovato!",
            "ora": f"Alle {value}, perfetto!",
            "cliente_nome": f"Piacere {value}!",
            "cliente_tel": "Annotato!",
        }
        return confirms.get(slot_id, "Ok!")

    def _handle_fallback(self, slot_id: str, user_input: str) -> Tuple[str, DialogState]:
        """Gestisce fallback quando input non valido"""
        if slot_id not in self.context.fallback_count:
            self.context.fallback_count[slot_id] = 0

        self.context.fallback_count[slot_id] += 1
        attempt = self.context.fallback_count[slot_id]

        if attempt >= self.MAX_FALLBACK_ATTEMPTS:
            # Escalation
            self.context.state = DialogState.FALLBACK_3_ESCALATION
            response = self.config_loader.get_prompt("escalation_message")

        elif attempt == 2:
            # Fallback esplicito con opzioni numerate
            self.context.state = DialogState.FALLBACK_2
            options_prompt = self._get_guided_options(slot_id)
            response = f"Aiutatemi a capire. {options_prompt}"

        else:
            # Primo fallback - soft
            self.context.state = DialogState.FALLBACK_1
            prompt = self._get_slot_prompt(slot_id)
            response = f"Scusate, non ho capito bene. {prompt}"

        self._log_turn("assistant", response)
        return response, self.context.state

    def _handle_confirmation(self, user_input: str) -> Tuple[str, DialogState]:
        """Gestisce risposta alla conferma finale"""
        if self.fuzzy.is_conferma_si(user_input):
            return self._save_booking()
        elif self.fuzzy.is_conferma_no(user_input):
            # Torna a modificare
            response = "Ok, cosa volete cambiare? Servizio, data o orario?"
            # Torna al primo slot
            first_slot = self.config_loader.get_slots_order()[0]
            self.context.state = SLOT_TO_STATE.get(first_slot, DialogState.COLLECTING_SERVIZIO)
            self._log_turn("assistant", response)
            return response, self.context.state
        else:
            response = "Scusate, confermate la prenotazione? Dite 'si' o 'no'."
            self._log_turn("assistant", response)
            return response, DialogState.CONFIRMING

    def _get_slot_prompt(self, slot_id: str) -> str:
        """Ottieni prompt per slot"""
        prompt_key = f"ask_{slot_id}"
        return self.config_loader.get_prompt(prompt_key)

    def _get_guided_options(self, slot_id: str) -> str:
        """Genera opzioni numerate per slot"""

        if slot_id == "servizio":
            services = self.config_loader.get_services(self.db_path, limit=5)
            if not services:
                return "Quale servizio vi interessa?"

            lines = ["Quale servizio preferite?"]
            for i, svc in enumerate(services, 1):
                prezzo = svc.get('prezzo', '?')
                lines.append(f"{i}) {svc['nome']} - {prezzo} euro")
            return "\n".join(lines)

        elif slot_id == "operatore":
            operatori = self.config_loader.get_operatori(self.db_path, limit=5)
            if not operatori:
                return "Con chi preferite?"

            lines = ["Con chi preferite?"]
            for i, op in enumerate(operatori, 1):
                nome = f"{op['nome']} {op.get('cognome', '')}".strip()
                lines.append(f"{i}) {nome}")
            lines.append(f"{len(operatori) + 1}) Chi e' disponibile")
            return "\n".join(lines)

        elif slot_id == "data":
            dates = self._get_available_dates(limit=5)
            lines = ["Quando vi va bene?"]
            for i, date_str in enumerate(dates, 1):
                lines.append(f"{i}) {self._format_date_italian(date_str)}")
            return "\n".join(lines)

        elif slot_id == "ora":
            times = self._get_available_times(limit=5)
            lines = ["A che ora?"]
            for i, time_str in enumerate(times, 1):
                lines.append(f"{i}) {time_str}")
            return "\n".join(lines)

        return self._get_slot_prompt(slot_id)

    def _advance_to_next_slot(self) -> str:
        """Avanza al prossimo slot nella sequenza"""
        slots_order = self.config_loader.get_slots_order()

        # Trova prossimo slot non compilato
        for slot_id in slots_order:
            if slot_id not in self.context.slot_values:
                # Se cliente noto, salta cliente_nome e cliente_tel
                if self.context.db_client_id and slot_id in ["cliente_nome", "cliente_tel"]:
                    continue

                self.context.state = SLOT_TO_STATE.get(slot_id, DialogState.COLLECTING_SERVIZIO)
                return self._get_slot_prompt(slot_id)

        # Tutti gli slot compilati - recap
        recap = self._generate_recap()
        self.context.state = DialogState.CONFIRMING
        return recap

    def _generate_recap(self) -> str:
        """Genera recap finale per conferma"""
        servizio = self.context.slot_values.get("servizio", "?")
        operatore = self.context.slot_values.get("operatore", "?")
        data_raw = self.context.slot_values.get("data", "?")
        ora = self.context.slot_values.get("ora", "?")

        data_formatted = self._format_date_italian(data_raw) if data_raw != "?" else "?"

        recap = self.config_loader.get_prompt(
            "recap",
            servizio=servizio,
            operatore=operatore,
            data=data_formatted,
            ora=ora
        )
        return f"{recap} Confermato?"

    def _save_booking(self) -> Tuple[str, DialogState]:
        """Salva prenotazione nel DB"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Ottieni o crea cliente
            cliente_id = self.context.db_client_id
            if not cliente_id:
                nome = self.context.slot_values.get("cliente_nome", "")
                telefono = self.context.slot_values.get("cliente_tel", "")

                # Splitta nome/cognome
                parti = nome.split(" ", 1)
                nome_db = parti[0]
                cognome_db = parti[1] if len(parti) > 1 else ""

                cursor.execute("""
                    INSERT INTO clienti (nome, cognome, telefono, created_at)
                    VALUES (?, ?, ?, datetime('now'))
                """, (nome_db, cognome_db, telefono))
                cliente_id = cursor.lastrowid

            # Trova servizio_id
            servizio_nome = self.context.slot_values.get("servizio", "")
            cursor.execute(
                "SELECT id FROM servizi WHERE nome LIKE ? LIMIT 1",
                (f"%{servizio_nome}%",)
            )
            row = cursor.fetchone()
            servizio_id = row[0] if row else 1

            # Trova operatore_id
            operatore_nome = self.context.slot_values.get("operatore", "")
            operatore_id = None
            if operatore_nome and operatore_nome != "primo disponibile":
                cursor.execute(
                    "SELECT id FROM operatori WHERE nome LIKE ? LIMIT 1",
                    (f"%{operatore_nome.split()[0]}%",)
                )
                row = cursor.fetchone()
                operatore_id = row[0] if row else None

            # Inserisci appuntamento
            data = self.context.slot_values.get("data", "")
            ora = self.context.slot_values.get("ora", "")
            if ora == "first_available":
                ora = "09:00"

            cursor.execute("""
                INSERT INTO appuntamenti
                (cliente_id, servizio_id, operatore_id, data, ora_inizio, stato, created_at)
                VALUES (?, ?, ?, ?, ?, 'confermato', datetime('now'))
            """, (cliente_id, servizio_id, operatore_id, data, ora))

            conn.commit()
            conn.close()

            self.context.state = DialogState.SUCCESS

            data_formatted = self._format_date_italian(data)
            response = self.config_loader.get_prompt("success", data=data_formatted)
            self._log_turn("assistant", response)

            return response, DialogState.SUCCESS

        except Exception as e:
            self.context.error_messages.append(str(e))
            self.context.state = DialogState.ERROR
            response = f"Scusate, c'e stato un problema tecnico. Vi passo a un collega."
            self._log_turn("assistant", response)
            print(f"[GUIDED] Save error: {e}")
            return response, DialogState.ERROR

    def _match_faq_inline(self, user_input: str) -> Optional[str]:
        """Match FAQ inline (prezzi, orari, etc.)"""
        user_lower = user_input.lower()

        for faq in self.config_loader.get_faq_inline():
            triggers = faq.get("triggers", [])
            if any(trigger in user_lower for trigger in triggers):
                return faq.get("risposta", "")

        return None

    def _lookup_cliente(self, phone: str) -> None:
        """Lookup cliente nel DB"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id, nome, cognome FROM clienti WHERE telefono = ?",
                (phone,)
            )

            row = cursor.fetchone()
            if row:
                self.context.db_client_id = row["id"]
                # sqlite3.Row doesn't have .get() - use dict() or direct access
                cognome = row["cognome"] if row["cognome"] else ""
                nome = f"{row['nome']} {cognome}".strip()
                self.context.slot_values["cliente_nome"] = nome
                self.context.slot_values["cliente_tel"] = phone

            conn.close()
        except Exception as e:
            print(f"[GUIDED] Lookup error: {e}")

    def _get_client_name(self) -> str:
        """Ottieni nome cliente da context"""
        return self.context.slot_values.get("cliente_nome", "Cliente")

    def _get_available_dates(self, limit: int = 7) -> List[str]:
        """Ottieni date disponibili (prossimi N giorni)"""
        dates = []
        today = datetime.now()
        for i in range(1, limit + 1):
            date = (today + timedelta(days=i)).strftime("%Y-%m-%d")
            dates.append(date)
        return dates

    def _get_available_times(self, limit: int = 5) -> List[str]:
        """Ottieni ore disponibili"""
        # TODO: Query reale da availability table
        return ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00", "17:00"][:limit]

    def _format_date_italian(self, date_str: str) -> str:
        """Formatta data in italiano"""
        if not date_str or date_str == "?":
            return date_str

        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            weekday_names = [
                "lunedi", "martedi", "mercoledi", "giovedi",
                "venerdi", "sabato", "domenica"
            ]
            month_names = [
                "", "gennaio", "febbraio", "marzo", "aprile", "maggio",
                "giugno", "luglio", "agosto", "settembre", "ottobre",
                "novembre", "dicembre"
            ]
            weekday = weekday_names[date_obj.weekday()]
            month = month_names[date_obj.month]
            return f"{weekday} {date_obj.day} {month}"
        except Exception:
            return date_str

    def _log_turn(self, speaker: str, message: str) -> None:
        """Log turno conversazione"""
        self.context.conversation_history.append({
            "speaker": speaker,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "state": self.context.state.value
        })

    def get_context(self) -> Dict:
        """Ottieni contesto per debug"""
        if not self.context:
            return {}
        return self.context.to_dict()


# ============================================================
# FASTAPI BRIDGE (Per Tauri)
# ============================================================

class VoiceAgentServer:
    """FastAPI server bridge per Tauri desktop app"""

    def __init__(self, db_path: str, config_path: Optional[Path] = None):
        self.db_path = db_path
        self.config_path = config_path
        self.engines: Dict[str, GuidedDialogEngine] = {}
        self.sessions: Dict[str, DialogContext] = {}

    def create_session(
        self,
        vertical_id: str,
        user_phone: Optional[str] = None
    ) -> Dict:
        """Crea nuova sessione dialogo"""
        engine = GuidedDialogEngine(vertical_id, self.db_path, self.config_path)
        greeting, context = engine.start_dialog(user_phone)

        session_id = f"{vertical_id}_{datetime.now().timestamp()}"
        if user_phone:
            session_id = f"{vertical_id}_{user_phone}_{datetime.now().timestamp()}"

        self.sessions[session_id] = context
        self.engines[session_id] = engine

        return {
            "session_id": session_id,
            "greeting": greeting,
            "state": context.state.value,
            "context": context.to_dict()
        }

    def process_input(self, session_id: str, user_input: str) -> Dict:
        """Processa input in sessione"""
        if session_id not in self.engines:
            return {"error": "Session not found", "session_id": session_id}

        engine = self.engines[session_id]
        response, new_state = engine.process_user_input(user_input)

        return {
            "session_id": session_id,
            "response": response,
            "state": new_state.value,
            "context": engine.get_context()
        }

    def get_session(self, session_id: str) -> Dict:
        """Ottieni stato sessione"""
        if session_id not in self.engines:
            return {"error": "Session not found"}

        engine = self.engines[session_id]
        return {
            "session_id": session_id,
            "context": engine.get_context()
        }

    def close_session(self, session_id: str) -> Dict:
        """Chiudi sessione"""
        if session_id in self.engines:
            del self.engines[session_id]
        if session_id in self.sessions:
            del self.sessions[session_id]
        return {"status": "closed", "session_id": session_id}

    def list_sessions(self) -> List[str]:
        """Lista sessioni attive"""
        return list(self.engines.keys())


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    print("=== GUIDED DIALOG ENGINE TEST ===\n")

    # Path DB (usa :memory: per test)
    db_path = ":memory:"

    # Setup DB di test
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clienti (
            id INTEGER PRIMARY KEY,
            nome TEXT, cognome TEXT,
            telefono TEXT UNIQUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS servizi (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            prezzo REAL,
            attivo BOOLEAN DEFAULT 1
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS operatori (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            cognome TEXT,
            attivo BOOLEAN DEFAULT 1
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appuntamenti (
            id INTEGER PRIMARY KEY,
            cliente_id INTEGER,
            servizio_id INTEGER,
            operatore_id INTEGER,
            data DATE,
            ora_inizio TIME,
            stato TEXT DEFAULT 'confermato',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Insert test data
    cursor.execute("INSERT INTO servizi (nome, prezzo) VALUES ('Taglio uomo', 20)")
    cursor.execute("INSERT INTO servizi (nome, prezzo) VALUES ('Taglio donna', 30)")
    cursor.execute("INSERT INTO servizi (nome, prezzo) VALUES ('Piega', 15)")
    cursor.execute("INSERT INTO operatori (nome, cognome) VALUES ('Marco', 'Rossi')")
    cursor.execute("INSERT INTO operatori (nome, cognome) VALUES ('Giulia', 'Bianchi')")
    conn.commit()

    # Salva DB temporaneo
    import tempfile
    import shutil

    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        temp_db = f.name

    # Copia DB in-memory a file
    disk_conn = sqlite3.connect(temp_db)
    conn.backup(disk_conn)
    disk_conn.close()
    conn.close()

    print(f"Test DB: {temp_db}\n")

    # Crea engine
    engine = GuidedDialogEngine(
        vertical_id="salone",
        db_path=temp_db
    )

    # Simula conversazione
    print("--- START SESSION ---")
    greeting, context = engine.start_dialog(user_phone=None)
    print(f"SARA: {greeting}")
    print(f"STATE: {context.state.value}\n")

    # Test inputs
    test_conversation = [
        ("1", "Seleziona primo servizio (Taglio uomo)"),
        ("Marco", "Seleziona operatore Marco"),
        ("domani", "Seleziona domani"),
        ("mattina", "Seleziona mattina"),
        ("Mario Rossi", "Nome cliente"),
        ("3331234567", "Telefono"),
        ("si", "Conferma"),
    ]

    for user_input, description in test_conversation:
        print(f"USER: {user_input} ({description})")
        response, state = engine.process_user_input(user_input)
        print(f"SARA: {response}")
        print(f"STATE: {state.value}\n")

        if state in [DialogState.SUCCESS, DialogState.ERROR]:
            break

    print("--- FINAL CONTEXT ---")
    import json
    print(json.dumps(engine.get_context(), indent=2, ensure_ascii=False))

    # Cleanup
    import os
    os.unlink(temp_db)

    print("\n=== TEST COMPLETATO ===")
