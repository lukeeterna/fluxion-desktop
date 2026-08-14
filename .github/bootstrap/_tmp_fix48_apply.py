#!/usr/bin/env python3
from pathlib import Path

P = Path('.github/bootstrap/fluxion-soleur-adapter.py')
text = P.read_text(encoding='utf-8')


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one match, got {count}')
    text = text.replace(old, new, 1)


replace_once(
    'import subprocess\nimport sys\nfrom pathlib import Path\n',
    'import subprocess\nimport sys\nimport tempfile\nfrom pathlib import Path\n',
    'tempfile import',
)

old_discovery = '''def parse_worktrees(repo: Path) -> list[dict[str, str]]:
    raw = git(repo, "worktree", "list", "--porcelain")
    out: list[dict[str, str]] = []
    cur: dict[str, str] = {}
    for line in raw.splitlines() + [""]:
        if not line:
            if cur:
                out.append(cur)
                cur = {}
            continue
        key, _, value = line.partition(" ")
        if key in {"worktree", "HEAD", "branch"}:
            cur[key] = value
    return out


def changed_paths(repo: Path, base: str, head: str) -> list[str]:
'''

new_discovery = '''def parse_worktrees(repo: Path) -> list[dict[str, str]]:
    raw = git(repo, "worktree", "list", "--porcelain")
    out: list[dict[str, str]] = []
    cur: dict[str, str] = {}
    for line in raw.splitlines() + [""]:
        if not line:
            if cur:
                out.append(cur)
                cur = {}
            continue
        key, _, value = line.partition(" ")
        if key in {"worktree", "HEAD", "branch"}:
            cur[key] = value
    return out


def parse_local_branches(repo: Path) -> list[dict[str, str]]:
    raw = git(repo, "for-each-ref", "--format=%(refname:short) %(objectname)", "refs/heads")
    out: list[dict[str, str]] = []
    for line in raw.splitlines():
        branch, sep, head = line.partition(" ")
        if not sep or not branch or not HEX40.fullmatch(head):
            raise Blocked("malformed local branch ref")
        out.append({"branch": branch, "HEAD": head})
    return out


def candidate_feature_refs(repo: Path) -> list[tuple[str, str]]:
    refs: set[tuple[str, str]] = set()
    for wt in parse_worktrees(repo):
        branch = wt.get("branch", "").removeprefix("refs/heads/")
        head = wt.get("HEAD", "")
        if branch and branch not in {"main", "master"} and HEX40.fullmatch(head):
            refs.add((branch, head))
    for ref in parse_local_branches(repo):
        branch = ref["branch"]
        head = ref["HEAD"]
        if branch not in {"main", "master"}:
            refs.add((branch, head))
    return sorted(refs)


def changed_paths(repo: Path, base: str, head: str) -> list[str]:
'''
replace_once(old_discovery, new_discovery, 'candidate discovery')

old_loop = '''    candidates: list[tuple[int, int, str, str, list[str]]] = []
    for wt in parse_worktrees(repo):
        head = wt.get("HEAD", "")
        branch = wt.get("branch", "").removeprefix("refs/heads/")
        if not HEX40.fullmatch(head) or head == base:
            continue
        mb = git(repo, "merge-base", base, head, check=False)
        if mb != base:
            continue
        paths = changed_paths(repo, base, head)
        n_allowed = sum(p in allowed for p in paths)
        if not n_allowed:
            continue
        count_s = git(repo, "rev-list", "--count", f"{base}..{head}")
        candidates.append((n_allowed, int(count_s), branch, head, paths))
    if not candidates:
        raise Blocked("no Soleur worktree with allowed-path changes found")
    candidates.sort(reverse=True)
    best = candidates[0]
    if len(candidates) > 1 and candidates[1][:2] == best[:2]:
        raise Blocked("ambiguous Soleur candidate worktrees")
'''

new_loop = '''    candidates: list[tuple[int, int, str, str, list[str]]] = []
    for branch, head in candidate_feature_refs(repo):
        if head == base:
            continue
        mb = git(repo, "merge-base", base, head, check=False)
        if mb != base:
            continue
        paths = changed_paths(repo, base, head)
        n_allowed = sum(p in allowed for p in paths)
        if not n_allowed:
            continue
        count_s = git(repo, "rev-list", "--count", f"{base}..{head}")
        candidates.append((n_allowed, int(count_s), branch, head, paths))
    if not candidates:
        raise Blocked("no Soleur feature ref with allowed-path changes found")
    candidates.sort(reverse=True)
    best = candidates[0]
    if len(candidates) > 1 and candidates[1][:2] == best[:2]:
        raise Blocked("ambiguous Soleur candidate refs")
'''
replace_once(old_loop, new_loop, 'export candidate loop')

old_selftest = '''def cmd_self_test(_: argparse.Namespace) -> int:
    sample = {
        "schema_version": 1,
        "channel": CHANNEL,
        "kind": "TASK",
        "session_id": "selftest",
        "task_id": "SELFTEST-1",
        "created_at": "2026-08-12T20:00:00Z",
        "base_commit": "a" * 40,
        "action_profile": "FIX_SCOPED_BUG",
        "specification": "x",
        "allowed_paths": ["voice-agent/src/example.py"],
        "forbidden_actions": [],
        "required_tests": [],
        "negative_tests": [],
        "evidence_required": [],
        "retry_limit": 0,
        "rollback": "git revert",
        "stop_conditions": [],
    }
    validate_task_obj(sample)
    bad = dict(sample)
    bad["allowed_paths"] = ["../escape"]
    try:
        validate_task_obj(bad)
    except Blocked:
        pass
    else:
        raise Blocked("self-test unsafe-path mutation survived")
    data = b"abc"
    assert git_blob_sha(data) == hashlib.sha1(b"blob 3\\0abc").hexdigest()
    print("SELF_TEST=PASS")
    return 0
'''

