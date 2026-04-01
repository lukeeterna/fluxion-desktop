"""
qa_check.py — FLUXION Video Factory
Quality assurance automatico per i video prodotti.
Verifica durata, risoluzione, audio, brand visibility e dimensione file.

Uso:
  python video_factory/qa_check.py --video output/parrucchiere/parrucchiere_video_9x16.mp4
  python video_factory/qa_check.py --dir output/           # QA su tutti i video
  python video_factory/qa_check.py --dir output/ --fix     # tenta fix automatici
"""

from __future__ import annotations
import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import ffmpeg

# ─── Config soglie ────────────────────────────────────────────────────────────

SPECS = {
    "9:16": {
        "width": 1080,
        "height": 1920,
        "min_duration": 25.0,
        "max_duration": 36.0,
        "max_file_mb": 50,
        "target_fps": 30,
    },
    "16:9": {
        "width": 1920,
        "height": 1080,
        "min_duration": 25.0,
        "max_duration": 36.0,
        "max_file_mb": 200,
        "target_fps": 30,
    },
}

REQUIRED_KEYWORDS_IN_FILENAME = ["9x16", "16x9"]


# ─── Dataclasses ─────────────────────────────────────────────────────────────

QAStatus = Literal["PASS", "WARN", "FAIL"]


@dataclass
class QACheck:
    name: str
    status: QAStatus
    value: str
    expected: str
    message: str = ""


@dataclass
class QAReport:
    video_path: Path
    checks: list[QACheck] = field(default_factory=list)
    overall: QAStatus = "PASS"

    def add(self, check: QACheck):
        self.checks.append(check)
        if check.status == "FAIL":
            self.overall = "FAIL"
        elif check.status == "WARN" and self.overall == "PASS":
            self.overall = "WARN"

    def summary(self) -> str:
        icon = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}[self.overall]
        lines = [f"\n{icon} {self.video_path.name} — {self.overall}"]
        for c in self.checks:
            ci = {"PASS": "  ✓", "WARN": "  ⚠", "FAIL": "  ✗"}[c.status]
            lines.append(f"{ci} {c.name}: {c.value} (atteso: {c.expected})")
            if c.message:
                lines.append(f"      → {c.message}")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "video": str(self.video_path),
            "overall": self.overall,
            "checks": [
                {
                    "name": c.name,
                    "status": c.status,
                    "value": c.value,
                    "expected": c.expected,
                    "message": c.message,
                }
                for c in self.checks
            ],
        }


# ─── Checks individuali ───────────────────────────────────────────────────────

def check_resolution(report: QAReport, streams: list[dict], ratio: str) -> None:
    spec = SPECS[ratio]
    video_stream = next((s for s in streams if s["codec_type"] == "video"), None)
    if not video_stream:
        report.add(QACheck("Risoluzione", "FAIL", "N/A", f"{spec['width']}×{spec['height']}", "Nessun stream video trovato"))
        return

    w = int(video_stream.get("width", 0))
    h = int(video_stream.get("height", 0))
    expected = f"{spec['width']}×{spec['height']}"
    actual = f"{w}×{h}"

    if w == spec["width"] and h == spec["height"]:
        status = "PASS"
    elif abs(w - spec["width"]) <= 2 and abs(h - spec["height"]) <= 2:
        status = "WARN"
    else:
        status = "FAIL"

    report.add(QACheck("Risoluzione", status, actual, expected))


def check_duration(report: QAReport, probe_data: dict, ratio: str) -> None:
    spec = SPECS[ratio]
    duration = float(probe_data["format"].get("duration", 0))
    expected = f"{spec['min_duration']}–{spec['max_duration']}s"
    actual = f"{duration:.1f}s"

    if spec["min_duration"] <= duration <= spec["max_duration"]:
        status = "PASS"
    elif spec["min_duration"] - 2 <= duration <= spec["max_duration"] + 4:
        status = "WARN"
    else:
        status = "FAIL"

    msg = ""
    if duration < spec["min_duration"]:
        msg = "Video troppo corto — il CTA frame potrebbe mancare"
    elif duration > spec["max_duration"]:
        msg = "Video troppo lungo — rischio scroll-away su WA"

    report.add(QACheck("Durata", status, actual, expected, msg))


