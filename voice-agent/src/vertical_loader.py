"""
FLUXION Voice Agent - Vertical FAQ Loader

Loads FAQ files based on business vertical (categoria_attivita).
Handles variable substitution from database settings.

Supported verticals:
- salone: Salone Parrucchiere
- wellness: Centro Benessere / Palestra
- medical: Studio Medico / Dentista
- auto: Officina / Carrozzeria
- altro: Generic business

FAQ files are stored in voice-agent/data/ with naming:
- faq_salone.json
- faq_wellness.json
- faq_medical.json
- faq_auto.json
- faq_altro.json (generic fallback)
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

# Mapping from vertical key to FAQ file
VERTICAL_FAQ_MAP = {
    "salone": "faq_salone.json",
    "wellness": "faq_wellness.json",
    "medical": "faq_medical.json",
    "auto": "faq_auto.json",
    "altro": "faq_altro.json",
}

# Default data directory (relative to this file)
DATA_DIR = Path(__file__).parent.parent / "data"


def get_faq_path(vertical: str, data_dir: Optional[Path] = None) -> Path:
    """
    Get the FAQ file path for a given vertical.

    Args:
        vertical: Business vertical key (salone, wellness, medical, auto, altro)
        data_dir: Optional custom data directory

    Returns:
        Path to FAQ JSON file
    """
    base_dir = data_dir or DATA_DIR
    filename = VERTICAL_FAQ_MAP.get(vertical, "faq_altro.json")
    return base_dir / filename


def substitute_variables(text: str, settings: Dict[str, Any]) -> str:
    """
    Substitute {{VARIABLE}} placeholders with values from settings.

    Args:
        text: Text with {{VARIABLE}} placeholders
        settings: Dictionary of variable values from DB

    Returns:
        Text with variables substituted
    """
    def replace_match(match):
        var_name = match.group(1)
        value = settings.get(var_name)
        if value is not None:
            return str(value)
        # Keep placeholder if variable not found (for debugging)
        return f"[{var_name}]"

    return re.sub(r'\{\{(\w+)\}\}', replace_match, text)


def load_faqs_for_vertical(
    vertical: str,
    settings: Optional[Dict[str, Any]] = None,
    data_dir: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """
    Load FAQs for a specific business vertical.

    Loads the appropriate FAQ file and substitutes variables
    from database settings.

    Args:
        vertical: Business vertical key
        settings: Dictionary of DB values for variable substitution
        data_dir: Optional custom data directory

    Returns:
        List of FAQ dictionaries with substituted variables
    """
    faq_path = get_faq_path(vertical, data_dir)

    if not faq_path.exists():
        print(f"[VERTICAL] FAQ file not found: {faq_path}")
        # Try fallback to altro
        if vertical != "altro":
            return load_faqs_for_vertical("altro", settings, data_dir)
        return []

    # Load JSON
    with open(faq_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Handle both formats: array or {"faqs": [...]}
    if isinstance(data, dict):
        faqs = data.get("faqs", [])
    else:
        faqs = data

    # Substitute variables if settings provided
    if settings:
        for faq in faqs:
            if "answer" in faq:
                faq["answer"] = substitute_variables(faq["answer"], settings)
            if "question" in faq:
                faq["question"] = substitute_variables(faq["question"], settings)

    print(f"[VERTICAL] Loaded {len(faqs)} FAQs for vertical '{vertical}'")
    return faqs


def get_db_settings_for_vertical(vertical: str) -> Dict[str, Any]:
    """
    Get default settings mapping for a vertical.

    These are the DB field mappings for variable substitution.
    The actual values should come from the database.

    Returns:
        Dictionary mapping variable names to DB field paths
    """
    # Common settings for all verticals
    common = {
        "NOME_ATTIVITA": "nome_attivita",
        "INDIRIZZO": "indirizzo_completo",
        "TELEFONO": "telefono",
        "EMAIL": "email",
        "ORARI_APERTURA": "orari_formattati",
        "METODI_PAGAMENTO": "metodi_pagamento",
    }

    # Vertical-specific settings
    vertical_settings = {
        "salone": {
            "PREZZO_TAGLIO_DONNA": "prezzo_taglio_donna",
            "PREZZO_TAGLIO_UOMO": "prezzo_taglio_uomo",
            "PREZZO_COLORE": "prezzo_colore",
            "PREZZO_PIEGA": "prezzo_piega",
            "PREZZO_BARBA": "prezzo_barba",
            "DURATA_TAGLIO_DONNA": "durata_taglio_donna",
            "DURATA_TAGLIO_UOMO": "durata_taglio_uomo",
            "LISTA_SERVIZI": "lista_servizi_formattata",
            "LISTA_OPERATORI": "lista_operatori",
        },
        "wellness": {
            "PREZZO_ABBONAMENTO_MENSILE": "prezzo_abb_mensile",
            "PREZZO_ABBONAMENTO_ANNUALE": "prezzo_abb_annuale",
            "PREZZO_PT": "prezzo_personal_trainer",
            "LISTA_CORSI": "lista_corsi",
            "RISPOSTA_PISCINA": "risposta_piscina",
            "RISPOSTA_PARCHEGGIO": "risposta_parcheggio",
        },
        "medical": {
            "PREZZO_VISITA_GENERALE": "prezzo_visita_generale",
            "PREZZO_VISITA_SPECIALISTICA": "prezzo_visita_spec",
            "LISTA_SPECIALISTI": "lista_specialisti",
            "RISPOSTA_SSN": "risposta_ssn",
            "RISPOSTA_PEDIATRIA": "risposta_pediatria",
        },
        "auto": {
            "PREZZO_REVISIONE": "prezzo_revisione",
            "PREZZO_DIAGNOSI": "prezzo_diagnosi",
            "PREZZO_CAMBIO_GOMME": "prezzo_cambio_gomme",
            "DURATA_GARANZIA": "durata_garanzia_mesi",
            "RISPOSTA_AUTO_SOSTITUTIVA": "risposta_auto_sostitutiva",
            "RISPOSTA_CARROZZERIA": "risposta_carrozzeria",
            "RISPOSTA_ELETTRICHE": "risposta_elettriche",
        },
    }

    result = common.copy()
    if vertical in vertical_settings:
        result.update(vertical_settings[vertical])

    return result


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def get_available_verticals() -> List[str]:
    """Get list of available vertical keys."""
    return list(VERTICAL_FAQ_MAP.keys())


def vertical_exists(vertical: str, data_dir: Optional[Path] = None) -> bool:
    """Check if FAQ file exists for a vertical."""
    return get_faq_path(vertical, data_dir).exists()


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=== Vertical FAQ Loader Test ===\n")

    # Test settings (simulating DB values)
    test_settings = {
        "NOME_ATTIVITA": "Salone Maria",
        "ORARI_APERTURA": "Lun-Ven 9-18, Sab 9-13",
        "TELEFONO": "02 1234567",
        "EMAIL": "info@salonemaria.it",
        "METODI_PAGAMENTO": "contanti, carte, Satispay",
        "PREZZO_TAGLIO_DONNA": "35",
        "PREZZO_TAGLIO_UOMO": "18",
        "DURATA_TAGLIO_DONNA": "60",
    }

    # Test each vertical
    for vertical in get_available_verticals():
        print(f"\n--- Testing vertical: {vertical} ---")
        if vertical_exists(vertical):
            faqs = load_faqs_for_vertical(vertical, test_settings)
            print(f"Loaded {len(faqs)} FAQs")
            if faqs:
                print(f"Sample: {faqs[0].get('question', 'N/A')}")
        else:
            print(f"FAQ file not found")
