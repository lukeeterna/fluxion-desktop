# FLUXION — Roadmap produzione
Scadenza: 27/08/2026. Cio' che non e' sul percorso critico verso il primo cliente pagante va in coda.

## Stato al 31/07/2026
- Gestionale: catena pagamento E2E validata con 1 EUR reale. Non blocca.
- Sara: B3 PROMOSSA. :3002 UP con go engine, SIP registered, trunk EHIWEB. La linea e' viva.
- Scorecard B3: M1 disclosure VERDE statico. M2 barge-in VERDE. M5 congedo VERDE live. M3 confirm-gated da FIX-C. Manca la sola prova RUNTIME di E6-exit e reprompt.
- Prezzo: 497 EUR base one-time, upgrade Sara 897 EUR one-time. Mai canone. On-premise con account EHIWEB+Groq del cliente. Windows requisito duro.

## Infrastruttura verificata — non riscoprirla
- Avvio: docs/judge/RUNBOOK-AVVIO.md. Selettore motore = env VOICE_ENGINE, main.py:1326. b3_open.sh pretende un processo gia' vivo: si bypassa.
- Endpoint: /api/voice/process (main.py:384), /api/voice/reset (main.py:386), /api/voice/process-with-vad (vad_http_handler.py:131), /api/voice/set-vertical.
- Taratura: reprompt_timer 22.0s (voip_goengine.py:87), E6_strike_threshold 3, VAD Silero, TTS EdgeTTS it-IT-IsabellaNeural.
- Fix in HEAD: FIX-A escalation_manager.py:97 (congedo onesto, senza "collega"), FIX-C booking_state_machine.py:756 (conferma nome).
- Asset test: voice-agent/tests/e2e/test_sara_stress_per_verticale.py, seed_stress_fixtures.py, .claude/SARA_STRESS_TEST_PATTERNS.md. Ricerca di dominio fatta per dentista, estetica, fisioterapia, officina, palestra, parrucchiere.

## GIA' FALSIFICATO — non ritentare

→ Lista completa e fonte in `docs/judge/FALSIFICATO.md` (append-only, fonte unica).
Non duplicare qui. Consultare FALSIFICATO.md per enunciato, metodo di falsificazione ed evidenza.

## Unita' residue, in ordine di dipendenza
U1 STRESS-VERTICALI — certifica il CONTENUTO per verticale (KB, argomentazioni, risposte, catalogo, booking, FAQ, guardrail) e misura la latenza per verticale. Corsia MACCHINA.
U2 CERT-21 — certifica il COMPORTAMENTO del motore con UNA chiamata vocale: reprompt su silenzio, tre strike, E6, congedo onesto, chiusura da Sara, latenza percepita. Vive nella FSM, non nella KB: vale per tutti i verticali. Owner: FOUNDER.
U3 LATENZA — misurare e ridurre. Noto: timeout STT 5s, TTS 586-2063ms, doppi prefissi empatici, engine sano 251-560ms. Corsia MACCHINA. BLOCCANTE.
U4 WINPORT — Sara su Windows. Mai tentato. Requisito duro. Corsia MACCHINA. BLOCCANTE. Rischio piu' grande verso il 27/08.
U5 PRE-PUSH AUDIT — dopo la chiusura di ARGOS SCRUB+PUSH v1.1.
U6 GIT-REALIGN — bonifica history (repo pubblico, incidente G2 wa_session), untrack fluxion.db*, gc sicuro. Founder-gated.
U7 WIZARD + KBPACK — onboarding on-premise, attivazione del verticale corretto per licenza con la KB di settore, account EHIWEB+Groq del cliente.
U8 BRAINSYNC — telefono prima del riepilogo, Keychain headless.
U9 PRIMO CLIENTE PAGANTE.

## Coda, non bloccante
Prefissi empatici, filtro plausibilita' nomi, mapping servizi via slot-log, fuori-orario mid-flow, 10 FAQ irrisolte, tavolo STT-digits. Robustezza go engine: accettare piu' di una m=audio. Gap FSM 4 verticali su 8. MEMORY.md oltre il limite loader. Crash-loop Timer_B. R-10 dati sanitari blocca il medical. Drift tools/VectCutAPI.

## Corsie
- CORSIA REPO (Claude Code web, VM cloud): documenti, scrittura codice, refactor, audit statico. Nessun accesso a :3002, rig, trunk, DB, log locali.
- CORSIA MACCHINA (CC locale su iMac): tutto cio' che tocca runtime, deploy, chiamate, Windows.
- Mai le due corsie sugli stessi file in contemporanea. Un solo blocco attivo alla volta.
- Vietato che lo stesso modello scriva il codice e lo giudichi. Il giudice legge solo il diff.
