# NEXT SESSION PROMPT — S241 (impartito dal founder a chiusura S240)

> Founder ha dettato in chiusura S240. Eseguire integralmente. NON deviare.
> Bug VoIP S240 T0 applicato ma NON testato (founder priority shift su production sprint).
> T0 status: applicato commit `4df32f1`, sync iMac OK, pipeline UP+SIP REGISTERED, NESSUN test live eseguito.
> Recovery T0 test possibile in S241 se founder lo chiede esplicitamente, altrimenti procedi con sprint sotto.

---

# Prompt FLUXION — Production Sprint S184-S188 — Public Launch Path

> **Workspace**: terminal Claude Code con `cwd /Volumes/MontereyT7/FLUXION`
> **NON** in terminal VOS o ARGOS. Workspace dedicato FLUXION (decisione split S170).
> **Priority CTO**: priority 1 production (founder S170-post-close: "FLUXION deve andare in produzione quanto prima").

---

## Stato attuale (verificato discovery S170 VOS-meta 2026-05-14)

**Pre-launch ALPHA in corso**. Documentazione completa:
- README ✓
- PRD-FLUXION-COMPLETE.md (PRD aggiornato 2026-03-03, sez 1 pricing patched S170-post-close)
- ROADMAP_S184_REVISED_ALPHA.md (sprint S184-S188, 14h lavoro pianificato)
- ROADMAP_REMAINING.md (sprint post S183)
- TESTING_SUITE_COMPLETE.md (26+ test case multi-turn Sara, 6 verticali)
- docs/launch/PRE-LAUNCH-AUDIT.md (gate 3 readiness check 2026-05-11)
- docs/launch/RUNBOOK-P1-SARA-LIVE-TEST.md
- docs/launch/RUNBOOK-P2-WIN-MSI-BUILD.md
- docs/perf/D3-voice-latency.md (P95 1330ms vs target <800ms)
- docs/SUPPORT-RUNBOOK.md (SLA P0-P2, triage matrix, 20+ template)
- docs/PMI_VERTICALS_ANALYSIS.md (9 verticali)

**Stack**: Tauri 2 + React 19 + SQLite + Voice Agent Python (Twilio + Groq + Piper TTS)

**Founder decision S170-post-close (CRITICAL CHANGES)**:
1. **Pricing 2-tier definitivo** (DROP €297 Base):
   - **PRO €497**: 3 verticali + 1 mese trial Sara Voice Agent **incluso**
   - **ENTERPRISE €897**: 6 verticali + Sara lifetime + WhatsApp + API
2. **Meccanica Sara post-trial €497**: cliente deve attivare abbonamento Ehiweb separato. **FLUXION deve SEMPLIFICARE questo processo** (founder explicit).
3. **Sales agent FLUXION pattern = AMBRA ARGOS**: "parla come un umano su WA", approccio dealer-style, video → landing. Skills marketing + research tools (founder: "ce la possiamo fare").

**Gap blocking production** (da PRE-LAUNCH-AUDIT.md):
- Build MSI Windows signed (SmartScreen bypass)
- Sentry crash reporter integration
- HW matrix VM test complete
- Sara latency optimization 1330ms → <800ms
- Beta program 6 clienti
- AI helpdesk content

---

## Goal Sprint S184-S188 (priorità riordinate post-S170)

### P0 — Patch pricing across codebase (1-2h)
**Trigger**: founder decision S170-post-close drop tier €297.

Audit codebase per riferimenti pricing tier:
```bash
grep -rE "297|tier.*[Bb]ase|tier.*BASE" --include="*.ts" --include="*.tsx" --include="*.rs" --include="*.py" --include="*.md" --include="*.json" --include="*.yaml" /Volumes/MontereyT7/FLUXION/ 2>/dev/null | head -30
```

Files probabili da update:
- `src-tauri/src/license/` (license validation per tier)
- `src/components/` (UI tier selection)
- `migrations/` (DB schema license_tier enum)
- `docs/context/BUSINESS-MODEL.md`
- Marketing materials (landing page, screenshots, demo videos)

**Done when**: zero reference a tier Base €297 in codebase production, UI mostra solo PRO/ENTERPRISE, DB migration aggiunto se necessario.

### P1 — Ehiweb subscription mechanic (3-4h, NEW)
**Trigger**: founder explicit "BISOGNA SEMPLIFICARE AL CLIENTE IL MODO PER FARE 1 MESE DI ABBONAMENTO A EHIWEB".

