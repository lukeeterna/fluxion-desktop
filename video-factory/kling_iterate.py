"""
kling_iterate.py — FLUXION Video Factory
Kling 3.0 free tier prompt iteration workflow.

Strategia: iterare prompt su Kling gratis (66 credits/day, watermarked)
prima di spendere crediti Veo 3.1 su Vertex AI.

Workflow:
  1. Carica storyboard JSON
  2. Esporta prompt per copia-incolla su klingai.com
  3. Logga risultati (buono/cattivo) per ogni prompt
  4. Quando tutti i prompt sono "proven", esporta per batch Veo 3.1

Uso:
  python kling_iterate.py export --vertical parrucchiere
  python kling_iterate.py log --vertical parrucchiere --beat 1 --rating good --notes "mani realistiche"
  python kling_iterate.py status
  python kling_iterate.py export-veo --vertical parrucchiere
"""

import json
import sys
from pathlib import Path
from datetime import datetime

STORYBOARDS_DIR = Path(__file__).parent / "output" / "storyboards"
ITERATION_LOG = Path(__file__).parent / "output" / "kling_iteration_log.json"

VERTICALS = [
    "parrucchiere", "barbiere", "officina", "carrozzeria",
    "dentista", "centro_estetico", "nail_artist", "palestra", "fisioterapista"
]


def load_storyboard(vertical: str) -> dict:
    path = STORYBOARDS_DIR / f"{vertical}.json"
    if not path.exists():
        print(f"Storyboard non trovato: {path}")
        sys.exit(1)
    return json.loads(path.read_text())


def load_log() -> dict:
    if ITERATION_LOG.exists():
        return json.loads(ITERATION_LOG.read_text())
    return {}


def save_log(log: dict):
    ITERATION_LOG.write_text(json.dumps(log, indent=2, ensure_ascii=False))


def cmd_export(vertical: str):
    """Esporta prompt formattati per copia-incolla su Kling 3.0."""
    sb = load_storyboard(vertical)
    print(f"\n{'='*60}")
    print(f"KLING 3.0 — Prompt per: {sb['label']}")
    print(f"{'='*60}")
    print(f"Aspect ratio: 9:16 | Mode: Standard | Duration: 5s")
    print(f"{'='*60}\n")

    for beat in sb["beats"]:
        prompt = beat.get("video_prompt")
        if not prompt:
            continue
        print(f"--- Beat {beat['beat']}: {beat['name']} ---")
        print(f"\n{prompt}\n")
        print(f"Negative: {sb['video_gen_config']['negative_prompt']}")
        print()


def cmd_log(vertical: str, beat: int, rating: str, notes: str = ""):
    """Logga risultato di un prompt testato su Kling."""
    log = load_log()
    key = f"{vertical}_beat{beat}"

    if key not in log:
        log[key] = []

    log[key].append({
        "timestamp": datetime.now().isoformat(),
        "rating": rating,  # good, ok, bad, retry
        "notes": notes,
    })

    save_log(log)
    total = len(log[key])
    good = sum(1 for e in log[key] if e["rating"] == "good")
    print(f"Logged: {vertical} beat {beat} = {rating}")
    print(f"Total iterations: {total} | Good: {good}")


def cmd_status():
    """Mostra stato iterazione per tutti i verticali."""
    log = load_log()

    print(f"\n{'='*60}")
    print(f"KLING ITERATION STATUS")
    print(f"{'='*60}\n")

    for v in VERTICALS:
        sb = load_storyboard(v)
        beats_with_prompt = [b for b in sb["beats"] if b.get("video_prompt")]
        total_beats = len(beats_with_prompt)
        proven = 0

        for beat in beats_with_prompt:
            key = f"{v}_beat{beat['beat']}"
            entries = log.get(key, [])
            has_good = any(e["rating"] == "good" for e in entries)
            if has_good:
                proven += 1

        status = "READY" if proven == total_beats else f"{proven}/{total_beats}"
        marker = " ✅" if proven == total_beats else ""
        print(f"  {v:20s} [{status}]{marker}")

    # Summary
    total_needed = 0
    total_proven = 0
    for v in VERTICALS:
        sb = load_storyboard(v)
        beats_with_prompt = [b for b in sb["beats"] if b.get("video_prompt")]
        total_needed += len(beats_with_prompt)
        for beat in beats_with_prompt:
            key = f"{v}_beat{beat['beat']}"
            entries = log.get(key, [])
            if any(e["rating"] == "good" for e in entries):
                total_proven += 1

    print(f"\nTotal: {total_proven}/{total_needed} proven prompts")
    if total_proven == total_needed:
        print("ALL PROVEN — Ready for Veo 3.1 batch generation!")
    else:
        remaining = total_needed - total_proven
        days = (remaining + 5) // 6  # ~6 clips/day on Kling free
        print(f"Remaining: {remaining} prompts (~{days} days at 6 clips/day)")


def cmd_export_veo(vertical: str):
    """Esporta prompt proven per batch Veo 3.1."""
    log = load_log()
    sb = load_storyboard(vertical)
    config = sb["video_gen_config"]

    veo_requests = []
    for beat in sb["beats"]:
        prompt = beat.get("video_prompt")
        if not prompt:
            continue

        key = f"{vertical}_beat{beat['beat']}"
        entries = log.get(key, [])
        has_good = any(e["rating"] == "good" for e in entries)

        if not has_good:
            print(f"WARNING: Beat {beat['beat']} not proven yet — including anyway")

        # Add style prefix
        style = config.get("style_prefix", "")
        full_prompt = f"{style}. {prompt}" if style else prompt

        veo_requests.append({
            "beat": beat["beat"],
            "prompt": full_prompt,
            "aspect_ratio": config.get("aspect_ratio", "9:16"),
            "duration_seconds": config.get("duration_per_clip", 8),
            "negative_prompt": config.get("negative_prompt", ""),
            "model_tier": config.get("veo_tier", "3.1-fast"),
        })

    output_path = STORYBOARDS_DIR.parent / "veo_batch" / f"{vertical}_veo_batch.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(veo_requests, indent=2, ensure_ascii=False))
    print(f"Exported {len(veo_requests)} Veo requests → {output_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Kling 3.0 Prompt Iteration")
    subparsers = parser.add_subparsers(dest="command")

    # Export prompts for Kling
    exp = subparsers.add_parser("export", help="Export prompts for Kling copy-paste")
    exp.add_argument("--vertical", required=True, choices=VERTICALS)

    # Log iteration result
    lg = subparsers.add_parser("log", help="Log Kling iteration result")
    lg.add_argument("--vertical", required=True, choices=VERTICALS)
    lg.add_argument("--beat", type=int, required=True)
    lg.add_argument("--rating", required=True, choices=["good", "ok", "bad", "retry"])
    lg.add_argument("--notes", default="")

    # Status
    subparsers.add_parser("status", help="Show iteration status")

    # Export for Veo batch
    veo = subparsers.add_parser("export-veo", help="Export proven prompts for Veo batch")
    veo.add_argument("--vertical", required=True, choices=VERTICALS)

    # Export all
    subparsers.add_parser("export-all", help="Export all verticals for Kling")

    args = parser.parse_args()

    if args.command == "export":
        cmd_export(args.vertical)
    elif args.command == "log":
        cmd_log(args.vertical, args.beat, args.rating, args.notes)
    elif args.command == "status":
        cmd_status()
    elif args.command == "export-veo":
        cmd_export_veo(args.vertical)
    elif args.command == "export-all":
        for v in VERTICALS:
            cmd_export(v)
    else:
        parser.print_help()
