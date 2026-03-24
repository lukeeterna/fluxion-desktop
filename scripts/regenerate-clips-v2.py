#!/usr/bin/env python3
"""
FLUXION V5 — Regenerate ALL AI clips with OPTIMIZED Veo 3 prompts.
Fixes: NO film borders, NO Kodak, clean digital look, generateAudio=false.
"""

import json, subprocess, base64, time, os, urllib.request
from pathlib import Path

OUTPUT_DIR = Path("/Volumes/MontereyT7/FLUXION/landing/assets/ai-clips-v2")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PROJECT = "project-07c591f2-ed4e-4865-8af"
LOCATION = "us-central1"
MODEL = "veo-3.0-generate-001"

# OPTIMIZED PROMPTS — Clean digital, NO film borders, NO Kodak
CLIPS = [
    {
        "id": "V01_salone",
        "prompt": "Medium shot of a busy hair salon during morning rush. A 38-year-old woman with shoulder-length brown hair wearing a fitted black cotton apron carefully cuts a female client's hair with professional scissors. Two other women sit in waiting chairs nearby, one reading a magazine, one checking her phone. Another stylist blow-dries hair in the background. Warm natural daylight streams through large windows. Modern salon interior with white walls, wood accents, large mirrors, professional products on shelves. A smartphone on the marble counter starts buzzing with an incoming call, screen lighting up. She glances at it with a stressed expression but cannot answer, both hands occupied. Camera: static tripod, slight shallow depth of field, eye-level. Style: clean digital cinematography, professional production, modern warm color grade, crisp and sharp. No film grain, no vintage effects."
    },
    {
        "id": "V02_officina",
        "prompt": "Low angle shot of a male auto mechanic in his late 40s with gray-streaked dark hair, wearing navy blue work coveralls, leaning under a raised car on a hydraulic lift. His hands are covered in dark grease, holding a ratchet wrench. Small family workshop with red tool cabinet, car posters on wall, concrete floor. Warm afternoon sunlight from the open garage door. Another car parked outside waiting. His phone in his chest pocket starts vibrating. He tries to reach it but his hands are too greasy, wipes his forehead with his forearm in frustration. Camera: low angle looking up, slow dolly out, shallow depth of field. Style: clean digital cinematography, professional production, natural warm tones. No film grain, no vintage effects, no film borders."
    },
    {
        "id": "V03_dentista",
        "prompt": "Over-the-shoulder shot of a female dentist in her mid-30s wearing a white coat, examining a patient reclined in a modern dental chair. Gloved hands holding a dental mirror and probe, focused expression. Modern dental studio with clean white walls, blue LED overhead light, digital X-ray screen showing teeth in background, small plant on windowsill. Her smartphone on the instrument tray vibrates, screen lighting up with an incoming call. She cannot break the sterile procedure, glances with slight concern. Camera: over-shoulder, gentle rack focus from hands to buzzing phone. Style: clean digital cinematography, modern clinical look, warm neutral palette with blue accents. No film grain, no vintage effects."
    },
    {
        "id": "V04_palestra",
        "prompt": "Wide shot of a modern gym. A 32-year-old athletic male trainer with short dark hair wearing a dark polo shirt spots a female client doing barbell squats. He stands behind her, hands ready to assist, encouraging expression. Two other gym members visible in background, one on treadmill, one lifting dumbbells. Modern gym with exposed brick accent wall, rubber flooring, large windows with natural daylight. His phone in a gym bag on the floor starts buzzing and lighting up. He cannot leave his client mid-set. Camera: wide establishing shot, slight pan toward the buzzing phone. Style: clean digital cinematography, energetic modern feel, natural warm lighting. No film grain, no vintage effects."
    },
    {
        "id": "V05_estetista",
        "prompt": "Close-up of a female beauty therapist in her late 30s with gentle expression, performing a facial treatment on a client lying on a white treatment bed. Her hands gently apply cream in circular motions. Intimate beauty center with soft warm lighting, rolled white towels, essential oil bottles, small candles, soft green plant accents. Her phone on a wooden side table buzzes softly, screen glowing. She maintains calm professional focus. Camera: close-up, slow gentle drift, ultra-shallow depth of field. Style: clean digital cinematography, soft warm lighting, spa atmosphere, crisp detail. No film grain, no vintage effects."
    },
    {
        "id": "V06_nails",
        "prompt": "Extreme close-up of a female nail artist in her late 20s with steady hands, performing intricate gel nail art with an ultra-fine brush on a client's fingernail. Client's hand is perfectly still under a bright LED task lamp. Clean nail studio with white and dusty pink decor, organized gel polish collections in acrylic display. Her phone on the workspace vibrates loudly. She cannot lift her brush, quick frustrated glance. Camera: macro close-up pulling back slowly to medium shot. Style: clean digital cinematography, bright warm lighting, crisp detail on precision work. No film grain, no vintage effects."
    },
    {
        "id": "V07_fisioterapista",
        "prompt": "Medium shot of a male physiotherapist in his early 40s wearing a white polo shirt, performing manual therapy on a patient's shoulder and neck. Strong careful hands pressing and manipulating the shoulder joint with practiced precision. Patient lying face-down on a treatment bed. Professional physiotherapy studio with anatomical poster on wall, resistance bands, warm wood floor, framed diplomas. His phone on a shelf starts vibrating with an incoming call. Both hands are engaged, he cannot stop. Camera: medium shot, gentle dolly-in toward his focused hands. Style: clean digital cinematography, warm earth tones, professional medical atmosphere. No film grain, no vintage effects."
    },
    {
        "id": "V08_gommista",
        "prompt": "Medium shot of a male tire technician in his 40s wearing dirty blue coveralls, using a pneumatic impact wrench to remove wheel nuts from a car on a lift. Dynamic action scene. Tire shop with stacks of tires along walls, air compressor, tire balancing machine. Both hands locked on the wrench, phone ringing on metal workbench, he cannot stop. Camera: dynamic medium shot, slight handheld feel, capturing the energy. Style: clean digital cinematography, natural industrial lighting, modern color grade. No film grain, no vintage effects, no film borders."
    },
    {
        "id": "V09_elettrauto",
        "prompt": "Close-up of a male auto electrician in his late 50s with reading glasses, carefully testing a wiring harness with a yellow digital multimeter. One hand holds colored wires, the other a multimeter probe. Small specialized workshop with oscilloscope screen showing waveforms, wire spools organized by color, diagnostic computer, coffee cup on bench. His phone lights up and buzzes on the counter. He cannot interrupt his precision work. Camera: close-up at workbench level, static, shallow depth of field. Style: clean digital cinematography, warm tungsten workshop lighting, modern technical atmosphere. No film grain, no vintage effects."
    },
    {
        "id": "V10_frustrazione",
        "prompt": "Medium shot of a woman in her early 40s sitting alone at a salon reception desk after hours. Evening blue-golden light through the window. She looks at her phone showing multiple missed calls on the screen. Tired expression, rubbing her temples with one hand. Empty salon chairs behind her, closed sign on the door. She sighs and puts the phone down. This is the weight of running everything alone. Camera: intimate medium shot, slow push-in on her worried face. Style: clean digital cinematography, melancholic blue-golden evening tones, emotional lighting. No film grain, no vintage effects."
    },
    {
        "id": "V11_qrcode",
        "prompt": "Close-up of a young woman's hands holding a modern smartphone, scanning a QR code on an elegant small acrylic stand sitting on a marble salon reception counter. The phone screen lights up showing a messaging conversation starting. In the blurred background, a hairdresser works on another client. Warm salon interior with golden afternoon light. The customer looks pleased. Camera: close-up of phone and QR code, gentle tilt up to her smiling face. Style: clean digital cinematography, warm natural tones, modern feel. No film grain, no vintage effects."
    },
    {
        "id": "V12_soddisfatta",
        "prompt": "Medium shot of a satisfied female business owner in her early 40s with brown hair, sitting relaxed at a clean modern reception desk with a laptop open. She smiles warmly, genuinely happy, looking at the laptop screen. Her salon is quiet, end of a successful day. Beautiful golden sunset light through the window. Clean desk with a coffee cup and small flower vase. She looks content and in control, no stress. Her phone on the desk shows zero missed calls. Camera: warm medium shot, slow gentle dolly-in to her satisfied expression. Style: clean digital cinematography, warm golden sunset tones, hopeful atmosphere. No film grain, no vintage effects."
    },
    {
        "id": "V13_finale",
        "prompt": "Quick montage sequence with soft transitions. First: a female hairdresser smiling while cutting hair, relaxed and happy. Second: a male mechanic wiping clean hands with a cloth, looking satisfied. Third: a female dentist removing gloves after a successful treatment, smiling. Fourth: a male trainer high-fiving his client after a great workout. All professionals are calm, happy, and in control. No stress, no ringing phones. Beautiful warm natural lighting in each shot. Camera: series of medium shots with soft focus transitions between each person. Style: clean digital cinematography, warm optimistic tones, professional modern look. No film grain, no vintage effects."
    }
]


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
            "negativePrompt": "film grain, film strip, sprocket holes, film borders, letterbox bars, vintage effect, analog noise, VHS, old film, scratches, dust particles, vignette, sepia tone, retro filter"
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

    print(f"    Op: ...{op_name[-20:]}")

    fetch_url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{PROJECT}/locations/{LOCATION}/publishers/google/models/{MODEL}:fetchPredictOperation"

    for i in range(30):
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

        print(f"    No video or error: {status.get('error', 'empty')}")
        return None

    print(f"    TIMEOUT")
    return None


def main():
    print("=" * 60)
    print("  FLUXION V5 — AI Clips V2 (Clean Digital, No Film Borders)")
    print(f"  Clips: {len(CLIPS)} | Audio: OFF (saves credits)")
    print(f"  Est. cost: ~${len(CLIPS) * 8 * 0.10:.1f} (generateAudio=false)")
    print("=" * 60)

    ok = 0
    fail = []
    for i, clip in enumerate(CLIPS):
        existing = OUTPUT_DIR / f"{clip['id']}.mp4"
        if existing.exists() and existing.stat().st_size > 100000:
            print(f"\n[{i+1}/{len(CLIPS)}] {clip['id']} — EXISTS, skip")
            ok += 1
            continue

        print(f"\n[{i+1}/{len(CLIPS)}] {clip['id']}")
        if generate(clip["prompt"], clip["id"]):
            ok += 1
        else:
            fail.append(clip["id"])
        if i < len(CLIPS) - 1:
            time.sleep(3)

    print(f"\n{'='*60}")
    print(f"  DONE: {ok}/{len(CLIPS)} | Failed: {len(fail)}")
    if fail:
        print(f"  Failed: {', '.join(fail)}")
    print(f"  Output: {OUTPUT_DIR}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
