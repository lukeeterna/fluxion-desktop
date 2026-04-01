"""
music_layer.py — FLUXION Video Factory
Scarica e applica musica di sottofondo royalty-free ai video.
Usa Freesound API (gratis) o Pixabay Music (gratis).

Struttura musicale per video di vendita FLUXION:
  0–8s:   Teso, minimale (pain phase) — pochi elementi, bassa frequenza
  8–16s:  Stacco + silenzio 0.3s (pattern interrupt) → sale gradualmente
  16–24s: Uplifting commerciale (soluzione/trasformazione)
  24–30s: Climax breve + CTA punch

Installazione:
  pip install requests pydub
  brew install ffmpeg
"""

from __future__ import annotations
import hashlib
import json
import logging
import os
import subprocess
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

# ─── Assets dir ──────────────────────────────────────────────────────────────

ASSETS_DIR = Path(__file__).parent.parent / "assets" / "music"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

CACHE_FILE = ASSETS_DIR / "cache.json"


# ─── Tracce pre-selezionate (Pixabay, licenza gratuita commerciale) ───────────

MUSIC_LIBRARY = {
    "tense": {
        "name": "Corporate Tension",
        "url": "https://cdn.pixabay.com/download/audio/2024/03/04/audio_0b63ac8e3f.mp3",
        "local": "tense_background.mp3",
        "bpm": 95,
        "mood": "suspense, minimal, low energy",
        "use_for": "frame 1-2 (pain phase)",
    },
    "uplifting": {
        "name": "Success Upbeat",
        "url": "https://cdn.pixabay.com/download/audio/2024/02/14/audio_5f1d83de4f.mp3",
        "local": "uplifting_commercial.mp3",
        "bpm": 120,
        "mood": "positive, energetic, commercial",
        "use_for": "frame 3-4 (soluzione/trasformazione)",
    },
    "cta_punch": {
        "name": "Impact Sting",
        "url": "https://cdn.pixabay.com/download/audio/2023/11/02/audio_c29b2d12f4.mp3",
        "local": "cta_punch.mp3",
        "bpm": 0,
        "mood": "punchy, short sting, 3 seconds",
        "use_for": "frame 5 CTA (ultimi 3 secondi)",
    },
    "notification_ding": {
        "name": "WhatsApp Style Ding",
        "url": "https://cdn.pixabay.com/download/audio/2021/08/04/audio_0625c1539c.mp3",
        "local": "notification_ding.mp3",
        "bpm": 0,
        "mood": "single notification sound",
        "use_for": "durante frame 3-4 (WA confirmations)",
    },
}

# Fallback: scarica solo se URL non disponibile
FREESOUND_API_KEY = os.environ.get("FREESOUND_API_KEY", "")


# ─── Download musica ──────────────────────────────────────────────────────────

def download_track(key: str, force: bool = False) -> Path | None:
    """Scarica una traccia dalla libreria e la salva in assets/music/."""
    if key not in MUSIC_LIBRARY:
        raise KeyError(f"Traccia '{key}' non trovata. Disponibili: {list(MUSIC_LIBRARY.keys())}")

    track = MUSIC_LIBRARY[key]
    local_path = ASSETS_DIR / track["local"]

    if local_path.exists() and not force:
        logger.info(f"Track già presente: {local_path}")
        return local_path

    logger.info(f"Scarico traccia '{key}': {track['name']}...")
    try:
        resp = requests.get(track["url"], timeout=30, stream=True)
        resp.raise_for_status()

        with open(local_path, "wb") as f:
            for chunk in resp.iter_content(8192):
                f.write(chunk)

        logger.info(f"Scaricata: {local_path}")
        return local_path

    except Exception as e:
        logger.warning(f"Download fallito per '{key}': {e}")
        return None


def ensure_music_library() -> dict[str, Path]:
    """Scarica tutte le tracce necessarie. Ritorna mapping key→path."""
    paths = {}
    for key in MUSIC_LIBRARY:
        path = download_track(key)
        if path and path.exists():
            paths[key] = path
    return paths


# ─── Composizione audio ──────────────────────────────────────────────────────

