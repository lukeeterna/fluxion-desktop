#!/bin/zsh
set -euo pipefail

EXPECTED_OS="11.7.10"
EXPECTED_BASE="${2:?expected canonical base required}"
EXPECTED_ROUTER_OLD_SHA="318021ca9ef20a95013640fddf83709d5323b406f559c54f63a83e2aaa842066"
EXPECTED_RO_SHA="563abeccf36ef3de2973fabdfbf1b75c7d34d2347872b9b098e40e63d40b26a9"
EXPECTED_GENERIC_SRC_SHA="b3bd8640ee4a30fc26a9eb4ea3c1ab5914f4d492206ff7da70ec44f53961bec3"
EXPECTED_ROUTER_SRC_SHA="967da5bec0e13413d0706ce03bd09bdb1f77e5b323159f5b2b9a3d994bf40d33"

SRC="${1:?bootstrap source dir required}"
GEN_SRC="$SRC/fluxion-generic-write-executor"
ROUTER_SRC="$SRC/fluxion-draft-bus-executor"

ROOT="$HOME/.local/share/fluxion-draft-bus"
REPO="/Volumes/MontereyT7/FLUXION"
EXEC="$HOME/.local/bin/fluxion-draft-bus-executor"
RO="$HOME/.local/bin/fluxion-draft-bus-executor-ro-core"
GEN="$HOME/.local/bin/fluxion-generic-write-executor"
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
MUTATED=0
COMMITTED=0

sha(){ shasum -a 256 "$1" | awk '{print $1}'; }

rollback_if_needed() {
  local rc=$?
  trap - EXIT
  rm -f "$GEN_TMP" "$ROUTER_TMP" 2>/dev/null || true
  if [ "$rc" -ne 0 ] && [ "$MUTATED" -eq 1 ] && [ "$COMMITTED" -eq 0 ]; then
    echo "ROLLBACK=START"
    if [ -f "$BACKUP" ]; then
      cp -p "$BACKUP" "$EXEC" || true
    fi
    rm -f "$GEN" "$ACTIVATED" "$REPORT" 2>/dev/null || true
    launchctl kickstart -k "$DOMAIN/$LABEL" >/dev/null 2>&1 || true
    echo "ROLLBACK=ATTEMPTED"
  fi
  exit "$rc"
}
trap rollback_if_needed EXIT

echo "=== FLUXION GENERIC WRITE LANE BOOTSTRAP ==="
echo "EXPECTED_BASE=$EXPECTED_BASE"

[ "$(sw_vers -productVersion)" = "$EXPECTED_OS" ] || { echo "STOP: OS inatteso"; exit 2; }
[ -f "$GEN_SRC" ] && [ -f "$ROUTER_SRC" ] || { echo "STOP: bootstrap sources missing"; exit 2; }
[ "$(sha "$GEN_SRC")" = "$EXPECTED_GENERIC_SRC_SHA" ] || { echo "STOP: generic source SHA mismatch"; exit 2; }
[ "$(sha "$ROUTER_SRC")" = "$EXPECTED_ROUTER_SRC_SHA" ] || { echo "STOP: router source SHA mismatch"; exit 2; }

[ -x "$EXEC" ] || { echo "STOP: current router missing"; exit 2; }
[ -x "$RO" ] || { echo "STOP: RO core missing"; exit 2; }
[ -x "$DRAFT" ] || { echo "STOP: secure publisher missing"; exit 2; }
[ -f "$PLIST" ] || { echo "STOP: executor LaunchAgent missing"; exit 2; }
[ -d "$ROOT" ] || { echo "STOP: Draft Bus root missing"; exit 2; }

if ps axww -o command= | grep -E '/[c]laude[[:space:]]+-p([[:space:]]|$)|(^|[[:space:]])[c]laude[[:space:]]+-p([[:space:]]|$)' >/dev/null; then
  echo "STOP: Claude headless active"
  exit 2
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
GEN_SHA="none"
[ -f "$GEN" ] && GEN_SHA="$(sha "$GEN")"
MARKER_STATE="absent"
[ -s "$ACTIVATED" ] && MARKER_STATE="present"

echo "RO_CORE_SHA=$RO_SHA"
echo "ROUTER_SHA_BEFORE=$ROUTER_SHA"
echo "GENERIC_SHA_BEFORE=$GEN_SHA"
echo "ACTIVATION_MARKER=$MARKER_STATE"
[ "$RO_SHA" = "$EXPECTED_RO_SHA" ] || { echo "STOP: RO core SHA inatteso"; exit 2; }

INSTALL_STATE=""
if [ "$ROUTER_SHA" = "$EXPECTED_ROUTER_OLD_SHA" ] && [ "$GEN_SHA" = "none" ] && [ "$MARKER_STATE" = "absent" ]; then
  INSTALL_STATE="CLEAN_OLD"
elif [ "$ROUTER_SHA" = "$EXPECTED_ROUTER_SRC_SHA" ] && [ "$GEN_SHA" = "$EXPECTED_GENERIC_SRC_SHA" ] && [ "$MARKER_STATE" = "present" ]; then
  INSTALL_STATE="ALREADY_INSTALLED_EXACT"
else
  echo "STOP: mixed or unknown generic-write installation state"
  echo "INSTALL_STATE=BLOCKED_MIXED_STATE"
  exit 2
fi

echo "INSTALL_STATE=$INSTALL_STATE"

if [ "$INSTALL_STATE" = "ALREADY_INSTALLED_EXACT" ]; then
  /bin/zsh -n "$GEN"
  python3 - "$EXEC" <<'PY'
