from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import vos_sol_bridge as bridge
import vos_worker_adapter as worker

ROOT = Path(__file__).resolve().parents[1]
THREAD = "019d1c0a-0137-73f3-bf4a-88c90739150c"
OTHER_THREAD = "019d1c0a-0137-73f3-bf4a-88c90739150d"


class ZeroShuttleTests(unittest.TestCase):
    def git(self, root: Path, *args: str) -> str:
        return subprocess.check_output(["git", *args], cwd=root, text=True).strip()

    def make_repo(self, root: Path, *, bad_path: bool = False) -> tuple[Path, dict[str, str]]:
        subprocess.run(["git", "init", "-q", "-b", "master", str(root)], check=True)
        self.git(root, "config", "user.email", "test@example.invalid")
        self.git(root, "config", "user.name", "VOS Test")
        for rel in ["bin", "docs/judge/mandati", "vos/control/plans"]:
            (root / rel).mkdir(parents=True, exist_ok=True)
        for name in ["vos_common.py", "vos_apply.py", "vos_worker_adapter.py"]:
            shutil.copy2(ROOT / "bin" / name, root / "bin" / name)
        (root / ".gitignore").write_text("vos/control/plans/\n", encoding="utf-8")
        target = "forbidden.txt" if bad_path else "out/result.txt"
        (root / "bin" / "task.py").write_text(
            "from pathlib import Path\n"
            f"p=Path({target!r}); p.parent.mkdir(parents=True, exist_ok=True); p.write_text('zero-shuttle-ok\\n')\n",
            encoding="utf-8",
        )
        mandate = root / "docs/judge/mandati/T-ZERO.md"
        mandate.write_text("ETICHETTA: SAFE_AUTO\nFixture zero shuttle.\n", encoding="utf-8")
        mandate_sha = hashlib.sha256(mandate.read_bytes()).hexdigest()
        manifest = {
            "schema_version": 1,
            "unit_id": "T-ZERO",
            "label": "SAFE_AUTO",
            "lane": "REPO",
            "risk": "A",
            "base_commit": "*",
            "mandate_md": "docs/judge/mandati/T-ZERO.md",
            "mandate_sha256": mandate_sha,
            "key": "T-ZERO@fixture",
            "allowed_paths": ["out"],
            "steps": [
                {
                    "id": "F1",
                    "argv": ["python3", "bin/task.py"],
                    "cwd": ".",
                    "timeout_seconds": 10,
                }
            ],
        }
        (root / "docs/judge/mandati/T-ZERO.json").write_text(
            json.dumps(manifest, sort_keys=True), encoding="utf-8"
        )
        self.git(root, "add", ".")
        self.git(root, "commit", "-qm", "fixture base")
        head = self.git(root, "rev-parse", "HEAD")

        stamp = "20260828T000000Z"
        body = f"PIANO_{stamp}_UNITS_1_HEAD_{head}"
        plan_digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
        plan_rel = "vos/control/plans/zero.md"
        plan = root / plan_rel
        plan.write_text(
            f"# Piano VOS — {stamp}\n"
            f"HEAD al momento della pianificazione: {head}\n"
            "Unità selezionate: 1\n"
            f"sha256: {plan_digest}\n\n"
            "### 1. T-ZERO\n",
            encoding="utf-8",
        )
        self.assertEqual(self.git(root, "status", "--porcelain"), "")
        catalog_item = {
            "unit_id": "T-ZERO",
            "plan_path": plan_rel,
            "plan_sha256": hashlib.sha256(plan.read_bytes()).hexdigest(),
            "mandate_sha256": mandate_sha,
            "base_commit": head,
        }
        return root, catalog_item

    def make_fake_codex(self, root: Path) -> Path:
        fake = root / "codex"
        fake.write_text(
            r'''#!/usr/bin/env python3
import json, os, re, sys
from pathlib import Path

THREAD = "019d1c0a-0137-73f3-bf4a-88c90739150c"
OTHER = "019d1c0a-0137-73f3-bf4a-88c90739150d"
args = sys.argv[1:]
home = Path(os.environ["CODEX_HOME"])
home.mkdir(parents=True, exist_ok=True)
with (home / "calls.txt").open("a", encoding="utf-8") as h:
    h.write("call\n")

def emit(tid, text):
    print(json.dumps({"type":"thread.started","thread_id":tid}))
    print(json.dumps({"type":"turn.started"}))
    print(json.dumps({"type":"item.completed","item":{"id":"i1","type":"agent_message","text":text}}))
    print(json.dumps({"type":"turn.completed","usage":{"input_tokens":1,"output_tokens":1}}))

if not args or args[0] != "exec":
    raise SystemExit(9)
if "resume" in args:
    idx = args.index("resume")
    requested = args[idx + 1]
    prompt = args[-1]
    m = re.search(r'"worker_result_sha256":\s*"([0-9a-f]{64})"', prompt)
    if not m:
        raise SystemExit(8)
    tid = OTHER if os.environ.get("FAKE_WRONG_THREAD") == "1" else requested
    emit(tid, json.dumps({"decision":"ACCEPT","evidence_hash":m.group(1),"next_action":"NONE"}, sort_keys=True))
    raise SystemExit(0)

session = home / "sessions" / "2026" / "08" / "28"
session.mkdir(parents=True, exist_ok=True)
(session / f"rollout-{THREAD}.jsonl").write_text(
    json.dumps({"type":"turn_context","payload":{"model":"gpt-5.6-sol"}}) + "\n",
    encoding="utf-8",
)
emit(THREAD, json.dumps({"unit_id":"T-ZERO","reason":"only sealed unit"}, sort_keys=True))
''',
            encoding="utf-8",
        )
        fake.chmod(0o755)
        return fake

    def prepare_flow(self, td: str, *, bad_path: bool = False):
        outer = Path(td)
        repo, catalog_item = self.make_repo(outer / "repo", bad_path=bad_path)
        codex_home = outer / "codex-home"
        codex_home.mkdir()
        fake = self.make_fake_codex(outer)
        catalog = outer / "catalog.json"
        catalog.write_text(json.dumps([catalog_item], sort_keys=True), encoding="utf-8")
        workspace = outer / "workspace"
        evidence = outer / "evidence"
        workspace.mkdir()
        evidence.mkdir()
        task_path = outer / "task.json"
        worker_result = outer / "worker-result.json"
        bridge_result = outer / "bridge-result.json"
        return repo, fake, codex_home, catalog, workspace, evidence, task_path, worker_result, bridge_result

    def with_codex_home(self, path: Path):
        class Env:
            def __enter__(inner):
                inner.old = os.environ.get("CODEX_HOME")
                os.environ["CODEX_HOME"] = str(path)
            def __exit__(inner, *_):
                if inner.old is None:
                    os.environ.pop("CODEX_HOME", None)
                else:
                    os.environ["CODEX_HOME"] = inner.old
        return Env()

    def start_task(self, fake: Path, codex_home: Path, catalog: Path, workspace: Path,
                   evidence: Path, task_path: Path):
        with self.with_codex_home(codex_home):
            started = bridge.start(
                codex=str(fake),
                codex_home=codex_home,
                model="gpt-5.6-sol",
                objective="Create the harmless zero-shuttle fixture result using the sealed SAFE_AUTO unit.",
                catalog_path=catalog,
                workspace=workspace,
                evidence=evidence,
                task_path=task_path,
                timeout=10,
            )
        self.assertEqual(started["status"], "PASS")
        self.assertEqual(started["thread_id"], THREAD)
        return json.loads(task_path.read_text(encoding="utf-8"))

    def test_zero_prompt_shuttle_end_to_end_and_idempotent(self):
        with tempfile.TemporaryDirectory() as td:
            repo, fake, home, catalog, workspace, evidence, task_path, worker_result, bridge_result = self.prepare_flow(td)
            task = self.start_task(fake, home, catalog, workspace, evidence, task_path)
            first_worker = worker.run_task(repo, task, output_path=worker_result)
            self.assertEqual(first_worker["status"], "PASS")
            self.assertEqual(worker.classify_terminal(repo, task["lease_nonce"]), "TERMINAL_PASS")
            with self.with_codex_home(home):
                first_bridge = bridge.resume(
                    codex=str(fake), task_path=task_path, worker_result_path=worker_result,
                    workspace=workspace, evidence=evidence, bridge_result_path=bridge_result, timeout=10,
                )
            self.assertEqual(first_bridge["decision"], "ACCEPT")
            self.assertEqual(first_bridge["thread_id_match"], "PASS")
            calls_before = (home / "calls.txt").read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(calls_before), 2)

            branches_before = self.git(repo, "branch", "--format=%(refname:short)").splitlines()
            second_worker = worker.run_task(repo, task, output_path=worker_result)
            with self.with_codex_home(home):
                second_bridge = bridge.resume(
                    codex=str(fake), task_path=task_path, worker_result_path=worker_result,
                    workspace=workspace, evidence=evidence, bridge_result_path=bridge_result, timeout=10,
                )
            branches_after = self.git(repo, "branch", "--format=%(refname:short)").splitlines()
            calls_after = (home / "calls.txt").read_text(encoding="utf-8").splitlines()
            self.assertEqual(second_worker["result_commit"], first_worker["result_commit"])
            self.assertEqual(second_bridge, first_bridge)
            self.assertEqual(branches_after, branches_before)
            self.assertEqual(len(calls_after), 2)

    def test_wrong_base_sha_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            repo, fake, home, catalog, workspace, evidence, task_path, worker_result, _ = self.prepare_flow(td)
            task = self.start_task(fake, home, catalog, workspace, evidence, task_path)
            task["base_commit"] = "0" * 40
            with self.assertRaises(worker.VOSFailure):
                worker.run_task(repo, task, output_path=worker_result)

    def test_wrong_mandate_hash_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            repo, fake, home, catalog, workspace, evidence, task_path, worker_result, _ = self.prepare_flow(td)
            task = self.start_task(fake, home, catalog, workspace, evidence, task_path)
            task["mandate_sha256"] = "0" * 64
            with self.assertRaises(worker.VOSFailure):
                worker.run_task(repo, task, output_path=worker_result)

    def test_fake_thread_id_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            repo, fake, home, catalog, workspace, evidence, task_path, worker_result, _ = self.prepare_flow(td)
            task = self.start_task(fake, home, catalog, workspace, evidence, task_path)
            task["thread_id"] = "not-a-thread"
            with self.assertRaises(worker.VOSFailure):
                worker.run_task(repo, task, output_path=worker_result)

    def test_forbidden_path_is_terminal_fail(self):
        with tempfile.TemporaryDirectory() as td:
            repo, fake, home, catalog, workspace, evidence, task_path, worker_result, _ = self.prepare_flow(td, bad_path=True)
            task = self.start_task(fake, home, catalog, workspace, evidence, task_path)
            with self.assertRaises(worker.VOSFailure):
                worker.run_task(repo, task, output_path=worker_result)
            self.assertEqual(worker.classify_terminal(repo, task["lease_nonce"]), "TERMINAL_FAIL")

    def test_dead_without_terminal_marker_is_classified(self):
        with tempfile.TemporaryDirectory() as td:
            repo, fake, home, catalog, workspace, evidence, task_path, _, _ = self.prepare_flow(td)
            task = self.start_task(fake, home, catalog, workspace, evidence, task_path)
            started, terminal = worker._control_paths(repo, task["lease_nonce"])
            started.parent.mkdir(parents=True, exist_ok=True)
            started.write_text("{}\n", encoding="utf-8")
            self.assertFalse(terminal.exists())
            self.assertEqual(worker.classify_terminal(repo, task["lease_nonce"]), "DEAD_WITHOUT_MARKER")

    def test_resume_rejects_changed_thread(self):
        with tempfile.TemporaryDirectory() as td:
            repo, fake, home, catalog, workspace, evidence, task_path, worker_result, bridge_result = self.prepare_flow(td)
            task = self.start_task(fake, home, catalog, workspace, evidence, task_path)
            worker.run_task(repo, task, output_path=worker_result)
            os.environ["FAKE_WRONG_THREAD"] = "1"
            try:
                with self.with_codex_home(home), self.assertRaises(bridge.BridgeError):
                    bridge.resume(
                        codex=str(fake), task_path=task_path, worker_result_path=worker_result,
                        workspace=workspace, evidence=evidence, bridge_result_path=bridge_result, timeout=10,
                    )
            finally:
                os.environ.pop("FAKE_WRONG_THREAD", None)

    def test_resume_rejects_tampered_worker_result(self):
        with tempfile.TemporaryDirectory() as td:
            repo, fake, home, catalog, workspace, evidence, task_path, worker_result, bridge_result = self.prepare_flow(td)
            task = self.start_task(fake, home, catalog, workspace, evidence, task_path)
            result = worker.run_task(repo, task, output_path=worker_result)
            result["mandate_sha256"] = "f" * 64
            worker_result.write_text(json.dumps(result, sort_keys=True), encoding="utf-8")
            with self.with_codex_home(home), self.assertRaises(bridge.BridgeError):
                bridge.resume(
                    codex=str(fake), task_path=task_path, worker_result_path=worker_result,
                    workspace=workspace, evidence=evidence, bridge_result_path=bridge_result, timeout=10,
                )


if __name__ == "__main__":
    unittest.main()
