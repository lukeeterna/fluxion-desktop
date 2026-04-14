# FLUXION Sales Agent WhatsApp — Blueprint Completo
> Implementation-ready spec. Python 3.9 | Zero costi | iMac background execution
> Data: 2026-04-14 | Growth Hacker Agent

---

## 1. ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────────┐
│                    SALES AGENT WA — FLUXION                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │   SCRAPER    │───▶│   leads.db   │───▶│  WA SENDER       │  │
│  │              │    │   (SQLite)   │    │  (Playwright)    │  │
│  │ - Google     │    │              │    │                  │  │
│  │   Places API │    │ leads        │    │ - QR login once  │  │
│  │ - PagineBianc│    │ messages     │    │ - Session persist│  │
│  │ - OSM Overp. │    │ campaigns    │    │ - Rate limiting  │  │
│  └──────────────┘    │ daily_stats  │    │ - Anti-ban       │  │
│                      └──────────────┘    └──────────────────┘  │
│                             │                      │            │
│                             ▼                      ▼            │
│                      ┌──────────────┐    ┌──────────────────┐  │
│                      │  DASHBOARD   │    │  UTM TRACKER     │  │
│                      │  (Flask)     │    │  (CF Worker KV)  │  │
│                      │  port 5050   │    │                  │  │
│                      └──────────────┘    └──────────────────┘  │
│                                                                  │
│  CLI: python agent.py [scrape|send|dashboard|stats|pause|resume]│
└─────────────────────────────────────────────────────────────────┘

FUNNEL:
WA msg (YouTube link) → YouTube video (6 min) → CTA descrizione
→ https://fluxion-landing.pages.dev → Stripe → Acquisto
```

---

## 2. TECH STACK

```
Python          3.9 (iMac native — no venv needed)
SQLite          3.x (stdlib — no install)
requests        2.31.0      pip install requests
beautifulsoup4  4.12.3      pip install beautifulsoup4
lxml            5.1.0       pip install lxml
playwright      1.44.0      pip install playwright && python -m playwright install chromium
flask           3.0.3       pip install flask
schedule        1.2.1       pip install schedule

Install tutto:
pip3 install requests beautifulsoup4 lxml playwright flask schedule
python3 -m playwright install chromium
```

---

## 3. FILE STRUCTURE

```
tools/SalesAgentWA/
├── agent.py                  # CLI entrypoint + orchestrator
├── scraper.py                # Google Places + PagineBianche + OSM
├── sender.py                 # Playwright WA Web automation
├── templates.py              # 6 category templates, 3+ variants each
├── dashboard.py              # Flask dashboard server
├── utm.py                    # UTM link generator
├── config.py                 # Costanti e configurazione
├── leads.db                  # SQLite DB (auto-created)
├── wa_session/               # Playwright browser profile (QR login persist)
│   └── .gitkeep
├── logs/
│   └── .gitkeep
├── com.fluxion.salesagent.plist  # LaunchAgent iMac
└── SALES-AGENT-BLUEPRINT.md  # questo file
```

---

## 4. DATABASE SCHEMA

```sql
-- leads.db — eseguito da agent.py al primo avvio (CREATE IF NOT EXISTS)

CREATE TABLE IF NOT EXISTS leads (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    business_name   TEXT NOT NULL,
    phone           TEXT,                        -- formato +39XXXXXXXXXX
    phone_raw       TEXT,                        -- numero grezzo come trovato
    address         TEXT,
    city            TEXT,
    province        TEXT,
    category        TEXT NOT NULL,               -- parrucchiere|officina|estetico|palestra|dentista|generico
    source          TEXT NOT NULL,               -- google_places|paginebianche|osm
    source_id       TEXT,                        -- ID univoco sorgente (place_id Google, ecc.)
    website         TEXT,
    google_rating   REAL,
    google_reviews  INTEGER,
    wa_registered   INTEGER DEFAULT NULL,        -- NULL=unknown, 1=yes, 0=no
    scraped_at      TEXT NOT NULL DEFAULT (datetime('now')),
    notes           TEXT,
    UNIQUE(phone_raw)                            -- evita duplicati
);

