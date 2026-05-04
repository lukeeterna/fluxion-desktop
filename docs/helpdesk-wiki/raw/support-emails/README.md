# raw/support-emails/

**Directory gitignored** — contiene email support con PII redacted.

## PII redaction OBBLIGATORIA prima di drop file qui

Sostituire prima del salvataggio:
- Email cliente reali → `[CLIENTE_X@example.com]`
- Numeri telefono italiani (`+39 ...`, `3xx xxx xxxx`) → `[PHONE_X]`
- Nomi/cognomi cliente → `[CLIENTE_X]` o `[OPERATORE_Y]`
- P.IVA/CF → `[PIVA_X]` / `[CF_X]`
- Indirizzi → `[INDIRIZZO_X]`

## Workflow founder

1. Email rilevante per knowledge base → copy raw text
2. Redact PII manualmente con find/replace
3. Salva in `raw/support-emails/YYYY-MM-DD-<topic-slug>.md` con frontmatter:
   ```yaml
   ---
   date: 2026-05-04
   topic: <slug>
   redaction_verified: true
   ---
   ```
4. Lancia ingest: `/ingest docs/helpdesk-wiki/raw/support-emails/<file>.md`

## Lint check

Lint workflow (sez. 6.7 HELPDESK.md) blocca commit se trova pattern PII non redacted in qualsiasi file `wiki/`. Le file in `raw/support-emails/` sono comunque gitignored come safety net.
