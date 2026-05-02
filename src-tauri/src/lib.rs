// ═══════════════════════════════════════════════════════════════════
// FLUXION - Tauri Backend Configuration
// ═══════════════════════════════════════════════════════════════════

use tauri::Manager;

// ───────────────────────────────────────────────────────────────────
// Modules
// ───────────────────────────────────────────────────────────────────

mod commands;
pub mod domain;
mod encryption;
mod http_bridge;
pub mod infra;
pub mod services;

// ───────────────────────────────────────────────────────────────────
// Application State
// ───────────────────────────────────────────────────────────────────

pub struct AppState {
    pub db: sqlx::SqlitePool,
    pub appuntamento_service: services::AppuntamentoService,
}

// ───────────────────────────────────────────────────────────────────
// Database Initialization
// ───────────────────────────────────────────────────────────────────

/// Parse SQL file into individual statements
/// Handles multi-line statements by tracking parentheses depth
fn parse_sql_statements(sql: &str) -> Vec<String> {
    let mut statements = Vec::new();
    let mut current_statement = String::new();
    let mut paren_depth = 0;

    for line in sql.lines() {
        let trimmed = line.trim();

        // Skip comment-only lines
        if trimmed.starts_with("--") || trimmed.is_empty() {
            continue;
        }

        // Track parentheses for CREATE TABLE statements
        paren_depth += line.matches('(').count() as i32;
        paren_depth -= line.matches(')').count() as i32;

        current_statement.push_str(line);
        current_statement.push('\n');

        // End of statement when we hit ; and we're not inside parentheses
        if trimmed.ends_with(';') && paren_depth == 0 {
            statements.push(current_statement.trim().to_string());
            current_statement.clear();
        }
    }

    // Add any remaining statement
    if !current_statement.trim().is_empty() {
        statements.push(current_statement.trim().to_string());
    }

    statements
}

/// Extract table name from CREATE TABLE statement
#[allow(dead_code)]
fn extract_table_name(sql: &str) -> String {
    sql.split_whitespace()
        .skip_while(|&w| w != "TABLE")
        .nth(1)
        .and_then(|name| {
            // Handle "IF NOT EXISTS table_name"
            if name == "IF" {
                sql.split_whitespace().skip_while(|&w| w != "EXISTS").nth(1)
            } else {
                Some(name)
            }
        })
        .unwrap_or("unknown")
        .trim()
        .to_string()
}

/// Run a single migration: execute each SQL statement, silently ignoring
/// "already exists" / "duplicate column" / "UNIQUE constraint" errors
/// (idempotent — safe to re-run on every startup).
async fn run_migration(pool: &sqlx::SqlitePool, label: &str, sql: &str) -> Result<(), String> {
    let statements = parse_sql_statements(sql);
    for (idx, statement) in statements.iter().enumerate() {
        let trimmed = statement.trim();
        if trimmed.is_empty() || trimmed.starts_with("--") {
            continue;
        }
        match sqlx::query(trimmed).execute(pool).await {
            Ok(_) => {}
            Err(e) => {
                let err_msg = e.to_string();
                if !err_msg.contains("already exists")
                    && !err_msg.contains("duplicate column")
                    && !err_msg.contains("UNIQUE constraint")
                {
                    eprintln!("⚠️  [{}] Statement {} failed: {}", label, idx + 1, err_msg);
                }
            }
        }
    }
    println!("  ✓ [{}] ready", label);
    Ok(())
}

/// S184 α.3.0-B — Detect if a path is inside a known cloud sync folder.
///
/// SQLite WAL mode does NOT survive cloud sync — files get partially uploaded
/// mid-write, causing data corruption (research-zero-bug-install §W10/M5).
/// Returns the name of the sync provider if detected, None if path is safe.
///
/// Detection is case-insensitive and component-aware to reduce false positives
/// (e.g. a folder literally named "OneDrive Backup" would match, but a file
/// named `backup-onedrive.sql` would not).
pub fn detect_cloud_sync_provider(path: &std::path::Path) -> Option<&'static str> {
    // Lowercase + normalize separators so Windows paths match the same patterns
    // (folder boundary detection relies on `/` in the patterns below).
    let path_lower = path
        .to_string_lossy()
        .replace('\\', "/")
        .to_lowercase();

    // Patterns ordered by likelihood on Italian PMI desktops
    const CLOUD_PATTERNS: &[(&str, &str)] = &[
        // macOS iCloud Drive — exact internal path
        ("library/mobile documents/com~apple~clouddocs", "iCloud Drive"),
        ("/icloud drive/", "iCloud Drive"),
        // OneDrive (Windows + macOS) — folder name is OS-localized but English form
        // is the most common; Italian Win10 default = "OneDrive" (English)
        ("/onedrive/", "OneDrive"),
        ("/onedrive -", "OneDrive Business"),
        // Other consumer sync clients
        ("/dropbox/", "Dropbox"),
        ("/google drive/", "Google Drive"),
        ("/googledrive/", "Google Drive"),
        ("/box sync/", "Box"),
        ("/box/", "Box"),
        ("/megasync/", "MEGAsync"),
        ("/pcloud/", "pCloud"),
        ("/sync/", "Sync.com"),
    ];

    for (pat, provider) in CLOUD_PATTERNS {
        if path_lower.contains(pat) {
            return Some(provider);
        }
    }
    None
}

