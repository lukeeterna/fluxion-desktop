#!/usr/bin/env python3
"""
FLUXION Voice Agent - Model Downloader

Downloads required models for NLU and TTS:
1. spaCy Italian model (it_core_news_lg) - 43MB
2. Aurora TTS voice (community, Dec 2024) - 63MB
3. UmBERTo (auto-downloaded on first use) - ~440MB

Usage:
    python scripts/download_models.py [--all | --spacy | --aurora | --umberto]
"""

import os
import sys
import argparse
import subprocess
import urllib.request
from pathlib import Path


# Model URLs (correct paths from HuggingFace)
AURORA_MODEL_URL = "https://huggingface.co/kirys79/piper_italiano/resolve/main/Aurora/it_IT-aurora-medium.onnx"
AURORA_CONFIG_URL = "https://huggingface.co/kirys79/piper_italiano/resolve/main/Aurora/it_IT-aurora-medium.onnx.json"

# Models directory
SCRIPT_DIR = Path(__file__).parent
VOICE_AGENT_DIR = SCRIPT_DIR.parent
MODELS_DIR = VOICE_AGENT_DIR / "models" / "tts"


def download_spacy():
    """Download spaCy Italian model."""
    print("\n" + "=" * 60)
    print("Downloading spaCy Italian model (it_core_news_lg)")
    print("=" * 60)

    try:
        subprocess.run(
            [sys.executable, "-m", "spacy", "download", "it_core_news_lg"],
            check=True
        )
        print("spaCy Italian model downloaded successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to download spaCy model: {e}")
        print("Try manually: python -m spacy download it_core_news_lg")
        return False


def download_aurora():
    """Download Aurora TTS voice."""
    print("\n" + "=" * 60)
    print("Downloading Aurora TTS voice (63MB)")
    print("=" * 60)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    model_path = MODELS_DIR / "it_IT-aurora-medium.onnx"
    config_path = MODELS_DIR / "it_IT-aurora-medium.onnx.json"

    try:
        # Download model
        if not model_path.exists():
            print(f"Downloading: {AURORA_MODEL_URL}")
            urllib.request.urlretrieve(AURORA_MODEL_URL, model_path)
            print(f"Saved to: {model_path}")
        else:
            print(f"Model already exists: {model_path}")

        # Download config
        if not config_path.exists():
            print(f"Downloading: {AURORA_CONFIG_URL}")
            urllib.request.urlretrieve(AURORA_CONFIG_URL, config_path)
            print(f"Saved to: {config_path}")
        else:
            print(f"Config already exists: {config_path}")

        print("Aurora TTS voice downloaded successfully!")
        return True

    except Exception as e:
        print(f"Failed to download Aurora voice: {e}")
        return False


def download_umberto():
    """Download UmBERTo model (optional, auto-downloads on first use)."""
    print("\n" + "=" * 60)
    print("Pre-downloading UmBERTo model (~440MB)")
    print("=" * 60)

    try:
        from transformers import pipeline
        import torch

        device = 0 if torch.cuda.is_available() else -1
        print(f"Using device: {'CUDA' if device == 0 else 'CPU'}")

        print("Loading UmBERTo (first download may take a few minutes)...")
        classifier = pipeline(
            "zero-shot-classification",
            model="Musixmatch/umberto-commoncrawl-cased-v1",
            device=device,
        )

        # Test it
        result = classifier("Io non sono mai stato da voi", ["nuovo cliente", "prenotazione"])
        print(f"Test result: {result['labels'][0]} ({result['scores'][0]:.2f})")

        print("UmBERTo model downloaded successfully!")
        return True

    except ImportError:
        print("transformers not installed. Run: pip install transformers torch")
        return False
    except Exception as e:
        print(f"Failed to download UmBERTo: {e}")
        return False


def check_models():
    """Check which models are installed."""
    print("\n" + "=" * 60)
    print("Model Status")
    print("=" * 60)

    # spaCy
    try:
        import spacy
        nlp = spacy.load("it_core_news_lg")
        print("spaCy it_core_news_lg: INSTALLED")
    except (ImportError, OSError):
        print("spaCy it_core_news_lg: NOT INSTALLED")

    # Aurora
    model_path = MODELS_DIR / "it_IT-aurora-medium.onnx"
    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024 * 1024)
        print(f"Aurora TTS voice: INSTALLED ({size_mb:.1f}MB)")
    else:
        print("Aurora TTS voice: NOT INSTALLED")

    # UmBERTo
    try:
        from transformers import AutoModel
        cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
        umberto_dirs = list(cache_dir.glob("*umberto*"))
        if umberto_dirs:
            print("UmBERTo: INSTALLED (cached)")
        else:
            print("UmBERTo: NOT INSTALLED (will download on first use)")
    except ImportError:
        print("UmBERTo: transformers not installed")


def main():
    parser = argparse.ArgumentParser(description="Download FLUXION Voice Agent models")
    parser.add_argument("--all", action="store_true", help="Download all models")
    parser.add_argument("--spacy", action="store_true", help="Download spaCy Italian")
    parser.add_argument("--aurora", action="store_true", help="Download Aurora TTS voice")
    parser.add_argument("--umberto", action="store_true", help="Pre-download UmBERTo")
    parser.add_argument("--check", action="store_true", help="Check installed models")

    args = parser.parse_args()

    # Default: download all essential models
    if not any([args.all, args.spacy, args.aurora, args.umberto, args.check]):
        args.spacy = True
        args.aurora = True

    print("=" * 60)
    print("FLUXION Voice Agent - Model Downloader")
    print("=" * 60)

    if args.check:
        check_models()
        return

    success = True

    if args.all or args.spacy:
        if not download_spacy():
            success = False

    if args.all or args.aurora:
        if not download_aurora():
            success = False

    if args.all or args.umberto:
        if not download_umberto():
            success = False

    # Show final status
    check_models()

    if success:
        print("\n All models downloaded successfully!")
        print("\nTo test the voice agent:")
        print("  cd voice-agent")
        print("  python -m src.nlu.italian_nlu  # Test NLU")
        print("  python -m src.tts              # Test TTS")
    else:
        print("\n Some models failed to download. Check errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
