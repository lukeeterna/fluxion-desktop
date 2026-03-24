#!/usr/bin/env python3
"""
FLUXION V5 — Generate all AI video clips via Google Veo 3.0 (Vertex AI)
Reads prompts from video-production-v5.json, generates clips, saves to landing/assets/ai-clips/
"""

import json
import subprocess
import base64
import time
import os
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
STORYBOARD = BASE / "scripts" / "video-production-v5.json"
OUTPUT_DIR = BASE / "landing" / "assets" / "ai-clips"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PROJECT = "project-07c591f2-ed4e-4865-8af"
LOCATION = "us-central1"
MODEL = "veo-3.0-generate-001"


def get_token():
    r = subprocess.run(
        ["/usr/local/share/google-cloud-sdk/bin/gcloud", "auth", "print-access-token"],
        capture_output=True, text=True
    )
    return r.stdout.strip()


def generate_video(prompt, clip_id):
    """Submit video generation and poll for result."""
    token = get_token()
    url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/{LOCATION}/publishers/google/models/{MODEL}:predictLongRunning"

    body = json.dumps({
        "instances": [{"prompt": prompt}],
        "parameters": {
            "aspectRatio": "16:9",
            "personGeneration": "allow_all",
            "generateAudio": True
        }
    }).encode()

    req = urllib.request.Request(url, data=body,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST")

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
    except Exception as e:
        print(f"    ERROR submitting: {e}")
        return None

    op_name = result.get("name", "")
    if not op_name:
        print(f"    ERROR: no operation name. Response: {result}")
        return None

    print(f"    Operation: {op_name.split('/')[-1][:16]}...")

    # Poll with fetchPredictOperation
    fetch_url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/{LOCATION}/publishers/google/models/{MODEL}:fetchPredictOperation"

    for i in range(30):
        time.sleep(15)
        token = get_token()  # refresh token
        fetch_body = json.dumps({"operationName": op_name}).encode()
        fetch_req = urllib.request.Request(fetch_url, data=fetch_body,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            method="POST")

        try:
            with urllib.request.urlopen(fetch_req) as resp:
                status = json.loads(resp.read())
        except Exception as e:
            print(f"    [{(i+1)*15}s] poll error: {e}")
            continue

        done = status.get("done", False)
        if not done:
            print(f"    [{(i+1)*15}s] generating...")
            continue

        # Done — extract video
        videos = status.get("response", {}).get("videos", [])
        if videos:
            b64 = videos[0].get("bytesBase64Encoded", "")
            if b64:
                fname = OUTPUT_DIR / f"{clip_id}.mp4"
                video_bytes = base64.b64decode(b64)
                with open(fname, "wb") as f:
                    f.write(video_bytes)
                size_mb = len(video_bytes) / 1024 / 1024
                print(f"    SAVED: {fname.name} ({size_mb:.1f} MB)")
                return str(fname)

        # Check for errors
        error = status.get("error", {})
        if error:
            print(f"    ERROR: {error}")
        else:
            print(f"    No video in response")
        return None

    print(f"    TIMEOUT after 7.5 min")
    return None


def main():
    with open(STORYBOARD) as f:
        storyboard = json.load(f)

    # Collect all AI video scenes
    ai_scenes = []
    for chapter in storyboard["chapters"]:
        for scene in chapter["scenes"]:
            if scene["type"] == "ai_video":
                ai_scenes.append(scene)

    print("=" * 60)
    print(f"  FLUXION V5 — AI Clip Generation")
    print(f"  Model: Veo 3.0 | Clips: {len(ai_scenes)}")
    print(f"  Estimated cost: ~${len(ai_scenes) * 8 * 0.10:.1f}")
    print("=" * 60)

    results = {}
    total_cost = 0

    for i, scene in enumerate(ai_scenes):
        clip_id = scene["id"]
        prompt = scene["prompt"]
        duration = scene.get("duration", 8)

        # Skip if already generated
        existing = OUTPUT_DIR / f"{clip_id}.mp4"
        if existing.exists() and existing.stat().st_size > 100000:
            print(f"\n[{i+1}/{len(ai_scenes)}] {clip_id} — ALREADY EXISTS, skipping")
            results[clip_id] = str(existing)
            continue

        print(f"\n[{i+1}/{len(ai_scenes)}] {clip_id}")
        print(f"    Prompt: {prompt[:80]}...")

        result = generate_video(prompt, clip_id)
        if result:
            results[clip_id] = result
            est_cost = duration * 0.10
            total_cost += est_cost
            print(f"    Est. cost: ~${est_cost:.2f} (running total: ${total_cost:.2f})")
        else:
            print(f"    FAILED — will retry later")

        # Small delay between requests to avoid rate limiting
        if i < len(ai_scenes) - 1:
            time.sleep(5)

    # Summary
    print("\n" + "=" * 60)
    print(f"  RESULTS: {len(results)}/{len(ai_scenes)} clips generated")
    print(f"  Estimated total cost: ~${total_cost:.2f}")
    print(f"  Output: {OUTPUT_DIR}")

    failed = [s["id"] for s in ai_scenes if s["id"] not in results]
    if failed:
        print(f"  FAILED: {', '.join(failed)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