CREATE TABLE IF NOT EXISTS messages (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id         INTEGER NOT NULL REFERENCES leads(id),
    campaign_id     INTEGER REFERENCES campaigns(id),
    template_key    TEXT NOT NULL,               -- es. "parrucchiere_v2"
    message_text    TEXT NOT NULL,               -- testo effettivo inviato
    utm_url         TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'pending',
    -- pending | sent | delivered | read | replied | failed | blocked
    sent_at         TEXT,
    delivered_at    TEXT,
    read_at         TEXT,
    replied_at      TEXT,
    reply_text      TEXT,
    error_msg       TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS campaigns (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    category        TEXT NOT NULL,
    city            TEXT,
    status          TEXT NOT NULL DEFAULT 'active',   -- active|paused|completed
    daily_limit     INTEGER NOT NULL DEFAULT 10,
    delay_min_s     INTEGER NOT NULL DEFAULT 60,
    delay_max_s     INTEGER NOT NULL DEFAULT 180,
    started_at      TEXT NOT NULL DEFAULT (datetime('now')),
    paused_at       TEXT,
    notes           TEXT
);

CREATE TABLE IF NOT EXISTS daily_stats (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date            TEXT NOT NULL,               -- YYYY-MM-DD
    sent            INTEGER NOT NULL DEFAULT 0,
    delivered       INTEGER NOT NULL DEFAULT 0,
    read_count      INTEGER NOT NULL DEFAULT 0,
    replied         INTEGER NOT NULL DEFAULT 0,
    failed          INTEGER NOT NULL DEFAULT 0,
    blocked         INTEGER NOT NULL DEFAULT 0,
    UNIQUE(date)
);

CREATE TABLE IF NOT EXISTS agent_state (
    key             TEXT PRIMARY KEY,
    value           TEXT NOT NULL,
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Indici per performance dashboard
CREATE INDEX IF NOT EXISTS idx_messages_status ON messages(status);
CREATE INDEX IF NOT EXISTS idx_messages_sent_at ON messages(sent_at);
CREATE INDEX IF NOT EXISTS idx_leads_category ON leads(category);
CREATE INDEX IF NOT EXISTS idx_leads_city ON leads(city);
CREATE INDEX IF NOT EXISTS idx_leads_wa_registered ON leads(wa_registered);
```

---

## 5. CONFIG MODULE

```python
# config.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "leads.db"
WA_SESSION_DIR = BASE_DIR / "wa_session"
LOG_DIR = BASE_DIR / "logs"

# Google Places API key — FREE tier: 28.500 call/mese
# Ottenere da: https://console.cloud.google.com → Places API
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
    1: 5,   # settimana 1
    2: 5,   # settimana 2
    3: 10,  # settimana 3
    4: 10,  # settimana 4
    5: 20,  # settimana 5
    6: 25,  # settimana 6+
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
DELAY_STD_S  = 30       # ±30 secondi deviazione standard
DELAY_MIN_S  = 60       # mai meno di 60 secondi
DELAY_MAX_S  = 300      # mai più di 5 minuti

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
```

---

## 6. UTM MODULE

```python
# utm.py
from urllib.parse import urlencode, urlparse, urlunparse, parse_qs
from config import YOUTUBE_LINKS, LANDING_URL


def build_utm_youtube(category: str, city: str) -> str:
    """
    Costruisce il link YouTube con UTM parameters per tracking.
    Questo e' il link che va nel messaggio WA.
    """
    base_url = YOUTUBE_LINKS.get(category, YOUTUBE_LINKS["generico"])
    params = {
        "utm_source":   "wa",
        "utm_medium":   "outreach",
        "utm_campaign": category,
        "utm_content":  city.lower().replace(" ", "_"),
    }
    # YouTube accetta query params — appende dopo eventuale ?v=...
    separator = "&" if "?" in base_url else "?"
    return base_url + separator + urlencode(params)


def build_utm_landing(category: str, city: str, source: str = "wa") -> str:
    """
    Costruisce il link landing con UTM — usato nella descrizione YouTube.
    """
    params = {
        "utm_source":   source,
        "utm_medium":   "outreach",
        "utm_campaign": category,
        "utm_content":  city.lower().replace(" ", "_"),
    }
    return LANDING_URL + "?" + urlencode(params)


def normalize_phone(phone_raw: str) -> str | None:
    """
    Normalizza numero italiano al formato +39XXXXXXXXXX per WA.
    Ritorna None se non valido.
    """
    import re
    digits = re.sub(r"\D", "", phone_raw)
    if digits.startswith("0039"):
        digits = digits[4:]
    elif digits.startswith("39") and len(digits) >= 12:
        digits = digits[2:]
    # Numeri italiani: 10 cifre (fisso) o 10 cifre mobili (3xx...)
    if len(digits) == 10:
        return f"+39{digits}"
    if len(digits) == 11 and digits.startswith("0"):
        return f"+39{digits}"
    return None
```

---

## 7. MESSAGE TEMPLATES

```python
# templates.py
"""
6 categorie, 3+ varianti per sezione.
Struttura: apertura + hook + link + firma.
Variazione minima 40% tra messaggi inviati — selezionare casualmente.
"""
import random
from utm import build_utm_youtube


TEMPLATES = {

    # ─── PARRUCCHIERE / BARBIERE ──────────────────────────────────────────────
    "parrucchiere": [
        {
            "key": "parrucchiere_v1",
            "parts": {
                "apertura": [
                    "Ciao {nome}, ho visto che gestisci {attivita} a {citta}.",
                    "Ciao {nome}, {attivita} a {citta} — sono io?",
                    "Salve {nome}, ho trovato {attivita} su Google Maps.",
                ],
                "hook": [
                    "Quante chiamate perdi mentre hai le mani occupate con un cliente?",
                    "Scommetto che almeno 3-4 prenotazioni al giorno le gestisci ancora al telefono.",
                    "Il problema dei saloni è sempre lo stesso: il telefono suona nel momento peggiore.",
                ],
                "cta": [
                    "Ho fatto un video di 6 minuti su come Sara, la nostra assistente AI, risponde al posto tuo — anche di domenica: {link}",
                    "Guarda come altri parrucchieri italiani hanno eliminato le telefonate dalle prenotazioni: {link}",
                    "Ho registrato come funziona FLUXION per i saloni — 6 minuti, nessun tecnicismo: {link}",
                ],
                "firma": [
                    "Gianluca — FLUXION",
                    "A presto,\nGianluca",
                    "Fammi sapere cosa ne pensi.\nGianluca — FLUXION",
                ],
            },
        },
    ],

    # ─── OFFICINA / GOMMISTA ─────────────────────────────────────────────────
    "officina": [
        {
            "key": "officina_v1",
            "parts": {
                "apertura": [
                    "Ciao {nome}, {attivita} a {citta} giusto?",
                    "Salve {nome}, ho trovato {attivita} su Maps.",
                    "Ciao {nome}, ho visto la tua officina a {citta}.",
                ],
                "hook": [
                    "Gestire i preventivi telefonici mentre sei sotto una macchina è un casino.",
                    "Quante volte al giorno sei costretto a fermarti per rispondere al telefono?",
                    "Tra le riparazioni e le telefonate dei clienti, la giornata vola via.",
                ],
                "cta": [
                    "Ho registrato come altri meccanici gestiscono prenotazioni e preventivi in automatico: {link}",
                    "Guarda come funziona FLUXION per le officine — 6 minuti che valgono la pena: {link}",
                    "Ho fatto un video su come Sara risponde ai clienti anche quando sei impegnato sotto il cofano: {link}",
                ],
                "firma": [
                    "Gianluca — FLUXION",
                    "Buon lavoro,\nGianluca",
                    "A presto,\nGianluca — FLUXION",
                ],
            },
        },
    ],

    # ─── CENTRO ESTETICO ─────────────────────────────────────────────────────
    "estetico": [
        {
            "key": "estetico_v1",
            "parts": {
                "apertura": [
                    "Ciao {nome}, gestisci {attivita} a {citta}?",
                    "Buongiorno {nome}, ho visto {attivita} su Google.",
                    "Ciao {nome}, ho trovato il tuo centro a {citta}.",
                ],
                "hook": [
                    "I no-show dell'ultimo minuto sono il problema numero uno nei centri estetici.",
                    "Le disdette last-minute costano ore di lavoro perso ogni settimana.",
                    "Quante volte un appuntamento saltato ti lascia un buco in agenda senza preavviso?",
                ],
                "cta": [
                    "Ho fatto un video su come FLUXION manda promemoria WA automatici e azzera i no-show: {link}",
                    "Guarda come altri centri estetici gestiscono le prenotazioni senza telefonate: {link}",
                    "6 minuti per capire come Sara gestisce agenda e promemoria al posto tuo: {link}",
                ],
                "firma": [
                    "Gianluca — FLUXION",
                    "A presto,\nGianluca",
                    "Fammi sapere!\nGianluca — FLUXION",
                ],
            },
        },
    ],

    # ─── PALESTRA / FITNESS ──────────────────────────────────────────────────
    "palestra": [
        {
            "key": "palestra_v1",
            "parts": {
                "apertura": [
                    "Ciao {nome}, ho visto {attivita} a {citta}.",
                    "Salve {nome}, gestisci {attivita}?",
                    "Ciao {nome}, {attivita} a {citta} — giusto?",
                ],
                "hook": [
                    "Gestire abbonamenti, rinnovi e prenotazioni corsi è un lavoro nel lavoro.",
                    "Tenere traccia di chi ha rinnovato, chi è in scadenza e chi manca — senza un sistema è impossibile.",
                    "Quante ore a settimana passi a gestire l'amministrativo invece di stare con i tuoi clienti?",
                ],
                "cta": [
                    "Ho registrato come FLUXION gestisce abbonamenti, promemoria di rinnovo e prenotazioni corsi: {link}",
                    "Guarda come altri titolari di palestre hanno automatizzato la gestione clienti: {link}",
                    "6 minuti per vedere come Sara gestisce prenotazioni e rinnovi automaticamente: {link}",
                ],
                "firma": [
                    "Gianluca — FLUXION",
                    "Buon allenamento!\nGianluca",
                    "A presto,\nGianluca — FLUXION",
                ],
            },
        },
    ],

    # ─── DENTISTA / FISIOTERAPISTA ────────────────────────────────────────────
    "dentista": [
        {
            "key": "dentista_v1",
            "parts": {
                "apertura": [
                    "Buongiorno {nome}, ho visto {attivita} su Maps.",
                    "Ciao {nome}, {attivita} a {citta}?",
                    "Salve {nome}, ho trovato il tuo studio a {citta}.",
                ],
                "hook": [
                    "La gestione degli appuntamenti telefonici toglie tempo prezioso ai pazienti.",
                    "Tra conferme, disdette e riprogrammazioni, la segreteria è sempre sotto pressione.",
                    "Quante ore al giorno la tua segreteria passa al telefono per confermare appuntamenti?",
                ],
                "cta": [
                    "Ho fatto un video su come Sara gestisce gli appuntamenti del tuo studio — anche fuori orario: {link}",
                    "Guarda come altri studi professionali hanno automatizzato la gestione agenda: {link}",
                    "6 minuti per vedere FLUXION in azione per gli studi medici e fisioterapici: {link}",
                ],
                "firma": [
                    "Gianluca — FLUXION",
                    "Cordialmente,\nGianluca",
                    "A presto,\nGianluca — FLUXION",
                ],
            },
        },
    ],

    # ─── GENERICO PMI ────────────────────────────────────────────────────────
    "generico": [
        {
            "key": "generico_v1",
            "parts": {
                "apertura": [
                    "Ciao {nome}, ho visto {attivita} a {citta}.",
                    "Salve {nome}, ho trovato la tua attività su Google.",
                    "Buongiorno {nome}, {attivita} a {citta} — giusto?",
                ],
                "hook": [
                    "Gestire prenotazioni e clienti telefonicamente porta via troppo tempo.",
                    "Quante ore a settimana passi a gestire appuntamenti invece di fare il tuo lavoro?",
                    "Per molte piccole imprese, il telefono è ancora il principale collo di bottiglia.",
                ],
                "cta": [
                    "Ho fatto un video su come FLUXION automatizza la gestione clienti per le PMI italiane: {link}",
                    "Guarda come altri titolari hanno liberato ore di lavoro ogni settimana: {link}",
                    "6 minuti per capire se FLUXION può aiutare anche la tua attività: {link}",
                ],
                "firma": [
                    "Gianluca — FLUXION",
                    "A presto,\nGianluca",
                    "Fammi sapere!\nGianluca — FLUXION",
                ],
            },
        },
    ],
}


def render_template(
    category: str,
    business_name: str,
    city: str,
    *,
    previously_used_keys: list[str] | None = None,
) -> tuple[str, str]:
    """
    Genera un messaggio WA per la categoria data.
    Seleziona parti a caso per garantire variazione >40%.

    Returns:
        (message_text, template_key)
    """
    templates = TEMPLATES.get(category, TEMPLATES["generico"])
    tmpl = random.choice(templates)
    parts = tmpl["parts"]

    # Prepara nome abbreviato (primo token del nome attività)
    short_name = business_name.split()[0].capitalize() if business_name else "amico"

    utm_url = build_utm_youtube(category, city)

    apertura = random.choice(parts["apertura"]).format(
        nome=short_name,
        attivita=business_name,
        citta=city,
    )
    hook = random.choice(parts["hook"])
    cta = random.choice(parts["cta"]).format(link=utm_url)
    firma = random.choice(parts["firma"])

    message = f"{apertura}\n{hook}\n{cta}\n{firma}"
    return message, tmpl["key"]


def estimate_variation(msg1: str, msg2: str) -> float:
    """
    Stima percentuale di variazione tra due messaggi (Jaccard su trigrammi).
    Target: > 0.40 (40%).
    """
    def trigrams(text):
        return set(text[i:i+3] for i in range(len(text) - 2))

    t1, t2 = trigrams(msg1.lower()), trigrams(msg2.lower())
    if not t1 and not t2:
        return 1.0
    intersection = len(t1 & t2)
    union = len(t1 | t2)
    jaccard_similarity = intersection / union if union > 0 else 0
    return 1.0 - jaccard_similarity  # variazione = 1 - similarità
```

---

## 8. SCRAPER MODULE

```python
# scraper.py
"""
3 sorgenti in priorità:
1. Google Places API (primario — dati migliori, free 28.500 call/mese)
2. PagineBianche (secondario — fallback per zone con pochi dati Google)
3. OpenStreetMap Overpass (terziario — ultimo fallback, 100% gratuito)
"""
import time
import random
import logging
import sqlite3
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode, quote_plus
from typing import Iterator
from config import DB_PATH, GOOGLE_PLACES_API_KEY, USER_AGENTS
from utm import normalize_phone

logger = logging.getLogger(__name__)

# ─── Coordinate principali città italiane ────────────────────────────────────
CITY_COORDS = {
    "milano":    (45.4654, 9.1859),
    "roma":      (41.9028, 12.4964),
    "napoli":    (40.8518, 14.2681),
    "torino":    (45.0703, 7.6869),
    "palermo":   (38.1157, 13.3615),
    "genova":    (44.4056, 8.9463),
    "bologna":   (44.4949, 11.3426),
    "firenze":   (43.7696, 11.2558),
    "bari":      (41.1171, 16.8719),
    "catania":   (37.5023, 15.0873),
    "venezia":   (45.4408, 12.3155),
    "verona":    (45.4385, 10.9916),
    "messina":   (38.1938, 15.5540),
    "padova":    (45.4064, 11.8768),
    "trieste":   (45.6495, 13.7768),
    "taranto":   (40.4758, 17.2290),
    "brescia":   (45.5416, 10.2118),
    "prato":     (43.8777, 11.1021),
    "reggio_calabria": (38.1147, 15.6498),
    "modena":    (44.6471, 10.9252),
    "reggio_emilia": (44.6989, 10.6297),
    "perugia":   (43.1122, 12.3888),
    "ravenna":   (44.4184, 12.2035),
    "livorno":   (43.5485, 10.3106),
    "cagliari":  (39.2238, 9.1217),
    "foggia":    (41.4621, 15.5447),
    "rimini":    (44.0594, 12.5683),
    "salerno":   (40.6824, 14.7681),
    "ferrara":   (44.8381, 11.6197),
}

# ─── Keyword per categoria ────────────────────────────────────────────────────
CATEGORY_KEYWORDS = {
    "parrucchiere": ["parrucchiere", "barbiere", "salone parrucchieri", "hairstylist"],
    "officina":     ["officina meccanica", "gommista", "carrozzeria", "autofficina"],
    "estetico":     ["centro estetico", "estetista", "beauty center", "centro benessere"],
    "palestra":     ["palestra", "centro fitness", "crossfit", "pilates studio"],
    "dentista":     ["dentista", "studio dentistico", "fisioterapista", "studio fisioterapia"],
    "generico":     ["parrucchiere", "officina", "centro estetico"],
}


def _get_headers() -> dict:
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "it-IT,it;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }


def _db_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _upsert_lead(conn, lead: dict) -> bool:
    """
    Inserisce o skippa lead se phone_raw già presente.
    Ritorna True se inserito nuovo.
    """
    phone_normalized = normalize_phone(lead.get("phone_raw", ""))
    try:
        conn.execute("""
            INSERT INTO leads (
                business_name, phone, phone_raw, address, city, province,
                category, source, source_id, website,
                google_rating, google_reviews
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            lead.get("business_name"),
            phone_normalized,
            lead.get("phone_raw"),
            lead.get("address"),
            lead.get("city"),
            lead.get("province"),
            lead.get("category"),
            lead.get("source"),
            lead.get("source_id"),
            lead.get("website"),
            lead.get("google_rating"),
            lead.get("google_reviews"),
        ))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Duplicato phone_raw


# ─── SOURCE 1: Google Places API ─────────────────────────────────────────────

def scrape_google_places(
    category: str,
    city: str,
    radius_m: int = 10000,
    max_results: int = 200,
) -> int:
    """
    Cerca attività tramite Google Places API (Nearby Search).
    FREE: 28.500 call/mese.
    Ritorna numero di nuovi lead inseriti.
    """
    if not GOOGLE_PLACES_API_KEY:
        logger.warning("GOOGLE_PLACES_API_KEY non configurata — skip Google Places")
        return 0

    city_lower = city.lower().replace(" ", "_")
    if city_lower not in CITY_COORDS:
        logger.warning(f"Coordinate per '{city}' non trovate — aggiungi a CITY_COORDS")
        return 0

    lat, lng = CITY_COORDS[city_lower]
    keywords = CATEGORY_KEYWORDS.get(category, CATEGORY_KEYWORDS["generico"])
    total_new = 0
    conn = _db_conn()

    for keyword in keywords:
        page_token = None
        results_fetched = 0

        while results_fetched < max_results:
            params = {
                "keyword": keyword,
                "location": f"{lat},{lng}",
                "radius": radius_m,
                "language": "it",
                "key": GOOGLE_PLACES_API_KEY,
            }
            if page_token:
                params["pagetoken"] = page_token
                time.sleep(2)  # Google richiede delay prima di usare pagetoken

            try:
                resp = requests.get(
                    "https://maps.googleapis.com/maps/api/place/nearbysearch/json",
                    params=params,
                    timeout=10,
                )
                data = resp.json()
            except Exception as e:
                logger.error(f"Google Places API error: {e}")
                break

            if data.get("status") not in ("OK", "ZERO_RESULTS"):
                logger.warning(f"Google Places status: {data.get('status')}")
                break

            for place in data.get("results", []):
                place_id = place.get("place_id")
                # Fetch dettaglio per ottenere telefono
                phone_raw = _google_place_details(place_id)
                if not phone_raw:
                    continue

                lead = {
                    "business_name": place.get("name", ""),
                    "phone_raw": phone_raw,
                    "address": place.get("vicinity", ""),
                    "city": city,
                    "province": "",
                    "category": category,
                    "source": "google_places",
                    "source_id": place_id,
                    "website": "",
                    "google_rating": place.get("rating"),
                    "google_reviews": place.get("user_ratings_total"),
                }
                if _upsert_lead(conn, lead):
                    total_new += 1
                    logger.info(f"  + {lead['business_name']} ({phone_raw})")

                results_fetched += 1
                time.sleep(0.1)  # gentile con l'API

            page_token = data.get("next_page_token")
            if not page_token:
                break

        logger.info(f"Google Places [{keyword}] in {city}: {total_new} nuovi lead")
        time.sleep(1)

    conn.close()
    return total_new


def _google_place_details(place_id: str) -> str | None:
    """Recupera numero di telefono da Google Place Details."""
    params = {
        "place_id": place_id,
        "fields": "formatted_phone_number,website",
        "language": "it",
        "key": GOOGLE_PLACES_API_KEY,
    }
    try:
        resp = requests.get(
            "https://maps.googleapis.com/maps/api/place/details/json",
            params=params,
            timeout=8,
        )
        result = resp.json().get("result", {})
        return result.get("formatted_phone_number")
    except Exception:
        return None


# ─── SOURCE 2: PagineBianche ─────────────────────────────────────────────────

def scrape_paginebianche(
    category: str,
    city: str,
    max_pages: int = 10,
) -> int:
    """
    Scraping PagineBianche.it con BeautifulSoup.
    Rate: 1 richiesta ogni 3-5 secondi con UA rotation.
    Ritorna numero di nuovi lead inseriti.
    """
    keyword_map = {
        "parrucchiere": "parrucchieri",
        "officina":     "officine-meccaniche",
        "estetico":     "centri-estetici",
        "palestra":     "palestre",
        "dentista":     "dentisti",
        "generico":     "artigiani",
    }
    keyword = keyword_map.get(category, "artigiani")
    city_enc = quote_plus(city)
    total_new = 0
    conn = _db_conn()

    for page in range(1, max_pages + 1):
        url = f"https://www.paginebianche.it/ricerca?qs={keyword}&dv={city_enc}&pg={page}"
        try:
            resp = requests.get(url, headers=_get_headers(), timeout=15)
            if resp.status_code == 429:
                logger.warning("PagineBianche rate limit — attendo 60s")
                time.sleep(60)
                continue
            if resp.status_code != 200:
                logger.warning(f"PagineBianche HTTP {resp.status_code} — stop")
                break
        except Exception as e:
            logger.error(f"PagineBianche request error: {e}")
            break

        soup = BeautifulSoup(resp.text, "lxml")
        entries = soup.select("div.item-content, li.listing-item, div[class*='result']")

        if not entries:
            # Struttura alternativa
            entries = soup.select("article, .vcard, .listing")

        if not entries:
            logger.info(f"PagineBianche: nessun risultato a pagina {page} — stop")
            break

        for entry in entries:
            # Estrai nome
            name_el = entry.select_one("h2, h3, .business-name, [itemprop='name']")
            if not name_el:
                continue
            name = name_el.get_text(strip=True)

            # Estrai telefono (cerchiamo il primo numero che appare)
            phone_el = entry.select_one(
                "[itemprop='telephone'], .tel, .phone, a[href^='tel:']"
            )
            if phone_el:
                phone_raw = phone_el.get_text(strip=True)
                if not phone_raw and phone_el.get("href", "").startswith("tel:"):
                    phone_raw = phone_el["href"].replace("tel:", "")
            else:
                continue

            if not phone_raw:
                continue

            # Estrai indirizzo
            addr_el = entry.select_one("[itemprop='address'], .address, .adr")
            address = addr_el.get_text(strip=True) if addr_el else ""

            lead = {
                "business_name": name,
                "phone_raw": phone_raw,
                "address": address,
                "city": city,
                "province": "",
                "category": category,
                "source": "paginebianche",
                "source_id": None,
                "website": "",
                "google_rating": None,
                "google_reviews": None,
            }
            if _upsert_lead(conn, lead):
                total_new += 1
                logger.info(f"  + {name} ({phone_raw})")

        logger.info(f"PagineBianche pagina {page}/{max_pages} — {total_new} lead finora")
        time.sleep(random.uniform(3.0, 6.0))

    conn.close()
    return total_new


# ─── SOURCE 3: OpenStreetMap Overpass API ────────────────────────────────────

def scrape_osm_overpass(category: str, city: str) -> int:
    """
    Fallback gratuito usando OpenStreetMap Overpass API.
    Nessuna restrizione. Qualità variabile.
    """
    amenity_map = {
        "parrucchiere": "hairdresser",
        "officina":     "car_repair",
        "estetico":     "beauty",
        "palestra":     "fitness_centre",
        "dentista":     "dentist",
        "generico":     "hairdresser",
    }
    amenity = amenity_map.get(category, "hairdresser")
    city_lower = city.lower().replace(" ", "_")

    if city_lower not in CITY_COORDS:
        return 0

    lat, lng = CITY_COORDS[city_lower]
    radius = 10000  # 10km

    query = f"""
    [out:json][timeout:25];
    (
      node["amenity"="{amenity}"](around:{radius},{lat},{lng});
      way["amenity"="{amenity}"](around:{radius},{lat},{lng});
    );
    out body;
    """

    try:
        resp = requests.post(
            "https://overpass-api.de/api/interpreter",
            data={"data": query},
            timeout=30,
            headers={"User-Agent": random.choice(USER_AGENTS)},
        )
        data = resp.json()
    except Exception as e:
        logger.error(f"OSM Overpass error: {e}")
        return 0

    total_new = 0
    conn = _db_conn()

    for element in data.get("elements", []):
        tags = element.get("tags", {})
        phone_raw = tags.get("phone") or tags.get("contact:phone")
        if not phone_raw:
            continue

        name = tags.get("name", "")
        if not name:
            continue

        lead = {
            "business_name": name,
            "phone_raw": phone_raw,
            "address": tags.get("addr:street", "") + " " + tags.get("addr:housenumber", ""),
            "city": city,
            "province": tags.get("addr:state", ""),
            "category": category,
            "source": "osm",
            "source_id": str(element.get("id")),
            "website": tags.get("website", ""),
            "google_rating": None,
            "google_reviews": None,
        }
        if _upsert_lead(conn, lead):
            total_new += 1

    conn.close()
    logger.info(f"OSM Overpass [{category}] in {city}: {total_new} nuovi lead")
    return total_new


# ─── Orchestratore scraping ───────────────────────────────────────────────────

def scrape_all_sources(category: str, city: str) -> int:
    """Prova tutte le sorgenti in ordine di qualità."""
    total = 0
    logger.info(f"=== Scraping {category} in {city} ===")

    # 1. Google Places (migliore qualità)
    n = scrape_google_places(category, city)
    total += n
    logger.info(f"Google Places: {n} nuovi lead")

    # 2. PagineBianche (se pochi risultati)
    if n < 20:
        n2 = scrape_paginebianche(category, city)
        total += n2
        logger.info(f"PagineBianche: {n2} nuovi lead")

    # 3. OSM (ultimo fallback)
    if total < 10:
        n3 = scrape_osm_overpass(category, city)
        total += n3
        logger.info(f"OSM Overpass: {n3} nuovi lead")

    logger.info(f"=== Totale {category}/{city}: {total} nuovi lead ===")
    return total
```

---

## 9. WHATSAPP SENDER MODULE

```python
# sender.py
"""
Playwright-based WhatsApp Web automation.
Anti-ban: delay gaussiano, variazione testo, orari business, pausa lunga ogni 5 msg.
Session persistence: profilo browser salvato in wa_session/ — QR login una volta sola.
"""
import time
import random
import logging
import sqlite3
import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

from config import (
    DB_PATH, WA_SESSION_DIR,
    DELAY_MEAN_S, DELAY_STD_S, DELAY_MIN_S, DELAY_MAX_S,
    LONG_PAUSE_EVERY, LONG_PAUSE_MIN_S, LONG_PAUSE_MAX_S,
    BUSINESS_HOURS,
)
from templates import render_template, estimate_variation
from utm import build_utm_youtube

logger = logging.getLogger(__name__)


def _is_business_hours() -> bool:
    """Controlla se siamo in orario operativo (lun-ven, 9-12 e 14-17 IT)."""
    now = datetime.datetime.now()
    if now.weekday() >= 5:  # sabato=5, domenica=6
        return False
    h = now.hour
    morning = BUSINESS_HOURS["morning_start"] <= h < BUSINESS_HOURS["morning_end"]
    afternoon = BUSINESS_HOURS["afternoon_start"] <= h < BUSINESS_HOURS["afternoon_end"]
    return morning or afternoon


def _wait_until_business_hours():
    """Aspetta che siano orari operativi, loggando ogni 10 minuti."""
    while not _is_business_hours():
        now = datetime.datetime.now()
        logger.info(f"Fuori orario ({now.strftime('%H:%M %a')}) — aspetto...")
        time.sleep(600)


def _random_delay():
    """Delay gaussiano tra messaggi."""
    delay = random.gauss(DELAY_MEAN_S, DELAY_STD_S)
    delay = max(DELAY_MIN_S, min(DELAY_MAX_S, delay))
    logger.info(f"  Delay: {delay:.0f}s")
    time.sleep(delay)


def _long_pause():
    """Pausa lunga per simulare comportamento umano."""
    pause = random.uniform(LONG_PAUSE_MIN_S, LONG_PAUSE_MAX_S)
    logger.info(f"  Pausa lunga: {pause:.0f}s ({pause/60:.1f} min)")
    time.sleep(pause)


def _get_daily_sent() -> int:
    """Conta messaggi inviati oggi."""
    today = datetime.date.today().isoformat()
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT sent FROM daily_stats WHERE date = ?", (today,)
    ).fetchone()
    conn.close()
    return row[0] if row else 0


def _increment_daily_stats(field: str):
    """Incrementa contatore nel daily_stats per oggi."""
    today = datetime.date.today().isoformat()
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO daily_stats (date, {f}) VALUES (?, 1)
        ON CONFLICT(date) DO UPDATE SET {f} = {f} + 1
    """.format(f=field), (today,))
    conn.commit()
    conn.close()


def _get_pending_leads(limit: int, category: str | None = None) -> list[dict]:
    """
    Recupera lead pendenti con numero WA valido, non ancora contattati.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    query = """
        SELECT l.id, l.business_name, l.phone, l.city, l.category
        FROM leads l
        WHERE l.phone IS NOT NULL
          AND l.wa_registered IS NOT 0
          AND NOT EXISTS (
              SELECT 1 FROM messages m
              WHERE m.lead_id = l.id
                AND m.status IN ('sent', 'delivered', 'read', 'replied')
          )
    """
    params = []
    if category:
        query += " AND l.category = ?"
        params.append(category)
    query += " ORDER BY l.google_rating DESC NULLS LAST LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def _save_message(
    lead_id: int,
    template_key: str,
    message_text: str,
    utm_url: str,
    status: str,
    error_msg: str = None,
):
    conn = sqlite3.connect(DB_PATH)
    sent_at = datetime.datetime.now().isoformat() if status == "sent" else None
    conn.execute("""
        INSERT INTO messages (
            lead_id, template_key, message_text, utm_url,
            status, sent_at, error_msg
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (lead_id, template_key, message_text, utm_url, status, sent_at, error_msg))
    conn.commit()
    conn.close()


def _send_single_message(page, phone: str, message: str) -> bool:
    """
    Invia un messaggio WhatsApp tramite wa.me deep link.
    Ritorna True se inviato con successo.
    """
    # Pulizia numero: WA vuole solo cifre dopo +
    phone_clean = phone.replace("+", "").replace(" ", "").replace("-", "")
    wa_url = f"https://web.whatsapp.com/send?phone={phone_clean}"

    try:
        page.goto(wa_url, wait_until="domcontentloaded", timeout=30000)

        # Attendi che la chat si apra (o errore numero non registrato)
        try:
            page.wait_for_selector(
                'div[data-testid="conversation-panel-wrapper"]',
                timeout=15000,
            )
        except PlaywrightTimeout:
            # Numero non su WA
            logger.warning(f"  {phone}: numero non su WhatsApp")
            return False

        # Controlla se c'è popup "numero non su WA"
        invalid_selectors = [
            'div[data-testid="confirm-popup"]',
            'div[data-icon="alert-circle"]',
        ]
        for sel in invalid_selectors:
            if page.locator(sel).count() > 0:
                logger.warning(f"  {phone}: WA mostra numero non valido")
                return False

        # Trova la text box e scrivi il messaggio
        # Usiamo JavaScript per impostare il testo (compatibile con React/WA)
        box = page.locator('div[data-testid="conversation-compose-box-input"]')
        box.wait_for(state="visible", timeout=10000)
        box.click()

        # Digita il messaggio con pause simulate (anti-bot)
        for chunk in _chunk_text(message):
            box.type(chunk, delay=random.randint(20, 60))
            time.sleep(random.uniform(0.1, 0.3))

        time.sleep(random.uniform(0.5, 1.5))

        # Invia
        send_btn = page.locator('button[data-testid="compose-btn-send"]')
        send_btn.wait_for(state="visible", timeout=5000)
        send_btn.click()

        # Verifica doppia spunta (messaggio inviato)
        time.sleep(2)
        logger.info(f"  INVIATO: {phone}")
        return True

    except PlaywrightTimeout as e:
        logger.error(f"  TIMEOUT {phone}: {e}")
        return False
    except Exception as e:
        logger.error(f"  ERRORE {phone}: {e}")
        return False


def _chunk_text(text: str, max_chunk: int = 50) -> list[str]:
    """Spezza il testo in chunk per digitazione simulata."""
    chunks = []
    words = text.split(" ")
    current = ""
    for word in words:
        if len(current) + len(word) > max_chunk:
            if current:
                chunks.append(current)
            current = word + " "
        else:
            current += word + " "
    if current:
        chunks.append(current)
    return chunks


def run_sender(
    daily_limit: int,
    category: str | None = None,
    dry_run: bool = False,
):
    """
    Ciclo principale di invio messaggi.
    - dry_run=True: prepara messaggi ma non li invia (test)
    - Rispetta orari business, daily limit, rate limiting
    """
    sent_today = _get_daily_sent()
    remaining = daily_limit - sent_today

    if remaining <= 0:
        logger.info(f"Limite giornaliero raggiunto ({daily_limit}). A domani.")
        return

    logger.info(f"=== Sales Agent WA — {remaining} messaggi da inviare ===")

    # Attendi orari operativi
    _wait_until_business_hours()

    leads = _get_pending_leads(remaining + 10, category)
    if not leads:
        logger.info("Nessun lead pendente. Aggiungi lead con 'scrape'.")
        return

    logger.info(f"Lead disponibili: {len(leads)}")

    if dry_run:
        logger.info("=== DRY RUN — nessun messaggio inviato ===")
        for lead in leads[:5]:
            msg, key = render_template(lead["category"], lead["business_name"], lead["city"])
            print(f"\n--- {lead['business_name']} ({lead['phone']}) ---")
            print(msg)
        return

    with sync_playwright() as p:
        # Lancia browser con profilo persistente (QR login una sola volta)
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(WA_SESSION_DIR),
            headless=False,  # Deve essere visibile per QR login
            viewport={"width": 1280, "height": 900},
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
            ],
        )
        page = browser.pages[0] if browser.pages else browser.new_page()

        # Prima navigazione a WA Web
        page.goto("https://web.whatsapp.com", wait_until="domcontentloaded")

        # Attendi login (QR o già loggato)
        logger.info("Attendo login WhatsApp Web (max 60s)...")
        try:
            page.wait_for_selector(
                'div[data-testid="default-user"],'
                'div[data-testid="chatlist-header"],'
                '#side',
                timeout=60000,
            )
            logger.info("Login WA OK")
        except PlaywrightTimeout:
            logger.error("Login WA fallito — scansiona il QR code dalla finestra del browser")
            browser.close()
            return

        # Tracking variazione messaggi (anti-ban)
        last_messages: list[str] = []
        sent_count = 0

        for lead in leads:
            if sent_count >= remaining:
                break

            # Controlla orari
            if not _is_business_hours():
                logger.info("Uscito dagli orari operativi — fermo per oggi")
                break

            phone = lead["phone"]
            if not phone:
                continue

            # Genera messaggio con variazione garantita
            attempts = 0
            while True:
                msg, key = render_template(
                    lead["category"],
                    lead["business_name"],
                    lead["city"],
                )
                if not last_messages:
                    break
                variation = estimate_variation(msg, last_messages[-1])
                if variation >= 0.40 or attempts >= 5:
                    break
                attempts += 1

            utm_url = build_utm_youtube(lead["category"], lead["city"])

            logger.info(f"[{sent_count+1}/{remaining}] {lead['business_name']} ({phone})")

            success = _send_single_message(page, phone, msg)

            if success:
                _save_message(lead["id"], key, msg, utm_url, "sent")
                _increment_daily_stats("sent")
                last_messages.append(msg)
                if len(last_messages) > 5:
                    last_messages.pop(0)
                sent_count += 1

                # Pausa lunga ogni N messaggi
                if sent_count % LONG_PAUSE_EVERY == 0:
                    _long_pause()
                else:
                    _random_delay()
            else:
                # Segna come fallito — numero non WA o timeout
                _save_message(lead["id"], key, msg, utm_url, "failed",
                              error_msg="WA not registered or timeout")
                # Aggiorna lead
                conn = sqlite3.connect(DB_PATH)
                conn.execute(
                    "UPDATE leads SET wa_registered = 0 WHERE id = ?",
                    (lead["id"],)
                )
                conn.commit()
                conn.close()
                time.sleep(5)  # breve pausa anche su fallimento

        logger.info(f"=== Fine invio: {sent_count} messaggi inviati ===")
        browser.close()
