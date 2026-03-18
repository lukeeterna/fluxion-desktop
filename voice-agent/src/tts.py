"""
FLUXION Voice Agent - Text-to-Speech
Multi-engine TTS: Chatterbox Italian (primary) + Piper (fallback)

Voice Assistant: Sara
All TTS engines output as "Sara" - the FLUXION voice assistant

TTS Engines (priority order):
1. Chatterbox Italian - Best quality (9/10), 100-150ms CPU, 200MB
2. Piper (fallback) - Fast (50ms), lightweight (60MB)
3. System TTS - macOS say command (last resort)
"""

import os
import re
import tempfile
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union
from enum import Enum

# FluxionTTS Adaptive engine layer (plans 01+02)
try:
    from .tts_engine import create_tts_engine, TTSMode, TTSEngineSelector
    from .tts_download_manager import TTSDownloadManager
    _ADAPTIVE_ENGINE_AVAILABLE = True
except ImportError:
    try:
        from tts_engine import create_tts_engine, TTSMode, TTSEngineSelector
        from tts_download_manager import TTSDownloadManager
        _ADAPTIVE_ENGINE_AVAILABLE = True
    except ImportError:
        _ADAPTIVE_ENGINE_AVAILABLE = False

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# TTS TEXT PREPROCESSING
# ═══════════════════════════════════════════════════════════════════

# Matches Italian mobile (3xxxxxxxxx) and landline (0x...) phone numbers,
# optionally prefixed with +39 or 0039. Must be isolated by word boundaries.
_PHONE_RE = re.compile(
    r'\b((?:\+39|0039)?(?:[3][0-9]{8,9}|0[0-9]{8,9}))\b'
)

