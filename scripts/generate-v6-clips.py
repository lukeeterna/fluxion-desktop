#!/usr/bin/env python3
"""
FLUXION V6 — Generate 5 NEW AI clips for Video V6.
New clips not in V5: hook opening, satisfied owner, WhatsApp confirm, female entrepreneur, serene studio.
Lessons from V5: NO film grain/Kodak, generateAudio=False, "Shot on Arri Alexa" required.
"""

import json, subprocess, base64, time, os, urllib.request
from pathlib import Path

OUTPUT_DIR = Path("/Volumes/MontereyT7/FLUXION/landing/assets/ai-clips-v2")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PROJECT = "project-07c591f2-ed4e-4865-8af"
LOCATION = "us-central1"
MODEL = "veo-3.0-generate-001"

# V6 CRITICAL RULES:
# 1. Negative prompt updated with celluloid, distorted hands, extra fingers
# 2. "Shot on Arri Alexa" mandatory — calibrates tone mapping to digital NOT film
# 3. Physical light source — not generic "warm light" but "warm afternoon light from south-facing windows"
# 4. Explicit camera movement — "very slow dolly push-in" (avoid Steadicam/drone = CGI look)
# 5. 150-200 word prompts reduce randomness

NEGATIVE_PROMPT = (
    "film grain, film strip, film borders, sprocket holes, celluloid, Kodak Vision, "
    "letterbox bars, black bars, vignette, sepia, VHS, retro filter, vintage look, "
    "anime, cartoon, watermark, text overlay, blurry faces, distorted hands, "
    "extra fingers, deformed limbs, motion blur artifacts"
)

# 5 new V6 clips (V6- prefix to distinguish from V5 clips)
CLIPS = [
    {
        "id": "V6-03_proprietario_soddisfatto",
        "filename": "V6-03_proprietario_soddisfatto.mp4",
        "prompt": (
            "Cinematic medium shot, shot on Arri Alexa, 85mm f/1.8. "
            "Italian male small business owner in his mid-40s, sitting relaxed at a clean modern desk "
            "with a tablet showing business dashboard. He wears a casual blue button-down shirt, "
            "sleeves rolled up. Genuine warm smile, relaxed posture, leaning back slightly. "
            "Modern Italian office space with warm afternoon light from south-facing windows, "
            "potted plant, framed family photo on shelf. His expression says everything is under control. "
            "Very slow dolly push-in toward his satisfied face. "
            "Warm golden hour tones, shallow depth of field, natural skin tones."
        )
    },
    {
        "id": "V6-04_cliente_whatsapp",
        "filename": "V6-04_cliente_whatsapp.mp4",
        "prompt": (
            "Cinematic close-up to medium shot, shot on Arri Alexa, 50mm lens. "
            "Young Italian woman in her late 20s, casual chic outfit, sitting at a cafe table. "
            "She picks up her smartphone and reads a WhatsApp message confirmation. "
            "Her face lights up with a genuine smile of pleasant surprise. "
            "The phone screen shows a green WhatsApp notification. "
            "Warm Mediterranean cafe atmosphere with espresso cup and pastry on marble table, "
            "blurred street scene through window. Warm afternoon light from south-facing windows, "
            "natural Italian ambiance. Gentle camera tilt up from phone to her smiling face."
        )
    },
    {
        "id": "V6-05_imprenditrice_pc",
        "filename": "V6-05_imprenditrice_pc.mp4",
        "prompt": (
            "Cinematic medium shot, shot on Arri Alexa, 50mm f/2.0. "
            "Italian woman entrepreneur in her late 30s, confident posture, sitting at a modern desk "
            "with laptop open. She wears elegant but practical business casual. "
            "Her expression is calm, in complete control, slight satisfied smile. "
            "Clean organized workspace with a coffee mug, small plant, natural wood desk. "
            "Warm golden hour light streaming through south-facing windows creates rim lighting on her hair. "
            "Very slow dolly push-in. "
            "She represents the modern Italian female business owner who has it all under control."
        )
    },
    {
        "id": "V6-11_salone_sereno",
        "filename": "V6-11_salone_sereno.mp4",
        "prompt": (
            "Cinematic wide establishing shot, shot on Arri Alexa, 35mm lens. "
            "Beautiful Italian hair salon at end of day, golden sunset light streaming through large windows. "
            "The space is clean, organized, serene — chairs neatly arranged, products aligned on shelves, "
            "fresh flowers on reception counter. No people visible. "
            "The atmosphere says a well-run business at peace. "
            "Very slow dolly push-in through the space. "
            "Warm golden Mediterranean tones, dust particles floating in light beams, "
            "elegant Italian interior design."
        )
    },
    {
        "id": "V6-13_hook_missed_calls",
        "filename": "V6-13_hook_missed_calls.mp4",
        "prompt": (
            "Cinematic intimate close-up, shot on Arri Alexa, 85mm f/1.4, ultra-shallow depth of field. "
            "Italian woman small business owner in her early 40s, sitting alone at her reception desk "
            "in the evening. Blue-golden late evening light, melancholic mixed color temperature. "
            "She looks exhausted, rubbing her temple with one hand. "
            "Her phone on the desk shows FIVE MISSED CALLS notification, screen glowing in the dim light. "
            "Empty salon chairs behind her in soft focus. "
            "This is the weight of running everything alone. "
            "Very slow push-in on her worried face. Melancholic but warm color palette."
        )
    },
]


