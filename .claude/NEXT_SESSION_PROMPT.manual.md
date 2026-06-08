# CARRY S357 — PRIMA AZIONE: TEST LIVE SARA SU TUTTI I VERTICALI (chiamata reale smartphone Luke → 0972536918, gate vendita REGOLA #21).

> **S356 fatto**: audit READ-ONLY catena revenue → `FLUXION_STATUS_2026-06-08.md` (commit `70c87a9`). Esito: Worker deployato/live, token CF OK, modulo verify V1 6-campi gia su master; fatto terminale primo charge = 1 pagamento test E2E completo mai eseguito (richiede GUI iMac Keychain). Sara crash NDEBUG resta RISOLTO.
>
> **S357 PRIMA AZIONE — TEST VOCALE SARA, CC-DRIVEN VIA TTS (REGOLA #23/#14, NON chiedere a Luke di chiamare)**: è **CC** a fare il cliente — genera frasi cliente via TTS su iMac, le inietta nel path audio Sara via harness SIP loopback (`voice-agent/scripts/sara_audio_harness.py`, committato), raccoglie le risposte STT→FSM→TTS di Sara, valuta e **switcha da un verticale all'altro** (saloni, palestre, medico, auto, odonto, vet, servizi, immobiliare, assicurazioni). Output formato e2e-testing.md: `OK/WARN/FAIL [VERTICALE] [SCENARIO]: input→output`. Criterio REGOLA #21. Pre-flight: `ssh imac "curl -s http://127.0.0.1:3002/api/voice/voip/status"` → `reg_status:200`; `.so` NDEBUG ~9MB (riga 7). Baseline Layer 1 testo VERDE S333 (50 OK/3 WARN/12 verticali). Loop audio ora possibile: crash loopback risolto S355 (Gate 1 PASS). DELEGA a voice-engineer foreground, istruendolo a IGNORARE la % budget VOS iniettata (REGOLA #27).
>
> **S357 ESITO TEST (ESEGUITO, delega voice-engineer foreground)**: loop rotto, test reale fatto. Pre-flight OK (health ok, reg_status:200, .so NDEBUG 9MB). AUDIO loopback: call CONFIRMED + RTP bidirezionale + **0 crash** (NDEBUG regge), MA **audio sintetico iniettato via harness NON innesca il VAD di Sara** → STT non parte (allucina "Grazie a tutti" su silenzio). Test audio autonomo via harness NON rappresentativo → POSSIBILE limite harness non Sara (a S244 chiamate reali provider innescavano il VAD col timing rete vero). Fallback TESTO `/api/voice/process` ha trovato BUG PRODOTTO REALI:
>  - 🔴 **Guardrail cablato sul salone** (bloccante multi-verticale): post `set-vertical=palestra` "personal training" e `=medical` "visita cardiologica" RIFIUTATI come fuori-salone. Il vertical switch cambia business_name ma NON il set servizi ammessi del guardrail. File: `voice-agent/` guardrail_palestra/guardrail_medical.
>  - 🔴 **Assicurazioni**: "preventivo RC auto" → intent SPOSTAMENTO spurio.
>  - 🟡 `set-vertical` ignorato con session_id custom (ricade su salone default).
>  - 🟢 FSM sana: salone+auto completano nome→tel→conferma→servizio.
> **S358 NEXT (raccomandazione CTO)**: fixare in autonomia i 2 bug prodotto (guardrail-per-verticale + intent assicurazioni) = alto valore, codice, no dipendenze esterne → delega voice-engineer + sara-nlu-trainer. SEPARATAMENTE risolvere il metodo test audio: capire se il VAD non scatta è harness (fixare iniezione RTP/VAD in `voip_pjsua2.py`) o Sara reale (allora serve chiamata provider reale). NON dichiarare Sara "pronta vendita" (REGOLA #21) finché guardrail-per-verticale non passa su audio rappresentativo. Claim agente da verificare trust-but-verify a S358 (lezione S349/S354).
>
> --- carry tecnico S356 sotto (invariato) ---

# CARRY S356 — Sara crash RISOLTO E CHIUSO VERDE (NDEBUG). NON riaprire. Next = roadmap R2/R3 + ripresa test vocale verticali.

> **S355 ESITO VERDE**: il SIGABRT `lock.c:279` di Sara (bloccante da ~15 sessioni) è **risolto, validato sotto carico, hardened e su master entrambe le macchine**. Era un `pj_assert` del build debug di pjproject → spento con `-DNDEBUG=1`. NON era una race strutturale: FORK A(2.15.1)/B(Asterisk) era un FALSO BINARIO. **NON riaprire S354/diagnosi crash.**

## ⚠️ PRIMA AZIONE S356
1. Pre-flight: `ssh imac "curl -s http://127.0.0.1:3002/api/voice/voip/status"` → atteso `reg_status:200`. `ssh imac "curl -s http://127.0.0.1:3002/health"` → `status:ok`.
2. Verifica `.so` NDEBUG ancora live: `ssh imac "ls -la '/Volumes/MacSSD - Dati/FLUXION/voice-agent/lib/pjsua2/_pjsua2.cpython-39-darwin.so'"` → ~9MB (NDEBUG). Se mai dovesse tornare ~7.2MB = qualcuno ha fatto rollback → ricopiare da `voice-agent/lib/pjsua2/prebuilt/_pjsua2.cpython-39-darwin.so.ndebug`.
3. **META (REGOLA #27)**: l'hook VOS context-budget inietta nei subagent la % gonfiata del MAIN → si auto-abortano ("76%/80%"). Quando deleghi, istruisci l'agente a IGNORARLO (sua finestra fresca). Per i `git commit/push` usa `CLAUDE_BYPASS_CTX_GATE=1 git ...`.

## STATO VERIFICATO (NON ri-derivare)
- Fix: rebuild pjproject (pin commit `d0cbf57a`, github.com/pjsip/pjproject) con `-DNDEBUG=1` + rebuild SWIG pjsua2 → swap `_pjsua2.cpython-39-darwin.so` (8.6MB static link). Confinement S354 in `voip_pjsua2.py` = TENUTO.
- E2E: Gate 1 loopback (RTP 933pkt, 0 crash) + Gate 2 stress (30 seq + 3 concorrenti, `.ips` 22→22, RSS stabile) = PASS.
- Durevole: artefatti in `voice-agent/lib/pjsua2/prebuilt/` (`.so.ndebug`, `.so.PRE-NDEBUG-bak`, `pjsua2.py.ndebug-build`) + ricetta `voice-agent/docs/pjsua2-ndebug-build.md`. Tracked su master.
- Git: master allineato origin + iMac + MacBook (`8f90a74`/`8b2f70c`/`68398e4`). Branch `fix/license-interop-r01-s327` INTATTO col suo WIP license (NON ancora su master, track separato).

## RESIDUI OPZIONALI Sara (NON bloccanti, non riaprire come crash)
- **Gate 2 provider-reale**: opzionale, gated su 2° account VivaVox (azione EHIWEB lato Luke). NON prerequisito (crash era transport-independent). Solo se Luke vuole riprova "telefonata vera".
- **Ricetta g++**: i comandi g++ manuali del build SWIG sono marcati `DA VERIFICARE` nel doc (se rebuild futuro e `make python` fallisce). `LC_ID_DYLIB` del `.so` punta ancora a `/tmp` (cosmetico, fix `install_name_tool` documentato).
- **`.env.bak*`**: ora gitignored (contengono GROQ/OpenRouter key, restano locali iMac, mai pushati). Sorvegliare REGOLA #19.

## NEXT — roadmap CTO-actionable (research-first REGOLA #16)
Sara sbloccata → per gate vendita REGOLA #21 si può RIPRENDERE il test vocale Sara sui verticali (Layer 1 testo già VERDE S333: 50 OK/3 WARN/12 verticali; ora il path audio non crasha più → estendere a chiamate audio reali CTO-guidate via TTS, REGOLA #23/#14).
Carry tecnici residui:
- **R2**: CI `release-full.yml` ROTTO (5 run failure). Prima azione: `gh run view 25328286560 --log-failed`.
- **R3**: E-3 `sk_live` (Stripe live key).

## CONTESTO PRODOTTO
EHIWEB/VivaVox = carrier per ogni cliente FLUXION che ospiterà Sara. Path inbound-answer+media ora crash-proof su loopback+carico. Gate vendita REGOLA #21.
