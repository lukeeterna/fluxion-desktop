"""
build_parrucchiere_v3.py — FLUXION Video Parrucchiere 80s
FIX: screenshot croppati per mobile, audio non tagliato, CTA con logo
"""

import asyncio
import subprocess
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ─── Config ────────────────────────────────────────────────────────────────
SCREENSHOTS = Path("../landing/screenshots")
CLIPS_DIR = Path("output/parrucchiere/clips")
LOGO = Path("../landing/logo_fluxion.jpg")
OUT_DIR = Path("output/parrucchiere")
OUT_DIR.mkdir(parents=True, exist_ok=True)

W, H = 1080, 1920  # 9:16
FPS = 30
TMP = Path(tempfile.mkdtemp())

FONT_PATH = "/System/Library/Fonts/Helvetica.ttc"


def font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except:
        return ImageFont.load_default()


# ─── Screenshot crop regions (focus su area rilevante) ─────────────────────
# Crop box = (left%, top%, right%, bottom%) dell'immagine originale
# Poi viene scalato a riempire 1080x1920

BLOCKS = [
    {
        "id": "01_hook",
        "type": "veo3",
        "source": CLIPS_DIR / "parrucchiere_salon_beauty_v2.mp4",  # v2 = 5.2MB, better quality
        "voiceover": "Ogni cliente ha la sua formula colore. Ma tu ce l'hai scritta a penna, su un quaderno. E quando ti chiede 'stesso colore di sempre', tu non la trovi più.",
        "vo_delay": 1.5,
        "min_duration": 10,
    },
    {
        "id": "02_dashboard",
        "type": "screenshot",
        "source": SCREENSHOTS / "01-dashboard.png",
        "crop": (0.02, 0.02, 0.98, 0.50),  # Top: Buongiorno + 4 card — crop aggressivo
        "zoom_start": 1.0, "zoom_end": 1.2,
        "zoom_cx": 0.5, "zoom_cy": 0.45,
        "voiceover": "Con FLUXION apri e vedi tutto. Appuntamenti di oggi, fatturato del mese, clienti in arrivo. Tutto in una schermata.",
        "vo_delay": 0.3,
        "min_duration": 8,
        "subtitle": "Tutto sotto controllo — ogni mattina",
    },
    {
        "id": "03_scheda",
        "type": "screenshot",
        "source": SCREENSHOTS / "12-scheda-parrucchiere.png",
        "crop": (0.28, 0.18, 0.97, 0.82),  # Modal scheda — crop stretto
        "zoom_start": 1.0, "zoom_end": 1.3,
        "zoom_cx": 0.5, "zoom_cy": 0.45,
        "voiceover": "La scheda di ogni cliente. Formula colore, tipo di capello, porosità, base naturale, trattamenti chimici. Sempre aggiornata, sempre leggibile.",
        "vo_delay": 0.3,
        "min_duration": 9,
        "subtitle": "Scheda cliente — Formula colore",
    },
    {
        "id": "04_calendario",
        "type": "screenshot",
        "source": SCREENSHOTS / "02-calendario.png",
        "crop": (0.12, 0.12, 0.95, 0.85),  # Calendario settimana — no sidebar
        "zoom_start": 1.0, "zoom_end": 1.25,
        "zoom_cx": 0.5, "zoom_cy": 0.4,
        "voiceover": "Calendario digitale. Un colore per ogni operatore, nessun conflitto. Sara conosce i tuoi clienti e i loro gusti, e prenota da sola.",
        "vo_delay": 0.3,
        "min_duration": 8,
        "subtitle": "Sara prenota — zero conflitti",
    },
    {
        "id": "05_pacchetti",
        "type": "screenshot",
        "source": SCREENSHOTS / "22-pacchetti.png",
        "crop": (0.05, 0.05, 0.95, 0.70),  # Pacchetti — focus bottoni
        "zoom_start": 1.0, "zoom_end": 1.2,
        "zoom_cx": 0.5, "zoom_cy": 0.3,
        "voiceover": "Crei i tuoi pacchetti promozionali. Natale, estate, festa del papà. Un click e il messaggio parte su WhatsApp a tutti i clienti.",
        "vo_delay": 0.3,
        "min_duration": 8,
        "subtitle": "Crei i tuoi pacchetti — WhatsApp automatico",
    },
    {
        "id": "06_analytics",
        "type": "screenshot",
        "source": SCREENSHOTS / "10-analytics.png",
        "crop": (0.0, 0.0, 0.60, 0.55),  # Focus stretto: tasso conferma + appuntamenti
        "zoom_start": 1.0, "zoom_end": 1.2,
        "zoom_cx": 0.4, "zoom_cy": 0.4,
        "voiceover": "I numeri parlano. Tasso di conferma WhatsApp: cento percento. Duecentotrentasei appuntamenti. Zero poltrone vuote.",
        "vo_delay": 0.3,
        "min_duration": 8,
        "subtitle": "Conferma WhatsApp: 100%",
    },
    {
        "id": "07_voice",
        "type": "screenshot",
        "source": SCREENSHOTS / "08-voice.png",
        "crop": (0.12, 0.08, 0.95, 0.65),  # Voice agent panel — no sidebar
        "zoom_start": 1.0, "zoom_end": 1.15,
        "zoom_cx": 0.5, "zoom_cy": 0.4,
        "voiceover": "Sara è l'assistente vocale. Risponde al telefono, prenota, conferma, manda i promemoria. E FLUXION fa anche le fatture, gli ordini ai fornitori, la cassa. Tutto in un programma solo.",
        "vo_delay": 0.3,
        "min_duration": 10,
        "subtitle": "Sara — fatture — fornitori — cassa",
    },
    {
        "id": "08_cta",
        "type": "cta",
        "voiceover": "FLUXION. Quattrocentonovantasette euro. Una volta. Per sempre. fluxion landing punto pages punto dev.",
        "vo_delay": 1.5,
        "min_duration": 22,
    },
]