/// Initialize SQLite database and run migrations
async fn init_database(app: &tauri::AppHandle) -> Result<(), Box<dyn std::error::Error>> {
    // Get database path in app data directory
    let app_data_dir = app
        .path()
        .app_data_dir()
        .map_err(|e| format!("Failed to get app data directory: {}", e))?;

    // Create directory if it doesn't exist
    std::fs::create_dir_all(&app_data_dir)?;

    let db_path = app_data_dir.join("fluxion.db");

    // ── S184 α.3.0-B: cloud sync corruption guard ───────────────────────
    // SQLite WAL + cloud sync = data loss. We detect known sync folders and
    // emit a loud warning + Sentry event. We do NOT abort: forcing the app
    // offline would be worse for the user. The pre-flight wizard (α.3.1-E)
    // will surface this in UI with remediation steps.
    if let Some(provider) = detect_cloud_sync_provider(&db_path) {
        let warning = format!(
            "⚠️  CRITICAL: Database path is inside {} sync folder!\n\
             Path: {}\n\
             SQLite WAL mode does not survive cloud sync — DATA LOSS RISK.\n\
             Recommended: pause sync for this folder OR move app data outside cloud.\n\
             Founder action required: contact support@fluxion (TODO landing).",
            provider,
            db_path.display()
        );
        eprintln!("{}", warning);
        // Best-effort Sentry capture (no-op if Sentry not initialised)
        sentry::capture_message(&warning, sentry::Level::Warning);
    }
    // ─────────────────────────────────────────────────────────────────────

    let db_url = format!("sqlite:{}?mode=rwc", db_path.display());

    println!("📁 Database path: {}", db_path.display());

    // Create database connection pool
    // A1 FIX CoVe2026: busy_timeout evita "database is locked" sotto carico concorrente
    let pool = sqlx::sqlite::SqlitePoolOptions::new()
        .max_connections(5)
        .acquire_timeout(std::time::Duration::from_secs(30))
        .connect(&db_url)
        .await?;

    // Enable WAL mode + performance PRAGMAs (A1 CoVe2026)
    // WAL permette letture concorrenti durante scritture — essenziale per voice agent + UI
    sqlx::query("PRAGMA journal_mode=WAL")
        .execute(&pool)
        .await?;
    sqlx::query("PRAGMA synchronous=NORMAL")
        .execute(&pool)
        .await?;
    sqlx::query("PRAGMA cache_size=-32000")
        .execute(&pool)
        .await?;
    sqlx::query("PRAGMA busy_timeout=30000")
        .execute(&pool)
        .await?;

    // Enable foreign keys
    sqlx::query("PRAGMA foreign_keys = ON")
        .execute(&pool)
        .await?;

    println!("✅ Database initialized");

    // Run migrations
    println!("🔄 Running migrations...");

    // ── All migrations (idempotent — safe to re-run on every startup) ──
    // Each migration's SQL uses IF NOT EXISTS / IF NOT EXISTS column guards,
    // and run_migration silently ignores "already exists" / "duplicate column"
    // / "UNIQUE constraint" errors.
    run_migration(&pool, "001", include_str!("../migrations/001_init.sql")).await?;
    run_migration(
        &pool,
        "002",
        include_str!("../migrations/002_whatsapp_templates.sql"),
    )
    .await?;
    run_migration(
        &pool,
        "003",
        include_str!("../migrations/003_orari_e_festivita.sql"),
    )
    .await?;
    run_migration(
        &pool,
        "004",
        include_str!("../migrations/004_appuntamenti_state_machine.sql"),
    )
    .await?;
    run_migration(
        &pool,
        "005",
        include_str!("../migrations/005_loyalty_pacchetti_vip.sql"),
    )
    .await?;
    run_migration(
        &pool,
        "006",
        include_str!("../migrations/006_pacchetto_servizi.sql"),
    )
    .await?;
    run_migration(
        &pool,
        "007",
        include_str!("../migrations/007_fatturazione_elettronica.sql"),
    )
    .await?;
    run_migration(
        &pool,
        "008",
        include_str!("../migrations/008_faq_template_soprannome.sql"),
    )
    .await?;
    run_migration(
        &pool,
        "009",
        include_str!("../migrations/009_cassa_incassi.sql"),
    )
    .await?;
    run_migration(
        &pool,
        "010",
        include_str!("../migrations/010_mock_data.sql"),
    )
    .await?;
    run_migration(
        &pool,
        "011",
        include_str!("../migrations/011_voice_agent.sql"),
    )
    .await?;
    run_migration(
        &pool,
        "012",
        include_str!("../migrations/012_operatori_voice_agent.sql"),
    )
    .await?;
    run_migration(&pool, "013", include_str!("../migrations/013_waitlist.sql")).await?;
    // NOTE: Migration 014 was intentionally skipped (number not used)
    run_migration(
        &pool,
        "015",
        include_str!("../migrations/015_license_system.sql"),
    )
    .await?;
    run_migration(
        &pool,
        "016",
        include_str!("../migrations/016_suppliers.sql"),
    )
    .await?;
    run_migration(
        &pool,
        "017",
        include_str!("../migrations/017_smtp_settings.sql"),
    )
    .await?;
    run_migration(
        &pool,
        "018",
        include_str!("../migrations/018_gdpr_audit_logs.sql"),
    )
    .await?;
    run_migration(
        &pool,
        "019",
        include_str!("../migrations/019_schede_clienti_verticali.sql"),
    )
    .await?;
    run_migration(
        &pool,
        "020",
        include_str!("../migrations/020_license_ed25519.sql"),
    )
    .await?;
    run_migration(
        &pool,
        "021",
        include_str!("../migrations/021_setup_config.sql"),
    )
    .await?;
    run_migration(
        &pool,
        "022",
        include_str!("../migrations/022_whatsapp_invii_pacchetti.sql"),
    )
    .await?;
    run_migration(
        &pool,
        "023",
        include_str!("../migrations/023_groq_setup.sql"),
    )
    .await?;
    run_migration(
        &pool,
        "024",
        include_str!("../migrations/024_operatori_features.sql"),
    )
    .await?;
    run_migration(
        &pool,
        "025",
        include_str!("../migrations/025_operatori_commissioni.sql"),
    )
    .await?;
    run_migration(
        &pool,
        "026",
        include_str!("../migrations/026_impostazioni_sdi_key.sql"),
    )
    .await?;
    run_migration(
        &pool,
        "027",
        include_str!("../migrations/027_scheda_fitness.sql"),
    )
    .await?;
    run_migration(
        &pool,
        "028",
        include_str!("../migrations/028_scheda_medica.sql"),
    )
    .await?;
    run_migration(
        &pool,
        "029",
        include_str!("../migrations/029_sdi_multi_provider.sql"),
    )
    .await?;
    run_migration(
        &pool,
        "030",
        include_str!("../migrations/030_cliente_media.sql"),
    )
    .await?;
    run_migration(
        &pool,
        "031",
        include_str!("../migrations/031_listini_fornitori.sql"),
    )
    .await?;
    run_migration(
        &pool,
        "032",
        include_str!("../migrations/032_voip_sip_credentials.sql"),
    )
    .await?;
    run_migration(
        &pool,
        "033",
        include_str!("../migrations/033_operatori_genere.sql"),
    )
    .await?;
    run_migration(
        &pool,
        "034",
        include_str!("../migrations/034_blocchi_orario.sql"),
    )
    .await?;
    run_migration(
        &pool,
        "035",
        include_str!("../migrations/035_scheda_pet.sql"),
    )
    .await?;
    run_migration(
        &pool,
        "036",
        include_str!("../migrations/036_missing_indexes.sql"),
    )
    .await?;
    run_migration(
        &pool,
        "037",
        include_str!("../migrations/037_gdpr_art9_consent.sql"),
    )
    .await?;

    println!("✅ Migrations completed");

    // Initialize service layer with repository
    let appuntamento_repo = Box::new(infra::SqliteAppuntamentoRepository::new(pool.clone()));
    let appuntamento_service = services::AppuntamentoService::new(appuntamento_repo);

    // Store pool in app state for later use
    // NOTE: We manage both pool (for legacy commands) and AppState (for new commands)
    // TODO: Refactor all commands to use AppState only
    let pool_clone = pool.clone();
    let state = AppState {
        db: pool,
        appuntamento_service,
    };
    app.manage(pool_clone);
    app.manage(state);
    app.manage(commands::settings::OAuthState::default());

    Ok(())
}

