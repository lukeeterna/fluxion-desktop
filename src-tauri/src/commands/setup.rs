// ═══════════════════════════════════════════════════════════════════
// FLUXION - Setup Wizard Commands
// Gestione configurazione iniziale all'installazione
// ═══════════════════════════════════════════════════════════════════

use serde::{Deserialize, Serialize};
use sqlx::SqlitePool;
use tauri::State;

// ─────────────────────────────────────────────────────────────────────
// TYPES
// ─────────────────────────────────────────────────────────────────────

#[derive(Debug, Serialize, Deserialize)]
pub struct SetupConfig {
    // Dati Azienda
    pub nome_attivita: String,
    pub partita_iva: Option<String>,
    pub codice_fiscale: Option<String>,
    pub indirizzo: Option<String>,
    pub cap: Option<String>,
    pub citta: Option<String>,
    pub provincia: Option<String>,
    pub telefono: Option<String>,
    pub email: Option<String>,
    pub pec: Option<String>,

    // Regime Fiscale (RF01=Ordinario, RF19=Forfettario)
    pub regime_fiscale: Option<String>,

    // FLUXION IA - Chiave per assistente intelligente (opzionale)
    pub fluxion_ia_key: Option<String>,

    // Categoria attività (per FAQ RAG)
    pub categoria_attivita: Option<String>, // salone, auto, wellness, medical
}

#[derive(Debug, Serialize)]
pub struct SetupStatus {
    pub is_completed: bool,
    pub nome_attivita: Option<String>,
    pub missing_fields: Vec<String>,
}

// ─────────────────────────────────────────────────────────────────────
// COMMANDS
// ─────────────────────────────────────────────────────────────────────

/// Verifica se il setup iniziale è stato completato
#[tauri::command]
pub async fn get_setup_status(pool: State<'_, SqlitePool>) -> Result<SetupStatus, String> {
    // Legge il nome attività dalle impostazioni
    let nome_result: Option<(String,)> =
        sqlx::query_as("SELECT valore FROM impostazioni WHERE chiave = 'nome_attivita'")
            .fetch_optional(pool.inner())
            .await
            .map_err(|e| e.to_string())?;

    // Verifica se setup_completed è true
    let setup_result: Option<(String,)> =
        sqlx::query_as("SELECT valore FROM impostazioni WHERE chiave = 'setup_completed'")
            .fetch_optional(pool.inner())
            .await
            .map_err(|e| e.to_string())?;

    let is_completed = setup_result.map(|(v,)| v == "true").unwrap_or(false);

    let nome_attivita = nome_result.map(|(v,)| v);

    // Se non completato, indica i campi mancanti
    let mut missing_fields = Vec::new();
    if nome_attivita
        .as_ref()
        .map(|n| n == "La Mia Attività")
        .unwrap_or(true)
    {
        missing_fields.push("nome_attivita".to_string());
    }

    Ok(SetupStatus {
        is_completed,
        nome_attivita,
        missing_fields,
    })
}

/// Salva la configurazione iniziale
#[tauri::command]
pub async fn save_setup_config(
    pool: State<'_, SqlitePool>,
    config: SetupConfig,
) -> Result<(), String> {
    // Funzione helper per salvare una impostazione
    async fn save_setting(
        pool: &SqlitePool,
        chiave: &str,
        valore: &str,
        tipo: &str,
    ) -> Result<(), String> {
        sqlx::query(
            "INSERT OR REPLACE INTO impostazioni (chiave, valore, tipo, updated_at) VALUES (?, ?, ?, datetime('now'))"
        )
        .bind(chiave)
        .bind(valore)
        .bind(tipo)
        .execute(pool)
        .await
        .map_err(|e| e.to_string())?;
        Ok(())
    }

    // Salva tutti i campi
    save_setting(
        pool.inner(),
        "nome_attivita",
        &config.nome_attivita,
        "string",
    )
    .await?;

    if let Some(ref v) = config.partita_iva {
        save_setting(pool.inner(), "partita_iva", v, "string").await?;
    }
    if let Some(ref v) = config.codice_fiscale {
        save_setting(pool.inner(), "codice_fiscale", v, "string").await?;
    }
    if let Some(ref v) = config.indirizzo {
        save_setting(pool.inner(), "indirizzo", v, "string").await?;
    }
    if let Some(ref v) = config.cap {
        save_setting(pool.inner(), "cap", v, "string").await?;
    }
    if let Some(ref v) = config.citta {
        save_setting(pool.inner(), "citta", v, "string").await?;
    }
    if let Some(ref v) = config.provincia {
        save_setting(pool.inner(), "provincia", v, "string").await?;
    }
    if let Some(ref v) = config.telefono {
        save_setting(pool.inner(), "telefono", v, "string").await?;
    }
    if let Some(ref v) = config.email {
        save_setting(pool.inner(), "email", v, "string").await?;
    }
    if let Some(ref v) = config.pec {
        save_setting(pool.inner(), "pec", v, "string").await?;
    }
    if let Some(ref v) = config.regime_fiscale {
        save_setting(pool.inner(), "regime_fiscale", v, "string").await?;
    }
    if let Some(ref v) = config.fluxion_ia_key {
        save_setting(pool.inner(), "fluxion_ia_key", v, "string").await?;
    }
    if let Some(ref v) = config.categoria_attivita {
        save_setting(pool.inner(), "categoria_attivita", v, "string").await?;
    }

    // Marca il setup come completato
    save_setting(pool.inner(), "setup_completed", "true", "boolean").await?;

    println!("✅ Setup completato per: {}", config.nome_attivita);

    Ok(())
}

/// Ottieni la configurazione corrente
#[tauri::command]
pub async fn get_setup_config(pool: State<'_, SqlitePool>) -> Result<SetupConfig, String> {
    // Funzione helper per leggere una impostazione
    async fn get_setting(pool: &SqlitePool, chiave: &str) -> Option<String> {
        let result: Option<(String,)> =
            sqlx::query_as("SELECT valore FROM impostazioni WHERE chiave = ?")
                .bind(chiave)
                .fetch_optional(pool)
                .await
                .ok()?;

        result.map(|(v,)| v)
    }

    Ok(SetupConfig {
        nome_attivita: get_setting(pool.inner(), "nome_attivita")
            .await
            .unwrap_or_else(|| "La Mia Attività".to_string()),
        partita_iva: get_setting(pool.inner(), "partita_iva").await,
        codice_fiscale: get_setting(pool.inner(), "codice_fiscale").await,
        indirizzo: get_setting(pool.inner(), "indirizzo").await,
        cap: get_setting(pool.inner(), "cap").await,
        citta: get_setting(pool.inner(), "citta").await,
        provincia: get_setting(pool.inner(), "provincia").await,
        telefono: get_setting(pool.inner(), "telefono").await,
        email: get_setting(pool.inner(), "email").await,
        pec: get_setting(pool.inner(), "pec").await,
        regime_fiscale: get_setting(pool.inner(), "regime_fiscale").await,
        fluxion_ia_key: get_setting(pool.inner(), "fluxion_ia_key").await,
        categoria_attivita: get_setting(pool.inner(), "categoria_attivita").await,
    })
}

/// Resetta il setup (per test/debug)
#[tauri::command]
pub async fn reset_setup(pool: State<'_, SqlitePool>) -> Result<(), String> {
    sqlx::query("DELETE FROM impostazioni WHERE chiave = 'setup_completed'")
        .execute(pool.inner())
        .await
        .map_err(|e| e.to_string())?;

    println!("🔄 Setup resettato");
    Ok(())
}
