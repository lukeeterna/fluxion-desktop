"""
WhatsApp Integration Module for FLUXION Voice Agent.

Week 5: WhatsApp integration with VoicePipeline NLU.
Interfaces with existing Node.js whatsapp-service.cjs for WhatsApp Web automation.

Features:
- Read/send messages through Node.js service
- Process messages with VoicePipeline NLU
- Rate limiting for outbound messages
- Message logging to analytics
"""

import asyncio
import json
import os
import re
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from .analytics import ConversationLogger, ConversationOutcome, get_logger


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class WhatsAppConfig:
    """WhatsApp service configuration."""
    # Paths (relative to FLUXION root)
    fluxion_root: Path = field(default_factory=lambda: Path(__file__).parent.parent.parent.parent)
    session_dir: Path = field(default_factory=lambda: Path.home() / ".whatsapp-session")
    service_script: str = "scripts/whatsapp-service.cjs"

    # Service settings
    auto_responder_enabled: bool = True
    faq_category: str = "salone"
    response_delay_ms: int = 1000

    # Rate limits (conservative to avoid WhatsApp ban)
    rate_limit_per_minute: int = 3
    rate_limit_per_hour: int = 30
    rate_limit_per_day: int = 200

    # NLU settings
    use_voice_pipeline: bool = True  # Use VoicePipeline for NLU
    confidence_threshold: float = 0.5  # Below this, pass to operator

    # Integration
    http_bridge_url: Optional[str] = None  # Optional HTTP bridge
    node_path: str = "node"  # Node.js executable

    def __post_init__(self):
        """Resolve paths."""
        if isinstance(self.fluxion_root, str):
            self.fluxion_root = Path(self.fluxion_root)
        if isinstance(self.session_dir, str):
            self.session_dir = Path(self.session_dir)

    @property
    def status_file(self) -> Path:
        """Status file path."""
        return self.session_dir / "status.json"

    @property
    def config_file(self) -> Path:
        """Config file path."""
        return self.session_dir / "config.json"

    @property
    def messages_log(self) -> Path:
        """Messages log file path."""
        return self.session_dir / "messages.jsonl"

    @property
    def pending_questions_file(self) -> Path:
        """Pending questions file path."""
        return self.session_dir / "pending_questions.jsonl"

    @property
    def service_path(self) -> Path:
        """Full path to service script."""
        return self.fluxion_root / self.service_script


class ConnectionStatus(Enum):
    """WhatsApp connection status."""
    NOT_INITIALIZED = "not_initialized"
    INITIALIZING = "initializing"
    WAITING_QR = "waiting_qr"
    LOADING = "loading"
    AUTHENTICATED = "authenticated"
    READY = "ready"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    STOPPED = "stopped"


class MessageDirection(Enum):
    """Message direction."""
    INBOUND = "inbound"
    OUTBOUND = "outbound"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class WhatsAppMessage:
    """WhatsApp message."""
    id: str = ""
    phone: str = ""
    name: str = ""
    body: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    direction: MessageDirection = MessageDirection.INBOUND
    reply_to: Optional[str] = None
    confidence: float = 0.0
    passed_to_operator: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "phone": self.phone,
            "name": self.name,
            "body": self.body,
            "timestamp": self.timestamp.isoformat(),
            "direction": self.direction.value,
            "reply_to": self.reply_to,
            "confidence": self.confidence,
            "passed_to_operator": self.passed_to_operator,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WhatsAppMessage":
        """Create from dictionary."""
        return cls(
            id=data.get("id", ""),
            phone=data.get("from", data.get("to", data.get("phone", ""))),
            name=data.get("name", ""),
            body=data.get("body", ""),
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.now(),
            direction=MessageDirection(data.get("type", "inbound").replace("received", "inbound").replace("sent", "outbound")),
            reply_to=data.get("inReplyTo"),
            confidence=data.get("confidence", 0.0),
            passed_to_operator=data.get("passedToOperator", False),
        )


