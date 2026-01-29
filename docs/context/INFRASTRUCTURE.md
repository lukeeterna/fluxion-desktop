# Fluxion Infrastructure

## Machines

```yaml
MacBook:
  os: macOS Big Sur (11.x)
  python: 3.13
  role: Development only (Tauri crashes on Big Sur)
  path: /Volumes/MontereyT7/FLUXION

iMac:
  host: imac (192.168.1.9)
  os: macOS Monterey (12.7.4)
  python: 3.9.6 (venv)
  role: Runtime, testing, E2E
  path: /Volumes/MacSSD - Dati/fluxion

Windows PC:
  host: 192.168.1.17
  path: C:\Users\gianluca\fluxion
  role: Cross-platform testing
```

## Ports

| Service | Port | Description |
|---------|------|-------------|
| HTTP Bridge (Tauri) | 3001 | Rust backend for voice agent |
| Voice Pipeline (Python) | 3002 | Python NLU/TTS/STT server |
| MCP Server | 5000 | Claude Code integration |
| Vite Dev Server | 1420 | Frontend dev |

## Environment Variables

```bash
GROQ_API_KEY=org_01k9jq26w4f2e8hfw9tmzmz556
GITHUB_TOKEN=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
KEYGEN_ACCOUNT_ID=b845d2ed-92a4-4048-b2d8-ee625206a5ae
VOIP_SIP_USER=DXMULTISERVICE
VOIP_SIP_SERVER=sip.ehiweb.it
TTS_ENGINE=chatterbox
TTS_FALLBACK=piper
TTS_VOICE_NAME=Sara
WHATSAPP_PHONE=393281536308
```

## Sync Workflow

```
1. Modify on MacBook
2. git push origin feat/workflow-tools
3. ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && git pull"
4. Restart services if Python/Rust changed
5. Test on iMac
```

## Service Management

```bash
# Check services
ssh imac "lsof -i :3001"  # HTTP Bridge
ssh imac "lsof -i :3002"  # Voice Pipeline

# Restart voice pipeline
ssh imac "kill $(lsof -ti:3002); cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && source venv/bin/activate && nohup python main.py > /tmp/voice-pipeline.log 2>&1 &"

# Health check
curl -s http://192.168.1.9:3002/health | python3 -m json.tool
```

## CI/CD

| Workflow | File | Trigger |
|----------|------|---------|
| Test Suite | `test-suite.yml` | push develop, PR main |
| E2E Tests | `e2e-tests.yml` | manual, schedule |
| Release | `release.yml` | tag v* |
| Release Full | `release-full.yml` | manual |

## Performance SLA

| Layer | Operation | Target |
|-------|-----------|--------|
| L0 | Regex match | <1ms |
| L1 | Intent (spaCy) | <5ms |
| L2 | Slot filling | <10ms |
| L3 | FAISS search | <50ms |
| L4 | Groq LLM | <500ms |
| E2E | Voice in->out | <2000ms |
