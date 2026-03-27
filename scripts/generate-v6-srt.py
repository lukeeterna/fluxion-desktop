#!/usr/bin/env python3
"""
FLUXION V6 — SRT Subtitle Generator
Reads storyboard JSON + voiceover manifest → generates Italian SRT subtitles.
Output: landing/assets/fluxion-promo-v6.srt
"""

import json
import textwrap
from pathlib import Path

BASE = Path("/Volumes/MontereyT7/FLUXION")
STORYBOARD = BASE / "scripts" / "video-production-v6.json"
MANIFEST = BASE / "tmp-video-build" / "voiceover-manifest.json"
OUTPUT = BASE / "landing" / "assets" / "fluxion-promo-v6.srt"

MAX_LINE_CHARS = 42  # YouTube subtitle standard
MAX_LINES = 2


def format_timestamp(seconds):
    """Convert seconds to SRT timestamp HH:MM:SS,mmm."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def split_text_into_segments(text, max_chars=MAX_LINE_CHARS, max_lines=MAX_LINES):
    """Split voiceover text into subtitle segments (max 2 lines x 42 chars)."""
    if not text:
        return []

    # Split on sentence boundaries first
    sentences = []
    current = ""
    for char in text:
        current += char
        if char in ".!?" and len(current.strip()) > 5:
            sentences.append(current.strip())
            current = ""
    if current.strip():
        sentences.append(current.strip())

    # Group sentences into subtitle segments
    segments = []
    buffer = ""

    for sentence in sentences:
        # Wrap this sentence into lines
        words = sentence.split()
        lines = []
        line = ""
        for word in words:
            test = f"{line} {word}".strip() if line else word
            if len(test) <= max_chars:
                line = test
            else:
                if line:
                    lines.append(line)
                line = word

        if line:
            lines.append(line)

        # If adding this sentence to buffer would exceed 2 lines, flush
        if buffer:
            buffer_lines = buffer.split("\n")
            if len(buffer_lines) + len(lines) > max_lines:
                segments.append(buffer)
                buffer = "\n".join(lines)
            else:
                buffer = buffer + "\n" + "\n".join(lines)
        else:
            # If sentence itself > 2 lines, split into chunks
            for chunk_start in range(0, len(lines), max_lines):
                chunk = "\n".join(lines[chunk_start:chunk_start + max_lines])
                if buffer:
                    segments.append(buffer)
                buffer = chunk

    if buffer:
        segments.append(buffer)

    return segments


def main():
    with open(STORYBOARD) as f:
        data = json.load(f)
    scenes = [s for ch in data["chapters"] for s in ch["scenes"]]

    with open(MANIFEST) as f:
        manifest = json.load(f)

    subtitles = []
    seq = 1
    cumulative_time = 0.0

    for scene in scenes:
        scene_id = scene["id"]
        m = manifest.get(scene_id, {})
        audio_dur = m.get("duration_seconds", 0)

        # Get voiceover text
        text = scene.get("voiceover")
        is_dialogue = scene.get("type") == "dialogue" or "voiceover_dialogue" in scene

        if is_dialogue and "voiceover_dialogue" in scene:
            # Dialogue — each line becomes a subtitle
            dialogue_lines = scene["voiceover_dialogue"]
            if audio_dur > 0:
                time_per_line = audio_dur / len(dialogue_lines)
            else:
                time_per_line = 3.0

            for j, line in enumerate(dialogue_lines):
                start = cumulative_time + j * time_per_line
                end = start + time_per_line - 0.1
                speaker = "Sara" if "Isabella" in line.get("voice", "") else ""
                prefix = f"— {speaker}: " if speaker else "— "
                sub_text = prefix + line["text"]

                # Wrap to max line length
                wrapped = textwrap.fill(sub_text, width=MAX_LINE_CHARS)
                lines = wrapped.split("\n")[:MAX_LINES]

                subtitles.append({
                    "seq": seq,
                    "start": start,
                    "end": end,
                    "text": "\n".join(lines)
                })
                seq += 1

        elif text:
            # Regular voiceover — split into subtitle segments
            segments = split_text_into_segments(text)
            if audio_dur > 0 and segments:
                time_per_seg = audio_dur / len(segments)
            else:
                time_per_seg = 4.0

            for j, seg in enumerate(segments):
                start = cumulative_time + j * time_per_seg
                end = start + time_per_seg - 0.1

                subtitles.append({
                    "seq": seq,
                    "start": start,
                    "end": end,
                    "text": seg
                })
                seq += 1

        # Advance cumulative time
        if audio_dur > 0:
            scene_dur = audio_dur + 0.5  # Same padding as compositing script
        else:
            # Silent scenes use trim duration or storyboard duration
            trim_s = scene.get("trim_start", 0)
            trim_e = scene.get("trim_end", None)
            if trim_e:
                scene_dur = trim_e - trim_s
            else:
                scene_dur = scene.get("duration", 5)

        cumulative_time += scene_dur

    # Write SRT file
    with open(OUTPUT, "w", encoding="utf-8") as f:
        for sub in subtitles:
            f.write(f"{sub['seq']}\n")
            f.write(f"{format_timestamp(sub['start'])} --> {format_timestamp(sub['end'])}\n")
            f.write(f"{sub['text']}\n")
            f.write("\n")

    print(f"SRT generated: {OUTPUT}")
    print(f"  Subtitles: {len(subtitles)}")
    print(f"  Last timestamp: {format_timestamp(cumulative_time)}")
    print(f"  Lines: {sum(1 for _ in open(OUTPUT))}")


if __name__ == "__main__":
    main()
