from pathlib import Path

SOURCE = Path("voice-agent/src/groq_client.py")
TEST = Path("voice-agent/tests/test_groq_stt_response_contract.py")

text = SOURCE.read_text(encoding="utf-8")

fallback_start = text.index("        # Fallback to direct Groq API call\n")
fallback_end = text.index("    async def generate_response(\n", fallback_start)
fallback = text[fallback_start:fallback_end]
old = "            return response.strip()\n"
new = "            return self._normalize_transcription_response(response)\n"
if fallback.count(old) != 1:
    raise SystemExit("direct Groq fallback return contract mismatch")
fallback = fallback.replace(old, new, 1)
text = text[:fallback_start] + fallback + text[fallback_end:]

anchor = "    async def transcribe_audio(\n"
if text.count(anchor) != 1:
    raise SystemExit("transcribe_audio anchor mismatch")
helper = '''    @staticmethod
    def _normalize_transcription_response(response: Any) -> str:
        """Normalize Groq STT text responses without leaking object reprs downstream."""
        if isinstance(response, str):
            return response.strip()

        text = response.get("text") if isinstance(response, dict) else getattr(response, "text", None)
        if not isinstance(text, str):
            raise TypeError(
                f"Unsupported Groq transcription response type: {type(response).__name__}"
            )
        return text.strip()

'''
text = text.replace(anchor, helper + anchor, 1)
SOURCE.write_text(text, encoding="utf-8")

TEST.write_text('''import asyncio
import importlib
import sys
import types
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SRC))

fake_groq = types.ModuleType("groq")
fake_groq.Groq = object
fake_groq.AsyncGroq = object
sys.modules["groq"] = fake_groq

fake_stt = types.ModuleType("stt")
fake_stt.get_stt_engine = lambda prefer_offline=True: None
fake_stt.STTEngine = object
sys.modules["stt"] = fake_stt

groq_client = importlib.import_module("groq_client")
GroqClient = groq_client.GroqClient

class _Transcriptions:
    def __init__(self, response):
        self.response = response

    def create(self, **_kwargs):
        return self.response

class _ResponseObject:
    def __init__(self, text):
        self.text = text

def _client(response):
    client = GroqClient.__new__(GroqClient)
    client._stt_engine = None
    client.client = types.SimpleNamespace(
        audio=types.SimpleNamespace(transcriptions=_Transcriptions(response))
    )
    return client

class GroqSTTResponseContractTests(unittest.TestCase):
    def test_plain_string(self):
        self.assertEqual(asyncio.run(_client("  ciao  ").transcribe_audio(b"wav")), "ciao")

    def test_object_text(self):
        self.assertEqual(asyncio.run(_client(_ResponseObject("  buongiorno  ")).transcribe_audio(b"wav")), "buongiorno")

    def test_mapping_text(self):
        self.assertEqual(asyncio.run(_client({"text": "  salve  "}).transcribe_audio(b"wav")), "salve")

    def test_unknown_schema_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError, "Unsupported Groq transcription response type"):
            asyncio.run(_client(object()).transcribe_audio(b"wav"))

if __name__ == "__main__":
    unittest.main()
''', encoding="utf-8")
