"""voip_goengine.py — Adapter Python per il motore telefonico Go (T-SARA-MEDIASWAP).

FILE ADDITIVO. NON tocca voip_pjsua2.py. Selezionato via VOICE_ENGINE=go in main.py
(default resta pjsua2 → reversibilità totale, vincolo #1d).

Ruolo: il "cervello" Sara (STT+NLU+TTS+FSM) resta identico; questo adapter sostituisce
il media-layer pjsua2 con un processo Go (engine/main.go) che fa SIP+RTP+G.711.
Comunicazione via ponte TCP locale FRAMED: tipo(1B)+len(2B big-endian)+payload.

Contratto (speculare a engine/main.go):
  Engine → Python: 0x01 STATUS | 0x02 CALL_START | 0x03 AUDIO_RX(320B) | 0x04 CALL_END
  Python → Engine: 0x10 AUDIO_TX(320B) | 0x11 HANGUP

Rifà il CONTRATTO MEDIA-LAYER §4 (STACK_SARA.md) lato cervello:
  (1) barge-in RMS (svuota TX + smette di inviare)
  (2) greeting all'answer (dal cervello, via pipeline.greet)
  (3) resample TX 16k→8k audioop.ratecv (in queue_tts_audio, replicato)
  (4) turn-taking VAD (energy-based, soglie coerenti con voip_pjsua2.py)
I punti 5-6 (thread confinement, NAT ICE/STUN) SPARISCONO col motore Go.
"""

from __future__ import annotations

import asyncio
import atexit
import audioop
import io
import logging
import os
import queue
import socket
import signal
import struct
import subprocess
import threading
import time
import wave
from collections import deque
from dataclasses import dataclass
from typing import Any, Dict, Optional

logger = logging.getLogger("voip_goengine")

# --- Tipi frame ponte (speculari a engine/main.go) ---
FRAME_STATUS = 0x01
FRAME_CALL_START = 0x02
FRAME_AUDIO_RX = 0x03
FRAME_CALL_END = 0x04
FRAME_AUDIO_TX = 0x10
FRAME_HANGUP = 0x11

FRAME_BYTES = 320  # 20ms PCM16 @ 8kHz mono

# --- Soglie replicate da voip_pjsua2.py (§4) ---
BARGE_IN_MARGIN = 500      # RMS sopra echo atteso per triggerare barge-in (voip_pjsua2.py:1130)
BARGE_IN_THRESHOLD = 4     # 80ms speech sostenuto (voip_pjsua2.py:1131)
ECHO_ATTENUATION = 0.5     # echo ~50% energia TX (voip_pjsua2.py:1132)
VAD_SPEECH_THRESHOLD = 400 # RMS soglia turn (voip_pjsua2.py: turn_rms<400 → skip)
VAD_SILENCE_TIMEOUT = 50   # frame silenzio (~1000ms @ 20ms) fine-turno
VAD_MIN_SPEECH_FRAMES = 15 # ≥300ms speech (voip_pjsua2.py:1207)

# --- Turn-taking half-duplex (T-SARA-TURNTAKING FASE 2, spec §4) ---
# Grace dopo l'ultimo frame TX: l'engine Go emette ~200ms oltre la coda Python vuota
# (txCapFrames=10 = 200ms) → la sua eco di linea rientra su RX mentre la coda è già
# vuota. Teniamo lo stato SPEAKING per questa finestra così RX non entra in STT.
TX_GRACE_S = 0.180
# Barge-in adattivo (spec 2.2): trigger = rms > max(soglia_base, k·echo_floor) sostenuto.
BARGE_IN_K = 2.5           # moltiplicatore sopra l'echo-floor misurato durante TX
BARGE_IN_SUSTAIN = 13      # ~260ms sostenuti (spec 2.2: ≥250-300ms, robusto su eco reale)
ECHO_FLOOR_ALPHA = 0.15    # coeff. media mobile echo-floor (RX durante TX)
# Ring-buffer pre-trigger (spec 2.4): inoltra a STT i frame del trigger, no perdita
# delle prime parole del chiamante.
RX_PRETRIGGER_FRAMES = BARGE_IN_SUSTAIN + 4  # ~340ms