// ───────────────────────────────────────────────────────────────────
// Tauri Commands (to be implemented in future phases)
// ───────────────────────────────────────────────────────────────────

// TODO: Add Tauri commands for CRUD operations
// Pattern from rust-backend.md:
// #[tauri::command]
// pub async fn get_clienti(pool: State<'_, SqlitePool>) -> Result<Vec<Cliente>, String> { ... }

// ───────────────────────────────────────────────────────────────────
// S184 α.1.3 — Sentry Crash Reporter
// No-op silenzioso se SENTRY_DSN_RUST assente (dev locale).
// PII filter: scrub campi italiani sensibili (clienti, telefoni, fatture).
// ───────────────────────────────────────────────────────────────────

const SENSITIVE_KEYS: &[&str] = &[
    "cliente",
    "cliente_id",
    "telefono",
    "email",
    "codice_fiscale",
    "partita_iva",
    "indirizzo",
    "nome",
    "cognome",
    "soprannome",
    "data_nascita",
    "xml_sdi",
    "fattura",
    "license_key",
    "stripe_payment_intent",
];

fn scrub_pii(mut event: sentry::protocol::Event<'static>) -> Option<sentry::protocol::Event<'static>> {
    // Scrub extra map
    for (k, v) in event.extra.iter_mut() {
        let lower = k.to_lowercase();
        if SENSITIVE_KEYS.iter().any(|s| lower.contains(s)) {
            *v = sentry::protocol::Value::String("[REDACTED]".into());
        }
    }
    // Scrub tags
    for (k, v) in event.tags.iter_mut() {
        let lower = k.to_lowercase();
        if SENSITIVE_KEYS.iter().any(|s| lower.contains(s)) {
            *v = "[REDACTED]".into();
        }
    }
    Some(event)
}

fn init_sentry() -> Option<sentry::ClientInitGuard> {
    let dsn = std::env::var("SENTRY_DSN_RUST").ok()?;
    if dsn.is_empty() {
        return None;
    }
    let release = format!("fluxion-rust@{}", env!("CARGO_PKG_VERSION"));
    let guard = sentry::init((
        dsn,
        sentry::ClientOptions {
            release: Some(release.into()),
            environment: Some(
                std::env::var("FLUXION_ENV")
                    .unwrap_or_else(|_| "production".to_string())
                    .into(),
            ),
            traces_sample_rate: 0.0,
            attach_stacktrace: true,
            send_default_pii: false,
            before_send: Some(std::sync::Arc::new(|event| scrub_pii(event))),
            ..Default::default()
        },
    ));
    println!("✅ Sentry crash reporter initialized (Rust)");
    Some(guard)
}

// ───────────────────────────────────────────────────────────────────
// Application Entry Point
// ───────────────────────────────────────────────────────────────────

#[cfg(not(test))]
#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    // Load .env file for API keys (optional - can also be configured via Setup Wizard)
    // Try multiple locations: current dir, project root, app data dir
    if let Err(e) = dotenvy::dotenv() {
        eprintln!("⚠️  .env file not found or invalid: {}", e);
        eprintln!("   FLUXION IA può essere configurato nel Setup Wizard o nelle Impostazioni");
    } else {
        println!("✅ Environment variables loaded from .env");
    }

    // ─── S184 α.1.3 — Sentry crash reporter ───
    // Init Sentry PRIMA di tutto (richiesto dal panic hook).
    // Guard mantenuto in vita per tutta la durata dell'app — drop = flush eventi pendenti.
    let _sentry_guard = init_sentry();

    let builder = tauri::Builder::default()
        // ─── Plugin Configuration ───
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_store::Builder::default().build())
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_process::init())
        .plugin(tauri_plugin_updater::Builder::new().build());

    // ─── MCP Server Plugin (Remote Debugging) ───
    // SECURITY: Only enabled when "mcp" feature is active (development only)
    #[cfg(feature = "mcp")]
    let builder = {
        println!("🤖 MCP Server plugin enabled for remote debugging");
        println!("   Socket path: /tmp/fluxion-mcp.sock");
        builder.plugin(tauri_plugin_mcp::init_with_config(
            tauri_plugin_mcp::PluginConfig::new("FLUXION".to_string())
                .start_socket_server(true)
                .socket_path("/tmp/fluxion-mcp.sock".to_string()),
        ))
    };

    // ─── E2E Testing Plugin (REQUIRED for macOS with CrabNebula) ───
    #[cfg(feature = "e2e")]
    let builder = {
        println!("🧪 E2E automation plugin enabled");
        builder.plugin(tauri_plugin_automation::init())
    };

    builder
        // ─── Setup Hook ───
        .setup(|app| {
            // Initialize database SYNCHRONOUSLY before app starts
            // This prevents race conditions where commands are called before pool is ready
            let app_handle = app.handle().clone();
            tauri::async_runtime::block_on(async move {
                if let Err(e) = init_database(&app_handle).await {
                    eprintln!("❌ Database initialization failed: {}", e);
                    eprintln!("   Error details: {:?}", e);
                    std::process::exit(1);
                }
            });

            // F13 — Auto-backup giornaliero (non-blocking, non-fatal)
            {
                let app_handle = app.handle().clone();
                tauri::async_runtime::spawn(async move {
                    if let Some(state) = app_handle.try_state::<crate::AppState>() {
                        match commands::support::run_auto_backup_if_needed(
                            app_handle.clone(),
                            state,
                        )
                        .await
                        {
                            Ok(msg) => println!("💾 Auto-backup: {}", msg),
                            Err(e) => eprintln!("⚠️  Auto-backup failed (non-fatal): {}", e),
                        }
                    }
                });
            }

            // Cleanup stale audio cache WAV files (GDPR + disk hygiene)
            commands::voice::cleanup_audio_cache_sync(app.handle());

            // Auto-start WhatsApp service (non-blocking)
            // Will gracefully skip if Node.js or dependencies not available
            commands::whatsapp::auto_start_whatsapp(app.handle());

            // Start HTTP Bridge for MCP integration (Live Testing)
            // This enables MCP Server to interact with the app
            #[cfg(debug_assertions)]
            {
                let app_handle = app.handle().clone();
                tauri::async_runtime::spawn(async move {
                    if let Err(e) = http_bridge::start_http_bridge(app_handle).await {
                        eprintln!("❌ HTTP Bridge failed to start: {}", e);
                    }
                });
            }

            println!("🚀 Application ready");
            Ok(())
        })
        // ─── Cleanup on Exit ───
        .on_window_event(|_window, event| {
            if let tauri::WindowEvent::Destroyed = event {
                // Stop WhatsApp service when app closes
                commands::whatsapp::stop_whatsapp_service();
            }
        })
        // ─── Invoke Handler ───
        .invoke_handler(tauri::generate_handler![
            // Clienti
            commands::get_clienti,
            commands::get_cliente,
            commands::create_cliente,
            commands::update_cliente,
            commands::delete_cliente,
            commands::gdpr_hard_delete_cliente,
            commands::search_clienti,
            // Servizi
            commands::get_servizi,
            commands::get_servizio,
            commands::create_servizio,
            commands::update_servizio,
            commands::delete_servizio,
            // Operatori
            commands::get_operatori,
            commands::get_operatore,
            commands::create_operatore,
            commands::update_operatore,
            commands::delete_operatore,
            // Operatori Servizi (B2)
            commands::get_operatore_servizi,
            commands::update_operatore_servizi,
            // Operatori Assenze (B2)
            commands::get_operatore_assenze,
            commands::create_operatore_assenza,
            commands::delete_operatore_assenza,
            // Operatori KPI Statistiche (B4)
            commands::get_kpi_operatore_storico,
            commands::get_top_operatori_mese,
            // Operatori Commissioni (B5)
            commands::get_operatore_commissioni,
            commands::create_operatore_commissione,
            commands::update_operatore_commissione,
            commands::delete_operatore_commissione,
            // Appuntamenti (legacy)
            commands::get_appuntamenti,
            commands::get_appuntamento,
            commands::create_appuntamento,
            commands::update_appuntamento,
            commands::delete_appuntamento,
            commands::confirm_appuntamento,
            commands::reject_appuntamento,
            // Appuntamenti (DDD layer - NEW)
            commands::crea_appuntamento_bozza,
            commands::proponi_appuntamento,
            commands::conferma_cliente_appuntamento,
            commands::conferma_operatore_appuntamento,
            commands::conferma_con_override_appuntamento,
            commands::rifiuta_appuntamento,
            commands::cancella_appuntamento_ddd,
            commands::completa_appuntamento_auto,
            // WhatsApp Local (NO API costs - uses system Chrome)
            commands::get_whatsapp_status,
            commands::is_whatsapp_ready,
            commands::start_whatsapp_service,
            commands::prepare_whatsapp_message,
            commands::get_pending_messages,
            commands::queue_whatsapp_message,
            commands::get_received_messages,
            commands::get_whatsapp_config,
            commands::update_whatsapp_config,
            // WhatsApp FAQ Learning System (Fase 7)
            commands::get_pending_questions,
            commands::update_pending_question_status,
            commands::delete_pending_question,
            commands::save_custom_faq,
            commands::get_custom_faqs,
            commands::get_pending_questions_count,
            commands::send_booking_confirm_wa,
            // Orari & Festività
            commands::get_orari_lavoro,
            commands::create_orario_lavoro,
            commands::delete_orario_lavoro,
            commands::get_giorni_festivi,
            commands::is_giorno_festivo,
            commands::create_giorno_festivo,
            commands::delete_giorno_festivo,
            commands::valida_orario_appuntamento,
            commands::get_orari_operatore,
            commands::set_orari_operatore,
            // Support & Diagnostics (Fluxion Care)
            commands::get_diagnostics_info,
            commands::backup_database,
            commands::restore_database,
            commands::list_backups,
            commands::delete_backup,
            // F13 — Auto-backup + CSV Export
            commands::run_auto_backup_if_needed,
            commands::export_clienti_csv,
            commands::export_appuntamenti_csv,
            // Loyalty & Pacchetti (Fase 5 - Quick Wins)
            commands::get_loyalty_info,
            commands::increment_loyalty_visits,
            commands::toggle_vip_status,
            commands::set_loyalty_threshold,
            commands::set_referral_source,
            commands::get_top_referrers,
            commands::get_loyalty_milestones,
            commands::get_clienti_compleanno_settimana,
            commands::get_pacchetti,
            commands::create_pacchetto,
            commands::proponi_pacchetto,
            commands::conferma_acquisto_pacchetto,
            commands::usa_servizio_pacchetto,
            commands::get_cliente_pacchetto,
            commands::get_cliente_pacchetti,
            // Pacchetto Management (Fase 5 v2)
            commands::delete_pacchetto,
            commands::update_pacchetto,
            commands::get_pacchetto_servizi,
            commands::add_servizio_to_pacchetto,
            commands::remove_servizio_from_pacchetto,
            // WhatsApp Marketing - Invio Pacchetti Selettivo (Fase 8)
            commands::get_clienti_per_invio_whatsapp,
            commands::invia_pacchetto_whatsapp_bulk,
            // Fatturazione Elettronica (Fase 6)
            commands::get_impostazioni_fatturazione,
            commands::update_impostazioni_fatturazione,
            commands::get_fatture,
            commands::get_fattura,
            commands::create_fattura,
            commands::add_riga_fattura,
            commands::delete_riga_fattura,
            commands::emetti_fattura,
            commands::annulla_fattura,
            commands::delete_fattura,
            commands::registra_pagamento,
            commands::get_codici_pagamento,
            commands::get_codici_natura_iva,
            commands::get_fattura_xml,
            commands::invia_sdi_fattura,
            commands::aggiorna_sdi_esito,
            // Voice (Piper TTS - Fase 7)
            commands::check_piper_installed,
            commands::get_piper_status,
            commands::synthesize_speech,
            commands::speak_text,
            commands::cleanup_audio_cache,
            // RAG with Groq LLM (Fase 7)
            commands::load_faqs,
            commands::list_faq_categories,
            commands::rag_answer,
            commands::quick_faq_search,
            commands::test_groq_connection,
            // Setup Wizard (Fase 7 - Onboarding)
            commands::get_setup_status,
            commands::save_setup_config,
            commands::get_setup_config,
            commands::reset_setup,
            commands::test_groq_key,
            // Settings (SMTP, configurazioni runtime)
            commands::get_smtp_settings,
            commands::save_smtp_settings,
            commands::test_smtp_connection,
            // Gmail OAuth2 (P0.6)
            commands::start_gmail_oauth,
            commands::get_gmail_oauth_status,
            commands::disconnect_gmail_oauth,
            commands::get_gmail_fresh_token,
            // Dashboard Statistics
            commands::get_dashboard_stats,
            commands::get_appuntamenti_oggi,
            // FAQ Template System (RAG Locale - Fase 7)
            commands::get_faq_settings,
            commands::update_faq_setting,
            commands::render_faq_template,
            commands::search_faq_local,
            commands::identifica_cliente_whatsapp,
            commands::rag_hybrid_answer, // RAG Ibrido: locale + Groq fallback
            // Voice Agent - Chiamate VoIP (Fase 7)
            commands::inizia_chiamata,
            commands::termina_chiamata,
            commands::get_chiamata,
            commands::get_chiamate_oggi,
            commands::get_storico_chiamate,
            commands::get_voice_config,
            commands::update_voice_config,
            commands::toggle_voice_agent,
            commands::get_voice_stats_oggi,
            commands::get_voice_stats_periodo,
            commands::get_voip_status,
            // Cassa/Incassi (Gestionale puro - RT separato)
            commands::registra_incasso,
            commands::get_incassi_oggi,
            commands::get_incassi_giornata,
            commands::get_report_incassi_periodo,
            commands::chiudi_cassa,
            commands::get_chiusure_cassa,
            commands::get_metodi_pagamento,
            commands::elimina_incasso,
            // Voice Pipeline - Python Voice Agent (Fase 7)
            commands::start_voice_pipeline,
            commands::stop_voice_pipeline,
            commands::get_voice_pipeline_status,
            commands::voice_process_text,
            commands::voice_process_audio,
            commands::voice_greet,
            commands::voice_say,
            commands::voice_reset_conversation,
            commands::get_voice_agent_config,
            // Remote Assistance (Phase 9)
            commands::generate_support_session,
            commands::get_remote_diagnostics,
            commands::execute_diagnostic_command,
            // License System (Phase 8 - Keygen.sh) - Legacy
            commands::get_license_status,
            commands::activate_license,
            commands::deactivate_license,
            commands::validate_license_online,
            commands::get_machine_fingerprint,
            commands::check_feature_access,
            // License System Ed25519 (Phase 8.5) - Offline
            commands::license_ed25519::get_license_status_ed25519,
            commands::license_ed25519::activate_license_ed25519,
            commands::license_ed25519::deactivate_license_ed25519,
            commands::license_ed25519::get_machine_fingerprint_ed25519,
            commands::license_ed25519::check_feature_access_ed25519,
            commands::license_ed25519::check_vertical_access_ed25519,
            commands::license_ed25519::get_tier_info_ed25519,
            commands::license_ed25519::get_license_token_ed25519,
            // Schede Cliente Verticali
            commands::get_scheda_odontoiatrica,
            commands::upsert_scheda_odontoiatrica,
            commands::delete_scheda_odontoiatrica,
            commands::has_scheda_odontoiatrica,
            commands::get_all_schede_odontoiatriche,
            commands::update_odontogramma,
            commands::add_trattamento_to_storia,
            // GDPR Encryption at Rest (Phase 7)
            encryption::gdpr_init_encryption,
            encryption::gdpr_is_ready,
            encryption::gdpr_encrypt,
            encryption::gdpr_decrypt,
            // Audit & GDPR (Fase 8)
            commands::query_audit_logs,
            commands::get_entity_audit_history,
            commands::get_user_audit_activity,
            commands::get_audit_statistics,
            commands::run_gdpr_anonymization,
            commands::cleanup_expired_audit_logs,
            commands::save_gdpr_consent,
            commands::has_art9_consent,
            commands::get_gdpr_settings,
            commands::update_gdpr_setting,
            // Supplier Management (Fase 7.5)
            commands::create_supplier,
            commands::get_supplier,
            commands::list_suppliers,
            commands::update_supplier,
            commands::delete_supplier,
            commands::search_suppliers,
            commands::create_supplier_order,
            commands::get_supplier_order,
            commands::get_supplier_orders,
            commands::list_all_orders,
            commands::update_order_status,
            commands::log_supplier_interaction,
            commands::get_supplier_interactions,
            commands::get_supplier_stats,
            // Schede Cliente Verticali (Fase 9)
            commands::schede_cliente::get_scheda_odontoiatrica,
            commands::schede_cliente::upsert_scheda_odontoiatrica,
            commands::schede_cliente::get_scheda_fisioterapia,
            commands::schede_cliente::upsert_scheda_fisioterapia,
            commands::schede_cliente::get_scheda_estetica,
            commands::schede_cliente::upsert_scheda_estetica,
            commands::schede_cliente::get_scheda_parrucchiere,
            commands::schede_cliente::upsert_scheda_parrucchiere,
            commands::schede_cliente::get_scheda_fitness,
            commands::schede_cliente::upsert_scheda_fitness,
            commands::schede_cliente::get_schede_veicoli,
            commands::schede_cliente::upsert_scheda_veicoli,
            commands::schede_cliente::get_schede_carrozzeria,
            commands::schede_cliente::upsert_scheda_carrozzeria,
            commands::schede_cliente::get_scheda_medica,
            commands::schede_cliente::upsert_scheda_medica,
            // Analytics mensili + PDF Report (Gap #9)
            commands::get_analytics_mensili,
            commands::genera_report_pdf_mensile,
            // Listini Fornitori (Gap #5)
            commands::listini::import_listino,
            commands::listini::get_listini_fornitore,
            commands::listini::get_listino_righe,
            commands::listini::delete_listino,
            commands::listini::get_listino_variazioni,
            // Media Upload (F06 Sprint A)
            commands::save_media_image,
            commands::save_media_video,
            commands::get_cliente_media,
            commands::delete_media,
            commands::read_media_file,
            commands::update_media_consent,
            commands::update_media_note,
            commands::export_media_pdf,
            // MCP Commands (AI Live Testing - debug only)
            #[cfg(debug_assertions)]
            commands::mcp::mcp_ping,
            #[cfg(debug_assertions)]
            commands::mcp::mcp_get_app_info,
            #[cfg(debug_assertions)]
            commands::mcp::mcp_take_screenshot,
            #[cfg(debug_assertions)]
            commands::mcp::mcp_get_dom_content,
            #[cfg(debug_assertions)]
            commands::mcp::mcp_execute_script,
            #[cfg(debug_assertions)]
            commands::mcp::mcp_mouse_click,
            #[cfg(debug_assertions)]
            commands::mcp::mcp_type_text,
            #[cfg(debug_assertions)]
            commands::mcp::mcp_key_press,
            #[cfg(debug_assertions)]
            commands::mcp::mcp_get_local_storage,
            #[cfg(debug_assertions)]
            commands::mcp::mcp_set_local_storage,
            #[cfg(debug_assertions)]
            commands::mcp::mcp_clear_local_storage,
        ])
        // ─── Run Application ───
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

