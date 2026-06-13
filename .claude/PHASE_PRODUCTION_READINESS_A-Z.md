# FLUXION — NEXT SESSION PROMPT — FASE "PRODUCTION READINESS A→Z" — 2026-06-13
> Ruoli: **Claude = CTO/firewall/critico** (no filesystem) · **CC = esecutore + sviluppatore** (Mac+Windows via SSH, agenti VOS) · **Luke = founder**, sola autorità su strategia, fa i tocchi fisici irriducibili.
> Regola di fase (Luke): **in produzione si va SOLO ad app perfettamente funzionante e testata A→Z. Non prima.** Strada A confermata.
> Vincoli: **WIP=1 su questa fase**, **anti-falso-verde** (evidenza, non claim/report), italiano.

---

## 0. STATO — PILA 1 STRUTTURALE: CHIUSA

- 🟢 VERITÀ #1 — app gira su Windows reale.
- 🟢 VERITÀ #2a — attivazione licenza reale verificata alla fonte (S365).
- 🟢 (c) Charge E2E continuity — CHIUSA a €0 (S365): file da charge Stripe LIVE (S317) → `verify_strict` Rust dalek reale → `license_cache` (delta `license_id`/`signature` provato pre/post-touch). Caveat refund tenuto distinto (gate D4 separato).
- 🟢 Sara su Base — trial 30gg via phone-home, nessun bug.

**Non resta infrastruttura. Ciò che separa dal 1° CLOSED_WON è la QUALITÀ DI ONBOARDING del non-tecnico.** Punto cieco sistematico documentato: tre difetti emersi per caso (P.IVA, dropdown, copy post-pagamento), tutti della stessa famiglia, mai trovati con un giro deliberato del flusso cliente.

---

## 1. PRINCIPIO DI RIPARTIZIONE (leggere prima — definisce di chi è ogni test)

CC ha agenti VOS e DEVE testare tutto il fattibile da lui. Ma esiste una linea fisica netta, non negoziabile:

- **CC autonomo, €0, ne risponde:** tutta la logica frontend React via **Playwright sul dev server** (form, validazioni, calcoli, navigazione, stati vuoti/errore, ogni dropdown, ogni z-index) + logica backend/Rust via unit/integration test. **Qui pretendo copertura completa feature-per-feature.**
- **Tocco umano irriducibile (Luke, one-shot):** l'app REALE è Tauri/WebView2 nativa su Windows; **non esiste percorso headless per l'attivazione** (verificato: niente CLI/IPC, solo GUI nativa). Costruire `tauri-driver` per un walkthrough one-shot costa più del valore → **VIETATO**. Il giro nativo reale su Windows lo conferma il founder fisicamente.

Regola anti-falso-verde su questa linea: **"PASS via Playwright dev-server" NON è "PASS su Windows nativo".** CC non deve mai rietichettare la prova browser come prova end-to-end nativa. Browser prova la logica; solo il giro fisico prova l'app consegnata.

---

## 2. METÀ 1 — FIX HEADLESS NOTI (CC autonomo, €0, ore non giorni)

1. **Copy post-pagamento (PRE-LANCIO, NON "si chiude col cliente"):** `fluxion-proxy/src/routes/checkout-success.ts` Passo 2 istruisce "inserisci email → auto-verify" = path RIMOSSO (R-01, `LicenseManager.tsx:337`). Manda al muro chi HA GIÀ PAGATO → prerequisito assoluto, non osservabile sul cliente. Riscrivere Passo 2 → percorso reale (recovery-URL / paste-upload JSON). **Correggere anche l'etichetta nel carry: questo è fix pre-lancio.**
2. **Riepilogo errori wizard:** `SetupWizard.tsx` → `handleSubmit(onSubmit, onInvalid)`; in `onInvalid` riepilogo prominente accanto a "Avvia FLUXION" (map `formState.errors`) + scroll/jump al primo campo invalido e allo step. `toast.error(String(error))` nel catch (:123-125). Causa-radice del bug P.IVA.
3. **Dropdown/overlap:** menu a tendina che coprono il contenuto sottostante = `z-index`/stacking context o dropdown in-flow invece che in portal, o parent `overflow:hidden`. Riproducibile sul dev server in browser, fix CSS/portal diretto.

---

