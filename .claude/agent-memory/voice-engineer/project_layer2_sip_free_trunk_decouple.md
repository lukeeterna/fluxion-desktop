---
name: Layer 2 audio test via free SIP trunk (decouple from EHIWEB 403) — S340
description: Path to test Sara Layer 2 (real voice answer) without EHIWEB. Loopback is structurally dead (see project_sip_loopback_crash_pjsip216.md); hypothesis is that a network trunk dilutes the media-thread race. Chosen trunk = sip.linphone.org (Flexisip free). BLOCKED-ON Luke creating 2 free SIP accounts (portal needs SMS/email verification, not scriptable).
type: project
---

## Decision (S340, 2026-06-04)
- **Chosen free trunk: `sip.linphone.org`** — Belledonne Flexisip free SIP service.
  - Verified real: DNS SRV `_sip._udp.sip.linphone.org` → `sip11/sip12.linphone.org:5060` (UDP+TCP). Portal `subscribe.linphone.org` = "Linphone Free SIP Service... powered by Flexisip proxy, HA" (796k users, no SLA). Standard RFC 3261 registrar usable by pjsua2.
  - Supports inbound+outbound audio between domain users → harness (account #2) can call Sara (account #1). Zero cost.
- **Why this path**: loopback 127.0.0.1 crashes structurally (pjsua2 conference port-add on media thread → group-lock SIGABRT, version+config independent, 3 cycles S336-S338). Provider calls (S244) did NOT crash → network timing dilutes the race. A free network trunk reproduces that benign timing without needing EHIWEB (403 BLOCKED-ON provider).

## How to configure (NO hardcode — env only)
`SIPConfig.from_env()` at `src/voip_pjsua2.py:179` reads everything from env. To switch trunk set in `voice-agent/.env`:
```
VOIP_SIP_SERVER=sip.linphone.org
VOIP_SIP_PORT=5060
VOIP_SIP_USER=<account1_sara>
VOIP_SIP_PASS=<pass1>
```
IMPORTANT also neutralize STUN: `SIPConfig.stun_server` defaults to `stun.voip.vivavox.it:3478` (hardcoded default at line ~169, NO env override exists for it!). The S340 log showed STUN timeouts to vivavox blocking. Either add a `VOIP_STUN_SERVER` env read or point stun to `stun.linphone.org` / empty. Check if stun_server has an env hook before assuming.
Backup before editing .env: done S340 = `voice-agent/.env.bak-PRE-S340-20260604-172511` (496B, mode 600).

## BLOCKED-ON Luke (external, not a tech loop)
Create 2 free accounts `@sip.linphone.org` via `subscribe.linphone.org` (SPA) or Linphone app. Registration needs SMS/email verification + interactive form → NOT scriptable from SSH. Need username+password for both (one for Sara, one for harness/caller).

## When credentials arrive — one-shot test plan
1. Edit .env (server/user/pass above) + fix STUN. Restart pipeline.
2. `curl http://192.168.1.2:3002/api/voice/voip/status` → expect `registered:true, reg_status:200`.
3. Harness `scripts/sara_audio_harness.py` (committed, CORRECT, do NOT modify) from account #2 calls Sara. WAV TX "Buongiorno, vorrei prenotare un appuntamento" (PCM16 8kHz mono: `say -o raw.aiff` + `afconvert -f WAVE -d LEI16@8000 -c 1`).
4. Verify: Sara no crash → 200 OK → audio bridge → capture Sara RTP reply WAV (dur>0) → transcribe → check pertinence.

## State at S340 close
- Pipeline PID 67091 was zombie: REGISTER→403 + STUN-timeout loop to vivavox, HTTP 3002 not responding. Needs clean restart after env switch.
- No code changed. Only backup created. EHIWEB/.env NOT touched (gated on credentials).
