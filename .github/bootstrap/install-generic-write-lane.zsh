#!/bin/zsh
set -euo pipefail

EXPECTED_OS="11.7.10"
EXPECTED_BASE="${2:?expected canonical base required}"
EXPECTED_ROUTER_OLD_SHA="318021ca9ef20a95013640fddf83709d5323b406f559c54f63a83e2aaa842066"
EXPECTED_RO_SHA="563abeccf36ef3de2973fabdfbf1b75c7d34d2347872b9b098e40e63d40b26a9"
EXPECTED_GENERIC_SRC_BLOB="d8c38da13f9f6b28a9bca1774b5bccf61594cf48"
EXPECTED_ROUTER_SRC_BLOB="e0a8074fadc9a536dce2af7992ee2849754f8c8a"
EXPECTED_PUBLISH_GATE_BLOB="af564e331e7cadb7e843ded4340087531ef4acc9"
PREVIOUS_GENERIC_BLOB="5ef606da6ea37ca2ccdbdfcc406a87582e1f30d7"
PREVIOUS_PUBLISH_GATE_BLOB="5d8ac03661a3125f53dee896c64750e4e22462fc"
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
BACKUP_DIR="$ROOT/bootstrap-backup-$STAMP"
REPORT="$ROOT/generic-write-lane-install-$STAMP.txt"
MUTATED=0
COMMITTED=0
sha(){ shasum -a 256 "$1" | awk '{print $1}'; }
blob(){ git hash-object --no-filters "$1"; }

rollback() {
  local rc=$?
  trap - EXIT
  if [ "$rc" -ne 0 ] && [ "$MUTATED" -eq 1 ] && [ "$COMMITTED" -eq 0 ]; then
    echo "ROLLBACK=START"
    for item in EXEC GEN GATE PIN MARKER; do
      src="$BACKUP_DIR/$item"
      case "$item" in
        EXEC) dst="$EXEC";; GEN) dst="$GEN";; GATE) dst="$GATE";; PIN) dst="$CLAUDE_PIN";; MARKER) dst="$ACTIVATED";;
      esac
      if [ -f "$src.present" ]; then cp -p "$src" "$dst"; else rm -f "$dst"; fi
    done
    launchctl kickstart -k "$DOMAIN/$LABEL" >/dev/null 2>&1 || true
    echo "ROLLBACK=PASS"
  fi
  exit "$rc"
}
trap rollback EXIT

find_claude() {
  local p="$HOME/.npm-global/bin/claude"
  [ -x "$p" ] || p="$(command -v claude || true)"
  [ -n "$p" ] && [ -x "$p" ] || return 2
  python3 - "$p" <<'PY'
import os,sys
print(os.path.realpath(sys.argv[1]))
PY
}

verify_pin_file() {
  local pin="$1" real="$2" expected_sha="$3"
  python3 - "$pin" "$real" "$expected_sha" "$EXPECTED_CLAUDE_VERSION" <<'PY'
import hashlib,json,os,sys
pin,path,sha,version=sys.argv[1:];d=json.load(open(pin,encoding='utf-8'))
assert d=={'path':path,'schema_version':1,'sha256':sha,'version':version}
h=hashlib.sha256()
with open(path,'rb') as f:
    for c in iter(lambda:f.read(1024*1024),b''):h.update(c)
assert h.hexdigest()==sha and os.path.realpath(path)==path and os.access(path,os.X_OK)
PY
}

backup_one(){
  local name="$1" path="$2"; mkdir -p "$BACKUP_DIR"
  if [ -e "$path" ]; then cp -p "$path" "$BACKUP_DIR/$name"; touch "$BACKUP_DIR/$name.present"; fi
}

verify_local(){
  /bin/zsh -n "$GEN"
  python3 -m py_compile "$EXEC" "$GATE"
  [ "$(blob "$GEN")" = "$EXPECTED_GENERIC_SRC_BLOB" ]
  [ "$(blob "$EXEC")" = "$EXPECTED_ROUTER_SRC_BLOB" ]
  [ "$(blob "$GATE")" = "$EXPECTED_PUBLISH_GATE_BLOB" ]
  [ "$(sha "$RO")" = "$EXPECTED_RO_SHA" ]
  verify_pin_file "$CLAUDE_PIN" "$CLAUDE_REAL" "$CLAUDE_SHA"
  [ "$(git -C "$REPO" rev-parse HEAD)" = "$EXPECTED_BASE" ]
  [ "$(git -C "$REPO" rev-parse refs/remotes/origin/master)" = "$EXPECTED_BASE" ]
  [ "$(git -C "$REPO" status --porcelain)" = "$CANON_STATUS" ]
}

