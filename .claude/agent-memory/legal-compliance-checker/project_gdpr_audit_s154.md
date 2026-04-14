---
name: GDPR Audit S154 Results
description: Full GDPR compliance audit of FLUXION desktop app — findings, gaps, and remediation roadmap
type: project
---

Full audit completed 2026-04-14. Report at `.claude/cache/agents/audit-s154/GDPR-AUDIT.md`.

## COMPLIANT (no action needed)
- PII inventory: all fields documented across 15+ tables
- Consent per-client: ClienteForm.tsx + MediaConsentModal.tsx properly collect and store consent
- Audio temp files: STT engines delete WAV files in `finally` blocks
- Retention policy: defined in `gdpr_settings` table with correct durations (7yr personal, 10yr financial)

## NON-COMPLIANT (must fix)
- **Encryption at rest**: `encryption.rs` (AES-256-GCM) exists but `encrypt_field()` is NEVER CALLED in clienti write path — PII stored as plaintext
- **Right to Erasure**: `delete_cliente` is soft-delete only (`deleted_at`), PII remains in DB — no hard-delete or field anonymization
- **Privacy Policy page**: No `landing/privacy.html` exists, footer has no privacy link — required before any purchase
- **Cookie consent**: Google Fonts CDN transmits visitor IP to Google without consent (Garante ruling 2022), no cookie banner
- **CF Worker DPA**: No documented DPA with Groq or Cerebras sub-processors; PII (client names) may transit to US servers
- **Caller notification**: Sara greeting has no GDPR disclosure ("questa chiamata è gestita da AI...")

## PARTIAL (improve post-launch)
- Data export: clienti + appuntamenti CSV exists; health records (schede_mediche etc.) NOT exportable
- Retention execution: policies defined but no scheduler call found to run anonymization automatically
- First-launch consent: no setup wizard screen for operator to accept data controller role

## Art. 9 Special Category Data
Tables: `schede_mediche`, `schede_fisioterapia`, `schede_odontoiatriche`, `schede_estetica`
Legal basis required: Art. 9(2)(h) medical purpose + explicit consent Art. 9(2)(a)

**Why:** Critical for launch — selling to medical/dental/physio verticals without Art. 9 basis documentation = direct GDPR violation.
**How to apply:** Any work on medical verticals must verify Art. 9 consent collection is in place.

## Remediation Priority
P1 (block launch): Privacy Policy page + self-host Google Fonts
P2 (before first customer): erasure command + activate encryption + Groq DPA + PII strip in NLU + caller notice
P3 (30 days post-launch): scheduler for anonymization, first-launch consent wizard, health data export
