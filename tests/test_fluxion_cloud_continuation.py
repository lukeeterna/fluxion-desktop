import datetime as dt, importlib.util, json, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/".github/bootstrap/fluxion-cloud-continuation.py"
S=importlib.util.spec_from_file_location("cloud",P); M=importlib.util.module_from_spec(S); S.loader.exec_module(M)

def fixture():
    h="a"*40
    task={"task_id":M.TASK_ID,"retry_limit":0,"allowed_paths":["tests/test_fluxion_cloud_continuation.py"]}
    issue={"number":68,"state":"open","title":f"TASK {M.TASK_ID}","labels":[{"name":M.LABEL}],"body":json.dumps(task)}
    pr={"number":60,"state":"open","head":{"ref":M.TARGET_BRANCH,"sha":h,"repo":{"full_name":M.REPOSITORY}},
      "base":{"ref":"master","repo":{"full_name":M.REPOSITORY}}}
    return h,issue,pr

class Target(unittest.TestCase):
    def test_exact(self):
        h,i,p=fixture(); self.assertEqual(M.validate_target(p,i,h)[0],h)
    def test_stale(self):
        _,i,p=fixture()
        with self.assertRaisesRegex(M.Blocked,"stale"): M.validate_target(p,i,"b"*40)
    def test_master_writer_rejected(self):
        h,i,p=fixture(); p["head"]["ref"]="master"
        with self.assertRaisesRegex(M.Blocked,"branch"): M.validate_target(p,i,h)
    def test_fork_rejected(self):
        h,i,p=fixture(); p["head"]["repo"]["full_name"]="attacker/fork"
        with self.assertRaisesRegex(M.Blocked,"repository"): M.validate_target(p,i,h)
    def test_non_master_base_rejected(self):
        h,i,p=fixture(); p["base"]["ref"]="develop"
        with self.assertRaisesRegex(M.Blocked,"canonical master"): M.validate_target(p,i,h)

class Persistence(unittest.TestCase):
    def comment(self,state,head="a"*40,lease=None,stop=False):
        return {"created_at":"2026-09-09T00:00:00Z","body":M.MARKER+"\n"+json.dumps(
          {"task_id":M.TASK_ID,"state":state,"candidate_sha":head,"lease":lease,"stop":stop})}
    def test_no_progress(self):
        with self.assertRaisesRegex(M.Blocked,"NO_PROGRESS"):
            M.resume_allowed([self.comment("RED")],"a"*40,"new",dt.datetime(2026,9,9,0,1,tzinfo=dt.timezone.utc))
    def test_duplicate_lease(self):
        with self.assertRaisesRegex(M.Blocked,"active lease"):
            M.resume_allowed([self.comment("ENGINEERING",lease={"owner":"old","ttl_minutes":95})],"b"*40,"new",dt.datetime(2026,9,9,0,1,tzinfo=dt.timezone.utc))
    def test_stop(self):
        with self.assertRaisesRegex(M.Blocked,"STOP"): M.resume_allowed([self.comment("OPEN",stop=True)],"b"*40,"new")
    def test_expired_lease(self):
        self.assertEqual(M.resume_allowed([self.comment("ENGINEERING",lease={"owner":"old","ttl_minutes":1})],"b"*40,"new",dt.datetime(2026,9,9,0,2,tzinfo=dt.timezone.utc)),"PROCEED")
    def test_skipped_cancelled_missing_are_red(self):
        for jobs in ({"a":"success","b":"skipped"},{"a":"success","b":"cancelled"},{"a":"success"}):
            with self.assertRaises(M.Blocked): M.validate_required_jobs(jobs,["a","b"])

class Checkpoint(unittest.TestCase):
    def test_binds_run_and_candidate(self):
        c=M.checkpoint("a"*40,"77","RED","x","y",{"job_id":1})
        self.assertEqual((c["candidate_sha"],c["run_id"],c["evidence"]["job_id"]),("a"*40,"77",1))
if __name__=="__main__": unittest.main()
