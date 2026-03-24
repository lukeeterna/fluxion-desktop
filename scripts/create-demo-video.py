#!/usr/bin/env python3
"""
FLUXION Demo Video Creator — V4 "Lasciali a Bocca Aperta"
Pipeline SEMPLIFICATA: screenshot REALI statici + crossfade + voiceover Edge-TTS.

V4 rules (from V3 lessons):
  - ZERO card Pillow (all 15 scenes use REAL screenshots)
  - ZERO zoompan (static images, crossfade between clips)
  - ZERO ristorante (not our vertical)
  - Logo burned via Pillow on every frame
  - Single Edge-TTS voiceover per scene
  - Simple xfade dissolve transitions
  - H.264 High Profile YouTube-optimized output

Usage: python3 scripts/create-demo-video.py
"""

import asyncio
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# Paths
BASE = Path(__file__).resolve().parent.parent
SCREENSHOTS = BASE / "landing" / "screenshots"
LOGO = BASE / "landing" / "assets" / "logo.png"
OUTPUT = BASE / "landing" / "assets"
OUTPUT.mkdir(parents=True, exist_ok=True)

# TTS config
VOICE = "it-IT-IsabellaNeural"
RATE = "-5%"

# Video config
CROSSFADE_DUR = 0.5  # seconds between scenes


# ============================================================
# V4 STORYBOARD — 15 scene, SOLO screenshot reali
# From: scripts/VIDEO_SCREENPLAY_V4.md
# ============================================================

