---
phase: sdi-aruba-multi-provider
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src-tauri/migrations/029_sdi_multi_provider.sql
  - src-tauri/src/commands/fatture.rs
autonomous: true

must_haves:
  truths:
    - "La tabella impostazioni_fatturazione ha colonne sdi_provider, aruba_api_key, openapi_api_key"
    - "Il trait SdiProvider è definito in fatture.rs con metodo asincrono invia_fattura"
    - "Esistono tre struct che implementano SdiProvider: ArubaProvider, OpenApiProvider, Fattura24Provider"
    - "La funzione factory sdi_provider_factory legge sdi_provider dal DB e restituisce il provider corretto"
  artifacts:
    - path: "src-tauri/migrations/029_sdi_multi_provider.sql"
      provides: "Migration SQL con tre nuove colonne in impostazioni_fatturazione"
      contains: "ALTER TABLE impostazioni_fatturazione ADD COLUMN sdi_provider"
    - path: "src-tauri/src/commands/fatture.rs"
      provides: "Trait SdiProvider + 3 implementazioni + factory function"
      exports: ["SdiProvider", "ArubaProvider", "OpenApiProvider", "Fattura24Provider"]
  key_links:
    - from: "invia_sdi_fattura command"
      to: "sdi_provider_factory"
      via: "chiamata diretta nella funzione invia_sdi_fattura"
      pattern: "sdi_provider_factory"
    - from: "sdi_provider_factory"
      to: "impostazioni_fatturazione.sdi_provider"
      via: "query SQL SELECT sdi_provider FROM impostazioni_fatturazione"
      pattern: "sdi_provider.*FROM impostazioni_fatturazione"
---

<objective>
Creare la migration SQL 029 che aggiunge il supporto multi-provider a impostazioni_fatturazione, e
refactoring del comando Rust invia_sdi_fattura usando il trait pattern SdiProvider con tre implementazioni:
Aruba (primario), OpenAPI.com (secondario), Fattura24 (retrocompat).

Purpose: Sblocca la scelta provider per l'utente e riduce costo SDI da €96-192/anno (Fattura24) a
€29.90/anno (Aruba). La migration deve essere applicata PRIMA dell'implementazione Rust.

Output: Migration 029 applicata + trait SdiProvider con 3 impl + command invia_sdi_fattura refactored
per usare il provider corretto basandosi su impostazioni_fatturazione.sdi_provider.
</objective>

<execution_context>
@./.claude/get-shit-done/workflows/execute-plan.md
@./.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/sdi-aruba-multi-provider/

# File esistenti chiave
@src-tauri/migrations/026_impostazioni_sdi_key.sql
@src-tauri/src/commands/fatture.rs
@.claude/cache/agents/sdi-free-research.md

# Regole Rust critiche
@.claude/rules/rust-backend.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Migration SQL 029 — colonne multi-provider</name>
  <files>src-tauri/migrations/029_sdi_multi_provider.sql</files>
  <action>
Crea il file `src-tauri/migrations/029_sdi_multi_provider.sql` con il seguente contenuto esatto:

```sql
-- ═══════════════════════════════════════════════════════════════
-- MIGRATION 029: SDI Multi-Provider
-- Aggiunge supporto Aruba FE (primario) + OpenAPI.com (secondario)
-- Mantiene Fattura24 per retrocompatibilità
-- Data: 2026-03-03
-- ═══════════════════════════════════════════════════════════════

-- Provider SDI attivo (default: fattura24 per retrocompat)
ALTER TABLE impostazioni_fatturazione ADD COLUMN sdi_provider TEXT NOT NULL DEFAULT 'fattura24';

-- API key Aruba Fatturazione Elettronica
-- Ottenibile da: fatturazioneelettronica.aruba.it → Account → API
ALTER TABLE impostazioni_fatturazione ADD COLUMN aruba_api_key TEXT;

-- API key OpenAPI.com SDI
-- Ottenibile da: console.openapi.com → API Keys
ALTER TABLE impostazioni_fatturazione ADD COLUMN openapi_api_key TEXT;

-- ═══════════════════════════════════════════════════════════════
-- VALIDAZIONE
-- ═══════════════════════════════════════════════════════════════
-- SELECT id, sdi_provider, aruba_api_key, openapi_api_key
-- FROM impostazioni_fatturazione WHERE id = 'default';
-- Expected: sdi_provider = 'fattura24', api keys = NULL
```

Valori ammessi per sdi_provider: 'fattura24', 'aruba', 'openapi'.
Il DEFAULT 'fattura24' garantisce retrocompatibilità — clienti esistenti non rompono nulla.
  </action>
  <verify>
```bash
# Verifica che il file esista e abbia il contenuto corretto
cat src-tauri/migrations/029_sdi_multi_provider.sql
# Deve mostrare 3 ALTER TABLE con sdi_provider, aruba_api_key, openapi_api_key
```
  </verify>
  <done>