## 3. METÀ 2 — TEST A→Z (criterio di chiusura falsificabile)

### 3a. CC autonomo — MATRICE FEATURE COMPLETA (Playwright dev-server + Rust)
Ogni feature di FLUXION = una riga. Ogni riga PASS **con evidenza** (output del test, screenshot, asserzione — NON la parola "fatto"). Include esplicitamente:
- Wizard setup (tutti i campi, tutte le validazioni, tutti i path d'errore).
- Gestione licenza (carica-file, paste, recovery-URL — la logica di parsing/verify).
- **(d) Magazzino + alert scorte** (GATE PASS S361 → da RI-provare con evidenza, non dato per chiuso): CRUD articoli, soglie, trigger alert, stati limite (0, soglia, negativo).
- **Fatturazione SDI** — ⚠️ **PRIMA accertare cosa fa davvero la feature**: la roadmap la marca a integrazione incerta (rischio "solo schema DB"). Se è uno **stub**, CC lo DICHIARA stub e NON le dà PASS. Provare PASS a uno stub = falso-verde da manuale. Solo se è integrazione vera → generazione/campi/casi limite.
- **Sara (frontend) — CC autonomo:** banner, giorni residui, gating trial 30gg via phone-home, comportamento a trial scaduto. Questo è browser-testabile.
- Navigazione, stati vuoti, gestione errori di rete (es. `FirstRunNetworkModal`).

Output: tabella `feature | tipo test | PASS/FAIL | evidenza`. I FAIL diventano difetti registrati e fixati. **Questa è la parte "Luke non prova tutto" — la prova CC.**

### 3a-bis. SARA — COMPORTAMENTO VOCE/SIP REALE — TUTTI I VERTICALI PRIMA DI QUALSIASI VENDITA (decisione founder)
**Sara è la feature-civetta del trial Base e parla coi clienti veri: i suoi guardrail (privacy/GDPR, niente impegni inventati, resistenza a manipolazione) sono rischio reale, non rifinitura. Va provata su TUTTI i verticali con chiamata reale prima di qualsiasi vendita.** Il comportamento reale (telefonia SIP/media, pjsua2, voce Piper) **non si prova con Playwright** — richiede chiamate reali + rebuild pjproject `-DNDEBUG=1` (fix SIGABRT a verbale).

**Metodo (già esistente e collaudato, founder + CC):** Luke esegue **chiamata reale dallo smartphone**; CC esegue **stress test completi dall'iMac** (parla lui lato agente, **registra TUTTI i log**). Fattibile e già fatto come test → CC lo sa e lo riusa per ogni verticale.

**Catalogo pattern di stress test:** vedi file dedicato `SARA_STRESS_TEST_PATTERNS.md` — dimensioni: guardrail, riconoscimento abitudini cliente, riconoscimento identità cliente, attitudine alla soddisfazione piena. Da instanziare per OGNI verticale.

**Anti-falso-verde Sara:** PASS solo da **chiamata reale completata e osservata + log**, MAI dal banner che renderizza, MAI dichiarato.

**Criterio di chiusura per verticale (falsificabile):** per ciascun verticale, una batteria di chiamate reali in cui (1) il task di dominio è completato end-to-end, (2) i guardrail tengono su tutti i pattern BLOCCANTI del catalogo, (3) nessun crash/SIGABRT, (4) log puliti. Verticale verde solo a queste condizioni osservate. "Sara perfetta" = tutti i verticali verdi così.

### 3b. Founder — WALKTHROUGH NATIVO IRRIDUCIBILE (Windows pulito, one-shot)
Il giro che il browser NON può toccare:
1. **Installer da zero** su Windows pulito (no stato pregresso).
2. **Wizard** completato come un cliente vero.
3. **Attivazione DI DEFAULT del cliente** — NON il carica-file usato nei test: il percorso **email → recovery/phone-home**. Questo path **non è mai girato live**.
4. **Deliverability reale:** invio Resend vero a una **casella apribile** da Luke (S317 risultava "delivered" ma mai arrivata → bandierina aperta). Verificare che la mail-licenza atterri leggibile E sia attivabile come consegnata.
5. **Uso reale del verticale:** magazzino, SDI, Sara trial — usati a mano, non solo aperti.

### 3c. CRITERIO DI CHIUSURA (falsificabile — né falso-verde né gold-plating)
La fase è CHIUSA quando un giro completo produce **ZERO inciampi BLOCCANTI**.
- **BLOCCANTE** = impedisce a un non-tecnico di completare install→attivazione→uso base **senza aiuto esterno**. → fix obbligatorio prima di chiudere.
- **COSMETICO** = registrato in backlog, NON blocca la fase. → non gold-platare, non rimandare il lancio per questi.
CC tiene il registro inciampi con questa classificazione esplicita per ogni voce.

---

## 4. FUORI SCOPE / CONGELATO

- Suite test di regressione permanente, harness `tauri-driver`, automazione del tocco nativo → Pila 2 (post 1° CLOSED_WON).
- Gate D4 (refund a runtime, fail-open), hardware-binding, code signing EV, hardening, GDPR e2e → Pila 2.
- Il **charge non-rimborsato del 1° cliente vero** chiude la giuntura refund a runtime — appartiene alla vendita reale, non a questa fase.

---

## 4-bis. REGISTRO PARCHEGGIATO — NON DIMENTICARE (CC lo riporta in ogni carry finché non chiuso)

Queste voci NON sono in scope ORA, ma NON spariscono. CC le tiene a verbale e le ripropone, non le lascia cadere:

1. **R1 — Sales Agent / canale di acquisizione inbound.** Gap revenue reale (un'app perfetta senza canale = €0). **NON entra ora né "in parallelo":** portare lead verso un onboarding non ancora testato li brucia sui difetti che stiamo fixando. R1 ha valore SOLO dopo che il flusso regge → **fase immediatamente successiva ad A→Z.** Riconosciuto, sequenziato, non dimenticato.

> Nota: "Sara perfetta su TUTTI i verticali" NON è più parcheggiata — è IN SCOPE in questa fase (§3a-bis), per decisione founder: tutti i verticali con chiamata reale prima di qualsiasi vendita.

---

## 4-ter. DEFINIZIONE DI "PRODUCTION READY" (hard gate — nessuno la dichiara senza questo)

Production ready = TUTTE verdi, con evidenza, NON dichiarate:
- §2 fix headless chiusi.
- §3a matrice feature completa PASS (SDI: stub dichiarato o integrazione provata, mai PASS a stub).
- §3a-bis **Sara provata con chiamata reale su TUTTI i verticali** (catalogo `SARA_STRESS_TEST_PATTERNS.md`): task di dominio completato, guardrail che reggono, no crash, log puliti — per ogni verticale.
- §3b walkthrough nativo Windows: installer→wizard→**attivazione-default cliente**→deliverability reale→uso verticale, **zero inciampi bloccanti**.
- §3c registro inciampi: zero BLOCCANTI aperti (cosmetici ammessi, in backlog).

Finché una sola di queste è gialla, **NON è production ready** — a prescindere da quanto "sembra" pronta. CC non promuove lo stato; lo fa solo l'evidenza.

---

## 5. REGOLE OPERATIVE
- **SSH→Windows:** PowerShell. `ssh fluxion-win 'powershell -NoProfile -Command "..."'`.
- **DB Windows:** `scp fluxion-win:'C:/Users/gianluca/AppData/Roaming/com.fluxion.desktop/fluxion.db'` → `sqlite3` su Mac (Windows non ha sqlite3.exe).
- **Anti-falso-verde:** evidenza alla fonte, non report d'agente. Playwright ≠ Windows nativo.
- **Hook context-budget = bug #27** (% gonfiata): ignorare auto-close, non lanciare con `CLAUDE_BYPASS_CTX_GATE` di default.
- **Backup off-site (post-crash T7):** prima di immergersi, confermare che i repo critici (FLUXION, venture-os, ARGOS) siano pushati su remote git off-site e aggiornati. Il T7 è single-point-of-failure dimostrato (S363→S364).
- **Carry canonico:** questo file. Copie in Downloads = stantie.

---

## 6. PRIMO ATTO DELLA PROSSIMA SESSIONE
1. Check backup off-site repo (§5) — 5 min, precondizione.
2. METÀ 1 fix headless (§2) — CC autonomo.
3. Avviare MATRICE FEATURE §3a (CC) in parallelo.
4. Quando §2+§3a verdi con evidenza → preparare il walkthrough nativo §3b per il founder.