SCENES = [
    # SCENA 1 — HOOK (dashboard sfocato leggero)
    {
        "id": "hook",
        "image": "01-dashboard.png",
        "blur": True,  # leggero blur per mood drammatico
        "text": (
            "Il telefono squilla. Hai le mani occupate. "
            "Non puoi rispondere. "
            "Quel cliente ha gia' chiamato qualcun altro."
        ),
        "chapter": "Il Problema",
        "padding": 1.0,
    },
    # SCENA 2 — AGITAZIONE (dashboard full sharp)
    {
        "id": "agitazione",
        "image": "01-dashboard.png",
        "text": (
            "Un cliente perso al giorno sono duecentocinquanta clienti all'anno. "
            "A trenta euro di media, sono settemilacinquecento euro buttati. "
            "E intanto, una receptionist ti costerebbe novecento euro al mese."
        ),
        "padding": 1.0,
    },
    # SCENA 3 — DASHBOARD
    {
        "id": "dashboard",
        "image": "01-dashboard.png",
        "text": (
            "Ecco FLUXION. Appena lo apri, la dashboard ti mostra tutto. "
            "Appuntamenti di oggi, clienti totali, fatturato del mese, "
            "e il servizio piu' richiesto. Tutto in un colpo d'occhio."
        ),
        "chapter": "La Dashboard",
        "padding": 0.8,
    },
    # SCENA 4 — CALENDARIO
    {
        "id": "calendario",
        "image": "02-calendario.png",
        "text": (
            "Il calendario. Vista settimanale, mensile, giornaliera. "
            "Per creare un appuntamento basta cliccare Nuovo Appuntamento. "
            "Scegli il cliente, il servizio, l'operatore, l'orario. "
            "Fatto. Due click."
        ),
        "chapter": "Il Calendario",
        "padding": 0.8,
    },
    # SCENA 5 — CLIENTI
    {
        "id": "clienti",
        "image": "03-clienti.png",
        "text": (
            "La rubrica clienti. Nome, telefono, email, punteggio fedelta'. "
            "Clicchi su un cliente e vedi tutto: "
            "lo storico visite, le preferenze, le note. "
            "Sai esattamente cosa ha fatto l'ultima volta."
        ),
        "chapter": "I Clienti",
        "padding": 0.8,
    },
    # SCENA 6 — SCHEDA PARRUCCHIERE
    {
        "id": "parrucchiere",
        "image": "13-scheda-parrucchiere.png",
        "text": (
            "Sei parrucchiere? Ogni cliente ha la sua scheda. "
            "Tipo di taglio, colore preferito, allergie ai prodotti. "
            "La prossima volta sai gia' cosa vuole. "
            "Sara risponde al telefono per te."
        ),
        "chapter": "Per il Tuo Settore",
        "padding": 0.8,
    },
    # SCENA 7 — SCHEDA VEICOLI
    {
        "id": "veicoli",
        "image": "14-scheda-veicoli.png",
        "text": (
            "Hai un'officina? La scheda veicolo tiene tutto: "
            "targa, chilometri, tagliandi, assicurazione. "
            "Sara prende l'appuntamento e salva il modello dell'auto. "
            "Tu non hai mosso un dito."
        ),
        "padding": 0.8,
    },
    # SCENA 8 — SCHEDA ODONTOIATRICA
    {
        "id": "odontoiatrica",
        "image": "15-scheda-odontoiatrica.png",
        "text": (
            "Studio medico? Anamnesi, allergie, piano terapeutico. "
            "Tutto nella scheda odontoiatrica. "
            "Il promemoria WhatsApp parte ventiquattro ore prima. "
            "La poltrona non resta vuota."
        ),
        "padding": 0.8,
    },
    # SCENA 9 — SARA VOICE
    {
        "id": "sara",
        "image": "08-voice.png",
        "text": (
            "E poi c'e' Sara. La tua receptionist che non va mai in ferie. "
            "Risponde al telefono ventiquattro ore su ventiquattro, "
            "in italiano perfetto. "
            "Capisce cosa vuole il cliente, prenota, "
            "e manda conferma WhatsApp. Tutto in automatico."
        ),
        "chapter": "Sara, la Tua Assistente",
        "padding": 1.0,
    },
    # SCENA 10 — SARA COSTO
    {
        "id": "sara_costo",
        "image": "08-voice.png",
        "text": (
            "Come avere una segretaria. "
            "Ma non costa novecento euro al mese. "
            "E' inclusa nella licenza FLUXION. Per sempre."
        ),
        "padding": 1.0,
    },
    # SCENA 11 — CASSA
    {
        "id": "cassa",
        "image": "07-cassa.png",
        "text": (
            "La cassa. A fine giornata sai esattamente quanto hai incassato. "
            "Contanti, carte, Satispay. Ogni transazione registrata."
        ),
        "chapter": "Cassa e Report",
        "padding": 0.6,
    },
    # SCENA 12 — ANALYTICS
    {
        "id": "analytics",
        "image": "10-analytics.png",
        "text": (
            "I report mensili. Fatturato, appuntamenti, top servizi, "
            "classifica operatori. "
            "Sai chi rende e dove investire."
        ),
        "padding": 0.6,
    },
    # SCENA 13 — SERVIZI
    {
        "id": "servizi",
        "image": "04-servizi.png",
        "text": (
            "Il listino servizi con prezzi e durate. "
            "Gli operatori con ruoli e specializzazioni. "
            "Tutto organizzato, tutto in italiano."
        ),
        "padding": 0.6,
    },
    # SCENA 14 — PREZZO
    {
        "id": "prezzo",
        "image": "01-dashboard.png",
        "text": (
            "Un gestionale in abbonamento ti costa seicento euro all'anno. "
            "In tre anni, milleottocento euro. E non sara' mai tuo. "
            "FLUXION costa quattrocentonovantasette euro. "
            "Una volta. Per sempre. Si ripaga in tre settimane."
        ),
        "chapter": "Il Prezzo",
        "padding": 1.0,
    },
    # SCENA 15 — CTA
    {
        "id": "cta",
        "image": "01-dashboard.png",
        "text": (
            "FLUXION. Paghi una volta, usi per sempre. "
            "Nessun abbonamento. Nessuna commissione. "
            "Trenta giorni soddisfatti o rimborsati."
        ),
        "chapter": "Inizia Ora",
        "padding": 1.5,
    },
]


# ============================================================
# PILLOW HELPERS — Solo logo burn (ZERO card generators)
# ============================================================

def burn_logo(img, logo_path, size=64, opacity=0.7):
    """Burn FLUXION logo onto a PIL Image (top-left). Returns modified image."""
    from PIL import Image
    if not os.path.exists(logo_path):
        return img

    logo = Image.open(logo_path).convert("RGBA")
    logo = logo.resize((size, size), Image.LANCZOS)

    if opacity < 1.0:
        alpha = logo.split()[3]
        alpha = alpha.point(lambda p: int(p * opacity))
        logo.putalpha(alpha)

    img_rgba = img.convert("RGBA")
    margin = 24
    img_rgba.paste(logo, (margin, margin), logo)
    return img_rgba.convert("RGB")