File 029_sdi_multi_provider.sql esiste con esattamente 3 colonne aggiunte:
- sdi_provider TEXT NOT NULL DEFAULT 'fattura24'
- aruba_api_key TEXT (nullable)
- openapi_api_key TEXT (nullable)
  </done>
</task>

<task type="auto">
  <name>Task 2: Rust — Trait SdiProvider + 3 implementazioni + refactoring invia_sdi_fattura</name>
  <files>src-tauri/src/commands/fatture.rs</files>
  <action>
Modifica `src-tauri/src/commands/fatture.rs` con le seguenti operazioni atomiche:

**STEP A — Aggiorna struct ImpostazioniFatturazione** (aggiunge 3 nuovi campi dopo fattura24_api_key):
```rust
pub struct ImpostazioniFatturazione {
    // ... campi esistenti invariati ...
    pub fattura24_api_key: Option<String>,
    // NUOVI campi migration 029:
    pub sdi_provider: String,          // 'fattura24' | 'aruba' | 'openapi'
    pub aruba_api_key: Option<String>,
    pub openapi_api_key: Option<String>,
}
```

**STEP B — Aggiunge trait SdiProvider e 3 implementazioni** (inserire PRIMA della sezione "Impostazioni Fatturazione"):
```rust
// ───────────────────────────────────────────────────────────────────
// SDI Multi-Provider Trait
// ───────────────────────────────────────────────────────────────────

/// Risposta normalizzata da qualsiasi provider SDI
#[derive(Debug)]
struct SdiInvioRisultato {
    id_trasmissione: String,
}

/// Trait asincrono per invio SDI — ogni provider implementa questo contratto
#[async_trait::async_trait]
trait SdiProvider: Send + Sync {
    async fn invia_fattura(
        &self,
        xml_content: &str,
        xml_filename: &str,
    ) -> Result<SdiInvioRisultato, String>;
}

// ─── Provider Fattura24 (retrocompat) ───────────────────────────────

struct Fattura24Provider {
    api_key: String,
}

#[async_trait::async_trait]
impl SdiProvider for Fattura24Provider {
    async fn invia_fattura(
        &self,
        xml_content: &str,
        _xml_filename: &str,
    ) -> Result<SdiInvioRisultato, String> {
        let client = reqwest::Client::new();
        let params = [
            ("apiKey", self.api_key.as_str()),
            ("xml", xml_content),
            ("showPdf", "0"),
        ];
        let response = client
            .post("https://api.fattura24.com/api/v0/SaveInvoice")
            .header("Content-Type", "application/x-www-form-urlencoded")
            .form(&params)
            .send()
            .await
            .map_err(|e| format!("Errore connessione Fattura24: {}", e))?;

        let body: Fattura24Response = response
            .json()
            .await
            .map_err(|e| format!("Errore parsing risposta Fattura24: {}", e))?;

        if body.error != "0" {
            return Err(format!("Fattura24 errore: {}", body.description));
        }
        Ok(SdiInvioRisultato {
            id_trasmissione: body.filename.unwrap_or_default(),
        })
    }
}

// ─── Provider Aruba FE (primario) ───────────────────────────────────

struct ArubaProvider {
    api_key: String,
}

#[async_trait::async_trait]
impl SdiProvider for ArubaProvider {
    async fn invia_fattura(
        &self,
        xml_content: &str,
        xml_filename: &str,
    ) -> Result<SdiInvioRisultato, String> {
        // Aruba REST API: POST /fe/v1/documents
        // Auth: Bearer token (api_key)
        // Body: multipart/form-data con file XML
        // Ref: https://fatturazioneelettronica.aruba.it/apidoc/docs.html
        let client = reqwest::Client::new();

        // Base64-encode XML per invio JSON (alternativa a multipart)
        use base64::{Engine as _, engine::general_purpose};
        let xml_b64 = general_purpose::STANDARD.encode(xml_content.as_bytes());

        let payload = serde_json::json!({
            "filename": xml_filename,
            "file": xml_b64,
            "invoice_type": "FPR12"
        });

        let response = client
            .post("https://ews.aruba.it/ArubaSMSSender/services/FEService")
            .bearer_auth(&self.api_key)
            .json(&payload)
            .send()
            .await
            .map_err(|e| format!("Errore connessione Aruba FE: {}", e))?;

        if !response.status().is_success() {
            let status = response.status().as_u16();
            let body = response.text().await.unwrap_or_default();
            return Err(format!("Aruba FE errore HTTP {}: {}", status, body));
        }

        let body: serde_json::Value = response
            .json()
            .await
            .map_err(|e| format!("Errore parsing risposta Aruba FE: {}", e))?;

        // Aruba restituisce un identificativo del documento inviato
        let id = body
            .get("id")
            .or_else(|| body.get("documentId"))
            .and_then(|v| v.as_str())
            .map(|s| s.to_string())
            .unwrap_or_else(|| format!("ARUBA-{}", xml_filename));

        Ok(SdiInvioRisultato { id_trasmissione: id })
    }
}

// ─── Provider OpenAPI.com (secondario) ──────────────────────────────

struct OpenApiProvider {
    api_key: String,
}

#[async_trait::async_trait]
impl SdiProvider for OpenApiProvider {
    async fn invia_fattura(
        &self,
        xml_content: &str,
        xml_filename: &str,
    ) -> Result<SdiInvioRisultato, String> {
        // OpenAPI.com SDI REST API
        // POST https://api.openapi.com/efatt/v1/send
        // Header: Authorization: Bearer {api_key}
        // Ref: https://openapi.com/products/italian-electronic-invoicing
        let client = reqwest::Client::new();

        use base64::{Engine as _, engine::general_purpose};
        let xml_b64 = general_purpose::STANDARD.encode(xml_content.as_bytes());

        let payload = serde_json::json!({
            "filename": xml_filename,
            "content": xml_b64
        });

        let response = client
            .post("https://api.openapi.com/efatt/v1/send")
            .bearer_auth(&self.api_key)
            .json(&payload)
            .send()
            .await
            .map_err(|e| format!("Errore connessione OpenAPI.com SDI: {}", e))?;

        if !response.status().is_success() {
            let status = response.status().as_u16();
            let body = response.text().await.unwrap_or_default();
            return Err(format!("OpenAPI.com SDI errore HTTP {}: {}", status, body));
        }

        let body: serde_json::Value = response
            .json()
            .await
            .map_err(|e| format!("Errore parsing risposta OpenAPI.com: {}", e))?;

        let id = body
            .get("id")
            .or_else(|| body.get("receipt_id"))
            .and_then(|v| v.as_str())
            .map(|s| s.to_string())
            .unwrap_or_else(|| format!("OPENAPI-{}", xml_filename));

        Ok(SdiInvioRisultato { id_trasmissione: id })
    }
}

// ─── Factory ────────────────────────────────────────────────────────

/// Legge sdi_provider e la relativa api_key dal DB, restituisce il provider corretto.
/// Errore se il provider attivo non ha API key configurata.
async fn sdi_provider_factory(
    pool: &SqlitePool,
) -> Result<Box<dyn SdiProvider>, String> {
    let row: (String, Option<String>, Option<String>, Option<String>) = sqlx::query_as(
        "SELECT sdi_provider, fattura24_api_key, aruba_api_key, openapi_api_key
         FROM impostazioni_fatturazione WHERE id = 'default'",
    )
    .fetch_one(pool)
    .await
    .map_err(|e| format!("Errore lettura impostazioni SDI: {}", e))?;

    let (provider, f24_key, aruba_key, openapi_key) = row;

    match provider.as_str() {
        "aruba" => {
            let key = aruba_key.ok_or_else(|| {
                "API key Aruba non configurata. Configurala in Impostazioni > Integrazione SDI."
                    .to_string()
            })?;
            Ok(Box::new(ArubaProvider { api_key: key }))
        }
        "openapi" => {
            let key = openapi_key.ok_or_else(|| {
                "API key OpenAPI.com non configurata. Configurala in Impostazioni > Integrazione SDI."
                    .to_string()
            })?;
            Ok(Box::new(OpenApiProvider { api_key: key }))
        }
        _ => {
            // Default: fattura24 (retrocompat)
            let key = f24_key.ok_or_else(|| {
                "API key Fattura24 non configurata. Configurala in Impostazioni > Integrazione SDI."
                    .to_string()
            })?;
            Ok(Box::new(Fattura24Provider { api_key: key }))
        }
    }
}
```

