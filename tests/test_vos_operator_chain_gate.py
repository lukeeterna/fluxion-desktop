from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("vos_operator_chain_gate", HERE / "bin/vos_operator_chain_gate.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load bin/vos_operator_chain_gate.py")
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


class OperatorChainGateTests(unittest.TestCase):
    def copy_fixture(self):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        shutil.copytree(HERE / "docs", root / "docs")
        shutil.copy2(HERE / "CLAUDE.md", root / "CLAUDE.md")
        (root / "bin").mkdir()
        (root / "tools").mkdir()
        (root / "vos").mkdir()
        (root / ".github/workflows").mkdir(parents=True)
        return temporary, root

    def test_pass(self):
        temporary, root = self.copy_fixture(); self.addCleanup(temporary.cleanup)
        self.assertEqual(gate.validate(root)["static_status"], "PASS")

    def test_reject_markdown_tamper(self):
        temporary, root = self.copy_fixture(); self.addCleanup(temporary.cleanup)
        (root / "docs/judge/OPERATOR-CHAIN.md").write_text("tamper")
        with self.assertRaises(gate.GateError): gate.validate(root)

    def test_blocks_action_reviewer_substitution(self):
        temporary, root = self.copy_fixture(); self.addCleanup(temporary.cleanup)
        (root / ".github/workflows/fluxion-sonnet-review.yml").write_text("name: forbidden\n")
        self.assertEqual(gate.validate(root)["static_status"], "BLOCKED")

    def test_blocks_local_reviewer_substitution(self):
        temporary, root = self.copy_fixture(); self.addCleanup(temporary.cleanup)
        (root / "tools/fluxion_sonnet_reviewer.py").write_text("forbidden")
        self.assertEqual(gate.validate(root)["static_status"], "BLOCKED")

    def test_blocks_legacy_autorun(self):
        temporary, root = self.copy_fixture(); self.addCleanup(temporary.cleanup)
        (root / "vos/autorun.sh").write_text("claude --allowedTools Read Edit Write Bash\ngit push origin master\n")
        self.assertEqual(gate.validate(root)["static_status"], "BLOCKED")

    def test_reject_legacy_root_role(self):
        temporary, root = self.copy_fixture(); self.addCleanup(temporary.cleanup)
        (root / "CLAUDE.md").write_text("Tu sei l'Architetto Capo. Implementa e fai git push origin master.\n")
        with self.assertRaises(gate.GateError): gate.validate(root)

    def test_reject_local_executor_contract_tamper(self):
        temporary, root = self.copy_fixture(); self.addCleanup(temporary.cleanup)
        (root / "docs/judge/CC-LOCAL-EXECUTOR-PROMPT.md").write_text("ROLE=CC_LOCAL\nauthor code\n")
        with self.assertRaises(gate.GateError): gate.validate(root)

    def test_reject_operator_capability_reassignment(self):
        temporary, root = self.copy_fixture(); self.addCleanup(temporary.cleanup)
        path = root / "docs/judge/OPERATOR-CHAIN.json"; data = json.loads(path.read_text())
        data["operators"][1]["required_capabilities"].append("AUTHOR_CODE")
        data["operators"][1]["forbidden_capabilities"].remove("AUTHOR_CODE")
        path.write_text(json.dumps(data))
        with self.assertRaises(gate.GateError): gate.validate(root)

    def test_reject_operator_identity_reassignment(self):
        temporary, root = self.copy_fixture(); self.addCleanup(temporary.cleanup)
        path = root / "docs/judge/OPERATOR-CHAIN.json"; data = json.loads(path.read_text())
        data["operators"][2]["identity"] = "Claude Code Action"; path.write_text(json.dumps(data))
        with self.assertRaises(gate.GateError): gate.validate(root)


if __name__ == "__main__":
    unittest.main()