def prepare_image(img_path, logo_path, blur=False):
    """Load screenshot, burn logo, optionally blur. Returns PIL Image."""
    from PIL import Image, ImageFilter
    img = Image.open(img_path).convert("RGB")

    # Resize to 1920x1080 if needed
    if img.size != (1920, 1080):
        img = img.resize((1920, 1080), Image.LANCZOS)

    # Optional blur for dramatic hook scene
    if blur:
        img = img.filter(ImageFilter.GaussianBlur(radius=3))

    # Burn logo
    img = burn_logo(img, logo_path)
    return img


# ============================================================
# TTS + FFMPEG
# ============================================================

async def generate_tts(text, output_path):
    """Generate Edge-TTS audio, return duration in seconds."""
    import edge_tts
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE)
    await communicate.save(output_path)
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", output_path],
        capture_output=True, text=True,
    )
    return float(result.stdout.strip())


def make_static_clip(image_path, audio_path, duration, output_path):
    """Create a static clip: looped image + audio. ZERO zoompan."""
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-t", str(duration), "-i", image_path,
        "-i", audio_path,
        "-vf", "format=yuv420p",
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERRORE ffmpeg clip: {result.stderr[-500:]}", file=sys.stderr)
        sys.exit(1)


# ============================================================
# SRT + METADATA
# ============================================================

def format_srt_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def format_chapter_time(seconds):
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m}:{s:02d}"


def generate_srt(scenes, durations, output_path):
    """Generate SRT subtitle file."""
    lines = []
    current_time = 0.0
    idx = 1

    for scene, duration in zip(scenes, durations):
        text = scene["text"].replace("'", "\u2019")
        words = text.split()
        sub_lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            if len(" ".join(current_line)) > 42:
                sub_lines.append(" ".join(current_line[:-1]))
                current_line = [word]
        if current_line:
            sub_lines.append(" ".join(current_line))

        chunks = [sub_lines[j:j + 2] for j in range(0, len(sub_lines), 2)]
        chunk_dur = duration / max(len(chunks), 1)

        for ci, chunk in enumerate(chunks):
            t_start = current_time + ci * chunk_dur
            t_end = t_start + chunk_dur
            lines.append(str(idx))
            lines.append(f"{format_srt_time(t_start)} --> {format_srt_time(t_end)}")
            lines.append("\n".join(chunk))
            lines.append("")
            idx += 1

        current_time += duration

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def generate_youtube_metadata(scenes, durations, output_path):
    """Generate YouTube metadata: title, description, chapters, tags."""
    lines = []
    lines.append("TITOLO:")
    lines.append("FLUXION \u2014 Il Gestionale per la Tua Attivit\u00e0 | "
                 "Parrucchieri, Officine, Cliniche")
    lines.append("")
    lines.append("DESCRIZIONE:")
    lines.append("FLUXION \u00e8 il gestionale desktop per PMI italiane.")
    lines.append("Appuntamenti, clienti, cassa, WhatsApp, e Sara \u2014 "
                 "l'assistente vocale AI che risponde al telefono 24/7.")
    lines.append("")
    lines.append("Paghi una volta, usi per sempre. Da \u20ac497.")
    lines.append("30 giorni soddisfatti o rimborsati.")
    lines.append("")
    lines.append("Scopri di piu': https://fluxion-landing.pages.dev")
    lines.append("")

    # YouTube chapters
    lines.append("CAPITOLI:")
    current_time = 0.0
    for i, scene in enumerate(scenes):
        chapter = scene.get("chapter")
        if chapter:
            lines.append(f"{format_chapter_time(current_time)} {chapter}")
        current_time += durations[i]
        if i > 0:
            current_time -= CROSSFADE_DUR

    lines.append("")
    lines.append("TAG:")
    lines.append("gestionale, gestionale parrucchiere, software gestionale, "
                 "gestionale italiano, gestionale PMI, gestionale appuntamenti, "
                 "gestionale officina, gestionale clinica, "
                 "software prenotazioni, assistente vocale, FLUXION, Sara AI")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return lines


