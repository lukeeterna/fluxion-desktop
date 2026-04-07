"""
kling_client.py — FLUXION Video Factory
Kling AI API client for automated text-to-video generation.

Reads storyboard JSON v1, submits all beats to Kling API,
polls for completion, downloads MP4 clips.

Usage:
  python kling_client.py generate --vertical parrucchiere
  python kling_client.py generate --vertical all
  python kling_client.py generate --vertical parrucchiere --model kling-v2-1
  python kling_client.py status --task-id <id>
"""

import json
import jwt
import os
import sys
import time
import requests
from pathlib import Path
from datetime import datetime

# ── Config ──────────────────────────────────────────────────────────

BASE_URL = "https://api.klingai.com"
ACCESS_KEY = os.environ.get("KLING_ACCESS_KEY", "")
SECRET_KEY = os.environ.get("KLING_SECRET_KEY", "")

STORYBOARDS_DIR = Path(__file__).parent / "output" / "storyboards"
OUTPUT_DIR = Path(__file__).parent / "output" / "kling_clips"
ITERATION_LOG = Path(__file__).parent / "output" / "kling_iteration_log.json"

# Default model: v2-1 supports negative_prompt; v3-0 does NOT
DEFAULT_MODEL = "kling-v2-1"
# Models that do NOT support negative_prompt
NO_NEGATIVE_MODELS = {"kling-v2-5-turbo", "kling-v2-6", "kling-v3-0"}

VERTICALS = [
    "parrucchiere", "barbiere", "officina", "carrozzeria",
    "dentista", "centro_estetico", "nail_artist", "palestra", "fisioterapista"
]

POLL_INTERVAL = 10  # seconds between status checks
POLL_TIMEOUT = 600  # max wait per task (10 min)


# ── Auth ────────────────────────────────────────────────────────────

