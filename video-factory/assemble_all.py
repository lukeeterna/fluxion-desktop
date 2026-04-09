#!/usr/bin/env python3
"""
assemble_all.py — Assembla video di vendita FLUXION per 9 verticali
FFmpeg + Pillow. Zero costi.

Design frame screenshot:
  - Sfondo gradiente radiale navy→nero
  - Logo FLUXION scontornato + testo badge in alto a sinistra
  - Screenshot a proporzioni naturali, angoli arrotondati, drop shadow
  - Testo vendita sotto lo screenshot

Struttura video (~44s):
  [0-8s]     Veo3 clip1 (hook problema) + musica tense
  [8-~18s]   Screenshot 1+2 + seg_1 voiceover (problema)
  [~18-~28s] Screenshot 3+4+5 + seg_2 voiceover (soluzione)
  [~28-34s]  Veo3 clip3 (soluzione) + musica uplifting
  [34-~42s]  CTA frame + seg_3 voiceover (prezzo)

Usage:
  python3 assemble_all.py           # tutti
  python3 assemble_all.py barbiere  # singolo
"""

import math
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ── Paths ────────────────────────────────────────────────────────────────────
BASE = Path(__file__).parent
OUTPUT = BASE / "output"
SCREENSHOTS = Path("/Volumes/MontereyT7/FLUXION/landing/screenshots")
MUSIC_BG = BASE / "assets" / "music" / "wholesome_corporate.mp3"  # Kevin MacLeod CC BY 4.0
LOGO_CUTOUT = BASE / "assets" / "logo_cutout.png"

W, H = 1080, 1920  # 9:16
FPS = 30

