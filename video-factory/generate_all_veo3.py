#!/usr/bin/env python3
"""
generate_all_veo3.py — Genera clip Veo 3 per tutti i verticali FLUXION
Con BUDGET TRACKER rigido — si ferma PRIMA di sforare i crediti gratuiti.

Usage:
  python3 generate_all_veo3.py                           # tutti, budget default €100
  python3 generate_all_veo3.py --budget 80               # budget custom
  python3 generate_all_veo3.py --vertical barbiere       # solo uno
  python3 generate_all_veo3.py --dry-run                 # mostra costi senza generare
"""

import json
import sys
import time
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from video_factory.veo3_client import Veo3Request, generate_clip

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent / "output" / "prompts"
OUTPUT_BASE = Path(__file__).parent / "output"
COST_LOG = Path(__file__).parent / "output" / "veo3_cost_log.json"

# ─── PRICING Veo 3 (Vertex AI, aprile 2026) ─────────────────────────────────
# Veo 3 generate-preview: $0.35/secondo di video generato
# 8 secondi × 2 sample = 16 secondi → $5.60 per richiesta (~€5.20)
# Fonte: https://cloud.google.com/vertex-ai/generative-ai/pricing
# NOTA: usiamo stime CONSERVATIVE (arrotondato per eccesso) per sicurezza
COST_PER_SECOND_USD = 0.35
USD_TO_EUR = 0.93  # tasso conservativo
SAFETY_MARGIN = 1.2  # 20% margine sicurezza

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

RATE_LIMIT_PAUSE = 25


# ─── Budget Tracker ─────────────────────────────────────────────────────────

class BudgetTracker:
    """Traccia costi Veo 3 con hard stop prima di sforare."""

    def __init__(self, budget_eur: float):
        self.budget_eur = budget_eur
        self.spent_eur = 0.0
        self.requests = []
        self._load_history()

    def _load_history(self):
        """Carica spesa precedente dal log."""
        if COST_LOG.exists():
            data = json.loads(COST_LOG.read_text())
            self.spent_eur = data.get("total_spent_eur", 0.0)
            self.requests = data.get("requests", [])
            logger.info(f"[BUDGET] Spesa precedente caricata: €{self.spent_eur:.2f}")

    def _save(self):
        """Salva log costi su disco."""
        COST_LOG.parent.mkdir(parents=True, exist_ok=True)
        COST_LOG.write_text(json.dumps({
            "total_spent_eur": round(self.spent_eur, 2),
            "budget_eur": self.budget_eur,
            "remaining_eur": round(self.budget_eur - self.spent_eur, 2),
            "total_requests": len(self.requests),
            "requests": self.requests,
        }, indent=2))

    def estimate_cost(self, duration_seconds: int, sample_count: int) -> float:
        """Stima costo di una richiesta in EUR (conservativa)."""
        total_seconds = duration_seconds * sample_count
        cost_usd = total_seconds * COST_PER_SECOND_USD
        cost_eur = cost_usd * USD_TO_EUR * SAFETY_MARGIN
        return round(cost_eur, 2)

    def can_afford(self, duration_seconds: int, sample_count: int) -> tuple[bool, float]:
        """Controlla se il budget copre questa richiesta."""
        cost = self.estimate_cost(duration_seconds, sample_count)
        remaining = self.budget_eur - self.spent_eur
        return cost <= remaining, cost

    def record(self, verticale: str, clip_num: int, duration: int, samples: int, success: bool):
        """Registra una richiesta (anche fallite, per tracking)."""
        cost = self.estimate_cost(duration, samples) if success else 0.0
        self.spent_eur += cost
        self.requests.append({
            "verticale": verticale,
            "clip": clip_num,
            "duration_s": duration,
            "samples": samples,
            "cost_eur": cost,
            "success": success,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        })
        self._save()
        return cost

    def summary(self) -> str:
        remaining = self.budget_eur - self.spent_eur
        return (
            f"SPESO: €{self.spent_eur:.2f} / €{self.budget_eur:.2f} "
            f"| RIMANENTE: €{remaining:.2f} "
            f"| Richieste: {len(self.requests)}"
        )


# ─── Generation ─────────────────────────────────────────────────────────────

def load_prompts(verticale: str) -> list[dict]:
    path = PROMPTS_DIR / f"{verticale}_prompts.json"
    if not path.exists():
        raise FileNotFoundError(f"Prompt file non trovato: {path}")
    data = json.loads(path.read_text())
    return data["veo3_requests"]


def clips_exist(verticale: str) -> list[int]:
    clips_dir = OUTPUT_BASE / verticale / "clips"
    existing = []
    if clips_dir.exists():
        for i in range(1, 4):
            matches = list(clips_dir.glob(f"{verticale}_clip{i}_v*.mp4"))
            if matches:
                existing.append(i)
    return existing


