"""
build_parrucchiere_v2.py — FLUXION Video Parrucchiere 80s
Storyboard definitivo: Veo3 hook + 6 screenshot Ken Burns + CTA
"""

import asyncio
import subprocess
import tempfile
from pathlib import Path

# ─── Config ────────────────────────────────────────────────────────────────
SCREENSHOTS = Path("../landing/screenshots")
CLIPS_DIR = Path("output/parrucchiere/clips")
OUT_DIR = Path("output/parrucchiere")
OUT_DIR.mkdir(parents=True, exist_ok=True)

W, H = 1080, 1920  # 9:16
FPS = 30

# ─── Blocks definition ────────────────────────────────────────────────────
BLOCKS = [
    {
        "id": "01_hook",
        "type": "veo3",
        "source": CLIPS_DIR / "parrucchiere_clip1_v1.mp4",
        "duration": 10,
        "voiceover": "Ogni cliente ha la sua formula. Ma e' scritta a penna, su un quaderno. Con la tua stessa calligrafia di sei mesi fa.",
        "vo_start": 2.0,
        "text_overlays": [],
    },
    {
        "id": "02_dashboard",
        "type": "screenshot",
        "source": SCREENSHOTS / "01-dashboard.png",
        "duration": 7,
        "zoom_start": 1.2, "zoom_end": 1.5,
        "zoom_cx": 0.6, "zoom_cy": 0.25,  # Focus fatturato card top-right
        "voiceover": "Ogni mattina apri FLUXION. Trentaquattro appuntamenti oggi. Cinquemila seicentotrenta di fatturato questo mese. Tutto li', al primo sguardo.",
        "vo_start": 0.0,
        "text_overlays": [
            {"t": 1.0, "text": "Tutto sotto controllo — ogni mattina"},
        ],
    },
    {
        "id": "03_scheda",
        "type": "screenshot",
        "source": SCREENSHOTS / "12-scheda-parrucchiere.png",
        "duration": 9,
        "zoom_start": 1.0, "zoom_end": 2.2,
        "zoom_cx": 0.5, "zoom_cy": 0.45,  # Focus scheda parrucchiere campi
        "voiceover": "Con FLUXION, la formula colore e' sempre li'. Tipo capello, porosita', lunghezza. Base naturale tono uno-dieci. Colore attuale. Ogni cliente. Sempre aggiornata.",
        "vo_start": 0.0,
        "text_overlays": [
            {"t": 0.5, "text": "Scheda cliente — Filippo Alberti"},
            {"t": 3.0, "text": "Formula colore — Tipo capello — Porosita'"},
            {"t": 6.0, "text": "Base naturale tono 1-10 — Trattamenti chimici"},
        ],
    },
    {
        "id": "04_calendario",
        "type": "screenshot",
        "source": SCREENSHOTS / "02-calendario.png",
        "duration": 8,
        "zoom_start": 1.1, "zoom_end": 1.6,
        "zoom_cx": 0.5, "zoom_cy": 0.4,
        "voiceover": "L'agenda digitale. Un colore per operatore. Ogni slot, ogni nome, ogni orario. Nessun doppio appuntamento. Mai.",
        "vo_start": 0.0,
        "text_overlays": [
            {"t": 1.0, "text": "Calendario digitale — Marzo 2026"},
            {"t": 4.0, "text": "Appuntamenti per operatore — colori distinti"},
        ],
    },
    {
        "id": "05_pacchetti",
        "type": "screenshot",
        "source": SCREENSHOTS / "22-pacchetti.png",
        "duration": 8,
        "zoom_start": 1.0, "zoom_end": 1.5,
        "zoom_cx": 0.5, "zoom_cy": 0.3,
        "voiceover": "Pacchetti stagionali gia' pronti. Festa del Papa' meno ventinove percento. Un click, il WhatsApp parte da solo ai tuoi clienti. Sara gestisce le prenotazioni.",
        "vo_start": 0.0,
        "text_overlays": [
            {"t": 0.5, "text": "Pacchetti promozionali"},
            {"t": 3.0, "text": "Festa del Papa' — Natale Glamour — Estate"},
            {"t": 5.5, "text": "1 click → WhatsApp inviato ai clienti"},
        ],
    },
    {
        "id": "06_analytics",
        "type": "screenshot",
        "source": SCREENSHOTS / "10-analytics.png",
        "duration": 8,
        "zoom_start": 1.2, "zoom_end": 1.8,
        "zoom_cx": 0.35, "zoom_cy": 0.3,  # Focus tasso conferma WA
        "voiceover": "Tasso di conferma WhatsApp: cento percento. Duecentotrentasei appuntamenti confermati. Zero no-show. Zero poltrone vuote.",
        "vo_start": 0.0,
        "text_overlays": [
            {"t": 1.0, "text": "Tasso conferma WhatsApp: 100%"},
            {"t": 4.0, "text": "236 appuntamenti — 0 no-show"},
        ],
    },
    {
        "id": "07_voice",
        "type": "screenshot",
        "source": SCREENSHOTS / "08-voice.png",
        "duration": 8,
        "zoom_start": 1.0, "zoom_end": 1.5,
        "zoom_cx": 0.5, "zoom_cy": 0.35,
        "voiceover": "Sara e' l'assistente vocale inclusa in FLUXION. Risponde al telefono mentre tu hai le mani nella chioma. Prenota, conferma, manda il promemoria. Nessun competitor ha questo.",
        "vo_start": 0.0,
        "text_overlays": [
            {"t": 0.5, "text": "Sara — Assistente vocale AI"},
            {"t": 3.0, "text": "Risponde al telefono — Prenota — Conferma"},
            {"t": 6.0, "text": "Inclusa nel prezzo — Nessun extra"},
        ],
    },
    {
        "id": "08_cta",
        "type": "cta",
        "duration": 22,
        "voiceover": "FLUXION. Quattrocentonovantasette euro. Una volta. Per sempre. fluxion punto app.",
        "vo_start": 1.0,
    },
]


