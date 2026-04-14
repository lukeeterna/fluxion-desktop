# S154 Audit — Critical Blockers

## 🔴 Blocker 1: Auto-Update Not Wired to GitHub Releases

**Status**: CONFIRMED  
**File**: `src-tauri/tauri.conf.json`  
**Issue**: Missing `updater` section with GitHub Releases endpoint

**Current state**:
```json
{
  "productName": "Fluxion",
  "version": "1.0.0",
  // ... NO updater config
}
```

**Fix required**:
```json
{
  "updater": {
    "active": true,
    "endpoints": ["https://api.github.com/repos/gianlucanewtech/fluxion/releases/download/latest/manifest.json"],
    "dialog": true,
    "pubkey": "c61b3c912cf953e06db979e54b72602da9e3e3cea9554e67a2baa246e7e67d39"
  }
}
```

Plus: GitHub Actions workflow to sign and publish releases.

**Impact**: Users cannot auto-update; must download DMG/MSI manually.

---

## 🔴 Blocker 2: Voice Pipeline No Auto-Restart

**Status**: CONFIRMED  
**Scope**: iMac 192.168.1.2, port 3002

**Current state**:
- ✅ Voice pipeline has `/health` endpoint (responds 200)
- ✅ Tauri app polls it every 30 seconds
- ❌ If process dies → stuck offline
- ❌ No LaunchAgent / systemd wrapper
- ❌ No health-check-triggered restart daemon

**Impact**: Sara unavailable until user SSH's to iMac and manually restarts.

**Solution**: Create watchdog daemon
- Option A (macOS): LaunchAgent that monitors HTTP 127.0.0.1:3002
- Option B (any OS): Tauri command `check_voice_pipeline_health()` that restarts on failure

---

## Non-Blockers (for reference)

- Lighthouse image optimization (P2)
- HTTP Bridge hard-coded bind address (P3)
- Documentation of startup sequence (P1)
