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
    """Add FLUXION branding with semi-transparent gradient overlay using Pillow."""
    img = Image.open(frame_path).convert("RGB")
    img = img.resize((TARGET_W, TARGET_H), Image.LANCZOS)

    # Create overlay layer for gradient
    overlay = Image.new("RGBA", (TARGET_W, TARGET_H), (0, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)

    # Dark gradient on left side for text readability
    gradient_width = 640  # left half
    for x in range(gradient_width):
        # Ease-out opacity: strong left, fades to transparent right
        t = 1.0 - (x / gradient_width)
        alpha = int(t * t * 165)  # max ~165/255 (~65% opacity at left edge)
        draw_overlay.line([(x, 0), (x, TARGET_H)], fill=(0, 0, 0, alpha))

    # Merge base image with overlay
    img_rgba = img.convert("RGBA")
    composited = Image.alpha_composite(img_rgba, overlay)
    img = composited.convert("RGB")

    # Draw text
    draw = ImageDraw.Draw(img)

    # --- FLUXION title ---
    # Try to use system fonts, fallback to default
    title_font = None
    subtitle_font = None
    tagline_font = None

    font_candidates_bold = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNSDisplay-Bold.otf",
        "/System/Library/Fonts/SFCompactDisplay-Bold.otf",
        "/Library/Fonts/Arial Bold.ttf",
        "/System/Library/Fonts/ArialBold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    ]
    font_candidates_regular = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNSText-Regular.otf",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Arial.ttf",
    ]

    for path in font_candidates_bold:
        if Path(path).exists():
            try:
                title_font = ImageFont.truetype(path, 88)
                subtitle_font = ImageFont.truetype(path, 38)
                break
            except Exception:
                continue

    for path in font_candidates_regular:
        if Path(path).exists():
            try:
                tagline_font = ImageFont.truetype(path, 30)
                break
            except Exception:
                continue

    if title_font is None:
        title_font = ImageFont.load_default()
    if subtitle_font is None:
        subtitle_font = title_font
    if tagline_font is None:
        tagline_font = subtitle_font

    SHADOW_COLOR = (0, 0, 0, 200)
    WHITE = (255, 255, 255)
    ACCENT = (255, 220, 60)   # warm gold accent

    pad_x = 54
    pad_y = 60
    shadow_offset = 3

    # --- FLUXION main title ---
    title_text = "FLUXION"
    # Shadow
    draw.text((pad_x + shadow_offset, pad_y + shadow_offset), title_text,
              font=title_font, fill=(0, 0, 0))
    # White text
    draw.text((pad_x, pad_y), title_text, font=title_font, fill=WHITE)

    # --- Subtitle ---
    subtitle_text = "Paghi Una Volta. Usi Per Sempre."
    sub_y = pad_y + 96
    draw.text((pad_x + shadow_offset, sub_y + shadow_offset), subtitle_text,
              font=subtitle_font, fill=(0, 0, 0))
    draw.text((pad_x, sub_y), subtitle_text, font=subtitle_font, fill=WHITE)

    # --- Accent line ---
    line_y = sub_y + 54
    draw.rectangle([(pad_x, line_y), (pad_x + 220, line_y + 4)], fill=ACCENT)

    # --- Tagline ---
    tagline_text = "Gestionale per PMI italiane"
    tag_y = line_y + 18
    draw.text((pad_x, tag_y), tagline_text, font=tagline_font, fill=(220, 220, 220))

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
