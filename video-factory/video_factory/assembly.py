"""
assembly.py — FLUXION Video Factory
Post-produzione: assembla clip Veo 3 + voiceover + overlay testi + CTA.

Requisiti:
  pip install ffmpeg-python edge-tts asyncio
  brew install ffmpeg  (con --with-freetype per testi)
"""

from __future__ import annotations
import asyncio
import json
import subprocess
import tempfile
from pathlib import Path
from dataclasses import dataclass

import ffmpeg  # pip install ffmpeg-python


# ─── Config ──────────────────────────────────────────────────────────────────

FLUXION_FONT = "Inter-Bold"
FLUXION_COLORS = {
    "white": "white",
    "red_price": "#FF4444",
    "gray_sub": "#CCCCCC",
    "blue_url": "#8888FF",
    "bg_black": "black",
}

MUSIC_TRACKS = {
    "tense": "assets/music/tense_background.mp3",
    "uplifting": "assets/music/uplifting_commercial.mp3",
}

# Font path (macOS + Linux)
FONT_PATHS = [
    "/System/Library/Fonts/Supplemental/Inter-Bold.ttf",
    "/usr/share/fonts/truetype/inter/Inter-Bold.ttf",
    "/Library/Fonts/Inter-Bold.ttf",
]


def find_font() -> str:
    for p in FONT_PATHS:
        if Path(p).exists():
            return p
    # Fallback system font
    return "/System/Library/Fonts/Helvetica.ttc"


FONT_PATH = find_font()


# ─── Dataclasses ─────────────────────────────────────────────────────────────

@dataclass
class AssemblyJob:
    verticale: str
    clip_paths: list[Path]          # 3 clip Veo 3 (best variant di ognuna)
    audio_path: Path | None         # voiceover mp3 (da voiceover_agent)
    output_dir: Path
    overlay_texts: list[dict]       # [{time_sec, text, style}]
    aspect_ratio: str = "9:16"      # "9:16" per WA, "16:9" per YT


@dataclass
class AssemblyResult:
    vertical_path: Path             # 9:16 per WA/Reels
    horizontal_path: Path           # 16:9 per YT/Vimeo
    thumbnail_path: Path
    duration_seconds: float


# ─── Voiceover (Edge-TTS) ────────────────────────────────────────────────────

async def generate_voiceover(
    segments: list[dict],
    output_path: Path,
    voice: str = "it-IT-IsabellaNeural"
) -> Path:
    """
    Genera voiceover italiano con Edge-TTS.
    Concatena tutti i segmenti in un unico mp3.
    """
    import edge_tts

    temp_files = []
    for i, seg in enumerate(segments):
        if not seg.get("text"):
            continue

        temp_path = output_path.parent / f"seg_{i}.mp3"
        communicator = edge_tts.Communicate(
            text=seg["text"],
            voice=voice,
            rate="+5%",    # leggermente più veloce per ritmo commerciale
            volume="+0%",
        )
        await communicator.save(str(temp_path))
        temp_files.append((seg.get("start_sec", 0), temp_path))

    if not temp_files:
        return None

    # Concatena con silenzio tra i segmenti
    filter_parts = []
    inputs = []
    for i, (start_sec, path) in enumerate(temp_files):
        inputs.append(ffmpeg.input(str(path)))
        filter_parts.append(f"[{i}:a]")

    concat_filter = "".join(filter_parts) + f"concat=n={len(inputs)}:v=0:a=1[out]"
    (
        ffmpeg
        .filter(inputs, "concat", n=len(inputs), v=0, a=1)
        .output(str(output_path), acodec="libmp3lame", audio_bitrate="192k")
        .overwrite_output()
        .run(quiet=True)
    )

    return output_path


# ─── CTA Frame (sfondo nero + testi) ─────────────────────────────────────────