echo "=== FLUXION GENERIC WRITE LANE BOOTSTRAP ==="
[ "$(sw_vers -productVersion)" = "$EXPECTED_OS" ] || { echo "STOP: OS inatteso"; exit 2; }
[ -f "$GEN_SRC" ] && [ -f "$ROUTER_SRC" ] && [ -f "$GATE_SRC" ] || { echo "STOP: bootstrap sources missing"; exit 2; }
[ "$(blob "$GEN_SRC")" = "$EXPECTED_GENERIC_SRC_BLOB" ] || { echo "STOP: generic source blob mismatch"; exit 2; }
[ "$(blob "$ROUTER_SRC")" = "$EXPECTED_ROUTER_SRC_BLOB" ] || { echo "STOP: router source blob mismatch"; exit 2; }
[ "$(blob "$GATE_SRC")" = "$EXPECTED_PUBLISH_GATE_BLOB" ] || { echo "STOP: publish gate source blob mismatch"; exit 2; }
[ -x "$EXEC" ] && [ -x "$RO" ] && [ -x "$DRAFT" ] && [ -f "$PLIST" ] || { echo "STOP: trusted local prerequisites missing"; exit 2; }
[ ! -e "$REPO/vos/STOP" ] || { echo "STOP: vos/STOP present"; exit 2; }
[ "$(git -C "$REPO" branch --show-current)" = master ] || { echo "STOP: canonical branch is not master"; exit 2; }
[ "$(git -C "$REPO" rev-parse HEAD)" = "$EXPECTED_BASE" ] || { echo "STOP: canonical HEAD mismatch"; exit 2; }
[ "$(git -C "$REPO" rev-parse refs/remotes/origin/master)" = "$EXPECTED_BASE" ] || { echo "STOP: origin/master mismatch"; exit 2; }
CANON_STATUS="$(git -C "$REPO" status --porcelain)"
if ps axww -o command= | grep -E '/[c]laude[[:space:]]+-p([[:space:]]|$)|(^|[[:space:]])[c]laude[[:space:]]+-p([[:space:]]|$)' >/dev/null; then echo "STOP: Claude headless active"; exit 2; fi

CLAUDE_REAL="$(find_claude)" || { echo "STOP: Claude runtime missing"; exit 2; }
"$CLAUDE_REAL" --version | grep -E "^${EXPECTED_CLAUDE_VERSION}([[:space:]]|$)" >/dev/null || { echo "STOP: Claude version mismatch"; exit 2; }
/usr/bin/codesign --verify --verbose=2 "$CLAUDE_REAL" >/dev/null 2>&1 || { echo "STOP: Claude codesign invalid"; exit 2; }
CLAUDE_SHA="$(sha "$CLAUDE_REAL")"

ROUTER_SHA="$(sha "$EXEC")"; ROUTER_BLOB="$(blob "$EXEC")"
GEN_BLOB="none"; [ -f "$GEN" ] && GEN_BLOB="$(blob "$GEN")"
GATE_BLOB="none"; [ -f "$GATE" ] && GATE_BLOB="$(blob "$GATE")"
MARKER=absent; [ -s "$ACTIVATED" ] && MARKER=present
PIN=absent; [ -s "$CLAUDE_PIN" ] && PIN=present

if [ "$ROUTER_SHA" = "$EXPECTED_ROUTER_OLD_SHA" ] && [ "$GEN_BLOB" = none ] && [ "$GATE_BLOB" = none ] && [ "$MARKER" = absent ] && [ "$PIN" = absent ]; then
  INSTALL_STATE=CLEAN_OLD
elif [ "$ROUTER_BLOB" = "$EXPECTED_ROUTER_SRC_BLOB" ] && [ "$GEN_BLOB" = "$EXPECTED_GENERIC_SRC_BLOB" ] && [ "$GATE_BLOB" = "$EXPECTED_PUBLISH_GATE_BLOB" ] && [ "$MARKER" = present ] && [ "$PIN" = present ]; then
  INSTALL_STATE=ALREADY_INSTALLED_EXACT
