# CLAUDE CODE WEB EVENT PROBE

Probe nonce: `CCWEB-20260806-2316-7f3d9b2a`

Purpose: verify the already-defined FLUXION operator chain without changing application, runtime, mandates, gates, or roadmap state.

Expected action from the **Claude Code Web GitHub-event node only**:

1. start a fresh Claude Code Web session from the pull-request event;
2. operate read-only;
3. post one PR comment containing exactly:

`CCWEB_EVENT_ACK CCWEB-20260806-2316-7f3d9b2a`

4. do not modify files, push commits, open another PR, review semantics, merge, or touch runtime.

Any other operator must ignore this probe.
