#!/usr/bin/env python3
"""Regenerate V16_sara_intro with ultra-aggressive anti-film prompt."""

import json, subprocess, base64, time, urllib.request
from pathlib import Path

OUTPUT_DIR = Path("/Volumes/MontereyT7/FLUXION/landing/assets/ai-clips-v2")
PROJECT = "project-07c591f2-ed4e-4865-8af"
LOCATION = "us-central1"
MODEL = "veo-3.0-generate-001"

# Back up old clip
old = OUTPUT_DIR / "V16_sara_intro.mp4"
if old.exists():
    old.rename(OUTPUT_DIR / "V16_sara_intro_OLD.mp4")

PROMPT = """Medium close-up shot of a stunningly beautiful Italian woman in her early 30s. She has captivating warm brown eyes and dark wavy hair falling softly past her shoulders with radiant olive skin. She wears a sleek modern wireless headset and a fitted elegant cream blouse. She sits at a modern minimalist desk and looks directly at camera with a magnetic warm confident smile. Behind her is a modern office with soft green plants and warm natural light streaming through sheer curtains. Golden hour Mediterranean lighting. Shallow depth of field. The image is shot on a modern digital cinema camera with clean sharp digital look. The frame is completely full with no borders, no letterboxing, no black bars, no film strip edges. Clean modern digital video production."""

NEGATIVE = "film grain, film strip, sprocket holes, film borders, letterbox, black bars, vintage effect, analog, VHS, old film, scratches, dust, vignette, sepia, retro, border, frame edge, Kodak, celluloid, 35mm film, movie border, cinematic bars, pillarbox, matte bars"

def get_token():
    r = subprocess.run(["/usr/local/share/google-cloud-sdk/bin/gcloud", "auth", "print-access-token"],
                       capture_output=True, text=True)
    return r.stdout.strip()

def generate():
    token = get_token()
    url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/{LOCATION}/publishers/google/models/{MODEL}:predictLongRunning"
    body = json.dumps({
        "instances": [{"prompt": PROMPT}],
        "parameters": {"aspectRatio": "16:9", "personGeneration": "allow_all", "generateAudio": False, "negativePrompt": NEGATIVE}
    }).encode()
    req = urllib.request.Request(url, data=body,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
    op_name = result.get("name", "")
    print(f"Op: ...{op_name[-30:]}")

    fetch_url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/{LOCATION}/publishers/google/models/{MODEL}:fetchPredictOperation"
    for i in range(40):
        time.sleep(15)
        token = get_token()
        fetch_body = json.dumps({"operationName": op_name}).encode()
        fetch_req = urllib.request.Request(fetch_url, data=fetch_body,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(fetch_req) as resp:
            status = json.loads(resp.read())
        if not status.get("done", False):
            print(f"  [{(i+1)*15}s] generating...")
            continue
        videos = status.get("response", {}).get("videos", [])
        if videos and videos[0].get("bytesBase64Encoded"):
            fname = OUTPUT_DIR / "V16_sara_intro.mp4"
            data = base64.b64decode(videos[0]["bytesBase64Encoded"])
            with open(fname, "wb") as f:
                f.write(data)
            print(f"SAVED: {fname.name} ({len(data)/1024/1024:.1f} MB)")
            return True
        print(f"Error: {status.get('error', 'empty')}")
        return False
    print("TIMEOUT")
    return False

print("Regenerating V16_sara_intro (anti-film borders)...")
generate()
