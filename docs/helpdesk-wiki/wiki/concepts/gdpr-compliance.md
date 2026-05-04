---
title: "GDPR Compliance"
type: concept
slug: gdpr-compliance
sources_consumed: []
last_ingest: 2026-05-04
status: draft
related:
  - license-key
  - network-firewall
  - sara-voice-agent
  - verticals-coverage
verticals: [all]
---

# GDPR Compliance

> Posizione GDPR FLUXION per PMI italiane. Architettura **offline-first SQLite locale** = dati cliente NON in transit cloud → riduzione enormemente superficie compliance vs SaaS competitor.

## Tesi corrente

FLUXION adotta **privacy-by-architecture** invece di privacy-by-policy. Vincoli operativi:

1. **Dati cliente in SQLite locale** crittografato AES-256-GCM. Mai in transit cloud.
2. **License key Ed25519 offline-verifiable** ([[license-key]]) — no phone-home, no tracking installazioni
3. **Sentry telemetry region DE** ([[network-firewall]]) — error stack only, NO PII (configurato esplicitamente per stay <5k errors/mese free tier GDPR-safe)
4. **Sara voice** ([[sara-voice-agent]]) — STT locale Whisper.cpp prima opzione, Groq fallback (US) OPTIONAL, audio buffer mai persistente
5. **WhatsApp Business** — meta-side compliance loro responsabilità (FLUXION solo client API)

## Perché importa per il cliente PMI

### Verticali ad alto rischio compliance

- **`medico`** — dati Art.9 GDPR (sensibili sanitari). Schede odontoiatrica/fisio includono anamnesi, allergie. Cliente PMI medico-legale ESPONE penalmente se SaaS competitor breach. FLUXION SQLite locale = dati restano in studio.
- **`beauty/estetista`** — fototipo Fitzpatrick + allergie cosmetiche = dati salute "minor"
- **`pet/veterinario`** — dati clinici animali (no GDPR strict ma good practice)
- **`professionale/avvocato`** — segreto professionale Art. 200 c.p.p. → SQLite locale è REQUIREMENT, non nice-to-have

### Verticali a basso rischio
- `hair`, `auto`, `wellness`, `formazione`, `professionale` (no avvocato) — dati comuni, SaaS sarebbe accettabile ma FLUXION mantiene vantaggio "no vendor lock-in".

## Come FLUXION lo realizza

### Data residency
- **Storage**: SQLite locale path utente OS-standard (`%APPDATA%\fluxion\` Win, `~/Library/Application Support/fluxion/` macOS)
- **Encryption at rest**: AES-256-GCM su file DB
- **Backup**: founder controlla (no auto-backup cloud built-in)
- **Export**: dump SQLite + CSV export utenti/appuntamenti (gap: format GDPR-compliant strutturato Art.20 portability, S185-bis target)

### Network outbound (whitelisted only)
Vedi [[network-firewall]] § "FQDN whitelist" per matrice completa. Highlights privacy:
- **Nessun tracker** (no GA, no Pixel, no Hotjar)
- **Nessun cloud per dati cliente** (PII mai out)
- **Sentry region DE** (`o*.ingest.de.sentry.io`) — error telemetry no PII
- **FLUXION Proxy CF Worker stateless** — LLM routing, no PII storage

### Sara voice + GDPR
- Audio buffer **locale** RAM only, mai persistente disco
- Transcript via Whisper.cpp **locale** (default) — no Groq se network blocked
- Groq STT fallback (US datacenter) — opt-in implicito, raccomandato disabilitare per `medico`
- LLM via FLUXION Proxy → Groq/Cerebras (US) — testo prompt include nome cliente, **TODO**: anonymization layer pre-LLM (S185-bis)

### License + identity
- Hardware fingerprint = pseudonymization (no nome+cognome cliente, solo CPU+RAM+OS hash)
- Ed25519 verify locale = no phone-home
- Email license da `onboarding@resend.dev` (Resend free tier, GDPR-compliant DPA)

## Tech debt aperti / Domande aperte

### Critical (S185-bis priority)
- **DPIA template per cliente PMI** — Data Protection Impact Assessment. Founder fornisce template generico per cliente verticali `medico`/`avvocato`?
- **Privacy policy ufficiale** — landing page non ha privacy policy linkata. Risk: GDPR Art.13 violation FLUXION-side
- **Data retention policy** — durata dati in DB locale = 0 policy (cliente decide). Gap docs.
- **Right-to-deletion (Art.17)** — workflow tecnico: cancellare cliente da CRM = soft delete vs hard delete. TODO spec.
- **Data portability (Art.20)** — CSV export esiste, format strutturato GDPR-compliant gap.
- **Sara LLM PII anonymization** — prompt include nome cliente, S185-bis design layer pre-LLM

### Important (deferred)
- **Audit trail** (mentioned `_bmad/sessions/2026-01-29-week3-sprint-quality.md` TODO) — log accessi dati sensibili
- **Consent logging** — checkbox cliente "trattamento dati per appuntamento + WhatsApp" + storage consent record
- **AES key rotation** — chiave DB statica vs rotation periodica
- **Backup encryption** — se cliente abilita auto-backup futuro, encryption end-to-end

### Out-of-scope FLUXION-side
- Conformità **WhatsApp Business API** = Meta lato (utente PMI accetta TOS WA)
- Conformità **Stripe checkout** = Stripe lato (PCI DSS Level 1)
- Conformità **Groq US datacenter** = solo via opt-in fallback STT, default Whisper.cpp locale

## Sources
- `_bmad/sessions/2026-01-29-week3-sprint-quality.md` § GDPR audit trail TODO
- `.claude/rules/architecture-distribution.md` — Sentry DE, no PII
- `MEMORY.md` § "SENTRY — ZERO COST GUARDRAIL" — region DE config
- `MEMORY.md` § "DOMINI — VINCOLO PERMANENTE" — Resend free tier sender
- (TODO ingest in S185-bis: GDPR-AUDIT-TRAIL-PLAN.md se esiste, DPIA template draft)
