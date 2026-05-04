# S185-A Research 1 — FLUXION Source Audit

## Obiettivo
Inventario completo raw sources per popolare layer Raw wiki helpdesk (Karpathy pattern, LLM-managed markdown). Mappa COSA è documentato, DOVE, stato attuale, per pianificare ingest senza duplicazione.

---

## Inventario per categoria

### 1. Install & Setup (Win/macOS)
| Path | Descrizione | Lunghezza | Stato |
|------|-------------|----------|-------|
| `scripts/install/README.md` | Overview post-install scripts + distribuzione DMG/Windows | ~100 lines | current (S184-α.3.2 chiusa) |
| `scripts/install/setup-mac.command` | Shell script rimuove xattr quarantine + SMB checks | 4.2KB | current |
| `scripts/install/setup-win.bat` | Batch script Defender exclusion + firewall localhost 3001/3002 + Unblock-File | 5.4KB | current |
| `scripts/install/docs/NETWORK-REQUIREMENTS.md` | Requisiti rete (firewall, proxy, FQDNs APIs Groq/Resend/Stripe) | ~200 lines | current |
| `scripts/install/docs/win10-fresh-compat.md` | Win10 fresh (25% PMI zero deps): VC++ Redist, WebView2, Python runtime | ~150 lines | current |
| `scripts/install/docs/alpha-3-VERIFY.md` | Build #19 SHA256 hashes, CI gates matrix, 5 root causes S184 documented | ~200 lines | current |
| `scripts/install/docs/virustotal-setup.md` | VirusTotal API gate (founder setup 5 min, secrets KV) | ~100 lines | current |
| `scripts/install/docs/av-submission-guide.md` | Strategie evitare false positivi AV (Defender, McAfee, Avast) | ~140 lines | current |
| `QUICKSTART-E2E-MACOS.md` | MacBook → iMac SSH dev setup (voice pipeline 3002, HTTP bridge 3001) | ~120 lines | current |

### 2. Product/PRD
| Path | Descrizione | Lunghezza | Stato |
|------|-------------|----------|-------|
| `PRD-FLUXION-COMPLETE.md` | Documento verità unico: vision, stack tech, moduli (CRM, billing, voice, schede verticali), target PMI Italia 1-15 dipendenti | ~1000 lines | current (aggiornato 2026-02-12) |
| `.planning/PROJECT.md` | Meta-project structure roadmap | ~80 lines | stale (ref phases) |
| `.planning/research/SUMMARY.md` | Tech stack, architecture, pitfalls discovered | ~150 lines | research-phase (stale) |
| `.planning/research/FEATURES.md` | Feature inventory by module | ~200 lines | research-phase |

### 3. Voice Agent Sara (5-Layer RAG Pipeline)
| Path | Descrizione | Lunghezza | Stato |
|------|-------------|----------|-------|
| `voice-agent/README.md` | Quick start, Docker setup, modules (intent, entity, FAQ, sentiment, analytics), verticali salone/palestra/medical/auto | ~150 lines | current |
| `voice-agent/IMPLEMENTATION_SUMMARY.md` | Fase implementation status, test 58/58 passati, latency ~1330ms (target <800ms), frontend Tauri integration NON ANCORA ATTIVA | ~100 lines | current |
| `voice-agent/docs/CONFIGURATION.md` | Verticale config, business_name, opening/closing hours, services mapping | ~100 lines | current |
| `voice-agent/docs/API.md` | HTTP endpoint spec `/health`, `/process`, WebSocket frame format | ~80 lines | current |
| `voice-agent/docs/TROUBLESHOOTING.md` | High latency diagnosis, low intent accuracy patterns, FAQ matching issues, circuit breaker status | ~150 lines | current |
| `.claude/rules/voice-agent.md` | Rules: Python 3.9 (iMac) vs 3.13 (MacBook), 5-layer RAG, sidecar Tauri, restart protocol SSH iMac | ~80 lines | current |
| `.claude/rules/voice-agent-details.md` | Extended voice FSM, booking_state_machine.py docstrings | ~150 lines | current |
| `voice-agent/src/_INDEX.md` | File index + module map | ~100 lines | current |
| `voice-agent/tests/e2e/INDEX.md` | E2E test coverage (58 test suite completato) | ~80 lines | current |
| `_bmad-output/planning-artifacts/voice-agent-epics.md` | Epic breakdown GDPR audit trail, consent logging, multi-turn dialog | ~200 lines | planning-phase |