Design opzioni:
- (a) **Affiliate link** Ehiweb diretto con UTM tracking + pre-fill dati cliente FLUXION
- (b) **Reseller account FLUXION**: FLUXION raccoglie €/mese, gira a Ehiweb (richiede contratto reseller — TBD founder discussion con Ehiweb)
- (c) **Wizard onboarding** in FLUXION app: step-by-step + copy-paste credentials Ehiweb (più friction ma zero dipendenza commerciale)

**Dubbi founder**: hai già rapporto con Ehiweb? Sei reseller? Hai link affiliate? Tariffa Ehiweb post-trial (€/mese)?

**Done when**: opzione scelta + spec funzionale + UI mockup. Implementazione differita a P5 se complexity alta.

### P2 — Build MSI Windows UNSIGNED (vincolo #5 zero-capex confermato founder S170-post-close)
Da `docs/launch/RUNBOOK-P2-WIN-MSI-BUILD.md`:
- Tauri build target Windows MSI
- **NO code signing** (founder decision S170-post-close: skip Azure Trusted Signing + Sectigo EV)
- Cliente vede SmartScreen "Editore sconosciuto" → workflow guidato "Maggiori informazioni → Esegui comunque" (one-time)
- Reference guida esistente: `docs/helpdesk-wiki/wiki/entities/win10-installation.md` (già documenta workflow + license certificato genuinità)
- Test installazione VM Windows Win10/Win11
- **NOTE "TUTTO MECHANIC" tradeoff**: 1 click extra one-time accettato come tradeoff per zero capex. Resto installazione MUST essere full automated (license activation auto, Sara auto-config, Ehiweb integration).

**Done when**: MSI builds clean + installs on Win10/Win11 VM via guida + Sara starts correctly + license auto-activates.

### P3 — Sentry crash reporter integration (2-3h)
Da ROADMAP_S184:
- Sentry free tier (5K errors/mese)
- SDK integration Tauri + Python Voice Agent
- Test crash simulation → event arrives in Sentry dashboard

**Done when**: forced crash → event in Sentry < 60s.

### P4 — Sara latency optimization (4-6h)
Da `docs/perf/D3-voice-latency.md` P95 1330ms target <800ms.
- Bottleneck IPC analysis (trace flame graph)
- Optimization candidates: Groq cascade vs single-model, Piper TTS streaming, Twilio WebRTC vs SIP
- Target: P95 <800ms, P99 <1200ms

**Done when**: latency benchmark verified 3x consecutive run.

### P5 — Sales agent FLUXION pattern AMBRA-style (5-8h, NEW)
**Trigger**: founder S170-post-close "AMBRA AGENT DI ARGOS HA DELLE CARATTERISTICHE CHE IL SALES AGENT DI FLUXION DOVREBBE AVERE, PARLA COME UN UMANO SU WA".

Cross-reference: ARGOS Phase 6 AMBRA design (TBD audit terminal ARGOS).

Design FLUXION sales agent:
- **Canale primario**: WhatsApp Business API o Baileys (riuso pattern ARGOS daemon? same stack iMac?)
- **Stile**: italiano natural, conversational, NO sales script, NO "americanate"
- **Flow base**:
  1. Discovery prospect SMB Italian (verticali target: saloni, medical, palestre, auto, odonto, vet, servizi, immobiliare, assicurazioni)
  2. Outreach WA personalizzato per verticale
  3. Engagement: chiede pain points ("come gestite gli appuntamenti?")
  4. **Video demo** Sara Voice Agent verticale-specifico (1-2 min, screen-record)
  5. CTA soft: link landing page verticale-specifica
  6. Follow-up se interest signal
  7. Handoff founder quando ready-to-buy

**Confermato founder S170-post-close**:
- **Numero WA FLUXION**: `3314928901` **già operativo, già brandato "Erica Fluxion"** + logo FLUXION
- Stack: Baileys (riuso pattern ARGOS daemon, stesso iMac PM2 OR instance separata)

**Dubbi founder residui**:
- Landing per ogni verticale già built? Quale URL?
- Video demo Sara già recorded per verticale? Quale formato/length?

**Done when**: 1 sales agent WA workflow funzionante per 1 verticale (es. saloni di bellezza) + 5 prospect contattati + 1 demo video sent + tracking conversioni.

