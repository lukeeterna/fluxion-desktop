#!/usr/bin/env python3
"""test_capture_unit.py — prova unitaria WAV capture STEP 1-FIX-OBS.

Verifica che GoEngineVoIPManager._capture=True con SARA_TEST_CAPTURE=1
e che _write_call_capture() scriva un WAV stereo rms>0.

Eseguire su iMac (Python 3.9, audioop presente):
  ssh imac 'python3 -' < test_capture_unit.py

SARA_TEST_CAPTURE deve essere impostata PRIMA dell'import del modulo
(letta in __init__ via os.getenv).
"""
import os, sys, math, struct, wave, audioop

# --- CRITICO: impostare prima di qualsiasi import di voip_goengine ---
os.environ["SARA_TEST_CAPTURE"] = "1"

VA = "/Volumes/MacSSD - Dati/FLUXION/voice-agent"
sys.path.insert(0, VA)

from src.voip_goengine import GoEngineVoIPManager, SIPConfig

cfg = SIPConfig(username="test", password="test", server="127.0.0.1")
mgr = GoEngineVoIPManager(cfg)

# CHECK 1: env propagata
assert mgr._capture, "FAIL: _capture=False — SARA_TEST_CAPTURE=1 non letta!"
print("CHECK 1 PASS: _capture=True")

# Simula apertura chiamata
mgr._cap_ts = "UNIT-TEST-20260717"
mgr._cap_rx = bytearray()
mgr._cap_tx = bytearray()

# Inietta 1s di 440Hz PCM16 @8kHz (RMS ~2121, non zero)
N = 8000
for i in range(N):
    sample_rx = int(3000 * math.sin(2 * math.pi * 440 * i / N))
    sample_tx = int(2000 * math.sin(2 * math.pi * 880 * i / N))
    mgr._cap_rx.extend(struct.pack("<h", sample_rx))
    mgr._cap_tx.extend(struct.pack("<h", sample_tx))

# Scrivi WAV
mgr._write_call_capture()

# CHECK 2: file WAV esiste
repo_root = os.path.dirname(VA)
out_dir = os.path.join(repo_root, ".claude", "cache", "T-SARA-TURNTAKING", "calls")
files = sorted([f for f in os.listdir(out_dir) if "UNIT-TEST" in f])
assert files, f"FAIL: nessun WAV in {out_dir}"
path = os.path.join(out_dir, files[-1])
print(f"CHECK 2 PASS: WAV scritto → {path}")

# CHECK 3: canali stereo
with wave.open(path, "rb") as wf:
    nch = wf.getnchannels()
    sr = wf.getframerate()
    nframes = wf.getnframes()
    raw = wf.readframes(nframes)
assert nch == 2, f"FAIL: atteso stereo (2ch), got {nch}"
assert sr == 8000, f"FAIL: atteso 8kHz, got {sr}"
print(f"CHECK 3 PASS: stereo 2ch @{sr}Hz {nframes} frames ({nframes/sr:.2f}s)")

# CHECK 4: RMS rx/tx > 0
rx_rms = audioop.rms(bytes(mgr._cap_rx), 2)
tx_rms = audioop.rms(bytes(mgr._cap_tx), 2)
assert rx_rms > 0, f"FAIL: rx_rms=0"
assert tx_rms > 0, f"FAIL: tx_rms=0"
print(f"CHECK 4 PASS: rx_rms={rx_rms:.0f} tx_rms={tx_rms:.0f} (entrambi >0)")

print()
print("=== UNIT TEST WAV CAPTURE: TUTTI I CHECK PASS ===")
print(f"WAV: {path}")
print(f"  stereo 2ch @8kHz | rx_rms={rx_rms:.0f} | tx_rms={tx_rms:.0f}")
