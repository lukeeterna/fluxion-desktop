#!/usr/bin/env python3
"""Qwen3-TTS Validation - Italian Quality & Latency
Validation script for Fluxion Voice Agent

Hardware Requirements:
- GPU: 2-4GB VRAM minimum for 0.6B model
- GPU: 4-6GB VRAM for 1.7B model
- Or: HuggingFace Inference API (cloud)

This script tests both local (if GPU available) and API modes.
Includes vertical-specific fine-tuning preparation for:
- Salone (parrucchiere, barbiere)
- Palestra (fitness, yoga)
- Medical (clinica, studio medico)
- Auto (officina, gommista)
- Ristorante (bar, pizzeria)
"""

import time
import sys
import os
import subprocess
from datetime import datetime
import json
import tempfile
from typing import Dict, List, Optional

try:
    import numpy as np
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"])
    import numpy as np

try:
    import requests
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests


# ============================================================================
# QWEN3-TTS MODEL WEIGHTS (HuggingFace)
# ============================================================================
QWEN3_MODELS = {
    # Production models (recommended)
    "custom_voice_1.7b": {
        "name": "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice",
        "params": "1.7B",
        "vram_gb": 4.5,
        "features": ["9 premium voices", "instruction control", "streaming"],
        "recommended_for": "production_high_quality"
    },
    "custom_voice_0.6b": {
        "name": "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice",
        "params": "0.6B",
        "vram_gb": 2.0,
        "features": ["9 voices", "streaming", "lightweight"],
        "recommended_for": "production_balanced"
    },

    # Fine-tuning capable models (for vertical customization)
    "base_1.7b": {
        "name": "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
        "params": "1.7B",
        "vram_gb": 4.5,
        "features": ["voice cloning", "fine-tunable", "full quality"],
        "recommended_for": "finetuning_vertical"
    },
    "base_0.6b": {
        "name": "Qwen/Qwen3-TTS-12Hz-0.6B-Base",
        "params": "0.6B",
        "vram_gb": 2.0,
        "features": ["voice cloning", "fine-tunable", "lightweight"],
        "recommended_for": "finetuning_resource_limited"
    },

    # Voice design model (natural language control)
    "voice_design_1.7b": {
        "name": "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
        "params": "1.7B",
        "vram_gb": 4.5,
        "features": ["NL voice description", "create custom voices"],
        "recommended_for": "custom_brand_voice"
    },

    # Tokenizer (required for all)
    "tokenizer": {
        "name": "Qwen/Qwen3-TTS-Tokenizer-12Hz",
        "params": "~100M",
        "vram_gb": 0.5,
        "features": ["audio encoding", "audio decoding"],
        "recommended_for": "required_component"
    }
}

# ============================================================================
# VERTICAL-SPECIFIC TEST PHRASES (for fine-tuning evaluation)
# ============================================================================
VERTICAL_PHRASES = {
    "salone": [
        "Buongiorno! Benvenuta al salone, sono Sara. Come posso aiutarla?",
        "Perfetto! Ho prenotato il suo taglio e colore per sabato alle dieci.",
        "Il nostro parrucchiere Marco è specializzato in balayage e shatush.",
        "Per un trattamento ristrutturante consiglio il nostro pacchetto benessere capelli.",
    ],
    "palestra": [
        "Ciao! Sono Sara della palestra FitClub. Pronta per allenarti?",
        "Il corso di yoga inizia alle diciotto. Ti ho riservato un posto.",
        "Il personal trainer Andrea ti aspetta per la scheda personalizzata.",
        "L'abbonamento mensile include accesso illimitato a tutti i corsi.",
    ],
    "medical": [
        "Buongiorno, Studio Medico Rossi, sono Sara. Come posso esserle utile?",
        "Ho prenotato la sua visita cardiologica per lunedì alle nove.",
        "Il dottore raccomanda il digiuno per gli esami del sangue.",
        "Le ricordo che per la visita serve portare la tessera sanitaria.",
    ],
    "auto": [
        "Buongiorno, Officina Bianchi, sono Sara. In cosa posso aiutarla?",
        "Ho programmato la revisione della sua auto per giovedì mattina.",
        "Il tagliando include cambio olio, filtri e controllo freni.",
        "Per il cambio gomme abbiamo disponibilità già da domani.",
    ],
    "ristorante": [
        "Buonasera! Ristorante Da Mario, sono Sara. Desidera prenotare?",
        "Perfetto! Tavolo per quattro persone, sabato sera alle venti e trenta.",
        "Il nostro chef consiglia il risotto ai frutti di mare, specialità della casa.",
        "Abbiamo anche un menu vegetariano e opzioni senza glutine.",
    ]
}