def create_cta_frame(
    output_path: Path,
    duration_seconds: int = 6,
    resolution: tuple = (1080, 1920),  # W×H per 9:16
    competitor_price: str = "€4.320 in 3 anni",
) -> Path:
    """
    Crea il frame CTA finale (sfondo nero + testi FLUXION + prezzo).
    Usando FFmpeg lavid2dtext filter.
    """
    w, h = resolution

    # Costruisce drawtext filter chain
    texts = [
        # FLUXION titolo
        f"drawtext=fontfile={FONT_PATH}:text='FLUXION':fontcolor=white:fontsize=88:x=(w-tw)/2:y=200:box=0",
        # Sottotitolo
        f"drawtext=fontfile={FONT_PATH}:text='Il gestionale che non ti costa ogni mese':fontcolor=#CCCCCC:fontsize=34:x=(w-tw)/2:y=330:box=0",
        # Prezzo FLUXION
        f"drawtext=fontfile={FONT_PATH}:text='€497 una volta. Per sempre.':fontcolor=white:fontsize=58:x=(w-tw)/2:y=460:box=0",
        # Prezzo competitor (rosso)
        f"drawtext=fontfile={FONT_PATH}:text='Competitor\\: {competitor_price}':fontcolor=#FF4444:fontsize=34:x=(w-tw)/2:y=570:box=0",
        # Separatore
        f"drawtext=fontfile={FONT_PATH}:text='─────────────────':fontcolor=#444444:fontsize=28:x=(w-tw)/2:y=640:box=0",
        # URL
        f"drawtext=fontfile={FONT_PATH}:text='fluxion-landing.pages.dev':fontcolor=#8888FF:fontsize=38:x=(w-tw)/2:y=700:box=0",
    ]

    vf = ",".join(texts)

    (
        ffmpeg
        .input(f"color=c=black:s={w}x{h}:d={duration_seconds}", f="lavfi")
        .output(
            str(output_path),
            vf=vf,
            vcodec="libx264",
            pix_fmt="yuv420p",
            r=30,
            t=duration_seconds,
        )
        .overwrite_output()
        .run(quiet=True)
    )

    return output_path


# ─── Overlay testi su clip ───────────────────────────────────────────────────

def add_text_overlay(
    input_path: Path,
    output_path: Path,
    overlay_text: str,
    start_sec: float = 1.0,
    end_sec: float = None,
    position: str = "bottom",  # "top" | "bottom" | "center"
    fontsize: int = 52,
    color: str = "white",
) -> Path:
    """Aggiunge testo overlay a una clip."""
    if end_sec is None:
        # Ottieni durata clip
        probe = ffmpeg.probe(str(input_path))
        end_sec = float(probe["streams"][0]["duration"]) - 0.5

    y_map = {
        "top": "80",
        "center": "(h-th)/2",
        "bottom": "h-th-80",
    }
    y = y_map.get(position, "h-th-80")

    drawtext = (
        f"drawtext=fontfile={FONT_PATH}"
        f":text='{overlay_text}'"
        f":fontcolor={color}"
        f":fontsize={fontsize}"
        f":x=(w-tw)/2"
        f":y={y}"
        f":box=1:boxcolor=black@0.5:boxborderw=12"
        f":enable='between(t,{start_sec},{end_sec})'"
    )

    (
        ffmpeg
        .input(str(input_path))
        .output(str(output_path), vf=drawtext, vcodec="libx264",
                acodec="copy", pix_fmt="yuv420p")
        .overwrite_output()
        .run(quiet=True)
    )

    return output_path


# ─── Assemblaggio finale ─────────────────────────────────────────────────────

def select_best_clip(variants: list[Path]) -> Path:
    """
    Sceglie la migliore variante tra quelle generate (per ora: prima variante).
    TODO: integra un modello VQA per scoring qualità visiva automatico.
    """
    # Semplice euristica: prendi il file più grande (meno artefatti di compressione)
    if not variants:
        raise ValueError("Nessuna variante disponibile")
    return max(variants, key=lambda p: p.stat().st_size if p.exists() else 0)


