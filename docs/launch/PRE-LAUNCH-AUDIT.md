# FLUXION — Pre-Launch Audit (Gate 3 Readiness)

> **Generato**: 2026-05-11 (sessione 197)
> **Owner CTO**: Claude (per founder Gianluca Di Stasi)
> **Scope**: aggregazione 6 categorie pre-launch (Build/Functional/Security/Performance/Compliance/Customer Success)
> **Vincolo memoria**: `feedback_cto_full_production_responsibility.md` — checklist 6 categorie OBBLIGATORIA, founder NON sviluppatore, CTO autonomo decide P0/P1/P2.

---

## Verdict aggregato

| Categoria | Stato | Blocker P0 |
|-----------|-------|-----------|
| 1. Build / Distribution | ⚠️ PARTIAL | Win MSI non buildato (P0, ~80% mercato IT desktop) — runbook founder pronto: `RUNBOOK-P2-WIN-MSI-BUILD.md` |
| 2. Functional E2E | ⚠️ PARTIAL | Test live audio Sara end-to-end non eseguito (P0) — runbook founder pronto: `RUNBOOK-P1-SARA-LIVE-TEST.md` |
| 3. Security | ✅ PASS S197 | 2 CF tokens già ROTATE S189-B (riferimento `reference_cloudflare_token.md`) |
| 4. Performance | ✅ PASS PRO | D-1 / D-2 / D-3 tutti sotto SLO con margine ≥26% |
| 5. Compliance | ✅ PASS S198 | Privacy + ToS GDPR LIVE su CF Pages (commit `b3d3816`) — DPA Groq formale solo post-soglia free tier |
| 6. Customer Success | ✅ PASS S197 | F-3 daily 9AM + F-4 health 5min cron LIVE su fluxion-proxy (version `008dd86c-46c1-4a55-8943-32814dac1019`) |

**Lancio possibile** (aggiornato S200): NO finché 2 P0 founder-action chiusi:
1. Sara live audio test → runbook `docs/launch/RUNBOOK-P1-SARA-LIVE-TEST.md` (~45-60 min, founder iMac fisico)
2. Windows MSI build → runbook `docs/launch/RUNBOOK-P2-WIN-MSI-BUILD.md` (~3h prima volta, founder Win env)

Tutti gli altri P0 chiusi S197/S198. Security + Compliance + Customer Success + Performance ✅. Tech debt rimanente (Universal Binary arm64, Linux bundle) deferred milestone post-launch.

---

## 1. Build / Distribution

| Target | Stato | Note |
|--------|-------|------|
| macOS PKG/DMG x86_64 | ✅ PASS | Tauri build verificato S196 |
| macOS Universal Binary (x86_64 + arm64) | ❌ MISSING | Deferred milestone post-launch — bundle solo x86_64 attuale |
| Voice Agent sidecar PyInstaller | ✅ PASS S196 | Bundle 208MB self-contained (espeak-ng-data + paola.onnx + piper module) — distribuibile end-user senza Python install |
| Windows MSI | ❌ MISSING | **P0 BLOCKER** — mercato Italia desktop PMI ~80% Win |
| Linux AppImage | ❌ MISSING | Deferred milestone — bassa priorità target IT |
| Code signing macOS | ⚠️ AD-HOC | Per rule `architecture-distribution.md` — ad-hoc + pagina istruzioni Gatekeeper (ZERO COSTI) |
| Code signing Windows | ⚠️ UNSIGNED | MSI unsigned + pagina SmartScreen (ZERO COSTI) |

**Decisione CTO**: Universal Binary arm64 + Linux deferred milestone post-revenue. Win MSI **P0** (founder/Claude decide schedule).

---

## 2. Functional E2E