// ─────────────────────────────────────────────────────────────────────
// Tests
// ─────────────────────────────────────────────────────────────────────
#[cfg(test)]
mod tests {
    use super::*;
    use std::path::PathBuf;

    #[test]
    fn detect_cloud_sync_safe_paths() {
        // Default app_data_dir locations should NEVER trigger detection
        let safe = [
            "/Users/mario/Library/Application Support/Fluxion/fluxion.db",
            "/home/mario/.local/share/Fluxion/fluxion.db",
            "C:\\Users\\Mario\\AppData\\Roaming\\Fluxion\\fluxion.db",
            "/var/app/Fluxion/data/fluxion.db",
        ];
        for p in safe {
            let path = PathBuf::from(p);
            assert_eq!(
                detect_cloud_sync_provider(&path),
                None,
                "False positive on safe path: {}",
                p
            );
        }
    }

    #[test]
    fn detect_cloud_sync_icloud() {
        let cases = [
            "/Users/mario/Library/Mobile Documents/com~apple~CloudDocs/Fluxion/fluxion.db",
            "/Users/mario/iCloud Drive/Fluxion/fluxion.db",
        ];
        for p in cases {
            assert_eq!(
                detect_cloud_sync_provider(&PathBuf::from(p)),
                Some("iCloud Drive"),
                "Missed iCloud detection on: {}",
                p
            );
        }
    }