def check_fps(report: QAReport, streams: list[dict]) -> None:
    video_stream = next((s for s in streams if s["codec_type"] == "video"), None)
    if not video_stream:
        return

    fps_str = video_stream.get("r_frame_rate", "0/1")
    try:
        num, den = fps_str.split("/")
        fps = round(int(num) / int(den), 2)
    except Exception:
        fps = 0

    status = "PASS" if 29 <= fps <= 31 else ("WARN" if 23 <= fps <= 31 else "FAIL")
    report.add(QACheck("FPS", status, str(fps), "29.97–30",
                       "FPS < 30 può causare stuttering su mobile" if fps < 29 else ""))


def check_codecs(report: QAReport, streams: list[dict]) -> None:
    video_codecs = [s["codec_name"] for s in streams if s["codec_type"] == "video"]
    audio_codecs = [s["codec_name"] for s in streams if s["codec_type"] == "audio"]

    v_status = "PASS" if "h264" in video_codecs else "FAIL"
    report.add(QACheck("Video codec", v_status,
                       video_codecs[0] if video_codecs else "NONE",
                       "h264",
                       "WhatsApp richiede H.264 per compatibilità universale" if v_status == "FAIL" else ""))

    if audio_codecs:
        a_status = "PASS" if any(c in ["aac", "mp3"] for c in audio_codecs) else "WARN"
        report.add(QACheck("Audio codec", a_status,
                           audio_codecs[0],
                           "aac",
                           "Considera conversione in AAC" if a_status == "WARN" else ""))
    else:
        report.add(QACheck("Audio codec", "WARN", "NONE", "aac",
                           "Nessuna traccia audio — il video non avrà suono"))


def check_audio_levels(report: QAReport, video_path: Path) -> None:
    """Verifica che il volume audio sia adeguato (non troppo basso/alto)."""
    try:
        result = subprocess.run([
            "ffmpeg", "-i", str(video_path),
            "-filter:a", "volumedetect",
            "-f", "null", "-",
        ], capture_output=True, text=True, timeout=30)

        output = result.stderr
        mean_vol = None
        max_vol = None

        for line in output.split("\n"):
            if "mean_volume:" in line:
                mean_vol = float(line.split("mean_volume:")[1].strip().split(" ")[0])
            if "max_volume:" in line:
                max_vol = float(line.split("max_volume:")[1].strip().split(" ")[0])

        if mean_vol is None:
            report.add(QACheck("Volume audio", "WARN", "N/A", "-20 dBFS mean",
                               "Impossibile misurare volume"))
            return

        status = "PASS"
        msg = ""
        if mean_vol < -35:
            status = "WARN"
            msg = f"Audio troppo basso ({mean_vol:.1f} dBFS) — usa: ffmpeg -filter:a 'volume=2.5'"
        elif max_vol > -1:
            status = "WARN"
            msg = f"Picco audio al limite ({max_vol:.1f} dBFS) — rischio clipping"

        report.add(QACheck("Volume audio", status,
                           f"{mean_vol:.1f} dBFS mean / {max_vol:.1f} dBFS peak",
                           "-20 dBFS mean / -3 dBFS peak", msg))

    except Exception as e:
        report.add(QACheck("Volume audio", "WARN", "Errore", "-20 dBFS",
                           f"Check fallito: {e}"))


def check_file_size(report: QAReport, video_path: Path, ratio: str) -> None:
    size_mb = video_path.stat().st_size / (1024 * 1024)
    max_mb = SPECS[ratio]["max_file_mb"]

    if size_mb <= max_mb * 0.7:
        status = "PASS"
        msg = ""
    elif size_mb <= max_mb:
        status = "WARN"
        msg = f"Dimensione vicina al limite WA ({max_mb}MB)"
    else:
        status = "FAIL"
        msg = f"File troppo grande per WA — comprimi con: ffmpeg -crf 28"

    report.add(QACheck("Dimensione file", status,
                       f"{size_mb:.1f}MB", f"< {max_mb}MB", msg))


