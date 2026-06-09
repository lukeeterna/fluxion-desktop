# FLUXION — INSTALLER WINDOWS: VERIFICA + SECURE STORAGE (rev. allineata allo stato reale)

## CONTESTO NOTO (da verificare, non da assumere)
Handoff S360 afferma che l'installer Windows è GIÀ stato buildato VERDE:
- CI run 27217198619 = SUCCESS
- artefatto "tauri-bundle-windows" = 404MB (.exe NSIS + .msi), da origin/master, incluso fix magazzino 042
- URL: github.com/lukeeterna/fluxion-desktop/actions/runs/27217198619
Quindi l'obiettivo "produrre un installer" potrebbe essere GIA' RAGGIUNTO.
Il lavoro vero residuo NON e' ri-buildare: e' (a) confermare che quell'artefatto e' dal master CORRENTE,
(b) verificare il secure-storage licenza su Windows, (c) nominare il blocco "PC Windows reale".

## OBIETTIVO
Stabilire con prova se esiste un installer Windows installabile E ATTIVABILE dal commit corrente di master,
oppure nominare con precisione cosa manca. NON ri-creare workflow gia' esistenti.

## REGOLE DURE
- NON refactorare/"migliorare" codice applicativo. Nessun file nuovo salvo STRETTA necessita', motivata.
- Lavorare dal commit corrente di master. Riportare l'hash (riproducibilita').
- Se qualcosa fallisce: STOP dopo max 2 tentativi, riportare l'errore ESATTO dal log CI. NO patch-e-ripeti.
- Italiano. Percorsi/termini in originale.

## FASE 1 — INVENTARIO con prova path:riga (read-only, prima di toccare nulla)
1. Framework + versione esatta: Tauri 2? (tauri.conf.json, Cargo.toml, package.json).
2. tauri.conf.json -> bundle.targets include Windows (msi/nsis)? identifier, version, productName.
3. .github/workflows/ : QUALE workflow builda Windows? E' lui che ha prodotto la run 27217198619?
   (NON creare un nuovo workflow se ne esiste gia' uno funzionante.)
4. ⚠️ CRITICO — Secure storage licenza su Windows. La licenza e' testata su Keychain macOS.
   Su Windows COM'E' implementata la persistenza sicura (DPAPI / Credential Manager / Tauri stronghold)? path:riga.
   Se NON esiste un backend Windows, l'attivazione fallira' anche con installer perfetto -> BLOCCO STRUTTURALE, nominalo.
   [Delegare l'audit a backend-architect: e' security-relevant.]
5. git remote -v (remote GitHub presente?).

## FASE 2 — RICONCILIAZIONE (sostituisce il "crea workflow" originale)
- Confronta la run 27217198619 col commit corrente master.
  - Se artefatto gia' dal master attuale -> obiettivo build RAGGIUNTO, NON ri-buildare.
  - Se master e' avanzato oltre quella run -> lancia il workflow ESISTENTE (workflow_dispatch o push), NON crearne uno nuovo.
- Installer NON firmato OK per il test (SmartScreen avvisa -> "Ulteriori info -> Esegui comunque"). NIENTE code signing ora.

## FASE 3 — ESITO
- Se artefatto pronto: URL run + link artifact (.msi/.exe) + commit hash + dimensione.
- Secure storage Windows: OK (path:riga del backend) oppure KO (blocco, cosa servirebbe).
- BLOCCO ESTERNO da nominare: "installabile e avviabile su PC Windows reale" richiede hardware/VM Windows
  che non abbiamo -> BLOCKED-ON: PC o VM Windows (founder). Non raggiungibile in autonomia da macOS.
- Se un build viene lanciato e fallisce: step + messaggio d'errore esatto dal log + causa probabile,
  senza eseguire il fix. Questo e' il blocco "macOS-locked" finalmente nominato con precisione.

## NON FARE
Non toccare catena revenue, magazzino, sales agent. Solo installer/attivazione Windows.

## ADDENDUM (read-only, idempotenti)
A1 — PROVENIENZA SHA: per la run 27217198619, estrai il commit SHA buildato e
verifica che sia su origin/master con `git branch -r --contains <sha>`.
"Verde da master" è un'AFFERMAZIONE dell'handoff, da provare con l'SHA, non da
assumere. Riporta: SHA della run | contiene origin/master sì/no | quanti commit
master è indietro/avanti.

A2 — SECURE STORAGE, STATO REALE (non solo esistenza): per il backend licenza
Windows, distingui esplicitamente:
  - 📝 il codice DPAPI/Credential Manager esiste? (path:riga)
  - 🧪 esiste un test che lo ESERCITA su Windows (non su macOS)? (path:riga o "NESSUNO")
Se il codice esiste ma nessun test lo esercita su Windows → dichiara
"WINDOWS-UNTESTED", non "OK". È lo scenario peggiore: sembra giusto e non ha mai
girato sull'OS dei clienti.

## VINCOLO OPERATIVO
git/gh/lettura log CI richiedono Bash. Bypass context-gate VOS: CONFERMATO ma SOLO questa sessione
(riavvii senza, dopo). La regola dura "nessun file nuovo / nessun refactor" resta intatta: con Bash
sbloccato e' l'unico vincolo che tiene CC sul deliverable invece che a gironzolare nel codice.
La FASE 1 read-only (Read/Grep) e' eseguibile anche senza Bash.
