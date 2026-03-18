# -*- mode: python ; coding: utf-8 -*-
# FLUXION Voice Agent — PyInstaller spec (cross-platform: macOS + Windows)
#
# Build (on iMac 192.168.1.2):
#   macOS:   pyinstaller voice-agent.spec
#   Windows: pyinstaller voice-agent.spec
#
# Output: dist/voice-agent  (Unix) | dist/voice-agent.exe  (Windows)
#
# Tauri sidecar naming convention:
#   macOS ARM:   voice-agent-aarch64-apple-darwin
#   macOS Intel: voice-agent-x86_64-apple-darwin
#   Windows:     voice-agent-x86_64-pc-windows-msvc.exe

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

# Sales knowledge base (se esiste)
sales_kb = BASE / "data" / "sales"
if sales_kb.exists():
    datas.append((str(sales_kb), "data/sales"))

# ── Hidden imports ─────────────────────────────────────────────────────
# PyInstaller non trova automaticamente i moduli importati dinamicamente
hidden_imports = [
    # HTTP server
    "aiohttp",
    "aiohttp.web",
    "aiohttp.web_runner",
    "aiohttp.web_request",
    "aiohttp.web_response",
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
    # NLU — LLM-based (2026 architecture)
    "dateparser",
    "dateparser.languages",
    "Levenshtein",
    "rapidfuzz",
    "rapidfuzz.fuzz",
    "rapidfuzz.process",
    "jellyfish",
    # Utility
    "numpy",
    # TTS — Edge-TTS (quality) + Piper (fast/offline)
    "edge_tts",
    "edge_tts.communicate",
    "piper_onnx",
    # System monitoring
    "psutil",
    # Scheduler
    "apscheduler",
    "apscheduler.schedulers.asyncio",
    # FLUXION — src core
    "src",
    "src.orchestrator",
    "src.booking_state_machine",
    "src.groq_client",
    "src.groq_key_pool",
    "src.tts",
    "src.tts_engine",
    "src.tts_download_manager",
    "src.stt",
    "src.intent_classifier",
    "src.intent_lru_cache",
    "src.entity_extractor",
    "src.disambiguation_handler",
    "src.analytics",
    "src.audit_client",
    "src.session_manager",
    "src.turn_tracker",
    "src.faq_manager",
    "src.faq_retriever",
    "src.http_client",
    "src.latency_optimizer",
    "src.vad_http_handler",
    "src.vad_wrapper",
    "src.supplier_email_service",
    "src.booking_manager",
    "src.availability_checker",
    "src.vertical_loader",
    "src.vertical_integration",
    "src.vertical_schemas",
    "src.error_recovery",
    "src.italian_regex",
    "src.sentiment",
    "src.service_resolver",
    "src.operator_gender",
    "src.name_corrector",
    "src.whatsapp",
    "src.whatsapp_callback",
    "src.reminder_scheduler",
    "src.sip_client",
    "src.voip",
    # FLUXION — Sales FSM
    "src.sales_state_machine",
    "src.sales_kb_loader",
    # FLUXION — submoduli VAD
    "src.vad",
    "src.vad.ten_vad_integration",
    "src.vad.vad_pipeline_integration",
    # FLUXION — submoduli NLU (LLM-based)
    "src.nlu",
    "src.nlu.llm_nlu",
    "src.nlu.providers",
    "src.nlu.schemas",
    "src.nlu.template_fallback",
    "src.nlu.semantic_classifier",
]

# Windows: aggiungi pyttsx3 per SystemTTS fallback
if IS_WINDOWS:
    hidden_imports += [
        "pyttsx3",
        "pyttsx3.drivers",
        "pyttsx3.drivers.sapi5",
        "win32com",
        "win32com.client",
    ]

# ── Esclusioni (riducono dimensione bundle) ───────────────────────────
excludes = [
    # PyTorch / heavy ML — non necessari (LLM via API, TTS via Edge-TTS/Piper)
    "torch",
    "torchaudio",
    "torchvision",
    "transformers",
    "chatterbox",
    # spaCy — rimosso in S83, NLU ora è LLM-based
    "spacy",
    # sentence-transformers / faiss — FAQ ora usa keyword search
    "sentence_transformers",
    "faiss",
    # scipy / sklearn — non più necessari
    "scipy",
    "sklearn",
    # VoIP — non usato in v1.0
    "pipecat",
    "pipecat_ai",
    "aiortc",
    "aioice",
    "av",
    # huggingface_hub — download manager non necessario nel bundle
    "huggingface_hub",
    # webrtcvad — hook PyInstaller incompatibile, Silero ONNX è il VAD primario
    "webrtcvad",
    # UI e tooling non necessari
    "tkinter",
    "matplotlib",
    "PIL",
    "IPython",
    "jupyter",
    "notebook",
    "pytest",
    "setuptools",
    "pip",
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
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,       # console visibile per log in produzione
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
