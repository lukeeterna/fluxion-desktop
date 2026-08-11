#!/bin/zsh
set -euo pipefail

EXPECTED_OS="11.7.10"
EXPECTED_BASE="${2:?expected canonical base required}"
EXPECTED_ROUTER_OLD_SHA="318021ca9ef20a95013640fddf83709d5323b406f559c54f63a83e2aaa842066"
EXPECTED_RO_SHA="563abeccf36ef3de2973fabdfbf1b75c7d34d2347872b9b098e40e63d40b26a9"
EXPECTED_GENERIC_SRC_BLOB="65f2b3d5a2d584d49c65f73c85bc01b1ce258003"
EXPECTED_ROUTER_SRC_BLOB="e0a8074fadc9a536dce2af7992ee2849754f8c8a"
EXPECTED_PUBLISH_GATE_BLOB="c91ab0af3948ff6c1105ec679e66abfd88c08a43"
EXPECTED_CLAUDE_VERSION="2.1.110"

SRC="${1:?bootstrap source dir required}"
GEN_SRC="$SRC/fluxion-generic-write-executor"
ROUTER_SRC="$SRC/fluxion-draft-bus-executor"
GATE_SRC="$SRC/fluxion-trusted-publish-gate.py"
ROOT="$HOME/.local/share/fluxion-draft-bus"
REPO="/Volumes/MontereyT7/FLUXION"
EXEC="$HOME/.local/bin/fluxion-draft-bus-executor"
RO="$HOME/.local/bin/fluxion-draft-bus-executor-ro-core"
GEN="$HOME/.local/bin/fluxion-generic-write-executor"
GATE="$HOME/.local/bin/fluxion-trusted-publish-gate"
DRAFT="$HOME/.local/bin/fluxion-draft-bus-secure"
PLIST="$HOME/Library/LaunchAgents/com.fluxion.draft-bus-executor.plist"
LABEL="com.fluxion.draft-bus-executor"
DOMAIN="gui/$(id -u)"
ACTIVATED="$ROOT/generic-write-activated-at.txt"
CLAUDE_PIN="$ROOT/generic-write-claude-pin.json"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP="$EXEC.pre-generic-write-$STAMP"
REPORT="$ROOT/generic-write-lane-install-$STAMP.txt"
GEN_TMP="$GEN.tmp-$STAMP"
ROUTER_TMP="$EXEC.tmp-$STAMP"
GATE_TMP="$GATE.tmp-$STAMP"
CLAUDE_PIN_TMP="$CLAUDE_PIN.tmp-$STAMP"
MARKER_TMP="$ACTIVATED.tmp-$STAMP"
MUTATED=0
COMMITTED=0
sha(){ shasum -a 256 "$1" | awk '{print $1}'; }
blob(){ git hash-object --no-filters "$1"; }

rollback_if_needed() {
  local rc=$?
  trap - EXIT
  rm -f "$GEN_TMP" "$ROUTER_TMP" "$GATE_TMP" "$CLAUDE_PIN_TMP" "$MARKER_TMP" 2>/dev/null || true
  if [ "$rc" -ne 0 ] && [ "$MUTATED" -eq 1 ] && [ "$COMMITTED" -eq 0 ]; then
    echo "ROLLBACK=START"
    [ -f "$BACKUP" ] && cp -p "$BACKUP" "$EXEC" || true
    rm -f "$GEN" "$GATE" "$CLAUDE_PIN" "$ACTIVATED" "$REPORT" 2>/dev/null || true
    launchctl kickstart -k "$DOMAIN/$LABEL" >/dev/null 2>&1 || true
    echo "ROLLBACK=ATTEMPTED"
  fi
  exit "$rc"
}
trap rollback_if_needed EXIT

find_claude_runtime() {
  local candidate="$HOME/.npm-global/bin/claude"
  [ -x "$candidate" ] || candidate="$(command -v claude || true)"
  [ -n "$candidate" ] && [ -x "$candidate" ] || return 2
  python3 - "$candidate" <<'PY'
import os,sys
print(os.path.realpath(sys.argv[1]))
PY
}