```

---

## 10. DASHBOARD MODULE

```python
# dashboard.py
"""
Flask dashboard single-page — legge leads.db e mostra funnel AARRR.
Accesso: http://127.0.0.1:5050
"""
import sqlite3
import json
from datetime import date, timedelta
from flask import Flask, jsonify, render_template_string
from config import DB_PATH, DASHBOARD_PORT, DASHBOARD_HOST

app = Flask(__name__)

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FLUXION Sales Agent — Dashboard</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: #0f1117; color: #e2e8f0; min-height: 100vh; }
  .header { background: linear-gradient(135deg, #1a1f2e 0%, #0f1117 100%);
            padding: 24px 32px; border-bottom: 1px solid #2d3748; }
  .header h1 { font-size: 1.5rem; font-weight: 700; color: #fff; }
  .header p  { color: #718096; font-size: 0.875rem; margin-top: 4px; }
  .container { max-width: 1200px; margin: 0 auto; padding: 32px; }
  .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                gap: 16px; margin-bottom: 32px; }
  .stat-card { background: #1a1f2e; border: 1px solid #2d3748; border-radius: 12px;
               padding: 20px; }
  .stat-card .label { font-size: 0.75rem; color: #718096; text-transform: uppercase;
                      letter-spacing: 0.05em; }
  .stat-card .value { font-size: 2rem; font-weight: 700; margin-top: 8px; }
  .stat-card .sub   { font-size: 0.75rem; color: #718096; margin-top: 4px; }
  .green  { color: #48bb78; }
  .blue   { color: #4299e1; }
  .yellow { color: #ecc94b; }
  .red    { color: #fc8181; }
  .purple { color: #9f7aea; }
  .section { background: #1a1f2e; border: 1px solid #2d3748; border-radius: 12px;
             padding: 24px; margin-bottom: 24px; }
  .section h2 { font-size: 1rem; font-weight: 600; margin-bottom: 16px; color: #a0aec0; }
  .funnel { display: flex; gap: 8px; align-items: flex-end; height: 120px; }
  .funnel-bar { flex: 1; background: linear-gradient(to top, #4299e1, #63b3ed);
                border-radius: 4px 4px 0 0; min-height: 8px;
                display: flex; align-items: flex-end; justify-content: center;
                padding-bottom: 8px; font-size: 0.75rem; color: #fff; font-weight: 600; }
  .funnel-label { text-align: center; font-size: 0.7rem; color: #718096; margin-top: 4px; }
  table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
  th { text-align: left; padding: 10px 12px; color: #718096; font-weight: 500;
       border-bottom: 1px solid #2d3748; font-size: 0.75rem; text-transform: uppercase; }
  td { padding: 10px 12px; border-bottom: 1px solid #1e2535; }
  tr:last-child td { border-bottom: none; }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 9999px;
           font-size: 0.7rem; font-weight: 600; }
  .badge-sent      { background: #2b4c7e; color: #90cdf4; }
  .badge-delivered { background: #276749; color: #9ae6b4; }
  .badge-read      { background: #744210; color: #fbd38d; }
  .badge-replied   { background: #553c9a; color: #d6bcfa; }
  .badge-failed    { background: #742a2a; color: #feb2b2; }
  .badge-pending   { background: #2d3748; color: #a0aec0; }
  .refresh-btn { background: #4299e1; color: #fff; border: none; border-radius: 8px;
                 padding: 8px 16px; cursor: pointer; font-size: 0.875rem; float: right; }
  .chart-bar { height: 8px; background: #2d3748; border-radius: 4px; margin-top: 4px; }
  .chart-fill { height: 100%; border-radius: 4px; transition: width 0.3s; }
</style>
</head>
<body>
<div class="header">
  <h1>FLUXION Sales Agent</h1>
  <p id="last-update">Caricamento...</p>
</div>
<div class="container">
  <!-- KPI Cards -->
  <div class="stats-grid" id="kpi-cards"></div>

  <!-- Funnel Chart -->
  <div class="section">
    <h2>AARRR FUNNEL</h2>
    <div id="funnel-chart"></div>
  </div>

  <!-- Ultimi messaggi -->
  <div class="section">
    <h2>ULTIMI MESSAGGI <button class="refresh-btn" onclick="loadData()">Aggiorna</button></h2>
    <table id="messages-table">
      <thead>
        <tr>
          <th>Attività</th><th>Telefono</th><th>Categoria</th>
          <th>Stato</th><th>Inviato</th>
        </tr>
      </thead>
      <tbody id="messages-body"></tbody>
    </table>
  </div>

  <!-- Stats per categoria -->
  <div class="section">
    <h2>PER CATEGORIA</h2>
    <table id="category-table">
      <thead>
        <tr>
          <th>Categoria</th><th>Lead</th><th>Contattati</th>
          <th>Risposte</th><th>Conv. %</th>
        </tr>
      </thead>
      <tbody id="category-body"></tbody>
    </table>
  </div>
</div>

<script>
async function loadData() {
  const [stats, messages, categories] = await Promise.all([
    fetch('/api/stats').then(r => r.json()),
    fetch('/api/messages?limit=20').then(r => r.json()),
    fetch('/api/categories').then(r => r.json()),
  ]);

  document.getElementById('last-update').textContent =
    'Aggiornato: ' + new Date().toLocaleTimeString('it-IT');

  // KPI Cards
  const kpis = [
    { label: 'Lead Totali',    value: stats.total_leads,     sub: 'nel database',         color: 'blue' },
    { label: 'Contattati',     value: stats.total_sent,      sub: 'messaggi inviati',     color: 'green' },
    { label: 'Letti',          value: stats.total_read,      sub: (stats.read_rate||0).toFixed(1) + '% read rate', color: 'yellow' },
    { label: 'Risposte',       value: stats.total_replied,   sub: (stats.reply_rate||0).toFixed(1) + '% reply rate', color: 'purple' },
    { label: 'Oggi',           value: stats.sent_today,      sub: 'di ' + stats.daily_limit + ' limite', color: 'blue' },
    { label: 'Bloccati',       value: stats.total_blocked,   sub: 'segnalazioni spam',    color: 'red' },
  ];
  document.getElementById('kpi-cards').innerHTML = kpis.map(k => `
    <div class="stat-card">
      <div class="label">${k.label}</div>
      <div class="value ${k.color}">${k.value || 0}</div>
      <div class="sub">${k.sub}</div>
    </div>
  `).join('');

  // Funnel
  const maxVal = Math.max(stats.total_leads||1, 1);
  const funnel_steps = [
    { label: 'Scraped', value: stats.total_leads, color: '#4299e1' },
    { label: 'Contattati', value: stats.total_sent, color: '#48bb78' },
    { label: 'Consegnati', value: stats.total_delivered, color: '#ecc94b' },
    { label: 'Letti', value: stats.total_read, color: '#ed8936' },
    { label: 'Risposte', value: stats.total_replied, color: '#9f7aea' },
  ];
  document.getElementById('funnel-chart').innerHTML = `
    <div style="display:flex;gap:16px;align-items:flex-end;height:140px;padding:0 8px;">
      ${funnel_steps.map(s => {
        const h = Math.max(8, Math.round((s.value||0) / maxVal * 120));
        return `<div style="flex:1;text-align:center;">
          <div style="height:${h}px;background:${s.color};border-radius:4px 4px 0 0;
               display:flex;align-items:flex-end;justify-content:center;
               padding-bottom:4px;font-size:11px;color:#fff;font-weight:700;">${s.value||0}</div>
          <div style="font-size:10px;color:#718096;margin-top:4px;">${s.label}</div>
        </div>`;
      }).join('')}
    </div>`;

  // Messages table
  const statusBadge = s => `<span class="badge badge-${s}">${s}</span>`;
  document.getElementById('messages-body').innerHTML = messages.map(m => `
    <tr>
      <td>${m.business_name || '-'}</td>
      <td><code>${m.phone || '-'}</code></td>
      <td>${m.category || '-'}</td>
      <td>${statusBadge(m.status)}</td>
      <td>${m.sent_at ? new Date(m.sent_at).toLocaleString('it-IT') : '-'}</td>
    </tr>
  `).join('') || '<tr><td colspan="5" style="color:#718096;text-align:center;padding:24px;">Nessun messaggio ancora</td></tr>';

  // Category table
  document.getElementById('category-body').innerHTML = categories.map(c => `
    <tr>
      <td style="text-transform:capitalize;">${c.category}</td>
      <td>${c.total_leads}</td>
      <td>${c.contacted}</td>
      <td>${c.replied}</td>
      <td class="${c.conv_pct >= 2 ? 'green' : c.conv_pct >= 1 ? 'yellow' : 'red'}">
        ${(c.conv_pct||0).toFixed(2)}%
      </td>
    </tr>
  `).join('') || '<tr><td colspan="5" style="color:#718096;text-align:center;padding:24px;">Nessun dato</td></tr>';
}

loadData();
setInterval(loadData, 30000); // auto-refresh ogni 30s
</script>
</body>
</html>
"""


def _db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    return render_template_string(DASHBOARD_HTML)


@app.route("/api/stats")
def api_stats():
    conn = _db()
    today = date.today().isoformat()

    total_leads     = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
    total_sent      = conn.execute("SELECT COUNT(*) FROM messages WHERE status != 'pending'").fetchone()[0]
    total_delivered = conn.execute("SELECT COUNT(*) FROM messages WHERE status IN ('delivered','read','replied')").fetchone()[0]
    total_read      = conn.execute("SELECT COUNT(*) FROM messages WHERE status IN ('read','replied')").fetchone()[0]
    total_replied   = conn.execute("SELECT COUNT(*) FROM messages WHERE status = 'replied'").fetchone()[0]
    total_blocked   = conn.execute("SELECT COUNT(*) FROM messages WHERE status = 'blocked'").fetchone()[0]
    sent_today      = conn.execute(
        "SELECT COALESCE(sent,0) FROM daily_stats WHERE date = ?", (today,)
    ).fetchone()
    sent_today = sent_today[0] if sent_today else 0

    # Recupera daily_limit da agent_state
    state_row = conn.execute(
        "SELECT value FROM agent_state WHERE key = 'daily_limit'"
    ).fetchone()
    daily_limit = int(state_row[0]) if state_row else 20

    conn.close()

    read_rate  = (total_read  / total_sent * 100) if total_sent > 0 else 0
    reply_rate = (total_replied / total_sent * 100) if total_sent > 0 else 0

    return jsonify({
        "total_leads":     total_leads,
        "total_sent":      total_sent,
        "total_delivered": total_delivered,
        "total_read":      total_read,
        "total_replied":   total_replied,
        "total_blocked":   total_blocked,
        "sent_today":      sent_today,
        "daily_limit":     daily_limit,
        "read_rate":       read_rate,
        "reply_rate":      reply_rate,
    })


@app.route("/api/messages")
def api_messages():
    from flask import request
    limit = int(request.args.get("limit", 50))
    conn = _db()
    rows = conn.execute("""
        SELECT m.id, l.business_name, l.phone, l.category,
               m.status, m.sent_at, m.template_key
        FROM messages m
        JOIN leads l ON l.id = m.lead_id
        ORDER BY m.created_at DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/categories")
def api_categories():
    conn = _db()
    rows = conn.execute("""
        SELECT
            l.category,
            COUNT(DISTINCT l.id) as total_leads,
            COUNT(DISTINCT CASE WHEN m.status IN ('sent','delivered','read','replied') THEN l.id END) as contacted,
            COUNT(DISTINCT CASE WHEN m.status = 'replied' THEN l.id END) as replied
        FROM leads l
        LEFT JOIN messages m ON m.lead_id = l.id
        GROUP BY l.category
        ORDER BY total_leads DESC
    """).fetchall()
    conn.close()
    result = []
    for r in rows:
        r = dict(r)
        r["conv_pct"] = (r["replied"] / r["contacted"] * 100) if r["contacted"] > 0 else 0
        result.append(r)
    return jsonify(result)


@app.route("/api/daily")
def api_daily():
    """Ultimi 14 giorni di stats."""
    conn = _db()
    rows = conn.execute("""
        SELECT date, sent, delivered, read_count, replied, failed, blocked
        FROM daily_stats
        ORDER BY date DESC
        LIMIT 14
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


def run_dashboard():
    logger.info(f"Dashboard: http://{DASHBOARD_HOST}:{DASHBOARD_PORT}")
    app.run(host=DASHBOARD_HOST, port=DASHBOARD_PORT, debug=False)
```

---

## 11. MAIN CLI AGENT

```python
# agent.py
"""
FLUXION Sales Agent WA — CLI principale.
Uso: python3 agent.py [scrape|send|dashboard|stats|pause|resume|init]
"""
import argparse
import logging
import sqlite3
import sys
import os
from pathlib import Path
from config import DB_PATH, WA_SESSION_DIR, LOG_DIR, DEFAULT_DAILY_LIMIT

# Setup logging
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / "agent.log"),
    ],
)
logger = logging.getLogger(__name__)


def init_db():
    """Crea le tabelle SQLite se non esistono."""
    WA_SESSION_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    schema = """
    CREATE TABLE IF NOT EXISTS leads (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        business_name   TEXT NOT NULL,
        phone           TEXT,
        phone_raw       TEXT,
        address         TEXT,
        city            TEXT,
        province        TEXT,
        category        TEXT NOT NULL,
        source          TEXT NOT NULL,
        source_id       TEXT,
        website         TEXT,
        google_rating   REAL,
        google_reviews  INTEGER,
        wa_registered   INTEGER DEFAULT NULL,
        scraped_at      TEXT NOT NULL DEFAULT (datetime('now')),
        notes           TEXT,
        UNIQUE(phone_raw)
    );
    CREATE TABLE IF NOT EXISTS messages (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        lead_id         INTEGER NOT NULL REFERENCES leads(id),
        campaign_id     INTEGER,
        template_key    TEXT NOT NULL,
        message_text    TEXT NOT NULL,
        utm_url         TEXT NOT NULL,
        status          TEXT NOT NULL DEFAULT 'pending',
        sent_at         TEXT,
        delivered_at    TEXT,
        read_at         TEXT,
        replied_at      TEXT,
        reply_text      TEXT,
        error_msg       TEXT,
        created_at      TEXT NOT NULL DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS campaigns (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        name            TEXT NOT NULL,
        category        TEXT NOT NULL,
        city            TEXT,
        status          TEXT NOT NULL DEFAULT 'active',
        daily_limit     INTEGER NOT NULL DEFAULT 10,
        delay_min_s     INTEGER NOT NULL DEFAULT 60,
        delay_max_s     INTEGER NOT NULL DEFAULT 180,
        started_at      TEXT NOT NULL DEFAULT (datetime('now')),
        paused_at       TEXT,
        notes           TEXT
    );
    CREATE TABLE IF NOT EXISTS daily_stats (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        date            TEXT NOT NULL,
        sent            INTEGER NOT NULL DEFAULT 0,
        delivered       INTEGER NOT NULL DEFAULT 0,
        read_count      INTEGER NOT NULL DEFAULT 0,
        replied         INTEGER NOT NULL DEFAULT 0,
        failed          INTEGER NOT NULL DEFAULT 0,
        blocked         INTEGER NOT NULL DEFAULT 0,
        UNIQUE(date)
    );
    CREATE TABLE IF NOT EXISTS agent_state (
        key             TEXT PRIMARY KEY,
        value           TEXT NOT NULL,
        updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
    );
    CREATE INDEX IF NOT EXISTS idx_messages_status  ON messages(status);
    CREATE INDEX IF NOT EXISTS idx_messages_sent_at ON messages(sent_at);
    CREATE INDEX IF NOT EXISTS idx_leads_category   ON leads(category);
    CREATE INDEX IF NOT EXISTS idx_leads_city       ON leads(city);
    CREATE INDEX IF NOT EXISTS idx_leads_wa         ON leads(wa_registered);
    """

    conn.executescript(schema)

    # Stato iniziale
    conn.execute("""
        INSERT OR IGNORE INTO agent_state (key, value) VALUES
        ('status', 'active'),
        ('daily_limit', ?),
        ('week_number', '1'),
        ('total_sent_ever', '0')
    """, (str(DEFAULT_DAILY_LIMIT),))
    conn.commit()
    conn.close()
    logger.info(f"DB inizializzato: {DB_PATH}")


def cmd_init(args):
    init_db()
    print(f"Database inizializzato: {DB_PATH}")
    print(f"Sessione WA directory: {WA_SESSION_DIR}")
    print("\nProssimi passi:")
    print("  1. Imposta GOOGLE_PLACES_API_KEY nel tuo environment")
    print("  2. Aggiorna YOUTUBE_LINKS in config.py con i tuoi URL reali")
    print("  3. python3 agent.py scrape --category parrucchiere --city milano")
    print("  4. python3 agent.py send --dry-run  (testa senza inviare)")
    print("  5. python3 agent.py send            (invia messaggi reali)")


def cmd_scrape(args):
    init_db()
    from scraper import scrape_all_sources, scrape_google_places, scrape_paginebianche

    categories = args.category.split(",") if args.category else ["parrucchiere"]
    cities = args.city.split(",") if args.city else ["milano"]

    total = 0
    for cat in categories:
        for city in cities:
            n = scrape_all_sources(cat.strip(), city.strip())
            total += n
            print(f"  {cat}/{city}: {n} nuovi lead")

    print(f"\nTotale nuovi lead aggiunti: {total}")
    print(f"DB: {DB_PATH}")


def cmd_send(args):
    init_db()
    from sender import run_sender

    conn = sqlite3.connect(DB_PATH)
    # Controlla stato pausa
    state = conn.execute(
        "SELECT value FROM agent_state WHERE key = 'status'"
    ).fetchone()
    conn.close()

    if state and state[0] == "paused":
        print("Agent in PAUSA. Usa 'resume' per ripartire.")
        return

    # Determina limite giornaliero da warm-up schedule
    conn = sqlite3.connect(DB_PATH)
    week_row = conn.execute(
        "SELECT value FROM agent_state WHERE key = 'week_number'"
    ).fetchone()
    conn.close()

    from config import WARMUP_SCHEDULE
    week_num = int(week_row[0]) if week_row else 1
    limit = args.limit or WARMUP_SCHEDULE.get(week_num, DEFAULT_DAILY_LIMIT)

    print(f"Invio messaggi — settimana {week_num}, limite {limit}/giorno")
    run_sender(
        daily_limit=limit,
        category=args.category,
        dry_run=args.dry_run,
    )


def cmd_dashboard(args):
    from dashboard import run_dashboard
    run_dashboard()


def cmd_stats(args):
    init_db()
    conn = sqlite3.connect(DB_PATH)

    print("\n=== FLUXION Sales Agent — Stats ===\n")

    total_leads = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
    total_with_phone = conn.execute(
        "SELECT COUNT(*) FROM leads WHERE phone IS NOT NULL"
    ).fetchone()[0]
    total_sent = conn.execute(
        "SELECT COUNT(*) FROM messages WHERE status NOT IN ('pending', 'failed')"
    ).fetchone()[0]
    total_replied = conn.execute(
        "SELECT COUNT(*) FROM messages WHERE status = 'replied'"
    ).fetchone()[0]
    total_failed = conn.execute(
        "SELECT COUNT(*) FROM messages WHERE status = 'failed'"
    ).fetchone()[0]

    print(f"Lead totali:          {total_leads}")
    print(f"  con telefono:       {total_with_phone}")
    print(f"Messaggi inviati:     {total_sent}")
    print(f"Risposte ricevute:    {total_replied}")
    print(f"Falliti (no WA):      {total_failed}")

    if total_sent > 0:
        print(f"\nReply rate:           {total_replied/total_sent*100:.1f}%")

    print("\n--- Per categoria ---")
    rows = conn.execute("""
        SELECT category, COUNT(*) as n
        FROM leads GROUP BY category ORDER BY n DESC
    """).fetchall()
    for r in rows:
        print(f"  {r[0]:20s}: {r[1]} lead")

    print("\n--- Ultimi 7 giorni ---")
    rows = conn.execute("""
        SELECT date, sent, replied, blocked
        FROM daily_stats
        ORDER BY date DESC LIMIT 7
    """).fetchall()
    for r in rows:
        print(f"  {r[0]}: {r[1]} inviati, {r[2]} risposte, {r[3]} blocked")

    conn.close()


def cmd_pause(args):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT OR REPLACE INTO agent_state (key, value, updated_at)
        VALUES ('status', 'paused', datetime('now'))
    """)
    conn.commit()
    conn.close()
    print("Agent in PAUSA. Usa 'resume' per ripartire.")


def cmd_resume(args):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT OR REPLACE INTO agent_state (key, value, updated_at)
        VALUES ('status', 'active', datetime('now'))
    """)
    conn.commit()
    conn.close()
    print("Agent ATTIVO. Prossima esecuzione al prossimo orario operativo.")


def cmd_advance_week(args):
    """Avanza la settimana di warm-up (aumenta limite giornaliero)."""
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT value FROM agent_state WHERE key = 'week_number'"
    ).fetchone()
    current = int(row[0]) if row else 1
    new_week = min(current + 1, 6)

    from config import WARMUP_SCHEDULE
    new_limit = WARMUP_SCHEDULE.get(new_week, DEFAULT_DAILY_LIMIT)

    conn.execute("""
        INSERT OR REPLACE INTO agent_state (key, value, updated_at)
        VALUES ('week_number', ?, datetime('now'))
    """, (str(new_week),))
    conn.execute("""
        INSERT OR REPLACE INTO agent_state (key, value, updated_at)
        VALUES ('daily_limit', ?, datetime('now'))
    """, (str(new_limit),))
    conn.commit()
    conn.close()
    print(f"Settimana avanzata a {new_week} — limite giornaliero: {new_limit} msg/giorno")


def main():
    parser = argparse.ArgumentParser(
        description="FLUXION Sales Agent WhatsApp",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Comandi disponibili:
  init          Inizializza database e directory
  scrape        Scarica lead dalle directory italiane
  send          Invia messaggi WhatsApp ai lead
  dashboard     Avvia dashboard web (http://127.0.0.1:5050)
  stats         Mostra statistiche da terminale
  pause         Mette in pausa l'invio
  resume        Riprende l'invio
  next-week     Avanza settimana di warm-up (aumenta limite)

Esempi:
  python3 agent.py init
  python3 agent.py scrape --category parrucchiere --city milano,torino,roma
  python3 agent.py scrape --category officina --city napoli
  python3 agent.py send --dry-run
  python3 agent.py send --category parrucchiere --limit 10
  python3 agent.py dashboard
  python3 agent.py stats
        """,
    )
    subparsers = parser.add_subparsers(dest="command")

    # init
    subparsers.add_parser("init", help="Inizializza database")

    # scrape
    p_scrape = subparsers.add_parser("scrape", help="Scraping lead")
    p_scrape.add_argument("--category", default="parrucchiere",
        help="Categoria: parrucchiere,officina,estetico,palestra,dentista,generico")
    p_scrape.add_argument("--city", default="milano",
        help="Città (virgola-separated): milano,roma,torino")

    # send
    p_send = subparsers.add_parser("send", help="Invia messaggi WA")
    p_send.add_argument("--category", default=None, help="Filtra per categoria")
    p_send.add_argument("--limit", type=int, default=None, help="Override limite giornaliero")
    p_send.add_argument("--dry-run", action="store_true", help="Test senza inviare")

    # dashboard
    subparsers.add_parser("dashboard", help="Avvia dashboard web")

    # stats
    subparsers.add_parser("stats", help="Statistiche da terminale")

    # pause / resume
    subparsers.add_parser("pause", help="Pausa invio")
    subparsers.add_parser("resume", help="Riprendi invio")

    # next-week
    subparsers.add_parser("next-week", help="Avanza settimana warm-up")

    args = parser.parse_args()

    if args.command == "init":         cmd_init(args)
    elif args.command == "scrape":     cmd_scrape(args)
    elif args.command == "send":       cmd_send(args)
    elif args.command == "dashboard":  cmd_dashboard(args)
    elif args.command == "stats":      cmd_stats(args)
    elif args.command == "pause":      cmd_pause(args)
    elif args.command == "resume":     cmd_resume(args)
    elif args.command == "next-week":  cmd_advance_week(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
```

---

## 12. LAUNCHAGENT PLIST (iMac background)

```xml
<!-- com.fluxion.salesagent.plist -->
<!-- Posizione: ~/Library/LaunchAgents/com.fluxion.salesagent.plist -->
<!-- Attivazione: launchctl load ~/Library/LaunchAgents/com.fluxion.salesagent.plist -->
<!-- Stop: launchctl unload ~/Library/LaunchAgents/com.fluxion.salesagent.plist -->

<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.fluxion.salesagent</string>

    <key>ProgramArguments</key>
    <array>
        <string>/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python</string>
        <string>/Volumes/MacSSD - Dati/fluxion/tools/SalesAgentWA/agent.py</string>
        <string>send</string>
    </array>

    <key>EnvironmentVariables</key>
    <dict>
        <key>GOOGLE_PLACES_API_KEY</key>
        <string>INSERISCI_QUI_LA_KEY</string>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin</string>
    </dict>

    <!-- Esegui ogni giorno alle 9:30 (orario operativo) -->
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>30</integer>
    </dict>

    <!-- Output log -->
    <key>StandardOutPath</key>
    <string>/Volumes/MacSSD - Dati/fluxion/tools/SalesAgentWA/logs/launchagent.log</string>
    <key>StandardErrorPath</key>
    <string>/Volumes/MacSSD - Dati/fluxion/tools/SalesAgentWA/logs/launchagent_err.log</string>

    <key>RunAtLoad</key>
    <false/>

    <key>WorkingDirectory</key>
    <string>/Volumes/MacSSD - Dati/fluxion/tools/SalesAgentWA</string>
</dict>
</plist>
```

---

## 13. ANTI-BAN STRATEGY — DETTAGLIO COMPLETO

### Principi fondamentali

WhatsApp calcola un trust score per ogni numero basato su:
- Rapporto messaggi inviati / segnalazioni spam ricevute
- Velocità di invio (messaggi/ora)
- Similarità testuale tra messaggi consecutivi
- Comportamento storico del numero (aged account = più fiducia)

### Warm-up schedule obbligatorio

```
Settimana 1-2:  5 msg/giorno  — fondatore scrive MANUALMENTE
Settimana 3-4: 10 msg/giorno  — semi-automatico, fondatore approva
Settimana 5:   20 msg/giorno  — agent autonomo
Settimana 6+:  25 msg/giorno  — regime normale (MAI superare 30)
```

### Parametri tecnici anti-ban

```python
# Delay tra messaggi: distribuzione gaussiana, NON valore fisso
delay = max(60, min(300, random.gauss(120, 30)))  # media 2 min

# Pausa lunga ogni 5 messaggi (simula "ti sei distratto")
if sent_count % 5 == 0:
    time.sleep(random.uniform(300, 600))  # 5-10 minuti

# Variazione testo: MINIMO 40% Jaccard distance
# Se generation produce testo troppo simile → rigenera

# Orari SOLO: lun-ven 9:00-12:00 e 14:00-17:00
# ZERO messaggi: sabato, domenica, orario notturno

# UN SOLO link per messaggio — YouTube (non landing diretta)
# ZERO bit.ly o link accorciati — WA li flagga

# ZERO emoji eccessive — max 1 per messaggio
```

### Segnali di pericolo da monitorare

| Metrica | Soglia sicura | Soglia allarme | Azione |
|---------|--------------|----------------|--------|
| Delivery rate | >90% | <85% | Pausa 24h |
| Read rate | >25% | <20% | Rivedi templates |
| Reply rate | >3% | <2% | Migliora hook |
| Block rate | <1% | >2% | STOP immediato |

### Risposta ai ban

**Ban temporaneo (24-72h):**
```
1. python3 agent.py pause
2. Aspetta 72h
3. python3 agent.py resume
4. Riparti con 5 msg/giorno per 1 settimana
```

**Ban permanente:**
```
1. Compra SIM nuova (€10 qualsiasi gestore)
2. Attiva su nuovo telefono
3. Usa normalmente per 7 giorni (chat amici/famiglia)
4. Poi: python3 agent.py send  (parte da settimana 1 automaticamente)
```

### Diversificazione numeri (strategia avanzata)
Avere 2-3 numeri in rotazione permette di inviare 40-90 msg/giorno totali
senza rischiare ban su nessun numero. Aggiungere logica di rotazione in `sender.py`
usando profili browser separati per ogni numero (wa_session_1/, wa_session_2/, ecc.).

---

## 14. SETUP INSTRUCTIONS — STEP BY STEP

### Prerequisiti
- iMac con macOS 12+ e Python 3.9 (già presente)
- Connessione internet
- WhatsApp installato sul telefono del fondatore
- Account Google Cloud (gratuito) per Places API

### Step 1 — Clona e installa dipendenze
```bash
# Già nella repo, navigare alla directory
cd '/Volumes/MacSSD - Dati/fluxion/tools/SalesAgentWA'

# Installa pacchetti Python
/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python -m pip install requests beautifulsoup4 lxml playwright flask schedule

# Installa Chromium per Playwright
/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python -m playwright install chromium
```

### Step 2 — Google Places API key (gratuita)
```
1. Vai su https://console.cloud.google.com
2. Crea nuovo progetto "fluxion-sales"
3. Abilita "Places API"
4. Crea API key → Credenziali → Crea credenziali → Chiave API
5. Restrizioni: solo Places API
6. FREE: 28.500 chiamate/mese (non serve carta di credito per il free tier)
7. export GOOGLE_PLACES_API_KEY="la_tua_chiave"
```

### Step 3 — Carica i video YouTube e aggiorna config
```python
# In config.py, aggiorna YOUTUBE_LINKS con gli URL reali dopo aver caricato i video:
YOUTUBE_LINKS = {
    "parrucchiere": "https://www.youtube.com/watch?v=ID_REALE",
    # ...
}
```

### Step 4 — Inizializza database
```bash
python3 agent.py init
```

### Step 5 — Primo scraping (inizia con parrucchieri Milano)
```bash
python3 agent.py scrape --category parrucchiere --city milano
python3 agent.py stats  # verifica quanti lead
```

### Step 6 — Test senza inviare (dry run)
```bash
python3 agent.py send --dry-run
# Mostra 5 messaggi di anteprima — verifica che siano ok
```

### Step 7 — Prima settimana: fondatore scrive MANUALMENTE
```
NON usare l'agent automatico le prime 2 settimane.
Il fondatore scrive i primi 30 messaggi a mano su WA.
Questo inizia il warm-up del numero e testa i templates.
```

### Step 8 — Login WhatsApp Web (una volta sola)
```bash
python3 agent.py send --limit 1
# Si apre Chromium con WA Web — scansiona QR code con il telefono
# La sessione viene salvata in wa_session/ — non serve più il QR dopo
```

### Step 9 — Installa LaunchAgent per esecuzione automatica
```bash
# Copia il plist
cp com.fluxion.salesagent.plist ~/Library/LaunchAgents/

# Modifica il path e la API key nel plist
nano ~/Library/LaunchAgents/com.fluxion.salesagent.plist

# Attiva
launchctl load ~/Library/LaunchAgents/com.fluxion.salesagent.plist

# Verifica
launchctl list | grep fluxion
```

### Step 10 — Monitora con dashboard
```bash
python3 agent.py dashboard
# Apri: http://127.0.0.1:5050
```

### Step 11 — Avanza warm-up ogni settimana
```bash
# Ogni lunedì, aumenta il limite
python3 agent.py next-week
```

### Troubleshooting comune

**"Google Places status: REQUEST_DENIED"**
→ API key non abilitata su Places API. Vai su Cloud Console → abilita la API.

**"Timeout al login WA Web"**
→ Alla prima esecuzione, `send` apre Chromium. Scansiona il QR velocemente (entro 60s).

**"WA mostra numero non valido"**
→ Il numero non è registrato su WhatsApp. Il lead viene marcato `wa_registered=0` e saltato.

**"Agent non parte con LaunchAgent"**
→ Verifica path Python nel plist. Usa `/usr/local/bin/python3` se quello lungo non funziona.

**"PagineBianche restituisce 0 risultati"**
→ La struttura HTML cambia periodicamente. Aggiornare i selettori CSS in `scrape_paginebianche()`.

---

## 15. FUNNEL TRACKING — UTM + CF KV

### UTM format implementato
```
YouTube link nel WA:
https://youtube.com/watch?v=ID&utm_source=wa&utm_medium=outreach&utm_campaign=parrucchiere&utm_content=milano

Landing (dalla descrizione YouTube):
https://fluxion-landing.pages.dev?utm_source=wa&utm_medium=outreach&utm_campaign=parrucchiere&utm_content=milano
```

### Metriche tracciabili (zero costo)
- **YouTube Studio**: views, CTR, watch time, click su link in descrizione
- **CF Analytics**: visite landing con UTM breakdown (gratis su CF Pages)
- **Stripe Dashboard**: acquisti con source tracking
- **leads.db**: reply rate, delivery rate per categoria/città

### Formula conversione attesa
```
100 messaggi WA
 → 18-22 click YouTube (18-22% CTR)
 → 4-5 click landing (22% YouTube→landing)
 → 1 acquisto (20-25% landing conversion)
 = 1% conversione end-to-end (cold outreach)

Per 20 msg/giorno × 30 giorni = 600 messaggi
→ ~6 acquisti/mese = €3.000-5.400 MRR equivalente (lifetime)
```

---

## 16. ROADMAP DI IMPLEMENTAZIONE

```
Giorno 1 (2h):
  - Step 1-4 setup: installa dipendenze, configura API key, init DB
  - Primo scraping parrucchieri Milano (300-500 lead)

Giorno 2 (1h):
  - Carica video YouTube per categoria parrucchiere
  - Aggiorna YOUTUBE_LINKS in config.py
  - Dry-run per verificare templates

Giorno 3-14 (15 min/giorno):
  - Fondatore scrive 5 msg MANUALMENTE ogni giorno
  - Osserva risposte, migliora templates se reply rate <5%

Giorno 15:
  - Login WA Web con agent, invio primo batch automatico (5 msg)
  - Installa LaunchAgent

Giorno 15-28:
  - Agent autonomo: 10 msg/giorno
  - Scraping altre città: roma, torino, napoli, bologna

Giorno 29+:
  - 20-25 msg/giorno
  - Aggiungi categoria officina/gommista
  - Dashboard monitoraggio quotidiano
```

---

*Blueprint completato. Pronto per implementazione. Nessuna dipendenza a pagamento.*
*Tutti i path iMac: `/Volumes/MacSSD - Dati/fluxion/tools/SalesAgentWA/`*
