#!/usr/bin/env python3
"""pyrtp_spike.py -- T-SARA-PYRTP-SPIKE (GO/NO-GO modello prodotto Sara on-premise).

Falsifica: "pyVoIP regge REGISTER + inbound + audio DUPLEX sul trunk EHIWEB".

VINCOLO PORTABILITA' (antenato del media-layer che girera' su Windows dal cliente):
  SOLO stdlib + pyVoIP. ZERO comandi OS (niente say/afconvert/ffmpeg). ZERO .so custom.

FORMATO AUDIO -- verificato dal sorgente reale pyVoIP 1.6.8 RTP.py (vince il disco):
  parse_pcmu : audioop.ulaw2lin(payload,1) + bias(+128)  -> read_audio() ritorna
               8-bit UNSIGNED PCM, mono, 8000 Hz, silenzio = 0x80.
  encode_pcmu: bias(-128) + audioop.lin2ulaw(.,1)        -> write_audio() SI ASPETTA
               8-bit UNSIGNED PCM, mono, 8000 Hz.
  => il beep e' generato 8-bit unsigned (128 +/- amp); l'echo write_audio(read_audio())
     e' byte-identico (nessuna conversione); RMS su segnale de-biasato.

PIANO NAT:
  A (default) = beep-first: appena risposto trasmetto ~2s di 440Hz per aprire il pinhole
                UDP attraverso il NAT e far latchare il ritorno RTP simmetrico del gateway.
  B (una sola iterazione, se i pacchetti UDP non arrivano proprio) = annunciare in SDP l'IP
                pubblico mantenendo bind locale (patch minima nel venv), poi UN ritest.

Uso:
  python pyrtp_spike.py --sip-port 5080 --rtp-low 4000 --rtp-high 4020 \
                        --my-ip 192.168.1.2 --wav capture_rx.wav --max-secs 120
Credenziali: env VOIP_SIP_USER / VOIP_SIP_PASS / VOIP_SIP_SERVER / VOIP_SIP_PORT.
"""
import os
import sys
import math
import time
import wave
import argparse
import audioop
import datetime

from pyVoIP.VoIP import VoIPPhone, VoIPCall, CallState, PhoneStatus

RATE = 8000
FRAME = 160  # 20 ms @ 8 kHz, 8-bit -> 160 byte

_state = {"call_done": False, "wav_path": None, "spoken_rms_max": 0, "total_rx": 0}


def log(msg):
    ts = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print("[spike %s] %s" % (ts, msg), flush=True)


def gen_beep_u8(freq=440, secs=2.0, amp=90):
    """Sinusoide 8-bit UNSIGNED centrata a 128 (formato write_audio)."""
    n = int(RATE * secs)
    buf = bytearray(n)
    for i in range(n):
        v = 128 + int(amp * math.sin(2.0 * math.pi * freq * i / RATE))
        buf[i] = 0 if v < 0 else (255 if v > 255 else v)
    return bytes(buf)


def rms_u8(buf):
    """RMS su buffer 8-bit unsigned: de-bias a signed, poi audioop.rms width=1."""
    if not buf:
        return 0
    return audioop.rms(audioop.bias(buf, 1, -128), 1)


