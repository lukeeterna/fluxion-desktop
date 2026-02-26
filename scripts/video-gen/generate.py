#!/usr/bin/env python3
"""
Fluxion Demo Video Generator — Hailuo 02 / MiniMax
Supporta due provider:
  - aimlapi  (default) — richiede verifica carta su https://aimlapi.com/app/verification
  - replicate         — $0.05 free credits su https://replicate.com

Uso:
  python3 scripts/video-gen/generate.py                     # aimlapi (default)
  python3 scripts/video-gen/generate.py --provider replicate
  python3 scripts/video-gen/generate.py --dry-run           # no API calls
  python3 scripts/video-gen/generate.py --scene S01         # solo una scena

Keys in .env:
  AIMLAPI_KEY=...
  REPLICATE_API_TOKEN=...

Output: /tmp/fluxion-video/
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

# ─── Config ───────────────────────────────────────────────────────────────────
PROMPTS_FILE  = Path(__file__).parent / "prompts.json"
OUTPUT_DIR    = Path("/tmp/fluxion-video")
POLL_INTERVAL = 10
MAX_WAIT      = 360
ENV_FILE      = Path(__file__).parents[2] / ".env"

PROVIDERS = {
    "aimlapi": {
        "post_url":    "https://api.aimlapi.com/v2/video/generations",
        "poll_url":    "https://api.aimlapi.com/v2/video/generations?generation_id={id}",
        "auth_header": "Authorization",
        "auth_prefix": "Bearer ",
        "env_key":     "AIMLAPI_KEY",
        "model":       "minimax/hailuo-2.3",
    },
    "replicate": {
        "post_url":    "https://api.replicate.com/v1/models/minimax/video-01/predictions",
        "poll_url":    "https://api.replicate.com/v1/predictions/{id}",
        "auth_header": "Authorization",
        "auth_prefix": "Token ",
        "env_key":     "REPLICATE_API_TOKEN",
        "model":       "minimax/video-01",
    },
}
# ──────────────────────────────────────────────────────────────────────────────


def load_env(path: Path) -> dict:
    env = {}
    if not path.exists():
        return env
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()
    return env


def get_key(provider: str) -> str:
    cfg = PROVIDERS[provider]
    key = os.environ.get(cfg["env_key"], "")
    if key:
        return key
    return load_env(ENV_FILE).get(cfg["env_key"], "")


def build_payload(scene: dict, provider: str) -> dict:
    if provider == "aimlapi":
        return {
            "model":          PROVIDERS["aimlapi"]["model"],
            "prompt":         scene["prompt"],
            "resolution":     "1080P",
            "duration":       scene.get("duration", 6),
            "enhance_prompt": True,
        }
    elif provider == "replicate":
        return {
            "input": {
                "prompt":   scene["prompt"],
                "duration": scene.get("duration", 6),
            }
        }
    raise ValueError(f"Provider sconosciuto: {provider}")


def http_post(url: str, payload: dict, key: str, provider: str) -> dict:
    cfg  = PROVIDERS[provider]
    data = json.dumps(payload).encode()
    req  = urllib.request.Request(
        url, data=data,
        headers={
            cfg["auth_header"]: cfg["auth_prefix"] + key,
            "Content-Type": "application/json",
            "User-Agent": "FluxionVideoGen/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def http_get(url: str, key: str, provider: str) -> dict:
    cfg = PROVIDERS[provider]
    req = urllib.request.Request(
        url,
        headers={cfg["auth_header"]: cfg["auth_prefix"] + key},
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def extract_status_and_url(resp: dict, provider: str):
    if provider == "aimlapi":
        status    = resp.get("status", "unknown")
        output    = resp.get("output")
        video_url = (
            resp.get("video_url")
            or (output.get("video_url") if isinstance(output, dict) else None)
            or (output[0] if isinstance(output, list) and output else None)
        )
        return status, video_url
    elif provider == "replicate":
        status    = resp.get("status", "unknown")   # starting / processing / succeeded / failed
        output    = resp.get("output")
        video_url = output if isinstance(output, str) else None
        # map replicate stati → nostri stati
        if status == "succeeded":
            status = "completed"
        elif status in ("starting", "processing"):
            status = "pending"
        return status, video_url
    return "unknown", None


def download_video(url: str, dest: Path):
    req = urllib.request.Request(url, headers={"User-Agent": "FluxionVideoGen/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        dest.write_bytes(resp.read())


def generate_scene(scene: dict, key: str, provider: str) -> Path | None:
    sid  = scene["id"]
    name = scene["name"]
    dest = OUTPUT_DIR / f"{sid}_{name}.mp4"

    if dest.exists():
        print(f"  ⏭️  {sid} già presente, skip.")
        return dest

    cfg     = PROVIDERS[provider]
    payload = build_payload(scene, provider)
    print(f"  📤 Invio {sid} — '{name}' [{provider}]...")

    try:
        resp = http_post(cfg["post_url"], payload, key, provider)
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  ❌ HTTP {e.code}: {body[:300]}")
        if "unverified_card" in body:
            print("  ⚠️  Account non verificato → vai su https://aimlapi.com/app/verification")
        return None

    gen_id = resp.get("id") or resp.get("generation_id")
    if not gen_id:
        print(f"  ❌ Risposta inattesa: {resp}")
        return None

    poll_url = cfg["poll_url"].format(id=gen_id)
    print(f"  ⏳ ID: {gen_id} — polling ogni {POLL_INTERVAL}s...")

    elapsed = 0
    while elapsed < MAX_WAIT:
        time.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL

        try:
            status_resp = http_get(poll_url, key, provider)
        except Exception as ex:
            print(f"  ⚠️  Poll error: {ex}")
            continue

        status, video_url = extract_status_and_url(status_resp, provider)
        print(f"     [{elapsed:>3}s] status={status}")

        if status == "completed" and video_url:
            print(f"  ⬇️  Download {sid}...")
            download_video(video_url, dest)
            mb = dest.stat().st_size / 1_000_000
            print(f"  ✅ {sid} salvato ({mb:.1f} MB): {dest}")
            return dest

        if status in ("failed", "error"):
            err = status_resp.get("error") or status_resp.get("message", "?")
            print(f"  ❌ {sid} fallito: {err}")
            return None

    print(f"  ⏰ Timeout {sid} dopo {MAX_WAIT}s")
    return None


def write_concat_file(files: list[Path]) -> Path:
    f = OUTPUT_DIR / "concat.txt"
    f.write_text("\n".join(f"file '{p.absolute()}'" for p in files) + "\n")
    return f


def ffmpeg_concat(concat_file: Path, output: Path) -> bool:
    cmd = (
        f"ffmpeg -y -f concat -safe 0 -i '{concat_file}' "
        f"-c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p "
        f"-movflags +faststart '{output}' 2>&1"
    )
    return os.system(cmd) == 0


def dry_run(scenes, order, provider):
    print("=" * 62)
    print(f"  DRY-RUN [{provider}] — nessuna chiamata API")
    print("=" * 62)
    for s in scenes:
        if s["id"] not in order:
            continue
        payload = build_payload(s, provider)
        print(f"\n── {s['id']}: {s['name']} ──")
        print(f"  caption : {s.get('caption','')}")
        print(f"  payload :\n{json.dumps(payload, indent=4, ensure_ascii=False)}")
        print(f"  chars   : {len(s['prompt'])}/2000")
    print("\n" + "=" * 62)
    print(f"  Scene totali : {len([s for s in scenes if s['id'] in order])}")
    print(f"  Provider     : {provider}")
    print(f"  Model        : {PROVIDERS[provider]['model']}")
    print(f"  Stima tempo  : ~{len(order)*2}-{len(order)*4} min")
    print("=" * 62)


def main():
    args     = sys.argv[1:]
    is_dry   = "--dry-run" in args
    provider = "aimlapi"
    only_sid = None

    if "--provider" in args:
        idx      = args.index("--provider")
        provider = args[idx + 1] if idx + 1 < len(args) else "aimlapi"
    if "--scene" in args:
        idx      = args.index("--scene")
        only_sid = args[idx + 1] if idx + 1 < len(args) else None

    if provider not in PROVIDERS:
        print(f"❌ Provider '{provider}' sconosciuto. Usa: {list(PROVIDERS.keys())}")
        sys.exit(1)

    with open(PROMPTS_FILE) as f:
        config = json.load(f)
    scenes = config["scenes"]
    order  = config.get("concat_order", [s["id"] for s in scenes])
    if only_sid:
        order = [only_sid]

    if is_dry:
        dry_run(scenes, order, provider)
        return

    key = get_key(provider)
    if not key:
        cfg = PROVIDERS[provider]
        print(f"❌ {cfg['env_key']} non trovata in .env o ambiente.")
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    masked = key[:6] + "..." + key[-4:] if len(key) > 10 else "****"
    print(f"🎬 Fluxion Demo Video Generator")
    print(f"   Provider : {provider} | Model: {PROVIDERS[provider]['model']}")
    print(f"   API key  : {masked}")
    print(f"   Scene    : {order}")
    print(f"   Output   : {OUTPUT_DIR}")
    print()

    generated: dict[str, Path] = {}
    for scene in scenes:
        sid = scene["id"]
        if sid not in order:
            continue
        print(f"── {sid}: {scene['name']} ──")
        result = generate_scene(scene, key, provider)
        if result:
            generated[sid] = result
        print()

    print("─" * 50)
    ok  = [s for s in order if s in generated]
    bad = [s for s in order if s not in generated]
    print(f"✅ Generate: {len(ok)}/{len(order)} — {ok}")
    if bad:
        print(f"❌ Fallite : {bad}")

    if len(ok) < 2:
        print("⚠️  Troppo poche scene per il concat.")
        return

    files       = [generated[s] for s in order if s in generated]
    concat_file = write_concat_file(files)
    final       = OUTPUT_DIR / "demo_final.mp4"

    print(f"\n🎞️  Concatenazione ffmpeg...")
    if ffmpeg_concat(concat_file, final):
        mb = final.stat().st_size / 1_000_000
        print(f"\n🏆 VIDEO FINALE: {final}  ({mb:.1f} MB)")
        print(f"\nProssimi passi:")
        print(f"  1. open {final}")
        print(f"  2. Aggiungi musica in iMovie")
        print(f"  3. Carica YouTube (non in elenco)")
        print(f"  4. Invia link a LemonSqueezy")
    else:
        print("❌ ffmpeg concat fallito — file singoli in /tmp/fluxion-video/")


if __name__ == "__main__":
    main()
