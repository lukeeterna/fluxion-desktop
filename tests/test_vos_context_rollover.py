from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

import vos_context_rollover as rollover

SOURCE_THREAD = "019d1c0a-0137-73f3-bf4a-88c90739150c"
NEW_THREAD = "019d1c0a-0137-73f3-bf4a-88c90739150d"


class ContextRolloverTests(unittest.TestCase):
    def git(self, root: Path, *args: str) -> str:
        return subprocess.check_output(["git", *args], cwd=root, text=True).strip()

    def make_repo(self, root: Path) -> str:
        subprocess.run(["git", "init", "-q", "-b", "master", str(root)], check=True)
        self.git(root, "config", "user.email", "test@example.invalid")
        self.git(root, "config", "user.name", "VOS Test")
        (root / "README.md").write_text("rollover fixture\n", encoding="utf-8")
        self.git(root, "add", ".")
        self.git(root, "commit", "-qm", "base")
        return self.git(root, "rev-parse", "HEAD")

    def make_inputs(self, root: Path, head: str):
        task = {
            "schema_version": 1,
            "unit_id": "T-ZERO",
            "plan_path": "vos/control/plans/zero.md",
            "plan_sha256": "1" * 64,
            "mandate_sha256": "2" * 64,
            "base_commit": head,
            "lease_nonce": "a" * 32,
            "thread_id": SOURCE_THREAD,
            "objective_sha256": "3" * 64,
        }
        task_sha = rollover.sha256_bytes(rollover.canonical_json(task))
        worker = {
            "schema_version": 1,
            "status": "PASS",
            "task_sha256": task_sha,
            "thread_id": SOURCE_THREAD,
            "objective_sha256": task["objective_sha256"],
            "unit_id": task["unit_id"],
            "lease_nonce": task["lease_nonce"],
            "mandate_sha256": task["mandate_sha256"],
            "base_commit": head,
            "result_commit": "b" * 40,
            "result_branch": "vos/unit/t-zero/fixture",
            "changed_paths": ["out/result.txt"],
            "log_sha256": {},
            "published": False,
        }
        task_path = root.parent / "task.json"
        worker_path = root.parent / "worker.json"
        prior_path = root.parent / "prior.json"
        checkpoint_path = root.parent / "checkpoint.json"
        result_path = root.parent / "rollover-result.json"
        task_path.write_text(json.dumps(task, sort_keys=True), encoding="utf-8")
        worker_path.write_text(json.dumps(worker, sort_keys=True), encoding="utf-8")
        worker_sha = rollover.sha256_file(worker_path)
        prior = {
            "schema_version": 1,
            "status": "PASS",
            "phase": "RESUME",
            "thread_id": SOURCE_THREAD,
            "thread_id_match": "PASS",
            "task_sha256": task_sha,
            "worker_result_sha256": worker_sha,
            "decision": "ACCEPT",
            "next_action": "Continue from durable checkpoint.",
        }
        prior_path.write_text(json.dumps(prior, sort_keys=True), encoding="utf-8")
        return task_path, worker_path, prior_path, checkpoint_path, result_path

    def make_fake_codex(self, root: Path) -> Path:
        fake = root / "codex"
        fake.write_text(
            r'''#!/usr/bin/env python3
import json, os, re, sys
from pathlib import Path
SOURCE="019d1c0a-0137-73f3-bf4a-88c90739150c"
NEW="019d1c0a-0137-73f3-bf4a-88c90739150d"
home=Path(os.environ["CODEX_HOME"])
home.mkdir(parents=True, exist_ok=True)
with (home/"rollover-calls.txt").open("a",encoding="utf-8") as h: h.write("call\n")
args=sys.argv[1:]
if not args or args[0] != "exec": raise SystemExit(9)
prompt=args[-1]
def grab(key):
    m=re.search(r'"'+re.escape(key)+r'":\s*(?:"([^"]*)"|(true|false))', prompt)
    if not m: raise SystemExit(8)
    return m.group(1) if m.group(1) is not None else (m.group(2)=="true")
checkpoint_match=re.search(r'Checkpoint SHA256: ([0-9a-f]{64})', prompt)
probe_match=re.search(r'Live probe SHA256: ([0-9a-f]{64})', prompt)
if not checkpoint_match or not probe_match: raise SystemExit(7)
checkpoint_sha=checkpoint_match.group(1)
probe_sha=probe_match.group(1)
if os.environ.get("FAKE_BAD_PROBE") == "1": probe_sha="f"*64
source=grab("source_thread_id")
head=grab("repo_head")
platform=grab("platform")
result_commit=grab("result_commit")
tid=SOURCE if os.environ.get("FAKE_SAME_THREAD")=="1" else NEW
session=home/"sessions"/"2026"/"08"/"29"
session.mkdir(parents=True, exist_ok=True)
(session/f"rollout-{tid}.jsonl").write_text(json.dumps({"type":"turn_context","payload":{"model":"gpt-5.6-sol"}})+"\n",encoding="utf-8")
print(json.dumps({"type":"thread.started","thread_id":tid}))
print(json.dumps({"type":"turn.started"}))
if os.environ.get("FAKE_FILE_CHANGE") == "1":
    print(json.dumps({"type":"item.completed","item":{"id":"f1","type":"file_change","changes":[{"path":"x","kind":"add"}],"status":"completed"}}))
response={"checkpoint_sha256":checkpoint_sha,"live_probe_sha256":probe_sha,"source_thread_id":source,"observed_head":head,"platform":platform,"worktree_clean":True,"prior_result_commit":result_commit,"continuation":"CONTINUE"}
print(json.dumps({"type":"item.completed","item":{"id":"a1","type":"agent_message","text":json.dumps(response,sort_keys=True)}}))
print(json.dumps({"type":"turn.completed","usage":{"input_tokens":1,"output_tokens":1}}))
''',
            encoding="utf-8",
        )
        fake.chmod(0o755)
        return fake

    def setup_flow(self, td: str):
        outer = Path(td)
        repo = outer / "repo"
        head = self.make_repo(repo)
        paths = self.make_inputs(repo, head)
        fake = self.make_fake_codex(outer)
        codex_home = outer / "codex-home"
        codex_home.mkdir()
        evidence = outer / "evidence"
        evidence.mkdir()
        return repo, head, fake, codex_home, evidence, paths

    def codex_env(self, home: Path):
        class Env:
            def __enter__(inner):
                inner.old = os.environ.get("CODEX_HOME")
                os.environ["CODEX_HOME"] = str(home)
            def __exit__(inner, *_):
                if inner.old is None:
                    os.environ.pop("CODEX_HOME", None)
                else:
                    os.environ["CODEX_HOME"] = inner.old
        return Env()

    def seal(self, repo: Path, paths):
        task, worker, prior, checkpoint, _ = paths
        return rollover.create_checkpoint(
            repo=repo, task_path=task, worker_result_path=worker,
            bridge_result_path=prior, checkpoint_path=checkpoint,
        )

    def run_rollover(self, repo, fake, home, evidence, paths):
        _, _, _, checkpoint, result = paths
        with self.codex_env(home):
            return rollover.rollover(
                codex=str(fake), codex_home=home, model="gpt-5.6-sol", repo=repo,
                checkpoint_path=checkpoint, evidence=evidence, result_path=result, timeout=10,
            )

    def test_rollover_uses_controller_probe_new_thread_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as td:
            repo, head, fake, home, evidence, paths = self.setup_flow(td)
            checkpoint = self.seal(repo, paths)
            first = self.run_rollover(repo, fake, home, evidence, paths)
            self.assertEqual(first["status"], "PASS")
            self.assertEqual(first["source_thread_id"], SOURCE_THREAD)
            self.assertEqual(first["new_thread_id"], NEW_THREAD)
            self.assertEqual(first["new_thread_distinct"], "PASS")
            self.assertEqual(first["live_state_match"], "PASS")
            self.assertEqual(first["live_probe_hash_match"], "PASS")
            self.assertEqual(first["checkpoint_sha256"], checkpoint["checkpoint_sha256"])
            self.assertEqual(first["live_repo_head"], head)
            probe=json.loads((evidence/"context-live-probe.json").read_text())
            self.assertEqual(probe["live_probe_sha256"], first["live_probe_sha256"])
            self.assertEqual(
                probe["live_probe_sha256"],
                rollover.sha256_bytes(rollover.canonical_json(probe["probe"])),
            )
            events=[json.loads(line) for line in (evidence/"context-rollover.jsonl").read_text().splitlines() if line.strip()]
            self.assertFalse(any(isinstance(e.get("item"),dict) and e["item"].get("type")=="command_execution" for e in events))
            self.assertEqual(len((home/"rollover-calls.txt").read_text().splitlines()), 1)
            second = self.run_rollover(repo, fake, home, evidence, paths)
            self.assertEqual(second, first)
            self.assertEqual(len((home/"rollover-calls.txt").read_text().splitlines()), 1)

    def test_tampered_checkpoint_blocks(self):
        with tempfile.TemporaryDirectory() as td:
            repo, _, fake, home, evidence, paths = self.setup_flow(td)
            self.seal(repo, paths)
            data = json.loads(paths[3].read_text())
            data["checkpoint"]["next_action"] = "tampered"
            paths[3].write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(rollover.RolloverError):
                self.run_rollover(repo, fake, home, evidence, paths)

    def test_stale_git_head_blocks_before_codex(self):
        with tempfile.TemporaryDirectory() as td:
            repo, _, fake, home, evidence, paths = self.setup_flow(td)
            self.seal(repo, paths)
            (repo/"README.md").write_text("changed\n", encoding="utf-8")
            self.git(repo, "add", ".")
            self.git(repo, "commit", "-qm", "advance")
            with self.assertRaises(rollover.RolloverError):
                self.run_rollover(repo, fake, home, evidence, paths)
            self.assertFalse((home/"rollover-calls.txt").exists())

    def test_dirty_repo_blocks_checkpoint(self):
        with tempfile.TemporaryDirectory() as td:
            repo, _, _, _, _, paths = self.setup_flow(td)
            (repo/"dirty.txt").write_text("dirty\n", encoding="utf-8")
            with self.assertRaises(rollover.RolloverError):
                self.seal(repo, paths)

    def test_dirty_repo_after_checkpoint_blocks_before_codex(self):
        with tempfile.TemporaryDirectory() as td:
            repo, _, fake, home, evidence, paths = self.setup_flow(td)
            self.seal(repo, paths)
            (repo/"dirty-after.txt").write_text("dirty\n", encoding="utf-8")
            with self.assertRaises(rollover.RolloverError):
                self.run_rollover(repo, fake, home, evidence, paths)
            self.assertFalse((home/"rollover-calls.txt").exists())

    def test_same_thread_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            repo, _, fake, home, evidence, paths = self.setup_flow(td)
            self.seal(repo, paths)
            os.environ["FAKE_SAME_THREAD"] = "1"
            try:
                with self.assertRaises(rollover.RolloverError):
                    self.run_rollover(repo, fake, home, evidence, paths)
            finally:
                os.environ.pop("FAKE_SAME_THREAD", None)

    def test_bad_live_probe_hash_from_new_thread_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            repo, _, fake, home, evidence, paths = self.setup_flow(td)
            self.seal(repo, paths)
            os.environ["FAKE_BAD_PROBE"] = "1"
            try:
                with self.assertRaises(rollover.RolloverError):
                    self.run_rollover(repo, fake, home, evidence, paths)
            finally:
                os.environ.pop("FAKE_BAD_PROBE", None)

    def test_file_change_event_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            repo, _, fake, home, evidence, paths = self.setup_flow(td)
            self.seal(repo, paths)
            os.environ["FAKE_FILE_CHANGE"] = "1"
            try:
                with self.assertRaises(rollover.RolloverError):
                    self.run_rollover(repo, fake, home, evidence, paths)
            finally:
                os.environ.pop("FAKE_FILE_CHANGE", None)

    def test_prior_reject_cannot_be_checkpointed(self):
        with tempfile.TemporaryDirectory() as td:
            repo, _, _, _, _, paths = self.setup_flow(td)
            prior = json.loads(paths[2].read_text())
            prior["decision"] = "REJECT"
            paths[2].write_text(json.dumps(prior), encoding="utf-8")
            with self.assertRaises(rollover.RolloverError):
                self.seal(repo, paths)


if __name__ == "__main__":
    unittest.main()
