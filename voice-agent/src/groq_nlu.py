"""
FLUXION Voice Agent - Groq NLU Fallback

Lightweight module that calls Groq LLM for entity extraction
when regex fails. Integrated directly into BookingStateMachine.

Architecture:
    Layer 1 (regex, <1ms) handles 90% of cases
    Layer 2 (Groq, 300-800ms) handles ambiguous/conversational input

Usage:
    nlu = GroqNLU(api_key="...")
    result = nlu.extract_surname("Vi ho appena detto, il cognome è Arquati", nome="Filippo")
    # → {"cognome": "Arquati", "tipo_azione": "cognome_fornito", "confidence": 0.98}
"""

import os
import json
import logging
import time
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Groq model - same as groq_client.py
LLM_MODEL = "llama-3.3-70b-versatile"

# System prompt shared across all states
SYSTEM_PROMPT = """Sei un parser NLU per un voice agent italiano di prenotazioni.
Estrai informazioni strutturate dall'input dell'utente.
Ignora interiezioni (ehi, senti, eh), balbettii, punteggiatura errata dall'STT.
Rispondi SOLO in JSON valido, niente altro."""


class GroqNLU:
    """Groq-based NLU fallback for BookingStateMachine."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        self._client = None
        self._call_count = 0
        self._total_latency_ms = 0.0

    @property
    def client(self):
        """Lazy-init Groq client (only when first needed)."""
        if self._client is None:
            if not self.api_key:
                logger.warning("[GroqNLU] No API key, fallback disabled")
                return None
            try:
                from groq import Groq
                self._client = Groq(api_key=self.api_key)
                logger.info("[GroqNLU] Client initialized")
            except ImportError:
                logger.error("[GroqNLU] groq package not installed")
                return None
        return self._client

    def _call_groq(self, user_prompt: str) -> Optional[Dict[str, Any]]:
        """Call Groq with JSON response format. Returns parsed dict or None."""
        if not self.client:
            return None

        start = time.time()
        try:
            response = self.client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.0,
                max_tokens=300,
                response_format={"type": "json_object"},
            )
            result_text = response.choices[0].message.content
            result = json.loads(result_text)

            latency = (time.time() - start) * 1000
            self._call_count += 1
            self._total_latency_ms += latency
            logger.info(f"[GroqNLU] {latency:.0f}ms | {result}")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"[GroqNLU] JSON parse error: {e}")
            return None
        except Exception as e:
            logger.error(f"[GroqNLU] Call failed: {e}")
            return None

    # =================================================================
    # STATE-SPECIFIC EXTRACTORS
    # =================================================================

    def extract_surname(
        self, utterance: str, nome: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        Extract surname from conversational Italian text.

        Called when regex fails in REGISTERING_SURNAME state.

        Returns:
            {"cognome": str, "tipo_azione": str, "confidence": float}
            tipo_azione: "cognome_fornito" | "correzione_nome" | "frustrazione" | "fuori_tema"
        """
        prompt = f"""Stato: sto chiedendo il COGNOME al cliente.
Nome già raccolto: "{nome}"
Input STT: "{utterance}"

Estrai in JSON:
- "cognome": string o null (solo il cognome, non il nome)
- "tipo_azione": "cognome_fornito" | "correzione_nome" | "frustrazione" | "fuori_tema"
- "confidence": float 0.0-1.0

Regole:
- "Arquati" → {{"cognome": "Arquati", "tipo_azione": "cognome_fornito", "confidence": 0.98}}
- "Vi ho già detto, il cognome è Rossi" → {{"cognome": "Rossi", "tipo_azione": "cognome_fornito", "confidence": 0.95}}
- "Ehi!" → {{"cognome": null, "tipo_azione": "frustrazione", "confidence": 0.98}}
- "No, Neri non Rossi" → {{"cognome": "Neri", "tipo_azione": "correzione_nome", "confidence": 0.96}}
- "Senti, il mio numero è 339..." → {{"cognome": null, "tipo_azione": "fuori_tema", "confidence": 0.90}}
- Parole come "Ehi", "Vedi", "Fatto", "Senti", "Aspetta" NON sono cognomi → null"""

        return self._call_groq(prompt)

    def extract_phone_correction(
        self, utterance: str, nome: str = "", cognome: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        Detect name/surname corrections while in REGISTERING_PHONE state.

        Called when regex finds no phone number AND text contains
        correction signals.

        Returns:
            {"tipo_azione": str, "campo": str, "valore": str, "confidence": float}
            tipo_azione: "correzione_cognome" | "correzione_nome" | "telefono_fornito" | "frustrazione"
        """
        prompt = f"""Stato: sto chiedendo il TELEFONO al cliente.
Dati raccolti: nome="{nome}", cognome="{cognome}"
Input STT: "{utterance}"

Estrai in JSON:
- "tipo_azione": "correzione_cognome" | "correzione_nome" | "frustrazione" | "fuori_tema"
- "campo": "cognome" | "nome" | null (quale campo viene corretto)
- "valore": string o null (il nuovo valore corretto)
- "confidence": float 0.0-1.0

Regole:
- "No, ho detto che di cognome è Neri" → {{"tipo_azione": "correzione_cognome", "campo": "cognome", "valore": "Neri", "confidence": 0.96}}
- "Mi chiamo Filippo Neri, non Rossi" → {{"tipo_azione": "correzione_cognome", "campo": "cognome", "valore": "Neri", "confidence": 0.95}}
- "Argh, il cognome è sbagliato!" → {{"tipo_azione": "frustrazione", "campo": "cognome", "valore": null, "confidence": 0.85}}
- "Ma non capite niente" → {{"tipo_azione": "frustrazione", "campo": null, "valore": null, "confidence": 0.90}}"""

        return self._call_groq(prompt)

    def extract_confirming(
        self,
        utterance: str,
        servizio: str = "",
        data: str = "",
        ora: str = "",
    ) -> Optional[Dict[str, Any]]:
        """
        Parse confirmation/correction/cancellation in CONFIRMING state.

        Called when _extract_level1_entities finds no entities AND text
        is not a simple yes/no.

        Returns:
            {"decisione": str, "campo_corretto": str, "nuovo_valore": str, "confidence": float}
            decisione: "confermato" | "correzione" | "cancellazione" | "fuori_tema"
        """
        prompt = f"""Stato: chiedo CONFERMA della prenotazione.
Prenotazione: servizio="{servizio}", data="{data}", ora="{ora}"
Input STT: "{utterance}"

Estrai in JSON:
- "decisione": "confermato" | "correzione" | "cancellazione" | "fuori_tema"
- "campo_corretto": "servizio" | "data" | "ora" | "operatore" | null
- "nuovo_valore": string o null
- "confidence": float 0.0-1.0

Regole:
- "Perfetto!" → {{"decisione": "confermato", "confidence": 0.99}}
- "Preferisco dopo le 17" → {{"decisione": "correzione", "campo_corretto": "ora", "nuovo_valore": "17:00", "confidence": 0.95}}
- "Meglio venerdì" → {{"decisione": "correzione", "campo_corretto": "data", "nuovo_valore": "venerdì", "confidence": 0.95}}
- "Annulla tutto" → {{"decisione": "cancellazione", "confidence": 0.98}}
- "Sì ma aggiungi anche la barba" → {{"decisione": "correzione", "campo_corretto": "servizio", "nuovo_valore": "aggiungi barba", "confidence": 0.92}}
- "Va bene ma preferisco un'operatrice" → {{"decisione": "correzione", "campo_corretto": "operatore", "nuovo_valore": "operatrice", "confidence": 0.90}}"""

        return self._call_groq(prompt)

    def extract_time_preference(
        self, utterance: str
    ) -> Optional[Dict[str, Any]]:
        """
        Extract time preference from conversational text.

        Called when extract_time regex fails but text likely contains
        a time reference (e.g. "dopo le 17", "prima di pranzo").

        Returns:
            {"ora": str, "tipo": "esatto" | "vincolo", "confidence": float}
        """
        prompt = f"""Estrai l'orario dall'input italiano.
Input STT: "{utterance}"

Estrai in JSON:
- "ora": string in formato HH:MM o null
- "tipo": "esatto" | "vincolo" | "nessuno"
- "confidence": float 0.0-1.0

Regole:
- "alle 15:30" → {{"ora": "15:30", "tipo": "esatto", "confidence": 0.99}}
- "dopo le 17" → {{"ora": "17:00", "tipo": "vincolo", "confidence": 0.95}}
- "prima delle 10" → {{"ora": "10:00", "tipo": "vincolo", "confidence": 0.95}}
- "nel pomeriggio dopo le 17" → {{"ora": "17:00", "tipo": "vincolo", "confidence": 0.93}}
- "quando volete voi" → {{"ora": null, "tipo": "nessuno", "confidence": 0.90}}
- "tre e mezza" → {{"ora": "15:30", "tipo": "esatto", "confidence": 0.85}}"""

        return self._call_groq(prompt)

    @property
    def stats(self) -> Dict[str, Any]:
        """Return call statistics."""
        avg = self._total_latency_ms / self._call_count if self._call_count else 0
        return {
            "calls": self._call_count,
            "avg_latency_ms": round(avg, 1),
            "total_latency_ms": round(self._total_latency_ms, 1),
        }
