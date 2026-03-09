#!/usr/bin/env python3
"""
FLUXION — Download foto stock da Pexels (CC0, license-free)
Uso: python3 download-stock-photos.py <PEXELS_API_KEY>
"""

import os
import subprocess
import sys
import time
import urllib.request
import urllib.parse
import json
from pathlib import Path

# ── Config ─────────────────────────────────────────────────────────────────────

OUTPUT_BASE = Path(__file__).parent.parent / "_bmad-output" / "f06-media"

CATEGORIES = {
    "fitness": {
        "queries": ["personal trainer client gym", "fitness progress workout", "gym exercise training"],
        "n": 6,
        "orientation": "portrait",  # foto progress verticali
    },
    "fisioterapia": {
        "queries": ["physiotherapy session rehabilitation", "physical therapy exercise", "physio patient treatment"],
        "n": 6,
        "orientation": "landscape",
    },
    "odontoiatrica": {
        "queries": ["dental consultation smile", "dentist patient clinic", "dental hygiene teeth"],
        "n": 6,
        "orientation": "landscape",
    },
    "veicoli": {
        "queries": ["car repair mechanic workshop", "auto mechanic vehicle", "car body repair garage"],
        "n": 6,
        "orientation": "landscape",
    },
    "estetica": {
        "queries": ["beauty treatment facial spa", "aesthetics salon treatment", "skin care beauty"],
        "n": 5,
        "orientation": "landscape",
    },
    "parrucchiere": {
        "queries": ["hair salon hairstylist", "hair coloring salon", "hairdresser client"],
        "n": 5,
        "orientation": "landscape",
    },
    "medica": {
        "queries": ["doctor patient consultation", "medical clinic professional", "physician examination"],
        "n": 5,
        "orientation": "landscape",
    },
    "carrozzeria": {
        "queries": ["auto body repair paint", "car bodywork repair shop", "vehicle paint spray booth"],
        "n": 5,
        "orientation": "landscape",
    },
}

MAX_W = 1200  # non serve più grande per demo in-app

# ── API ────────────────────────────────────────────────────────────────────────

def pexels_search(api_key: str, query: str, per_page: int, orientation: str) -> list[dict]:
    q = urllib.parse.quote(query)
    url = f"https://api.pexels.com/v1/search?query={q}&per_page={per_page}&orientation={orientation}&size=medium"
    req = urllib.request.Request(url, headers={
        "Authorization": api_key,
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())
    return data.get("photos", [])


def download_photo(photo: dict, dest: Path, orientation: str) -> bool:
    src_url = photo["src"].get("large") or photo["src"].get("medium")
    if not src_url:
        return False
    try:
        result = subprocess.run(
            ["curl", "-s", "-L", "--max-time", "20", src_url, "-o", str(dest)],
            capture_output=True,
        )
        if result.returncode == 0 and dest.exists() and dest.stat().st_size > 1000:
            return True
        dest.unlink(missing_ok=True)
        return False
    except Exception as e:
        print(f"  ✗ errore download {dest.name}: {e}")
        return False


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Uso: python3 download-stock-photos.py <PEXELS_API_KEY>")
        sys.exit(1)

    api_key = sys.argv[1].strip()
    total_ok = 0
    total_fail = 0

    for category, cfg in CATEGORIES.items():
        dest_dir = OUTPUT_BASE / category
        dest_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n📁 {category.upper()} — target {cfg['n']} foto")
        collected: list[dict] = []

        for query in cfg["queries"]:
            if len(collected) >= cfg["n"]:
                break
            needed = cfg["n"] - len(collected)
            try:
                photos = pexels_search(api_key, query, per_page=min(needed + 2, 10), orientation=cfg["orientation"])
                # dedup per id
                existing_ids = {p["id"] for p in collected}
                new_photos = [p for p in photos if p["id"] not in existing_ids]
                collected.extend(new_photos[:needed])
                print(f"  query '{query}' → {len(new_photos)} foto trovate")
                time.sleep(0.3)  # rate limit cortesia
            except Exception as e:
                print(f"  ✗ query fallita '{query}': {e}")

        # scarica
        for i, photo in enumerate(collected[:cfg["n"]], 1):
            ext = "jpg"
            fname = f"{category}_{i:02d}.{ext}"
            dest = dest_dir / fname
            print(f"  ↓ {fname} (pexels id {photo['id']}) ... ", end="", flush=True)
            ok = download_photo(photo, dest, cfg["orientation"])
            if ok:
                size_kb = dest.stat().st_size // 1024
                print(f"✓ {size_kb}KB")
                total_ok += 1
            else:
                total_fail += 1

    print(f"\n{'─'*50}")
    print(f"✅ Scaricate: {total_ok} | ✗ Fallite: {total_fail}")
    print(f"📂 Output: {OUTPUT_BASE}")


if __name__ == "__main__":
    main()
