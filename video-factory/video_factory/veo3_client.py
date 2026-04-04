"""
veo3_client.py — FLUXION Video Factory
Vertex AI Veo API client — supports Veo 2.0 GA, 3.0, 3.1 GA.
Retry, polling, download automatico.

Requisiti:
  pip install google-cloud-aiplatform google-cloud-storage google-auth requests tqdm

Auth:
  export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service_account.json"
  oppure: gcloud auth application-default login
"""

import os
import json
import time
import logging
import base64
import re
import requests
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

import google.auth
import google.auth.transport.requests

logger = logging.getLogger(__name__)

# ─── Config ───────────────────────────────────────────────────────────────────

GCP_PROJECT_ID   = os.environ.get("GCP_PROJECT_ID", "project-07c591f2-ed4e-4865-8af")
GCP_LOCATION     = os.environ.get("GCP_LOCATION", "us-central1")
MAX_POLL_SECONDS = 300                                  # 5 minuti max per generazione
POLL_INTERVAL    = 10                                   # controlla ogni 10s

# ─── Model tiers ─────────────────────────────────────────────────────────────

MODELS = {
    # Veo 3.1 GA (recommended)
    "3.1":      "veo-3.1-generate-001",
    "3.1-fast": "veo-3.1-fast-generate-001",
    "3.1-lite": "veo-3.1-lite-generate-001",
    # Veo 3.0 (deprecated June 30, 2026)
    "3.0":      "veo-3.0-generate-001",
    "3.0-fast": "veo-3.0-fast-generate-001",
    # Veo 2.0 GA (stable)
    "2.0":      "veo-2.0-generate-001",
}

DEFAULT_MODEL_KEY = os.environ.get("VEO_MODEL_TIER", "3.1-fast")


TIER_ALIASES = {
    "fast": "3.1-fast",
    "standard": "3.1",
    "premium": "3.1",
    "lite": "3.1-lite",
}


def _get_model_id(tier: str | None = None) -> str:
    """Resolve model tier key to full model ID."""
    key = tier or DEFAULT_MODEL_KEY
    # Resolve aliases (e.g. "fast" → "3.1-fast")
    key = TIER_ALIASES.get(key, key)
    if key in MODELS:
        return MODELS[key]
    # Allow passing full model ID directly
    if key.startswith("veo-"):
        return key
    raise ValueError(f"Unknown Veo model tier: {key}. Available: {list(MODELS.keys())}")


def _base_url(model_id: str) -> str:
    return (
        f"https://{GCP_LOCATION}-aiplatform.googleapis.com/v1"
        f"/projects/{GCP_PROJECT_ID}/locations/{GCP_LOCATION}"
        f"/publishers/google/models/{model_id}"
    )


# ─── Dataclasses ──────────────────────────────────────────────────────────────

@dataclass
class VeoRequest:
    prompt: str
    aspect_ratio: str = "9:16"          # "9:16" | "16:9"
    duration_seconds: int = 8           # 4, 6, or 8 seconds
    sample_count: int = 2               # 1-4 varianti
    negative_prompt: str = (
        "text, watermarks, logos, blurry, distorted, low quality, "
        "overexposed, underexposed, artifacts, generic stock photo look"
    )
    resolution: str = "720p"            # "720p" | "1080p" | "4k" (3.1 only)
    person_generation: str = "allow_adult"  # "allow_adult" | "disallow"
    seed: Optional[int] = None
    storage_uri: Optional[str] = None   # GCS bucket for output (optional)
    model_tier: Optional[str] = None    # Override default model tier


@dataclass
class VeoResult:
    operation_name: str
    video_uris: list[str]               # GCS URI o path locali
    local_paths: list[Path]             # path locali dopo download
    duration_seconds: int
    prompt: str
    model_id: str = ""


# ─── Auth ─────────────────────────────────────────────────────────────────────

def _get_auth_token() -> str:
    """Ottieni access token Google OAuth2."""
    creds, _ = google.auth.default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    auth_req = google.auth.transport.requests.Request()
    creds.refresh(auth_req)
    return creds.token


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {_get_auth_token()}",
        "Content-Type": "application/json",
    }


# ─── Core API ────────────────────────────────────────────────────────────────

