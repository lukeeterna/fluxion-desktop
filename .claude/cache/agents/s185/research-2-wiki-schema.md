# S185-A Research 2 — Wiki Schema Design (Karpathy pattern adapted to FLUXION)

Scope: definire convenzioni operative del wiki helpdesk FLUXION (`docs/helpdesk-wiki/`) prima della FASE 3 IMPLEMENT. Output usabile da un altro agente Claude Code per ingest/query/lint senza ulteriori chiarimenti.

Pattern di riferimento: gist Karpathy "LLM Wiki" (3 layer: raw / wiki / schema). Adattamento dominio: helpdesk PMI italiane multi-verticale, target riduzione volume support email founder (`fluxion.gestionale@gmail.com`).

---

## 1. Directory structure proposta

```
docs/helpdesk-wiki/
├── HELPDESK.md                    # SCHEMA — agent instructions (CLAUDE.md-style, THE config)
├── index.md                       # CATALOG — content-oriented, aggiornato ad ogni ingest
├── log.md                         # CHRONO — append-only, prefix `## [YYYY-MM-DD HH:MM]`
├── raw/                           # IMMUTABLE source documents, mai modificati da LLM
│   ├── install/                   # win10-fresh-compat.md, NETWORK-REQUIREMENTS.md, alpha-3-VERIFY.md
│   ├── product/                   # PRD-FLUXION-COMPLETE.md slices, pricing snapshot
│   ├── voice/                     # SARA-lifetime-spec.md, PRD-VOICE-AGENT.md
│   ├── verticals/                 # VERTICALS-FINAL-6.md, MICRO-CATEGORIE-PMI.md
│   ├── compliance/                # GDPR-AUDIT-TRAIL-PLAN.md
│   ├── support-emails/            # email founder → cliente sanitizzate (PII redacted)
│   └── transcripts/               # YouTube/screen-recording transcripts (skill youtube-transcript-fetch)
└── wiki/                          # LLM-MANAGED pages, l'agente ha ownership totale
    ├── overview.md                # synthesis page, entry point per nuovi agenti/founder
    ├── entities/                  # cose CONCRETE (1 file = 1 cosa nominabile)
    │   ├── win10-installation.md
    │   ├── win11-installation.md
    │   ├── macos-installation.md
    │   ├── license-key.md
    │   ├── sara-voice-agent.md
    │   ├── stripe-checkout.md
    │   ├── webview2-runtime.md
    │   └── ...
    ├── concepts/                  # idee TRASVERSALI (non riducibili a entità singola)
    │   ├── pricing-tiers.md       # Base €497 / Pro €897
    │   ├── verticals-coverage.md  # 6 macro × 17 sotto-verticali
    │   ├── gdpr-compliance.md
    │   ├── refund-policy.md
    │   ├── three-pillars.md       # Comunicazione / Marketing / Gestione
    │   ├── offline-capability.md
    │   └── ...
    └── sources/                   # 1 page = 1 source consumed (summary + cross-links)
        ├── win10-fresh-compat-summary.md
        ├── network-requirements-summary.md
        └── ...
