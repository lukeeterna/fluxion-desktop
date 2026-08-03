from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('vos_apply', ROOT / 'bin' / 'vos_apply.py')
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

class ApplyTests(unittest.TestCase):
    def git(self, root: Path, *args: str) -> str:
        return subprocess.check_output(['git', *args], cwd=root, text=True).strip()

    def make_repo(self, td: str, *, bad_path: bool = False, label: str = 'SAFE_AUTO'):
        root = Path(td)
        subprocess.run(['git', 'init', '-q', '-b', 'master', str(root)], check=True)
        self.git(root, 'config', 'user.email', 'test@example.invalid')
        self.git(root, 'config', 'user.name', 'Test')
        for rel in ['bin', 'tests', 'docs/judge/mandati']:
            (root / rel).mkdir(parents=True, exist_ok=True)
        for name in ['vos_common.py', 'vos_apply.py']:
            (root / 'bin' / name).write_bytes((ROOT / 'bin' / name).read_bytes())
        target = 'forbidden.txt' if bad_path else 'out/result.txt'
        (root / 'bin/task.py').write_text(
            "from pathlib import Path\n"
            f"p=Path({target!r}); p.parent.mkdir(parents=True,exist_ok=True); p.write_text('ok\\n')\n",
            encoding='utf-8',
        )
        md = root / 'docs/judge/mandati/T-TEST.md'
        md.write_text('ETICHETTA: SAFE_AUTO\n', encoding='utf-8')
        manifest = {
            'schema_version': 1,
            'unit_id': 'T-TEST',
            'label': label,
            'lane': 'REPO',
            'risk': 'A',
            'base_commit': '*',
            'mandate_md': 'docs/judge/mandati/T-TEST.md',
            'mandate_sha256': hashlib.sha256(md.read_bytes()).hexdigest(),
            'key': 'T-TEST@fixture',
            'allowed_paths': ['out'],
            'steps': [{'id': 'F1', 'argv': ['python3', 'bin/task.py'], 'cwd': '.', 'timeout_seconds': 10}],
        }
        (root / 'docs/judge/mandati/T-TEST.json').write_text(json.dumps(manifest, sort_keys=True), encoding='utf-8')
        self.git(root, 'add', '.')
        self.git(root, 'commit', '-qm', 'base')
        return root, self.git(root, 'rev-parse', 'HEAD')

    def test_positive_creates_real_result_commit(self):
        with tempfile.TemporaryDirectory() as td:
            root, head = self.make_repo(td)
            lease = 'a' * 32
            result = mod.execute_unit(root, {'head': head[:7]}, 'T-TEST', publish=False, lease_nonce=lease)
            self.assertEqual(result['status'], 'PASS')
            self.assertEqual(result['lease_nonce'], lease)
            self.assertFalse(result['published'])
            self.assertRegex(result['result_commit'], r'^[0-9a-f]{40}$')
            self.assertIn('out/result.txt', result['changed_paths'])
            self.assertEqual(self.git(root, 'show', f"{result['result_commit']}:out/result.txt"), 'ok')
            envelope = self.git(root, 'show', f"{result['result_commit']}:vos/control/results/{result['lease_nonce']}.json")
            self.assertEqual(json.loads(envelope)['mandate_sha256'], result['mandate_sha256'])

    def test_manifest_rejects_confirm_first(self):
        with tempfile.TemporaryDirectory() as td:
            root, head = self.make_repo(td, label='CONFIRM_FIRST')
            with self.assertRaises(mod.VOSFailure):
                mod.validate_manifest(root, 'T-TEST', head[:7])

    def test_step_rejects_shell_string(self):
        with self.assertRaises(mod.VOSFailure):
            mod.validate_step({'id': 'F1', 'argv': ['bash', '-c', 'rm -rf /'], 'cwd': '.', 'timeout_seconds': 1})

    def test_path_guard_blocks_result(self):
        with tempfile.TemporaryDirectory() as td:
            root, head = self.make_repo(td, bad_path=True)
            with self.assertRaises(mod.VOSFailure):
                mod.execute_unit(root, {'head': head[:7]}, 'T-TEST', publish=False)

if __name__ == '__main__':
    unittest.main()