# ── Vertical configs ─────────────────────────────────────────────────────────
VERTICALS = {
    "landing": {
        "label": "Landing (Generalista Multi-Settore)",
        "competitor_line": "I gestionali in abbonamento? €120/mese. €1.440/anno. Per sempre.",
        "clips_from": "parrucchiere",
        "multi_sector": True,
        "screenshots": [
            ("01-dashboard.png", "Tutta la tua attivita'. Un colpo d'occhio."),
            ("02-calendario.png", "Sara risponde al telefono. Tu lavori."),
            ("03-clienti.png", "I tuoi clienti. Tutti i dettagli. Sempre."),
            ("22-pacchetti.png", "Promozioni in 2 click. Messaggi automatici."),
            ("10-analytics.png", "Sai sempre come va. Nessuna sorpresa."),
        ],
    },
    "parrucchiere": {
        "label": "Salone di Parrucchiere",
        "competitor_line": "I gestionali in abbonamento? €120/mese. €1.440/anno. Per sempre.",
        "screenshots": [
            ("01-dashboard.png", "Tutto il tuo business. Un colpo d'occhio."),
            ("12-scheda-parrucchiere.png", "Ogni cliente ha la sua storia. Tu la conosci tutta."),
            ("02-calendario.png", "Sara risponde al telefono. Tu lavori."),
            ("22-pacchetti.png", "Promozioni in 2 click. Messaggi automatici."),
            ("10-analytics.png", "Sai sempre come va. Nessuna sorpresa."),
        ],
    },
    "barbiere": {
        "label": "Barbiere",
        "competitor_line": "I gestionali in abbonamento? €120/mese. €1.440/anno. Per sempre.",
        "screenshots": [
            ("01-dashboard.png", "Tutto il tuo business. Un colpo d'occhio."),
            ("12-scheda-parrucchiere.png", "Ogni cliente ha la sua storia. Tu la conosci tutta."),
            ("02-calendario.png", "Sara prenota mentre hai il rasoio in mano."),
            ("22-pacchetti.png", "Promozioni in 2 click. Messaggi automatici."),
            ("10-analytics.png", "Sai sempre come va. Nessuna sorpresa."),
        ],
    },
    "officina": {
        "label": "Officina Meccanica",
        "competitor_line": "I gestionali in abbonamento? €120/mese. €1.440/anno. Per sempre.",
        "screenshots": [
            ("01-dashboard.png", "Tutto il tuo business. Un colpo d'occhio."),
            ("18-scheda-veicoli.png", "Ogni veicolo ha la sua storia. Tu la conosci tutta."),
            ("02-calendario.png", "Sara risponde mentre sei sotto al cofano."),
            ("03-clienti.png", "Messaggio automatico. L'auto e' pronta."),
            ("10-analytics.png", "Sai sempre come va. Nessuna sorpresa."),
        ],
    },
    "carrozzeria": {
        "label": "Carrozzeria",
        "competitor_line": "I gestionali in abbonamento? €120/mese. €1.440/anno. Per sempre.",
        "screenshots": [
            ("01-dashboard.png", "Tutto il tuo business. Un colpo d'occhio."),
            ("19-scheda-carrozzeria.png", "Ogni sinistro tracciato. Stato riparazione chiaro."),
            ("02-calendario.png", "Il cliente sa tutto. Non ti chiama piu'."),
            ("03-clienti.png", "Messaggio automatico. Zero telefonate."),
            ("10-analytics.png", "Sai sempre come va. Nessuna sorpresa."),
        ],
    },
    "dentista": {
        "label": "Studio Dentistico",
        "competitor_line": "I gestionali in abbonamento? €120/mese. €1.440/anno. Per sempre.",
        "screenshots": [
            ("01-dashboard.png", "Tutto il tuo studio. Un colpo d'occhio."),
            ("17-scheda-odontoiatrica.png", "Anamnesi digitale. Tutto tracciato."),
            ("02-calendario.png", "Promemoria automatico. Meno appuntamenti saltati."),
            ("22-pacchetti.png", "Pacchetti trattamenti. Tutto sotto controllo."),
            ("10-analytics.png", "Sai sempre come va. Nessuna sorpresa."),
        ],
    },
    "centro_estetico": {
        "label": "Centro Estetico",
        "competitor_line": "I gestionali in abbonamento? €120/mese. €1.440/anno. Per sempre.",
        "screenshots": [
            ("01-dashboard.png", "Tutto il tuo business. Un colpo d'occhio."),
            ("14-scheda-estetica.png", "Controindicazioni e allergie. Tutto tracciato."),
            ("02-calendario.png", "I tuoi clienti sono tuoi. Punto."),
            ("22-pacchetti.png", "Pacchetti promo. Sedute tracciate."),
            ("10-analytics.png", "Sai sempre come va. Nessuna sorpresa."),
        ],
    },
    "nail_artist": {
        "label": "Nail Artist",
        "competitor_line": "I gestionali in abbonamento? €120/mese. €1.440/anno. Per sempre.",
        "screenshots": [
            ("01-dashboard.png", "Tutto il tuo business. Un colpo d'occhio."),
            ("14-scheda-estetica.png", "Allergie e preferenze. Tutto tracciato."),
            ("02-calendario.png", "Sara prenota. Le tue mani restano ferme."),
            ("22-pacchetti.png", "Pacchetti nail art. Tutto sotto controllo."),
            ("10-analytics.png", "Sai sempre come va. Nessuna sorpresa."),
        ],
    },
    "palestra": {
        "label": "Palestra",
        "competitor_line": "I gestionali in abbonamento? €120/mese. €1.440/anno. Per sempre.",
        "screenshots": [
            ("01-dashboard.png", "Tutto il tuo business. Un colpo d'occhio."),
            ("13-scheda-fitness.png", "Abbonamenti e certificati. Tutto tracciato."),
            ("02-calendario.png", "Promemoria rinnovo. Nessuno sparisce."),
            ("23-fedelta.png", "Programma fedelta'. Clienti che tornano."),
            ("10-analytics.png", "Sai sempre come va. Nessuna sorpresa."),
        ],
    },
    "fisioterapista": {
        "label": "Fisioterapista",
        "competitor_line": "I gestionali in abbonamento? €120/mese. €1.440/anno. Per sempre.",
        "screenshots": [
            ("01-dashboard.png", "Tutto il tuo studio. Un colpo d'occhio."),
            ("16-scheda-fisioterapia.png", "Scheda VAS e sedute. Tutto tracciato."),
            ("02-calendario.png", "Promemoria seduta. Il ciclo va a termine."),
            ("03-clienti.png", "Progressione tracciata. Il paziente guarisce."),
            ("10-analytics.png", "Sai sempre come va. Nessuna sorpresa."),
        ],
    },
}


# ── Helpers ──────────────────────────────────────────────────────────────────

def run(cmd, desc=""):
    if desc:
        print(f"  {desc}...", end=" ", flush=True)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("ERRORE")
        print(f"    {(result.stderr or 'no stderr')[-500:]}")
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
    return float(r.stdout.strip()) if r.stdout.strip() else 0


def best_clip(vert, clip_num, clips_from=None):
    source = clips_from or vert
    clips_dir = OUTPUT / source / "clips"
    variants = list(clips_dir.glob(f"{source}_clip{clip_num}_v*.mp4"))
    if not variants:
        variants = list(clips_dir.glob(f"{source}_*.mp4"))
    if not variants:
        return None
    return max(variants, key=lambda p: p.stat().st_size)


def find_font_bold(size):
    for f in ["/System/Library/Fonts/Supplemental/Arial Bold.ttf",
              "/Library/Fonts/Inter-Bold.ttf"]:
        if os.path.exists(f):
            try:
                return ImageFont.truetype(f, size)
            except Exception:
                continue
    return ImageFont.load_default()


def find_font_regular(size):
    for f in ["/System/Library/Fonts/Supplemental/Arial.ttf",
              "/Library/Fonts/Inter-Regular.ttf",
              "/System/Library/Fonts/Helvetica.ttc"]:
        if os.path.exists(f):
            try:
                return ImageFont.truetype(f, size)
            except Exception:
                continue
    return ImageFont.load_default()


