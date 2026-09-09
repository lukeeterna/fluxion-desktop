#!/usr/bin/env python3
"""Deterministic, fail-closed checkpoint core for FLUXION PR #60."""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, re, sys
from pathlib import Path

REPOSITORY="lukeeterna/fluxion-desktop"
PR_NUMBER=60
ISSUE_NUMBER=68
TARGET_BRANCH="fix/sara-gate-shell-only"
TASK_ID="FX-CLOUD-PR60-CONTINUATION-001"
LABEL="fluxion:auto"
MARKER="<!-- fluxion-cloud-state:v1 -->"
HEX40=re.compile(r"^[0-9a-f]{40}$")

class Blocked(RuntimeError): pass

def load(path):
    value=json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value,(dict,list)): raise Blocked("JSON root invalid")
    return value

def labels(issue):
    return {x if isinstance(x,str) else x.get("name") for x in issue.get("labels",[])}

def validate_target(pr,issue,expected_head=None):
    if pr.get("number")!=PR_NUMBER or pr.get("state")!="open": raise Blocked("canonical PR is not open")
    head=pr.get("head") or {}; base=pr.get("base") or {}
    if head.get("ref")!=TARGET_BRANCH: raise Blocked("PR head branch mismatch")
    if (head.get("repo") or {}).get("full_name")!=REPOSITORY: raise Blocked("PR head repository mismatch")
    if base.get("ref")!="master" or (base.get("repo") or {}).get("full_name")!=REPOSITORY: raise Blocked("PR base is not canonical master")
    sha=head.get("sha")
    if not isinstance(sha,str) or not HEX40.fullmatch(sha): raise Blocked("PR head SHA malformed")
    if expected_head and sha!=expected_head: raise Blocked(f"stale PR head expected={expected_head} actual={sha}")
    if issue.get("number")!=ISSUE_NUMBER or issue.get("state")!="open": raise Blocked("canonical issue is not open")
    if issue.get("title")!=f"TASK {TASK_ID}" or LABEL not in labels(issue): raise Blocked("canonical issue identity mismatch")
    try: task=json.loads(issue.get("body",""))
    except Exception as exc: raise Blocked(f"canonical TASK JSON invalid: {exc}") from exc
    if task.get("task_id")!=TASK_ID or task.get("retry_limit")!=0: raise Blocked("canonical TASK policy mismatch")
    allowed=task.get("allowed_paths")
    if not isinstance(allowed,list) or not allowed: raise Blocked("allowed_paths missing")
    return sha,task

def parse_checkpoint(comment):
    body=comment.get("body","") if isinstance(comment,dict) else ""
    if MARKER not in body: return None
    try: state=json.loads(body.split(MARKER,1)[1].strip())
    except Exception: return None
    return state if state.get("task_id")==TASK_ID else None

def resume_allowed(comments,current_head,run_id,now=None):
    now=now or dt.datetime.now(dt.timezone.utc)
    found=[(c.get("created_at",""),parse_checkpoint(c)) for c in comments]
    found=[x for x in found if x[1] is not None]
    if not found: return "PROCEED"
    created,state=sorted(found,key=lambda x:x[0])[-1]
    if state.get("stop") is True or state.get("state")=="STOPPED": raise Blocked("STOP requested")
    lease=state.get("lease") or {}
    if state.get("state")=="ENGINEERING" and lease.get("owner") not in (None,run_id):
        acquired=dt.datetime.fromisoformat(created.replace("Z","+00:00"))
        if acquired+dt.timedelta(minutes=int(lease.get("ttl_minutes",95)))>now: raise Blocked("active lease")
    if state.get("candidate_sha")==current_head and state.get("state") in {"RED","BLOCKED"}:
        raise Blocked("BLOCKED_NO_PROGRESS unchanged candidate")
    if state.get("candidate_sha")==current_head and state.get("state")=="GREEN":
        raise Blocked("TASK already GREEN at exact head")
    return "PROCEED"

def validate_required_jobs(jobs,required):
    missing=[x for x in required if x not in jobs]
    bad={x:jobs.get(x) for x in required if jobs.get(x)!="success"}
    if missing or bad: raise Blocked(f"required jobs not GREEN missing={missing} bad={bad}")

def checkpoint(candidate,run_id,state,first_red,next_event,evidence=None):
    if not HEX40.fullmatch(candidate): raise Blocked("checkpoint candidate malformed")
    return {"schema_version":1,"task_id":TASK_ID,"issue_number":ISSUE_NUMBER,"pr_number":PR_NUMBER,
      "target_branch":TARGET_BRANCH,"candidate_sha":candidate,"run_id":str(run_id),"state":state,
      "first_red":first_red,"evidence":evidence or {},"lease":None,"stop":False,"next_event":next_event}

def main():
    p=argparse.ArgumentParser(); p.add_argument("--pr",required=True); p.add_argument("--issue",required=True)
    p.add_argument("--comments",required=True); p.add_argument("--expected-head"); p.add_argument("--run-id",required=True)
    p.add_argument("--out",required=True); a=p.parse_args()
    try:
        head,task=validate_target(load(a.pr),load(a.issue),a.expected_head)
        resume_allowed(load(a.comments),head,a.run_id)
        body=checkpoint(head,a.run_id,"BLOCKED","HOSTED_ENGINE_AUTH_RED",
          "CONTROL_PLANE_CHANGE_REQUIRED",{"canonical_task_sha256":hashlib.sha256((json.dumps(task,sort_keys=True)+"\n").encode()).hexdigest()})
        Path(a.out).write_text(MARKER+"\n"+json.dumps(body,sort_keys=True,separators=(",",":"))+"\n")
        print(f"CLOUD_PREFLIGHT=PASS head={head}")
        return 0
    except Blocked as exc:
        print(f"BLOCKED: {exc}",file=sys.stderr); return 2
if __name__=="__main__": raise SystemExit(main())
