#!/usr/bin/env python3
"""
FLUXION V8 — Generate INCREMENTAL voiceovers for V8 update.
Only generates NEW scenes not in V7 manifest, then merges into v8-voiceover-manifest.json.
"""

import asyncio
import json
import subprocess
import shutil
from pathlib import Path

BASE = Path("/Volumes/MontereyT7/FLUXION")
TMPDIR = BASE / "tmp-video-build"
TMPDIR.mkdir(exist_ok=True)

VOICE_SARA = "it-IT-IsabellaNeural"
VOICE_CLIENT = "it-IT-DiegoNeural"
RATE_SARA = "-5%"
RATE_CLIENT = "+0%"

# V8 NEW/CHANGED scenes only
NEW_SCENES = [
    # Fedeltà scene (after s34 Pacchetti)
    {"id": "s34b", "vo": "Il programma fedelta'. Punti VIP per ogni visita, timbri digitali, premi personalizzati. I tuoi clienti migliori si sentono speciali. E tornano sempre.", "voice": "sara"},

    # "Con Sara lavori ordinato" — replaces broken s31 (portfolio)
    {"id": "s31", "vo": "Con Sara lavori in maniera ordinata. Ogni appuntamento registrato, ogni cliente tracciato, ogni incasso contabilizzato. Niente piu' foglietti, niente piu' caos.", "voice": "sara"},
]


async def generate_tts(text, output_path, voice=VOICE_SARA, rate=RATE_SARA):
    """Generate TTS audio, return duration."""
    import edge_tts
    comm = edge_tts.Communicate(text, voice, rate=rate)
    await comm.save(output_path)
    r = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1", output_path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


async def main():
    print("=" * 60)
    print("  FLUXION V8 — Incremental Voiceover Generation")
    print(f"  New scenes: {len(NEW_SCENES)}")
    print("=" * 60)

    # Load existing V7 manifest as base
    v7_manifest_path = TMPDIR / "v7-voiceover-manifest.json"
    if v7_manifest_path.exists():
        with open(v7_manifest_path) as f:
            manifest = json.load(f)
        print(f"  Loaded V7 manifest: {len(manifest)} scenes")
    else:
        manifest = {}
        print("  WARNING: No V7 manifest found, starting fresh")

    # Generate only new voiceovers
    for scene in NEW_SCENES:
        sid = scene["id"]
        vo = scene.get("vo")
        voice_type = scene.get("voice", "sara")

        if not vo:
            manifest[sid] = {"mp3_path": None, "duration_seconds": 0.0, "type": "silent"}
            print(f"  {sid}: silent")
            continue

        mp3_path = str(TMPDIR / f"{sid}.mp3")

        if voice_type == "client":
            voice, rate = VOICE_CLIENT, RATE_CLIENT
        else:
            voice, rate = VOICE_SARA, RATE_SARA

        dur = await generate_tts(vo, mp3_path, voice=voice, rate=rate)
        manifest[sid] = {
            "mp3_path": mp3_path,
            "duration_seconds": round(dur, 2),
            "type": "dialogue" if voice_type == "client" else "narration",
            "voice": voice.split("-")[-1]
        }
        print(f"  {sid}: {dur:.1f}s ({voice_type})")

    # Save V8 manifest
    v8_manifest_path = TMPDIR / "v8-voiceover-manifest.json"
    with open(v8_manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nV8 Manifest: {v8_manifest_path}")

    total = sum(v["duration_seconds"] for v in manifest.values())
    print(f"Total voiceover: {total:.0f}s ({total/60:.1f} min)")


if __name__ == "__main__":
    asyncio.run(main())
