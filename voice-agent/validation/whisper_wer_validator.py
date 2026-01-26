#!/usr/bin/env python3
"""Whisper.cpp WER Validation - Italian Language on M1 Mac
Validation script for Fluxion Voice Agent
Target: WER < 12% on Italian speech

Note: This script requires pre-recorded test audio files.
If not available, it will use macOS 'say' command to generate test audio
and then transcribe with whisper.cpp (synthetic test).
"""

import subprocess
import os
import sys
import time
import tempfile
from datetime import datetime
import json

try:
    import numpy as np
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"])
    import numpy as np


class WhisperWERValidator:
    def __init__(self):
        self.whisper_path = None
        self.model_path = None
        self.results = []
        self._find_whisper()

    def _find_whisper(self):
        """Find whisper.cpp executable and model"""
        locations = [
            os.path.expanduser("~/whisper.cpp/main"),
            os.path.expanduser("~/whisper.cpp/build/bin/main"),
            "/usr/local/bin/whisper-cpp",
            "./whisper.cpp/main",
            "./main",
        ]

        for loc in locations:
            if os.path.exists(loc):
                self.whisper_path = loc
                break

        # Find model
        model_locations = [
            os.path.expanduser("~/whisper.cpp/models/ggml-large-v3.bin"),
            os.path.expanduser("~/whisper.cpp/models/ggml-medium.bin"),
            os.path.expanduser("~/whisper.cpp/models/ggml-small.bin"),
            os.path.expanduser("~/whisper.cpp/models/ggml-base.bin"),
            "./models/ggml-large-v3.bin",
            "./models/ggml-medium.bin",
        ]

        for loc in model_locations:
            if os.path.exists(loc):
                self.model_path = loc
                break

    def setup_whisper(self):
        """Build whisper.cpp if not found"""
        if self.whisper_path and self.model_path:
            print(f"  Whisper.cpp found: {self.whisper_path}")
            print(f"  Model found: {self.model_path}")
            return True

        print("\n  Whisper.cpp not found. Setting up...")

        whisper_dir = os.path.expanduser("~/whisper.cpp")

        # Clone and build
        if not os.path.exists(whisper_dir):
            print("  Cloning whisper.cpp...")
            try:
                subprocess.run([
                    "git", "clone", "https://github.com/ggerganov/whisper.cpp.git",
                    whisper_dir
                ], check=True)
            except Exception as e:
                print(f"  ❌ Failed to clone: {e}")
                return False

        # Build
        print("  Building whisper.cpp...")
        try:
            subprocess.run(["make", "-j4"], cwd=whisper_dir, check=True)
            self.whisper_path = f"{whisper_dir}/main"
        except Exception as e:
            print(f"  ❌ Build failed: {e}")
            return False

        # Download model (medium for balance of speed/accuracy)
        print("  Downloading medium model...")
        models_dir = f"{whisper_dir}/models"
        try:
            subprocess.run([
                "bash", f"{whisper_dir}/models/download-ggml-model.sh", "medium"
            ], cwd=whisper_dir, check=True)
            self.model_path = f"{models_dir}/ggml-medium.bin"
        except Exception as e:
            print(f"  ❌ Model download failed: {e}")
            return False

        print("  ✅ Whisper.cpp setup complete")
        return True

    def calculate_wer(self, reference: str, hypothesis: str) -> float:
        """Calculate Word Error Rate using edit distance"""
        ref_words = reference.lower().split()
        hyp_words = hypothesis.lower().split()

        # Levenshtein distance
        m, n = len(ref_words), len(hyp_words)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if ref_words[i-1] == hyp_words[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])

        edits = dp[m][n]
        wer = (edits / max(m, 1)) * 100
        return min(wer, 100)  # Cap at 100%

    def generate_test_audio(self, text: str, output_path: str) -> bool:
        """Generate test audio using macOS say command"""
        try:
            # First generate AIFF
            aiff_path = output_path.replace('.wav', '.aiff')
            subprocess.run([
                "say", "-v", "Alice",  # Italian voice
                "-o", aiff_path,
                text
            ], check=True)

            # Convert to WAV (16kHz mono for whisper)
            subprocess.run([
                "ffmpeg", "-y", "-i", aiff_path,
                "-ar", "16000", "-ac", "1",
                output_path
            ], check=True, capture_output=True)

            # Cleanup
            if os.path.exists(aiff_path):
                os.unlink(aiff_path)

            return os.path.exists(output_path)
        except Exception as e:
            print(f"  Audio generation failed: {e}")
            return False

    def transcribe(self, audio_path: str) -> tuple:
        """Transcribe audio using whisper.cpp, return (text, latency_ms)"""
        try:
            start = time.time()
            result = subprocess.run([
                self.whisper_path,
                "-m", self.model_path,
                "-l", "it",  # Italian
                "-f", audio_path,
                "--no-timestamps"
            ], capture_output=True, text=True, timeout=60)
            elapsed = (time.time() - start) * 1000

            # Parse output
            output = result.stdout.strip()
            # Remove timing info if present
            lines = [l for l in output.split('\n') if not l.startswith('[')]
            text = ' '.join(lines).strip()

            return text, elapsed
        except subprocess.TimeoutExpired:
            return "", 60000
        except Exception as e:
            print(f"  Transcription error: {e}")
            return "", 0

    def test_whisper_accuracy(self):
        """Test Whisper WER on Italian speech"""

        if not self.setup_whisper():
            return {"pass_criteria": False, "error": "Whisper.cpp not available"}

        # Test utterances (realistic for voice agent)
        test_cases = [
            "Vorrei prenotare un taglio per sabato mattina",
            "Mi chiamo Marco Rossi",
            "Il numero è tre tre tre uno due tre quattro cinque sei sette",
            "Avete disponibilità giovedì pomeriggio?",
            "Quanto costa una visita dal cardiologo?",
            "Posso spostare la mia prenotazione a lunedì?",
            "Un tavolo per quattro persone sabato sera",
            "La mia email è mario chiocciola esempio punto com",
            "Buongiorno, vorrei informazioni sui vostri servizi",
            "Va bene, allora facciamo alle dieci e trenta",
            "Devo annullare l'appuntamento di domani",
            "Sì, confermo la prenotazione",
        ]

        print(f"\n{'='*60}")
        print(f"  WHISPER.CPP WER TEST (ITALIAN)")
        print(f"  Whisper: {self.whisper_path}")
        print(f"  Model: {os.path.basename(self.model_path)}")
        print(f"  Samples: {len(test_cases)}")
        print(f"  Target: WER < 12%")
        print(f"{'='*60}")
        print("\n  Note: Using synthetic audio (macOS say) for testing")
        print("  Real-world WER may vary with actual recordings\n")

        wers = []
        latencies = []

        for idx, reference in enumerate(test_cases, 1):
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                audio_path = tmp.name

            try:
                # Generate audio
                if not self.generate_test_audio(reference, audio_path):
                    print(f"{idx:2d}. ❌ Audio generation failed")
                    continue

                # Transcribe
                hypothesis, latency = self.transcribe(audio_path)
                latencies.append(latency)

                # Calculate WER
                wer = self.calculate_wer(reference, hypothesis)
                wers.append(wer)

                self.results.append({
                    "reference": reference,
                    "hypothesis": hypothesis,
                    "wer": wer,
                    "latency_ms": latency
                })

                status = "✅" if wer < 15 else "⚠️" if wer < 25 else "❌"
                print(f"{idx:2d}. {status} WER: {wer:5.1f}% [{latency:.0f}ms]")
                print(f"      Ref: {reference[:50]}")
                print(f"      Hyp: {hypothesis[:50]}")

            finally:
                if os.path.exists(audio_path):
                    os.unlink(audio_path)

        if not wers:
            return {"pass_criteria": False, "error": "No successful transcriptions"}

        wers_arr = np.array(wers)
        latencies_arr = np.array(latencies)

        print(f"\n{'='*60}")
        print(f"  WER STATISTICS")
        print(f"{'='*60}")
        print(f"  Mean WER:   {wers_arr.mean():6.1f}%")
        print(f"  Median WER: {np.median(wers_arr):6.1f}%")
        print(f"  Min WER:    {wers_arr.min():6.1f}%")
        print(f"  Max WER:    {wers_arr.max():6.1f}%")
        print(f"  Std Dev:    {wers_arr.std():6.1f}%")
        print(f"{'='*60}")
        print(f"\n  Transcription Latency:")
        print(f"  Mean:   {latencies_arr.mean():7.0f} ms")
        print(f"  Median: {np.median(latencies_arr):7.0f} ms")

        mean_wer = float(wers_arr.mean())
        pass_criteria = mean_wer < 12

        result = {
            "timestamp": datetime.now().isoformat(),
            "whisper_path": self.whisper_path,
            "model": os.path.basename(self.model_path),
            "mean_wer": mean_wer,
            "median_wer": float(np.median(wers_arr)),
            "min_wer": float(wers_arr.min()),
            "max_wer": float(wers_arr.max()),
            "std_wer": float(wers_arr.std()),
            "mean_latency_ms": float(latencies_arr.mean()),
            "samples": len(wers),
            "pass_criteria": pass_criteria,
            "note": "Synthetic audio test (macOS say). Real WER may be higher.",
            "results": self.results
        }

        with open("whisper_validation_results.json", "w") as f:
            json.dump(result, f, indent=2)

        print(f"\n{'='*60}")
        if pass_criteria:
            print(f"  ✅ PASS: Whisper WER {mean_wer:.1f}% < 12%")
            print(f"  Recommendation: Whisper.cpp suitable for Italian STT")
        elif mean_wer < 20:
            print(f"  ⚠️  YELLOW: WER {mean_wer:.1f}% (12-20%)")
            print(f"  Recommendation: Acceptable, consider larger model")
        else:
            print(f"  ❌ FAIL: WER {mean_wer:.1f}% > 20%")
            print(f"  Recommendation: Use cloud STT or fine-tune model")

        print(f"\n  ⚠️  Note: This is synthetic audio test.")
        print(f"  Real recordings may have different WER.")
        print(f"{'='*60}\n")

        return result


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  FLUXION VOICE AGENT - WHISPER.CPP VALIDATION")
    print("="*60)
    print("\nPrerequisites:")
    print("  1. whisper.cpp built or will be built automatically")
    print("  2. ffmpeg installed (for audio conversion)")
    print("  3. macOS with Italian voice (Alice)")
    print()

    validator = WhisperWERValidator()
    results = validator.test_whisper_accuracy()
