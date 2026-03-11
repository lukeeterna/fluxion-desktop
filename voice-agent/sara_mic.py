#!/usr/bin/env python3
"""
sara_mic.py — Parla con Sara via microfono reale
Premi INVIO per iniziare a registrare, INVIO di nuovo per fermare.
"""
import json
import urllib.request
import sounddevice as sd
import numpy as np
import wave
import tempfile
import os
import base64
import subprocess

BASE = "http://127.0.0.1:3002"
SAMPLE_RATE = 16000

def post(path, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(
        BASE + path, data=body,
        headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read())

def record_until_enter():
    print("  🎙  Registrazione... premi INVIO per fermare")
    frames = []
    recording = [True]

    def callback(indata, frame_count, time_info, status):
        if recording[0]:
            frames.append(indata.copy())

    stream = sd.InputStream(samplerate=SAMPLE_RATE, channels=1,
                            dtype='int16', callback=callback, device=0)
    stream.start()
    input()
    recording[0] = False
    stream.stop()
    stream.close()

    if not frames:
        return None
    audio = np.concatenate(frames, axis=0)
    return audio

def save_wav(audio):
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    with wave.open(tmp.name, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(audio.tobytes())
    return tmp.name

def play_audio_base64(b64):
    try:
        wav_bytes = base64.b64decode(b64)
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp.write(wav_bytes)
        tmp.close()
        subprocess.run(["afplay", tmp.name], check=False)
        os.unlink(tmp.name)
    except Exception as e:
        print(f"  [audio play error: {e}]")

def process_audio(wav_path):
    """Invia WAV a Sara via audio_hex → STT + pipeline completa"""
    with open(wav_path, 'rb') as f:
        audio_hex = f.read().hex()
    return post("/api/voice/process", {"audio_hex": audio_hex})

def main():
    print("=" * 55)
    print("  FLUXION — Sara Voice Test (microfono reale)")
    print("  Premi INVIO per registrare, INVIO per fermare")
    print("  Digita 'quit' per uscire | 'reset' per nuova sessione")
    print("=" * 55)

    # Reset sessione
    post("/api/voice/reset", {})
    print("  ✅ Sessione resettata\n")

    while True:
        cmd = input("👤 [INVIO=parla / reset / quit] > ").strip().lower()

        if cmd == "quit":
            print("  Ciao!")
            break

        if cmd == "reset":
            post("/api/voice/reset", {})
            print("  ✅ Sessione resettata\n")
            continue

        # Registra audio
        audio = record_until_enter()
        if audio is None or len(audio) < 1600:
            print("  ⚠️  Audio troppo corto, riprova\n")
            continue

        duration = len(audio) / SAMPLE_RATE
        print(f"  📼 Registrati {duration:.1f}s — trascrivo...")

        # Salva WAV e prova STT
        wav_path = save_wav(audio)
        print(f"  ⏳ Invio a Sara (STT + pipeline)...")

        # Invia audio direttamente a Sara
        try:
            r = process_audio(wav_path)
            os.unlink(wav_path)

            transcription = r.get("transcription", "?")
            response = r.get("response", "?")
            intent = r.get("intent", "?")
            fsm = r.get("fsm_state", "?")
            latency = r.get("latency_ms", "?")
            audio_b64 = r.get("audio_base64", "")

            print(f"  📝 STT: \"{transcription}\"")
            print(f"\n  🤖 Sara: \"{response}\"")
            print(f"     intent={intent} | fsm={fsm} | {latency}ms\n")

            if audio_b64:
                play_audio_base64(audio_b64)

        except Exception as e:
            print(f"  ❌ Errore: {e}\n")

if __name__ == "__main__":
    main()
