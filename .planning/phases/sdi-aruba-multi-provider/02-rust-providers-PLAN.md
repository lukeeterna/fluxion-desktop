---
phase: sdi-aruba-multi-provider
plan: 02
type: execute
wave: 1
depends_on: []
files_modified:
  - src-tauri/src/commands/fatture.rs
  - src-tauri/Cargo.toml
autonomous: true

must_haves:
  truths:
    - "update_impostazioni_fatturazione accetta i 3 nuovi parametri SDI provider"
    - "Il comando get_impostazioni_fatturazione restituisce sdi_provider, aruba_api_key, openapi_api_key"
    - "Cargo.toml contiene async-trait e base64 nelle dependencies"
  artifacts:
    - path: "src-tauri/src/commands/fatture.rs"
      provides: "update_impostazioni_fatturazione con parametri multi-provider"
      contains: "sdi_provider: String"
    - path: "src-tauri/Cargo.toml"
      provides: "Dipendenze async-trait e base64"
      contains: "async-trait"
  key_links:
    - from: "update_impostazioni_fatturazione (Rust)"
      to: "impostazioni_fatturazione DB"
      via: "UPDATE SQL con bind sdi_provider, aruba_api_key, openapi_api_key"
      pattern: "sdi_provider.*=.*\\?"
    - from: "TypeScript useUpdateImpostazioniFatturazione"
      to: "update_impostazioni_fatturazione Tauri command"
      via: "invoke('update_impostazioni_fatturazione', { sdi_provider, aruba_api_key, openapi_api_key })"
      pattern: "sdi_provider.*aruba_api_key.*openapi_api_key"
---

<objective>
Aggiornare il comando Rust `update_impostazioni_fatturazione` per accettare e persistere i 3 nuovi
parametri SDI (sdi_provider, aruba_api_key, openapi_api_key). Aggiornare anche `Cargo.toml` con
le dipendenze async-trait e base64 necessarie per il trait SdiProvider del Plan 01.

Purpose: Senza questo aggiornamento, il frontend non può salvare la scelta provider.
Il comando `get_impostazioni_fatturazione` funziona già (SELECT *) ma `update` deve essere
esteso con i 3 nuovi parametri.

Output: Command `update_impostazioni_fatturazione` aggiornato con 3 parametri aggiuntivi +
Cargo.toml con dipendenze corrette.
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/sdi-aruba-multi-provider/

# File chiave
@src-tauri/src/commands/fatture.rs
@src-tauri/Cargo.toml
@.claude/rules/rust-backend.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Cargo.toml — aggiungi async-trait e base64</name>
  <files>src-tauri/Cargo.toml</files>
  <action>
Leggi `src-tauri/Cargo.toml` e aggiungi nella sezione `[dependencies]` le righe mancanti:

```toml
async-trait = "0.1"
base64 = "0.22"
```

IMPORTANTE: controlla prima se esistono già (grep "async-trait\|base64"). Se esistono, non duplicarli.
`reqwest` deve già essere presente con la feature `json` — verificarlo. Se `reqwest` è presente
senza `features = ["json"]`, aggiungere quella feature.

Esempio configurazione attesa nella sezione [dependencies]:
```toml
reqwest = { version = "0.12", features = ["json"] }
async-trait = "0.1"
base64 = "0.22"
serde_json = "1"
```

serde_json è necessario per i payload JSON nei provider Aruba e OpenAPI. Se non presente, aggiungilo.
  </action>
  <verify>
```bash
grep -n "async-trait\|base64\|serde_json\|reqwest" src-tauri/Cargo.toml
# Tutte e 4 le righe devono essere presenti
```
  </verify>
  <done>
Cargo.toml ha async-trait, base64, serde_json e reqwest con feature json nelle dependencies.
  </done>
</task>

<task type="auto">
  <name>Task 2: Rust — update_impostazioni_fatturazione con parametri multi-provider</name>
  <files>src-tauri/src/commands/fatture.rs</files>
  <action>
Modifica la funzione `update_impostazioni_fatturazione` in `src-tauri/src/commands/fatture.rs`
per aggiungere 3 nuovi parametri e aggiornarli nel DB.

La firma attuale ha questi parametri (tra gli altri):
```rust
fattura24_api_key: Option<String>,
```

**Aggiungi dopo `fattura24_api_key`** questi 3 parametri:
```rust
sdi_provider: Option<String>,
aruba_api_key: Option<String>,
openapi_api_key: Option<String>,
```

**Aggiorna il body SQL** della UPDATE per includere i 3 nuovi campi:
Nella query SQL dell'UPDATE, aggiungi PRIMA di `updated_at = datetime('now')`:
```sql
            sdi_provider = COALESCE(?, sdi_provider),
            aruba_api_key = ?,
            openapi_api_key = ?,
```

**Aggiorna i bind** nella catena `.bind()` dopo il bind di `fattura24_api_key`:
```rust
.bind(&sdi_provider)
.bind(&aruba_api_key)
.bind(&openapi_api_key)
```

**Regola COALESCE**: `sdi_provider` usa `COALESCE(?, sdi_provider)` per non sovrascrivere
il provider con NULL se il frontend invia None (retrocompat). `aruba_api_key` e `openapi_api_key`
possono essere NULL (permettono di cancellare la key).

La funzione rimane marcata `#[allow(clippy::too_many_arguments)]` che è già presente.

Verifica che il tipo `ImpostazioniFatturazione` usato come return type abbia i nuovi campi —
questo è stato fatto nel Plan 01. Se il Plan 01 non è ancora eseguito, assicurarsi che
la struct abbia i campi corretti.
  </action>
  <verify>
```bash
# Verifica parametri nella firma della funzione
grep -A 30 "pub async fn update_impostazioni_fatturazione" src-tauri/src/commands/fatture.rs | grep -E "sdi_provider|aruba_api_key|openapi_api_key"
# Deve mostrare 3 righe

# Verifica bind nella query
grep -n "sdi_provider\|aruba_api_key\|openapi_api_key" src-tauri/src/commands/fatture.rs | grep -v "struct\|pub sdi\|pub aruba\|pub openapi"
# Deve mostrare le righe con bind e SQL
```
  </verify>
  <done>
- Funzione update_impostazioni_fatturazione ha 3 parametri aggiuntivi: sdi_provider, aruba_api_key, openapi_api_key
- SQL UPDATE include le 3 nuove colonne con COALESCE per sdi_provider
- Catena .bind() include i 3 nuovi valori nell'ordine corretto
  </done>
</task>

</tasks>

<verification>
Verifica su MacBook (NO Rust build):
1. `grep -c "unwrap()" src-tauri/src/commands/fatture.rs` — non deve aumentare
2. `grep "async-trait\|base64" src-tauri/Cargo.toml` — entrambe presenti
3. `grep -n "sdi_provider\|aruba_api_key\|openapi_api_key" src-tauri/src/commands/fatture.rs | wc -l` — almeno 12 occorrenze (struct + update firma + SQL + bind x3)
</verification>

<success_criteria>
- Cargo.toml: async-trait, base64, serde_json presenti nelle dependencies
- update_impostazioni_fatturazione: accetta sdi_provider, aruba_api_key, openapi_api_key
- SQL UPDATE: persistisce correttamente i 3 nuovi campi
- Nessun unwrap() nuovo introdotto
</success_criteria>

<output>
Dopo completamento, crea `.planning/phases/sdi-aruba-multi-provider/sdi-aruba-02-SUMMARY.md`
</output>