**STEP C — Refactoring invia_sdi_fattura** (sostituisce il body esistente del comando):

Sostituisci l'intera funzione `invia_sdi_fattura` (da riga ~1351 a ~1439) con:

```rust
#[tauri::command]
pub async fn invia_sdi_fattura(
    pool: State<'_, SqlitePool>,
    fattura_id: String,
) -> Result<Fattura, String> {
    // 0. Seleziona provider corretto in base a impostazioni
    let provider = sdi_provider_factory(pool.inner()).await?;

    // 1. Legge fattura dal DB
    let fattura =
        sqlx::query_as::<_, Fattura>("SELECT * FROM fatture WHERE id = ? AND deleted_at IS NULL")
            .bind(&fattura_id)
            .fetch_one(pool.inner())
            .await
            .map_err(|e| format!("Fattura non trovata: {}", e))?;

    // 2. Verifica stato 'emessa'
    if fattura.stato != "emessa" {
        return Err(
            "Solo le fatture in stato 'emessa' possono essere inviate allo SDI".to_string(),
        );
    }

    // 3. Verifica presenza xml_content e xml_filename
    let xml_content = fattura
        .xml_content
        .ok_or_else(|| "XML non generato. Emetti prima la fattura.".to_string())?;

    let xml_filename = fattura
        .xml_filename
        .unwrap_or_else(|| format!("fattura_{}.xml", &fattura_id[..8]));

    // 4. Invio tramite provider selezionato
    let risultato = provider.invia_fattura(&xml_content, &xml_filename).await?;

    // 5. Aggiorna DB con dati SDI
    sqlx::query(
        r#"
        UPDATE fatture SET
            stato = 'inviata_sdi',
            sdi_id_trasmissione = ?,
            sdi_data_invio = datetime('now'),
            sdi_esito = 'MC',
            updated_at = datetime('now')
        WHERE id = ?
        "#,
    )
    .bind(&risultato.id_trasmissione)
    .bind(&fattura_id)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Errore aggiornamento fattura dopo invio SDI: {}", e))?;

    sqlx::query_as::<_, Fattura>("SELECT * FROM fatture WHERE id = ?")
        .bind(&fattura_id)
        .fetch_one(pool.inner())
        .await
        .map_err(|e| format!("Errore recupero fattura: {}", e))
}
```