def assemble_video(job: AssemblyJob) -> AssemblyResult:
    """
    Pipeline completa:
    1. Seleziona best variant per ogni clip
    2. Aggiunge overlay testi
    3. Crea CTA frame
    4. Concatena tutto
    5. Aggiunge audio (voiceover + musica)
    6. Produce versione 9:16 e 16:9
    """
    job.output_dir.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp())

    print(f"Assemblaggio: {job.verticale}")

    # Step 1 — Seleziona migliori clip
    best_clips = []
    for i, clip_path in enumerate(job.clip_paths):
        # Clip path può essere dir con varianti o file singolo
        if clip_path.is_dir():
            variants = list(clip_path.glob("*.mp4"))
            best = select_best_clip(variants)
        else:
            best = clip_path
        print(f"  Clip {i+1}: {best.name}")
        best_clips.append(best)

    # Step 2 — Aggiungi overlay testi alle clip
    overlayed_clips = []
    overlay_map = {item["clip"]: item for item in job.overlay_texts}

    for i, clip in enumerate(best_clips):
        clip_num = i + 1
        out = tmp / f"overlay_{clip_num}.mp4"
        if clip_num in overlay_map:
            ov = overlay_map[clip_num]
            add_text_overlay(
                input_path=clip,
                output_path=out,
                overlay_text=ov["text"],
                position=ov.get("position", "bottom"),
                color=ov.get("color", "white"),
            )
        else:
            # Copia senza overlay
            ffmpeg.input(str(clip)).output(str(out)).overwrite_output().run(quiet=True)
        overlayed_clips.append(out)

    # Step 3 — Crea CTA frame
    cta_path = tmp / "cta_frame.mp4"
    create_cta_frame(cta_path, duration_seconds=6)
    overlayed_clips.append(cta_path)

    # Step 4 — Concatena tutte le clip
    concat_path = tmp / "concat_no_audio.mp4"
    _concat_clips(overlayed_clips, concat_path)

    # Step 5 — Merge audio + video
    final_9x16_path = job.output_dir / f"{job.verticale}_video_9x16.mp4"

    if job.audio_path and job.audio_path.exists():
        _merge_audio(concat_path, job.audio_path, final_9x16_path)
    else:
        # Solo musica di sottofondo (se disponibile)
        music_path = Path(MUSIC_TRACKS.get("uplifting", ""))
        if music_path.exists():
            _merge_audio(concat_path, music_path, final_9x16_path, audio_vol=0.3)
        else:
            ffmpeg.input(str(concat_path)).output(str(final_9x16_path)).overwrite_output().run(quiet=True)

    # Step 6 — Versione 16:9 per YT/Vimeo (letterbox)
    final_16x9_path = job.output_dir / f"{job.verticale}_video_16x9.mp4"
    _convert_to_16x9(final_9x16_path, final_16x9_path)

    # Step 7 — Thumbnail (frame al secondo 18 = momento trasformazione)
    thumbnail_path = job.output_dir / f"{job.verticale}_thumbnail.jpg"
    _extract_thumbnail(final_16x9_path, thumbnail_path, time_sec=18)

    # Durata finale
    probe = ffmpeg.probe(str(final_9x16_path))
    duration = float(probe["format"]["duration"])

    print(f"  Output 9:16: {final_9x16_path}")
    print(f"  Output 16:9: {final_16x9_path}")
    print(f"  Durata: {duration:.1f}s")

    return AssemblyResult(
        vertical_path=final_9x16_path,
        horizontal_path=final_16x9_path,
        thumbnail_path=thumbnail_path,
        duration_seconds=duration,
    )


def _concat_clips(clip_paths: list[Path], output_path: Path) -> None:
    """Concatena clip con dissolve 0.3s tra ognuna."""
    if len(clip_paths) == 1:
        ffmpeg.input(str(clip_paths[0])).output(str(output_path)).overwrite_output().run(quiet=True)
        return

    # Crea file list per concat demuxer
    list_file = output_path.parent / "concat_list.txt"
    with open(list_file, "w") as f:
        for p in clip_paths:
            f.write(f"file '{p.absolute()}'\n")

    (
        ffmpeg
        .input(str(list_file), format="concat", safe=0)
        .output(str(output_path), vcodec="libx264", acodec="aac", pix_fmt="yuv420p")
        .overwrite_output()
        .run(quiet=True)
    )


