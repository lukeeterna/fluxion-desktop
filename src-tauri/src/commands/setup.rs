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

    // Categoria attività legacy (per FAQ RAG)
    pub categoria_attivita: Option<String>, // salone, auto, wellness, medical

    // NUOVO: Macro e Micro categoria per verticali
    pub macro_categoria: Option<String>, // medico, beauty, hair, auto, wellness, professionale
    pub micro_categoria: Option<String>, // odontoiatra, fisioterapia, etc.

    // NUOVO: Tier licenza selezionato
    pub license_tier: Option<String>, // trial, base, pro, enterprise

    // NUOVO: Configurazione comunicazioni (Step 6 - Config)
    pub whatsapp_number: Option<String>, // Numero WhatsApp Business per notifiche
    pub ehiweb_number: Option<String>,   // Numero linea fissa EhiWeb (opzionale)

    // NUOVO: Groq API key per Voice Agent Sara (Step 7 wizard)
    pub groq_api_key: Option<String>,
}

#[derive(Debug, Serialize)]
pub struct SetupStatus {
    pub is_completed: bool,
    pub nome_attivita: Option<String>,
    pub missing_fields: Vec<String>,
    pub macro_categoria: Option<String>,
    pub micro_categoria: Option<String>,
    pub license_tier: Option<String>,
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

    // Leggi macro/micro categorie
    let macro_result: Option<(String,)> =
        sqlx::query_as("SELECT valore FROM impostazioni WHERE chiave = 'macro_categoria'")
            .fetch_optional(pool.inner())
            .await
            .map_err(|e| e.to_string())?;

    let micro_result: Option<(String,)> =
        sqlx::query_as("SELECT valore FROM impostazioni WHERE chiave = 'micro_categoria'")
            .fetch_optional(pool.inner())
            .await
            .map_err(|e| e.to_string())?;

    let license_result: Option<(String,)> =
        sqlx::query_as("SELECT valore FROM impostazioni WHERE chiave = 'license_tier'")
            .fetch_optional(pool.inner())
            .await
            .map_err(|e| e.to_string())?;

    // Se non completato, indica i campi mancanti
    let mut missing_fields = Vec::new();
    if nome_attivita
        .as_ref()
        .map(|n| n == "La Mia Attività" || n.is_empty())
        .unwrap_or(true)
    {
        missing_fields.push("nome_attivita".to_string());
    }

    Ok(SetupStatus {
        is_completed,
        nome_attivita,
        missing_fields,
        macro_categoria: macro_result.map(|(v,)| v).filter(|v| !v.is_empty()),
        micro_categoria: micro_result.map(|(v,)| v).filter(|v| !v.is_empty()),
        license_tier: license_result.map(|(v,)| v).filter(|v| !v.is_empty()),
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

    // NUOVO: Salva macro/micro categoria
    if let Some(ref v) = config.macro_categoria {
        save_setting(pool.inner(), "macro_categoria", v, "string").await?;
    }
    if let Some(ref v) = config.micro_categoria {
        save_setting(pool.inner(), "micro_categoria", v, "string").await?;
    }
    if let Some(ref v) = config.license_tier {
        save_setting(pool.inner(), "license_tier", v, "string").await?;
    }

    // NUOVO: Salva configurazioni comunicazioni
    if let Some(ref v) = config.whatsapp_number {
        save_setting(pool.inner(), "whatsapp_number", v, "string").await?;
    }
    if let Some(ref v) = config.ehiweb_number {
        save_setting(pool.inner(), "ehiweb_number", v, "string").await?;
    }

    // NUOVO: Salva Groq API key per Voice Agent (Step 7)
    if let Some(ref v) = config.groq_api_key {
        if !v.is_empty() {
            save_setting(pool.inner(), "groq_api_key", v, "string").await?;
        }
    }

    // Marca il setup come completato
    save_setting(pool.inner(), "setup_completed", "true", "boolean").await?;

    println!("✅ Setup completato per: {}", config.nome_attivita);
    println!(
        "   Macro: {:?}, Micro: {:?}, Tier: {:?}",
        config.macro_categoria, config.micro_categoria, config.license_tier
    );

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
        macro_categoria: get_setting(pool.inner(), "macro_categoria").await,
        micro_categoria: get_setting(pool.inner(), "micro_categoria").await,
        license_tier: get_setting(pool.inner(), "license_tier").await,
        whatsapp_number: get_setting(pool.inner(), "whatsapp_number").await,
        ehiweb_number: get_setting(pool.inner(), "ehiweb_number").await,
        groq_api_key: get_setting(pool.inner(), "groq_api_key").await,
    })
}

// ─────────────────────────────────────────────────────────────────────
// TEST GROQ KEY — verifica reale via API Groq
// ─────────────────────────────────────────────────────────────────────

#[derive(Debug, Serialize)]
pub struct GroqTestResult {
    pub ok: bool,
    pub message: String,
}

/// Verifica una Groq API key chiamando realmente l'API (lista modelli)
#[tauri::command]
pub async fn test_groq_key(api_key: String) -> Result<GroqTestResult, String> {
    let key = api_key.trim().to_string();

    if key.is_empty() {
        return Ok(GroqTestResult {
            ok: false,
            message: "Inserisci la chiave API prima di testarla.".to_string(),
        });
    }

    if !key.starts_with("gsk_") {
        return Ok(GroqTestResult {
            ok: false,
            message: "❌ Formato non valido — la chiave deve iniziare con \"gsk_\"".to_string(),
        });
    }

    let client = reqwest::Client::builder()
        .timeout(std::time::Duration::from_secs(8))
        .build()
        .map_err(|e| e.to_string())?;

    let response = client
        .get("https://api.groq.com/openai/v1/models")
        .header("Authorization", format!("Bearer {}", key))
        .send()
        .await;

    match response {
        Ok(res) => {
            if res.status().is_success() {
                Ok(GroqTestResult {
                    ok: true,
                    message: "✅ Fluxion AI attivo! Sara è pronta a rispondere al telefono."
                        .to_string(),
                })
            } else if res.status() == 401 {
                Ok(GroqTestResult {
                    ok: false,
                    message: "❌ Chiave non valida — controlla di aver copiato tutta la chiave."
                        .to_string(),
                })
            } else {
                Ok(GroqTestResult {
                    ok: false,
                    message: format!(
                        "❌ Errore Fluxion AI ({}). Riprova tra qualche minuto.",
                        res.status()
                    ),
                })
            }
        }
        Err(e) if e.is_timeout() => Ok(GroqTestResult {
            ok: false,
            message: "❌ Nessuna connessione internet. Connetti il computer a internet e riprova."
                .to_string(),
        }),
        Err(_) => Ok(GroqTestResult {
            ok: false,
            message: "❌ Impossibile contattare Fluxion AI. Verifica la connessione internet."
                .to_string(),
        }),
    }
}

/// Resetta il setup (per test/debug)
#[tauri::command]
pub async fn reset_setup(pool: State<'_, SqlitePool>) -> Result<(), String> {
    sqlx::query("DELETE FROM impostazioni WHERE chiave = 'setup_completed'")
        .execute(pool.inner())
        .await
        .map_err(|e| e.to_string())?;

    sqlx::query("DELETE FROM impostazioni WHERE chiave = 'macro_categoria'")
        .execute(pool.inner())
        .await
        .map_err(|e| e.to_string())?;

    sqlx::query("DELETE FROM impostazioni WHERE chiave = 'micro_categoria'")
        .execute(pool.inner())
        .await
        .map_err(|e| e.to_string())?;

    println!("🔄 Setup resettato");
    Ok(())
}
