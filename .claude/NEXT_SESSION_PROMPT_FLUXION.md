# NEXT_SESSION_PROMPT — FLUXION (handoff complessivo) · 2026-06-01

> Da incollare a CC per CHIUDERE la sessione corrente e ripartire pulito. Ruoli: CC = esecutore Mac ·
> Claude AI = giudice/researcher · Luke = autorità. Vincoli: solo `filesystem:*` MCP; **L0 ask-always**
> (diff + yes/no per file prima di scrivere); **chiusura context ~60%** (non iniziare task critici sopra
> soglia); **nessun valore di credenziale in chat/file** (solo "configurato ✅").
> **Regola: la prossima sessione sceglie UN blocco e lo apre a context fresco. Non incatenarli.**

## ⚠️ SICUREZZA — azione immediata
La password VoIP EHIWEB (`VOIP_SIP_PASS`) è stata **esposta in chiaro in chat** → **RIGENERARLA dal
pannello EHIWEB** e aggiornare SOLO il `.env` iMac. Non inlinarla mai più su riga ssh o in prompt.
Precedenti già successi (Auto.dev key, token Telegram): trattare come compromessa.

## STATO COMPLESSIVO (code-truth)
| Anello | Stato | Note |
|---|---|---|
| Payment rail (Worker/D1/Ed25519/Resend) | VERIFICATO codice | secret prod OK (`ED25519_PRIVATE_KEY_PKCS8`) |
| **R-01 interop licenza** | 🔴 BLOCKER revenue, deciso, da implementare | Worker firma `LicensePayloadV1`(6) ≠ Rust verifica `FluxionLicense`(11) → `verify()` sempre false; `issued_at` tipo diverso |
| B9 (3 route Resend) | ✅ FATTO S326 (commit 4d932e8) | migrate a `licenze@fluxion-app.com` |
| B6 (rm dead-code LemonSqueezy) | ✅ FATTO S326 (commit 4d932e8) | `git rm -r scripts/license-delivery/` (7 file) |
| D1 (schede vuote) | GO, da implementare | `SchedaPet.tsx` + rimappare 4 micro |
| **Sara vocale live (S322)** | 🟡 SIP registra, **audio RTP non validato** | baseline HTTP 21 OK/8 WARN/0 FAIL (7/8 falsi negativi) |
| **R-10 GDPR Art.9** | 🔴 gate verticali sanitari | dati sanitari plaintext + gate consenso non enforced |
| GTM automatico zero-cost | da costruire (Estetica-first) | founder non vende manuale → automazione necessaria |
| Skills/combo contenuti | [DA VERIFICARE] | parere onesto CC su efficacia |

## DECISIONI GIÀ PRESE (non ri-chiedere a Luke)
- **R-01 = modello (b)**: Worker INTOCCATO firma `LicensePayloadV1`; Rust verifica QUELLA firma e
  **deriva `FluxionLicense` localmente**; hardware-lock = **bind locale post-verifica al 1° avvio, NON
  nella firma** (hardware-lock rigido NON richiesto, rischio pirateria B2B accettato). In scope:
  **percorso ri-attivazione** (reinstallo/cambio disco → ri-bind da stessa email/license_id),
  unificare `issued_at` a int. **Niente activation server / revoca online in v1.** Chiudere con **E2E
  reale** (carta 4242 → webhook → D1 → firma → Resend → wizard activate) + evidence salvata.
- **B9 → GO** (migrare a `licenze@fluxion-app.com`); **B6 → GO**; **D1 → GO** (no `hasScheda:false`,
  rimap: dermatologo/logopedista→Medica, makeup_artist→Estetica, autolavaggio→Veicoli).
- **Pricing**: solo **una tantum** (NO ricorrente). Prezzo d'ingresso **basso come leva** → poi **sale**
  (verso €890–1.500, ancorato al costo receptionist). Comunicare "prezzo fondatore, salirà".
- **GTM**: **automatico, autogenerato da CC, zero-cost, NO ads a pagamento (assoluto)**. Estetica-first,
  poi replica. Sara-telefono NON promettere finché non validato.

## BACKLOG ORDINATO — un blocco per sessione, a context fresco
**B0 (chiudibile ora, basso costo)**: completare B9 (3 diff) + B6 (`git rm`). ✅ FATTO S326. Poi commit + chiusura.