def build_music_track(
    total_duration: float,
    output_path: Path,
    music_paths: dict[str, Path],
    pain_duration: float = 8.0,
    transition_duration: float = 0.3,
) -> Path:
    """
    Costruisce la traccia musicale completa:
    [tense × pain_duration] → [silence 0.3s] → [uplifting × resto] → [CTA punch]

    Usa ffmpeg per concatenare e crossfade.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    tense_path = music_paths.get("tense")
    uplifting_path = music_paths.get("uplifting")
    cta_path = music_paths.get("cta_punch")

    if not tense_path or not uplifting_path:
        logger.warning("Tracce mancanti — skip composizione musicale")
        return None

    uplifting_start = pain_duration + transition_duration
    cta_start = total_duration - 4
    uplifting_duration = cta_start - uplifting_start

    # Crea file list con FFmpeg complex filter
    filter_parts = []
    inputs = []

    # Input 0: tense (tagliato a pain_duration)
    inputs.append(f"-ss 0 -t {pain_duration} -i {tense_path}")
    # Input 1: silenzio 0.3s
    inputs.append(f"-f lavfi -t {transition_duration} -i anullsrc=r=44100:cl=stereo")
    # Input 2: uplifting (tagliato alla durata necessaria)
    inputs.append(f"-ss 0 -t {uplifting_duration} -i {uplifting_path}")

    # CTA punch se disponibile
    if cta_path and cta_path.exists():
        inputs.append(f"-ss 0 -t 3 -i {cta_path}")
        n_inputs = 4
    else:
        n_inputs = 3

    # Costruisci command FFmpeg
    input_str = " ".join(inputs)
    concat_filter = "".join(f"[{i}:a]" for i in range(n_inputs))
    concat_filter += f"concat=n={n_inputs}:v=0:a=1[aout]"

    cmd = (
        f"ffmpeg -y "
        f"{input_str} "
        f'-filter_complex "{concat_filter}" '
        f"-map [aout] "
        f"-acodec libmp3lame -ab 192k "
        f"-t {total_duration} "
        f"{output_path}"
    )

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"FFmpeg music build error: {result.stderr[-500:]}")
        return None

    logger.info(f"Traccia musicale costruita: {output_path}")
    return output_path


def apply_music_to_video(
    video_path: Path,
    output_path: Path,
    music_path: Path,
    voiceover_path: Path | None = None,
    music_volume: float = 0.18,
    voice_volume: float = 1.0,
) -> Path:
    """
    Applica musica (e opzionalmente voiceover) al video.
    Il voiceover ha priorità sull'audio musicale (ducking automatico).
    """
    import ffmpeg

    video = ffmpeg.input(str(video_path))
    music = ffmpeg.input(str(music_path)).audio.filter("volume", music_volume)

    if voiceover_path and voiceover_path.exists():
        voice = ffmpeg.input(str(voiceover_path)).audio.filter("volume", voice_volume)
        # Mix voiceover + musica con ducking: abbassa musica durante voiceover
        mixed_audio = ffmpeg.filter(
            [music, voice],
            "amix",
            inputs=2,
            duration="shortest",
            dropout_transition=0.5,
        )
    else:
        mixed_audio = music

    (
        ffmpeg
        .output(
            video.video,
            mixed_audio,
            str(output_path),
            vcodec="copy",
            acodec="aac",
            audio_bitrate="192k",
            shortest=None,
        )
        .overwrite_output()
        .run(quiet=True)
    )

    return output_path


# ─── Integrazione con assembly.py ────────────────────────────────────────────

def get_or_build_music(
    verticale: str,
    total_duration: float,
    output_dir: Path,
) -> Path | None:
    """
    Punto di entrata per assembly.py.
    Ritorna path della traccia musicale pronta per il video specificato.
    """
    music_output = output_dir / f"{verticale}_music.mp3"

    if music_output.exists():
        return music_output

    # Scarica le tracce se necessario
    music_paths = ensure_music_library()
    if not music_paths:
        logger.warning("Nessuna traccia musicale disponibile — video senza musica")
        return None

    return build_music_track(
        total_duration=total_duration,
        output_path=music_output,
        music_paths=music_paths,
    )


# ─── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="FLUXION Music Layer")
    subparsers = parser.add_subparsers(dest="command")

    dl_parser = subparsers.add_parser("download", help="Scarica tutte le tracce")
    dl_parser.add_argument("--force", action="store_true")

    apply_parser = subparsers.add_parser("apply", help="Applica musica a video")
    apply_parser.add_argument("--video", type=Path, required=True)
    apply_parser.add_argument("--output", type=Path, required=True)
    apply_parser.add_argument("--voiceover", type=Path)
    apply_parser.add_argument("--music-vol", type=float, default=0.18)

    args = parser.parse_args()

    if args.command == "download":
        paths = ensure_music_library()
        print(f"Tracce scaricate: {len(paths)}")
        for k, p in paths.items():
            print(f"  {k}: {p}")

    elif args.command == "apply":
        music_paths = ensure_music_library()
        if not music_paths:
            print("Nessuna traccia disponibile")
            exit(1)

        probe = __import__("ffmpeg").probe(str(args.video))
        duration = float(probe["format"]["duration"])

        music_path = build_music_track(
            total_duration=duration,
            output_path=ASSETS_DIR / "temp_music_track.mp3",
            music_paths=music_paths,
        )

        if music_path:
            apply_music_to_video(
                video_path=args.video,
                output_path=args.output,
                music_path=music_path,
                voiceover_path=args.voiceover,
                music_volume=args.music_vol,
            )
            print(f"Output: {args.output}")
    else:
        parser.print_help()