# ─── Pillow helpers ────────────────────────────────────────────────────────

def make_text_bar(text: str, width: int = W, height: int = 80) -> str:
    """Create a PNG text bar with black semi-transparent background."""
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("RGBA", (width, height), (0, 0, 0, 160))
    draw = ImageDraw.Draw(img)

    font_path = "/System/Library/Fonts/Helvetica.ttc"
    try:
        font = ImageFont.truetype(font_path, 28)
    except Exception:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (width - tw) // 2
    y = (height - th) // 2
    draw.text((x, y), text, font=font, fill="white")

    path = tempfile.mktemp(suffix=".png")
    img.save(path)
    return path


def make_cta_frame_image() -> str:
    """Create CTA frame as PNG."""
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("RGB", (W, H), "black")
    draw = ImageDraw.Draw(img)

    font_path = "/System/Library/Fonts/Helvetica.ttc"

    def font(size):
        try:
            return ImageFont.truetype(font_path, size)
        except Exception:
            return ImageFont.load_default()

    def centered(text, y, f, fill="white"):
        bbox = draw.textbbox((0, 0), text, font=f)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) // 2, y), text, font=f, fill=fill)

    centered("FLUXION", 450, font(88), "white")
    centered("Il gestionale che non ti costa ogni mese", 570, font(26), "#AAAAAA")

    # Separator
    draw.rectangle([(W * 0.1, 630), (W * 0.9, 632)], fill="#333333")

    centered("€497", 680, font(96), "white")
    centered("una volta. per sempre.", 800, font(34), "white")

    # Separator 2
    draw.rectangle([(W * 0.1, 870), (W * 0.9, 872)], fill="#333333")

    centered("Treatwell: €120/mese + 25% commissioni", 910, font(22), "#FF5555")
    centered("= €4.320 in 3 anni, senza commissioni", 950, font(20), "#FF7777")

    centered("fluxion-landing.pages.dev", 1050, font(44), "#7799FF")

    path = tempfile.mktemp(suffix=".png")
    img.save(path)
    return path


# ─── FFmpeg builders ───────────────────────────────────────────────────────

def build_screenshot_clip(block: dict, out_path: str) -> None:
    """Build Ken Burns animated clip from screenshot with zoompan."""
    src = str(block["source"])
    dur = block["duration"]
    zs = block["zoom_start"]
    ze = block["zoom_end"]
    cx = block["zoom_cx"]
    cy = block["zoom_cy"]

    # zoompan: zoom from zs to ze, centered on cx,cy
    # z='zs+(ze-zs)*on/total_frames'
    total_frames = dur * FPS
    zoom_expr = f"'{zs}+({ze}-{zs})*on/{total_frames}'"
    # x and y keep center point stable during zoom
    x_expr = f"'(iw-iw/zoom)*{cx}'"
    y_expr = f"'(ih-ih/zoom)*{cy}'"

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", src,
        "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo",
        "-filter_complex",
        f"[0:v]scale=4320:-1,zoompan=z={zoom_expr}:x={x_expr}:y={y_expr}:d={total_frames}:s={W}x{H}:fps={FPS}[v]",
        "-map", "[v]", "-map", "1:a",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(dur), "-pix_fmt", "yuv420p",
        "-shortest",
        out_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"  ✓ {block['id']}: {dur}s Ken Burns")


def build_veo3_clip(block: dict, out_path: str) -> None:
    """Normalize Veo 3 clip to target resolution."""
    src = str(block["source"])
    dur = block["duration"]

    cmd = [
        "ffmpeg", "-y", "-i", src,
        "-vf", f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2",
        "-c:v", "libx264", "-preset", "fast", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-t", str(dur), "-r", str(FPS), "-pix_fmt", "yuv420p",
        out_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"  ✓ {block['id']}: {dur}s Veo 3 clip")