@dataclass
class PendingQuestion:
    """Pending question for operator review."""
    id: str = ""
    question: str = ""
    from_phone: str = ""
    from_name: str = ""
    category: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    status: str = "pending"  # pending, answered, saved_as_faq
    operator_response: Optional[str] = None
    response_timestamp: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PendingQuestion":
        """Create from dictionary."""
        return cls(
            id=data.get("id", ""),
            question=data.get("question", ""),
            from_phone=data.get("fromPhone", ""),
            from_name=data.get("fromName", ""),
            category=data.get("category", ""),
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.now(),
            status=data.get("status", "pending"),
            operator_response=data.get("operatorResponse"),
            response_timestamp=datetime.fromisoformat(data["responseTimestamp"]) if data.get("responseTimestamp") else None,
        )


# =============================================================================
# Rate Limiter
# =============================================================================

class WhatsAppRateLimiter:
    """Rate limiter for WhatsApp messages."""

    def __init__(
        self,
        per_minute: int = 3,
        per_hour: int = 30,
        per_day: int = 200
    ):
        self.limits = {
            "minute": per_minute,
            "hour": per_hour,
            "day": per_day,
        }
        self.counters = {
            "minute": 0,
            "hour": 0,
            "day": 0,
        }
        self.reset_times = {
            "minute": time.time(),
            "hour": time.time(),
            "day": time.time(),
        }
        self.reset_intervals = {
            "minute": 60,
            "hour": 3600,
            "day": 86400,
        }

    def _reset_if_needed(self):
        """Reset counters if time window has passed."""
        now = time.time()
        for period in self.counters:
            if now - self.reset_times[period] > self.reset_intervals[period]:
                self.counters[period] = 0
                self.reset_times[period] = now

    def can_send(self) -> bool:
        """Check if we can send a message."""
        self._reset_if_needed()
        return all(
            self.counters[period] < self.limits[period]
            for period in self.counters
        )

    def record_sent(self):
        """Record that a message was sent."""
        for period in self.counters:
            self.counters[period] += 1

    def get_status(self) -> Dict[str, Any]:
        """Get rate limit status."""
        self._reset_if_needed()
        return {
            "can_send": self.can_send(),
            "remaining": {
                period: self.limits[period] - self.counters[period]
                for period in self.counters
            },
            "next_reset": {
                period: int(self.reset_intervals[period] - (time.time() - self.reset_times[period]))
                for period in self.counters
            }
        }


# =============================================================================
# Message Templates
# =============================================================================