import pathlib,sys
p=pathlib.Path(sys.argv[1])
compile(p.read_text(encoding='utf-8'), str(p), 'exec')
PY
  [ "$(sha "$RO")" = "$EXPECTED_RO_SHA" ] || { echo "STOP: RO core changed"; exit 2; }
  [ "$(git -C "$REPO" rev-parse HEAD)" = "$CANON_HEAD" ] || { echo "STOP: canonical HEAD mutated"; exit 2; }
  [ "$(git -C "$REPO" rev-parse refs/remotes/origin/master)" = "$ORIGIN_HEAD" ] || { echo "STOP: origin/master changed"; exit 2; }
  [ "$(git -C "$REPO" status --porcelain)" = "$CANON_STATUS" ] || { echo "STOP: canonical status changed"; exit 2; }
  echo "GENERIC_WRITE_LANE_INSTALLED=YES"
  echo "RO_CORE_PRESERVED=YES"
  echo "PUBLISHER_BOUNDARY=TRUSTED_NON_LLM"
  echo "SUPPORTED_WRITE_PROFILES=FIX_SCOPED_BUG,APPLY_EXISTING_UNIT"
  echo "PUSH_DEPLOY=NEVER"
  echo "INSTALL_RESULT=PASS"
  COMMITTED=1
  exit 0
fi

install -m 700 "$GEN_SRC" "$GEN_TMP"
install -m 700 "$ROUTER_SRC" "$ROUTER_TMP"
[ "$(sha "$GEN_TMP")" = "$EXPECTED_GENERIC_SRC_SHA" ] || { echo "STOP: staged generic SHA mismatch"; exit 2; }
[ "$(sha "$ROUTER_TMP")" = "$EXPECTED_ROUTER_SRC_SHA" ] || { echo "STOP: staged router SHA mismatch"; exit 2; }
/bin/zsh -n "$GEN_TMP"
python3 - "$ROUTER_TMP" <<'PY'
import pathlib,sys
p=pathlib.Path(sys.argv[1])
compile(p.read_text(encoding='utf-8'), str(p), 'exec')
PY

cp -p "$EXEC" "$BACKUP"
echo "ROUTER_BACKUP=$BACKUP"

mv "$GEN_TMP" "$GEN"
mv "$ROUTER_TMP" "$EXEC"
MUTATED=1

GEN_SHA="$(sha "$GEN")"
NEW_ROUTER_SHA="$(sha "$EXEC")"
[ "$GEN_SHA" = "$EXPECTED_GENERIC_SRC_SHA" ] || { echo "STOP: installed generic SHA mismatch"; exit 2; }
[ "$NEW_ROUTER_SHA" = "$EXPECTED_ROUTER_SRC_SHA" ] || { echo "STOP: installed router SHA mismatch"; exit 2; }
[ "$(sha "$RO")" = "$EXPECTED_RO_SHA" ] || { echo "STOP: RO core changed"; exit 2; }

MARKER_TMP="$ACTIVATED.tmp-$STAMP"
date -u +%Y-%m-%dT%H:%M:%SZ > "$MARKER_TMP"
chmod 600 "$MARKER_TMP"
mv "$MARKER_TMP" "$ACTIVATED"

[ "$(git -C "$REPO" rev-parse HEAD)" = "$CANON_HEAD" ] || { echo "STOP: canonical HEAD mutated"; exit 2; }
[ "$(git -C "$REPO" rev-parse refs/remotes/origin/master)" = "$ORIGIN_HEAD" ] || { echo "STOP: origin/master changed"; exit 2; }
[ "$(git -C "$REPO" status --porcelain)" = "$CANON_STATUS" ] || { echo "STOP: canonical status changed"; exit 2; }

launchctl kickstart -k "$DOMAIN/$LABEL"
sleep 2
launchctl print "$DOMAIN/$LABEL" > "$ROOT/launchctl-generic-write-$STAMP.txt"

cat > "$REPORT" <<EOF
installed_at=$STAMP
base=$EXPECTED_BASE
install_state=INSTALLED_NOW
ro_core_sha=$RO_SHA
router_sha_before=$ROUTER_SHA
router_sha_after=$NEW_ROUTER_SHA
generic_write_sha=$GEN_SHA
router_backup=$BACKUP
profiles=FIX_SCOPED_BUG,APPLY_EXISTING_UNIT
publisher_boundary=trusted-non-llm
canonical_repo_status_preserved=yes
EOF
chmod 600 "$REPORT"

[ "$(sha "$RO")" = "$EXPECTED_RO_SHA" ] || { echo "STOP: RO core changed after restart"; exit 2; }
[ "$(git -C "$REPO" rev-parse HEAD)" = "$CANON_HEAD" ] || { echo "STOP: canonical HEAD changed after restart"; exit 2; }
[ "$(git -C "$REPO" rev-parse refs/remotes/origin/master)" = "$ORIGIN_HEAD" ] || { echo "STOP: origin/master changed after restart"; exit 2; }
[ "$(git -C "$REPO" status --porcelain)" = "$CANON_STATUS" ] || { echo "STOP: canonical status changed after restart"; exit 2; }

COMMITTED=1
echo "GENERIC_WRITE_SHA=$GEN_SHA"
echo "ROUTER_SHA_AFTER=$NEW_ROUTER_SHA"
echo "GENERIC_WRITE_LANE_INSTALLED=YES"
echo "RO_CORE_PRESERVED=YES"
echo "PUBLISHER_BOUNDARY=TRUSTED_NON_LLM"
echo "SUPPORTED_WRITE_PROFILES=FIX_SCOPED_BUG,APPLY_EXISTING_UNIT"
echo "PUSH_DEPLOY=NEVER"
echo "INSTALL_RESULT=PASS"