# --- Idle-timeout a livello CHIAMATA (FASE 3.0): 2ª gamba LEGITTIMA dell'hangup ---
# Distinto dal VAD end-of-turn (VAD_SILENCE_TIMEOUT = 1s = fine-turno): qui è il
# silenzio TOTALE del chiamante a livello di chiamata. Senza questo, una call in cui
# il chiamante tace del tutto resta appesa all'infinito (il loop RX riceve solo silenzio,
# nessun turno completa mai) → il numero risulta OCCUPATO per tutti i clienti successivi.
# Dopo IDLE_REPROMPT_S di silenzio combinato (né Sara né chiamante) → UN reprompt;
# dopo altri IDLE_HANGUP_S di silenzio → congedo cortese + hangup legittimo loggato.
IDLE_REPROMPT_S = 22.0   # ~20-25s senza parlato del chiamante → reprompt
IDLE_HANGUP_S = 18.0     # +~15-20s dopo il reprompt ancora muto → congedo + hangup
IDLE_REPROMPT_TEXT = "Pronto, è ancora in linea?"
IDLE_GOODBYE_TEXT = "Non la sento più. Grazie per aver chiamato, arrivederci."


@dataclass
class SIPConfig:
    """Config SIP letta dalle STESSE env di Sara (voip_pjsua2.py SIPConfig.from_env)."""
    username: str
    password: str
    server: str
    port: int = 5060
    local_port: int = 5080
    external: str = ""

    @classmethod
    def from_env(cls) -> "SIPConfig":
        return cls(
            username=os.getenv("VOIP_SIP_USER", "").strip(),
            password=os.getenv("VOIP_SIP_PASS", "").strip(),
            server=os.getenv("VOIP_SIP_SERVER", "").strip(),
            port=int(os.getenv("VOIP_SIP_PORT", "5060") or "5060"),
            local_port=int(os.getenv("VOIP_LOCAL_PORT", "5080") or "5080"),
            external=os.getenv("VOIP_EXTERNAL_IP", "").strip(),
        )