```

**Motivazioni e trade-off**:

- **Tre directory `entities/concepts/sources/` invece di flat**: a ~50+ pagine il flat diventa illeggibile in `ls`. Separazione ortogonale a tag frontmatter (cumulativa). Trade-off: link interni più verbosi (`[[entities/win10-installation]]` vs `[[win10-installation]]`). Mitigato dalla regola "kebab-case file globalmente unico" → l'agente può linkare `[[win10-installation]]` e risolverlo via index.
- **`sources/` come 3a sub-dir wiki/** invece che dentro `raw/`: i summary sono LLM-generated (mutable), i raw no. Tenerli separati onora invariante "raw immutable".
- **`raw/support-emails/`**: PII redaction OBBLIGATORIA prima ingest (regex email/telefono/nome → `[CLIENTE_X]`). Se non sanitizzato → NON ingerire.
- **Niente `assets/` per ora**: helpdesk testuale, screenshot solo on-demand. Se servono → `raw/assets/` (Karpathy convention).
- **Alternative scartate**: (a) singolo file mega-FAQ.md → non scala, no cross-ref; (b) struttura per verticale (salone/palestra/...) → la maggior parte del contenuto è cross-verticale (install, license, pricing) → duplicazione inevitabile.

---

## 2. HELPDESK.md schema content (draft completo)

Il file `docs/helpdesk-wiki/HELPDESK.md` è THE config. Deve contenere ESATTAMENTE le sezioni seguenti, in quest'ordine:

### 2.1 Persona/role
> Sei il maintainer del FLUXION Helpdesk Wiki. Il tuo lavoro è leggere fonti curate dal founder, integrarle in pagine markdown interlinkate, mantenere il wiki coerente, e rispondere a query support con citazioni precise. Tu scrivi tutto in `wiki/`. Tu non tocchi mai `raw/`. Output sempre in italiano (target PMI italiane). Tono: chiaro, tecnico-friendly, zero gergo.

### 2.2 Workflow INGEST (step-by-step)
1. Leggi il source path fornito dall'utente (path relativo a `raw/`)
2. Discuti con l'utente i 3-5 takeaway chiave (output: bullet list + chiedi conferma prima di scrivere)
3. Crea `wiki/sources/<source-slug>-summary.md` con frontmatter + sezione Takeaways + sezione Citazioni-chiave (block quote con line range)
4. Identifica entità nominate nel source (es. "Win10", "WebView2", "license key"). Per ognuna:
   - Se `wiki/entities/<entity-slug>.md` esiste → AGGIORNA (aggiungi sezione, marca `last_ingest`)
   - Se non esiste → CREA con template entity (sez. 3.1)
5. Identifica concept trasversali (es. "GDPR", "refund"). Stesso flusso su `wiki/concepts/`
6. Aggiorna `wiki/overview.md` se il source cambia synthesis di alto livello (rare, ~1 ogni 5 ingest)
7. Aggiorna `index.md` aggiungendo/modificando le righe relative
8. Append entry a `log.md`: `## [YYYY-MM-DD HH:MM] ingest | <source-title>` + lista pagine toccate
9. Output finale all'utente: lista pagine create/modificate + 1-line summary per ognuna

### 2.3 Workflow QUERY (step-by-step)
1. Leggi `index.md` interamente (è piccolo, <500 righe a regime)
2. Identifica 2-5 pagine candidate dall'index (entities + concepts + sources)
3. Leggi quelle pagine
4. Compose answer in italiano, struttura: **Risposta diretta** (1-3 frasi) + **Dettagli** (se utile) + **Citazioni** (lista `[[link]]` con line numbers se applicabile)
5. Se il source primario non è nel wiki ma è in `raw/`, leggi il raw e cita con path completo
6. Se l'analisi prodotta è non-banale (es. comparison, decision matrix) → chiedi all'utente "Vuoi che archivi questo come pagina nel wiki?" → se sì, crea `wiki/concepts/<topic>.md` o `wiki/sources/<analysis-slug>.md`
7. Append entry log: `## [YYYY-MM-DD HH:MM] query | <question-summary>`

### 2.4 Workflow LINT (step-by-step)
1. Build inbound link map: per ogni file in `wiki/`, conta `[[link]]` entranti
2. Esegui checklist sez. 6 in ordine
3. Per ogni issue → aggiungi a `wiki/_lint-report.md` (overwrite ogni run) con sezione per categoria
4. Proporre all'utente fix prioritizzati (top 5)
5. Su conferma utente, applica fix uno alla volta
6. Append entry log: `## [YYYY-MM-DD HH:MM] lint | <N issues found, M fixed>`

### 2.5 Page templates → sez. 3 sotto

### 2.6 Naming conventions
- File: `kebab-case.md` (es. `win10-installation.md`, `gdpr-compliance.md`)
- Slug entità: nome canonico italiano se ovvio (`licenza-software.md`), altrimenti termine tecnico inglese se più chiaro (`webview2-runtime.md`)
- Internal link: `[[file-slug-no-extension]]` — l'agente risolve cercando in `wiki/entities/`, `wiki/concepts/`, `wiki/sources/` (kebab-case globalmente unico)
- Frontmatter: YAML obbligatorio, vedi sez. 2.7
- Citazione raw: `[raw/install/win10-fresh-compat.md:42-58]` (path + line range)
- Citazione wiki: `[[entity-slug]]` o `[[entity-slug#sezione]]`

### 2.7 Frontmatter convention
Schema YAML obbligatorio in cima a OGNI pagina wiki:

