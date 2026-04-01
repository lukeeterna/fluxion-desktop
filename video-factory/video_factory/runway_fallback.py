"""
runway_fallback.py — FLUXION Video Factory
Client Runway ML Gen-4 Turbo come fallback se Veo 3 non è disponibile.

Runway Gen-4 Turbo:
  - Qualità comparabile a Veo 3 su scene realistiche
  - ~$0.05/secondo (vs ~$0.35/s Veo 3)
  - API stabile con SDK ufficiale
  - Rate limit: 3 concurrent generations

Installazione:
  pip install runwayml

Documentazione: https://docs.dev.runwayml.com
"""

from __future__ import annotations
import os
import time
import logging
import requests
from pathlib import Path
from dataclasses import dataclass

logger = logging.getLogger(__name__)

RUNWAY_API_KEY = os.environ.get("RUNWAY_API_KEY", "")
RUNWAY_API_VERSION = "2024-11-06"
BASE_URL = "https://api.dev.runwayml.com/v1"

# ─── Dataclasses compatibili con veo3_client ─────────────────────────────────

@dataclass
class RunwayRequest:
    """Compatibile con Veo3Request per drop-in replacement."""
    prompt: str
    aspect_ratio: str = "9:16"
    duration_seconds: int = 8          # Runway supporta 5 o 10
    sample_count: int = 1              # Runway genera 1 alla volta
    negative_prompt: str = (
        "text, watermarks, logos, blurry, distorted, low quality, CGI"
    )
    seed: int | None = None
    model: str = "gen4_turbo"          # gen4_turbo | gen3a_turbo


@dataclass
class RunwayResult:
    """Output compatibile con Veo3Result."""
    operation_name: str
    video_uris: list[str]
    local_paths: list[Path]
    duration_seconds: int
    prompt: str


# ─── Conversione aspect ratio ────────────────────────────────────────────────

RATIO_MAP = {
    "9:16": "720:1280",   # Runway usa WxH
    "16:9": "1280:720",
    "1:1":  "1080:1080",
}


# ─── API client ──────────────────────────────────────────────────────────────

def _headers() -> dict:
    if not RUNWAY_API_KEY:
        raise EnvironmentError(
            "RUNWAY_API_KEY non impostato. "
            "Ottieni la chiave su: https://app.dev.runwayml.com/settings"
        )
    return {
        "Authorization": f"Bearer {RUNWAY_API_KEY}",
        "Content-Type": "application/json",
        "X-Runway-Version": RUNWAY_API_VERSION,
    }


def submit_generation(req: RunwayRequest) -> str:
    """Invia richiesta text-to-video a Runway. Ritorna task_id."""
    ratio = RATIO_MAP.get(req.aspect_ratio, "720:1280")
    w, h = ratio.split(":")

    # Runway supporta solo 5 o 10 secondi
    duration = 10 if req.duration_seconds >= 9 else 5

    payload = {
        "model": req.model,
        "promptText": req.prompt,
        "ratio": ratio,
        "duration": duration,
        **({"seed": req.seed} if req.seed else {}),
    }

    resp = requests.post(
        f"{BASE_URL}/text_to_video",
        headers=_headers(),
        json=payload,
        timeout=60,
    )

    if resp.status_code not in (200, 201):
        raise RuntimeError(
            f"Runway submit failed [{resp.status_code}]: {resp.text}"
        )

    data = resp.json()
    task_id = data.get("id")
    if not task_id:
        raise RuntimeError(f"No task ID in response: {data}")

    logger.info(f"Runway task submitted: {task_id}")
    return task_id


def poll_task(task_id: str, timeout: int = 300) -> dict:
    """Polling finché il task non è SUCCEEDED o FAILED."""
    elapsed = 0
    poll_interval = 8

    while elapsed < timeout:
        time.sleep(poll_interval)
        elapsed += poll_interval

        resp = requests.get(
            f"{BASE_URL}/tasks/{task_id}",
            headers=_headers(),
            timeout=30,
        )

        if resp.status_code != 200:
            logger.warning(f"Runway poll [{resp.status_code}], retry...")
            continue

        data = resp.json()
        status = data.get("status", "")
        logger.info(f"Runway [{elapsed}s]: {status} — progress: {data.get('progress', 0):.0%}")

        if status == "SUCCEEDED":
            return data
        elif status == "FAILED":
            error = data.get("failure", "Unknown error")
            raise RuntimeError(f"Runway generation FAILED: {error}")

    raise TimeoutError(f"Runway task timed out after {timeout}s")


