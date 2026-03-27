#!/usr/bin/env python3
"""
FLUXION V6 — Generate YouTube thumbnail 1280x720.
Strategy: Extract best frame from V6-05_imprenditrice_pc.mp4 (person in work context),
then add FLUXION branding overlay via Pillow.

VID-05 requirement: Person in work context (NOT app UI screenshot).
"""

import subprocess
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "Pillow", "-q"], check=True)
    from PIL import Image, ImageDraw, ImageFont

# Paths
FLUXION_ROOT = Path("/Volumes/MontereyT7/FLUXION")
CLIPS_DIR = FLUXION_ROOT / "landing/assets/ai-clips-v2"
OUTPUT_PATH = FLUXION_ROOT / "landing/assets/fluxion-thumbnail-v6.jpg"
TEMP_FRAME = FLUXION_ROOT / "landing/assets/thumbnail-frame-temp.jpg"

# Source clip: female entrepreneur at laptop — best "after" scene for thumbnail
SOURCE_CLIP = CLIPS_DIR / "V6-05_imprenditrice_pc.mp4"
FALLBACK_CLIP = CLIPS_DIR / "V6-03_proprietario_soddisfatto.mp4"

TARGET_W, TARGET_H = 1280, 720


def extract_frame(clip_path: Path, output_path: Path, timestamp: float = 4.0) -> bool:
    """Extract a single frame at the given timestamp using ffmpeg."""
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(timestamp),
        "-i", str(clip_path),
        "-frames:v", "1",
        "-q:v", "1",   # highest quality
        "-vf", f"scale={TARGET_W}:{TARGET_H}:force_original_aspect_ratio=increase,crop={TARGET_W}:{TARGET_H}",
        str(output_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ffmpeg error: {result.stderr[-200:]}")
        return False
    return output_path.exists() and output_path.stat().st_size > 10_000


def add_branding_overlay(frame_path: Path, output_path: Path):
    """Add FLUXION logo + bold branding with gradient overlay using Pillow."""
    img = Image.open(frame_path).convert("RGB")
    img = img.resize((TARGET_W, TARGET_H), Image.LANCZOS)

    # Create overlay layer for gradient
    overlay = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)

    # Dark gradient on left side for text readability — wider + stronger
    gradient_width = 750
    for x in range(gradient_width):
        t = 1.0 - (x / gradient_width)
        alpha = int(t * t * 200)  # stronger opacity for readability
        draw_overlay.line([(x, 0), (x, TARGET_H)], fill=(0, 0, 0, alpha))

    # Bottom strip for price/tagline
    for y in range(TARGET_H - 120, TARGET_H):
        t = (y - (TARGET_H - 120)) / 120.0
        alpha = int(t * 180)
        draw_overlay.line([(0, y), (TARGET_W, y)], fill=(0, 0, 0, alpha))

    # Merge
    img_rgba = img.convert("RGBA")
    composited = Image.alpha_composite(img_rgba, overlay)

    # --- FLUXION Logo (top-left) — use the real 3D ribbon logo ---
    logo_path = FLUXION_ROOT / "landing" / "assets" / "logo_fluxion.jpg"
    if logo_path.exists():
        logo = Image.open(logo_path).convert("RGBA")
        # Crop center square (remove grey background padding)
        w, h = logo.size
        crop_size = min(w, h) * 0.7  # crop inner 70% to remove grey border
        left = (w - crop_size) / 2
        top = (h - crop_size) / 2
        logo = logo.crop((int(left), int(top), int(left + crop_size), int(top + crop_size)))
        logo_size = 110
        logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
        # Add rounded corners
        mask = Image.new("L", (logo_size, logo_size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([(0, 0), (logo_size - 1, logo_size - 1)], radius=18, fill=255)
        composited.paste(logo, (35, 28), mask)
        print(f"  Logo FLUXION added ({logo_size}x{logo_size}, cropped from {w}x{h})")

    img = composited.convert("RGB")
    draw = ImageDraw.Draw(img)

    # Fonts — Impact for title (YouTube standard), Arial Bold for subtitle
    IMPACT = "/System/Library/Fonts/Supplemental/Impact.ttf"
    ARIAL_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
    HELVETICA = "/System/Library/Fonts/Helvetica.ttc"

    try:
        title_font = ImageFont.truetype(IMPACT, 140)
    except Exception:
        title_font = ImageFont.truetype(HELVETICA, 140)

    try:
        subtitle_font = ImageFont.truetype(IMPACT, 52)
    except Exception:
        subtitle_font = ImageFont.truetype(HELVETICA, 52)

    try:
        tagline_font = ImageFont.truetype(ARIAL_BOLD, 36)
    except Exception:
        tagline_font = ImageFont.truetype(HELVETICA, 36)

    try:
        price_font = ImageFont.truetype(IMPACT, 42)
    except Exception:
        price_font = ImageFont.truetype(HELVETICA, 42)

    WHITE = (255, 255, 255)
    ACCENT = (255, 200, 40)   # warm gold
    BLACK = (0, 0, 0)

    shadow = 4
    pad_x = 50
    logo_text_x = pad_x + 125  # right of logo

    # --- FLUXION title next to logo ---
    title_y = 35
    title_text = "FLUXION"
    for dx, dy in [(-shadow, -shadow), (shadow, shadow), (-shadow, shadow), (shadow, -shadow), (0, shadow), (shadow, 0)]:
        draw.text((logo_text_x + dx, title_y + dy), title_text, font=title_font, fill=BLACK)
    draw.text((logo_text_x, title_y), title_text, font=title_font, fill=WHITE)

    # --- Subtitle ---
    sub_y = title_y + 155
    subtitle_text = "Paghi Una Volta."
    for dx, dy in [(shadow, shadow), (-shadow, shadow)]:
        draw.text((pad_x + dx, sub_y + dy), subtitle_text, font=subtitle_font, fill=BLACK)
    draw.text((pad_x, sub_y), subtitle_text, font=subtitle_font, fill=ACCENT)

    sub2_y = sub_y + 55
    subtitle_text2 = "Usi Per Sempre."
    for dx, dy in [(shadow, shadow), (-shadow, shadow)]:
        draw.text((pad_x + dx, sub2_y + dy), subtitle_text2, font=subtitle_font, fill=BLACK)
    draw.text((pad_x, sub2_y), subtitle_text2, font=subtitle_font, fill=WHITE)

    # --- Gold accent line ---
    line_y = sub2_y + 65
    draw.rectangle([(pad_x, line_y), (pad_x + 350, line_y + 5)], fill=ACCENT)

    # --- Tagline ---
    tag_y = line_y + 18
    tagline_text = "Il gestionale per PMI italiane"
    for dx, dy in [(2, 2)]:
        draw.text((pad_x + dx, tag_y + dy), tagline_text, font=tagline_font, fill=BLACK)
    draw.text((pad_x, tag_y), tagline_text, font=tagline_font, fill=(230, 230, 230))

    # --- Bottom strip: price ---
    price_text = "Base €497  |  Pro €897  —  Licenza Lifetime"
    bbox = draw.textbbox((0, 0), price_text, font=price_font)
    price_w = bbox[2] - bbox[0]
    price_x = (TARGET_W - price_w) // 2
    price_y = TARGET_H - 55
    for dx, dy in [(2, 2), (-2, 2)]:
        draw.text((price_x + dx, price_y + dy), price_text, font=price_font, fill=BLACK)
    draw.text((price_x, price_y), price_text, font=price_font, fill=WHITE)

    # Save
    img.save(str(output_path), "JPEG", quality=95, optimize=True)
    size_kb = output_path.stat().st_size / 1024
    print(f"  SAVED: {output_path.name} ({size_kb:.0f} KB)")
    return True


def main():
    print("=" * 60)
    print("  FLUXION V6 — YouTube Thumbnail Generator")
    print(f"  Target: {TARGET_W}x{TARGET_H} JPEG")
    print(f"  Output: {OUTPUT_PATH}")
    print("=" * 60)

    # Choose source clip
    source = None
    for clip in [SOURCE_CLIP, FALLBACK_CLIP]:
        if clip.exists() and clip.stat().st_size > 500_000:
            source = clip
            print(f"\n  Source clip: {clip.name}")
            break

    if source is None:
        print("  ERROR: No source clip found. Run generate-v6-clips.py first.")
        sys.exit(1)

    # Try multiple timestamps to get the best frame
    print(f"\n[1/3] Extracting frame from {source.name}...")
    extracted = False
    for ts in [4.0, 3.0, 5.0, 2.0]:
        print(f"  Trying timestamp {ts}s...")
        if extract_frame(source, TEMP_FRAME, timestamp=ts):
            extracted = True
            print(f"  Frame extracted at {ts}s")
            break

    if not extracted:
        print("  ERROR: Could not extract frame from clip.")
        sys.exit(1)

    print(f"\n[2/3] Adding FLUXION branding overlay...")
    add_branding_overlay(TEMP_FRAME, OUTPUT_PATH)

    print(f"\n[3/3] Verifying output...")
    if OUTPUT_PATH.exists():
        img = Image.open(OUTPUT_PATH)
        w, h = img.size
        size_kb = OUTPUT_PATH.stat().st_size / 1024
        print(f"  Dimensions: {w}x{h}")
        print(f"  File size: {size_kb:.0f} KB")
        if w == TARGET_W and h == TARGET_H:
            print(f"  Dimensions OK: {TARGET_W}x{TARGET_H}")
        else:
            print(f"  WARNING: Expected {TARGET_W}x{TARGET_H}, got {w}x{h}")
        if 50 < size_kb < 2000:
            print(f"  Size OK: {size_kb:.0f}KB")
        else:
            print(f"  WARNING: Size outside expected range (50-2000KB)")
    else:
        print("  ERROR: Output file not created.")
        sys.exit(1)

    # Cleanup temp file
    if TEMP_FRAME.exists():
        TEMP_FRAME.unlink()

    print(f"\n  DONE: Open to verify — open {OUTPUT_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    main()