```yaml
---
title: "Win10 Installation"
type: entity                      # entity | concept | source-summary | overview | lint-report
slug: win10-installation          # = filename senza .md
sources_consumed:                 # list di raw/ paths usati per costruire questa pagina
  - raw/install/win10-fresh-compat.md
  - raw/install/alpha-3-VERIFY.md
last_ingest: 2026-05-04           # ultima data in cui è stata aggiornata da ingest
status: stable                    # draft | stable | stale | contradicted
related:                          # cross-ref espliciti a entità/concetti correlati
  - webview2-runtime
  - vc-runtime
  - license-key
verticals: [all]                  # [all] | [salone, palestra] | etc — copertura per verticale
---
```

### 2.8 Log entry format
```
## [2026-05-04 14:32] ingest | Win10 Fresh Compat
- raw: raw/install/win10-fresh-compat.md
- wiki touched: wiki/entities/win10-installation.md (CREATED), wiki/entities/webview2-runtime.md (UPDATED), wiki/concepts/install-prerequisites.md (UPDATED), wiki/sources/win10-fresh-compat-summary.md (CREATED)
- index.md: 4 entries added
```

Parsabile via `grep "^## \[" log.md | tail -10`.

---

## 3. Page templates

### 3.1 Entity page template

```markdown
---
title: "Win10 Installation"
type: entity
slug: win10-installation
sources_consumed:
  - raw/install/win10-fresh-compat.md
last_ingest: 2026-05-04
status: stable
related:
  - webview2-runtime
  - vc-runtime
  - license-key
verticals: [all]
---

# Win10 Installation

> Una riga di sintesi: cosa è e perché un cliente PMI ne legge questa pagina.

## TL;DR
2-4 bullet con risposta diretta a "come si fa" o "cosa devo sapere".

## Prerequisiti
- Win10 1909+ o Win11 (verificato `setup-win.bat`)
- 1 GB disco libero
- Connessione internet (solo primo avvio per attivazione license)

## Procedura
1. Step concreto
2. Step concreto
3. ...

## Errori comuni
| Sintomo | Causa | Fix |
|---------|-------|-----|
| "vcruntime140.dll missing" | VC++ runtime mancante | Risolto da static CRT v1.0.1+ ([[vc-runtime]]) |

## Cross-references
- [[webview2-runtime]] — runtime embedded nell'installer
- [[license-key]] — attivazione post-install

## Sources
- [raw/install/win10-fresh-compat.md](../../raw/install/win10-fresh-compat.md) — compat matrix Win10/Win11
- [[sources/win10-fresh-compat-summary]]
```

### 3.2 Concept page template

```markdown
---
title: "GDPR Compliance"
type: concept
slug: gdpr-compliance
sources_consumed:
  - raw/compliance/gdpr-audit-trail-plan.md
last_ingest: 2026-05-04
status: stable
related:
  - data-residency
  - sentry-monitoring
  - license-key
verticals: [all]
---

# GDPR Compliance

> Idea trasversale: come FLUXION rispetta GDPR per PMI italiane.

## Tesi corrente
1-3 frasi sulla posizione consolidata. Se contraddetta da source futuri → flag `status: contradicted` e sezione "Contradictions".

## Perché importa per il cliente PMI
- Studio medico/clinica: dati sensibili Art.9
- Salone/palestra: dati cliente Art.5
- ...

## Come FLUXION lo risolve
- SQLite locale → no transit cloud per dati cliente ([[offline-capability]])
- Sentry DE region (no PII) ([[sentry-monitoring]])
- ...

## Domande aperte / Tech debt
- DPIA template per cliente → TODO

## Sources
- [[sources/gdpr-audit-trail-plan-summary]]
```

### 3.3 Source summary page template

```markdown
---
title: "Source Summary — Win10 Fresh Compat"
type: source-summary
slug: win10-fresh-compat-summary
sources_consumed:
  - raw/install/win10-fresh-compat.md
last_ingest: 2026-05-04
status: stable
related:
  - win10-installation
  - webview2-runtime
verticals: [all]
---

# Source Summary — Win10 Fresh Compat

**Original**: [raw/install/win10-fresh-compat.md](../../raw/install/win10-fresh-compat.md) (110 lines, S184 α.3.3)

## Takeaways
1. VC++ runtime risolto via static CRT (`+crt-static`) → zero dipendenze esterne
2. WebView2 embedded nell'installer NSIS (~150KB bootstrapper)
3. NSIS pre-flight hooks verificano Win10+, x64, 1GB disco
4. Test matrix: Win10 1909/22H2 + Win11 22H2

## Citazioni-chiave
> Static CRT elimina dipendenza vcruntime140.dll/msvcp140.dll (top install failure ~25% Win10 fresh PMI). Trade-off ~+1.5MB binario.
> — [raw/install/win10-fresh-compat.md:23-27]

## Pagine wiki impattate
- [[win10-installation]] — CREATED
- [[webview2-runtime]] — sezione "embed mode" UPDATED
- [[vc-runtime]] — CREATED

## Status
stable — fonte tecnica autoritativa interna FLUXION (S184 closure).
```