verify_claude_pin() {
  [ -f "$CLAUDE_PIN" ] || return 2
  python3 - "$CLAUDE_PIN" "$CLAUDE_REAL" "$CLAUDE_SHA" "$EXPECTED_CLAUDE_VERSION" <<'PY'
import hashlib,json,os,re,sys
pin,path,expected_sha,expected_version=sys.argv[1:]
d=json.load(open(pin,encoding='utf-8'))
assert d.get('schema_version')==1
assert d.get('path')==path and os.path.realpath(path)==path and os.access(path,os.X_OK)
assert d.get('version')==expected_version
assert d.get('sha256')==expected_sha and re.fullmatch(r'[0-9a-f]{64}',expected_sha)
h=hashlib.sha256()
with open(path,'rb') as f:
    for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
assert h.hexdigest()==expected_sha
PY
  "$CLAUDE_REAL" --version | grep -E "^${EXPECTED_CLAUDE_VERSION}([[:space:]]|$)" >/dev/null
  /usr/bin/codesign --verify --verbose=2 "$CLAUDE_REAL" >/dev/null 2>&1
}

echo "=== FLUXION GENERIC WRITE LANE BOOTSTRAP ==="
echo "EXPECTED_BASE=$EXPECTED_BASE"
[ "$(sw_vers -productVersion)" = "$EXPECTED_OS" ] || { echo "STOP: OS inatteso"; exit 2; }
[ -f "$GEN_SRC" ] && [ -f "$ROUTER_SRC" ] && [ -f "$GATE_SRC" ] || { echo "STOP: bootstrap sources missing"; exit 2; }
[ "$(blob "$GEN_SRC")" = "$EXPECTED_GENERIC_SRC_BLOB" ] || { echo "STOP: generic source blob mismatch"; exit 2; }
[ "$(blob "$ROUTER_SRC")" = "$EXPECTED_ROUTER_SRC_BLOB" ] || { echo "STOP: router source blob mismatch"; exit 2; }
[ "$(blob "$GATE_SRC")" = "$EXPECTED_PUBLISH_GATE_BLOB" ] || { echo "STOP: publish gate source blob mismatch"; exit 2; }
[ -x "$EXEC" ] || { echo "STOP: current router missing"; exit 2; }
[ -x "$RO" ] || { echo "STOP: RO core missing"; exit 2; }
[ -x "$DRAFT" ] || { echo "STOP: secure Gmail publisher missing"; exit 2; }
[ -f "$PLIST" ] || { echo "STOP: executor LaunchAgent missing"; exit 2; }
[ -d "$ROOT" ] || { echo "STOP: Draft Bus root missing"; exit 2; }
if ps axww -o command= | grep -E '/[c]laude[[:space:]]+-p([[:space:]]|$)|(^|[[:space:]])[c]laude[[:space:]]+-p([[:space:]]|$)' >/dev/null; then
  echo "STOP: Claude headless active"; exit 2
fi
[ ! -e "$REPO/vos/STOP" ] || { echo "STOP: vos/STOP present"; exit 2; }
[ "$(git -C "$REPO" branch --show-current)" = "master" ] || { echo "STOP: canonical branch is not master"; exit 2; }
CANON_HEAD="$(git -C "$REPO" rev-parse HEAD)"
ORIGIN_HEAD="$(git -C "$REPO" rev-parse refs/remotes/origin/master)"
CANON_STATUS="$(git -C "$REPO" status --porcelain)"
[ "$CANON_HEAD" = "$EXPECTED_BASE" ] || { echo "STOP: canonical HEAD mismatch"; exit 2; }
[ "$ORIGIN_HEAD" = "$EXPECTED_BASE" ] || { echo "STOP: origin/master mismatch"; exit 2; }

CLAUDE_REAL="$(find_claude_runtime)" || { echo "STOP: Claude runtime missing"; exit 2; }
"$CLAUDE_REAL" --version | grep -E "^${EXPECTED_CLAUDE_VERSION}([[:space:]]|$)" >/dev/null || { echo "STOP: Claude version is not pinned 2.1.110"; exit 2; }
/usr/bin/codesign --verify --verbose=2 "$CLAUDE_REAL" >/dev/null 2>&1 || { echo "STOP: Claude code signature invalid"; exit 2; }
CLAUDE_SHA="$(sha "$CLAUDE_REAL")"
python3 - "$CLAUDE_PIN_TMP" "$CLAUDE_REAL" "$CLAUDE_SHA" "$EXPECTED_CLAUDE_VERSION" <<'PY'
import json,sys
p,path,sha,version=sys.argv[1:]
with open(p,'w',encoding='utf-8') as f:
    f.write(json.dumps({'schema_version':1,'path':path,'version':version,'sha256':sha},sort_keys=True,separators=(',',':'))+'\n')
