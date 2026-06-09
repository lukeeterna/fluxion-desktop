# CARRY MAGAZZINO — FASI 1-5 COMPLETE E VERIFICATE. Restano: FASE 6 E2E (founder GUI) + igiene repo iMac.

> **Stato (commit `e138345` codice + `176eba1` docs, su origin/master)**: modulo Magazzino+alert sottoscorta completo backend+UI+gating.
> - FASI 1-3 backend (migration 042, 9 cmd Tauri, alert anti-spam): `cargo test --lib magazzino::` 4/4.
> - FASE 4 UI React: pagina Magazzino + hook `use-magazzino` + sidebar badge (`magazzino_alert_count`) + dashboard widget + route + gating upsell (`MagazzinoBloccato`) + toast su ogni mutation. `npm run type-check` 0 errori.
> - FASE 5 gating Pro-only: flag `magazzino_alert` in `LicenseFeatures` (Trial/Pro/Enterprise=true, Base=false) + match arm `check_feature_access_ed25519`. `cargo check` iMac 0 errori. Payload firmato NON toccato.
> - Decisioni founder risolte (REGOLA #15): gate=Pro-only (no nuovo SKU Stripe); email sottoscorta 3c=DEFER (no scope-creep Python, `TODO(magazzino-3c)` resta).
>
> **RESIDUO MAGAZZINO — FASE 6 BLOCCATA DA PREREQUISITO (P1 scattato, indagine 2026-06-09)**:
> Stato reale iMac VERIFICATO: HEAD `40fcb80d` **97 commit dietro** origin; **frontend FASE 4 ASSENTE** (Magazzino.tsx/use-magazzino.ts/types/magazzino.ts non esistono su iMac — committati solo su origin `e138345`); backend magazzino presente ma non committato. → il binario girante NON contiene il magazzino e non esiste pagina/sidebar. FASE 6 E2E IMPOSSIBILE finché l'iMac non ha il codice completo.
>
> **PREREQUISITO FASE 6 = riconciliare iMac → origin/master `95d21cc` (con Luke presente, GO esplicito sul reset --hard).**
> Sicurezza già analizzata: (a) `.so` NDEBUG Sara sono git-TRACKED e su origin via `8b2f70c` → reset NON li perde; (b) magazzino backend uncommitted su iMac = redundante (su origin `e138345`); (c) commit locale `40fcb80d` = contenuto su origin via `8b2f70c` → redundante; (d) 33 stash = WIP storici, il reset NON tocca gli stash. Comando:
> ```
> cd '/Volumes/MacSSD - Dati/fluxion'
> git stash push -u -m "PRE-FASE6-safety-$(date +%Y%m%d)"   # rete di sicurezza (redundante)
> git fetch origin master && git reset --hard origin/master
> git log --oneline -1   # deve mostrare 95d21cc
> ```
> Poi: build/launch app Tauri su iMac (npm install se serve) → poi E2E S1-S7 (addendum sotto).
>
> **FASE 6 E2E — ADDENDUM SCENARI** (HITL, Luke clicca / CC osserva DB+log read-only, verdetto OK/FAIL con prova): S1 crea articolo (giacenza10/soglia5, alert=0) · S2 badge=0 sopra soglia · S3 scarico 6→giacenza4 alert=1 count=1 · S4 badge sale SENZA aprire pagina · S5 pagina evidenzia sottoscorta · S6 anti-spam (2° scarico non ri-emette; carico sopra soglia→alert=0) · S7 gate licenza Base=upsell (serve licenza Base; se manca → PENDING non PASS). 🚀 solo se S1-S6 PASS (S7 PASS o PENDING). Output: tabella in MAGAZZINO_BUILD_2026-06-08.md + verdetto secco.
> **ORDINE FOUNDER (2026-06-09)**: FASE 6 Magazzino → poi Windows (R2) → poi Sara.
>
> **Trade-off segnalato (REGOLA #29)**: Magazzino è fuori dal percorso revenue. Il vero gap €497 resta **R1 Sales Agent → checkout** (vedi sotto / ROADMAP_REMAINING.md). Valutare se riprendere R1 o test Sara prima di altre feature prodotto.
>
> --- carry Sara S356-S358 sotto (invariato) ---

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
> **S358 METODO TEST AUDIO DEFINITIVO (chiarito da Luke S357, vincolante)**: il VAD non scattava perché l'harness inietta audio SINTETICO, non perché Sara è rotta. Flusso corretto IBRIDO: (1) CC dice a Luke "effettua la chiamata"; (2) **Luke chiama 0972536918 dal suo telefono** = apre canale RTP REALE (1 gesto, unico compito di Luke); (3) Sara risponde, VAD scatta su audio reale; (4) **CC fa il cliente via TTS su iMac**, switcha tutti i verticali; (5) **CC legge i log Sara iMac** in tempo reale (STT capito + risposta FSM/TTS), registra, **perfeziona Sara**. PRIMA AZIONE S358 = CC risolve+testa il routing audio "TTS iMac → dentro la chiamata di Luke" (vivavoce telefono accanto a casse iMac OPPURE routing audio iMac OPPURE softphone uscente sull'iMac che chiama il numero col timing provider reale) **PRIMA** di chiedere a Luke di chiamare, così la chiamata non si spreca.
> **S358 FIX PRODOTTO PARALLELI (autonomi, no chiamata)**: i 2 bug TESTO trovati S357 — guardrail-per-verticale + intent assicurazioni — si fixano senza chiamata (delega voice-engineer + sara-nlu-trainer). NON dichiarare Sara "pronta vendita" (REGOLA #21) finché guardrail-per-verticale non passa su chiamata reale. Claim agente S357 da verificare trust-but-verify (lezione S349/S354).
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
