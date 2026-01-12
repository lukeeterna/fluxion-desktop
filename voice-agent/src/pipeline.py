"""
FLUXION Voice Agent - Main Pipeline
Orchestrates STT -> LLM -> TTS flow with RAG and DB integration
"""

import os
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Callable
from pathlib import Path

from .groq_client import GroqClient
from .tts import get_tts, PiperTTS, SystemTTS
from .intent_classifier import classify_intent, IntentCategory
from .entity_extractor import extract_date, extract_time, extract_name, extract_all

# Try to import FAQ Manager (hybrid keyword + semantic)
try:
    from .faq_manager import FAQManager, FAQConfig, create_faq_manager
    HAS_FAQ_MANAGER = True
except ImportError:
    HAS_FAQ_MANAGER = False

# Import Sentiment Analyzer (Week 3 Day 1-2)
from .sentiment import SentimentAnalyzer, FrustrationLevel, Sentiment

# Import Error Recovery (Week 3 Day 3-4)
from .error_recovery import (
    RecoveryManager,
    get_fallback_response,
    get_recovery_manager,
    ErrorCategory,
)

# HTTP Bridge URL (Tauri backend)
HTTP_BRIDGE_URL = "http://127.0.0.1:3001"

# System prompt template with FAQ knowledge
SYSTEM_PROMPT = """
Sei Paola, l'assistente vocale di {business_name}.

PERSONALITA':
- Cordiale, professionale, empatica
- Parli italiano fluente con accento neutro
- Risposte BREVI (massimo 2-3 frasi per volta)
- Usa "Lei" (formale), ma in modo caldo

CAPACITA':
1. Prenotare appuntamenti
2. Verificare disponibilita'
3. Cancellare appuntamenti
4. Fornire info su servizi e prezzi
5. Spostare appuntamenti esistenti

INFORMAZIONI ATTIVITA':
- Nome: {business_name}
- Orari: {opening_hours} - {closing_hours}
- Giorni: {working_days}
- Servizi: {services}

KNOWLEDGE BASE (USA QUESTE INFO PER RISPONDERE):
{faq_knowledge}

FLOW PRENOTAZIONE:
1. Se cliente vuole prenotare, chiedi:
   a. Nome (se non lo conosci gia')
   b. Quale servizio desidera
   c. Giorno e ora preferiti
2. Conferma tutti i dettagli
3. Concludi con conferma prenotazione

REGOLE IMPORTANTI:
- Usa SOLO le informazioni dalla KNOWLEDGE BASE sopra
- NON inventare prezzi, orari o servizi non elencati
- Se non hai l'informazione, dì che verifichi e richiami
- Rispondi SEMPRE in italiano
- Se riconosci il nome del cliente, salutalo per nome
"""


def load_faq_file(faq_path: Path, settings: dict = None) -> tuple[str, dict]:
    """Load FAQ markdown file, substitute variables, return (knowledge_str, qa_dict)."""
    if not faq_path.exists():
        return "", {}

    content = faq_path.read_text(encoding='utf-8')

    # Substitute {{variable}} placeholders with settings values
    if settings:
        import re
        def replace_var(match):
            var_name = match.group(1)
            return settings.get(var_name, f"[{var_name}]")
        content = re.sub(r'\{\{(\w+)\}\}', replace_var, content)

    # Parse markdown FAQ format
    knowledge = []
    qa_dict = {}  # For direct lookup

    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('- ') and ':' in line:
            # Q&A format: "- question: answer"
            parts = line[2:].split(':', 1)
            if len(parts) == 2:
                q, a = parts[0].strip().lower(), parts[1].strip()
                # Skip lines with unresolved variables
                if '[' not in a:
                    knowledge.append(f"D: {q}\nR: {a}")
                    qa_dict[q] = a
                    # Also store key words
                    for word in q.split():
                        if len(word) > 3:
                            if word not in qa_dict:
                                qa_dict[word] = a

    return '\n\n'.join(knowledge), qa_dict