def submit_generation(req: VeoRequest) -> tuple[str, str]:
    """
    Invia richiesta di generazione video.
    Ritorna (operation_name, model_id).
    """
    model_id = _get_model_id(req.model_tier)
    base = _base_url(model_id)

    payload: dict = {
        "instances": [
            {
                "prompt": req.prompt,
            }
        ],
        "parameters": {
            "aspectRatio": req.aspect_ratio,
            "sampleCount": req.sample_count,
            "negativePrompt": req.negative_prompt,
            "personGeneration": req.person_generation,
        },
    }

    # Duration — Veo 3.x uses durationSeconds, Veo 2.0 also supports it
    payload["parameters"]["durationSeconds"] = req.duration_seconds

    # Resolution — only Veo 3.x supports this
    if not model_id.startswith("veo-2"):
        payload["parameters"]["resolution"] = req.resolution

    # Seed
    if req.seed is not None:
        payload["parameters"]["seed"] = req.seed

    # Storage URI — if provided, output goes to GCS bucket
    if req.storage_uri:
        payload["parameters"]["storageUri"] = req.storage_uri

    url = f"{base}:predictLongRunning"
    logger.info(f"Submitting {model_id} request: {req.prompt[:80]}...")

    resp = requests.post(url, headers=_headers(), json=payload, timeout=60)

    if resp.status_code != 200:
        raise RuntimeError(
            f"Veo submission failed [{resp.status_code}]: {resp.text}"
        )

    data = resp.json()
    operation_name = data.get("name") or data.get("operationName")
    if not operation_name:
        raise RuntimeError(f"No operation name in response: {data}")

    logger.info(f"Operation submitted: {operation_name}")
    return operation_name, model_id


def poll_operation(operation_name: str, model_id: str) -> dict:
    """
    Fa polling sull'operazione long-running via fetchPredictOperation.
    Ritorna il response body finale.
    """
    base = _base_url(model_id)
    fetch_url = f"{base}:fetchPredictOperation"

    elapsed = 0
    while elapsed < MAX_POLL_SECONDS:
        time.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL

        resp = requests.post(
            fetch_url,
            headers=_headers(),
            json={"operationName": operation_name},
            timeout=30,
        )
        if resp.status_code != 200:
            logger.warning(f"Poll failed [{resp.status_code}], retrying...")
            continue

        data = resp.json()
        logger.debug(f"Poll [{elapsed}s]: done={data.get('done', False)}")

        if data.get("done"):
            if "error" in data:
                raise RuntimeError(f"Veo generation error: {data['error']}")
            return data

    raise TimeoutError(f"Veo operation timed out after {MAX_POLL_SECONDS}s")


def extract_videos(operation_result: dict, output_dir: Path, clip_name: str) -> list[Path]:
    """
    Estrae video dal risultato dell'operazione.
    Supporta:
      - GCS URIs (Veo 3.x default con storageUri)
      - base64 inline (Veo 2.0 senza storageUri)
      - nested video objects
    Ritorna lista di path locali.
    """
    response = operation_result.get("response", {})
    # Veo 3.x usa "videos" con gcsUri, Veo 2.0 puo usare base64
    items = response.get("videos", []) or response.get("predictions", [])
    local_paths = []

    output_dir.mkdir(parents=True, exist_ok=True)

    for i, pred in enumerate(items):
        path = output_dir / f"{clip_name}_v{i+1}.mp4"

        # Formato 1: GCS URI (Veo 3.x, Veo 2.0 con storageUri)
        if "gcsUri" in pred:
            _download_from_gcs(pred["gcsUri"], path)
            local_paths.append(path)

        # Formato 2: base64 inline (Veo 2.0 senza storageUri)
        elif "bytesBase64Encoded" in pred:
            video_bytes = base64.b64decode(pred["bytesBase64Encoded"])
            path.write_bytes(video_bytes)
            size_mb = len(video_bytes) / (1024 * 1024)
            logger.info(f"Decoded base64 → {path.name} ({size_mb:.1f} MB)")
            local_paths.append(path)

        # Formato 3: nested video object
        elif "video" in pred:
            video = pred["video"]
            if "gcsUri" in video:
                _download_from_gcs(video["gcsUri"], path)
                local_paths.append(path)
            elif "bytesBase64Encoded" in video:
                video_bytes = base64.b64decode(video["bytesBase64Encoded"])
                path.write_bytes(video_bytes)
                local_paths.append(path)

    # Fallback: cerca GCS URIs nel JSON raw
    if not local_paths:
        raw = json.dumps(operation_result)
        uris = re.findall(r'"gcsUri"\s*:\s*"(gs://[^"]+)"', raw)
        for i, uri in enumerate(uris):
            path = output_dir / f"{clip_name}_v{i+1}.mp4"
            _download_from_gcs(uri, path)
            local_paths.append(path)

    return local_paths


def _download_from_gcs(gcs_uri: str, output_path: Path) -> Path:
    """Scarica video da GCS a path locale."""
    from google.cloud import storage

    output_path.parent.mkdir(parents=True, exist_ok=True)
    without_prefix = gcs_uri[len("gs://"):]
    bucket_name, blob_name = without_prefix.split("/", 1)

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.download_to_filename(str(output_path))

    logger.info(f"Downloaded: {gcs_uri} → {output_path}")
    return output_path


# ─── High-level interface ────────────────────────────────────────────────────

