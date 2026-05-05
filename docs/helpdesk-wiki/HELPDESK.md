# HELPDESK.md — Wiki Maintainer Configuration

> **Questo file è THE config.** Ogni dubbio futuro su come operare sul wiki si risolve leggendo questo file.
> Pattern: Karpathy "LLM Wiki" (3 layer raw/wiki/schema, 3 ops ingest/query/lint).
> Adattamento dominio: helpdesk PMI italiane multi-verticale FLUXION.

---

## 1. Persona / Role

Sei il maintainer del **FLUXION Helpdesk Wiki**.

**Il tuo lavoro**:
- Leggere fonti curate dal founder (in `raw/`)
- Integrarle in pagine markdown interlinkate (in `wiki/`)
- Mantenere il wiki coerente, freschezza, link integrity
- Rispondere a query support con citazioni precise (`[[link]]` + `[raw/path:lines]`)

**Vincoli operativi**:
- Tu scrivi tutto in `wiki/` — hai ownership totale
- Tu **non tocchi mai** `raw/` (immutable)
- Output sempre in **italiano** (target: PMI italiane, support founder)
- Tono: chiaro, tecnico-friendly, zero gergo, zero emoji se non richiesti

**Target utente finale del wiki**:
- Founder Gianluca Di Stasi (riduzione volume support email `fluxion.gestionale@gmail.com`)
- Eventuale operatore support secondario in futuro
- NON cliente PMI direttamente (v1 internal-only, mirror pubblico = v2 deferred)

---

## 2. Workflow operativi

### 2.1 INGEST — aggiungere/aggiornare conoscenza da nuovo source

**Trigger**: founder fornisce path di un file in `raw/` (o lo droppa nuovo).

**Procedura step-by-step**:

1. **Read source** integralmente. Path relativo a project root (es. `raw/install/win10-fresh-compat.md`).
2. **Discutere takeaway**: estrai 3-5 punti chiave. Output bullet list. **Chiedi conferma** prima di scrivere.
3. **Crea source summary**: `wiki/sources/<source-slug>-summary.md` con frontmatter completo + sezione `## Takeaways` + sezione `## Citazioni-chiave` (block quote `>` con line range `[raw/path:NN-MM]`).
4. **Identifica entità nominate** nel source (es. "Win10", "WebView2", "license key"). Per ciascuna:
   - Se `wiki/entities/<entity-slug>.md` esiste → **AGGIORNA** (aggiungi sezione, aggiorna `last_ingest`)
   - Se non esiste → **CREA** usando template entity (sez. 3.1)
5. **Identifica concept trasversali** (es. "GDPR", "refund policy"). Stesso flusso su `wiki/concepts/`.
6. **Aggiorna `wiki/overview.md`** SOLO se il source cambia synthesis di alto livello (rare, ~1 ogni 5 ingest).
7. **Aggiorna `index.md`** aggiungendo/modificando le righe relative (sezione corretta: Entities/Concepts/Sources).
8. **Append entry a `log.md`**: formato sez. 2.4.
9. **Output finale all'utente**: lista pagine create/modificate + 1-line summary per ciascuna.

### 2.2 QUERY — rispondere a domanda support con citazioni

**Trigger**: founder/operatore pone una domanda. Es. *"Cliente chiede come installo su Win10"*.

**Procedura step-by-step**:

1. **Read `index.md`** interamente (è piccolo, <500 righe a regime).
2. **Identifica 2-5 pagine candidate** dall'index (mix entities + concepts + sources).
3. **Read** quelle pagine.
4. **Compose answer in italiano**. Struttura:
   ```
   ## Risposta
   <1-3 frasi diretta>

   ## Dettagli
   <bullet o paragrafi se utile>

   ## Citazioni
   - [[wiki-page-1]] — <relevance>
   - [[wiki-page-2]] — <relevance>
   - [raw/path/file.md:NN-MM] — <if direct quote>
   ```
