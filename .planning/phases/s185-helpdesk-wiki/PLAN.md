# S185-A — FLUXION Helpdesk Wiki (Karpathy LLM Wiki pattern)

**Phase**: S185-A | **Status**: in_progress | **Created**: 2026-05-04
**Research inputs**:
- `.claude/cache/agents/s185/research-1-source-audit.md` (45 sources, 10 seed pages, 8 gaps)
- `.claude/cache/agents/s185/research-2-wiki-schema.md` (schema completo, AC misurabili, templates)
- `.claude/cache/agents/s185/karpathy-llm-wiki-gist.md` (gist originale verificato)

## Goal
Riduzione volume support email founder via knowledge base markdown LLM-managed (pattern Karpathy: `raw → wiki → schema`, ops `ingest/query/lint`). Internal-only v1 (no public mirror), filesystem + grep (no embeddings).

## Decisioni architetturali (delta vs research)
1. **Pricing canonico** = `Base €497 / Pro €897` (CLAUDE.md/MEMORY autoritativi, ignoro PRD obsoleto cit. research-1).
2. **Path** = `docs/helpdesk-wiki/` (root project, gitignored solo `raw/support-emails/` per PII safety).
3. **Verticali frontmatter**: subset di `{medico, beauty, hair, auto, wellness, professionale, pet, formazione}` (8 macro per `src/types/setup.ts`, NON 6 come citato CLAUDE.md — CLAUDE.md è obsoleto su questo punto, source primaria è il codice).
4. **Seed scope FASE 3**: 5 pagine minime (AC5) ma punto a 8 (Win10 + License + Sara + Pricing + Pillars + Verticals + Network + GDPR) per coverage 3-pillar e gap critici.
5. **Lint MVP**: implemento checklist sez. 6 ma report inline (output a console + `wiki/_lint-report.md`), NO automation cron.

## AC consolidati (da research-2 sez. 8 + delta)

### Skeleton (commit 1)
- [ ] AC1: `HELPDESK.md` ≥250 righe, 8 sezioni schema
- [ ] AC2: `index.md` skeleton (Entities/Concepts/Sources/Overview)
- [ ] AC3: `log.md` skeleton + bootstrap entry
- [ ] AC4: `wiki/overview.md` synthesis page

### Seed (commit 2)
- [ ] AC5+: 8 wiki seed pages (extends research min 5):
  - `wiki/entities/win10-installation.md`
  - `wiki/entities/license-key.md`
  - `wiki/entities/sara-voice-agent.md`
  - `wiki/entities/network-firewall.md`
  - `wiki/concepts/pricing-tiers.md`
  - `wiki/concepts/three-pillars.md`
  - `wiki/concepts/verticals-coverage.md`
  - `wiki/concepts/gdpr-compliance.md`

### Ingest E2E (commit 3)
- [ ] AC6: `raw/install/win10-fresh-compat.md` copiato + `wiki/sources/win10-fresh-compat-summary.md` creato
- [ ] AC7: log.md ingest entry

### Verify (commit 4)
- [ ] AC8: Query test "Come installo su Win10?" → answer ≥2 citation valide
- [ ] AC9: Lint MVP report 0 CRITICAL (PII)
- [ ] AC10: YAML frontmatter all-valid (script python verifica)
- [ ] AC11: Tutti `[[link]]` risolvono
- [ ] AC12: `verticals` coerenti
- [ ] AC13: Update `HANDOFF.md` con run instructions

## Anti-goals (esplicitamente NON in scope S185-A)
- Public CF Pages mirror (deferred v2 dopo 10 clienti)
- Auto-ingest da Gmail inbox (PII risk, v2)
- qmd CLI search (sotto threshold 100 pagine)
- WhatsApp Business doc (gap noto, deferred S185-bis se serve)
- Embeddings/vector DB (esplicitamente fuori dal pattern Karpathy)

## Stima
~6-8h FASE 3 IMPLEMENT + ~1h VERIFY + ~30min DEPLOY/closure = ~10h totali. In linea con scope ~12h annunciato S184 closure.

## Verticali authoritative (da `src/types/setup.ts` letto 2026-05-04)
**8 macro × ~50 micro categorie** (NOT 6×17 come dice CLAUDE.md/PRD obsoleti):
- `medico` (10): odontoiatra, fisioterapia, medico_generico, specialista, osteopata, podologo, psicologo, nutrizionista, logopedista, dermatologo
- `beauty` (7): estetista_viso, estetista_corpo, nail_specialist, epilazione_laser, centro_abbronzatura, spa, makeup_artist
- `hair` (6): salone_donna, barbiere, salone_unisex, extension_specialist, color_specialist, tricologo
- `auto` (7): officina_meccanica, carrozzeria, elettrauto, gommista, revisioni, detailing, autolavaggio
- `wellness` (6): palestra, personal_trainer, yoga_pilates, crossfit, piscina, arti_marziali
- `professionale` (5): commercialista, avvocato, consulente, agenzia, architetto
- `pet` (4): toelettatura, veterinario, pensione_animali, dog_sitter
- `formazione` (5): scuola_guida, scuola_musica, scuola_danza, scuola_lingue, tutor_ripetizioni

## License tiers authoritative (da `src/types/setup.ts:202-227`)
- `trial`: €0, 30gg, 1 nicchia
- `base`: €497 lifetime, CRM + Calendario + Fatturazione + 1 nicchia
- `pro`: €897 lifetime, Base + Sara AI + VoIP + WhatsApp + Loyalty