### 4. Architecture & Rules
| Path | Descrizione | Lunghezza | Stato |
|------|-------------|----------|-------|
| `.claude/rules/architecture-distribution.md` | TTS 3-tier (Edge-TTS premium vs Piper offline), LLM zero-config proxy CF Workers, Stripe+Ed25519 payment, no code signing costs | ~50 lines | current |
| `.claude/rules/react-frontend.md` | React 19 + Tailwind + shadcn/ui, React Query, Zustand, pre-commit tsc+eslint | ~30 lines | current |
| `.claude/rules/rust-backend.md` | Rust 1.75+, SQLx, 100+ Tauri commands, domain services, repository pattern | ~30 lines | current |
| `.claude/rules/e2e-testing.md` | Playwright, data-testid, E2E smoke test suite | ~40 lines | current |
| `.claude/rules/testing.md` | Unit + integration + E2E strategy, coverage targets | ~50 lines | current |
| `.claude/rules/workflow-cove2026.md` | CoVe 2026 workflow (dual-track research + CTO/founder roles) | ~60 lines | current |

### 5. Verticali (6 macro × 17 sotto)
| Path | Descrizione | Lunghezza | Stato |
|------|-------------|----------|-------|
| `src/types/setup.ts` | MACRO_CATEGORIE (medico, beauty, hair, auto, wellness, professionale, pet, formazione) + MICRO_CATEGORIE record con 17 sotto-categorie mappate | ~200 lines | current |
| `src/components/schede/OdontoiatricaScheda.tsx` | Odontogramma FDI (32 denti), anamnesi, allergie | ~300 lines | ✅ complete |
| `src/components/schede/FisioterapiaScheda.tsx` | Zone corpo, scale VAS/Oswestry/NDI, progresso sedute | ~250 lines | ✅ complete |
| `src/components/schede/EstericaScheda.tsx` | Fototipo Fitzpatrick (1-6), routine skincare, allergie | ~280 lines | ✅ complete |
| `src/components/schede/[Parrucchiere/Auto/Medica/Fitness]Scheda.tsx` | Placeholder per altre 4 verticali | ~50 lines each | 📝 stub/TODO |
| `PRD-FLUXION-COMPLETE.md` § 3.2 | Stato implementazione 3 schede complete, 5 stub, roadmap FASE 2 | ~150 lines | current |

### 6. Troubleshooting (Known Issues & Edge Cases)
| Path | Descrizione | Lunghezza | Stato |
|------|-------------|----------|-------|
| `HANDOFF.md` | Sessione-by-session context rot record: S184 α.3.2 root cause #1-#5, iMac RAM cleanup, UTM/Win11 VM prep (BLOCKER Founder actions), tech debts open | ~1000 lines | current (s184-bis3 cleanup chiusa) |
| `voice-agent/docs/TROUBLESHOOTING.md` § "High Latency" | Groq fallback rate diagnostic (target <20%), FAQ coverage improvement loop | ~50 lines | current |
| `voice-agent/docs/TROUBLESHOOTING.md` § "Low Intent Accuracy" | Pattern matching failures (es. "disdire" → INFO instead CANCELLAZIONE), Levenshtein fuzzy match fix | ~60 lines | current |
| `NETWORK-CONFIG.md` | Cloud-sync corruption guard (iCloud, OneDrive, Dropbox, Google Drive detection), WAL pragma risks | ~150 lines | current |
| `_bmad-output/planning-artifacts/voice-agent-epics.md` § "Error Recovery" | Circuit breaker, retry logic, graceful fallbacks, Groq throttle mitigation | ~100 lines | planning-phase |