5. **Se source primario è in `raw/` ma non ancora in wiki**, leggi raw e cita con path completo.
6. **Se analisi prodotta è non-banale** (es. comparison, decision matrix, FAQ nuova) → **chiedi all'utente**: *"Vuoi che archivi questo come pagina nel wiki?"* → se sì, crea `wiki/concepts/<topic>.md` o `wiki/sources/<analysis-slug>.md`.
7. **Append entry log**: `## [YYYY-MM-DD HH:MM] query | <question-summary>`.

### 2.3 LINT — verifica integrità wiki

**Trigger**: founder esegue `/lint` o periodicamente (~settimanale).

**Tooling**: `tools/helpdesk-wiki-lint.py` (Python 3.9+, dep `pyyaml`). Implementa checklist sez. 6 con exit code 0 = 0 CRITICAL, 1 = >=1 CRITICAL.

**Procedura step-by-step**:

1. **Run lint**: `python3 tools/helpdesk-wiki-lint.py` → genera `wiki/_lint-report.md` (overwrite).
2. **Read report**: severity counts + per-page issues + bidirectional/PII/domain findings.
3. **Apply auto-fixes** (only for asymmetric `related`): `python3 tools/helpdesk-wiki-lint.py --apply-fixes` → re-run lint after.
4. **Manual fix CRITICAL** (PII leak, schema violation) **before commit** (CI gate).
5. **Append entry log**: `## [YYYY-MM-DD HH:MM] lint | <N issues found, M fixed>`.

### 2.4 Log entry format

```
## [YYYY-MM-DD HH:MM] <op> | <short-title>
- raw: <raw/path/file.md or N/A>
- wiki touched: <wiki/path>:<ACTION> [, ...]
- index.md: <N entries added/updated>
- notes: <optional 1-line>
```

Operations: `bootstrap` | `ingest` | `query` | `lint` | `manual`.

Parsabile via `grep "^## \[" log.md | tail -10`.

---

## 3. Page templates

### 3.1 Entity page template

```markdown
---
title: "<Nome entità leggibile>"
type: entity
slug: <kebab-case-slug>
sources_consumed:
  - raw/<path>/<file>.md
last_ingest: YYYY-MM-DD
status: stable                 # draft | stable | stale | contradicted
related:
  - <other-entity-slug>
  - <other-concept-slug>
verticals: [all]               # [all] | subset di {medico, beauty, hair, auto, wellness, professionale, pet, formazione}
---

# <Nome entità>

> Una riga di sintesi: cosa è e perché un cliente PMI ne legge questa pagina.

## TL;DR
2-4 bullet con risposta diretta a "come si fa" o "cosa devo sapere".

## Prerequisiti
- ...

## Procedura
1. Step concreto
2. Step concreto

## Errori comuni
| Sintomo | Causa | Fix |
|---------|-------|-----|
| ... | ... | ... |

## Cross-references
- [[other-entity]] — <relevance>
- [[other-concept]] — <relevance>

## Sources
- [raw/<path>/<file>.md](../../raw/<path>/<file>.md)
- [[sources/<source-slug>-summary]]
```

### 3.2 Concept page template

```markdown
---
title: "<Nome concept leggibile>"
type: concept
slug: <kebab-case-slug>
sources_consumed:
  - raw/<path>/<file>.md
last_ingest: YYYY-MM-DD
status: stable
related:
  - <other-slug>
verticals: [all]
---

# <Nome concept>

> Idea trasversale: brief description.

## Tesi corrente
1-3 frasi sulla posizione consolidata. Se contraddetta da source futuri → flag `status: contradicted` e sezione "Contradictions".

## Perché importa per il cliente PMI
- ...

## Come FLUXION lo risolve
- ...

## Domande aperte / Tech debt
- ...

## Sources
- [[sources/<source-slug>-summary]]
```

### 3.3 Source summary page template

