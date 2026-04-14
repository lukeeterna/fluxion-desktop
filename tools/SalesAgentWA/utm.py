"""FLUXION Sales Agent WA — UTM link builder + phone normalizer."""
from __future__ import annotations

import re
from urllib.parse import urlencode

from config import YOUTUBE_LINKS, LANDING_URL


def build_utm_youtube(category: str, city: str) -> str:
    """Costruisce il link YouTube con UTM parameters per tracking."""
    base_url = YOUTUBE_LINKS.get(category, YOUTUBE_LINKS["generico"])
    params = {
        "utm_source":   "wa",
        "utm_medium":   "outreach",
        "utm_campaign": category,
        "utm_content":  city.lower().replace(" ", "_"),
    }
    separator = "&" if "?" in base_url else "?"
    return base_url + separator + urlencode(params)


def build_utm_landing(category: str, city: str, source: str = "wa") -> str:
    """Costruisce il link landing con UTM."""
    params = {
        "utm_source":   source,
        "utm_medium":   "outreach",
        "utm_campaign": category,
        "utm_content":  city.lower().replace(" ", "_"),
    }
    return LANDING_URL + "?" + urlencode(params)


def normalize_phone(phone_raw: str) -> str:
    """
    Normalizza numero italiano al formato +39XXXXXXXXXX per WA.
    Ritorna stringa vuota se non valido.
    """
    if not phone_raw:
        return ""
    digits = re.sub(r"\D", "", phone_raw)
    if digits.startswith("0039"):
        digits = digits[4:]
    elif digits.startswith("39") and len(digits) >= 12:
        digits = digits[2:]
    # Numeri italiani: 10 cifre (fisso/mobile)
    if len(digits) == 10:
        return "+39" + digits
    if len(digits) == 11 and digits.startswith("0"):
        return "+39" + digits
    return ""
