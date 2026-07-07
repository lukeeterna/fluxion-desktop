#!/usr/bin/env python3
"""selftest.py — SELFTEST SENZA TRUNK del media-swap Go (GATE 1, T-SARA-MEDIASWAP).

Simula una chiamata locale SENZA SIP/trunk:
  - istanzia la pipeline Sara REALE + GoEngineVoIPManager,
  - fa da FAKE-ENGINE (client TCP sul ponte): invia CALL_START + un WAV 8k come
    sequenza di frame AUDIO_RX, e CATTURA gli AUDIO_TX in uscita.

PROVA:
  (a) rx_queue riceve e la pipeline processa → /api/metrics/latency count>0
      (verificato leggendo analytics.get_percentile_stats PRIMA/DOPO).
  (b) il TTS torna come AUDIO_TX cadenzato (conteggio frame catturati > 0).
  (c) il barge-in taglia la coda TX (clear_tx svuota _tx_queue).

Output grezzi committati in .claude/cache/T-SARA-MEDIASWAP/.
Non tocca SIP, non registra sul trunk, non tocca la Sara live (usa istanza propria
in-process con VoIP disabilitato).
"""
import asyncio
import io
import json
import os
import socket
import struct
import sys
import time
import wave

HERE = os.path.dirname(os.path.abspath(__file__))
VA_ROOT = os.path.dirname(HERE)  # voice-agent/
sys.path.insert(0, VA_ROOT)

# Ponte su porta dedicata al selftest (evita collisioni con eventuale engine live).
BRIDGE_PORT = 8399

FRAME_STATUS = 0x01
FRAME_CALL_START = 0x02
FRAME_AUDIO_RX = 0x03
FRAME_CALL_END = 0x04
FRAME_AUDIO_TX = 0x10
FRAME_HANGUP = 0x11

OUT_DIR = os.path.abspath(os.path.join(VA_ROOT, "..", ".claude", "cache", "T-SARA-MEDIASWAP"))
os.makedirs(OUT_DIR, exist_ok=True)


def make_wav_8k(seconds: float = 1.2, freq: float = 300.0) -> bytes:
    import math
    sr = 8000
    n = int(sr * seconds)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        frames = bytearray()
        amp = 0.6 * 32767
        for i in range(n):
            v = int(amp * math.sin(2 * math.pi * freq * i / sr))
            frames += struct.pack("<h", v)
        wf.writeframes(bytes(frames))
    return buf.getvalue()


def send_frame(sock, typ, payload=b""):
    sock.sendall(bytes([typ]) + struct.pack(">H", len(payload)) + payload)


def recv_exact(sock, n):
    buf = bytearray()
    while len(buf) < n:
        c = sock.recv(n - len(buf))
        if not c:
            return None
        buf += c
    return bytes(buf)


class FakeEngine:
    """Fake-engine lato client TCP: inietta AUDIO_RX, cattura AUDIO_TX."""

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.audio_tx_frames = []
        self.stop = False

    def run(self, wav_pcm_frames, log):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for _ in range(50):
            try:
                s.connect((self.host, self.port))
                break
            except OSError:
                time.sleep(0.1)
        else:
            log("FAKE-ENGINE: impossibile connettersi al ponte")
            return
        log(f"FAKE-ENGINE: connesso al ponte {self.host}:{self.port}")
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        # Emetti STATUS + CALL_START.
        send_frame(s, FRAME_STATUS, json.dumps(
            {"registered": True, "reg_status": 200, "username": "selftest", "server": "local"}
        ).encode())
        send_frame(s, FRAME_CALL_START, b"selftest-caller")
        log("FAKE-ENGINE: STATUS+CALL_START inviati")

        # Thread ricezione AUDIO_TX.
        import threading
        def rx():
            s.settimeout(0.5)
            while not self.stop:
                try:
                    hdr = recv_exact(s, 3)
                except (socket.timeout, TimeoutError):
                    continue
                except OSError:
                    return
                if hdr is None:
                    return
                (ln,) = struct.unpack(">H", hdr[1:3])
                pl = recv_exact(s, ln) if ln else b""
                if hdr[0] == FRAME_AUDIO_TX:
                    self.audio_tx_frames.append(pl)
        t = threading.Thread(target=rx, daemon=True)
        t.start()

        # Inietta il WAV come AUDIO_RX cadenzati 20ms (turn), poi silenzio per chiudere il turno.
        for f in wav_pcm_frames:
            send_frame(s, FRAME_AUDIO_RX, f)
            time.sleep(0.02)
        # Silenzio: 60 frame (~1.2s) per superare VAD_SILENCE_TIMEOUT (50).
        silence = b"\x00" * 320
        for _ in range(60):
            send_frame(s, FRAME_AUDIO_RX, silence)
            time.sleep(0.02)
        log("FAKE-ENGINE: RX turn injected, attendo risposta TTS")

        # Attendi che arrivino AUDIO_TX (fino a 25s: STT Groq + TTS).
        deadline = time.time() + 25
        while time.time() < deadline and len(self.audio_tx_frames) == 0:
            time.sleep(0.2)
        # Lascia accumulare qualche frame TTS.
        time.sleep(2.0)
        self.stop = True
        send_frame(s, FRAME_CALL_END, b"")
        s.close()


