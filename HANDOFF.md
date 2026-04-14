# FLUXION — Handoff Sessione 154 → 155 (2026-04-14)

## CTO MANDATE — NON NEGOZIABILE
> **"Tu sei il CTO. Il founder da la direzione, tu porti soluzioni."**
> **"A PROVA DI BAMBINO. L'utente PMI non sa fare nulla se non 2 click."**
> **"LASCIALI A BOCCA APERTA!"**

---

## GUARDRAIL SESSIONE
**Working directory**: `/Volumes/MontereyT7/FLUXION`
**Memory**: `/Users/macbook/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/MEMORY.md`
**iMac**: `192.168.1.2` | Voice pipeline porta 3002 | SIP: 0972536918

---

## COMPLETATO SESSIONE 154 — PRODUCTION READINESS AUDIT

### Verdetto: GO-WITH-CONDITIONS

11 specialist agents executed in 3 parallel waves:
- **Wave 1** (4 agents): Coverage, Infrastructure, Security, Database
- **Wave 2** (4 agents): Backend, Frontend, Voice, Performance
- **Wave 3** (3 agents): UI Design, GDPR, Deploy

### 9 Audit Reports Completed
```
.claude/cache/agents/audit-s154/
├── COVERAGE-AUDIT.md      (1857 Python tests, 36 Rust, 0 frontend)
├── INFRA-AUDIT.md         (CF Workers OK, self-healing OK, auto-update NOT wired)
├── BACKEND-AUDIT.md       (0 launch blockers, 5 MEDIUM unwrap)
├── VOICE-AUDIT.md         (B1 fix sound, TTS gap found, VoIP VAD gap)
├── PERF-AUDIT.md          (startup <3s, 5 missing indexes)
├── DEPLOY-AUDIT.md        (macOS GO, Windows GO with SmartScreen)
├── UI-AUDIT.md            (design consistent, 3 minor inline styles)
├── GDPR-AUDIT.md          (4 gaps: privacy page, cookies, hard-delete, voice WAV)
└── PRODUCTION-READINESS-REPORT.md  ← VERDETTO FINALE
```

### Bug Triage Results
| Bug | Verdict |
|-----|---------|
| B1 pjsua2 deadlock | **FIX APPLIED S153** — threadCnt=0+mainThreadOnly+lockCodecEnabled=False. Needs live test. |
| B2 Gommista | **RESOLVED** — regex requires "cambio gomme" compound. Needs regression test. |
| B3 VAD hookup | **PARTIAL** — HTTP/WS works. VoIP path still fixed 1000ms. |
| B4 FAQ variables | **NOT A BUG** — unresolved vars → FAQ skipped |
| B5 Guardrail vertical | **NOT A BUG** — guardrails ARE vertical-aware |
| B6 DB services | **BY DESIGN** — user creates own services |
| B7 Latency | **DEFERRED v1.1** — P95<100ms for L0-L2, ~1700ms for L4+Edge-TTS |
| B8-B9 | **RESOLVED** — health check + self-healing implemented |
| B10 Code signing | **BY DESIGN** — ad-hoc macOS, unsigned Windows |
| B11 Auto-update | **OPEN** — plugin loaded, GH Releases NOT wired |
| B16 TypeScript any | **ZERO** — strict mode, 0 any types |

### Key Findings
- **TypeScript**: strict:true, ZERO any types
- **Console.log**: 53 occurrences across 20 files (cleanup needed)
- **SQLite**: 5 missing indexes (clienti.deleted_at, appuntamenti.data_ora_inizio, etc.)
- **GDPR Article 9**: Medical schede contain health data requiring explicit consent
- **TTS**: Runtime Edge-TTS failure not caught → no fallback → silent response

---

## 7 BLOCKERS (12.5h total fix time)

0. **ROTATE ALL SECRETS** — `memory/reference_*.md` has live Stripe/Resend/CF/SIP creds in git — 2h
1. **Fix CORS wildcard** — `fluxion-proxy/src/index.ts:14` — 30min
2. **Privacy policy page** — `landing/privacy.html` — 2h
3. **Self-host Inter font** — Google Fonts CDN violates Garante ruling — 1h
4. **TTS runtime fallback** — `tts_engine.py` try/except in synthesize() — 4h
5. **Live VoIP test** — call 0972536918, verify audio — 1h
6. **DB backup mechanism** — zero backup code in codebase — 2h

---

## PROSSIMA SESSIONE (155) — FRAMEWORK

### PRIORITA' 1: FIX 4 BLOCKERS (8h)
```
STEP 0: ROTATE ALL SECRETS (Stripe, Resend, CF, SIP) + git filter-branch
STEP 1: Fix CORS wildcard in fluxion-proxy/src/index.ts
STEP 2: Create landing/privacy.html (GDPR Art.13)
STEP 3: Self-host Inter font (remove Google Fonts CDN)
STEP 4: Fix TTS runtime fallback in voice-agent/src/tts_engine.py
STEP 5: Add DB backup command (VACUUM INTO or file copy)
STEP 6: Live VoIP call test on iMac (0972536918)
```

### PRIORITA' 2: HIGH FIXES (25h)
```
H-1: GDPR hard-delete for clienti
H-2: Article 9 consent for medical schede
H-3: Remove 53 console.log from src/
H-4: Add 5 missing SQLite indexes (migration 035)
H-5: Wire auto-update to GitHub Releases
H-6: Wire VoIP VAD to adaptive silence
H-7-8: Add B2/B3 regression tests
H-9: Voice temp WAV cleanup + GDPR notice
```

### PRIORITA' 3: POST-LAUNCH BACKLOG
- Frontend test suite (vitest)
- IPC command tests
- Lighthouse optimization
- Stress test baseline persistence

### Suite da caricare
```
SKILLS:     /fluxion-voice-agent, /frontend-developer, /legal-compliance-checker
AGENTS:     voice-engineer, frontend-developer, backend-architect, content-creator
```

### Prompt di ripartenza S155
```
Leggi HANDOFF.md. Sessione 155.
VERDETTO S154: GO-WITH-CONDITIONS. 4 blockers da fixare (8h).
PRIORITA' 1: Fix i 4 blockers per il lancio:
1. landing/privacy.html (GDPR)
2. Cookie consent banner
3. TTS runtime fallback (tts_engine.py)
4. Live VoIP test su iMac
Dopo blockers: fix i 9 HIGH items.
Report completo in .claude/cache/agents/audit-s154/PRODUCTION-READINESS-REPORT.md
```

---

## SECURITY ACTION ITEMS (manual — founder action required)

### URGENT (before public launch)
- [ ] Stripe: rotate restricted key → dashboard.stripe.com/apikeys
- [ ] Resend: rotate API key → resend.com/api-keys
- [ ] Cloudflare Workers: rotate API token → dash.cloudflare.com/profile/api-tokens

**WHY**: queste chiavi sono state caricate nel context di Claude via MEMORY.md.
Anche se non sono in git, sono state esposte al modello. Rotazione precauzionale raccomandata.

### NOT URGENT (GCP disabled)
- [ ] Google OAuth client_secret — rimosso da git (S155), GCP disabilitato

---

## STATO GIT
```
Branch: master | HEAD: 25b149d
Ultimo commit: security(S155): remove google credentials from git tracking
```
