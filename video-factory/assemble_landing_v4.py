#!/usr/bin/env python3
"""
assemble_landing_v4.py — Video landing FLUXION v4

Struttura PAS + Sara dialogue (waveform animata) + blur BG 16:9
Durata target: ~115 secondi

Sections:
  [0:00-0:08]  Clip Veo3 hook (parrucchiere stanca) + voiceover immediato
  [0:08-0:20]  Clip Veo3 agenda carta + voiceover problema
  [0:20-0:32]  Clip Veo3 hook_warm + voiceover agitazione
  [0:32-0:40]  Transizione → Sara intro
  [0:40-1:02]  WAVEFORM Sara dialogue (22s) con testo + tags
  [1:02-1:14]  Screenshot scheda parrucchiere + voiceover "Sara conosce"
  [1:14-1:22]  Screenshot calendario + voiceover promemoria WA
  [1:22-1:30]  Montaggio 3 schede (parrucchiere/veicoli/odontoiatrica)
  [1:30-1:50]  CTA frame prezzo + feature list bullets
  [1:50-1:57]  Logo + URL

Usage:
  python3 assemble_landing_v4.py           # genera tutto
  python3 assemble_landing_v4.py --audio-only  # solo audio
  python3 assemble_landing_v4.py --assemble-only  # solo video (audio già generato)
"""

import asyncio
import math
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import edge_tts
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE       = Path(__file__).parent
OUTPUT_DIR = BASE / "output" / "landing_v4"
CLIPS_DIR  = BASE / "output" / "parrucchiere" / "clips"
SCREENSHOTS = BASE.parent / "landing" / "screenshots"  # repo-relative (portable MacBook/iMac)
MUSIC_TENSE    = BASE / "assets" / "music" / "tense_background.mp3"
MUSIC_UPLIFTING = BASE / "assets" / "music" / "uplifting_commercial.mp3"
LOGO_CUTOUT    = BASE / "assets" / "logo_cutout.png"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Dimensions ────────────────────────────────────────────────────────────────
W, H = 1920, 1080   # 16:9 output
FPS  = 30
VOICE_SARA    = "it-IT-IsabellaNeural"
VOICE_CLIENTE = "it-IT-DiegoNeural"

# ── Audio segments ─────────────────────────────────────────────────────────────
SEGMENTS = {
    "hook": {
        "voice": VOICE_SARA,
        "text": "Il telefono squilla. Hai le mani occupate. Non puoi rispondere.",
        "rate": "-5%",
    },
    "problema": {
        "voice": VOICE_SARA,
        "text": "Quel cliente non ha aspettato. Ha già chiamato qualcun altro. Ti succede tutti i giorni.",
        "rate": "-5%",
    },
    "agitazione": {
        "voice": VOICE_SARA,
        "text": "Un cliente perso al giorno. Duecentocinquanta all'anno. Settemila e cinquecento euro che non tornano. E l'agenda è un disastro: doppie prenotazioni, appuntamenti saltati.",
        "rate": "-5%",
    },
    "sara_intro": {
        "voice": VOICE_SARA,
        "text": "E se qualcuno rispondesse per te? Sempre. Anche di sera. Anche la domenica. Si chiama Sara.",
        "rate": "-5%",
    },
    # Dialogo Sara — ogni battuta separata per timing preciso
    "dial_sara_1": {
        "voice": VOICE_SARA,
        "text": "Buongiorno, Salone Bella — sono Sara!",
        "rate": "+0%",
    },
    "dial_cliente_1": {
        "voice": VOICE_CLIENTE,
        "text": "Ciao, sono Marco, vorrei prenotare per questa settimana.",
        "rate": "+0%",
    },
    "dial_sara_2": {
        "voice": VOICE_SARA,
        "text": "Ciao Marco! L'ultima volta ha fatto colore con Marta... rifacciamo lo stesso?",
        "rate": "+0%",
    },
    "dial_cliente_2": {
        "voice": VOICE_CLIENTE,
        "text": "Sì, esatto.",
        "rate": "+0%",
    },
    "dial_sara_3": {
        "voice": VOICE_SARA,
        "text": "Perfetto! So che preferisce il mattino — giovedì alle dieci con Marta va bene?",
        "rate": "+0%",
    },
    "dial_cliente_3": {
        "voice": VOICE_CLIENTE,
        "text": "Benissimo, grazie.",
        "rate": "+0%",
    },
    "dial_sara_4": {
        "voice": VOICE_SARA,
        "text": "Le mando la conferma su WhatsApp. A giovedì Marco!",
        "rate": "+0%",
    },
    "sara_conosce": {
        "voice": VOICE_SARA,
        "text": "Sara non risponde solo al telefono. Sa cosa ha fatto ogni cliente l'ultima volta. Conosce le sue preferenze, la sua operatrice preferita, se ama chiacchierare o stare in silenzio. Come la tua migliore dipendente. Sempre.",
        "rate": "-5%",
    },
    "app_demo": {
        "voice": VOICE_SARA,
        "text": "Il calendario si aggiorna da solo. Il promemoria WhatsApp parte ventiquattro ore prima. Gli appuntamenti saltati si dimezzano.",
        "rate": "-5%",
    },
    "verticals": {
        "voice": VOICE_SARA,
        "text": "Sei parrucchiere, meccanico o dentista — FLUXION si adatta al tuo lavoro con la scheda giusta per ogni settore.",
        "rate": "-5%",
    },
    "cta_price": {
        "voice": VOICE_SARA,
        "text": "FLUXION costa quattrocentonovantasette euro. Non al mese. Non all'anno. Una volta sola. Per sempre. Nessun canone, nessun abbonamento. Tutto incluso: Sara, calendario, WhatsApp automatico, schede clienti, cassa, analytics e molto altro. Si ripaga con i primi diciassette clienti che Sara recupera per te.",
        "rate": "-5%",
    },
    "cta_url": {
        "voice": VOICE_SARA,
        "text": "Vai su fluxion punto it. Smetti di regalare clienti alla concorrenza.",
        "rate": "-5%",
    },
}