def check_brand_visibility(report: QAReport, video_path: Path) -> None:
    """
    Estrae l'ultimo frame e controlla che ci sia testo bianco su sfondo scuro
    (approssimazione per rilevare il frame CTA senza OCR completo).
    Usa OCR (pytesseract) se disponibile.
    """
    try:
        import pytesseract
        from PIL import Image
        import tempfile, os

        # Estrai frame a t=-2s (2 secondi dalla fine = dentro CTA)
        probe = ffmpeg.probe(str(video_path))
        duration = float(probe["format"]["duration"])
        thumb_time = max(0, duration - 3)

        tmp = Path(tempfile.mktemp(suffix=".jpg"))
        (
            ffmpeg
            .input(str(video_path), ss=thumb_time)
            .output(str(tmp), vframes=1, format="image2")
            .overwrite_output()
            .run(quiet=True)
        )

        img = Image.open(tmp)
        text = pytesseract.image_to_string(img, lang="ita").upper()
        tmp.unlink()

        has_fluxion = "FLUXION" in text
        has_price = "497" in text or "€" in text

        if has_fluxion and has_price:
            status = "PASS"
            msg = "FLUXION e prezzo rilevati nel frame CTA"
        elif has_fluxion or has_price:
            status = "WARN"
            msg = f"Parziale: FLUXION={'✓' if has_fluxion else '✗'}, €497={'✓' if has_price else '✗'}"
        else:
            status = "WARN"
            msg = "OCR non ha rilevato FLUXION/€497 — verifica manualmente il frame finale"

        report.add(QACheck("Brand CTA visibility", status,
                           f"FLUXION={has_fluxion}, €497={has_price}",
                           "FLUXION + €497 visibili", msg))

    except ImportError:
        report.add(QACheck("Brand CTA visibility", "WARN",
                           "pytesseract non installato",
                           "FLUXION + €497 visibili",
                           "Installa: pip install pytesseract pillow + brew install tesseract"))
    except Exception as e:
        report.add(QACheck("Brand CTA visibility", "WARN",
                           f"Errore: {e}", "FLUXION + €497 visibili"))


def check_bitrate(report: QAReport, probe_data: dict) -> None:
    bitrate_kbps = int(probe_data["format"].get("bit_rate", 0)) // 1000
    if 2000 <= bitrate_kbps <= 12000:
        status = "PASS"
        msg = ""
    elif bitrate_kbps < 2000:
        status = "WARN"
        msg = "Bitrate basso — qualità visiva potenzialmente scadente"
    else:
        status = "WARN"
        msg = "Bitrate alto — file più grande del necessario"

    report.add(QACheck("Bitrate video", status,
                       f"{bitrate_kbps} kbps", "2000–8000 kbps", msg))


# ─── Auto-fix ─────────────────────────────────────────────────────────────────

def auto_fix(video_path: Path, report: QAReport) -> Path | None:
    """
    Tenta fix automatici per i problemi FAIL/WARN rilevati.
    Ritorna il path del video fixato, o None se non ci sono fix da fare.
    """
    needs_fix = False
    fixes = []

    for check in report.checks:
        if check.status == "FAIL":
            if check.name == "Video codec":
                fixes.append(("codec", "libx264"))
                needs_fix = True
            elif check.name == "Dimensione file":
                fixes.append(("compress", None))
                needs_fix = True
        elif check.status == "WARN":
            if "Audio troppo basso" in check.message:
                fixes.append(("volume", "2.5"))
                needs_fix = True

    if not needs_fix:
        return None

    fixed_path = video_path.parent / f"{video_path.stem}_fixed.mp4"

    # Build FFmpeg command con tutti i fix
    input_stream = ffmpeg.input(str(video_path))
    video = input_stream.video
    audio = input_stream.audio

    vcodec = "libx264"
    acodec = "aac"
    extra_args = {"pix_fmt": "yuv420p", "crf": "23"}

    for fix_type, fix_val in fixes:
        if fix_type == "compress":
            extra_args["crf"] = "28"
        elif fix_type == "volume" and fix_val:
            audio = audio.filter("volume", fix_val)

    (
        ffmpeg
        .output(video, audio, str(fixed_path),
                vcodec=vcodec, acodec=acodec, **extra_args)
        .overwrite_output()
        .run(quiet=True)
    )

    print(f"  → Auto-fixed: {fixed_path.name}")
    return fixed_path