# ─── Step 1: Generate all voiceovers FIRST ─────────────────────────────────

async def gen_vo(block):
    """Generate voiceover, return (path, duration)."""
    import edge_tts
    text = block.get("voiceover")
    if not text:
        return None, 0

    path = str(TMP / f"vo_{block['id']}.mp3")
    comm = edge_tts.Communicate(text=text, voice="it-IT-IsabellaNeural", rate="+0%")
    await comm.save(path)

    # Get duration
    import json
    probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "json", path],
        capture_output=True, text=True
    )
    dur = float(json.loads(probe.stdout)["format"]["duration"])
    return path, dur


async def gen_all_vo():
    results = {}
    for b in BLOCKS:
        path, dur = await gen_vo(b)
        if path:
            results[b["id"]] = {"path": path, "duration": dur}
            # Set block duration = max(min_duration, vo_delay + vo_duration + 1.0)
            needed = b.get("vo_delay", 0) + dur + 1.0
            b["duration"] = max(b.get("min_duration", 7), needed)
            print(f"  VO {b['id']}: {dur:.1f}s → block {b['duration']:.1f}s")
        else:
            b["duration"] = b.get("min_duration", 7)
    return results


# ─── Step 2: Crop + prepare screenshots for mobile ────────────────────────

def crop_screenshot_for_mobile(src: str, crop_box: tuple, out_path: str, subtitle: str = "", block_title: str = ""):
    """Crop screenshot to relevant area, add phone-friendly frame with title + subtitle."""
    img = Image.open(src)
    iw, ih = img.size

    # Crop
    l, t, r, b = crop_box
    cropped = img.crop((int(l * iw), int(t * ih), int(r * iw), int(b * ih)))
    cw, ch = cropped.size

    # Create 9:16 canvas with dark gradient background
    canvas = Image.new("RGB", (W, H), (8, 8, 15))
    draw = ImageDraw.Draw(canvas)

    # Subtle gradient overlay (darker at top and bottom)
    for y_pos in range(200):
        alpha = int(255 * (1 - y_pos / 200) * 0.3)
        draw.rectangle([(0, y_pos), (W, y_pos + 1)], fill=(0, 0, 0))
    for y_pos in range(H - 250, H):
        alpha = int(255 * ((y_pos - (H - 250)) / 250) * 0.4)
        draw.rectangle([(0, y_pos), (W, y_pos + 1)], fill=(0, 0, 0))

    # Scale screenshot to fill ~90% width with rounded corner effect
    padding = 30
    target_w = W - padding * 2
    scale = target_w / cw
    new_w = target_w
    new_h = int(ch * scale)

    # Cap height (leave room for title above and subtitle below)
    max_h = H - 500
    if new_h > max_h:
        scale2 = max_h / new_h
        new_w = int(new_w * scale2)
        new_h = max_h

    resized = cropped.resize((new_w, new_h), Image.LANCZOS)

    # Add rounded corners to screenshot
    from PIL import ImageDraw as ID2
    mask = Image.new("L", (new_w, new_h), 0)
    mask_draw = ID2.Draw(mask)
    radius = 16
    mask_draw.rounded_rectangle([(0, 0), (new_w - 1, new_h - 1)], radius=radius, fill=255)

    # Add subtle border glow
    border = Image.new("RGB", (new_w + 4, new_h + 4), (34, 211, 238))  # cyan glow
    border_mask = Image.new("L", (new_w + 4, new_h + 4), 0)
    bm_draw = ID2.Draw(border_mask)
    bm_draw.rounded_rectangle([(0, 0), (new_w + 3, new_h + 3)], radius=radius + 2, fill=40)

    # Position screenshot (above center)
    x = (W - new_w) // 2
    y = 280

    # Paste border glow
    canvas.paste(Image.blend(canvas.crop((x - 2, y - 2, x + new_w + 2, y + new_h + 2)), border, 0.15), (x - 2, y - 2))

    # Paste screenshot with rounded mask
    canvas.paste(resized, (x, y), mask)

    # Add shadow under screenshot
    shadow = Image.new("RGBA", (new_w, 30), (0, 0, 0, 60))
    canvas.paste(Image.new("RGB", (new_w, 30), (8, 8, 15)), (x, y + new_h))

    # Title text above screenshot (block_title or subtitle)
    if subtitle:
        f_title = font(32)
        bbox = draw.textbbox((0, 0), subtitle, font=f_title)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) // 2, 200), subtitle, font=f_title, fill=(34, 211, 238))  # cyan

    # Small FLUXION watermark top-left
    f_small = font(16)
    draw.text((40, 40), "FLUXION", font=f_small, fill=(100, 100, 120))

    # Decorative line under title
    if subtitle:
        line_w = min(tw + 40, W - 80)
        line_x = (W - line_w) // 2
        draw.rectangle([(line_x, 245), (line_x + line_w, 246)], fill=(34, 211, 238, 60))

    canvas.save(out_path, quality=95)
    return out_path


