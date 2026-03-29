---
status: diagnosed
trigger: "URGENT: Debug why incoming SIP calls don't reach Sara on iMac despite successful SIP REGISTER"
created: 2026-03-28T00:00:00Z
updated: 2026-03-28T00:00:00Z
---

## Current Focus

hypothesis: THREE compounding NAT traversal bugs prevent inbound INVITE from reaching Sara
test: Code review of voip.py + SIP/NAT protocol analysis
expecting: Confirmed root causes with specific code fixes
next_action: Implement fixes in voip.py

## Symptoms

expected: Incoming calls to 0972536918 reach Sara voice pipeline on iMac
actual: Callers hear "occupato" (busy). ZERO INVITE packets in pipeline log.
errors: No errors visible - packets silently dropped by NAT
reproduction: Call 0972536918 from any phone
started: Always broken for inbound calls. REGISTER works, INVITE never arrives.

## Eliminated

- hypothesis: SIP socket not bound / not listening
  evidence: Socket bound to 0.0.0.0:5080 (line 389), receive loop running (line 448-468)
  timestamp: 2026-03-28

- hypothesis: INVITE handler code bug
  evidence: _handle_invite at line 549 is structurally correct - it parses From, creates CallSession, etc. The problem is packets never reach the socket.
  timestamp: 2026-03-28

## Evidence

- timestamp: 2026-03-28
  checked: Socket creation (line 378-390)
  found: Binds 0.0.0.0:5080, SO_REUSEADDR, timeout 0.5s
  implication: Local listening is correct

- timestamp: 2026-03-28
  checked: STUN discovery (line 264-345)
  found: Uses SIP socket, sends to stun.voip.vivavox.it:3478, discovers 151.26.24.125:5080
  implication: STUN mapping goes to STUN server, not SIP server. On symmetric NAT, the SIP server mapping will have a DIFFERENT external port.

- timestamp: 2026-03-28
  checked: Contact header (line 399-403)
  found: Uses STUN-discovered IP:port (151.26.24.125:5080) in Contact header
  implication: If symmetric NAT assigns different port for sip.vivavox.it destination, Contact header advertises wrong port

- timestamp: 2026-03-28
  checked: REGISTER response handling (line 503-520)
  found: Only checks 200/401 status. IGNORES rport and received parameters from Via header in response.
  implication: Even though Via includes ;rport (line 397) requesting the server to report observed address, the response is never parsed. The actual port the SIP server sees is discarded.

- timestamp: 2026-03-28
  checked: NAT keepalive mechanism
  found: NONE. Only re-registration every 270s (line 914). No CRLF keepalive, no OPTIONS ping.
  implication: UDP NAT mappings on consumer routers expire in 30-60s. The mapping dies long before re-registration.

- timestamp: 2026-03-28
  checked: start() flow (line 875-909)
  found: _stun_discover() called at line 888 but RETURN VALUE DISCARDED. _get_public_ip() later calls _stun_discover() AGAIN creating inconsistent state.
  implication: Minor issue but shows STUN result caching is fragile

## Resolution

root_cause: |
  THREE compounding NAT traversal bugs in voip.py prevent inbound SIP INVITE packets from reaching the iMac:

  **BUG 1 (CRITICAL): Symmetric NAT defeats STUN-based port discovery**
  The STUN Binding Request goes to stun.voip.vivavox.it:3478, but REGISTER goes to sip.vivavox.it:5060.
  On a symmetric NAT (common on consumer routers), each unique (dest_ip, dest_port) gets a DIFFERENT
  external port mapping. So STUN discovers port 5080, but the actual mapping for sip.vivavox.it might
  be port 5081 or 5082. The Contact header advertises 151.26.24.125:5080, but the SIP proxy sees traffic
  from :5081 and sends INVITE to :5080 which has no matching NAT pinhole.

  **BUG 2 (CRITICAL): rport/received from REGISTER 200 OK is ignored**
  The Via header correctly requests rport (line 397), so the SIP server responds with the actual observed
  source IP:port in the Via header (e.g., "received=151.26.24.125;rport=5081"). But _handle_register_response()
  (line 503-520) only checks status codes - it NEVER parses rport/received to update the Contact header.
  This is the SIP standard mechanism for NAT traversal (RFC 3581) and it's completely unused.

  **BUG 3 (CRITICAL): No NAT keepalive between re-registrations**
  Re-registration happens every 270 seconds (line 914). Consumer router NAT mappings for UDP typically
  expire in 30-60 seconds. Between re-registrations, the NAT pinhole closes and ALL inbound packets
  (including INVITE) are silently dropped. A keepalive (CRLF or OPTIONS) must be sent every 15-25 seconds.

  **Combined effect:** Even if bugs 1 and 2 were fixed, bug 3 means the NAT pinhole closes after ~60 seconds,
  making inbound calls work only in a brief window after each REGISTER. All three must be fixed together.

  **Why callers hear "occupato" (busy):** The SIP proxy (sip.vivavox.it) sends INVITE to the Contact address.
  The packet is dropped by NAT. After timeout (~32 seconds), the proxy gives up and returns 480/408 to the
  calling party's carrier, which the PSTN maps to a busy tone.

fix: |
  See /tmp/voip-debug.md for complete fix implementation.

verification: |
  Not yet verified - diagnosed only.

files_changed:
  - voice-agent/src/voip.py
