"""FLUXION Sales Agent WA — Configuration."""
from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "leads.db"
WA_SESSION_DIR = BASE_DIR / "wa_session"
LOG_DIR = BASE_DIR / "logs"

# Google Places API key — FREE tier: 28.500 call/mese
# GCP credits esauriti — questo source sara' skippato se non configurato
GOOGLE_PLACES_API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY", "")

# YouTube links per categoria (inserire URL reali dopo upload)
YOUTUBE_LINKS = {
    "parrucchiere": "https://www.youtube.com/watch?v=PLACEHOLDER_PARRUCCHIERE",
    "officina":     "https://www.youtube.com/watch?v=PLACEHOLDER_OFFICINA",
    "estetico":     "https://www.youtube.com/watch?v=PLACEHOLDER_ESTETICO",
    "palestra":     "https://www.youtube.com/watch?v=PLACEHOLDER_PALESTRA",
    "dentista":     "https://www.youtube.com/watch?v=PLACEHOLDER_DENTISTA",
    "generico":     "https://www.youtube.com/watch?v=PLACEHOLDER_GENERICO",
}

LANDING_URL = "https://fluxion-landing.pages.dev"

# Rate limiting — warm-up schedule
# Settimana 1-2: 5/giorno, Settimana 3-4: 10/giorno, Settimana 5+: 20-30/giorno
WARMUP_SCHEDULE = {
    1: 5,
    2: 5,
    3: 10,
    4: 10,
    5: 20,
    6: 25,
}
DEFAULT_DAILY_LIMIT = 20

# Orari operativi (lun-ven, ora italiana)
BUSINESS_HOURS = {
    "morning_start": 9,
    "morning_end":   12,
    "afternoon_start": 14,
    "afternoon_end":   17,
}

# Delay tra messaggi in secondi (distribuzione gaussiana)
DELAY_MEAN_S = 120      # 2 minuti media
DELAY_STD_S  = 30       # +/- 30 secondi deviazione standard
DELAY_MIN_S  = 60       # mai meno di 60 secondi
DELAY_MAX_S  = 300      # mai piu' di 5 minuti

# Pausa lunga ogni N messaggi
LONG_PAUSE_EVERY = 5
LONG_PAUSE_MIN_S = 300   # 5 minuti
LONG_PAUSE_MAX_S = 600   # 10 minuti

# User agent rotation per scraper
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
]

DASHBOARD_PORT = 5050
DASHBOARD_HOST = "127.0.0.1"
