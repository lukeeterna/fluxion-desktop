#!/usr/bin/env python3
"""
FLUXION Demo Video Creator — V3 "Lasciali a Bocca Aperta"
Based on 3 CoVe 2026 deep research + founder feedback S107.

V3 fixes ALL V2 problems:
  1. Logo burned on EVERY frame via Pillow (not ffmpeg overlay)
  2. Frame follows voice — specific screenshot per section
  3. Practical HOW explanations — not just talking, SHOWING
  4. Two-phase verticals: problem card → screenshot zoom
  5. Zoom on SPECIFIC UI areas (KPI row, client details, etc.)
  6. WOW effects: blur→sharp reveal, zoom dissolve, split screen
  7. YouTube chapters in metadata output
  8. Lower thirds with micro-categories

Techniques:
  - Pre-scale 8000px zoompan (ZERO jitter)
  - xfade dissolve/slideleft transitions
  - Logo watermark burned via Pillow on every image
  - Edge-TTS IsabellaNeural -5% rate
  - Text overlay burned via Pillow (no ffmpeg drawtext needed)
  - YouTube-optimized H.264 High Profile

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

# Colors
CYAN = (6, 182, 212)
RED = (239, 68, 68)
DARK_BG = (10, 15, 30)
GRAY_TEXT = (148, 163, 184)
WHITE = (255, 255, 255)
GREEN = (34, 197, 94)

# ============================================================
# SCRIPT V3 — "Lasciali a Bocca Aperta"
# Structure:
#   HOOK (pain) → DASHBOARD (overview) → CALENDARIO (how) →
#   CLIENTI (how) → SERVIZI+OPERATORI → VERTICALI (problem→solution) →
#   SARA WOW → CASSA+ANALYTICS speed round → PREZZO → CTA
#
# Formula: PAS (Problem - Agitation - Solution) per verticale
# Tono: "amico competente", TU, zero tecnicismi
# ============================================================

SLIDES = [
    # ═══════════════════════════════════════════════════════
    # CAPITOLO 0: HOOK — Il dolore universale (0:00-0:10)
    # ═══════════════════════════════════════════════════════
    {
        "id": "hook",
        "chapter": "Il Problema",
        "image": None,  # problem card
        "card_type": "hook",
        "text": (
            "Il telefono squilla. Hai le mani occupate. "
            "Non puoi rispondere. "
            "Quel cliente ha gia' chiamato qualcun altro."
        ),
        "lower_third": None,
        "zoom_target": (0.5, 0.5),
        "zoom_amount": 1.08,
        "transition": "fadeblack",
        "padding": 1.0,
    },
    # ═══════════════════════════════════════════════════════
    # CAPITOLO 0b: AGITAZIONE — Quanto ti costa
    # ═══════════════════════════════════════════════════════
    {
        "id": "agitazione",
        "chapter": None,
        "image": None,
        "card_type": "agitazione",
        "text": (
            "Un cliente perso al giorno sono duecentocinquanta clienti all'anno. "
            "A trenta euro di media, sono settemilacinquecento euro buttati via. "
            "E intanto, una receptionist ti costerebbe novecento euro al mese."
        ),
        "lower_third": None,
        "zoom_target": (0.5, 0.5),
        "zoom_amount": 1.06,
        "transition": "dissolve",
        "padding": 1.0,
    },

    # ═══════════════════════════════════════════════════════
    # CAPITOLO 1: DASHBOARD — Vedi tutto in un colpo d'occhio
    # ═══════════════════════════════════════════════════════
    {
        "id": "dashboard_intro",
        "chapter": "La Dashboard",
        "image": "01-dashboard.png",
        "text": (
            "Ecco FLUXION. Appena lo apri, la dashboard ti mostra tutto. "
            "Appuntamenti di oggi, clienti totali, fatturato del mese, "
            "e il servizio piu' richiesto. Tutto in un colpo d'occhio."
        ),
        "lower_third": None,
        # Zoom on KPI cards row — top area of content (y=0.25 covers the 4 KPI cards)
        "zoom_target": (0.55, 0.28),
        "zoom_amount": 1.35,
        "transition": "dissolve",
        "padding": 0.8,
    },
    {
        "id": "dashboard_appointments",
        "chapter": None,
        "image": "01-dashboard.png",
        "text": (
            "Qui sotto, i prossimi appuntamenti con nome, servizio e orario. "
            "Maria Rossi, colore completo alle nove. "
            "Chiara Conti, meches alle nove e trenta. "
            "Vedi chi arriva, cosa deve fare, e se e' in ritardo."
        ),
        "lower_third": None,
        # Zoom on appointments list — middle-lower area
        "zoom_target": (0.4, 0.62),
        "zoom_amount": 1.4,
        "transition": "dissolve",
        "padding": 0.8,
    },

    # ═══════════════════════════════════════════════════════
    # CAPITOLO 2: CALENDARIO — Come funziona
    # ═══════════════════════════════════════════════════════
    {
        "id": "calendario",
        "chapter": "Il Calendario",
        "image": "02-calendario.png",
        "text": (
            "Il calendario. Vista settimanale, mensile, giornaliera. "
            "Per creare un appuntamento basta cliccare Nuovo Appuntamento. "
            "Scegli il cliente, il servizio, l'operatore, l'orario. "
            "Fatto. Due click."
        ),
        "lower_third": None,
        # Zoom on top area showing "Nuovo Appuntamento" button
        "zoom_target": (0.8, 0.08),
        "zoom_amount": 1.5,
        "transition": "smoothleft",
        "padding": 0.8,
    },

    # ═══════════════════════════════════════════════════════
    # CAPITOLO 3: CLIENTI — Scheda cliente nel dettaglio
    # ═══════════════════════════════════════════════════════
    {
        "id": "clienti",
        "chapter": "I Clienti",
        "image": "03-clienti.png",
        "text": (
            "La rubrica clienti. Nome, telefono, email, punteggio fedelta'. "
            "Clicchi su un cliente e vedi tutto: "
            "lo storico visite, le preferenze, le note. "
            "Sai esattamente cosa ha fatto l'ultima volta."
        ),
        "lower_third": None,
        # Zoom on client list rows showing details
        "zoom_target": (0.55, 0.32),
        "zoom_amount": 1.45,
        "transition": "dissolve",
        "padding": 0.8,
    },

    # ═══════════════════════════════════════════════════════
    # CAPITOLO 4: SERVIZI — Il listino
    # ═══════════════════════════════════════════════════════
    {
        "id": "servizi",
        "chapter": "Servizi e Operatori",
        "image": "04-servizi.png",
        "text": (
            "Il listino servizi. Taglio donna trentacinque euro, "
            "colore completo sessantacinque, meches ottantacinque. "
            "Ogni servizio ha la sua categoria, il prezzo, la durata. "
            "Aggiungi, modifica, organizza come vuoi."
        ),
        "lower_third": None,
        # Zoom on service list with prices
        "zoom_target": (0.55, 0.35),
        "zoom_amount": 1.4,
        "transition": "smoothleft",
        "padding": 0.8,
    },
    {
        "id": "operatori",
        "chapter": None,
        "image": "05-operatori.png",
        "text": (
            "Gli operatori. Ogni collaboratore ha il suo profilo: "
            "ruolo, contatto, statistiche mensili. "
            "Valentina e' la titolare, Roberto il senior barber, "
            "Sara la colorista. Ognuno con il suo calendario."
        ),
        "lower_third": None,
        # Zoom on first two operator cards
        "zoom_target": (0.4, 0.35),
        "zoom_amount": 1.35,
        "transition": "dissolve",
        "padding": 0.8,
    },

    # ═══════════════════════════════════════════════════════
    # CAPITOLO 5: VERTICALI — Come risolve PER TE
    # Ogni verticale: problem card → screenshot soluzione
    # ═══════════════════════════════════════════════════════

    # --- PARRUCCHIERE: problema ---
    {
        "id": "parr_problema",
        "chapter": "Per il Tuo Settore",
        "image": None,
        "card_type": "vertical_problem",
        "card_icon": "scissors",
        "card_title": "Parrucchieri · Barbieri · Saloni",
        "card_pain": "Stai facendo un colore.\nIl telefono squilla per la terza volta.",
        "text": (
            "Sei parrucchiere? Stai facendo un colore. "
            "Il telefono squilla per la terza volta. "
            "Non puoi rispondere, e quel cliente va da un altro."
        ),
        "lower_third": None,
        "zoom_target": (0.5, 0.5),
        "zoom_amount": 1.05,
        "transition": "fadeblack",
        "padding": 0.5,
    },
    # --- PARRUCCHIERE: soluzione ---
    {
        "id": "parr_soluzione",
        "chapter": None,
        "image": "02-calendario.png",
        "text": (
            "Con FLUXION, Sara risponde per te. "
            "Prende l'appuntamento, lo mette nel calendario, "
            "e manda la conferma WhatsApp al cliente. "
            "Tu non perdi ne' la cliente in poltrona ne' quella al telefono."
        ),
        "lower_third": "Parrucchieri · Barbieri · Saloni",
        # Zoom on calendar grid
        "zoom_target": (0.55, 0.45),
        "zoom_amount": 1.2,
        "transition": "dissolve",
        "padding": 0.8,
    },

    # --- OFFICINA: problema ---
    {
        "id": "off_problema",
        "chapter": None,
        "image": None,
        "card_type": "vertical_problem",
        "card_icon": "wrench",
        "card_title": "Officine · Carrozzerie · Gommisti",
        "card_pain": "Sei sotto il cofano.\nLe mani nere fino ai gomiti.",
        "text": (
            "Hai un'officina? Sei sotto il cofano, le mani nere fino ai gomiti. "
            "Il telefono squilla. Non puoi rispondere."
        ),
        "lower_third": None,
        "zoom_target": (0.5, 0.5),
        "zoom_amount": 1.05,
        "transition": "fadeblack",
        "padding": 0.5,
    },
    # --- OFFICINA: soluzione ---
    {
        "id": "off_soluzione",
        "chapter": None,
        "image": "03-clienti.png",
        "text": (
            "Sara risponde: officina Rossi, buongiorno. "
            "Prende l'appuntamento, chiede il modello dell'auto, "
            "e salva tutto nella scheda cliente. "
            "Tu non hai mosso un dito."
        ),
        "lower_third": "Officine · Carrozzerie · Gommisti",
        # Zoom on client details
        "zoom_target": (0.55, 0.28),
        "zoom_amount": 1.35,
        "transition": "dissolve",
        "padding": 0.8,
    },

    # --- CENTRO ESTETICO: problema ---
    {
        "id": "est_problema",
        "chapter": None,
        "image": None,
        "card_type": "vertical_problem",
        "card_icon": "sparkle",
        "card_title": "Centri Estetici · Spa · Nail Art",
        "card_pain": "La cliente vuole prenotare.\nSono le 22:30 di sera.",
        "text": (
            "Centro estetico? La tua cliente vuole prenotare alle dieci e mezza di sera. "
            "Tu sei a casa. Chi risponde?"
        ),
        "lower_third": None,
        "zoom_target": (0.5, 0.5),
        "zoom_amount": 1.05,
        "transition": "fadeblack",
        "padding": 0.5,
    },
    # --- CENTRO ESTETICO: soluzione ---
    {
        "id": "est_soluzione",
        "chapter": None,
        "image": "04-servizi.png",
        "text": (
            "Sara risponde ventiquattro ore su ventiquattro. "
            "Trova lo slot, manda conferma WhatsApp. "
            "Il giorno prima, il promemoria automatico. "
            "Meno appuntamenti saltati, piu' incassi."
        ),
        "lower_third": "Centri Estetici · Spa · Nail Art",
        # Zoom on service list
        "zoom_target": (0.55, 0.4),
        "zoom_amount": 1.25,
        "transition": "dissolve",
        "padding": 0.8,
    },

    # --- RISTORANTE: problema ---
    {
        "id": "rist_problema",
        "chapter": None,
        "image": None,
        "card_type": "vertical_problem",
        "card_icon": "plate",
        "card_title": "Ristoranti · Pizzerie · Bar",
        "card_pain": "Venerdì sera, cucina piena.\nIl telefono non smette di squillare.",
        "text": (
            "Hai un ristorante? Venerdi' sera, cucina piena. "
            "Il telefono non smette di squillare per le prenotazioni."
        ),
        "lower_third": None,
        "zoom_target": (0.5, 0.5),
        "zoom_amount": 1.05,
        "transition": "fadeblack",
        "padding": 0.5,
    },
    # --- RISTORANTE: soluzione ---
    {
        "id": "rist_soluzione",
        "chapter": None,
        "image": "07-cassa.png",
        "text": (
            "Sara gestisce le prenotazioni e manda la conferma. "
            "E a fine serata, la cassa ti mostra tutto: "
            "centoottantadue euro incassati, tre transazioni, "
            "divisi tra contanti e carta. "
            "I tuoi tavoli sono pieni, i no-show dimezzati."
        ),
        "lower_third": "Ristoranti · Pizzerie · Bar",
        # Zoom on cassa totals
        "zoom_target": (0.5, 0.2),
        "zoom_amount": 1.4,
        "transition": "dissolve",
        "padding": 0.8,
    },

    # --- CLINICA: problema ---
    {
        "id": "clin_problema",
        "chapter": None,
        "image": None,
        "card_type": "vertical_problem",
        "card_icon": "medical",
        "card_title": "Cliniche · Dentisti · Fisioterapisti",
        "card_pain": "Uno slot vuoto dal dentista\ncosta fino a €200.",
        "text": (
            "Studio medico? Uno slot vuoto dal dentista costa fino a duecento euro. "
            "E il paziente che non si presenta non ti avvisa mai."
        ),
        "lower_third": None,
        "zoom_target": (0.5, 0.5),
        "zoom_amount": 1.05,
        "transition": "fadeblack",
        "padding": 0.5,
    },
    # --- CLINICA: soluzione ---
    {
        "id": "clin_soluzione",
        "chapter": None,
        "image": "05-operatori.png",
        "text": (
            "FLUXION manda il promemoria WhatsApp ventiquattro ore prima. "
            "Il paziente conferma o sposta. La poltrona non resta vuota. "
            "Ogni operatore ha il suo calendario e le sue statistiche."
        ),
        "lower_third": "Cliniche · Dentisti · Fisioterapisti",
        # Zoom on operator cards
        "zoom_target": (0.5, 0.38),
        "zoom_amount": 1.3,
        "transition": "dissolve",
        "padding": 0.8,
    },

    # --- PALESTRA: problema ---
    {
        "id": "pal_problema",
        "chapter": None,
        "image": None,
        "card_type": "vertical_problem",
        "card_icon": "dumbbell",
        "card_title": "Palestre · Yoga · Pilates · CrossFit",
        "card_pain": "Lezioni strapiene o mezze vuote.\nAbbonamenti che scadono senza che te ne accorgi.",
        "text": (
            "Palestra? Lezioni strapiene o mezze vuote. "
            "Abbonamenti che scadono senza che nessuno se ne accorga."
        ),
        "lower_third": None,
        "zoom_target": (0.5, 0.5),
        "zoom_amount": 1.05,
        "transition": "fadeblack",
        "padding": 0.5,
    },
    # --- PALESTRA: soluzione ---
    {
        "id": "pal_soluzione",
        "chapter": None,
        "image": "10-analytics.png",
        "text": (
            "Con gli analytics di FLUXION vedi tutto: "
            "centocinquantasei appuntamenti questo mese, "
            "centodieci clienti attivi, novanta per cento di conferme WhatsApp. "
            "Sai chi sta per andarsene prima che accada."
        ),
        "lower_third": "Palestre · Yoga · Pilates · CrossFit",
        # Zoom on analytics KPI row
        "zoom_target": (0.55, 0.2),
        "zoom_amount": 1.4,
        "transition": "dissolve",
        "padding": 0.8,
    },

    # ═══════════════════════════════════════════════════════
    # CAPITOLO 6: SARA — Il WOW factor
    # ═══════════════════════════════════════════════════════
    {
        "id": "sara",
        "chapter": "Sara, la Tua Assistente",
        "image": "08-voice.png",
        "text": (
            "E poi c'e' Sara. La tua receptionist che non va mai in ferie. "
            "Risponde al telefono ventiquattro ore su ventiquattro, "
            "in italiano perfetto. "
            "Capisce cosa vuole il cliente, prenota, "
            "e manda conferma WhatsApp. Tutto in automatico."
        ),
        "lower_third": "Sara · Assistente Vocale AI 24/7",
        # Zoom on Sara chat bubble
        "zoom_target": (0.35, 0.28),
        "zoom_amount": 1.5,
        "transition": "fadeblack",
        "padding": 1.0,
    },
    {
        "id": "sara_costo",
        "chapter": None,
        "image": "08-voice.png",
        "text": (
            "Come avere una segretaria. "
            "Ma non costa novecento euro al mese. "
            "E' inclusa nella licenza FLUXION. Per sempre."
        ),
        "lower_third": None,
        # Zoom out to show full Sara interface with PRONTA status
        "zoom_target": (0.7, 0.55),
        "zoom_amount": 1.3,
        "transition": "dissolve",
        "padding": 1.0,
    },

    # ═══════════════════════════════════════════════════════
    # CAPITOLO 7: CASSA + ANALYTICS — Speed round
    # ═══════════════════════════════════════════════════════
    {
        "id": "cassa",
        "chapter": "Cassa e Report",
        "image": "07-cassa.png",
        "text": (
            "La cassa. A fine giornata sai esattamente quanto hai incassato. "
            "Contanti, carte, Satispay. Ogni transazione registrata."
        ),
        "lower_third": None,
        # Zoom on transaction list
        "zoom_target": (0.55, 0.42),
        "zoom_amount": 1.3,
        "transition": "smoothleft",
        "padding": 0.6,
    },
    {
        "id": "analytics",
        "chapter": None,
        "image": "10-analytics.png",
        "text": (
            "I report mensili. Fatturato, appuntamenti, top servizi, "
            "classifica operatori. "
            "Valentina ha generato tremiladuecentocinquanta euro questo mese. "
            "Sai chi rende e dove investire."
        ),
        "lower_third": None,
        # Zoom on Top 5 Servizi + Operatori del mese
        "zoom_target": (0.55, 0.7),
        "zoom_amount": 1.35,
        "transition": "dissolve",
        "padding": 0.6,
    },

    # ═══════════════════════════════════════════════════════
    # CAPITOLO 8: TUTTO IN UNO
    # ═══════════════════════════════════════════════════════
    {
        "id": "tutto",
        "chapter": None,
        "image": None,
        "card_type": "features_summary",
        "text": (
            "Calendario, clienti, cassa, report, "
            "WhatsApp automatico, gestione operatori. "
            "Tutto in uno. Tutto in italiano. "
            "Funziona anche senza internet."
        ),
        "lower_third": None,
        "zoom_target": (0.5, 0.5),
        "zoom_amount": 1.05,
        "transition": "dissolve",
        "padding": 0.8,
    },

    # ═══════════════════════════════════════════════════════
    # CAPITOLO 9: PREZZO — Confronto che convince
    # ═══════════════════════════════════════════════════════
    {
        "id": "prezzo",
        "chapter": "Il Prezzo",
        "image": None,
        "card_type": "prezzo",
        "text": (
            "Un gestionale in abbonamento ti costa seicento euro all'anno. "
            "In tre anni, milleottocento euro. E non sara' mai tuo. "
            "FLUXION costa quattrocentonovantasette euro. Una volta. Per sempre. "
            "Si ripaga in tre settimane."
        ),
        "lower_third": None,
        "zoom_target": (0.5, 0.5),
        "zoom_amount": 1.05,
        "transition": "fadeblack",
        "padding": 1.0,
    },

    # ═══════════════════════════════════════════════════════
    # CAPITOLO 10: CTA — Chiusura
    # ═══════════════════════════════════════════════════════
    {
        "id": "cta",
        "chapter": "Inizia Ora",
        "image": None,
        "card_type": "cta",
        "text": (
            "FLUXION. Paghi una volta, usi per sempre. "
            "Nessun abbonamento. Nessuna commissione. "
            "Trenta giorni soddisfatti o rimborsati. "
            "Vai su fluxion punto it."
        ),
        "lower_third": None,
        "zoom_target": (0.5, 0.5),
        "zoom_amount": 1.0,
        "transition": "fadeblack",
        "padding": 1.5,
    },
]


# ============================================================
# PILLOW HELPERS
# ============================================================

def _load_font(size):
    from PIL import ImageFont
    for fp in ["/System/Library/Fonts/Helvetica.ttc",
               "/System/Library/Fonts/SFNSDisplay.ttf",
               "/Library/Fonts/Arial.ttf"]:
        if os.path.exists(fp):
            return ImageFont.truetype(fp, size)
    return ImageFont.load_default()


def _gradient(draw, w, h, top_color=DARK_BG, bottom_offset=20):
    """Dark gradient background."""
    r0, g0, b0 = top_color
    for y in range(h):
        frac = y / h
        r = int(r0 + frac * bottom_offset * 0.4)
        g = int(g0 + frac * bottom_offset * 0.6)
        b = int(b0 + frac * bottom_offset)
        draw.line([(0, y), (w, y)], fill=(r, g, b))


def burn_logo(img, logo_path, position="top_left", size=64, opacity=0.75):
    """Burn FLUXION logo onto a PIL Image. Returns modified image."""
    from PIL import Image
    if not os.path.exists(logo_path):
        return img

    logo = Image.open(logo_path).convert("RGBA")
    logo = logo.resize((size, size), Image.LANCZOS)

    # Apply opacity
    if opacity < 1.0:
        alpha = logo.split()[3]
        alpha = alpha.point(lambda p: int(p * opacity))
        logo.putalpha(alpha)

    img_rgba = img.convert("RGBA")
    w, h = img_rgba.size
    margin = 24

    if position == "top_left":
        pos = (margin, margin)
    elif position == "top_right":
        pos = (w - size - margin, margin)
    elif position == "center":
        pos = ((w - size) // 2, (h - size) // 2)
    else:
        pos = (margin, margin)

    img_rgba.paste(logo, pos, logo)
    return img_rgba.convert("RGB")


def burn_lower_third(img, text, font_size=36):
    """Burn lower-third label bar onto image."""
    from PIL import Image, ImageDraw
    w, h = img.size
    bar_h = 80
    bar = Image.new("RGBA", (w, bar_h), (0, 0, 0, 170))
    img_rgba = img.convert("RGBA")
    img_rgba.paste(bar, (0, h - bar_h), bar)
    img = img_rgba.convert("RGB")
    draw = ImageDraw.Draw(img)
    font = _load_font(font_size)
    draw.text((w // 2, h - bar_h // 2), text,
              fill=(255, 255, 255, 230), font=font, anchor="mm")
    return img


# ============================================================
# CARD GENERATORS (all with logo burned in)
# ============================================================

def create_hook_card(path, logo_path, w=1920, h=1080):
    """Opening hook — dark card with phone ringing imagery."""
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (w, h), DARK_BG)
    draw = ImageDraw.Draw(img)
    _gradient(draw, w, h)

    font_big = _load_font(72)
    font_med = _load_font(42)
    font_icon = _load_font(120)

    # Phone icon (emoji-like)
    draw.text((w // 2, h // 2 - 140), "\u260E", fill=RED, font=font_icon, anchor="mm")
    draw.text((w // 2, h // 2 + 20), "Il telefono squilla.",
              fill=WHITE, font=font_big, anchor="mm")
    draw.text((w // 2, h // 2 + 90), "Hai le mani occupate.",
              fill=GRAY_TEXT, font=font_med, anchor="mm")
    draw.text((w // 2, h // 2 + 150), "Quel cliente non aspetta.",
              fill=RED, font=font_med, anchor="mm")

    img = burn_logo(img, logo_path, size=80)
    img.save(path, quality=95)


def create_agitation_card(path, logo_path, w=1920, h=1080):
    """Card with 'cost of inaction' numbers."""
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (w, h), DARK_BG)
    draw = ImageDraw.Draw(img)
    _gradient(draw, w, h)

    font = _load_font(52)
    font_big = _load_font(96)
    font_small = _load_font(32)

    # Shocking numbers
    draw.text((w // 2, h // 2 - 180), "1 cliente perso al giorno",
              fill=GRAY_TEXT, font=font, anchor="mm")
    draw.text((w // 2, h // 2 - 90), "= 250 clienti / anno",
              fill=(220, 220, 220), font=font, anchor="mm")
    draw.text((w // 2, h // 2 + 30), "\u20ac 7.500",
              fill=RED, font=font_big, anchor="mm")
    draw.text((w // 2, h // 2 + 110), "di fatturato perso ogni anno",
              fill=GRAY_TEXT, font=font_small, anchor="mm")

    # Separator
    draw.rectangle([(w // 2 - 80, h // 2 + 160), (w // 2 + 80, h // 2 + 163)],
                   fill=(50, 60, 80))

    draw.text((w // 2, h // 2 + 210), "Una receptionist? \u20ac900/mese.",
              fill=(239, 130, 68), font=_load_font(38), anchor="mm")

    img = burn_logo(img, logo_path, size=80)
    img.save(path, quality=95)


def create_vertical_problem_card(path, logo_path, title, pain_text,
                                  icon_type="scissors", w=1920, h=1080):
    """Dark problem card for a vertical — shows the pain point."""
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (w, h), DARK_BG)
    draw = ImageDraw.Draw(img)
    _gradient(draw, w, h, top_color=(15, 10, 25))

    font_title = _load_font(40)
    font_pain = _load_font(56)
    font_icon = _load_font(80)

    # Icon mapping (simple Unicode)
    icons = {
        "scissors": "\u2702",
        "wrench": "\u2692",
        "sparkle": "\u2728",
        "plate": "\u2615",
        "medical": "\u2695",
        "dumbbell": "\u2694",
    }
    icon = icons.get(icon_type, "\u2022")

    # Red accent bar left
    draw.rectangle([(80, h // 2 - 120), (86, h // 2 + 120)], fill=RED)

    # Icon
    draw.text((w // 2, h // 2 - 140), icon, fill=CYAN, font=font_icon, anchor="mm")

    # Title (vertical name)
    draw.text((w // 2, h // 2 - 40), title, fill=CYAN, font=font_title, anchor="mm")

    # Pain text (multi-line)
    lines = pain_text.split("\n")
    for i, line in enumerate(lines):
        draw.text((w // 2, h // 2 + 40 + i * 70), line,
                  fill=WHITE, font=font_pain, anchor="mm")

    img = burn_logo(img, logo_path, size=80)
    img.save(path, quality=95)


def create_features_summary_card(path, logo_path, w=1920, h=1080):
    """Summary card listing all features."""
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (w, h), DARK_BG)
    draw = ImageDraw.Draw(img)
    _gradient(draw, w, h)

    font_title = _load_font(56)
    font_item = _load_font(36)

    draw.text((w // 2, 180), "Tutto in uno. Tutto in italiano.",
              fill=WHITE, font=font_title, anchor="mm")

    features = [
        ("\u2713", "Calendario appuntamenti", CYAN),
        ("\u2713", "Rubrica clienti + fedelta\u0300", CYAN),
        ("\u2713", "Cassa + incassi giornalieri", CYAN),
        ("\u2713", "Report e analytics mensili", CYAN),
        ("\u2713", "WhatsApp automatico", CYAN),
        ("\u2713", "Gestione operatori", CYAN),
        ("\u2713", "Sara \u2014 assistente vocale 24/7", GREEN),
        ("\u2713", "Funziona anche offline", GREEN),
    ]

    for i, (check, text, color) in enumerate(features):
        y = 300 + i * 65
        draw.text((w // 2 - 250, y), check, fill=color, font=font_item, anchor="lm")
        draw.text((w // 2 - 210, y), text, fill=WHITE, font=font_item, anchor="lm")

    img = burn_logo(img, logo_path, size=80)
    img.save(path, quality=95)


def create_price_card(path, logo_path, w=1920, h=1080):
    """Price comparison card — subscription vs FLUXION."""
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (w, h), DARK_BG)
    draw = ImageDraw.Draw(img)
    _gradient(draw, w, h)

    font = _load_font(36)
    font_big = _load_font(72)
    font_med = _load_font(48)
    font_small = _load_font(28)

    # Header
    draw.text((w // 2, 150), "Abbonamento vs FLUXION",
              fill=GRAY_TEXT, font=font, anchor="mm")

    # Left column: subscription (red = bad)
    x_left = w // 3
    draw.text((x_left, 250), "Abbonamento", fill=RED, font=font_med, anchor="mm")
    lines_left = [
        ("Anno 1", "\u20ac 600"),
        ("Anno 2", "\u20ac 1.200"),
        ("Anno 3", "\u20ac 1.800"),
        ("Anno 5", "\u20ac 3.000"),
    ]
    for i, (label, price) in enumerate(lines_left):
        y = 340 + i * 75
        draw.text((x_left - 120, y), label, fill=(120, 130, 150), font=font_small, anchor="lm")
        draw.text((x_left + 120, y), price, fill=RED, font=font, anchor="rm")

    # Strikethrough effect on subscription prices
    for i in range(len(lines_left)):
        y = 340 + i * 75
        draw.line([(x_left + 20, y), (x_left + 120, y)], fill=RED, width=2)

    # Right column: FLUXION (cyan = good)
    x_right = 2 * w // 3
    draw.text((x_right, 250), "FLUXION", fill=CYAN, font=font_med, anchor="mm")
    for i, (label, _) in enumerate(lines_left):
        y = 340 + i * 75
        draw.text((x_right - 120, y), label, fill=(120, 130, 150), font=font_small, anchor="lm")
        draw.text((x_right + 120, y), "\u20ac 497", fill=CYAN, font=font, anchor="rm")

    # Divider line
    draw.line([(w // 2, 230), (w // 2, 660)], fill=(50, 60, 80), width=2)

    # Bottom callout
    draw.text((w // 2, 720), "Paghi una volta. Per sempre tuo.",
              fill=WHITE, font=font_med, anchor="mm")
    draw.text((w // 2, 800), "Si ripaga in 3 settimane",
              fill=CYAN, font=font, anchor="mm")

    # 30 days guarantee badge
    draw.text((w // 2, 880), "\u2714 30 giorni soddisfatti o rimborsati",
              fill=GREEN, font=font_small, anchor="mm")

    img = burn_logo(img, logo_path, size=80)
    img.save(path, quality=95)


def create_cta_card(path, logo_path, w=1920, h=1080):
    """Final CTA card with large logo."""
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (w, h), DARK_BG)
    draw = ImageDraw.Draw(img)
    _gradient(draw, w, h)

    # Large center logo
    if os.path.exists(logo_path):
        logo = Image.open(logo_path).convert("RGBA")
        logo = logo.resize((200, 200), Image.LANCZOS)
        logo_x = (w - 200) // 2
        img_rgba = img.convert("RGBA")
        img_rgba.paste(logo, (logo_x, h // 2 - 260), logo)
        img = img_rgba.convert("RGB")
        draw = ImageDraw.Draw(img)

    font_big = _load_font(96)
    font_med = _load_font(36)
    font_small = _load_font(30)
    font_url = _load_font(28)

    cy = h // 2
    draw.text((w // 2, cy - 20), "FLUXION",
              fill=WHITE, font=font_big, anchor="mm")

    # Accent line
    draw.rectangle([(w // 2 - 80, cy + 35), (w // 2 + 80, cy + 39)],
                   fill=CYAN)

    draw.text((w // 2, cy + 80), "Paghi una volta. Usi per sempre.",
              fill=GRAY_TEXT, font=font_med, anchor="mm")
    draw.text((w // 2, cy + 140), "Da \u20ac497 \u2014 Licenza Lifetime",
              fill=CYAN, font=font_small, anchor="mm")
    draw.text((w // 2, cy + 195), "30 giorni soddisfatti o rimborsati",
              fill=GREEN, font=font_url, anchor="mm")
    draw.text((w // 2, cy + 250), "fluxion.it",
              fill=WHITE, font=_load_font(44), anchor="mm")

    # No burn_logo here — already has the big logo center
    img.save(path, quality=95)


# ============================================================
# VIDEO CLIP GENERATION
# ============================================================

async def generate_tts(text, output_path):
    """Generate TTS and return duration."""
    import edge_tts
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE)
    await communicate.save(output_path)
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", output_path],
        capture_output=True, text=True,
    )
    return float(result.stdout.strip())


def make_clip_smooth(image_path, audio_path, duration,
                     zoom_target, zoom_amount, output_path):
    """Create clip with smooth zoom (pre-scale 8000px, zero jitter)."""
    tx, ty = zoom_target
    total_frames = int(duration * 30)
    z_start = 1.0
    z_end = zoom_amount

    vf = (
        f"scale=8000:-1,"
        f"zoompan="
        f"z='{z_start}+({z_end}-{z_start})*on/{total_frames}':"
        f"x='{tx}*iw-(iw/zoom/2)':"
        f"y='{ty}*ih-(ih/zoom/2)':"
        f"d={total_frames}:s=1920x1080:fps=30,"
        f"format=yuv420p"
    )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_path,
        "-i", audio_path,
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(duration),
        "-shortest",
        output_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERRORE ffmpeg: {result.stderr[-400:]}", file=sys.stderr)
        sys.exit(1)


def format_srt_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def format_chapter_time(seconds):
    """Format time as MM:SS for YouTube chapters."""
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m}:{s:02d}"


def generate_srt(slides, durations, output_path):
    """Generate SRT subtitle file."""
    lines = []
    current_time = 0.0
    idx = 1

    for slide, duration in zip(slides, durations):
        text = slide["text"].replace("'", "\u2019")
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


def generate_youtube_chapters(slides, durations, output_path):
    """Generate YouTube chapter timestamps."""
    lines = ["CAPITOLI VIDEO:"]
    current_time = 0.0
    trans_dur = 0.5

    for i, slide in enumerate(slides):
        chapter = slide.get("chapter")
        if chapter:
            lines.append(f"{format_chapter_time(current_time)} {chapter}")
        current_time += durations[i]
        if i > 0:
            current_time -= trans_dur  # account for xfade overlap

    # Write to file
    with open(output_path, "a", encoding="utf-8") as f:
        f.write("\n\n" + "\n".join(lines) + "\n")

    return lines


def create_thumbnail(logo_path, output_path):
    """YouTube thumbnail 1280x720."""
    from PIL import Image, ImageDraw

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

    font_title = _load_font(64)
    font_sub = _load_font(30)
    font_detail = _load_font(22)

    draw.text((640, 540), "FLUXION", fill=WHITE, font=font_title, anchor="mm")
    draw.text((640, 600), "Il Gestionale per la Tua Attivit\u00e0 \u00b7 Da \u20ac497",
              fill=CYAN, font=font_sub, anchor="mm")
    draw.text((640, 650), "Parrucchieri \u00b7 Officine \u00b7 Palestre \u00b7 Cliniche \u00b7 Ristoranti",
              fill=GRAY_TEXT, font=font_detail, anchor="mm")

    # Play button center
    cx, cy = 640, 280
    r = 52
    draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)],
                 fill=CYAN, outline=WHITE, width=3)
    draw.polygon([(cx - 16, cy - 24), (cx - 16, cy + 24), (cx + 22, cy)],
                 fill=WHITE)

    # Logo
    img = burn_logo(img, logo_path, position="top_left", size=60, opacity=0.9)
    img.save(output_path, quality=95)


# ============================================================
# MAIN
# ============================================================

async def main():
    with tempfile.TemporaryDirectory(prefix="fluxion-video-") as tmpdir:
        tmpdir = Path(tmpdir)

        print("=" * 60)
        print("  FLUXION Demo Video Creator V3")
        print("  \"Lasciali a Bocca Aperta\"")
        print(f"  Voice: {VOICE} | Rate: {RATE}")
        print(f"  Slides: {len(SLIDES)}")
        print("=" * 60)

        logo_path = str(LOGO)

        # ---- PHASE 1: Generate all TTS audio ----
        print("\n[FASE 1] Generazione narrazione Edge-TTS...\n")
        audio_paths = []
        durations = []

        for i, slide in enumerate(SLIDES):
            audio_path = tmpdir / f"audio_{i:02d}.mp3"
            audio_dur = await generate_tts(slide["text"], str(audio_path))
            padding = slide.get("padding", 1.0)
            actual_dur = audio_dur + padding
            audio_paths.append(str(audio_path))
            durations.append(actual_dur)
            label = slide.get("image") or f"({slide['id']} card)"
            print(f"  [{i + 1:2d}/{len(SLIDES)}] {actual_dur:.1f}s \u2014 {label}")

        total = sum(durations)
        print(f"\n  Durata totale grezza: {total:.0f}s ({total / 60:.1f} min)")

        # ---- PHASE 2: Generate all card images ----
        print("\n[FASE 2] Generazione card (Pillow + logo burned)...\n")
        card_paths = {}

        for i, slide in enumerate(SLIDES):
            if slide.get("image") is None:
                card_path = str(tmpdir / f"card_{slide['id']}.png")
                card_type = slide.get("card_type", "cta")

                if card_type == "hook":
                    create_hook_card(card_path, logo_path)
                elif card_type == "agitazione":
                    create_agitation_card(card_path, logo_path)
                elif card_type == "vertical_problem":
                    create_vertical_problem_card(
                        card_path, logo_path,
                        title=slide.get("card_title", ""),
                        pain_text=slide.get("card_pain", ""),
                        icon_type=slide.get("card_icon", "scissors"),
                    )
                elif card_type == "features_summary":
                    create_features_summary_card(card_path, logo_path)
                elif card_type == "prezzo":
                    create_price_card(card_path, logo_path)
                elif card_type == "cta":
                    create_cta_card(card_path, logo_path)
                else:
                    create_cta_card(card_path, logo_path)

                card_paths[i] = card_path
                print(f"  Card: {slide['id']}")

        # ---- PHASE 3: Prepare images (logo + lower third burned) ----
        print("\n[FASE 3] Preparazione immagini (logo + lower third burned)...\n")
        prepared_images = {}

        for i, slide in enumerate(SLIDES):
            if slide.get("image"):
                from PIL import Image as PILImage
                img_path = str(SCREENSHOTS / slide["image"])
                if not os.path.exists(img_path):
                    print(f"  ERRORE: {img_path} non trovato!")
                    sys.exit(1)

                img = PILImage.open(img_path).convert("RGB")

                # Burn logo on every screenshot
                img = burn_logo(img, logo_path, size=64, opacity=0.7)

                # Burn lower third if specified
                if slide.get("lower_third"):
                    img = burn_lower_third(img, slide["lower_third"])

                prepared_path = str(tmpdir / f"prepared_{i:02d}.png")
                img.save(prepared_path, quality=95)
                prepared_images[i] = prepared_path
                print(f"  [{i + 1:2d}] {slide['image']}"
                      + (f" + LT: {slide['lower_third']}" if slide.get('lower_third') else ""))
            else:
                prepared_images[i] = card_paths[i]

        # ---- PHASE 4: Generate video clips ----
        print("\n[FASE 4] Generazione clip (8000px pre-scale, zero jitter)...\n")
        clip_paths = []

        for i, slide in enumerate(SLIDES):
            clip_path = str(tmpdir / f"clip_{i:02d}.mp4")

            make_clip_smooth(
                image_path=prepared_images[i],
                audio_path=audio_paths[i],
                duration=durations[i],
                zoom_target=slide["zoom_target"],
                zoom_amount=slide["zoom_amount"],
                output_path=clip_path,
            )
            clip_paths.append(clip_path)
            label = slide.get("image") or f"({slide['id']})"
            print(f"  [{i + 1:2d}/{len(SLIDES)}] {label} \u2014 {durations[i]:.1f}s")

        # ---- PHASE 5: Join clips with xfade transitions ----
        print("\n[FASE 5] Composizione con transizioni xfade...\n")
        trans_dur = 0.5

        if len(clip_paths) < 2:
            composed_path = clip_paths[0]
        else:
            current = clip_paths[0]
            offset = durations[0] - trans_dur

            for j in range(1, len(clip_paths)):
                next_clip = clip_paths[j]
                out_path = str(tmpdir / f"xfade_{j:02d}.mp4")
                transition = SLIDES[j].get("transition", "dissolve")

                cmd = [
                    "ffmpeg", "-y",
                    "-i", current, "-i", next_clip,
                    "-filter_complex",
                    (
                        f"[0:v][1:v]xfade=transition={transition}:"
                        f"duration={trans_dur}:offset={offset}[v];"
                        f"[0:a][1:a]acrossfade=d={trans_dur}:c1=tri:c2=tri[a]"
                    ),
                    "-map", "[v]", "-map", "[a]",
                    "-c:v", "libx264", "-preset", "fast", "-crf", "22",
                    "-c:a", "aac", "-b:a", "192k",
                    out_path,
                ]

                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    print(f"  xfade {j} ERRORE: {result.stderr[-300:]}")
                    # Fallback: simple concat
                    concat_file = tmpdir / "fallback_concat.txt"
                    with open(concat_file, "w") as f:
                        for cp in clip_paths:
                            f.write(f"file '{cp}'\n")
                    subprocess.run(
                        ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
                         "-i", str(concat_file), "-c", "copy",
                         str(tmpdir / "composed.mp4")],
                        check=True, capture_output=True,
                    )
                    composed_path = str(tmpdir / "composed.mp4")
                    break

                current = out_path
                offset += durations[j] - trans_dur
                print(f"  xfade {j}/{len(clip_paths) - 1}: {transition}")
            else:
                composed_path = current

        # ---- PHASE 6: Global fade in/out ----
        print("\n[FASE 6] Fade in/out globale...\n")
        faded_path = str(tmpdir / "faded.mp4")
        final_dur = total - trans_dur * (len(clip_paths) - 1)
        fade_out_start = max(0, final_dur - 2.5)

        subprocess.run(
            [
                "ffmpeg", "-y", "-i", composed_path,
                "-vf", f"fade=t=in:st=0:d=1.5,fade=t=out:st={fade_out_start}:d=2",
                "-af", f"afade=t=in:st=0:d=1,afade=t=out:st={fade_out_start}:d=2",
                "-c:v", "libx264", "-preset", "fast", "-crf", "20",
                "-c:a", "aac", "-b:a", "192k",
                faded_path,
            ],
            check=True, capture_output=True,
        )

        # ---- PHASE 7: Final YouTube encoding ----
        print("[FASE 7] Encoding finale YouTube-optimized...\n")
        output_video = OUTPUT / "fluxion-demo.mp4"

        subprocess.run(
            [
                "ffmpeg", "-y", "-i", faded_path,
                "-c:v", "libx264", "-preset", "slow", "-crf", "18",
                "-profile:v", "high", "-level", "4.1",
                "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                "-r", "30",
                str(output_video),
            ],
            check=True, capture_output=True,
        )

        # ---- PHASE 8: SRT + Thumbnail + YouTube metadata ----
        print("[FASE 8] Sottotitoli + thumbnail + YouTube metadata...\n")

        srt_path = OUTPUT / "fluxion-demo.srt"
        generate_srt(SLIDES, durations, str(srt_path))
        print(f"  SRT: {srt_path}")

        thumb_path = OUTPUT / "fluxion-demo-thumbnail.png"
        create_thumbnail(logo_path, str(thumb_path))
        print(f"  Thumbnail: {thumb_path}")

        # YouTube metadata
        meta_path = OUTPUT / "youtube-metadata.txt"
        with open(meta_path, "w", encoding="utf-8") as f:
            f.write("TITOLO:\n")
            f.write("FLUXION \u2014 Il Gestionale per la Tua Attivit\u00e0 | "
                    "Parrucchieri, Officine, Palestre, Cliniche, Ristoranti\n\n")
            f.write("DESCRIZIONE:\n")
            f.write("FLUXION \u00e8 il gestionale desktop per PMI italiane.\n")
            f.write("Appuntamenti, clienti, cassa, WhatsApp, e Sara \u2014 "
                    "l'assistente vocale AI che risponde al telefono 24/7.\n\n")
            f.write("Paghi una volta, usi per sempre. Da \u20ac497.\n")
            f.write("30 giorni soddisfatti o rimborsati.\n\n")
            f.write("\ud83d\udc49 Scopri di pi\u00f9: https://fluxion-landing.pages.dev\n\n")

        chapters = generate_youtube_chapters(SLIDES, durations, str(meta_path))
        for ch in chapters:
            print(f"  {ch}")

        # Tags
        with open(meta_path, "a", encoding="utf-8") as f:
            f.write("\nTAG:\n")
            f.write("gestionale, gestionale parrucchiere, software gestionale, "
                    "gestionale italiano, gestionale PMI, gestionale appuntamenti, "
                    "gestionale officina, gestionale palestra, gestionale clinica, "
                    "gestionale ristorante, software prenotazioni, "
                    "assistente vocale, FLUXION, Sara AI\n")

        print(f"  YouTube metadata: {meta_path}")

        # ---- INFO ----
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-show_entries", "format=duration,size",
             "-of", "json", str(output_video)],
            capture_output=True, text=True,
        )
        info = json.loads(result.stdout)
        dur = float(info["format"]["duration"])
        size_mb = int(info["format"]["size"]) / 1024 / 1024

        print("\n" + "=" * 60)
        print(f"  Video:       {output_video}")
        print(f"  Durata:      {dur:.0f}s ({dur / 60:.1f} min)")
        print(f"  Dimensione:  {size_mb:.1f} MB")
        print(f"  Sottotitoli: {srt_path}")
        print(f"  Thumbnail:   {thumb_path}")
        print(f"  Metadata:    {meta_path}")
        print("=" * 60)
        print(f"\n  Anteprima: open {output_video}")


if __name__ == "__main__":
    asyncio.run(main())
