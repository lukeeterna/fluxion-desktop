"""
FLUXION Voice Agent - VoIP Module (Week 4)

Real SIP/RTP implementation for Ehiweb VoIP integration.
Handles SIP registration, call management, and audio streaming.
"""

import asyncio
import hashlib
import logging
import os
import socket
import struct
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class SIPConfig:
    """Ehiweb SIP configuration."""
    server: str = "sip.ehiweb.it"
    port: int = 5060
    username: str = ""
    password: str = ""
    transport: str = "udp"
    codecs: Tuple[str, ...] = ("PCMU", "PCMA")  # G.711 mu-law, A-law
    local_ip: str = ""
    local_port: int = 5060
    rtp_port_start: int = 10000
    rtp_port_end: int = 10100
    register_interval: int = 300
    user_agent: str = "FLUXION-VoiceAgent/1.0"

    @classmethod
    def from_env(cls) -> "SIPConfig":
        """Load configuration from environment variables."""
        return cls(
            server=os.getenv("VOIP_SIP_SERVER", "sip.ehiweb.it"),
            port=int(os.getenv("VOIP_SIP_PORT", "5060")),
            username=os.getenv("VOIP_SIP_USER", ""),
            password=os.getenv("VOIP_SIP_PASSWORD", ""),
            local_ip=os.getenv("VOIP_LOCAL_IP", ""),
        )


# =============================================================================
# Call State Management
# =============================================================================

class CallState(Enum):
    """SIP call states."""
    IDLE = "idle"
    REGISTERING = "registering"
    REGISTERED = "registered"
    INVITING = "inviting"
    RINGING = "ringing"
    CONNECTED = "connected"
    HOLDING = "holding"
    ENDING = "ending"
    ENDED = "ended"
    FAILED = "failed"


class CallDirection(Enum):
    """Call direction."""
    INBOUND = "inbound"
    OUTBOUND = "outbound"


@dataclass
class CallSession:
    """Active call session information."""
    call_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    direction: CallDirection = CallDirection.INBOUND
    remote_uri: str = ""
    remote_number: str = ""
    local_tag: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    remote_tag: str = ""
    state: CallState = CallState.IDLE
    cseq: int = 1

    # Timing
    start_time: Optional[float] = None
    connect_time: Optional[float] = None
    end_time: Optional[float] = None

    # RTP
    local_rtp_port: int = 0
    remote_rtp_ip: str = ""
    remote_rtp_port: int = 0

    # SDP
    local_sdp: str = ""
    remote_sdp: str = ""

    @property
    def duration_seconds(self) -> int:
        """Get call duration in seconds."""
        if self.connect_time and self.end_time:
            return int(self.end_time - self.connect_time)
        elif self.connect_time:
            return int(time.time() - self.connect_time)
        return 0


# =============================================================================
# SIP Protocol Implementation
# =============================================================================

class SIPMessage:
    """SIP message parser and builder."""

    def __init__(self):
        self.method: str = ""
        self.uri: str = ""
        self.version: str = "SIP/2.0"
        self.status_code: int = 0
        self.reason_phrase: str = ""
        self.headers: Dict[str, str] = {}
        self.body: str = ""
        self.is_request: bool = True

    @classmethod
    def parse(cls, data: bytes) -> "SIPMessage":
        """Parse SIP message from bytes."""
        msg = cls()
        text = data.decode('utf-8', errors='replace')
        lines = text.split('\r\n')

        if not lines:
            return msg

        # Parse first line (request-line or status-line)
        first_line = lines[0]
        if first_line.startswith('SIP/'):
            # Response: SIP/2.0 200 OK
            msg.is_request = False
            parts = first_line.split(' ', 2)
            msg.version = parts[0]
            msg.status_code = int(parts[1]) if len(parts) > 1 else 0
            msg.reason_phrase = parts[2] if len(parts) > 2 else ""
        else:
            # Request: INVITE sip:user@host SIP/2.0
            msg.is_request = True
            parts = first_line.split(' ')
            msg.method = parts[0]
            msg.uri = parts[1] if len(parts) > 1 else ""
            msg.version = parts[2] if len(parts) > 2 else "SIP/2.0"

        # Parse headers
        body_start = -1
        for i, line in enumerate(lines[1:], 1):
            if line == '':
                body_start = i + 1
                break
            if ':' in line:
                key, value = line.split(':', 1)
                msg.headers[key.strip()] = value.strip()

        # Parse body
        if body_start > 0 and body_start < len(lines):
            msg.body = '\r\n'.join(lines[body_start:])

        return msg

    def build(self) -> bytes:
        """Build SIP message to bytes."""
        lines = []

        if self.is_request:
            lines.append(f"{self.method} {self.uri} {self.version}")
        else:
            lines.append(f"{self.version} {self.status_code} {self.reason_phrase}")

        for key, value in self.headers.items():
            lines.append(f"{key}: {value}")

        if self.body:
            lines.append(f"Content-Length: {len(self.body)}")
        else:
            lines.append("Content-Length: 0")

        lines.append('')
        if self.body:
            lines.append(self.body)

        return '\r\n'.join(lines).encode('utf-8')


