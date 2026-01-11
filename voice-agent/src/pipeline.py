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

    # Direct phrase matching
    for question, answer in qa_dict.items():
        if len(question) > 5 and question in text_lower:
            return answer

    # Keyword matching with scoring
    best_match = None
    best_score = 0

    keywords_map = {
        "prezzo": ["quanto costa", "prezzo", "prezzi", "costo"],
        "orario": ["orario", "orari", "aprite", "chiudete", "aperti", "quando"],
        "taglio": ["taglio", "tagliare", "tagliata"],
        "colore": ["colore", "tinta", "colorare"],
        "barba": ["barba"],
        "pagamento": ["pagare", "carta", "contanti", "satispay"],
        "parcheggio": ["parcheggio", "parcheggiare"],
        "prenot": ["prenotare", "prenoto", "prenotazione", "disdire"],
    }

    for category, keywords in keywords_map.items():
        for kw in keywords:
            if kw in text_lower:
                # Find relevant FAQ
                for q, a in qa_dict.items():
                    if category in q or any(k in q for k in keywords):
                        score = sum(1 for k in keywords if k in text_lower)
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

        # Try to load static FAQ synchronously for now
        faq_paths = [
            Path(__file__).parent.parent.parent / "data" / "faq_salone.md",
            Path("data/faq_salone.md"),
        ]
        for path in faq_paths:
            if path.exists():
                self.faq_knowledge, self.faq_dict = load_faq_file(path)
                print(f"   Loaded static FAQ from: {path} ({len(self.faq_dict)} entries)")
                break

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

        # Callbacks
        self.on_transcription: Optional[Callable[[str], None]] = None
        self.on_response: Optional[Callable[[str], None]] = None
        self.on_intent: Optional[Callable[[str], None]] = None
        self.on_booking: Optional[Callable[[Dict], None]] = None

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

    async def search_client(self, name: str) -> Optional[Dict]:
        """Search for client by name in database."""
        # Try HTTP bridge
        result = await self._call_http_bridge(f"/api/clienti/search?q={name}")
        if result and isinstance(result, list) and len(result) > 0:
            return result[0]
        return None

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

    async def crea_appuntamento(self, cliente_id: str, servizio: str, data: str, ora: str) -> Dict:
        """Create appointment via HTTP bridge."""
        result = await self._call_http_bridge(
            "/api/appuntamenti/create",
            method="POST",
            data={
                "cliente_id": cliente_id,
                "servizio": servizio,
                "data": data,
                "ora": ora
            }
        )
        return result or {"success": False, "error": "Bridge non disponibile"}

    def _extract_booking_info(self, text: str) -> Dict[str, Any]:
        """Extract booking information from user text."""
        text_lower = text.lower()
        info = {}

        # Extract service
        services = {
            "taglio": ["taglio", "tagliare", "accorciare"],
            "piega": ["piega", "messa in piega", "asciugatura"],
            "colore": ["colore", "tinta", "colorare"],
            "barba": ["barba"],
            "trattamento": ["trattamento", "cheratina"]
        }
        for service, keywords in services.items():
            if any(kw in text_lower for kw in keywords):
                info["servizio"] = service
                break

        # Extract day references
        today = datetime.now()
        if "oggi" in text_lower:
            info["data"] = today.strftime("%Y-%m-%d")
        elif "domani" in text_lower:
            info["data"] = (today + timedelta(days=1)).strftime("%Y-%m-%d")
        elif "dopodomani" in text_lower:
            info["data"] = (today + timedelta(days=2)).strftime("%Y-%m-%d")

        # Extract time
        import re
        time_match = re.search(r'(\d{1,2})[:\.]?(\d{2})?', text_lower)
        if time_match:
            hour = int(time_match.group(1))
            minute = time_match.group(2) or "00"
            if 8 <= hour <= 19:
                info["ora"] = f"{hour:02d}:{minute}"

        # Common time expressions
        if "pomeriggio" in text_lower:
            info["preferenza_orario"] = "pomeriggio"
        elif "mattina" in text_lower:
            info["preferenza_orario"] = "mattina"

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

        # Try to identify client if name mentioned
        words = text.split()
        for i, word in enumerate(words):
            # Look for "sono X" or "mi chiamo X" patterns
            if word.lower() in ["sono", "chiamo"] and i + 1 < len(words):
                potential_name = words[i + 1].capitalize()
                if len(potential_name) > 2:
                    client = await self.search_client(potential_name)
                    if client:
                        self.identified_client = client
                        self.booking_context["cliente_id"] = client.get("id")
                        self.booking_context["cliente_nome"] = client.get("nome")
                        print(f"   Cliente identificato: {client.get('nome')} {client.get('cognome')}")

        # Build context-aware message
        context_note = ""
        if self.identified_client:
            context_note = f"\n[NOTA SISTEMA: Cliente identificato come {self.identified_client.get('nome')} {self.identified_client.get('cognome', '')}]"
        if self.booking_context:
            context_note += f"\n[CONTESTO PRENOTAZIONE: {json.dumps(self.booking_context, ensure_ascii=False)}]"

        # Add to history
        self.conversation_history.append({
            "role": "user",
            "content": text + context_note
        })

        # STEP 1: Try local RAG first (no API call)
        response = None
        use_groq = False

        if intent == "informazioni":
            # FAQ lookup for info queries
            faq_answer = find_faq_answer(text, self.faq_dict)
            if faq_answer:
                response = faq_answer
                print(f"   RAG match: {response[:50]}...")

        # STEP 2: Use Groq for complex queries or booking flow
        if response is None:
            use_groq = True
            try:
                response = await self.groq.generate_response(
                    messages=self.conversation_history,
                    system_prompt=self.system_prompt
                )
                print(f"   Groq response: {response[:50]}...")
            except Exception as e:
                # Fallback to simple response if Groq fails
                print(f"   Groq failed: {e}, using fallback")
                if intent == "prenotazione":
                    response = "Perfetto! Per prenotare mi serve sapere: nome, servizio desiderato e giorno/ora preferiti."
                elif intent == "informazioni":
                    response = "Mi scusi, non ho trovato questa informazione. Può riformulare la domanda?"
                else:
                    response = "Sono qui per aiutarla con prenotazioni e informazioni. Come posso assisterla?"

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
            # Try to create the booking
            ora = ctx.get("ora", "10:00")
            result = await self.crea_appuntamento(
                ctx["cliente_id"],
                ctx["servizio"],
                ctx["data"],
                ora
            )
            return {
                "action": "booking_created",
                "result": result,
                "context": ctx
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