PY
chmod 600 "$CLAUDE_PIN_TMP"

RO_SHA="$(sha "$RO")"
ROUTER_SHA="$(sha "$EXEC")"
ROUTER_BLOB="$(blob "$EXEC")"
GEN_BLOB="none"; [ -f "$GEN" ] && GEN_BLOB="$(blob "$GEN")"
GATE_BLOB="none"; [ -f "$GATE" ] && GATE_BLOB="$(blob "$GATE")"
MARKER_STATE="absent"; [ -s "$ACTIVATED" ] && MARKER_STATE="present"
PIN_STATE="absent"; [ -s "$CLAUDE_PIN" ] && PIN_STATE="present"
echo "RO_CORE_SHA=$RO_SHA"
echo "ROUTER_SHA_BEFORE=$ROUTER_SHA"
echo "ROUTER_BLOB_BEFORE=$ROUTER_BLOB"
echo "GENERIC_BLOB_BEFORE=$GEN_BLOB"
echo "PUBLISH_GATE_BLOB_BEFORE=$GATE_BLOB"
echo "ACTIVATION_MARKER=$MARKER_STATE"
echo "CLAUDE_PIN_STATE=$PIN_STATE"
echo "CLAUDE_VERSION=$EXPECTED_CLAUDE_VERSION"
echo "CLAUDE_SHA256=$CLAUDE_SHA"
[ "$RO_SHA" = "$EXPECTED_RO_SHA" ] || { echo "STOP: RO core SHA inatteso"; exit 2; }
if [ "$ROUTER_SHA" = "$EXPECTED_ROUTER_OLD_SHA" ] && [ "$GEN_BLOB" = "none" ] && [ "$GATE_BLOB" = "none" ] && [ "$MARKER_STATE" = "absent" ] && [ "$PIN_STATE" = "absent" ]; then
  INSTALL_STATE="CLEAN_OLD"
elif [ "$ROUTER_BLOB" = "$EXPECTED_ROUTER_SRC_BLOB" ] && [ "$GEN_BLOB" = "$EXPECTED_GENERIC_SRC_BLOB" ] && [ "$GATE_BLOB" = "$EXPECTED_PUBLISH_GATE_BLOB" ] && [ "$MARKER_STATE" = "present" ] && [ "$PIN_STATE" = "present" ]; then
  INSTALL_STATE="ALREADY_INSTALLED_EXACT"
else
  echo "INSTALL_STATE=BLOCKED_MIXED_STATE"
  echo "STOP: mixed or unknown generic-write installation state"
  exit 2
fi
echo "INSTALL_STATE=$INSTALL_STATE"

verify_local() {
  /bin/zsh -n "$GEN"
  python3 -m py_compile "$EXEC" "$GATE"
  [ "$(blob "$GEN")" = "$EXPECTED_GENERIC_SRC_BLOB" ] || return 2
  [ "$(blob "$EXEC")" = "$EXPECTED_ROUTER_SRC_BLOB" ] || return 2
  [ "$(blob "$GATE")" = "$EXPECTED_PUBLISH_GATE_BLOB" ] || return 2
  [ "$(sha "$RO")" = "$EXPECTED_RO_SHA" ] || return 2
  verify_claude_pin || return 2
  [ "$(git -C "$REPO" rev-parse HEAD)" = "$CANON_HEAD" ] || return 2
  [ "$(git -C "$REPO" rev-parse refs/remotes/origin/master)" = "$ORIGIN_HEAD" ] || return 2
  [ "$(git -C "$REPO" status --porcelain)" = "$CANON_STATUS" ] || return 2
}

if [ "$INSTALL_STATE" = "ALREADY_INSTALLED_EXACT" ]; then
  rm -f "$CLAUDE_PIN_TMP"
  verify_local || { echo "STOP: exact installed state failed verification"; exit 2; }
  echo "GENERIC_WRITE_LANE_INSTALLED=YES"
  echo "TRUSTED_PUBLISH_GATE_INSTALLED=YES"
  echo "CLAUDE_RUNTIME_PIN=PASS"
  echo "RO_CORE_PRESERVED=YES"
  echo "PUBLISHER_BOUNDARY=TRUSTED_NON_LLM"
  echo "SUPPORTED_WRITE_PROFILES=FIX_SCOPED_BUG,APPLY_EXISTING_UNIT"
  echo "INSTALL_RESULT=PASS"
  COMMITTED=1
  exit 0