class SIPClient:
    """
    SIP Client for Ehiweb VoIP.

    Implements SIP REGISTER, INVITE, BYE methods.
    Uses UDP transport as per Ehiweb configuration.
    """

    def __init__(self, config: Optional[SIPConfig] = None):
        self.config = config or SIPConfig.from_env()
        self._socket: Optional[socket.socket] = None
        self._registered = False
        self._register_task: Optional[asyncio.Task] = None
        self._receive_task: Optional[asyncio.Task] = None
        self._running = False

        # Registration state
        self._cseq = 1
        self._call_id = str(uuid.uuid4())
        self._local_tag = uuid.uuid4().hex[:8]
        self._realm = ""
        self._nonce = ""

        # Active call
        self.active_call: Optional[CallSession] = None

        # Callbacks
        self.on_incoming_call: Optional[Callable[[CallSession], None]] = None
        self.on_call_connected: Optional[Callable[[CallSession], None]] = None
        self.on_call_ended: Optional[Callable[[CallSession], None]] = None
        self.on_audio_frame: Optional[Callable[[bytes, int], None]] = None

    def _get_local_ip(self) -> str:
        """Get local IP address for SIP."""
        if self.config.local_ip:
            return self.config.local_ip

        # Auto-detect local IP
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect((self.config.server, self.config.port))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return "127.0.0.1"

    def _create_socket(self):
        """Create UDP socket for SIP."""
        if self._socket:
            return

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.setblocking(False)

        local_ip = self._get_local_ip()
        self._socket.bind((local_ip, self.config.local_port))
        logger.info(f"SIP socket bound to {local_ip}:{self.config.local_port}")

    def _build_via_header(self) -> str:
        """Build Via header."""
        local_ip = self._get_local_ip()
        branch = f"z9hG4bK{uuid.uuid4().hex[:16]}"
        return f"SIP/2.0/UDP {local_ip}:{self.config.local_port};branch={branch};rport"

    def _build_contact_header(self) -> str:
        """Build Contact header."""
        local_ip = self._get_local_ip()
        return f"<sip:{self.config.username}@{local_ip}:{self.config.local_port}>"

    def _compute_digest_response(self, method: str, uri: str) -> str:
        """Compute MD5 digest for authentication."""
        # HA1 = MD5(username:realm:password)
        ha1 = hashlib.md5(
            f"{self.config.username}:{self._realm}:{self.config.password}".encode()
        ).hexdigest()

        # HA2 = MD5(method:uri)
        ha2 = hashlib.md5(f"{method}:{uri}".encode()).hexdigest()

        # Response = MD5(HA1:nonce:HA2)
        response = hashlib.md5(f"{ha1}:{self._nonce}:{ha2}".encode()).hexdigest()

        return response

    def _build_auth_header(self, method: str, uri: str) -> str:
        """Build Authorization header for digest auth."""
        response = self._compute_digest_response(method, uri)
        return (
            f'Digest username="{self.config.username}", '
            f'realm="{self._realm}", '
            f'nonce="{self._nonce}", '
            f'uri="{uri}", '
            f'response="{response}", '
            f'algorithm=MD5'
        )

    async def _send_message(self, msg: SIPMessage):
        """Send SIP message via UDP."""
        if not self._socket:
            return

        data = msg.build()
        loop = asyncio.get_event_loop()
        await loop.sock_sendto(self._socket, data, (self.config.server, self.config.port))

        if msg.is_request:
            logger.debug(f"SIP >> {msg.method} {msg.uri}")
        else:
            logger.debug(f"SIP >> {msg.status_code} {msg.reason_phrase}")

    async def _receive_loop(self):
        """Receive SIP messages."""
        loop = asyncio.get_event_loop()

        while self._running:
            try:
                data, addr = await loop.sock_recvfrom(self._socket, 4096)
                msg = SIPMessage.parse(data)
                await self._handle_message(msg, addr)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"SIP receive error: {e}")
                await asyncio.sleep(0.1)

    async def _handle_message(self, msg: SIPMessage, addr: Tuple[str, int]):
        """Handle received SIP message."""
        if msg.is_request:
            logger.debug(f"SIP << {msg.method} from {addr}")
            await self._handle_request(msg, addr)
        else:
            logger.debug(f"SIP << {msg.status_code} {msg.reason_phrase}")
            await self._handle_response(msg)

    async def _handle_request(self, msg: SIPMessage, addr: Tuple[str, int]):
        """Handle incoming SIP request."""
        if msg.method == "INVITE":
            await self._handle_invite(msg, addr)
        elif msg.method == "BYE":
            await self._handle_bye(msg, addr)
        elif msg.method == "ACK":
            pass  # ACK doesn't need response
        elif msg.method == "CANCEL":
            await self._handle_cancel(msg, addr)
        elif msg.method == "OPTIONS":
            await self._send_options_response(msg, addr)

    async def _handle_response(self, msg: SIPMessage):
        """Handle SIP response."""
        cseq = msg.headers.get("CSeq", "")

        if "REGISTER" in cseq:
            await self._handle_register_response(msg)
        elif "INVITE" in cseq:
            await self._handle_invite_response(msg)
        elif "BYE" in cseq:
            await self._handle_bye_response(msg)

    async def _handle_register_response(self, msg: SIPMessage):
        """Handle REGISTER response."""
        if msg.status_code == 200:
            self._registered = True
            logger.info("SIP registration successful")
        elif msg.status_code == 401:
            # WWW-Authenticate challenge
            auth = msg.headers.get("WWW-Authenticate", "")
            if 'realm="' in auth:
                self._realm = auth.split('realm="')[1].split('"')[0]
            if 'nonce="' in auth:
                self._nonce = auth.split('nonce="')[1].split('"')[0]

            # Retry with authentication
            await self._send_register(with_auth=True)
        else:
            logger.error(f"Registration failed: {msg.status_code} {msg.reason_phrase}")
            self._registered = False

    async def _send_register(self, with_auth: bool = False):
        """Send REGISTER request."""
        self._cseq += 1
        uri = f"sip:{self.config.server}"

        msg = SIPMessage()
        msg.is_request = True
        msg.method = "REGISTER"
        msg.uri = uri

        msg.headers = {
            "Via": self._build_via_header(),
            "Max-Forwards": "70",
            "From": f"<sip:{self.config.username}@{self.config.server}>;tag={self._local_tag}",
            "To": f"<sip:{self.config.username}@{self.config.server}>",
            "Call-ID": self._call_id,
            "CSeq": f"{self._cseq} REGISTER",
            "Contact": self._build_contact_header(),
            "Expires": str(self.config.register_interval),
            "User-Agent": self.config.user_agent,
        }

        if with_auth and self._nonce:
            msg.headers["Authorization"] = self._build_auth_header("REGISTER", uri)

        await self._send_message(msg)

    async def _handle_invite(self, msg: SIPMessage, addr: Tuple[str, int]):
        """Handle incoming INVITE (inbound call)."""
        # Parse From header to get caller number
        from_header = msg.headers.get("From", "")
        remote_number = ""
        if "<sip:" in from_header:
            remote_number = from_header.split("<sip:")[1].split("@")[0]

        # Extract remote tag
        remote_tag = ""
        if ";tag=" in from_header:
            remote_tag = from_header.split(";tag=")[1].split(">")[0]

        # Create call session
        self.active_call = CallSession(
            call_id=msg.headers.get("Call-ID", str(uuid.uuid4())),
            direction=CallDirection.INBOUND,
            remote_uri=msg.uri,
            remote_number=remote_number,
            remote_tag=remote_tag,
            state=CallState.RINGING,
            start_time=time.time(),
        )

        # Parse SDP for RTP info
        if msg.body:
            self.active_call.remote_sdp = msg.body
            self._parse_sdp(msg.body)

        # Send 180 Ringing
        await self._send_response(msg, 180, "Ringing")

        logger.info(f"Incoming call from {remote_number}")

        # Notify callback
        if self.on_incoming_call:
            self.on_incoming_call(self.active_call)

    async def _send_response(self, request: SIPMessage, code: int, reason: str, sdp: str = ""):
        """Send SIP response."""
        msg = SIPMessage()
        msg.is_request = False
        msg.status_code = code
        msg.reason_phrase = reason

        msg.headers = {
            "Via": request.headers.get("Via", ""),
            "From": request.headers.get("From", ""),
            "To": request.headers.get("To", ""),
            "Call-ID": request.headers.get("Call-ID", ""),
            "CSeq": request.headers.get("CSeq", ""),
            "User-Agent": self.config.user_agent,
        }

        # Add tag to To header if not present
        if self.active_call and ";tag=" not in msg.headers["To"]:
            msg.headers["To"] = f'{msg.headers["To"]};tag={self.active_call.local_tag}'

        if sdp:
            msg.headers["Content-Type"] = "application/sdp"
            msg.body = sdp

        await self._send_message(msg)

    def _generate_sdp(self) -> str:
        """Generate SDP offer/answer."""
        local_ip = self._get_local_ip()
        rtp_port = self.active_call.local_rtp_port if self.active_call else 10000

        sdp = (
            "v=0\r\n"
            f"o=- {int(time.time())} 1 IN IP4 {local_ip}\r\n"
            "s=FLUXION Voice\r\n"
            f"c=IN IP4 {local_ip}\r\n"
            "t=0 0\r\n"
            f"m=audio {rtp_port} RTP/AVP 0 8\r\n"
            "a=rtpmap:0 PCMU/8000\r\n"
            "a=rtpmap:8 PCMA/8000\r\n"
            "a=sendrecv\r\n"
        )
        return sdp

    def _parse_sdp(self, sdp: str):
        """Parse SDP to extract RTP endpoint."""
        if not self.active_call:
            return

        for line in sdp.split('\r\n'):
            if line.startswith('c=IN IP4 '):
                self.active_call.remote_rtp_ip = line.split(' ')[2]
            elif line.startswith('m=audio '):
                parts = line.split(' ')
                self.active_call.remote_rtp_port = int(parts[1])

    async def answer_call(self):
        """Answer incoming call with 200 OK."""
        if not self.active_call or self.active_call.state != CallState.RINGING:
            return False

        # Allocate RTP port
        self.active_call.local_rtp_port = self._allocate_rtp_port()
        self.active_call.local_sdp = self._generate_sdp()

        # Build 200 OK with SDP
        msg = SIPMessage()
        msg.is_request = False
        msg.status_code = 200
        msg.reason_phrase = "OK"

        # Reconstruct request for response
        request = SIPMessage()
        request.headers = {
            "Via": "",  # Will be filled from stored call info
            "From": f"<sip:{self.active_call.remote_number}@{self.config.server}>;tag={self.active_call.remote_tag}",
            "To": f"<sip:{self.config.username}@{self.config.server}>;tag={self.active_call.local_tag}",
            "Call-ID": self.active_call.call_id,
            "CSeq": f"{self.active_call.cseq} INVITE",
        }

        await self._send_response(request, 200, "OK", self.active_call.local_sdp)

        self.active_call.state = CallState.CONNECTED
        self.active_call.connect_time = time.time()

        logger.info("Call answered")

        if self.on_call_connected:
            self.on_call_connected(self.active_call)

        return True

    def _allocate_rtp_port(self) -> int:
        """Allocate an available RTP port."""
        for port in range(self.config.rtp_port_start, self.config.rtp_port_end, 2):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.bind(('', port))
                s.close()
                return port
            except OSError:
                continue
        return self.config.rtp_port_start

    async def _handle_bye(self, msg: SIPMessage, addr: Tuple[str, int]):
        """Handle BYE request (remote hangup)."""
        # Send 200 OK
        await self._send_response(msg, 200, "OK")

        if self.active_call:
            self.active_call.state = CallState.ENDED
            self.active_call.end_time = time.time()

            logger.info(f"Call ended by remote (duration: {self.active_call.duration_seconds}s)")

            if self.on_call_ended:
                self.on_call_ended(self.active_call)

            self.active_call = None

    async def _handle_cancel(self, msg: SIPMessage, addr: Tuple[str, int]):
        """Handle CANCEL request."""
        await self._send_response(msg, 200, "OK")

        if self.active_call:
            self.active_call.state = CallState.ENDED
            self.active_call.end_time = time.time()
            self.active_call = None

    async def _handle_invite_response(self, msg: SIPMessage):
        """Handle response to outbound INVITE."""
        if not self.active_call:
            return

        if msg.status_code == 100:
            logger.debug("Call: Trying...")
        elif msg.status_code == 180 or msg.status_code == 183:
            self.active_call.state = CallState.RINGING
            logger.info("Call: Ringing...")
        elif msg.status_code == 200:
            # Call answered
            self.active_call.state = CallState.CONNECTED
            self.active_call.connect_time = time.time()

            # Parse remote SDP
            if msg.body:
                self.active_call.remote_sdp = msg.body
                self._parse_sdp(msg.body)

            # Send ACK
            await self._send_ack()

            logger.info("Call connected")

            if self.on_call_connected:
                self.on_call_connected(self.active_call)
        elif msg.status_code >= 400:
            self.active_call.state = CallState.FAILED
            logger.error(f"Call failed: {msg.status_code} {msg.reason_phrase}")
            self.active_call = None

    async def _send_ack(self):
        """Send ACK for 200 OK."""
        if not self.active_call:
            return

        msg = SIPMessage()
        msg.is_request = True
        msg.method = "ACK"
        msg.uri = self.active_call.remote_uri

        msg.headers = {
            "Via": self._build_via_header(),
            "Max-Forwards": "70",
            "From": f"<sip:{self.config.username}@{self.config.server}>;tag={self.active_call.local_tag}",
            "To": f"<sip:{self.active_call.remote_number}@{self.config.server}>;tag={self.active_call.remote_tag}",
            "Call-ID": self.active_call.call_id,
            "CSeq": f"{self.active_call.cseq} ACK",
        }

        await self._send_message(msg)

    async def _handle_bye_response(self, msg: SIPMessage):
        """Handle BYE response."""
        if self.active_call:
            self.active_call.state = CallState.ENDED
            self.active_call.end_time = time.time()

            if self.on_call_ended:
                self.on_call_ended(self.active_call)

            self.active_call = None

    async def _send_options_response(self, msg: SIPMessage, addr: Tuple[str, int]):
        """Send 200 OK response to OPTIONS (keepalive)."""
        await self._send_response(msg, 200, "OK")

    async def make_call(self, number: str) -> Optional[CallSession]:
        """
        Initiate outbound call.

        Args:
            number: Phone number or SIP URI to call

        Returns:
            CallSession if initiated, None on failure
        """
        if not self._registered:
            logger.error("Not registered, cannot make call")
            return None

        if self.active_call:
            logger.error("Already in a call")
            return None

        # Create call session
        self.active_call = CallSession(
            call_id=str(uuid.uuid4()),
            direction=CallDirection.OUTBOUND,
            remote_number=number,
            remote_uri=f"sip:{number}@{self.config.server}",
            state=CallState.INVITING,
            start_time=time.time(),
            local_rtp_port=self._allocate_rtp_port(),
        )

        self.active_call.local_sdp = self._generate_sdp()

        # Send INVITE
        msg = SIPMessage()
        msg.is_request = True
        msg.method = "INVITE"
        msg.uri = self.active_call.remote_uri

        msg.headers = {
            "Via": self._build_via_header(),
            "Max-Forwards": "70",
            "From": f"<sip:{self.config.username}@{self.config.server}>;tag={self.active_call.local_tag}",
            "To": f"<sip:{number}@{self.config.server}>",
            "Call-ID": self.active_call.call_id,
            "CSeq": f"{self.active_call.cseq} INVITE",
            "Contact": self._build_contact_header(),
            "Content-Type": "application/sdp",
            "User-Agent": self.config.user_agent,
        }

        # Add auth if we have credentials
        if self._nonce:
            msg.headers["Authorization"] = self._build_auth_header("INVITE", self.active_call.remote_uri)

        msg.body = self.active_call.local_sdp

        await self._send_message(msg)

        logger.info(f"Calling {number}...")
        return self.active_call

    async def hangup(self) -> bool:
        """End current call."""
        if not self.active_call:
            return False

        if self.active_call.state not in (CallState.CONNECTED, CallState.RINGING):
            return False

        self.active_call.cseq += 1

        msg = SIPMessage()
        msg.is_request = True
        msg.method = "BYE"
        msg.uri = self.active_call.remote_uri

        msg.headers = {
            "Via": self._build_via_header(),
            "Max-Forwards": "70",
            "From": f"<sip:{self.config.username}@{self.config.server}>;tag={self.active_call.local_tag}",
            "To": f"<sip:{self.active_call.remote_number}@{self.config.server}>;tag={self.active_call.remote_tag}",
            "Call-ID": self.active_call.call_id,
            "CSeq": f"{self.active_call.cseq} BYE",
        }

        await self._send_message(msg)

        self.active_call.state = CallState.ENDING
        logger.info("Hanging up...")
        return True

    async def start(self) -> bool:
        """Start SIP client and register."""
        if self._running:
            return True

        if not self.config.username or not self.config.password:
            logger.error("SIP credentials not configured")
            return False

        self._create_socket()
        self._running = True

        # Start receive loop
        self._receive_task = asyncio.create_task(self._receive_loop())

        # Register with server
        await self._send_register()

        # Wait for registration (with timeout)
        for _ in range(30):  # 3 seconds timeout
            await asyncio.sleep(0.1)
            if self._registered:
                break

        if not self._registered:
            logger.error("Registration timeout")
            return False

        # Start periodic re-registration
        self._register_task = asyncio.create_task(self._register_loop())

        return True

    async def _register_loop(self):
        """Periodic registration refresh."""
        while self._running:
            await asyncio.sleep(self.config.register_interval - 30)  # Refresh 30s before expiry
            if self._running:
                await self._send_register(with_auth=True)

    async def stop(self):
        """Stop SIP client."""
        self._running = False

        # Cancel tasks
        if self._register_task:
            self._register_task.cancel()
        if self._receive_task:
            self._receive_task.cancel()

        # Unregister
        if self._registered:
            self._cseq += 1
            msg = SIPMessage()
            msg.is_request = True
            msg.method = "REGISTER"
            msg.uri = f"sip:{self.config.server}"
            msg.headers = {
                "Via": self._build_via_header(),
                "From": f"<sip:{self.config.username}@{self.config.server}>;tag={self._local_tag}",
                "To": f"<sip:{self.config.username}@{self.config.server}>",
                "Call-ID": self._call_id,
                "CSeq": f"{self._cseq} REGISTER",
                "Contact": self._build_contact_header(),
                "Expires": "0",  # Unregister
            }
            if self._nonce:
                msg.headers["Authorization"] = self._build_auth_header("REGISTER", msg.uri)
            await self._send_message(msg)

        # Close socket
        if self._socket:
            self._socket.close()
            self._socket = None

        self._registered = False
        logger.info("SIP client stopped")

    @property
    def is_registered(self) -> bool:
        """Check if registered with SIP server."""
        return self._registered

    def get_status(self) -> Dict[str, Any]:
        """Get current SIP client status."""
        return {
            "registered": self._registered,
            "server": self.config.server,
            "username": self.config.username,
            "running": self._running,
            "active_call": {
                "call_id": self.active_call.call_id,
                "direction": self.active_call.direction.value,
                "remote_number": self.active_call.remote_number,
                "state": self.active_call.state.value,
                "duration": self.active_call.duration_seconds,
            } if self.active_call else None
        }