**Regole Rust obbligatorie:**
- Zero `unwrap()` bare — usare `.map_err(|e| format!(...))` o `.ok_or_else(||...)`
- Zero `any` (non applicabile in Rust ma ricordare semantica)
- Il trait object `Box<dyn SdiProvider>` è idiomatico Rust per polimorfismo runtime
- `#[async_trait::async_trait]` è NECESSARIO per trait con metodi async in Rust stable
  </action>
  <verify>
```bash
# Verifica tipo check su MacBook (solo TypeScript — Rust build SOLO su iMac)
# Verifica manuale che il file contenga i marcatori chiave:
grep -n "trait SdiProvider" src-tauri/src/commands/fatture.rs
grep -n "ArubaProvider" src-tauri/src/commands/fatture.rs
grep -n "OpenApiProvider" src-tauri/src/commands/fatture.rs
grep -n "sdi_provider_factory" src-tauri/src/commands/fatture.rs
grep -n "sdi_provider" src-tauri/src/commands/fatture.rs | head -5
# Verifica struct ImpostazioniFatturazione ha nuovi campi:
grep -n "sdi_provider\|aruba_api_key\|openapi_api_key" src-tauri/src/commands/fatture.rs
# Verifica Cargo.toml ha le dipendenze:
grep -n "async-trait\|base64" src-tauri/Cargo.toml
```
  </verify>
  <done>
- `trait SdiProvider` definito con metodo `invia_fattura`
- Struct `ArubaProvider`, `OpenApiProvider`, `Fattura24Provider` tutte implementano `SdiProvider`
- `sdi_provider_factory` legge provider dal DB e ritorna `Box<dyn SdiProvider>`
- `invia_sdi_fattura` usa factory invece di codice Fattura24 hardcoded
- `struct ImpostazioniFatturazione` ha campi `sdi_provider`, `aruba_api_key`, `openapi_api_key`
- `Cargo.toml` ha `async-trait` e `base64` nelle dependencies
- Zero `unwrap()` bare nel codice aggiunto
  </done>
</task>

</tasks>

<verification>
Verifica manuale pre-commit (su MacBook — NO Rust build):
1. `grep -c "unwrap()" src-tauri/src/commands/fatture.rs` — il numero NON deve aumentare rispetto a prima
2. `cat src-tauri/migrations/029_sdi_multi_provider.sql` — 3 ALTER TABLE visibili
3. `grep -n "sdi_provider_factory\|SdiProvider\|ArubaProvider\|OpenApiProvider" src-tauri/src/commands/fatture.rs` — tutti presenti

Il Rust build (cargo check) va eseguito SOLO su iMac (192.168.1.2) nel Plan 04.
</verification>

<success_criteria>
- Migration 029 SQL: 3 nuove colonne con DEFAULT 'fattura24' per retrocompat
- Trait SdiProvider definito con async invia_fattura
- 3 implementazioni: Fattura24Provider (retrocompat), ArubaProvider (primario), OpenApiProvider (secondario)
- Factory function sdi_provider_factory che legge provider dal DB
- invia_sdi_fattura refactored per usare la factory
- Zero unwrap() bare aggiunti
- ImpostazioniFatturazione struct aggiornata con 3 nuovi campi
</success_criteria>

<output>
Dopo completamento, crea `.planning/phases/sdi-aruba-multi-provider/sdi-aruba-01-SUMMARY.md`
</output>