def generate_verticale(verticale: str, budget: BudgetTracker, dry_run: bool = False) -> int:
    prompts = load_prompts(verticale)
    existing = clips_exist(verticale)
    clips_dir = OUTPUT_BASE / verticale / "clips"

    to_generate = [p for p in prompts if p["clip"] not in existing]

    logger.info(f"\n{'='*60}")
    logger.info(f"VERTICALE: {verticale.upper()}")
    logger.info(f"Clip esistenti: {existing or 'nessuna'}")
    logger.info(f"Clip da generare: {[p['clip'] for p in to_generate]}")
    logger.info(f"[BUDGET] {budget.summary()}")
    logger.info(f"{'='*60}")

    generated = 0
    for prompt_data in to_generate:
        clip_num = prompt_data["clip"]
        duration = prompt_data.get("duration_seconds", 8)
        samples = 2

        # ─── BUDGET CHECK (HARD STOP) ───
        can_pay, est_cost = budget.can_afford(duration, samples)
        if not can_pay:
            logger.error(
                f"  [STOP] BUDGET ESAURITO! "
                f"Clip {clip_num} costerebbe ~€{est_cost:.2f} "
                f"ma rimangono solo €{budget.budget_eur - budget.spent_eur:.2f}"
            )
            logger.error(f"  [STOP] Generazione FERMATA per proteggere il budget.")
            return generated

        if dry_run:
            logger.info(f"  [DRY-RUN] Clip {clip_num}: ~€{est_cost:.2f} | {prompt_data['prompt'][:60]}...")
            budget.record(verticale, clip_num, duration, samples, success=False)
            generated += 1
            continue

        logger.info(f"  [GEN] Clip {clip_num} (~€{est_cost:.2f}): {prompt_data['prompt'][:60]}...")

        req = Veo3Request(
            prompt=prompt_data["prompt"],
            aspect_ratio=prompt_data.get("aspect_ratio", "9:16"),
            duration_seconds=duration,
            sample_count=samples,
            negative_prompt=prompt_data.get(
                "negative_prompt",
                "text overlay, watermarks, logos, brand names, blurry, distorted faces, "
                "low quality, overexposed, artifacts, generic stock footage look, CGI, artificial"
            ),
        )

        try:
            result = generate_clip(req, clips_dir, f"{verticale}_clip{clip_num}")
            actual_cost = budget.record(verticale, clip_num, duration, samples, success=True)
            logger.info(f"  [OK] Clip {clip_num}: {len(result.local_paths)} varianti | -€{actual_cost:.2f}")
            logger.info(f"  [BUDGET] {budget.summary()}")
            for p in result.local_paths:
                logger.info(f"       → {p}")
            generated += 1
        except Exception as e:
            budget.record(verticale, clip_num, duration, samples, success=False)
            logger.error(f"  [FAIL] Clip {clip_num}: {e}")
            continue

        # Rate limit
        if generated < len(to_generate):
            logger.info(f"  [WAIT] Rate limit ({RATE_LIMIT_PAUSE}s)...")
            time.sleep(RATE_LIMIT_PAUSE)

    return generated


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Genera clip Veo 3 con budget tracker")
    parser.add_argument("--vertical", "-v", help="Verticale specifico")
    parser.add_argument("--budget", "-b", type=float, default=100.0,
                        help="Budget massimo in EUR (default: €100)")
    parser.add_argument("--dry-run", action="store_true", help="Mostra costi senza generare")
    parser.add_argument("--reset-log", action="store_true", help="Resetta il log dei costi")
    args = parser.parse_args()

    if args.reset_log and COST_LOG.exists():
        COST_LOG.unlink()
        logger.info("Log costi resettato.")

    budget = BudgetTracker(args.budget)
    verticali = [args.vertical] if args.vertical else VERTICALI

    # Pre-flight: stima costo totale
    total_clips = 0
    for v in verticali:
        try:
            prompts = load_prompts(v)
            existing = clips_exist(v)
            total_clips += sum(1 for p in prompts if p["clip"] not in existing)
        except FileNotFoundError:
            pass

    est_total = budget.estimate_cost(8, 2) * total_clips

    logger.info(f"╔══════════════════════════════════════════════════════════╗")
    logger.info(f"║  FLUXION Video Factory — Veo 3 con Budget Tracker      ║")
    logger.info(f"╠══════════════════════════════════════════════════════════╣")
    logger.info(f"║  Budget:     €{args.budget:>8.2f}                               ║")
    logger.info(f"║  Gia speso:  €{budget.spent_eur:>8.2f}                               ║")
    logger.info(f"║  Rimanente:  €{args.budget - budget.spent_eur:>8.2f}                               ║")
    logger.info(f"║  Clip nuove: {total_clips:>3} (stima: ~€{est_total:.2f})                    ║")
    logger.info(f"╚══════════════════════════════════════════════════════════╝")

    if est_total > (args.budget - budget.spent_eur):
        logger.warning(
            f"⚠️  ATTENZIONE: stima €{est_total:.2f} SUPERA budget rimanente "
            f"€{args.budget - budget.spent_eur:.2f}!"
        )
        logger.warning(f"Lo script si FERMERA automaticamente al raggiungimento del limite.")

    if args.dry_run:
        logger.info("*** DRY RUN — nessuna generazione, solo stime ***")

    start_time = time.time()
    total_generated = 0
    total_failed = 0

    for i, verticale in enumerate(verticali):
        # Budget check before starting vertical
        if budget.spent_eur >= budget.budget_eur:
            logger.error(f"[STOP] Budget raggiunto. Verticali rimanenti saltati.")
            break

        try:
            gen = generate_verticale(verticale, budget, dry_run=args.dry_run)
            total_generated += gen
        except FileNotFoundError as e:
            logger.error(f"[SKIP] {verticale}: {e}")
            total_failed += 1
            continue

        if i < len(verticali) - 1 and gen > 0 and not args.dry_run:
            logger.info(f"\n--- Pausa tra verticali (30s) ---\n")
            time.sleep(30)

    elapsed = time.time() - start_time

    logger.info(f"\n╔══════════════════════════════════════════════════════════╗")
    logger.info(f"║  RISULTATO FINALE                                       ║")
    logger.info(f"╠══════════════════════════════════════════════════════════╣")
    logger.info(f"║  Tempo:      {elapsed/60:>6.1f} minuti                            ║")
    logger.info(f"║  Clip OK:    {total_generated:>3}                                      ║")
    logger.info(f"║  Fallite:    {total_failed:>3}                                      ║")
    logger.info(f"║  {budget.summary():<55} ║")
    logger.info(f"╚══════════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
