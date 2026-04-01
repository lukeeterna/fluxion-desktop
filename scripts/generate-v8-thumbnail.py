#!/usr/bin/env python3
"""
Generate YouTube thumbnail for FLUXION V8 promo.
1280x720, high contrast, readable at mobile size.
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

BASE = Path("/Volumes/MontereyT7/FLUXION")
OUTPUT = BASE / "landing" / "assets" / "youtube-thumbnail-v8.png"
SCREENSHOT = BASE / "landing" / "screenshots" / "01-dashboard.png"
LOGO = BASE / "logo_fluxion.jpg"

W, H = 1280, 720

FONT_PATHS = [
    "/System/Library/Fonts/Supplemental/Impact.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/Library/Fonts/Arial Bold.ttf",
]

def get_font(size):
    for fp in FONT_PATHS:
        if Path(fp).exists():
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
    return ImageFont.load_default()


def main():
    # Start with dashboard screenshot as background
    if SCREENSHOT.exists():
        bg = Image.open(str(SCREENSHOT)).convert("RGB")
        bg = bg.resize((W, H), Image.LANCZOS)
    else:
        bg = Image.new("RGB", (W, H), (20, 20, 40))

    draw = ImageDraw.Draw(bg)

    # Dark gradient overlay (left side for text)
    for x in range(W * 2 // 3):
        alpha = int(220 * (1 - x / (W * 2 / 3)))
        for y in range(H):
            r, g, b = bg.getpixel((x, y))
            r = int(r * (1 - alpha / 255))
            g = int(g * (1 - alpha / 255))
            b = int(b * (1 - alpha / 255))
            bg.putpixel((x, y), (r, g, b))

    # Main headline
    font_title = get_font(72)
    font_sub = get_font(42)
    font_price = get_font(56)

    # "GESTIONALE" line
    draw.text((60, 120), "GESTIONALE", font=font_title, fill=(255, 255, 255))

    # "PER LA TUA" line
    draw.text((60, 200), "PER LA TUA", font=font_title, fill=(255, 255, 255))

    # "ATTIVITA'" line in accent color
    draw.text((60, 280), "ATTIVITA'", font=font_title, fill=(78, 205, 196))

    # Price badge
    draw.rectangle([(50, 400), (420, 470)], fill=(78, 205, 196))
    draw.text((70, 408), "€497 PER SEMPRE", font=font_price, fill=(255, 255, 255))

    # Subline
    draw.text((60, 500), "Zero abbonamenti.", font=font_sub, fill=(200, 200, 200))
    draw.text((60, 550), "Sara risponde 24/7.", font=font_sub, fill=(200, 200, 200))

    # FLUXION logo top-left
    if LOGO.exists():
        logo = Image.open(str(LOGO)).convert("RGBA")
        logo = logo.resize((80, 80), Image.LANCZOS)
        alpha = logo.split()[3].point(lambda p: int(p * 0.9))
        logo.putalpha(alpha)
        bg_rgba = bg.convert("RGBA")
        bg_rgba.paste(logo, (60, 20), logo)
        bg = bg_rgba.convert("RGB")

    # Red accent bar at bottom
    draw = ImageDraw.Draw(bg)
    draw.rectangle([(0, H - 8), (W, H)], fill=(255, 75, 75))

    bg.save(str(OUTPUT), quality=95)
    print(f"Thumbnail saved: {OUTPUT}")
    print(f"Size: {OUTPUT.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
