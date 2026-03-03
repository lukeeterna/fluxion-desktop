---
phase: sdi-aruba-multi-provider
plan: 04
type: execute
wave: 3
depends_on:
  - sdi-aruba-01
  - sdi-aruba-02
  - sdi-aruba-03
files_modified: []
autonomous: false

must_haves:
  truths:
    - "npm run type-check restituisce 0 errori"
    - "cargo check su iMac restituisce 0 errori"
    - "Il commit atomico è presente con il messaggio feat(fatture): SDI multi-provider"
    - "L'utente ha verificato visivamente la selezione provider in Impostazioni"
  artifacts:
    - path: "src-tauri/migrations/029_sdi_multi_provider.sql"
      provides: "Migration SQL verificata e presente"
      contains: "sdi_provider"
    - path: "src/components/impostazioni/SdiProviderSettings.tsx"
      provides: "Componente UI verificato"
      exports: ["SdiProviderSettings"]
  key_links:
    - from: "npm run type-check"
      to: "0 errori TypeScript"
      via: "tsc --noEmit"
      pattern: "error TS"
    - from: "commit Git"
      to: "feat(fatture): SDI multi-provider"
      via: "git commit"
      pattern: "SDI multi-provider"
---

<objective>
Verificare l'intera implementazione SDI multi-provider: TypeScript check, cargo check remoto su iMac,
verifica manuale UI provider switch, e commit atomico finale con messaggio standardizzato.

Purpose: Nessun task è completato finché non è verificato. Il Rust build NON va mai eseguito
su MacBook — solo su iMac via SSH. Il type-check TypeScript è il gate di qualità principale su MacBook.

Output: Commit atomico `feat(fatture): SDI multi-provider — Aruba + OpenAPI + Fattura24 retrocompat`
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/sdi-aruba-multi-provider/
@.planning/phases/sdi-aruba-multi-provider/sdi-aruba-01-SUMMARY.md
@.planning/phases/sdi-aruba-multi-provider/sdi-aruba-02-SUMMARY.md
@.planning/phases/sdi-aruba-multi-provider/sdi-aruba-03-SUMMARY.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: npm run type-check — 0 errori TypeScript</name>
  <files></files>
  <action>
Esegui il type check TypeScript:
```bash
cd /Volumes/MontereyT7/FLUXION && npm run type-check
```

Se ci sono errori TypeScript:
1. Leggi il messaggio di errore completo
2. Identifica il file e la riga
3. Correggi l'errore nel file appropriato
4. Riesegui type-check
5. Ripeti finché 0 errori

Errori tipici attesi e soluzioni:
- `Property 'sdi_provider' does not exist on type 'ImpostazioniFatturazione'` → verifica che src/types/fatture.ts abbia il campo
- `Argument of type ... is not assignable` in use-fatture.ts → verifica il mapping esplicito del hook
- `Cannot find module` → verifica import path in Impostazioni.tsx e SdiProviderSettings.tsx

NON procedere al Task 2 se type-check ha errori.
  </action>
  <verify>
```bash
cd /Volumes/MontereyT7/FLUXION && npm run type-check 2>&1 | tail -5
# Output atteso: "Found 0 errors." oppure nessun output di errore
```
  </verify>
  <done>
`npm run type-check` completa con 0 errori TypeScript.
  </done>
</task>

<task type="auto">
  <name>Task 2: cargo check su iMac via SSH</name>
  <files></files>
  <action>
Esegui cargo check su iMac via SSH (NON su MacBook — Rust build SOLO su iMac):

```bash
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && git pull origin master && source ~/.cargo/env && cargo check 2>&1 | tail -20"
```

Se cargo check fallisce con errori di compilazione Rust:
1. Leggi l'errore (es. "cannot find trait SdiProvider" o "missing field sdi_provider")
2. Identifica la causa (campo mancante in struct, import mancante, tipo errato)
3. Correggi su MacBook nel file src-tauri/src/commands/fatture.rs o Cargo.toml
4. git push origin master
5. Riprova cargo check su iMac

Errori comuni Rust e soluzioni:
- `no field sdi_provider on type ImpostazioniFatturazione` → verifica che il campo sia stato aggiunto alla struct nel Plan 01
- `cannot find macro async_trait` → verifica `async-trait = "0.1"` in Cargo.toml E `use async_trait::async_trait;` nel file
- `cannot find type base64` → verifica `base64 = "0.22"` in Cargo.toml
- `error[E0277]: the trait bound ... is not satisfied` → tipicamente problema con async_trait macro

Se SSH non è disponibile (iMac offline), skippa questo task e nota nel summary che cargo check
richiede verifica manuale al prossimo avvio iMac.
  </action>
  <verify>
```bash
# Se iMac disponibile:
ssh imac "cd '/Volumes/MacSSD - Dati/fluxion' && source ~/.cargo/env && cargo check 2>&1 | grep -E 'error|warning.*unused' | head -10"
# Atteso: nessun output 'error[E' — warning sono accettabili

# Se iMac non disponibile:
echo "iMac offline — cargo check pendente. Verificare al prossimo avvio."
```
  </verify>
  <done>
