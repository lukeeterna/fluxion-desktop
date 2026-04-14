"""
FLUXION Sales Agent WA — Lead scraper.
3 sorgenti in priorita':
1. Google Places API (primario - dati migliori, free 28.500 call/mese)
2. PagineBianche (secondario - fallback)
3. OpenStreetMap Overpass (terziario - 100% gratuito)
"""
from __future__ import annotations

import time
import random
import logging
import sqlite3
from typing import Dict, Optional
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup

from config import DB_PATH, GOOGLE_PLACES_API_KEY, USER_AGENTS
from utm import normalize_phone

logger = logging.getLogger(__name__)

# Coordinate principali citta' italiane
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

# Keyword per categoria
CATEGORY_KEYWORDS = {
    "parrucchiere": ["parrucchiere", "barbiere", "salone parrucchieri", "hairstylist"],
    "officina":     ["officina meccanica", "gommista", "carrozzeria", "autofficina"],
    "estetico":     ["centro estetico", "estetista", "beauty center", "centro benessere"],
    "palestra":     ["palestra", "centro fitness", "crossfit", "pilates studio"],
    "dentista":     ["dentista", "studio dentistico", "fisioterapista", "studio fisioterapia"],
    "generico":     ["parrucchiere", "officina", "centro estetico"],
}


def _get_headers() -> Dict[str, str]:
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "it-IT,it;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }


def _db_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def _upsert_lead(conn, lead: dict) -> bool:
    """Inserisce o skippa lead se phone_raw gia' presente. Ritorna True se nuovo."""
    phone_normalized = normalize_phone(lead.get("phone_raw", ""))
    if not phone_normalized:
        return False
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
        return False


# --- SOURCE 1: Google Places API ---

def scrape_google_places(
    category: str,
    city: str,
    radius_m: int = 10000,
    max_results: int = 200,
) -> int:
    """
    Cerca attivita' tramite Google Places API (Nearby Search).
    FREE: 28.500 call/mese. Ritorna numero di nuovi lead inseriti.
    """
    if not GOOGLE_PLACES_API_KEY:
        logger.warning("GOOGLE_PLACES_API_KEY non configurata - skip Google Places")
        return 0

    city_lower = city.lower().replace(" ", "_")
    if city_lower not in CITY_COORDS:
        logger.warning("Coordinate per '%s' non trovate - aggiungi a CITY_COORDS", city)
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
                "location": "{},{}".format(lat, lng),
                "radius": radius_m,
                "language": "it",
                "key": GOOGLE_PLACES_API_KEY,
            }
            if page_token:
                params["pagetoken"] = page_token
                time.sleep(2)

            try:
                resp = requests.get(
                    "https://maps.googleapis.com/maps/api/place/nearbysearch/json",
                    params=params,
                    timeout=10,
                )
                data = resp.json()
            except Exception as e:
                logger.error("Google Places API error: %s", e)
                break

            if data.get("status") not in ("OK", "ZERO_RESULTS"):
                logger.warning("Google Places status: %s", data.get("status"))
                break

            for place in data.get("results", []):
                place_id = place.get("place_id")
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
                    logger.info("  + %s (%s)", lead["business_name"], phone_raw)

                results_fetched += 1
                time.sleep(0.1)

            page_token = data.get("next_page_token")
            if not page_token:
                break

        logger.info("Google Places [%s] in %s: %d nuovi lead", keyword, city, total_new)
        time.sleep(1)

    conn.close()
    return total_new


def _google_place_details(place_id: str) -> Optional[str]:
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


# --- SOURCE 2: PagineBianche ---

