#!/usr/bin/env python3
"""
VAD Microphone Demo
===================

Demonstrates real-time VAD with microphone input.
Press Ctrl+C to stop.

Requirements:
    pip install sounddevice numpy ten-vad

Usage:
    python vad_microphone_demo.py
"""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import sounddevice as sd
from src.vad import FluxionVAD, VADConfig

# Audio config
SAMPLE_RATE = 16000
CHANNELS = 1
BLOCKSIZE = 1600  # 100ms at 16kHz


def main():
    print("=" * 60)
    print("Fluxion VAD Microphone Demo")
    print("=" * 60)
    print("\nUsing TEN VAD for voice activity detection")
    print("Speak into your microphone to test.\n")
    print("Press Ctrl+C to stop.\n")

    # Configure VAD
    config = VADConfig(
        vad_threshold=0.5,
        silence_duration_ms=700,
        prefix_padding_ms=300
    )

    vad = FluxionVAD(config)
    vad.start()

    turn_audio = []
    is_recording = False

    def audio_callback(indata, frames, time_info, status):
        nonlocal turn_audio, is_recording

        if status:
            print(f"Status: {status}")

        # Convert to bytes
        audio_bytes = (indata[:, 0] * 32767).astype(np.int16).tobytes()

        # Process through VAD
        result = vad.process_audio(audio_bytes)

        # Visual indicator
        prob_bar = "█" * int(max(0, result.probability) * 20)
        state_icon = "🎤" if result.state.name == "SPEAKING" else "  "

        print(f"\r{state_icon} [{prob_bar:<20}] {result.probability:+.2f} ", end="")

        # Handle events
        if result.event == "start_of_speech":
            print("\n>>> Speech started!")
            is_recording = True
            turn_audio = []

        if is_recording:
            turn_audio.append(audio_bytes)

        if result.event == "end_of_speech":
            duration_ms = len(b"".join(turn_audio)) * 1000 // (SAMPLE_RATE * 2)
            print(f"\n<<< Speech ended! Duration: {duration_ms}ms")
            print("-" * 40)
            is_recording = False

    try:
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            blocksize=BLOCKSIZE,
            dtype=np.float32,
            callback=audio_callback
        ):
            print("Listening... (Ctrl+C to stop)\n")
            while True:
                sd.sleep(100)
    except KeyboardInterrupt:
        print("\n\nStopping...")
    finally:
        vad.stop()
        print("Done!")


if __name__ == "__main__":
    main()
