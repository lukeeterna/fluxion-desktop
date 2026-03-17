"""
FLUXION Voice Agent — Sales Knowledge Base Loader

Loads and serves the sales knowledge base from JSON.
Used by SalesStateMachine for pitch, objection handling, and closing.
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, List

logger = logging.getLogger("fluxion.sales.kb")

_KB_PATH = Path(__file__).parent.parent / "data" / "sales_knowledge_base.json"

_cached_kb: Optional[Dict] = None


def load_sales_kb() -> Dict:
    """Load sales knowledge base from JSON file. Cached after first load."""
    global _cached_kb
    if _cached_kb is not None:
        return _cached_kb

    if not _KB_PATH.exists():
        logger.error("[Sales KB] File not found: %s", _KB_PATH)
        return {}

    with open(_KB_PATH, "r", encoding="utf-8") as f:
        _cached_kb = json.load(f)

    logger.info("[Sales KB] Loaded: %d pitches, %d objections, %d closing tiers",
                len(_cached_kb.get("product_pitch", {})),
                len(_cached_kb.get("objections", {})),
                len(_cached_kb.get("closing_messages", {})))
    return _cached_kb


def get_pitch(vertical: str) -> Optional[Dict]:
    """Get vertical-specific pitch (headline + pitch + key_number)."""
    kb = load_sales_kb()
    return kb.get("product_pitch", {}).get(vertical)


def get_objection_response(text: str) -> Optional[str]:
    """Match user text against objection trigger phrases, return response."""
    kb = load_sales_kb()
    text_lower = text.lower().strip()

    for obj_key, obj_data in kb.get("objections", {}).items():
        for trigger in obj_data.get("trigger_phrases", []):
            if trigger.lower() in text_lower:
                return obj_data.get("response")
    return None


def get_qualification_question(index: int) -> Optional[Dict]:
    """Get qualification question by index (0-based)."""
    kb = load_sales_kb()
    questions = kb.get("qualification_questions", [])
    if 0 <= index < len(questions):
        return questions[index]
    return None


def get_qualification_count() -> int:
    """Number of qualification questions."""
    kb = load_sales_kb()
    return len(kb.get("qualification_questions", []))


def get_closing_message(tier: str) -> Optional[Dict]:
    """Get closing message for tier (tier_base, tier_pro, tier_clinic)."""
    kb = load_sales_kb()
    return kb.get("closing_messages", {}).get(tier)


def get_pain_points(vertical: str) -> List[str]:
    """Get pain points for a vertical."""
    kb = load_sales_kb()
    return kb.get("pain_points_by_vertical", {}).get(vertical, [])


def get_competitive_response(competitor: str) -> Optional[Dict]:
    """Get competitive comparison for a competitor key (vs_fresha, vs_treatwell, etc.)."""
    kb = load_sales_kb()
    return kb.get("competitive_comparison", {}).get(competitor)


def get_followup_template(timing: str) -> Optional[Dict]:
    """Get followup template by timing key (24h, 48h, 7d, post_purchase_1h, etc.)."""
    kb = load_sales_kb()
    return kb.get("followup_messages", {}).get(timing)


def get_personality_rules() -> Dict:
    """Get Sara sales personality rules (tone, forbidden words, preferred words)."""
    kb = load_sales_kb()
    return kb.get("sara_personality_sales", {})


def sanitize_sales_text(text: str) -> str:
    """Replace forbidden words with preferred alternatives."""
    rules = get_personality_rules()
    preferred = rules.get("preferred_words", {})
    result = text
    for forbidden, replacement in preferred.items():
        # Case-insensitive replacement
        lower = result.lower()
        idx = lower.find(forbidden.lower())
        while idx >= 0:
            result = result[:idx] + replacement + result[idx + len(forbidden):]
            lower = result.lower()
            idx = lower.find(forbidden.lower(), idx + len(replacement))
    return result


# ─────────────────────────────────────────────────────────────────
# Vertical mapping (user text → KB key)
# ─────────────────────────────────────────────────────────────────

_VERTICAL_ALIASES = {
    "parrucchiere": "parrucchiere",
    "parrucchiera": "parrucchiere",
    "salone": "parrucchiere",
    "barbiere": "parrucchiere",
    "barber": "parrucchiere",
    "hair": "parrucchiere",
    "meccanico": "meccanico",
    "officina": "meccanico",
    "autofficina": "meccanico",
    "auto": "meccanico",
    "gommista": "gommista",
    "pneumatici": "gommista",
    "gomme": "gommista",
    "carrozziere": "carrozziere",
    "carrozzeria": "carrozziere",
    "estetista": "estetista",
    "estetica": "estetista",
    "centro estetico": "estetista",
    "beauty": "estetista",
    "palestra": "palestra",
    "fitness": "palestra",
    "gym": "palestra",
    "clinica": "clinica",
    "studio medico": "clinica",
    "medico": "clinica",
    "dentista": "clinica",
    "fisioterapista": "clinica",
    "fisioterapia": "clinica",
    "odontoiatra": "clinica",
    "studio professionale": "studio_professionale",
    "avvocato": "studio_professionale",
    "commercialista": "studio_professionale",
    "consulente": "studio_professionale",
    "studio": "studio_professionale",
}


def resolve_vertical(text: str) -> Optional[str]:
    """Resolve user text to a vertical KB key."""
    text_lower = text.lower().strip()
    # Direct match
    if text_lower in _VERTICAL_ALIASES:
        return _VERTICAL_ALIASES[text_lower]
    # Substring match
    for alias, vertical in _VERTICAL_ALIASES.items():
        if alias in text_lower:
            return vertical
    return None
