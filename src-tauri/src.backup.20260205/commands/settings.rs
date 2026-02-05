// ═══════════════════════════════════════════════════════════════════
// FLUXION - Settings Commands
// Gestione impostazioni configurabili via UI
// ═══════════════════════════════════════════════════════════════════

use serde::{Deserialize, Serialize};
use sqlx::SqlitePool;
use tauri::State;

// ─────────────────────────────────────────────────────────────────────
// TYPES
// ─────────────────────────────────────────────────────────────────────

#[derive(Debug, Serialize, Deserialize, Default)]
pub struct SmtpSettings {
    pub smtp_host: String,
    pub smtp_port: i32,
    pub smtp_email_from: String,
    pub smtp_password: String,
    pub smtp_enabled: bool,
}

// ─────────────────────────────────────────────────────────────────────
// HELPER FUNCTIONS
// ─────────────────────────────────────────────────────────────────────

async fn get_setting(pool: &SqlitePool, chiave: &str) -> Option<String> {
    let result: Option<(String,)> =
        sqlx::query_as("SELECT valore FROM impostazioni WHERE chiave = ?")
            .bind(chiave)
            .fetch_optional(pool)
            .await
            .ok()?;

    result.map(|(v,)| v)
}

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

// ─────────────────────────────────────────────────────────────────────
// SMTP SETTINGS COMMANDS
// ─────────────────────────────────────────────────────────────────────

/// Ottieni le impostazioni SMTP correnti
#[tauri::command]
pub async fn get_smtp_settings(pool: State<'_, SqlitePool>) -> Result<SmtpSettings, String> {
    let smtp_host = get_setting(pool.inner(), "smtp_host")
        .await
        .unwrap_or_else(|| "smtp.gmail.com".to_string());

    let smtp_port = get_setting(pool.inner(), "smtp_port")
        .await
        .and_then(|v| v.parse().ok())
        .unwrap_or(587);

    let smtp_email_from = get_setting(pool.inner(), "smtp_email_from")
        .await
        .unwrap_or_default();

    let smtp_password = get_setting(pool.inner(), "smtp_password")
        .await
        .unwrap_or_default();

    let smtp_enabled = get_setting(pool.inner(), "smtp_enabled")
        .await
        .map(|v| v == "true")
        .unwrap_or(false);

    Ok(SmtpSettings {
        smtp_host,
        smtp_port,
        smtp_email_from,
        smtp_password,
        smtp_enabled,
    })
}

/// Salva le impostazioni SMTP
#[tauri::command]
pub async fn save_smtp_settings(
    pool: State<'_, SqlitePool>,
    settings: SmtpSettings,
) -> Result<(), String> {
    save_setting(pool.inner(), "smtp_host", &settings.smtp_host, "string").await?;
    save_setting(
        pool.inner(),
        "smtp_port",
        &settings.smtp_port.to_string(),
        "number",
    )
    .await?;
    save_setting(
        pool.inner(),
        "smtp_email_from",
        &settings.smtp_email_from,
        "string",
    )
    .await?;
    save_setting(
        pool.inner(),
        "smtp_password",
        &settings.smtp_password,
        "string",
    )
    .await?;
    save_setting(
        pool.inner(),
        "smtp_enabled",
        if settings.smtp_enabled {
            "true"
        } else {
            "false"
        },
        "boolean",
    )
    .await?;

    println!("✅ SMTP settings saved for: {}", settings.smtp_email_from);
    Ok(())
}

/// Test connessione SMTP (senza inviare email)
#[tauri::command]
pub async fn test_smtp_connection(pool: State<'_, SqlitePool>) -> Result<bool, String> {
    let settings = get_smtp_settings(pool).await?;

    if settings.smtp_email_from.is_empty() || settings.smtp_password.is_empty() {
        return Err("SMTP email e password sono richiesti".to_string());
    }

    // Per ora ritorna true se le credenziali sono configurate
    // In futuro: test reale connessione SMTP
    Ok(true)
}
