#!/usr/bin/env python3
"""Primitive condivise del control plane FLUXION VOS.

Solo libreria standard. Nessun segreto viene serializzato nel repository.
"""
from __future__ import annotations

import contextlib
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any, Iterator

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
UNIT_RE = re.compile(r"^[A-Z][A-Z0-9_-]{2,63}$")
NONCE_RE = re.compile(r"^[0-9a-f]{32}$")

class VOSFailure(RuntimeError):
    pass


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def parse_utc(value: str) -> dt.datetime:
    parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n').encode('utf-8')


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except FileNotFoundError as exc:
        raise VOSFailure(f"file mancante: {path}") from exc
    except json.JSONDecodeError as exc:
        raise VOSFailure(f"JSON non valido: {path}: {exc}") from exc


def atomic_write_bytes(path: Path, data: bytes, mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f'.{path.name}.', dir=str(path.parent))
    tmp = Path(name)
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(tmp, mode)
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def atomic_write_json(path: Path, value: Any, mode: int = 0o644) -> None:
    atomic_write_bytes(path, canonical_json(value), mode)


def run(command: list[str], *, cwd: Path | None = None, check: bool = True,
        timeout: int | None = None, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        text=True,
        input=input_text,
        capture_output=True,
        timeout=timeout,
    )
    if check and completed.returncode != 0:
        raise VOSFailure(
            f"comando fallito ({completed.returncode}): {' '.join(command)}; "
            f"stderr={completed.stderr.strip()!r}"
        )
    return completed


def git(root: Path, *args: str, check: bool = True, timeout: int | None = None) -> str:
    return run(['git', *args], cwd=root, check=check, timeout=timeout).stdout.strip()


def repo_root(start: Path | None = None) -> Path:
    start = (start or Path.cwd()).resolve()
    return Path(run(['git', 'rev-parse', '--show-toplevel'], cwd=start).stdout.strip()).resolve()


def git_dir(root: Path) -> Path:
    raw = git(root, 'rev-parse', '--git-dir')
    path = Path(raw)
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def ensure_relative_path(value: str) -> Path:
    p = Path(value)
    if p.is_absolute() or '..' in p.parts or value in {'', '.'}:
        raise VOSFailure(f"path relativo non sicuro: {value!r}")
    return p


def check_stop(root: Path) -> None:
    local_stop = root / 'vos' / 'STOP'
    global_stop = root / 'vos' / 'control' / 'STOP.json'
    if local_stop.exists():
        raise VOSFailure(f"freno locale attivo: {local_stop}")
    if global_stop.exists():
        raise VOSFailure(f"freno globale attivo: {global_stop}")


def dirty_paths(root: Path) -> list[str]:
    output = git(root, 'status', '--porcelain=v1', '--untracked-files=all', '-z')
    if not output:
        return []
    paths: list[str] = []
    records = output.split('\0')
    i = 0
    while i < len(records):
        rec = records[i]
        if not rec:
            i += 1
            continue
        code = rec[:2]
        path = rec[3:]
        if code.startswith('R') or code.startswith('C'):
            i += 1
            if i < len(records):
                path = records[i]
        paths.append(path)
        i += 1
    return paths


def path_allowed(path: str, allowed: list[str]) -> bool:
    normalized = path.rstrip('/')
    for entry in allowed:
        base = entry.rstrip('/')
        if normalized == base or normalized.startswith(base + '/'):
            return True
    return False


def validate_changed_paths(paths: list[str], allowed: list[str]) -> None:
    bad = sorted(p for p in paths if not path_allowed(p, allowed))
    if bad:
        raise VOSFailure('path fuori mandato: ' + ', '.join(bad))


@contextlib.contextmanager
def atomic_lock(lock_dir: Path, *, stale_after_seconds: int = 3600) -> Iterator[None]:
    lock_dir.parent.mkdir(parents=True, exist_ok=True)
    try:
        lock_dir.mkdir()
    except FileExistsError:
        try:
            age = time.time() - lock_dir.stat().st_mtime
        except FileNotFoundError:
            age = 0
        if age > stale_after_seconds:
            shutil.rmtree(lock_dir, ignore_errors=True)
            lock_dir.mkdir()
        else:
            raise VOSFailure(f"lock già attivo: {lock_dir}")
    try:
        atomic_write_json(lock_dir / 'owner.json', {'pid': os.getpid(), 'created_at_utc': utc_now()}, 0o600)
        yield
    finally:
        shutil.rmtree(lock_dir, ignore_errors=True)


def run_interruptible(command: list[str], *, cwd: Path, root: Path, timeout: int,
                      stdout_path: Path, stderr_path: Path) -> int:
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    with stdout_path.open('w', encoding='utf-8') as out, stderr_path.open('w', encoding='utf-8') as err:
        proc = subprocess.Popen(
            command,
            cwd=str(cwd),
            text=True,
            stdout=out,
            stderr=err,
            start_new_session=True,
        )
        try:
            while True:
                rc = proc.poll()
                if rc is not None:
                    return rc
                if time.monotonic() - started > timeout:
                    os.killpg(proc.pid, signal.SIGTERM)
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        os.killpg(proc.pid, signal.SIGKILL)
                    raise VOSFailure(f"timeout dopo {timeout}s: {' '.join(command)}")
                try:
                    check_stop(root)
                except VOSFailure:
                    os.killpg(proc.pid, signal.SIGTERM)
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        os.killpg(proc.pid, signal.SIGKILL)
                    raise
                time.sleep(0.25)
        finally:
            if proc.poll() is None:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
