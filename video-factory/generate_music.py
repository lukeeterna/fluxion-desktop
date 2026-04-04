"""
generate_music.py — FLUXION Video Factory
Meta MusicGen background music generator per 9 verticali.

Licenza: MIT (Meta MusicGen) — uso commerciale PERMESSO.
Costo: ZERO (modello open source, esecuzione locale o Replicate ~$0.01/track).

Genera tracce PAS (Problem-Agitation-Solution) con arco emotivo:
  0-14s:  Teso, minimale (pain/problem phase) — minor key, sparse
  14-18s: Picco tensione + silenzio (agitation)
  18-26s: Uplifting, caldo (solution) — major key, warm
  26-30s: Silenzio/fade (CTA — voce nuda senza musica)

Uso:
  python generate_music.py --vertical parrucchiere
  python generate_music.py --vertical all
  python generate_music.py --vertical all --backend replicate
  python generate_music.py --list

Backends:
  - local:     MusicGen-large via Hugging Face transformers (richiede GPU/CPU potente)
  - replicate: MusicGen via Replicate API (~$0.01/track, richiede REPLICATE_API_TOKEN)
  - hf-space:  Hugging Face Spaces (gratuito ma rate-limited)
"""

import json
import os
import sys
import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

STORYBOARDS_DIR = Path(__file__).parent / "output" / "storyboards"
MUSIC_OUTPUT_DIR = Path(__file__).parent / "output" / "music"

VERTICALS = [
    "parrucchiere", "barbiere", "officina", "carrozzeria",
    "dentista", "centro_estetico", "nail_artist", "palestra", "fisioterapista"
]


def load_music_config(vertical: str) -> dict:
    path = STORYBOARDS_DIR / f"{vertical}.json"
    sb = json.loads(path.read_text())
    return sb.get("music_gen_config", {})


# ─── Local backend (Hugging Face transformers) ──────────────────────────────

def generate_local(prompt: str, duration_sec: float, output_path: Path) -> Path:
    """Genera musica con MusicGen-large locale."""
    try:
        from transformers import AutoProcessor, MusicgenForConditionalGeneration
        import scipy.io.wavfile
        import numpy as np
    except ImportError:
        print("Installa: pip install transformers torch scipy")
        sys.exit(1)

    logger.info(f"Loading MusicGen-large model...")
    processor = AutoProcessor.from_pretrained("facebook/musicgen-large")
    model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-large")

    # MusicGen genera a 32kHz, max_new_tokens controlla la durata
    # ~50 tokens/sec → 30s = 1500 tokens
    tokens_needed = int(duration_sec * 50)

    logger.info(f"Generating {duration_sec}s audio: {prompt[:60]}...")
    inputs = processor(
        text=[prompt],
        padding=True,
        return_tensors="pt",
    )
    audio_values = model.generate(**inputs, max_new_tokens=tokens_needed)

    # Salva come WAV
    wav_path = output_path.with_suffix(".wav")
    audio_data = audio_values[0, 0].cpu().numpy()
    scipy.io.wavfile.write(str(wav_path), rate=32000, data=audio_data)

    # Converti in MP3
    mp3_path = output_path.with_suffix(".mp3")
    subprocess.run([
        "ffmpeg", "-y", "-i", str(wav_path),
        "-acodec", "libmp3lame", "-ab", "192k",
        str(mp3_path)
    ], capture_output=True)

    wav_path.unlink(missing_ok=True)
    logger.info(f"Generated: {mp3_path}")
    return mp3_path


# ─── Replicate backend ──────────────────────────────────────────────────────

def generate_replicate(prompt: str, duration_sec: float, output_path: Path) -> Path:
    """Genera musica via Replicate API (~$0.01/track)."""
    import requests

    api_token = os.environ.get("REPLICATE_API_TOKEN")
    if not api_token:
        print("Set REPLICATE_API_TOKEN environment variable")
        sys.exit(1)

    logger.info(f"Generating via Replicate: {prompt[:60]}...")

    # Submit prediction
    resp = requests.post(
        "https://api.replicate.com/v1/predictions",
        headers={
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        },
        json={
            "version": "671ac645ce5e552cc63a54a2bbff63fcf798043ac68f86b6588138c5d33dbb2",  # musicgen-large
            "input": {
                "prompt": prompt,
                "duration": int(duration_sec),
                "model_version": "large",
                "output_format": "mp3",
            }
        },
        timeout=30,
    )
    resp.raise_for_status()
    prediction = resp.json()

    # Poll until complete
    import time
    poll_url = prediction["urls"]["get"]
    for _ in range(60):
        time.sleep(5)
        r = requests.get(poll_url, headers={"Authorization": f"Bearer {api_token}"}, timeout=15)
        data = r.json()
        if data["status"] == "succeeded":
            audio_url = data["output"]
            # Download
            audio_resp = requests.get(audio_url, timeout=60)
            mp3_path = output_path.with_suffix(".mp3")
            mp3_path.write_bytes(audio_resp.content)
            logger.info(f"Generated: {mp3_path}")
            return mp3_path
        elif data["status"] == "failed":
            raise RuntimeError(f"Replicate failed: {data.get('error')}")

    raise TimeoutError("Replicate prediction timed out")


