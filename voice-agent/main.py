#!/usr/bin/env python3
"""
FLUXION Voice Agent - Main Entry Point
Starts the voice pipeline server for Tauri integration

Uses the Enterprise Orchestrator with 4-layer RAG pipeline:
- L0: Special commands (aiuto, operatore, annulla)
- L1: Exact match cortesia (buongiorno, grazie)
- L2: Slot filling (booking state machine)
- L3: FAQ retrieval
- L4: Groq LLM fallback
"""

import os
import sys

# Fix OMP Error #15: multiple libraries loading libiomp5.dylib (numpy + onnxruntime)
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import json
import time
import asyncio
import argparse
from collections import defaultdict
from pathlib import Path
from typing import Dict, Optional

# Add src to path — works both from source and PyInstaller bundle
if getattr(sys, "frozen", False):
    sys.path.insert(0, str(Path(sys._MEIPASS) / "src"))
else:
    sys.path.insert(0, str(Path(__file__).parent / "src"))

import logging

from dotenv import load_dotenv
from aiohttp import web

# Load environment variables from .env file
load_dotenv()

# ─────────────────────────────────────────────────────────────────
# Logging: verbose for conversation debugging
# ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('fluxion.voice')

# ─────────────────────────────────────────────────────────────────
# Security: allowed origins (localhost only — F14)
# ─────────────────────────────────────────────────────────────────
_ALLOWED_ORIGINS = {
    "http://localhost",
    "http://127.0.0.1",
    "tauri://localhost",
}

def _is_allowed_origin(origin: str) -> bool:
    """Return True if origin is a localhost variant."""
    if not origin:
        return True  # No origin header = same-origin request from Tauri
    for allowed in _ALLOWED_ORIGINS:
        if origin.startswith(allowed):
            return True
    return False

# ─────────────────────────────────────────────────────────────────
# Security: CORS — localhost only (F14)
# ─────────────────────────────────────────────────────────────────
@web.middleware
async def cors_middleware(request, handler):
    """CORS middleware — restricted to localhost origins only (F14 Security)."""
    origin = request.headers.get("Origin", "")

    if request.method == "OPTIONS":
        if _is_allowed_origin(origin):
            response = web.Response(status=204)
            response.headers["Access-Control-Allow-Origin"] = origin or "http://localhost"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type"
            return response
        return web.Response(status=403)

    response = await handler(request)

    if _is_allowed_origin(origin):
        response.headers["Access-Control-Allow-Origin"] = origin or "http://localhost"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

# ─────────────────────────────────────────────────────────────────
# Security: rate limiting — max 100 req/min per IP (F14)
# ─────────────────────────────────────────────────────────────────
_rate_limit_store: dict = defaultdict(list)
_RATE_LIMIT_MAX = 100
_RATE_LIMIT_WINDOW = 60.0  # seconds
_RATE_LIMIT_MAX_KEYS = 500  # H3: hard cap on tracked IPs to prevent memory growth

