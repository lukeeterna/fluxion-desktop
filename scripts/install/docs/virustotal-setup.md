# VirusTotal Pre-Release Gate — Founder Setup

Workflow: `.github/workflows/virustotal-gate.yml` (S184 α.3.0-D)

## One-time setup (5 min, ZERO COSTS)

### 1. Create VT account
- Visit https://www.virustotal.com/gui/sign-up
- Use `fluxion.gestionale@gmail.com` (consistent with Sentry, Resend)
- Confirm email

### 2. Get API key
- After login → click avatar (top right) → **API key**
- Copy the long alphanumeric string

### 3. Add as GitHub secret
- Visit https://github.com/lukeeterna/fluxion-desktop/settings/secrets/actions
- Click **New repository secret**
- Name: `VT_API_KEY`
- Value: paste the API key
- **Save**

## Free tier limits (current FLUXION usage compatible)

| Limit | Free tier | FLUXION need |
|-------|-----------|--------------|
| Lookup requests | 4/min, 500/day | ~5 per release × 2 releases/month = 10/mo |
| Upload (file ≤32MB) | included | MSI ~70MB → hash lookup only |
| Upload (file >32MB) | manual via web UI | DMG/MSI require manual first-time upload |

## How the gate works

1. Trigger: `workflow_dispatch` (manual) or `workflow_call` from `release-full.yml`
2. Downloads release artifacts from latest GitHub release
3. Computes SHA256, queries VT v3 `/files/{hash}` (no upload, unlimited)
4. **If known** → checks detection count; fails if > 2 (default)
5. **If unknown ≤32MB** → uploads for fresh scan (rate-limited)
6. **If unknown >32MB** → emits warning, blocks release until manual upload

## Manual large-file upload (when needed)

For DMG/MSI ≥32MB on first scan:

1. Download the artifact locally from GitHub Release
2. Visit https://www.virustotal.com/gui/home/upload
3. Drag-drop the file → wait ~3 min for scan
4. Re-trigger the workflow:
   ```
   gh workflow run virustotal-gate.yml --field release_tag=v1.0.1
   ```
   (now hash is in VT DB → gate proceeds normally)

## When the gate fails (>2 detections)

The workflow auto-creates a GitHub issue tagged `release-blocker` `P0`.

**Action sequence**:
1. Identify which AV vendors flagged (workflow logs show top 5)
2. Submit false-positive appeals using `av-submission-guide.md` templates
3. **DO NOT promote release** to landing/auto-update until appeals approved
4. Track appeal turnaround (typical 24-72h for Defender, longer for Norton)

## Tuning detection threshold

Default `VT_MAX_DETECTIONS=2` is industry-standard for unsigned executables.

To override (e.g. during initial appeals when 3-4 vendors flag while we wait):
```
gh workflow run virustotal-gate.yml \
  --field release_tag=v1.0.1 \
  --field max_detections=4
```

**Never** set `max_detections > 5` for a public release — beyond that means
the binary is genuinely suspicious and needs investigation, not threshold tuning.

## Cost ceiling

Free tier limits guarantee ZERO COSTS for FLUXION expected volume:
- 2 releases/month × 5 artifacts each × 2 lookup retries = 20 lookups/month
- vs free quota: 500/day × 30 days = 15,000/month

We have **750× headroom** before paid tier ($35/mo) becomes relevant.