def generate_token() -> str:
    """Generate JWT token for Kling API auth."""
    if not ACCESS_KEY or not SECRET_KEY:
        print("ERROR: Set KLING_ACCESS_KEY and KLING_SECRET_KEY env vars")
        sys.exit(1)
    now = int(time.time())
    payload = {
        "iss": ACCESS_KEY,
        "exp": now + 1800,
        "nbf": now - 5,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def headers() -> dict:
    return {
        "Authorization": f"Bearer {generate_token()}",
        "Content-Type": "application/json",
    }


# ── API Calls ───────────────────────────────────────────────────────

def submit_text2video(prompt: str, negative_prompt: str = "",
                      aspect_ratio: str = "9:16", duration: str = "5",
                      mode: str = "std", model: str = DEFAULT_MODEL,
                      cfg_scale: float = 0.5) -> dict:
    """Submit a text-to-video generation task. Returns API response."""
    body = {
        "model_name": model,
        "prompt": prompt,
        "mode": mode,
        "aspect_ratio": aspect_ratio,
        "duration": duration,
    }

    # Only add negative_prompt and cfg_scale for models that support it
    if model not in NO_NEGATIVE_MODELS:
        if negative_prompt:
            body["negative_prompt"] = negative_prompt
        body["cfg_scale"] = cfg_scale

    resp = requests.post(f"{BASE_URL}/v1/videos/text2video",
                         headers=headers(), json=body, timeout=30)
    if resp.status_code != 200:
        print(f"  HTTP {resp.status_code}: {resp.text[:500]}")
        return {"error": resp.text}
    data = resp.json()

    if data.get("code") != 0:
        print(f"  API ERROR: {data.get('message', 'unknown')}")
        return data

    return data


def poll_task(task_id: str) -> dict:
    """Poll until task completes or fails. Returns final response."""
    start = time.time()
    while time.time() - start < POLL_TIMEOUT:
        resp = requests.get(f"{BASE_URL}/v1/videos/text2video/{task_id}",
                            headers=headers(), timeout=30)
        resp.raise_for_status()
        data = resp.json()

        status = data.get("data", {}).get("task_status", "unknown")
        if status == "succeed":
            return data
        elif status == "failed":
            msg = data.get("data", {}).get("task_status_msg", "unknown error")
            print(f"  FAILED: {msg}")
            return data

        elapsed = int(time.time() - start)
        print(f"  [{elapsed}s] Status: {status}...", end="\r")
        time.sleep(POLL_INTERVAL)

    print(f"\n  TIMEOUT after {POLL_TIMEOUT}s")
    return {"error": "timeout"}


def download_video(url: str, output_path: Path) -> bool:
    """Download video from URL to local path."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        resp = requests.get(url, stream=True, timeout=120)
        resp.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        size_mb = output_path.stat().st_size / (1024 * 1024)
        print(f"  Downloaded: {output_path.name} ({size_mb:.1f}MB)")
        return True
    except Exception as e:
        print(f"  Download error: {e}")
        return False


# ── Storyboard Processing ──────────────────────────────────────────

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


def generate_vertical(vertical: str, model: str = DEFAULT_MODEL,
                      mode: str = "std", skip_proven: bool = True):
    """Generate all clips for a vertical via Kling API."""
    sb = load_storyboard(vertical)
    config = sb["video_gen_config"]
    log = load_log()

    beats_with_prompt = [b for b in sb["beats"] if b.get("video_prompt")]
    out_dir = OUTPUT_DIR / vertical

    print(f"\n{'='*60}")
    print(f"KLING API — {sb['label']}")
    print(f"Model: {model} | Mode: {mode} | Beats: {len(beats_with_prompt)}")
    print(f"{'='*60}\n")

    tasks = []  # (beat, task_id)

    for beat in beats_with_prompt:
        beat_num = beat["beat"]
        key = f"{vertical}_beat{beat_num}"

        # Skip if already proven
        if skip_proven:
            entries = log.get(key, [])
            if any(e["rating"] == "good" for e in entries):
                print(f"  Beat {beat_num} ({beat['name']}): SKIPPED (already proven)")
                continue

        # Add style prefix
        style = config.get("style_prefix", "")
        prompt = f"{style}. {beat['video_prompt']}" if style else beat["video_prompt"]
        negative = config.get("negative_prompt", "")
        aspect = config.get("aspect_ratio", "9:16")
        kling_mode = mode or config.get("kling_mode", "std")

        print(f"  Beat {beat_num} ({beat['name']}): Submitting...")

        result = submit_text2video(
            prompt=prompt,
            negative_prompt=negative,
            aspect_ratio=aspect,
            duration="5",
            mode=kling_mode,
            model=model,
        )

        task_id = result.get("data", {}).get("task_id")
        if task_id:
            print(f"  Beat {beat_num}: Task ID = {task_id}")
            tasks.append((beat, task_id))
        else:
            print(f"  Beat {beat_num}: SUBMIT FAILED — {result}")

        # Small delay between submissions
        time.sleep(1)

    if not tasks:
        print("\nNo tasks submitted (all proven or errors).")
        return

    # Poll all tasks
    print(f"\n--- Polling {len(tasks)} tasks ---\n")
    results = []

    for beat, task_id in tasks:
        beat_num = beat["beat"]
        print(f"  Beat {beat_num} ({beat['name']}): Waiting...")

        data = poll_task(task_id)
        status = data.get("data", {}).get("task_status", "unknown")

        if status == "succeed":
            videos = data["data"]["task_result"]["videos"]
            for i, video in enumerate(videos):
                url = video["url"]
                suffix = f"_v{i+1}" if len(videos) > 1 else ""
                out_path = out_dir / f"{vertical}_beat{beat_num}{suffix}.mp4"
                if download_video(url, out_path):
                    # Auto-log as "good" since API-generated
                    key = f"{vertical}_beat{beat_num}"
                    if key not in log:
                        log[key] = []
                    log[key].append({
                        "timestamp": datetime.now().isoformat(),
                        "rating": "good",
                        "notes": f"API generated, model={model}, task_id={task_id}",
                        "file": str(out_path),
                    })
                    results.append((beat_num, "OK", str(out_path)))
        else:
            results.append((beat_num, "FAIL", status))

    save_log(log)

    # Summary
    print(f"\n{'='*60}")
    print(f"RESULTS — {sb['label']}")
    print(f"{'='*60}")
    for beat_num, status, detail in results:
        marker = "✅" if status == "OK" else "❌"
        print(f"  {marker} Beat {beat_num}: {status} — {detail}")


def generate_all(model: str = DEFAULT_MODEL, mode: str = "std"):
    """Generate clips for all 9 verticals."""
    for v in VERTICALS:
        generate_vertical(v, model=model, mode=mode)


# ── CLI ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Kling AI API Client — FLUXION")
    subparsers = parser.add_subparsers(dest="command")

    # Generate
    gen = subparsers.add_parser("generate", help="Generate clips from storyboard")
    gen.add_argument("--vertical", required=True,
                     help="Vertical name or 'all'")
    gen.add_argument("--model", default=DEFAULT_MODEL,
                     help=f"Model name (default: {DEFAULT_MODEL})")
    gen.add_argument("--mode", default="std", choices=["std", "pro"],
                     help="Generation mode (default: std)")
    gen.add_argument("--no-skip", action="store_true",
                     help="Regenerate even if already proven")

    # Status check
    st = subparsers.add_parser("status", help="Check task status")
    st.add_argument("--task-id", required=True, help="Task ID to check")

    args = parser.parse_args()

    if args.command == "generate":
        if args.vertical == "all":
            generate_all(model=args.model, mode=args.mode)
        elif args.vertical in VERTICALS:
            generate_vertical(args.vertical, model=args.model,
                              mode=args.mode, skip_proven=not args.no_skip)
        else:
            print(f"Unknown vertical: {args.vertical}")
            print(f"Available: {', '.join(VERTICALS)}")
            sys.exit(1)

    elif args.command == "status":
        data = poll_task(args.task_id)
        print(json.dumps(data, indent=2, ensure_ascii=False))

    else:
        parser.print_help()