def handle_call(call):
    """callCallback: pyVoIP invoca in un thread nuovo all'arrivo dell'INVITE."""
    try:
        log("INBOUND INVITE ricevuto -> answer()")
        call.answer()
        log("ANSWERED -- invio beep-first (Piano A latching)")

        beep = gen_beep_u8(freq=440, secs=2.0, amp=90)
        for off in range(0, len(beep), FRAME):
            call.write_audio(beep[off:off + FRAME])
            time.sleep(0.02)
        log("beep inviato (%d byte)" % len(beep))

        wav = wave.open(_state["wav_path"], "wb")
        wav.setnchannels(1)
        wav.setsampwidth(1)   # 8-bit unsigned (WAV spec) == formato read_audio
        wav.setframerate(RATE)

        start = time.time()
        last = start
        sec_buf = bytearray()
        sec_idx = 0
        total_rx = 0
        max_secs = _state["max_secs"]

        while (time.time() - start) < max_secs:
            st = getattr(call, "state", None)
            if st is not None and st != CallState.ANSWERED:
                log("call.state=%s -> esco dal loop" % st)
                break
            try:
                data = call.read_audio(FRAME, blocking=False)
            except Exception as e:
                log("read_audio errore: %r" % e)
                break
            if data:
                call.write_audio(data)      # ECO
                wav.writeframes(data)        # cattura RX
                sec_buf += data
                total_rx += len(data)
            time.sleep(0.02)

            if (time.time() - last) >= 1.0:
                r = rms_u8(bytes(sec_buf))
                if r > _state["spoken_rms_max"]:
                    _state["spoken_rms_max"] = r
                log("t=%2ds  frames_rx~%3d  bytes_rx=%5d  RMS=%d"
                    % (sec_idx, len(sec_buf) // FRAME, len(sec_buf), r))
                sec_buf = bytearray()
                last = time.time()
                sec_idx += 1

        wav.close()
        _state["total_rx"] = total_rx
        log("fine loop call: total_rx=%d byte  rms_max=%d  wav=%s"
            % (total_rx, _state["spoken_rms_max"], _state["wav_path"]))
    except Exception as e:
        log("handle_call EXCEPTION: %r" % e)
    finally:
        try:
            call.hangup()
            log("hangup() eseguito")
        except Exception:
            pass
        _state["call_done"] = True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sip-port", type=int, default=5080)
    ap.add_argument("--rtp-low", type=int, default=4000)
    ap.add_argument("--rtp-high", type=int, default=4020)
    ap.add_argument("--my-ip", default="192.168.1.2")
    ap.add_argument("--wav", default="capture_rx.wav")
    ap.add_argument("--max-secs", type=int, default=120)
    ap.add_argument("--reg-timeout", type=int, default=15)
    args = ap.parse_args()

    server = os.environ.get("VOIP_SIP_SERVER")
    user = os.environ.get("VOIP_SIP_USER")
    passwd = os.environ.get("VOIP_SIP_PASS")
    srv_port = int(os.environ.get("VOIP_SIP_PORT", "5060"))
    if not (server and user and passwd):
        log("ERRORE: VOIP_SIP_SERVER/USER/PASS non presenti nell'ambiente")
        sys.exit(3)

    _state["wav_path"] = args.wav
    _state["max_secs"] = args.max_secs

    log("VoIPPhone: server=%s:%d user=%s myIP=%s sipPort=%d rtp=%d-%d"
        % (server, srv_port, user, args.my_ip, args.sip_port, args.rtp_low, args.rtp_high))

    phone = VoIPPhone(
        server, srv_port, user, passwd,
        myIP=args.my_ip,
        callCallback=handle_call,
        sipPort=args.sip_port,
        rtpPortLow=args.rtp_low,
        rtpPortHigh=args.rtp_high,
    )
    phone.start()

    deadline = time.time() + args.reg_timeout
    status = None
    while time.time() < deadline:
        status = phone.get_status()
        if status == PhoneStatus.REGISTERED:
            break
        if status == PhoneStatus.FAILED:
            log("ROSSO-REGISTER: PhoneStatus.FAILED")
            phone.stop()
            sys.exit(2)
        time.sleep(0.3)

    if status != PhoneStatus.REGISTERED:
        log("ROSSO-REGISTER: timeout, ultimo status=%s" % status)
        phone.stop()
        sys.exit(2)

    log("REGISTER ok -> status=%s" % status)
    print("=" * 60, flush=True)
    print("PRONTO -- chiama ORA il  0972536918 , ascolta il beep, parla",
          flush=True)
    print("~20 secondi verificando l'ECO della TUA voce, poi riaggancia.",
          flush=True)
    print("=" * 60, flush=True)

    # attesa call o max complessivo (self-stop portabile, no signal.alarm)
    overall_deadline = time.time() + args.max_secs + 60
    while not _state["call_done"] and time.time() < overall_deadline:
        time.sleep(0.5)

    log("de-REGISTER / stop phone")
    try:
        phone.stop()
    except Exception:
        pass

    # verdetto grezzo (la prova la valida il founder + il WAV su disco)
    print("---SPIKE-RESULT--- rms_max=%d total_rx=%d wav=%s"
          % (_state["spoken_rms_max"], _state["total_rx"], _state["wav_path"]),
          flush=True)


if __name__ == "__main__":
    main()