async def load_faq_settings_from_db() -> dict:
    """Load FAQ settings from database via HTTP Bridge."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{HTTP_BRIDGE_URL}/api/faq/settings",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
    except Exception as e:
        print(f"   Could not load FAQ settings: {e}")
    return {}


def find_faq_answer(text: str, qa_dict: dict) -> Optional[str]:
    """Find FAQ answer using keyword matching."""
    text_lower = text.lower()

    # Special handling for price queries - most common question
    if any(kw in text_lower for kw in ["quanto costa", "prezzo", "costo", "costa"]):
        # Check what service they're asking about
        for service, price_key in [
            ("taglio", "quanto costa un taglio"),
            ("colore", "quanto costa il colore"),
            ("barba", "barba"),
            ("piega", "piega"),
            ("trattamento", "trattamento cheratina")
        ]:
            if service in text_lower:
                # Look for exact match first
                if price_key in qa_dict:
                    return qa_dict[price_key]
                # Look for service name in question
                for q, a in qa_dict.items():
                    if service in q and ("€" in a or "euro" in a.lower()):
                        return a
        # Generic price request
        if "quanto costa un taglio" in qa_dict:
            return qa_dict["quanto costa un taglio"]

    # Direct phrase matching - exact match in question
    for question, answer in qa_dict.items():
        if len(question) > 5 and question in text_lower:
            return answer

    # Reverse match - check if user text contains FAQ question key
    for question, answer in qa_dict.items():
        if len(question) > 5 and text_lower in question:
            return answer

    # Keyword matching with scoring
    best_match = None
    best_score = 0

    keywords_map = {
        "prezzo": ["quanto costa", "prezzo", "prezzi", "costo", "costa", "euro"],
        "orario": ["orario", "orari", "aprite", "chiudete", "aperti", "quando apre", "a che ora"],
        "taglio": ["taglio", "tagliare", "tagliata"],
        "colore": ["colore", "tinta", "colorare"],
        "barba": ["barba"],
        "pagamento": ["pagare", "carta", "contanti", "satispay", "bancomat"],
        "parcheggio": ["parcheggio", "parcheggiare", "posteggio"],
        "prenot": ["prenotare", "prenoto", "prenotazione", "disdire", "appuntamento"],
        "wifi": ["wifi", "internet", "connessione"],
        "prodotti": ["prodotti", "shampoo", "comprare"],
    }

    for category, keywords in keywords_map.items():
        for kw in keywords:
            if kw in text_lower:
                # Find relevant FAQ - give higher score to longer matches
                for q, a in qa_dict.items():
                    if category in q or any(k in q for k in keywords):
                        # Score based on: keyword matches + answer length (prefer detailed answers)
                        score = sum(1 for k in keywords if k in text_lower)
                        # Boost score if answer contains price (euro sign)
                        if "€" in a:
                            score += 2
                        if score > best_score:
                            best_score = score
                            best_match = a

    return best_match if best_score >= 1 else None


class VoicePipeline:
    """
    FLUXION Voice Agent Pipeline with RAG and DB integration.
    """

    def __init__(
        self,
        business_config: Dict[str, Any],
        groq_api_key: Optional[str] = None,
        use_piper: bool = True,
        faq_path: Optional[Path] = None
    ):
        self.config = business_config
        self.groq = GroqClient(api_key=groq_api_key)
        self.tts = get_tts(use_piper=use_piper)

        self.conversation_history: List[Dict[str, str]] = []
        self.current_intent: Optional[str] = None
        self.booking_context: Dict[str, Any] = {}
        self.identified_client: Optional[Dict] = None

        # Load FAQ knowledge base (will be populated by load_faq_async)
        self.faq_knowledge = ""
        self.faq_dict = {}
        self.faq_path = faq_path
        self._faq_loaded = False

        # Initialize Sentiment Analyzer (Week 3 Day 1-2)
        self.sentiment_analyzer = SentimentAnalyzer()

        # Initialize Recovery Manager (Week 3 Day 3-4)
        self.recovery_manager = get_recovery_manager()

        # Initialize FAQ Manager (hybrid keyword + semantic retrieval)
        self.faq_manager = None
        if HAS_FAQ_MANAGER:
            self.faq_manager = FAQManager()
            # Try JSON FAQ first (structured, with categories)
            json_faq_paths = [
                Path(__file__).parent.parent / "data" / "faq_salone_test.json",
                Path("data/faq_salone_test.json"),
            ]
            for json_path in json_faq_paths:
                if json_path.exists():
                    self.faq_manager.load_faqs_from_json(str(json_path))
                    print(f"   [FAQManager] Loaded JSON FAQ: {json_path}")
                    break

        # Try to load static FAQ synchronously (legacy, for system prompt)
        faq_paths = [
            Path(__file__).parent.parent / "data" / "faq_salone.md",
            Path("data/faq_salone.md"),
        ]
        for path in faq_paths:
            if path.exists():
                self.faq_knowledge, self.faq_dict = load_faq_file(path)
                print(f"   Loaded static FAQ from: {path} ({len(self.faq_dict)} entries)")
                # Also load markdown into FAQManager if available
                if self.faq_manager:
                    self.faq_manager.load_faqs_from_markdown(str(path))
                break

        # Build initial system prompt
        self.system_prompt = self._build_system_prompt()

        # Callbacks
        self.on_transcription: Optional[Callable[[str], None]] = None
        self.on_response: Optional[Callable[[str], None]] = None
        self.on_intent: Optional[Callable[[str], None]] = None
        self.on_booking: Optional[Callable[[Dict], None]] = None

    async def load_faq_from_db(self):
        """Load FAQ with variables substituted from database."""
        if self._faq_loaded:
            return

        # Load settings from DB
        settings = await load_faq_settings_from_db()
        if not settings:
            print("   No FAQ settings from DB, using static FAQ")
            self._faq_loaded = True
            return

        # Try to load FAQ with variables
        faq_var_paths = [
            Path(__file__).parent.parent.parent / "data" / "faq_salone_variabili.md",
            Path("data/faq_salone_variabili.md"),
        ]
        for path in faq_var_paths:
            if path.exists():
                self.faq_knowledge, self.faq_dict = load_faq_file(path, settings)
                print(f"   Loaded dynamic FAQ from: {path} ({len(self.faq_dict)} entries)")
                break

        self._faq_loaded = True
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        """Build system prompt from config and FAQ."""
        return SYSTEM_PROMPT.format(
            business_name=self.config.get("business_name", "FLUXION"),
            opening_hours=self.config.get("opening_hours", "09:00"),
            closing_hours=self.config.get("closing_hours", "19:00"),
            working_days=self.config.get("working_days", "Martedi-Sabato"),
            services=", ".join(self.config.get("services", ["Taglio", "Piega", "Colore"])),
            faq_knowledge=self.faq_knowledge if self.faq_knowledge else "Nessuna FAQ caricata"
        )

    async def _call_http_bridge(self, endpoint: str, method: str = "GET", data: Dict = None) -> Optional[Dict]:
        """Call Tauri HTTP bridge for database operations."""
        try:
            url = f"{HTTP_BRIDGE_URL}{endpoint}"
            async with aiohttp.ClientSession() as session:
                if method == "GET":
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                        if resp.status == 200:
                            return await resp.json()
                else:
                    async with session.post(url, json=data, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                        if resp.status == 200:
                            return await resp.json()
        except Exception as e:
            print(f"   HTTP Bridge error: {e}")
        return None

    async def search_client(self, name: str, data_nascita: Optional[str] = None) -> Dict:
        """
        Search for client by name in database.
        Returns: {clienti: [...], ambiguo: bool, messaggio: str}
        If ambiguo=True, need to ask for data_nascita to disambiguate.
        """
        # Build query params
        url = f"/api/clienti/search?q={name}"
        if data_nascita:
            url += f"&data_nascita={data_nascita}"

        result = await self._call_http_bridge(url)

        # Handle new response format with disambiguation
        if result:
            if "clienti" in result:
                return result  # New format {clienti, ambiguo, messaggio}
            elif isinstance(result, list):
                # Old format compatibility
                return {"clienti": result, "ambiguo": len(result) > 1, "messaggio": ""}

        return {"clienti": [], "ambiguo": False, "messaggio": ""}

    async def get_operatori(self) -> List[Dict]:
        """Get list of operators with specializations and positive descriptions."""
        result = await self._call_http_bridge("/api/operatori/list")
        if result and isinstance(result, list):
            return result
        return []

    async def check_operatore_disponibilita(self, operatore_id: str, data: str, ora: Optional[str] = None) -> Dict:
        """
        Check operator availability for a date/time.
        Returns: {disponibile, slots, alternative_operators (if not available)}
        """
        result = await self._call_http_bridge(
            "/api/operatori/disponibilita",
            method="POST",
            data={"operatore_id": operatore_id, "data": data, "ora": ora}
        )
        return result or {"disponibile": False, "slots": [], "alternative_operators": []}

    async def create_client(self, nome: str, cognome: Optional[str] = None,
                           telefono: Optional[str] = None, data_nascita: Optional[str] = None) -> Dict:
        """Create a new client via Voice Agent conversation."""
        result = await self._call_http_bridge(
            "/api/clienti/create",
            method="POST",
            data={
                "nome": nome,
                "cognome": cognome,
                "telefono": telefono,
                "data_nascita": data_nascita
            }
        )
        return result or {"success": False, "error": "Bridge non disponibile"}

    async def add_to_waitlist(self, cliente_id: str, servizio: str,
                              data_preferita: Optional[str] = None,
                              ora_preferita: Optional[str] = None,
                              operatore_preferito: Optional[str] = None,
                              priorita: str = "normale") -> Dict:
        """Add client to waitlist with optional VIP priority."""
        result = await self._call_http_bridge(
            "/api/waitlist/add",
            method="POST",
            data={
                "cliente_id": cliente_id,
                "servizio": servizio,
                "data_preferita": data_preferita,
                "ora_preferita": ora_preferita,
                "operatore_preferito": operatore_preferito,
                "priorita": priorita
            }
        )
        return result or {"success": False, "error": "Bridge non disponibile"}

    async def get_disponibilita(self, data: str, servizio: str) -> List[str]:
        """Get available time slots for a date."""
        result = await self._call_http_bridge(
            "/api/appuntamenti/disponibilita",
            method="POST",
            data={"data": data, "servizio": servizio}
        )
        if result and "slots" in result:
            return result["slots"]
        # Default slots if bridge not available
        return ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00", "17:00"]

    async def crea_appuntamento(self, cliente_id: str, servizio: str, data: str, ora: str,
                                operatore_id: Optional[str] = None) -> Dict:
        """Create appointment via HTTP bridge with optional operator preference."""
        payload = {
            "cliente_id": cliente_id,
            "servizio": servizio,
            "data": data,
            "ora": ora
        }
        if operatore_id:
            payload["operatore_id"] = operatore_id

        result = await self._call_http_bridge(
            "/api/appuntamenti/create",
            method="POST",
            data=payload
        )
        return result or {"success": False, "error": "Bridge non disponibile"}

    def _extract_booking_info(self, text: str) -> Dict[str, Any]:
        """Extract booking information from user text.

        Uses the enterprise entity extractor for date/time/name extraction,
        with fallback to specialized patterns for specific use cases.
        """
        text_lower = text.lower()
        info = {}

        # =================================================================
        # ENTERPRISE ENTITY EXTRACTION (Day 3)
        # Use the new entity extractor for date/time/name
        # =================================================================
        services_config = {
            "taglio": ["taglio", "tagliare", "accorciare", "sforbiciata", "spuntatina"],
            "piega": ["piega", "messa in piega", "asciugatura"],
            "colore": ["colore", "tinta", "colorare", "colorazione"],
            "barba": ["barba", "rasatura"],
            "trattamento": ["trattamento", "cheratina", "maschera"]
        }

        extracted = extract_all(text, services_config)

        # Populate info from extracted entities
        if extracted.date:
            info["data"] = extracted.date.to_string("%Y-%m-%d")
            info["data_italiana"] = extracted.date.to_italian()
            print(f"   [ENTITY] Date: {info['data']} ({info['data_italiana']})")

        if extracted.time:
            info["ora"] = extracted.time.to_string()
            if extracted.time.is_approximate:
                info["preferenza_orario"] = extracted.time.original_text
            print(f"   [ENTITY] Time: {info['ora']}")

        if extracted.service:
            info["servizio"] = extracted.service
            print(f"   [ENTITY] Service: {info['servizio']}")

        if extracted.name:
            info["cliente_nome_estratto"] = extracted.name.name
            print(f"   [ENTITY] Name: {info['cliente_nome_estratto']}")

        if extracted.phone:
            info["telefono"] = extracted.phone
            print(f"   [ENTITY] Phone: {info['telefono']}")

        if extracted.email:
            info["email"] = extracted.email
            print(f"   [ENTITY] Email: {info['email']}")

        # =================================================================
        # FALLBACK: Legacy extraction for fields not covered
        # =================================================================

        # Extract service (fallback if not found by entity extractor)
        if "servizio" not in info:
            for service, keywords in services_config.items():
                if any(kw in text_lower for kw in keywords):
                    info["servizio"] = service
                    break

        # Legacy time preference (kept for compatibility)
        if "preferenza_orario" not in info:
            if "pomeriggio" in text_lower:
                info["preferenza_orario"] = "pomeriggio"
            elif "mattina" in text_lower:
                info["preferenza_orario"] = "mattina"

        # Extract birth date for client disambiguation
        # Patterns: "sono nato il 15 marzo 1985", "15/03/1985", "15-03-1985", "1985-03-15"
        import re

        # Italian months mapping
        mesi_it = {
            "gennaio": "01", "febbraio": "02", "marzo": "03", "aprile": "04",
            "maggio": "05", "giugno": "06", "luglio": "07", "agosto": "08",
            "settembre": "09", "ottobre": "10", "novembre": "11", "dicembre": "12"
        }

        # Pattern: "15 marzo 1985" or "nato il 15 marzo 1985"
        date_pattern_it = r'(?:nato|nata|nascita)[^\d]*(\d{1,2})\s+(\w+)\s+(\d{4})'
        match = re.search(date_pattern_it, text_lower)
        if match:
            day, month_name, year = match.groups()
            month = mesi_it.get(month_name.lower())
            if month:
                info["data_nascita"] = f"{year}-{month}-{day.zfill(2)}"
                print(f"   Extracted birth date (IT): {info['data_nascita']}")

        # Pattern: "15/03/1985" or "15-03-1985"
        if "data_nascita" not in info:
            date_pattern_slash = r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})'
            match = re.search(date_pattern_slash, text_lower)
            if match:
                day, month, year = match.groups()
                info["data_nascita"] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                print(f"   Extracted birth date (slash): {info['data_nascita']}")

        # Pattern: "1985-03-15" (ISO format)
        if "data_nascita" not in info:
            date_pattern_iso = r'(\d{4})-(\d{2})-(\d{2})'
            match = re.search(date_pattern_iso, text_lower)
            if match:
                info["data_nascita"] = match.group(0)
                print(f"   Extracted birth date (ISO): {info['data_nascita']}")

        # Extract phone number for new client registration
        # Patterns: "333 1234567", "333.123.4567", "+39 333 1234567"
        phone_patterns = [
            r'(?:numero|telefono|cell(?:ulare)?)[^\d]*(\+?\d[\d\s\.\-]{7,})',  # "numero è 333..."
            r'(?:mi\s+trovi\s+al|chiamami\s+al)[^\d]*(\+?\d[\d\s\.\-]{7,})',  # "chiamami al 333..."
            r'(\+39\s*\d{3}[\s\.\-]?\d{3}[\s\.\-]?\d{4})',  # +39 format
            r'(3\d{2}[\s\.\-]?\d{3}[\s\.\-]?\d{4})',  # Italian mobile starting with 3
        ]
        for pattern in phone_patterns:
            match = re.search(pattern, text_lower)
            if match:
                # Clean phone number
                phone = re.sub(r'[\s\.\-]', '', match.group(1))
                info["telefono"] = phone
                print(f"   Extracted phone: {phone}")
                break

        # Extract full name with surname for registration
        # Patterns: "mi chiamo Mario Rossi", "sono Mario Rossi", "nome è Mario cognome Rossi"
        fullname_patterns = [
            r'(?:mi\s+chiamo|sono)\s+([A-Z][a-z]+)\s+([A-Z][a-z]+)',  # "mi chiamo Mario Rossi"
            r'nome\s+(?:è\s+)?([A-Z][a-z]+).*cognome\s+(?:è\s+)?([A-Z][a-z]+)',  # "nome Mario cognome Rossi"
        ]
        # Use original text for name extraction (preserve case)
        for pattern in fullname_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info["nuovo_cliente_nome_completo"] = match.group(1).capitalize()
                info["nuovo_cliente_cognome"] = match.group(2).capitalize()
                print(f"   Extracted full name: {info['nuovo_cliente_nome_completo']} {info['nuovo_cliente_cognome']}")
                break

        # Extract email
        email_pattern = r'[\w\.\-]+@[\w\.\-]+\.\w+'
        email_match = re.search(email_pattern, text_lower)
        if email_match:
            info["email"] = email_match.group(0)
            print(f"   Extracted email: {info['email']}")

        # Extract operator preference: "con Maria", "preferisco Marco Rossi", "da Laura Bianchi"
        # Patterns capture name + optional surname (2 words)
        # NOTE: Order matters - more specific patterns first
        operator_patterns = [
            r'(?:come\s+)?operatore\s+(\w+(?:\s+\w+)?)',  # "come operatore Marco Rossi" or "operatore Marco"
            r'(?:preferisco|vorrei)\s+(\w+(?:\s+\w+)?)\s+(?:come\s+)?operatore',  # "preferisco Marco Rossi come operatore"
            r'(?:preferisco|vorrei)\s+(?:come\s+)?operatore\s+(\w+(?:\s+\w+)?)',  # "vorrei come operatore Marco Rossi"
            r'con\s+(\w+(?:\s+\w+)?)\s+(?:come\s+)?operatore',  # "con Maria come operatore"
            r'preferisco\s+(\w+(?:\s+\w+)?)',  # "preferisco Laura Bianchi"
            r'con\s+(\w+(?:\s+\w+)?)',  # "con Marco Rossi" (with optional surname)
            r'da\s+(\w+(?:\s+\w+)?)',  # "da Marco Rossi" (with optional surname)
        ]
        for pattern in operator_patterns:
            match = re.search(pattern, text_lower)
            if match:
                # Capitalize each word in name
                name_parts = match.group(1).split()
                potential_operator = ' '.join(word.capitalize() for word in name_parts)
                info["operatore_preferito_nome"] = potential_operator
                print(f"   Extracted operator preference: {potential_operator}")
                break

        return info

    async def process_audio(self, audio_data: bytes) -> Dict[str, Any]:
        """Process audio input through full pipeline."""
        # Step 1: Speech-to-Text
        transcription = await self.groq.transcribe_audio(audio_data)

        if self.on_transcription:
            self.on_transcription(transcription)

        return await self._process_input(transcription)

    async def process_text(self, text: str) -> Dict[str, Any]:
        """Process text input."""
        return await self._process_input(text)

    async def _process_input(self, text: str) -> Dict[str, Any]:
        """Process user input (text or transcribed audio)."""
        # Load FAQ from DB on first request (lazy loading)
        if not self._faq_loaded:
            await self.load_faq_from_db()

        # Detect intent
        intent = self.groq._detect_intent(text)
        self.current_intent = intent

        if self.on_intent:
            self.on_intent(intent)

        # Extract booking info and update context
        booking_info = self._extract_booking_info(text)
        self.booking_context.update(booking_info)

        # Handle disambiguation with birth date (if user provided data_nascita in response)
        if self.booking_context.get("needs_disambiguation") and booking_info.get("data_nascita"):
            # User provided birth date to disambiguate
            potential_name = self.booking_context.get("disambiguazione_nome", "")
            data_nascita = booking_info["data_nascita"]
            print(f"   Disambiguating '{potential_name}' with birth date: {data_nascita}")

            result = await self.search_client(potential_name, data_nascita=data_nascita)
            clienti = result.get("clienti", [])

            if len(clienti) == 1:
                # Found unique match with birth date
                client = clienti[0]
                self.identified_client = client
                self.booking_context["cliente_id"] = client.get("id")
                self.booking_context["cliente_nome"] = client.get("nome")
                self.booking_context["needs_disambiguation"] = False
                del self.booking_context["potential_clients"]
                print(f"   Cliente disambiguato: {client.get('nome')} {client.get('cognome')}")
            elif not clienti:
                # Birth date didn't match any client - propose registration
                self.booking_context["needs_disambiguation"] = False
                self.booking_context["cliente_non_trovato"] = True
                self.booking_context["proponi_registrazione"] = True
                print(f"   Nessun cliente trovato con data nascita {data_nascita}, propongo registrazione")

        # Try to identify client if name mentioned (only if not already identified/disambiguating)
        if not self.identified_client and not self.booking_context.get("needs_disambiguation"):
            words = text.split()
            for i, word in enumerate(words):
                # Look for "sono X" or "mi chiamo X" patterns
                if word.lower() in ["sono", "chiamo"] and i + 1 < len(words):
                    potential_name = words[i + 1].capitalize()
                    if len(potential_name) > 2:
                        result = await self.search_client(potential_name)
                        clienti = result.get("clienti", [])

                        if result.get("ambiguo"):
                            # Multiple matches - need disambiguation
                            self.booking_context["needs_disambiguation"] = True
                            self.booking_context["potential_clients"] = clienti
                            self.booking_context["disambiguazione_nome"] = potential_name
                            print(f"   Client ambiguo: {len(clienti)} matches per '{potential_name}'")
                        elif clienti:
                            # Single match - client identified
                            client = clienti[0]
                            self.identified_client = client
                            self.booking_context["cliente_id"] = client.get("id")
                            self.booking_context["cliente_nome"] = client.get("nome")
                            print(f"   Cliente identificato: {client.get('nome')} {client.get('cognome')}")
                        else:
                            # No client found - propose registration
                            self.booking_context["cliente_non_trovato"] = True
                            self.booking_context["proponi_registrazione"] = True
                            self.booking_context["nuovo_cliente_nome"] = potential_name
                            print(f"   Cliente '{potential_name}' non trovato, propongo registrazione")

        # Try to create new client if we have enough info
        if self.booking_context.get("proponi_registrazione") and not self.identified_client:
            # Check if we have minimum required data (name + phone)
            nome = booking_info.get("nuovo_cliente_nome_completo") or self.booking_context.get("nuovo_cliente_nome")
            cognome = booking_info.get("nuovo_cliente_cognome")
            telefono = booking_info.get("telefono") or self.booking_context.get("telefono")
            data_nascita = booking_info.get("data_nascita")
            email = booking_info.get("email")

            if nome and telefono:
                # We have minimum data - create client
                print(f"   Creating new client: {nome} {cognome or ''}, tel: {telefono}")
                result = await self.create_client(
                    nome=nome,
                    cognome=cognome,
                    telefono=telefono,
                    data_nascita=data_nascita
                )
                if result.get("success"):
                    # Client created successfully
                    self.identified_client = {
                        "id": result.get("cliente_id"),
                        "nome": nome,
                        "cognome": cognome,
                        "telefono": telefono
                    }
                    self.booking_context["cliente_id"] = result.get("cliente_id")
                    self.booking_context["cliente_nome"] = nome
                    self.booking_context["cliente_registrato"] = True
                    self.booking_context["proponi_registrazione"] = False
                    print(f"   Nuovo cliente registrato: {nome} {cognome or ''} (ID: {result.get('cliente_id')})")
                else:
                    print(f"   Errore creazione cliente: {result.get('error')}")

        # Handle operator preference if mentioned
        if "operatore_preferito_nome" in self.booking_context and not self.booking_context.get("operatore_id"):
            op_name = self.booking_context["operatore_preferito_nome"].lower()
            operatori = await self.get_operatori()

            # Try to match operator by: full name, nome only, or cognome only
            for op in operatori:
                nome = op.get("nome", "").lower()
                cognome = op.get("cognome", "").lower()
                full_name = f"{nome} {cognome}".strip()

                # Match conditions: full name, nome+cognome, nome only, cognome only
                if (op_name == full_name or
                    op_name == nome or
                    op_name == cognome or
                    (nome and cognome and op_name == f"{nome} {cognome}") or
                    (nome in op_name) or
                    (cognome and cognome in op_name)):
                    self.booking_context["operatore_id"] = op.get("id")
                    self.booking_context["operatore_nome"] = op.get("nome")
                    self.booking_context["operatore_cognome"] = op.get("cognome")
                    self.booking_context["operatore_descrizione"] = op.get("descrizione_positiva")
                    print(f"   Operatore preferito trovato: {op.get('nome')} {op.get('cognome', '')} - {op.get('descrizione_positiva')}")
                    break
            else:
                # No match found - log it
                print(f"   Operatore '{op_name}' non trovato nel database")

        # Check operator availability if we have operator, date and time
        if (self.booking_context.get("operatore_id") and
            self.booking_context.get("data") and
            not self.booking_context.get("operatore_disponibilita_checked")):
            op_id = self.booking_context["operatore_id"]
            data = self.booking_context["data"]
            ora = self.booking_context.get("ora")

            dispo = await self.check_operatore_disponibilita(op_id, data, ora)
            self.booking_context["operatore_disponibilita_checked"] = True

            if not dispo.get("disponibile"):
                # Operator not available - store alternatives
                self.booking_context["operatore_non_disponibile"] = True
                alternatives = dispo.get("alternative_operators", [])
                if alternatives:
                    self.booking_context["operatori_alternativi"] = alternatives
                    # Build suggestion text for LLM context
                    alt_text = []
                    for alt in alternatives[:3]:
                        desc = alt.get("descrizione_positiva", "esperto professionista")
                        slots = alt.get("slots_disponibili", [])[:3]
                        alt_text.append(f"{alt.get('nome')}: {desc} (disponibile: {', '.join(slots)})")
                    self.booking_context["suggerimento_alternativi"] = "; ".join(alt_text)
                    print(f"   Operatore non disponibile, alternative: {len(alternatives)}")
            else:
                self.booking_context["operatore_disponibile"] = True
                print(f"   Operatore disponibile: {self.booking_context.get('operatore_nome')}")

        # Handle waitlist intent or propose waitlist when no availability
        if intent == "waitlist" or (
            self.booking_context.get("operatore_non_disponibile") and
            not self.booking_context.get("operatori_alternativi") and
            self.identified_client
        ):
            # Check if client is VIP for priority
            is_vip = False
            if self.identified_client:
                is_vip = self.identified_client.get("is_vip", False)

            # If user explicitly wants waitlist, add them
            if intent == "waitlist" and self.identified_client:
                cliente_id = self.identified_client.get("id")
                servizio = self.booking_context.get("servizio", "taglio")
                data_pref = self.booking_context.get("data")
                ora_pref = self.booking_context.get("ora") or self.booking_context.get("preferenza_orario")
                operatore_pref = self.booking_context.get("operatore_id")
                priorita = "vip" if is_vip else "normale"

                print(f"   Adding to waitlist: {cliente_id}, servizio={servizio}, priorita={priorita}")
                result = await self.add_to_waitlist(
                    cliente_id=cliente_id,
                    servizio=servizio,
                    data_preferita=data_pref,
                    ora_preferita=ora_pref,
                    operatore_preferito=operatore_pref,
                    priorita=priorita
                )
                if result.get("success"):
                    self.booking_context["waitlist_aggiunto"] = True
                    self.booking_context["waitlist_posizione"] = result.get("posizione", "N/A")
                    self.booking_context["waitlist_priorita"] = priorita
                    print(f"   Aggiunto a waitlist con priorità {priorita}")
                else:
                    print(f"   Errore waitlist: {result.get('error')}")
            else:
                # Propose waitlist (operator not available, no alternatives)
                self.booking_context["proponi_waitlist"] = True
                self.booking_context["waitlist_priorita_potenziale"] = "VIP (priorità alta)" if is_vip else "normale"

        # Build context-aware message for LLM
        context_note = ""
        if self.identified_client:
            context_note = f"\n[NOTA SISTEMA: Cliente identificato come {self.identified_client.get('nome')} {self.identified_client.get('cognome', '')}]"

        # Special context for disambiguation
        if self.booking_context.get("needs_disambiguation"):
            clienti = self.booking_context.get("potential_clients", [])
            nomi = [f"{c.get('nome')} {c.get('cognome', '')}" for c in clienti[:3]]
            context_note += f"\n[DISAMBIGUAZIONE RICHIESTA: Trovati {len(clienti)} clienti con questo nome: {', '.join(nomi)}. Chiedi la data di nascita per confermare l'identità.]"

        # Context for new client registration
        if self.booking_context.get("proponi_registrazione"):
            nome_nuovo = self.booking_context.get("nuovo_cliente_nome", "")
            context_note += f"\n[NUOVO CLIENTE: '{nome_nuovo}' non è in archivio. Chiedi se vuole registrarsi. Se sì, chiedi: 1) Nome completo, 2) Cognome, 3) Numero di telefono, 4) Email (opzionale), 5) Data di nascita (per futura identificazione)]"

        # Context for successful registration
        if self.booking_context.get("cliente_registrato"):
            nome = self.booking_context.get("cliente_nome", "")
            context_note += f"\n[CLIENTE REGISTRATO: {nome} è stato registrato con successo! Ora puoi procedere con la prenotazione.]"

        # Context for waitlist proposal
        if self.booking_context.get("proponi_waitlist"):
            priorita = self.booking_context.get("waitlist_priorita_potenziale", "normale")
            context_note += f"\n[PROPONI LISTA D'ATTESA: Non ci sono slot disponibili. Proponi al cliente di essere inserito in lista d'attesa. Se accetta, sarà contattato al primo posto libero. Priorità: {priorita}. Chiedi: 'Vuole che la inserisca in lista d'attesa? La contatteremo appena si libera un posto.']"

        # Context for successful waitlist addition
        if self.booking_context.get("waitlist_aggiunto"):
            priorita = self.booking_context.get("waitlist_priorita", "normale")
            posizione = self.booking_context.get("waitlist_posizione", "")
            if priorita == "vip":
                context_note += f"\n[LISTA D'ATTESA CONFERMATA: Cliente VIP inserito con PRIORITÀ ALTA! Conferma: 'Perfetto! L'ho inserita in lista d'attesa con priorità VIP. La contatteremo prima degli altri non appena si libera un posto!']"
            else:
                context_note += f"\n[LISTA D'ATTESA CONFERMATA: Cliente inserito in lista d'attesa. Conferma: 'Perfetto! L'ho inserita in lista d'attesa. La contatteremo appena si libera un posto per il servizio richiesto.']"

        # Context for operator not available with alternatives
        if self.booking_context.get("operatore_non_disponibile"):
            op_nome = self.booking_context.get("operatore_nome", "l'operatore richiesto")
            suggerimenti = self.booking_context.get("suggerimento_alternativi", "")
            context_note += f"\n[OPERATORE NON DISPONIBILE: {op_nome} non è disponibile per questa data/ora. Proponi con entusiasmo queste alternative: {suggerimenti}]"
        elif self.booking_context.get("operatore_disponibile"):
            context_note += f"\n[OPERATORE DISPONIBILE: {self.booking_context.get('operatore_nome')} è disponibile]"

        # General booking context (filtered for sensitive info and already-noted items)
        safe_context = {k: v for k, v in self.booking_context.items()
                       if k not in ['potential_clients', 'operatori_alternativi', 'needs_disambiguation',
                                   'operatore_non_disponibile', 'operatore_disponibilita_checked',
                                   'proponi_waitlist', 'waitlist_aggiunto', 'waitlist_priorita',
                                   'waitlist_posizione', 'waitlist_priorita_potenziale']}
        if safe_context:
            context_note += f"\n[CONTESTO PRENOTAZIONE: {json.dumps(safe_context, ensure_ascii=False)}]"

        # LAYER 0 (Pre-RAG): Sentiment Analysis for early frustration detection
        sentiment_result = self.sentiment_analyzer.analyze(text)
        self.booking_context["_last_sentiment"] = sentiment_result.sentiment.value
        self.booking_context["_last_frustration"] = sentiment_result.frustration_level.value

        # Add sentiment context for LLM if high frustration detected
        if sentiment_result.frustration_level.value >= FrustrationLevel.HIGH.value:
            context_note += "\n[ATTENZIONE: Il cliente sembra frustrato. Rispondi con empatia e offri di passare a un operatore se preferisce.]"

        # Add to history
        self.conversation_history.append({
            "role": "user",
            "content": text + context_note
        })

        # =================================================================
        # 4-LAYER RAG PIPELINE (Enterprise)
        # Layer 0: Sentiment Analysis - <5ms (already computed above)
        # Layer 1: Exact Match (cortesia) - O(1), <1ms
        # Layer 2: Intent Classification (patterns) - <20ms
        # Layer 3: FAQ Retrieval (keywords) - <50ms
        # Layer 4: Groq LLM (fallback) - 500-1000ms
        # =================================================================

        response = None
        use_groq = False

        # LAYER 0: Use pre-computed sentiment analysis result
        print(f"   [L0 SENTIMENT] {sentiment_result.sentiment.value}, frustration={sentiment_result.frustration_level.value}, escalate={sentiment_result.should_escalate}")

        # Handle escalation if user is frustrated
        if sentiment_result.should_escalate:
            if sentiment_result.escalation_reason == "user_requested":
                # User explicitly asked for operator
                intent = "operatore"
                response = "Mi dispiace, la passo subito a un operatore. Un attimo di pazienza..."
                print(f"   [L0 ESCALATION] User requested operator")
            elif sentiment_result.frustration_level == FrustrationLevel.CRITICAL:
                # Critical frustration - immediate escalation
                intent = "operatore"
                response = "Mi dispiace per il disagio. La metto subito in contatto con un operatore che potrà aiutarla meglio."
                print(f"   [L0 ESCALATION] Critical frustration detected")

        # LAYER 1: Exact Match (cortesia phrases)
        intent_result = classify_intent(text)

        if response is None and intent_result.response and intent_result.category in [
            IntentCategory.CORTESIA,
            IntentCategory.CONFERMA,
            IntentCategory.RIFIUTO,
            IntentCategory.OPERATORE,
        ]:
            # Direct response for cortesia/confirmation phrases
            response = intent_result.response
            print(f"   [L1 EXACT] {intent_result.category.value}: {response[:50]}...")

            # Update intent from classifier
            if intent_result.category == IntentCategory.CONFERMA:
                intent = "conferma"
            elif intent_result.category == IntentCategory.RIFIUTO:
                intent = "rifiuto"
            elif intent_result.category == IntentCategory.OPERATORE:
                intent = "operatore"

        # LAYER 2 + 3: Pattern-based intent + FAQ lookup
        if response is None:
            # Update intent from classifier for booking/info flow
            if intent_result.category == IntentCategory.PRENOTAZIONE:
                intent = "prenotazione"
                print(f"   [L2 PATTERN] Intent: prenotazione (confidence: {intent_result.confidence:.2f})")
            elif intent_result.category == IntentCategory.CANCELLAZIONE:
                intent = "cancellazione"
                print(f"   [L2 PATTERN] Intent: cancellazione (confidence: {intent_result.confidence:.2f})")
            elif intent_result.category == IntentCategory.INFO:
                intent = "informazioni"
                print(f"   [L2 PATTERN] Intent: informazioni (confidence: {intent_result.confidence:.2f})")

            # LAYER 3: FAQ Retrieval (hybrid keyword + semantic)
            faq_answer = None
            if self.faq_manager:
                # Use hybrid FAQManager (keyword + semantic)
                faq_result = self.faq_manager.find_answer(text)
                if faq_result:
                    faq_answer = faq_result.answer
                    print(f"   [L3 FAQ] {faq_result.source} match ({faq_result.confidence:.2f}): {faq_answer[:60]}...")
            else:
                # Fallback to legacy keyword matching
                faq_answer = find_faq_answer(text, self.faq_dict)
                if faq_answer:
                    print(f"   [L3 FAQ] Legacy match: {faq_answer[:60]}...")

            if faq_answer:
                response = faq_answer
            else:
                print(f"   [L3 FAQ] No match for: {text[:50]}...")

        # LAYER 4: Groq LLM (fallback for complex queries)
        if response is None:
            use_groq = True
            print(f"   [L4 GROQ] Fallback needed (intent: {intent})")

            # Use RecoveryManager for Groq API call with circuit breaker
            groq_breaker = self.recovery_manager.get_circuit_breaker("groq")

            if groq_breaker.can_execute():
                try:
                    response = await self.groq.generate_response(
                        messages=self.conversation_history,
                        system_prompt=self.system_prompt
                    )
                    groq_breaker.record_success()
                    print(f"   [L4 GROQ] Response: {response[:50]}...")
                except Exception as e:
                    groq_breaker.record_failure()
                    print(f"   [L4 GROQ] Failed: {e}, using error recovery fallback")
                    # Use intelligent fallback from error_recovery module
                    response = get_fallback_response(intent=intent, error_category=ErrorCategory.SERVICE)
            else:
                # Circuit breaker open - use fallback immediately
                print(f"   [L4 GROQ] Circuit breaker OPEN, using fallback")
                response = get_fallback_response(intent=intent, error_category=ErrorCategory.SERVICE)

        if self.on_response:
            self.on_response(response)

        # Add response to history (without context notes)
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })

        # Generate audio
        audio_response = await self.tts.synthesize(response)

        # Check for booking action
        booking_action = await self._check_booking_action(text, intent)

        if booking_action and self.on_booking:
            self.on_booking(booking_action)

        return {
            "transcription": text,
            "response": response,
            "intent": intent,
            "audio_response": audio_response,
            "booking_action": booking_action,
            "identified_client": self.identified_client
        }

    async def _check_booking_action(self, text: str, intent: str) -> Optional[Dict]:
        """Check if a booking action should be triggered."""
        # Check if we have enough info to create booking
        ctx = self.booking_context

        if intent == "conferma" and ctx.get("cliente_id") and ctx.get("servizio") and ctx.get("data"):
            # Try to create the booking with optional operator preference
            ora = ctx.get("ora", "10:00")
            operatore_id = ctx.get("operatore_id")

            result = await self.crea_appuntamento(
                ctx["cliente_id"],
                ctx["servizio"],
                ctx["data"],
                ora,
                operatore_id=operatore_id
            )
            return {
                "action": "booking_created",
                "result": result,
                "context": ctx,
                "operatore": ctx.get("operatore_nome")
            }

        if intent == "prenotazione":
            return {
                "action": "booking_in_progress",
                "context": ctx,
                "missing": self._get_missing_booking_fields()
            }
        elif intent == "cancellazione":
            return {
                "action": "cancel_booking",
                "context": ctx
            }
        elif intent == "spostamento":
            return {
                "action": "modify_booking",
                "context": ctx
            }
        return None

    def _get_missing_booking_fields(self) -> List[str]:
        """Get list of missing fields for booking."""
        required = ["cliente_nome", "servizio", "data"]
        return [f for f in required if f not in self.booking_context]

    def reset_conversation(self):
        """Reset conversation history."""
        self.conversation_history = []
        self.current_intent = None
        self.booking_context = {}
        self.identified_client = None

    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get conversation summary."""
        return {
            "messages": len(self.conversation_history),
            "current_intent": self.current_intent,
            "booking_context": self.booking_context,
            "identified_client": self.identified_client,
            "history": self.conversation_history
        }

    async def say(self, text: str) -> bytes:
        """Just synthesize speech without processing."""
        return await self.tts.synthesize(text)

    async def greet(self) -> Dict[str, Any]:
        """Generate initial greeting."""
        greeting = f"Buongiorno, sono Paola, l'assistente vocale di {self.config.get('business_name', 'FLUXION')}. Come posso aiutarla?"

        audio = await self.tts.synthesize(greeting)

        self.conversation_history.append({
            "role": "assistant",
            "content": greeting
        })

        return {
            "response": greeting,
            "audio_response": audio
        }