new_selftest = '''def _selftest_task(base: str) -> dict:
    return {
        "schema_version": 1,
        "channel": CHANNEL,
        "kind": "TASK",
        "session_id": "selftest",
        "task_id": "SELFTEST-1",
        "created_at": "2026-08-12T20:00:00Z",
        "base_commit": base,
        "action_profile": "FIX_SCOPED_BUG",
        "specification": "x",
        "allowed_paths": ["allowed.txt"],
        "forbidden_actions": [],
        "required_tests": [],
        "negative_tests": [],
        "evidence_required": [],
        "retry_limit": 0,
        "rollback": "git revert",
        "stop_conditions": [],
    }


def _selftest_repo(root: Path) -> tuple[Path, str]:
    repo = root / "repo"
    repo.mkdir()
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.name", "FLUXION Self-Test")
    git(repo, "config", "user.email", "selftest@example.invalid")
    (repo / "allowed.txt").write_text("base\\n", encoding="utf-8")
    git(repo, "add", "allowed.txt")
    git(repo, "commit", "-m", "base")
    return repo, git(repo, "rev-parse", "HEAD")


def _selftest_export(repo: Path, task: dict, root: Path) -> dict:
    task_path = root / "task.json"
    patch_path = root / "out.patch"
    meta_path = root / "out.json"
    write_json(task_path, task)
    args = argparse.Namespace(
        repo=str(repo), task=str(task_path), out_patch=str(patch_path), out_meta=str(meta_path)
    )
    cmd_export(args)
    if not patch_path.read_bytes().strip():
        raise Blocked("self-test export produced empty patch")
    return load_json(meta_path)


def cmd_self_test(_: argparse.Namespace) -> int:
    sample = _selftest_task("a" * 40)
    validate_task_obj(sample)
    bad = dict(sample)
    bad["allowed_paths"] = ["../escape"]
    try:
        validate_task_obj(bad)
    except Blocked:
        pass
    else:
        raise Blocked("self-test unsafe-path mutation survived")
    data = b"abc"
    assert git_blob_sha(data) == hashlib.sha1(b"blob 3\\0abc").hexdigest()

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        repo, base = _selftest_repo(root)
        git(repo, "checkout", "-b", "feat/reviewed")
        (repo / "allowed.txt").write_text("reviewed\\n", encoding="utf-8")
        git(repo, "add", "allowed.txt")
        git(repo, "commit", "-m", "reviewed")
        reviewed_head = git(repo, "rev-parse", "HEAD")
        git(repo, "checkout", "main")
        if len(parse_worktrees(repo)) != 1:
            raise Blocked("self-test expected feature worktree to be absent")
        meta = _selftest_export(repo, _selftest_task(base), root)
        if meta.get("source_branch") != "feat/reviewed" or meta.get("source_head") != reviewed_head:
            raise Blocked("self-test failed to recover reviewed local branch")
        if meta.get("allowed_changed_paths") != ["allowed.txt"]:
            raise Blocked("self-test exported unexpected path set")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        repo, base = _selftest_repo(root)
        git(repo, "checkout", "-b", "feat/out-of-scope")
        (repo / "other.txt").write_text("x\\n", encoding="utf-8")
        git(repo, "add", "other.txt")
        git(repo, "commit", "-m", "other")
        git(repo, "checkout", "main")
        try:
            _selftest_export(repo, _selftest_task(base), root)
        except Blocked:
            pass
        else:
            raise Blocked("self-test accepted out-of-scope-only branch")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        repo, base = _selftest_repo(root)
        git(repo, "checkout", "--orphan", "feat/wrong-ancestry")
        git(repo, "rm", "-rf", ".")
        (repo / "allowed.txt").write_text("foreign\\n", encoding="utf-8")
        git(repo, "add", "allowed.txt")
        git(repo, "commit", "-m", "foreign")
        git(repo, "checkout", "main")
        try:
            _selftest_export(repo, _selftest_task(base), root)
        except Blocked:
            pass
        else:
            raise Blocked("self-test accepted wrong-ancestry branch")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        repo, base = _selftest_repo(root)
        for branch, body in (("feat/a", "a\\n"), ("feat/b", "b\\n")):
            git(repo, "checkout", "-b", branch, base)
            (repo / "allowed.txt").write_text(body, encoding="utf-8")
            git(repo, "add", "allowed.txt")
            git(repo, "commit", "-m", branch)
            git(repo, "checkout", "main")
        try:
            _selftest_export(repo, _selftest_task(base), root)
        except Blocked as exc:
            if "ambiguous Soleur candidate refs" not in str(exc):
                raise
        else:
            raise Blocked("self-test failed to block ambiguous candidate refs")

    print("SELF_TEST=PASS")
    return 0
'''
replace_once(old_selftest, new_selftest, 'self-test')

P.write_text(text, encoding='utf-8')
print('FIX48_PATCH_APPLIED=PASS')