# ─── Main QA runner ───────────────────────────────────────────────────────────

def qa_video(video_path: Path, auto_fix_enabled: bool = False) -> QAReport:
    """Esegui tutti i check su un video."""
    report = QAReport(video_path=video_path)

    if not video_path.exists():
        report.add(QACheck("File esiste", "FAIL", "NO", "YES"))
        return report

    report.add(QACheck("File esiste", "PASS", "YES", "YES"))

    # Determina il ratio dal nome file
    if "9x16" in video_path.name or "9:16" in video_path.name:
        ratio = "9:16"
    elif "16x9" in video_path.name or "16:9" in video_path.name:
        ratio = "16:9"
    else:
        ratio = "9:16"  # default

    try:
        probe = ffmpeg.probe(str(video_path))
        streams = probe["streams"]
    except Exception as e:
        report.add(QACheck("FFprobe", "FAIL", str(e), "OK"))
        return report

    check_resolution(report, streams, ratio)
    check_duration(report, probe, ratio)
    check_fps(report, streams)
    check_codecs(report, streams)
    check_audio_levels(report, video_path)
    check_file_size(report, video_path, ratio)
    check_bitrate(report, probe)
    check_brand_visibility(report, video_path)

    if auto_fix_enabled and report.overall != "PASS":
        fixed = auto_fix(video_path, report)
        if fixed:
            report.add(QACheck("Auto-fix", "PASS", str(fixed.name), "Applied"))

    return report


def qa_directory(output_dir: Path, auto_fix_enabled: bool = False) -> list[QAReport]:
    """QA su tutti i video _9x16.mp4 e _16x9.mp4 trovati."""
    videos = sorted(output_dir.rglob("*_video_*.mp4"))
    if not videos:
        print(f"Nessun video trovato in {output_dir}")
        return []

    print(f"QA su {len(videos)} video...\n")
    reports = []

    for video in videos:
        report = qa_video(video, auto_fix_enabled)
        reports.append(report)
        print(report.summary())

    # Summary finale
    passed = sum(1 for r in reports if r.overall == "PASS")
    warned = sum(1 for r in reports if r.overall == "WARN")
    failed = sum(1 for r in reports if r.overall == "FAIL")

    print(f"\n{'═'*50}")
    print(f"QA RESULTS: ✅ {passed} PASS  ⚠️  {warned} WARN  ❌ {failed} FAIL")
    print(f"{'═'*50}")

    # Salva report JSON
    report_path = output_dir / "qa_report.json"
    report_path.write_text(
        json.dumps([r.to_dict() for r in reports], indent=2, ensure_ascii=False)
    )
    print(f"Report salvato: {report_path}")

    return reports


# ─── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="FLUXION QA Check")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--video", type=Path, help="Path video singolo")
    group.add_argument("--dir", type=Path, help="Directory con tutti i video")
    parser.add_argument("--fix", action="store_true",
                        help="Tenta auto-fix per problemi FAIL/WARN")
    args = parser.parse_args()

    if args.video:
        report = qa_video(args.video, args.fix)
        print(report.summary())
        sys.exit(0 if report.overall in ["PASS", "WARN"] else 1)
    else:
        reports = qa_directory(args.dir, args.fix)
        has_failures = any(r.overall == "FAIL" for r in reports)
        sys.exit(1 if has_failures else 0)