@web.middleware
async def rate_limit_middleware(request, handler):
    """Rate limiter: max 100 req/min per IP (F14). Localhost escluso (app locale + VAD chunks)."""
    ip = request.remote or "unknown"

    # Localhost escluso: VAD invia chunk ogni 100ms = 600 req/min, limite non ha senso per traffico locale
    if ip in ("127.0.0.1", "::1", "localhost"):
        return await handler(request)

    now = time.monotonic()
    window_start = now - _RATE_LIMIT_WINDOW

    # H3: Evict stale entries to prevent unbounded memory growth
    stale_keys = [k for k, v in _rate_limit_store.items() if not v or now - v[-1] > 120]
    for k in stale_keys:
        del _rate_limit_store[k]

    # H3: Hard cap — if too many tracked IPs, evict oldest half
    if len(_rate_limit_store) > _RATE_LIMIT_MAX_KEYS:
        sorted_keys = sorted(_rate_limit_store, key=lambda k: _rate_limit_store[k][-1] if _rate_limit_store[k] else 0)
        for k in sorted_keys[:len(sorted_keys) // 2]:
            del _rate_limit_store[k]

    # Keep only timestamps within the window
    timestamps = _rate_limit_store[ip]
    _rate_limit_store[ip] = [t for t in timestamps if t > window_start]

    if len(_rate_limit_store[ip]) >= _RATE_LIMIT_MAX:
        return web.json_response({
            "success": False,
            "response": "Mi scusi, il sistema è momentaneamente occupato. Riprovi tra qualche secondo.",
            "error": "rate_limit",
            "intent": "error_rate_limit",
            "audio_base64": None,
            "transcription": None,
            "fsm_state": None,
        }, status=200)

    _rate_limit_store[ip].append(now)
    return await handler(request)

# Use enterprise orchestrator instead of old pipeline
from src.orchestrator import VoiceOrchestrator
from src.groq_client import GroqClient
from src.tts import get_tts
from src.stt import get_stt_engine
from src.http_client import close_http_session
from src.supplier_email_service import get_email_service
from src.vad_http_handler import VADHTTPHandler, add_wav_header
from src.whatsapp_callback import WhatsAppCallbackHandler
from src.reminder_scheduler import start_reminder_scheduler
from src.tts_download_manager import TTSDownloadManager
from src.sales_state_machine import SalesStateMachine


# Default configuration (loaded from database at runtime)
# business_name will be fetched from verticale config via HTTP Bridge
DEFAULT_CONFIG = {
    "business_name": None,  # Will be loaded from DB - MUST be configured!
    "opening_hours": "09:00",
    "closing_hours": "19:00",
    "working_days": "Lunedi-Sabato",
    "services": ["Taglio", "Piega", "Colore", "Trattamenti"]
}


def _load_business_config_from_sqlite() -> Optional[dict]:
    """
    Read business config directly from Fluxion SQLite DB.
    Used as fallback when Tauri HTTP Bridge (port 3001) is offline.
    Returns dict with nome_attivita, categoria_attivita, orari, etc.
    """
    import sqlite3
    home = Path.home()
    if sys.platform == "win32":
        appdata = Path(os.environ.get("APPDATA", home / "AppData" / "Roaming"))
        candidates = [
            appdata / "com.fluxion.desktop" / "fluxion.db",
            appdata / "fluxion" / "fluxion.db",
        ]
    else:
        candidates = [
            home / "Library" / "Application Support" / "com.fluxion.desktop" / "fluxion.db",
            home / "Library" / "Application Support" / "fluxion" / "fluxion.db",
        ]
    db_path = os.environ.get("FLUXION_DB_PATH")
    if db_path:
        candidates.insert(0, Path(db_path))

    for path in candidates:
        if path.exists():
            try:
                with sqlite3.connect(str(path), timeout=3) as conn:
                    rows = {
                        r[0]: r[1] for r in conn.execute(
                            "SELECT chiave, valore FROM impostazioni WHERE chiave IN "
                            "('nome_attivita','categoria_attivita','macro_categoria','micro_categoria',"
                            "'orario_apertura','orario_chiusura','giorni_lavorativi')"
                        ).fetchall()
                    }
                if rows.get("nome_attivita"):
                    print(f"   ✅ config da SQLite: '{rows['nome_attivita']}' vertical='{rows.get('categoria_attivita', '')}' ({path})")
                    return rows
            except Exception as e:
                print(f"   SQLite fallback error ({path}): {e}")
    return None


def _load_business_name_from_sqlite() -> Optional[str]:
    """Legacy wrapper — returns just the name string."""
    cfg = _load_business_config_from_sqlite()
    return cfg.get("nome_attivita") if cfg else None


async def load_business_config_from_db() -> dict:
    """
    Load business configuration from database via HTTP Bridge.
    Falls back to direct SQLite read when Tauri is not running.

    The business_name is configured in the verticale settings during
    initial setup, NOT hardcoded as "FLUXION Demo".

    Returns:
        Config dict with business_name from database
    """
    import aiohttp
    try:
        async with aiohttp.ClientSession() as session:
            # Try to get verticale config via HTTP Bridge (Tauri must be running)
            async with session.get(
                "http://127.0.0.1:3001/api/verticale/config",
                timeout=aiohttp.ClientTimeout(total=2)
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "business_name": data.get("nome_attivita") or data.get("business_name"),
                        "verticale_id": data.get("categoria_attivita") or data.get("verticale_id", ""),
                        "micro_categoria": data.get("micro_categoria", ""),
                        "opening_hours": data.get("orario_apertura", "09:00"),
                        "closing_hours": data.get("orario_chiusura", "19:00"),
                        "working_days": data.get("giorni_lavorativi", "Lunedi-Sabato"),
                        "services": data.get("servizi", ["Taglio", "Piega", "Colore"])
                    }
    except Exception:
        pass

    # Fallback: read directly from SQLite (Tauri offline = standalone mode)
    db_cfg = _load_business_config_from_sqlite()
    if db_cfg and db_cfg.get("nome_attivita"):
        return {
            "business_name": db_cfg["nome_attivita"],
            "verticale_id": db_cfg.get("categoria_attivita", ""),
            "micro_categoria": db_cfg.get("micro_categoria", ""),
            "opening_hours": db_cfg.get("orario_apertura", "09:00"),
            "closing_hours": db_cfg.get("orario_chiusura", "19:00"),
            "working_days": db_cfg.get("giorni_lavorativi", "Lunedi-Sabato"),
            "services": ["Taglio", "Piega", "Colore", "Trattamenti"]
        }

    print("   ⚠️  WARNING: nome_attivita non configurato nel DB!")
    return None


class VoiceAgentHTTPServer:
    """HTTP Server for Tauri integration using Enterprise Orchestrator."""

    def __init__(
        self,
        orchestrator: VoiceOrchestrator,
        groq_client: GroqClient,
        host: str = "127.0.0.1",
        port: int = 3002
    ):
        self.orchestrator = orchestrator
        self.groq = groq_client
        self.host = host
        self.port = port
        self.app = web.Application(
            middlewares=[rate_limit_middleware, cors_middleware],
            client_max_size=50 * 1024 * 1024,  # 50MB per audio uploads
        )
        # H7: Single-tenant design — one salon, one pipeline instance, one active
        # session at a time. Not shared across concurrent requests; used as fallback
        # when request does not include session_id. Safe for single-user voice pipeline.
        self._current_session_id: Optional[str] = None

        # Initialize VAD handler
        self.vad_handler = VADHTTPHandler(orchestrator, groq_client)

        # Initialize WhatsApp callback handler
        self.wa_callback = WhatsAppCallbackHandler(orchestrator=orchestrator)

        # F15: VoIPManager — injected after startup by main() if SIP is configured
        self.voip_manager = None
        # GAP-P1-7: WhatsApp client — injected after startup by main() for waitlist trigger
        self.wa_client = None

        # F18: Sales FSM instances (keyed by phone/session for multi-lead support)
        self._sales_sessions: Dict[str, SalesStateMachine] = {}

        self._setup_routes()

    def _setup_routes(self):
        """Setup HTTP routes."""
        self.app.router.add_get("/health", self.health_handler)
        self.app.router.add_post("/api/voice/greet", self.greet_handler)
        self.app.router.add_post("/api/voice/process", self.process_handler)
        self.app.router.add_post("/api/voice/say", self.say_handler)
        self.app.router.add_post("/api/voice/reset", self.reset_handler)
        self.app.router.add_get("/api/voice/status", self.status_handler)
        # Supplier email endpoint
        self.app.router.add_post("/api/supplier-orders/send-email", self.send_email_handler)

        # WhatsApp callback (incoming messages pushed from whatsapp-service.cjs)
        self.app.router.add_post("/api/voice/whatsapp/callback", self.wa_callback.handle)
        # Gap #4: send booking confirmation WA + register pending (called by Tauri on booking create)
        self.app.router.add_post("/api/voice/whatsapp/send_confirmation", self.wa_send_confirmation_handler)
        self.app.router.add_post("/api/voice/whatsapp/register_pending", self.wa_register_pending_handler)

        # F03: Latency monitoring endpoint - P50/P95/P99 from analytics DB
        self.app.router.add_get("/api/metrics/latency", self.latency_metrics_handler)

        # F-SARA-VOICE: TTS hardware detection + mode management endpoints
        self.app.router.add_get("/api/tts/hardware", self.tts_hardware_handler)
        self.app.router.add_get("/api/tts/mode", self.tts_mode_handler)
        self.app.router.add_post("/api/tts/mode", self.tts_mode_set_handler)

        # GAP-P1-7: Waitlist immediate trigger (called by http_bridge on appointment cancel)
        self.app.router.add_post("/api/waitlist/trigger", self.waitlist_trigger_handler)

        # F15: VoIP endpoints (SIP status + control)
        self.app.router.add_get("/api/voice/voip/status", self.voip_status_handler)
        self.app.router.add_post("/api/voice/voip/hangup", self.voip_hangup_handler)

        # Vertical switching (for testing / multi-vertical support)
        self.app.router.add_post("/api/voice/set-vertical", self.set_vertical_handler)

        # F18: Sales endpoints (Sara sells FLUXION via WhatsApp)
        self.app.router.add_post("/api/sales/process", self.sales_process_handler)
        self.app.router.add_post("/api/sales/reset", self.sales_reset_handler)
        self.app.router.add_get("/api/sales/status", self.sales_status_handler)

        # Alias routes without prefix (for frontend HTTP fallback / E2E tests)
        self.app.router.add_get("/status", self.status_handler)
        self.app.router.add_post("/greet", self.greet_handler)
        self.app.router.add_post("/process", self.process_handler)
        self.app.router.add_post("/say", self.say_handler)
        self.app.router.add_post("/reset", self.reset_handler)
        self.app.router.add_post("/process-audio", self.process_handler)  # Same as /process

        # VAD endpoints (real-time voice activity detection)
        self.vad_handler.setup_routes(self.app)

    async def health_handler(self, request):
        """Health check endpoint."""
        from src.stt import _stt_instance
        stt_label = "not-loaded"
        if _stt_instance is not None:
            primary = getattr(_stt_instance, 'primary', _stt_instance)
            stt_label = type(primary).__name__
        return web.json_response({
            "status": "ok",
            "service": "FLUXION Voice Agent Enterprise",
            "version": "2.1.0",
            "pipeline": "4-layer RAG",
            "features": {
                "vad": True,
                "vad_library": "silero-or-webrtc",
                "stt": stt_label,
                "tts": "adaptive"
            }
        })

    async def greet_handler(self, request):
        """Generate greeting and start new session."""
        try:
            logger.info("=== GREET REQUEST ===")
            result = await self.orchestrator.start_session()
            self._current_session_id = result.session_id
            logger.info("SARA: %s [session=%s]", result.response, result.session_id)

            return web.json_response({
                "success": True,
                "response": result.response,
                "audio_base64": result.audio_bytes.hex() if result.audio_bytes else "",
                "session_id": result.session_id,
                "intent": result.intent,
                "layer": result.layer.value
            })
        except Exception as e:
            logger.error("Greet handler error: %s", e, exc_info=True)
            return web.json_response({
                "success": False,
                "error": "Errore interno del server"
            }, status=500)

    async def process_handler(self, request):
        """Process voice/text input through 4-layer pipeline."""
        try:
            data = await request.json()
            transcription = None
            logger.info("=== PROCESS REQUEST === keys=%s", list(data.keys()))

            if "audio_hex" in data:
                # STT: Transcribe audio first
                audio_hex_len = len(data["audio_hex"])
                logger.info("AUDIO: received %d hex chars (~%.1f sec)", audio_hex_len, audio_hex_len / 2 / 16000)
                audio_data = bytes.fromhex(data["audio_hex"])
                # Add WAV header only if data is raw PCM (not already WAV)
                wav_data = audio_data if audio_data[:4] == b'RIFF' else add_wav_header(audio_data)
                transcription = await self.groq.transcribe_audio(wav_data)
                logger.info("STT: '%s'", transcription)
                user_input = transcription
            elif "text" in data:
                user_input = data["text"]
                transcription = user_input
            else:
                return web.json_response({
                    "success": False,
                    "error": "Missing 'audio_hex' or 'text' in request"
                }, status=400)

            # Process through orchestrator
            # Use session_id from request, fallback to current session
            request_session_id = data.get("session_id") or self._current_session_id
            result = await self.orchestrator.process(
                user_input=user_input,
                session_id=request_session_id
            )
            fsm_state = 'n/a'
            try:
                fsm_state = self.orchestrator.booking_sm.context.state.value
            except (AttributeError, TypeError):
                pass
            logger.info("USER: '%s' → SARA: '%s' [intent=%s, layer=%s, fsm=%s]",
                        user_input, (result.response or '')[:100],
                        result.intent, result.layer.value if result.layer else '?',
                        fsm_state)

            # Build booking action if relevant
            booking_action = None
            if result.booking_created:
                booking_action = {
                    "action": "booking_created",
                    "booking_id": result.booking_id,
                    "context": result.booking_context
                }
            elif result.booking_context:
                booking_action = {
                    "action": "booking_in_progress",
                    "context": result.booking_context
                }

            # Expose FSM state for debugging/frontend (BUG 6 fix)
            try:
                fsm_state = self.orchestrator.booking_sm.context.state.value
            except Exception:
                fsm_state = "unknown"

            return web.json_response({
                "success": True,
                "transcription": transcription,
                "response": result.response,
                "intent": result.intent,
                "layer": result.layer.value,
                "fsm_state": fsm_state,
                "audio_base64": result.audio_bytes.hex() if result.audio_bytes else "",
                "booking_action": booking_action,
                "should_escalate": result.should_escalate,
                "should_exit": result.should_exit,
                "needs_disambiguation": result.needs_disambiguation,
                "session_id": result.session_id,
                "latency_ms": result.latency_ms
            })

        except Exception as e:
            logger.error("Process handler error: %s", e, exc_info=True)
            return web.json_response({
                "success": False,
                "error": "Errore interno del server"
            }, status=500)

    async def say_handler(self, request):
        """Text-to-speech only (no NLU processing)."""
        try:
            data = await request.json()
            text = data.get("text", "")

            if not text:
                return web.json_response({
                    "success": False,
                    "error": "Missing 'text' in request"
                }, status=400)

            # Use orchestrator's TTS directly
            audio = await self.orchestrator.tts.synthesize(text)

            return web.json_response({
                "success": True,
                "audio_base64": audio.hex() if audio else ""
            })

        except Exception as e:
            logger.error("Say handler error: %s", e, exc_info=True)
            return web.json_response({
                "success": False,
                "error": "Errore interno del server"
            }, status=500)

    async def reset_handler(self, request):
        """Reset conversation and start fresh. Accepts optional {'vertical': 'medical'} for testing."""
        try:
            # Check for vertical override (test-only)
            vertical = None
            try:
                body = await request.json()
                vertical = body.get("vertical") if isinstance(body, dict) else None
            except Exception:
                pass

            # Full reset: wipe client identity (explicit /api/voice/reset call)
            self.orchestrator.booking_sm.reset(full_reset=True)
            self.orchestrator.disambiguation.reset()
            self.orchestrator._reset_cancel_reschedule_state()

            # Apply vertical override before starting session
            if vertical:
                self.orchestrator.set_vertical(vertical)

            # Start new session
            result = await self.orchestrator.start_session()
            self._current_session_id = result.session_id

            return web.json_response({
                "success": True,
                "message": "Conversation reset",
                "session_id": result.session_id,
                "vertical": self.orchestrator._faq_vertical
            })
        except Exception as e:
            logger.error("Reset handler error: %s", e, exc_info=True)
            return web.json_response({
                "success": False,
                "error": "Errore interno del server"
            }, status=500)

    async def set_vertical_handler(self, request):
        """Switch business vertical. POST {"vertical": "salone"} or "auto", "medical", etc."""
        try:
            data = await request.json()
            vertical = data.get("vertical", "")
            if not vertical:
                return web.json_response({"success": False, "error": "Missing 'vertical'"}, status=400)

            ok = self.orchestrator.set_vertical(vertical)
            if not ok:
                return web.json_response({"success": False, "error": f"Unknown vertical: {vertical}"}, status=400)

            # Override business name for test verticals
            _TEST_NAMES = {
                "auto": "Officina Demo FLUXION",
                "medical": "Studio Medico Demo FLUXION",
                "medico": "Studio Medico Demo FLUXION",
                "wellness": "Centro Benessere Demo FLUXION",
                "beauty": "Centro Estetico Demo FLUXION",
                "palestra": "Palestra Demo FLUXION",
                "salone": "Salone Demo FLUXION",
            }
            if vertical in _TEST_NAMES:
                self.orchestrator.business_name = _TEST_NAMES[vertical]

            # Reset FSM for clean start with new vertical
            self.orchestrator.booking_sm.reset(full_reset=True)
            self.orchestrator.disambiguation.reset()
            result = await self.orchestrator.start_session()
            self._current_session_id = result.session_id

            return web.json_response({
                "success": True,
                "vertical": vertical,
                "session_id": result.session_id,
                "business": self.orchestrator.business_name
            })
        except Exception as e:
            logger.error("Set-vertical handler error: %s", e, exc_info=True)
            return web.json_response({"success": False, "error": str(e)}, status=500)

    async def status_handler(self, request):
        """Get pipeline status and conversation state."""
        try:
            session = self.orchestrator._current_session
            booking_ctx = self.orchestrator.booking_sm.context

            return web.json_response({
                "success": True,
                "status": "running",
                "pipeline": "enterprise_4layer",
                "session": {
                    "id": session.session_id if session else None,
                    "business": self.orchestrator.business_name,
                    "turn_count": session.total_turns if session else 0
                },
                "booking": {
                    "state": booking_ctx.state.value,
                    "service": booking_ctx.service,
                    "date": booking_ctx.date,
                    "time": booking_ctx.time,
                    "client": booking_ctx.client_id
                }
            })
        except Exception as e:
            logger.error("Status handler error: %s", e, exc_info=True)
            return web.json_response({
                "success": False,
                "error": "Errore interno del server"
            }, status=500)

    async def send_email_handler(self, request):
        """Send supplier order via SMTP email."""
        try:
            data = await request.json()

            # Validate required fields
            required = ['email', 'ordine_numero', 'items', 'importo_totale']
            for field in required:
                if field not in data:
                    return web.json_response({
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }, status=400)

            # Build order data
            order_data = {
                'ordine_numero': data['ordine_numero'],
                'data_ordine': data.get('data_ordine'),
                'data_consegna_prevista': data.get('data_consegna_prevista', 'Da definire'),
                'items': data['items'],
                'importo_totale': data['importo_totale'],
                'notes': data.get('notes', '')
            }

            # Send via SMTP
            email_service = get_email_service()
            success = await email_service.send_order_email(
                supplier_email=data['email'],
                order_data=order_data
            )

            if success:
                return web.json_response({
                    "success": True,
                    "status": "sent",
                    "message": f"Order {data['ordine_numero']} sent to {data['email']}"
                })
            else:
                return web.json_response({
                    "success": False,
                    "error": "SMTP send failed - check email configuration"
                }, status=500)

        except Exception as e:
            logger.error("Send email handler error: %s", e, exc_info=True)
            return web.json_response({
                "success": False,
                "error": "Errore interno del server"
            }, status=500)

    async def wa_send_confirmation_handler(self, request):
        """
        POST /api/voice/whatsapp/send_confirmation
        Gap #4: Invia WA di conferma prenotazione con CTA CONFERMO/CANCELLO/SPOSTO.
        Chiamato da Tauri subito dopo la creazione appuntamento.

        Body JSON: {
            phone: str,
            nome: str,
            servizio: str,
            data: str,           # "DD/MM/YYYY"
            ora: str,            # "HH:MM"
            appointment_id: str,
            operatore?: str,
            nome_attivita?: str
        }
        """
        try:
            data = await request.json()
            phone = data.get("phone", "")
            nome = data.get("nome", "Cliente")
            servizio = data.get("servizio", "")
            data_str = data.get("data", "")
            ora_str = data.get("ora", "")
            appointment_id = data.get("appointment_id", "")
            operatore = data.get("operatore")
            nome_attivita = data.get("nome_attivita")

            if not phone or not servizio or not data_str or not ora_str:
                return web.json_response(
                    {"success": False, "error": "Missing required fields: phone, servizio, data, ora"},
                    status=400
                )

            # Import WhatsApp client + templates
            from src.whatsapp import WhatsAppClient, WhatsAppTemplates
            wa_client = WhatsAppClient()

            if not wa_client.is_connected():
                return web.json_response(
                    {"success": False, "error": "WhatsApp not connected"},
                    status=503
                )

            message = WhatsAppTemplates.booking_confirm_interactive(
                nome=nome,
                servizio=servizio,
                data=data_str,
                ora=ora_str,
                operatore=operatore,
                nome_attivita=nome_attivita,
            )

            result = wa_client.send_message(phone, message)
            success = result.get("success", False)

            if success and appointment_id:
                # Register pending so client reply is attributed correctly
                normalized_phone = wa_client.normalize_phone(phone)
                self.wa_callback.register_pending_appointment(normalized_phone, appointment_id, nome)
                logger.info("[Gap#4] WA confirm sent → %s (apt %s)", nome, appointment_id)

            return web.json_response({"success": success, "result": result})

        except Exception as e:
            logger.error("WA send confirmation handler error: %s", e, exc_info=True)
            return web.json_response({"success": False, "error": "Errore interno del server"}, status=500)

    async def wa_register_pending_handler(self, request):
        """
        POST /api/voice/whatsapp/register_pending
        Gap #4: Registra appuntamento pending senza inviare WA.
        Utile quando il reminder è già stato inviato (es. dal scheduler).

        Body JSON: {phone: str, appointment_id: str, client_name?: str}
        """
        try:
            data = await request.json()
            phone = data.get("phone", "")
            appointment_id = data.get("appointment_id", "")
            client_name = data.get("client_name", "Cliente")

            if not phone or not appointment_id:
                return web.json_response(
                    {"success": False, "error": "Missing phone or appointment_id"},
                    status=400
                )

            from src.whatsapp import WhatsAppClient
            wa_client = WhatsAppClient()
            normalized_phone = wa_client.normalize_phone(phone)
            self.wa_callback.register_pending_appointment(normalized_phone, appointment_id, client_name)

            return web.json_response({"success": True})

        except Exception as e:
            logger.error("WA register pending handler error: %s", e, exc_info=True)
            return web.json_response({"success": False, "error": "Errore interno del server"}, status=500)

    async def latency_metrics_handler(self, request):
        """
        GET /api/metrics/latency
        F03: P50/P95/P99 latency monitoring endpoint.

        Query params:
            hours (int, optional): lookback window in hours (default: 24)

        Returns JSON: {p50_ms, p95_ms, p99_ms, count, hours}
        """
        try:
            from src.analytics import get_logger
            hours = int(request.rel_url.query.get("hours", "24"))
            analytics_logger = get_logger()
            stats = analytics_logger.get_percentile_stats(hours=hours)
            return web.json_response(stats)
        except Exception as e:
            logger.error("Latency metrics handler error: %s", e, exc_info=True)
            return web.json_response({"error": "Errore interno del server"}, status=500)

    # ─────────────────────────────────────────────────────────────────
    # F-SARA-VOICE: TTS hardware + mode handlers
    # ─────────────────────────────────────────────────────────────────

    async def tts_hardware_handler(self, request):
        """Return hardware capability for TTS quality selection."""
        try:
            from src.tts_engine import TTSEngineSelector
            hw = TTSEngineSelector.detect_hardware()
            return web.json_response({
                "success": True,
                "ram_gb": round(hw["ram_gb"], 1),
                "cpu_cores": hw["cpu_cores"],
                "avx2": hw.get("avx2", False),
                "capable": hw["capable"],
                "recommended_mode": "quality" if hw["capable"] else "fast",
                "model_downloaded": TTSDownloadManager.is_model_downloaded(),
            })
        except Exception as e:
            logger.error("TTS hardware handler error: %s", e, exc_info=True)
            return web.json_response({"success": False, "error": "Errore interno del server"}, status=500)

    async def tts_mode_handler(self, request):
        """Return current TTS mode and model status."""
        try:
            return web.json_response({
                "success": True,
                "current_mode": TTSDownloadManager.read_mode(),
                "model_downloaded": TTSDownloadManager.is_model_downloaded(),
                "reference_audio_path": TTSDownloadManager.get_reference_audio_path(),
            })
        except Exception as e:
            logger.error("TTS mode handler error: %s", e, exc_info=True)
            return web.json_response({"success": False, "error": "Errore interno del server"}, status=500)

    async def tts_mode_set_handler(self, request):
        """Persist TTS mode preference."""
        try:
            data = await request.json()
            mode = data.get("mode", "auto")
            if mode not in ("quality", "fast", "auto"):
                return web.json_response(
                    {"success": False, "error": f"Invalid mode: {mode}"},
                    status=400
                )
            TTSDownloadManager.write_mode(mode)
            return web.json_response({"success": True, "mode": mode})
        except Exception as e:
            logger.error("TTS mode set handler error: %s", e, exc_info=True)
            return web.json_response({"success": False, "error": "Errore interno del server"}, status=500)

    # ─────────────────────────────────────────────────────────────────
    # F15: VoIP handlers
    # ─────────────────────────────────────────────────────────────────

    async def voip_status_handler(self, request):
        """GET /api/voice/voip/status — SIP registration state."""
        if self.voip_manager:
            return web.json_response(self.voip_manager.get_status())
        return web.json_response({
            "running": False,
            "sip": {"registered": False},
            "rtp_active": False,
        })

    async def voip_hangup_handler(self, request):
        """POST /api/voice/voip/hangup — End active call."""
        if not self.voip_manager:
            return web.json_response({"success": False, "error": "VoIP not running"}, status=503)
        try:
            ok = await self.voip_manager.hangup()
            return web.json_response({"success": ok})
        except Exception as exc:
            logger.error("VoIP hangup handler error: %s", exc, exc_info=True)
            return web.json_response({"success": False, "error": "Errore interno del server"}, status=500)

    async def waitlist_trigger_handler(self, request):
        """POST /api/waitlist/trigger — Immediate waitlist check after appointment cancellation.

        GAP-P1-7: Called by http_bridge (Tauri) on UI-initiated cancellation to avoid
        waiting up to 5min for the scheduled polling cycle.
        Fire-and-forget: always returns 202 immediately.
        """
        try:
            from src.reminder_scheduler import check_and_notify_waitlist
            asyncio.create_task(check_and_notify_waitlist(self.wa_client))
            return web.json_response({"success": True, "message": "waitlist check triggered"}, status=202)
        except Exception as exc:
            logger.error("Waitlist trigger handler error: %s", exc, exc_info=True)
            return web.json_response({"success": False, "error": "Errore interno del server"}, status=500)

    # ─── F18: Sales Endpoints ─────────────────────────────────────

    MAX_SALES_SESSIONS = 100

    def _get_sales_fsm(self, session_id: str) -> SalesStateMachine:
        """Get or create a SalesStateMachine for a session."""
        if session_id not in self._sales_sessions:
            # H4: Evict oldest session if at capacity to prevent unbounded memory growth
            if len(self._sales_sessions) >= self.MAX_SALES_SESSIONS:
                oldest_key = min(
                    self._sales_sessions,
                    key=lambda k: getattr(self._sales_sessions[k], 'last_access', 0)
                )
                del self._sales_sessions[oldest_key]
                logger.info("[Sales] Evicted oldest session: %s", oldest_key)
            self._sales_sessions[session_id] = SalesStateMachine()
            logger.info("[Sales] New session: %s", session_id)
        return self._sales_sessions[session_id]

    async def sales_process_handler(self, request):
        """POST /api/sales/process — Process sales conversation message.

        Body: {"text": "...", "session_id": "phone_or_id", "lead_name": "optional", "lead_phone": "optional"}
        Returns: {"success": true, "response": "...", "state": "...", "context": {...}, "checkout_url": null}
        """
        try:
            data = await request.json()
            text = data.get("text", "").strip()
            session_id = data.get("session_id", "default")

            if not text:
                return web.json_response({
                    "success": False, "error": "Missing 'text' in request"
                }, status=400)

            fsm = self._get_sales_fsm(session_id)

            # Set lead info if provided (first message)
            if data.get("lead_name") and not fsm.ctx.lead_name:
                fsm.ctx.lead_name = data["lead_name"]
            if data.get("lead_phone") and not fsm.ctx.lead_phone:
                fsm.ctx.lead_phone = data["lead_phone"]

            result = fsm.process(text)

            logger.info("[Sales] session=%s | '%s' → '%s' [state=%s]",
                        session_id, text[:60], result.response[:80], result.state.value)

            return web.json_response({
                "success": True,
                "response": result.response,
                "state": result.state.value,
                "context": result.context,
                "checkout_url": result.checkout_url,
                "followup_wa": result.followup_wa,
                "is_terminal": result.is_terminal,
            })
        except Exception as exc:
            logger.error("[Sales] process error: %s", exc, exc_info=True)
            return web.json_response({
                "success": False, "error": "Errore interno del server"
            }, status=500)

    async def sales_reset_handler(self, request):
        """POST /api/sales/reset — Reset sales session.

        Body: {"session_id": "phone_or_id"}
        """
        try:
            data = await request.json()
            session_id = data.get("session_id", "default")
            if session_id in self._sales_sessions:
                del self._sales_sessions[session_id]
            logger.info("[Sales] Session reset: %s", session_id)
            return web.json_response({"success": True, "message": "Sales session reset"})
        except Exception as exc:
            logger.error("Sales reset handler error: %s", exc, exc_info=True)
            return web.json_response({"success": False, "error": "Errore interno del server"}, status=500)

    async def sales_status_handler(self, request):
        """GET /api/sales/status — Get all active sales sessions."""
        sessions = {}
        for sid, fsm in self._sales_sessions.items():
            sessions[sid] = {
                "state": fsm.state.value,
                "context": fsm.ctx.to_dict(),
            }
        return web.json_response({
            "success": True,
            "active_sessions": len(sessions),
            "sessions": sessions,
        })

    async def start(self):
        """Start HTTP server."""
        # Increase max request size to 50MB for audio uploads (default is 1MB)
        runner = web.AppRunner(self.app, client_max_size=50*1024*1024)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        print(f"🎙️  Voice Agent HTTP server started on http://{self.host}:{self.port}")


async def main(config_path: Optional[str] = None, port: int = 3002, host: str = "127.0.0.1"):
    """Main entry point."""
    # Load environment variables
    load_dotenv()

    # Check for Groq API key
    # Priority: 1) .env / environment, 2) FLUXION DB via HTTP Bridge, 3) offline mode
    groq_api_key = os.environ.get("GROQ_API_KEY")
    _offline_mode = False

    # Load config - priority: 1) file, 2) database, 3) defaults
    config = None
    verticale_id = "default"

    if config_path and Path(config_path).exists():
        with open(config_path) as f:
            config = json.load(f)
            verticale_id = config.get("verticale_id", "default")
            print(f"   Loaded config from file: {config_path}")
    else:
        # Try to load from database (HTTP Bridge)
        print("   Loading business config from database...")
        config = await load_business_config_from_db()

        if config and config.get("business_name"):
            verticale_id = config.get("verticale_id", "default")
            print(f"   Loaded config from database: {config['business_name']}")
            # Leggi groq_api_key dal DB se non già in env
            if not groq_api_key and config.get("groq_api_key"):
                groq_api_key = config["groq_api_key"]
                print("   ✅ Groq API key caricata da FLUXION database (wizard Step 7)")
        else:
            # Fallback to defaults with warning
            config = DEFAULT_CONFIG.copy()
            config["business_name"] = os.environ.get("BUSINESS_NAME", "La tua attivita")
            print("   ⚠️  WARNING: business_name not configured in database!")
            print("   ⚠️  Using environment variable BUSINESS_NAME or placeholder.")
            print("   ⚠️  Configure your business name in FLUXION settings.")

    # Determina modalità in base alla disponibilità della key
    if not groq_api_key:
        print("⚠️  GROQ_API_KEY non configurata — avvio in modalità offline")
        print("   → STT: FasterWhisper locale | LLM L4: non disponibile")
        print("   → Configura la Groq API key in FLUXION: Impostazioni → Voice Agent")
        _offline_mode = True

    print(f"""
╔═══════════════════════════════════════════════════════════════╗
║  🎙️  FLUXION Voice Agent Enterprise v2.1                      ║
╠═══════════════════════════════════════════════════════════════╣
║  Business: {config['business_name']:<47} ║
║  Hours:    {config['opening_hours']} - {config['closing_hours']:<40} ║
║  Listen:   {host}:{port:<43} ║
║  Pipeline: 4-Layer RAG (L0→L1→L2→L3→L4)                       ║
║  VAD:      Silero ONNX / webrtcvad fallback (noise-robust)    ║
╚═══════════════════════════════════════════════════════════════╝
    """)

    # Initialize Groq client — STT: Groq primary (~200ms) + FasterWhisper fallback (lazy)
    # CoVe 2026-02-25: su iMac 2012 Intel i5, FasterWhisper base = RTF 1.17x (4.7s su 4s audio)
    # Groq Whisper large-v3 = ~200ms. Swap primary/fallback = -4500ms latency.
    # Offline mode: prefer_offline_stt=True, api_key=None → FasterWhisper only, no LLM
    groq_client = GroqClient(api_key=groq_api_key, prefer_offline_stt=_offline_mode)
    if _offline_mode:
        print("⚠️  Groq client offline (FasterWhisper only, nessun LLM)")
    else:
        print("✅ Groq client inizializzato (STT: Groq primary + LLM)")

    # Initialize enterprise orchestrator
    # Use SystemTTS (macOS say) as default - Chatterbox/Piper require PyTorch
    orchestrator = VoiceOrchestrator(
        verticale_id=verticale_id,
        business_name=config["business_name"],
        groq_api_key=groq_api_key,
        use_piper_tts=True  # FluxionTTS Adaptive: Edge-TTS quality + Piper/SystemTTS fallback
    )
    tts_info = orchestrator.tts.get_info() if hasattr(orchestrator.tts, 'get_info') else {}
    tts_engine_name = tts_info.get("engine", "unknown")
    print("✅ Enterprise orchestrator inizializzato")
    print("   - STT: Groq primary (~200ms) + FasterWhisper fallback (lazy)")
    print(f"   - TTS: {tts_engine_name} (quality {tts_info.get('quality', '?')}/10) + TTSCache")
    print("   - L0: Special commands (aiuto, operatore, annulla)")
    print("   - L1: Exact match cortesia")
    print("   - L2: Slot filling (booking state machine)")
    print("   - L3: FAQ retrieval")
    print("   - L4: Groq LLM fallback")

    # Pre-warm TTS cache with static templates (eliminates synthesis latency for common phrases)
    from src.booking_state_machine import TEMPLATES as FSM_TEMPLATES
    static_phrases = [v for v in FSM_TEMPLATES.values() if '{' not in v]
    static_phrases += [
        "Buongiorno! Come posso aiutarla?",
        "Buon pomeriggio! Come posso aiutarla?",
        "Buonasera! Come posso aiutarla?",
        "Di nulla! Arrivederci, buona giornata!",
        "Grazie, a presto!",
        "Arrivederci, buona giornata!",
        # F03: Pre-warm L4 fallback phrases (eliminate TTS latency for common fallbacks)
        "Mi scusi, sto impiegando un po' di tempo. Posso aiutarla a prenotare un appuntamento?",
        "Posso aiutarla principalmente con le prenotazioni. Desidera fissare un appuntamento?",
        "Mi scusi, sono momentaneamente sovraccarica. Puo ripetere?",
        "Mi dice il cognome?",
        "Perfetto, le confermo: ",
        "Un momento, verifico la disponibilita.",
    ]
    print(f"⏳ Pre-warming TTS cache ({len(static_phrases)} frasi statiche)...")
    await orchestrator.tts.warm_cache(static_phrases)
    print(f"✅ TTS cache pronta ({len(static_phrases)} frasi → 0ms latency)")

    # F03: Wire FluxionLatencyOptimizer (connection pool + metrics tracking)
    # Non-fatal: if optimizer fails, startup continues without it
    if groq_api_key:
        try:
            from src.latency_optimizer import FluxionLatencyOptimizer
            latency_optimizer = FluxionLatencyOptimizer(groq_api_key=groq_api_key)
            if hasattr(latency_optimizer, 'setup'):
                await latency_optimizer.setup()
            elif hasattr(latency_optimizer, 'initialize'):
                await latency_optimizer.initialize()
            print("✅ Latency optimizer initialized")
        except Exception as e:
            print(f"⚠️  Latency optimizer init failed (non-fatal): {e}")
    else:
        print("⚠️  Latency optimizer skipped (no Groq API key — offline mode)")

    # Start HTTP server (before scheduler so wa_callback is available)
    server = VoiceAgentHTTPServer(orchestrator, groq_client, host=host, port=port)
    await server.start()

    # Gap #2+#4 CoVe 2026: Start reminder scheduler (-24h/-1h automated WA reminders)
    # Gap #4: pass wa_callback so client replies (CONFERMO/CANCELLO/SPOSTO) are attributed.
    # Revenue: -40% no-show = +25% slot fill. Non-fatal: WA unavailable → scheduler logs warning.
    try:
        from src.whatsapp import WhatsAppClient
        wa_client = WhatsAppClient()
        server.wa_client = wa_client  # GAP-P1-7: expose for waitlist_trigger_handler
        reminder_scheduler = start_reminder_scheduler(wa_client, callback_handler=server.wa_callback)
        if reminder_scheduler:
            print("✅ Reminder scheduler avviato (WA -24h/-1h ogni 15min | Gap #4 confirm/cancel attivo)")
        else:
            print("⚠️  Reminder scheduler non avviato (APScheduler non installato)")
    except Exception as e:
        print(f"⚠️  Reminder scheduler init failed (non-fatal): {e}")
        reminder_scheduler = None

    # F15: Start VoIP service if SIP credentials are configured in env
    voip_sip_user = os.getenv("VOIP_SIP_USER", "").strip()
    if voip_sip_user:
        try:
            from src.voip_pjsua2 import VoIPManager, SIPConfig
            voip_config = SIPConfig.from_env()
            voip_manager = VoIPManager(voip_config)
            voip_manager.set_pipeline(orchestrator)
            if await voip_manager.start():
                server.voip_manager = voip_manager
                print(f"✅ VoIP service avviato (SIP: {voip_sip_user}@{voip_config.server})")
            else:
                print(f"⚠️  VoIP service non avviato (SIP registration fallita)")
        except Exception as exc:
            print(f"⚠️  VoIP init non riuscita (non-fatal): {exc}")
    else:
        print("ℹ️  VoIP non configurato (imposta VOIP_SIP_USER in config.env per abilitare)")

    # Keep running
    print("\n🎤 Voice Agent ready. Press Ctrl+C to stop.")
    try:
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        print("\n👋 Voice Agent shutting down...")
        if server.voip_manager:
            await server.voip_manager.stop()
        await close_http_session()


def cli():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="FLUXION Voice Agent Enterprise")
    parser.add_argument("--config", "-c", help="Path to config JSON file")
    parser.add_argument("--port", "-p", type=int, default=3002, help="HTTP port (default: 3002)")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1 — localhost only)")
    parser.add_argument("--test", action="store_true", help="Run integration tests and exit")

    args = parser.parse_args()

    if args.test:
        # Run enterprise integration tests
        import subprocess
        import sys
        test_script = Path(__file__).parent / "test_enterprise_integration.py"
        if test_script.exists():
            result = subprocess.run([sys.executable, str(test_script)])
            sys.exit(result.returncode)
        else:
            print("Test script not found. Run: python test_enterprise_integration.py")
            sys.exit(1)
    else:
        # Start server
        asyncio.run(main(args.config, args.port, args.host))


if __name__ == "__main__":
    cli()
