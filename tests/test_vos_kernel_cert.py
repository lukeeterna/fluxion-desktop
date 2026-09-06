from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "bin"
if str(BIN) not in sys.path:
    sys.path.insert(0, str(BIN))
SPEC = importlib.util.spec_from_file_location("vos_apply_g3", BIN / "vos_apply.py")
assert SPEC and SPEC.loader
vos_apply = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(vos_apply)


class KernelCertificationTests(unittest.TestCase):
    def git(self, root: Path, *args: str) -> str:
        return subprocess.check_output(["git", *args], cwd=root, text=True).strip()

    def make_repo(
        self,
        td: str,
        *,
        task_source: str = "from pathlib import Path\np=Path('out/result.txt'); p.parent.mkdir(parents=True, exist_ok=True); p.write_text('ok\\n')\n",
        timeout_seconds: int = 10,
    ) -> tuple[Path, str]:
        root = Path(td)
        subprocess.run(["git", "init", "-q", "-b", "master", str(root)], check=True)
        self.git(root, "config", "user.email", "test@example.invalid")
        self.git(root, "config", "user.name", "Test")
        for rel in ["bin", "tests", "docs/judge/mandati"]:
            (root / rel).mkdir(parents=True, exist_ok=True)
        for name in ["vos_common.py", "vos_apply.py"]:
            (root / "bin" / name).write_bytes((ROOT / "bin" / name).read_bytes())
        (root / "bin/task.py").write_text(task_source, encoding="utf-8")
        md = root / "docs/judge/mandati/T-CERT.md"
        md.write_text("ETICHETTA: SAFE_AUTO\n", encoding="utf-8")
        manifest = {
            "schema_version": 1,
            "unit_id": "T-CERT",
            "label": "SAFE_AUTO",
            "lane": "REPO",
            "risk": "A",
            "base_commit": "*",
            "mandate_md": "docs/judge/mandati/T-CERT.md",
            "mandate_sha256": hashlib.sha256(md.read_bytes()).hexdigest(),
            "key": "T-CERT@fixture",
            "allowed_paths": ["out"],
            "steps": [
                {
                    "id": "F1",
                    "argv": ["python3", "bin/task.py"],
                    "cwd": ".",
                    "timeout_seconds": timeout_seconds,
                }
            ],
        }
        (root / "docs/judge/mandati/T-CERT.json").write_text(
            json.dumps(manifest, sort_keys=True), encoding="utf-8"
        )
        self.git(root, "add", ".")
        self.git(root, "commit", "-qm", "base")
        return root, self.git(root, "rev-parse", "HEAD")

    def failed_checkpoint(self, root: Path, nonce: str) -> dict[str, object]:
        path = vos_apply.git_dir(root) / "vos-control" / "checkpoints" / f"{nonce}.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def test_wrong_mandate_sha_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root, head = self.make_repo(td)
            manifest_path = root / "docs/judge/mandati/T-CERT.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["mandate_sha256"] = "0" * 64
            manifest_path.write_text(json.dumps(manifest, sort_keys=True), encoding="utf-8")
            with self.assertRaisesRegex(vos_apply.VOSFailure, "hash del mandato"):
                vos_apply.validate_manifest(root, "T-CERT", head[:7])

    def test_wrong_plan_head_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root, _ = self.make_repo(td)
            with self.assertRaisesRegex(vos_apply.VOSFailure, "non coincide con base del piano"):
                vos_apply.validate_manifest(root, "T-CERT", "deadbee")

    def test_stop_files_fail_closed_before_execution(self) -> None:
        for relative in (Path("vos/STOP"), Path("vos/control/STOP.json")):
            with self.subTest(stop=str(relative)), tempfile.TemporaryDirectory() as td:
                root, head = self.make_repo(td)
                stop = root / relative
                stop.parent.mkdir(parents=True, exist_ok=True)
                stop.write_text("STOP\n", encoding="utf-8")
                with self.assertRaisesRegex(vos_apply.VOSFailure, "freno"):
                    vos_apply.execute_unit(
                        root,
                        {"head": head[:7]},
                        "T-CERT",
                        publish=False,
                        lease_nonce="b" * 32,
                    )

    def test_timeout_is_terminal_and_checkpointed_failed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root, head = self.make_repo(
                td,
                task_source="import time\ntime.sleep(5)\n",
                timeout_seconds=1,
            )
            nonce = "c" * 32
            with self.assertRaisesRegex(vos_apply.VOSFailure, "timeout dopo 1s"):
                vos_apply.execute_unit(
                    root,
                    {"head": head[:7]},
                    "T-CERT",
                    publish=False,
                    lease_nonce=nonce,
                )
            checkpoint = self.failed_checkpoint(root, nonce)
            self.assertEqual(checkpoint["phase"], "FAILED")
            self.assertEqual(checkpoint["sequence"], 999)
            self.assertIn("timeout dopo 1s", str(checkpoint["error"]))

    def test_worker_failure_is_terminal_and_checkpointed_failed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root, head = self.make_repo(
                td,
                task_source="import sys\nprint('fixture failure')\nsys.exit(7)\n",
            )
            nonce = "d" * 32
            with self.assertRaisesRegex(vos_apply.VOSFailure, "codice 7"):
                vos_apply.execute_unit(
                    root,
                    {"head": head[:7]},
                    "T-CERT",
                    publish=False,
                    lease_nonce=nonce,
                )
            checkpoint = self.failed_checkpoint(root, nonce)
            self.assertEqual(checkpoint["phase"], "FAILED")
            self.assertIn("codice 7", str(checkpoint["error"]))

    def test_result_and_log_hashes_are_content_addressed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root, head = self.make_repo(td)
            nonce = "e" * 32
            result = vos_apply.execute_unit(
                root,
                {"head": head[:7]},
                "T-CERT",
                publish=False,
                lease_nonce=nonce,
            )
            self.assertEqual(result["status"], "PASS")
            log_dir = vos_apply.git_dir(root) / "vos-control" / "runs" / nonce
            self.assertTrue(result["log_sha256"])
            for name, expected in result["log_sha256"].items():
                self.assertRegex(expected, r"^[0-9a-f]{64}$")
                self.assertEqual(vos_apply.sha256_file(log_dir / name), expected)

            local_result = json.loads((log_dir / "result.json").read_text(encoding="utf-8"))
            self.assertEqual(local_result["log_sha256"], result["log_sha256"])
            self.assertEqual(local_result["result_commit"], result["result_commit"])

            envelope_text = self.git(
                root,
                "show",
                f"{result['result_commit']}:vos/control/results/{nonce}.json",
            )
            envelope = json.loads(envelope_text)
            self.assertEqual(envelope["mandate_sha256"], result["mandate_sha256"])
            self.assertEqual(envelope["log_sha256"], result["log_sha256"])
            self.assertEqual(envelope["changed_paths"], ["out/result.txt"])


if __name__ == "__main__":
    unittest.main()
