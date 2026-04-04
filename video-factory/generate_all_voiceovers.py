#!/usr/bin/env python3
"""
generate_all_voiceovers.py — Genera voiceover Edge-TTS per tutti i verticali FLUXION
Usa i copioni in output/prompts/*_prompts.json

Usage:
  python3 generate_all_voiceovers.py                     # tutti
  python3 generate_all_voiceovers.py --vertical barbiere # solo uno
"""

import asyncio
import json
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from video_factory.assembly import generate_voiceover

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent / "output" / "prompts"
OUTPUT_BASE = Path(__file__).parent / "output"

VERTICALI = [
    "barbiere",
    "officina",
    "carrozzeria",
    "dentista",
    "centro_estetico",
    "nail_artist",
    "palestra",
    "fisioterapista",
]


async def generate_for_verticale(verticale: str) -> bool:
    """Genera voiceover per un verticale. Ritorna True se successo."""
    prompts_path = PROMPTS_DIR / f"{verticale}_prompts.json"
    if not prompts_path.exists():
        logger.error(f"[SKIP] {verticale}: prompt file non trovato")
        return False

    data = json.loads(prompts_path.read_text())
    narration = data.get("narration_script", {})
    segments = narration.get("segments", [])

    if not segments:
        logger.error(f"[SKIP] {verticale}: nessun segmento narrazione")
        return False

    output_dir = OUTPUT_BASE / verticale
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{verticale}_voiceover.mp3"

    if output_path.exists():
        logger.info(f"[SKIP] {verticale}: voiceover gia esistente ({output_path})")
        return True

    logger.info(f"[GEN] {verticale}: {len([s for s in segments if s.get('text')])} segmenti...")

    try:
        result = await generate_voiceover(
            segments=segments,
            output_path=output_path,
            voice="it-IT-IsabellaNeural",
        )
        if result:
            size_kb = output_path.stat().st_size / 1024
            logger.info(f"[OK] {verticale}: {output_path.name} ({size_kb:.0f} KB)")
            return True
        else:
            logger.error(f"[FAIL] {verticale}: nessun segmento con testo")
            return False
    except Exception as e:
        logger.error(f"[FAIL] {verticale}: {e}")
        return False


async def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--vertical", "-v", help="Verticale specifico")
    args = parser.parse_args()

    verticali = [args.vertical] if args.vertical else VERTICALI

    logger.info(f"FLUXION — Voiceover Edge-TTS Batch")
    logger.info(f"Verticali: {', '.join(verticali)}")
    logger.info("")

    ok = 0
    fail = 0
    for v in verticali:
        if await generate_for_verticale(v):
            ok += 1
        else:
            fail += 1

    logger.info(f"\nCompletato: {ok} OK, {fail} falliti")


if __name__ == "__main__":
    asyncio.run(main())