class WhatsAppTemplates:
    """WhatsApp message templates."""

    @staticmethod
    def conferma(
        nome: str, servizio: str, data: str, ora: str,
        operatore: Optional[str] = None, nome_attivita: Optional[str] = None
    ) -> str:
        """Appointment confirmation template - cordiale e con leve commerciali."""
        attivita = nome_attivita or "noi"
        msg = (
            f"*Prenotazione Confermata!*\n\n"
            f"Ciao {nome},\n"
            f"il tuo appuntamento e' confermato:\n\n"
            f"  {servizio}\n"
            f"  {data} alle {ora}\n"
        )
        if operatore:
            msg += f"  con {operatore}\n"
        msg += (
            f"\nTi aspettiamo da {attivita}!\n\n"
            f"Per modificare o cancellare, rispondi qui o chiamaci.\n"
            f"Consiglia {attivita} a un amico: chi ti presenta riceve il 10% di sconto sul primo trattamento!"
        )
        return msg

    @staticmethod
    def reminder_24h(nome: str, servizio: str, data: str, ora: str) -> str:
        """24-hour reminder template."""
        return (
            f"⏰ *Promemoria Appuntamento*\n\n"
            f"Ciao {nome}!\n\n"
            f"Ti ricordiamo il tuo appuntamento di *domani*:\n\n"
            f"📋 {servizio}\n"
            f"🕐 Ore {ora}\n\n"
            f"Rispondi:\n"
            f"✅ *OK* per confermare\n"
            f"❌ *ANNULLA* per disdire"
        )

    @staticmethod
    def reminder_2h(nome: str, ora: str) -> str:
        """2-hour reminder template."""
        return (
            f"🔔 *Ci vediamo tra poco!*\n\n"
            f"Ciao {nome}, ti aspettiamo alle {ora}.\n\n"
            f"A tra poco! 😊"
        )

    @staticmethod
    def cancellazione(nome: str, data: str, ora: str) -> str:
        """Cancellation confirmation template."""
        return (
            f"❌ *Appuntamento Cancellato*\n\n"
            f"Ciao {nome},\n\n"
            f"Il tuo appuntamento del {data} alle {ora} è stato cancellato.\n\n"
            f"Per una nuova prenotazione, rispondi a questo messaggio o chiamaci."
        )

    @staticmethod
    def benvenuto(nome: str, nome_attivita: str) -> str:
        """Welcome message template."""
        return (
            f"👋 *Benvenuto/a {nome}!*\n\n"
            f"Grazie per aver scelto {nome_attivita}!\n\n"
            f"Da oggi puoi:\n"
            f"📅 Prenotare appuntamenti\n"
            f"🔔 Ricevere promemoria\n"
            f"💬 Contattarci direttamente\n\n"
            f"Scrivi *PRENOTA* per fissare un appuntamento!"
        )

    @staticmethod
    def compleanno(nome: str, sconto: Optional[int] = None) -> str:
        """Birthday greeting template."""
        msg = (
            f"🎂 *Tanti Auguri {nome}!*\n\n"
            f"Ti auguriamo un fantastico compleanno! 🎉\n\n"
        )
        if sconto:
            msg += f"🎁 Come regalo, per te uno sconto del {sconto}% sul prossimo appuntamento!\n\n"
        msg += "Un abbraccio dal nostro team! 💝"
        return msg

    @staticmethod
    def no_info() -> str:
        """No information available template."""
        return (
            "Non ho informazioni sufficienti su questo argomento. 🤔\n\n"
            "Ho inoltrato la tua domanda al team, ti risponderanno a breve!\n\n"
            "Per urgenze puoi chiamarci direttamente. 📞"
        )

    @staticmethod
    def error() -> str:
        """Error template."""
        return "Mi dispiace, c'è un problema tecnico. Prova a chiamarci direttamente! 📞"

    @staticmethod
    def menu(nome: str) -> str:
        """Main menu template."""
        return (
            f"Ciao {nome}! 👋\n\n"
            f"Come posso aiutarti?\n\n"
            f"📅 *PRENOTA* - Nuovo appuntamento\n"
            f"❌ *ANNULLA* - Cancella prenotazione\n"
            f"🕐 *ORARI* - Orari di apertura\n"
            f"💰 *SERVIZI* - Listino prezzi\n\n"
            f"Oppure scrivi la tua domanda!"
        )


# =============================================================================
# WhatsApp Client
# =============================================================================

