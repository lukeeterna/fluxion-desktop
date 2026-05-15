# S242 — FLUXION Resume Prompt

**Generato**: 2026-05-15 fine S241
**Status S241**: VERDE (P0 done + P2 audit done, blocker outreach identificati)
**Repo**: `/Volumes/MontereyT7/FLUXION` master
**Last commit**: `be607d3 chore(S241-P0): cleanup canonical refs to non-existent €297 BASE tier`

## S241 Outcome (cosa è successo)

1. **P0 €297 cleanup ✅** (commit `be607d3`): rimossi riferimenti tier €297 BASE inesistente da PRD, helpdesk wiki, Video.tsx marketing. Allineamento 2-tier €497/€897 (Pro/Enterprise). Guardrail PLAYBOOK e lint mantenuti.
2. **P2 audit WA pipeline ✅** (no code change, report cache): subagent backend-architect ha auditato `whatsapp-service.cjs` (1104L) + `whatsapp.rs` (756L) + `whatsapp.py` (1254L) + `loyalty.rs`. Report: `.claude/cache/agents/s241/wa-pipeline-audit-P2.md` (425 righe).
3. **Plan S242 produzione**: P5 outreach 100 clienti BLOCCATO da 4 finding P0 della pipeline WA.

## P2 Audit Findings — 4 P0 blocker outreach

- **P0-A** Queue outbound `message_queue.json` SENZA CONSUMER. Loyalty/marketing UI dichiara "inviato" ma messaggi NON partono mai. UI bugiarda.
- **P0-B** Read-modify-write su `message_queue.json` senza lock (Rust + Node). Race condition → duplicate sends al primo drain reale.
- **P0-C** `voice-agent/src/whatsapp.py:559` fa `subprocess.run(['node','whatsapp-service.cjs','send',...])` che instanzia secondo Client `whatsapp-web.js` con LocalAuth condivisa = session steal certo (issue whatsapp-web.js#2856) + ban risk concurrent sessions.
- **P0-D** Zero idempotency check end-to-end. Double-click UI "Invia campagna" → 100 clienti ricevono 2x → ban WA + danno brand.

## P1 Pre-launch

- **P1-A** Retry/backoff assenti, errori swallowed (silent miss 2-5 su 100).
- **P1-B** `responseCounters` rate limiter in-memory perso al restart.
- **P1-C** Doppia scrittura `pending_questions.jsonl` con stesso schema id Python+Node.

## Plan S242 — WA Outbox SQLite (P0 blocker)

**Goal**: pipeline WA production-ready PRIMA di P5 outreach 100 clienti. Effort stimato 9-11h (≈2 sessioni dedicate).

**Strategia singola** (no liste): SQLite outbox come single source of truth, idempotency_key sha256(phone+template+content+bucket_5min), drainer in-process nel daemon Node, eliminare `subprocess.run('node send')` da voice-agent (path B), unificare tutto sotto client whatsapp-web.js singleton.

**File da toccare**:
- `src-tauri/migrations/0042_whatsapp_outbox.sql` (NUOVO) — schema outbox
- `src-tauri/src/commands/whatsapp.rs:249` — rewrite `queue_whatsapp_message` con SQLite + idempotency
- `src-tauri/src/commands/loyalty.rs:1001-1015, 1163-1201` — rimuovi `queue_whatsapp_message_internal` file-based
- `scripts/whatsapp-service.cjs` — aggiungi `drainOutbox(client)` con claim atomico SQLite + retry esponenziale
- `voice-agent/src/whatsapp.py:559-630` — rewrite `send_message` per scrivere su outbox (no più subprocess Node)
- `src-tauri/src/lib.rs` — migration block 0042

**Pre-build verifiche**:
- `cargo add sha2 uuid --features uuid/v7` (verifica già presenti in `Cargo.toml`)
- `npm ls better-sqlite3` daemon Node
- Env var `FLUXION_DB_PATH` propagation Tauri → Python sidecar

**E2E test obbligatorio**:
1. 100 messaggi sequenziali su numero test founder (NON 3314928901 reale)
2. `SELECT COUNT(*) FROM whatsapp_outbox WHERE status='sent'` = 100
3. Double-click smoke: invocare `queue_whatsapp_message` 5x con stesso payload in 30s → 1 sola row `status='sent'`
4. Restart drainer mid-batch: nessun messaggio perso, nessun duplicate

**Build**: solo iMac via SSH `ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && cargo build --release"`.

## Priorità S242 — start qui

**Primo task S242**: leggere `.claude/cache/agents/s241/wa-pipeline-audit-P2.md` integrale + decidere se procedere fix P0 outbox OR rispondere prima a Open Q founder #3 (tariffa Ehiweb €/mese per wizard onboarding P1).

**Raccomandazione singola CTO**: procedere fix P0 outbox WA in S242 — è blocker hard per P5 outreach, mentre wizard onboarding P1 dipende da risposta esterna Ehiweb (non actionable senza founder action).

## Vincoli mantenuti

- Zero-cost (#5): SQLite WAL già attivo, `better-sqlite3` peer dep da verificare, no nuovi servizi paid.
- Italiano per founder, tecnica in EN.
- D-01 VOS DECISIONS.md: 2-tier €497/€897, FLUXION = gestionale + Voice Agent Sara, mai "tool video marketing".
- Context budget: monitor `/context`, sopra 50% NO edit schema/migration, sopra 60% chiudi.

## Open Q founder pendenti (S241 non risolte, da chiedere S242 start)

1. **Tariffa Ehiweb €/mese cliente** (D-03 Open Q #3): founder deve chiedere a Ehiweb. Necessaria per UI pricing onesto wizard P1.
2. **Decisione fix P0 WA**: founder OK con 2 sessioni dedicate per outbox refactor PRIMA di P5 outreach? Alternativa = outreach manuale (singolo invio human-in-the-loop) per primi 10-20 clienti finché pipeline non è fixata.

## Stato repo

- MacBook: `be607d3` master synced.
- iMac: TODO sync (`git pull` post-commit S241 chiusura).
- Pipeline iMac voice-agent: DOWN (chiusa S240).
- WA daemon: NOT running.
