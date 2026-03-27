#!/usr/bin/env python3
"""
FLUXION V6 — Final Video Compositing
Reads storyboard JSON + voiceover manifest, assembles 27 scenes with
crossfades, music mixing, logo watermark, and endcard animation.
Output: landing/assets/fluxion-promo-v6.mp4
"""

import json
import os
import subprocess
import shutil
import sys
from pathlib import Path

BASE = Path("/Volumes/MontereyT7/FLUXION")
STORYBOARD = BASE / "scripts" / "video-production-v6.json"
AI_CLIPS = BASE / "landing" / "assets" / "ai-clips-v2"
SCREENSHOTS = BASE / "landing" / "screenshots"
LOGO = BASE / "logo_fluxion.jpg"
MUSIC = BASE / "landing" / "assets" / "background-music.mp3"
OUTPUT = BASE / "landing" / "assets" / "fluxion-promo-v6.mp4"
TMPDIR = BASE / "tmp-video-build"
MANIFEST = TMPDIR / "voiceover-manifest.json"
ENDCARD_VIDEO = TMPDIR / "endcard-animated.mp4"

W, H, FPS = 1280, 720, 30
SCALE_FILTER = f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,format=yuv420p"


def run_ff(args, label=""):
    """Run ffmpeg/ffprobe and return result."""
    r = subprocess.run(args, capture_output=True, text=True)
    if r.returncode != 0 and label:
        print(f"  WARN [{label}]: {r.stderr[:200]}")
    return r


