#!/usr/bin/env python3
"""FLUXION trusted CAS publisher.

Root of trust: deterministic checks performed by the trusted local runtime.
FRESH_REVIEW is recorded as model judgment only and is never itself proof.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, subprocess, sys, tempfile
from pathlib import Path
from typing import Sequence

HEX40=re.compile(r"^[0-9a-f]{40}$")
HEX64=re.compile(r"^[0-9a-f]{64}$")
class Blocked(RuntimeError): pass

DETERMINISTIC_REQUIRED={
    'DIFF_CHECK':'PASS',
    'EXPECTED_BASE_ENFORCED':'PASS',
    'CANDIDATE_EXACT_PARENT':'PASS',
    'ALLOWED_PATHS_ENFORCED':'PASS',
    'WRITER_CAPABILITY_BOUNDARY':'PASS',
    'WRITER_CAN_LAUNCH_REVIEW':'NO',
    'REVIEW_FRESH_SESSION':'PASS',
    'REVIEW_DOSSIER_PIN':'PASS',
    'REVIEW_NO_MUTATION':'PASS',
    'NO_INSTALL_PATH_IN_CANARY':'PASS',
}

def run(repo:Path, argv:Sequence[str], check:bool=True):
    p=subprocess.run(list(argv),cwd=repo,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
    if check and p.returncode!=0:
        raise Blocked(f"command failed rc={p.returncode}: {' '.join(argv)}; stderr={p.stderr.strip()[:400]}")
    return p

def git(repo:Path,*args:str,check:bool=True)->str:
    return run(repo,("git",*args),check=check).stdout.strip()

def sha256_file(p:Path)->str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for c in iter(lambda:f.read(1024*1024),b''): h.update(c)
    return h.hexdigest()

def require_hex(name:str,value:str,rx):
    if not rx.fullmatch(value): raise Blocked(f"{name} malformed")
    return value

def validate_local_file(path:Path,role:str):
    if not path.is_file(): raise Blocked(f"{role} is not regular file")
    st=path.stat(); parent=path.parent.stat()
    if st.st_uid!=os.getuid() or parent.st_uid!=os.getuid(): raise Blocked(f"{role} owner mismatch")
    if st.st_mode & 0o022 or parent.st_mode & 0o022: raise Blocked(f"{role} writable by group/world")

def load_json_file(path:Path,expected_sha:str,role:str):
    validate_local_file(path,role)
    if sha256_file(path)!=expected_sha: raise Blocked(f"{role} sha mismatch")
    try: d=json.loads(path.read_text(encoding='utf-8'))
    except Exception as e: raise Blocked(f"{role} invalid json: {e}") from e
    if not isinstance(d,dict): raise Blocked(f"{role} is not object")
    return d

def validate_allowed_paths(repo:Path,expected:str,candidate:str,allowed:list[str]):
    if not allowed or not all(isinstance(x,str) and x for x in allowed): raise Blocked('allowed_paths invalid')
    for x in allowed:
        p=Path(x)
        if p.is_absolute() or '..' in p.parts or '.git' in p.parts: raise Blocked(f'unsafe allowed path: {x}')
    changed=sorted(x for x in git(repo,'diff','--name-only',expected,candidate).splitlines() if x)
    if not changed: raise Blocked('candidate diff empty')
    outside=sorted(set(changed)-set(allowed))
    if outside: raise Blocked('candidate changed forbidden paths: '+','.join(outside))
    return changed

def fetch_master(repo:Path)->str:
    git(repo,'fetch','--no-tags','origin','refs/heads/master:refs/remotes/origin/master')
    return require_hex('CURRENT_ORIGIN_MASTER',git(repo,'rev-parse','refs/remotes/origin/master'),HEX40)

def validate_dossier(repo:Path,d:dict,task:str,expected:str,candidate:str,allowed:list[str],writer_sha:str):
    if d.get('schema_version')!=1 or d.get('kind')!='SEALED_REVIEW_DOSSIER': raise Blocked('dossier schema mismatch')
    if d.get('task_id')!=task or d.get('expected_base_sha')!=expected or d.get('candidate_sha')!=candidate: raise Blocked('dossier identity mismatch')
    if d.get('merge_base_sha')!=expected or git(repo,'merge-base',expected,candidate)!=expected: raise Blocked('dossier merge-base mismatch')
    if sorted(d.get('allowed_paths') or [])!=sorted(allowed): raise Blocked('dossier allowed_paths mismatch')
    changed=validate_allowed_paths(repo,expected,candidate,allowed)
    if sorted(d.get('changed_paths') or [])!=changed: raise Blocked('dossier changed_paths mismatch')
    actual=git(repo,'diff','--no-ext-diff','--no-color','--binary',expected,candidate)
    if d.get('diff') not in {actual,actual+'\n'}: raise Blocked('dossier diff mismatch')
    if d.get('writer_result_sha256')!=writer_sha: raise Blocked('dossier writer result sha mismatch')
    static=d.get('deterministic_results') or {}
    for k in ('DIFF_CHECK','EXPECTED_BASE_ENFORCED','CANDIDATE_EXACT_PARENT','ALLOWED_PATHS_ENFORCED','WRITER_CAPABILITY_BOUNDARY','WRITER_CAN_LAUNCH_REVIEW','NO_INSTALL_PATH_IN_CANARY'):
        if static.get(k)!=DETERMINISTIC_REQUIRED[k]: raise Blocked(f'dossier deterministic result mismatch: {k}')
    return changed

def atomic_attestation(path:Path,candidate:str,task:str,evidence_sha:str,dossier_sha:str,review_sha:str,review_verdict:str):
    import datetime
    path.parent.mkdir(parents=True,exist_ok=True)
    payload=(f"APPROVED_SHA={candidate}\nAPPROVED_TASK={task}\nEVIDENCE_SHA256={evidence_sha}\nDOSSIER_SHA256={dossier_sha}\n"
             f"FRESH_REVIEW_SHA256={review_sha}\nFRESH_REVIEW_VERDICT={review_verdict}\n"
             f"APPROVED_AT={datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')}\n")
    fd,tmp=tempfile.mkstemp(prefix=path.name+'.',dir=str(path.parent))
    try:
        os.fchmod(fd,0o600)
        with os.fdopen(fd,'w',encoding='utf-8') as h:
            h.write(payload); h.flush(); os.fsync(h.fileno())
        os.replace(tmp,path)
    finally:
        try: os.unlink(tmp)
        except FileNotFoundError: pass

def load_attestation(path:Path):
    if not path.is_file(): raise Blocked('APPROVAL_FILE_MISSING')
    vals={}
    for raw in path.read_text(encoding='utf-8').splitlines():
        k,s,v=raw.partition('=')
        if s and k: vals[k]=v
    return require_hex('APPROVED_SHA',vals.get('APPROVED_SHA',''),HEX40),vals.get('APPROVED_TASK',''),require_hex('EVIDENCE_SHA256',vals.get('EVIDENCE_SHA256',''),HEX64)

def assert_approved(a)->int:
    try:
        repo=Path(a.repo).resolve(); approved,task,evidence=load_attestation(Path(a.approval_file).resolve())
        if fetch_master(repo)!=approved: raise Blocked('UNATTESTED_MASTER')
        print(f'APPROVED_SHA={approved}'); print(f'APPROVED_TASK={task}'); print(f'EVIDENCE_SHA256={evidence}'); print('APPROVED_MASTER=PASS'); return 0
    except Blocked as e:
        print(f'APPROVED_MASTER=BLOCKED reason={e}',file=sys.stderr); return 2

def publish(a)->int:
    try:
        repo=Path(a.repo).resolve()
        if not (repo/'.git').exists(): raise Blocked('repo is not git working tree')
        expected=require_hex('EXPECTED_BASE_SHA',a.expected_base_sha,HEX40)
        candidate=require_hex('CANDIDATE_SHA',a.candidate_sha,HEX40)
        wsha=require_hex('WRITER_RESULT_SHA',a.writer_result_sha,HEX64)
        rsha=require_hex('FRESH_REVIEW_SHA',a.fresh_review_sha,HEX64)
        dsha=require_hex('DOSSIER_SHA256',a.dossier_sha256,HEX64)
        esha=require_hex('EVIDENCE_SHA256',a.evidence_sha256,HEX64)
        if not a.task_id or len(a.task_id)>160: raise Blocked('TASK_ID invalid')
        try: allowed=json.loads(a.allowed_paths_json)
        except Exception as e: raise Blocked(f'ALLOWED_PATHS invalid json: {e}') from e
        if not isinstance(allowed,list): raise Blocked('ALLOWED_PATHS must be list')

        if fetch_master(repo)!=expected: raise Blocked('BLOCKED_ORIGIN_MOVED')
        parents=git(repo,'rev-list','--parents','-n','1',candidate).split()
        if len(parents)!=2 or parents[1]!=expected: raise Blocked('candidate exact parent mismatch')

        writer=load_json_file(Path(a.writer_result).resolve(),wsha,'writer result')
        if writer.get('status')!='PASS' or writer.get('result_commit')!=candidate: raise Blocked('writer result mismatch')
        writer_session=str(writer.get('session_id') or '')
        if not writer_session: raise Blocked('writer session missing')
        if writer.get('bash') is not False or writer.get('network') is not False or writer.get('publisher') is not False: raise Blocked('writer capability boundary mismatch')

        dossier=load_json_file(Path(a.dossier).resolve(),dsha,'dossier')
        validate_dossier(repo,dossier,a.task_id,expected,candidate,allowed,wsha)

        review=load_json_file(Path(a.fresh_review).resolve(),rsha,'fresh review')
        if review.get('kind')!='FRESH_REVIEW' or review.get('profile')!='FRESH_REVIEW': raise Blocked('fresh review profile mismatch')
        verdict=review.get('verdict')
        if verdict not in {'GREEN','RED','BLOCKED'}: raise Blocked('fresh review verdict invalid')
        if review.get('independent') is not True: raise Blocked('fresh review provenance mismatch')
        if review.get('result_commit')!=candidate or review.get('writer_session_id')!=writer_session: raise Blocked('fresh review candidate/writer binding mismatch')
        if review.get('session_id')==writer_session or not review.get('session_id'): raise Blocked('fresh review session not fresh/distinct')
        if review.get('dossier_sha256')!=dsha: raise Blocked('fresh review dossier pin mismatch')
        if review.get('tools_used') not in ([],None): raise Blocked('fresh review used tools')

        evidence=load_json_file(Path(a.evidence).resolve(),esha,'evidence')
        if evidence.get('task_id')!=a.task_id or evidence.get('expected_base_sha')!=expected or evidence.get('candidate_sha')!=candidate: raise Blocked('evidence identity mismatch')
        if evidence.get('writer_result_sha256')!=wsha or evidence.get('fresh_review_sha256')!=rsha or evidence.get('dossier_sha256')!=dsha: raise Blocked('evidence hash binding mismatch')
        proofs=evidence.get('deterministic_proofs') or {}
        for k,v in DETERMINISTIC_REQUIRED.items():
            if proofs.get(k)!=v: raise Blocked(f'deterministic proof missing/failed: {k}')
        judgment=evidence.get('model_judgment') or {}
        if judgment.get('kind')!='FRESH_REVIEW' or judgment.get('verdict')!=verdict or judgment.get('sha256')!=rsha:
            raise Blocked('model judgment evidence mismatch')

        # E2: model judgment is not root of trust. Deterministic proofs authorize;
        # FRESH_REVIEW can veto only when it is RED.
        if verdict=='RED': raise Blocked('FRESH_REVIEW_RED')

        if fetch_master(repo)!=expected: raise Blocked('BLOCKED_ORIGIN_MOVED')
        p=run(repo,('git','push','--porcelain','origin',f'{candidate}:refs/heads/master'),check=False)
        if p.returncode!=0: raise Blocked('BLOCKED_NON_FAST_FORWARD_OR_PUBLISH_FAILURE: '+p.stderr.strip()[:400])
        if fetch_master(repo)!=candidate: raise Blocked('BLOCKED_POST_PUBLISH_MASTER_MISMATCH')
        atomic_attestation(Path(a.approval_file).resolve(),candidate,a.task_id,esha,dsha,rsha,verdict)
        print(f'APPROVED_SHA={candidate}')
        print('DETERMINISTIC_PROOFS=PASS')
        print(f'FRESH_REVIEW={verdict}')
        print(f'FRESH_REVIEW_SHA256={rsha}')
        print(f'DOSSIER_SHA256={dsha}')
        print(f'EVIDENCE_SHA256={esha}')
        print('TRUSTED_PUBLISH_GATE=PASS')
        return 0
    except Blocked as e:
        print(f'TRUSTED_PUBLISH_GATE=BLOCKED reason={e}',file=sys.stderr); return 2

# deterministic self-test
def cmd(cwd:Path,*argv:str)->str:
    p=subprocess.run(argv,cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False)
    if p.returncode!=0: raise RuntimeError(f'cmd failed {argv}: {p.stderr}')
    return p.stdout.strip()

def fixture(root:Path,name:str,change='allowed.txt',two=False):
    origin=root/f'{name}.git'; work=root/f'{name}-work'
    cmd(root,'git','init','--bare',str(origin)); cmd(root,'git','clone',str(origin),str(work))
    cmd(work,'git','config','user.name','FLUXION Canary'); cmd(work,'git','config','user.email','canary@invalid.example')
    (work/'allowed.txt').write_text('base\n'); cmd(work,'git','add','allowed.txt'); cmd(work,'git','commit','-m','base')
    base=cmd(work,'git','rev-parse','HEAD'); cmd(work,'git','branch','-M','master'); cmd(work,'git','push','origin','master')
    p=work/change; p.write_text((p.read_text() if p.exists() else '')+'candidate\n'); cmd(work,'git','add',change); cmd(work,'git','commit','-m','candidate')
    if two:
        (work/'allowed.txt').write_text((work/'allowed.txt').read_text()+'second\n'); cmd(work,'git','add','allowed.txt'); cmd(work,'git','commit','-m','second')
    return origin,work,base,cmd(work,'git','rev-parse','HEAD')

def evidence_files(root:Path,work:Path,task:str,base:str,candidate:str,allowed:list[str],prefix:str,verdict='GREEN',bad_dossier=False,independent=True):
    writer=root/f'{prefix}-writer.json'; ws=f'writer-{prefix}'
    writer.write_text(json.dumps({'status':'PASS','result_commit':candidate,'session_id':ws,'bash':False,'network':False,'publisher':False},sort_keys=True)+'\n'); writer.chmod(0o600); wsha=sha256_file(writer)
    changed=cmd(work,'git','diff','--name-only',base,candidate).splitlines(); diff=cmd(work,'git','diff','--no-ext-diff','--no-color','--binary',base,candidate)
    det={'DIFF_CHECK':'PASS','EXPECTED_BASE_ENFORCED':'PASS','CANDIDATE_EXACT_PARENT':'PASS','ALLOWED_PATHS_ENFORCED':'PASS','WRITER_CAPABILITY_BOUNDARY':'PASS','WRITER_CAN_LAUNCH_REVIEW':'NO','NO_INSTALL_PATH_IN_CANARY':'PASS'}
    dossier=root/f'{prefix}-dossier.json'; d={'schema_version':1,'kind':'SEALED_REVIEW_DOSSIER','task_id':task,'expected_base_sha':base,'candidate_sha':candidate,'merge_base_sha':base,'allowed_paths':sorted(allowed),'changed_paths':sorted(changed),'diff':diff,'deterministic_results':det,'writer_result_sha256':wsha,'writer_session_id':ws}
    dossier.write_text(json.dumps(d,sort_keys=True,separators=(',',':'))+'\n'); dossier.chmod(0o600); dsha=sha256_file(dossier)
    review=root/f'{prefix}-review.json'; review.write_text(json.dumps({'kind':'FRESH_REVIEW','profile':'FRESH_REVIEW','verdict':verdict,'independent':independent,'result_commit':candidate,'session_id':f'review-{prefix}','writer_session_id':ws,'dossier_sha256':('0'*64 if bad_dossier else dsha),'tools_used':[]},sort_keys=True)+'\n'); review.chmod(0o600); rsha=sha256_file(review)
    proofs=dict(DETERMINISTIC_REQUIRED)
    ev=root/f'{prefix}-evidence.json'; ev.write_text(json.dumps({'task_id':task,'expected_base_sha':base,'candidate_sha':candidate,'writer_result_sha256':wsha,'fresh_review_sha256':rsha,'dossier_sha256':dsha,'deterministic_proofs':proofs,'model_judgment':{'kind':'FRESH_REVIEW','verdict':verdict,'sha256':rsha}},sort_keys=True)+'\n'); ev.chmod(0o600); esha=sha256_file(ev)
    return writer,wsha,review,rsha,dossier,dsha,ev,esha

def invoke(script:Path,work:Path,base:str,candidate:str,allowed:list[str],prefix:str,expected_override:str|None=None,**kw):
    task=f'CANARY.{prefix}'; w,wsha,r,rsha,d,dsha,e,esha=evidence_files(work.parent,work,task,base,candidate,allowed,prefix,**kw); approval=work.parent/f'{prefix}-APPROVED.txt'; expected=expected_override or base
    argv=[sys.executable,str(script),'--repo',str(work),'--expected-base-sha',expected,'--candidate-sha',candidate,'--task-id',task,'--allowed-paths-json',json.dumps(allowed,separators=(',',':')),'--writer-result',str(w),'--writer-result-sha',wsha,'--fresh-review',str(r),'--fresh-review-sha',rsha,'--dossier',str(d),'--dossier-sha256',dsha,'--evidence',str(e),'--evidence-sha256',esha,'--approval-file',str(approval)]
    return subprocess.run(argv,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False),approval

def self_test()->int:
    script=Path(__file__).resolve()
    with tempfile.TemporaryDirectory(prefix='fluxion-publish-canary-') as td:
        root=Path(td)
        origin,work,base,cand=fixture(root,'positive'); p,approval=invoke(script,work,base,cand,['allowed.txt'],'positive'); assert p.returncode==0,p.stderr; print('TRUSTED_PUBLISHER_PRESENT=PASS'); print('TRUSTED_PUBLISH_POSITIVE=PASS')
        ap=subprocess.run([sys.executable,str(script),'--assert-approved','--repo',str(work),'--approval-file',str(approval)],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE); assert ap.returncode==0
        approval_before=approval.read_bytes(); other=root/'unattested'; cmd(root,'git','clone',str(origin),str(other)); cmd(other,'git','config','user.name','Canary'); cmd(other,'git','config','user.email','c@invalid'); (other/'x').write_text('x'); cmd(other,'git','add','x'); cmd(other,'git','commit','-m','move'); moved=cmd(other,'git','rev-parse','HEAD'); cmd(other,'git','push','origin','master'); ap2=subprocess.run([sys.executable,str(script),'--assert-approved','--repo',str(work),'--approval-file',str(approval)],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE); assert ap2.returncode==2 and 'UNATTESTED_MASTER' in ap2.stderr and approval.read_bytes()==approval_before; print('UNATTESTED_MASTER_BLOCKS=PASS')
        origin,work,base,cand=fixture(root,'dossier'); p,_=invoke(script,work,base,cand,['allowed.txt'],'dossier',bad_dossier=True); assert p.returncode==2; print('REVIEW_DOSSIER_PIN_ENFORCED=PASS')
        origin,work,base,cand=fixture(root,'red'); p,_=invoke(script,work,base,cand,['allowed.txt'],'red',verdict='RED'); assert p.returncode==2 and 'FRESH_REVIEW_RED' in p.stderr; print('FRESH_REVIEW_RED_BLOCKS=PASS')
        origin,work,base,cand=fixture(root,'blocked'); p,_=invoke(script,work,base,cand,['allowed.txt'],'blocked',verdict='BLOCKED'); assert p.returncode==0,p.stderr; print('FRESH_REVIEW_NON_RED_NOT_ROOT_OF_TRUST=PASS')
        origin,work,base,cand=fixture(root,'wrongbase'); p,_=invoke(script,work,base,cand,['allowed.txt'],'wrongbase',expected_override='0'*40); assert p.returncode==2; print('EXPECTED_BASE_ENFORCED=PASS')
        origin,work,base,cand=fixture(root,'parent',two=True); p,_=invoke(script,work,base,cand,['allowed.txt'],'parent'); assert p.returncode==2; print('CANDIDATE_EXACT_PARENT=PASS')
        origin,work,base,cand=fixture(root,'forbidden','forbidden.txt'); p,_=invoke(script,work,base,cand,['allowed.txt'],'forbidden'); assert p.returncode==2; print('ALLOWED_PATHS_ENFORCED=PASS')
        origin,work,base,cand=fixture(root,'moved'); other=root/'moved-other'; cmd(root,'git','clone',str(origin),str(other)); cmd(other,'git','config','user.name','Canary'); cmd(other,'git','config','user.email','c@invalid'); (other/'x').write_text('x'); cmd(other,'git','add','x'); cmd(other,'git','commit','-m','move'); moved=cmd(other,'git','rev-parse','HEAD'); cmd(other,'git','push','origin','master'); p,_=invoke(script,work,base,cand,['allowed.txt'],'moved'); assert p.returncode==2; print('UNEXPECTED_ORIGIN_MOVE_BLOCKS=PASS')
        origin,work,base,cand=fixture(root,'race'); sib=root/'race-sib'; cmd(root,'git','clone',str(origin),str(sib)); cmd(sib,'git','config','user.name','Canary'); cmd(sib,'git','config','user.email','c@invalid'); (sib/'x').write_text('x'); cmd(sib,'git','add','x'); cmd(sib,'git','commit','-m','sibling'); s=cmd(sib,'git','rev-parse','HEAD'); cmd(sib,'git','push','origin',f'{s}:refs/heads/sibling'); hooks=work/'.git'/'hooks'; hooks.mkdir(exist_ok=True); h=hooks/'pre-push'; h.write_text(f"#!/bin/sh\ngit --git-dir='{origin}' update-ref refs/heads/master {s} {base}\nexit 0\n"); h.chmod(0o700); p,_=invoke(script,work,base,cand,['allowed.txt'],'race'); assert p.returncode==2; print('NON_FORCE_PUBLISH=PASS'); print('NON_FAST_FORWARD_BLOCKS=PASS')
        print('TRUSTED_PUBLISH_SELFTEST=PASS'); return 0

def parser():
    ap=argparse.ArgumentParser(); ap.add_argument('--self-test',action='store_true'); ap.add_argument('--assert-approved',action='store_true')
    for n in ('repo','expected-base-sha','candidate-sha','task-id','allowed-paths-json','writer-result','writer-result-sha','fresh-review','fresh-review-sha','dossier','dossier-sha256','evidence','evidence-sha256','approval-file'): ap.add_argument('--'+n)
    return ap

def main():
    a=parser().parse_args()
    if a.self_test: return self_test()
    if a.assert_approved:
        if not a.repo or not a.approval_file: print('APPROVED_MASTER=BLOCKED reason=missing args',file=sys.stderr); return 2
        return assert_approved(a)
    missing=[k for k,v in vars(a).items() if k not in {'self_test','assert_approved'} and not v]
    if missing: print('TRUSTED_PUBLISH_GATE=BLOCKED reason=missing arguments: '+','.join(missing),file=sys.stderr); return 2
    return publish(a)

if __name__=='__main__': raise SystemExit(main())
