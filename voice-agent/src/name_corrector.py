"""
STT Name Corrector — CoVe 2026
================================
Risolve il mishear fonetico di nomi propri italiani nel transcript Whisper.

Layer 1 — Prompt Injection (0ms overhead):
    Costruisce un prompt contestuale con i nomi clienti più frequenti dal DB.
    Iniettato in ogni chiamata STT → bias decoder verso nomi registrati.
    Gold standard: Retell AI, Vapi, OpenAI Cookbook pattern.

Layer 2 — Phonetic Fast-Path (1-5ms):
    Jaro-Winkler similarity via jellyfish ≥ 0.85 → sostituzione deterministica.
    Es: "l'episcopo" (JW=0.88 con "Piscopo") → "Piscopo".

Dipendenza opzionale: pip install jellyfish
"""
import re
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import List, Optional

logger = logging.getLogger(__name__)

# Prefissi nobiliari/geografici italiani da ignorare nel confronto fonico
_NOBLE_PREFIXES = {
    'de', 'di', 'del', 'della', 'degli', 'dei',
    'lo', 'la', 'le', "d", 'da', 'dall', 'dell',
    'al', 'il', 'un'
}


def get_frequent_client_names(db_path: str, limit: int = 40) -> List[str]:
    """
    Carica i nomi clienti più frequenti (ultimi 30gg) dal DB SQLite.
    Ordinati per frequenza appuntamenti — i più prenotati sono più probabili nel transcript.
    """
    try:
        cutoff = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        conn = sqlite3.connect(db_path, timeout=3)
        cursor = conn.execute("""
            SELECT c.cognome || ' ' || c.nome AS full_name, COUNT(a.id) AS freq
            FROM clienti c
            LEFT JOIN appuntamenti a ON a.cliente_id = c.id AND a.data >= ?
            GROUP BY c.id
            ORDER BY freq DESC
            LIMIT ?
        """, (cutoff, limit))
        names = [row[0] for row in cursor.fetchall() if row[0] and row[0].strip()]
        conn.close()
        return names
    except Exception as e:
        logger.warning(f"[NameCorrector] DB load failed: {e}")
        return []


def build_whisper_prompt(client_names: List[str], max_chars: int = 400) -> str:
    """
    Costruisce prompt ottimale per Groq Whisper (max ~224 token).
    Formato raccomandato OpenAI Cookbook: intestazione + lista nomi.

    Gli ultimi 224 token contano → nomi rari devono stare in coda.
    Stima: ~1.3 token/parola italiano → 400 char ≈ 180 token (margine sicurezza).
    """
    prefix = "Telefonata italiana per prenotazione appuntamento. Clienti: "
    suffix = "."

    selected: List[str] = []
    chars_used = len(prefix) + len(suffix)

    for name in client_names:
        sep = ", " if selected else ""
        addition = sep + name
        if chars_used + len(addition) > max_chars:
            break
        selected.append(name)
        chars_used += len(addition)

    if not selected:
        return "Telefonata in italiano per prenotazione appuntamento."

    return f"{prefix}{', '.join(selected)}{suffix}"


class STTNameCorrector:
    """
    Corregge mishear fonetici dei nomi clienti nel transcript Whisper.

    Uso:
        corrector = STTNameCorrector(db_path)
        prompt = corrector.get_prompt()          # Layer 1: passare a STT
        fixed  = corrector.correct(transcript)   # Layer 2: phonetic fix
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._names: List[str] = []
        self._cache_ts: datetime = datetime.min
        self._jellyfish_ok: bool = False

        try:
            import jellyfish  # noqa: F401
            self._jellyfish_ok = True
            logger.info("[NameCorrector] jellyfish disponibile — phonetic fast-path attivo")
        except ImportError:
            logger.warning(
                "[NameCorrector] jellyfish non trovato — phonetic fast-path disabilitato. "
                "Installa: pip install jellyfish"
            )

    def _refresh_cache(self) -> None:
        """Aggiorna cache nomi ogni 5 minuti."""
        now = datetime.now()
        if (now - self._cache_ts).total_seconds() > 300:
            self._names = get_frequent_client_names(self.db_path)
            self._cache_ts = now
            if self._names:
                logger.debug(f"[NameCorrector] Cache aggiornata: {len(self._names)} clienti")

    def get_prompt(self) -> str:
        """Layer 1 — Restituisce prompt STT aggiornato con lista clienti."""
        self._refresh_cache()
        return build_whisper_prompt(self._names)

    def correct(self, transcript: str) -> str:
        """
        Layer 2 — Phonetic fast-path: sostituisce parole con Jaro-Winkler ≥ 0.85
        rispetto ai nomi clienti in cache.

        Logica: confronta ogni parola del transcript con ogni parte dei nomi
        (ignorando prefissi nobiliari brevi). Se similarità ≥ 0.85 → sostituzione.
        """
        if not transcript or not self._jellyfish_ok or not self._names:
            return transcript

        import jellyfish

        words = transcript.split()
        corrected: List[str] = []

        for word in words:
            clean = re.sub(r"[',.\-!?]", "", word.lower())
            if len(clean) < 3:
                corrected.append(word)
                continue

            best_match: Optional[str] = None
            best_score = 0.0

            for name in self._names:
                name_parts = name.split()
                for i, part in enumerate(name_parts):
                    clean_part = re.sub(r"[',.\-]", "", part.lower())
                    if len(clean_part) < 3 or clean_part in _NOBLE_PREFIXES:
                        continue
                    score = jellyfish.jaro_winkler_similarity(clean, clean_part)
                    if score > best_score:
                        best_score = score
                        best_match = name_parts[i]  # capitalizzazione originale dal DB

            if best_score >= 0.85 and best_match:
                if best_match.lower() != word.lower():
                    logger.info(
                        f"[NameCorrector] Fix fonetico: '{word}' → '{best_match}' "
                        f"(JW={best_score:.2f})"
                    )
                corrected.append(best_match)
            else:
                corrected.append(word)

        return " ".join(corrected)