# ── Dialogue lines for waveform overlay ──────────────────────────────────────
DIALOGUE_LINES = [
    ("SARA",    "dial_sara_1",    "Buongiorno, Salone Bella — sono Sara!",                    None),
    ("CLIENTE", "dial_cliente_1", "Ciao, sono Marco, vorrei prenotare.",                       None),
    ("SARA",    "dial_sara_2",    "Ciao Marco! L'ultima volta colore con Marta...",             "📋 Ultima visita: 12 mar"),
    ("CLIENTE", "dial_cliente_2", "Sì, esatto.",                                                None),
    ("SARA",    "dial_sara_3",    "So che preferisce il mattino — giovedì alle 10?",            "⭐ Preferenze salvate"),
    ("CLIENTE", "dial_cliente_3", "Benissimo, grazie.",                                         None),
    ("SARA",    "dial_sara_4",    "Conferma su WhatsApp. A giovedì!",                           "📱 WhatsApp automatico"),
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def run(cmd, desc="", check=True):
    if desc:
        print(f"  {desc}...", end=" ", flush=True)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 and check:
        print("ERRORE")
        print(f"    {(result.stderr or 'no stderr')[-600:]}")
        return False
    if desc:
        print("OK")
    return True


def get_duration(path):
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True,
    )
    try:
        return float(r.stdout.strip())
    except Exception:
        return 0.0


def best_clip(name):
    candidates = sorted(CLIPS_DIR.glob(f"*{name}*.mp4"), key=lambda p: p.stat().st_size, reverse=True)
    return candidates[0] if candidates else None


def find_font(bold=True, size=40):
    fonts = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Inter-Bold.ttf" if bold else "/Library/Fonts/Inter-Regular.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for f in fonts:
        if os.path.exists(f):
            try:
                return ImageFont.truetype(f, size)
            except Exception:
                continue
    return ImageFont.load_default()


# ── Step 1: Generate audio ────────────────────────────────────────────────────

async def gen_segment(key, seg, out_path):
    communicate = edge_tts.Communicate(
        seg["text"],
        seg["voice"],
        rate=seg.get("rate", "0%"),
    )
    await communicate.save(str(out_path))


async def generate_all_audio():
    print("\n[AUDIO] Generazione segmenti voiceover...")
    for key, seg in SEGMENTS.items():
        out = OUTPUT_DIR / f"seg_{key}.mp3"
        if out.exists() and out.stat().st_size > 1000:
            print(f"  {key}: già esistente, skip")
            continue
        print(f"  {key}: generando...", end=" ", flush=True)
        try:
            await gen_segment(key, seg, out)
            size = out.stat().st_size if out.exists() else 0
            print(f"OK ({size//1024}KB)")
        except Exception as e:
            print(f"ERRORE: {e}")
    print("[AUDIO] Tutti i segmenti pronti.")


def concat_dialogue_audio():
    """Concatena le battute del dialogo in un unico file con silenzio tra le righe."""
    parts = []
    for _, seg_key, _, _ in DIALOGUE_LINES:
        p = OUTPUT_DIR / f"seg_{seg_key}.mp3"
        if p.exists():
            parts.append(str(p))

    if not parts:
        return None

    out = OUTPUT_DIR / "dialogue_full.mp3"
    if out.exists():
        print("  dialogue_full.mp3: già esistente, skip")
        return out

    # Usa ffmpeg concat con 0.3s silenzio tra battute
    silence = OUTPUT_DIR / "silence_03s.mp3"
    if not silence.exists():
        run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
             "-t", "0.3", "-acodec", "libmp3lame", "-ar", "24000", str(silence)],
            "Generazione silenzio 0.3s")

    # Build inputs + filter
    inputs = []
    filter_parts = []
    idx = 0
    for i, p in enumerate(parts):
        inputs += ["-i", p]
        filter_parts.append(f"[{idx}:a]")
        idx += 1
        if i < len(parts) - 1:
            inputs += ["-i", str(silence)]
            filter_parts.append(f"[{idx}:a]")
            idx += 1

    n = len(filter_parts)
    filter_str = "".join(filter_parts) + f"concat=n={n}:v=0:a=1[out]"

    cmd = ["ffmpeg", "-y"] + inputs + [
        "-filter_complex", filter_str,
        "-map", "[out]",
        "-acodec", "libmp3lame", "-ar", "24000",
        str(out)
    ]
    run(cmd, "Concatenazione dialogo")
    return out