# ─── Step 3: Build video blocks ───────────────────────────────────────────

def build_screenshot_block(block, out_path):
    """Screenshot with SMOOTH Ken Burns — no jitter, text overlays baked in."""
    # Crop + add title/subtitle text into the image itself
    cropped_path = str(TMP / f"{block['id']}_cropped.png")
    crop_screenshot_for_mobile(
        str(block["source"]),
        block.get("crop", (0, 0, 1, 1)),
        cropped_path,
        subtitle=block.get("subtitle", ""),
    )

    dur = block["duration"]
    total_frames = int(dur * FPS)

    # SMOOTH zoom: scale image to 6x first (eliminates sub-pixel jitter)
    # then use very gentle zoom 1.0→1.08 (subtle, professional)
    zoom_expr = f"'1.0+0.08*on/{total_frames}'"
    # Center zoom (no pan = no jitter)
    x_expr = f"'(iw-iw/zoom)/2'"
    y_expr = f"'(ih-ih/zoom)/2'"

    base_path = str(TMP / f"{block['id']}_base.mp4")
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", cropped_path,
        "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo",
        "-filter_complex",
        f"[0:v]scale=6480:-1,zoompan=z={zoom_expr}:x={x_expr}:y={y_expr}:d={total_frames}:s={W}x{H}:fps={FPS}[v]",
        "-map", "[v]", "-map", "1:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "17",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(dur), "-pix_fmt", "yuv420p", "-shortest",
        out_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"  ✓ {block['id']}: {dur:.1f}s screenshot [{block.get('subtitle', '')}]")


def build_veo3_block(block, out_path):
    """Normalize Veo 3 clip."""
    src = str(block["source"])
    dur = block["duration"]
    cmd = [
        "ffmpeg", "-y", "-i", src,
        "-vf", f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-t", str(dur), "-r", str(FPS), "-pix_fmt", "yuv420p",
        out_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"  ✓ {block['id']}: {dur:.1f}s Veo 3")


def build_cta_block(block, out_path):
    """CTA frame with logo FLUXION."""
    dur = block["duration"]

    img = Image.new("RGB", (W, H), "black")
    draw = ImageDraw.Draw(img)

    def centered(text, y, f, fill="white"):
        bbox = draw.textbbox((0, 0), text, font=f)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) // 2, y), text, font=f, fill=fill)

    # Logo FLUXION
    if LOGO.exists():
        logo = Image.open(str(LOGO)).convert("RGBA")
        logo_size = 200
        logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
        # Center logo
        lx = (W - logo_size) // 2
        ly = 300
        # Paste with alpha
        img.paste(logo, (lx, ly), logo if logo.mode == "RGBA" else None)

    centered("FLUXION", 530, font(80), "white")
    centered("Il gestionale che non ti costa ogni mese", 640, font(24), "#AAAAAA")

    # Separator
    draw.rectangle([(W * 0.15, 700), (W * 0.85, 702)], fill="#333333")

    centered("€497", 750, font(96), "white")
    centered("una volta. per sempre.", 870, font(34), "white")

    # Separator
    draw.rectangle([(W * 0.15, 940), (W * 0.85, 942)], fill="#333333")

    centered("Treatwell: €120/mese + 25% commissioni", 980, font(22), "#FF5555")
    centered("= €4.320 in 3 anni + commissioni", 1015, font(20), "#FF7777")

    # Separator
    draw.rectangle([(W * 0.2, 1070), (W * 0.8, 1072)], fill="#333333")

    centered("fluxion-landing.pages.dev", 1120, font(36), "#7799FF")

    cta_img = str(TMP / "cta.png")
    img.save(cta_img)

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", cta_img,
        "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(dur), "-r", str(FPS), "-pix_fmt", "yuv420p", "-shortest",
        out_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"  ✓ {block['id']}: {dur:.1f}s CTA + logo")