`cargo check` su iMac completa senza errori di compilazione.
Oppure: iMac offline documentato nel summary con cargo check da eseguire al prossimo avvio.
  </done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <what-built>
UI Impostazioni con sezione "Integrazione SDI" che mostra 3 provider selezionabili
(Aruba €29.90/anno, OpenAPI €0.025/fattura, Fattura24 legacy).
Clicking su un provider card lo evidenzia con bordo cyan e mostra il campo API Key corrispondente.
  </what-built>
  <how-to-verify>
1. Avvia l'app: `npm run dev` nella cartella FLUXION (apri nel browser Vite dev server)
2. Naviga su Impostazioni (menu laterale)
3. Scendi fino alla sezione "Integrazione SDI"
4. Verifica che appaiano 3 card provider (Aruba / OpenAPI.com / Fattura24)
5. Click su "Aruba Fatturazione Elettronica" → bordo cyan + campo "API Key Aruba FE"
6. Click su "OpenAPI.com SDI" → bordo cyan + campo "API Key OpenAPI.com"
7. Click su "Fattura24" → bordo cyan + campo "API Key Fattura24"
8. Inserisci un testo nel campo API Key e click "Salva Impostazioni SDI"
9. Verifica che appaia un toast "Impostazioni SDI salvate" (verde, in basso)
10. Ricarica la pagina — il provider e il valore API Key devono persistere
  </how-to-verify>
  <resume-signal>
Scrivi "approved" se tutto funziona correttamente.
Scrivi "issues: [descrizione]" se c'è qualcosa da correggere.
  </resume-signal>
</task>

<task type="auto">
  <name>Task 4: Commit atomico finale</name>
  <files></files>
  <action>
Dopo approvazione human-verify, esegui il commit atomico:

```bash
cd /Volumes/MontereyT7/FLUXION

# Verifica status
git status

# Stage tutti i file modificati della fase
git add \
  src-tauri/migrations/029_sdi_multi_provider.sql \
  src-tauri/src/commands/fatture.rs \
  src-tauri/Cargo.toml \
  src/types/fatture.ts \
  src/hooks/use-fatture.ts \
  src/components/impostazioni/SdiProviderSettings.tsx \
  src/pages/Impostazioni.tsx

# Verifica che NON ci siano file .env o API keys staged
git diff --cached --name-only

# Commit atomico con messaggio standardizzato
git commit -m "feat(fatture): SDI multi-provider — Aruba + OpenAPI + Fattura24 retrocompat

- Migration 029: sdi_provider + aruba_api_key + openapi_api_key
- Rust: trait SdiProvider con 3 impl + factory sdi_provider_factory
- update_impostazioni_fatturazione: accetta parametri multi-provider
- UI: SdiProviderSettings — selezione provider con API key dinamica
- TypeScript: ImpostazioniFatturazione aggiornato con 3 nuovi campi
- Risparmio potenziale: da €96-192/anno (Fattura24) a €29.90/anno (Aruba)
- Retrocompat: DEFAULT 'fattura24' per clienti esistenti"
```

NON usare `--no-verify` — i pre-commit hook devono passare.
Se un hook fallisce, correggi il problema (type-check o ESLint) e ricommit.

Dopo il commit, push su origin:
```bash
git push origin master
```
  </action>
  <verify>
```bash
git log --oneline -3
# Il primo commit deve contenere "feat(fatture): SDI multi-provider"

git show --stat HEAD | head -15
# Deve mostrare i 7 file modificati/creati
```
  </verify>
  <done>
Commit con hash presente nel log con messaggio "feat(fatture): SDI multi-provider".
7 file inclusi nel commit: migration SQL, fatture.rs, Cargo.toml, fatture.ts, use-fatture.ts,
SdiProviderSettings.tsx, Impostazioni.tsx.
Push su origin master completato.
  </done>
</task>

</tasks>

<verification>
Checklist finale fase SDI multi-provider:
1. [ ] `npm run type-check` → 0 errori TypeScript
2. [ ] `cargo check` su iMac → 0 errori Rust (o documentato come pending)
3. [ ] UI: 3 provider card visibili e selezionabili
4. [ ] UI: campo API key cambia in base al provider selezionato
5. [ ] UI: salvataggio persiste provider e API key nel DB
6. [ ] Commit con messaggio standardizzato presente in git log
7. [ ] Push su origin master completato
8. [ ] Nessuna API key committata nel codice
</verification>

<success_criteria>
- `npm run type-check` → 0 errori (OBBLIGATORIO)
- `cargo check` iMac → 0 errori (o pending se iMac offline)
- Human verify: provider switch UI funzionante e persistente
- Commit atomico con messaggio `feat(fatture): SDI multi-provider — Aruba + OpenAPI + Fattura24 retrocompat`
- Git push origin master completato
</success_criteria>

<output>
Dopo completamento, crea `.planning/phases/sdi-aruba-multi-provider/sdi-aruba-04-SUMMARY.md`

Aggiorna anche HANDOFF.md e MEMORY.md con:
- Stato: SDI multi-provider completato
- Migration 029 applicata
- Provider Aruba attivabile da Impostazioni → Integrazione SDI
</output>