# ── Step 2: Build per-section video segments ──────────────────────────────────

def make_blur_bg_clip(source_clip, duration, out_path):
    """
    Converte clip 9:16 in 16:9 con blur background.
    - sfondo: clip scalata a 1920x1080, blur forte
    - foreground: clip al centro, proportional fit
    - output forzato a 30fps per compatibilità concat
    """
    if Path(out_path).exists():
        print(f"  {Path(out_path).name}: già esistente, skip")
        return True

    cmd = [
        "ffmpeg", "-y",
        "-i", str(source_clip),
        "-t", str(duration),
        "-vf",
        (
            "split[original][copy];"
            "[copy]scale=1920:1080,setsar=1,gblur=sigma=30[bg];"
            "[original]scale=607:1080,setsar=1[fg];"
            "[bg][fg]overlay=(W-w)/2:(H-h)/2,"
            f"fps={FPS}"
        ),
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-an",
        str(out_path)
    ]
    return run(cmd, f"Blur BG: {Path(out_path).name}")


def make_screenshot_frame_16x9(screenshot_path, subtitle, output_path, duration=6.0):
    """Frame 1920x1080: gradient navy bg + logo badge + screenshot centrato + sottotitolo."""
    if Path(output_path).exists():
        return

    # Background gradient
    bg = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    pixels = bg.load()
    cx, cy = W / 2, H / 2
    max_dist = math.sqrt(cx**2 + cy**2)
    for y in range(H):
        for x in range(W):
            dist = min(math.sqrt((x-cx)**2 + (y-cy)**2) / max_dist, 1.0)
            r = int(12 * (1 - dist * 0.8))
            g = int(25 * (1 - dist * 0.8))
            b = int(50 * (1 - dist * 0.8))
            pixels[x, y] = (r, g, b, 255)

    # Logo badge top-left
    if LOGO_CUTOUT.exists():
        logo = Image.open(str(LOGO_CUTOUT)).convert("RGBA")
        logo_sm = logo.resize((52, 52), Image.LANCZOS)
        bg.paste(logo_sm, (32, 28), logo_sm)

    draw = ImageDraw.Draw(bg)
    draw.text((94, 40), "FLUXION", fill=(80, 195, 215, 240), font=find_font(bold=True, size=28))

    # Screenshot
    scr = Image.open(str(screenshot_path)).convert("RGBA")
    max_w = W - 200
    max_h = H - 220
    scale = min(max_w / scr.width, max_h / scr.height)
    scr_w, scr_h = int(scr.width * scale), int(scr.height * scale)
    scr = scr.resize((scr_w, scr_h), Image.LANCZOS)

    radius = 16
    mask = Image.new("L", (scr_w, scr_h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, scr_w-1, scr_h-1], radius=radius, fill=255)
    shadow = Image.new("RGBA", (scr_w+60, scr_h+60), (0,0,0,0))
    ImageDraw.Draw(shadow).rounded_rectangle([30, 30, scr_w+29, scr_h+29], radius=radius, fill=(0,0,0,140))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=18))

    scr_x = (W - scr_w) // 2
    scr_y = (H - scr_h) // 2 - 30
    bg.paste(shadow, (scr_x - 30, scr_y - 30), shadow)
    bg.paste(scr, (scr_x, scr_y), mask)

    # Subtitle
    font_sub = find_font(bold=False, size=36)
    draw.text((W//2, scr_y + scr_h + 40), subtitle,
              fill=(200, 220, 240, 220), font=font_sub, anchor="mm")

    png_path = str(output_path).replace(".mp4", ".png")
    bg.convert("RGB").save(png_path)

    # PNG → video
    run(["ffmpeg", "-y", "-loop", "1", "-i", png_path,
         "-t", str(duration), "-vf", f"fps={FPS}",
         "-c:v", "libx264", "-preset", "fast", "-crf", "23",
         "-pix_fmt", "yuv420p", "-an", str(output_path)], check=False)


def make_waveform_section(dialogue_audio, out_path):
    """
    Sezione Sara dialogue: waveform animata + testo battute + tags.
    Sfondo navy scuro, waveform teal al centro, testo in basso.
    """
    if Path(out_path).exists():
        print(f"  {Path(out_path).name}: già esistente, skip")
        return True

    duration = get_duration(str(dialogue_audio))

    # Step 1: genera PNG background per la sezione waveform
    bg_png = OUTPUT_DIR / "waveform_bg.png"
    if not bg_png.exists():
        bg = Image.new("RGB", (W, H), (8, 18, 38))
        draw = ImageDraw.Draw(bg)

        # Logo + brand top-left
        if LOGO_CUTOUT.exists():
            logo = Image.open(str(LOGO_CUTOUT)).convert("RGBA")
            logo_sm = logo.resize((52, 52), Image.LANCZOS)
            bg.paste(logo_sm, (32, 28), logo_sm)
        draw.text((94, 40), "FLUXION", fill=(80, 195, 215), font=find_font(bold=True, size=28))

        # "SARA — La tua segretaria" header
        draw.text((W//2, 120), "SARA — La tua segretaria che non va mai in ferie",
                  fill=(80, 195, 215), font=find_font(bold=True, size=42), anchor="mm")

        # Icona telefono / indicatore chiamata
        draw.ellipse([(W//2 - 8, 170), (W//2 + 8, 186)], fill=(80, 195, 215))
        draw.text((W//2, 205), "● CHIAMATA IN CORSO",
                  fill=(80, 195, 215, 180), font=find_font(bold=False, size=28), anchor="mm")

        bg.save(str(bg_png))

    # Step 2: genera video waveform con FFmpeg showwaves
    # Overlay: sfondo PNG + waveform centrata verticalmente
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(bg_png),
        "-i", str(dialogue_audio),
        "-filter_complex",
        (
            f"[1:a]showwaves=s={W}x220:mode=cline:colors=0x50C3D7|0x50C3D7:"
            f"scale=lin:draw=full[wv];"
            f"[0:v]scale={W}:{H},fps={FPS}[bg];"
            f"[bg][wv]overlay=0:{H//2 - 110}[out]"
        ),
        "-map", "[out]", "-map", "1:a",
        "-t", str(duration),
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        str(out_path)
    ]
    return run(cmd, "Waveform Sara dialogue")


def make_cta_frame(out_path, duration=20.0):
    """Frame CTA: prezzo grande + feature bullets + URL."""
    if Path(out_path).exists():
        print(f"  {Path(out_path).name}: già esistente, skip")
        return

    bg = Image.new("RGB", (W, H), (8, 18, 38))
    draw = ImageDraw.Draw(bg)

    # Gradient radiale leggero
    cx, cy = W // 2, H // 2
    max_d = math.sqrt(cx**2 + cy**2)
    pixels = bg.load()
    for y in range(H):
        for x in range(W):
            d = min(math.sqrt((x-cx)**2 + (y-cy)**2) / max_d, 1.0)
            r = int(8 + 10*(1-d))
            g = int(18 + 20*(1-d))
            b = int(38 + 40*(1-d))
            pixels[x, y] = (r, g, b)

    # Logo
    if LOGO_CUTOUT.exists():
        logo = Image.open(str(LOGO_CUTOUT)).convert("RGBA")
        logo_sm = logo.resize((64, 64), Image.LANCZOS)
        bg.paste(logo_sm, (32, 28), logo_sm)
    draw.text((106, 42), "FLUXION", fill=(80, 195, 215), font=find_font(bold=True, size=36))

    # Prezzo centrale
    draw.text((W//2, 260), "€497", fill=(255, 255, 255), font=find_font(bold=True, size=160), anchor="mm")
    draw.text((W//2, 360), "una volta sola — per sempre", fill=(80, 195, 215), font=find_font(bold=False, size=44), anchor="mm")
    draw.text((W//2, 415), "Nessun canone mensile. Nessun abbonamento.", fill=(160, 180, 200), font=find_font(bold=False, size=32), anchor="mm")

    # Linea separatrice
    draw.line([(W//2 - 400, 455), (W//2 + 400, 455)], fill=(50, 80, 120), width=2)

    # Feature bullets — 2 colonne
    features_left = [
        "✓  Sara — segretaria AI 24/7",
        "✓  Calendario appuntamenti",
        "✓  Schede clienti avanzate",
        "✓  Cassa integrata",
    ]
    features_right = [
        "✓  WhatsApp automatico",
        "✓  Analytics e report",
        "✓  Pacchetti fedeltà",
        "✓  Fatturazione",
    ]
    font_feat = find_font(bold=False, size=34)
    y_start = 490
    for i, f in enumerate(features_left):
        draw.text((W//2 - 420, y_start + i*52), f, fill=(200, 220, 240), font=font_feat)
    for i, f in enumerate(features_right):
        draw.text((W//2 + 30, y_start + i*52), f, fill=(200, 220, 240), font=font_feat)

    # ROI hint
    draw.text((W//2, 720), "Si ripaga con i primi 17 clienti recuperati da Sara",
              fill=(80, 195, 215), font=find_font(bold=False, size=32), anchor="mm")

    # URL
    draw.rectangle([(W//2 - 300, 770), (W//2 + 300, 830)], fill=(80, 195, 215))
    draw.text((W//2, 800), "fluxion-landing.pages.dev", fill=(8, 18, 38), font=find_font(bold=True, size=38), anchor="mm")

    # Competitor contrast
    draw.text((W//2, 880), "Competitor come Treatwell: €120/mese + commissioni",
              fill=(120, 140, 160), font=find_font(bold=False, size=26), anchor="mm")

    png_path = str(out_path).replace(".mp4", ".png")
    bg.save(png_path)
    run(["ffmpeg", "-y", "-loop", "1", "-i", png_path,
         "-t", str(duration), "-vf", f"fps={FPS}",
         "-c:v", "libx264", "-preset", "fast", "-crf", "23",
         "-pix_fmt", "yuv420p", "-an", str(out_path)], check=False)


def make_multi_vertical_frame(out_path, duration=8.0):
    """Montaggio 3 schede verticali fianco a fianco: parrucchiere / veicoli / odontoiatrica."""
    if Path(out_path).exists():
        print(f"  {Path(out_path).name}: già esistente, skip")
        return

    bg = Image.new("RGB", (W, H), (8, 18, 38))
    draw = ImageDraw.Draw(bg)

    # Gradient
    pixels = bg.load()
    cx, cy = W//2, H//2
    max_d = math.sqrt(cx**2 + cy**2)
    for y in range(H):
        for x in range(W):
            d = min(math.sqrt((x-cx)**2 + (y-cy)**2) / max_d, 1.0)
            pixels[x, y] = (int(8+8*(1-d)), int(18+16*(1-d)), int(38+30*(1-d)))

    # Logo
    if LOGO_CUTOUT.exists():
        logo = Image.open(str(LOGO_CUTOUT)).convert("RGBA")
        bg.paste(logo.resize((52, 52), Image.LANCZOS), (32, 28), logo.resize((52, 52), Image.LANCZOS))
    draw.text((94, 40), "FLUXION", fill=(80, 195, 215), font=find_font(bold=True, size=28))

    screenshots = [
        (SCREENSHOTS / "12-scheda-parrucchiere.png", "Parrucchiere"),
        (SCREENSHOTS / "18-scheda-veicoli.png", "Officina"),
        (SCREENSHOTS / "17-scheda-odontoiatrica.png", "Dentista"),
    ]

    n = len(screenshots)
    pad = 60
    slot_w = (W - pad * (n + 1)) // n
    y_top = 130

    for i, (scr_path, label) in enumerate(screenshots):
        if not scr_path.exists():
            continue
        scr = Image.open(str(scr_path)).convert("RGBA")
        max_h = H - y_top - 120
        scale = min(slot_w / scr.width, max_h / scr.height)
        sw, sh = int(scr.width * scale), int(scr.height * scale)
        scr = scr.resize((sw, sh), Image.LANCZOS)

        mask = Image.new("L", (sw, sh), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, sw-1, sh-1], radius=14, fill=255)

        x = pad + i * (slot_w + pad) + (slot_w - sw) // 2
        y = y_top
        shadow = Image.new("RGBA", (sw+40, sh+40), (0,0,0,0))
        ImageDraw.Draw(shadow).rounded_rectangle([20, 20, sw+19, sh+19], radius=14, fill=(0,0,0,130))
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=12))
        bg.paste(shadow, (x-20, y-20), shadow)
        bg.paste(scr, (x, y), mask)
        draw.text((x + sw//2, y + sh + 20), label,
                  fill=(80, 195, 215), font=find_font(bold=True, size=34), anchor="mm")

    draw.text((W//2, H - 40), "La scheda giusta per ogni settore",
              fill=(160, 180, 200), font=find_font(bold=False, size=30), anchor="mm")

    png_path = str(out_path).replace(".mp4", ".png")
    bg.save(png_path)
    run(["ffmpeg", "-y", "-loop", "1", "-i", png_path,
         "-t", str(duration), "-vf", f"fps={FPS}",
         "-c:v", "libx264", "-preset", "fast", "-crf", "23",
         "-pix_fmt", "yuv420p", "-an", str(out_path)], check=False)


# ── Step 3: Assemble final video ──────────────────────────────────────────────

def attach_audio_to_clip(video_path, audio_path, out_path):
    """Attacca audio a un video muto, troncando al più corto."""
    if Path(out_path).exists():
        return
    v_dur = get_duration(str(video_path))
    a_dur = get_duration(str(audio_path))
    duration = min(v_dur, a_dur) if a_dur > 0 else v_dur

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-t", str(duration),
        "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
        "-shortest",
        str(out_path)
    ]
    run(cmd, f"Attach audio: {Path(out_path).name}")


def make_text_overlay_png(t0, t1, line1, line2, idx):
    """
    Genera un PNG RGBA 1920x1080 con testo overlay.
    - Semi-transparent pill background
    - line1: bianco grande
    - line2: teal (se presente)
    Restituisce path del PNG.
    """
    out_png = OUTPUT_DIR / f"overlay_{idx:02d}.png"
    if out_png.exists():
        return out_png

    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    TEAL_COL  = (80, 195, 215, 255)
    WHITE_COL = (255, 255, 255, 255)
    BOX_COL   = (0, 0, 0, 160)

    font1 = find_font(bold=True,  size=68)
    font2 = find_font(bold=True,  size=82)

    # Calcola dimensioni testo
    bb1 = draw.textbbox((0, 0), line1, font=font1)
    tw1, th1 = bb1[2] - bb1[0], bb1[3] - bb1[1]

    if line2:
        bb2 = draw.textbbox((0, 0), line2, font=font2)
        tw2, th2 = bb2[2] - bb2[0], bb2[3] - bb2[1]
    else:
        tw2, th2 = 0, 0

    # Box background: copre entrambe le righe
    total_h = th1 + (th2 + 20 if line2 else 0)
    max_w = max(tw1, tw2) + 80
    box_y1 = int(H * 0.76) - 20
    box_y2 = box_y1 + total_h + 40
    box_x1 = (W - max_w) // 2
    box_x2 = box_x1 + max_w

    # Disegna rettangolo arrotondato semi-trasparente
    draw.rounded_rectangle([box_x1, box_y1, box_x2, box_y2], radius=20, fill=BOX_COL)

    # Testo line1 (bianco) con shadow
    x1 = (W - tw1) // 2
    y1 = box_y1 + 18
    # Shadow
    for dx, dy in [(2,2),(3,3)]:
        draw.text((x1+dx, y1+dy), line1, font=font1, fill=(0,0,0,200))
    draw.text((x1, y1), line1, font=font1, fill=WHITE_COL)

    # Testo line2 (teal)
    if line2:
        x2 = (W - tw2) // 2
        y2 = y1 + th1 + 16
        for dx, dy in [(2,2),(3,3)]:
            draw.text((x2+dx, y2+dy), line2, font=font2, fill=(0,0,0,200))
        draw.text((x2, y2), line2, font=font2, fill=TEAL_COL)

    img.save(str(out_png))
    return out_png


def add_kinetic_text(video_path, out_path, section_timings):
    """
    Aggiunge kinetic text overlay usando Pillow PNG + FFmpeg overlay filter.
    section_timings: lista di (t_start, t_end, line1, line2_teal)
    """
    if Path(out_path).exists():
        print(f"  {Path(out_path).name}: già esistente, skip")
        return True

    print("  Generazione PNG overlay...", end=" ", flush=True)
    overlays = []
    for i, (t0, t1, line1, line2) in enumerate(section_timings):
        png = make_text_overlay_png(t0, t1, line1, line2, i)
        overlays.append((t0, t1, png))
    print("OK")

    # Build FFmpeg command con overlay multiplo
    # Input 0: video principale
    # Input 1..N: PNG overlay
    inputs = ["-i", str(video_path)]
    for _, _, png in overlays:
        inputs += ["-i", str(png)]

    # Filter complex: chain di overlay con enable='between(t,start,end)'
    # Ogni overlay converte PNG in video e lo applica
    filter_parts = []
    prev = "[0:v]"
    for i, (t0, t1, png) in enumerate(overlays):
        stream_idx = i + 1
        cur = f"[v{i+1}]"
        filter_parts.append(
            f"{prev}[{stream_idx}:v]overlay=0:0:enable='between(t,{t0:.2f},{t1:.2f})'{cur}"
        )
        prev = cur

    filter_complex = ";".join(filter_parts)
    out_map = f"[v{len(overlays)}]"

    cmd = (
        ["ffmpeg", "-y"]
        + inputs
        + [
            "-filter_complex", filter_complex,
            "-map", out_map,
            "-map", "0:a",
            "-c:v", "libx264", "-preset", "fast", "-crf", "22",
            "-c:a", "copy",
            "-pix_fmt", "yuv420p",
            str(out_path),
        ]
    )
    return run(cmd, "Kinetic text overlay")


def mix_with_music(video_path, music_path, out_path, music_vol=0.08):
    """Mixa audio esistente del video con musica di sottofondo."""
    if Path(out_path).exists():
        return
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-stream_loop", "-1", "-i", str(music_path),
        "-filter_complex",
        f"[1:a]volume={music_vol}[music];[0:a][music]amix=inputs=2:duration=first[aout]",
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
        str(out_path)
    ]
    run(cmd, f"Mix musica: {Path(out_path).name}")


def concat_videos(video_list, out_path):
    """Concatena lista di video in un unico file."""
    list_file = OUTPUT_DIR / "concat_list.txt"
    with open(str(list_file), "w") as f:
        for v in video_list:
            f.write(f"file '{v}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(list_file),
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "aac", "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        str(out_path)
    ]
    return run(cmd, "Concatenazione finale")


def pad_video_to_audio(video_path, audio_path, out_path):
    """Attacca audio al video. Se audio > video, fa LOOP del video (no freeze frame).

    Fix S167: sostituito tpad=stop_mode=clone (che congelava l'ultimo frame causando
    17 freeze events per 105s totali nel landing_v4_16x9.mp4) con -stream_loop -1
    che ricicla la clip finche' l'audio finisce. -shortest garantisce stop pulito.
    """
    v_dur = get_duration(str(video_path))
    a_dur = get_duration(str(audio_path))
    needs_loop = a_dur > v_dur

    cmd = ["ffmpeg", "-y"]
    if needs_loop:
        cmd += ["-stream_loop", "-1"]  # loop video input fino a -shortest
    cmd += [
        "-i", str(video_path),
        "-i", str(audio_path),
        "-filter_complex", f"[0:v]fps={FPS},scale={W}:{H},setsar=1[vout]",
        "-map", "[vout]", "-map", "1:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        str(out_path)
    ]
    run(cmd, f"Pad: {Path(out_path).name}")


def assemble():
    print("\n[ASSEMBLE] Costruzione sezioni video...")
    segs = {k: OUTPUT_DIR / f"seg_{k}.mp3" for k in SEGMENTS}

    # Clip Veo3 — 3 settori diversi per varietà visiva
    BASE_CLIPS = Path(__file__).parent / "output"
    def get_clip(vertical, pattern):
        d = BASE_CLIPS / vertical / "clips"
        candidates = sorted(d.glob(f"*{pattern}*.mp4"), key=lambda p: p.stat().st_size, reverse=True)
        return candidates[0] if candidates else None

    clip_s1 = get_clip("parrucchiere", "clip1_v2") or get_clip("parrucchiere", "clip1")
    clip_s2 = get_clip("officina", "clip1")        # meccanico — non può rispondere
    clip_s3 = get_clip("barbiere", "clip1")         # barbiere con rasoio — stesso pain
    if not clip_s2: clip_s2 = get_clip("parrucchiere", "clip2")
    if not clip_s3: clip_s3 = get_clip("parrucchiere", "hook_warm") or get_clip("parrucchiere", "clip3")

    sections = []

    # ── S1: HOOK (parrucchiera stanca) ────────────────────────────────────────
    s1_mute = OUTPUT_DIR / "s1_clip_mute.mp4"
    make_blur_bg_clip(clip_s1, 8.0, s1_mute)
    s1 = OUTPUT_DIR / "s1.mp4"
    pad_video_to_audio(s1_mute, segs["hook"], s1)
    sections.append(s1)

    # ── S2: PROBLEMA (meccanico — officina) ───────────────────────────────────
    s2_mute = OUTPUT_DIR / "s2_clip_mute.mp4"
    make_blur_bg_clip(clip_s2, 10.0, s2_mute)
    s2 = OUTPUT_DIR / "s2.mp4"
    pad_video_to_audio(s2_mute, segs["problema"], s2)
    sections.append(s2)

    # ── S3: AGITAZIONE (barbiere con rasoio) ──────────────────────────────────
    s3_mute = OUTPUT_DIR / "s3_clip_mute.mp4"
    make_blur_bg_clip(clip_s3, 16.0, s3_mute)
    s3 = OUTPUT_DIR / "s3.mp4"
    pad_video_to_audio(s3_mute, segs["agitazione"], s3)
    sections.append(s3)

    # ── S4: SARA INTRO (screenshot 08-voice + voiceover) ──────────────────────
    s4_mute = OUTPUT_DIR / "s4_mute.mp4"
    make_screenshot_frame_16x9(SCREENSHOTS / "08-voice.png", "Sara — La tua segretaria AI", s4_mute, duration=10.0)
    s4 = OUTPUT_DIR / "s4.mp4"
    pad_video_to_audio(s4_mute, segs["sara_intro"], s4)
    sections.append(s4)

    # ── S5: WAVEFORM DIALOGO ───────────────────────────────────────────────────
    dialogue_audio = concat_dialogue_audio()
    s5 = OUTPUT_DIR / "s5_waveform.mp4"
    make_waveform_section(dialogue_audio, s5)
    sections.append(s5)

    # ── S6: SARA CONOSCE (scheda parrucchiere + voiceover) ────────────────────
    s6_mute = OUTPUT_DIR / "s6_mute.mp4"
    make_screenshot_frame_16x9(SCREENSHOTS / "12-scheda-parrucchiere.png",
                                "Storico completo per ogni cliente", s6_mute, duration=16.0)
    s6 = OUTPUT_DIR / "s6.mp4"
    pad_video_to_audio(s6_mute, segs["sara_conosce"], s6)
    sections.append(s6)

    # ── S7: APP DEMO — calendario (screenshot 02 + voiceover) ─────────────────
    s7_mute = OUTPUT_DIR / "s7_mute.mp4"
    make_screenshot_frame_16x9(SCREENSHOTS / "02-calendario.png",
                                "Promemoria WhatsApp automatico 24h prima", s7_mute, duration=10.0)
    s7 = OUTPUT_DIR / "s7.mp4"
    pad_video_to_audio(s7_mute, segs["app_demo"], s7)
    sections.append(s7)

    # ── S8: VERTICALS MONTAGGIO ────────────────────────────────────────────────
    s8_mute = OUTPUT_DIR / "s8_mute.mp4"
    make_multi_vertical_frame(s8_mute, duration=10.0)
    s8 = OUTPUT_DIR / "s8.mp4"
    pad_video_to_audio(s8_mute, segs["verticals"], s8)
    sections.append(s8)

    # ── S9: CTA PREZZO + FEATURE LIST ─────────────────────────────────────────
    s9_mute = OUTPUT_DIR / "s9_cta_mute.mp4"
    make_cta_frame(s9_mute, duration=25.0)
    s9 = OUTPUT_DIR / "s9.mp4"
    pad_video_to_audio(s9_mute, segs["cta_price"], s9)
    sections.append(s9)

    # ── S10: URL FINALE ────────────────────────────────────────────────────────
    s10_mute = OUTPUT_DIR / "s10_mute.mp4"
    make_screenshot_frame_16x9(SCREENSHOTS / "01-dashboard.png",
                                "fluxion-landing.pages.dev", s10_mute, duration=10.0)
    s10 = OUTPUT_DIR / "s10.mp4"
    pad_video_to_audio(s10_mute, segs["cta_url"], s10)
    sections.append(s10)

    # ── CALC TIMINGS per kinetic text ─────────────────────────────────────────
    print("\n[ASSEMBLE] Calcolo timings sezioni...")
    timings = []
    cursor = 0.0
    for sec in sections:
        d = get_duration(str(sec))
        timings.append((cursor, cursor + d))
        cursor += d
    # timings[i] = (t_start, t_end) per sezione i
    # sections: s1=0,s2=1,s3=2,s4=3,s5=4,s6=5,s7=6,s8=7,s9=8,s10=9
    def T(i, frac_start=0.0, frac_end=1.0):
        t0, t1 = timings[i]
        dur = t1 - t0
        return t0 + dur * frac_start, t0 + dur * frac_end

    # Kinetic text SOLO sulle clip Veo3 (S1/S2/S3) — no testo built-in
    # Le sezioni screenshot/waveform/CTA hanno già testo proprio → no overlap
    text_overlays = [
        # S1 (0): parrucchiera — hook
        (*T(0, 0.25, 0.90), "Il telefono squilla.", "Hai le mani occupate."),
        # S2 (1): meccanico officina — problema
        (*T(1, 0.25, 0.90), "Quel cliente non ha aspettato.", "Ha chiamato qualcun altro."),
        # S3 (2): barbiere — agitazione con numero
        (*T(2, 0.08, 0.45), "250 clienti persi all'anno.", "€7.500 che non tornano."),
        (*T(2, 0.55, 0.90), "Doppie prenotazioni.", "Appuntamenti saltati."),
    ]

    # ── CONCAT FINALE ─────────────────────────────────────────────────────────
    print("\n[ASSEMBLE] Concatenazione finale...")
    raw_concat = OUTPUT_DIR / "landing_v4_raw.mp4"
    ok = concat_videos([str(s) for s in sections if s.exists()], raw_concat)
    if not ok:
        print("ERRORE: concatenazione fallita")
        return

    # ── KINETIC TEXT ──────────────────────────────────────────────────────────
    with_text = OUTPUT_DIR / "landing_v4_text.mp4"
    add_kinetic_text(raw_concat, with_text, text_overlays)

    # ── MIX MUSICA ────────────────────────────────────────────────────────────
    final = OUTPUT_DIR / "landing_v4_16x9.mp4"
    mix_with_music(with_text, MUSIC_UPLIFTING, final, music_vol=0.07)

    total = get_duration(str(final))
    print(f"\n✅ VIDEO COMPLETATO: {final}")
    print(f"   Durata: {total:.1f}s ({total/60:.1f} minuti)")
    print(f"   Dimensione: {final.stat().st_size / 1024 / 1024:.1f} MB")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    audio_only   = "--audio-only"   in sys.argv
    assemble_only = "--assemble-only" in sys.argv

    if not assemble_only:
        asyncio.run(generate_all_audio())
        concat_dialogue_audio()

    if not audio_only:
        assemble()


if __name__ == "__main__":
    main()
