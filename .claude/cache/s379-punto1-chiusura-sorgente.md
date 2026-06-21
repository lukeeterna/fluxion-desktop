# PUNTO 1 — chiusura per sorgente (S379, read-only, main only, ZERO fix, ZERO commit)

## ⚠️ La realtà del repo smentisce l'assunzione centrale della procedura — riporto il FATTO
La procedura diceva: «§10 era difettosa: confrontava un fingerprint SALVATO con il
runtime, ma `machine_id` in `license_cache` è VUOTO → quel confronto darebbe != per
artefatto → falso HARDWARE_MISMATCH».

**Falso secondo il sorgente.** Il confronto NON legge `machine_id`. Vince la realtà.

## STEP 1 — verbatim + verdetto (file: `src-tauri/src/commands/license_ed25519.rs`)

### a) Quale campo è il lato SALVATO del confronto?
La colonna dedicata **`fingerprint`** di `license_cache`, NON `machine_id`
(`machine_id` non è nemmeno SELEZIONATO da questa funzione).
- Load (`:484`): `SELECT fingerprint, tier, status, … FROM license_cache WHERE id = 1`
- Bind (`:498`): la 1ª colonna `fingerprint` → variabile `fp`
- Confronto (`:544`): `if tier != LicenseTier::Trial && fp != fingerprint`  ← `fp`=salvato, `fingerprint`=`generate_fingerprint()` runtime (`:463`)
- Stesso confronto per il codice (`:558`): `} else if fp != fingerprint { "HARDWARE_MISMATCH" }`

### b) Quel campo è popolato o vuoto nel DB?
**POPOLATO.** Da S378 (lettura DB Windows pagante): colonna `fingerprint` =
`343865fe7623b3063a50941e55e68e29`. Il campo VUOTO è `machine_id` — ma `machine_id`
NON entra in questo confronto. L'attivazione popola `fingerprint` col fingerprint
runtime catturato all'attivazione:
- upsert (`:415` / `:418` / `:420`): colonna `fingerprint` = `excluded.fingerprint`
- bind (`:436`): `.bind(&license.hardware_fingerprint)`
- origine (`:786`): `hardware_fingerprint: generate_fingerprint()`

### c) Il confronto `fp != fingerprint` è GUARDATO quando il salvato è vuoto/null?
**NO guardia-su-vuoto.** L'unica guardia a `:544` è `tier != LicenseTier::Trial`
(scatta solo per licenze attivate, non trial). È un confronto stringa diretto fra
due fingerprint. → La domanda "mismatch inerte quando il salvato è vuoto" è **N/A**:
il salvato NON è vuoto, è un fingerprint reale (`343865fe…`).

## Verdetto: PUNTO 1 CHIUSO PER SORGENTE (+ S378), ma per una ragione diversa da quella ipotizzata
Il sorgente NON chiude Punto 1 con una "guardia contro il vuoto" (non esiste, e non
serve perché il salvato non è vuoto). Il sorgente RIDUCE Punto 1 esattamente alla
domanda di stabilità temporale del fingerprint:

  HARDWARE_MISMATCH su Base attiva scatta **se e solo se**
  `generate_fingerprint()`@attivazione  ≠  `generate_fingerprint()`@avvio.

Ed è precisamente ciò che **S378 ha verificato**: ricostruito l'hash dai valori
hardware LIVE della macchina pagante → `343865fe…` == colonna `fingerprint` salvata.
Quindi `fp != fingerprint` = **false** → niente mismatch → `is_valid=true` → `active`
(coerente con S376: se non fosse uguale non sarebbe mai stata active — nessuna
contraddizione).

**Corollario importante**: il metodo S378 NON era difettoso. Confrontava la colonna
`fingerprint` (popolata), che è il campo GIUSTO. L'assunzione "§10 confrontava
machine_id vuoto" è errata: machine_id non è coinvolto.

## Riconferma legacy orfano (richiesta in coda)
La sola sorgente di re-prompt è il sistema licenza LEGACY (`use-license.ts` →
`get_license_status`, `useLicenseGate`/`needsActivation` `:114/:125`,
`LicenseStatus.tsx`/`LicenseDialog.tsx`). Grep: `useLicenseGate`/`needsActivation`
definiti SOLO in `use-license.ts`; `LicenseStatus`/`LicenseDialog` si importano fra
loro ma **nessun `App.tsx`/page li monta** → orfano (coerente §5). L'attivo è
`use-license-ed25519.ts` → `get_license_status_ed25519` (la funzione analizzata sopra).

## Conclusione
**Punto 1 = chiuso per sorgente + S378.** Sulla macchina pagante un eventuale
re-prompt NON è il fingerprint (== verificato): è il path legacy orfano o una build
vecchia. Nessun ramo `!=` (node-lock) si verifica con `fingerprint` popolato e
stabile. Niente Windows necessario. Node-lock Q4/Q6 NON toccato. Zero fix, zero
commit, zero subagent.
