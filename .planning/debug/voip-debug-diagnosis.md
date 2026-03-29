# SIP Inbound INVITE Debug - Root Cause Analysis

## Status: ROOT CAUSE FOUND - 3 Compounding NAT Traversal Bugs

## The Problem

Incoming SIP calls to 0972536918 never reach Sara. Callers hear "occupato" (busy).
REGISTER succeeds (200 OK), STUN works, but ZERO INVITE packets arrive at the pipeline.

---

## Root Cause: Three Compounding Bugs in voice-agent/src/voip.py

### BUG 1 (CRITICAL): Symmetric NAT Defeats STUN Port Discovery

**Location:** `_stun_discover()` (line 264) + `_build_contact_header()` (line 399)

**Mechanism:**
```
STUN request:  local:5080 --> stun.voip.vivavox.it:3478
               NAT mapping A: 192.168.1.2:5080 <-> 151.26.24.125:5080 (for STUN server)

REGISTER:      local:5080 --> sip.vivavox.it:5060
               NAT mapping B: 192.168.1.2:5080 <-> 151.26.24.125:5081 (for SIP server)
                                                                 ^^^^
                                                     DIFFERENT PORT on symmetric NAT!

Contact header says: sip:0972536918@151.26.24.125:5080
SIP server sees us at:                             :5081
SIP server sends INVITE to:                        :5080 (from Contact)
NAT drops it: no pinhole for :5080 from SIP server
```

On symmetric NAT (most consumer routers), each unique destination gets a different external port.
STUN tells us the mapping for the STUN server, not for the SIP server. The Contact header
advertises the wrong port.

### BUG 2 (CRITICAL): rport/received From REGISTER Response Ignored

**Location:** `_handle_register_response()` (line 503-520)

The code correctly requests `rport` in the Via header (line 397):
```
Via: SIP/2.0/UDP 151.26.24.125:5080;branch=z9hG4bK...;rport
```

The SIP server responds with the ACTUAL observed source address in Via:
```
Via: SIP/2.0/UDP 151.26.24.125:5080;branch=z9hG4bK...;rport=5081;received=151.26.24.125
```

But `_handle_register_response()` only checks status codes (200/401). It **never parses
rport or received** from the response Via header. This is RFC 3581, the standard SIP
mechanism for NAT traversal, and it is completely wasted.

**This is the key fix:** After the first REGISTER 200 OK, parse rport/received from the Via
header and use those values in subsequent Contact headers. This gives us the EXACT port
the SIP server sees, regardless of NAT type.

### BUG 3 (CRITICAL): No NAT Keepalive Between Re-Registrations

**Location:** `_register_loop()` (line 911-916)

Re-registration interval: every 270 seconds (300 - 30).
Consumer router UDP NAT timeout: typically 30-60 seconds.

Between re-registrations, the NAT mapping expires and **all inbound packets are silently
dropped**. Even if bugs 1 and 2 were fixed, calls would only work in a ~60 second window
after each REGISTER.

**Standard fix:** Send CRLF keepalive every 15-25 seconds to the SIP server.
This refreshes the NAT mapping without generating SIP traffic. (RFC 5626, Section 4.4.1)

---

## Combined Effect

```
Timeline:
  T=0s:   REGISTER sent, NAT pinhole opens for sip.vivavox.it
  T=0.1s: REGISTER 200 OK received (but rport ignored = wrong Contact)
  T=30s:  NAT mapping starts expiring (router-dependent)
  T=60s:  NAT mapping DEAD - all inbound packets dropped
  T=270s: Re-REGISTER refreshes pinhole briefly
  T=330s: NAT mapping dead again
  ...repeat forever, calls almost never get through
```

Even in the brief window when NAT is open, the INVITE goes to the STUN-discovered port
(bug 1), not the actual NAT-mapped port for the SIP server. So it NEVER works.

---

## Fix Implementation

### Fix 1: Parse rport/received from REGISTER 200 OK

In `_handle_register_response()`, after confirming 200 OK, add rport/received parsing:

