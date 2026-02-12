"""
FLUXION Voice Agent - Groq Client
STT (Whisper) and LLM (Llama) integration

E7-S1: Updated to use hybrid STT engine (whisper.cpp + Groq fallback).
E7-S2: Added streaming LLM support (2026-02-11) - Best Practice Reddit r/LLMDevs
"""

import os
import time
import asyncio
from typing import Optional, List, Dict, Any, AsyncGenerator
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

    # =============================================================================
    # STREAMING LLM (Best Practice 2026)
    # =============================================================================

    async def generate_response_streaming(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 300,
        model: Optional[str] = None,
        min_chunk_size: int = 20
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate response with streaming - Yields TTS-ready chunks.
        
        Best Practice 2026 (Reddit r/LLMDevs):
        - Non aspettare LLM completion, stream tokens immediatamente
        - Buffering intelligente: yield su punteggiatura o buffer size
        - Parallel TTS: inizia sintesi vocale mentre LLM ancora genera
        
        Args:
            messages: Conversation history
            system_prompt: System instructions
            temperature: Creativity (0.0-1.0)
            max_tokens: Max response length
            model: Model name (default: llama-3.3-70b-versatile)
            min_chunk_size: Min characters before yielding
            
        Yields:
            Dict con: {"text": str, "is_final": bool, "latency_ms": float}
        """
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        model = model or LLM_MODEL
        start_time = time.perf_counter()
        buffer = ""
        first_token_time = None
        sentence_delimiters = ['.', '!', '?', ';', ':', '\n']

        try:
            stream = await self.async_client.chat.completions.create(
                model=model,
                messages=full_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )

            async for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                
                if first_token_time is None and delta:
                    first_token_time = time.perf_counter() - start_time
                
                buffer += delta
                
                # Yield su condizioni
                should_yield = False
                if len(buffer) >= min_chunk_size * 3:  # Max chunk
                    should_yield = True
                elif len(buffer) >= min_chunk_size:
                    # Check delimitatori
                    if any(d in buffer for d in sentence_delimiters):
                        should_yield = True
                    # Check parole di transizione italiane
                    transition_words = [' e ', ' ma ', ' però ', ' quindi ', ' allora ', ' per ']
                    if any(w in buffer.lower() for w in transition_words):
                        should_yield = True
                
                if should_yield:
                    # Trova punto ottimale per spezzare
                    split_point = len(buffer)
                    for delim in ['. ', '! ', '? ', '; ', ': ', '\n', ' e ', ' ma ']:
                        idx = buffer.rfind(delim, min_chunk_size // 2, len(buffer))
                        if idx > 0:
                            split_point = idx + len(delim)
                            break
                    
                    to_yield = buffer[:split_point].strip()
                    buffer = buffer[split_point:].strip()
                    
                    if to_yield:
                        yield {
                            "text": to_yield,
                            "is_final": False,
                            "latency_ms": (time.perf_counter() - start_time) * 1000,
                            "first_token_ms": first_token_time * 1000 if first_token_time else 0
                        }
            
            # Yield finale
            if buffer.strip():
                yield {
                    "text": buffer.strip(),
                    "is_final": True,
                    "latency_ms": (time.perf_counter() - start_time) * 1000,
                    "first_token_ms": first_token_time * 1000 if first_token_time else 0
                }

        except Exception as e:
            # Fallback a non-streaming
            print(f"[GroqClient] Streaming failed, fallback to sync: {e}")
            try:
                response = await self.generate_response(
                    messages=messages,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                yield {
                    "text": response,
                    "is_final": True,
                    "latency_ms": (time.perf_counter() - start_time) * 1000,
                    "first_token_ms": 0
                }
            except Exception as e2:
                raise RuntimeError(f"LLM streaming failed: {e2}")

    async def generate_with_model_selection(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        complexity: str = "auto"
    ) -> str:
        """
        Generate with automatic model selection.
        
        Args:
            complexity: "simple" -> mixtral-8x7b (fast), 
                       "complex" -> llama-3.3-70b (accurate),
                       "auto" -> decide based on context
        """
        if complexity == "simple":
            model = "mixtral-8x7b-32768"
        elif complexity == "complex":
            model = LLM_MODEL
        else:  # auto
            # Euristiche per determinare complessità
            last_message = messages[-1]["content"].lower() if messages else ""
            simple_patterns = ['sì', 'no', 'va bene', 'confermo', 'cancella', 'grazie']
            if any(p in last_message for p in simple_patterns):
                model = "mixtral-8x7b-32768"
            else:
                model = LLM_MODEL
        
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=model,
                messages=full_messages,
                temperature=0.7,
                max_tokens=300
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise RuntimeError(f"LLM failed: {e}")


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