def generate_clip(
    req: VeoRequest,
    output_dir: Path,
    clip_name: str = "clip"
) -> VeoResult:
    """
    End-to-end: invia prompt, aspetta, scarica i video.
    Ritorna VeoResult con path locali.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Submit
    operation_name, model_id = submit_generation(req)

    # Poll fino al completamento
    logger.info("Waiting for generation...")
    result = poll_operation(operation_name, model_id)

    # Estrai e salva video
    local_paths = extract_videos(result, output_dir, clip_name)
    if not local_paths:
        raise RuntimeError(f"No videos in result: {json.dumps(result)[:500]}")

    return VeoResult(
        operation_name=operation_name,
        video_uris=[str(p) for p in local_paths],
        local_paths=local_paths,
        duration_seconds=req.duration_seconds,
        prompt=req.prompt,
        model_id=model_id,
    )


def generate_clips_batch(
    requests_list: list[VeoRequest],
    output_dir: Path,
    verticale: str,
    concurrent: bool = False,
) -> list[VeoResult]:
    """
    Genera piu clip in sequenza (o concorrente se concurrent=True).
    Rate limit Veo 3.1: 50 req/min GA.
    """
    results = []

    if concurrent:
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(
                    generate_clip,
                    req,
                    output_dir,
                    f"{verticale}_clip{i+1}"
                )
                for i, req in enumerate(requests_list)
            ]
            for fut in concurrent.futures.as_completed(futures):
                results.append(fut.result())
    else:
        for i, req in enumerate(requests_list):
            logger.info(f"Generating clip {i+1}/{len(requests_list)}...")
            result = generate_clip(
                req,
                output_dir,
                f"{verticale}_clip{i+1}"
            )
            results.append(result)
            # Rate limiting — 2s between requests (50/min limit)
            if i < len(requests_list) - 1:
                logger.info("Rate limit pause (2s)...")
                time.sleep(2)

    return results


# ─── Storyboard loader ───────────────────────────────────────────────────────

def load_storyboard(storyboard_path: Path) -> list[VeoRequest]:
    """
    Carica un JSON storyboard v1 e converte i beat in VeoRequest.
    Salta beat senza video_prompt (es. CTA frame).
    """
    with open(storyboard_path) as f:
        sb = json.load(f)

    config = sb.get("video_gen_config", {})
    requests_list = []

    for beat in sb["beats"]:
        prompt = beat.get("video_prompt")
        if not prompt:
            continue

        # Prepend style prefix
        style = config.get("style_prefix", "")
        if style and not prompt.startswith(style):
            prompt = f"{style}. {prompt}"

        requests_list.append(VeoRequest(
            prompt=prompt,
            aspect_ratio=config.get("aspect_ratio", "9:16"),
            duration_seconds=config.get("duration_per_clip", 8),
            sample_count=2,
            negative_prompt=config.get("negative_prompt", ""),
            resolution="720p",
            model_tier=config.get("veo_tier", "3.1-fast"),
        ))

    return requests_list


# ─── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="FLUXION Veo Video Generator")
    subparsers = parser.add_subparsers(dest="command")

    # Single clip
    clip_parser = subparsers.add_parser("clip", help="Generate single clip")
    clip_parser.add_argument("--prompt", required=True)
    clip_parser.add_argument("--ratio", default="9:16")
    clip_parser.add_argument("--duration", type=int, default=8)
    clip_parser.add_argument("--tier", default=None, help="Model tier: 3.1, 3.1-fast, 2.0, etc.")
    clip_parser.add_argument("--resolution", default="720p")
    clip_parser.add_argument("--output", default="./output/test")

    # Storyboard batch
    sb_parser = subparsers.add_parser("storyboard", help="Generate from storyboard JSON")
    sb_parser.add_argument("--file", type=Path, required=True, help="Path to storyboard JSON")
    sb_parser.add_argument("--output", type=Path, default=Path("./output"))
    sb_parser.add_argument("--concurrent", action="store_true")

    # List models
    subparsers.add_parser("models", help="List available model tiers")

    args = parser.parse_args()

    if args.command == "clip":
        req = VeoRequest(
            prompt=args.prompt,
            aspect_ratio=args.ratio,
            duration_seconds=args.duration,
            resolution=args.resolution,
            model_tier=args.tier,
        )
        result = generate_clip(req, Path(args.output), "test_clip")
        print(f"\nGenerati {len(result.local_paths)} video ({result.model_id}):")
        for p in result.local_paths:
            print(f"  {p}")

    elif args.command == "storyboard":
        sb = json.loads(args.file.read_text())
        verticale = sb["verticale"]
        reqs = load_storyboard(args.file)
        out_dir = args.output / verticale / "clips"
        print(f"Generating {len(reqs)} clips for {verticale}...")
        results = generate_clips_batch(reqs, out_dir, verticale, args.concurrent)
        print(f"\nDone! {sum(len(r.local_paths) for r in results)} videos generated.")

    elif args.command == "models":
        print("Available Veo model tiers:")
        for key, model_id in MODELS.items():
            marker = " ← default" if key == DEFAULT_MODEL_KEY else ""
            print(f"  {key:12s} → {model_id}{marker}")

    else:
        parser.print_help()