---

## 4. Internal link conventions

- **Sintassi**: `[[slug]]` (Obsidian-style). NO path completi nei link. Slug = filename senza `.md`. Globalmente unico (kebab-case enforced).
- **Eccezione**: link a sezione → `[[slug#sezione-kebab]]`.
- **Risoluzione agente**: cerca in ordine `wiki/entities/<slug>.md` → `wiki/concepts/<slug>.md` → `wiki/sources/<slug>.md`. Se non trova → propone creazione (potential orphan).
- **Path relativi a `raw/`**: usa path completo da root wiki (`../../raw/install/file.md`) — link standard markdown, NON `[[ ]]`.
- **Quando creare nuova page vs estendere esistente**:
  - Nuova page: il termine ha (a) nome canonico riconoscibile dal cliente, (b) almeno 3 cross-ref attesi, (c) >150 parole di contenuto specifico.
  - Estendi esistente: il termine è una variazione/sottosezione (es. "Win10 22H2" è sezione di [[win10-installation]], non pagina nuova).
- **Bidirectional links**: agente OBBLIGATO durante ingest a verificare reciprocità. Se A linka B → B deve avere link a A nella sezione "Cross-references" o "Related" frontmatter. Lint check sez. 6.

---

## 5. Query interface design

### Decision tree generale
```
1. Parse query → estrai keyword + intent (install / pricing / voice / vertical / compliance / billing)
2. Read index.md → match keyword/intent a 2-5 candidate pages
3. Read candidate pages
4. Se confidence alta (≥1 page risponde direttamente) → compose answer + citations
5. Se confidence bassa → leggi raw/ corrispondenti via sources_consumed frontmatter
6. Se ancora insufficiente → flag "knowledge gap" → suggerisci ingest source
```

### Esempi concreti

**Q: "Cliente chiede come installo su Win10"**
- Step 1: intent=install, keywords=[win10, installazione]
- Step 2: index match → [[win10-installation]] (entity), [[install-prerequisites]] (concept)
- Step 3: leggi entrambe
- Step 4: compose:
  ```
  Per installare FLUXION su Windows 10:

  **Prerequisiti** ([[install-prerequisites]]):
  - Win10 versione 1909 o successiva
  - 1 GB disco libero
  - Connessione internet (solo primo avvio)

  **Procedura** ([[win10-installation]]):
  1. Scarica `Fluxion_1.0.1_x64-setup.exe` dal link email
  2. Doppio click — l'installer include WebView2 e VC++ runtime
  3. Inserisci license key ricevuta via email ([[license-key]])

  **Errori comuni**: vedi sezione "Errori comuni" in [[win10-installation]].

  Fonti: [[win10-installation]], [[install-prerequisites]],
  [raw/install/win10-fresh-compat.md](docs/helpdesk-wiki/raw/install/win10-fresh-compat.md)
  ```
- Step 7: log entry

**Q: "Quanto costa Pro?"**
- Step 1: intent=pricing
- Step 2: index match → [[pricing-tiers]]
- Step 4: compose:
  ```
  **Pro €897** lifetime — pagamento unico, NO subscription.

  Include:
  - Tutto del piano Base (€497)
  - 1 verticale dedicato a scelta ([[verticals-coverage]])
  - Sara voice agent permanente (Base ha 30gg trial)

  Fonti: [[pricing-tiers]] (synthesis da CLAUDE.md project + landing).
  ```

**Q: "Ho problema con microfono Sara"**
- Step 1: intent=voice/troubleshooting
- Step 2: index match → [[sara-voice-agent]] (entity), [[microphone-setup]] (concept se esiste)
- Step 3: lettura
- Step 4: se [[microphone-setup]] non esiste → flag gap, leggi raw/voice/SARA-lifetime-spec.md, costruisci risposta + propone "Vuoi che crei pagina [[microphone-setup]]?"
- Step 6: file-back se confermato

