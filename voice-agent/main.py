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
import json
import asyncio
import argparse
from pathlib import Path
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
from aiohttp import web

# Load environment variables from .env file
load_dotenv()

# CORS middleware for browser-based E2E testing
@web.middleware
async def cors_middleware(request, handler):
    """Add CORS headers for browser-based testing (Playwright E2E)."""
    # Handle preflight OPTIONS request
    if request.method == "OPTIONS":
        response = web.Response()
    else:
        response = await handler(request)

    # Add CORS headers
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

# Use enterprise orchestrator instead of old pipeline
from src.orchestrator import VoiceOrchestrator
from src.groq_client import GroqClient
from src.tts import get_tts
from src.stt import get_stt_engine
from src.supplier_email_service import get_email_service
from src.vad_http_handler import VADHTTPHandler, add_wav_header


# Default configuration (loaded from database at runtime)
# business_name will be fetched from verticale config via HTTP Bridge
DEFAULT_CONFIG = {
    "business_name": None,  # Will be loaded from DB - MUST be configured!
    "opening_hours": "09:00",
    "closing_hours": "19:00",
    "working_days": "Lunedi-Sabato",
    "services": ["Taglio", "Piega", "Colore", "Trattamenti"]
}


def _load_business_name_from_sqlite() -> Optional[str]:
    """
    Read nome_attivita directly from Fluxion SQLite DB.
    Used as fallback when Tauri HTTP Bridge (port 3001) is offline.
    """
    import sqlite3
    home = Path.home()
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
                conn = sqlite3.connect(str(path), timeout=3)
                row = conn.execute(
                    "SELECT valore FROM impostazioni WHERE chiave = 'nome_attivita' LIMIT 1"
                ).fetchone()
                conn.close()
                if row and row[0]:
                    print(f"   ✅ nome_attivita da SQLite: '{row[0]}' ({path})")
                    return row[0]
            except Exception as e:
                print(f"   SQLite fallback error ({path}): {e}")
    return None


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
                        "opening_hours": data.get("orario_apertura", "09:00"),
                        "closing_hours": data.get("orario_chiusura", "19:00"),
                        "working_days": data.get("giorni_lavorativi", "Lunedi-Sabato"),
                        "services": data.get("servizi", ["Taglio", "Piega", "Colore"])
                    }
    except Exception:
        pass

    # Fallback: read directly from SQLite (Tauri offline = standalone mode)
    nome = _load_business_name_from_sqlite()
    if nome:
        return {
            "business_name": nome,
            "opening_hours": "09:00",
            "closing_hours": "19:00",
            "working_days": "Lunedi-Sabato",
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
        host: str = "0.0.0.0",
        port: int = 3002
    ):
        self.orchestrator = orchestrator
        self.groq = groq_client
        self.host = host
        self.port = port
        self.app = web.Application(middlewares=[cors_middleware])
        self._current_session_id: Optional[str] = None

        # Initialize VAD handler
        self.vad_handler = VADHTTPHandler(orchestrator, groq_client)

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
                "tts": "system"
            }
        })

    async def greet_handler(self, request):
        """Generate greeting and start new session."""
        try:
            result = await self.orchestrator.start_session()
            self._current_session_id = result.session_id

            return web.json_response({
                "success": True,
                "response": result.response,
                "audio_base64": result.audio_bytes.hex() if result.audio_bytes else "",
                "session_id": result.session_id,
                "intent": result.intent,
                "layer": result.layer.value
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    async def process_handler(self, request):
        """Process voice/text input through 4-layer pipeline."""
        try:
            data = await request.json()
            transcription = None

            if "audio_hex" in data:
                # STT: Transcribe audio first
                audio_data = bytes.fromhex(data["audio_hex"])
                # Add WAV header only if data is raw PCM (not already WAV)
                wav_data = audio_data if audio_data[:4] == b'RIFF' else add_wav_header(audio_data)
                transcription = await self.groq.transcribe_audio(wav_data)
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
            import traceback
            traceback.print_exc()
            return web.json_response({
                "success": False,
                "error": str(e)
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
            import traceback
            traceback.print_exc()
            return web.json_response({
                "success": False,
                "error": str(e)
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

            # Reset state machines
            self.orchestrator.booking_sm.reset()
            self.orchestrator.disambiguation.reset()

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
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

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
            return web.json_response({
                "success": False,
                "error": str(e)
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
            import traceback
            traceback.print_exc()
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    async def start(self):
        """Start HTTP server."""
        # Increase max request size to 50MB for audio uploads (default is 1MB)
        runner = web.AppRunner(self.app, client_max_size=50*1024*1024)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        print(f"🎙️  Voice Agent HTTP server started on http://{self.host}:{self.port}")


async def main(config_path: Optional[str] = None, port: int = 3002):
    """Main entry point."""
    # Load environment variables
    load_dotenv()

    # Check for Groq API key
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        print("Error: GROQ_API_KEY not set")
        print("Set it in .env file or environment")
        sys.exit(1)

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
        else:
            # Fallback to defaults with warning
            config = DEFAULT_CONFIG.copy()
            config["business_name"] = os.environ.get("BUSINESS_NAME", "La tua attivita")
            print("   ⚠️  WARNING: business_name not configured in database!")
            print("   ⚠️  Using environment variable BUSINESS_NAME or placeholder.")
            print("   ⚠️  Configure your business name in FLUXION settings.")

    print(f"""
╔═══════════════════════════════════════════════════════════════╗
║  🎙️  FLUXION Voice Agent Enterprise v2.1                      ║
╠═══════════════════════════════════════════════════════════════╣
║  Business: {config['business_name']:<47} ║
║  Hours:    {config['opening_hours']} - {config['closing_hours']:<40} ║
║  Port:     {port:<47} ║
║  Pipeline: 4-Layer RAG (L0→L1→L2→L3→L4)                       ║
║  VAD:      Silero ONNX / webrtcvad fallback (noise-robust)    ║
╚═══════════════════════════════════════════════════════════════╝
    """)

    # Pre-warm STT engine (loads model into RAM — avoids 7s delay on first request)
    print("⏳ Loading STT model (one-time, ~8s)...")
    stt_engine = get_stt_engine(prefer_offline=True)
    stt_name = type(stt_engine.primary).__name__ if hasattr(stt_engine, 'primary') else type(stt_engine).__name__
    # Trigger lazy model load for FasterWhisperSTT
    if hasattr(stt_engine, 'primary') and hasattr(stt_engine.primary, '_get_model'):
        stt_engine.primary._get_model()
    print(f"✅ STT engine ready: {stt_name}")

    # Initialize Groq client for STT
    groq_client = GroqClient(api_key=groq_api_key)
    print("✅ Groq client initialized (LLM)")

    # Initialize enterprise orchestrator
    # Use SystemTTS (macOS say) as default - Chatterbox/Piper require PyTorch
    orchestrator = VoiceOrchestrator(
        verticale_id=verticale_id,
        business_name=config["business_name"],
        groq_api_key=groq_api_key,
        use_piper_tts=False  # Force SystemTTS - works without PyTorch
    )
    print("✅ Enterprise orchestrator initialized")
    print("   - TTS: SystemTTS (macOS say)")
    print("   - L0: Special commands (aiuto, operatore, annulla)")
    print("   - L1: Exact match cortesia")
    print("   - L2: Slot filling (booking state machine)")
    print("   - L3: FAQ retrieval")
    print("   - L4: Groq LLM fallback")

    # Start HTTP server
    server = VoiceAgentHTTPServer(orchestrator, groq_client, port=port)
    await server.start()

    # Keep running
    print("\n🎤 Voice Agent ready. Press Ctrl+C to stop.")
    try:
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        print("\n👋 Voice Agent shutting down...")


def cli():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="FLUXION Voice Agent Enterprise")
    parser.add_argument("--config", "-c", help="Path to config JSON file")
    parser.add_argument("--port", "-p", type=int, default=3002, help="HTTP port (default: 3002)")
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
        asyncio.run(main(args.config, args.port))


if __name__ == "__main__":
    cli()
