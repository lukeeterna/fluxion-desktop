"""
FLUXION Voice Agent - Main Pipeline
Orchestrates STT -> LLM -> TTS flow
"""

import os
import json
import asyncio
import tempfile
from datetime import datetime
from typing import Optional, Dict, Any, List, Callable
from pathlib import Path

from .groq_client import GroqClient
from .tts import get_tts, PiperTTS, SystemTTS

# System prompt template
SYSTEM_PROMPT = """
Sei Sara, l'assistente vocale di {business_name}.

PERSONALITA':
- Cordiale, professionale, empatica
- Parli italiano fluente con accento neutro
- Risposte BREVI (massimo 2 frasi per volta)
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

FLOW PRENOTAZIONE:
1. Saluta e chiedi come puoi aiutare
2. Se vuole prenotare:
   a. Chiedi nome (se non lo conosci)
   b. Chiedi quale servizio desidera
   c. Chiedi giorno preferito
   d. Proponi orario disponibile
   e. Conferma tutti i dettagli
   f. Saluta cordialmente

REGOLE:
- Se non capisci, chiedi GENTILMENTE di ripetere
- Se la richiesta e' fuori scope, suggerisci di chiamare il numero diretto
- Conferma sempre i dati prima di prenotare
- Rispondi SEMPRE in italiano
"""


class VoicePipeline:
    """
    FLUXION Voice Agent Pipeline.

    Handles the full conversation flow:
    Audio In -> STT -> LLM -> TTS -> Audio Out
    """

    def __init__(
        self,
        business_config: Dict[str, Any],
        groq_api_key: Optional[str] = None,
        use_piper: bool = True
    ):
        """
        Initialize voice pipeline.

        Args:
            business_config: Business settings (name, hours, services)
            groq_api_key: Groq API key (or from env)
            use_piper: Use Piper TTS (recommended)
        """
        self.config = business_config
        self.groq = GroqClient(api_key=groq_api_key)
        self.tts = get_tts(use_piper=use_piper)

        self.conversation_history: List[Dict[str, str]] = []
        self.current_intent: Optional[str] = None
        self.booking_context: Dict[str, Any] = {}

        self.system_prompt = self._build_system_prompt()

        # Callbacks
        self.on_transcription: Optional[Callable[[str], None]] = None
        self.on_response: Optional[Callable[[str], None]] = None
        self.on_intent: Optional[Callable[[str], None]] = None
        self.on_booking: Optional[Callable[[Dict], None]] = None

    def _build_system_prompt(self) -> str:
        """Build system prompt from config."""
        return SYSTEM_PROMPT.format(
            business_name=self.config.get("business_name", "FLUXION"),
            opening_hours=self.config.get("opening_hours", "09:00"),
            closing_hours=self.config.get("closing_hours", "19:00"),
            working_days=self.config.get("working_days", "Lunedi-Sabato"),
            services=", ".join(self.config.get("services", ["Taglio", "Piega", "Colore"]))
        )

    async def process_audio(self, audio_data: bytes) -> Dict[str, Any]:
        """
        Process audio input through full pipeline.

        Args:
            audio_data: WAV audio bytes

        Returns:
            {
                "transcription": str,
                "response": str,
                "intent": str,
                "audio_response": bytes,
                "booking_action": Optional[Dict]
            }
        """
        # Step 1: Speech-to-Text
        transcription = await self.groq.transcribe_audio(audio_data)

        if self.on_transcription:
            self.on_transcription(transcription)

        # Step 2: Detect intent
        intent = self.groq._detect_intent(transcription)
        self.current_intent = intent

        if self.on_intent:
            self.on_intent(intent)

        # Step 3: Add to history
        self.conversation_history.append({
            "role": "user",
            "content": transcription
        })

        # Step 4: Generate response
        response = await self.groq.generate_response(
            messages=self.conversation_history,
            system_prompt=self.system_prompt
        )

        if self.on_response:
            self.on_response(response)

        # Step 5: Add response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })

        # Step 6: Text-to-Speech
        audio_response = await self.tts.synthesize(response)

        # Step 7: Check for booking action
        booking_action = self._check_booking_action(transcription, intent)

        if booking_action and self.on_booking:
            self.on_booking(booking_action)

        return {
            "transcription": transcription,
            "response": response,
            "intent": intent,
            "audio_response": audio_response,
            "booking_action": booking_action
        }

    async def process_text(self, text: str) -> Dict[str, Any]:
        """
        Process text input (for testing without audio).

        Args:
            text: User text input

        Returns:
            Same as process_audio but without audio_response
        """
        # Detect intent
        intent = self.groq._detect_intent(text)
        self.current_intent = intent

        # Add to history
        self.conversation_history.append({
            "role": "user",
            "content": text
        })

        # Generate response
        response = await self.groq.generate_response(
            messages=self.conversation_history,
            system_prompt=self.system_prompt
        )

        # Add response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })

        # Generate audio
        audio_response = await self.tts.synthesize(response)

        return {
            "transcription": text,
            "response": response,
            "intent": intent,
            "audio_response": audio_response,
            "booking_action": self._check_booking_action(text, intent)
        }

    def _check_booking_action(self, text: str, intent: str) -> Optional[Dict]:
        """Check if a booking action should be triggered."""
        if intent == "prenotazione":
            return {
                "action": "create_booking",
                "context": self.booking_context
            }
        elif intent == "cancellazione":
            return {
                "action": "cancel_booking",
                "context": self.booking_context
            }
        elif intent == "spostamento":
            return {
                "action": "modify_booking",
                "context": self.booking_context
            }
        return None

    def reset_conversation(self):
        """Reset conversation history."""
        self.conversation_history = []
        self.current_intent = None
        self.booking_context = {}

    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get conversation summary."""
        return {
            "messages": len(self.conversation_history),
            "current_intent": self.current_intent,
            "booking_context": self.booking_context,
            "history": self.conversation_history
        }

    async def say(self, text: str) -> bytes:
        """
        Just synthesize speech without processing.

        Args:
            text: Text to speak

        Returns:
            WAV audio bytes
        """
        return await self.tts.synthesize(text)

    async def greet(self) -> Dict[str, Any]:
        """Generate initial greeting."""
        greeting = f"Buongiorno, sono Sara, l'assistente vocale di {self.config.get('business_name', 'FLUXION')}. Come posso aiutarla?"

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
    """
    HTTP server to expose voice pipeline to Tauri.
    """

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
        "working_days": "Lunedi-Sabato",
        "services": ["Taglio", "Piega", "Colore", "Trattamenti"]
    }

    pipeline = VoicePipeline(config)

    # Test greeting
    print("Testing greeting...")
    greeting = await pipeline.greet()
    print(f"Greeting: {greeting['response']}")
    print(f"Audio size: {len(greeting['audio_response'])} bytes")

    # Test text processing
    print("\nTesting text processing...")
    result = await pipeline.process_text("Vorrei prenotare un taglio per domani")
    print(f"User: Vorrei prenotare un taglio per domani")
    print(f"Sara: {result['response']}")
    print(f"Intent: {result['intent']}")

    return True


if __name__ == "__main__":
    asyncio.run(test_pipeline())
