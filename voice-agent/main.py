#!/usr/bin/env python3
"""
FLUXION Voice Agent - Main Entry Point
Starts the voice pipeline server for Tauri integration
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

from src.pipeline import VoicePipeline, VoiceAgentServer
from src.groq_client import GroqClient
from src.tts import get_tts


# Default configuration
DEFAULT_CONFIG = {
    "business_name": "FLUXION Demo",
    "opening_hours": "09:00",
    "closing_hours": "19:00",
    "working_days": "Lunedi-Sabato",
    "services": ["Taglio", "Piega", "Colore", "Trattamenti"]
}


class VoiceAgentHTTPServer:
    """HTTP Server for Tauri integration."""

    def __init__(self, pipeline: VoicePipeline, host: str = "127.0.0.1", port: int = 3002):
        self.pipeline = pipeline
        self.host = host
        self.port = port
        self.app = web.Application()
        self._setup_routes()

    def _setup_routes(self):
        """Setup HTTP routes."""
        self.app.router.add_get("/health", self.health_handler)
        self.app.router.add_post("/api/voice/greet", self.greet_handler)
        self.app.router.add_post("/api/voice/process", self.process_handler)
        self.app.router.add_post("/api/voice/say", self.say_handler)
        self.app.router.add_post("/api/voice/reset", self.reset_handler)
        self.app.router.add_get("/api/voice/status", self.status_handler)

    async def health_handler(self, request):
        """Health check endpoint."""
        return web.json_response({
            "status": "ok",
            "service": "FLUXION Voice Agent",
            "version": "0.1.0"
        })

    async def greet_handler(self, request):
        """Generate greeting."""
        try:
            result = await self.pipeline.greet()
            return web.json_response({
                "success": True,
                "response": result["response"],
                "audio_base64": result["audio_response"].hex()
            })
        except Exception as e:
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    async def process_handler(self, request):
        """Process voice/text input."""
        try:
            data = await request.json()

            if "audio_hex" in data:
                # Process audio
                audio_data = bytes.fromhex(data["audio_hex"])
                result = await self.pipeline.process_audio(audio_data)
            elif "text" in data:
                # Process text
                result = await self.pipeline.process_text(data["text"])
            else:
                return web.json_response({
                    "success": False,
                    "error": "Missing 'audio_hex' or 'text' in request"
                }, status=400)

            return web.json_response({
                "success": True,
                "transcription": result["transcription"],
                "response": result["response"],
                "intent": result["intent"],
                "audio_base64": result["audio_response"].hex(),
                "booking_action": result.get("booking_action")
            })

        except Exception as e:
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    async def say_handler(self, request):
        """Text-to-speech only."""
        try:
            data = await request.json()
            text = data.get("text", "")

            if not text:
                return web.json_response({
                    "success": False,
                    "error": "Missing 'text' in request"
                }, status=400)

            audio = await self.pipeline.say(text)

            return web.json_response({
                "success": True,
                "audio_base64": audio.hex()
            })

        except Exception as e:
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    async def reset_handler(self, request):
        """Reset conversation."""
        self.pipeline.reset_conversation()
        return web.json_response({
            "success": True,
            "message": "Conversation reset"
        })

    async def status_handler(self, request):
        """Get pipeline status."""
        summary = self.pipeline.get_conversation_summary()
        return web.json_response({
            "success": True,
            "status": "running",
            "conversation": summary
        })

    async def start(self):
        """Start HTTP server."""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        print(f"🎙️  Voice Agent HTTP server started on http://{self.host}:{self.port}")


async def main(config_path: Optional[str] = None, port: int = 3002):
    """Main entry point."""
    # Load environment variables
    load_dotenv()

    # Check for Groq API key
    if not os.environ.get("GROQ_API_KEY"):
        print("Error: GROQ_API_KEY not set")
        print("Set it in .env file or environment")
        sys.exit(1)

    # Load config
    if config_path and Path(config_path).exists():
        with open(config_path) as f:
            config = json.load(f)
    else:
        config = DEFAULT_CONFIG
        print("Using default configuration")

    print(f"""
╔════════════════════════════════════════════════════════╗
║  🎙️  FLUXION Voice Agent Starting                      ║
╠════════════════════════════════════════════════════════╣
║  Business: {config['business_name']:<42} ║
║  Hours:    {config['opening_hours']} - {config['closing_hours']:<35} ║
║  Port:     {port:<42} ║
╚════════════════════════════════════════════════════════╝
    """)

    # Initialize pipeline
    try:
        pipeline = VoicePipeline(config, use_piper=True)
        print("✅ Voice pipeline initialized")
    except Exception as e:
        print(f"⚠️  Voice pipeline init warning: {e}")
        print("   Continuing with fallback TTS...")
        pipeline = VoicePipeline(config, use_piper=False)

    # Start HTTP server
    server = VoiceAgentHTTPServer(pipeline, port=port)
    await server.start()

    # Keep running
    print("\nVoice Agent ready. Press Ctrl+C to stop.")
    try:
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        print("\n👋 Voice Agent shutting down...")


def cli():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="FLUXION Voice Agent")
    parser.add_argument("--config", "-c", help="Path to config JSON file")
    parser.add_argument("--port", "-p", type=int, default=3002, help="HTTP port (default: 3002)")
    parser.add_argument("--test", action="store_true", help="Run tests and exit")

    args = parser.parse_args()

    if args.test:
        # Run tests
        from src.pipeline import test_pipeline
        asyncio.run(test_pipeline())
    else:
        # Start server
        asyncio.run(main(args.config, args.port))


if __name__ == "__main__":
    cli()