elif [ "$ROUTER_BLOB" = "$EXPECTED_ROUTER_SRC_BLOB" ] && [ "$GEN_BLOB" = "$PREVIOUS_GENERIC_BLOB" ] && [ "$GATE_BLOB" = "$PREVIOUS_PUBLISH_GATE_BLOB" ] && [ "$MARKER" = present ] && [ "$PIN" = present ]; then
  INSTALL_STATE=UPGRADE_PREVIOUS_CONTROL
else
  echo "INSTALL_STATE=BLOCKED_MIXED_STATE"; echo "STOP: mixed or unknown installation state"; exit 2
fi
echo "INSTALL_STATE=$INSTALL_STATE"

if [ "$INSTALL_STATE" = ALREADY_INSTALLED_EXACT ]; then
  verify_local || { echo "STOP: exact installed state failed verification"; exit 2; }
  echo "ALREADY_INSTALLED_EXACT"
  echo "GENERIC_EXECUTOR_INSTALLED=yes"
  echo "EXECUTOR_INTEGRITY=PASS"
  echo "CLAUDE_RUNTIME_PIN=PASS"
  echo "NO_CLAUDE_INSTALL_OR_UPDATE=PASS"
  echo "INSTALL_RESULT=PASS"
  COMMITTED=1
  exit 0
fi

backup_one EXEC "$EXEC"; backup_one GEN "$GEN"; backup_one GATE "$GATE"; backup_one PIN "$CLAUDE_PIN"; backup_one MARKER "$ACTIVATED"
MUTATED=1
install -m 700 "$GEN_SRC" "$GEN"
install -m 700 "$ROUTER_SRC" "$EXEC"
install -m 700 "$GATE_SRC" "$GATE"
python3 - "$CLAUDE_PIN" "$CLAUDE_REAL" "$CLAUDE_SHA" "$EXPECTED_CLAUDE_VERSION" <<'PY'
import json,os,sys,tempfile
p,path,sha,version=sys.argv[1:]; parent=os.path.dirname(p); fd,tmp=tempfile.mkstemp(prefix='.claude-pin.',dir=parent)
try:
    os.fchmod(fd,0o600)
    with os.fdopen(fd,'w',encoding='utf-8') as h:h.write(json.dumps({'path':path,'schema_version':1,'sha256':sha,'version':version},sort_keys=True,separators=(',',':'))+'\n');h.flush();os.fsync(h.fileno())
    os.replace(tmp,p)
finally:
    try:os.unlink(tmp)
    except FileNotFoundError:pass
PY
date -u +%Y-%m-%dT%H:%M:%SZ > "$ACTIVATED"; chmod 600 "$ACTIVATED"
verify_local || { echo "STOP: installed files failed verification"; exit 2; }
launchctl kickstart -k "$DOMAIN/$LABEL"
sleep 2
launchctl print "$DOMAIN/$LABEL" > "$ROOT/launchctl-generic-write-$STAMP.txt"
cat > "$REPORT" <<EOF
installed_at=$STAMP
base=$EXPECTED_BASE
install_state=$INSTALL_STATE
router_blob=$(blob "$EXEC")
generic_blob=$(blob "$GEN")
publish_gate_blob=$(blob "$GATE")
claude_path=$CLAUDE_REAL
claude_version=$EXPECTED_CLAUDE_VERSION
claude_sha256=$CLAUDE_SHA
claude_codesign=verified
claude_install_or_update=absent
publisher_boundary=trusted-local-non-llm
fresh_review=trusted-local-sonnet-no-tools-advisory
EOF
chmod 600 "$REPORT"
COMMITTED=1
echo "BOOTSTRAP_STARTED=yes"
echo "GENERIC_EXECUTOR_INSTALLED=yes"
echo "EXECUTOR_INTEGRITY=PASS"
echo "CLAUDE_RUNTIME_PIN=PASS"
echo "NO_CLAUDE_INSTALL_OR_UPDATE=PASS"
echo "TRUSTED_PUBLISH_GATE_INSTALLED=YES"
echo "INSTALL_RESULT=PASS"