def download_video(url: str, output_path: Path) -> Path:
    """Scarica video da URL Runway a path locale."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    resp = requests.get(url, stream=True, timeout=120)
    resp.raise_for_status()

    with open(output_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

    logger.info(f"Downloaded Runway video → {output_path}")
    return output_path


# ─── High-level interface (compatibile con veo3_client) ──────────────────────

def generate_clip(
    req: RunwayRequest,
    output_dir: Path,
    clip_name: str = "clip",
) -> RunwayResult:
    """
    Drop-in replacement per veo3_client.generate_clip().
    Stessa interfaccia, stesso output.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    task_id = submit_generation(req)
    result = poll_task(task_id)

    # Estrai URL video dall'output
    output_data = result.get("output", [])
    if not output_data:
        raise RuntimeError(f"No output in Runway result: {result}")

    local_paths = []
    video_uris = []

    for i, video_url in enumerate(output_data):
        if not video_url or not video_url.startswith("http"):
            continue
        path = output_dir / f"{clip_name}_v{i+1}.mp4"
        download_video(video_url, path)
        local_paths.append(path)
        video_uris.append(video_url)

    return RunwayResult(
        operation_name=task_id,
        video_uris=video_uris,
        local_paths=local_paths,
        duration_seconds=req.duration_seconds,
        prompt=req.prompt,
    )


def generate_clips_batch(
    requests_list: list[RunwayRequest],
    output_dir: Path,
    verticale: str,
    concurrent: bool = False,
) -> list[RunwayResult]:
    """
    Drop-in replacement per veo3_client.generate_clips_batch().
    Rate limit Runway: max 3 concurrent, ~12s processing/5s video.
    """
    results = []

    for i, req in enumerate(requests_list):
        logger.info(f"Runway clip {i+1}/{len(requests_list)}...")
        result = generate_clip(req, output_dir, f"{verticale}_clip{i+1}")
        results.append(result)
        # Runway rate limit: 1 req/5s
        if i < len(requests_list) - 1:
            time.sleep(5)

    return results


# ─── Adapter per usare Runway invece di Veo 3 ────────────────────────────────

def patch_run_all_to_use_runway():
    """
    Monkey-patch run_all.py per usare Runway invece di Veo 3.
    Chiama questa funzione prima di run_all.main() se Veo 3 non è disponibile.

    Uso:
      import video_factory.runway_fallback as runway
      runway.patch_run_all_to_use_runway()
      import run_all; asyncio.run(run_all.main())
    """
    import video_factory.veo3_client as veo3_module
    import video_factory.script_generator as script_module

    # Sostituisci le funzioni con quelle Runway
    veo3_module.generate_clips_batch = generate_clips_batch
    veo3_module.generate_clip = generate_clip

    # Adatta i Veo3Request in RunwayRequest automaticamente
    original_build = script_module.build_veo3_requests

    def build_runway_requests(verticale_key: str) -> list[RunwayRequest]:
        veo3_reqs = original_build(verticale_key)
        return [
            RunwayRequest(
                prompt=r.prompt,
                aspect_ratio=r.aspect_ratio,
                duration_seconds=min(r.duration_seconds, 10),
                sample_count=1,
                negative_prompt=r.negative_prompt,
                seed=r.seed,
            )
            for r in veo3_reqs
        ]

    script_module.build_veo3_requests = build_runway_requests
    logger.info("Runway fallback attivato — Veo 3 sostituito con Runway Gen-4 Turbo")


# ─── CLI test ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Test Runway ML single clip")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--ratio", default="9:16")
    parser.add_argument("--duration", type=int, default=8)
    parser.add_argument("--output", default="./output/runway_test")
    args = parser.parse_args()

    req = RunwayRequest(
        prompt=args.prompt,
        aspect_ratio=args.ratio,
        duration_seconds=args.duration,
    )

    result = generate_clip(req, Path(args.output), "runway_test")
    print(f"\nGenerati {len(result.local_paths)} video:")
    for p in result.local_paths:
        print(f"  {p}")
