#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, re, subprocess, sys, tempfile
from pathlib import Path
from typing import Sequence
HEX40=re.compile(r"^[0-9a-f]{40}$")
HEX64=re.compile(r"^[0-9a-f]{64}$")
class Blocked(RuntimeError): pass
def run(repo: Path, argv: Sequence[str], check: bool=True):
    p=subprocess.run(list(argv),cwd=repo,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
    if check and p.returncode!=0: raise Blocked(f"command failed rc={p.returncode}: {' '.join(argv)}; stderr={p.stderr.strip()[:400]}")
    return p
def git(repo: Path,*args:str,check:bool=True)->str:
    return run(repo,("git",*args),check=check).stdout.strip()
def sha256_file(path: Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()
def require_hex(name,value,rx):
    if not rx.fullmatch(value): raise Blocked(f"{name} malformed")
    return value
def load_result(path,expected_sha,role,candidate):
    if sha256_file(path)!=expected_sha: raise Blocked(f"{role} result sha mismatch")
    try: d=json.loads(path.read_text(encoding="utf-8"))
    except Exception as e: raise Blocked(f"{role} result invalid json: {e}") from e
    if not isinstance(d,dict): raise Blocked(f"{role} result is not object")
    if d.get("status")!="PASS": raise Blocked(f"{role} status is not PASS")
    verdict=str(d.get("verdict") or d.get("summary") or "")
    if role=="verifier" and "GREEN" not in verdict.upper() and "VERDE" not in verdict.upper(): raise Blocked("fresh verifier is not GREEN")
    rc=str(d.get("result_commit") or d.get("candidate_sha") or "")
    if rc!=candidate: raise Blocked(f"{role} result_commit does not match candidate")
def validate_allowed_paths(repo,expected,candidate,allowed):
    if not allowed or not all(isinstance(x,str) and x for x in allowed): raise Blocked("allowed_paths invalid")
    for item in allowed:
        p=Path(item)
        if p.is_absolute() or ".." in p.parts or ".git" in p.parts: raise Blocked(f"unsafe allowed path: {item}")
    changed=[x for x in git(repo,"diff","--name-only",expected,candidate).splitlines() if x]
    if not changed: raise Blocked("candidate diff is empty")
    outside=sorted(set(changed)-set(allowed))
    if outside: raise Blocked("candidate changed forbidden paths: "+",".join(outside))
    return sorted(changed)
def fetch_master(repo):
    git(repo,"fetch","--no-tags","origin","refs/heads/master:refs/remotes/origin/master")
    cur=git(repo,"rev-parse","refs/remotes/origin/master")
    require_hex("CURRENT_ORIGIN_MASTER",cur,HEX40)
    return cur
def atomic_attestation(path,candidate,task_id,evidence_sha):
    import datetime
    path.parent.mkdir(parents=True,exist_ok=True)
    payload=(f"APPROVED_SHA={candidate}\nAPPROVED_TASK={task_id}\nEVIDENCE_SHA256={evidence_sha}\nAPPROVED_AT={datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')}\n")
    fd,tmp=tempfile.mkstemp(prefix=path.name+".",dir=str(path.parent))
    try:
        os.fchmod(fd,0o600)
        with os.fdopen(fd,"w",encoding="utf-8") as h:
            h.write(payload); h.flush(); os.fsync(h.fileno())
        os.replace(tmp,path)
    finally:
        try: os.unlink(tmp)
        except FileNotFoundError: pass
def main():
    ap=argparse.ArgumentParser()
    for name in ("repo","expected-base-sha","candidate-sha","task-id","allowed-paths-json","writer-result","writer-result-sha","verifier-result","verifier-result-sha","evidence","evidence-sha256","approval-file"):
        ap.add_argument("--"+name,required=True)
    a=ap.parse_args()
    try:
        repo=Path(a.repo).resolve()
        if not (repo/".git").exists(): raise Blocked("repo is not git working tree")
        expected=require_hex("EXPECTED_BASE_SHA",a.expected_base_sha,HEX40)
        candidate=require_hex("CANDIDATE_SHA",a.candidate_sha,HEX40)
        wsha=require_hex("WRITER_RESULT_SHA",a.writer_result_sha,HEX64)
        vsha=require_hex("VERIFIER_RESULT_SHA",a.verifier_result_sha,HEX64)
        esha=require_hex("EVIDENCE_SHA256",a.evidence_sha256,HEX64)
        if not a.task_id or len(a.task_id)>160: raise Blocked("TASK_ID invalid")
        try: allowed=json.loads(a.allowed_paths_json)
        except Exception as e: raise Blocked(f"ALLOWED_PATHS invalid json: {e}") from e
        if not isinstance(allowed,list): raise Blocked("ALLOWED_PATHS must be list")
        if fetch_master(repo)!=expected: raise Blocked("BLOCKED_ORIGIN_MOVED")
        parents=git(repo,"rev-list","--parents","-n","1",candidate).split()
        if len(parents)!=2: raise Blocked("candidate is merge commit or parent count != 1")
        if parents[1]!=expected: raise Blocked("candidate exact parent mismatch")
        validate_allowed_paths(repo,expected,candidate,allowed)
        ep=Path(a.evidence).resolve()
        if sha256_file(ep)!=esha: raise Blocked("evidence sha mismatch")
        load_result(Path(a.writer_result).resolve(),wsha,"writer",candidate)
        load_result(Path(a.verifier_result).resolve(),vsha,"verifier",candidate)
        if fetch_master(repo)!=expected: raise Blocked("BLOCKED_ORIGIN_MOVED")
        p=run(repo,("git","push","--porcelain","origin",f"{candidate}:refs/heads/master"),check=False)
        if p.returncode!=0: raise Blocked("BLOCKED_NON_FAST_FORWARD_OR_PUBLISH_FAILURE: "+p.stderr.strip()[:400])
        after=fetch_master(repo)
        if after!=candidate: raise Blocked("BLOCKED_POST_PUBLISH_MASTER_MISMATCH")
        atomic_attestation(Path(a.approval_file).resolve(),candidate,a.task_id,esha)
        print(f"APPROVED_SHA={candidate}"); print(f"APPROVED_TASK={a.task_id}"); print(f"EVIDENCE_SHA256={esha}"); print("TRUSTED_PUBLISH_GATE=PASS")
        return 0
    except Blocked as e:
        print(f"TRUSTED_PUBLISH_GATE=BLOCKED reason={e}",file=sys.stderr); return 2
if __name__=="__main__": raise SystemExit(main())
