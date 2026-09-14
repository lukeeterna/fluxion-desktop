# FLUXION — ROADMAP REMAINING TO PRODUCTION (AUTHORITATIVE)

> **Stato canonico aggiornato: 2026-08-22.** Questo file è l'unico elenco operativo dei gate rimanenti verso produzione.
> La precedente roadmap revenue/S344 è storica e non governa più la sequenza di certificazione corrente.
> **Regola:** nessun gate è GREEN per inferenza. Ogni chiusura richiede evidenza verificabile sullo SHA candidato esatto; un failure di infrastruttura resta RED/BLOCKED, non viene mascherato come prodotto certificato.

## Candidato corrente

- PR attiva: **#60 — `fix/sara-gate-shell-only`**
- Base: `master`
- Gate corrente: **G1 — CI/runtime #60**
- Gli SHA sono candidati temporanei finché G1 non è interamente GREEN; ogni commit successivo invalida le certificazioni exact-SHA precedenti.

---

## G1 — PR #60: CI/runtime completo

**Stato: IN PROGRESS / RED.**

Done-condition:
- tutti i workflow richiesti della PR sono GREEN sullo **stesso head SHA**;
- nessun test viene neutralizzato o escluso per ottenere il verde;
- failure di test, lint, security scan, Rust/Tauri, E2E e Sara release gate vengono distinti tra difetto prodotto e difetto CI/runtime e corretti alla causa;
- il `Sara Release Gate (Full)` deve raggiungere realmente la pipeline prevista sul candidato exact-SHA, non solo superare il bootstrap shell.

Evidenza minima:
- head SHA della PR;
- elenco workflow + conclusion sul medesimo SHA;
- log dei fix reali applicati.

Stato osservato prima dell'ultima tornata di fix:
- Control Plane Static Gate: GREEN;
- Main CI / Python: RED per assertion conversazionale brittle a fronte di FSM corretta;
- Voice Agent CI: RED, da chiudere senza indebolire Ruff/security scan;
- E2E: RED per browser Playwright non installato coerentemente con il progetto Firefox; fix in corso sul branch;
- Rust/Tauri Test Suite: RED, causa da certificare dai log prima di modificare codice;
- Sara Release Gate Full: RED nel pre-flight, causa da certificare dai log prima di dichiarare iMac eseguito.

---

## G2 — Issue #65: verdetto indipendente P0

**Stato: BLOCKED ON G1.**

Done-condition:
- review realmente indipendente del P0 sullo SHA che ha chiuso G1;
- verdict esplicito **APPROVE**;
- nessun self-approval o verdict sintetizzato dall'autore del fix;
- pubblicazione/merge consentiti solo dopo APPROVE.

Se il verdict è REQUEST_CHANGES/REJECT, si torna a G1 con nuovo SHA e nuova review.

---

## G3 — iMac exact-SHA performance gate

**Stato: BLOCKED ON G2.**

Done-condition:
- checkout/esecuzione sull'iMac del medesimo SHA approvato in G2;
- prova runtime reale;
- **P95 < 2000 ms**;
- report/log legato allo SHA esatto.

Una prova su SHA precedente o su working tree dirty non vale.

---

## G4 — Trasferimento EHIWEB reale / B2BUA

**Stato: BLOCKED ON G3.**

Done-condition, su trunk EHIWEB reale:
- chiamata Sara reale e richiesta trasferimento;
- seconda gamba verso operatore;
- **risposta effettiva dell'operatore** prima di considerare il transfer riuscito;
- continuità audio B2BUA verificata tra le gambe previste;
- scenari `busy`, `no-answer` ed `error` verificati fail-safe;
- privacy/ownership del trasferimento e dei dati chiamata verificata;
- log/report riconducibili allo SHA certificato.

Un SIP REFER accettato o un semplice `200` di segnalazione non costituiscono da soli prova di trasferimento riuscito.

---

## G5 — Windows nativo pulito

**Stato: BLOCKED ON G4.**

La precedente certificazione/PR #62 **non vale** come certificazione finale di questo gate.

Done-condition su macchina/runner Windows pulito:
- Python runtime/dependency path verificato;
- Go build/runtime verificato;
- Rust/Tauri build e test verificati;
- CRT statico dove richiesto dal disegno di release;
- installer **NSIS** prodotto e installato;
- avvio applicazione post-install reale;
- nessuna dipendenza accidentale dalla workstation di sviluppo;
- artifact e checksum registrati sullo SHA candidato.

---

## G6 — Credential hardening / Issue #63

**Stato: BLOCKED ON G5.**

Done-condition:
- scanner/check CI rileva credenziali hard-coded reali evitando falsi positivi da semplici nomi di variabili, senza diventare permissivo;
- virtualenv/vendor/third-party non contaminano il risultato lint/security;
- segreti runtime sono gestiti tramite secret store/env previsto;
- **la credenziale già esposta è realmente revocata/ruotata presso il provider**;
- evidenza della revoca/rotazione registrata senza pubblicare il nuovo segreto;
- issue #63 chiusa solo dopo entrambe le parti: hardening codice + revoca reale.

La sola modifica dello scanner non chiude G6.

---

## G7 — Installer / release / updater / rollback

**Stato: BLOCKED ON G6.**

Done-condition:
- release candidate generata dallo SHA certificato;
- installer macOS/Windows richiesti presenti e installabili;
- release pubblica coerente: nessuna `latest` vuota o senza asset richiesti;
- updater prova upgrade verso la release candidata;
- rollback prova ritorno alla versione precedente/sicura senza perdita o corruzione dei dati prevista dal prodotto;
- checksum/manifest degli artifact registrati;
- smoke post-install/post-update/post-rollback GREEN.

---

## G8 — Gate primo cliente

**Stato: BLOCKED ON G7.**

Done-condition:
- tutti G1–G7 GREEN con evidenza;
- percorso di installazione/onboarding del primo cliente eseguito sul pacchetto certificato;
- servizi necessari operativi in produzione;
- chiamata/booking/gestionale e percorso commerciale in-scope verificati secondo configurazione cliente;
- rollback/support path disponibile;
- GO esplicito alla produzione solo dopo il terminal fact del primo cliente.

---

## Ordine vincolante

`G1 #60 CI/runtime` → `G2 #65 APPROVE` → `G3 iMac exact-SHA P95<2000` → `G4 EHIWEB transfer reale` → `G5 Windows nativo pulito` → `G6 #63 + revoca` → `G7 release/updater/rollback` → `G8 primo cliente`.

**PRODUCTION = tutti gli otto gate GREEN.**
