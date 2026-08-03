#!/usr/bin/env python3
"""Import atomico di un bundle di mandati approvati.

Un solo comando importa tutti i file; nessun overwrite è permesso, salvo byte
identici. Il bundle contiene payload base64 e SHA-256 per ogni file.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

from vos_common import VOSFailure, read_json, repo_root, sha256_bytes


def safe_rel(value: str) -> Path:
    p = Path(value)
    if p.is_absolute() or '..' in p.parts or not str(p).startswith('docs/judge/mandati/'):
        raise VOSFailure(f"destinazione bundle non ammessa: {value}")
    return p


def apply_bundle(root: Path, bundle_path: Path) -> dict[str, int]:
    bundle = read_json(bundle_path)
    if bundle.get('schema_version') != 1 or not isinstance(bundle.get('files'), list):
        raise VOSFailure('bundle non conforme')
    stage = Path(tempfile.mkdtemp(prefix='vos-mandates-', dir=str(root / '.git')))
    prepared: list[tuple[Path, Path, bool]] = []
    try:
        for entry in bundle['files']:
            rel = safe_rel(str(entry.get('path', '')))
            try:
                data = base64.b64decode(entry['base64'], validate=True)
            except Exception as exc:
                raise VOSFailure(f"base64 non valido per {rel}") from exc
            actual = sha256_bytes(data)
            if actual != entry.get('sha256'):
                raise VOSFailure(f"SHA-256 non coincide per {rel}")
            dest = root / rel
            same = dest.exists() and dest.is_file() and dest.read_bytes() == data
            if dest.exists() and not same:
                raise VOSFailure(f"overwrite rifiutato: {rel}")
            staged = stage / rel
            staged.parent.mkdir(parents=True, exist_ok=True)
            staged.write_bytes(data)
            prepared.append((staged, dest, same))
        created = 0
        identical = 0
        for staged, dest, same in prepared:
            if same:
                identical += 1
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            os.replace(staged, dest)
            created += 1
        return {'created': created, 'identical': identical}
    finally:
        shutil.rmtree(stage, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('bundle')
    args = parser.parse_args()
    try:
        root = repo_root(Path(__file__).resolve().parent)
        path = Path(args.bundle)
        if not path.is_absolute():
            path = root / path
        print(json.dumps(apply_bundle(root, path), sort_keys=True))
        return 0
    except VOSFailure as exc:
        print(f'ERRORE: {exc}', file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