# ─── Date expansion for TTS ────────────────────────────────────────────────────
_MONTHS_IT = {
    1: "gennaio", 2: "febbraio", 3: "marzo", 4: "aprile",
    5: "maggio", 6: "giugno", 7: "luglio", 8: "agosto",
    9: "settembre", 10: "ottobre", 11: "novembre", 12: "dicembre",
}
_ORDINALS_IT = {
    1: "primo", 2: "due", 3: "tre", 4: "quattro", 5: "cinque",
    6: "sei", 7: "sette", 8: "otto", 9: "nove", 10: "dieci",
    11: "undici", 12: "dodici", 13: "tredici", 14: "quattordici",
    15: "quindici", 16: "sedici", 17: "diciassette", 18: "diciotto",
    19: "diciannove", 20: "venti", 21: "ventuno", 22: "ventidue",
    23: "ventitre", 24: "ventiquattro", 25: "venticinque",
    26: "ventisei", 27: "ventisette", 28: "ventotto", 29: "ventinove",
    30: "trenta", 31: "trentuno",
}
_YEARS_IT = {
    2024: "duemilaventiquattro", 2025: "duemilaventicinque",
    2026: "duemilaventisei", 2027: "duemilaventisette",
}
# Matches DD/MM/YYYY (full) or DD/MM (short) — only valid day/month ranges
_DATE_FULL_RE = re.compile(r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b')
_DATE_SHORT_RE = re.compile(r'\b(\d{1,2})/(\d{1,2})\b')

# ─── Italian number-to-words for TTS ────────────────────────────────────────
_UNITS_IT = [
    "", "uno", "due", "tre", "quattro", "cinque",
    "sei", "sette", "otto", "nove", "dieci",
    "undici", "dodici", "tredici", "quattordici", "quindici",
    "sedici", "diciassette", "diciotto", "diciannove",
]
_TENS_IT = [
    "", "", "venti", "trenta", "quaranta", "cinquanta",
    "sessanta", "settanta", "ottanta", "novanta",
]


def _number_to_italian(n: int) -> str:
    """Convert integer 0..999_999_999 to Italian words for TTS."""
    if n == 0:
        return "zero"
    if n < 0:
        return "meno " + _number_to_italian(-n)

    parts = []

    # Milioni
    if n >= 1_000_000:
        milioni = n // 1_000_000
        n %= 1_000_000
        if milioni == 1:
            parts.append("un milione")
        else:
            parts.append(_number_to_italian(milioni) + " milioni")

    # Migliaia
    if n >= 1000:
        migliaia = n // 1000
        n %= 1000
        if migliaia == 1:
            parts.append("mille")
        else:
            parts.append(_under_thousand(migliaia) + "mila")

    # Centinaia + decine + unità
    if n > 0:
        parts.append(_under_thousand(n))

    return " ".join(parts).replace("  ", " ").strip()


def _under_thousand(n: int) -> str:
    """Convert 1..999 to Italian words."""
    result = ""
    if n >= 100:
        centinaia = n // 100
        n %= 100
        if centinaia == 1:
            result = "cento"
        else:
            result = _UNITS_IT[centinaia] + "cento"

    if n >= 20:
        decine = n // 10
        unita = n % 10
        ten_word = _TENS_IT[decine]
        # Italian elision: venti+uno→ventuno, trenta+otto→trentotto
        if unita in (1, 8):
            ten_word = ten_word[:-1]
        result += ten_word + _UNITS_IT[unita]
    elif n > 0:
        result += _UNITS_IT[n]

    return result


# Matches Italian thousands-separator numbers: 1.000, 3.500, 1.500.000
# Must have dot every 3 digits. Negative lookbehind for / avoids matching dates.
_ITALIAN_NUMBER_RE = re.compile(
    r'(?<!/)\b(\d{1,3}(?:\.\d{3})+)\b'
)
# Simple integers (4+ digits, no dots) — e.g. "3000" without separator
_PLAIN_NUMBER_RE = re.compile(r'\b(\d{4,9})\b')


def _expand_italian_number(m: re.Match) -> str:
    """Convert dot-separated Italian number to words: '3.000' → 'tremila'."""
    raw = m.group(1).replace(".", "")
    try:
        n = int(raw)
        if n > 999_999_999:
            return m.group(0)  # too large, leave as-is
        return _number_to_italian(n)
    except ValueError:
        return m.group(0)


def _expand_plain_number(m: re.Match) -> str:
    """Convert plain large integer to Italian words: '3000' → 'tremila'."""
    try:
        n = int(m.group(1))
        if n > 999_999_999:
            return m.group(0)
        return _number_to_italian(n)
    except ValueError:
        return m.group(0)


def _expand_date_for_tts(m: re.Match) -> str:
    """Convert numeric date match to Italian spoken form."""
    groups = m.groups()
    day = int(groups[0])
    month = int(groups[1])
    if not (1 <= day <= 31 and 1 <= month <= 12):
        return m.group(0)  # not a valid date — leave untouched
    day_str = _ORDINALS_IT.get(day, str(day))
    month_str = _MONTHS_IT.get(month, str(month))
    if len(groups) == 3:
        year = int(groups[2])
        year_str = _YEARS_IT.get(year, str(year))
        return f"{day_str} {month_str} {year_str}"
    return f"{day_str} {month_str}"


def preprocess_for_tts(text: str) -> str:
    """
    Pre-process text before TTS synthesis.

    1. Expands numeric dates so Piper/SystemTTS reads them correctly:
       "13/03"        → "tredici marzo"
       "13/03/2026"   → "tredici marzo duemilaventisei"

    2. Expands Italian numbers with dot separators:
       "3.000"        → "tremila"
       "1.500.000"    → "un milione cinquecentomila"

    3. Expands large plain integers:
       "3000"         → "tremila"

    4. Expands Italian phone numbers digit-by-digit:
       "3807769822"   → "3 8 0 7 7 6 9 8 2 2"

    Examples:
        "Appuntamento il 13/03 alle 10:00" →
        "Appuntamento il tredici marzo alle 10:00"

        "Il servizio costa 3.000 euro" →
        "Il servizio costa tremila euro"
    """
    # Dates first (full before short to avoid partial match on year digits)
    text = _DATE_FULL_RE.sub(_expand_date_for_tts, text)
    text = _DATE_SHORT_RE.sub(_expand_date_for_tts, text)

    # Italian dot-separated numbers (before phone, since phone regex is broader)
    text = _ITALIAN_NUMBER_RE.sub(_expand_italian_number, text)

    # Plain large integers (4+ digits without dots)
    # Must run AFTER phone expansion to avoid conflicts
    def _expand_phone(m: re.Match) -> str:
        digits = re.sub(r'\D', '', m.group(0))
        return ' '.join(digits)

    text = _PHONE_RE.sub(_expand_phone, text)

    # Plain large numbers that aren't phone numbers (run after phone to avoid double-expand)
    text = _PLAIN_NUMBER_RE.sub(_expand_plain_number, text)

    return text


# ═══════════════════════════════════════════════════════════════════
# VOICE ASSISTANT: Sara
# ═══════════════════════════════════════════════════════════════════

VOICE_NAME = "Sara"  # Public-facing name for the voice assistant


class TTSEngine(Enum):
    """Available TTS engines."""
    CHATTERBOX = "chatterbox"  # Legacy — maps to QUALITY adaptive engine
    PIPER = "piper"            # Fallback: Fast, lightweight
    SYSTEM = "system"          # Last resort: macOS say
    QUALITY = "quality"        # New: Qwen3-TTS adaptive (high quality)
    FAST = "fast"              # New: Piper adaptive (low latency)


# Default TTS engine
DEFAULT_ENGINE = TTSEngine.CHATTERBOX

# Internal configs (not exposed to users)
_PIPER_MODEL = "it_IT-paola-medium"

_CHATTERBOX_CONFIG = {
    "model_id": "ayahyaa3/chatterbox-italian-tts",
    "quality": 9.0,
    "latency_ms": "100-150",
    "size_mb": 200,
    "exaggeration": 0.4,
    "cfg": 0.4,
}


# ═══════════════════════════════════════════════════════════════════
# CHATTERBOX TTS (Primary Engine)
# ═══════════════════════════════════════════════════════════════════

class ChatterboxTTS:
    """
    Chatterbox Italian TTS - Best quality for Italian voice agent.
    Quality: 9/10 | Latency: 100-150ms CPU | Size: 200MB
    """

    _model = None

    def __init__(
        self,
        device: str = "cpu",
        exaggeration: float = 0.4,
        cfg: float = 0.4,
        lazy_load: bool = True
    ):
        """
        Initialize Chatterbox TTS.

        Args:
            device: "cpu" or "cuda"
            exaggeration: Voice expressiveness (0.3-0.5 for natural)
            cfg: Guidance scale (0.3-0.5 for stable rhythm)
            lazy_load: Load model on first use (saves startup time)
        """
        self.device = device
        self.exaggeration = exaggeration
        self.cfg = cfg
        self._loaded = False

        if not lazy_load:
            self._load_model()

    def _load_model(self):
        """Load Chatterbox model."""
        if ChatterboxTTS._model is not None:
            self._loaded = True
            return

        try:
            from chatterbox.tts import ChatterboxTTS as CBModel

            logger.info(f"Loading {VOICE_NAME} TTS (device={self.device})...")
            ChatterboxTTS._model = CBModel.from_pretrained(
                _CHATTERBOX_CONFIG["model_id"],
                device=self.device
            )
            self._loaded = True
            logger.info(f"✅ {VOICE_NAME} TTS loaded successfully")

        except ImportError:
            raise RuntimeError(
                f"{VOICE_NAME} TTS not available. Install with:\n"
                "pip install chatterbox-tts torch torchaudio scipy"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load {VOICE_NAME} TTS: {e}")

    async def synthesize(self, text: str) -> bytes:
        """
        Convert text to speech.

        Args:
            text: Italian text to synthesize

        Returns:
            WAV audio bytes (24kHz)
        """
        self._load_model()

        # Ensure Italian mode with [it] prefix
        if not text.strip().startswith("[it]"):
            text = "[it] " + text

        # Generate audio
        wav = ChatterboxTTS._model.generate(
            text,
            exaggeration=self.exaggeration,
            cfg=self.cfg
        )

        # Save to temp file and read bytes
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            output_path = f.name

        try:
            import torchaudio as ta
            ta.save(output_path, wav, ChatterboxTTS._model.sr)

            with open(output_path, "rb") as f:
                audio_data = f.read()

            return audio_data

        finally:
            if os.path.exists(output_path):
                os.remove(output_path)

    async def synthesize_to_file(self, text: str, output_path: str) -> str:
        """Convert text to speech and save to file."""
        self._load_model()

        if not text.strip().startswith("[it]"):
            text = "[it] " + text

        wav = ChatterboxTTS._model.generate(
            text,
            exaggeration=self.exaggeration,
            cfg=self.cfg
        )

        import torchaudio as ta
        ta.save(output_path, wav, ChatterboxTTS._model.sr)

        return output_path

    def get_info(self) -> dict:
        """Get TTS configuration info."""
        return {
            "engine": "chatterbox",
            "voice_name": VOICE_NAME,
            "quality": _CHATTERBOX_CONFIG["quality"],
            "latency": _CHATTERBOX_CONFIG["latency_ms"],
            "device": self.device,
            "loaded": self._loaded,
        }


# ═══════════════════════════════════════════════════════════════════
# PIPER TTS (Fallback Engine)
# ═══════════════════════════════════════════════════════════════════

class PiperTTS:
    """Piper TTS wrapper - Fast fallback engine."""

    def __init__(
        self,
        model_path: Optional[str] = None,
        piper_binary: Optional[str] = None,
    ):
        """Initialize Piper TTS."""
        # FLUXION models directory
        self.models_dir = Path(__file__).parent.parent / "models" / "tts"
        self.models_dir.mkdir(parents=True, exist_ok=True)

        # Find piper binary
        if piper_binary:
            self.piper_binary = Path(piper_binary)
        else:
            import sys
            venv_bin = Path(sys.executable).parent / "piper"
            venv_bin_exe = Path(sys.executable).parent / "piper.exe"

            if sys.platform == "win32":
                possible_paths = [
                    venv_bin_exe,
                    Path(sys.executable).parent.parent / "Scripts" / "piper.exe",
                    Path.home() / "AppData" / "Local" / "Programs" / "piper" / "piper.exe",
                    Path("C:/Program Files/piper/piper.exe"),
                ]
            else:
                possible_paths = [
                    venv_bin,
                    Path.home() / ".local" / "bin" / "piper",
                    Path("/usr/local/bin/piper"),
                    Path("/usr/bin/piper"),
                ]
            self.piper_binary = None
            for path in possible_paths:
                if path.exists():
                    self.piper_binary = path
                    break

        # Find model
        if model_path:
            self.model_path = Path(model_path)
        else:
            self.model_path = self.models_dir / f"{_PIPER_MODEL}.onnx"
            if not self.model_path.exists():
                system_dir = Path.home() / ".local" / "share" / "piper" / "voices"
                self.model_path = system_dir / f"{_PIPER_MODEL}.onnx"

        self._validate()

    def _validate(self):
        """Validate piper and model exist."""
        if self.piper_binary is None or not self.piper_binary.exists():
            raise RuntimeError("Piper binary not found. Install with: pip install piper-tts")

        if not self.model_path.exists():
            raise RuntimeError(f"Voice model not found: {self.model_path}")

    async def synthesize(self, text: str) -> bytes:
        """Convert text to speech."""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            output_path = f.name

        try:
            process = await asyncio.create_subprocess_exec(
                str(self.piper_binary),
                "--model", str(self.model_path),
                "--output_file", output_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate(text.encode())

            if process.returncode != 0:
                raise RuntimeError(f"Piper failed: {stderr.decode()}")

            with open(output_path, "rb") as f:
                audio_data = f.read()

            return audio_data

        finally:
            if os.path.exists(output_path):
                os.remove(output_path)

    async def synthesize_to_file(self, text: str, output_path: str) -> str:
        """Convert text to speech and save to file."""
        process = await asyncio.create_subprocess_exec(
            str(self.piper_binary),
            "--model", str(self.model_path),
            "--output_file", output_path,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate(text.encode())

        if process.returncode != 0:
            raise RuntimeError(f"Piper failed: {stderr.decode()}")

        return output_path

    def get_info(self) -> dict:
        """Get TTS configuration info."""
        return {
            "engine": "piper",
            "voice_name": VOICE_NAME,
            "quality": 7.5,
            "model_path": str(self.model_path),
            "piper_binary": str(self.piper_binary),
        }


# ═══════════════════════════════════════════════════════════════════
# SYSTEM TTS (Last Resort Fallback)
# ═══════════════════════════════════════════════════════════════════

class SystemTTS:
    """Fallback TTS using OS-native speech synthesis (cross-platform)."""

    def __init__(self, voice: str = "Alice"):
        self.voice = voice  # macOS voice name (ignored on Windows)

    async def synthesize(self, text: str) -> bytes:
        """Synthesize using OS-native TTS (macOS: say/afconvert, Windows: pyttsx3)."""
        import sys
        if sys.platform == "win32":
            return await self._synthesize_windows(text)
        else:
            return await self._synthesize_macos(text)

    async def _synthesize_macos(self, text: str) -> bytes:
        """macOS synthesis via say + afconvert."""
        with tempfile.NamedTemporaryFile(suffix=".aiff", delete=False) as f:
            output_path = f.name

        try:
            process = await asyncio.create_subprocess_exec(
                "say",
                "-v", self.voice,
                "-o", output_path,
                text,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()

            wav_path = output_path.replace(".aiff", ".wav")
            convert = await asyncio.create_subprocess_exec(
                "afconvert",
                "-f", "WAVE",
                "-d", "LEI16@16000",
                output_path, wav_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await convert.communicate()

            with open(wav_path, "rb") as f:
                audio_data = f.read()

            os.remove(wav_path)
            return audio_data

        finally:
            if os.path.exists(output_path):
                os.remove(output_path)

    async def _synthesize_windows(self, text: str) -> bytes:
        """Windows synthesis via pyttsx3 + Windows SAPI5."""
        try:
            import pyttsx3
        except ImportError:
            raise RuntimeError(
                "pyttsx3 non installato. Su Windows esegui: pip install pyttsx3"
            )

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            output_path = f.name

        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._pyttsx3_save, text, output_path)

            with open(output_path, "rb") as f:
                return f.read()
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)

    def _pyttsx3_save(self, text: str, output_path: str) -> None:
        """Synchronous pyttsx3 synthesis (run in executor)."""
        import pyttsx3
        engine = pyttsx3.init()
        # Try to set an Italian voice if available
        for voice in engine.getProperty("voices"):
            if "italian" in voice.name.lower() or "it" in voice.id.lower():
                engine.setProperty("voice", voice.id)
                break
        engine.save_to_file(text, output_path)
        engine.runAndWait()
        engine.stop()

    def get_info(self) -> dict:
        """Get TTS configuration info."""
        import sys
        return {
            "engine": "system",
            "platform": sys.platform,
            "voice_name": VOICE_NAME,
            "quality": 5.0,
        }


# ═══════════════════════════════════════════════════════════════════
# TTS FACTORY
# ═══════════════════════════════════════════════════════════════════

def get_tts(
    engine: TTSEngine = DEFAULT_ENGINE,
    use_piper: bool = True,  # Legacy parameter — kept for backward compat
    **kwargs
):
    """
    Get TTS instance. Now delegates to FluxionTTS Adaptive engine selector.
    Legacy use_piper param preserved for orchestrator compatibility.

    Args:
        engine: TTS engine hint (default: Chatterbox → adaptive auto)
        use_piper: Legacy param - if False forces SystemTTS
        **kwargs: Passed through to fallback constructors if adaptive unavailable

    Returns:
        TTS instance (Sara voice) — adaptive, Piper, or System
    """
    # Handle legacy use_piper=False → force SystemTTS (no-audio mode)
    if not use_piper:
        logger.warning("Legacy SYSTEM TTS requested — using SystemTTS fallback")
        return SystemTTS()

    # Delegate to FluxionTTS Adaptive engine selector if available
    if _ADAPTIVE_ENGINE_AVAILABLE:
        try:
            # Read persisted mode preference (.tts_mode file)
            try:
                persisted_mode_str = TTSDownloadManager.read_mode()
                persisted_mode = TTSMode(persisted_mode_str)
            except Exception:
                persisted_mode = TTSMode.AUTO

            adaptive_engine = create_tts_engine(
                user_pref=persisted_mode,
            )
            return adaptive_engine
        except Exception as e:
            logger.warning(f"AdaptiveTTS selector failed ({e}), falling back to PiperTTS")

    # Fallback: try Piper directly
    try:
        return PiperTTS(**kwargs)
    except RuntimeError as e:
        logger.warning(f"Piper not available: {e}")

    # Last resort: System TTS
    logger.warning("Using SystemTTS as last resort")
    return SystemTTS()


def get_sara_tts(**kwargs) -> Union[ChatterboxTTS, PiperTTS, SystemTTS]:
    """Get Sara TTS (FLUXION voice assistant)."""
    return get_tts(**kwargs)


# ═══════════════════════════════════════════════════════════════════
# TTS CACHE WRAPPER
# ═══════════════════════════════════════════════════════════════════

class TTSCache:
    """
    Cache wrapper for any TTS engine.

    Eliminates TTS latency for repeated phrases (L1/L2 templates).
    Static responses (greetings, questions, confirmations) are pre-warmed
    at startup so the first request is also instant.

    Usage:
        tts = TTSCache(get_tts())
        await tts.warm_cache(["Mi dice il suo nome?", ...])
        audio = await tts.synthesize("Mi dice il suo nome?")  # 0ms (cached)
    """

    def __init__(self, engine: Union[ChatterboxTTS, PiperTTS, SystemTTS]):
        self._engine = engine
        self._cache: Dict[str, bytes] = {}
        self._hits = 0
        self._misses = 0

    async def synthesize(self, text: str) -> bytes:
        """Return cached audio or synthesize and cache for future calls."""
        key = text.strip()
        if key in self._cache:
            self._hits += 1
            return self._cache[key]

        self._misses += 1
        # Pre-process text: expand phone numbers digit-by-digit so TTS engines
        # read "3807769822" as "3 8 0 7 7 6 9 8 2 2" instead of "3 miliardi..."
        processed = preprocess_for_tts(key)
        audio = await self._engine.synthesize(processed)
        self._cache[key] = audio
        return audio

    async def warm_cache(self, texts: List[str]) -> None:
        """Pre-synthesize a list of strings concurrently at startup."""
        uncached = [t.strip() for t in texts if t.strip() and t.strip() not in self._cache]
        if not uncached:
            return

        tasks = [self._engine.synthesize(t) for t in uncached]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        warmed = 0
        for text, result in zip(uncached, results):
            if isinstance(result, bytes):
                self._cache[text] = result
                warmed += 1
            else:
                logger.warning(f"[TTSCache] warm failed for '{text[:30]}': {result}")

        logger.info(f"[TTSCache] Pre-warmed {warmed}/{len(uncached)} phrases")

    def get_info(self) -> dict:
        info = self._engine.get_info()
        info["cache_hits"] = self._hits
        info["cache_misses"] = self._misses
        info["cache_size"] = len(self._cache)
        return info


# ═══════════════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════════════

async def test_tts():
    """Test TTS."""
    print("=" * 60)
    print(f"FLUXION TTS Test - {VOICE_NAME} Voice")
    print("=" * 60)

    test_phrase = f"Buongiorno! Sono {VOICE_NAME}, come posso aiutarla?"

    # Test Chatterbox
    try:
        print(f"\n1. Testing Chatterbox (primary)...")
        tts = ChatterboxTTS()
        audio = await tts.synthesize(test_phrase)
        print(f"   ✅ Generated {len(audio)} bytes")
        print(f"   Info: {tts.get_info()}")
        return True
    except Exception as e:
        print(f"   ❌ Chatterbox not available: {e}")

    # Test Piper fallback
    try:
        print(f"\n2. Testing Piper (fallback)...")
        tts = PiperTTS()
        audio = await tts.synthesize(test_phrase)
        print(f"   ✅ Generated {len(audio)} bytes")
        print(f"   Info: {tts.get_info()}")
        return True
    except Exception as e:
        print(f"   ❌ Piper not available: {e}")

    # System fallback
    print(f"\n3. Testing System TTS (last resort)...")
    tts = SystemTTS()
    audio = await tts.synthesize(test_phrase)
    print(f"   ✅ Generated {len(audio)} bytes")
    return True


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(test_tts())
