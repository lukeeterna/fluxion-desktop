#!/usr/bin/env python3
"""
FLUXION V7 — Generate 5 new Veo3 clips for Video V7.
Sara (volto), Cliente (volto), Medico+paziente, Portfolio foto.
"""

import json, subprocess, base64, time, urllib.request
from pathlib import Path

OUTPUT_DIR = Path("/Volumes/MontereyT7/FLUXION/landing/assets/ai-clips-v2")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PROJECT = "project-07c591f2-ed4e-4865-8af"
LOCATION = "us-central1"
MODEL = "veo-3.0-generate-001"

CLIPS = [
    {
        "id": "V16_sara_intro",
        "prompt": "Stunningly beautiful Italian woman in her early 30s, captivating warm brown eyes, dark wavy hair falling softly past her shoulders, radiant olive skin, wearing a sleek modern wireless headset, fitted elegant blouse in soft cream color, sitting at a modern minimalist desk, looking directly at camera with a magnetic smile that is simultaneously warm, confident, subtly alluring and deeply reassuring, she radiates the energy of someone you instantly trust and want to talk to, modern office with soft green plants and warm natural light streaming through sheer curtains, golden hour Mediterranean lighting, shallow depth of field, medium close-up shot. Style: clean digital cinematography, professional production, warm golden tones, crisp and sharp. No film grain, no vintage effects, no film borders."
    },
    {
        "id": "V17_sara_dialogo",
        "prompt": "Same stunningly beautiful Italian woman in her early 30s with dark wavy hair and wireless headset, actively speaking on a phone call with naturally expressive face, her eyes light up as she recognizes the caller, warm genuine smile, she gestures elegantly with one hand while speaking, nodding reassuringly with perfect composure and warmth, her manner is both professionally competent and personally caring, same modern office with golden natural light, close-up to medium shot. The viewer feels instantly reassured just watching her. Style: clean digital cinematography, warm golden tones, cinematic documentary. No film grain, no vintage effects, no film borders."
    },
    {
        "id": "V18_cliente_telefono",
        "prompt": "Handsome Italian man in his late 30s, well-groomed dark hair and short beard, wearing a fitted casual blazer over a crisp white shirt, talking on his smartphone with a slightly impatient but polite expression, he is busy and demanding but not rude, standing in a bright modern Italian street or cafe terrace, warm Mediterranean daylight, his expression gradually softens into a pleased smile as he gets the answer he wanted. Medium close-up shot, shallow depth of field. Style: clean digital cinematography, warm natural Mediterranean tones, professional production. No film grain, no vintage effects, no film borders."
    },
    {
        "id": "V14_medico_paziente",
        "prompt": "Interior of a modern Italian medical clinic. A male doctor in his mid-40s wearing a white coat carefully examines a patient sitting on the exam table, focused and attentive, his hands are busy with the patient. A smartphone on the desk in the background glows with an incoming call he cannot answer. Warm natural light from a large window, clean professional environment with medical certificates on wall, potted plant. Medium shot, the scene conveys a doctor who is dedicated to his patient and cannot be interrupted. Style: clean digital cinematography, warm neutral clinical tones, professional medical atmosphere. No film grain, no vintage effects, no film borders."
    },
    {
        "id": "V15_foto_portfolio",
        "prompt": "Close-up of a woman's hands scrolling through a photo gallery on a modern tablet showing before and after beauty treatment results, the photos show dramatic hair color transformations. Warm golden ambient light, hair salon interior with soft bokeh in background, gentle natural scrolling movements, she pauses on one impressive result and smiles. Medium close-up pulling back to show her satisfied expression. Style: clean digital cinematography, warm golden tones, soft natural lighting. No film grain, no vintage effects, no film borders."
    },
]

NEGATIVE = "film grain, film strip, sprocket holes, film borders, letterbox bars, vintage effect, analog noise, VHS, old film, scratches, dust particles, vignette, sepia tone, retro filter"


def get_token():
    r = subprocess.run(
        ["/usr/local/share/google-cloud-sdk/bin/gcloud", "auth", "print-access-token"],
        capture_output=True, text=True)
    return r.stdout.strip()


def generate(prompt, clip_id):
    token = get_token()
    url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/{LOCATION}/publishers/google/models/{MODEL}:predictLongRunning"

    body = json.dumps({
        "instances": [{"prompt": prompt}],
        "parameters": {
            "aspectRatio": "16:9",
            "personGeneration": "allow_all",
            "generateAudio": False,
            "negativePrompt": NEGATIVE
        }
    }).encode()

    req = urllib.request.Request(url, data=body,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST")

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
    except Exception as e:
        print(f"    SUBMIT ERROR: {e}")
        return None

    op_name = result.get("name", "")
    if not op_name:
        print(f"    NO OP: {result}")
        return None

    print(f"    Op: ...{op_name[-30:]}")

    fetch_url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/{LOCATION}/publishers/google/models/{MODEL}:fetchPredictOperation"

    for i in range(40):
        time.sleep(15)
        token = get_token()
        fetch_body = json.dumps({"operationName": op_name}).encode()
        fetch_req = urllib.request.Request(fetch_url, data=fetch_body,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            method="POST")
        try:
            with urllib.request.urlopen(fetch_req) as resp:
                status = json.loads(resp.read())
        except Exception as e:
            print(f"    [{(i+1)*15}s] poll err: {e}")
            continue

        if not status.get("done", False):
            print(f"    [{(i+1)*15}s] generating...")
            continue

        videos = status.get("response", {}).get("videos", [])
        if videos and videos[0].get("bytesBase64Encoded"):
            fname = OUTPUT_DIR / f"{clip_id}.mp4"
            data = base64.b64decode(videos[0]["bytesBase64Encoded"])
            with open(fname, "wb") as f:
                f.write(data)
            print(f"    SAVED: {fname.name} ({len(data)/1024/1024:.1f} MB)")
            return str(fname)

        err = status.get("error", {})
        print(f"    No video: {err.get('message', 'empty response')}")
        return None

    print(f"    TIMEOUT after 10 min")
    return None


def main():
    print("=" * 60)
    print("  FLUXION V7 — 5 New Veo3 Clips")
    print(f"  Clips: {len(CLIPS)} | Audio: OFF")
    print("=" * 60)

    ok = 0
    fail = []
    for i, clip in enumerate(CLIPS):
        existing = OUTPUT_DIR / f"{clip['id']}.mp4"
        if existing.exists() and existing.stat().st_size > 100000:
            print(f"\n[{i+1}/{len(CLIPS)}] {clip['id']} — SKIP (already exists, {existing.stat().st_size/1024/1024:.1f}MB)")
            ok += 1
            continue

        print(f"\n[{i+1}/{len(CLIPS)}] {clip['id']} — generating...")
        result = generate(clip["prompt"], clip["id"])
        if result:
            ok += 1
        else:
            fail.append(clip["id"])

    print("\n" + "=" * 60)
    print(f"  DONE: {ok}/{len(CLIPS)} clips")
    if fail:
        print(f"  FAILED: {', '.join(fail)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
