#!/usr/bin/env python3
"""
FLUXION Demo Video Creator
- Edge-TTS IsabellaNeural voiceover (Italian)
- ffmpeg slideshow from real screenshots
- SRT subtitles auto-generated
- Output: landing/assets/fluxion-demo.mp4

Usage: python3 scripts/create-demo-video.py
"""

import asyncio
import json
import os
import subprocess
import tempfile
from pathlib import Path

# Paths
BASE = Path(__file__).resolve().parent.parent
SCREENSHOTS = BASE / "landing" / "screenshots"
OUTPUT = BASE / "landing" / "assets"
OUTPUT.mkdir(parents=True, exist_ok=True)

# TTS config
VOICE = "it-IT-IsabellaNeural"
RATE = "+5%"  # Slightly faster for professional feel

# Slide script: (screenshot_filename, voiceover_text, duration_seconds)
SLIDES = [
    (
        "01-dashboard.png",
        "Benvenuto in Fluxion. Ecco la tua dashboard: "
        "appuntamenti di oggi, clienti totali, fatturato del mese — "
        "tutto a colpo d'occhio, appena apri il programma.",
        8,
    ),
    (
        "02-calendario.png",
        "Il calendario ti mostra tutti gli appuntamenti del mese. "
        "Confermati, completati, cancellati — ogni giorno con il suo punto colorato. "
        "Niente più agende di carta.",
        7,
    ),
    (
        "03-clienti.png",
        "L'anagrafica clienti completa: nome, telefono, email, note. "
        "Cerca in un istante, vedi quante visite ha fatto ogni cliente, "
        "chi è VIP e chi è nuovo questo mese.",
        7,
    ),
    (
        "04-servizi.png",
        "Il tuo listino servizi con prezzi, durata e categoria. "
        "Taglio donna trentacinque euro, colore sessantacinque, "
        "meches ottantacinque — tutto organizzato e modificabile in un click.",
        7,
    ),
    (
        "05-operatori.png",
        "Gestione operatori: ogni membro del team ha il suo profilo "
        "con ruolo, contatti e statistiche mensili. "
        "Valentina, Roberto, Sara, Matteo — ognuno con il suo colore nel calendario.",
        7,
    ),
    (
        "06-fatture.png",
        "Fatturazione elettronica integrata. "
        "Crei la fattura con un click dopo l'appuntamento, "
        "la invii al Sistema di Interscambio direttamente da Fluxion. "
        "XML FatturaPA generato in automatico.",
        8,
    ),
    (
        "07-cassa.png",
        "La cassa giornaliera: contanti, carta, Satispay. "
        "Ogni incasso collegato al cliente e al servizio. "
        "A fine giornata, chiudi cassa con un click — senza fogli di calcolo.",
        7,
    ),
    (
        "08-voice.png",
        "E questa è Sara, la tua receptionist con intelligenza artificiale. "
        "Risponde al telefono ventiquattro ore su ventiquattro, "
        "capisce il cliente, prenota l'appuntamento "
        "e invia conferma su WhatsApp — tutto in automatico.",
        9,
    ),
    (
        "10-analytics.png",
        "Report e statistiche: fatturato del mese con confronto, "
        "appuntamenti completati, tasso di conferma WhatsApp, "
        "top servizi e top operatori. Tutto quello che ti serve per decidere.",
        8,
    ),
    (
        "09-fornitori.png",
        "Gestione fornitori e listini prezzi. "
        "Importa il listino da Excel con un click, "
        "traccia le variazioni di prezzo nel tempo. "
        "L'Oréal, Wella, GHD — tutto in ordine.",
        7,
    ),
    (
        "11-impostazioni.png",
        "Impostazioni complete: orari, festivi, email, WhatsApp, Sara, "
        "fatturazione, fedeltà, licenza e diagnostica. "
        "Tutto configurabile da un'unica pagina, in italiano.",
        7,
    ),
    (
        None,  # Final slide - title card
        "Fluxion. Il gestionale per la tua attività. "
        "Paghi una volta, per sempre. "
        "Da quattrocentonovantasette euro. "
        "Vai su fluxion punto it per scoprire di più.",
        8,
    ),
]


async def generate_tts(text: str, output_path: str) -> float:
    """Generate TTS audio and return duration in seconds."""
    import edge_tts

    communicate = edge_tts.Communicate(text, VOICE, rate=RATE)
    await communicate.save(output_path)

    # Get duration via ffprobe
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "quiet",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            output_path,
        ],
        capture_output=True,
        text=True,
    )
    return float(result.stdout.strip())