class GoEngineVoIPManager:
    """Drop-in replacement di VoIPManager (voip_pjsua2.py) basato sul motore Go.

    Espone la stessa interfaccia consumata da main.py:
      set_pipeline(pipeline), await start()->bool, get_status()->dict,
      await hangup()->bool, await stop().
    """

    def __init__(self, config: SIPConfig, bridge_host: str = "127.0.0.1", bridge_port: int = 8300):
        self.config = config
        self.bridge_host = bridge_host
        self.bridge_port = bridge_port

        self.pipeline = None
        self._main_loop: Optional[asyncio.AbstractEventLoop] = None

        self._running = False
        self._registered = False
        self._reg_status = 0
        self._call_active = False
        self._caller = ""

        # Ponte TCP (Python = SERVER, engine = client).
        self._srv_sock: Optional[socket.socket] = None
        self._conn: Optional[socket.socket] = None
        self._conn_lock = threading.Lock()

        # Coda RX (audio chiamante) — STESSO formato che la pipeline consuma
        # oggi con pjsua2 (PCM16 8k mono, frame 320B). Drop-in su rx_queue.
        self.rx_queue: "queue.Queue[bytes]" = queue.Queue(maxsize=500)
        # Coda TX locale (per barge-in Python-side): drenata → AUDIO_TX.
        self._tx_queue: "queue.Queue[bytes]" = queue.Queue(maxsize=3000)
        self._current_tx_rms = 0.0
        # Stato-turno esplicito (FASE 2 spec 2.1): autorità unica su SPEAKING.
        # _tx_last_frame_ts = monotonic dell'ultimo frame TX inviato all'engine;
        # la grace (TX_GRACE_S) copre la coda RTP residua dell'engine dopo la coda vuota.
        self._tx_last_frame_ts = 0.0
        # Echo-floor: media mobile dell'RMS RX misurata DURANTE TX (barge-in adattivo 2.2).
        self._echo_floor = 0.0
        # Idle-timeout a livello chiamata (FASE 3.0): monotonic dell'ultimo parlato REALE
        # del chiamante; flag reprompt-emesso; istante del reprompt. Azzerati a CALL_START.
        self._last_caller_voice_ts = 0.0
        self._idle_reprompted = False
        self._idle_reprompt_ts = 0.0
        # GATE2R metriche TX (ring-by-ring): drenati da _tx_queue, scritti a socket, byte.
        self._m_tx_drained = 0
        self._m_tx_written = 0
        self._m_tx_bytes = 0

        # Processo engine.
        self._proc: Optional[subprocess.Popen] = None
        self._threads: list[threading.Thread] = []
        self._stop_evt = threading.Event()

        # Ultimo risultato di turno (per selftest/diagnostica). Non usato in produzione.
        self.last_turn_result: Optional[Dict[str, Any]] = None

        # Analytics: STESSO singleton letto da /api/metrics/latency (main.py:858 get_logger()).
        # La sessione si apre a CALL_START; ogni turno reale scrive conversation_turns
        # → alimenta get_percentile_stats (count). Best-effort: mai bloccare il media-layer.
        try:
            from src.analytics import get_logger
            self._analytics = get_logger()
        except Exception as exc:  # pragma: no cover
            logger.warning("analytics non disponibile: %s", exc)
            self._analytics = None
        self._analytics_sid: Optional[str] = None
        self._verticale_id: str = os.getenv("VOICE_VERTICALE", "salone").strip() or "salone"

    # --- interfaccia VoIPManager ---

    def set_pipeline(self, pipeline):
        self.pipeline = pipeline

    async def start(self) -> bool:
        self._main_loop = asyncio.get_running_loop()
        if not (self.config.username and self.config.password and self.config.server):
            logger.error("SIP config incompleta (VOIP_SIP_USER/PASS/SERVER)")
            return False

        # 1) apri il listener TCP del ponte PRIMA di spawnare l'engine.
        self._srv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._srv_sock.bind((self.bridge_host, self.bridge_port))
        self._srv_sock.listen(1)
        self._running = True
        self._stop_evt.clear()

        # DIFETTO B: bonifica engine orfani da run precedenti (match sul path binario).
        self._reap_orphan_engines()
        # DIFETTO B: garantisci kill del child anche su exit non pulito.
        atexit.register(self._atexit_kill_engine)
        # atexit NON gira sui segnali: installa handler SIGTERM/SIGINT che killa il
        # child engine e poi rilancia l'handler precedente (best-effort, solo main thread).
        self._install_signal_handlers()

        t_accept = threading.Thread(target=self._accept_loop, daemon=True, name="goengine-accept")
        t_accept.start()
        self._threads.append(t_accept)

        # 2) supervisione engine (spawn + backoff restart).
        t_sup = threading.Thread(target=self._supervise_engine, daemon=True, name="goengine-supervise")
        t_sup.start()
        self._threads.append(t_sup)

        # 3) turn-taking VAD loop (consuma rx_queue → pipeline).
        t_audio = threading.Thread(target=self._audio_processing_loop, daemon=True, name="goengine-audio")
        t_audio.start()
        self._threads.append(t_audio)

        # Attendi brevemente la registrazione (best-effort; non blocca l'avvio).
        for _ in range(60):  # ~6s
            if self._registered:
                break
            await asyncio.sleep(0.1)
        logger.info("GoEngine start: registered=%s reg_status=%s", self._registered, self._reg_status)
        # Ritorna True se il motore è vivo (registrazione può arrivare poco dopo).
        return self._running

    async def stop(self):
        self._running = False
        self._stop_evt.set()
        # Termina engine.
        if self._proc and self._proc.poll() is None:
            try:
                try:
                    os.killpg(os.getpgid(self._proc.pid), signal.SIGTERM)
                except (ProcessLookupError, PermissionError, OSError):
                    self._proc.terminate()
                try:
                    self._proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    try:
                        os.killpg(os.getpgid(self._proc.pid), signal.SIGKILL)
                    except (ProcessLookupError, PermissionError, OSError):
                        self._proc.kill()
            except Exception as exc:  # pragma: no cover
                logger.warning("stop engine: %s", exc)
        with self._conn_lock:
            for s in (self._conn, self._srv_sock):
                if s:
                    try:
                        s.close()
                    except OSError:
                        pass
            self._conn = None
            self._srv_sock = None

    async def hangup(self) -> bool:
        self._send_frame(FRAME_HANGUP, b"")
        return True

    def get_status(self) -> Dict[str, Any]:
        return {
            "running": self._running,
            "sip": {
                "registered": self._registered,
                "reg_status": self._reg_status,
                "username": self.config.username,
                "server": self.config.server,
            },
            "rtp_active": self._call_active,
            "engine": "go",
        }

    # --- ponte TCP (Python = server) ---

    def _accept_loop(self):
        while self._running and not self._stop_evt.is_set():
            try:
                self._srv_sock.settimeout(1.0)
                conn, addr = self._srv_sock.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            logger.info("engine connesso al ponte da %s", addr)
            with self._conn_lock:
                self._conn = conn
            self._read_frames(conn)
            with self._conn_lock:
                if self._conn is conn:
                    self._conn = None
            try:
                conn.close()
            except OSError:
                pass

    def _read_frames(self, conn: socket.socket):
        header = b""
        conn.settimeout(1.0)
        while self._running and not self._stop_evt.is_set():
            try:
                header = self._recv_exact(conn, 3)
            except (socket.timeout, TimeoutError):
                continue
            except (OSError, ConnectionError):
                return
            if header is None:
                return
            typ = header[0]
            (ln,) = struct.unpack(">H", header[1:3])
            payload = b""
            if ln:
                try:
                    payload = self._recv_exact(conn, ln)
                except (OSError, ConnectionError):
                    return
                if payload is None:
                    return
            self._dispatch(typ, payload)

    @staticmethod
    def _recv_exact(conn: socket.socket, n: int) -> Optional[bytes]:
        buf = bytearray()
        while len(buf) < n:
            chunk = conn.recv(n - len(buf))
            if not chunk:
                return None
            buf.extend(chunk)
        return bytes(buf)

    def _dispatch(self, typ: int, payload: bytes):
        if typ == FRAME_AUDIO_RX:
            try:
                self.rx_queue.put_nowait(payload)
            except queue.Full:
                pass  # real-time: scarta se pieno
        elif typ == FRAME_STATUS:
            self._on_status(payload)
        elif typ == FRAME_CALL_START:
            self._on_call_start(payload.decode("utf-8", "replace"))
        elif typ == FRAME_CALL_END:
            self._on_call_end()
        else:
            logger.warning("frame engine ignoto: type=0x%02x len=%d", typ, len(payload))

    def _on_status(self, payload: bytes):
        try:
            import json
            data = json.loads(payload.decode("utf-8"))
            self._registered = bool(data.get("registered", False))
            self._reg_status = int(data.get("reg_status", 0))
        except Exception as exc:
            logger.warning("STATUS parse: %s", exc)

    def _on_call_start(self, caller: str):
        logger.info("CALL_START caller=%s", caller)
        self._call_active = True
        self._caller = caller
        # Idle-timeout (FASE 3.0): arma il timer dall'inizio chiamata, nessun reprompt pendente.
        self._last_caller_voice_ts = time.monotonic()
        self._idle_reprompted = False
        self._idle_reprompt_ts = 0.0
        # Svuota code residue del turno precedente.
        self._drain_queue(self.rx_queue)
        self._drain_queue(self._tx_queue)
        # Apri sessione analytics per la chiamata (i turni la aggiornano → count).
        if self._analytics is not None:
            try:
                verticale = getattr(self.pipeline, "verticale_id", None) or self._verticale_id
                self._analytics_sid = self._analytics.start_session(verticale)
            except Exception as exc:
                logger.warning("analytics.start_session errore: %s", exc)
                self._analytics_sid = None
        # Greeting DAL CERVELLO (non nell'engine).
        threading.Thread(target=self._send_greeting, args=(caller,), daemon=True).start()

    def _on_call_end(self):
        logger.info("CALL_END")
        self._call_active = False
        self._caller = ""
        # Idle-timeout (FASE 3.0): disarma per la prossima chiamata.
        self._idle_reprompted = False
        self._drain_queue(self.rx_queue)
        self._drain_queue(self._tx_queue)

    @staticmethod
    def _drain_queue(q: "queue.Queue"):
        try:
            while True:
                q.get_nowait()
        except queue.Empty:
            pass

    def _send_frame(self, typ: int, payload: bytes):
        with self._conn_lock:
            conn = self._conn
        if conn is None:
            return
        try:
            conn.sendall(bytes([typ]) + struct.pack(">H", len(payload)) + payload)
        except (OSError, ConnectionError) as exc:
            logger.warning("ponte send errore type=0x%02x: %s", typ, exc)

    # --- supervisione engine (spawn + backoff) ---

    def _supervise_engine(self):
        backoff = 0.5
        engine_bin = self._engine_binary_path()
        while self._running and not self._stop_evt.is_set():
            env = dict(os.environ)
            env["VOIP_SIP_USER"] = self.config.username
            env["VOIP_SIP_PASS"] = self.config.password
            env["VOIP_SIP_SERVER"] = self.config.server
            args = [
                engine_bin,
                "-port", str(self.config.local_port),
                "-bridge", f"{self.bridge_host}:{self.bridge_port}",
            ]
            if self.config.external:
                args += ["-external", self.config.external]
            logger.info("spawn engine: %s", " ".join(a for a in args if "PASS" not in a))
            try:
                self._proc = subprocess.Popen(args, env=env, start_new_session=True)
            except OSError as exc:
                logger.error("spawn engine fallito: %s", exc)
                if self._stop_evt.wait(backoff):
                    return
                backoff = min(backoff * 2, 10.0)
                continue
            backoff = 0.5
            self._proc.wait()
            if not self._running or self._stop_evt.is_set():
                return
            logger.warning("engine terminato (rc=%s), restart con backoff", self._proc.returncode)
            self._registered = False
            self._reg_status = 0
            if self._stop_evt.wait(backoff):
                return
            backoff = min(backoff * 2, 10.0)

    def _install_signal_handlers(self):
        """DIFETTO B: su SIGTERM/SIGINT killa l'engine (atexit non copre i segnali)."""
        def _make(sig):
            prev = signal.getsignal(sig)
            def _handler(signum, frame):
                try:
                    self._atexit_kill_engine()
                finally:
                    if callable(prev) and prev not in (signal.SIG_DFL, signal.SIG_IGN):
                        prev(signum, frame)
                    else:
                        raise SystemExit(0)
            return _handler
        try:
            for sig in (signal.SIGTERM, signal.SIGINT):
                signal.signal(sig, _make(sig))
        except (ValueError, OSError) as exc:
            # non nel main thread: fallback su atexit soltanto.
            logger.warning("signal handler non installato (%s); resta atexit + reap-orfani", exc)

    def _atexit_kill_engine(self):
        """DIFETTO B: killa il child engine (e il suo gruppo) su interprete in uscita."""
        proc = self._proc
        if proc is None or proc.poll() is not None:
            return
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except (ProcessLookupError, PermissionError, OSError):
            try:
                proc.terminate()
            except OSError:
                pass
        try:
            proc.wait(timeout=2)
        except Exception:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except (ProcessLookupError, PermissionError, OSError):
                pass

    def _reap_orphan_engines(self):
        """DIFETTO B: uccide engine orfani (stesso path binario) rimasti da run precedenti."""
        binpath = self._engine_binary_path()
        binname = os.path.basename(binpath)
        try:
            out = subprocess.run(["pgrep", "-f", binname], capture_output=True, text=True, timeout=5)
        except (OSError, subprocess.SubprocessError) as exc:
            logger.warning("reap orfani: pgrep fallito: %s", exc)
            return
        mypid = os.getpid()
        killed = []
        for line in out.stdout.split():
            try:
                pid = int(line)
            except ValueError:
                continue
            if pid == mypid:
                continue
            # verifica che il comando contenga davvero il path del binario engine
            try:
                cmd = subprocess.run(["ps", "-o", "command=", "-p", str(pid)],
                                     capture_output=True, text=True, timeout=3).stdout
            except (OSError, subprocess.SubprocessError):
                continue
            if binname not in cmd:
                continue
            try:
                os.kill(pid, signal.SIGTERM)
                killed.append(pid)
            except (ProcessLookupError, PermissionError, OSError):
                pass
        if killed:
            logger.warning("reap orfani engine: uccisi pid=%s", killed)
        else:
            logger.info("reap orfani engine: nessun orfano")

    @staticmethod
    def _engine_binary_path() -> str:
        # Binario buildato accanto ai sorgenti engine/.
        here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # voice-agent/
        cand = os.path.join(here, "engine", "engine_darwin_amd64")
        if os.path.exists(cand):
            return cand
        # fallback: nome generico se buildato con `go build -o engine`.
        return os.path.join(here, "engine", "engine")

    # --- greeting + queue TTS (contratto §4 punti 2,3) ---

    def _send_greeting(self, caller: str):
        if not self.pipeline or self._main_loop is None:
            return
        try:
            time.sleep(0.3)  # media stabilize
            fut = asyncio.run_coroutine_threadsafe(
                self.pipeline.greet(phone_number=caller), self._main_loop
            )
            greeting = fut.result(timeout=15)
            if greeting and greeting.get("audio_response"):
                self.queue_tts_audio(greeting["audio_response"])
                logger.info("greeting in coda TX")
        except Exception as exc:
            logger.warning("greeting errore: %s", exc)

    def queue_tts_audio(self, audio_data: bytes, src_rate: int = 16000):
        """Replica voip_pjsua2.py:298-328 — parse WAV, resample 16k→8k, chunk 320B → TX."""
        pcm_data = audio_data
        if audio_data[:4] == b"RIFF":
            try:
                with wave.open(io.BytesIO(audio_data), "rb") as wf:
                    src_rate = wf.getframerate()
                    pcm_data = wf.readframes(wf.getnframes())
            except Exception as exc:
                logger.warning("WAV parse fallito: %s, raw @%dHz", exc, src_rate)
        if src_rate != 8000:
            pcm_data, _ = audioop.ratecv(pcm_data, 2, 1, src_rate, 8000, None)
        for i in range(0, len(pcm_data), FRAME_BYTES):
            chunk = pcm_data[i:i + FRAME_BYTES]
            if len(chunk) < FRAME_BYTES:
                chunk = chunk + b"\x00" * (FRAME_BYTES - len(chunk))
            try:
                self._tx_queue.put_nowait(chunk)
            except queue.Full:
                break

    def clear_tx(self):
        """Barge-in: svuota la coda TX Python (l'engine cappa a 200ms il resto)."""
        self._drain_queue(self._tx_queue)
        self._current_tx_rms = 0.0
        # Forza la fine della grace: il chiamante ha preso la parola → LISTENING subito,
        # altrimenti la grace continuerebbe a sopprimere l'RX post-barge-in (spec 2.1).
        self._tx_last_frame_ts = 0.0

    def _is_sara_speaking(self) -> bool:
        """Autorità unica dello stato-turno SPEAKING (spec 2.1).

        SPEAKING sse: c'è TX ancora in coda OPPURE siamo entro la grace dopo l'ultimo
        frame TX (l'engine Go emette ~200ms oltre la coda vuota → la sua eco di linea
        rientra su RX mentre Python crede che Sara abbia smesso). In SPEAKING l'RX non
        entra in STT (solo barge-in può interrompere).
        """
        if not self._tx_queue.empty():
            return True
        return (time.monotonic() - self._tx_last_frame_ts) < TX_GRACE_S

    # --- turn-taking VAD + barge-in (contratto §4 punti 1,4) ---

    def _tx_pump(self):
        """Drena la coda TX e invia AUDIO_TX all'engine con PACING 20ms (GATE2R fix H1).

        RED baseline: senza pacing il greeting (~452 frame) veniva scritto a socket in burst;
        l'engine (txCapFrames=10) scartava ~441 frame → ~11 frame di voce su RTP → MUTO.
        Fix: invia 1 frame ogni FRAME_MS su clock monotonico → l'engine consuma 1:1 al suo
        clock RTP 20ms, push_drop≈0. clear_tx (barge-in) resta: svuota la coda e il pump
        torna a idle.
        """
        FRAME_MS = 0.020  # 20ms per frame (8kHz, 320B)
        _last_log = time.time()
        _next = time.monotonic()
        while self._running and not self._stop_evt.is_set():
            try:
                chunk = self._tx_queue.get(timeout=0.1)
            except queue.Empty:
                # idle: risincronizza il clock così il primo frame del prossimo
                # greeting non parta "in ritardo" accumulato.
                _next = time.monotonic()
                # Difetto 2 (spec 2.1): azzera l'RMS TX quando la coda si svuota, così
                # non resta "bloccato" al valore dell'ultimo frame voce (che terrebbe
                # sara_speaking=True per sempre → RX soppressa a vita). Lo stato SPEAKING
                # nella grace è ora retto da _tx_last_frame_ts, non da questo RMS stale.
                self._current_tx_rms = 0.0
                if time.time() - _last_log >= 1.0:
                    logger.info("[GATE2R-PY-TX] drained=%d written=%d bytes=%d",
                                self._m_tx_drained, self._m_tx_written, self._m_tx_bytes)
                    _last_log = time.time()
                continue
            self._m_tx_drained += 1
            self._current_tx_rms = self._rms(chunk)
            self._send_frame(FRAME_AUDIO_TX, chunk)
            # Difetto 1 (spec 2.1): marca l'istante dell'ultimo frame TX per la grace.
            self._tx_last_frame_ts = time.monotonic()
            self._m_tx_written += 1
            self._m_tx_bytes += len(chunk)
            # Pacing: attendi fino al prossimo slot da 20ms.
            _next += FRAME_MS
            _sleep = _next - time.monotonic()
            if _sleep > 0:
                time.sleep(_sleep)
            else:
                # in ritardo: non accumulare debito, risincronizza.
                _next = time.monotonic()
            if time.time() - _last_log >= 1.0:
                logger.info("[GATE2R-PY-TX] drained=%d written=%d bytes=%d",
                            self._m_tx_drained, self._m_tx_written, self._m_tx_bytes)
                _last_log = time.time()

    def _audio_processing_loop(self):
        """Turn-taking VAD energy-based su rx_queue + barge-in. Replica §4 1/4."""
        # TX pump separato: invia audio appena disponibile (no pacing lato Python).
        t_tx = threading.Thread(target=self._tx_pump, daemon=True, name="goengine-txpump")
        t_tx.start()
        self._threads.append(t_tx)

        # Idle-monitor separato (FASE 3.0): reprompt + hangup su silenzio a livello chiamata.
        t_idle = threading.Thread(target=self._idle_monitor_loop, daemon=True, name="goengine-idle")
        t_idle.start()
        self._threads.append(t_idle)

        speech = bytearray()
        speech_frames = 0
        silence_frames = 0
        barge_in_frames = 0
        # Ring-buffer pre-trigger (spec 2.4): ultimi frame RX raccolti durante SPEAKING,
        # inoltrati a STT quando scatta il barge-in → le prime parole non si perdono.
        rx_ring: "deque[bytes]" = deque(maxlen=RX_PRETRIGGER_FRAMES)

        while self._running and not self._stop_evt.is_set():
            try:
                frame = self.rx_queue.get(timeout=0.1)
            except queue.Empty:
                continue
            if len(frame) < 2:
                continue

            rms = self._rms(frame)
            sara_speaking = self._is_sara_speaking()

            if sara_speaking:
                # Echo-floor adattivo (spec 2.2): media mobile dell'RMS RX mentre Sara
                # parla = livello dell'eco di linea da superare per un barge-in vero.
                self._echo_floor = (
                    (1.0 - ECHO_FLOOR_ALPHA) * self._echo_floor + ECHO_FLOOR_ALPHA * rms
                )
                rx_ring.append(frame)
                # Trigger adattivo: sopra sia la soglia base sia k×echo_floor, sostenuto.
                thr = max(BARGE_IN_MARGIN, BARGE_IN_K * self._echo_floor)
                if rms > thr:
                    barge_in_frames += 1
                    if barge_in_frames >= BARGE_IN_SUSTAIN:
                        logger.info(
                            "BARGE-IN: rms=%.0f thr=%.0f floor=%.0f (pre=%d frame)",
                            rms, thr, self._echo_floor, len(rx_ring),
                        )
                        self.clear_tx()  # svuota TX + stop invio + fine grace
                        # Idle-timeout (FASE 3.0): il chiamante ha parlato → riarma il timer.
                        self._last_caller_voice_ts = time.monotonic()
                        self._idle_reprompted = False
                        # Inoltra il buffer pre-trigger a STT (spec 2.4).
                        speech = bytearray()
                        for f in rx_ring:
                            speech.extend(f)
                        speech_frames = len(speech) // FRAME_BYTES
                        silence_frames = 0
                        barge_in_frames = 0
                        rx_ring.clear()
                else:
                    barge_in_frames = 0
                continue

            # VAD normale.
            if rms > VAD_SPEECH_THRESHOLD:
                speech_frames += 1
                silence_frames = 0
                speech.extend(frame)
                # Idle-timeout (FASE 3.0): parlato reale del chiamante → riarma il timer.
                self._last_caller_voice_ts = time.monotonic()
                self._idle_reprompted = False
            else:
                if speech_frames > 0:
                    silence_frames += 1
                    speech.extend(frame)

            if speech_frames >= VAD_MIN_SPEECH_FRAMES and silence_frames >= VAD_SILENCE_TIMEOUT:
                full_audio = bytes(speech)
                speech.clear()
                speech_frames = 0
                silence_frames = 0
                if full_audio and self.pipeline and self._main_loop is not None:
                    turn_rms = self._rms(full_audio)
                    dur_ms = len(full_audio) / 16  # 8k 16-bit = 16 B/ms
                    if dur_ms < 300 or turn_rms < VAD_SPEECH_THRESHOLD:
                        continue
                    self._process_caller_audio(full_audio)

    def _process_caller_audio(self, audio_8k: bytes):
        """Upsample 8k→16k → pipeline.process_audio → queue_tts_audio (§2/§4)."""
        try:
            audio_16k, _ = audioop.ratecv(audio_8k, 2, 1, 8000, 16000, None)
            fut = asyncio.run_coroutine_threadsafe(
                self.pipeline.process_audio(audio_16k), self._main_loop
            )
            result = fut.result(timeout=15)
            self.last_turn_result = result
            # Log del turno REALE in conversation_turns (stesso writer letto da
            # /api/metrics/latency). Alimenta get_percentile_stats(count). Best-effort.
            self._log_turn_analytics(result)
            if result and result.get("audio_response") is not None:
                self.queue_tts_audio(result["audio_response"])
                logger.info("risposta TTS in coda TX (%dB)", len(result["audio_response"]))
            if result and result.get("should_exit"):
                # FSM-HANGUP GUARD (FASE 2 spec 2.3): Sara NON riaggancia mai per prima.
                # should_exit ha molte origini nella FSM (booking done, confusione,
                # garbage bare-name); riagganciamo SOLO su intento di congedo esplicito
                # (mutuo "arrivederci"). Su ogni altro should_exit Sara resta in linea →
                # è il chiamante a chiudere. Elimina l'auto-hangup su STT sporco del GATE B.
                _intent = (result.get("intent") or "").lower()
                _explicit_goodbye = ("goodbye" in _intent) or ("chiusura" in _intent)
                if _explicit_goodbye:
                    # Hangup dopo che la coda TX si svuota.
                    threading.Thread(target=self._hangup_after_drain, daemon=True).start()
                else:
                    logger.info(
                        "HANGUP soppresso (FSM-guard): should_exit ma intent non-congedo "
                        "(%r) — Sara resta in linea", _intent,
                    )
        except Exception as exc:
            logger.warning("process_caller_audio errore: %s", exc, exc_info=True)

    def _log_turn_analytics(self, result: Optional[Dict[str, Any]]):
        """Scrive il turno reale in conversation_turns via analytics (best-effort).

        Usa la STESSA istanza singleton `get_logger()` che /api/metrics/latency LEGGE
        (main.py:858) → il count della metrica sale su OGNI turno di chiamata reale.
        Salta turni vuoti (STT nullo / nessuna risposta) per non gonfiare la metrica.
        """
        if self._analytics is None or not result:
            return
        transcription = (result.get("transcription") or "").strip()
        # STT vuoto o mishear rifiutato → nessun turno significativo, non loggare.
        if not transcription or transcription.startswith("[rejected:"):
            return
        try:
            if self._analytics_sid is None:
                verticale = getattr(self.pipeline, "verticale_id", None) or self._verticale_id
                self._analytics_sid = self._analytics.start_session(verticale)
            self._analytics.log_turn(
                session_id_or_turn=self._analytics_sid,
                user_input=transcription,
                response=result.get("text", "") or "",
                latency_ms=float(result.get("latency_ms") or 0.0),
                layer_used="voip_go",
                used_groq=False,
            )
            logger.info(
                "turno reale loggato in conversation_turns (latency=%sms)",
                result.get("latency_ms"),
            )
        except Exception as exc:
            logger.warning("analytics.log_turn errore: %s", exc)

    def _hangup_after_drain(self):
        deadline = time.time() + 10
        while time.time() < deadline and not self._tx_queue.empty():
            time.sleep(0.1)
        time.sleep(0.5)
        self._send_frame(FRAME_HANGUP, b"")

    def _idle_monitor_loop(self):
        """FASE 3.0: idle-timeout a livello CHIAMATA (2ª gamba legittima dell'hangup).

        Misura il silenzio COMBINATO: né Sara parla (TX/grace) né il chiamante parla.
        Durante il TX di Sara non conta (il chiamante ascolta). Dopo IDLE_REPROMPT_S di
        silenzio → UN reprompt ("è ancora in linea?"). Se dopo IDLE_HANGUP_S dalla fine
        del reprompt è ancora muto → congedo cortese + hangup legittimo. Il timer si
        riarma appena il chiamante parla (in _audio_processing_loop).

        Distinto dalla FSM-HANGUP GUARD (spec 2.3): quella sopprime l'auto-hangup su STT
        sporco; questo è l'UNICO altro hangup lecito per Sara oltre al congedo esplicito.
        """
        while self._running and not self._stop_evt.is_set():
            if self._stop_evt.wait(0.5):
                break
            if not self._call_active:
                self._idle_reprompted = False
                continue
            # Sara sta parlando (TX in coda o grace): non è silenzio della chiamata.
            if self._is_sara_speaking():
                continue
            now = time.monotonic()
            # Riferimento silenzio = ultimo evento audio: parlato chiamante O ultimo TX Sara
            # (così il conteggio parte dalla fine del parlato di Sara, non da metà).
            last_audio = max(self._last_caller_voice_ts, self._tx_last_frame_ts)
            if not self._idle_reprompted:
                if now - last_audio >= IDLE_REPROMPT_S:
                    logger.info("IDLE: %.0fs di silenzio chiamante → reprompt", now - last_audio)
                    self._idle_reprompted = True
                    self._idle_reprompt_ts = now
                    self._speak_canned(IDLE_REPROMPT_TEXT)
            else:
                # Già repromptato: misura il silenzio DOPO che il reprompt ha finito di suonare.
                since = now - max(self._idle_reprompt_ts, self._tx_last_frame_ts)
                if since >= IDLE_HANGUP_S:
                    logger.info(
                        "HANGUP timeout-silenzio: chiamante muto %.0fs dopo il reprompt", since,
                    )
                    self._speak_canned(IDLE_GOODBYE_TEXT)
                    self._idle_reprompted = False
                    # Congedo + chiusura legittima dopo che la coda TX si svuota.
                    self._hangup_after_drain()

    def _speak_canned(self, text: str):
        """Sintetizza una frase canned (reprompt/congedo) e la mette in coda TX.

        Usa la STESSA TTS del cervello (pipeline.tts.synthesize) → voce coerente e stesso
        sink provato (queue_tts_audio, GATE 2R). Best-effort: mai sollevare nel monitor.
        """
        if not self.pipeline or self._main_loop is None:
            return
        tts = getattr(self.pipeline, "tts", None)
        if tts is None:
            logger.warning("_speak_canned: pipeline.tts assente, salto %r", text)
            return
        try:
            fut = asyncio.run_coroutine_threadsafe(tts.synthesize(text), self._main_loop)
            audio = fut.result(timeout=15)
            if audio:
                self.queue_tts_audio(audio)
                logger.info("canned TTS in coda TX: %r", text)
        except Exception as exc:
            logger.warning("_speak_canned errore: %s", exc)

    @staticmethod
    def _rms(pcm: bytes) -> float:
        if len(pcm) < 2:
            return 0.0
        return float(audioop.rms(pcm, 2))
