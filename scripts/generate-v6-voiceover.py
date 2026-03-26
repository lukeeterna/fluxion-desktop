#!/usr/bin/env python3
"""
FLUXION V6 — Voiceover Generation Script
Reads video-production-v6.json and generates all Edge-TTS MP3 files.
Output: tmp-video-build/voice_scene_NN.mp3 + voiceover-manifest.json

Usage:
    python3 scripts/generate-v6-voiceover.py
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

BASE = Path("/Volumes/MontereyT7/FLUXION")
STORYBOARD = BASE / "scripts" / "video-production-v6.json"
TMPDIR = BASE / "tmp-video-build"
MANIFEST_PATH = TMPDIR / "voiceover-manifest.json"

VOICE_SARA = "it-IT-IsabellaNeural"
VOICE_CLIENT = "it-IT-DiegoNeural"
RATE_SARA = "-5%"
RATE_CLIENT = "+0%"


def get_duration(mp3_path: str) -> float:
    """Return duration in seconds of an MP3 file via ffprobe."""
    r = subprocess.run(
        [
            "ffprobe",
            "-v", "quiet",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            mp3_path,
        ],
        capture_output=True,
        text=True,
    )
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


async def generate_tts(text: str, output_path: str, voice: str, rate: str) -> float:
    """Generate TTS audio via edge_tts. Returns duration in seconds."""
    import edge_tts
    comm = edge_tts.Communicate(text, voice, rate=rate)
    await comm.save(output_path)
    return get_duration(output_path)


def ensure_silence_300ms() -> str:
    """Create a 300ms silence MP3 if it doesn't exist. Returns path."""
    silence = TMPDIR / "silence_300ms.mp3"
    if not silence.exists():
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-f", "lavfi",
                "-i", "anullsrc=r=24000:cl=mono",
                "-t", "0.3",
                "-c:a", "libmp3lame",
                str(silence),
            ],
            capture_output=True,
        )
    return str(silence)


async def generate_dialogue_scene(scene: dict) -> float:
    """
    Generate a multi-voice dialogue scene by:
    1. Generating each line with its voice
    2. Concatenating with 0.3s silence gaps via ffmpeg
    Returns total duration in seconds.
    """
    scene_id = scene["id"]
    lines = scene["voiceover_dialogue"]
    parts = []
    silence = ensure_silence_300ms()

    print(f"  {scene_id} — dialogue ({len(lines)} lines):")
    for j, line in enumerate(lines):
        part_path = TMPDIR / f"voice_{scene_id}_part{j:02d}.mp3"
        voice = VOICE_CLIENT if line["voice"] == "DiegoNeural" else VOICE_SARA
        rate = RATE_CLIENT if line["voice"] == "DiegoNeural" else RATE_SARA
        dur = await generate_tts(line["text"], str(part_path), voice=voice, rate=rate)
        parts.append(str(part_path))
        speaker = "Cliente" if line["voice"] == "DiegoNeural" else "Sara"
        print(f"    part{j:02d} ({speaker}): {dur:.1f}s — \"{line['text'][:50]}...\"")

    # Build concat file
    concat_file = TMPDIR / f"concat_{scene_id}.txt"
    with open(concat_file, "w") as f:
        for pi, p in enumerate(parts):
            f.write(f"file '{p}'\n")
            if pi < len(parts) - 1:
                f.write(f"file '{silence}'\n")

    output_path = TMPDIR / f"voice_{scene_id}.mp3"
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-c", "copy",
            str(output_path),
        ],
        capture_output=True,
    )

    total_dur = get_duration(str(output_path))
    print(f"  {scene_id} — dialogue concat total: {total_dur:.1f}s")
    return total_dur


async def main():
    print("=" * 60)
    print("  FLUXION V6 — Voiceover Generation (Edge-TTS)")
    print("=" * 60)

    # Load storyboard
    if not STORYBOARD.exists():
        print(f"ERROR: Storyboard not found: {STORYBOARD}", file=sys.stderr)
        sys.exit(1)

    with open(STORYBOARD) as f:
        storyboard = json.load(f)

    TMPDIR.mkdir(exist_ok=True)

    manifest = {}
    total_duration = 0.0
    voiced_count = 0
    silent_count = 0

    # Collect all scenes in order
    all_scenes = []
    for chapter in storyboard["chapters"]:
        for scene in chapter["scenes"]:
            all_scenes.append(scene)

    total_scenes = len(all_scenes)
    print(f"\nLoaded storyboard: {total_scenes} scenes in {len(storyboard['chapters'])} chapters\n")

    print("[1/1] Generating voiceovers...\n")

    for scene in all_scenes:
        scene_id = scene["id"]
        output_path = TMPDIR / f"voice_{scene_id}.mp3"

        if scene.get("type") == "dialogue" and "voiceover_dialogue" in scene:
            # Multi-voice dialogue
            dur = await generate_dialogue_scene(scene)
            manifest[scene_id] = {
                "mp3_path": str(output_path),
                "duration_seconds": round(dur, 2),
                "type": "dialogue",
                "voices": ["DiegoNeural", "IsabellaNeural"],
            }
            total_duration += dur
            voiced_count += 1

        elif scene.get("voiceover"):
            # Single-voice narration (Sara)
            voice = VOICE_SARA
            rate = RATE_SARA
            dur = await generate_tts(scene["voiceover"], str(output_path), voice=voice, rate=rate)
            print(f"  {scene_id}: {dur:.1f}s — \"{scene['voiceover'][:60]}...\"")
            manifest[scene_id] = {
                "mp3_path": str(output_path),
                "duration_seconds": round(dur, 2),
                "type": "narration",
                "voice": "IsabellaNeural",
            }
            total_duration += dur
            voiced_count += 1

        else:
            # No voiceover
            print(f"  {scene_id}: no voiceover (silent)")
            manifest[scene_id] = {
                "mp3_path": None,
                "duration_seconds": 0.0,
                "type": "silent",
            }
            silent_count += 1

    # Write manifest
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    # Summary
    print("\n" + "=" * 60)
    print(f"  Generation complete!")
    print(f"  Voiced scenes:  {voiced_count}")
    print(f"  Silent scenes:  {silent_count}")
    print(f"  Total voiceover duration: {total_duration:.1f}s ({total_duration/60:.1f} min)")
    print(f"  Manifest: {MANIFEST_PATH}")
    print("=" * 60)

    # Verify key scenes
    print("\nKey scene durations:")
    for key_id in ["scene_05", "scene_06", "scene_07", "scene_08", "scene_09", "scene_23"]:
        if key_id in manifest and manifest[key_id]["mp3_path"]:
            dur = manifest[key_id]["duration_seconds"]
            print(f"  {key_id}: {dur:.1f}s")


if __name__ == "__main__":
    asyncio.run(main())