def scrape_paginebianche(
    category: str,
    city: str,
    max_pages: int = 10,
) -> int:
    """
    Scraping PagineBianche.it con BeautifulSoup.
    Rate: 1 richiesta ogni 3-5 secondi con UA rotation.
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
        url = "https://www.paginebianche.it/ricerca?qs={}&dv={}&pg={}".format(
            keyword, city_enc, page
        )
        try:
            resp = requests.get(url, headers=_get_headers(), timeout=15)
            if resp.status_code == 429:
                logger.warning("PagineBianche rate limit - attendo 60s")
                time.sleep(60)
                continue
            if resp.status_code != 200:
                logger.warning("PagineBianche HTTP %d - stop", resp.status_code)
                break
        except Exception as e:
            logger.error("PagineBianche request error: %s", e)
            break

        soup = BeautifulSoup(resp.text, "lxml")

        # PagineBianche 2026: listing container is div.list-element__content
        entries = soup.select("div.list-element__content")

        if not entries:
            # Fallback: try finding containers that have tel: links
            entries = soup.select("div.item-content, li.listing-item, article")

        if not entries:
            logger.info("PagineBianche: nessun risultato a pagina %d - stop", page)
            break

        for entry in entries:
            # Name: h2, h3, strong, or card-title
            name_el = entry.select_one("h2, h3, strong, .card-title")
            if not name_el:
                continue
            name = name_el.get_text(strip=True)
            if not name or len(name) < 3:
                continue

            # Phone: tel: link
            phone_el = entry.select_one("a[href^='tel:']")
            if phone_el:
                phone_raw = phone_el.get("href", "").replace("tel:", "").strip()
                if not phone_raw:
                    phone_raw = phone_el.get_text(strip=True)
            else:
                # Fallback: .hsearch__phone or itemprop
                phone_el = entry.select_one(".hsearch__phone, [itemprop='telephone']")
                if phone_el:
                    phone_raw = phone_el.get_text(strip=True)
                else:
                    continue

            if not phone_raw or phone_raw in ("800011411", "1240"):
                continue

            addr_el = entry.select_one("[class*='addr'], [class*='location'], [itemprop='address']")
            if not addr_el:
                # Fallback: look for text containing via/piazza/corso
                for el in entry.select("span, div, p"):
                    txt = el.get_text(strip=True)
                    if any(w in txt.lower() for w in ("via ", "piazza ", "corso ", "viale ")):
                        addr_el = el
                        break
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
                logger.info("  + %s (%s)", name, phone_raw)

        logger.info("PagineBianche pagina %d/%d - %d lead finora", page, max_pages, total_new)
        time.sleep(random.uniform(3.0, 6.0))

    conn.close()
    return total_new


# --- SOURCE 3: OpenStreetMap Overpass API ---

def scrape_osm_overpass(category: str, city: str) -> int:
    """Fallback gratuito usando OpenStreetMap Overpass API."""
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
    radius = 10000

    query = """
    [out:json][timeout:25];
    (
      node["amenity"="{amenity}"](around:{radius},{lat},{lng});
      way["amenity"="{amenity}"](around:{radius},{lat},{lng});
    );
    out body;
    """.format(amenity=amenity, radius=radius, lat=lat, lng=lng)

    try:
        resp = requests.post(
            "https://overpass-api.de/api/interpreter",
            data={"data": query},
            timeout=30,
            headers={"User-Agent": random.choice(USER_AGENTS)},
        )
        if resp.status_code != 200:
            logger.warning("OSM Overpass HTTP %d", resp.status_code)
            return 0
        if not resp.text.strip():
            logger.warning("OSM Overpass: empty response")
            return 0
        data = resp.json()
    except Exception as e:
        logger.error("OSM Overpass error: %s", e)
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
            "address": (tags.get("addr:street", "") + " " + tags.get("addr:housenumber", "")).strip(),
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
    logger.info("OSM Overpass [%s] in %s: %d nuovi lead", category, city, total_new)
    return total_new


# --- Orchestratore scraping ---

def scrape_all_sources(category: str, city: str) -> int:
    """Prova tutte le sorgenti in ordine di qualita'."""
    total = 0
    logger.info("=== Scraping %s in %s ===", category, city)

    # 1. Google Places (migliore qualita')
    n = scrape_google_places(category, city)
    total += n
    logger.info("Google Places: %d nuovi lead", n)

    # 2. PagineBianche (se pochi risultati)
    if n < 20:
        n2 = scrape_paginebianche(category, city)
        total += n2
        logger.info("PagineBianche: %d nuovi lead", n2)

    # 3. OSM (ultimo fallback)
    if total < 10:
        n3 = scrape_osm_overpass(category, city)
        total += n3
        logger.info("OSM Overpass: %d nuovi lead", n3)

    logger.info("=== Totale %s/%s: %d nuovi lead ===", category, city, total)
    return total
