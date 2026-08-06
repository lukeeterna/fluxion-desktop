from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from unittest import mock


MODULE_PATH = (
    Path(__file__).resolve().parents[1] / "bin" / "vos_machine.py"
)
SPEC = importlib.util.spec_from_file_location(
    "vos_machine_under_test", MODULE_PATH
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load bin/vos_machine.py")

vos_machine = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(vos_machine)


class VerifyCurrentRepoRootHmacTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path("/private/fluxion-test-root")
        self.registry = {"validated": True}
        self.machine = {
            "machine_id": "macbook",
            "fingerprint_sha256": "f" * 64,
            "roles": ["repo_authority"],
            "repo_root_hmac_sha256": "a" * 64,
            "origin": vos_machine.REPOSITORY_ID,
        }

    def test_matching_hmac_passes_without_cleartext_repo_root(self) -> None:
        self.assertNotIn("repo_root", self.machine)

        with (
            mock.patch.object(
                vos_machine, "read_json", return_value=self.registry
            ),
            mock.patch.object(
                vos_machine,
                "validate_registry",
                return_value=self.registry,
            ),
            mock.patch.object(
                vos_machine, "repo_root", return_value=self.root
            ),
            mock.patch.object(vos_machine, "refresh_origin_master"),
            mock.patch.object(
                vos_machine,
                "find_current_machine",
                return_value=self.machine,
            ),
            mock.patch.object(
                vos_machine,
                "repo_root_hmac_sha256",
                return_value="a" * 64,
            ),
            mock.patch.object(
                vos_machine,
                "git",
                side_effect=[
                    "git@github.com:lukeeterna/fluxion-desktop.git",
                    "1" * 40,
                    "1" * 40,
                ],
            ),
        ):
            result = vos_machine.verify_current(
                Path("docs/judge/MACHINES.json"),
                "repo_authority",
            )

        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["machine_id"], "macbook")
        self.assertEqual(result["head"], "1" * 40)

    def test_mismatching_hmac_fails_closed_without_disclosing_path(self) -> None:
        self.assertNotIn("repo_root", self.machine)

        with (
            mock.patch.object(
                vos_machine, "read_json", return_value=self.registry
            ),
            mock.patch.object(
                vos_machine,
                "validate_registry",
                return_value=self.registry,
            ),
            mock.patch.object(
                vos_machine, "repo_root", return_value=self.root
            ),
            mock.patch.object(vos_machine, "refresh_origin_master"),
            mock.patch.object(
                vos_machine,
                "find_current_machine",
                return_value=self.machine,
            ),
            mock.patch.object(
                vos_machine,
                "repo_root_hmac_sha256",
                return_value="b" * 64,
            ),
        ):
            with self.assertRaises(vos_machine.MachineError) as caught:
                vos_machine.verify_current(
                    Path("docs/judge/MACHINES.json"),
                    "repo_authority",
                )

        message = str(caught.exception)
        self.assertIn("repo path digest mismatch", message)
        self.assertNotIn(str(self.root), message)
        self.assertNotIn("a" * 64, message)
        self.assertNotIn("b" * 64, message)


if __name__ == "__main__":
    unittest.main()