def get_token():
    r = subprocess.run(
        ["/usr/local/share/google-cloud-sdk/bin/gcloud", "auth", "print-access-token"],
        capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"gcloud auth failed: {r.stderr.strip()}")
    return r.stdout.strip()


def generate(prompt, clip_id, filename):
    token = get_token()
    url = (
        f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT}"
        f"/locations/{LOCATION}/publishers/google/models/{MODEL}:predictLongRunning"
    )

    body = json.dumps({
        "instances": [{"prompt": prompt}],
        "parameters": {
            "aspectRatio": "16:9",
            "personGeneration": "allow_all",
            "generateAudio": False,
            "negativePrompt": NEGATIVE_PROMPT
        }
    }).encode()

    req = urllib.request.Request(
        url, data=body,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
    except Exception as e:
        print(f"    SUBMIT ERROR: {e}")
        return None

    op_name = result.get("name", "")
    if not op_name:
        print(f"    NO OP returned: {result}")
        return None

    print(f"    Op: ...{op_name[-30:]}")

    fetch_url = (
        f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT}"
        f"/locations/{LOCATION}/publishers/google/models/{MODEL}:fetchPredictOperation"
    )

    for i in range(40):  # 40 x 15s = 10 minutes max
        time.sleep(15)
        token = get_token()
        fetch_body = json.dumps({"operationName": op_name}).encode()
        fetch_req = urllib.request.Request(
            fetch_url, data=fetch_body,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(fetch_req) as resp:
                status = json.loads(resp.read())
        except Exception as e:
            print(f"    [{(i+1)*15}s] poll error: {e}")
            continue

        if not status.get("done", False):
            print(f"    [{(i+1)*15}s] generating...")
            continue

        videos = status.get("response", {}).get("videos", [])
        if videos and videos[0].get("bytesBase64Encoded"):
            fname = OUTPUT_DIR / filename
            data = base64.b64decode(videos[0]["bytesBase64Encoded"])
            with open(fname, "wb") as f:
                f.write(data)
            size_mb = len(data) / 1024 / 1024
            print(f"    SAVED: {fname.name} ({size_mb:.1f} MB)")
            return str(fname)

        error = status.get("error", status.get("response", {}).get("raiFilteredReason", "empty response"))
        print(f"    No video in response: {error}")
        return None

    print(f"    TIMEOUT after {40*15}s")
    return None


def main():
    print("=" * 65)
    print("  FLUXION V6 — Generate 5 New AI Clips (Clean Digital Look)")
    print(f"  Model: {MODEL}")
    print(f"  Clips: {len(CLIPS)} | Audio: OFF | negativePrompt: updated")
    print(f"  Est. cost: ~${len(CLIPS) * 8 * 0.10:.1f} (no audio multiplier)")
    print(f"  Output: {OUTPUT_DIR}")
    print("=" * 65)

    ok = 0
    failed = []

    for i, clip in enumerate(CLIPS):
        output_path = OUTPUT_DIR / clip["filename"]

        if output_path.exists() and output_path.stat().st_size > 500_000:
            print(f"\n[{i+1}/{len(CLIPS)}] {clip['id']} — EXISTS ({output_path.stat().st_size / 1024:.0f} KB), skip")
            ok += 1
            continue

        print(f"\n[{i+1}/{len(CLIPS)}] Generating: {clip['id']}")
        print(f"    Prompt: {clip['prompt'][:80]}...")

        result = generate(clip["prompt"], clip["id"], clip["filename"])
        if result:
            ok += 1
        else:
            failed.append(clip["id"])

        if i < len(CLIPS) - 1:
            print("    Waiting 5s before next request...")
            time.sleep(5)

    print(f"\n{'=' * 65}")
    print(f"  RESULT: {ok}/{len(CLIPS)} clips generated successfully")
    if failed:
        print(f"  FAILED: {', '.join(failed)}")
    else:
        print(f"  All clips ready in: {OUTPUT_DIR}")
    print(f"{'=' * 65}")


if __name__ == "__main__":
    main()
