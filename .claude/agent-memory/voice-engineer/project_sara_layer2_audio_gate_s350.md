---
name: Sara Layer 2 audio gate — anti-crash hypothesis FALSIFIED (LAN + provider, 2026-06-08)
description: reg verde su VivaVox NON sblocca il test audio — LAN INVITE crasha identico al loopback (grp_lock_release), provider INVITE anonimo dà 403. Serve fix strutturale o 2° account VivaVox.
type: project
---

Sara Layer 2 (audio reale via SIP) è il gate vendita REGOLA #21 — ancora APERTO al 2026-06-08 dopo run reale.

**SIP REGISTRATO VERDE confermato (2026-06-08)**: `curl 127.0.0.1:3002/api/voice/voip/status` → `registered:true, reg_status:200`, VivaVox/EHIWEB, username 0972536918, sip.vivavox.it, engine pjsua2. Pre-req S349 tenuto.

**ESPERIMENTO 1 — INVITE diretto via IP LAN (192.168.1.2:5080, NON loopback 127.0.0.1) — CRASH IDENTICO, ipotesi FALSIFICATA (4° ciclo, STOP REGOLA #1c)**
- Harness `scripts/sara_audio_harness.py` invariato, target `--sara-ip 192.168.1.2`. Sara risponde `100 Trying` → `Answering call 0: code=200` → SDP negoziato Success → RTP/ICE setup completo.
- Crash su `conference.c onCallMediaS "Add port 2 (sara_bridge) queued"` → `libHandleEvents` → SIGABRT con assert `grp_lock_release` (estratto da crash report `~/Library/Logs/DiagnosticReports/Python-2026-06-08-094137.ips`). Sara DOWN (port 3002 morto) post-run.
- **VERDETTO**: cambiare transport da `127.0.0.1` a IP LAN `192.168.1.2` NON cambia il timing della race. La race è INTERNA al dispatch dei callback media C-side (`onCallMediaState` gira su thread `onCallMediaS`, op-queue processata su `_pjsua2_thread` in `libHandleEvents` → group-lock owner mismatch). È indipendente dal transport di rete. Conferma per la 4ª volta la diagnosi strutturale S336/S337/S338 (non pjsip-version, non mainThreadOnly-config, non transport-dependent). NON Python-fixabile.

**ESPERIMENTO 2 — INVITE via softswitch provider VivaVox (sip:0972536918@sip.vivavox.it:5060) — 403 FORBIDDEN**
- Harness anonimo (non registrato) verso il proxy `79.98.45.133:5060`: `100 Trying` → `403 Forbidden`. Il softswitch MOR rifiuta chiamate anonime non autenticate verso il numero (anti-toll-fraud). L'INVITE NON raggiunge mai Sara → Sara NON crasha (resta UP, reg verde).
- **VERDETTO**: l'ipotesi "via provider il timing diverso evita la race (come S244)" NON è testabile con questo harness, perché il provider richiede un SECONDO account VivaVox AUTENTICATO che chiami il numero. L'harness in chiaro/anonimo è respinto a monte. Non esiste un 2° account (S349 ha riattivato un solo trial single-account).

**ESPERIMENTO 3 — fix thread-confinement `libIsThreadRegistered` guard (S352) — CRASH IDENTICO, ipotesi FALSIFICATA (5°? NO: nuovo asse, ma esito strutturale confermato)**
- Ipotesi S352: i fix S237-S244 chiamavano `libRegisterThread` incondizionato anche sui thread pjmedia GIÀ registrati (es. `onCallMediaS`), sovrascrivendo il `pj_thread_desc` in TLS → owner del group-lock corrotto. Fix: helper `_register_thread_if_needed()` che registra SOLO se `ep.libIsThreadRegistered()` è False. Applicato a tutti e 7 i siti `libRegisterThread` (backup `voip_pjsua2.py.bak-PRE-S352-20260608-102756`, deployato iMac, SHA match, AST OK, pipeline riavviata, reg_status:200 verde).
- Run harness LAN diretto (`--sara-ip 127.0.0.1 --wav /tmp/book.wav`): Sara `Answering 200` → SDP OK → RTP `Remote RTP switched to 192.168.1.2:4023` → `conference.c Added port 1/2 (harness_bridge) transmitting` → **`os_core_unix.c "possibly re-registering existing thread"` ANCORA PRESENTE (grep count=1)** → SIGABRT `Assertion failed (glock->owner == pj_thread_this()), grp_lock_unset_owner_thread, lock.c:279`. HARNESS_EXIT=134 (128+6=SIGABRT). Nuovo crash report `Python-2026-06-08-103035.ips`.
- **VERDETTO**: il guard `libIsThreadRegistered()` NON elimina il warning "re-registering" né il crash. Il thread che corrompe l'owner del group-lock è registrato/toccato C-side da pjmedia in un punto che il guard Python non intercetta (la registrazione avviene dentro il dispatch SWIG-director del media callback, fuori dai 7 siti patchati). Conferma definitiva: la race è strutturale nel conference-bridge pjsua2, NON sanabile dal lato Python con thread-registration guards (5 fix falliti: S237-S244 aggressivi, S352 conservativo). Solo path = (1) fix architetturale o (2) provider-inbound autenticato.

**FATTO TERMINALE ESTERNO per sbloccare il gate (BLOCKED-ON, scegliere UNO):**
1. **Fix strutturale pjsua2** (architetturale, non Python-patch): far avvenire TUTTI i conference port-add sul thread di `libHandleEvents`, OPPURE rimpiazzare il conference-bridge pjsua2 (es. Asterisk ARI come SIP/media layer, Sara solo brain — opzione N5 dossier S337). Decisione main/founder, non quick fix.
2. **2° account VivaVox/EHIWEB autenticato** (azione esterna Luke→EHIWEB): un secondo SIP user che chiami 0972536918 via softswitch = vero path provider, replica le condizioni S244 dove le chiamate provider NON crashavano. Questo È il vero esperimento che valida l'ipotesi anti-crash, ma richiede credenziali esterne.

**How to apply**: NON ritentare un 5° ciclo loopback/LAN (radice falsificata 4x, REGOLA #1c). Il gate Layer 2 resta BLOCKED-ON su (1) decisione architetturale o (2) 2° account provider. Stato lasciato: Sara UP, SIP reg:200 verde, `.env` intatto, harness invariato. WAV test `/tmp/book.wav` (PCM16 8kHz mono) generato. Crash reports: `Python-2026-06-08-094137.ips` (Sara, grp_lock_release), `094212/094355.ips` (teardown harness, line 407 = ep.libDestroy, non Sara).
