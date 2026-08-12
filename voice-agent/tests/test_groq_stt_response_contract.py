import asyncio
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
