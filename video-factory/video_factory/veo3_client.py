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
VEO3_MODEL       = os.environ.get("VEO_MODEL", "veo-2.0-generate-001")  # veo-2.0 GA (veo-3.0-generate-preview richiede accesso speciale)
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
    Fa polling sull'operazione long-running via fetchPredictOperation.
    Ritorna il response body finale.
    """
    fetch_url = f"{BASE_URL}:fetchPredictOperation"

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
    Supporta sia base64 inline (Veo 2.0) che GCS URIs (Veo 3.0).
    Ritorna lista di path locali.
    """
    import base64

    response = operation_result.get("response", {})
    # Veo 2.0 GA usa "videos", Veo 3.0 preview usa "predictions"
    items = response.get("videos", []) or response.get("predictions", [])
    local_paths = []

    output_dir.mkdir(parents=True, exist_ok=True)

    for i, pred in enumerate(items):
        path = output_dir / f"{clip_name}_v{i+1}.mp4"

        # Formato 1: base64 inline (Veo 2.0 GA)
        if "bytesBase64Encoded" in pred:
            video_bytes = base64.b64decode(pred["bytesBase64Encoded"])
            path.write_bytes(video_bytes)
            size_mb = len(video_bytes) / (1024 * 1024)
            logger.info(f"Decoded base64 → {path.name} ({size_mb:.1f} MB)")
            local_paths.append(path)

        # Formato 2: GCS URI (Veo 3.0 preview)
        elif "gcsUri" in pred:
            _download_from_gcs(pred["gcsUri"], path)
            local_paths.append(path)

        # Formato 3: nested video object
        elif "video" in pred:
            video = pred["video"]
            if "bytesBase64Encoded" in video:
                video_bytes = base64.b64decode(video["bytesBase64Encoded"])
                path.write_bytes(video_bytes)
                local_paths.append(path)
            elif "gcsUri" in video:
                _download_from_gcs(video["gcsUri"], path)
                local_paths.append(path)

    # Fallback: cerca GCS URIs nel JSON raw
    if not local_paths:
        import re
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

    # Estrai e salva video (base64 o GCS)
    local_paths = extract_videos(result, output_dir, clip_name)
    if not local_paths:
        raise RuntimeError(f"No videos in result: {json.dumps(result)[:500]}")

    return Veo3Result(
        operation_name=operation_name,
        video_uris=[str(p) for p in local_paths],
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