# ── Pre-generate gradient background (reused for all frames) ─────────────────

_BG_CACHE = None

def get_gradient_bg():
    global _BG_CACHE
    if _BG_CACHE is not None:
        return _BG_CACHE.copy()

    print("  Generating gradient background...", end=" ", flush=True)
    bg = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    pixels = bg.load()
    cx, cy = W / 2, H / 2
    max_dist = math.sqrt(cx * cx + cy * cy)
    for y in range(H):
        for x in range(W):
            dist = min(math.sqrt((x - cx) ** 2 + (y - cy) ** 2) / max_dist, 1.0)
            r = int(12 * (1 - dist * 0.8))
            g = int(25 * (1 - dist * 0.8))
            b = int(50 * (1 - dist * 0.8))
            pixels[x, y] = (r, g, b, 255)
    _BG_CACHE = bg
    print("OK")
    return bg.copy()


# ── Pillow frame generators ─────────────────────────────────────────────────

def make_screenshot_frame(screenshot_path, subtitle, output_path):
    """Generate a 1080x1920 PNG frame: gradient bg + logo badge + screenshot + text."""
    bg = get_gradient_bg()

    # Logo badge top-left
    if LOGO_CUTOUT.exists():
        logo = Image.open(str(LOGO_CUTOUT)).convert("RGBA")
        logo_small = logo.resize((52, 52), Image.LANCZOS)
        r_c, g_c, b_c, a_c = logo_small.split()
        a_c = a_c.point(lambda x: min(255, int(x * 1.5)))
        logo_small = Image.merge("RGBA", (r_c, g_c, b_c, a_c))
        bg.paste(logo_small, (32, 28), logo_small)

    draw = ImageDraw.Draw(bg)
    badge_font = find_font_bold(28)
    draw.text((94, 40), "FLUXION", fill=(80, 195, 215, 240), font=badge_font)

    # Screenshot with rounded corners + shadow
    scr = Image.open(str(screenshot_path)).convert("RGBA")
    max_w = W - 100
    scale = max_w / scr.width
    scr_w = int(scr.width * scale)
    scr_h = int(scr.height * scale)
    scr = scr.resize((scr_w, scr_h), Image.LANCZOS)

    radius = 20
    mask = Image.new("L", (scr_w, scr_h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, scr_w - 1, scr_h - 1], radius=radius, fill=255)

    shadow = Image.new("RGBA", (scr_w + 60, scr_h + 60), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle([30, 30, scr_w + 29, scr_h + 29], radius=radius, fill=(0, 0, 0, 140))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=20))

    scr_x = (W - scr_w) // 2
    scr_y = 320
    bg.paste(shadow, (scr_x - 30, scr_y - 30 + 15), shadow)
    scr_rounded = Image.new("RGBA", (scr_w, scr_h), (0, 0, 0, 0))
    scr_rounded.paste(scr, (0, 0), mask)
    bg.paste(scr_rounded, (scr_x, scr_y), scr_rounded)

    # Selling text below with glow + shadow
    font = find_font_bold(40)
    bbox = ImageDraw.Draw(bg).textbbox((0, 0), subtitle, font=font)
    tw = bbox[2] - bbox[0]
    text_x = (W - tw) // 2
    text_y = scr_y + scr_h + 50

    # Glow (teal, 2 passes)
    for blur_r, alpha in [(12, 50), (5, 90)]:
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(glow).text((text_x, text_y), subtitle, fill=(60, 200, 220, alpha), font=font)
        glow = glow.filter(ImageFilter.GaussianBlur(radius=blur_r))
        bg = Image.alpha_composite(bg, glow)

    # Sharp text
    ImageDraw.Draw(bg).text((text_x, text_y), subtitle, fill=(255, 255, 255, 255), font=font)

    # Small accent line under text
    line_y = text_y + 55
    line_w = min(tw, 300)
    line_x = (W - line_w) // 2
    ImageDraw.Draw(bg).line([(line_x, line_y), (line_x + line_w, line_y)], fill=(60, 200, 220, 120), width=2)

    bg.convert("RGB").save(str(output_path), "PNG", quality=95)


FEATURES_LIST = [
    ("Fatture elettroniche", "Emetti e ricevi. Lo SDI lo gestisce lui."),
    ("Ordini ai fornitori", "Sai cosa ordinare. Prima che finisca."),
    ("Gestione dipendenti", "Turni, ferie, provvigioni. Senza fogli Excel."),
    ("Cassa e prima nota", "Il commercialista ti ringrazia."),
    ("Schede professionali", "Ogni cliente ha la sua storia. Tutta in un posto."),
    ("Segretaria AI 24/7", "Risponde al telefono anche di notte."),
    ("Messaggi automatici", "Promemoria, auguri, promo. Tu non tocchi nulla."),
    ("Salvataggio automatico", "I tuoi 10 anni di dati. Al sicuro. Per sempre."),
]