def probe_duration(path):
    """Get media duration in seconds."""
    r = run_ff(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", str(path)])
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def burn_logo(img_path, output_path):
    """Burn FLUXION logo watermark on image via Pillow."""
    from PIL import Image
    img = Image.open(img_path).convert("RGB")
    if img.size != (W, H):
        img = img.resize((W, H), Image.LANCZOS)

    if LOGO.exists():
        logo = Image.open(str(LOGO)).convert("RGBA")
        logo = logo.resize((64, 64), Image.LANCZOS)
        alpha = logo.split()[3].point(lambda p: int(p * 0.7))
        logo.putalpha(alpha)
        img_rgba = img.convert("RGBA")
        img_rgba.paste(logo, (24, 24), logo)
        img = img_rgba.convert("RGB")

    img.save(output_path, quality=95)


def main():
    # Load storyboard
    with open(STORYBOARD) as f:
        data = json.load(f)
    scenes = [s for ch in data["chapters"] for s in ch["scenes"]]

    # Load voiceover manifest
    with open(MANIFEST) as f:
        manifest = json.load(f)

    print("=" * 60)
    print("  FLUXION V6 — Final Video Compositing")
    print(f"  Scenes: {len(scenes)}")
    print("=" * 60)

    # ================================================================
    # Phase 1: Collect voiceover info from manifest (already generated)
    # ================================================================
    print("\n[1/5] Loading voiceover manifest...\n")
    for scene_id, info in manifest.items():
        mp3 = info.get("mp3_path")
        dur = info.get("duration_seconds", 0)
        stype = info.get("type", "silent")
        if mp3 and Path(mp3).exists():
            print(f"  {scene_id}: {dur:.1f}s ({stype})")
        elif stype != "silent":
            print(f"  {scene_id}: MISSING {mp3}")
        else:
            print(f"  {scene_id}: silent")

    # ================================================================
    # Phase 2: Build individual scene clips
    # ================================================================
    print(f"\n[2/5] Building {len(scenes)} individual clips...\n")
    clip_paths = []

    for i, scene in enumerate(scenes):
        scene_id = scene["id"]
        scene_type = scene.get("type", "screenshot")
        clip_out = TMPDIR / f"v6_clip_{i:02d}_{scene_id}.mp4"

        # Get voiceover from manifest
        m = manifest.get(scene_id, {})
        audio = m.get("mp3_path")
        audio_dur = m.get("duration_seconds", 0)
        if audio and not Path(audio).exists():
            audio = None
            audio_dur = 0

        # Scene 27 (endcard) — use pre-rendered endcard animation
        if scene_id == "scene_27":
            if ENDCARD_VIDEO.exists():
                # Normalize endcard to match format
                run_ff([
                    "ffmpeg", "-y", "-i", str(ENDCARD_VIDEO),
                    "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                    "-t", "5",
                    "-vf", SCALE_FILTER,
                    "-c:v", "libx264", "-preset", "fast", "-crf", "22",
                    "-c:a", "aac", "-b:a", "192k", "-shortest",
                    str(clip_out)
                ], f"endcard {scene_id}")
            else:
                print(f"  MISSING endcard: {ENDCARD_VIDEO}")
                continue

        elif scene_type == "ai":
            # AI clip with optional trimming
            file_path = BASE / scene["file"] if scene["file"].startswith("landing/") else AI_CLIPS / scene["file"]
            if not file_path.exists():
                print(f"  MISSING: {file_path}")
                continue

            trim_start = scene.get("trim_start", 0)
            trim_end = scene.get("trim_end", None)

            if audio and audio_dur > 0:
                # AI clip with voiceover — duration = max(voiceover + 0.5s, trim range)
                target_dur = audio_dur + 0.5
                trim_dur = (trim_end - trim_start) if trim_end else 8.0

                cmd = ["ffmpeg", "-y"]
                if target_dur > trim_dur:
                    # Loop the clip to fill voiceover duration
                    cmd += ["-stream_loop", "-1"]
                cmd += [
                    "-ss", str(trim_start), "-i", str(file_path),
                    "-i", str(audio),
                    "-t", str(target_dur),
                    "-vf", SCALE_FILTER,
                    "-c:v", "libx264", "-preset", "fast", "-crf", "22",
                    "-c:a", "aac", "-b:a", "192k",
                    "-map", "0:v:0", "-map", "1:a:0",
                    str(clip_out)
                ]
                run_ff(cmd, f"ai+voice {scene_id}")
            else:
                # AI clip without voiceover — use trim range or default 2s
                trim_dur = (trim_end - trim_start) if trim_end else 2.0
                run_ff([
                    "ffmpeg", "-y",
                    "-ss", str(trim_start), "-i", str(file_path),
                    "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                    "-t", str(trim_dur),
                    "-vf", SCALE_FILTER,
                    "-c:v", "libx264", "-preset", "fast", "-crf", "22",
                    "-c:a", "aac", "-b:a", "192k", "-shortest",
                    str(clip_out)
                ], f"ai silent {scene_id}")

        elif scene_type in ("screenshot", "dialogue"):
            # Screenshot or dialogue scene — still image with voiceover
            file_path = BASE / scene["file"] if scene["file"].startswith("landing/") else SCREENSHOTS / scene["file"]
            if not file_path.exists():
                print(f"  MISSING: {file_path}")
                continue

            # Burn logo on screenshot
            prepared = TMPDIR / f"v6_prepared_{scene_id}.png"
            burn_logo(str(file_path), str(prepared))

            if audio and audio_dur > 0:
                target_dur = audio_dur + 0.5
                run_ff([
                    "ffmpeg", "-y",
                    "-loop", "1", "-t", str(target_dur), "-i", str(prepared),
                    "-i", str(audio),
                    "-vf", "format=yuv420p",
                    "-c:v", "libx264", "-preset", "fast", "-crf", "22",
                    "-c:a", "aac", "-b:a", "192k",
                    "-shortest", str(clip_out)
                ], f"ss+voice {scene_id}")
            else:
                # Silent screenshot (shouldn't happen often)
                dur = scene.get("duration", 5)
                run_ff([
                    "ffmpeg", "-y",
                    "-loop", "1", "-t", str(dur), "-i", str(prepared),
                    "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                    "-vf", "format=yuv420p",
                    "-c:v", "libx264", "-preset", "fast", "-crf", "22",
                    "-c:a", "aac", "-b:a", "192k", "-shortest",
                    str(clip_out)
                ], f"ss silent {scene_id}")

        # Check result
        if clip_out.exists() and clip_out.stat().st_size > 1000:
            dur = probe_duration(clip_out)
            print(f"  [{i+1:2d}/{len(scenes)}] {scene_id}: {dur:.1f}s")
            clip_paths.append(str(clip_out))
        else:
            print(f"  [{i+1:2d}/{len(scenes)}] {scene_id}: FAILED")

    if not clip_paths:
        print("ERROR: No clips built!")
        sys.exit(1)

    # ================================================================
    # Phase 3: Normalize and concatenate
    # ================================================================
    print(f"\n[3/5] Normalizing and concatenating {len(clip_paths)} clips...\n")
    norm_paths = []
    for ci, cp in enumerate(clip_paths):
        norm_path = TMPDIR / f"v6_norm_{ci:02d}.ts"
        run_ff([
            "ffmpeg", "-y", "-i", cp,
            "-vf", f"scale={W}:{H},format=yuv420p",
            "-c:v", "libx264", "-preset", "fast", "-crf", "22",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-bsf:v", "h264_mp4toannexb",
            str(norm_path)
        ], f"norm {ci}")
        if norm_path.exists() and norm_path.stat().st_size > 1000:
            norm_paths.append(str(norm_path))

    concat_file = TMPDIR / "v6_concat.txt"
    with open(concat_file, "w") as f:
        for np in norm_paths:
            f.write(f"file '{np}'\n")

    concat_out = TMPDIR / "v6_concatenated.mp4"
    run_ff([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy",
        str(concat_out)
    ], "concat")

    total_dur = probe_duration(concat_out)
    print(f"  Total duration: {total_dur:.0f}s ({total_dur/60:.1f} min)")

    # ================================================================
    # Phase 4: Mix background music
    # ================================================================
    print(f"\n[4/5] Mixing background music...\n")
    music_out = TMPDIR / "v6_with_music.mp4"

    # Music at -20dB under voice, fade in 2s, fade out 3s
    fade_out_music = max(0, total_dur - 3)
    run_ff([
        "ffmpeg", "-y",
        "-i", str(concat_out),
        "-stream_loop", "-1", "-i", str(MUSIC),
        "-t", str(total_dur),
        "-filter_complex",
        f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=1.0[voice];"
        f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.08,"
        f"afade=t=in:d=2,afade=t=out:st={fade_out_music}:d=3[music];"
        f"[voice][music]amix=inputs=2:duration=first:dropout_transition=3[aout]",
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        str(music_out)
    ], "music mix")
    print("  Music mixed.")

    # ================================================================
    # Phase 5: Final encode with fade in/out
    # ================================================================
    print(f"\n[5/5] Final encode (H.264 High, CRF 18, fade in/out)...\n")
    fade_out_start = max(0, total_dur - 2.5)

    run_ff([
        "ffmpeg", "-y", "-i", str(music_out),
        "-vf", f"fade=t=in:st=0:d=1.5,fade=t=out:st={fade_out_start}:d=2",
        "-af", f"afade=t=in:st=0:d=1,afade=t=out:st={fade_out_start}:d=2",
        "-c:v", "libx264", "-preset", "slow", "-crf", "18",
        "-profile:v", "high", "-level", "4.1",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
        str(OUTPUT)
    ], "final encode")

    # Fallback chain
    if not OUTPUT.exists() or OUTPUT.stat().st_size < 1000:
        if music_out.exists() and music_out.stat().st_size > 1000:
            shutil.copy2(str(music_out), str(OUTPUT))
        elif concat_out.exists():
            shutil.copy2(str(concat_out), str(OUTPUT))

    # Final info
    final_dur = probe_duration(OUTPUT)
    size_mb = OUTPUT.stat().st_size / 1024 / 1024 if OUTPUT.exists() else 0

    print("\n" + "=" * 60)
    print(f"  FLUXION V6 — VIDEO COMPLETATO")
    print(f"  Output:   {OUTPUT}")
    print(f"  Durata:   {final_dur:.0f}s ({final_dur/60:.1f} min)")
    print(f"  Size:     {size_mb:.1f} MB")
    print(f"  Scenes:   {len(clip_paths)}")
    print("=" * 60)
    print(f"\n  open '{OUTPUT}'")


if __name__ == "__main__":
    main()