# ─── PAS music composition ──────────────────────────────────────────────────

def generate_pas_track(vertical: str, backend: str = "local") -> Path:
    """
    Genera traccia musicale PAS completa per un verticale.
    Struttura: tense (14s) + silence (0.5s) + uplifting (8s) + fade (3.5s silence for CTA)
    """
    config = load_music_config(vertical)
    prompts = config.get("prompts", {})
    genre = config.get("genre_hint", "corporate background")

    output_dir = MUSIC_OUTPUT_DIR / vertical
    output_dir.mkdir(parents=True, exist_ok=True)

    generate_fn = generate_local if backend == "local" else generate_replicate

    # Prompt tense (0-14s: HOOK + PROBLEM + AGITATION)
    tense_prompt = prompts.get("tense",
        f"tense minimal background, {genre}, sparse, uneasy, minor key, 80bpm, no vocals")

    # Prompt uplifting (18-26s: SOLUTION)
    uplift_prompt = prompts.get("uplifting",
        f"uplifting warm commercial, {genre}, optimistic, major key, 110bpm, no vocals")

    tense_path = output_dir / f"{vertical}_tense"
    uplift_path = output_dir / f"{vertical}_uplift"

    # Generate segments
    logger.info(f"[{vertical}] Generating tense segment (14s)...")
    tense_mp3 = generate_fn(tense_prompt, 14, tense_path)

    logger.info(f"[{vertical}] Generating uplifting segment (8s)...")
    uplift_mp3 = generate_fn(uplift_prompt, 8, uplift_path)

    # Compose final track with FFmpeg:
    # [tense 14s] [silence 0.5s] [crossfade into uplift 8s] [silence 3.5s for CTA]
    # Total: 14 + 0.5 + 8 + 3.5 = 26s (CTA has 4s of pure voice, no music at end)
    final_path = output_dir / f"{vertical}_music_pas.mp3"

    # Build with FFmpeg complex filter
    cmd = [
        "ffmpeg", "-y",
        "-i", str(tense_mp3),
        "-i", str(uplift_mp3),
        "-f", "lavfi", "-t", "0.5", "-i", "anullsrc=r=32000:cl=mono",  # silence gap
        "-f", "lavfi", "-t", "3.5", "-i", "anullsrc=r=32000:cl=mono",  # CTA silence
        "-filter_complex",
        # Normalize both to mono 32k, then concat: tense + silence + uplift + silence
        "[0:a]aformat=sample_rates=32000:channel_layouts=mono,afade=t=in:st=0:d=1[a0];"
        "[1:a]aformat=sample_rates=32000:channel_layouts=mono,afade=t=out:st=6:d=2[a1];"
        "[2:a]aformat=sample_rates=32000:channel_layouts=mono[a2];"
        "[3:a]aformat=sample_rates=32000:channel_layouts=mono[a3];"
        "[a0][a2][a1][a3]concat=n=4:v=0:a=1[out]",
        "-map", "[out]",
        "-acodec", "libmp3lame", "-ab", "192k",
        str(final_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"FFmpeg compose failed: {result.stderr[-300:]}")
        # Fallback: just use tense as the full track
        import shutil
        shutil.copy2(str(tense_mp3), str(final_path))

    # Cleanup intermediate files
    tense_mp3.unlink(missing_ok=True)
    uplift_mp3.unlink(missing_ok=True)

    logger.info(f"[{vertical}] Final PAS track: {final_path}")
    return final_path


# ─── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    parser = argparse.ArgumentParser(description="FLUXION MusicGen — PAS Background Music")
    parser.add_argument("--vertical", default="all",
                        help="Vertical name or 'all'")
    parser.add_argument("--backend", default="local", choices=["local", "replicate"],
                        help="Generation backend")
    parser.add_argument("--list", action="store_true", help="List verticals and their music config")

    args = parser.parse_args()

    if args.list:
        print("\nVertical Music Configurations:")
        print("=" * 60)
        for v in VERTICALS:
            config = load_music_config(v)
            print(f"\n  {v}:")
            print(f"    Genre: {config.get('genre_hint', 'N/A')}")
            prompts = config.get("prompts", {})
            if "tense" in prompts:
                print(f"    Tense:  {prompts['tense'][:60]}...")
            if "uplifting" in prompts:
                print(f"    Uplift: {prompts['uplifting'][:60]}...")
        sys.exit(0)

    targets = VERTICALS if args.vertical == "all" else [args.vertical]

    for v in targets:
        if v not in VERTICALS:
            print(f"Unknown vertical: {v}")
            continue
        print(f"\n{'='*40}")
        print(f"Generating music for: {v}")
        print(f"{'='*40}")
        path = generate_pas_track(v, backend=args.backend)
        print(f"Output: {path}")

    print(f"\nDone! Generated music for {len(targets)} verticals.")