# ─── Step 4: Merge VO + Concat ─────────────────────────────────────────────

def merge_vo(clip, vo_path, vo_delay, dur, out_path):
    cmd = [
        "ffmpeg", "-y", "-i", clip, "-i", vo_path,
        "-filter_complex",
        f"[1:a]adelay={int(vo_delay*1000)}|{int(vo_delay*1000)},volume=1.0[vo];"
        f"[0:a]volume=0.03[bg];"
        f"[bg][vo]amix=inputs=2:duration=first[a]",
        "-map", "0:v", "-map", "[a]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", str(dur),
        out_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def concat_all(clips, out_path):
    ts_paths = []
    for i, cp in enumerate(clips):
        ts = str(TMP / f"final_{i:02d}.ts")
        cmd = [
            "ffmpeg", "-y", "-i", cp,
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-r", str(FPS), "-s", f"{W}x{H}", "-pix_fmt", "yuv420p",
            "-bsf:v", "h264_mp4toannexb", "-f", "mpegts",
            ts,
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        ts_paths.append(ts)

    concat_str = "|".join(ts_paths)
    cmd = [
        "ffmpeg", "-y",
        "-i", f"concat:{concat_str}",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        out_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)


# ─── Main ──────────────────────────────────────────────────────────────────

async def main():
    print("=" * 50)
    print("FLUXION — Parrucchiere V3 (80s mobile-optimized)")
    print("=" * 50)

    # 1. Generate ALL voiceovers first → set block durations
    print("\n[1/4] Voiceovers (durate dinamiche)...")
    vo_data = await gen_all_vo()

    total = sum(b["duration"] for b in BLOCKS)
    print(f"\n  Durata totale: {total:.1f}s")

    # 2. Build video blocks
    print("\n[2/4] Building blocks...")
    raw_clips = {}
    for b in BLOCKS:
        clip_path = str(TMP / f"{b['id']}_raw.mp4")
        if b["type"] == "veo3":
            build_veo3_block(b, clip_path)
        elif b["type"] == "screenshot":
            build_screenshot_block(b, clip_path)
        elif b["type"] == "cta":
            build_cta_block(b, clip_path)
        raw_clips[b["id"]] = clip_path

    # 3. Merge VO into clips
    print("\n[3/4] Merging voiceover...")
    final_clips = []
    for b in BLOCKS:
        raw = raw_clips[b["id"]]
        vo = vo_data.get(b["id"])
        if vo:
            merged = str(TMP / f"{b['id']}_final.mp4")
            merge_vo(raw, vo["path"], b.get("vo_delay", 0), b["duration"], merged)
            final_clips.append(merged)
            print(f"  ✓ {b['id']} + VO ({vo['duration']:.1f}s)")
        else:
            final_clips.append(raw)

    # 4. Concat
    print("\n[4/5] Concat...")
    concat_no_music = str(TMP / "concat_no_music.mp4")
    concat_all(final_clips, concat_no_music)

    # 5. Add background music
    print("\n[5/5] Adding background music...")
    MUSIC = Path("../landing/assets/background-music.mp3")
    final = str(OUT_DIR / "parrucchiere_80s_v3.mp4")

    if MUSIC.exists():
        cmd = [
            "ffmpeg", "-y",
            "-i", concat_no_music,
            "-i", str(MUSIC),
            "-filter_complex",
            # Music: low volume (8%), fade in 2s, fade out last 5s
            "[1:a]volume=0.08,afade=t=in:st=0:d=2,afade=t=out:st=95:d=8[music];"
            # Mix voiceover (already in video) + music
            "[0:a][music]amix=inputs=2:duration=first:dropout_transition=3[aout]",
            "-map", "0:v", "-map", "[aout]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart",
            final,
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"  Music added: {MUSIC.name}")
    else:
        subprocess.run(["cp", concat_no_music, final])
        print("  No music file found, skipping")

    # Verify
    import json
    probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration,size",
         "-show_entries", "stream=width,height", "-of", "json", final],
        capture_output=True, text=True
    )
    info = json.loads(probe.stdout)
    dur = float(info["format"]["duration"])
    size_mb = int(info["format"]["size"]) / (1024 * 1024)

    print(f"\n{'=' * 50}")
    print(f"DONE: {final}")
    print(f"Durata: {dur:.1f}s | Size: {size_mb:.1f}MB | 1080x1920 9:16")
    print(f"{'=' * 50}")

    # Open
    subprocess.run(["open", final])


if __name__ == "__main__":
    asyncio.run(main())