class VoiceAgentServer:
    """HTTP server to expose voice pipeline to Tauri."""

    def __init__(self, pipeline: VoicePipeline, port: int = 3002):
        self.pipeline = pipeline
        self.port = port
        self.running = False

    async def handle_request(self, request: Dict) -> Dict:
        """Handle incoming request."""
        action = request.get("action")

        if action == "process_audio":
            audio_data = bytes.fromhex(request.get("audio_hex", ""))
            result = await self.pipeline.process_audio(audio_data)
            result["audio_response"] = result["audio_response"].hex()
            return result

        elif action == "process_text":
            text = request.get("text", "")
            result = await self.pipeline.process_text(text)
            result["audio_response"] = result["audio_response"].hex()
            return result

        elif action == "greet":
            result = await self.pipeline.greet()
            result["audio_response"] = result["audio_response"].hex()
            return result

        elif action == "say":
            text = request.get("text", "")
            audio = await self.pipeline.say(text)
            return {"audio_response": audio.hex()}

        elif action == "reset":
            self.pipeline.reset_conversation()
            return {"status": "ok"}

        elif action == "status":
            return {
                "status": "running",
                "conversation": self.pipeline.get_conversation_summary()
            }

        else:
            return {"error": f"Unknown action: {action}"}


# Test
async def test_pipeline():
    """Test voice pipeline."""
    from dotenv import load_dotenv
    load_dotenv()

    config = {
        "business_name": "Salone Bella Vita",
        "opening_hours": "09:00",
        "closing_hours": "19:00",
        "working_days": "Martedi-Sabato",
        "services": ["Taglio", "Piega", "Colore", "Trattamenti"]
    }

    pipeline = VoicePipeline(config)

    # Test greeting
    print("Testing greeting...")
    greeting = await pipeline.greet()
    print(f"Greeting: {greeting['response']}")

    # Test FAQ-based response
    print("\nTesting FAQ response...")
    result = await pipeline.process_text("Quanto costa un taglio?")
    print(f"User: Quanto costa un taglio?")
    print(f"Paola: {result['response']}")

    # Test booking
    print("\nTesting booking...")
    result = await pipeline.process_text("Vorrei prenotare un taglio per domani")
    print(f"User: Vorrei prenotare un taglio per domani")
    print(f"Paola: {result['response']}")
    print(f"Intent: {result['intent']}")
    print(f"Booking context: {pipeline.booking_context}")

    return True


if __name__ == "__main__":
    asyncio.run(test_pipeline())