def create_title_card(output_path: str, width: int = 1920, height: int = 1080):
    """Create a title card image using Pillow."""
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("RGB", (width, height), (15, 23, 42))  # #0f172a
    draw = ImageDraw.Draw(img)

    # Try to find a good font
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNSDisplay.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    font_path = None
    for fp in font_paths:
        if os.path.exists(fp):
            font_path = fp
            break

    if font_path:
        font_big = ImageFont.truetype(font_path, 96)
        font_med = ImageFont.truetype(font_path, 36)
        font_small = ImageFont.truetype(font_path, 32)
        font_tiny = ImageFont.truetype(font_path, 24)
    else:
        font_big = ImageFont.load_default()
        font_med = font_big
        font_small = font_big
        font_tiny = font_big

    cy = height // 2

    # FLUXION title
    draw.text((width // 2, cy - 80), "FLUXION", fill="white", font=font_big, anchor="mm")
    # Subtitle
    draw.text(
        (width // 2, cy + 40),
        "Il gestionale per la tua attivita'.",
        fill=(148, 163, 184),
        font=font_med,
        anchor="mm",
    )
    # Price
    draw.text(
        (width // 2, cy + 100),
        "Da 497 euro — una volta sola",
        fill=(6, 182, 212),
        font=font_small,
        anchor="mm",
    )
    # URL
    draw.text(
        (width // 2, cy + 160),
        "fluxion-landing.pages.dev",
        fill=(100, 116, 139),
        font=font_tiny,
        anchor="mm",
    )

    img.save(output_path)


def generate_srt(slides_data: list, output_path: str):
    """Generate SRT subtitle file."""
    lines = []
    current_time = 0.0

    for i, (_, text, duration) in enumerate(slides_data, 1):
        start = format_srt_time(current_time)
        end = format_srt_time(current_time + duration)
        lines.append(f"{i}")
        lines.append(f"{start} --> {end}")
        lines.append(text)
        lines.append("")
        current_time += duration

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def format_srt_time(seconds: float) -> str:
    """Format seconds to SRT time format HH:MM:SS,mmm."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


async def main():
    with tempfile.TemporaryDirectory(prefix="fluxion-video-") as tmpdir:
        tmpdir = Path(tmpdir)
        audio_files = []
        image_files = []
        durations = []

        print("🎙️  Generating voiceover with Edge-TTS IsabellaNeural...")

        for i, (screenshot, text, min_duration) in enumerate(SLIDES):
            # Generate audio
            audio_path = tmpdir / f"audio_{i:02d}.mp3"
            audio_duration = await generate_tts(text, str(audio_path))
            actual_duration = max(audio_duration, min_duration)
            audio_files.append(str(audio_path))
            durations.append(actual_duration)
            print(f"  ✅ Slide {i + 1}/{len(SLIDES)}: {actual_duration:.1f}s — {text[:50]}...")

            # Prepare image
            if screenshot:
                img_src = SCREENSHOTS / screenshot
                if not img_src.exists():
                    print(f"  ⚠️  Missing: {img_src}")
                    continue
                image_files.append(str(img_src))
            else:
                # Title card
                title_path = tmpdir / "title_card.png"
                create_title_card(str(title_path))
                image_files.append(str(title_path))

        # Build ffmpeg concat file for images
        print("\n🎬 Building video with ffmpeg...")
        concat_file = tmpdir / "concat.txt"
        with open(concat_file, "w") as f:
            for img, dur in zip(image_files, durations):
                f.write(f"file '{img}'\n")
                f.write(f"duration {dur}\n")
            # Repeat last image for ffmpeg concat demuxer
            f.write(f"file '{image_files[-1]}'\n")

        # Concatenate audio
        audio_list = tmpdir / "audio_list.txt"
        with open(audio_list, "w") as f:
            for af in audio_files:
                f.write(f"file '{af}'\n")

        concat_audio = tmpdir / "full_audio.mp3"
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0",
                "-i", str(audio_list),
                "-c", "copy",
                str(concat_audio),
            ],
            check=True,
            capture_output=True,
        )

        # Build video: images + audio
        output_video = OUTPUT / "fluxion-demo.mp4"
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0",
                "-i", str(concat_file),
                "-i", str(concat_audio),
                "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=0x0f172a,format=yuv420p",
                "-c:v", "libx264", "-preset", "slow", "-crf", "20",
                "-c:a", "aac", "-b:a", "192k",
                "-shortest",
                "-movflags", "+faststart",
                str(output_video),
            ],
            check=True,
            capture_output=True,
        )

        # Generate SRT
        srt_path = OUTPUT / "fluxion-demo.srt"
        generate_srt(SLIDES, str(srt_path))

        # Get video info
        result = subprocess.run(
            [
                "ffprobe", "-v", "quiet",
                "-show_entries", "format=duration,size",
                "-of", "json",
                str(output_video),
            ],
            capture_output=True,
            text=True,
        )
        info = json.loads(result.stdout)
        duration = float(info["format"]["duration"])
        size_mb = int(info["format"]["size"]) / 1024 / 1024

        print(f"\n✅ Video created: {output_video}")
        print(f"   Duration: {duration:.0f}s ({duration / 60:.1f} min)")
        print(f"   Size: {size_mb:.1f} MB")
        print(f"   Subtitles: {srt_path}")
        print(f"\n📺 To preview: open {output_video}")


if __name__ == "__main__":
    asyncio.run(main())