    #[test]
    fn detect_cloud_sync_onedrive() {
        // Personal OneDrive — Win10/11 default install path
        assert_eq!(
            detect_cloud_sync_provider(&PathBuf::from(
                "C:\\Users\\Mario\\OneDrive\\Fluxion\\fluxion.db"
            )),
            Some("OneDrive")
        );
        // OneDrive Business / SharePoint sync (folder name "OneDrive - Acme Spa")
        assert_eq!(
            detect_cloud_sync_provider(&PathBuf::from(
                "/Users/mario/OneDrive - Acme Spa/Fluxion/fluxion.db"
            )),
            Some("OneDrive Business")
        );
    }

    #[test]
    fn detect_cloud_sync_other_providers() {
        let cases = [
            ("/Users/mario/Dropbox/Fluxion/fluxion.db", "Dropbox"),
            ("/Users/mario/Google Drive/Fluxion/fluxion.db", "Google Drive"),
            ("/Users/mario/Box Sync/Fluxion/fluxion.db", "Box"),
            ("/Users/mario/MEGAsync/Fluxion/fluxion.db", "MEGAsync"),
            ("/Users/mario/pCloud/Fluxion/fluxion.db", "pCloud"),
        ];
        for (p, expected) in cases {
            assert_eq!(
                detect_cloud_sync_provider(&PathBuf::from(p)),
                Some(expected),
                "Detection mismatch for: {}",
                p
            );
        }
    }

    #[test]
    fn detect_cloud_sync_case_insensitive() {
        // Real macOS path uses "iCloud Drive" exactly; on Win some users have
        // unusual capitalisation in folder names from manual sync setup
        assert_eq!(
            detect_cloud_sync_provider(&PathBuf::from(
                "/Users/mario/ICLOUD DRIVE/Fluxion/fluxion.db"
            )),
            Some("iCloud Drive")
        );
        assert_eq!(
            detect_cloud_sync_provider(&PathBuf::from(
                "C:\\Users\\Mario\\onedrive\\Fluxion\\fluxion.db"
            )),
            Some("OneDrive")
        );
    }

    #[test]
    fn detect_cloud_sync_no_substring_false_positives() {
        // A file named "backup-onedrive.sql" inside a safe dir must NOT trigger
        let safe_with_keyword = [
            "/Users/mario/Library/Application Support/Fluxion/backup-onedrive.sql",
            "/home/mario/.local/share/Fluxion/dropbox-export.json",
        ];
        for p in safe_with_keyword {
            assert_eq!(
                detect_cloud_sync_provider(&PathBuf::from(p)),
                None,
                "False positive on safe file with keyword in name: {}",
                p
            );
        }
    }
}