def create_thumbnail(logo_path, output_path):
    """YouTube thumbnail 1280x720 from dashboard screenshot."""
    from PIL import Image, ImageDraw, ImageFont

    dashboard = SCREENSHOTS / "01-dashboard.png"
    if not dashboard.exists():
        return

    img = Image.open(str(dashboard)).convert("RGB")
    img = img.resize((1280, 720), Image.LANCZOS)

    # Dark gradient overlay bottom
    overlay = Image.new("RGBA", (1280, 250), (0, 0, 0, 200))
    img_rgba = img.convert("RGBA")
    img_rgba.paste(overlay, (0, 470), overlay)
    img = img_rgba.convert("RGB")
    draw = ImageDraw.Draw(img)

    def _font(size):
        for fp in ["/System/Library/Fonts/Helvetica.ttc",
                   "/System/Library/Fonts/SFNSDisplay.ttf",
                   "/Library/Fonts/Arial.ttf"]:
            if os.path.exists(fp):
                return ImageFont.truetype(fp, size)
        return ImageFont.load_default()

    draw.text((640, 540), "FLUXION", fill=(255, 255, 255),
              font=_font(64), anchor="mm")
    draw.text((640, 600), "Il Gestionale per la Tua Attivit\u00e0 \u00b7 Da \u20ac497",
              fill=(6, 182, 212), font=_font(30), anchor="mm")
    draw.text((640, 650), "Parrucchieri \u00b7 Officine \u00b7 Cliniche \u00b7 Centri Estetici",
              fill=(148, 163, 184), font=_font(22), anchor="mm")

    # Play button center
    cx, cy = 640, 280
    r = 52
    draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)],
                 fill=(6, 182, 212), outline=(255, 255, 255), width=3)
    draw.polygon([(cx - 16, cy - 24), (cx - 16, cy + 24), (cx + 22, cy)],
                 fill=(255, 255, 255))

    img = burn_logo(img, logo_path, size=60, opacity=0.9)
    img.save(output_path, quality=95)


# ============================================================
# MAIN PIPELINE
# ============================================================