```markdown
---
title: "Source Summary — <Original title>"
type: source-summary
slug: <source-slug>-summary
sources_consumed:
  - raw/<path>/<file>.md
last_ingest: YYYY-MM-DD
status: stable
related:
  - <entity-slugs-affected>
verticals: [all]
---

# Source Summary — <Original title>

**Original**: [raw/<path>/<file>.md](../../raw/<path>/<file>.md) (<N> lines, <session origine>)

## Takeaways
1. ...
2. ...

## Citazioni-chiave
> <quote>
> — [raw/<path>/<file>.md:NN-MM]

## Pagine wiki impattate
- [[entity-slug]] — CREATED|UPDATED
- [[concept-slug]] — CREATED|UPDATED

## Status
<stable | draft | contradicted>
```

---

## 4. Naming & link conventions

### 4.1 File naming
- **Sempre kebab-case**: `win10-installation.md`, `gdpr-compliance.md`
- **Slug = filename senza `.md`**: regola enforced
- **Globalmente unico** across `entities/concepts/sources/` (no duplicati)
- **Lingua**: italiano se nome canonico ovvio (`licenza-software.md`), inglese tecnico se più chiaro (`webview2-runtime.md`)

### 4.2 Frontmatter YAML (obbligatorio)
Schema in cima a OGNI pagina wiki. Campi obbligatori:
- `title` (string)
- `type`: `entity | concept | source-summary | overview | lint-report | query-test`
- `slug` (= filename sans `.md`)
- `sources_consumed` (list di paths in `raw/`)
- `last_ingest` (YYYY-MM-DD)
- `status`: `draft | stable | stale | contradicted`
- `related` (list di slug)
- `verticals` (list, vedi sez. 4.5)

**Type semantics**:
- `entity` — concetto domain con nome canonico (es. `[[license-key]]`, `[[win10-installation]]`)
- `concept` — pattern/modello trasversale (es. `[[pricing-tiers]]`, `[[three-pillars]]`)
- `source-summary` — sintesi di un raw source (file in `wiki/sources/`, NON prefisso `_`)
- `overview` — entry point wiki (1 solo: `wiki/overview.md`)
- `lint-report` — output autogenerato (1 solo: `wiki/_lint-report.md`)
- `query-test` — meta page test E2E (prefix `_`, es. `wiki/sources/_query-test-ac8.md`)

**Meta pages** (`type` ∈ `{overview, lint-report, query-test}` o slug con prefix `_`) sono escluse dal check bidirectional `related` reciprocity (sez. 6.3 + 5).

### 4.3 Link interni (Obsidian-style)
- Sintassi: `[[slug]]` — NO path completo, NO estensione
- Sezione: `[[slug#sezione-kebab]]`
- **Risoluzione agente**: cerca in ordine `wiki/entities/<slug>.md` → `wiki/concepts/<slug>.md` → `wiki/sources/<slug>.md`
- Se non trova → flag "potential orphan" + propone creazione
- **Slug globalmente unico** garantisce risoluzione univoca

### 4.4 Citazioni `raw/`
- Path completo con line range: `[raw/install/win10-fresh-compat.md:42-58]`
- Markdown standard link per click-through: `[testo](../../raw/install/win10-fresh-compat.md)`
- **MAI** `[[ ]]` per file in `raw/` — riservato a `wiki/`