### Output format standard query
```markdown
## Risposta

<1-3 frasi diretta>

## Dettagli

<bullet o paragrafi>

## Citazioni

- [[wiki-page-1]] — <relevance>
- [[wiki-page-2]] — <relevance>
- [raw/path/file.md:lines] — <if direct quote>

---
File-back? [[suggested-new-page-slug]] — propose se rilevante.
```

---

## 6. Lint checklist concreto

Eseguire in quest'ordine. Output → `wiki/_lint-report.md`.

### 6.1 Structural
- [ ] Ogni file in `wiki/` ha frontmatter YAML valido (parse safe)
- [ ] Ogni frontmatter ha campi obbligatori: `title`, `type`, `slug`, `last_ingest`, `status`
- [ ] `slug` == filename (sans `.md`)
- [ ] Nessun duplicato di slug across `entities/concepts/sources/`

### 6.2 Link integrity
- [ ] Ogni `[[link]]` risolve a un file esistente
- [ ] Pagine SENZA inbound links (orphan): se age > 30gg → flag review (proposta merge/delete)
- [ ] Pagine HUB con >20 inbound links: flag per possibile split

### 6.3 Bidirectional consistency
- [ ] Se A.related contiene B → B.related contiene A. Else flag "asymmetric ref"

### 6.4 Freshness
- [ ] `last_ingest` > 90gg → flag `status: stale` (review need)
- [ ] `status: draft` > 14gg → flag promote-or-delete

### 6.5 Contradictions (regex-based per dominio FLUXION)
- [ ] Pricing: `grep -E "€\s*(497|897)|prezzo|pricing|costo"` su tutto wiki → check coerenza tier (Base 497, Pro 897). Flag se trovati altri numeri non spiegati.
- [ ] Versioni: `grep -E "v?1\.[0-9]+\.[0-9]+"` → versione corrente FLUXION coerente
- [ ] Endpoint: `grep -E "https?://[a-z0-9.-]+"` → no domain inattesi (white-list: fluxion-landing.pages.dev, fluxion-proxy.gianlucanewtech.workers.dev, github.com/lukeeterna)
- [ ] Email: solo `fluxion.gestionale@gmail.com` o `onboarding@resend.dev` (white-list)
- [ ] Verticali: count distinto rispetta "6 macro × 17 sotto" (CLAUDE.md). Flag se cita "5 verticali" o numeri diversi.

### 6.6 Coverage gaps (FLUXION-specific)
Per ognuno dei 3 pilastri (Comunicazione/Marketing/Gestione) deve esistere ≥1 entity + ≥1 concept page.
Per ogni macro-verticale deve esistere ≥1 page riferita.
Mancanza → flag gap con suggested page slug.

### 6.7 PII leak (CRITICAL)
- [ ] Regex telefono italiano `\+?39?\s?\d{3}\s?\d{6,7}` → 0 match in `wiki/`
- [ ] Regex email cliente (qualsiasi che NON sia white-list) → 0 match
- [ ] Nome cliente in chiaro → human review, troppo costoso regex (delegare manual)
- [ ] Trovato match → blocca commit, flag CRITICAL

---

## 7. Trade-off discussion

### 7.1 Internal-only vs public CF Pages mirror
- **Internal-only (default)**: helpdesk privato founder, NO mirror pubblico. Founder copia-incolla risposta in email cliente. Pro: zero compliance overhead, controllo totale tono. Contro: founder bottleneck.
- **Public CF Pages mirror (futuro v2)**: build statico Astro/Hugo da `wiki/` → `helpdesk.fluxion-landing.pages.dev`. Pro: cliente self-service, riduce volume email. Contro: tone-of-voice review obbligatoria, risk PII leak, search infra.
- **Decisione S185-A**: internal-only. Mirror pubblico = tech debt v2 dopo 10 clienti reali (allineato vincolo dominio CLAUDE.md).

### 7.2 Search CLI (qmd) vs index.md only
- **index.md only**: funziona fino a ~100-150 pagine (~50KB index). Karpathy conferma "moderate scale".
- **qmd CLI** (BM25+vector locale): switch quando index.md > 50KB o agente impiega >5s a leggere index.
- **Threshold concreto**: 100 pagine totali in `wiki/` → install qmd. Fino a quel punto, index.md sufficiente. Stima realistica S185 FASE 3 seed: 15-25 pagine. qmd NON necessario v1.

