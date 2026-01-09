"""
FLUXION Voice Agent - SIP Client
Ehiweb VoIP integration for inbound/outbound calls
"""

import os
import asyncio
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
from enum import Enum


class CallDirection(Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class CallState(Enum):
    IDLE = "idle"
    RINGING = "ringing"
    CONNECTED = "connected"
    ENDED = "ended"
    FAILED = "failed"


@dataclass
class SIPConfig:
    """Ehiweb SIP configuration."""
    server: str = "sip.ehiweb.it"
    port: int = 5060
    username: str = ""
    password: str = ""
    transport: str = "udp"
    codecs: tuple = ("PCMA", "PCMU")  # G.711
    register: bool = True
    register_interval: int = 300

    @classmethod
    def from_env(cls) -> "SIPConfig":
        """Load configuration from environment variables."""
        return cls(
            server=os.getenv("VOIP_SIP_SERVER", "sip.ehiweb.it"),
            port=int(os.getenv("VOIP_SIP_PORT", "5060")),
            username=os.getenv("VOIP_SIP_USER", ""),
            password=os.getenv("VOIP_SIP_PASSWORD", ""),
        )


@dataclass
class CallInfo:
    """Active call information."""
    call_id: str
    direction: CallDirection
    remote_number: str
    state: CallState
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    duration_seconds: int = 0


class SIPClient:
    """
    SIP Client for Ehiweb VoIP.

    Handles SIP registration, inbound/outbound calls,
    and audio stream management.
    """

    def __init__(self, config: Optional[SIPConfig] = None):
        self.config = config or SIPConfig.from_env()
        self.registered = False
        self.active_call: Optional[CallInfo] = None

        # Callbacks
        self.on_incoming_call: Optional[Callable[[CallInfo], None]] = None
        self.on_call_connected: Optional[Callable[[CallInfo], None]] = None
        self.on_call_ended: Optional[Callable[[CallInfo], None]] = None
        self.on_audio_received: Optional[Callable[[bytes], None]] = None

    async def register(self) -> bool:
        """
        Register with SIP server.

        Returns:
            True if registration successful
        """
        if not self.config.username or not self.config.password:
            print("⚠️  SIP credentials not configured")
            return False

        print(f"📞 Registering with {self.config.server}...")
        print(f"   User: {self.config.username}")

        # Note: Full SIP implementation requires pjsua2 or similar
        # This is a placeholder for the actual SIP stack
        # For production, use: pipecat-ai[sip] or pjsip

        try:
            # Simulated registration for now
            # Real implementation would use pjsua2 or aiortc
            await asyncio.sleep(0.5)
            self.registered = True
            print("✅ SIP registration successful")
            return True
        except Exception as e:
            print(f"❌ SIP registration failed: {e}")
            self.registered = False
            return False

    async def unregister(self) -> bool:
        """Unregister from SIP server."""
        if self.registered:
            self.registered = False
            print("📞 SIP unregistered")
        return True

    async def make_call(self, number: str) -> Optional[CallInfo]:
        """
        Initiate outbound call.

        Args:
            number: Phone number to call (e.g., "+393281234567")

        Returns:
            CallInfo if call initiated, None on failure
        """
        if not self.registered:
            print("❌ Not registered with SIP server")
            return None

        if self.active_call:
            print("❌ Already in a call")
            return None

        import time
        call_id = f"call_{int(time.time())}"

        self.active_call = CallInfo(
            call_id=call_id,
            direction=CallDirection.OUTBOUND,
            remote_number=number,
            state=CallState.RINGING,
            start_time=time.time()
        )

        print(f"📞 Calling {number}...")

        # In production, this would use the SIP stack to initiate call
        # For now, we simulate the call states

        return self.active_call

    async def answer_call(self) -> bool:
        """Answer incoming call."""
        if not self.active_call or self.active_call.state != CallState.RINGING:
            return False

        self.active_call.state = CallState.CONNECTED
        import time
        self.active_call.start_time = time.time()

        if self.on_call_connected:
            self.on_call_connected(self.active_call)

        print("✅ Call answered")
        return True

    async def hangup(self) -> bool:
        """End current call."""
        if not self.active_call:
            return False

        import time
        self.active_call.state = CallState.ENDED
        self.active_call.end_time = time.time()

        if self.active_call.start_time:
            self.active_call.duration_seconds = int(
                self.active_call.end_time - self.active_call.start_time
            )

        if self.on_call_ended:
            self.on_call_ended(self.active_call)

        call_info = self.active_call
        self.active_call = None

        print(f"📞 Call ended (duration: {call_info.duration_seconds}s)")
        return True

    async def send_audio(self, audio_data: bytes) -> bool:
        """
        Send audio to remote party.

        Args:
            audio_data: PCM audio data (16-bit, 16kHz)

        Returns:
            True if sent successfully
        """
        if not self.active_call or self.active_call.state != CallState.CONNECTED:
            return False

        # In production, this would encode and send via RTP
        # Audio format: PCM 16-bit, 16kHz, mono
        return True

    def get_status(self) -> Dict[str, Any]:
        """Get current SIP client status."""
        return {
            "registered": self.registered,
            "server": self.config.server,
            "username": self.config.username,
            "active_call": {
                "call_id": self.active_call.call_id,
                "direction": self.active_call.direction.value,
                "remote_number": self.active_call.remote_number,
                "state": self.active_call.state.value,
                "duration": self.active_call.duration_seconds,
            } if self.active_call else None
        }


class VoIPManager:
    """
    High-level VoIP manager for FLUXION.

    Integrates SIP client with voice pipeline.
    """

    def __init__(self, pipeline=None):
        self.sip = SIPClient()
        self.pipeline = pipeline
        self.running = False

    async def start(self) -> bool:
        """Start VoIP service."""
        if self.running:
            return True

        # Register with SIP server
        if not await self.sip.register():
            return False

        # Set up callbacks
        self.sip.on_incoming_call = self._on_incoming_call
        self.sip.on_call_connected = self._on_call_connected
        self.sip.on_call_ended = self._on_call_ended
        self.sip.on_audio_received = self._on_audio_received

        self.running = True
        print("🎙️ VoIP service started")
        return True

    async def stop(self) -> bool:
        """Stop VoIP service."""
        if not self.running:
            return True

        # Hang up active call
        if self.sip.active_call:
            await self.sip.hangup()

        # Unregister
        await self.sip.unregister()

        self.running = False
        print("🛑 VoIP service stopped")
        return True

    def _on_incoming_call(self, call: CallInfo):
        """Handle incoming call."""
        print(f"📞 Incoming call from {call.remote_number}")
        # Auto-answer after greeting
        asyncio.create_task(self._handle_incoming_call(call))

    async def _handle_incoming_call(self, call: CallInfo):
        """Process incoming call with voice pipeline."""
        # Answer call
        await self.sip.answer_call()

        # Play greeting
        if self.pipeline:
            greeting = await self.pipeline.greet()
            if greeting.get("audio_response"):
                await self.sip.send_audio(greeting["audio_response"])

    def _on_call_connected(self, call: CallInfo):
        """Handle call connected."""
        print(f"✅ Call connected: {call.call_id}")

    def _on_call_ended(self, call: CallInfo):
        """Handle call ended."""
        print(f"📞 Call ended: {call.call_id} ({call.duration_seconds}s)")

    def _on_audio_received(self, audio_data: bytes):
        """Handle received audio - send to STT."""
        if self.pipeline:
            asyncio.create_task(self._process_audio(audio_data))

    async def _process_audio(self, audio_data: bytes):
        """Process received audio through pipeline."""
        if self.pipeline:
            result = await self.pipeline.process_audio(audio_data)
            # Send response audio back
            if result.get("audio_response"):
                await self.sip.send_audio(result["audio_response"])

    async def make_call(self, number: str) -> Optional[CallInfo]:
        """Make outbound call."""
        if not self.running:
            print("❌ VoIP service not running")
            return None

        call = await self.sip.make_call(number)
        if call:
            # Play greeting when call connects
            asyncio.create_task(self._wait_and_greet(call))
        return call

    async def _wait_and_greet(self, call: CallInfo):
        """Wait for call to connect, then greet."""
        # Wait for connection (simulated)
        await asyncio.sleep(2)

        if self.sip.active_call and self.sip.active_call.state == CallState.RINGING:
            self.sip.active_call.state = CallState.CONNECTED
            if self.on_call_connected:
                self._on_call_connected(self.sip.active_call)

            # Play greeting
            if self.pipeline:
                greeting = await self.pipeline.greet()
                if greeting.get("audio_response"):
                    await self.sip.send_audio(greeting["audio_response"])

    def get_status(self) -> Dict[str, Any]:
        """Get VoIP manager status."""
        return {
            "running": self.running,
            "sip": self.sip.get_status()
        }


# Test
async def test_sip():
    """Test SIP client."""
    from dotenv import load_dotenv
    load_dotenv()

    config = SIPConfig.from_env()
    print(f"SIP Config: {config.server}:{config.port}")
    print(f"Username: {config.username}")

    client = SIPClient(config)

    # Test registration
    registered = await client.register()
    print(f"Registered: {registered}")

    # Test status
    status = client.get_status()
    print(f"Status: {status}")

    # Cleanup
    await client.unregister()


if __name__ == "__main__":
    asyncio.run(test_sip())