def _merge_audio(
    video_path: Path,
    audio_path: Path,
    output_path: Path,
    audio_vol: float = 1.0,
    music_vol: float = 0.15,
) -> None:
    """Merge video + audio, taglia l'audio alla durata del video."""
    video = ffmpeg.input(str(video_path))
    audio = ffmpeg.input(str(audio_path))

    # Se c'è già audio nel video (es. musica background), mix
    probe = ffmpeg.probe(str(video_path))
    has_audio = any(s["codec_type"] == "audio" for s in probe["streams"])

    if has_audio:
        video_audio = video.audio.filter("volume", music_vol)
        voiceover = audio.filter("volume", audio_vol)
        mixed = ffmpeg.filter([video_audio, voiceover], "amix", inputs=2, duration="shortest")
        (
            ffmpeg
            .output(video.video, mixed, str(output_path),
                    vcodec="copy", acodec="aac", audio_bitrate="192k",
                    shortest=None)
            .overwrite_output()
            .run(quiet=True)
        )
    else:
        (
            ffmpeg
            .output(video.video, audio.filter("volume", audio_vol),
                    str(output_path),
                    vcodec="copy", acodec="aac", audio_bitrate="192k",
                    shortest=None)
            .overwrite_output()
            .run(quiet=True)
        )


def _convert_to_16x9(input_path: Path, output_path: Path) -> None:
    """Converte 9:16 in 16:9 con letterbox nero ai lati."""
    (
        ffmpeg
        .input(str(input_path))
        .filter("pad", width="1920", height="1080",
                x="(ow-iw)/2", y="(oh-ih)/2",
                color="black")
        .filter("scale", 1920, 1080)
        .output(str(output_path), vcodec="libx264",
                acodec="aac", pix_fmt="yuv420p")
        .overwrite_output()
        .run(quiet=True)
    )


def _extract_thumbnail(video_path: Path, output_path: Path, time_sec: float = 18) -> None:
    """Estrae frame per thumbnail YT."""
    (
        ffmpeg
        .input(str(video_path), ss=time_sec)
        .output(str(output_path), vframes=1, format="image2",
                vcodec="mjpeg", qscale="2")
        .overwrite_output()
        .run(quiet=True)
    )


# ─── Agent per Claude Code ───────────────────────────────────────────────────

def run_assembly_for_verticale(
    verticale: str,
    clips_dir: Path,
    audio_path: Path,
    output_dir: Path,
    overlay_config: dict,
) -> AssemblyResult:
    """Entry point per assembly-agent in Claude Code."""
    from script_generator import VERTICALI

    if verticale not in VERTICALI:
        raise ValueError(f"Verticale '{verticale}' non trovata. Disponibili: {list(VERTICALI.keys())}")

    data = VERTICALI[verticale]

    # Costruisce overlay_texts dal config verticale
    overlay_texts = [
        {
            "clip": 2,
            "text": data["pain_stat"],
            "position": "center",
            "color": "white",
        },
        {
            "clip": 3,
            "text": data["feature_hero"],
            "position": "bottom",
            "color": "white",
        },
        {
            "clip": 3,  # secondo overlay clip 3
            "text": data["transform_text"],
            "position": "top",
            "color": "#AAFFAA",
        },
    ]

    # Trova le clip nella dir
    clip_paths = sorted(clips_dir.glob(f"{verticale}_clip*.mp4"))
    if len(clip_paths) < 3:
        raise FileNotFoundError(
            f"Servono almeno 3 clip per {verticale}, trovate: {clip_paths}"
        )

    job = AssemblyJob(
        verticale=verticale,
        clip_paths=clip_paths[:3],
        audio_path=audio_path,
        output_dir=output_dir,
        overlay_texts=overlay_texts,
    )

    return assemble_video(job)
