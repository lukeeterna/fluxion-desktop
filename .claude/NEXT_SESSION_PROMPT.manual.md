# CARRY S352 — GATE SARA LAYER 2: BLOCCO STRUTTURALE pjsua2 (NON budget) — DECISIONE FOUNDER PENDENTE

> S351: loop ~15 sessioni ROTTO. Test audio reale ESEGUITO con output reale (non più HARD_STOP da budget falso).
> Esito: il gate resta aperto per una limitazione STRUTTURALE di pjsua2, non di budget. Serve decisione founder sul fork architetturale.

## Cosa è stato fatto S351 (output reale, NON re-investigare)
- SIP confermato VERDE: `ssh imac "curl -s http://127.0.0.1:3002/api/voice/voip/status"` → `registered:true, reg_status:200` (VivaVox 0972536918@sip.vivavox.it).
- Delega a `voice-engineer` (foreground, 22 tool-use) → test chiamata audio ESEGUITO:
  - **Path LAN** (`192.168.1.2:5080`): Sara risponde `200`, SDP negoziato OK → **SIGABRT prima del CONFIRMED**. Assert `grp_lock_release` su `libHandleEvents`/`_pjsua2_thread`, trigger `conference.c onCallMediaS "Add port sara_bridge"`. Crash report `Python-2026-06-08-094137.ips`. **Identico a S336-S338**. Sara DOWN → riavviata.
  - **Path provider** (`sip.vivavox.it`): INVITE anonimo → **403 Forbidden** dal softswitch. Mai arrivato a Sara.
- **Ipotesi anti-crash FALSIFICATA (4ª volta, REGOLA #1c: NO 5° ciclo)**: la race è interna al dispatch dei callback media C-side di pjsua2, INDIPENDENTE dal transport. Loopback→LAN non cambia il timing.

## Perché S244 funzionava
A S244 la chiamata era **inbound autenticato dal provider** (timing rete reale). NON riproducibile in autonomia oggi: (a) softswitch respinge INVITE anonimo dell'harness (403), (b) solo 1 account trial.

## DECISIONE FOUNDER (fork) — raccomandazione CTO
**Raccomandato (REGOLA #1b, fatto più economico+falsificabile prima della rework grande)**:
> Richiedere a EHIWEB un **2° account SIP autenticato** (VivaVox sub-account o 2° trial, €0). Con quello il CTO esegue il test **provider-inbound reale** in autonomia (rispetta REGOLA #23, niente telefono) — unica config storicamente non-crashante (S244). Esperimento falsificabile in 1 sessione.

**Fallback se anche provider-inbound crasha** → rework **Asterisk ARI**: Asterisk gestisce SIP+media (battle-tested, no race), Sara = solo brain STT→NLU→TTS. Più lavoro, ma gold-standard enterprise (guardrail #2), elimina la race alla radice.

## DONE-CONDITION gate Sara Layer 2 (REGOLA #21)
Sara risponde PERTINENTE al golden-path booking via AUDIO REALE (cattura+trascrizione) senza crash. **BLOCKED-ON**: 2° credenziale SIP (azione esterna Luke→EHIWEB) OPPURE decisione rework Asterisk.

## Stato lasciato S351
Pipeline Sara UP (riavviata), SIP `reg_status:200` verde, `.env` intatto, harness invariato. WAV `/tmp/book.wav` (PCM16 8kHz mono) generato. Memoria agent voice-engineer aggiornata.

## Carry residui (dopo decisione gate Sara)
- **R2**: CI `release-full.yml` ROTTO (5 run failure 2026-05-04, step Build Tauri App macos-arm). Prima azione: `gh run view 25328286560 --log-failed`.
- **R3**: E-3 sk_live (Stripe live key).
