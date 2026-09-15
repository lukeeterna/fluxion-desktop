#!/usr/bin/env bash
# One-time founder gate for VOS Fabric A2 direct official Antigravity auth.
# Run interactively on the iMac only. It does not read/print stored credentials.
set -euo pipefail
export LC_ALL=C LANG=C

fail(){ printf 'A2_AUTH_ONCE_BLOCKED=%s\n' "$*" >&2; exit 2; }
[ "$(uname -s)" = "Darwin" ] || fail IMAC_DARWIN_REQUIRED

MP=""
for c in "$(command -v multipass 2>/dev/null||true)" /usr/local/bin/multipass /opt/homebrew/bin/multipass "/Library/Application Support/com.canonical.multipass/bin/multipass"; do
  [ -z "$c" ] || [ ! -x "$c" ] || { MP="$c"; break; }
done
[ -n "$MP" ] || fail MULTIPASS_MISSING
"$MP" info vos-worker >/dev/null 2>&1 || fail VOS_WORKER_MISSING
owner="$($MP exec vos-worker -- sh -c 'cat /var/lib/vos-fabric/worker-owner 2>/dev/null||true')"
[ "$owner" = "VOS_FABRIC_G2" ] || fail "UNEXPECTED_OWNER_$owner"
"$MP" info vos-worker | grep -q 'State:[[:space:]]*Running' || "$MP" start vos-worker

GUEST_IP="$($MP exec vos-worker -- hostname -I | awk '{print $1}')"
[ "$GUEST_IP" = "192.168.64.3" ] || fail "UNEXPECTED_GUEST_IP_$GUEST_IP"
ifconfig bridge100 | grep -q 'inet 192\.168\.64\.1 ' || fail BRIDGE100_MISSING

"$MP" exec vos-worker -- sh -lc 'test -x "$HOME/.local/bin/agy"' || fail AGY_NOT_INSTALLED
"$MP" exec vos-worker -- sh -lc 'mkdir -p "$HOME/.gemini/antigravity-cli"; python3 - <<"PY"
import json, os
p=os.path.expanduser("~/.gemini/antigravity-cli/settings.json")
d={}
if os.path.exists(p):
    with open(p,encoding="utf-8") as f:d=json.load(f)
d.pop("modelProvider",None)
d["useG1Credits"]=False
q=p+".tmp"
with open(q,"w",encoding="utf-8") as f:json.dump(d,f,sort_keys=True,indent=2);f.write("\n")
os.chmod(q,0o600);os.replace(q,p)
PY'

PORT=$((28000 + $$ % 7000))
PROXY="$(mktemp -t vos-a2-auth-proxy.XXXXXX.py)"
LOG="$(mktemp -t vos-a2-auth-proxy.XXXXXX.log)"
cat >"$PROXY" <<PY
#!/usr/bin/env python3
import select,socket,socketserver
BIND=("192.168.64.1",$PORT); ALLOWED="192.168.64.3"
class H(socketserver.StreamRequestHandler):
    def handle(self):
        if self.client_address[0] != ALLOWED:return
        self.connection.settimeout(30)
        p=self.rfile.readline(8192).decode("ascii","replace").strip().split()
        if len(p)!=3 or p[0].upper()!="CONNECT" or ":" not in p[1]:return
        host,ps=p[1].rsplit(":",1)
        try:port=int(ps)
        except ValueError:return
        if port!=443:return
        while True:
            h=self.rfile.readline(8192)
            if h in (b"\r\n",b"\n",b""):break
        try:up=socket.create_connection((host,port),timeout=20)
        except OSError:return
        with up:
            up.setblocking(False);self.connection.setblocking(False)
            self.wfile.write(b"HTTP/1.1 200 Connection Established\r\n\r\n")
            socks=[self.connection,up]
            while True:
                r,_,x=select.select(socks,[],socks,120)
                if x or not r:return
                for src in r:
                    dst=up if src is self.connection else self.connection
                    try:data=src.recv(65536)
                    except OSError:return
                    if not data:return
                    try:dst.sendall(data)
                    except OSError:return
class S(socketserver.ThreadingTCPServer):allow_reuse_address=True;daemon_threads=True
with S(BIND,H) as s:
    print("READY",flush=True);s.serve_forever()
PY

/usr/bin/python3 "$PROXY" >"$LOG" 2>&1 &
PROXY_PID=$!
cleanup(){ kill "$PROXY_PID" >/dev/null 2>&1||true; rm -f "$PROXY" "$LOG"; }
trap cleanup EXIT INT TERM
for _ in 1 2 3 4 5; do grep -q '^READY$' "$LOG" 2>/dev/null && break; sleep 1; done
grep -q '^READY$' "$LOG" || fail PROXY_NOT_READY

printf '%s\n' 'A2_AUTH_ONCE=READY'
printf '%s\n' 'Google official remote OAuth will print an authorization URL.'
printf '%s\n' 'Open that URL in your browser, sign in, paste the returned code here, then type /exit after the CLI opens.'
printf '%s\n' 'No API key and no paid-credit fallback are enabled.'

set +e
"$MP" exec vos-worker -- env \
  HOME=/home/ubuntu \
  PATH=/home/ubuntu/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
  HTTPS_PROXY="http://192.168.64.1:$PORT" \
  HTTP_PROXY="http://192.168.64.1:$PORT" \
  https_proxy="http://192.168.64.1:$PORT" \
  http_proxy="http://192.168.64.1:$PORT" \
  SSH_CONNECTION='127.0.0.1 22000 127.0.0.1 22' \
  TERM="${TERM:-xterm-256color}" \
  /home/ubuntu/.local/bin/agy
RC=$?
set -e
[ "$RC" -eq 0 ] || fail "AGY_INTERACTIVE_RC_$RC"

"$MP" exec vos-worker -- env \
  HOME=/home/ubuntu \
  PATH=/home/ubuntu/.local/bin:/usr/local/bin:/usr/bin:/bin \
  HTTPS_PROXY="http://192.168.64.1:$PORT" \
  HTTP_PROXY="http://192.168.64.1:$PORT" \
  SSH_CONNECTION='127.0.0.1 22000 127.0.0.1 22' \
  timeout 60s /home/ubuntu/.local/bin/agy models >/dev/null 2>&1 \
  || fail AUTH_PERSISTENCE_CHECK_FAILED

printf '%s\n' 'A2_DIRECT_GOOGLE_AUTH=GREEN'
printf '%s\n' 'ANTIGRAVITY_CREDIT_FALLBACK=0'
printf '%s\n' 'NEXT=RUN_A2_RUNTIME_QUALIFIER'
