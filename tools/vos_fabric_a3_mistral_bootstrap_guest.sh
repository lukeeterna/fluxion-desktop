#!/usr/bin/env bash
# Run only inside the isolated vos-worker. Installs pinned bootstrap tooling and
# Mistral Vibe without any inference/model call. Account billing eligibility is
# deliberately not inferred from local files.
set -euo pipefail
export LC_ALL=C LANG=C
: "${VOS_PROXY_PORT:?}" "${UV_VERSION:?}" "${UV_INSTALLER_SHA256:?}" "${VIBE_VERSION:?}" "${VIBE_WHEEL_SHA256:?}"

export HTTPS_PROXY="http://192.168.64.1:${VOS_PROXY_PORT}"
export HTTP_PROXY="$HTTPS_PROXY"
export https_proxy="$HTTPS_PROXY"
export http_proxy="$HTTPS_PROXY"
export PATH="$HOME/.local/bin:$PATH"

echo A3_INFERENCE_CALLS=0
echo A3_MAX_COST_USD=0
echo A3_PAID_API_FALLBACK=0

tmp="$(mktemp -d -t vos-a3-bootstrap.XXXXXX)"
trap 'rm -rf "$tmp"' EXIT INT TERM

curl -LsSf --retry 4 --retry-delay 2 \
  "https://astral.sh/uv/${UV_VERSION}/install.sh" -o "$tmp/uv-install.sh"
actual_uv_installer="$(sha256sum "$tmp/uv-install.sh" | awk '{print $1}')"
[ "$actual_uv_installer" = "$UV_INSTALLER_SHA256" ] || {
  echo A3_BOOTSTRAP_BLOCKED=UV_INSTALLER_SHA_MISMATCH
  exit 2
}
sh "$tmp/uv-install.sh" >/dev/null
export PATH="$HOME/.local/bin:$PATH"
uv --version | grep -F "uv ${UV_VERSION}" >/dev/null || {
  echo A3_BOOTSTRAP_BLOCKED=UV_VERSION_DRIFT
  exit 2
}
echo "A3_UV_VERSION=$(uv --version | head -1)"
echo "A3_UV_BINARY_SHA256=$(sha256sum "$(command -v uv)" | awk '{print $1}')"

curl -LsSf --retry 4 --retry-delay 2 \
  "https://pypi.org/pypi/mistral-vibe/${VIBE_VERSION}/json" -o "$tmp/pypi.json"
python3 - "$tmp/pypi.json" "$VIBE_WHEEL_SHA256" "$tmp/wheel-url" <<'PY'
import json, sys
metadata_path, expected, output_path = sys.argv[1:]
with open(metadata_path, encoding="utf-8") as handle:
    data = json.load(handle)
version = data.get("info", {}).get("version")
expected_name = "mistral_vibe-%s-py3-none-any.whl" % version
matches = [
    item for item in data.get("urls", [])
    if item.get("packagetype") == "bdist_wheel"
    and item.get("filename") == expected_name
]
if len(matches) != 1:
    raise SystemExit("wheel metadata not unique")
item = matches[0]
if item.get("digests", {}).get("sha256") != expected:
    raise SystemExit("PyPI digest mismatch")
if item.get("yanked"):
    raise SystemExit("wheel is yanked")
with open(output_path, "w", encoding="utf-8") as handle:
    handle.write(item["url"])
print("A3_PYPI_VERSION=" + str(version))
print("A3_PYPI_WHEEL_DIGEST=GREEN")
PY
curl -LsSf --retry 4 --retry-delay 2 "$(cat "$tmp/wheel-url")" \
  -o "$tmp/mistral_vibe-${VIBE_VERSION}-py3-none-any.whl"
actual_wheel="$(sha256sum "$tmp/mistral_vibe-${VIBE_VERSION}-py3-none-any.whl" | awk '{print $1}')"
[ "$actual_wheel" = "$VIBE_WHEEL_SHA256" ] || {
  echo A3_BOOTSTRAP_BLOCKED=VIBE_WHEEL_SHA_MISMATCH
  exit 2
}
echo A3_VIBE_WHEEL_SHA256=GREEN

# uv provisions an isolated Python >=3.12 for the tool; host/guest system Python is
# left unchanged. Network remains behind the VOS-authorized ephemeral CONNECT relay.
uv tool install "$tmp/mistral_vibe-${VIBE_VERSION}-py3-none-any.whl" \
  --python 3.12 --force >/dev/null
vibe --version | grep -F "$VIBE_VERSION" >/dev/null || {
  echo A3_BOOTSTRAP_BLOCKED=VIBE_VERSION_DRIFT
  exit 2
}
echo "A3_VIBE_VERSION=$(vibe --version | head -1)"
echo "A3_VIBE_ENTRYPOINT_SHA256=$(sha256sum "$(command -v vibe)" | awk '{print $1}')"
echo "A3_VIBE_PYTHON_SHEBANG=$(head -1 "$(command -v vibe)")"

help_text="$(vibe --help 2>&1 || true)"
for flag in --prompt --resume --max-turns --enabled-tools --output --trust; do
  printf '%s\n' "$help_text" | grep -F -- "$flag" >/dev/null || {
    echo "A3_BOOTSTRAP_BLOCKED=MISSING_FLAG_${flag#--}"
    exit 2
  }
done

echo A3_PROGRAMMATIC_SURFACE=GREEN
echo A3_ACCOUNT_PLAN=UNKNOWN
echo A3_PAYG_OFF_PROVEN=0
echo A3_INFERENCE_CALLS=0
echo A3_BOOTSTRAP=GREEN
echo A3=BLOCKED_ACCOUNT_PLAN_EVIDENCE