def frame_wav(wav_bytes):
    with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
        pcm = wf.readframes(wf.getnframes())
    frames = []
    for i in range(0, len(pcm), 320):
        c = pcm[i:i + 320]
        if len(c) < 320:
            c = c + b"\x00" * (320 - len(c))
        frames.append(c)
    return frames


async def main():
    log_lines = []
    def log(m):
        line = f"[{time.strftime('%H:%M:%S')}] {m}"
        print(line, flush=True)
        log_lines.append(line)

    log("=== SELFTEST MEDIASWAP GATE 1 ===")

    # 1) analytics count PRIMA.
    from src.analytics import get_logger
    alog = get_logger()
    before = alog.get_percentile_stats(hours=24)
    log(f"analytics latency count PRIMA: {before.get('count')}")

    # 2) pipeline REALE (stessi argomenti di main.py:1129).
    from src.orchestrator import VoiceOrchestrator
    verticale_id = os.getenv("SELFTEST_VERTICALE", "salone")
    business_name = os.getenv("SELFTEST_BUSINESS", "Studio Demo")
    groq_key = os.getenv("GROQ_API_KEY", "").strip() or None
    orch = VoiceOrchestrator(
        verticale_id=verticale_id,
        business_name=business_name,
        groq_api_key=groq_key,
        use_piper_tts=True,
    )
    log(f"orchestrator inizializzato (verticale={verticale_id}, business={business_name})")

    # 3) adapter Go-engine (SENZA spawnare l'engine: siamo noi il fake-engine).
    from src.voip_goengine import GoEngineVoIPManager, SIPConfig
    cfg = SIPConfig(username="selftest", password="x", server="local")
    mgr = GoEngineVoIPManager(cfg, bridge_port=BRIDGE_PORT)
    mgr.set_pipeline(orch)
    mgr._main_loop = asyncio.get_running_loop()

    # Avvia SOLO il ponte + loop audio, NON il supervisor engine (niente SIP).
    mgr._srv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mgr._srv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    mgr._srv_sock.bind((mgr.bridge_host, mgr.bridge_port))
    mgr._srv_sock.listen(1)
    mgr._running = True
    mgr._stop_evt.clear()
    import threading
    threading.Thread(target=mgr._accept_loop, daemon=True).start()
    threading.Thread(target=mgr._audio_processing_loop, daemon=True).start()
    log(f"adapter avviato, ponte in ascolto su :{BRIDGE_PORT}")

    # 4) fake-engine: inietta un WAV di PARLATO REALE (così Whisper trascrive → turno
    #    loggato in analytics → count>0). Generiamo il parlato con la TTS di Sara stessa,
    #    poi lo ricampioniamo a 8k (è ciò che l'engine consegnerebbe da RTP G.711).
    import audioop
    speech_wav16 = None
    try:
        tts_bytes = await orch.tts.synthesize("Buongiorno, vorrei prenotare un taglio per domani.")
        if tts_bytes and tts_bytes[:4] == b"RIFF":
            with wave.open(io.BytesIO(tts_bytes), "rb") as wf:
                sr = wf.getframerate()
                pcm = wf.readframes(wf.getnframes())
            if sr != 8000:
                pcm, _ = audioop.ratecv(pcm, 2, 1, sr, 8000, None)
            # ri-incapsula 8k mono 16-bit
            b = io.BytesIO()
            with wave.open(b, "wb") as wf:
                wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(8000)
                wf.writeframes(pcm)
            speech_wav16 = b.getvalue()
            log(f"parlato TTS generato per RX: {len(pcm)}B @8k")
    except Exception as exc:
        log(f"TTS parlato non disponibile ({exc}), fallback tono")
    wav = speech_wav16 if speech_wav16 else make_wav_8k()
    frames = frame_wav(wav)
    fe = FakeEngine(mgr.bridge_host, mgr.bridge_port)
    threading.Thread(target=fe.run, args=(frames, log), daemon=True).start()

    # Attendi elaborazione del turno REALE (fino a 60s: STT tiny ~5s + pipeline + TTS).
    deadline = time.time() + 60
    while time.time() < deadline:
        if mgr.last_turn_result is not None and len(fe.audio_tx_frames) > 0:
            break
        await asyncio.sleep(0.5)
    # Lascia accumulare la coda TX della risposta.
    await asyncio.sleep(2.0)

    tx_count = len(fe.audio_tx_frames)
    log(f"(b) AUDIO_TX catturati: {tx_count} frame ({tx_count*20}ms)")

    # (a) La pipeline ha processato il turno RX reale?
    ltr = mgr.last_turn_result
    turn_ok = bool(ltr and ltr.get("transcription") and ltr.get("audio_response") is not None)
    if ltr:
        log(f"(a) turno pipeline: STT='{ltr.get('transcription','')[:60]}' → "
            f"resp='{ltr.get('text','')[:60]}' latency={ltr.get('latency_ms')}ms audio={len(ltr.get('audio_response') or b'')}B")
    # ONESTÀ SELFTEST (GATE 1): NON registriamo più il turno a mano qui.
    # La scrittura di conversation_turns avviene NEL PATH DI PRODUZIONE
    # (voip_goengine._process_caller_audio → _log_turn_analytics), lo stesso che
    # gira su chiamata reale. Se il count NON sale sotto, il wiring #1 è rotto
    # (da correggere nell'adapter, NON re-iniettando qui).

    # 5) test barge-in (c): riempi TX e verifica clear_tx.
    mgr.queue_tts_audio(wav)  # riempie _tx_queue
    filled = mgr._tx_queue.qsize()
    mgr.clear_tx()
    after_clear = mgr._tx_queue.qsize()
    barge_ok = filled > 0 and after_clear == 0
    log(f"(c) barge-in: TX riempita={filled} → dopo clear_tx={after_clear} → {'OK' if barge_ok else 'FAIL'}")

    # 6) analytics count DOPO.
    after = alog.get_percentile_stats(hours=24)
    count_up = (after.get("count", 0) or 0) > (before.get("count", 0) or 0)
    log(f"analytics latency count: {before.get('count')} → {after.get('count')} (count>0: {count_up})")
    # (a) VERDE se la pipeline ha processato il turno RX reale (turn_ok) E il count
    #     della metrica sale. turn_ok è la prova sostanziale RX→pipeline→TTS.
    rx_ok = turn_ok and count_up
    log(f"(a) rx_queue→pipeline→metrica: turn_ok={turn_ok} count>0={count_up} → {'OK' if rx_ok else 'FAIL'}")

    # 7) cattura WAV TX per evidenza.
    if fe.audio_tx_frames:
        tx_pcm = b"".join(fe.audio_tx_frames)
        tx_wav_path = os.path.join(OUT_DIR, "selftest_tx_capture.wav")
        with wave.open(tx_wav_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(8000)
            wf.writeframes(tx_pcm)
        log(f"WAV TX catturato: {tx_wav_path} ({len(tx_pcm)}B)")

    # Verdetto.
    verdict = "VERDE" if (rx_ok and tx_count > 0 and barge_ok) else "ROSSO"
    log(f"=== VERDETTO GATE 1 SELFTEST: {verdict} ===")

    metrics = {
        "verdict": verdict,
        "rx_ok_a": rx_ok,
        "turn_ok": turn_ok,
        "transcription": (ltr or {}).get("transcription"),
        "response": (ltr or {}).get("text"),
        "turn_latency_ms": (ltr or {}).get("latency_ms"),
        "analytics_count_before": before.get("count"),
        "analytics_count_after": after.get("count"),
        "audio_tx_frames_b": tx_count,
        "barge_in_ok_c": barge_ok,
        "tx_filled": filled,
        "tx_after_clear": after_clear,
    }
    with open(os.path.join(OUT_DIR, "selftest_metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    with open(os.path.join(OUT_DIR, "selftest.log"), "w") as f:
        f.write("\n".join(log_lines) + "\n")

    mgr._running = False
    mgr._stop_evt.set()
    return 0 if verdict == "VERDE" else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
