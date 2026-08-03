#!/usr/bin/env python3
"""Esecutore reale VOS per piani SAFE_AUTO.

Esegue manifest JSON sigillati, senza shell, in un worktree isolato. Ogni passo
controlla STOP, timeout, path autorizzati e checkpoint. Le unità CONFIRM_FIRST
non vengono mai eseguite da questo programma.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import shutil
import sys
from pathlib import Path
from typing import Any

from vos_common import (
    NONCE_RE,
    UNIT_RE,
    VOSFailure,
    atomic_lock,
    atomic_write_json,
    check_stop,
    dirty_paths,
    git,
    git_dir,
    path_allowed,
    read_json,
    repo_root,
    run_interruptible,
    sha256_file,
    utc_now,
    validate_changed_paths,
)

PLAN_TITLE_RE = re.compile(r'^# Piano VOS — (\S+)$', re.M)
PLAN_HEAD_RE = re.compile(r'^HEAD al momento della pianificazione: ([0-9a-f]{7,40})$', re.M)
PLAN_COUNT_RE = re.compile(r'^Unità selezionate: (\d+)', re.M)
PLAN_SHA_RE = re.compile(r'^sha256: ([0-9a-f]{64})$', re.M)
PLAN_UNIT_RE = re.compile(r'^### \d+\. ([A-Z][A-Z0-9_-]{2,63})$', re.M)


def parse_plan(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding='utf-8')
    title = PLAN_TITLE_RE.search(text)
    head = PLAN_HEAD_RE.search(text)
    count = PLAN_COUNT_RE.search(text)
    declared = PLAN_SHA_RE.search(text)
    units = PLAN_UNIT_RE.findall(text)
    if not all((title, head, count, declared)):
        raise VOSFailure('piano non conforme al formato vos_plan.sh')
    expected_body = f"PIANO_{title.group(1)}_UNITS_{count.group(1)}_HEAD_{head.group(1)}"
    actual_sha = hashlib.sha256(expected_body.encode('utf-8')).hexdigest()
    if actual_sha != declared.group(1):
        raise VOSFailure(f"sha256 piano errato: atteso {declared.group(1)}, calcolato {actual_sha}")
    if len(units) != int(count.group(1)):
        raise VOSFailure('conteggio unità del piano incoerente')
    return {'timestamp': title.group(1), 'head': head.group(1), 'units': units, 'sha256': actual_sha}


def validate_manifest(root: Path, unit_id: str, plan_head: str) -> dict[str, Any]:
    if not UNIT_RE.fullmatch(unit_id):
        raise VOSFailure(f"unit_id non valido: {unit_id}")
    path = root / 'docs' / 'judge' / 'mandati' / f'{unit_id}.json'
    manifest = read_json(path)
    required = {
        'schema_version', 'unit_id', 'label', 'lane', 'risk', 'base_commit',
        'mandate_md', 'mandate_sha256', 'key', 'allowed_paths', 'steps'
    }
    missing = sorted(required - set(manifest))
    if missing:
        raise VOSFailure(f"manifest {unit_id} incompleto: {', '.join(missing)}")
    if manifest['schema_version'] != 1 or manifest['unit_id'] != unit_id:
        raise VOSFailure(f"manifest {unit_id} schema/id incoerente")
    if manifest['label'] != 'SAFE_AUTO':
        raise VOSFailure(f"{unit_id}: etichetta {manifest['label']} non SAFE_AUTO")
    if manifest['risk'] != 'A':
        raise VOSFailure(f"{unit_id}: solo rischio A è auto-eseguibile")
    if manifest['lane'] not in {'REPO', 'WEB', 'MACCHINA_READONLY'}:
        raise VOSFailure(f"{unit_id}: corsia non auto-eseguibile: {manifest['lane']}")
    current = git(root, 'rev-parse', 'HEAD')
    if not current.startswith(plan_head):
        raise VOSFailure(f"HEAD {current} non coincide con base del piano {plan_head}")
    base = str(manifest['base_commit'])
    if base.startswith('ancestor:'):
        ancestor = base.split(':', 1)[1]
        if not re.fullmatch(r'[0-9a-f]{7,40}', ancestor):
            raise VOSFailure(f"{unit_id}: base ancestor malformata: {base}")
        probe = run(['git', 'merge-base', '--is-ancestor', ancestor, current], cwd=root, check=False)
        if probe.returncode != 0:
            raise VOSFailure(f"{unit_id}: HEAD {current} non discende da {ancestor}")
    elif base != '*' and not current.startswith(base):
        raise VOSFailure(f"{unit_id}: base mandato {base} diversa da HEAD {current}")
    md_rel = str(manifest['mandate_md'])
    md_path = root / md_rel
    if sha256_file(md_path) != manifest['mandate_sha256']:
        raise VOSFailure(f"{unit_id}: hash del mandato Markdown non coincide")
    allowed = manifest['allowed_paths']
    if not isinstance(allowed, list) or not allowed or not all(isinstance(x, str) for x in allowed):
        raise VOSFailure(f"{unit_id}: allowed_paths non valido")
    for step in manifest['steps']:
        validate_step(step)
    return manifest


def validate_step(step: Any) -> None:
    if not isinstance(step, dict):
        raise VOSFailure('passo non oggetto')
    if set(step) - {'id', 'argv', 'cwd', 'timeout_seconds'}:
        raise VOSFailure(f"campi passo non ammessi: {sorted(set(step) - {'id','argv','cwd','timeout_seconds'})}")
    if not re.fullmatch(r'F[1-9][0-9]*', str(step.get('id', ''))):
        raise VOSFailure('id passo non valido')
    argv = step.get('argv')
    if not isinstance(argv, list) or not argv or not all(isinstance(x, str) and x for x in argv):
        raise VOSFailure('argv non valido')
    exe = argv[0]
    if exe == 'python3':
        if len(argv) < 2:
            raise VOSFailure('python3 senza target')
        if argv[1] == '-m':
            if len(argv) < 3 or argv[2] != 'unittest':
                raise VOSFailure('solo python3 -m unittest è ammesso')
        else:
            target = Path(argv[1])
            if target.is_absolute() or '..' in target.parts or not str(target).startswith(('bin/', 'tests/')):
                raise VOSFailure('script Python fuori da bin/ o tests/')
    elif exe in {'bash', 'sh'}:
        if len(argv) < 2:
            raise VOSFailure('shell senza script')
        target = Path(argv[1])
        if target.is_absolute() or '..' in target.parts or not str(target).startswith(('bin/', 'tests/')):
            raise VOSFailure('script shell fuori da bin/ o tests/')
    else:
        raise VOSFailure(f"eseguibile non ammesso: {exe}")
    cwd = Path(str(step.get('cwd', '.')))
    if cwd.is_absolute() or '..' in cwd.parts:
        raise VOSFailure('cwd non sicura')
    timeout = int(step.get('timeout_seconds', 300))
    if timeout < 1 or timeout > 3600:
        raise VOSFailure('timeout fuori intervallo 1..3600')


def make_checkpoint(root: Path, nonce: str, **fields: Any) -> None:
    data = {
        'schema_version': 1,
        'lease_nonce': nonce,
        'updated_at_utc': utc_now(),
        **fields,
    }
    path = git_dir(root) / 'vos-control' / 'checkpoints' / f'{nonce}.json'
    atomic_write_json(path, data, 0o600)


def execute_unit(root: Path, plan: dict[str, Any], unit_id: str, *, publish: bool, lease_nonce: str | None = None) -> dict[str, Any]:
    check_stop(root)
    manifest = validate_manifest(root, unit_id, plan['head'])
    nonce = lease_nonce or secrets.token_hex(16)
    if not NONCE_RE.fullmatch(nonce):
        raise VOSFailure('lease nonce non valido')
    gdir = git_dir(root)
    worktree = gdir / 'vos-control' / 'worktrees' / nonce
    log_dir = gdir / 'vos-control' / 'runs' / nonce
    branch = f"vos/unit/{unit_id.lower()}/{nonce[:12]}"
    make_checkpoint(root, nonce, unit_id=unit_id, phase='CLAIMED', sequence=1, checkpoint='pre-worktree')
    git(root, 'worktree', 'add', '--detach', str(worktree), 'HEAD')
    success = False
    try:
        initial = dirty_paths(worktree)
        if initial:
            raise VOSFailure(f"worktree isolato non pulito: {initial}")
        for index, step in enumerate(manifest['steps'], start=1):
            check_stop(root)
            step_id = step['id']
            make_checkpoint(root, nonce, unit_id=unit_id, phase='EXECUTING', sequence=index + 1,
                            checkpoint=f'before:{step_id}')
            command = list(step['argv'])
            cwd = (worktree / step.get('cwd', '.')).resolve()
            if worktree not in (cwd, *cwd.parents):
                raise VOSFailure(f"cwd fuori worktree: {cwd}")
            rc = run_interruptible(
                command,
                cwd=cwd,
                root=root,
                timeout=int(step.get('timeout_seconds', 300)),
                stdout_path=log_dir / f'{step_id}.stdout.log',
                stderr_path=log_dir / f'{step_id}.stderr.log',
            )
            if rc != 0:
                raise VOSFailure(f"{unit_id}/{step_id} terminato con codice {rc}")
            changed = dirty_paths(worktree)
            validate_changed_paths(changed, manifest['allowed_paths'])
            make_checkpoint(root, nonce, unit_id=unit_id, phase='EXECUTING', sequence=index + 1,
                            checkpoint=f'after:{step_id}', changed_paths=changed)

        changed = dirty_paths(worktree)
        validate_changed_paths(changed, manifest['allowed_paths'])
        result_rel = Path('vos/control/results') / f'{nonce}.json'
        result = {
            'schema_version': 1,
            'unit_id': unit_id,
            'lease_nonce': nonce,
            'key': manifest['key'],
            'mandate_sha256': manifest['mandate_sha256'],
            'base_commit': git(worktree, 'rev-parse', 'HEAD'),
            'status': 'PASS',
            'completed_at_utc': utc_now(),
            'changed_paths': sorted(changed),
            'log_sha256': {
                p.name: sha256_file(p) for p in sorted(log_dir.glob('*.log'))
            },
            'result_branch': branch,
        }
        atomic_write_json(worktree / result_rel, result)
        allowed_for_commit = list(manifest['allowed_paths']) + ['vos/control/results']
        validate_changed_paths(dirty_paths(worktree), allowed_for_commit)
        git(worktree, 'switch', '-c', branch)
        git(worktree, 'add', '--', *dirty_paths(worktree))
        git(worktree, 'commit', '-m', f"vos({unit_id}): result {nonce[:12]}\n\nVOS-Key: {manifest['key']}\nVOS-Mandate-SHA256: {manifest['mandate_sha256']}\nVOS-Lease: {nonce}")
        result_commit = git(worktree, 'rev-parse', 'HEAD')
        result['result_commit'] = result_commit
        atomic_write_json(log_dir / 'result.json', result, 0o600)
        if publish:
            git(worktree, 'push', '--porcelain', 'origin', f'HEAD:refs/heads/{branch}', timeout=120)
            result['published'] = True
        else:
            result['published'] = False
        make_checkpoint(root, nonce, unit_id=unit_id, phase='RESULT_READY', sequence=len(manifest['steps']) + 2,
                        checkpoint=f'result:{result_commit}', result_branch=branch)
        success = True
        return result
    except Exception as exc:
        make_checkpoint(root, nonce, unit_id=unit_id, phase='FAILED', sequence=999,
                        checkpoint='failed', error=str(exc))
        raise
    finally:
        try:
            git(root, 'worktree', 'remove', '--force', str(worktree), check=False)
        finally:
            if worktree.exists():
                shutil.rmtree(worktree, ignore_errors=True)
        if not success:
            git(root, 'branch', '-D', branch, check=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('plan')
    parser.add_argument('--no-publish', action='store_true', help='non eseguire git push del branch risultato')
    parser.add_argument('--unit', help='eseguire una sola unità già presente nel piano')
    parser.add_argument('--lease-nonce', help='nonce del lease esterno; richiede --unit')
    args = parser.parse_args()
    root = repo_root(Path(__file__).resolve().parent)
    plan_path = Path(args.plan)
    if not plan_path.is_absolute():
        plan_path = root / plan_path
    lock = git_dir(root) / 'vos-control' / 'apply.lock'
    try:
        with atomic_lock(lock):
            check_stop(root)
            if dirty_paths(root):
                raise VOSFailure('worktree principale sporco: il runner rifiuta di partire')
            plan = parse_plan(plan_path)
            selected = list(plan['units'])
            if args.unit:
                if args.unit not in selected:
                    raise VOSFailure(f'unità richiesta non presente nel piano: {args.unit}')
                selected = [args.unit]
            if args.lease_nonce and not args.unit:
                raise VOSFailure('--lease-nonce richiede --unit')
            results = []
            for unit_id in selected:
                results.append(execute_unit(
                    root,
                    plan,
                    unit_id,
                    publish=not args.no_publish,
                    lease_nonce=args.lease_nonce if args.unit else None,
                ))
            print(json.dumps({'status': 'PASS', 'results': results}, ensure_ascii=False, sort_keys=True))
            return 0
    except VOSFailure as exc:
        print(f'ERRORE VOS: {exc}', file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