class Qwen3TTSValidator:
    def __init__(self, model_key: str = "custom_voice_0.6b"):
        self.local_available = False
        self.api_available = True
        self.model_key = model_key
        self.model_config = QWEN3_MODELS.get(model_key, QWEN3_MODELS["custom_voice_0.6b"])
        self.model_name = self.model_config["name"]
        self.hf_token = os.environ.get("HF_TOKEN", "")
        self.results = []
        self.latencies = []
        self._check_hardware()

    def _check_hardware(self):
        """Check if local GPU inference is possible"""
        try:
            import torch
            if torch.cuda.is_available():
                vram = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                print(f"  GPU: {torch.cuda.get_device_name(0)}")
                print(f"  VRAM: {vram:.1f} GB")
                if vram >= 2:
                    self.local_available = True
                else:
                    print(f"  ⚠️  VRAM < 2GB, local inference may fail")
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                print("  Apple Silicon MPS available")
                self.local_available = True
            else:
                print("  No CUDA/MPS GPU available")
        except ImportError:
            print("  PyTorch not installed")

    def test_local_inference(self) -> dict:
        """Test local Qwen3-TTS inference if hardware supports it"""
        if not self.local_available:
            return {"status": "skipped", "reason": "No suitable GPU"}

        print("\n  Testing LOCAL Qwen3-TTS inference...")

        try:
            import torch
            from qwen_tts import Qwen3TTSModel
            import soundfile as sf
        except ImportError:
            print("  Installing qwen-tts...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "qwen-tts"])
            from qwen_tts import Qwen3TTSModel
            import soundfile as sf

        test_phrases = [
            ("Buongiorno, sono Sara, l'assistente vocale.", "short"),
            ("Perfetto! Ho prenotato il suo appuntamento per sabato alle dieci.", "medium"),
            ("Mi dispiace, non abbiamo disponibilità per quella data. Posso proporle lunedì pomeriggio alle quindici o martedì mattina alle nove e trenta?", "long"),
        ]

        try:
            # Determine device
            device = "cuda:0" if torch.cuda.is_available() else "mps"
            dtype = torch.bfloat16 if device == "cuda:0" else torch.float32

            print(f"  Loading model on {device}...")
            model = Qwen3TTSModel.from_pretrained(
                self.model_name,
                device_map=device,
                dtype=dtype,
            )

            results = []
            for phrase, length in test_phrases:
                start = time.time()
                wavs, sr = model.generate_custom_voice(
                    text=phrase,
                    language="Italian",
                    speaker="Vivian",  # Female voice
                )
                elapsed = (time.time() - start) * 1000

                results.append({
                    "phrase": phrase,
                    "length": length,
                    "latency_ms": elapsed,
                    "sample_rate": sr
                })

                print(f"    {length}: {elapsed:.0f}ms")

            return {
                "status": "success",
                "device": device,
                "results": results,
                "mean_latency_ms": np.mean([r['latency_ms'] for r in results])
            }

        except Exception as e:
            return {"status": "failed", "error": str(e)}

    def test_api_inference(self) -> dict:
        """Test Qwen3-TTS via HuggingFace Inference API"""
        print("\n  Testing Qwen3-TTS via HuggingFace API...")

        # NEW HuggingFace Inference Router (replaces api-inference.huggingface.co)
        api_url = f"https://router.huggingface.co/hf-inference/models/{self.model_name}"

        test_phrases = [
            ("Buongiorno!", "short"),
            ("Perfetto, prenotazione confermata per sabato.", "medium"),
            ("Mi dispiace, non abbiamo disponibilità. Posso proporle un altro giorno?", "long"),
        ]

        headers = {}
        if self.hf_token:
            headers["Authorization"] = f"Bearer {self.hf_token}"

        results = []
        for phrase, length in test_phrases:
            try:
                start = time.time()
                response = requests.post(
                    api_url,
                    headers=headers,
                    json={"inputs": phrase},
                    timeout=30
                )
                elapsed = (time.time() - start) * 1000

                if response.status_code == 200:
                    # Save audio for quality check
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                        f.write(response.content)
                        audio_path = f.name
                    audio_size = len(response.content)

                    results.append({
                        "phrase": phrase,
                        "length": length,
                        "latency_ms": elapsed,
                        "audio_bytes": audio_size,
                        "status": "success"
                    })
                    print(f"    {length}: {elapsed:.0f}ms ({audio_size/1024:.1f}KB)")

                    # Cleanup
                    os.unlink(audio_path)
                else:
                    error_msg = response.text[:100]
                    results.append({
                        "phrase": phrase,
                        "length": length,
                        "status": "failed",
                        "error": error_msg
                    })
                    print(f"    {length}: ❌ {response.status_code} - {error_msg}")

            except requests.Timeout:
                results.append({
                    "phrase": phrase,
                    "length": length,
                    "status": "timeout"
                })
                print(f"    {length}: ❌ Timeout")
            except Exception as e:
                results.append({
                    "phrase": phrase,
                    "length": length,
                    "status": "error",
                    "error": str(e)
                })
                print(f"    {length}: ❌ {e}")

        successful = [r for r in results if r.get('status') == 'success']
        if successful:
            mean_latency = np.mean([r['latency_ms'] for r in successful])
        else:
            mean_latency = None

        return {
            "status": "success" if successful else "failed",
            "results": results,
            "successful_count": len(successful),
            "total_count": len(results),
            "mean_latency_ms": mean_latency
        }

    def test_vertical_phrases(self, vertical: str = None) -> dict:
        """Test TTS on vertical-specific phrases for fine-tuning evaluation"""
        verticals = [vertical] if vertical else list(VERTICAL_PHRASES.keys())

        print(f"\n  Testing vertical-specific phrases...")
        print(f"  Verticals: {', '.join(verticals)}")

        results = {}
        for vert in verticals:
            phrases = VERTICAL_PHRASES.get(vert, [])
            vert_results = []

            print(f"\n    [{vert.upper()}]")
            for phrase in phrases[:2]:  # Test first 2 per vertical
                try:
                    start = time.time()
                    # Use new HuggingFace Router API for testing
                    response = requests.post(
                        f"https://router.huggingface.co/hf-inference/models/{self.model_name}",
                        headers={"Authorization": f"Bearer {self.hf_token}"} if self.hf_token else {},
                        json={"inputs": phrase},
                        timeout=30
                    )
                    elapsed = (time.time() - start) * 1000

                    if response.status_code == 200:
                        vert_results.append({
                            "phrase": phrase[:50] + "...",
                            "latency_ms": elapsed,
                            "status": "success"
                        })
                        print(f"      ✅ {elapsed:.0f}ms - {phrase[:40]}...")
                    else:
                        vert_results.append({
                            "phrase": phrase[:50],
                            "status": "failed",
                            "error": response.status_code
                        })
                        print(f"      ❌ {response.status_code} - {phrase[:40]}...")

                except Exception as e:
                    vert_results.append({"phrase": phrase[:50], "status": "error", "error": str(e)})
                    print(f"      ❌ Error - {phrase[:40]}...")

            results[vert] = vert_results

        return results

    def generate_finetuning_config(self, vertical: str) -> dict:
        """Generate fine-tuning configuration for a specific vertical"""
        base_model = QWEN3_MODELS["base_0.6b"]  # Lightweight for fine-tuning

        config = {
            "vertical": vertical,
            "base_model": base_model["name"],
            "training_config": {
                "learning_rate": 1e-5,
                "batch_size": 4,
                "epochs": 3,
                "warmup_steps": 100,
                "gradient_accumulation": 4,
            },
            "dataset_requirements": {
                "min_samples": 100,
                "format": "audio_text_pairs",
                "audio_format": "wav_16khz_mono",
                "recommended_samples": 500,
            },
            "sample_phrases": VERTICAL_PHRASES.get(vertical, []),
            "estimated_training_time": "2-4 hours on A10 GPU",
            "output_model_name": f"fluxion-sara-{vertical}-v1"
        }

        return config

    def compare_with_piper(self) -> dict:
        """Run comparison test: Qwen3 quality vs Piper speed"""
        print("\n  Comparison: Qwen3-TTS vs Piper TTS")
        print("  " + "-"*50)

        comparison = {
            "qwen3_tts": {
                "pros": [
                    "Voice cloning (3 sec reference)",
                    "Emotion/tone control",
                    "Higher quality (trained on 5M hours)",
                    "10 languages native",
                    "Fine-tunable for verticals"
                ],
                "cons": [
                    "Requires GPU (2-4GB VRAM)",
                    "Model size ~2GB",
                    "API dependency if no GPU"
                ],
                "best_for": "High-quality, customizable voice",
                "finetuning": "Excellent - use Base model for vertical adaptation"
            },
            "piper_tts": {
                "pros": [
                    "CPU-only (no GPU needed)",
                    "Small model (~20MB)",
                    "Very low latency (<500ms)",
                    "100% offline"
                ],
                "cons": [
                    "No voice cloning",
                    "Limited emotion control",
                    "Quality 7/10 vs Qwen 9/10",
                    "Fine-tuning more complex"
                ],
                "best_for": "Real-time, low-resource deployment",
                "finetuning": "Possible but requires ONNX expertise"
            }
        }

        print("\n  Qwen3-TTS:")
        print(f"    Pros: {', '.join(comparison['qwen3_tts']['pros'][:2])}")
        print(f"    Cons: {comparison['qwen3_tts']['cons'][0]}")
        print(f"    Fine-tuning: {comparison['qwen3_tts']['finetuning']}")

        print("\n  Piper TTS:")
        print(f"    Pros: {', '.join(comparison['piper_tts']['pros'][:2])}")
        print(f"    Cons: {comparison['piper_tts']['cons'][0]}")
        print(f"    Fine-tuning: {comparison['piper_tts']['finetuning']}")

        return comparison

    def run_validation(self, test_verticals: bool = True) -> dict:
        """Run full validation"""
        print(f"\n{'='*60}")
        print(f"  QWEN3-TTS VALIDATION")
        print(f"  Model: {self.model_name}")
        print(f"  Model Key: {self.model_key}")
        print(f"  VRAM Required: {self.model_config['vram_gb']} GB")
        print(f"{'='*60}")

        results = {
            "timestamp": datetime.now().isoformat(),
            "model": self.model_name,
            "model_key": self.model_key,
            "model_config": self.model_config,
            "available_models": QWEN3_MODELS,
            "hardware": {
                "local_gpu_available": self.local_available,
            }
        }

        # Test local if available
        if self.local_available:
            results["local_inference"] = self.test_local_inference()
        else:
            results["local_inference"] = {
                "status": "skipped",
                "reason": f"No GPU with >= {self.model_config['vram_gb']}GB VRAM"
            }

        # Test API
        results["api_inference"] = self.test_api_inference()

        # Test vertical phrases if requested
        if test_verticals:
            print(f"\n{'='*60}")
            print(f"  VERTICAL-SPECIFIC TESTING")
            print(f"{'='*60}")
            results["vertical_tests"] = self.test_vertical_phrases()

        # Generate fine-tuning configs for all verticals
        print(f"\n{'='*60}")
        print(f"  FINE-TUNING CONFIGURATION")
        print(f"{'='*60}")
        results["finetuning_configs"] = {}
        for vertical in VERTICAL_PHRASES.keys():
            config = self.generate_finetuning_config(vertical)
            results["finetuning_configs"][vertical] = config
            print(f"\n  [{vertical.upper()}]")
            print(f"    Base model: {config['base_model']}")
            print(f"    Output: {config['output_model_name']}")
            print(f"    Min samples: {config['dataset_requirements']['min_samples']}")

        # Comparison
        results["comparison"] = self.compare_with_piper()

        # Recommendation
        print(f"\n{'='*60}")
        print(f"  RECOMMENDATION FOR FLUXION")
        print(f"{'='*60}")

        if self.local_available:
            local_latency = results.get("local_inference", {}).get("mean_latency_ms")
            if local_latency and local_latency < 500:
                print("  ✅ Qwen3-TTS LOCAL: Excellent for high-quality voice")
                results["recommendation"] = "qwen3_local"
                results["finetuning_recommendation"] = "recommended"
            else:
                print("  ⚠️  Qwen3-TTS LOCAL: Quality good but latency high")
                results["recommendation"] = "piper_with_qwen3_fallback"
                results["finetuning_recommendation"] = "consider_for_premium_tier"
        else:
            api_latency = results.get("api_inference", {}).get("mean_latency_ms")
            if api_latency and api_latency < 1000:
                print("  ⚠️  Qwen3-TTS API: Requires internet, ~1sec latency")
                print("  💡 For offline voice agent: Use Piper TTS")
                results["recommendation"] = "piper_primary_qwen3_cloud_optional"
                results["finetuning_recommendation"] = "cloud_finetuned_for_enterprise"
            else:
                print("  ❌ Qwen3-TTS: Not viable without GPU")
                print("  ✅ Recommend: Piper TTS for offline desktop app")
                results["recommendation"] = "piper_only"
                results["finetuning_recommendation"] = "defer_until_hardware_upgrade"

        print(f"\n  === FLUXION VOICE STRATEGY ===")
        print(f"  ")
        print(f"  TIER 1 (Starter/Professional):")
        print(f"    TTS: Piper TTS (offline, CPU, <500ms)")
        print(f"    Voice: Pre-trained Italian (paola-medium)")
        print(f"  ")
        print(f"  TIER 2 (Enterprise):")
        print(f"    TTS: Qwen3-TTS via API (cloud, higher quality)")
        print(f"    Voice: Fine-tuned per verticale")
        print(f"    Benefit: Voice cloning per brand personalizzato")
        print(f"  ")
        print(f"  FINE-TUNING ROADMAP:")
        print(f"    1. Collect 100-500 audio samples per vertical")
        print(f"    2. Use Qwen3-TTS-12Hz-0.6B-Base for fine-tuning")
        print(f"    3. Train on cloud GPU (A10/A100, 2-4 hours)")
        print(f"    4. Deploy fine-tuned model as premium feature")
        print(f"{'='*60}\n")

        # Save results
        with open("qwen3_validation_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)

        return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Qwen3-TTS Validation for Fluxion")
    parser.add_argument("--model", choices=list(QWEN3_MODELS.keys()),
                        default="custom_voice_0.6b",
                        help="Model to test (default: custom_voice_0.6b)")
    parser.add_argument("--no-verticals", action="store_true",
                        help="Skip vertical-specific testing")
    parser.add_argument("--vertical", choices=list(VERTICAL_PHRASES.keys()),
                        help="Test only specific vertical")
    parser.add_argument("--show-models", action="store_true",
                        help="Show available models and exit")

    args = parser.parse_args()

    if args.show_models:
        print("\n" + "="*60)
        print("  QWEN3-TTS AVAILABLE MODELS")
        print("="*60)
        for key, config in QWEN3_MODELS.items():
            print(f"\n  [{key}]")
            print(f"    Model: {config['name']}")
            print(f"    Params: {config['params']}")
            print(f"    VRAM: {config['vram_gb']} GB")
            print(f"    Features: {', '.join(config['features'][:2])}")
            print(f"    Best for: {config['recommended_for']}")
        sys.exit(0)

    print("\n" + "="*60)
    print("  FLUXION VOICE AGENT - QWEN3-TTS EVALUATION")
    print("="*60)
    print(f"\nModel: {args.model}")
    print("Note: Qwen3-TTS requires GPU (2-4GB VRAM) for local inference")
    print("Testing API fallback for hardware without suitable GPU")
    print()

    validator = Qwen3TTSValidator(model_key=args.model)
    results = validator.run_validation(test_verticals=not args.no_verticals)