def build_cta_clip(block: dict, out_path: str) -> None:
    """Build CTA frame as video."""
    cta_img = make_cta_frame_image()
    dur = block["duration"]

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", cta_img,
        "-f", "lavfi", "-i", f"anullsrc=r=48000:cl=stereo",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(dur), "-r", str(FPS), "-pix_fmt", "yuv420p",
        "-shortest",
        out_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    Path(cta_img).unlink(missing_ok=True)
    print(f"  ✓ {block['id']}: {dur}s CTA frame")


# ─── Voiceover ─────────────────────────────────────────────────────────────

async def generate_block_voiceover(block: dict, out_path: str) -> None:
    """Generate Edge-TTS voiceover for a single block."""
    import edge_tts

    text = block.get("voiceover")
    if not text:
        return

    comm = edge_tts.Communicate(
        text=text,
        voice="it-IT-IsabellaNeural",
        rate="+0%",
    )
    await comm.save(out_path)


async def generate_all_voiceovers(blocks: list, tmp_dir: Path) -> dict:
    """Generate all voiceovers, return {block_id: path}."""
    results = {}
    for block in blocks:
        if not block.get("voiceover"):
            continue
        path = str(tmp_dir / f"vo_{block['id']}.mp3")
        await generate_block_voiceover(block, path)
        results[block["id"]] = path
        print(f"  ✓ VO {block['id']}")
    return results


# ─── Final assembly ────────────────────────────────────────────────────────

def merge_vo_into_clip(clip_path: str, vo_path: str, vo_start: float, out_path: str, dur: float) -> None:
    """Merge voiceover into clip at specified start time."""
    cmd = [
        "ffmpeg", "-y",
        "-i", clip_path,
        "-i", vo_path,
        "-filter_complex",
        f"[1:a]adelay={int(vo_start*1000)}|{int(vo_start*1000)},volume=1.0[vo];"
        f"[0:a]volume=0.05[bg];"
        f"[bg][vo]amix=inputs=2:duration=first[aout]",
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-t", str(dur),
        out_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def concat_final(clip_paths: list, out_path: str) -> None:
    """Concat all blocks into final video using concat demuxer with TS intermediates."""
    tmp_dir = Path(tempfile.mkdtemp())

    # Re-encode to .ts for clean concat
    ts_paths = []
    for i, cp in enumerate(clip_paths):
        ts = str(tmp_dir / f"seg_{i:02d}.ts")
        cmd = [
            "ffmpeg", "-y", "-i", cp,
            "-c:v", "libx264", "-preset", "fast", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-r", str(FPS), "-s", f"{W}x{H}", "-pix_fmt", "yuv420p",
            "-bsf:v", "h264_mp4toannexb",
            "-f", "mpegts",
            ts,
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        ts_paths.append(ts)

    # Concat
    concat_str = "|".join(ts_paths)
    cmd = [
        "ffmpeg", "-y",
        "-i", f"concat:{concat_str}",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        out_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)


# ─── Main ──────────────────────────────────────────────────────────────────

async def main():
    tmp = Path(tempfile.mkdtemp())
    print("=" * 50)
    print("FLUXION — Parrucchiere Video 80s")
    print("=" * 50)

    # 1. Build video clips
    print("\n[1/4] Building video blocks...")
    block_clips = {}
    for block in BLOCKS:
        clip_path = str(tmp / f"{block['id']}_raw.mp4")
        if block["type"] == "veo3":
            build_veo3_clip(block, clip_path)
        elif block["type"] == "screenshot":
            build_screenshot_clip(block, clip_path)
        elif block["type"] == "cta":
            build_cta_clip(block, clip_path)
        block_clips[block["id"]] = clip_path

    # 2. Generate voiceovers
    print("\n[2/4] Generating voiceovers...")
    vo_paths = await generate_all_voiceovers(BLOCKS, tmp)

    # 3. Merge voiceovers into clips
    print("\n[3/4] Merging voiceover into clips...")
    final_clips = []
    for block in BLOCKS:
        raw_clip = block_clips[block["id"]]
        vo = vo_paths.get(block["id"])

        if vo:
            merged = str(tmp / f"{block['id']}_merged.mp4")
            merge_vo_into_clip(raw_clip, vo, block.get("vo_start", 0), merged, block["duration"])
            final_clips.append(merged)
            print(f"  ✓ {block['id']} + VO")
        else:
            final_clips.append(raw_clip)
            print(f"  ✓ {block['id']} (no VO)")

    # 4. Concat all
    print("\n[4/4] Concatenating final video...")
    final_path = str(OUT_DIR / "parrucchiere_80s_final.mp4")
    concat_final(final_clips, final_path)

    # Verify
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration,size",
         "-show_entries", "stream=width,height", "-of", "compact", final_path],
        capture_output=True, text=True
    )
    print(f"\n{'=' * 50}")
    print(f"DONE: {final_path}")
    print(result.stdout)
    print(f"{'=' * 50}")


if __name__ == "__main__":
    asyncio.run(main())