### 7. Pricing/License/Legal
| Path | Descrizione | Lunghezza | Stato |
|------|-------------|----------|-------|
| `PRD-FLUXION-COMPLETE.md` § 1.3 | License LIFETIME: Base €297, Pro €497, Enterprise €897. No SaaS commissioni, offline-first | ~30 lines | current |
| `.claude/rules/architecture-distribution.md` § "Pagamento" | Stripe Checkout → webhook CF Worker → Ed25519 license → email Resend | ~15 lines | current |
| `src-tauri/src/commands/license_ed25519.rs` | Firma Ed25519 offline, hardware fingerprint (hostname+CPU+RAM+OS), 3 tier access control | ~300 lines | current |
| `.env.example` + `src-tauri/.env` (gitignored) | Stripe keys, Resend API, Groq key, Tauri signing secrets | ~20 lines | current (secrets excluded from VCS) |
| `ROADMAP_S184_PROGRESS.md` § "Tech debt #4" | ⚠️ Tauri updater signing password mismatch — founder action POST-S184: regenerate key + GitHub secrets | ~30 lines | current issue |
| GDPR/Privacy | Mentioned in `_bmad/sessions/2026-01-29-week3-sprint-quality.md` (GDPR audit trail TODO) | ~5 lines | TODO |

### 8. Build/Release/CI-CD
| Path | Descrizione | Lunghezza | Stato |
|------|-------------|----------|-------|
| `.github/workflows/release-full.yml` | Master workflow: setup release, security audit, voice agent (3 OS), tauri (3 OS), integration tests, manifest generate | ~300 lines | current |
| `.github/workflows/smoke-test-installers.yml` | Cross-OS matrix (Win/macOS-arm/macOS-x64/Ubuntu × py3.11), health-check gate | ~150 lines | current (α.3.0-C) |
| `.github/workflows/verify-windows-static-crt.yml` | dumpbin /imports gate (NO vcruntime140), NSIS macro verify | ~100 lines | current (α.3.3-D) |
| `.github/workflows/virustotal-gate.yml` | SHA256 lookup VT API, auto GitHub issue P0 if detections >2, founder manual upload >32MB | ~120 lines | current (α.3.0-D) |
| `.github/workflows/e2e-tests.yml` | Playwright browser tests, data-testid selectors | ~80 lines | current |
| `scripts/install/docs/alpha-3-VERIFY.md` | Build #19 SHA256 proof matrix, 5 root causes documented, 3 OS CI gates | ~200 lines | current |
| `ROADMAP_S184_PROGRESS.md` | Sessione-by-session build attempt tracking (build #15-#19), root cause timeline | ~500 lines | current |

### 9. Roadmap & Planning (Completed Features)
| Path | Descrizione | Lunghezza | Stato |
|------|-------------|----------|-------|
| `ROADMAP_S184_PROGRESS.md` | α.1 setup wizard ✅ + α.2 CRM ✅ + α.3.0 quick wins ✅ + α.3.1 preflight/diagnostics ✅ + α.3.2 CI gates ✅ + α.3.3 Win static CRT ✅ + α.4 roadmap next | ~800 lines | current (S184 closure complete 2026-05-04) |
| `ROADMAP_S184_REVISED_ALPHA.md` | Original α.1-α.4 planning doc (reference archived) | ~400 lines | archived reference |
| `ROADMAP_REMAINING.md` | Post-S184 roadmap (S185 path A: helpdesk wiki vs B: PMI demo launch) | ~150 lines | current |
| `.planning/ROADMAP.md` | Meta roadmap structure | ~60 lines | current |
| `.planning/phases/f02-vertical-system-sara/*SUMMARY.md` | F02 (Voice Agent NLU hardening) shipped, 3 phase summaries | ~300 lines | shipped |
| `.planning/phases/f-sara-voice/*SUMMARY.md` | F-Sara voice quality improvements, 5 phase summaries | ~400 lines | shipped |
| `.planning/phases/f-sara-nlu-patterns/*SUMMARY.md` | F-Sara NLU pattern expansion (4 phases shipped) | ~500 lines | shipped |

---

## Recurring topic emergenti (cluster)

### Win10 Install (25% PMI failure surface)
- **Referenced in**: `win10-fresh-compat.md`, `alpha-3-VERIFY.md`, `PRD § 2.2`, `release-full.yml`, `verify-windows-static-crt.yml`
- **Key docs**: vcruntime140 static CRT linking (α.3.3-A), WebView2 bundling (α.3.3-B), Defender exclusion setup-win.bat, SmartScreen gate docs
- **Gap**: Real hardware install E2E (deferred to founder first PMI demo)

### Voice Agent Setup & Latency
- **Referenced in**: `voice-agent/README.md`, `voice-agent/TROUBLESHOOTING.md`, `IMPLEMENTATION_SUMMARY.md`, `.claude/rules/voice-agent.md`
- **Key docs**: Docker setup, health-check CLI flag, 5-layer RAG latency targets, Groq fallback rate diagnostics
- **Gap**: Production tuning guide (FAQ coverage expand loop, intent pattern updates)

### Verticali Config & Customization
- **Referenced in**: `src/types/setup.ts`, `PRD § 3.2`, voice-agent docs (business_name, services, hours)
- **Key docs**: Macro/micro schema, 17 sottocategorie mappate, 3 complete schede cliente
- **Gap**: Setup wizard step-by-step for each verticale (salone vs medical vs auto differences)

### License Activation & Refund
- **Referenced in**: `PRD § 1.3`, `license_ed25519.rs`, `.env vars`
- **Key docs**: Base/Pro/Enterprise tier prices (€297/€497/€897), offline Ed25519 verify
- **Gap**: Refund process, downgrade lifetime→trial, license key validation troubleshooting (client-facing FAQ)

### Auto-Update & Code Signing
- **Referenced in**: `ROADMAP_S184_PROGRESS.md` (tech debt #4), `architecture-distribution.md`, `.github/workflows/`
- **Key docs**: Ad-hoc macOS signing, unsigned Windows MSI gate docs (SmartScreen)
- **Gap**: Auto-update trust model, key regeneration procedure (founder action pending)

### Network & Security
- **Referenced in**: `NETWORK-REQUIREMENTS.md`, `NETWORK-CONFIG.md`, `preflight.rs`, cloud-sync detection
- **Key docs**: Firewall rules localhost 3001/3002, cloud-sync provider detection, proxy handling
- **Gap**: Corporate proxy authentication, VPN + cloud-sync conflict matrix

### GDPR/Privacy
- **Referenced in**: `_bmad/sessions/2026-01-29` (TODO), `PRD` (implied by SMB offline), `voice-agent/docs` (GDPR audit trail epic)
- **Key docs**: Consent logging, conversation audit trail, data encryption AES-256-GCM
- **Gap**: Privacy policy doc, data deletion procedure, CCPA/GDPR compliance checklist

---

## Gap identificati

### Support-relevant ma NON documentato in alcun file
1. **Refund process** — PRD lists prices ma zero info refund window, approval criteria, payment reversal
2. **License downgrade path** — Lifetime → Trial downgrade scenario (SMB cost-cutting, return requests)
3. **Bluetooth microphone support** — Voice agent assumes USB/built-in mic, zero troubleshooting for wireless pairing
4. **Multi-location / multi-branch** — Pricing è per singola attività; zero guidance su gestione 2+ locations (comune PMI capogruppo)
5. **Auto-update trust model** — Tauri updater key rotation, signature verification, manual update fallback
6. **Corporate proxy + Groq API auth** — Network-Requirements.md copre proxy ma zero Groq+Stripe+Resend auth via proxy
7. **Data export / GDPR right-to-deletion** — HANDOFF mentions TODO GDPR audit trail; zero spec su export format o data purge procedure
8. **Training/onboarding per team membro aggiuntivo** — Operatori module esiste (`src-tauri/commands/operatori.rs`) ma zero docs
9. **Importazione dati legacy** (es. clienti da precedente CRM) — Zero spec CSV schema, mapping business logic
10. **Vertical-specific API integrations** (es. salone sync booking calendar → Google Calendar, auto SMS appointment confirm)

### Documentazione parziale / work-in-progress
- **Voice Agent Tauri Integration** — Bridge HTTP 3001 esiste ma frontend non ancora integrato (IMPLEMENTATION_SUMMARY.md flag "Frontend non integrato con Voice Agent (HTTP diretto)")
- **Schede Cliente incomplete** — 3/8 verticali complete, 5 stub (Parrucchiere, Auto, Medica, Fitness, Veterinaria)
- **Auto-update system** — Code scaffolded ma `createUpdaterArtifacts: false` (tech debt #4)
- **WhatsApp Business integration** — Referenced in PRD, commands/whatsapp.rs exists, zero user guide
- **Fatturazione XML (FatturaPA)** — commands/fatture.rs exists, zero step-by-step invoice generation guide

---

## Raccomandazione seed pages prioritarie (top 10)

| # | Entità/Topic | Frequenza(stima) | Valore self-service | Fonte primaria |
|----|--|---|---|---|
| 1 | **Win10 Fresh Install (VC++/WebView2 missing)** | Very high (~25% PMI no deps) | CRITICAL (blocker first launch) | win10-fresh-compat.md, alpha-3-VERIFY.md |
| 2 | **Voice Agent Setup & Config** | High (all Sara users) | CRITICAL (booking automation) | voice-agent/README.md, CONFIGURATION.md, iMac quickstart |
| 3 | **License Activation / Key Not Found** | High (post-purchase) | CRITICAL (app won't launch) | license_ed25519.rs, PRD § 1.3 |
| 4 | **Network/Firewall Config (ports 3001/3002, Groq API)** | Medium-High (IT managers) | HIGH (enabler) | NETWORK-REQUIREMENTS.md, preflight.rs |
| 5 | **Voice Agent Latency / Groq Fallback High** | Medium (power users) | HIGH (performance) | TROUBLESHOOTING.md, IMPLEMENTATION_SUMMARY.md |
| 6 | **Verticale Setup (Salone vs Medical vs Auto)** | Medium (initial setup) | CRITICAL (onboarding) | setup.ts MICRO_CATEGORIE, PRD § 3.2 |
| 7 | **CRM Client Import / Data Migration** | Medium (SMB switching from competitor) | CRITICAL (adoption) | GAP — zero docs yet |
| 8 | **Cloud-Sync Corruption (iCloud/OneDrive)** | Medium-Low (power users + edge case) | MEDIUM (data protection) | NETWORK-CONFIG.md, preflight.rs |
| 9 | **Refund / License Downgrade** | Low (post-purchase friction) | MEDIUM (support reduction) | GAP — zero docs yet |
| 10 | **WhatsApp Business Config (booking notification)** | Low (advanced feature) | MEDIUM (engagement) | GAP — command exists, zero UX guide |

---

## Prossimi step (S185 planning)

### Path A: Karpathy Wiki Helpdesk Ingest (recommended)
1. **Wiki structure**: Raw (source audit ✓) → Processed (normalized markdown chunks) → Compiled (LLM-indexed FAQs)
2. **Seed 3-5 top pages** (Win10, Voice setup, License activation) from sources above
3. **Prompt LLM** to generate FAQ + troubleshooting from raw → wiki markdown Karpathy style
4. **Iterate**: monitor support queries, close gaps (refund, training, data export)

### Path B: Launch Path PMI (parallel)
1. Founder installa MSI v1.0.1 su Win10 box reale (artifacts ready build #19)
2. First PMI beta tester (parrucchiere/palestra zona Roma)
3. Real-world feedback loop → doc updates (hand-written edge case capture)
4. Inform Wiki with production learnings

---

**Audit date**: 2026-05-04  
**Codebase state**: S184 closure complete, S185 path identification phase  
**Total sources catalogued**: 45 primary files, 8 gaps identified, 10 seed pages prioritized
