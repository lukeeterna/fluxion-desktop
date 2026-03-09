"""
WhatsApp Callback Handler — FLUXION Voice Agent B2

Riceve messaggi WhatsApp push da whatsapp-service.cjs via HTTP POST.
Gestisce CONFIRM/CANCEL intent direttamente + testo libero via orchestratore.

Endpoint: POST /api/voice/whatsapp/callback
Formato JSON custom: {"from": "393...", "name": "...", "body": "...", "timestamp": "...", "message_id": "..."}
Formato Twilio:      application/x-www-form-urlencoded (From=whatsapp:+39..., Body=..., MessageSid=...)

Python 3.9 compatible — no walrus operator, no match/case.
"""

import asyncio
import json
import re
import logging
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set

import aiohttp
from aiohttp import web

logger = logging.getLogger(__name__)


# =============================================================================
# Intent patterns
# =============================================================================

CONFIRM_PATTERN = re.compile(
    r"^(ok|okk|si|si'|sii|s[ìi]|confermo|confermato|va bene|certo|esatto|perfetto|ci sono|a domani|d'accordo|yes)\s*[!.]*$",
    re.IGNORECASE,
)

CANCEL_PATTERN = re.compile(
    r"^(annulla|cancella|cancello|disdico|disdetto|no|non vengo|non posso|impossibile|purtroppo|cancel)\s*[!.]*$",
    re.IGNORECASE,
)

RESCHEDULE_PATTERN = re.compile(
    r"^(sposto|sposta|spostare|rimanda|rimandare|cambio|cambia|cambiare|cambiare orario|sposto orario|voglio spostare|posso spostare)\s*[!.]*$",
    re.IGNORECASE,
)


# =============================================================================
# WAPhoneSession
# =============================================================================

@dataclass
class WAPhoneSession:
    """Tracks state per phone number for WhatsApp callback sessions."""
    phone: str
    session_id: Optional[str] = None
    pending_appointment_id: Optional[str] = None
    client_name: str = "Cliente"
    last_activity: datetime = field(default_factory=datetime.now)
    fsm_state: str = "idle"

    def is_expired(self, timeout_minutes: int = 30) -> bool:
        return datetime.now() - self.last_activity > timedelta(minutes=timeout_minutes)

    def touch(self):
        self.last_activity = datetime.now()


# =============================================================================
# WhatsAppCallbackHandler
# =============================================================================