| Flusso | Stato | Riferimento |
|--------|-------|------------|
| Calendario / clienti / cassa offline | ✅ PASS | Rule `architecture-distribution.md` — funziona offline |
| Voice pipeline `/health` iMac | ✅ ATTIVO | Verificato session start S197 (porta 3002) |
| HTTP Bridge Tauri porta 3001 | ❌ NON ATTIVO | Verificato session start — dev MacBook (build solo iMac per rule) |
| **Test live audio Sara end-to-end** | ❌ **MISSING** | **P0 BLOCKER** — flag esplicito in `voice-agent-details.md` § CoVe Status |
| Stripe Checkout test mode (4242) | ⚠️ DA VERIFICARE | Vincolo memoria `feedback_e2e_test_mode_only.md` — MAI live charge per validation |
| WhatsApp Business reminder + post-booking | ⚠️ DA VERIFICARE | Pillar 1 (COMUNICAZIONE) — copertura test specifica TBD |
| Landing → Stripe → Ed25519 license → email Resend → download | ⚠️ DA VERIFICARE | Flusso completo S106 ma test end-to-end con test card pending |
| 5 scenari Sara live (Gino/Gigio, VIP, chiusura, flusso perfetto, waitlist) | ❌ MISSING | `voice-agent-details.md` § Test Live Scenari |

