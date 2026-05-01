# FLUXION — Roadmap Revisione α (S184→S188)

> **Generato**: 2026-05-01 — sessione S183-bis
> **Override**: complementa `ROADMAP_S183_S190.md` (NON sostituisce — aggiunge gate items)
> **Direttiva founder S183-bis**: Opzione α onesta lenta confermata. ETA +3 settimane vs roadmap S182. Confidenza target lancio cold-traffic ~80%.
> **Strategia beta**: 1 cliente per macro-vertical × 6 macro = test coverage realistico tutti path codice.
> **Helpdesk**: AI autonomo RAG + LLM (Karpathy LLM-from-scratch concept) su Groq llama-3.3 (zero costi extra, già in proxy).
> **Bypass installazione**: enumerare e mitigare TUTTI i blocchi (SmartScreen, Gatekeeper, AV vendor, corporate firewall, captive portal).

---

## RAZIONALE STRATEGICO

CI workflow GREEN copre ~5% rischio reale. Restanti 95% = HW reale + AV vendor + network condition + edge case applicativi + adozione reale.

**3 leve per portare confidenza da 5% a 80%**:

1. **Crash reporter Sentry free tier** (5k events/mese) → cattura stack trace TS+Rust+Python automatico ad ogni crash cliente. Senza questo, ogni segnalazione = ricostruzione blind.
2. **HW test matrix VM** (Win10 + Win11 + Mac Intel + Mac M1) → riproduzione locale gratuita su Mac M1 founder con UTM/VMware Fusion (free tier) + immagini ufficiali Microsoft Edge dev VM (gratis 90gg).
3. **Beta program 6 clienti reali** (1 per macro-vertical: Saloni, Palestre, Cliniche, Officine, Sanitario locale, Servizi persona) → 2 settimane bug bash con AI helpdesk auto-rispondente + escalation diretta founder.

**Il punto critico**: founder solo NON può sostenere supporto manuale di 50+ clienti senza queste 3 leve. AI helpdesk è la moltiplicatore di produttività che rende sostenibile lancio massa.

---

## SPRINT S184 — α-INFRA (Sentry + Bypass installazione + HW Matrix VM) (~14h)

**Obiettivo**: posa infrastruttura osservabilità + matrix HW realistica + tutti bypass blocchi installazione documentati.

### Task α.1 — Crash reporter Sentry (~3h)

| Step | ID | Descrizione | ETA | Agent |
|------|----|----|-----|-------|
| α.1.1 | OBS-1 | Account Sentry free tier + create project FLUXION (Tauri custom) + DSN | 0.5h | `devops-automator` |
| α.1.2 | OBS-2 | Integrazione frontend `@sentry/react` con `Sentry.init()` su `main.tsx` + ErrorBoundary | 1h | `frontend-developer` |
| α.1.3 | OBS-3 | Integrazione Rust `sentry` crate in `lib.rs` con `tauri::async_runtime` + panic hook | 1h | `backend-architect` |
| α.1.4 | OBS-4 | Integrazione Python `sentry-sdk` in `voice-agent/main.py` + `before_send` filtro PII | 0.5h | `voice-engineer` |

**Verify**: provocare crash deliberato (3 OS) → evento visibile su Sentry dashboard entro 30s.

**Privacy**: PII filter mandatory (no nomi clienti, no telefoni, no XML SDI). Solo stack trace + OS version + app version.

### Task α.2 — Bypass installazione TUTTI gli scenari (~4h)