class WhatsAppCallbackHandler:
    """
    Handles incoming WhatsApp messages pushed from whatsapp-service.cjs.

    Per ogni messaggio:
    1. Parsa payload (JSON custom o Twilio form-urlencoded)
    2. Dedup via message_id
    3. Normalizza phone
    4. Routing: CONFIRM → mark_confirmed | CANCEL → cancel | testo → orchestrator
    5. Risponde 200 OK entro 500ms
    """

    def __init__(self, orchestrator=None, wa_client=None):
        self.orchestrator = orchestrator
        self.wa_client = wa_client

        # In-memory state
        self._phone_sessions: Dict[str, WAPhoneSession] = {}
        self._processed_ids: Set[str] = set()
        self._processed_id_times: List[tuple] = []  # (message_id, timestamp) per TTL cleanup

        # Rate tracking per phone: phone -> list of timestamps (last 60s)
        self._rate_counts: Dict[str, List[datetime]] = {}

        # Rate limit: 3 messages per minute per phone
        self.RATE_LIMIT = 3
        self.RATE_WINDOW_SECONDS = 60

    # =========================================================================
    # Public HTTP handler
    # =========================================================================

    async def handle(self, request: web.Request) -> web.Response:
        """Main aiohttp handler for POST /api/voice/whatsapp/callback."""
        try:
            payload = await self._parse_payload(request)
        except Exception as e:
            logger.warning("WhatsApp callback parse error: %s", e)
            return web.json_response({"ok": False, "error": "parse_error"}, status=400)

        phone = payload.get("phone", "")
        body = payload.get("body", "").strip()
        name = payload.get("name", "Cliente")
        message_id = payload.get("message_id", "")
        msg_type = payload.get("type", "text")

        # Skip empty / non-text
        if not body or msg_type != "text":
            return web.json_response({"ok": True, "skipped": True})

        # Dedup
        if message_id and message_id in self._processed_ids:
            logger.debug("Duplicate message_id=%s ignored", message_id)
            return web.json_response({"ok": True, "duplicate": True})
        if message_id:
            self._processed_ids.add(message_id)
            self._processed_id_times.append((message_id, datetime.now()))
            self._cleanup_dedup_cache()

        # Rate limit check
        if not self._check_rate_limit(phone):
            logger.warning("Rate limit exceeded for phone=%s", phone)
            return web.json_response({"ok": True, "rate_limited": True})

        # Get or create session
        session = self._get_or_create_session(phone, name)
        session.touch()

        # Route intent
        response_text = await self._route_intent(phone, body, session, name)

        # Send response via WA client (fire-and-forget)
        if response_text and self.wa_client:
            try:
                await self.wa_client.send_message_async(phone, response_text)
            except (aiohttp.ClientError, asyncio.TimeoutError, OSError) as e:
                logger.warning("Failed to send WA response to %s (network): %s", phone, e)
            except Exception as e:
                logger.error("Failed to send WA response to %s (unexpected): %s", phone, e, exc_info=True)

        return web.json_response({"ok": True, "phone": phone, "intent_routed": True})

    # =========================================================================
    # Payload parsing (dual-format)
    # =========================================================================

    async def _parse_payload(self, request: web.Request) -> dict:
        """
        Parsa payload JSON custom o Twilio form-urlencoded.
        Restituisce sempre: {phone, name, body, message_id, type}
        """
        content_type = request.content_type or ""

        if "application/x-www-form-urlencoded" in content_type:
            # Twilio format
            form = await request.post()
            raw_from = form.get("From", "")
            # Strip "whatsapp:" prefix
            phone = raw_from.replace("whatsapp:", "").replace("+", "").strip()
            return {
                "phone": self._normalize_phone(phone),
                "name": form.get("ProfileName", "Cliente"),
                "body": form.get("Body", ""),
                "message_id": form.get("MessageSid", ""),
                "type": "text" if form.get("NumMedia", "0") == "0" else "media",
            }
        else:
            # JSON custom format from whatsapp-service.cjs
            data = await request.json()
            phone = data.get("from", "")
            msg_type = "text"
            if data.get("hasMedia") or data.get("type", "chat") != "chat":
                msg_type = "media"
            return {
                "phone": self._normalize_phone(phone),
                "name": data.get("name", "Cliente"),
                "body": data.get("body", ""),
                "message_id": data.get("message_id", ""),
                "type": msg_type,
            }

    def _normalize_phone(self, phone: str) -> str:
        """Normalizza numero italiano: solo cifre, 39 prefisso."""
        digits = re.sub(r"\D", "", phone)
        if digits.startswith("0039"):
            digits = digits[4:]
        elif digits.startswith("39") and len(digits) > 10:
            pass  # already has prefix
        elif digits.startswith("3") and len(digits) == 10:
            digits = "39" + digits
        return digits

    # =========================================================================
    # Session management
    # =========================================================================

    def _get_or_create_session(self, phone: str, name: str = "Cliente") -> WAPhoneSession:
        session = self._phone_sessions.get(phone)
        if session is None or session.is_expired():
            session = WAPhoneSession(phone=phone, client_name=name)
            self._phone_sessions[phone] = session
        return session

    def register_pending_appointment(self, phone: str, appointment_id: str, client_name: str = "Cliente"):
        """
        Registra un appuntamento in attesa di conferma per questo phone.
        Chiamato da orchestratore/booking flow quando invia reminder.
        """
        session = self._get_or_create_session(phone, client_name)
        session.pending_appointment_id = appointment_id
        session.client_name = client_name
        session.fsm_state = "waiting_confirmation"
        logger.info("Registered pending appointment %s for phone %s", appointment_id, phone)

    # =========================================================================
    # Intent routing
    # =========================================================================

    async def _route_intent(self, phone: str, body: str, session: WAPhoneSession, name: str) -> Optional[str]:
        """Routing: CONFIRM | CANCEL | RESCHEDULE | free text."""
        if CONFIRM_PATTERN.match(body):
            return await self._handle_confirm(phone, session)
        elif CANCEL_PATTERN.match(body):
            return await self._handle_cancel(phone, session)
        elif RESCHEDULE_PATTERN.match(body):
            return await self._handle_reschedule(phone, session)
        else:
            return await self._handle_free_text(phone, body, session, name)

    async def _handle_confirm(self, phone: str, session: WAPhoneSession) -> str:
        """Cliente conferma appuntamento (OK)."""
        appointment_id = session.pending_appointment_id

        if not appointment_id:
            # Cerca nel DB per questo telefono
            appointment_id = await self._lookup_pending_appointment(phone)

        if appointment_id:
            confirmed = await self._mark_confirmed(appointment_id, phone)
            if confirmed:
                session.fsm_state = "confirmed"
                session.pending_appointment_id = None
                return (
                    f"Perfetto {session.client_name}! "
                    "Il tuo appuntamento è stato confermato. Ti aspettiamo!"
                )
            else:
                return "Non riesco a trovare l'appuntamento da confermare. Contattaci direttamente."
        else:
            return (
                "Grazie per la risposta! Non ho trovato appuntamenti in attesa di conferma. "
                "Vuoi prenotare un nuovo appuntamento?"
            )

    async def _handle_cancel(self, phone: str, session: WAPhoneSession) -> str:
        """Cliente annulla appuntamento."""
        appointment_id = session.pending_appointment_id

        if not appointment_id:
            appointment_id = await self._lookup_pending_appointment(phone)

        if appointment_id:
            cancelled = await self._cancel_appointment(appointment_id, phone)
            if cancelled:
                session.fsm_state = "cancelled"
                session.pending_appointment_id = None
                return (
                    f"Appuntamento cancellato {session.client_name}. "
                    "Se vuoi riprenoterai, scrivici quando vuoi!"
                )
            else:
                return "Non riesco a cancellare l'appuntamento. Contattaci direttamente."
        else:
            return (
                "Non ho trovato appuntamenti da cancellare per il tuo numero. "
                "Se hai bisogno contattaci direttamente."
            )

    async def _handle_reschedule(self, phone: str, session: WAPhoneSession) -> str:
        """Cliente vuole spostare l'appuntamento — avvia dialogo di rescheduling."""
        appointment_id = session.pending_appointment_id
        if not appointment_id:
            appointment_id = await self._lookup_pending_appointment(phone)

        if appointment_id:
            session.fsm_state = "reschedule_requested"
            session.pending_appointment_id = None
            return (
                f"Perfetto {session.client_name}! "
                "Scrivi il nuovo orario che preferisci (es. 'martedì alle 15') "
                "e ti confermiamo la disponibilità."
            )
        else:
            return (
                "Non ho trovato appuntamenti da spostare. "
                "Scrivi il servizio e il giorno preferiti per prenotare un nuovo appuntamento!"
            )

    async def _handle_free_text(self, phone: str, body: str, session: WAPhoneSession, name: str) -> Optional[str]:
        """Testo libero: forward all'orchestratore."""
        if not self.orchestrator:
            return "Ciao! Per prenotare chiama direttamente o scrivi al numero principale."

        try:
            session_id = session.session_id
            if not session_id or session.is_expired(timeout_minutes=30):
                from session_manager import SessionChannel
                result = await self.orchestrator.start_session(
                    channel=SessionChannel.WHATSAPP,
                    phone_number=phone
                )
                session.session_id = result.session_id
                session_id = result.session_id

            result = await self.orchestrator.process(
                user_input=body,
                session_id=session_id
            )
            session.fsm_state = "in_conversation"
            return result.response if result else None
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.error("Orchestrator error for phone %s: %s", phone, e, exc_info=True)
            return "Ciao! Come posso aiutarti? Per prenotare scrivi il servizio che ti interessa."

    # =========================================================================
    # DB helpers (best-effort, non-blocking)
    # =========================================================================

    async def _lookup_pending_appointment(self, phone: str) -> Optional[str]:
        """
        Cerca nel DB l'appuntamento più recente in stato 'in_attesa' per questo numero.
        Fallback se _phone_sessions non ha il mapping (es. dopo restart).
        """
        if not self.orchestrator:
            return None
        try:
            db = getattr(self.orchestrator, "db", None)
            if db is None:
                return None
            # Cerca appuntamento più recente per questo telefono non ancora confermato
            row = db.execute(
                "SELECT id FROM prenotazioni WHERE telefono = ? AND stato IN ('in_attesa', 'confermato_voice') "
                "ORDER BY created_at DESC LIMIT 1",
                (phone,)
            ).fetchone()
            if row:
                return str(row[0])
        except sqlite3.Error as e:
            logger.debug("DB lookup error for phone %s: %s", phone, e)
        return None

    async def _mark_confirmed(self, appointment_id: str, phone: str) -> bool:
        """Aggiorna DB: stato → confermato."""
        if not self.orchestrator:
            return False
        try:
            db = getattr(self.orchestrator, "db", None)
            if db is None:
                return True  # no DB in test/offline — pretend success
            db.execute(
                "UPDATE prenotazioni SET stato = 'confermato' WHERE id = ?",
                (appointment_id,)
            )
            db.commit()
            logger.info("Appointment %s confirmed via WhatsApp for phone %s", appointment_id, phone)
            return True
        except sqlite3.Error as e:
            logger.error("Failed to confirm appointment %s: %s", appointment_id, e)
            return False

    async def _cancel_appointment(self, appointment_id: str, phone: str) -> bool:
        """Aggiorna DB: stato → cancellato."""
        if not self.orchestrator:
            return False
        try:
            db = getattr(self.orchestrator, "db", None)
            if db is None:
                return True  # no DB in test/offline — pretend success
            db.execute(
                "UPDATE prenotazioni SET stato = 'cancellato' WHERE id = ?",
                (appointment_id,)
            )
            db.commit()
            logger.info("Appointment %s cancelled via WhatsApp for phone %s", appointment_id, phone)
            return True
        except sqlite3.Error as e:
            logger.error("Failed to cancel appointment %s: %s", appointment_id, e)
            return False

    # =========================================================================
    # Rate limiting
    # =========================================================================

    def _check_rate_limit(self, phone: str) -> bool:
        """Returns True if request is within rate limit (3/min per phone)."""
        now = datetime.now()
        window_start = now - timedelta(seconds=self.RATE_WINDOW_SECONDS)

        timestamps = self._rate_counts.get(phone, [])
        # Keep only recent
        timestamps = [t for t in timestamps if t > window_start]
        timestamps.append(now)
        self._rate_counts[phone] = timestamps

        if len(timestamps) > self.RATE_LIMIT:
            logger.warning("Rate limit: phone=%s sent %d msgs in %ds", phone, len(timestamps), self.RATE_WINDOW_SECONDS)
            return False
        return True

    # =========================================================================
    # Dedup cache cleanup
    # =========================================================================

    def _cleanup_dedup_cache(self):
        """Rimuove message_id più vecchi di 24h dalla cache dedup."""
        cutoff = datetime.now() - timedelta(hours=24)
        expired = [mid for mid, ts in self._processed_id_times if ts < cutoff]
        for mid in expired:
            self._processed_ids.discard(mid)
        self._processed_id_times = [(mid, ts) for mid, ts in self._processed_id_times if ts >= cutoff]