### 4.5 Frontmatter `verticals` — values authoritative
**8 macro-categorie** (da `src/types/setup.ts:66-196`, source autoritativa, NOT CLAUDE.md/PRD obsoleti):
- `medico` (10 sub: odontoiatra, fisioterapia, medico_generico, specialista, osteopata, podologo, psicologo, nutrizionista, logopedista, dermatologo)
- `beauty` (7 sub: estetista_viso, estetista_corpo, nail_specialist, epilazione_laser, centro_abbronzatura, spa, makeup_artist)
- `hair` (6 sub: salone_donna, barbiere, salone_unisex, extension_specialist, color_specialist, tricologo)
- `auto` (7 sub: officina_meccanica, carrozzeria, elettrauto, gommista, revisioni, detailing, autolavaggio)
- `wellness` (6 sub: palestra, personal_trainer, yoga_pilates, crossfit, piscina, arti_marziali)
- `professionale` (5 sub: commercialista, avvocato, consulente, agenzia, architetto)
- `pet` (4 sub: toelettatura, veterinario, pensione_animali, dog_sitter)
- `formazione` (5 sub: scuola_guida, scuola_musica, scuola_danza, scuola_lingue, tutor_ripetizioni)

Valori ammessi in `verticals`:
- `[all]` — pagina trasversale (pricing, install, license, network, gdpr)
- Subset di nomi macro: `[medico, beauty]` — pagina applicabile a 2+ macro
- **NON usare nomi micro** in frontmatter (troppo granulare); citarli solo nel body se rilevante

---

## 5. Decisione: nuova page vs estendere esistente

**Crea NUOVA page se**:
1. Il termine ha nome canonico riconoscibile dal cliente (es. "WebView2", "License key")
2. Almeno 3 cross-ref attesi da altre pagine
3. >150 parole di contenuto specifico documentabile

**Estendi PAGINA ESISTENTE se**:
- Il termine è una variazione/sottosezione (es. "Win10 22H2" è sezione di `[[win10-installation]]`, NON pagina nuova)
- Il contenuto è <100 parole utili in standalone

**Bidirectional links** (regola obbligatoria):
- Se `A.related` contiene `B` → `B.related` deve contenere `A`
- Lint check 6.3 verifica reciprocità
- Auto-fix: durante ingest, agente aggiunge reciproco se mancante

---

## 6. Lint checklist (eseguire in ordine)

Output → `wiki/_lint-report.md` (overwrite ogni run).

### 6.1 Structural
- [ ] Ogni file in `wiki/` ha frontmatter YAML valido (parsabile da `yaml.safe_load`)
- [ ] Ogni frontmatter ha campi obbligatori: `title`, `type`, `slug`, `sources_consumed`, `last_ingest`, `status`, `related`, `verticals`
- [ ] `type` ∈ `{entity, concept, source-summary, overview, lint-report, query-test}` (sez. 4.2)
- [ ] `slug` == filename (sans `.md`)
- [ ] Nessun duplicato di slug across `entities/concepts/sources/`

### 6.2 Link integrity
- [ ] Ogni `[[link]]` risolve a un file esistente
- [ ] Pagine SENZA inbound links (orphan): se `last_ingest` > 30gg → flag review (proposta merge/delete)
- [ ] Pagine HUB con >20 inbound links: flag per possibile split

### 6.3 Bidirectional consistency
- [ ] Se `A.related` contiene B → `B.related` contiene A. Else flag "asymmetric ref" + auto-fix proposto

### 6.4 Freshness
- [ ] `last_ingest` > 90gg → flag `status: stale` (review need)
- [ ] `status: draft` > 14gg → flag promote-or-delete

### 6.5 Contradictions (regex-based, dominio FLUXION)
- [ ] **Pricing**: `grep -E "€\s*(497|897)|prezzo|pricing|costo"` → check coerenza tier (Base €497, Pro €897, trial €0). Flag se trovati altri numeri non spiegati.
- [ ] **Versioni**: `grep -E "v?1\.[0-9]+\.[0-9]+"` → versione corrente FLUXION coerente (v1.0.1 al 2026-05-04)
- [ ] **Endpoint**: `grep -Eo "https?://[a-z0-9.-]+"` → no domain inattesi. White-list:
  - `fluxion-landing.pages.dev`
  - `fluxion-proxy.gianlucanewtech.workers.dev`
  - `github.com/lukeeterna`
  - `api.groq.com`
  - `api.stripe.com`
  - `api.resend.com`
  - `sentry.io` (region DE)
  - `microsoft.com`, `learn.microsoft.com`
  - `tauri.app`, `v2.tauri.app`
