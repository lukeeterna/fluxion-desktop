# T-SARA-TRUNK / CALL-1 — Report

## CALL-1 (2026-07-04 18:17:18 -> 18:17:37 UTC, ~18.5s) = C.3 CASO SPORCO (non verdetto)
Founder ha chiamato 0972536918 dal cellulare, Sara ha risposto ("officina demo fluxion" = verticale
default FSM auto), founder ha RIAGGANCIATO SUBITO senza pronunciare un turno di parlato.

### Fatti certi (log grezzi in postcall_delta.txt / postcall_python_markers.txt):
- INVITE via TRUNK: `RX 958 bytes INVITE from UDP 79.98.45.133:5060` (EHIWEB) -> `sip:0972536918@151.45.159.109:5080`.
  Caller 3281536308. = path S244 reale (inbound autenticato, IP pubblico), NON direct-INVITE.
- Bridge WIRED bidirezionale sul clock thread: Added port 1 (caller) + port 2 (sara_bridge);
  Port1->Port2 E Port2->Port1 transmitting. RTP fluito (jitter buffer normal frames, ~18s).
- Sara PID 54563 invariato, NO SIGABRT (NDEBUG regge). Post-call rtp_active:false, reg 200.
- Founder ha SENTITO il saluto -> TX audio Sara arrivato al telefono via PSTN.

### Fatti che negano un verdetto pulito:
- /api/metrics/latency count=0, NESSUNA riga "Speech turn detected RMS=". Riaggancio immediato
  senza parlato -> VAD non ha chiuso turno -> count=0 CONFUSO (no parlato != RX pump morta).
- Firma crash PRESENTE sul trunk: os_core_unix.c clock "possibly re-registering existing thread"
  + ERROR lock.c sara_audio_c "Assert failed: glock->owner == pj_thread_this()" (18:17:18.670).
  IDENTICA a S351/S354/T-SARA-WIRING -> la patologia clock-thread NON e' specifica del direct-INVITE.
- ANOMALIA (flaggata, NON riaperta - vincolo #1c): ZERO righe Python app-log di Sara nel delta
  (ne' onCallMediaState, ne' _send_greeting, ne' Audio processing loop) benche' il saluto sia stato
  udito. Il layer Python di turn-processing non ha loggato nulla per questa call.

### Verdetto CALL-1: C.3 (call agganciata + Sara risponde, ma senza turno di parlato -> non falsificabile).
Serve UNA re-do: founder parla ~20s (frase di prenotazione reale) SENZA riagganciare finche' Sara non replica.
Solo allora count>0/RMS>0 (VERDE) oppure count=0 con parlato reale (ROSSO -> S244 cade, Asterisk ARI a founder).
=== REARM offsets 2026-07-04T16:24:03Z ===
fd1  5009717
fd2  4591616
latency count now: {"p50_ms": 0, "p95_ms": 0, "p99_ms": 0, "count": 0, "hours": 24}