### 7.3 Manual founder ingest vs auto-ingest da support email
- **Manual (default v1)**: founder droppa file in `raw/support-emails/` con PII redaction → `/ingest <path>` → agente esegue workflow. Vantaggio: PII review human-in-the-loop garantita.
- **Auto-ingest** (v2): cron job legge inbox Gmail, redact PII via regex+LLM, dump in `raw/support-emails/`, trigger agent ingest. Rischio: PII leak se redaction fallisce. NON FARE in v1.
- **Decisione**: manual ingest v1. Eventuale auto in v2 con LLM-based PII redactor verificato.

---

## 8. AC misurabili per FASE 3 IMPLEMENT

Definition of Done FASE 3 — ognuno verificabile da agente successivo:

- [ ] **AC1**: `docs/helpdesk-wiki/HELPDESK.md` esiste, ≥250 righe, contiene tutte le 8 sottosezioni di sez. 2 di questo doc
- [ ] **AC2**: `docs/helpdesk-wiki/index.md` skeleton creato con sezioni `## Entities`, `## Concepts`, `## Sources`, `## Overview` (anche se vuote inizialmente)
- [ ] **AC3**: `docs/helpdesk-wiki/log.md` skeleton con prima entry `## [YYYY-MM-DD HH:MM] bootstrap | wiki initialized` + lista files creati
- [ ] **AC4**: `docs/helpdesk-wiki/wiki/overview.md` creato (synthesis page entry-point) con frontmatter + sezione "Wiki structure" + sezione "How to query"
- [ ] **AC5**: ≥5 wiki seed pages create rispettando i template sez. 3:
  - `wiki/entities/win10-installation.md`
  - `wiki/entities/license-key.md`
  - `wiki/entities/sara-voice-agent.md`
  - `wiki/concepts/pricing-tiers.md`
  - `wiki/concepts/three-pillars.md`
- [ ] **AC6**: ≥1 raw source ingerito end-to-end (`raw/install/win10-fresh-compat.md` copiato da `scripts/install/docs/win10-fresh-compat.md`) con `wiki/sources/win10-fresh-compat-summary.md` corrispondente
- [ ] **AC7**: log.md contiene ≥1 entry `ingest` oltre a bootstrap
- [ ] **AC8**: Query test E2E — esegui query "Come installo su Win10?" → answer contiene ≥2 citation `[[link]]` valide + ≥1 ref a `raw/`
- [ ] **AC9**: Lint test — esegui checklist sez. 6 → produce `wiki/_lint-report.md` con 0 issue CRITICAL (PII), max 2 issue WARN (stale/orphan acceptable seed-state)
- [ ] **AC10**: Tutti i frontmatter YAML valid-parsabili (verifica `python3 -c "import yaml,sys; [yaml.safe_load(open(f).read().split('---')[1]) for f in sys.argv[1:]]" wiki/**/*.md`)
- [ ] **AC11**: Ogni `[[link]]` in seed pages risolve a file esistente (no broken)
- [ ] **AC12**: Frontmatter `verticals` coerente: `[all]` o subset di `{salone, palestra, medical, auto, clinica, officina}`
- [ ] **AC13**: Documentato in `HANDOFF.md` come triggerare workflow ingest/query/lint da nuova sessione (esempio comando `/ingest raw/install/win10-fresh-compat.md`)

Stima FASE 3 implement: ~6-8h (3 setup + 3 seed pages + 1 ingest + 1 verify).

---

## 9. Note operative per agente FASE 3

- Iniziare da `HELPDESK.md` (è il file che si auto-spiega — ogni dubbio futuro si risolve leggendolo)
- Seed pages devono essere REALI, non placeholder. Estrarre contenuto da: `CLAUDE.md`, `scripts/install/docs/win10-fresh-compat.md`, `docs/SARA-lifetime-spec.md`, MEMORY.md.
- NON inventare. Se manca info → frontmatter `status: draft` + sezione `## TODO research`.
- Commit atomico per AC: 1 commit per "skeleton" (AC1-3), 1 per "seed pages" (AC4-5), 1 per "first ingest" (AC6-7), 1 per "verify" (AC8-13).
- Test E2E AC8 OBBLIGATORIO prima di chiudere FASE 3 (rule `.claude/rules/e2e-testing.md`).