### P6 — Beta program 6 clienti (gate finale pre-launch)
Da ROADMAP_REMAINING.md:
- Recruit 6 beta clienti SMB Italian (1-2 per verticale top: saloni, medical, palestre)
- Free tier 1 mese o sconto 50% per feedback estensivo
- Daily ping support, weekly check
- Metric: bug count, feature requests, satisfaction NPS

**Done when**: 6 beta clienti onboarded + 4 settimane data + go/no-go decision launch public.

### P7 — Public launch (Week 4-5 from now if all green)
- Landing page production-ready
- Pricing 2-tier €497/€897 visibile
- Demo videos per verticale
- Sales agent attivo + monitoring
- Support runbook attivo
- First public buyer paying €497 = MILESTONE 1

---

## DUBBI FOUNDER da chiarire (vincolo "SE HAI DUBBI CHIEDI")

**Risolti S170-post-close** ✅:
- ~~Numero WA FLUXION~~ → `3314928901` Erica Fluxion brand già operativo
- ~~Code signing Windows~~ → NO cert, install guide self-signed approach esistente in `docs/helpdesk-wiki/wiki/entities/win10-installation.md`
- ~~Stack WA~~ → Baileys (riuso pattern ARGOS)

**Dubbi residui da risolvere**:
1. **Ehiweb rapporto commerciale**: sei già reseller Ehiweb? Hai link affiliate? Quale tariffa cliente paga (€/mese)?
2. **Pricing migration**: clienti BASE €297 esistenti (se ne esistono) come gestiamo? Grandfathered? Upgrade forced? Refund?
3. **Landing pages per verticale**: già built? URL? O da fare?
4. **Video demo Sara**: già recorded per ogni verticale o da produrre?
5. **Beta clienti 6**: hai già lead identificati o serve scout da zero?

---

## Vincoli S184-S188

- **#1** verifica fattuale: Tauri/Sentry/Twilio docs verified
- **#3** raccomandazione singola CTO per P0-P7
- **#4** autocritica 4 punti per ogni feature critical
- **#5** zero capex (Sentry free tier, no signing cert € se possibile)
- **#6** verde gate: 6 beta clienti onboarded OR handoff sprint S189 strutturato
- **#7** /context periodicamente
- **#9** no diplomatico
- **#10** verificato > verosimile (P4 latency benchmark con dati reali, no claim ottimisti)
- **#11** root cause (P0 pricing audit completo, no missed reference)

---

## Memory pointers VOS-side da leggere

Path: `~/.claude/projects/-Volumes-MontereyT7-venture-os/memory/`
File rilevanti per FLUXION:
- `feedback_workspace_split_vos_vs_argos.md` — regola workspace (FLUXION = terminal separato)
- `feedback_premature_optimization.md` — NO legale/fiscale pre-revenue
- `feedback_pattern_S159_mitigation.md` — B6 3-line check
- `MEMORY.md` index — pointer altri feedback

(FLUXION-specific memory: ~/.claude/projects/-Volumes-MontereyT7-FLUXION/memory/ — se vuota, lavora da scratch in dir locale FLUXION-instance.)

---

## Riferimenti FLUXION

- Repo: `/Volumes/MontereyT7/FLUXION/`
- PRD: `PRD-FLUXION-COMPLETE.md` (patched S170: 2-tier €497/€897 + Ehiweb mechanic)
- Roadmap: `ROADMAP_S184_REVISED_ALPHA.md` + `ROADMAP_REMAINING.md`
- Audit pre-launch: `docs/launch/PRE-LAUNCH-AUDIT.md`
- Runbook MSI Win: `docs/launch/RUNBOOK-P2-WIN-MSI-BUILD.md`
- Runbook Sara live test: `docs/launch/RUNBOOK-P1-SARA-LIVE-TEST.md`
- Testing suite: `TESTING_SUITE_COMPLETE.md` (26 test case)
- Latency analysis: `docs/perf/D3-voice-latency.md`
- Verticali analysis: `docs/PMI_VERTICALS_ANALYSIS.md`

## Start trigger

Founder apre terminal FLUXION (`cwd /Volumes/MontereyT7/FLUXION`), copia-incolla questo prompt. Tu (Claude FLUXION-instance) parti da:
1. **Rispondi prima ai 8 DUBBI FOUNDER** (block until clarified — molti unblock cascading)
2. Poi P0 pricing patch (1-2h immediate) — autonomous
3. P1 Ehiweb mechanic design (depends Dubbio #1 risposta founder)
4. Sequenza P2-P7 dopo unblock dubbi