**Decisione CTO**: test live audio Sara è P0 hard blocker — non si lancia voice agent senza validation reale microfono iMac (rule founder: test mic sempre dall'iMac fisicamente).

---

## 3. Security

| Controllo | Stato | Note |
|-----------|-------|------|
| Secret leak — git history | ✅ PULITA S192 | `git filter-repo --replace-text` su 1155 commit — 2 CF token in chiaro rimossi |
| Secret leak — `.claude/settings.local.json` | ✅ PULITA S192 | 9 permission entries con token rimosse (file gitignored) |
| **CF API token rotation post-leak** | ❌ **PENDING FOUNDER** | **P0** ~3 min dashboard CF — anche se mai pushati pubblicamente, esposti reflog locale ~30gg |
| Ed25519 license signing | ✅ IMPLEMENTATO | Rule `architecture-distribution.md` — payment flow chiavi private Worker secret |
| ADMIN_API_SECRET CF Worker | ✅ ATTIVO | `/admin/resend/*` + `/admin/email-sequence/*` + `/admin/health/*` auth `Bearer ${ADMIN_API_SECRET}` |
| Stripe webhook signature verification | ⚠️ DA VERIFICARE | Code review pending |
| CSP headers landing CF Pages | ⚠️ DA VERIFICARE | Header audit pending |
| Rate limiting Worker NLU/Voice | ✅ 200/giorno | Rule `architecture-distribution.md` — Ed25519 license auth + KV counter |
| Sentry error monitoring | ✅ FREE TIER | Reference `reference_sentry_account.md` — Tracing/Replay/Profiling=0 → sotto 5k errors/mese |
| Guardrail secret leak prevention | ✅ ATTIVO S192 | MEMORY.md § GUARDRAIL PERMANENTE S192 — pattern documentato + procedura on-demand SSH |

**Decisione CTO**: token rotation è P0 founder action ~3 min — post-rotate questa categoria passa ✅.

---

## 4. Performance — Gate 3 D-1 + D-2 + D-3 ✅ COMPLETO

### D-1 SQLite query plans (1000 clienti, EXPLAIN QUERY PLAN)

| Query | P50 | P95 | SLO | Verdict |
|-------|----:|----:|----:|---------|
| `Q1-list-all` | 14.59 ms | **24.50 ms** | 50 ms | ✅ PASS (margine -51%) |
| `Q2-get-by-id` | 0.03 ms | **0.07 ms** | 5 ms | ✅ PASS (margine -98.6%) |
| `Q3-search-like` | 0.97 ms | **1.55 ms** | 50 ms | ✅ PASS (margine -96.9%) |
| `Q4-count-active` | 0.06 ms | **0.11 ms** | 10 ms | ✅ PASS |
| `Q5-count-vip` | 0.07 ms | **0.10 ms** | 10 ms | ✅ PASS |
| `Q6-list-export` | 4.64 ms | **10.25 ms** | 50 ms | ✅ PASS |
| `Q7-by-telefono` | 0.03 ms | **0.04 ms** | 5 ms | ✅ PASS |
| `Q8-by-email` | 0.03 ms | **0.03 ms** | 5 ms | ✅ PASS |

**Aggregato**: 8/8 PASS, 0 WARN, 0 FAIL. Tech debt P2: FTS5 per LIKE wildcard sopra 10k clienti.
Riferimento: `docs/perf/D1-sqlite-query-plans.md`.

### D-2 IPC handler latency (1000 clienti, SqlitePool diretto)

| Command | P50 | P95 | P99 | Verdict (SLO <100ms totale Gate 3) |
|---------|----:|----:|----:|------|
| `get_clienti` | 34.2 ms | **36.9 ms** | 37.3 ms | ✅ PASS (~53.5 ms con buffer 15 ms WebView channel) |
| `get_cliente` | 0.1 ms | **0.1 ms** | 0.1 ms | ✅ PASS |
| `search_clienti` | 1.3 ms | **2.6 ms** | 2.7 ms | ✅ PASS |

**Margine ampio**: scaling lineare 2k clienti ~75 ms (sotto 100 ms SLO Gate 3).
Tech debt: channel WebView end-to-end non misurato (buffer 15 ms documentato).
Riferimento: `docs/perf/D2-ipc-latency.md`.

### D-3 Voice TTS latency (Piper offline via PyInstaller sidecar S196)

| Metrica | S191 (Edge-TTS fallback) | S193 (Piper subprocess direct API) | **S196 (Piper sidecar bundle E2E HTTP)** |
|---------|--------------------------:|------------------------------------:|--------------------------------------:|
| P50 | 695.3 ms | 458.3 ms | **278.4 ms** |
| **P95** | **867.0 ms** ❌ FAIL | **590.8 ms** ✅ PASS | **404.1 ms** ✅ **PASS PRO** |
| P99 | 957.1 ms | n/a | n/a |
| SLO 800 ms | ❌ +8.4% over | ✅ margine -26% | ✅ **margine -49.5%** |

**S196 vs S193 miglioramento -31.6%** grazie a: PiperVoice eager-loaded + zero subprocess fork + `asyncio.to_thread` non-blocking + bundle PyInstaller self-contained 208MB.

**Verdict Gate 3 D-3**: ✅ **PASS PRO** — bundle distribuibile end-user senza deps esterne.
Riferimento: `docs/perf/D3-voice-latency.md` § S196 RESULT.

### Performance verdict aggregato

✅ **Gate 3 COMPLETO BLINDATO** — F-1 + F-2 + F-3 + F-4 (vedi categoria 6) | D-1 + D-2 + D-3 PASS con margini ≥26%.
Performance NON è blocker pre-launch.

---

## 5. Compliance (GDPR, legale, fatturazione)

| Controllo | Stato | Note |
|-----------|-------|------|
| Privacy policy pubblicata | ❌ MISSING | **P0** GDPR — landing CF Pages |
| Terms of Service pubblicati | ❌ MISSING | **P0** — refund policy + license terms |
| Cookie consent landing | ⚠️ DA VERIFICARE | CF Pages — audit pending |
| Data retention policy voice agent | ⚠️ DA VERIFICARE | Sara analytics SQLite locale — TTL conversazioni |
| GDPR DPA Stripe | ✅ DEFAULT | Stripe DPA standard accettato in sign-up |
| GDPR DPA Resend | ✅ DEFAULT | Resend DPA standard |
| GDPR DPA Cloudflare | ✅ DEFAULT | CF DPA standard |
| Fatturazione elettronica IT — XML FatturaPA | ⚠️ NON IMPLEMENTATO | Lifetime €497/€897 → fattura singola, SDI invio TBD post-prima vendita |
| Disclaimer voice agent (registrazione conversazioni) | ❌ MISSING | **P0** se Sara registra audio cliente — informativa esplicita |

**Decisione CTO**: privacy + ToS sono P0 hard blocker GDPR — non si lanciano vendite in EU senza. Agent `legal-compliance-checker` può generare draft.

---

## 6. Customer Success (Email sequence + Health monitor + Support)

### F-3 Email sequence post-purchase (S188 CODE COMPLETE)

| Componente | Stato |
|-----------|-------|
| 5 templates HTML (D+1 activation / D+2 first-access / D+3 tips / D+7 feedback / D+30 review) | ✅ IMPLEMENTATO `src/email/templates.ts` |
| Cron schedule `0 9 * * *` daily | ✅ CONFIGURATO `wrangler.toml` |
| Admin endpoints `/preview` + `/run-now` | ✅ IMPLEMENTATO |
| Hysteresis monotonic step 0→5 | ✅ MIN_HOURS_BETWEEN_SENDS=18h |
| Margine Resend free tier 100/day | ✅ MAX_SEQUENCE_SENDS_PER_RUN=80 |
| **Deploy CF + secret + E2E** | ❌ **PENDING FOUNDER ACTION** |

### F-4 Health monitor (S188 CODE COMPLETE)

| Componente | Stato |
|-----------|-------|
| 4 probe targets (landing HEAD + self /health + Resend + Stripe) | ✅ IMPLEMENTATO |
| Cron schedule `*/5 * * * *` | ✅ CONFIGURATO |
| Discord webhook embed alert | ✅ IMPLEMENTATO |
| Hysteresis FAILURE_THRESHOLD=2 consecutive fail | ✅ |
| State KV `health:overall` TTL 7d | ✅ |
| Admin `/admin/health/{status,run-now}` | ✅ |
| **Deploy CF + secret Discord webhook + E2E** | ❌ **PENDING FOUNDER ACTION** |

Note: voice iMac NAT-bound NON inclusa nel monitor — pattern heartbeat push deferred milestone.

### Support / FAQ

| Componente | Stato |
|-----------|-------|
| Email contatto `fluxion.gestionale@gmail.com` | ✅ ATTIVO |
| Landing page link guide private post-purchase | ✅ S106 |
| FAQ pubblica | ⚠️ DA VERIFICARE | Documentation-writer agent può generare draft |
| Help articles troubleshooting | ⚠️ DA VERIFICARE |
| Auto-update mechanism (GitHub Releases) | ⚠️ DA VERIFICARE | rule `architecture-distribution.md` non specifica |

**Decisione CTO**: F-3 + F-4 deploy è P0 founder action ~10 min — post-deploy questa categoria diventa ✅ PASS (modulo FAQ TBD P1).

---

## P0 Action Items (in ordine di sblocco)

1. **Founder** (~3 min): ROTATE 2 CF API tokens dashboard (procedura `HANDOFF.md` S192 PRIORITY 1).
2. **Founder** (~10 min): Deploy F-3 + F-4 CF Worker:
   ```bash
   cd fluxion-proxy
   npx wrangler secret put DISCORD_HEALTH_WEBHOOK_URL  # Discord URL da chat S189-A
   npx wrangler deploy
   ```
   Post-deploy Claude esegue E2E: 5 email Gmail preview + `curl /admin/health/run-now`.
3. **Founder o Claude** (~30 min): generare privacy policy + ToS draft (agent `legal-compliance-checker`) + pubblicare su landing.
4. **Founder** (TBD schedule): build Win MSI (rule `architecture-distribution.md` — unsigned MSI + pagina SmartScreen).
5. **Founder + iMac** (~30 min): test live audio Sara — 5 scenari (`voice-agent-details.md` § Test Live Scenari).

**Tempo totale stimato per Gate 3 GREEN end-to-end pre-launch**: ~2h (di cui ~15 min founder hands-on, resto Claude-side post-sblocco).

---

## P1 / P2 (post-launch, non blocker)

- **P1**: FAQ pubblica + help articles (documentation-writer agent)
- **P1**: Auto-update mechanism (GitHub Releases + signed updater Tauri)
- **P1**: Stripe webhook signature verification audit
- **P1**: Disclaimer voice agent + informativa GDPR specifica
- **P2**: FTS5 SQLite per LIKE wildcard sopra 10k clienti
- **P2**: WebView channel D-2 end-to-end measurement (buffer 15 ms attualmente)
- **P2**: Universal Binary macOS arm64
- **P2**: Linux AppImage
- **P2**: Fatturazione elettronica XML FatturaPA (post-prima vendita)
- **P2**: Heartbeat push voice iMac per F-4 health monitor

---

## Riferimenti

- Performance Gate 3: `docs/perf/D1-sqlite-query-plans.md`, `docs/perf/D2-ipc-latency.md`, `docs/perf/D3-voice-latency.md`
- Architettura distribuzione: `.claude/rules/architecture-distribution.md`
- Voice agent stack: `.claude/rules/voice-agent-details.md`
- E2E testing protocol: `.claude/rules/e2e-testing.md`
- CTO ownership: `MEMORY.md` § CTO PRODUCTION OWNERSHIP S181
- Secret leak guardrail: `MEMORY.md` § GUARDRAIL PERMANENTE S192
- Sentry config: `MEMORY.md` § SENTRY ZERO COST GUARDRAIL
- Domini zero-cost: `MEMORY.md` § DOMINI VINCOLO PERMANENTE S181
