#!/usr/bin/env python3
"""Piper TTS Latency Validation - M1 Mac
Validation script for Fluxion Voice Agent
Target: p95 < 800ms latency
"""

import time
import sys
import os
import subprocess
import tempfile
from datetime import datetime
import json

# Try to import numpy, install if needed
try:
    import numpy as np
except ImportError:
    print("Installing numpy...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"])
    import numpy as np


class PiperLatencyValidator:
    def __init__(self):
        self.piper_path = None
        self.model_path = None
        self.latencies = []
        self.results = []
        self._find_piper()

    def _find_piper(self):
        """Find piper executable and model"""
        # Check common locations
        locations = [
            "/usr/local/bin/piper",
            "/opt/homebrew/bin/piper",
            os.path.expanduser("~/piper/piper"),
            os.path.expanduser("~/.local/bin/piper"),
            "./piper",
        ]

        for loc in locations:
            if os.path.exists(loc):
                self.piper_path = loc
                break

        if not self.piper_path:
            # Try which
            result = subprocess.run(["which", "piper"], capture_output=True, text=True)
            if result.returncode == 0:
                self.piper_path = result.stdout.strip()

        # Find Italian model
        model_locations = [
            os.path.expanduser("~/.local/share/piper/voices/it_IT-paola-medium.onnx"),
            os.path.expanduser("~/piper-voices/it_IT-paola-medium.onnx"),
            "./it_IT-paola-medium.onnx",
            "/usr/local/share/piper/voices/it_IT-paola-medium.onnx",
        ]

        for loc in model_locations:
            if os.path.exists(loc):
                self.model_path = loc
                break

    def setup_piper(self):
        """Download and setup Piper if not found"""
        if self.piper_path and self.model_path:
            print(f"  Piper found: {self.piper_path}")
            print(f"  Model found: {self.model_path}")
            return True

        print("\n  Piper not found. Setting up...")

        # Create directory
        piper_dir = os.path.expanduser("~/piper")
        os.makedirs(piper_dir, exist_ok=True)

        # Download piper binary for macOS
        print("  Downloading Piper...")
        piper_url = "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_macos_x64.tar.gz"
        try:
            subprocess.run([
                "curl", "-L", "-o", f"{piper_dir}/piper.tar.gz", piper_url
            ], check=True)
            subprocess.run([
                "tar", "-xzf", f"{piper_dir}/piper.tar.gz", "-C", piper_dir
            ], check=True)
            self.piper_path = f"{piper_dir}/piper/piper"
            os.chmod(self.piper_path, 0o755)
        except Exception as e:
            print(f"  ❌ Failed to download Piper: {e}")
            return False

        # Download Italian voice
        print("  Downloading Italian voice (paola-medium)...")
        voice_dir = os.path.expanduser("~/piper-voices")
        os.makedirs(voice_dir, exist_ok=True)

        model_url = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/it/it_IT/paola/medium/it_IT-paola-medium.onnx"
        config_url = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/it/it_IT/paola/medium/it_IT-paola-medium.onnx.json"

        try:
            subprocess.run([
                "curl", "-L", "-o", f"{voice_dir}/it_IT-paola-medium.onnx", model_url
            ], check=True)
            subprocess.run([
                "curl", "-L", "-o", f"{voice_dir}/it_IT-paola-medium.onnx.json", config_url
            ], check=True)
            self.model_path = f"{voice_dir}/it_IT-paola-medium.onnx"
        except Exception as e:
            print(f"  ❌ Failed to download voice: {e}")
            return False

        print("  ✅ Piper setup complete")
        return True

    def test_tts_latency(self):
        """Test latency on 24 phrases of different lengths"""

        if not self.setup_piper():
            return {"pass_criteria": False, "error": "Piper not available"}

        test_phrases = [
            # Brevi (booking confirm) - ~10-20 chars
            "Perfetto, prenotazione confermata.",
            "Va bene per giovedì alle 15.",
            "Ottimo, la aspettiamo.",
            "Buongiorno!",

            # Medie (dialog flow) - ~40-60 chars
            "Quale servizio ti interessa? Abbiamo taglio, colore, piega.",
            "Che giorno preferisci? Abbiamo disponibilità da lunedì a sabato.",
            "Mi può dire il suo nome e cognome per favore?",
            "A che ora preferisce? Abbiamo slot ogni mezz'ora.",

            # Lunghe (info dettagliato) - ~80-120 chars
            "La prenotazione è stata salvata. Ti manderemo una conferma via SMS con il numero di telefono e i dettagli del servizio.",
            "Abbiamo diversi servizi disponibili: taglio uomo, taglio donna, colore, piega, trattamenti speciali e barba.",
            "Ho trovato due clienti con questo nome. Mi può dire la sua data di nascita per identificarla correttamente?",
            "Mi dispiace, non ho disponibilità per quella data. Posso proporle sabato prossimo alle 10 o lunedì alle 15?",

            # Numeri e date (test pronuncia)
            "Il suo appuntamento è confermato per sabato 25 gennaio alle ore 10 e 30.",
            "Il numero da contattare è 333 123 4567.",
            "L'importo totale è di 45 euro e 50 centesimi.",

            # Domande (intonazione)
            "Preferisce mattina o pomeriggio?",
            "Posso avere un recapito telefonico?",
            "Desidera altro?",

            # Formali
            "La ringrazio per averci contattato. Arrivederci e buona giornata.",
            "Saremo lieti di accoglierla nel nostro salone.",

            # Colloquiali
            "Ok perfetto! Allora ci vediamo sabato!",
            "Nessun problema, possiamo spostare senza problemi.",

            # Edge cases
            "Mmm...",
            "Sì.",
        ]

        print(f"\n{'='*60}")
        print(f"  PIPER TTS LATENCY TEST")
        print(f"  Piper: {self.piper_path}")
        print(f"  Model: {self.model_path}")
        print(f"  Samples: {len(test_phrases)}")
        print(f"  Target: p95 < 800ms")
        print(f"{'='*60}\n")

        for idx, phrase in enumerate(test_phrases, 1):
            try:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    tmp_path = tmp.name

                start = time.time()

                # Run piper
                result = subprocess.run(
                    [self.piper_path, "--model", self.model_path, "--output_file", tmp_path],
                    input=phrase.encode(),
                    capture_output=True,
                    timeout=10
                )

                elapsed = time.time() - start
                elapsed_ms = elapsed * 1000

                # Get file size (proxy for audio length)
                file_size = os.path.getsize(tmp_path) if os.path.exists(tmp_path) else 0

                self.latencies.append(elapsed_ms)
                self.results.append({
                    "phrase": phrase,
                    "char_count": len(phrase),
                    "latency_ms": elapsed_ms,
                    "audio_bytes": file_size
                })

                # Cleanup
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

                status = "✅" if elapsed_ms < 800 else "⚠️"
                print(f"{idx:2d}. {status} [{elapsed_ms:6.0f}ms] {phrase[:50]}...")

            except subprocess.TimeoutExpired:
                print(f"{idx:2d}. ❌ TIMEOUT: {phrase[:50]}...")
                self.latencies.append(10000)  # 10 sec penalty
            except Exception as e:
                print(f"{idx:2d}. ❌ ERROR: {e}")
                self.latencies.append(10000)

        # Statistics
        latencies_arr = np.array(self.latencies)

        print(f"\n{'='*60}")
        print(f"  LATENCY STATISTICS")
        print(f"{'='*60}")
        print(f"  Mean:   {latencies_arr.mean():7.1f} ms")
        print(f"  Median: {np.median(latencies_arr):7.1f} ms")
        print(f"  p95:    {np.percentile(latencies_arr, 95):7.1f} ms")
        print(f"  p99:    {np.percentile(latencies_arr, 99):7.1f} ms")
        print(f"  Min:    {latencies_arr.min():7.1f} ms")
        print(f"  Max:    {latencies_arr.max():7.1f} ms")
        print(f"{'='*60}")

        # Latency by phrase length
        print("\n  Latency by phrase length:")
        short = [r for r in self.results if r['char_count'] < 30]
        medium = [r for r in self.results if 30 <= r['char_count'] < 80]
        long = [r for r in self.results if r['char_count'] >= 80]

        if short:
            print(f"    Short (<30 chars):  {np.mean([r['latency_ms'] for r in short]):.0f}ms avg")
        if medium:
            print(f"    Medium (30-80):     {np.mean([r['latency_ms'] for r in medium]):.0f}ms avg")
        if long:
            print(f"    Long (80+):         {np.mean([r['latency_ms'] for r in long]):.0f}ms avg")

        p95 = float(np.percentile(latencies_arr, 95))
        pass_criteria = p95 < 800

        result = {
            "timestamp": datetime.now().isoformat(),
            "piper_path": self.piper_path,
            "model_path": self.model_path,
            "mean_latency_ms": float(latencies_arr.mean()),
            "median_latency_ms": float(np.median(latencies_arr)),
            "p95_latency_ms": p95,
            "p99_latency_ms": float(np.percentile(latencies_arr, 99)),
            "min_latency_ms": float(latencies_arr.min()),
            "max_latency_ms": float(latencies_arr.max()),
            "samples": len(test_phrases),
            "pass_criteria": pass_criteria,
            "results": self.results
        }

        # Save results
        with open("piper_validation_results.json", "w") as f:
            json.dump(result, f, indent=2)

        print(f"\n{'='*60}")
        if pass_criteria:
            print(f"  ✅ PASS: Piper TTS p95 latency {p95:.0f}ms < 800ms")
            print(f"  Recommendation: Piper TTS suitable for real-time voice")
        elif p95 < 1500:
            print(f"  ⚠️  YELLOW: p95 latency {p95:.0f}ms (800-1500ms)")
            print(f"  Recommendation: Acceptable with async TTS or buffering")
        else:
            print(f"  ❌ FAIL: p95 latency {p95:.0f}ms > 1500ms")
            print(f"  Recommendation: Not viable for real-time voice UX")
        print(f"{'='*60}\n")

        return result


if __name__ == "__main__":
    print("\n" + "="*60)
    print("  FLUXION VOICE AGENT - PIPER TTS VALIDATION")
    print("="*60)

    validator = PiperLatencyValidator()
    results = validator.test_tts_latency()
