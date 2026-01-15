"""
FLUXION Voice Agent - Groq Client
STT (Whisper) and LLM (Llama) integration
"""

import os
import asyncio
from typing import Optional, List, Dict, Any
from groq import Groq, AsyncGroq

# Models
STT_MODEL = "whisper-large-v3"
LLM_MODEL = "llama-3.3-70b-versatile"


class GroqClient:
    """Client for Groq API (STT + LLM)."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not set")

        self.client = Groq(api_key=self.api_key)
        self.async_client = AsyncGroq(api_key=self.api_key)

    async def transcribe_audio(
        self,
        audio_data: bytes,
        language: str = "it",
        filename: str = "audio.wav"
    ) -> str:
        """
        Speech-to-Text using Groq Whisper.

        Args:
            audio_data: Raw audio bytes (WAV format)
            language: Language code (default: Italian)
            filename: Filename hint for the API

        Returns:
            Transcribed text
        """
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