| Step | ID | Descrizione | ETA | Agent |
|------|----|----|-----|-------|
| α.2.1 | INST-1 | Script post-install macOS `setup-mac.command` che apre System Settings → Privacy automaticamente con `osascript` | 0.5h | `installer-builder` |
| α.2.2 | INST-2 | Script post-install Windows `setup-win.bat` con `powershell -Command "Add-MpPreference -ExclusionPath ..."` (richiede admin, instructions fallback) | 0.5h | `installer-builder` |
| α.2.3 | INST-3 | Submit DMG + MSI a Microsoft Defender SmartScreen (https://www.microsoft.com/wdsi/filesubmission) — gratis, riduce false positive entro 7gg | 0.25h | `code-signer` |
| α.2.4 | INST-4 | Submit a Norton + Kaspersky + Avast vendor portals (whitelist request gratis) | 0.5h | `code-signer` |
| α.2.5 | INST-5 | Video tutorial 3min (3 OS): "Come installare FLUXION superando AV/Gatekeeper" — record con OBS Studio gratis | 1h | `video-editor` + `documentation-writer` |
| α.2.6 | INST-6 | `come-installare.html` add: video embed + diagrammi step-by-step + sezione "errori comuni" (8 scenari: SmartScreen, Gatekeeper, Defender, Norton, network firewall, IPv6-only, captive portal, FileVault) | 1h | `documentation-writer` |
| α.2.7 | INST-7 | App-side: detect first-run network failure → mostra modal "Probabile firewall corporate, contatta IT" con whitelist domains list (`*.workers.dev`, `api.stripe.com`, `api.groq.com`) | 0.25h | `frontend-developer` |

**Verify**:
- [ ] Test installazione su Win10 con Defender attivo + Norton trial → SmartScreen warning + Norton quarantine → istruzioni recovery funzionanti
- [ ] Test installazione macOS Ventura clean con Gatekeeper strict → ctrl+click flow E2E
- [ ] Test app dietro firewall corporate simulato (`pfctl` block `*.workers.dev`) → modal warning visibile

### Task α.3 — HW Test Matrix VM (~4h)

| Step | ID | Descrizione | ETA | Agent |
|------|----|----|-----|-------|
| α.3.1 | HW-1 | Setup UTM (free) su Mac M1 founder → install Win10 21H2 IT-locale | 1h | `imac-operator` |
| α.3.2 | HW-2 | Setup UTM Win11 23H2 IT-locale + ARM64 image | 1h | `imac-operator` |
| α.3.3 | HW-3 | Snapshot baseline VM + script automation `install-fluxion.ps1` | 0.5h | `devops-automator` |
| α.3.4 | HW-4 | E2E install + smoke test 4 OS (Mac Intel host + Mac M1 host + Win10 VM + Win11 VM) | 1.5h | `build-verifier` |

**Verify**:
- [ ] DMG installabile + lancia su Mac Intel macOS Ventura (founder iMac) + Mac M1 macOS Sonoma
- [ ] MSI installabile + lancia su Win10 21H2 + Win11 23H2 VM
- [ ] App rimane stabile 30min senza crash su ogni VM
- [ ] License activation E2E funzionante 4/4

### Task α.4 — Audit network condition (~2h)

| Step | ID | Descrizione | ETA | Agent |
|------|----|----|-----|-------|
| α.4.1 | NET-1 | Script `tools/network-test.sh` che simula 4G slow + IPv6-only + corporate firewall | 0.5h | `infrastructure-maintainer` |
| α.4.2 | NET-2 | Test app behavior in 3 condition + record degradation (license cache works offline, voice fallback Piper, etc) | 1h | `api-tester` |
| α.4.3 | NET-3 | Document `docs/NETWORK-REQUIREMENTS.md` — minimum bandwidth, ports, domains whitelist | 0.5h | `documentation-writer` |

### Task α.5 — Closure S184 (~1h)
- Update HANDOFF + MEMORY + ROADMAP con S184 chiusa
- Commit + push

**Gate α.S184 PASS condition**: 4/4 verify above + Sentry catturando 3 crash test reali.

---

## SPRINT S185 — α-HELPDESK AI Autonomo (~10h)

**Obiettivo**: build AI helpdesk RAG che riduce carico founder 80% durante beta + post-launch.

### Architettura

```
Cliente in app → FAQ search local (instant) → fail → AI Chat widget
                                                ↓
                                    Cloudflare Worker /api/v1/helpdesk
                                                ↓
                                    RAG retrieval su KB (KV indexed embeddings)
                                                ↓
                                    Groq llama-3.3-70b context-injected prompt
                                                ↓
                                    Response + confidence score
                                                ↓
                              Confidence ≥0.7 → mostra → solved
                              Confidence <0.7  → email founder + log Sentry
```

### Knowledge Base

```
support-kb/
  installation/         # SmartScreen, Gatekeeper, AV bypass (auto-genera da INST-* docs)
  features/             # Per ogni hero feature: cos'è, come si usa, troubleshooting
  vertical-specifics/   # 6 macro-vertical-specific FAQ
  errors/               # Stack trace pattern → soluzione
  pricing-licensing/    # Trial, Base/Pro, refund, lifetime
  common-questions/     # Top 50 inevitabili (chi siete, perché €497, come funziona AI)
```

### Task

| Step | ID | Descrizione | ETA | Agent |
|------|----|----|-----|-------|
| α.5.1 | KB-1 | Genera `support-kb/` 50 articoli iniziali Markdown (frontmatter title/category/tags) | 3h | `support-responder` + `content-creator` |
| α.5.2 | KB-2 | Build embeddings via OpenRouter `text-embedding-ada-002:free` → store in CF KV `kb-embeddings:{id}` | 1.5h | `ai-engineer` |
| α.5.3 | KB-3 | Worker route `POST /api/v1/helpdesk` con cosine similarity top-k=3 + Groq context injection | 2h | `cloudflare-engineer` + `ai-engineer` |
| α.5.4 | KB-4 | Confidence scoring (`logprobs` Groq + similarity score) → threshold 0.7 escalation | 1h | `ai-engineer` |
| α.5.5 | KB-5 | Frontend chat widget shadcn/ui Dialog + streaming response | 1.5h | `frontend-developer` |
| α.5.6 | KB-6 | Email escalation template Resend + log conversation in KV `helpdesk-conv:{id}` (24h TTL) per debugging | 0.5h | `email-marketer` |
| α.5.7 | KB-7 | Embed widget in app (Tauri sidebar) + landing footer + email post-purchase | 0.5h | `frontend-developer` |

**Verify**:
- [ ] Pose 20 domande comuni (top 5 install, top 5 feature, top 5 pricing, top 5 errori) → 80% confidence ≥0.7 risposta corretta
- [ ] Domanda fuori scope → confidence <0.7 → email founder ricevuta entro 30s
- [ ] Conversazione log salvato KV per debugging
- [ ] Streaming response visibile <500ms first token

**Gate α.S185 PASS condition**: 16/20 risposte corrette + escalation funzionante.

---

## SPRINT S186 — α-BETA Acquisition + Onboarding (~8h)

**Obiettivo**: identificare + onboardare 6 beta tester (1 per macro-vertical) con AI helpdesk attivo.

### Strategia acquisition

| Macro-vertical | Strategia outreach | Target |
|----|----|---|
| Saloni (parrucchieri/estetiste/nail) | Facebook gruppi "Parrucchieri Italiani" 50k+ membri + Instagram DM proprietari salone follower 500-2000 | 1 cliente |
| Palestre (palestre/PT/yoga/pilates) | LinkedIn DM personal trainer/owner palestra mid-size + r/PMI Reddit | 1 cliente |
| Cliniche (medici/dentisti/fisio/psicologi) | LinkedIn outreach professionisti sanitari + AssoCare community | 1 cliente |
| Officine (auto/moto/gomme) | Google "officina meccanica Roma/Milano sito web" → email diretta + Confartigianato local chapter | 1 cliente |
| Sanitario locale (farmacie/erboristerie) | Federfarma social channel + r/farmacia | 1 cliente |
| Servizi persona (lavanderie/pet shop/etc) | Subreddit r/imprenditoreITALIA + pet shop FB groups | 1 cliente |

### Offer beta

```
- Trial gratuito 30 giorni (no carta richiesta)
- Setup wizard guidato + onboarding video personale
- AI helpdesk priority + escalation diretta founder
- Sconto 50% lifetime se pagano post-trial (€497 → €248 Base / €897 → €448 Pro)
- In cambio: 1 call 30min/settimana per feedback + bug report dettagliato
```

### Task

| Step | ID | Descrizione | ETA | Agent |
|------|----|----|-----|-------|
| α.6.1 | BETA-1 | Drafting outreach copy 6 vertical-specific con `growth-hacker` + `brand-guardian` | 2h | `growth-hacker` + `marketing-vertical-researcher` |
| α.6.2 | BETA-2 | Lista 30 target prospect/vertical (180 totali) → script outreach + tracking | 1.5h | `marketing-vertical-researcher` |
| α.6.3 | BETA-3 | Landing dedicato `landing/beta/index.html` con form application | 1h | `landing-optimizer` + `frontend-developer` |
| α.6.4 | BETA-4 | License code beta (separato da live) + KV `beta:{email}` con flag e weekly_call_count | 0.5h | `license-manager` |
| α.6.5 | BETA-5 | Email seq 3 step (welcome + day-3 check-in + day-7 feedback request) Resend free | 1h | `email-marketer` |
| α.6.6 | BETA-6 | Bug tracker integration: Sentry + helpdesk → GitHub Issues auto-create con label `beta-{vertical}` | 1h | `devops-automator` |
| α.6.7 | BETA-7 | Setup founder weekly call calendar (6 slot 30min) + Calendly free | 0.5h | `studio-producer` |
| α.6.8 | BETA-8 | Outreach manuale founder iniziale 6 vertical (3-5 messaggi/vertical) | 0.5h | `growth-hacker` (script ready, founder execute) |

**Verify**:
- [ ] 6 beta confermati entro 7gg da outreach (1 per vertical)
- [ ] Onboarding completo + license attivata 6/6
- [ ] Setup wizard completato senza richiedere founder intervention 4/6
- [ ] Helpdesk AI risolve 80% domande beta (~20 domande/settimana/cliente)

**Gate α.S186 PASS condition**: ≥4 beta attivi e usano app daily.

---

## SPRINT S187 — α-BETA RUN + bug bash (~12h calendario, ~6h work attivo)

**Obiettivo**: 2 settimane calendario di osservazione attiva beta + bug fix iterativo.

### Cadenza

```
Settimana 1:
  Daily: review Sentry events + helpdesk escalation queue (30min/giorno = 2.5h)
  Mid-week: 6 weekly call beta (30min × 6 = 3h)
  Bug fix sprint: P0 critical fix entro 48h
  
Settimana 2:
  Daily: review Sentry trend (30min/giorno = 2.5h)
  Mid-week: 6 weekly call (3h)
  Bug fix: P1 fix + feature request triage
  
Closure:
  Verifica metriche: crash-free rate ≥98%, NPS beta ≥7/10, conversioni paid ≥30%
```

### Task

| Step | ID | Descrizione | ETA | Agent |
|------|----|----|-----|-------|
| α.7.1 | RUN-1 | Daily review Sentry dashboard + helpdesk queue (script automation alert se >5 escalation/giorno) | 5h spread | `infrastructure-maintainer` |
| α.7.2 | RUN-2 | Bug fix P0 (anomalie crash >10/giorno o blocking workflow) | 4h reactive | `debugger` |
| α.7.3 | RUN-3 | Weekly call beta × 12 (6 × 2 settimane) + feedback synthesis | 6h | `feedback-synthesizer` |
| α.7.4 | RUN-4 | Metriche dashboard: Sentry trend + helpdesk solved rate + beta DAU | 1h | `analytics-reporter` |

**Verify**:
- [ ] Crash-free rate ≥98% per OS (Mac Intel/M1, Win10, Win11)
- [ ] Helpdesk AI auto-resolve rate ≥75%
- [ ] Founder time/cliente ≤3h totali in 2 settimane (call + escalation)
- [ ] ≥4/6 beta tester convertono a paid post-trial

**Gate α.S187 PASS condition**: tutte 4 metriche above. Se NON raggiunte → S187-bis bug bash extra.

---

## SPRINT S188 — α-LAUNCH cold-traffic (existing roadmap S188 + α additions)

**Obiettivo**: lancio cold-traffic con confidenza ~80% (vs ~30% senza α-strategy).

### Aggiunte vs roadmap S182

| Step | ID | Descrizione | ETA |
|------|----|----|-----|
| LAUNCH-α.1 | LIVE-α1 | Sentry alerts production: crash-rate >2% → notifica founder + auto-rollback canary | 1h |
| LAUNCH-α.2 | LIVE-α2 | Helpdesk monitoring dashboard: queue depth + resolve rate + escalation trend | 0.5h |
| LAUNCH-α.3 | LIVE-α3 | Beta tester testimonials → landing page (con liberatoria signed) | 1h |
| LAUNCH-α.4 | LIVE-α4 | Public bug tracker GitHub Issues template + roadmap pubblica | 0.5h |

---

## METRICHE SUCCESSO α-STRATEGY

| KPI | Target | Misurazione |
|-----|--------|-------------|
| Crash-free rate (Sentry) | ≥98% per OS | Sentry dashboard daily |
| Helpdesk AI resolve rate | ≥75% senza escalation | KV `helpdesk-resolved:{id}` flag |
| Beta conversion rate | ≥4/6 (66%) | License KV `beta:{email}` + Stripe purchase |
| Founder time/cliente | ≤3h in 2 settimane | Calendly + email log |
| Cold-traffic confidence | ≥80% (vs 5% CI-only) | Aggregate metrics composite |

---

## ETA REVISIONATA

| Sprint | Ore lavoro | Days calendar | Cumulative |
|--------|-----------|---------------|------------|
| S183 (current) | ~12h | 2 | 2gg |
| S184 α-INFRA | ~14h | 2-3 | 5gg |
| S185 α-HELPDESK | ~10h | 2 | 7gg |
| S186 α-BETA acquisition | ~8h | 1-2 | 9gg |
| S187 α-BETA RUN | ~12h spread | 14 (cal) | 23gg |
| S188 α-LAUNCH | ~5h α + existing | 1 | 24gg |
| **TOTALE α-strategy** | **~61h work** | **~24-25 giorni** | — |

**Vs roadmap S182 originale**: +3 settimane circa, confidenza 5% → 80%.

---

## DECISIONI CTO PRESE AUTONOMAMENTE (S181 directive)

1. ✅ Opzione α confermata (founder approved)
2. ✅ 1 cliente per macro-vertical (founder direction explicit)
3. ✅ AI helpdesk RAG su Groq llama-3.3 (zero costi extra, riusa proxy esistente)
4. ✅ HW matrix via VM gratuite (UTM Mac M1 + Edge dev VM Microsoft) — no spese hardware
5. ✅ Sentry free tier 5k events/mese sufficienti per beta + primi 50 clienti production
6. ✅ Embedding via OpenRouter free (text-embedding-ada-002:free) — coerente vincolo zero costi S181
7. ✅ Beta sconto 50% lifetime (€248 Base / €448 Pro) — accettabile vs valore feedback
8. ✅ Bypass installazione: documentazione + video + AV vendor submission (no cert paid €400/anno)

---

## TECH DEBT ACCETTATO POST-α (revisione S189-S190 buffer)

- v1.1 streaming LLM voice (target P95 <800ms) — D-4 audit
- Sentry Plus $26/mese se >5k events ($26 = €24/mese — valuteremo dopo 100 clienti reali)
- Code signing EV Microsoft $400/anno — solo se SmartScreen submission whitelist non basta dopo 30gg
- Localizzazione regionale italiana avanzata (PA encoding speciali) — P1 post-launch
- Anti-debugger / anti-piracy — non priority per €497 desktop B2B

---

**Generato da**: CTO autonomous decision per founder S183-bis directive
**Approvato**: Decisione α formale ricevuta in chat
**Next session**: S184 α.1 Sentry integration (start)
