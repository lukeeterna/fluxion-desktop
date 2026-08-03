from __future__ import annotations

import base64
import hashlib
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('vos_seed_mandates', ROOT / 'bin' / 'vos_seed_mandates.py')
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

class SeedTests(unittest.TestCase):
    def test_atomic_import_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            subprocess.run(['git','init','-q',str(root)], check=True)
            data = b'ETICHETTA: SAFE_AUTO\n'
            bundle = {
                'schema_version': 1,
                'files': [{
                    'path': 'docs/judge/mandati/T-X.md',
                    'sha256': hashlib.sha256(data).hexdigest(),
                    'base64': base64.b64encode(data).decode(),
                }],
            }
            path = root / 'bundle.json'
            path.write_text(json.dumps(bundle), encoding='utf-8')
            result = mod.apply_bundle(root, path)
            self.assertEqual(result['created'], 1)
            self.assertEqual((root / 'docs/judge/mandati/T-X.md').read_bytes(), data)
            result2 = mod.apply_bundle(root, path)
            self.assertEqual(result2['identical'], 1)
            (root / 'docs/judge/mandati/T-X.md').write_text('different', encoding='utf-8')
            with self.assertRaises(mod.VOSFailure):
                mod.apply_bundle(root, path)

    def test_bad_hash_changes_nothing(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            subprocess.run(['git','init','-q',str(root)], check=True)
            bundle = {'schema_version':1,'files':[{'path':'docs/judge/mandati/T-Y.md','sha256':'0'*64,'base64':base64.b64encode(b'x').decode()}]}
            path = root / 'bundle.json'
            path.write_text(json.dumps(bundle), encoding='utf-8')
            with self.assertRaises(mod.VOSFailure):
                mod.apply_bundle(root, path)
            self.assertFalse((root/'docs/judge/mandati/T-Y.md').exists())

if __name__ == '__main__':
    unittest.main()