**B1 — R-01 (PRIORITÀ revenue, sessione dedicata)**: implementare modello (b) come sopra + E2E reale.
Acceptance: `verify()` PASS su payload reale del Worker, tamper→false; E2E con evidence (G1+G2);
ri-attivazione testata. Worker/landing intoccati. (Prompt di dettaglio: `PROMPT_CC_SESSIONE_R01.md`.)

**B2 — Sara vocale live S322 (sessione dedicata, Filo B)** — *basato sul prompt S322 di CC, corretto*:
- STATO: canale EHIWEB riattivato, **SIP `registered:true`** su `0972536918@sip.vivavox.it` (pjsua2 +
  `.env` iMac). Baseline HTTP `test_all_verticals_e2e.py` = 21 OK/8 WARN/0 FAIL (7/8 WARN = falsi
  negativi; 1 reale: routing FAQ "fisioterapia/seduta" → fix). **BLOCKER residuo: audio RTP E2E mai
  validato a runtime** (SIP register ≠ audio funziona).
- FASE 0-bis (research-first, zero-cost): costruire harness audio autonomo (CTO parla a Sara via TTS,
  non Luke al telefono — REGOLA #23). NON esiste endpoint HTTP audio-in→STT; lo STT vive nel path
  SIP/RTP. Metodo: secondo client SIP che riproduce WAV (TTS) e cattura RTP → STT → valutazione.
  ⚠ **Verificare PRIMA se chiamare il numero PSTN da un secondo client genera costi EHIWEB**; restare
  zero-cost (secondo account SIP interno, non PSTN, se il PSTN costa). Delegabile a `voice-engineer`.
- Avvio pipeline (la password sta nel `.env` iMac già caricato — **NON inlinare**, e rigenerala):
  `ssh imac "cd '/Volumes/MacSSD - Dati/fluxion/voice-agent' && nohup python main.py --port 3002 > /tmp/sara.log 2>&1 &"` poi `ssh imac "curl -s http://127.0.0.1:3002/api/voice/voip/status"`.
- Poi FASI 1-4: harness stress 9 verticali → misura lacune (booking ok, FAQ ok, disambiguazione,
  latenza p95<800ms, naturalezza) → piano integrazione con E2E obbligatori. NO "Sara ready" senza
  evidence + GO Luke.

**B3 — D1**: `SchedaPet.tsx` (schema pronto) + 4 rimappature. Context fresco.

**B4 — R-10 GDPR Art.9** (prima di qualunque GTM/vendita ai verticali sanitari): censire campi Art.9 →
cifrarli (riusa crypto `clienti.rs:263-308`) → enforce gate `has_art9_consent` fail-closed →
`revoke_consent` + export audit. (Prompt: `PROMPT_CC_FIX_GDPR_ART9.md`.) NON blocca Estetica.

**B5 — GTM automatico Estetica + parere contenuti**: prima far dare a CC il **parere sul MASTER +
assessment skills contenuti** (`PROMPT_CC_PARERE_MASTER_E_CONTENUTI.md` + zip MASTER), poi costruire la
pipeline (`PROMPT_CC_GTM_AUTOMATICO.md`): lead-gen + outreach WA con guardrail anti-ban (SIM IT,
warm-up 14gg, 5 nuovi/giorno, DAILY_LIMIT=30, opt-out) + landing + dashboard lead-score. Zero-cost, no ads.

## CLEANUP carry-over
- PLAN.md `OBIETTIVO:19` "9 verticali" → "8 macro / 6 con scheda (5 funzionanti + pet)".
- Nascondere `professionale` + `formazione` dal Setup Wizard finché senza scheda+demo (toglie falsa
  promessa di vendita).
- Allineare ref stale: `rusqlite`→sqlx 0.7, RAG "4-layer"→5, FSM "23"→14, rimuovere ref LemonSqueezy.

## ORDINE CONSIGLIATO (CTO)
B0 (chiudi ora) → **B1 (R-01, revenue)** → B2 (Sara live) ‖ B5 (GTM, parallelo no-code) → B3 → B4
(prima dei sanitari). R-01 e Sara-live in **sessioni separate**: non far mangiare a Sara il context di R-01.

## CHIUSURA (REGOLA #5)
Commit di B9/B6 se applicati + salvare questo handoff come prompt di ripartenza. STOP. VALUTALO IN NEXT SESSION PRIMA DI ESEGUIRE
