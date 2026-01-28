"""
FLUXION Voice Agent - Groq Client
STT (Whisper) and LLM (Llama) integration

E7-S1: Updated to use hybrid STT engine (whisper.cpp + Groq fallback).
"""

import os
import asyncio
from typing import Optional, List, Dict, Any
from groq import Groq, AsyncGroq

# Import hybrid STT engine
try:
    try:
        from .stt import get_stt_engine, STTEngine
    except ImportError:
        from stt import get_stt_engine, STTEngine
    HAS_HYBRID_STT = True
except ImportError:
    HAS_HYBRID_STT = False

# Models
STT_MODEL = "whisper-large-v3"
LLM_MODEL = "llama-3.3-70b-versatile"


class GroqClient:
    """Client for Groq API (STT + LLM).

    E7-S1: Now uses hybrid STT engine (whisper.cpp primary + Groq fallback)
    for improved accuracy (WER 9-11% vs 21.7% with Groq alone).
    """

    def __init__(self, api_key: Optional[str] = None, prefer_offline_stt: bool = True):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not set")

        self.client = Groq(api_key=self.api_key)
        self.async_client = AsyncGroq(api_key=self.api_key)

        # E7-S1: Initialize hybrid STT engine
        self._stt_engine: Optional[STTEngine] = None
        self._prefer_offline_stt = prefer_offline_stt
        if HAS_HYBRID_STT and prefer_offline_stt:
            try:
                self._stt_engine = get_stt_engine(prefer_offline=True)
                print("[GroqClient] Using hybrid STT engine (whisper.cpp + Groq fallback)")
            except Exception as e:
                print(f"[GroqClient] Hybrid STT init failed, using Groq only: {e}")

    async def transcribe_audio(
        self,
        audio_data: bytes,
        language: str = "it",
        filename: str = "audio.wav"
    ) -> str:
        """
        Speech-to-Text using hybrid engine (whisper.cpp + Groq fallback).

        E7-S1: Now uses whisper.cpp locally for better accuracy (WER 9-11%)
        and falls back to Groq if whisper.cpp is unavailable.

        Args:
            audio_data: Raw audio bytes (WAV format)
            language: Language code (default: Italian)
            filename: Filename hint for the API

        Returns:
            Transcribed text
        """
        # E7-S1: Try hybrid STT engine first
        if self._stt_engine is not None:
            try:
                result = await self._stt_engine.transcribe(audio_data, language)
                if result.get("text"):
                    engine = result.get("engine", "unknown")
                    latency = result.get("latency_ms", 0)
                    print(f"[STT] Transcribed via {engine} in {latency:.0f}ms")
                    return result["text"]
            except Exception as e:
                print(f"[STT] Hybrid engine failed, falling back to Groq: {e}")

        # Fallback to direct Groq API call
        try:
            response = await asyncio.to_thread(
                self.client.audio.transcriptions.create,
                file=(filename, audio_data),
                model=STT_MODEL,
                language=language,
                response_format="text"
            )
            return response.strip()
        except Exception as e:
            raise RuntimeError(f"STT failed: {e}")

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 300
    ) -> str:
        """
        Generate response using Groq Llama.

        Args:
            messages: Conversation history [{"role": "user/assistant", "content": "..."}]
            system_prompt: System instructions
            temperature: Creativity (0.0-1.0)
            max_tokens: Max response length

        Returns:
            Generated response text
        """
        full_messages = []

        if system_prompt:
            full_messages.append({
                "role": "system",
                "content": system_prompt
            })

        full_messages.extend(messages)

        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=LLM_MODEL,
                messages=full_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise RuntimeError(f"LLM failed: {e}")

    async def transcribe_and_respond(
        self,
        audio_data: bytes,
        conversation_history: List[Dict[str, str]],
        system_prompt: str
    ) -> Dict[str, Any]:
        """
        Full pipeline: STT -> LLM -> Response.

        Args:
            audio_data: Input audio
            conversation_history: Previous messages
            system_prompt: System instructions

        Returns:
            {
                "transcription": "user text",
                "response": "assistant text",
                "intent": "detected intent"
            }
        """
        # Step 1: Transcribe
        transcription = await self.transcribe_audio(audio_data)

        # Step 2: Add to history
        messages = conversation_history + [
            {"role": "user", "content": transcription}
        ]

        # Step 3: Generate response
        response = await self.generate_response(
            messages=messages,
            system_prompt=system_prompt
        )

        # Step 4: Detect intent (simple keyword matching)
        intent = self._detect_intent(transcription)

        return {
            "transcription": transcription,
            "response": response,
            "intent": intent
        }

    def _detect_intent(self, text: str) -> str:
        """Simple intent detection from text."""
        text_lower = text.lower()

        intents = {
            "prenotazione": ["prenotare", "appuntamento", "fissare", "prendere", "disponibilità"],
            "cancellazione": ["cancellare", "disdire", "annullare", "eliminare"],
            "spostamento": ["spostare", "cambiare", "modificare", "anticipare", "posticipare"],
            "informazioni": ["quanto costa", "prezzo", "prezzi", "orari", "servizi"],
            "waitlist": ["lista d'attesa", "lista attesa", "avvisami", "avvisatemi", "chiamami quando", "fatemi sapere", "primo posto disponibile"],
            "conferma": ["sì", "va bene", "ok", "confermo", "perfetto", "certo", "assolutamente"],
            "negazione": ["no", "non voglio", "annulla", "lascia stare", "niente"]
        }

        for intent, keywords in intents.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return intent

        return "unknown"


# Test function
async def test_groq():
    """Test Groq connection."""
    client = GroqClient()

    # Test LLM
    response = await client.generate_response(
        messages=[{"role": "user", "content": "Ciao, come stai?"}],
        system_prompt="Sei Sara, assistente vocale di un salone di bellezza. Rispondi brevemente in italiano."
    )
    print(f"LLM Response: {response}")

    return True


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_groq())
