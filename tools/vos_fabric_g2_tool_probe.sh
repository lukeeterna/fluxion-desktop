#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C LANG=C
: "${VOS_CODEX_MODEL:=gpt-5.6-terra}"

fail(){ printf 'G2_TOOL_PROBE_BLOCKED=%s\n' "$*" >&2; exit 2; }
production_green(){
  uid="$(id -u)"
  launch_running(){
    label="$1"
    for d in "gui/$uid" "user/$uid" system; do
      launchctl print "$d/$label" 2>/dev/null | grep -Eq 'state = running|pid = [0-9]+' && return 0
    done
    launchctl list 2>/dev/null | awk -v label="$label" '$3==label && $1 ~ /^[0-9]+$/ {ok=1} END{exit ok?0:1}'
  }
  launch_running com.zeroclaw.fall-detector && \
  launch_running com.go2rtc && \
  launch_running com.mosquitto.broker && \
  curl -fsS --max-time 3 http://127.0.0.1:3002/health >/dev/null && \
  mount | grep -q ' on /Volumes/NAS_LOCAL '
}

production_green || fail PRE_PRODUCTION
MP=''
for c in "$(command -v multipass 2>/dev/null || true)" /usr/local/bin/multipass /opt/homebrew/bin/multipass "/Library/Application Support/com.canonical.multipass/bin/multipass"; do
  [ -n "$c" ] && [ -x "$c" ] && { MP="$c"; break; }
done
[ -n "$MP" ] || fail MULTIPASS_MISSING

guest_ip="$($MP exec vos-worker -- sh -c "hostname -I | awk '{print \$1}'" | tail -1)"
printf '%s\n' "$guest_ip" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$' || fail GUEST_IP
$MP exec vos-worker -- sh -c 'test -z "${OPENAI_API_KEY:-}"' >/dev/null || fail PAID_API_ENV_PRESENT
$MP exec vos-worker -- timeout 15s env CODEX_HOME=/home/ubuntu/.codex-vos-fabric /usr/local/bin/codex login status >/dev/null || fail AUTH

nonce="VOS_TOOL_PROBE_$(date +%s)_$$"
$MP exec vos-worker -- rm -rf /tmp/g2-tool-probe
$MP exec vos-worker -- mkdir -p /tmp/g2-tool-probe
printf '%s\n' "$nonce" | $MP exec vos-worker -- sh -c 'cat > /tmp/g2-tool-probe/probe.txt'
cat <<'PROMPT' | $MP exec vos-worker -- sh -c 'cat > /tmp/g2-tool-probe/prompt.txt'
Use the shell tool to run exactly this command and no other command:
cat ./probe.txt
The command must exit with status 0. You must read the file; do not infer, guess, or skip the command. After it succeeds, reply with exactly VOS_FABRIC_PING= followed immediately by the exact stdout from that command, with no other text.
PROMPT

PORT=$((25000 + $$ % 7000))
PROXY="/tmp/g2-tool-proxy-${PORT}.py"
PROXY_LOG="/tmp/g2-tool-proxy-${PORT}.log"
JSON="/tmp/g2-tool-probe-${PORT}.jsonl"
ERR="/tmp/g2-tool-probe-${PORT}.stderr"
cat > "$PROXY" <<'PY'
import os,select,socket,socketserver
bind=('192.168.64.1',int(os.environ['PORT']))
allowed=os.environ['GUEST_IP']
class H(socketserver.StreamRequestHandler):
    def handle(self):
        if self.client_address[0] != allowed: return
        p=self.rfile.readline(8192).decode('ascii','replace').strip().split()
        if len(p)!=3 or p[0].upper()!='CONNECT' or ':' not in p[1]: return
        host,ps=p[1].rsplit(':',1)
        try: port=int(ps)
        except ValueError: return
        if port!=443: return
        print('CONNECT_HOST=%s:443'%host,flush=True)
        while True:
            h=self.rfile.readline(8192)
            if h in (b'\r\n',b'\n',b''): break
        try: up=socket.create_connection((host,443),timeout=20)
        except OSError: return
        with up:
            up.setblocking(False); self.connection.setblocking(False)
            self.wfile.write(b'HTTP/1.1 200 Connection Established\r\n\r\n')
            sockets=[self.connection,up]
            while True:
                r,_,x=select.select(sockets,[],sockets,90)
                if x or not r: return
                for s in r:
                    d=up if s is self.connection else self.connection
                    try: data=s.recv(65536)
                    except OSError: return
                    if not data: return
                    try: d.sendall(data)
                    except OSError: return