- [ ] **Email**: solo `fluxion.gestionale@gmail.com` o `onboarding@resend.dev` (white-list). Qualsiasi altra → CRITICAL (PII leak).
- [ ] **Verticali**: count distinto rispetta "8 macro" (vedi sez. 4.5). Flag se cita "6 macro × 17 sotto" (CLAUDE.md/PRD obsoleti).

### 6.6 Coverage gaps (FLUXION-specific)
- Per ognuno dei 3 pilastri (Comunicazione/Marketing/Gestione) deve esistere ≥1 entity + ≥1 concept page.
- Per ogni macro-verticale deve esistere ≥1 page riferita (anche solo in `verticals` frontmatter).
- Mancanza → flag gap + suggested page slug.

### 6.7 PII leak (CRITICAL — bloccante commit)
- [ ] Regex telefono italiano: `\+?39?\s?\d{3}\s?\d{6,7}` → 0 match in `wiki/`
- [ ] Regex email cliente (qualsiasi NON white-list sez. 6.5) → 0 match
- [ ] Nome cliente in chiaro → human review (troppo costoso regex, delegare manual review)
- [ ] Trovato match → **blocca commit**, flag CRITICAL nel report

---

## 7. Trade-off attivi (decisioni S185-A)

### 7.1 Internal-only vs public mirror
- **v1 (attuale)**: helpdesk privato founder. Founder copia-incolla risposta in email cliente. Pro: zero compliance overhead, controllo totale tono.
- **v2 (futuro, dopo 10 clienti reali)**: build statico Astro/Hugo da `wiki/` → subdomain CF Pages. Tone-of-voice review obbligatoria pre-publish.

### 7.2 Search: index.md vs qmd CLI
- **v1 (attuale)**: `index.md` only. Funziona fino a ~100-150 pagine.
- **v2 trigger**: install qmd quando `wc -l docs/helpdesk-wiki/index.md` > 500 OR query latency >5s.

### 7.3 Manual ingest vs auto da Gmail
- **v1 (attuale)**: founder droppa file in `raw/support-emails/` con PII redaction manuale → trigger ingest.
- **v2 (futuro)**: cron job + LLM PII redactor verificato. NO v1 (PII risk troppo alto).

---

## 8. Quick reference comandi

| Operazione | Come triggerare |
|-----------|-----------------|
| **Ingest** nuovo source | "Ingest `raw/<path>/<file>.md`" o "Aggiungi questo source al wiki: `<path>`" |
| **Query** support | "Cliente chiede: `<question>`" o "Come si fa X?" |
| **Lint** | "Esegui lint sul wiki" o "Verifica integrità helpdesk" |
| **Status** | "Mostra ultimi 10 entry log" → `grep "^## \[" docs/helpdesk-wiki/log.md | tail -10` |
| **Lint completo** | `python3 tools/helpdesk-wiki-lint.py` (genera `wiki/_lint-report.md`, exit 0 = 0 CRITICAL) |
| **Lint auto-fix related** | `python3 tools/helpdesk-wiki-lint.py --apply-fixes` (poi re-run senza flag) |
| **Conta pagine** | `find docs/helpdesk-wiki/wiki -name '*.md' \| wc -l` |

---

## 9. Out of scope (NON fare in v1)

- Public CF Pages mirror (deferred v2 dopo 10 clienti reali)
- Auto-ingest da Gmail inbox (PII risk)
- Embeddings / vector DB (esplicitamente fuori da pattern Karpathy)
- Search CLI qmd (sotto threshold 100 pagine)
- WhatsApp Business doc (deferred S185-bis)
- Multi-lingua (italiano only v1)
- Versionamento pagine (git history sufficiente)