fi

install -m 700 "$GEN_SRC" "$GEN_TMP"
install -m 700 "$ROUTER_SRC" "$ROUTER_TMP"
install -m 700 "$GATE_SRC" "$GATE_TMP"
[ "$(blob "$GEN_TMP")" = "$EXPECTED_GENERIC_SRC_BLOB" ] || { echo "STOP: staged generic blob mismatch"; exit 2; }
[ "$(blob "$ROUTER_TMP")" = "$EXPECTED_ROUTER_SRC_BLOB" ] || { echo "STOP: staged router blob mismatch"; exit 2; }
[ "$(blob "$GATE_TMP")" = "$EXPECTED_PUBLISH_GATE_BLOB" ] || { echo "STOP: staged gate blob mismatch"; exit 2; }
/bin/zsh -n "$GEN_TMP"
python3 -m py_compile "$ROUTER_TMP" "$GATE_TMP"
cp -p "$EXEC" "$BACKUP"
echo "ROUTER_BACKUP=$BACKUP"

# From the first filesystem mutation onward every failure MUST enter rollback.
MUTATED=1
mv "$GEN_TMP" "$GEN"
mv "$GATE_TMP" "$GATE"
mv "$ROUTER_TMP" "$EXEC"
mv "$CLAUDE_PIN_TMP" "$CLAUDE_PIN"
date -u +%Y-%m-%dT%H:%M:%SZ > "$MARKER_TMP"
chmod 600 "$MARKER_TMP"
mv "$MARKER_TMP" "$ACTIVATED"

verify_local || { echo "STOP: installed files failed verification"; exit 2; }
launchctl kickstart -k "$DOMAIN/$LABEL"
sleep 2
launchctl print "$DOMAIN/$LABEL" > "$ROOT/launchctl-generic-write-$STAMP.txt"
cat > "$REPORT" <<EOF
installed_at=$STAMP
base=$EXPECTED_BASE
install_state=INSTALLED_NOW
ro_core_sha=$RO_SHA
router_sha_before=$ROUTER_SHA
router_sha_after=$(sha "$EXEC")
router_blob_after=$(blob "$EXEC")
generic_write_sha=$(sha "$GEN")
generic_write_blob=$(blob "$GEN")
trusted_publish_gate_sha=$(sha "$GATE")
trusted_publish_gate_blob=$(blob "$GATE")
claude_path=$CLAUDE_REAL
claude_version=$EXPECTED_CLAUDE_VERSION
claude_sha256=$CLAUDE_SHA
claude_codesign=verified
router_backup=$BACKUP
profiles=FIX_SCOPED_BUG,APPLY_EXISTING_UNIT
publisher_boundary=trusted-non-llm
canonical_repo_status_preserved=yes
EOF
chmod 600 "$REPORT"
verify_local || { echo "STOP: post-restart verification failed"; exit 2; }
COMMITTED=1
echo "GENERIC_WRITE_SHA=$(sha "$GEN")"
echo "GENERIC_WRITE_BLOB=$(blob "$GEN")"
echo "ROUTER_SHA_AFTER=$(sha "$EXEC")"
echo "ROUTER_BLOB_AFTER=$(blob "$EXEC")"
echo "TRUSTED_PUBLISH_GATE_SHA=$(sha "$GATE")"
echo "TRUSTED_PUBLISH_GATE_BLOB=$(blob "$GATE")"
echo "CLAUDE_RUNTIME_PIN=PASS"
echo "GENERIC_WRITE_LANE_INSTALLED=YES"
echo "TRUSTED_PUBLISH_GATE_INSTALLED=YES"
echo "RO_CORE_PRESERVED=YES"
echo "PUBLISHER_BOUNDARY=TRUSTED_NON_LLM"
echo "SUPPORTED_WRITE_PROFILES=FIX_SCOPED_BUG,APPLY_EXISTING_UNIT"
echo "INSTALL_RESULT=PASS"
