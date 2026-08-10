#!/bin/zsh
set -euo pipefail

EXPECTED_OS="11.7.10"
EXPECTED_BASE="${2:?expected canonical base required}"
EXPECTED_ROUTER_OLD_SHA="318021ca9ef20a95013640fddf83709d5323b406f559c54f63a83e2aaa842066"
EXPECTED_RO_SHA="563abeccf36ef3de2973fabdfbf1b75c7d34d2347872b9b098e40e63d40b26a9"
EXPECTED_GENERIC_SRC_BLOB="a96d94cdad206f76cf67508d839b2d0bc0eb94d4"
EXPECTED_ROUTER_SRC_SHA="967da5bec0e13413d0706ce03bd09bdb1f77e5b323159f5b2b9a3d994bf40d33"
EXPECTED_PUBLISH_GATE_SHA="87f59ef644ff5f2d5a91de5debce4e38f0a6f695cb24dac1dce5f3ce6d703678"

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
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP="$EXEC.pre-generic-write-$STAMP"
REPORT="$ROOT/generic-write-lane-install-$STAMP.txt"
GEN_TMP="$GEN.tmp-$STAMP"
ROUTER_TMP="$EXEC.tmp-$STAMP"
GATE_TMP="$GATE.tmp-$STAMP"
MUTATED=0
COMMITTED=0

sha(){ shasum -a 256 "$1" | awk '{print $1}'; }
blob(){ git hash-object --no-filters "$1"; }

rollback_if_needed() {
  local rc=$?
  trap - EXIT
  rm -f "$GEN_TMP" "$ROUTER_TMP" "$GATE_TMP" 2>/dev/null || true
  if [ "$rc" -ne 0 ] && [ "$MUTATED" -eq 1 ] && [ "$COMMITTED" -eq 0 ]; then
    echo "ROLLBACK=START"
    [ -f "$BACKUP" ] && cp -p "$BACKUP" "$EXEC" || true
    rm -f "$GEN" "$GATE" "$ACTIVATED" "$REPORT" 2>/dev/null || true
    launchctl kickstart -k "$DOMAIN/$LABEL" >/dev/null 2>&1 || true
    echo "ROLLBACK=ATTEMPTED"
  fi
  exit "$rc"
}
trap rollback_if_needed EXIT

echo "=== FLUXION GENERIC WRITE LANE BOOTSTRAP ==="
echo "EXPECTED_BASE=$EXPECTED_BASE"

[ "$(sw_vers -productVersion)" = "$EXPECTED_OS" ] || { echo "STOP: OS inatteso"; exit 2; }
[ -f "$GEN_SRC" ] && [ -f "$ROUTER_SRC" ] && [ -f "$GATE_SRC" ] || { echo "STOP: bootstrap sources missing"; exit 2; }
[ "$(blob "$GEN_SRC")" = "$EXPECTED_GENERIC_SRC_BLOB" ] || { echo "STOP: generic source blob mismatch"; exit 2; }
[ "$(sha "$ROUTER_SRC")" = "$EXPECTED_ROUTER_SRC_SHA" ] || { echo "STOP: router source SHA mismatch"; exit 2; }
[ "$(sha "$GATE_SRC")" = "$EXPECTED_PUBLISH_GATE_SHA" ] || { echo "STOP: publish gate source SHA mismatch"; exit 2; }

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

RO_SHA="$(sha "$RO")"
ROUTER_SHA="$(sha "$EXEC")"
GEN_BLOB="none"; [ -f "$GEN" ] && GEN_BLOB="$(blob "$GEN")"
GATE_SHA="none"; [ -f "$GATE" ] && GATE_SHA="$(sha "$GATE")"
MARKER_STATE="absent"; [ -s "$ACTIVATED" ] && MARKER_STATE="present"

echo "RO_CORE_SHA=$RO_SHA"
echo "ROUTER_SHA_BEFORE=$ROUTER_SHA"
echo "GENERIC_BLOB_BEFORE=$GEN_BLOB"
echo "PUBLISH_GATE_SHA_BEFORE=$GATE_SHA"
echo "ACTIVATION_MARKER=$MARKER_STATE"
[ "$RO_SHA" = "$EXPECTED_RO_SHA" ] || { echo "STOP: RO core SHA inatteso"; exit 2; }

if [ "$ROUTER_SHA" = "$EXPECTED_ROUTER_OLD_SHA" ] && [ "$GEN_BLOB" = "none" ] && [ "$GATE_SHA" = "none" ] && [ "$MARKER_STATE" = "absent" ]; then
  INSTALL_STATE="CLEAN_OLD"
elif [ "$ROUTER_SHA" = "$EXPECTED_ROUTER_SRC_SHA" ] && [ "$GEN_BLOB" = "$EXPECTED_GENERIC_SRC_BLOB" ] && [ "$GATE_SHA" = "$EXPECTED_PUBLISH_GATE_SHA" ] && [ "$MARKER_STATE" = "present" ]; then
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
  [ "$(sha "$EXEC")" = "$EXPECTED_ROUTER_SRC_SHA" ] || return 2
  [ "$(sha "$GATE")" = "$EXPECTED_PUBLISH_GATE_SHA" ] || return 2
  [ "$(sha "$RO")" = "$EXPECTED_RO_SHA" ] || return 2
  [ "$(git -C "$REPO" rev-parse HEAD)" = "$CANON_HEAD" ] || return 2
  [ "$(git -C "$REPO" rev-parse refs/remotes/origin/master)" = "$ORIGIN_HEAD" ] || return 2
  [ "$(git -C "$REPO" status --porcelain)" = "$CANON_STATUS" ] || return 2
}

if [ "$INSTALL_STATE" = "ALREADY_INSTALLED_EXACT" ]; then
  verify_local || { echo "STOP: exact installed state failed verification"; exit 2; }
  echo "GENERIC_WRITE_LANE_INSTALLED=YES"
  echo "TRUSTED_PUBLISH_GATE_INSTALLED=YES"
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
[ "$(sha "$ROUTER_TMP")" = "$EXPECTED_ROUTER_SRC_SHA" ] || { echo "STOP: staged router SHA mismatch"; exit 2; }
[ "$(sha "$GATE_TMP")" = "$EXPECTED_PUBLISH_GATE_SHA" ] || { echo "STOP: staged gate SHA mismatch"; exit 2; }
/bin/zsh -n "$GEN_TMP"
python3 -m py_compile "$ROUTER_TMP" "$GATE_TMP"

cp -p "$EXEC" "$BACKUP"
echo "ROUTER_BACKUP=$BACKUP"
mv "$GEN_TMP" "$GEN"
mv "$GATE_TMP" "$GATE"
mv "$ROUTER_TMP" "$EXEC"
MUTATED=1

MARKER_TMP="$ACTIVATED.tmp-$STAMP"
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
generic_write_sha=$(sha "$GEN")
generic_write_blob=$(blob "$GEN")
trusted_publish_gate_sha=$(sha "$GATE")
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
echo "TRUSTED_PUBLISH_GATE_SHA=$(sha "$GATE")"
echo "GENERIC_WRITE_LANE_INSTALLED=YES"
echo "TRUSTED_PUBLISH_GATE_INSTALLED=YES"
echo "RO_CORE_PRESERVED=YES"
echo "PUBLISHER_BOUNDARY=TRUSTED_NON_LLM"
echo "SUPPORTED_WRITE_PROFILES=FIX_SCOPED_BUG,APPLY_EXISTING_UNIT"
echo "INSTALL_RESULT=PASS"