class S(socketserver.ThreadingTCPServer):
    allow_reuse_address=True
    daemon_threads=True
with S(bind,H) as srv:
    print('READY=%s:%d'%bind,flush=True)
    srv.serve_forever()
PY

proxy_pid=''
cleanup(){
  [ -z "$proxy_pid" ] || kill "$proxy_pid" >/dev/null 2>&1 || true
  rm -f "$PROXY" "$PROXY_LOG" "$JSON" "$ERR"
  $MP exec vos-worker -- rm -rf /tmp/g2-tool-probe >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM
PORT="$PORT" GUEST_IP="$guest_ip" /usr/bin/python3 "$PROXY" >"$PROXY_LOG" 2>&1 & proxy_pid=$!
for _ in 1 2 3 4 5; do grep -q '^READY=' "$PROXY_LOG" 2>/dev/null && break; sleep 1; done
grep -q '^READY=' "$PROXY_LOG" || fail PROXY_NOT_READY
proxy="http://192.168.64.1:${PORT}"

set +e
$MP exec vos-worker -- env \
  CODEX_HOME=/home/ubuntu/.codex-vos-fabric \
  HTTPS_PROXY="$proxy" HTTP_PROXY="$proxy" https_proxy="$proxy" http_proxy="$proxy" \
  VOS_CODEX_MODEL="$VOS_CODEX_MODEL" \
  sh -lc 'cd /tmp/g2-tool-probe && timeout 120s /usr/local/bin/codex exec --json --sandbox read-only -c '\''approval_policy="never"'\'' --model "$VOS_CODEX_MODEL" --skip-git-repo-check - < prompt.txt' \
  >"$JSON" 2>"$ERR"
rc=$?
set -e

echo "G2_TOOL_PROBE_CODEX_RC=$rc"
python3 - "$JSON" "$nonce" <<'PY'
import json,sys
path,nonce=sys.argv[1:]
for raw in open(path,encoding='utf-8',errors='replace'):
    raw=raw.strip()
    if not raw:
        continue
    try:
        obj=json.loads(raw)
    except Exception:
        print('G2_TOOL_PROBE_NONJSON=1')
        continue
    typ=obj.get('type')
    print('G2_TOOL_PROBE_EVENT='+str(typ))
    item=obj.get('item') or {}
    if item:
        print('G2_TOOL_PROBE_ITEM_TYPE='+str(item.get('type')))
        if item.get('type')=='command_execution':
            print('G2_TOOL_PROBE_COMMAND='+str(item.get('command'))[:300])
            print('G2_TOOL_PROBE_EXIT='+str(item.get('exit_code')))
            out=str(item.get('aggregated_output') or '').replace('\n',' ')[:300]
            print('G2_TOOL_PROBE_OUTPUT='+out.replace(nonce,'<NONCE>'))
    if typ in {'turn.failed','error'}:
        def walk(x):
            if isinstance(x,dict):
                for k,v in x.items():
                    if str(k).lower() in {'message','code','reason','type'} and isinstance(v,(str,int,float,bool)):
                        s=str(v).replace('\n',' ')[:700].replace(nonce,'<NONCE>')
                        print('G2_TOOL_PROBE_DETAIL_%s=%s'%(str(k).upper(),s))
                    walk(v)
            elif isinstance(x,list):
                for v in x: walk(v)
        walk(obj)
PY

if [ -s "$ERR" ]; then
  echo 'G2_TOOL_PROBE_STDERR_BEGIN'
  sed -n '1,40p' "$ERR" | sed "s/${nonce}/<NONCE>/g"
  echo 'G2_TOOL_PROBE_STDERR_END'
fi
echo "G2_TOOL_PROBE_EVENTS_SHA256=$(shasum -a 256 "$JSON" | awk '{print $1}')"
echo "G2_TOOL_PROBE_STDERR_SHA256=$(shasum -a 256 "$ERR" | awk '{print $1}')"
grep -E '^(READY|CONNECT_HOST)=' "$PROXY_LOG" || true
production_green || fail POST_PRODUCTION
echo 'G2_TOOL_PROBE_PRODUCTION_REGRESSION=0'
echo "G2_TOOL_PROBE_VERDICT=CODEX_RC_${rc}"
exit 0
