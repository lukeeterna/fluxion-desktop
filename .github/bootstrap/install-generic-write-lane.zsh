#!/bin/zsh
set -euo pipefail

EXPECTED_OS="11.7.10"
EXPECTED_BASE="63b1b10637c2fa1acfcb03c94e930b71088d9221"
EXPECTED_ROUTER_SHA="318021ca9ef20a95013640fddf83709d5323b406f559c54f63a83e2aaa842066"
EXPECTED_RO_SHA="563abeccf36ef3de2973fabdfbf1b75c7d34d2347872b9b098e40e63d40b26a9"
EXPECTED_GENERIC_SRC_SHA="9a2ce8cdf594f104309f54ec488995af4631f75c5203b6dbe3d605bbafa4f154"
EXPECTED_ROUTER_SRC_SHA="c33798d39023558918636674d5192ba702565f70b9f21d2589e4a9acb824adae"

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
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP="$EXEC.pre-generic-write-$STAMP"

sha(){ shasum -a 256 "$1" | awk '{print $1}'; }

echo "=== FLUXION GENERIC WRITE LANE BOOTSTRAP ==="

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

RO_SHA="$(sha "$RO")"
ROUTER_SHA="$(sha "$EXEC")"
echo "RO_CORE_SHA=$RO_SHA"
echo "ROUTER_SHA_BEFORE=$ROUTER_SHA"
[ "$RO_SHA" = "$EXPECTED_RO_SHA" ] || { echo "STOP: RO core SHA inatteso"; exit 2; }
[ "$ROUTER_SHA" = "$EXPECTED_ROUTER_SHA" ] || { echo "STOP: router SHA inatteso"; exit 2; }

[ ! -e "$REPO/vos/STOP" ] || { echo "STOP: vos/STOP present"; exit 2; }
CANON_HEAD="$(git -C "$REPO" rev-parse HEAD)"
ORIGIN_HEAD="$(git -C "$REPO" rev-parse refs/remotes/origin/master)"
CANON_STATUS="$(git -C "$REPO" status --porcelain)"
[ "$CANON_HEAD" = "$EXPECTED_BASE" ] || { echo "STOP: canonical HEAD mismatch"; exit 2; }
[ "$ORIGIN_HEAD" = "$EXPECTED_BASE" ] || { echo "STOP: origin/master mismatch"; exit 2; }

cp -p "$EXEC" "$BACKUP"
echo "ROUTER_BACKUP=$BACKUP"

install -m 700 "$GEN_SRC" "$GEN"
install -m 700 "$ROUTER_SRC" "$EXEC"

/bin/zsh -n "$GEN"
python3 -m py_compile "$EXEC"

GEN_SHA="$(sha "$GEN")"
NEW_ROUTER_SHA="$(sha "$EXEC")"
echo "GENERIC_WRITE_SHA=$GEN_SHA"
echo "ROUTER_SHA_AFTER=$NEW_ROUTER_SHA"
[ "$GEN_SHA" = "$EXPECTED_GENERIC_SRC_SHA" ] || { echo "STOP: installed generic SHA mismatch"; exit 2; }
[ "$NEW_ROUTER_SHA" = "$EXPECTED_ROUTER_SRC_SHA" ] || { echo "STOP: installed router SHA mismatch"; exit 2; }

date -u +%Y-%m-%dT%H:%M:%SZ > "$ROOT/generic-write-activated-at.txt"
chmod 600 "$ROOT/generic-write-activated-at.txt"

[ "$(git -C "$REPO" rev-parse HEAD)" = "$CANON_HEAD" ] || { echo "STOP: canonical HEAD mutated"; exit 2; }
[ "$(git -C "$REPO" rev-parse refs/remotes/origin/master)" = "$ORIGIN_HEAD" ] || { echo "STOP: origin/master changed"; exit 2; }
[ "$(git -C "$REPO" status --porcelain)" = "$CANON_STATUS" ] || { echo "STOP: canonical status changed"; exit 2; }

cat > "$ROOT/generic-write-lane-install-$STAMP.txt" <<EOF
installed_at=$STAMP
base=$EXPECTED_BASE
ro_core_sha=$RO_SHA
router_sha_before=$ROUTER_SHA
router_sha_after=$NEW_ROUTER_SHA
generic_write_sha=$GEN_SHA
router_backup=$BACKUP
profiles=FIX_SCOPED_BUG,APPLY_EXISTING_UNIT
publisher_boundary=trusted-non-llm
claude_keychain_access=never
canonical_repo_unchanged=yes
EOF
chmod 600 "$ROOT/generic-write-lane-install-$STAMP.txt"

launchctl kickstart -k "$DOMAIN/$LABEL"
sleep 2
launchctl print "$DOMAIN/$LABEL" 2>/dev/null | grep -E 'state =|runs =|last exit code|program =' || true

echo "GENERIC_WRITE_LANE_INSTALLED=YES"
echo "RO_CORE_PRESERVED=YES"
echo "PUBLISHER_BOUNDARY=TRUSTED_NON_LLM"
echo "CLAUDE_KEYCHAIN_ACCESS=NEVER"
echo "SUPPORTED_WRITE_PROFILES=FIX_SCOPED_BUG,APPLY_EXISTING_UNIT"
echo "PUSH_DEPLOY=NEVER"
echo "INSTALL_RESULT=PASS"
