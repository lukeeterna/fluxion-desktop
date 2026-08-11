#!/usr/bin/env python3
"""FLUXION trusted CAS publish gate.

Non-LLM root of trust for publishing reviewed candidates to origin/master.
It never force-pushes and never retries a compare-and-swap failure.

Trust boundary for result provenance:
- writer/verifier result JSON is produced by the trusted local runtime after the
  model process exits, not by the model itself;
- Claude writer has no Bash/Git/network/publisher capability and is confined to
  its isolated worktree, so it cannot invoke this gate or write these result files;
- this gate requires result files owned by the current trusted OS account and
  not group/world-writable, verifies their caller-supplied content SHA-256, binds
  both results to the exact candidate, and requires a fresh verifier marked
  independent with a distinct session bound to the writer session;
- the local runtime account is explicitly part of the TCB. This mechanism does
  not claim to defend against compromise of that same trusted OS account.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Sequence

HEX40=re.compile(r"^[0-9a-f]{40}$")
HEX64=re.compile(r"^[0-9a-f]{64}$")
class Blocked(RuntimeError): pass

def run(repo: Path, argv: Sequence[str], check: bool=True, env: dict[str,str] | None=None):
    p=subprocess.run(list(argv),cwd=repo,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False,env=env)
    if check and p.returncode!=0:
        raise Blocked(f"command failed rc={p.returncode}: {' '.join(argv)}; stderr={p.stderr.strip()[:400]}")
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

def validate_local_result_file(path:Path,role:str):
    if not path.is_file(): raise Blocked(f"{role} result is not a regular file")
    st=path.stat()
    if st.st_uid!=os.getuid(): raise Blocked(f"{role} result owner mismatch")
    if st.st_mode & 0o022: raise Blocked(f"{role} result is group/world writable")
    parent=path.parent.stat()
    if parent.st_uid!=os.getuid(): raise Blocked(f"{role} result directory owner mismatch")
    if parent.st_mode & 0o022: raise Blocked(f"{role} result directory is group/world writable")

def load_result(path: Path,expected_sha:str,role:str,candidate:str):
    validate_local_result_file(path,role)
    if sha256_file(path)!=expected_sha: raise Blocked(f"{role} result sha mismatch")
    try: d=json.loads(path.read_text(encoding="utf-8"))
    except Exception as e: raise Blocked(f"{role} result invalid json: {e}") from e
    if not isinstance(d,dict): raise Blocked(f"{role} result is not object")
    if d.get("status")!="PASS": raise Blocked(f"{role} status is not PASS")
    session=str(d.get("session_id") or "").strip()
    if not session or len(session)>200: raise Blocked(f"{role} session_id missing or invalid")
    if role=="verifier":
        if d.get("verdict") not in {"GREEN","VERDE"}: raise Blocked("fresh verifier is not GREEN")
        if d.get("independent") is not True: raise Blocked("fresh verifier is not marked independent")
        if d.get("profile")!="RUN_VERIFICATION": raise Blocked("fresh verifier profile mismatch")
    if str(d.get("result_commit") or d.get("candidate_sha") or "")!=candidate:
        raise Blocked(f"{role} result_commit does not match candidate")
    return d

def validate_allowed_paths(repo:Path,expected:str,candidate:str,allowed:list[str]):
    if not allowed or not all(isinstance(x,str) and x for x in allowed): raise Blocked("allowed_paths invalid")
    for item in allowed:
        p=Path(item)
        if p.is_absolute() or ".." in p.parts or ".git" in p.parts: raise Blocked(f"unsafe allowed path: {item}")
    changed=[x for x in git(repo,"diff","--name-only",expected,candidate).splitlines() if x]
    if not changed: raise Blocked("candidate diff is empty")
    outside=sorted(set(changed)-set(allowed))
    if outside: raise Blocked("candidate changed forbidden paths: "+",".join(outside))

def fetch_master(repo:Path)->str:
    git(repo,"fetch","--no-tags","origin","refs/heads/master:refs/remotes/origin/master")
    cur=git(repo,"rev-parse","refs/remotes/origin/master")
    require_hex("CURRENT_ORIGIN_MASTER",cur,HEX40)
    return cur

def atomic_attestation(path:Path,candidate:str,task_id:str,evidence_sha:str):
    import datetime
    path.parent.mkdir(parents=True,exist_ok=True)
    payload=(f"APPROVED_SHA={candidate}\nAPPROVED_TASK={task_id}\nEVIDENCE_SHA256={evidence_sha}\n"
             f"APPROVED_AT={datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')}\n")
    fd,tmp=tempfile.mkstemp(prefix=path.name+".",dir=str(path.parent))
    try:
        os.fchmod(fd,0o600)
        with os.fdopen(fd,"w",encoding="utf-8") as h:
            h.write(payload); h.flush(); os.fsync(h.fileno())
        os.replace(tmp,path)
    finally:
        try: os.unlink(tmp)
        except FileNotFoundError: pass

def load_attestation(path:Path)->tuple[str,str,str]:
    if not path.is_file(): raise Blocked("APPROVAL_FILE_MISSING")
    values={}
    for raw in path.read_text(encoding="utf-8").splitlines():
        key,sep,value=raw.partition("=")
        if sep and key: values[key]=value
    approved=require_hex("APPROVED_SHA",values.get("APPROVED_SHA",""),HEX40)
    evidence=require_hex("EVIDENCE_SHA256",values.get("EVIDENCE_SHA256",""),HEX64)
    task=values.get("APPROVED_TASK","")
    if not task or len(task)>160: raise Blocked("APPROVED_TASK invalid")
    return approved,task,evidence

def assert_approved(a)->int:
    try:
        repo=Path(a.repo).resolve()
        if not (repo/".git").exists(): raise Blocked("repo is not git working tree")
        approved,task,evidence=load_attestation(Path(a.approval_file).resolve())
        current=fetch_master(repo)
        if current!=approved: raise Blocked("UNATTESTED_MASTER")
        print(f"APPROVED_SHA={approved}")
        print(f"APPROVED_TASK={task}")
        print(f"EVIDENCE_SHA256={evidence}")
        print("APPROVED_MASTER=PASS")
        return 0
    except Blocked as e:
        print(f"APPROVED_MASTER=BLOCKED reason={e}",file=sys.stderr)
        return 2

def publish(a)->int:
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

        evidence=Path(a.evidence).resolve()
        if sha256_file(evidence)!=esha: raise Blocked("evidence sha mismatch")
        writer_path=Path(a.writer_result).resolve()
        verifier_path=Path(a.verifier_result).resolve()
        if writer_path==verifier_path: raise Blocked("writer/verifier result path collision")
        writer=load_result(writer_path,wsha,"writer",candidate)
        verifier=load_result(verifier_path,vsha,"verifier",candidate)
        if verifier.get("writer_session_id")!=writer.get("session_id"):
            raise Blocked("verifier is not bound to writer session")
        if verifier.get("session_id")==writer.get("session_id"):
            raise Blocked("verifier session is not fresh/distinct")

        if fetch_master(repo)!=expected: raise Blocked("BLOCKED_ORIGIN_MOVED")

        p=run(repo,("git","push","--porcelain","origin",f"{candidate}:refs/heads/master"),check=False)
        if p.returncode!=0:
            raise Blocked("BLOCKED_NON_FAST_FORWARD_OR_PUBLISH_FAILURE: "+p.stderr.strip()[:400])

        after=fetch_master(repo)
        if after!=candidate: raise Blocked("BLOCKED_POST_PUBLISH_MASTER_MISMATCH")

        atomic_attestation(Path(a.approval_file).resolve(),candidate,a.task_id,esha)
        print(f"APPROVED_SHA={candidate}")
        print(f"APPROVED_TASK={a.task_id}")
        print(f"EVIDENCE_SHA256={esha}")
        print("TRUSTED_PUBLISH_GATE=PASS")
        return 0
    except Blocked as e:
        print(f"TRUSTED_PUBLISH_GATE=BLOCKED reason={e}",file=sys.stderr)
        return 2

def _cmd(cwd:Path,*argv:str)->str:
    p=subprocess.run(argv,cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
    if p.returncode!=0: raise RuntimeError(f"self-test command failed: {argv}: {p.stderr}")
    return p.stdout.strip()

def _fixture(root:Path,name:str,change_path:str="allowed.txt",two_commits:bool=False):
    origin=root/f"{name}.git"; work=root/f"{name}-work"
    _cmd(root,"git","init","--bare",str(origin))
    _cmd(root,"git","clone",str(origin),str(work))
    _cmd(work,"git","config","user.name","FLUXION Canary")
    _cmd(work,"git","config","user.email","canary@invalid.example")
    (work/"allowed.txt").write_text("base\n",encoding="utf-8")
    _cmd(work,"git","add","allowed.txt"); _cmd(work,"git","commit","-m","base")
    base=_cmd(work,"git","rev-parse","HEAD")
    _cmd(work,"git","branch","-M","master"); _cmd(work,"git","push","origin","master")
    target=work/change_path
    target.write_text(target.read_text(encoding="utf-8")+"candidate\n" if target.exists() else "candidate\n",encoding="utf-8")
    _cmd(work,"git","add",change_path); _cmd(work,"git","commit","-m","candidate")
    if two_commits:
        (work/"allowed.txt").write_text((work/"allowed.txt").read_text()+"second\n",encoding="utf-8")
        _cmd(work,"git","add","allowed.txt"); _cmd(work,"git","commit","-m","second")
    candidate=_cmd(work,"git","rev-parse","HEAD")
    return origin,work,base,candidate

def _evidence(root:Path,candidate:str,prefix:str,verifier_independent:bool=True):
    writer=root/f"{prefix}-writer.json"; verifier=root/f"{prefix}-verifier.json"; evidence=root/f"{prefix}-evidence.bin"
    writer_session=f"writer-{prefix}"
    writer.write_text(json.dumps({"status":"PASS","result_commit":candidate,"verdict":"VERDE","session_id":writer_session},sort_keys=True)+"\n",encoding="utf-8")
    verifier.write_text(json.dumps({"status":"PASS","result_commit":candidate,"verdict":"GREEN","session_id":f"verifier-{prefix}","writer_session_id":writer_session,"independent":verifier_independent,"profile":"RUN_VERIFICATION"},sort_keys=True)+"\n",encoding="utf-8")
    evidence.write_bytes(b"content-addressed-evidence\n")
    writer.chmod(0o600); verifier.chmod(0o600); evidence.chmod(0o600)
    return writer,sha256_file(writer),verifier,sha256_file(verifier),evidence,sha256_file(evidence)

def _invoke(script:Path,work:Path,base:str,candidate:str,allowed:list[str],prefix:str,verifier_independent:bool=True):
    writer,wsha,verifier,vsha,evidence,esha=_evidence(work.parent,candidate,prefix,verifier_independent)
    approval=work.parent/f"{prefix}-APPROVED.txt"
    argv=[sys.executable,str(script),"--repo",str(work),"--expected-base-sha",base,"--candidate-sha",candidate,
          "--task-id",f"CANARY.{prefix}","--allowed-paths-json",json.dumps(allowed,separators=(",",":")),
          "--writer-result",str(writer),"--writer-result-sha",wsha,"--verifier-result",str(verifier),
          "--verifier-result-sha",vsha,"--evidence",str(evidence),"--evidence-sha256",esha,
          "--approval-file",str(approval)]
    p=subprocess.run(argv,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
    return p,approval

def _assert_invoke(script:Path,work:Path,approval:Path):
    return subprocess.run([sys.executable,str(script),"--assert-approved","--repo",str(work),"--approval-file",str(approval)],
                          text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)

def self_test()->int:
    script=Path(__file__).resolve()
    with tempfile.TemporaryDirectory(prefix="fluxion-publish-canary-") as td:
        root=Path(td)

        origin,work,base,candidate=_fixture(root,"positive")
        p,approval=_invoke(script,work,base,candidate,["allowed.txt"],"positive")
        assert p.returncode==0, p.stderr
        assert _cmd(work,"git","ls-remote","origin","refs/heads/master").split()[0]==candidate
        att=approval.read_text(encoding="utf-8")
        assert f"APPROVED_SHA={candidate}" in att
        ap=_assert_invoke(script,work,approval)
        assert ap.returncode==0, ap.stderr
        assert "APPROVED_MASTER=PASS" in ap.stdout
        print("TRUSTED_PUBLISHER_PRESENT=PASS")
        print("TRUSTED_PUBLISH_POSITIVE=PASS")

        origin,work,base,candidate=_fixture(root,"provenance")
        p,_=_invoke(script,work,base,candidate,["allowed.txt"],"provenance",verifier_independent=False)
        assert p.returncode==2
        assert _cmd(work,"git","ls-remote","origin","refs/heads/master").split()[0]==base
        print("VERIFIER_PROVENANCE_ENFORCED=PASS")

        other=root/"positive-unattested"; _cmd(root,"git","clone",str(origin),str(other))
        _cmd(other,"git","config","user.name","FLUXION Canary"); _cmd(other,"git","config","user.email","canary@invalid.example")
        # Use a separately attested positive fixture for unattested-master testing.
        origin_u,work_u,base_u,candidate_u=_fixture(root,"unattested-positive")
        p_u,approval_u=_invoke(script,work_u,base_u,candidate_u,["allowed.txt"],"unattested-positive")
        assert p_u.returncode==0, p_u.stderr
        other_u=root/"unattested-other"; _cmd(root,"git","clone",str(origin_u),str(other_u))
        _cmd(other_u,"git","config","user.name","FLUXION Canary"); _cmd(other_u,"git","config","user.email","canary@invalid.example")
        (other_u/"unattested.txt").write_text("unattested\n",encoding="utf-8")
        _cmd(other_u,"git","add","unattested.txt"); _cmd(other_u,"git","commit","-m","unattested master")
        unattested=_cmd(other_u,"git","rev-parse","HEAD")
        _cmd(other_u,"git","push","origin","master")
        approval_before=approval_u.read_bytes()
        ap=_assert_invoke(script,work_u,approval_u)
        assert ap.returncode==2
        assert "UNATTESTED_MASTER" in ap.stderr
        assert _cmd(work_u,"git","ls-remote","origin","refs/heads/master").split()[0]==unattested
        assert approval_u.read_bytes()==approval_before
        print("UNATTESTED_MASTER_BLOCKS=PASS")

        origin,work,base,candidate=_fixture(root,"wrongbase")
        p,_=_invoke(script,work,"0"*40,candidate,["allowed.txt"],"wrongbase")
        assert p.returncode==2
        assert _cmd(work,"git","ls-remote","origin","refs/heads/master").split()[0]==base
        print("EXPECTED_BASE_ENFORCED=PASS")

        origin,work,base,candidate=_fixture(root,"parent",two_commits=True)
        p,_=_invoke(script,work,base,candidate,["allowed.txt"],"parent")
        assert p.returncode==2
        assert _cmd(work,"git","ls-remote","origin","refs/heads/master").split()[0]==base
        print("CANDIDATE_EXACT_PARENT=PASS")

        origin,work,base,candidate=_fixture(root,"forbidden",change_path="forbidden.txt")
        p,_=_invoke(script,work,base,candidate,["allowed.txt"],"forbidden")
        assert p.returncode==2
        assert _cmd(work,"git","ls-remote","origin","refs/heads/master").split()[0]==base
        print("ALLOWED_PATHS_ENFORCED=PASS")

        origin,work,base,candidate=_fixture(root,"moved")
        other=root/"moved-other"; _cmd(root,"git","clone",str(origin),str(other))
        _cmd(other,"git","config","user.name","FLUXION Canary"); _cmd(other,"git","config","user.email","canary@invalid.example")
        (other/"other.txt").write_text("moved\n",encoding="utf-8")
        _cmd(other,"git","add","other.txt"); _cmd(other,"git","commit","-m","move origin"); moved=_cmd(other,"git","rev-parse","HEAD")
        _cmd(other,"git","push","origin","master")
        p,_=_invoke(script,work,base,candidate,["allowed.txt"],"moved")
        assert p.returncode==2
        assert _cmd(work,"git","ls-remote","origin","refs/heads/master").split()[0]==moved
        print("UNEXPECTED_ORIGIN_MOVE_BLOCKS=PASS")

        origin,work,base,candidate=_fixture(root,"race")
        sibling_work=root/"race-sibling"; _cmd(root,"git","clone",str(origin),str(sibling_work))
        _cmd(sibling_work,"git","config","user.name","FLUXION Canary"); _cmd(sibling_work,"git","config","user.email","canary@invalid.example")
        (sibling_work/"sibling.txt").write_text("sibling\n",encoding="utf-8")
        _cmd(sibling_work,"git","add","sibling.txt"); _cmd(sibling_work,"git","commit","-m","sibling")
        sibling=_cmd(sibling_work,"git","rev-parse","HEAD")
        _cmd(sibling_work,"git","push","origin",f"{sibling}:refs/heads/canary-sibling")
        hooks=work/".git"/"hooks"; hooks.mkdir(exist_ok=True)
        hook=hooks/"pre-push"
        hook.write_text(f"#!/bin/sh\ngit --git-dir='{origin}' update-ref refs/heads/master {sibling} {base}\nexit 0\n",encoding="utf-8")
        hook.chmod(0o700)
        p,_=_invoke(script,work,base,candidate,["allowed.txt"],"race")
        assert p.returncode==2
        assert _cmd(work,"git","ls-remote","origin","refs/heads/master").split()[0]==sibling
        print("NON_FORCE_PUBLISH=PASS")
        print("NON_FAST_FORWARD_BLOCKS=PASS")

        print("TRUSTED_PUBLISH_SELFTEST=PASS")
        return 0

def parser():
    ap=argparse.ArgumentParser()
    ap.add_argument("--self-test",action="store_true")
    ap.add_argument("--assert-approved",action="store_true")
    for name in ("repo","expected-base-sha","candidate-sha","task-id","allowed-paths-json","writer-result","writer-result-sha","verifier-result","verifier-result-sha","evidence","evidence-sha256","approval-file"):
        ap.add_argument("--"+name)
    return ap

def main():
    a=parser().parse_args()
    if a.self_test: return self_test()
    if a.assert_approved:
        if not a.repo or not a.approval_file:
            print("APPROVED_MASTER=BLOCKED reason=missing repo or approval-file",file=sys.stderr); return 2
        return assert_approved(a)
    missing=[k for k,v in vars(a).items() if k not in {"self_test","assert_approved"} and not v]
    if missing:
        print("TRUSTED_PUBLISH_GATE=BLOCKED reason=missing arguments: "+",".join(missing),file=sys.stderr); return 2
    return publish(a)

if __name__=="__main__": raise SystemExit(main())