async def main():
    with tempfile.TemporaryDirectory(prefix="fluxion-v4-") as tmpdir:
        tmpdir = Path(tmpdir)

        print("=" * 60)
        print("  FLUXION Demo Video Creator V4")
        print("  Pipeline: screenshot statici + crossfade + voiceover")
        print(f"  Voice: {VOICE} | Rate: {RATE}")
        print(f"  Scenes: {len(SCENES)} | Crossfade: {CROSSFADE_DUR}s")
        print("=" * 60)

        logo_path = str(LOGO)

        # ---- PHASE 1: Verify all screenshots exist ----
        print("\n[1/7] Verifica screenshot...\n")
        for scene in SCENES:
            img_file = SCREENSHOTS / scene["image"]
            if not img_file.exists():
                print(f"  ERRORE: {img_file} non trovato!")
                sys.exit(1)
            print(f"  OK: {scene['image']}")

        # ---- PHASE 2: Generate all TTS audio ----
        print("\n[2/7] Generazione voiceover Edge-TTS...\n")
        audio_paths = []
        durations = []

        for i, scene in enumerate(SCENES):
            audio_path = tmpdir / f"audio_{i:02d}.mp3"
            audio_dur = await generate_tts(scene["text"], str(audio_path))
            padding = scene.get("padding", 0.8)
            actual_dur = audio_dur + padding
            audio_paths.append(str(audio_path))
            durations.append(actual_dur)
            print(f"  [{i + 1:2d}/{len(SCENES)}] {actual_dur:.1f}s — {scene['image']}")

        total_raw = sum(durations)
        total_with_xfade = total_raw - CROSSFADE_DUR * (len(SCENES) - 1)
        print(f"\n  Durata stimata: {total_with_xfade:.0f}s "
              f"({total_with_xfade / 60:.1f} min)")

        # ---- PHASE 3: Prepare images (logo burned) ----
        print("\n[3/7] Preparazione immagini (logo burned)...\n")
        prepared_paths = []

        for i, scene in enumerate(SCENES):
            img_path = str(SCREENSHOTS / scene["image"])
            img = prepare_image(img_path, logo_path, blur=scene.get("blur", False))
            prepared_path = str(tmpdir / f"prepared_{i:02d}.png")
            img.save(prepared_path, quality=95)
            prepared_paths.append(prepared_path)
            extra = " [blur]" if scene.get("blur") else ""
            print(f"  [{i + 1:2d}] {scene['image']}{extra}")

        # ---- PHASE 4: Generate static clips ----
        print("\n[4/7] Generazione clip statici (ZERO zoompan)...\n")
        clip_paths = []

        for i, scene in enumerate(SCENES):
            clip_path = str(tmpdir / f"clip_{i:02d}.mp4")
            make_static_clip(
                image_path=prepared_paths[i],
                audio_path=audio_paths[i],
                duration=durations[i],
                output_path=clip_path,
            )
            clip_paths.append(clip_path)
            print(f"  [{i + 1:2d}/{len(SCENES)}] {scene['id']} — {durations[i]:.1f}s")

        # ---- PHASE 5: Join clips with xfade dissolve ----
        print("\n[5/7] Composizione con crossfade dissolve...\n")

        if len(clip_paths) < 2:
            composed_path = clip_paths[0]
        else:
            # Sequential xfade: merge pairs one by one
            current = clip_paths[0]
            offset = durations[0] - CROSSFADE_DUR

            xfade_ok = True
            for j in range(1, len(clip_paths)):
                out_path = str(tmpdir / f"xfade_{j:02d}.mp4")
                cmd = [
                    "ffmpeg", "-y",
                    "-i", current, "-i", clip_paths[j],
                    "-filter_complex",
                    (
                        f"[0:v][1:v]xfade=transition=dissolve:"
                        f"duration={CROSSFADE_DUR}:offset={offset}[v];"
                        f"[0:a][1:a]acrossfade=d={CROSSFADE_DUR}:c1=tri:c2=tri[a]"
                    ),
                    "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-preset", "fast", "-crf", "22",
                    "-c:a", "aac", "-b:a", "192k",
                    out_path,
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"  xfade {j} ERRORE — fallback a concat semplice")
                    print(f"  {result.stderr[-300:]}")
                    xfade_ok = False
                    break

                current = out_path
                offset += durations[j] - CROSSFADE_DUR
                print(f"  xfade {j}/{len(clip_paths) - 1} OK")

            if xfade_ok:
                composed_path = current
            else:
                # Fallback: simple concat (no crossfade)
                print("  Fallback: concat demuxer (senza crossfade)")
                concat_file = tmpdir / "concat.txt"
                with open(concat_file, "w") as f:
                    for cp in clip_paths:
                        f.write(f"file '{cp}'\n")
                fallback_path = str(tmpdir / "composed.mp4")
                subprocess.run(
                    ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
                     "-i", str(concat_file), "-c", "copy", fallback_path],
                    check=True, capture_output=True,
                )
                composed_path = fallback_path

        # ---- PHASE 6: Global fade in/out + final encoding ----
        print("\n[6/7] Fade in/out + encoding YouTube H.264 High...\n")
        output_video = str(OUTPUT / "fluxion-demo.mp4")

        # Get actual composed duration
        probe = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", composed_path],
            capture_output=True, text=True,
        )
        composed_dur = float(probe.stdout.strip())
        fade_out_start = max(0, composed_dur - 2.5)

        cmd = [
            "ffmpeg", "-y", "-i", composed_path,
            "-vf", f"fade=t=in:st=0:d=1.5,fade=t=out:st={fade_out_start}:d=2",
            "-af", f"afade=t=in:st=0:d=1,afade=t=out:st={fade_out_start}:d=2",
            "-c:v", "libx264", "-preset", "slow", "-crf", "18",
            "-profile:v", "high", "-level", "4.1",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-r", "30",
            output_video,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  ERRORE encoding finale: {result.stderr[-500:]}")
            sys.exit(1)
        print("  Encoding completato.")

        # ---- PHASE 7: SRT + Thumbnail + Metadata ----
        print("\n[7/7] Sottotitoli + thumbnail + metadata...\n")

        srt_path = str(OUTPUT / "fluxion-demo.srt")
        generate_srt(SCENES, durations, srt_path)
        print(f"  SRT: {srt_path}")

        thumb_path = str(OUTPUT / "fluxion-demo-thumbnail.png")
        create_thumbnail(logo_path, thumb_path)
        print(f"  Thumbnail: {thumb_path}")

        meta_path = str(OUTPUT / "youtube-metadata.txt")
        chapters = generate_youtube_metadata(SCENES, durations, meta_path)
        print(f"  Metadata: {meta_path}")

        # ---- RESULT ----
        info = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration,size",
             "-of", "json", output_video],
            capture_output=True, text=True,
        )
        fmt = json.loads(info.stdout)["format"]
        dur = float(fmt["duration"])
        size_mb = int(fmt["size"]) / 1024 / 1024

        print("\n" + "=" * 60)
        print(f"  Video:       {output_video}")
        print(f"  Durata:      {dur:.0f}s ({dur / 60:.1f} min)")
        print(f"  Dimensione:  {size_mb:.1f} MB")
        print(f"  Sottotitoli: {srt_path}")
        print(f"  Thumbnail:   {thumb_path}")
        print(f"  Metadata:    {meta_path}")
        print("=" * 60)
        print(f"\n  Anteprima: open '{output_video}'")


if __name__ == "__main__":
    asyncio.run(main())