# =============================================================================
# RTP Audio Transport
# =============================================================================

class RTPTransport:
    """
    RTP audio transport for voice streaming.

    Handles encoding/decoding of G.711 audio (PCMU/PCMA).
    """

    PCMU_PAYLOAD_TYPE = 0
    PCMA_PAYLOAD_TYPE = 8
    RTP_HEADER_SIZE = 12
    SAMPLE_RATE = 8000
    SAMPLES_PER_PACKET = 160  # 20ms of audio at 8kHz

    def __init__(self, local_port: int, remote_ip: str = "", remote_port: int = 0):
        self.local_port = local_port
        self.remote_ip = remote_ip
        self.remote_port = remote_port
        self._socket: Optional[socket.socket] = None
        self._running = False
        self._receive_task: Optional[asyncio.Task] = None

        # RTP state
        self._ssrc = int.from_bytes(os.urandom(4), 'big')
        self._sequence = 0
        self._timestamp = 0

        # Callbacks
        self.on_audio_received: Optional[Callable[[bytes], None]] = None

    async def start(self):
        """Start RTP transport."""
        if self._running:
            return

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.setblocking(False)
        self._socket.bind(('', self.local_port))

        self._running = True
        self._receive_task = asyncio.create_task(self._receive_loop())

        logger.info(f"RTP transport started on port {self.local_port}")

    async def stop(self):
        """Stop RTP transport."""
        self._running = False

        if self._receive_task:
            self._receive_task.cancel()

        if self._socket:
            self._socket.close()
            self._socket = None

    async def _receive_loop(self):
        """Receive RTP packets."""
        loop = asyncio.get_event_loop()

        while self._running:
            try:
                data, addr = await loop.sock_recvfrom(self._socket, 2048)
                if len(data) > self.RTP_HEADER_SIZE:
                    # Extract audio payload (skip RTP header)
                    payload = data[self.RTP_HEADER_SIZE:]

                    # Decode from G.711
                    pcm = self._decode_pcmu(payload)

                    if self.on_audio_received:
                        self.on_audio_received(pcm)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"RTP receive error: {e}")

    def _decode_pcmu(self, data: bytes) -> bytes:
        """Decode G.711 mu-law to PCM 16-bit."""
        # mu-law to linear 16-bit conversion table
        pcm = bytearray(len(data) * 2)
        for i, byte in enumerate(data):
            # mu-law decoding
            byte = ~byte
            sign = byte & 0x80
            exponent = (byte >> 4) & 0x07
            mantissa = byte & 0x0F

            sample = ((mantissa << 3) + 0x84) << exponent
            sample -= 0x84

            if sign:
                sample = -sample

            # Write as 16-bit little-endian
            pcm[i*2] = sample & 0xFF
            pcm[i*2 + 1] = (sample >> 8) & 0xFF

        return bytes(pcm)

    def _encode_pcmu(self, pcm: bytes) -> bytes:
        """Encode PCM 16-bit to G.711 mu-law."""
        ulaw = bytearray(len(pcm) // 2)

        for i in range(0, len(pcm), 2):
            # Read 16-bit sample (little-endian)
            sample = struct.unpack('<h', pcm[i:i+2])[0]

            # mu-law encoding
            sign = 0x80 if sample >= 0 else 0
            if sample < 0:
                sample = -sample

            sample = min(sample, 32767)
            sample += 0x84

            # Find exponent
            exponent = 7
            for exp in range(7, -1, -1):
                if sample & (1 << (exp + 7)):
                    exponent = exp
                    break

            mantissa = (sample >> (exponent + 3)) & 0x0F

            ulaw[i//2] = ~(sign | (exponent << 4) | mantissa) & 0xFF

        return bytes(ulaw)

    async def send_audio(self, pcm_data: bytes):
        """
        Send audio data via RTP.

        Args:
            pcm_data: PCM 16-bit, 8kHz audio data
        """
        if not self._socket or not self.remote_ip or not self.remote_port:
            return

        # Encode to G.711 mu-law
        payload = self._encode_pcmu(pcm_data)

        # Build RTP header
        header = struct.pack(
            '>BBHII',
            0x80,  # Version 2, no padding, no extension, no CSRC
            self.PCMU_PAYLOAD_TYPE,  # Payload type
            self._sequence & 0xFFFF,
            self._timestamp & 0xFFFFFFFF,
            self._ssrc
        )

        packet = header + payload

        # Send
        loop = asyncio.get_event_loop()
        await loop.sock_sendto(
            self._socket,
            packet,
            (self.remote_ip, self.remote_port)
        )

        # Update sequence and timestamp
        self._sequence += 1
        self._timestamp += len(payload)


# =============================================================================
# VoIP Manager (High-level integration)
# =============================================================================

class VoIPManager:
    """
    High-level VoIP manager for FLUXION Voice Agent.

    Integrates SIP client with RTP transport and voice pipeline.
    """

    def __init__(self, config: Optional[SIPConfig] = None):
        self.config = config or SIPConfig.from_env()
        self.sip = SIPClient(self.config)
        self.rtp: Optional[RTPTransport] = None
        self.pipeline = None  # VoicePipeline instance
        self._running = False

        # Audio buffer for accumulating samples
        self._audio_buffer = bytearray()
        self._buffer_threshold = 8000  # ~500ms at 8kHz 16-bit

    def set_pipeline(self, pipeline):
        """Set voice pipeline for processing."""
        self.pipeline = pipeline

    async def start(self) -> bool:
        """Start VoIP service."""
        if self._running:
            return True

        # Set up SIP callbacks
        self.sip.on_incoming_call = self._on_incoming_call
        self.sip.on_call_connected = self._on_call_connected
        self.sip.on_call_ended = self._on_call_ended

        # Start SIP client
        if not await self.sip.start():
            return False

        self._running = True
        logger.info("VoIP service started")
        return True

    async def stop(self):
        """Stop VoIP service."""
        if not self._running:
            return

        # Stop RTP if active
        if self.rtp:
            await self.rtp.stop()
            self.rtp = None

        # Stop SIP
        await self.sip.stop()

        self._running = False
        logger.info("VoIP service stopped")

    def _on_incoming_call(self, call: CallSession):
        """Handle incoming call."""
        logger.info(f"Incoming call from {call.remote_number}")
        # Auto-answer (can be configured)
        asyncio.create_task(self._auto_answer())

    async def _auto_answer(self):
        """Auto-answer incoming call."""
        await asyncio.sleep(1)  # Brief delay before answering
        await self.answer_call()

    async def _on_call_connected(self, call: CallSession):
        """Handle call connected."""
        logger.info(f"Call connected: {call.remote_number}")

        # Start RTP transport
        self.rtp = RTPTransport(
            local_port=call.local_rtp_port,
            remote_ip=call.remote_rtp_ip,
            remote_port=call.remote_rtp_port
        )
        self.rtp.on_audio_received = self._on_audio_received
        await self.rtp.start()

        # Play greeting
        if self.pipeline:
            greeting = await self.pipeline.greet()
            if greeting.get("audio_response"):
                await self._send_audio(greeting["audio_response"])

    def _on_call_ended(self, call: CallSession):
        """Handle call ended."""
        logger.info(f"Call ended: {call.remote_number} (duration: {call.duration_seconds}s)")

        # Stop RTP
        if self.rtp:
            asyncio.create_task(self.rtp.stop())
            self.rtp = None

        # Clear audio buffer
        self._audio_buffer.clear()

    def _on_audio_received(self, pcm_data: bytes):
        """Handle received audio."""
        # Accumulate audio in buffer
        self._audio_buffer.extend(pcm_data)

        # Process when we have enough
        if len(self._audio_buffer) >= self._buffer_threshold:
            audio = bytes(self._audio_buffer)
            self._audio_buffer.clear()
            asyncio.create_task(self._process_audio(audio))

    async def _process_audio(self, audio_data: bytes):
        """Process received audio through voice pipeline."""
        if not self.pipeline:
            return

        try:
            # Convert from 8kHz to 16kHz for Whisper
            audio_16k = self._upsample_audio(audio_data)

            # Process through pipeline
            result = await self.pipeline.process_audio(audio_16k)

            # Send response audio
            if result.get("audio_response"):
                await self._send_audio(result["audio_response"])
        except Exception as e:
            logger.error(f"Audio processing error: {e}")

    def _upsample_audio(self, audio_8k: bytes) -> bytes:
        """Upsample from 8kHz to 16kHz (simple linear interpolation)."""
        samples = struct.unpack(f'<{len(audio_8k)//2}h', audio_8k)
        upsampled = []
        for i in range(len(samples) - 1):
            upsampled.append(samples[i])
            upsampled.append((samples[i] + samples[i+1]) // 2)
        upsampled.append(samples[-1])
        upsampled.append(samples[-1])
        return struct.pack(f'<{len(upsampled)}h', *upsampled)

    def _downsample_audio(self, audio_16k: bytes) -> bytes:
        """Downsample from 16kHz to 8kHz."""
        samples = struct.unpack(f'<{len(audio_16k)//2}h', audio_16k)
        downsampled = samples[::2]  # Take every other sample
        return struct.pack(f'<{len(downsampled)}h', *downsampled)

    async def _send_audio(self, audio_data: bytes):
        """Send audio to remote party."""
        if not self.rtp:
            return

        # Downsample if needed (pipeline outputs 16kHz, RTP uses 8kHz)
        audio_8k = self._downsample_audio(audio_data)

        # Send in chunks
        chunk_size = 320  # 160 samples * 2 bytes = 20ms
        for i in range(0, len(audio_8k), chunk_size):
            chunk = audio_8k[i:i+chunk_size]
            if len(chunk) == chunk_size:
                await self.rtp.send_audio(chunk)
                await asyncio.sleep(0.02)  # 20ms pacing

    async def answer_call(self) -> bool:
        """Answer incoming call."""
        return await self.sip.answer_call()

    async def make_call(self, number: str) -> Optional[CallSession]:
        """Make outbound call."""
        return await self.sip.make_call(number)

    async def hangup(self) -> bool:
        """End current call."""
        return await self.sip.hangup()

    def get_status(self) -> Dict[str, Any]:
        """Get VoIP manager status."""
        return {
            "running": self._running,
            "sip": self.sip.get_status(),
            "rtp_active": self.rtp is not None
        }


# =============================================================================
# Test
# =============================================================================

async def test_voip():
    """Test VoIP manager."""
    from dotenv import load_dotenv
    load_dotenv()

    logging.basicConfig(level=logging.DEBUG)

    config = SIPConfig.from_env()
    print(f"SIP Server: {config.server}")
    print(f"Username: {config.username}")

    manager = VoIPManager(config)

    # Start
    print("\nStarting VoIP service...")
    if await manager.start():
        print("VoIP service started successfully")
        print(f"Status: {manager.get_status()}")

        # Wait for a bit (would receive calls)
        print("\nWaiting for calls (press Ctrl+C to stop)...")
        try:
            await asyncio.sleep(30)
        except KeyboardInterrupt:
            pass

        # Stop
        print("\nStopping...")
        await manager.stop()
    else:
        print("Failed to start VoIP service")


if __name__ == "__main__":
    asyncio.run(test_voip())
