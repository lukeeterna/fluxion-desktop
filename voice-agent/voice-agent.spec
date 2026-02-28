# -*- mode: python ; coding: utf-8 -*-
# FLUXION Voice Agent — PyInstaller spec (cross-platform: macOS + Windows)
#
# Build:
#   macOS/Linux: pyinstaller voice-agent.spec
#   Windows:     pyinstaller voice-agent.spec
#
# Output: dist/voice-agent  (Unix) | dist/voice-agent.exe  (Windows)

import sys
import os
from pathlib import Path

block_cipher = None
IS_WINDOWS = sys.platform == "win32"

# SPECPATH è fornito da PyInstaller: directory del file .spec
BASE = Path(SPECPATH)  # noqa: F821 — variabile globale PyInstaller

# ── Dati da includere nel bundle ──────────────────────────────────────
datas = [
    # FAQ knowledge base (tutte le verticali)
    (str(BASE / "data"), "data"),
    # Silero VAD — modello ONNX (~2MB)
    (str(BASE / "models" / "silero_vad.onnx"), "models"),
]

# Piper TTS models (opzionale — inclusi se presenti)
piper_models = BASE / "models" / "tts"
if piper_models.exists() and any(piper_models.iterdir()):
    datas.append((str(piper_models), "models/tts"))

# Verticals config (se directory esiste)
verticals_dir = BASE / "verticals"
if verticals_dir.exists():
    datas.append((str(verticals_dir), "verticals"))

# ── Hidden imports ─────────────────────────────────────────────────────
# PyInstaller non trova automaticamente i moduli importati dinamicamente
hidden_imports = [
    # HTTP server
    "aiohttp",
    "aiohttp.web",
    "aiohttp.web_runner",
    # Groq / API
    "groq",
    "groq._client",
    # Env
    "dotenv",
    # STT
    "faster_whisper",
    "ctranslate2",
    # VAD
    "onnxruntime",
    "onnxruntime.capi",
    # Audio
    "sounddevice",
    "soundfile",
    # NLU
    "sentence_transformers",
    "sentence_transformers.models",
    "faiss",
    "spacy",
    "transformers",
    "dateparser",
    "dateparser.languages",
    "Levenshtein",
    # Utility
    "scipy",
    "numpy",
    "sklearn",
    "sklearn.metrics",
    # TTS
    "piper_onnx",
    # FLUXION — src core
    "src",
    "src.orchestrator",
    "src.booking_state_machine",
    "src.groq_client",
    "src.tts",
    "src.stt",
    "src.intent_classifier",
    "src.entity_extractor",
    "src.disambiguation_handler",
    "src.analytics",
    "src.session_manager",
    "src.turn_tracker",
    "src.faq_manager",
    "src.faq_retriever",
    "src.http_client",
    "src.latency_optimizer",
    "src.vad_http_handler",
    "src.supplier_email_service",
    "src.booking_manager",
    "src.booking_orchestrator",
    "src.availability_checker",
    "src.vertical_loader",
    "src.vertical_integration",
    "src.error_recovery",
    "src.italian_regex",
    "src.sentiment",
    # FLUXION — submoduli
    "src.vad",
    "src.vad.ten_vad_integration",
    "src.vad.vad_pipeline_integration",
    "src.nlu",
    "src.nlu.semantic_classifier",
    "src.nlu.italian_nlu",
]

# Windows: aggiungi pyttsx3 per SystemTTS fallback
if IS_WINDOWS:
    hidden_imports += [
        "pyttsx3",
        "pyttsx3.drivers",
        "pyttsx3.drivers.sapi5",
        "win32com",
        "win32com.client",
        "webrtcvad",
    ]

# ── Esclusioni (riducono dimensione bundle) ───────────────────────────
excludes = [
    # TTS primario pesante — non nel bundle Windows (2.5GB)
    "chatterbox",
    "torchaudio",
    "torch",
    # VoIP — non usato in v1.0
    "pipecat",
    "aiortc",
    "aioice",
    "av",
    # webrtcvad-wheels ha hook PyInstaller incompatibile — Silero ONNX è il VAD primario
    "webrtcvad",
    # UI e tooling non necessari
    "tkinter",
    "matplotlib",
    "PIL",
    "IPython",
    "jupyter",
    "notebook",
    "pytest",
]

# ── Analysis ──────────────────────────────────────────────────────────
a = Analysis(
    ["main.py"],
    pathex=[str(BASE), str(BASE / "src")],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)  # noqa: F821

exe = EXE(  # noqa: F821
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="voice-agent",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,          # compressione UPX (riduce ~30% su Windows)
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,      # console visibile — utile per debug produzione
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,         # TODO: aggiungere icona Fluxion .ico per Windows
)
