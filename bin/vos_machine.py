#!/usr/bin/env python3
"""FLUXION VOS machine registry and fail-closed authority gate.

The tool never persists a hardware serial or platform UUID.  It hashes the
machine identifier locally with a repository-specific domain separator and
stores only the digest.  It is intentionally macOS-first because the current
production topology is MacBook + iMac.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import hmac
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = 1
REPOSITORY_ID = "github.com/lukeeterna/fluxion-desktop"
FINGERPRINT_DOMAIN = b"fluxion-vos-machine-v1\0"
PATH_DOMAIN = b"fluxion-vos-repo-path-v1\0"
LOCAL_KEY_RELATIVE = Path("vos-machine/identity-key.bin")
VALID_ROLES = {"repo_authority", "runtime_authority", "repo_mirror"}
DEFAULT_REGISTRY = Path("docs/judge/MACHINES.json")
MACHINE_ID_RE = re.compile(r"^[a-z][a-z0-9_-]{2,31}$")


class MachineError(RuntimeError):
    pass


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def run(
    command: list[str],
    *,
    cwd: Path | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
    )
    if check and completed.returncode != 0:
        raise MachineError(
            f"command failed ({completed.returncode}): {' '.join(command)}; "
            f"stderr={completed.stderr.strip()!r}"
        )
    return completed


def repo_root() -> Path:
    completed = run(["git", "rev-parse", "--show-toplevel"])
    return Path(completed.stdout.strip()).resolve()


def git(root: Path, *arguments: str, check: bool = True) -> str:
    return run(["git", *arguments], cwd=root, check=check).stdout.strip()


def canonical_remote(remote: str) -> str:
    value = remote.strip()
    patterns = (
        r"^(?:https?://)?github\.com/(?P<path>[^/]+/[^/]+?)(?:\.git)?$",
        r"^git@github\.com:(?P<path>[^/]+/[^/]+?)(?:\.git)?$",
        r"^ssh://git@github\.com/(?P<path>[^/]+/[^/]+?)(?:\.git)?$",
    )
    for pattern in patterns:
        match = re.match(pattern, value)
        if match:
            return f"github.com/{match.group('path').removesuffix('.git')}"
    return value.removesuffix(".git")


def raw_platform_identifier() -> str:
    if platform.system() != "Darwin":
        raise MachineError("machine fingerprinting is supported only on macOS")

    ioreg = run(
        ["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"],
        check=False,
    )
    if ioreg.returncode == 0:
        match = re.search(r'"IOPlatformUUID"\s*=\s*"([^"]+)"', ioreg.stdout)
        if match:
            return match.group(1)

    kern_uuid = run(["sysctl", "-n", "kern.uuid"], check=False)
    if kern_uuid.returncode == 0 and kern_uuid.stdout.strip():
        return kern_uuid.stdout.strip()

    raise MachineError("cannot derive a stable macOS platform identifier")


def git_dir(root: Path) -> Path:
    value = Path(git(root, "rev-parse", "--git-dir"))
    return value.resolve() if value.is_absolute() else (root / value).resolve()


def local_identity_key(root: Path) -> bytes:
    path = git_dir(root) / LOCAL_KEY_RELATIVE
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        descriptor = os.open(path, flags, 0o600)
        try:
            key = os.urandom(32)
            os.write(descriptor, key)
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    mode = path.stat().st_mode & 0o777
    if mode & 0o077:
        raise MachineError(f"local machine key permissions are too broad: {oct(mode)}")
    key = path.read_bytes()
    if len(key) != 32:
        raise MachineError("local machine key must contain exactly 32 bytes")
    return key


def keyed_digest(root: Path, domain: bytes, value: str) -> str:
    key = local_identity_key(root)
    return hmac.new(key, domain + value.encode("utf-8"), hashlib.sha256).hexdigest()


def fingerprint_sha256(root: Path) -> str:
    return keyed_digest(root, FINGERPRINT_DOMAIN, raw_platform_identifier())


def repo_root_hmac_sha256(root: Path) -> str:
    return keyed_digest(root, PATH_DOMAIN, str(root.resolve()))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent)
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise MachineError(f"missing JSON file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise MachineError(f"invalid JSON file {path}: {exc}") from exc


def parse_roles(text: str) -> list[str]:
    roles = sorted({item.strip() for item in text.split(",") if item.strip()})
    unknown = set(roles) - VALID_ROLES
    if unknown:
        raise MachineError(f"unknown roles: {sorted(unknown)}")
    return roles


def listener_pids(port: int) -> list[int]:
    completed = run(
        ["lsof", "-nP", f"-iTCP:{port}", "-sTCP:LISTEN", "-t"],
        check=False,
    )
    if completed.returncode not in {0, 1}:
        raise MachineError(f"lsof failed: {completed.stderr.strip()}")
    pids: list[int] = []
    for line in completed.stdout.splitlines():
        line = line.strip()
        if line:
            pids.append(int(line))
    return sorted(set(pids))


def refresh_origin_master(root: Path) -> None:
    completed = run(
        ["git", "fetch", "--quiet", "origin", "master"],
        cwd=root,
        check=False,
    )
    if completed.returncode != 0:
        raise MachineError(
            "cannot refresh origin/master; authority verification is fail-closed: "
            + completed.stderr.strip()
        )


def head_relation(root: Path) -> dict[str, bool]:
    head = git(root, "rev-parse", "HEAD")
    origin = git(root, "rev-parse", "origin/master")
    head_is_ancestor = (
        run(
            ["git", "merge-base", "--is-ancestor", head, origin],
            cwd=root,
            check=False,
        ).returncode
        == 0
    )
    origin_is_ancestor = (
        run(
            ["git", "merge-base", "--is-ancestor", origin, head],
            cwd=root,
            check=False,
        ).returncode
        == 0
    )
    return {
        "head_equals_origin_master": head == origin,
        "head_is_ancestor_of_origin_master": head_is_ancestor,
        "origin_master_is_ancestor_of_head": origin_is_ancestor,
    }


def make_probe(machine_id: str, declared_roles: list[str], service_port: int) -> dict[str, Any]:
    if not MACHINE_ID_RE.fullmatch(machine_id):
        raise MachineError(
            "machine id must match ^[a-z][a-z0-9_-]{2,31}$"
        )
    root = repo_root()
    refresh_origin_master(root)
    remote_raw = git(root, "config", "--get", "remote.origin.url")
    remote = canonical_remote(remote_raw)
    if remote != REPOSITORY_ID:
        raise MachineError(
            f"unexpected origin: {remote!r}; expected {REPOSITORY_ID!r}"
        )

    dirty_lines = [
        line
        for line in git(root, "status", "--porcelain", "--untracked-files=all").splitlines()
        if line.strip()
    ]
    probe = {
        "schema_version": SCHEMA_VERSION,
        "machine_id": machine_id,
        "fingerprint_sha256": fingerprint_sha256(root),
        "declared_roles": declared_roles,
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
        "repository": REPOSITORY_ID,
        "repo_root": str(root),
        "repo_root_hmac_sha256": repo_root_hmac_sha256(root),
        "origin": remote,
        "head": git(root, "rev-parse", "HEAD"),
        "origin_master": git(root, "rev-parse", "origin/master"),
        "head_relation": head_relation(root),
        "dirty_entry_count": len(dirty_lines),
        "service_probe": {
            "port": service_port,
            "listener_pids": listener_pids(service_port),
        },
        "probed_at_utc": utc_now(),
    }
    return probe


def validate_probe(probe: Any) -> dict[str, Any]:
    if not isinstance(probe, dict):
        raise MachineError("probe must be a JSON object")
    required = {
        "schema_version",
        "machine_id",
        "fingerprint_sha256",
        "declared_roles",
        "repository",
        "repo_root",
        "repo_root_hmac_sha256",
        "origin",
        "head",
        "origin_master",
        "head_relation",
        "service_probe",
        "probed_at_utc",
    }
    missing = required - probe.keys()
    if missing:
        raise MachineError(f"probe missing fields: {sorted(missing)}")
    if probe["schema_version"] != SCHEMA_VERSION:
        raise MachineError("unsupported probe schema version")
    if not MACHINE_ID_RE.fullmatch(str(probe["machine_id"])):
        raise MachineError(f"invalid machine id: {probe['machine_id']!r}")
    if not re.fullmatch(r"[0-9a-f]{64}", str(probe["fingerprint_sha256"])):
        raise MachineError("invalid fingerprint digest")
    roles = probe["declared_roles"]
    if not isinstance(roles, list) or set(roles) - VALID_ROLES:
        raise MachineError(f"invalid declared roles for {probe['machine_id']}")
    if not re.fullmatch(r"[0-9a-f]{64}", str(probe["repo_root_hmac_sha256"])):
        raise MachineError("invalid repo root digest")
    if probe["repository"] != REPOSITORY_ID or probe["origin"] != REPOSITORY_ID:
        raise MachineError(f"probe {probe['machine_id']} targets a different repository")
    return probe


def load_probes(paths: Iterable[Path]) -> list[dict[str, Any]]:
    probes = [validate_probe(read_json(path)) for path in paths]
    if len(probes) < 2:
        raise MachineError("at least two machine probes are required")
    ids = [str(probe["machine_id"]) for probe in probes]
    fingerprints = [str(probe["fingerprint_sha256"]) for probe in probes]
    if len(set(ids)) != len(ids):
        raise MachineError("duplicate machine ids in probes")
    if len(set(fingerprints)) != len(fingerprints):
        raise MachineError("two ids resolve to the same physical machine")
    origin_refs = {str(probe["origin_master"]) for probe in probes}
    if len(origin_refs) != 1:
        raise MachineError(
            "machine probes disagree on origin/master; fetch and reconcile before enrollment"
        )
    return probes


def build_registry(
    probes: list[dict[str, Any]], repo_machine_id: str, runtime_machine_id: str
) -> dict[str, Any]:
    by_id = {str(probe["machine_id"]): probe for probe in probes}
    for authority in (repo_machine_id, runtime_machine_id):
        if authority not in by_id:
            raise MachineError(f"authority machine not present in probes: {authority}")

    for machine_id in (repo_machine_id, runtime_machine_id):
        relation = by_id[machine_id]["head_relation"]
        if not relation.get("head_equals_origin_master"):
            raise MachineError(
                f"authority {machine_id} is not at origin/master; enrollment refused"
            )

    machines: list[dict[str, Any]] = []
    for probe in sorted(probes, key=lambda item: str(item["machine_id"])):
        machine_id = str(probe["machine_id"])
        roles = set(probe["declared_roles"])
        roles.discard("repo_authority")
        roles.discard("runtime_authority")
        if machine_id == repo_machine_id:
            roles.add("repo_authority")
        if machine_id == runtime_machine_id:
            roles.add("runtime_authority")
        if machine_id not in {repo_machine_id, runtime_machine_id}:
            roles.add("repo_mirror")
        machines.append(
            {
                "machine_id": machine_id,
                "fingerprint_sha256": probe["fingerprint_sha256"],
                "roles": sorted(roles),
                "repo_root_hmac_sha256": probe["repo_root_hmac_sha256"],
                "origin": probe["origin"],
                "enrolled_head": probe["head"],
                "enrolled_origin_master": probe["origin_master"],
                "platform": probe["platform"],
                "service_ports": (
                    [probe["service_probe"]["port"]]
                    if machine_id == runtime_machine_id
                    else []
                ),
            }
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "repository": REPOSITORY_ID,
        "status": "ACTIVE",
        "generated_at_utc": utc_now(),
        "origin_master_at_enrollment": probes[0]["origin_master"],
        "authorities": {
            "repo_machine_id": repo_machine_id,
            "runtime_machine_id": runtime_machine_id,
        },
        "machines": machines,
    }


def validate_registry(registry: Any) -> dict[str, Any]:
    if not isinstance(registry, dict):
        raise MachineError("registry must be a JSON object")
    if registry.get("schema_version") != SCHEMA_VERSION:
        raise MachineError("unsupported machine registry schema")
    if registry.get("repository") != REPOSITORY_ID:
        raise MachineError("machine registry belongs to a different repository")
    if registry.get("status") != "ACTIVE":
        raise MachineError("machine registry is not ACTIVE")
    authorities = registry.get("authorities")
    machines = registry.get("machines")
    if not isinstance(authorities, dict) or not isinstance(machines, list):
        raise MachineError("invalid machine registry structure")
    if len(machines) < 2:
        raise MachineError("registry must describe at least two machines")

    ids: set[str] = set()
    fingerprints: set[str] = set()
    role_owners: dict[str, list[str]] = {role: [] for role in VALID_ROLES}
    for machine in machines:
        if not isinstance(machine, dict):
            raise MachineError("invalid machine entry")
        machine_id = str(machine.get("machine_id", ""))
        fingerprint = str(machine.get("fingerprint_sha256", ""))
        roles = machine.get("roles")
        if not MACHINE_ID_RE.fullmatch(machine_id):
            raise MachineError(f"invalid machine id: {machine_id!r}")
        if machine_id in ids:
            raise MachineError(f"duplicate machine id: {machine_id}")
        ids.add(machine_id)
        if not re.fullmatch(r"[0-9a-f]{64}", fingerprint):
            raise MachineError(f"invalid fingerprint for {machine_id}")
        if fingerprint in fingerprints:
            raise MachineError("duplicate physical machine fingerprint")
        fingerprints.add(fingerprint)
        if not isinstance(roles, list) or set(roles) - VALID_ROLES:
            raise MachineError(f"invalid roles for {machine_id}")
        for role in roles:
            role_owners[role].append(machine_id)
        if machine.get("origin") != REPOSITORY_ID:
            raise MachineError(f"unexpected origin for {machine_id}")
        if not re.fullmatch(r"[0-9a-f]{64}", str(machine.get("repo_root_hmac_sha256", ""))):
            raise MachineError(f"invalid repo root digest for {machine_id}")

    for role in ("repo_authority", "runtime_authority"):
        if len(role_owners[role]) != 1:
            raise MachineError(f"role {role} must have exactly one owner")
        authority_field = f"{role.removesuffix('_authority')}_machine_id"
        if authorities.get(authority_field) != role_owners[role][0]:
            raise MachineError(f"authority map disagrees for {role}")
    return registry


def find_current_machine(registry: dict[str, Any], root: Path) -> dict[str, Any]:
    current_fingerprint = fingerprint_sha256(root)
    matches = [
        machine
        for machine in registry["machines"]
        if machine["fingerprint_sha256"] == current_fingerprint
    ]
    if len(matches) != 1:
        raise MachineError(
            "current physical machine is not uniquely enrolled in MACHINES.json"
        )
    return matches[0]


def verify_current(registry_path: Path, required_role: str | None) -> dict[str, Any]:
    registry = validate_registry(read_json(registry_path))
    root = repo_root()
    refresh_origin_master(root)
    machine = find_current_machine(registry, root)
    if required_role and required_role not in machine["roles"]:
        raise MachineError(
            f"machine {machine['machine_id']} lacks required role {required_role}"
        )

    enrolled_root_hmac = str(machine["repo_root_hmac_sha256"])
    current_root_hmac = repo_root_hmac_sha256(root)
    if not hmac.compare_digest(current_root_hmac, enrolled_root_hmac):
        raise MachineError(
            "repo path digest mismatch for enrolled machine "
            f"{machine['machine_id']}"
        )
    remote = canonical_remote(git(root, "config", "--get", "remote.origin.url"))
    if remote != machine["origin"]:
        raise MachineError(
            f"origin mismatch: registry={machine['origin']!r}, current={remote!r}"
        )
    head = git(root, "rev-parse", "HEAD")
    origin_master = git(root, "rev-parse", "origin/master")
    if head != origin_master:
        raise MachineError(
            f"authority verification requires HEAD == origin/master ({head} != {origin_master})"
        )
    return {
        "status": "PASS",
        "machine_id": machine["machine_id"],
        "fingerprint_sha256": machine["fingerprint_sha256"],
        "roles": machine["roles"],
        "repo_root": str(root),
        "head": head,
        "origin_master": origin_master,
    }


def cmd_probe(args: argparse.Namespace) -> int:
    probe = make_probe(args.machine_id, parse_roles(args.roles), args.service_port)
    text = json.dumps(probe, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        output = Path(args.output).expanduser().resolve()
        atomic_write_json(output, probe)
        print(f"PROBE_WRITTEN {output} sha256={sha256_file(output)}")
    else:
        sys.stdout.write(text)
    return 0


def cmd_build_registry(args: argparse.Namespace) -> int:
    output = Path(args.output).expanduser().resolve()
    if output.exists() and args.expected_sha256:
        actual = sha256_file(output)
        if actual != args.expected_sha256:
            raise MachineError(
                f"registry precondition failed: expected sha256 {args.expected_sha256}, got {actual}"
            )
    elif output.exists() and not args.expected_sha256:
        raise MachineError(
            "refusing to overwrite an existing registry without --expected-sha256"
        )
    probes = load_probes(Path(item).expanduser().resolve() for item in args.probe)
    registry = build_registry(probes, args.repo_machine, args.runtime_machine)
    validate_registry(registry)
    atomic_write_json(output, registry)
    print(f"REGISTRY_WRITTEN {output} sha256={sha256_file(output)}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    path = Path(args.registry).expanduser().resolve()
    registry = validate_registry(read_json(path))
    print(
        json.dumps(
            {
                "status": "PASS",
                "registry": str(path),
                "machines": len(registry["machines"]),
                "authorities": registry["authorities"],
                "sha256": sha256_file(path),
            },
            sort_keys=True,
        )
    )
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    if args.role and args.role not in VALID_ROLES:
        raise MachineError(f"unknown role: {args.role}")
    result = verify_current(Path(args.registry).expanduser().resolve(), args.role)
    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print(
            "MACHINE_GATE PASS "
            f"machine_id={result['machine_id']} roles={','.join(result['roles'])} "
            f"head={result['head']}"
        )
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    subparsers = root.add_subparsers(dest="command", required=True)

    probe = subparsers.add_parser("probe", help="create a redacted machine probe")
    probe.add_argument("--machine-id", required=True)
    probe.add_argument("--roles", default="repo_mirror")
    probe.add_argument("--service-port", type=int, default=3002)
    probe.add_argument("--output")
    probe.set_defaults(func=cmd_probe)

    build = subparsers.add_parser(
        "build-registry", help="merge at least two probes into MACHINES.json"
    )
    build.add_argument("--probe", action="append", required=True)
    build.add_argument("--repo-machine", required=True)
    build.add_argument("--runtime-machine", required=True)
    build.add_argument("--output", default=str(DEFAULT_REGISTRY))
    build.add_argument("--expected-sha256")
    build.set_defaults(func=cmd_build_registry)

    validate = subparsers.add_parser("validate", help="validate the registry")
    validate.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    validate.set_defaults(func=cmd_validate)

    verify = subparsers.add_parser(
        "verify", help="verify that this host is the enrolled authority"
    )
    verify.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    verify.add_argument("--role", choices=sorted(VALID_ROLES))
    verify.add_argument("--json", action="store_true")
    verify.set_defaults(func=cmd_verify)
    return root


def main() -> int:
    args = parser().parse_args()
    try:
        return int(args.func(args))
    except MachineError as exc:
        print(f"MACHINE_GATE FAIL {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