```python
async def _handle_register_response(self, msg: SIPMessage):
    """Handle REGISTER response."""
    if msg.status_code == 200:
        self._registered = True

        # --- FIX: Parse rport/received from Via for NAT traversal (RFC 3581) ---
        via = msg.headers.get("Via", "")
        if "rport=" in via:
            try:
                rport = int(via.split("rport=")[1].split(";")[0].split(",")[0].strip())
                self._cached_public_port = rport
                logger.info(f"NAT: SIP server sees us on port {rport} (rport)")
            except (ValueError, IndexError):
                pass
        if "received=" in via:
            try:
                received = via.split("received=")[1].split(";")[0].split(",")[0].strip()
                self._cached_public_ip = received
                logger.info(f"NAT: SIP server sees us at IP {received} (received)")
            except IndexError:
                pass
        # --- END FIX ---

        logger.info("SIP registration successful")
    elif msg.status_code == 401:
        # ... existing auth code unchanged ...
```

### Fix 2: Contact header automatically updated

The existing `_build_contact_header()` already reads `_cached_public_port` and
`_cached_public_ip`, so Fix 1 automatically flows through to subsequent REGISTER
refreshes and all SIP headers.

### Fix 3: Add CRLF NAT Keepalive

New method in SIPClient:

```python
async def _keepalive_loop(self):
    """Send CRLF keepalive to maintain NAT mapping (RFC 5626 Section 4.4.1).

    Consumer routers expire UDP NAT mappings in 30-60 seconds.
    We send CRLF every 20 seconds to keep the pinhole open.
    """
    while self._running:
        await asyncio.sleep(20)
        if self._running and self._socket:
            try:
                self._socket.sendto(
                    b"\r\n\r\n",
                    (self.config.server, self.config.port)
                )
                logger.debug("NAT keepalive sent")
            except OSError as e:
                logger.warning(f"NAT keepalive failed: {e}")
```

Start in `start()` after registration:
```python
# After: self._register_task = asyncio.create_task(self._register_loop())
self._keepalive_task = asyncio.create_task(self._keepalive_loop())
```

Stop in `stop()`:
```python
if self._keepalive_task:
    self._keepalive_task.cancel()
```

Initialize in `__init__`:
```python
self._keepalive_task: Optional[asyncio.Task] = None
```

---

## Additional Checks

### Router SIP ALG (CHECK THIS FIRST)
Many consumer routers have "SIP ALG" that rewrites SIP packets and BREAKS VoIP.
Check router admin panel and **DISABLE SIP ALG**.

### iMac Firewall
```bash
ssh imac "sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate"
```

### tcpdump Verification (after fixes)
```bash
ssh imac "sudo tcpdump -i any udp port 5080 -c 20 -nn"
# Then call 0972536918 -- should see INVITE packets arriving
```

### Port Forwarding (Nuclear Option)
If symmetric NAT + rport still fails: static port forward on router
external UDP 5080 -> 192.168.1.2:5080. Bypasses NAT entirely.

---

## Priority Order

1. **Fix 3 (CRLF keepalive)** - Easiest, highest impact
2. **Fix 1 (rport parsing)** - Correct port for symmetric NAT
3. **Disable SIP ALG on router** - Can cause bizarre failures
4. **Port forwarding** - Only if all else fails

---

## Verification Plan

1. Restart voice pipeline on iMac
2. Logs: "NAT keepalive sent" every 20 seconds
3. Logs: "NAT: SIP server sees us on port XXXX" after REGISTER
4. Wait 2+ minutes (verify keepalive sustains NAT mapping)
5. Call 0972536918 from a phone
6. Logs: "SIP << INVITE from ..."
7. Caller hears ringing, then Sara greeting

---

## Files to Modify

- `voice-agent/src/voip.py`:
  - `__init__()` - Add `_keepalive_task` field
  - `_handle_register_response()` - Parse rport/received from Via header
  - New `_keepalive_loop()` method
  - `start()` - Launch keepalive task
  - `stop()` - Cancel keepalive task