class WhatsAppClient:
    """
    WhatsApp client that interfaces with Node.js whatsapp-service.cjs.

    Communication happens via:
    1. File system (status.json, messages.jsonl)
    2. Subprocess calls for commands (send, status, etc.)

    For message processing, integrates with VoicePipeline NLU.
    """

    def __init__(self, config: Optional[WhatsAppConfig] = None):
        """
        Initialize WhatsApp client.

        Args:
            config: WhatsApp configuration
        """
        self.config = config or WhatsAppConfig()
        self.rate_limiter = WhatsAppRateLimiter(
            per_minute=self.config.rate_limit_per_minute,
            per_hour=self.config.rate_limit_per_hour,
            per_day=self.config.rate_limit_per_day,
        )
        self.templates = WhatsAppTemplates()

        # Analytics logger
        self._analytics_logger: Optional[ConversationLogger] = None

        # Message handler callback
        self._message_handler: Optional[Callable[[WhatsAppMessage], None]] = None

        # VoicePipeline/Orchestrator integration
        self._pipeline = None
        self._orchestrator = None  # Preferred: has disambiguation

        # Conversation sessions by phone number
        self._sessions: Dict[str, str] = {}  # phone -> session_id

        # Ensure session directory exists
        self.config.session_dir.mkdir(parents=True, exist_ok=True)

    @property
    def analytics(self) -> ConversationLogger:
        """Get analytics logger."""
        if self._analytics_logger is None:
            self._analytics_logger = get_logger()
        return self._analytics_logger

    def set_pipeline(self, pipeline):
        """Set VoicePipeline for NLU processing."""
        self._pipeline = pipeline

    def set_orchestrator(self, orchestrator):
        """Set VoiceOrchestrator for NLU processing (with disambiguation)."""
        self._orchestrator = orchestrator

    def set_message_handler(self, handler: Callable[[WhatsAppMessage], None]):
        """Set callback for incoming messages."""
        self._message_handler = handler

    # =========================================================================
    # Status & Connection
    # =========================================================================

    def get_status(self) -> Dict[str, Any]:
        """
        Get WhatsApp service status.

        Returns:
            Status dictionary
        """
        if not self.config.status_file.exists():
            return {"status": ConnectionStatus.NOT_INITIALIZED.value}

        try:
            with open(self.config.status_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"status": ConnectionStatus.ERROR.value}

    def is_connected(self) -> bool:
        """Check if WhatsApp is connected and ready."""
        status = self.get_status()
        return status.get("status") == ConnectionStatus.READY.value

    def start_service(self) -> bool:
        """
        Start WhatsApp service (requires QR scan).

        Note: This blocks until QR is scanned or timeout.
        For production, run service in background.

        Returns:
            True if service started successfully
        """
        if not self.config.service_path.exists():
            raise FileNotFoundError(f"WhatsApp service not found: {self.config.service_path}")

        try:
            # Start service in background
            subprocess.Popen(
                [self.config.node_path, str(self.config.service_path), "start"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.config.fluxion_root),
            )
            return True
        except subprocess.SubprocessError as e:
            print(f"Failed to start WhatsApp service: {e}")
            return False

    # =========================================================================
    # Message Sending
    # =========================================================================

    def normalize_phone(self, phone: str) -> str:
        """
        Normalize Italian phone number.

        Args:
            phone: Phone number in any format

        Returns:
            Normalized phone number (39XXXXXXXXX)
        """
        # Remove non-digit characters
        cleaned = re.sub(r'\D', '', phone)

        # Add Italy prefix if missing
        if cleaned.startswith('0'):
            cleaned = '39' + cleaned[1:]
        elif not cleaned.startswith('39'):
            cleaned = '39' + cleaned

        return cleaned

    def send_message(self, phone: str, message: str) -> Dict[str, Any]:
        """
        Send WhatsApp message via Node.js service.

        Args:
            phone: Recipient phone number
            message: Message text

        Returns:
            Result dictionary with success status
        """
        # Check rate limit
        if not self.rate_limiter.can_send():
            return {
                "success": False,
                "error": "Rate limit reached",
                "rate_limit": self.rate_limiter.get_status(),
            }

        # Check connection
        if not self.is_connected():
            return {
                "success": False,
                "error": "WhatsApp not connected",
                "status": self.get_status(),
            }

        # Normalize phone number
        normalized_phone = self.normalize_phone(phone)

        try:
            # Call Node.js service
            result = subprocess.run(
                [
                    self.config.node_path,
                    str(self.config.service_path),
                    "send",
                    normalized_phone,
                    message,
                ],
                cwd=str(self.config.fluxion_root),
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                self.rate_limiter.record_sent()

                # Log to analytics
                self._log_message(
                    phone=normalized_phone,
                    body=message,
                    direction=MessageDirection.OUTBOUND,
                )

                return {"success": True}
            else:
                return {
                    "success": False,
                    "error": result.stderr or "Send failed",
                }

        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Send timeout"}
        except subprocess.SubprocessError as e:
            return {"success": False, "error": str(e)}

    async def send_message_async(self, phone: str, message: str) -> Dict[str, Any]:
        """Async version of send_message."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.send_message, phone, message)

    def send_template(
        self,
        phone: str,
        template_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send templated message.

        Args:
            phone: Recipient phone number
            template_name: Template name (conferma, reminder_24h, etc.)
            **kwargs: Template parameters

        Returns:
            Result dictionary
        """
        template_func = getattr(self.templates, template_name, None)
        if not template_func:
            return {"success": False, "error": f"Unknown template: {template_name}"}

        message = template_func(**kwargs)
        return self.send_message(phone, message)

    # =========================================================================
    # Message Reading & Processing
    # =========================================================================

    def get_messages(
        self,
        since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[WhatsAppMessage]:
        """
        Get messages from log file.

        Args:
            since: Only messages after this time
            limit: Maximum number of messages

        Returns:
            List of messages
        """
        if not self.config.messages_log.exists():
            return []

        messages = []
        try:
            with open(self.config.messages_log, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        msg = WhatsAppMessage.from_dict(data)
                        if since and msg.timestamp < since:
                            continue
                        messages.append(msg)
                    except (json.JSONDecodeError, KeyError):
                        continue
        except IOError:
            return []

        # Sort by timestamp and limit
        messages.sort(key=lambda m: m.timestamp, reverse=True)
        return messages[:limit]

    def get_pending_questions(self) -> List[PendingQuestion]:
        """Get pending questions for operator review."""
        if not self.config.pending_questions_file.exists():
            return []

        questions = []
        try:
            with open(self.config.pending_questions_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        questions.append(PendingQuestion.from_dict(data))
                    except (json.JSONDecodeError, KeyError):
                        continue
        except IOError:
            return []

        return [q for q in questions if q.status == "pending"]

    async def process_message(
        self,
        message: WhatsAppMessage,
        verticale_id: str = "salone"
    ) -> Optional[str]:
        """
        Process incoming message with VoiceOrchestrator (preferred) or VoicePipeline.

        Orchestrator includes disambiguation (data_nascita + soprannome).

        Args:
            message: Incoming WhatsApp message
            verticale_id: Business vertical ID

        Returns:
            Response text or None if passed to operator
        """
        if not self._orchestrator and not self._pipeline:
            # No NLU engine, use Node.js auto-responder
            return None

        # Get or create session for this phone
        session_id = self._sessions.get(message.phone)
        if not session_id:
            session_id = self.analytics.start_session(
                verticale_id=verticale_id,
                client_name=message.name,
            )
            self._sessions[message.phone] = session_id

        start_time = time.time()

        try:
            # Prefer orchestrator (has disambiguation)
            if self._orchestrator:
                result = await self._orchestrator.process(message.body)
                response = result.response
                intent = result.intent
                layer = result.layer.value
                latency_ms = result.latency_ms
                confidence = 1.0  # Orchestrator is deterministic
            else:
                # Fallback to pipeline
                response = await self._pipeline.process_input(
                    message.body,
                    verticale_id=verticale_id,
                )
                latency_ms = (time.time() - start_time) * 1000
                intent_result = self._pipeline.last_intent_result
                intent = intent_result.intent if intent_result else "unknown"
                layer = intent_result.layer_used if intent_result else "unknown"
                confidence = intent_result.confidence if intent_result else 0.0

                if confidence < self.config.confidence_threshold:
                    # Low confidence - pass to operator
                    self._save_pending_question(message)
                    return self.templates.no_info()

            # Log analytics
            self.analytics.log_turn(
                session_id=session_id,
                user_input=message.body,
                intent=intent,
                response=response,
                latency_ms=latency_ms,
                layer_used=layer,
                intent_confidence=confidence,
            )

            return response

        except Exception as e:
            print(f"NLU processing error: {e}")
            return self.templates.error()

    def _save_pending_question(self, message: WhatsAppMessage):
        """Save message as pending question for operator."""
        question = {
            "id": f"pq_{int(time.time() * 1000)}",
            "question": message.body,
            "fromPhone": message.phone,
            "fromName": message.name,
            "category": self.config.faq_category,
            "timestamp": datetime.now().isoformat(),
            "status": "pending",
            "operatorResponse": None,
            "responseTimestamp": None,
        }

        with open(self.config.pending_questions_file, "a") as f:
            f.write(json.dumps(question) + "\n")

    # =========================================================================
    # Analytics Logging
    # =========================================================================

    def _log_message(
        self,
        phone: str,
        body: str,
        direction: MessageDirection,
        name: str = "",
        confidence: float = 0.0,
        passed_to_operator: bool = False,
    ):
        """Log message to analytics."""
        self.analytics.log_whatsapp_message(
            phone=phone,
            name=name,
            body=body,
            direction=direction.value,
            confidence=confidence,
            passed_to_operator=passed_to_operator,
        )

    # =========================================================================
    # Service Configuration
    # =========================================================================

    def get_config(self) -> Dict[str, Any]:
        """Get Node.js service configuration."""
        if not self.config.config_file.exists():
            return {}

        try:
            with open(self.config.config_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}

    def update_config(self, **kwargs):
        """Update Node.js service configuration."""
        config = self.get_config()
        config.update(kwargs)

        with open(self.config.config_file, "w") as f:
            json.dump(config, f, indent=2)

    def enable_auto_responder(self):
        """Enable auto-responder."""
        self.update_config(autoResponderEnabled=True)

    def disable_auto_responder(self):
        """Disable auto-responder."""
        self.update_config(autoResponderEnabled=False)

    def set_faq_category(self, category: str):
        """Set FAQ category."""
        self.update_config(faqCategory=category)
        self.config.faq_category = category


# =============================================================================
# Analytics Extension
# =============================================================================

def _add_whatsapp_logging_to_analytics():
    """Add WhatsApp message logging methods to ConversationLogger."""

    # Extend schema
    WHATSAPP_SCHEMA = """
    -- WhatsApp messages table (Week 5)
    CREATE TABLE IF NOT EXISTS whatsapp_messages (
        id TEXT PRIMARY KEY,
        conversation_id TEXT,
        phone TEXT NOT NULL,
        name TEXT,
        body TEXT NOT NULL,
        direction TEXT NOT NULL,
        timestamp DATETIME NOT NULL,
        confidence REAL DEFAULT 0.0,
        passed_to_operator BOOLEAN DEFAULT FALSE,
        template_used TEXT,
        delivery_status TEXT DEFAULT 'sent',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (conversation_id) REFERENCES conversations(id)
    );

    CREATE INDEX IF NOT EXISTS idx_wa_messages_phone ON whatsapp_messages(phone);
    CREATE INDEX IF NOT EXISTS idx_wa_messages_timestamp ON whatsapp_messages(timestamp);
    """

    def log_whatsapp_message(
        self,
        phone: str,
        body: str,
        direction: str,
        name: str = "",
        confidence: float = 0.0,
        passed_to_operator: bool = False,
        template_used: Optional[str] = None,
        conversation_id: Optional[str] = None,
    ) -> str:
        """
        Log WhatsApp message.

        Args:
            phone: Phone number
            body: Message body
            direction: "inbound" or "outbound"
            name: Contact name
            confidence: Response confidence (for auto-responses)
            passed_to_operator: Whether message was escalated
            template_used: Template name if used
            conversation_id: Optional linked conversation

        Returns:
            Message ID
        """
        import uuid
        msg_id = str(uuid.uuid4())

        with self._get_connection() as conn:
            # Ensure table exists
            conn.executescript(WHATSAPP_SCHEMA)

            conn.execute("""
                INSERT INTO whatsapp_messages (
                    id, conversation_id, phone, name, body, direction,
                    timestamp, confidence, passed_to_operator, template_used
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                msg_id,
                conversation_id,
                phone,
                name,
                body,
                direction,
                datetime.now().isoformat(),
                confidence,
                passed_to_operator,
                template_used,
            ))
            conn.commit()

        return msg_id

    def get_whatsapp_metrics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Get WhatsApp messaging metrics.

        Returns:
            Dictionary with messaging statistics
        """
        with self._get_connection() as conn:
            # Ensure table exists
            conn.executescript(WHATSAPP_SCHEMA)

            # Build date filter
            date_filter = ""
            params = []
            if start_date:
                date_filter = " WHERE timestamp >= ?"
                params.append(start_date.isoformat())
            if end_date:
                if date_filter:
                    date_filter += " AND timestamp <= ?"
                else:
                    date_filter = " WHERE timestamp <= ?"
                params.append(end_date.isoformat())

            row = conn.execute(f"""
                SELECT
                    COUNT(*) as total_messages,
                    SUM(CASE WHEN direction = 'inbound' THEN 1 ELSE 0 END) as inbound_messages,
                    SUM(CASE WHEN direction = 'outbound' THEN 1 ELSE 0 END) as outbound_messages,
                    SUM(CASE WHEN passed_to_operator = 1 THEN 1 ELSE 0 END) as escalated_messages,
                    AVG(confidence) as avg_confidence,
                    COUNT(DISTINCT phone) as unique_contacts
                FROM whatsapp_messages
                {date_filter}
            """, params).fetchone()

            return {
                "total_messages": row["total_messages"] or 0,
                "inbound_messages": row["inbound_messages"] or 0,
                "outbound_messages": row["outbound_messages"] or 0,
                "escalated_messages": row["escalated_messages"] or 0,
                "avg_confidence": row["avg_confidence"] or 0,
                "unique_contacts": row["unique_contacts"] or 0,
                "auto_response_rate": (
                    (row["outbound_messages"] or 0) / (row["inbound_messages"] or 1)
                ),
                "escalation_rate": (
                    (row["escalated_messages"] or 0) / (row["total_messages"] or 1)
                ),
            }

    # Add methods to ConversationLogger
    ConversationLogger.log_whatsapp_message = log_whatsapp_message
    ConversationLogger.get_whatsapp_metrics = get_whatsapp_metrics


# Initialize analytics extension
_add_whatsapp_logging_to_analytics()


# =============================================================================
# WhatsApp Manager (High-Level Interface)
# =============================================================================

class WhatsAppManager:
    """
    High-level WhatsApp manager for FLUXION integration.

    Combines WhatsApp client, VoiceOrchestrator/VoicePipeline, and analytics.
    """

    def __init__(self, config: Optional[WhatsAppConfig] = None):
        """
        Initialize WhatsApp manager.

        Args:
            config: WhatsApp configuration
        """
        self.config = config or WhatsAppConfig()
        self.client = WhatsAppClient(self.config)
        self._running = False
        self._poll_task: Optional[asyncio.Task] = None
        self._last_message_time: Optional[datetime] = None

    def set_pipeline(self, pipeline):
        """Set VoicePipeline for NLU processing."""
        self.client.set_pipeline(pipeline)

    def set_orchestrator(self, orchestrator):
        """Set VoiceOrchestrator for NLU processing (with disambiguation)."""
        self.client.set_orchestrator(orchestrator)

    async def start(self) -> bool:
        """
        Start WhatsApp manager.

        Returns:
            True if started successfully
        """
        if not self.client.is_connected():
            print("WhatsApp not connected. Run Node.js service first.")
            return False

        self._running = True
        self._last_message_time = datetime.now()

        # Start message polling
        self._poll_task = asyncio.create_task(self._poll_messages())

        print("WhatsApp manager started")
        return True

    async def stop(self):
        """Stop WhatsApp manager."""
        self._running = False

        if self._poll_task:
            self._poll_task.cancel()
            try:
                await self._poll_task
            except asyncio.CancelledError:
                pass

        print("WhatsApp manager stopped")

    async def _poll_messages(self, interval: float = 2.0):
        """Poll for new messages."""
        while self._running:
            try:
                messages = self.client.get_messages(since=self._last_message_time)

                for msg in messages:
                    if msg.direction == MessageDirection.INBOUND:
                        await self._handle_message(msg)

                if messages:
                    self._last_message_time = max(m.timestamp for m in messages)

            except Exception as e:
                print(f"Message poll error: {e}")

            await asyncio.sleep(interval)

    async def _handle_message(self, message: WhatsAppMessage):
        """Handle incoming message."""
        print(f"[WhatsApp] From {message.name or message.phone}: {message.body[:50]}...")

        # Process with pipeline
        response = await self.client.process_message(message)

        if response:
            # Send auto-response
            await asyncio.sleep(self.config.response_delay_ms / 1000)
            result = await self.client.send_message_async(message.phone, response)

            if result["success"]:
                print(f"[WhatsApp] Sent auto-response to {message.phone}")
            else:
                print(f"[WhatsApp] Failed to send: {result.get('error')}")

    # =========================================================================
    # Convenience Methods
    # =========================================================================

    async def send_reminder(
        self,
        phone: str,
        nome: str,
        servizio: str,
        data: str,
        ora: str,
        hours_before: int = 24,
    ) -> Dict[str, Any]:
        """
        Send appointment reminder.

        Args:
            phone: Client phone number
            nome: Client name
            servizio: Service name
            data: Appointment date
            ora: Appointment time
            hours_before: Hours before appointment (24 or 2)

        Returns:
            Send result
        """
        if hours_before >= 24:
            template = "reminder_24h"
        else:
            template = "reminder_2h"

        return self.client.send_template(
            phone,
            template,
            nome=nome,
            servizio=servizio,
            data=data,
            ora=ora,
        )

    async def send_confirmation(
        self,
        phone: str,
        nome: str,
        servizio: str,
        data: str,
        ora: str,
        operatore: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send appointment confirmation."""
        return self.client.send_template(
            phone,
            "conferma",
            nome=nome,
            servizio=servizio,
            data=data,
            ora=ora,
            operatore=operatore,
        )

    async def send_cancellation(
        self,
        phone: str,
        nome: str,
        data: str,
        ora: str,
    ) -> Dict[str, Any]:
        """Send cancellation confirmation."""
        return self.client.send_template(
            phone,
            "cancellazione",
            nome=nome,
            data=data,
            ora=ora,
        )

    def get_status(self) -> Dict[str, Any]:
        """Get manager status."""
        return {
            "connected": self.client.is_connected(),
            "running": self._running,
            "service_status": self.client.get_status(),
            "rate_limit": self.client.rate_limiter.get_status(),
            "pending_questions": len(self.client.get_pending_questions()),
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get WhatsApp metrics."""
        return self.client.analytics.get_whatsapp_metrics()


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Configuration
    "WhatsAppConfig",
    "ConnectionStatus",
    "MessageDirection",
    # Data classes
    "WhatsAppMessage",
    "PendingQuestion",
    # Core classes
    "WhatsAppClient",
    "WhatsAppManager",
    "WhatsAppRateLimiter",
    "WhatsAppTemplates",
]
