"""
veo3_client.py — FLUXION Video Factory
Vertex AI Veo 3 API client con retry, polling e download automatico.

Requisiti:
  pip install google-cloud-aiplatform google-auth requests tqdm

Auth:
  export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service_account.json"
  oppure: gcloud auth application-default login
"""

import os
import json
import time
import logging
import requests
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

import google.auth
import google.auth.transport.requests

logger = logging.getLogger(__name__)

# ─── Config ───────────────────────────────────────────────────────────────────

GCP_PROJECT_ID   = os.environ.get("GCP_PROJECT_ID", "project-07c591f2-ed4e-4865-8af")
GCP_LOCATION     = os.environ.get("GCP_LOCATION", "us-central1")
VEO3_MODEL       = "veo-3.0-generate-preview"          # aggiorna se Google cambia versione
MAX_POLL_SECONDS = 300                                  # 5 minuti max per generazione
POLL_INTERVAL    = 10                                   # controlla ogni 10s

BASE_URL = (
    f"https://{GCP_LOCATION}-aiplatform.googleapis.com/v1"
    f"/projects/{GCP_PROJECT_ID}/locations/{GCP_LOCATION}"
    f"/publishers/google/models/{VEO3_MODEL}"
)


# ─── Dataclasses ──────────────────────────────────────────────────────────────

@dataclass
class Veo3Request:
    prompt: str
    aspect_ratio: str = "9:16"          # "9:16" | "16:9" | "1:1"
    duration_seconds: int = 8           # 5–8 secondi
    sample_count: int = 2               # quante varianti generare
    negative_prompt: str = (
        "text, watermarks, logos, blurry, distorted, low quality, "
        "overexposed, underexposed, artifacts, generic stock photo look"
    )
    seed: Optional[int] = None


@dataclass
class Veo3Result:
    operation_name: str
    video_uris: list[str]               # GCS URI dei video generati
    local_paths: list[Path]             # path locali dopo download
    duration_seconds: int
    prompt: str


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

def submit_generation(req: Veo3Request) -> str:
    """
    Invia richiesta di generazione video a Veo 3.
    Ritorna il nome dell'operazione long-running.
    """
    payload = {
        "instances": [
            {
                "prompt": req.prompt,
            }
        ],
        "parameters": {
            "aspectRatio": req.aspect_ratio,
            "sampleCount": req.sample_count,
            "durationSeconds": req.duration_seconds,
            "negativePrompt": req.negative_prompt,
            **({"seed": req.seed} if req.seed else {}),
        },
    }

    url = f"{BASE_URL}:predictLongRunning"
    logger.info(f"Submitting Veo 3 request: {req.prompt[:80]}...")

    resp = requests.post(url, headers=_headers(), json=payload, timeout=60)

    if resp.status_code != 200:
        raise RuntimeError(
            f"Veo 3 submission failed [{resp.status_code}]: {resp.text}"
        )

    data = resp.json()
    operation_name = data.get("name") or data.get("operationName")
    if not operation_name:
        raise RuntimeError(f"No operation name in response: {data}")

    logger.info(f"Operation submitted: {operation_name}")
    return operation_name


def poll_operation(operation_name: str) -> dict:
    """
    Fa polling sull'operazione long-running finché non è completata.
    Ritorna il response body finale.
    """
    operations_url = (
        f"https://{GCP_LOCATION}-aiplatform.googleapis.com/v1/{operation_name}"
    )

    elapsed = 0
    while elapsed < MAX_POLL_SECONDS:
        time.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL

        resp = requests.get(operations_url, headers=_headers(), timeout=30)
        if resp.status_code != 200:
            logger.warning(f"Poll failed [{resp.status_code}], retrying...")
            continue

        data = resp.json()
        logger.debug(f"Poll [{elapsed}s]: done={data.get('done', False)}")

        if data.get("done"):
            if "error" in data:
                raise RuntimeError(f"Veo 3 generation error: {data['error']}")
            return data

    raise TimeoutError(f"Veo 3 operation timed out after {MAX_POLL_SECONDS}s")


def extract_video_uris(operation_result: dict) -> list[str]:
    """Estrae gli URI GCS dei video dal risultato dell'operazione."""
    response = operation_result.get("response", {})

    # Struttura tipica Vertex AI video generation
    predictions = response.get("predictions", [])
    uris = []
    for pred in predictions:
        # Formato: {"bytesBase64Encoded": "...", "mimeType": "video/mp4"}
        # oppure: {"gcsUri": "gs://..."}
        if "gcsUri" in pred:
            uris.append(pred["gcsUri"])
        elif "video" in pred:
            uris.append(pred["video"].get("gcsUri", ""))

    if not uris:
        # Fallback: cerca ricorsivamente qualsiasi gcsUri
        raw = json.dumps(operation_result)
        import re
        uris = re.findall(r'"gcsUri"\s*:\s*"(gs://[^"]+)"', raw)

    return [u for u in uris if u]


def download_video(gcs_uri: str, output_path: Path) -> Path:
    """Scarica video da GCS a path locale."""
    from google.cloud import storage

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Parsa gs://bucket/path
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
    req: Veo3Request,
    output_dir: Path,
    clip_name: str = "clip"
) -> Veo3Result:
    """
    End-to-end: invia prompt, aspetta, scarica i video.
    Ritorna Veo3Result con path locali.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Submit
    operation_name = submit_generation(req)

    # Poll fino al completamento
    logger.info("Waiting for generation...")
    result = poll_operation(operation_name)

    # Estrai URI
    video_uris = extract_video_uris(result)
    if not video_uris:
        raise RuntimeError(f"No video URIs in result: {result}")

    # Download tutti i sample
    local_paths = []
    for i, uri in enumerate(video_uris):
        path = output_dir / f"{clip_name}_v{i+1}.mp4"
        download_video(uri, path)
        local_paths.append(path)

    return Veo3Result(
        operation_name=operation_name,
        video_uris=video_uris,
        local_paths=local_paths,
        duration_seconds=req.duration_seconds,
        prompt=req.prompt,
    )


def generate_clips_batch(
    requests_list: list[Veo3Request],
    output_dir: Path,
    verticale: str,
    concurrent: bool = False,
) -> list[Veo3Result]:
    """
    Genera più clip in sequenza (o concorrente se concurrent=True).
    Rate limit Veo 3: max 3 req/min in preview.
    """
    results = []

    if concurrent:
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
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
            # Rate limiting — Veo 3 preview: ~1 req/20s
            if i < len(requests_list) - 1:
                logger.info("Rate limit pause (20s)...")
                time.sleep(20)

    return results


# ─── CLI test ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Test Veo 3 single clip")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--ratio", default="9:16")
    parser.add_argument("--duration", type=int, default=8)
    parser.add_argument("--output", default="./output/test")
    args = parser.parse_args()

    req = Veo3Request(
        prompt=args.prompt,
        aspect_ratio=args.ratio,
        duration_seconds=args.duration,
    )

    result = generate_clip(req, Path(args.output), "test_clip")
    print(f"\nGenerati {len(result.local_paths)} video:")
    for p in result.local_paths:
        print(f"  {p}")
