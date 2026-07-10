# REPORT T-SARA-TURNTAKING — TASK#0 TRIM MEMORY.md (sessione 2026-07-10)

Gate label (#1c): **TASK#0 / trim meccanico lossless** · Verdetto: 🟢 **TASK#0 CHIUSO (D0 provato)** · FASE 1-R mutazione **rinviata 3ª volta MA root-cause FIXATA** (defer qualitativamente diverso) · Mutazioni codice prodotto: **ZERO**.

## VERDETTO
FASE 0 riverificata VERDE (baseline live identica al PREFLIGHT, zero drift). TASK#0 eseguito e provato: MEMORY.md **920→151 righe** (188010→26158 byte, −86%) con metodo MECCANICO lossless (REGOLA #26 + #1d), archivio verbatim committato. Il defer di FASE 1 stavolta NON è a vuoto: la root cause del doppio-defer (boot pesante ~180KB MEMORY) è rimossa → prossimo boot ~26KB → FASE 1+2 a headroom pieno.

## FASE 0 — baseline live (prova grezza, ssh imac)
- Sara `main.py --port 3002` PID **82763** (unico), default pjsua2 (`VOICE_ENGINE` non settato).
- `/health` ok v2.1.0; `/voip/status` → `registered:true, reg_status:200, engine:"pjsua2", rtp_active:false`.
- **3003 DOWN** (curl exit 7 = refused); **zero orfani** engine_darwin/gospike; `calls/` vuota (default-OFF).
- uac.go md5 **`850d32a904ee1fbc6c85eb3c2021fc2e`** (10861B) iMac==MacBook = INVARIATO = versione buggy df3fda5 (atteso dal mandato ✓).

## TASK#0 — TRIM (D0)
### Metodo (#1d + #26, meccanico non LLM-rewrite)
1. **PRE-TRIM**: md5 `96194ddb850b0de28f7f556ebd13c7b1`, 188010B, 920 righe.
2. **#1d BACKUP** (stessa dir, fuori /tmp): `MEMORY.md.bak-PRE-TRIM-20260710-175449` (188010B, md5 identico).
3. **ARCHIVIO verbatim** (repo, committato): `.claude/cache/MEMORY_ARCHIVE_20260710.md` = `cp` byte-per-byte dell'originale → `diff` originale↔archivio = **0** (lossless per costruzione).
4. **TRIM** = estrazione byte-per-byte (`sed`) dei soli blocchi load-bearing, NIENTE riscrittura:
   - righe 1-54 (header: REGOLE #1-#32 + firme falsificazione S354/S355/S244/S364/S365/scraper + verità Windows)
   - righe 672-757 (guardrail permanenti: PATH MEMORY, WORKFLOW, E2E PAYMENT, KARPATHY, CTO OWNERSHIP, CONTEXT ROT, FILE SCHEMA CRITICI, MULTIPASS, SENTRY, DOMINI, Fondatore, Progetto, SSH iMac)
   - righe 915-920 (nota archivio storico + REGOLA #30 stray S362)
   - + additive: REGOLA #33 (≤250 righe→archivio) + pointer archivio completo.
   - SCARTATE (verbatim in archivio): righe 55-671 e 758-914 = log sessione-per-sessione S354→S256 (pjsua2 saga, Stripe/CF/Brevo/Resend, Windows, PII encryption).

### Prova D0 (non a racconto)
- **Lossless riga-per-riga**: ogni riga non-vuota del trim (escluse le 2 nuove REGOLA #33) → `grep -F` presente nell'archivio = **0 mancanti**.
- **Lossless insiemistico**: `diff <(sort backup) <(sort archivio)` = **0** → archivio ⊇ ogni riga dell'originale.
- **Fatto terminale #1d (contenuto presente DOPO, non soglia dimensione)**:
  - **33 REGOLE** definizioni blockquote presenti (#1-21, #23-27, #29-33). #22/#28 non furono MAI definizioni-header (solo menzioni narrative nei log) → preservate in archivio, nessuna perdita di definizione canonica.
  - Firme falsificazione: S354 CONFINEMENT FALSIFICATO / S355 CRASH RISOLTO / S244 FALSIFICATA / S364 / S365 / SCRAPER EVAL → tutte OK.
  - Vincoli duri: GUARDRAIL PATH / E2E PAYMENT / CTO OWNERSHIP / CONTEXT ROT / FILE SCHEMA CRITICI / DOMINI / SSH iMac / WORKFLOW → tutti OK.
- **POST-SWAP**: MEMORY.md 151 righe, 26158B, md5 `f3355a7475b627a913a673dca87cdd68`. Backup #1d + archivio intatti (restore garantito).

### Context guadagnato (numero, non impressione)
Boot memory persistente: **188010B → 26158B = −161852B (−86%)**, ~**40k token in meno per boot**. Root cause del doppio/triplo-defer (#11) rimossa.

### Regola di chiusura aggiunta
REGOLA #33 nel header MEMORY.md: a fine sessione se >250 righe → trim meccanico lossless verso `.claude/cache/MEMORY_ARCHIVE_<data>.md`. Da incorporare nel rito di chiusura permanente.

## FASE 1-R — perché rinviata (onesto #9, NON diplomatico)
Context reale oltre il ceiling mutante ~45-50% (hook RAW 53→57%, gonfiato #27 ma boot+letture reali pesanti) + #7 chiude a 60%. Avviare ora il rewrite Go RX-goroutine/TX-ticker + build darwin + cross windows + scp + smoke 3003 (open-ended, 2 macchine, con iterazione) = rischio stop a 60% **a metà mutazione** = uac.go sporco su 2 macchine. Asimmetria #1b/#6/#7 invariata. **Differenza vs S-precedenti: la root cause è ora fixata** → il defer non è sterile, è il completamento del prerequisito.

## STATO LASCIATO
- Sara default **pjsua2 PID 82763** su 3002, `reg_status:200`, INVARIATA (zero edit runtime). Restore point intatto.
- 3003 DOWN, zero orfani, `calls/` vuota (default-OFF).
- uac.go/main.go harness INTATTI (md5 `850d32a9…` invariato). Backup pre-F31 `.bak-PRE-F31-20260709-170519` su disco (untracked).
- VectCutAPI NON toccato (resta modificato da prima, fuori scope).

## PROSSIMO (sessione fresca = boot leggero, headroom pieno)
1. FASE 0 rapida: baseline live (PID 82763 atteso), context reale (ora parte leggero).
2. FASE 1-R: #1d backup uac.go (md5 `850d32a9…`) → refactor spec (PREFLIGHT §7: RX-goroutine echoBuf+mutex+cancelCall / TX-ticker 20ms echo+inject / BYE+CALL_END a -dur / import sync) → `go build` darwin + cross `GOOS=windows GOARCH=amd64 CGO_ENABLED=0` SUL MACBOOK → scp `gospike_darwin_amd64` → iMac → smoke D1 su 3003 (VOICE_ENGINE=go, VOIP_SIP_SERVER=127.0.0.1 dummy, SARA_TEST_CAPTURE=1, -dur 30): harness termina solo + WAV non-vuoto in `calls/`, default-OFF riverificato.
3. FASE 2 GATE A3: 5 scenari (ECO / BARGE-IN / FILLER-zero / NO-HANGUP / SILENZIO 22s+18s) + ADDENDUM W, artefatti WAV+derivato per scenario.
4. CHECKPOINT → FASE 4 GATE B3 (founder). T-GIT-REALIGN resta parcheggiato (deploy scp+md5, no pull iMac).
