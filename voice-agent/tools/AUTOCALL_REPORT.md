# AUTOCALL REPORT — T-SARA-AUTOCALL STEP 2-5 (PARZIALE)

> Runner `tools/sara_autocall.py` (direct-INVITE via `scripts/sara_audio_harness.py`, NO trunk EHIWEB).
> Sessione 2026-07-03. Chiuso a context 60% (vincolo #7) DOPO S1. **Resume da S2.**

## Pre-flight (VERDE)
- `:3002/health` 200; SIP **registered reg_status:200** (user `0972536918`, sip.vivavox.it, pjsua2).
- `:3001` bridge health ok (pid 57494).
- **Sara PID baseline = 54563** (riferimento no-crash).
- Runner sincronizzato su iMac (commit `6e7fb8c` pull OK). Interprete: CommandLineTools Py3.9.6, `pjsua2` importabile.
- Baseline voice bookings = **3** (atteso). Clienti = 15 (PII cifrata).

## Tabella scenari

| SCENARIO | completato | appuntamento DB (id) | crash | anomalie dialogo | durata | audio file |
|----------|-----------|----------------------|-------|------------------|--------|------------|
| S1 SALONE cliente NUOVO (Gianfranco Sgueglia) | connesso NO booking | nessuno (voice=3 invariato) | NO (PID 54563 pre==post) | `sara_heard:false` su 2/2 turni → fallback fisso 14s; call dropped before 'chiusura'; latency count=0 | 38.87s | `/tmp/autocall/S1_call.wav` (512044 B) |
| S2 | DA ESEGUIRE | — | — | — | — | — |
| S3 | DA ESEGUIRE | — | — | — | — | — |
| S4 | DA ESEGUIRE | — | — | — | — | — |
| S5 | DA ESEGUIRE | — | — | — | — | — |
| OVERLAP ×2 | DA ESEGUIRE | — | — | — | — | — |

## Latency `/api/metrics/latency`
- Pre S1: `p50=0 p95=0 p99=0 count=0`.
- Post S1: `p50=0 p95=0 p99=0 count=0` → **Sara non ha processato NESSUN turno** attraverso il path direct-INVITE.

## Ramo Keychain S1 (caveat GDPR)
- Cliente nuovo "Gianfranco Sgueglia" **NON creato** nel DB clienti (count 15 invariato, nessun `cli-` nuovo). Il ramo PII/Keychain **non è stato esercitato** perché Sara non ha processato il turno di apertura. Caveat GDPR resta **NON verificato**.

## Trascrizioni STT vs copione
- Copione S1 apertura: *"Buongiorno, non sono mai venuto da voi, mi chiamo Gianfranco Sgueglia, vorrei prenotare un taglio giovedì pomeriggio"*.
- STT lato Sara: **assente** (latency count=0, nessun turn log di comprensione). Il WAV catturato `S1_call.wav` è finestra fissa 512000 B PCM (contenuto Sara non confermato — probabile silenzio/no-RTP-decodato).

## DISCORDANZA @ S1 — smoke green ≠ turno conversazionale
- **PREMESSA** (da HANDOFF smoke): direct-INVITE regge → stack pronto per stress multi-turn con booking.
- **FATTO DISCO**: il call si CONNETTE e Sara **sopravvive (no SIGABRT, NDEBUG regge)**, ma la pipeline conversazionale **non viene esercitata**: `latency count=0`, `sara_heard=false`, zero booking, zero cliente. Il de-risk provato dallo smoke = "lo stack non crasha su 1 INVITE", NON "Sara conversa e prenota via questo path".
- **CORREZIONE**: prima di girare S2-S5 serve chiudere il gap RTP: (a) Sara riceve RTP decodabile dall'harness? (codec/ptime negoziati); (b) la silence-detection `audioop.rms ≥0.8s` dell'harness misura l'RTP di Sara o solo il proprio TX? `sara_heard:false` + `count=0` puntano a **audio non fluito Sara→harness E/O harness→Sara**. Root cause candidata: il direct-INVITE IP-to-IP negozia media ma il flusso RTP audio effettivo verso la STT di Sara non parte (a differenza dell'inbound autenticato provider di S244).

## VERDETTO PARZIALE
- **5 SCENARI: 1 avviato (S1), 0 completati con booking, 0 crash.**
- **PRONTO PER CHIAMATA FOUNDER (trunk + giudizio): NO** — prima chiudere il gap RTP/turn-taking (Sara non processa turni sul path auto). Lo stack sopravvive ma non dimostra ancora conversazione+booking end-to-end in autonomia.
