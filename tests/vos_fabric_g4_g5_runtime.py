#!/usr/bin/env python3
"""VOS Fabric G4/G5 real multi-worker runtime certification harness.

G4 routes a fixed PUBLIC objective from VOS through the deterministic certified
worker registry. Codex is skipped only because VOS has exact provider-capacity
evidence and its breaker is OPEN; A2 Antigravity is therefore selected as the
DIRECT_OFFICIAL PUBLIC-only worker.

G5 is a distinct process invocation. It reloads the durable checkpoint, proves
exactly-once effect semantics, creates a new A2 continuation from the checkpoint
boundary, completes VOS rollover, then exactly resumes that new continuation.
No founder prompt is passed between stages.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, Mapping, Tuple


MANDATE_ID = "T-VOS-FABRIC-G4-G5"
G3_CERTIFIED_SHA = "1f16ab2505480adab67b20411cf0b5819179a2b2"
FABRIC_CERTIFICATION_SHA = "aadd263f62fd7bd8d349d54d4e9ed5f82107b7c9"
DATA_CLASS = "PUBLIC"
DATA_POLICY = "PUBLIC_ONLY"
EFFECT_ID = "g5-isolated-certification-write-once"
A2_AGY_BIN = "/home/ubuntu/.local/bin/agy"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def canonical_json_sha256(value: Mapping[str, Any]) -> str:
    payload = json.dumps(dict(value), sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(payload)


def read_json(path: Path) -> Dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise RuntimeError("%s must contain a JSON object" % path)
    return raw


def write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(dict(value), sort_keys=True, indent=2) + "\n", encoding="utf-8")


def load_fabric(fabric_dir: Path):
    sys.path.insert(0, str(fabric_dir))
    import bridge  # type: ignore
    import checkpoint  # type: ignore
    import rollover  # type: ignore
    import router  # type: ignore
    import worker_adapter  # type: ignore
    import worker_registry  # type: ignore
    return bridge, checkpoint, rollover, router, worker_adapter, worker_registry


def validate_mandate(md_path: Path, json_path: Path) -> Dict[str, Any]:
    manifest = read_json(json_path)
    required = {
        "schema_version", "unit_id", "label", "risk", "lane",
        "base_certified_g3_sha", "mandate_md", "mandate_sha256", "key",
        "founder_go", "authorization_class", "max_cost_usd",
        "paid_api_fallback", "quota_circumvention", "production_mutation",
        "isolated_effect_scope", "gates",
    }
    if set(manifest) != required:
        raise RuntimeError("mandate manifest fields are not exact")
    if manifest["schema_version"] != 1 or manifest["unit_id"] != MANDATE_ID:
        raise RuntimeError("mandate schema/id mismatch")
    if manifest["label"] != "CONFIRM_FIRST" or manifest["risk"] != "B":
        raise RuntimeError("runtime mandate must remain CONFIRM_FIRST risk B")
    if manifest["base_certified_g3_sha"] != G3_CERTIFIED_SHA:
        raise RuntimeError("mandate not bound to certified G3 SHA")
    if manifest["founder_go"] is not True:
        raise RuntimeError("founder GO missing")
    if manifest["authorization_class"] != "FOUNDER_CONFIRMED_RUNTIME_CERTIFICATION":
        raise RuntimeError("authorization class mismatch")
    if manifest["max_cost_usd"] != 0:
        raise RuntimeError("nonzero cost forbidden")
    if manifest["paid_api_fallback"] is not False:
        raise RuntimeError("paid API fallback must be false")
    if manifest["quota_circumvention"] is not False:
        raise RuntimeError("quota circumvention must be false")
    if manifest["production_mutation"] is not False:
        raise RuntimeError("production mutation must be false")
    if manifest["isolated_effect_scope"] != "vos-worker-temporary":
        raise RuntimeError("effect scope mismatch")
    if manifest["gates"] != ["G4", "G5"]:
        raise RuntimeError("gate scope mismatch")
    actual = sha256_bytes(md_path.read_bytes())
    if actual != manifest["mandate_sha256"]:
        raise RuntimeError("mandate Markdown SHA-256 mismatch")
    return manifest


def select_a2(worker_registry):
    routed = worker_registry.route_public_request()
    decision = routed["decision"]
    capacity = routed["capacity"]
    worker = decision.get("worker")
    if not isinstance(worker, Mapping):
        raise RuntimeError("router returned no selected worker")
    if worker.get("worker_id") != worker_registry.A2_WORKER_ID:
        raise RuntimeError("canonical route did not select A2")
    if worker.get("kind") != "DIRECT_OFFICIAL":
        raise RuntimeError("A2 must remain DIRECT_OFFICIAL")
    if worker.get("data_classes") != [DATA_CLASS] or worker.get("data_policy") != DATA_POLICY:
        raise RuntimeError("A2 must remain PUBLIC_ONLY")
    if worker.get("qualification_ref") != worker_registry.A2_QUALIFICATION_REF:
        raise RuntimeError("A2 exact qualification ref drift")
    if worker.get("max_cost_usd") != 0 or worker.get("zero_cost_hard_stop") is not True:
        raise RuntimeError("A2 zero-cost hard stop drift")
    if worker.get("consumer_oauth_proxy") is not False:
        raise RuntimeError("unofficial OAuth proxy is forbidden")
    codex_breaker = capacity["breakers"].get(worker_registry.CODEX_WORKER_ID)
    if not isinstance(codex_breaker, Mapping) or codex_breaker.get("state") != "OPEN":
        raise RuntimeError("Codex breaker is not truthfully OPEN")
    if (
        capacity["evidence"].get(worker_registry.CODEX_WORKER_ID)
        != worker_registry.CODEX_CAPACITY_EVIDENCE_REF
    ):
        raise RuntimeError("Codex OPEN breaker lost exact provider-capacity evidence")
    return dict(worker), routed, canonical_json_sha256(routed)


def explicit_worker_env(proxy_url: str) -> Dict[str, str]:
    return {
        "HOME": "/home/ubuntu",
        "USER": "ubuntu",
        "LOGNAME": "ubuntu",
        "PATH": "/home/ubuntu/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
        "HTTPS_PROXY": proxy_url,
        "HTTP_PROXY": proxy_url,
        "https_proxy": proxy_url,
        "http_proxy": proxy_url,
        "LC_ALL": "C",
        "LANG": "C",
    }


def make_worker_spec(
    runtime_dir: Path,
    live_worker: Path,
    selected_worker: Mapping[str, Any],
    *,
    mode: str,
    prefix: str,
    expected_proof: str,
    proxy_url: str,
    authorization_ref: str,
    prompt: str,
    conversation_id: str = "",
) -> Tuple[Dict[str, Any], Path]:
    prompt_path = runtime_dir / ("%s.prompt" % prefix)
    events_path = runtime_dir / ("%s.events.jsonl" % prefix)
    stderr_path = runtime_dir / ("%s.stderr" % prefix)
    evidence_path = runtime_dir / ("%s.evidence.json" % prefix)
    prompt_path.write_text(prompt, encoding="utf-8")

    command = [
        "/usr/bin/python3", str(live_worker),
        "--mode", mode,
        "--agy-bin", A2_AGY_BIN,
        "--model", str(selected_worker["model_id"]),
        "--prompt-file", str(prompt_path),
        "--events-file", str(events_path),
        "--stderr-file", str(stderr_path),
        "--evidence-file", str(evidence_path),
        "--expected-proof", expected_proof,
        "--timeout-seconds", "180",
    ]
    if mode == "resume":
        if not conversation_id:
            raise RuntimeError("resume requires conversation id")
        command.extend(["--conversation-id", conversation_id])
    elif conversation_id:
        raise RuntimeError("start must not receive conversation id")

    worker_id = str(selected_worker["worker_id"])
    spec = {
        "worker_id": worker_id,
        "eligible_workers": [worker_id],
        "data_class": DATA_CLASS,
        "max_cost_usd": 0,
        "network": "VOS_AUTHORIZED",
        "network_authorization_ref": authorization_ref,
        "external_effects": False,
        "command": command,
        "allowed_executables": ["/usr/bin/python3"],
        "allowed_paths": [str(runtime_dir)],
        "cwd": str(runtime_dir),
        "timeout_seconds": 240,
        "env": explicit_worker_env(proxy_url),
    }
    return spec, evidence_path


def assert_worker_done(result: Mapping[str, Any]) -> None:
    if result.get("status") != "DONE" or result.get("exit_code") != 0:
        raise RuntimeError("live worker did not complete successfully: %s" % result.get("status"))


def assert_a2_evidence(evidence: Mapping[str, Any], mode: str) -> str:
    if evidence.get("mode") != mode:
        raise RuntimeError("A2 evidence mode mismatch")
    if evidence.get("model") != "gemini-3.8-flash-high":
        raise RuntimeError("A2 evidence model drift")
    if evidence.get("antigravity_version") != "1.2.3":
        raise RuntimeError("A2 version drift")
    if (
        evidence.get("antigravity_binary_sha256")
        != "c4c8a6722f9b570e370941b0953ba29051336307d7999ec842bdf7500b0ca7c8"
    ):
        raise RuntimeError("A2 binary SHA drift")
    if evidence.get("structured_output_verified") is not True:
        raise RuntimeError("A2 structured output was not deterministically verified")
    for key in ("api_key_fallback", "credit_fallback", "paid_api_fallback", "production_mutations"):
        if evidence.get(key) != 0:
            raise RuntimeError("A2 forbidden fallback/mutation detected: " + key)
    conversation = evidence.get("observed_conversation_id")
    if not isinstance(conversation, str) or not conversation:
        raise RuntimeError("A2 conversation id missing")
    return conversation


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=("stage1", "stage2"))
    parser.add_argument("--fabric-dir", required=True)
    parser.add_argument("--runtime-dir", required=True)
    parser.add_argument("--live-worker", required=True)
    parser.add_argument("--mandate-md", required=True)
    parser.add_argument("--mandate-json", required=True)
    parser.add_argument("--authorization-ref", required=True)
    parser.add_argument("--fabric-sha", required=True)
    parser.add_argument("--proxy-url", required=True)
    args = parser.parse_args()

    if args.fabric_sha != FABRIC_CERTIFICATION_SHA:
        raise RuntimeError("runtime Fabric SHA does not match certified registry SHA")

    runtime_dir = Path(args.runtime_dir).resolve()
    runtime_dir.mkdir(parents=True, exist_ok=True)
    live_worker = Path(args.live_worker).resolve()
    fabric_dir = Path(args.fabric_dir).resolve()
    manifest = validate_mandate(Path(args.mandate_md), Path(args.mandate_json))
    expected_ref_fragment = "mandate_sha256=%s" % manifest["mandate_sha256"]
    if expected_ref_fragment not in args.authorization_ref:
        raise RuntimeError("authorization ref is not bound to mandate SHA-256")
    if "g3=%s" % G3_CERTIFIED_SHA not in args.authorization_ref:
        raise RuntimeError("authorization ref is not bound to certified G3 SHA")
    if "fabric=%s" % FABRIC_CERTIFICATION_SHA not in args.authorization_ref:
        raise RuntimeError("authorization ref is not bound to exact Fabric SHA")

    bridge, checkpoint, rollover, router, worker_adapter, worker_registry = load_fabric(fabric_dir)
    selected_worker, routed, route_binding_sha = select_a2(worker_registry)

    checkpoint_path = runtime_dir / "g5.checkpoint.json"
    stage1_path = runtime_dir / "g5.stage1.json"
    marker_path = runtime_dir / "g5.effect.marker"

    if args.stage == "stage1":
        cp0 = checkpoint.new_checkpoint(
            "VOS-FABRIC-G4-G5-RUNTIME",
            manifest["mandate_sha256"],
            sha256_text(G3_CERTIFIED_SHA),
        )
        g4_prompt = (
            "PUBLIC VOS Fabric certification objective. "
            "Your structured output field named proof must be exactly: "
            "VOS_G4_A2_RUNTIME=OK"
        )
        spec, evidence_path = make_worker_spec(
            runtime_dir,
            live_worker,
            selected_worker,
            mode="start",
            prefix="g4-a2",
            expected_proof="VOS_G4_A2_RUNTIME=OK",
            proxy_url=args.proxy_url,
            authorization_ref=args.authorization_ref,
            prompt=g4_prompt,
        )
        prepared = bridge.prepare_dispatch(
            cp0,
            spec,
            vos_authorization_ref=args.authorization_ref,
            continuation_ref=None,
        )
        if prepared["founder_prompt_shuttling"] != 0:
            raise RuntimeError("bridge reported founder prompt shuttling")
        result = worker_adapter.run_request(prepared["worker_request"])
        assert_worker_done(result)
        consumed = bridge.consume_result(prepared["checkpoint"], result)
        if consumed["founder_prompt_shuttling"] != 0:
            raise RuntimeError("bridge result reported founder prompt shuttling")

        g4_evidence = read_json(evidence_path)
        old_ref = assert_a2_evidence(g4_evidence, "start")
        cp_ready = checkpoint.advance(
            consumed["checkpoint"],
            state="READY",
            continuation_ref=old_ref,
            last_result_sha256=consumed["checkpoint"]["last_result_sha256"],
        )

        effect_payload = (
            "VOS_G5_ISOLATED_EFFECT:%s:%s\n"
            % (manifest["mandate_sha256"], old_ref)
        ).encode("utf-8")
        effect_sha = sha256_bytes(effect_payload)
        cp_claimed, claimed_now = checkpoint.claim_effect(cp_ready, EFFECT_ID, effect_sha)
        if not claimed_now:
            raise RuntimeError("first isolated certification effect was not newly claimed")
        if marker_path.exists():
            raise RuntimeError("isolated effect marker pre-existed")
        marker_path.write_bytes(effect_payload)

        # This is an explicit VOS certification/process boundary, not fabricated
        # provider context telemetry. G5 must reload this durable state in a new
        # process and create a distinct continuation before completing rollover.
        cp_rollover = checkpoint.advance(
            cp_claimed,
            state="ROLLOVER_REQUIRED",
            continuation_ref=old_ref,
            last_result_sha256=cp_claimed["last_result_sha256"],
        )
        checkpoint_file_sha = checkpoint.write_atomic(checkpoint_path, cp_rollover)
        write_json(
            stage1_path,
            {
                "schema_version": 1,
                "authorization_ref_sha256": sha256_text(args.authorization_ref),
                "mandate_sha256": manifest["mandate_sha256"],
                "fabric_sha": args.fabric_sha,
                "data_class": DATA_CLASS,
                "data_policy": DATA_POLICY,
                "route_binding_sha256": route_binding_sha,
                "a2_qualification_ref_sha256": sha256_text(worker_registry.A2_QUALIFICATION_REF),
                "codex_capacity_evidence_ref_sha256": sha256_text(
                    worker_registry.CODEX_CAPACITY_EVIDENCE_REF
                ),
                "codex_breaker_state": routed["capacity"]["breakers"][
                    worker_registry.CODEX_WORKER_ID
                ]["state"],
                "old_continuation_ref_sha256": sha256_text(old_ref),
                "effect_id": EFFECT_ID,
                "effect_sha256": effect_sha,
                "checkpoint_file_sha256": checkpoint_file_sha,
                "g4_worker_result_sha256": consumed["result_sha256"],
                "g4_events_sha256": g4_evidence["events_sha256"],
                "rollover_trigger": "VOS_MANDATE_PROCESS_BOUNDARY",
                "founder_prompt_shuttling": 0,
                "paid_api_fallback": 0,
                "production_mutations": 0,
            },
        )
        print("G4_ROUTER_PATH=A2_DIRECT_OFFICIAL")
        print("G4_CODEX_BREAKER=OPEN")
        print("G4_DATA_CLASS=PUBLIC")
        print("G4_DATA_POLICY=PUBLIC_ONLY")
        print("G4_NORMALIZED_RESULT=GREEN")
        print("G4_DETERMINISTIC_VERIFICATION=GREEN")
        print("G4_DURABLE_CHECKPOINT=GREEN")
        print("FOUNDER_PROMPT_SHUTTLING=0")
        print("PAID_API_FALLBACK=0")
        print("PRODUCTION_MUTATIONS=0")
        return 0

    cp = checkpoint.read_checkpoint(checkpoint_path)
    stage1 = read_json(stage1_path)
    if cp["state"] != "ROLLOVER_REQUIRED":
        raise RuntimeError("durable checkpoint is not ROLLOVER_REQUIRED")
    if stage1["authorization_ref_sha256"] != sha256_text(args.authorization_ref):
        raise RuntimeError("authorization ref changed across process boundary")
    if stage1["fabric_sha"] != args.fabric_sha:
        raise RuntimeError("Fabric SHA changed across process boundary")
    if stage1.get("data_class") != DATA_CLASS or stage1.get("data_policy") != DATA_POLICY:
        raise RuntimeError("data-policy boundary changed across process boundary")
    if stage1.get("route_binding_sha256") != route_binding_sha:
        raise RuntimeError("router binding changed across process boundary")
    if (
        stage1.get("a2_qualification_ref_sha256")
        != sha256_text(worker_registry.A2_QUALIFICATION_REF)
    ):
        raise RuntimeError("A2 qualification reference changed across process boundary")
    if (
        stage1.get("codex_capacity_evidence_ref_sha256")
        != sha256_text(worker_registry.CODEX_CAPACITY_EVIDENCE_REF)
    ):
        raise RuntimeError("Codex capacity evidence changed across process boundary")
    if stage1.get("codex_breaker_state") != "OPEN":
        raise RuntimeError("Codex breaker state changed across process boundary")

    old_ref = cp["continuation_ref"]
    if not isinstance(old_ref, str) or not old_ref:
        raise RuntimeError("durable old continuation ref missing")
    if stage1["old_continuation_ref_sha256"] != sha256_text(old_ref):
        raise RuntimeError("durable old continuation ref mismatch")
    expected_marker = (
        "VOS_G5_ISOLATED_EFFECT:%s:%s\n"
        % (manifest["mandate_sha256"], old_ref)
    ).encode("utf-8")
    if marker_path.read_bytes() != expected_marker:
        raise RuntimeError("isolated effect marker mismatch before G5")

    replay_cp, claimed_now = checkpoint.claim_effect(
        cp,
        stage1["effect_id"],
        stage1["effect_sha256"],
    )
    if claimed_now:
        raise RuntimeError("same-payload effect replay was incorrectly claimed again")
    if marker_path.read_bytes() != expected_marker:
        raise RuntimeError("isolated effect marker changed on safe replay")

    conflicting_replay_rejected = False
    conflict_sha = sha256_bytes(expected_marker + b"CONFLICT")
    try:
        checkpoint.claim_effect(replay_cp, stage1["effect_id"], conflict_sha)
    except checkpoint.CheckpointError:
        conflicting_replay_rejected = True
    if not conflicting_replay_rejected:
        raise RuntimeError("conflicting effect replay was not rejected fail-closed")
    if marker_path.read_bytes() != expected_marker:
        raise RuntimeError("isolated effect marker changed on conflicting replay")

    boundary_digest = checkpoint.checkpoint_digest(replay_cp)
    g5_start_prompt = (
        "PUBLIC VOS Fabric continuation from durable checkpoint digest %s. "
        "Your structured output field named proof must be exactly: "
        "VOS_G5_A2_NEW_CONTINUATION=OK"
        % boundary_digest
    )
    start_spec, start_evidence_path = make_worker_spec(
        runtime_dir,
        live_worker,
        selected_worker,
        mode="start",
        prefix="g5-a2-new",
        expected_proof="VOS_G5_A2_NEW_CONTINUATION=OK",
        proxy_url=args.proxy_url,
        authorization_ref=args.authorization_ref,
        prompt=g5_start_prompt,
    )
    start_request = dict(start_spec)
    start_request["request_id"] = "vos-rollover-" + sha256_text(
        manifest["mandate_sha256"] + "\0" + old_ref
    )[:24]
    start_request["mandate_sha256"] = manifest["mandate_sha256"]
    start_result = worker_adapter.run_request(start_request)
    assert_worker_done(start_result)
    start_evidence = read_json(start_evidence_path)
    new_ref = assert_a2_evidence(start_evidence, "start")
    if new_ref == old_ref:
        raise RuntimeError("G5 did not create a distinct continuation ref")

    completed = rollover.complete_rollover(
        replay_cp,
        expected_old_continuation_ref=old_ref,
        new_continuation_ref=new_ref,
    )
    if not completed["completed_now"]:
        raise RuntimeError("G5 rollover completion was unexpectedly a replay")
    if completed["founder_prompt_shuttling"] != 0:
        raise RuntimeError("rollover completion reported founder prompt shuttling")
    cp_ready = completed["checkpoint"]

    g5_resume_prompt = (
        "PUBLIC VOS Fabric post-rollover continuation. "
        "Your structured output field named proof must be exactly: "
        "VOS_G5_A2_EXACT_RESUME=OK"
    )
    resume_spec, resume_evidence_path = make_worker_spec(
        runtime_dir,
        live_worker,
        selected_worker,
        mode="resume",
        prefix="g5-a2-resume",
        expected_proof="VOS_G5_A2_EXACT_RESUME=OK",
        proxy_url=args.proxy_url,
        authorization_ref=args.authorization_ref,
        prompt=g5_resume_prompt,
        conversation_id=new_ref,
    )
    prepared = bridge.prepare_dispatch(
        cp_ready,
        resume_spec,
        vos_authorization_ref=args.authorization_ref,
        continuation_ref=new_ref,
    )
    if prepared["founder_prompt_shuttling"] != 0:
        raise RuntimeError("post-rollover bridge reported founder prompt shuttling")
    resume_result = worker_adapter.run_request(prepared["worker_request"])
    assert_worker_done(resume_result)
    consumed = bridge.consume_result(prepared["checkpoint"], resume_result)
    if consumed["founder_prompt_shuttling"] != 0:
        raise RuntimeError("post-rollover result reported founder prompt shuttling")
    resume_evidence = read_json(resume_evidence_path)
    resumed_ref = assert_a2_evidence(resume_evidence, "resume")
    if resumed_ref != new_ref:
        raise RuntimeError("post-rollover exact resume changed continuation ref")

    final_checkpoint_sha = checkpoint.write_atomic(checkpoint_path, consumed["checkpoint"])
    final_evidence = {
        "schema_version": 1,
        "g4": "GREEN",
        "g5": "GREEN",
        "router": "GREEN",
        "router_worker_id": worker_registry.A2_WORKER_ID,
        "route_binding_sha256": route_binding_sha,
        "a2_qualification_ref": worker_registry.A2_QUALIFICATION_REF,
        "codex_capacity_evidence_ref": worker_registry.CODEX_CAPACITY_EVIDENCE_REF,
        "codex_breaker_state": "OPEN",
        "data_class": DATA_CLASS,
        "data_policy": DATA_POLICY,
        "old_continuation_ref_sha256": sha256_text(old_ref),
        "new_continuation_ref_sha256": sha256_text(new_ref),
        "continuation_changed": True,
        "post_rollover_resume_exact": True,
        "effect_claimed_once": True,
        "same_payload_replay_claimed_now": False,
        "conflicting_replay_rejected": True,
        "effect_marker_sha256": sha256_bytes(marker_path.read_bytes()),
        "final_checkpoint_sha256": final_checkpoint_sha,
        "g5_new_events_sha256": start_evidence["events_sha256"],
        "g5_resume_events_sha256": resume_evidence["events_sha256"],
        "founder_prompt_shuttling": 0,
        "api_key_fallback": 0,
        "credit_fallback": 0,
        "paid_api_fallback": 0,
        "production_mutations": 0,
        "rollover_trigger": "VOS_MANDATE_PROCESS_BOUNDARY",
    }
    write_json(runtime_dir / "g4-g5-runtime-evidence.json", final_evidence)
    print("G4_ROUTER_PATH=A2_DIRECT_OFFICIAL")
    print("G4_CODEX_BREAKER=OPEN")
    print("G5_DISTINCT_PROCESS_BOUNDARY=GREEN")
    print("G5_NEW_CONTINUATION=GREEN")
    print("G5_POST_ROLLOVER_EXACT_RESUME=GREEN")
    print("G5_EFFECT_CLAIMED_ONCE=GREEN")
    print("G5_SAME_PAYLOAD_REPLAY_CLAIMED=0")
    print("G5_CONFLICTING_REPLAY_REJECTED=GREEN")
    print("G5_DUPLICATED_EFFECTS=0")
    print("FOUNDER_PROMPT_SHUTTLING=0")
    print("PAID_API_FALLBACK=0")
    print("PRODUCTION_MUTATIONS=0")
    print("G4=GREEN")
    print("G5=GREEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