def _draw_features_base(bg):
    """Draw header, subtitle, accent line on bg. Returns draw object."""
    # Logo badge top-left
    if LOGO_CUTOUT.exists():
        logo = Image.open(str(LOGO_CUTOUT)).convert("RGBA")
        logo_small = logo.resize((52, 52), Image.LANCZOS)
        r_c, g_c, b_c, a_c = logo_small.split()
        a_c = a_c.point(lambda x: min(255, int(x * 1.5)))
        logo_small = Image.merge("RGBA", (r_c, g_c, b_c, a_c))
        bg.paste(logo_small, (32, 28), logo_small)

    draw = ImageDraw.Draw(bg)
    draw.text((94, 40), "FLUXION", fill=(80, 195, 215, 240), font=find_font_bold(28))

    # Header with glow
    header_font = find_font_bold(58)
    header = "Un unico software."
    bbox = draw.textbbox((0, 0), header, font=header_font)
    hx = (W - (bbox[2] - bbox[0])) // 2
    hy = 160
    for blur_r, alpha in [(18, 45), (8, 85)]:
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(glow).text((hx, hy), header, fill=(60, 200, 220, alpha), font=header_font)
        glow = glow.filter(ImageFilter.GaussianBlur(radius=blur_r))
        bg = Image.alpha_composite(bg, glow)
    draw = ImageDraw.Draw(bg)
    draw.text((hx, hy), header, fill=(255, 255, 255, 255), font=header_font)

    # Subtitle
    sub_font = find_font_bold(58)
    sub = "Tutta la tua attivita'."
    bbox = draw.textbbox((0, 0), sub, font=sub_font)
    draw.text(((W - (bbox[2] - bbox[0])) // 2, 240), sub, fill=(60, 200, 220, 255), font=sub_font)

    # Accent line
    draw.line([(W // 2 - 200, 330), (W // 2 + 200, 330)], fill=(60, 200, 220, 80), width=2)
    return bg


def make_features_step(output_path, show_up_to, highlight_idx=None, show_tagline=False):
    """Generate features frame showing items 0..show_up_to. highlight_idx gets emphasis."""
    bg = _draw_features_base(get_gradient_bg())

    feat_font = find_font_bold(32)
    feat_font_hi = find_font_bold(36)
    desc_font = find_font_regular(25)
    desc_font_hi = find_font_regular(28)
    check_font = find_font_bold(36)
    check_font_hi = find_font_bold(42)
    y_start = 390
    y_step = 148
    x_check = 70
    x_text = 130

    for i in range(show_up_to + 1):
        if i >= len(FEATURES_LIST):
            break
        feat, desc = FEATURES_LIST[i]
        y = y_start + i * y_step
        is_hi = (i == highlight_idx)

        if is_hi:
            # Highlighted: larger, brighter, with glow behind the whole row
            row_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            row_draw = ImageDraw.Draw(row_glow)
            row_draw.rounded_rectangle(
                [x_check - 20, y - 16, W - 50, y + 80],
                radius=12, fill=(60, 200, 220, 18),
            )
            row_glow = row_glow.filter(ImageFilter.GaussianBlur(radius=8))
            bg = Image.alpha_composite(bg, row_glow)
            draw = ImageDraw.Draw(bg)

            # Checkmark glow (stronger)
            for blur_r, alpha in [(8, 70), (4, 110)]:
                glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
                ImageDraw.Draw(glow).text((x_check - 3, y - 6), "\u2713", fill=(60, 200, 220, alpha), font=check_font_hi)
                glow = glow.filter(ImageFilter.GaussianBlur(radius=blur_r))
                bg = Image.alpha_composite(bg, glow)
            draw = ImageDraw.Draw(bg)
            draw.text((x_check - 3, y - 6), "\u2713", fill=(60, 220, 240, 255), font=check_font_hi)
            draw.text((x_text, y - 4), feat, fill=(255, 255, 255, 255), font=feat_font_hi)
            draw.text((x_text, y + 44), desc, fill=(210, 210, 220, 255), font=desc_font_hi)
        else:
            # Previous items: dimmed
            draw = ImageDraw.Draw(bg)
            draw.text((x_check, y - 2), "\u2713", fill=(60, 200, 220, 140), font=check_font)
            draw.text((x_text, y), feat, fill=(180, 180, 180, 180), font=feat_font)
            draw.text((x_text, y + 42), desc, fill=(120, 120, 130, 150), font=desc_font)

    if show_tagline:
        tag_font = find_font_bold(34)
        tagline = "Tutto questo. Un solo acquisto."
        bbox = ImageDraw.Draw(bg).textbbox((0, 0), tagline, font=tag_font)
        tx = (W - (bbox[2] - bbox[0])) // 2
        ty = y_start + len(FEATURES_LIST) * y_step + 30
        for blur_r, alpha in [(10, 40), (5, 70)]:
            glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(glow).text((tx, ty), tagline, fill=(60, 200, 220, alpha), font=tag_font)
            glow = glow.filter(ImageFilter.GaussianBlur(radius=blur_r))
            bg = Image.alpha_composite(bg, glow)
        ImageDraw.Draw(bg).text((tx, ty), tagline, fill=(255, 255, 255, 255), font=tag_font)

    bg.convert("RGB").save(str(output_path), "PNG", quality=95)


def make_features_sequence(tmp_dir):
    """Generate feature build-up video: features appear one by one, ~10s total."""
    n = len(FEATURES_LIST)
    frame_clips = []

    # Each feature appears for 2.0s highlighted, then dims
    for i in range(n):
        png = tmp_dir / f"feat_step_{i}.png"
        make_features_step(png, show_up_to=i, highlight_idx=i, show_tagline=False)
        vid = tmp_dir / f"feat_step_{i}.mp4"
        if still_to_video(png, 2.0, vid):
            frame_clips.append(vid)

    # Final frame: all visible + tagline (3.0s)
    png_final = tmp_dir / "feat_final.png"
    make_features_step(png_final, show_up_to=n - 1, highlight_idx=None, show_tagline=True)
    vid_final = tmp_dir / "feat_final.mp4"
    if still_to_video(png_final, 3.0, vid_final):
        frame_clips.append(vid_final)

    # Concatenate all steps into one clip
    if len(frame_clips) < 2:
        return None
    out = tmp_dir / "02_features.mp4"
    if concat_segments(frame_clips, out):
        return out
    return None


def make_cta_frame(output_path, competitor_line):
    """Generate CTA frame: logo grande + glow text + strikethrough competitor."""
    bg = get_gradient_bg()

    # Logo badge top-left
    if LOGO_CUTOUT.exists():
        logo = Image.open(str(LOGO_CUTOUT)).convert("RGBA")
        logo_small = logo.resize((52, 52), Image.LANCZOS)
        r_c, g_c, b_c, a_c = logo_small.split()
        a_c = a_c.point(lambda x: min(255, int(x * 1.5)))
        logo_small = Image.merge("RGBA", (r_c, g_c, b_c, a_c))
        bg.paste(logo_small, (32, 28), logo_small)

        # Logo grande al centro (30% opacity)
        logo_big = logo.resize((400, 400), Image.LANCZOS)
        r_c, g_c, b_c, a_c = logo_big.split()
        a_c = a_c.point(lambda x: min(255, int(x * 0.30)))
        logo_big = Image.merge("RGBA", (r_c, g_c, b_c, a_c))
        bg.paste(logo_big, ((W - 400) // 2, 180), logo_big)

    draw = ImageDraw.Draw(bg)
    draw.text((94, 40), "FLUXION", fill=(80, 195, 215, 240), font=find_font_bold(28))

    # FLUXION title with glow
    title_font = find_font_bold(100)
    title = "FLUXION"
    bbox = draw.textbbox((0, 0), title, font=title_font)
    tx = (W - (bbox[2] - bbox[0])) // 2
    ty = 620
    for blur_r, alpha in [(20, 40), (10, 70), (5, 120)]:
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(glow).text((tx, ty), title, fill=(60, 200, 220, alpha), font=title_font)
        glow = glow.filter(ImageFilter.GaussianBlur(radius=blur_r))
        bg = Image.alpha_composite(bg, glow)
    draw = ImageDraw.Draw(bg)
    draw.text((tx, ty), title, fill=(255, 255, 255, 255), font=title_font)

    # Subtitle
    sub_font = find_font_regular(34)
    sub = "Il gestionale che non ti costa ogni mese"
    bbox = draw.textbbox((0, 0), sub, font=sub_font)
    draw.text(((W - bbox[2] + bbox[0]) // 2, 760), sub, fill=(200, 200, 200, 255), font=sub_font)

    # Price with glow
    price_font = find_font_bold(64)
    price = "\u20ac497 una volta. Per sempre."
    bbox = draw.textbbox((0, 0), price, font=price_font)
    px = (W - (bbox[2] - bbox[0])) // 2
    py = 880
    for blur_r, alpha in [(15, 50), (8, 90)]:
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(glow).text((px, py), price, fill=(60, 200, 220, alpha), font=price_font)
        glow = glow.filter(ImageFilter.GaussianBlur(radius=blur_r))
        bg = Image.alpha_composite(bg, glow)
    draw = ImageDraw.Draw(bg)
    draw.text((px, py), price, fill=(255, 255, 255, 255), font=price_font)

    # Competitor with strikethrough
    comp_font = find_font_regular(32)
    draw.text(((W - draw.textbbox((0, 0), "I gestionali in abbonamento?", font=comp_font)[2]) // 2, 1020),
              "I gestionali in abbonamento?", fill=(200, 200, 200, 220), font=comp_font)

    comp2_font = find_font_bold(36)
    comp2 = "\u20ac120/mese = \u20ac1.440/anno = PER SEMPRE"
    bbox2 = draw.textbbox((0, 0), comp2, font=comp2_font)
    cw = bbox2[2] - bbox2[0]
    cx2 = (W - cw) // 2
    cy2 = 1070
    draw.text((cx2, cy2), comp2, fill=(255, 70, 70, 240), font=comp2_font)
    draw.line([(cx2, cy2 + 22), (cx2 + cw, cy2 + 22)], fill=(255, 70, 70, 200), width=3)

    # Separator + URL with glow
    draw.line([(W // 2 - 200, 1140), (W // 2 + 200, 1140)], fill=(80, 80, 100, 150), width=2)
    url_font = find_font_bold(40)
    url = "fluxion-landing.pages.dev"
    bbox = draw.textbbox((0, 0), url, font=url_font)
    ux = (W - (bbox[2] - bbox[0])) // 2
    uy = 1180
    for blur_r, alpha in [(10, 40), (5, 70)]:
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(glow).text((ux, uy), url, fill=(100, 100, 255, alpha), font=url_font)
        glow = glow.filter(ImageFilter.GaussianBlur(radius=blur_r))
        bg = Image.alpha_composite(bg, glow)
    ImageDraw.Draw(bg).text((ux, uy), url, fill=(140, 140, 255, 255), font=url_font)

    bg.convert("RGB").save(str(output_path), "PNG", quality=95)


# ── FFmpeg operations ────────────────────────────────────────────────────────

def scale_clip(input_path, output_path, duration=None):
    dur_args = ["-t", str(duration)] if duration else []
    cmd = [
        "ffmpeg", "-y", "-i", str(input_path), *dur_args,
        "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},format=yuv420p",
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-pix_fmt", "yuv420p", "-an", str(output_path),
    ]
    return run(cmd, f"Scale {input_path.name}")


def image_to_video(img_path, duration, output_path):
    """Convert still PNG to video with subtle Ken Burns zoom."""
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(img_path),
        "-vf", (
            f"scale={W}:{H},format=yuv420p,"
            f"zoompan=z='1.0+0.002*on':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":d={int(duration * FPS)}:s={W}x{H}:fps={FPS}"
        ),
        "-t", str(duration),
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-pix_fmt", "yuv420p", "-an", str(output_path),
    ]
    return run(cmd, f"Image→Video ({duration:.1f}s)")


def still_to_video(img_path, duration, output_path):
    """Convert still PNG to video (no zoom, for CTA)."""
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(img_path),
        "-vf", f"scale={W}:{H},format=yuv420p",
        "-t", str(duration), "-r", str(FPS),
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-an", str(output_path),
    ]
    return run(cmd, f"CTA video ({duration:.1f}s)")


def concat_segments(segment_paths, output_path):
    list_file = output_path.parent / "concat_list.txt"
    with open(list_file, "w") as f:
        for p in segment_paths:
            f.write(f"file '{p.absolute()}'\n")
    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-pix_fmt", "yuv420p", "-r", str(FPS), "-an", str(output_path),
    ]
    ok = run(cmd, "Concatenate")
    list_file.unlink(missing_ok=True)
    return ok


def mix_audio(video_path, voiceover_path, hook_dur, output_path):
    total_dur = get_duration(video_path)
    vo_delay = int(hook_dur * 1000)

    # Mix: music from 0s (immediate) + voiceover (delayed after hook)
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path), "-i", str(voiceover_path),
        "-i", str(MUSIC_BG),
        "-filter_complex",
        (
            f"[1:a]adelay={vo_delay}|{vo_delay},volume=1.0,apad[vo];"
            f"[2:a]volume=0.18,"
            f"afade=t=in:st=0:d=0.3,"
            f"afade=t=out:st={total_dur - 3}:d=3,apad[music];"
            f"[vo][music]amix=inputs=2:duration=shortest:dropout_transition=3[out]"
        ),
        "-map", "0:v", "-map", "[out]",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-t", str(total_dur), str(output_path),
    ]
    if run(cmd, "Mix audio (voiceover + musica)"):
        return True

    # Fallback: just voiceover
    print("  Retry: solo voiceover...")
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path), "-i", str(voiceover_path),
        "-filter_complex", f"[1:a]adelay={vo_delay}|{vo_delay}[vo]",
        "-map", "0:v", "-map", "[vo]",
        "-c:v", "copy", "-c:a", "aac", "-shortest", str(output_path),
    ]
    return run(cmd, "Mix audio (solo voiceover)")


def convert_16x9(input_path, output_path):
    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-filter_complex",
        (
            f"[0:v]scale=1920:1080:force_original_aspect_ratio=increase,"
            f"crop=1920:1080,avgblur=sizeX=40:sizeY=40,setsar=1[bg];"
            f"[0:v]scale=-1:1080,setsar=1[fg];"
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2"
        ),
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-c:a", "copy", "-pix_fmt", "yuv420p", str(output_path),
    ]
    return run(cmd, "Convert 16:9")


def extract_thumbnail(video_path, output_path, time_sec=20):
    cmd = [
        "ffmpeg", "-y", "-ss", str(time_sec),
        "-i", str(video_path), "-vframes", "1", "-q:v", "2", str(output_path),
    ]
    return run(cmd, "Thumbnail")


# ── Main assembly ────────────────────────────────────────────────────────────

def assemble_vertical(vert, config):
    label = config["label"]
    print(f"\n{'=' * 60}")
    print(f"  FLUXION Video — {label} ({vert})")
    print(f"{'=' * 60}")

    vert_dir = OUTPUT / vert
    vert_dir.mkdir(parents=True, exist_ok=True)
    clips_from = config.get("clips_from")
    tmp = Path(tempfile.mkdtemp(prefix=f"fluxion_{vert}_"))
    segments = []

    # ── 1. Hook clip(s) ───────────────────────────────────────────
    is_multi = config.get("multi_sector", False)

    if is_multi:
        # Multi-sector montage: 2s clip from each of 9 verticals
        montage_verts = ["parrucchiere", "barbiere", "officina", "dentista",
                         "centro_estetico", "nail_artist", "palestra",
                         "fisioterapista", "carrozzeria"]
        montage_clips = []
        for i, mv in enumerate(montage_verts):
            mc = best_clip(mv, 1)
            if mc:
                mc_out = tmp / f"01_montage_{i}.mp4"
                if scale_clip(mc, mc_out, duration=2):
                    montage_clips.append(mc_out)
        if not montage_clips:
            print(f"  SKIP: nessuna clip per montaggio")
            return False
        hook_path = tmp / "01_hook.mp4"
        if not concat_segments(montage_clips, hook_path):
            return False
        segments.append(hook_path)
        hook_dur = len(montage_clips) * 2.0
    else:
        clip1 = best_clip(vert, 1, clips_from)
        if not clip1:
            print(f"  SKIP: clip1 non trovata")
            return False
        hook_path = tmp / "01_hook.mp4"
        if not scale_clip(clip1, hook_path, duration=8):
            return False
        segments.append(hook_path)
        hook_dur = 8.0

    # ── 2. Features build-up (one by one, ~9s) — prima degli screenshot
    feat_vid = make_features_sequence(tmp)
    if feat_vid:
        segments.append(feat_vid)
    else:
        print("  WARN: features sequence failed, skipping")


    # ── 3. Screenshot segments (Pillow frames → FFmpeg video) ────
    # Segment audio: check local dir first, then clips_from source
    def _seg_path(name):
        local = vert_dir / name
        if local.exists():
            return local
        if clips_from:
            fallback = OUTPUT / clips_from / name
            if fallback.exists():
                return fallback
        return local

    seg1_dur = get_duration(_seg_path("seg_1.mp3")) if _seg_path("seg_1.mp3").exists() else 8.0
    seg2_dur = get_duration(_seg_path("seg_2.mp3")) if _seg_path("seg_2.mp3").exists() else 10.0

    screenshots = config["screenshots"]
    problem_screens = screenshots[:2]
    solution_screens = screenshots[2:]

    # Problem screenshots (timed to seg_1)
    dur_each = seg1_dur / max(len(problem_screens), 1)
    for i, (fname, subtitle) in enumerate(problem_screens):
        img = SCREENSHOTS / fname
        if not img.exists():
            print(f"  WARN: {fname} mancante")
            continue
        frame_png = tmp / f"frame_prob_{i}.png"
        make_screenshot_frame(img, subtitle, frame_png)
        vid = tmp / f"02_prob_{i}.mp4"
        if image_to_video(frame_png, dur_each, vid):
            segments.append(vid)

    # Solution screenshots (timed to seg_2)
    dur_each = seg2_dur / max(len(solution_screens), 1)
    for i, (fname, subtitle) in enumerate(solution_screens):
        img = SCREENSHOTS / fname
        if not img.exists():
            print(f"  WARN: {fname} mancante")
            continue
        frame_png = tmp / f"frame_sol_{i}.png"
        make_screenshot_frame(img, subtitle, frame_png)
        vid = tmp / f"03_sol_{i}.mp4"
        if image_to_video(frame_png, dur_each, vid):
            segments.append(vid)

    # ── 4. Solution clip(s) ────────────────────────────────────────
    if is_multi:
        # Multi-sector: 2s clip3 from 3 diverse verticals
        for i, mv in enumerate(["parrucchiere", "palestra", "dentista"]):
            mc3 = best_clip(mv, 3)
            if mc3:
                mc3_out = tmp / f"04_solution_{i}.mp4"
                if scale_clip(mc3, mc3_out, duration=2):
                    segments.append(mc3_out)
    else:
        clip3 = best_clip(vert, 3, clips_from)
        if clip3:
            clip3_vid = tmp / "04_solution.mp4"
            if scale_clip(clip3, clip3_vid, duration=6):
                segments.append(clip3_vid)

    # ── 5. CTA frame ────────────────────────────────────────────
    seg3_dur = get_duration(_seg_path("seg_3.mp3")) if _seg_path("seg_3.mp3").exists() else 7.0
    cta_dur = max(seg3_dur + 1.0, 7.0)

    cta_png = tmp / "cta.png"
    make_cta_frame(cta_png, config["competitor_line"])
    cta_vid = tmp / "06_cta.mp4"
    if not still_to_video(cta_png, cta_dur, cta_vid):
        return False
    segments.append(cta_vid)

    if len(segments) < 4:
        print(f"  ERRORE: troppo pochi segmenti ({len(segments)})")
        return False

    # ── 5. Concatenate ───────────────────────────────────────────
    concat_path = tmp / "concat.mp4"
    if not concat_segments(segments, concat_path):
        return False

    # ── 6. Audio ─────────────────────────────────────────────────
    voiceover = vert_dir / f"{vert}_voiceover.mp3"
    # Fallback: use source vertical's voiceover if clips_from is set
    if not voiceover.exists() and clips_from:
        voiceover = OUTPUT / clips_from / f"{clips_from}_voiceover.mp3"
    final_9x16 = vert_dir / f"{vert}_final_9x16.mp4"

    if voiceover.exists():
        if not mix_audio(concat_path, voiceover, hook_dur, final_9x16):
            subprocess.run(["cp", str(concat_path), str(final_9x16)])
    else:
        subprocess.run(["cp", str(concat_path), str(final_9x16)])

    # ── 7. 16:9 ──────────────────────────────────────────────────
    final_16x9 = vert_dir / f"{vert}_final_16x9.mp4"
    convert_16x9(final_9x16, final_16x9)

    # ── 8. Thumbnail ─────────────────────────────────────────────
    thumb = vert_dir / f"{vert}_thumb.jpg"
    total = get_duration(final_9x16)
    extract_thumbnail(final_16x9, thumb, time_sec=min(20, max(1, total - 5)))

    # ── Report ───────────────────────────────────────────────────
    dur = get_duration(final_9x16)
    size_mb = final_9x16.stat().st_size / (1024 * 1024) if final_9x16.exists() else 0
    print(f"\n  FATTO: {vert}")
    print(f"    9:16  {final_9x16.name} — {dur:.1f}s, {size_mb:.1f}MB")
    if final_16x9.exists():
        size16 = final_16x9.stat().st_size / (1024 * 1024)
        print(f"    16:9  {final_16x9.name} — {size16:.1f}MB")
    if thumb.exists():
        print(f"    Thumb {thumb.name}")

    # Cleanup
    for f in tmp.glob("*"):
        f.unlink()
    tmp.rmdir()
    return True


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "all"

    print("=" * 60)
    print("  FLUXION — Video Assembly Pipeline v2")
    print(f"  Design: logo badge + gradient bg + rounded screenshots")
    print(f"  Target: {target}")
    print("=" * 60)

    if not MUSIC_BG.exists():
        print(f"ERRORE: musica mancante: {MUSIC_BG}")
        sys.exit(1)
    if not LOGO_CUTOUT.exists():
        print(f"ERRORE: logo scontornato mancante: {LOGO_CUTOUT}")
        sys.exit(1)

    if target == "all":
        verts = list(VERTICALS.keys())
    elif target in VERTICALS:
        verts = [target]
    else:
        print(f"Verticale '{target}' non valido.")
        print(f"Usa: {list(VERTICALS.keys())} o 'all'")
        sys.exit(1)

    results = {}
    for vert in verts:
        ok = assemble_vertical(vert, VERTICALS[vert])
        results[vert] = "OK" if ok else "FAIL"

    print(f"\n{'=' * 60}")
    print("  REPORT FINALE")
    print(f"{'=' * 60}")
    for vert, status in results.items():
        label = VERTICALS[vert]["label"]
        icon = "OK  " if status == "OK" else "FAIL"
        f = OUTPUT / vert / f"{vert}_final_9x16.mp4"
        dur = get_duration(f) if f.exists() else 0
        size = f.stat().st_size / (1024 * 1024) if f.exists() else 0
        print(f"  [{icon}] {label:25s} — {dur:.1f}s / {size:.1f}MB")

    ok_count = sum(1 for v in results.values() if v == "OK")
    fail_count = len(results) - ok_count
    print(f"\n  {ok_count}/{len(results)} assemblati" + (f" ({fail_count} falliti)" if fail_count else ""))


if __name__ == "__main__":
    main()
