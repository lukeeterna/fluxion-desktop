// ═══════════════════════════════════════════════════════════════════
// FLUXION - Tauri Backend Configuration
// ═══════════════════════════════════════════════════════════════════

use tauri::Manager;

// ───────────────────────────────────────────────────────────────────
// Modules
// ───────────────────────────────────────────────────────────────────

mod commands;
pub mod domain;
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
    let db_url = format!("sqlite:{}?mode=rwc", db_path.display());

    println!("📁 Database path: {}", db_path.display());

    // Create database connection pool
    let pool = sqlx::sqlite::SqlitePoolOptions::new()
        .max_connections(5)
        .connect(&db_url)
        .await?;

    // Enable foreign keys
    sqlx::query("PRAGMA foreign_keys = ON")
        .execute(&pool)
        .await?;

    println!("✅ Database initialized");

    // Run migrations
    println!("🔄 Running migrations...");

    // Run Migration 001: Initial schema
    let migration_001 = include_str!("../migrations/001_init.sql");
    let statements_001 = parse_sql_statements(migration_001);

    for (idx, statement) in statements_001.iter().enumerate() {
        let trimmed = statement.trim();
        if trimmed.is_empty() || trimmed.starts_with("--") {
            continue;
        }

        match sqlx::query(trimmed).execute(&pool).await {
            Ok(_) => {
                if trimmed.starts_with("CREATE TABLE") {
                    let table_name = extract_table_name(trimmed);
                    println!("  ✓ [001] Created table: {}", table_name);
                } else if trimmed.starts_with("CREATE INDEX") {
                    println!("  ✓ [001] Created index");
                } else if trimmed.starts_with("INSERT") {
                    println!("  ✓ [001] Inserted default data");
                }
            }
            Err(e) => {
                let err_msg = e.to_string();
                if !err_msg.contains("already exists") {
                    eprintln!("⚠️  [001] Statement {} failed: {}", idx + 1, err_msg);
                }
            }
        }
    }

    // Run Migration 002: WhatsApp Templates
    let migration_002 = include_str!("../migrations/002_whatsapp_templates.sql");
    let statements_002 = parse_sql_statements(migration_002);

    for (idx, statement) in statements_002.iter().enumerate() {
        let trimmed = statement.trim();
        if trimmed.is_empty() || trimmed.starts_with("--") {
            continue;
        }

        match sqlx::query(trimmed).execute(&pool).await {
            Ok(_) => {
                if trimmed.starts_with("CREATE TABLE") {
                    let table_name = extract_table_name(trimmed);
                    println!("  ✓ [002] Created table: {}", table_name);
                } else if trimmed.starts_with("CREATE INDEX") {
                    println!("  ✓ [002] Created index");
                } else if trimmed.starts_with("INSERT") {
                    // Don't log every template insert
                }
            }
            Err(e) => {
                let err_msg = e.to_string();
                if !err_msg.contains("already exists") {
                    eprintln!("⚠️  [002] Statement {} failed: {}", idx + 1, err_msg);
                }
            }
        }
    }

    println!("  ✓ [002] Seeded WhatsApp templates");

    // Run Migration 003: Orari Lavoro + Festività
    let migration_003 = include_str!("../migrations/003_orari_e_festivita.sql");
    let statements_003 = parse_sql_statements(migration_003);

    for (idx, statement) in statements_003.iter().enumerate() {
        let trimmed = statement.trim();
        if trimmed.is_empty() || trimmed.starts_with("--") {
            continue;
        }

        match sqlx::query(trimmed).execute(&pool).await {
            Ok(_) => {
                if trimmed.starts_with("CREATE TABLE") {
                    let table_name = extract_table_name(trimmed);
                    println!("  ✓ [003] Created table: {}", table_name);
                } else if trimmed.starts_with("CREATE INDEX") {
                    println!("  ✓ [003] Created index");
                } else if trimmed.starts_with("INSERT") {
                    // Don't log every orari/festivi insert
                }
            }
            Err(e) => {
                let err_msg = e.to_string();
                if !err_msg.contains("already exists") {
                    eprintln!("⚠️  [003] Statement {} failed: {}", idx + 1, err_msg);
                }
            }
        }
    }

    println!("  ✓ [003] Seeded orari lavoro + festività");

    // Run Migration 004: Appuntamenti State Machine + Override Info
    let migration_004 = include_str!("../migrations/004_appuntamenti_state_machine.sql");
    let statements_004 = parse_sql_statements(migration_004);

    for (idx, statement) in statements_004.iter().enumerate() {
        let trimmed = statement.trim();
        if trimmed.is_empty() || trimmed.starts_with("--") {
            continue;
        }

        match sqlx::query(trimmed).execute(&pool).await {
            Ok(_) => {
                if trimmed.starts_with("ALTER TABLE") {
                    println!("  ✓ [004] Altered table schema");
                } else if trimmed.starts_with("UPDATE") {
                    println!("  ✓ [004] Migrated existing states");
                } else if trimmed.starts_with("CREATE INDEX") {
                    println!("  ✓ [004] Created index");
                }
            }
            Err(e) => {
                let err_msg = e.to_string();
                // Ignore "duplicate column" errors if migration already run
                if !err_msg.contains("already exists") && !err_msg.contains("duplicate column") {
                    eprintln!("⚠️  [004] Statement {} failed: {}", idx + 1, err_msg);
                }
            }
        }
    }

    println!("  ✓ [004] Appuntamenti state machine ready");

    // Run Migration 005: Loyalty + VIP + Referral + Pacchetti (Fase 5)
    let migration_005 = include_str!("../migrations/005_loyalty_pacchetti_vip.sql");
    let statements_005 = parse_sql_statements(migration_005);

    for (idx, statement) in statements_005.iter().enumerate() {
        let trimmed = statement.trim();
        if trimmed.is_empty() || trimmed.starts_with("--") {
            continue;
        }

        match sqlx::query(trimmed).execute(&pool).await {
            Ok(_) => {
                if trimmed.starts_with("ALTER TABLE") {
                    println!("  ✓ [005] Added loyalty/VIP columns to clienti");
                } else if trimmed.starts_with("CREATE TABLE") {
                    println!("  ✓ [005] Created table");
                } else if trimmed.starts_with("INSERT INTO pacchetti") {
                    println!("  ✓ [005] Seeded demo pacchetti");
                }
            }
            Err(e) => {
                let err_msg = e.to_string();
                // Ignore "already exists" errors if migration already run
                if !err_msg.contains("already exists")
                    && !err_msg.contains("duplicate column")
                    && !err_msg.contains("UNIQUE constraint")
                {
                    eprintln!("⚠️  [005] Statement {} failed: {}", idx + 1, err_msg);
                }
            }
        }
    }

    println!("  ✓ [005] Loyalty + Pacchetti + Waitlist ready");

    // Run Migration 006: Pacchetto Servizi (Many-to-Many)
    let migration_006 = include_str!("../migrations/006_pacchetto_servizi.sql");
    let statements_006 = parse_sql_statements(migration_006);

    for (idx, statement) in statements_006.iter().enumerate() {
        let trimmed = statement.trim();
        if trimmed.is_empty() || trimmed.starts_with("--") {
            continue;
        }

        match sqlx::query(trimmed).execute(&pool).await {
            Ok(_) => {
                if trimmed.to_uppercase().starts_with("CREATE TABLE") {
                    let table_name = extract_table_name(trimmed);
                    println!("  ✓ [006] Created table: {}", table_name);
                }
            }
            Err(e) => {
                let err_msg = e.to_string();
                if !err_msg.contains("already exists")
                    && !err_msg.contains("duplicate column")
                    && !err_msg.contains("UNIQUE constraint")
                {
                    eprintln!("⚠️  [006] Statement {} failed: {}", idx + 1, err_msg);
                }
            }
        }
    }

    println!("  ✓ [006] Pacchetto Servizi ready");

    // Run Migration 007: Fatturazione Elettronica
    let migration_007 = include_str!("../migrations/007_fatturazione_elettronica.sql");
    let statements_007 = parse_sql_statements(migration_007);

    for (idx, statement) in statements_007.iter().enumerate() {
        let trimmed = statement.trim();
        if trimmed.is_empty() || trimmed.starts_with("--") {
            continue;
        }

        match sqlx::query(trimmed).execute(&pool).await {
            Ok(_) => {
                if trimmed.to_uppercase().starts_with("CREATE TABLE") {
                    let table_name = extract_table_name(trimmed);
                    println!("  ✓ [007] Created table: {}", table_name);
                } else if trimmed.to_uppercase().starts_with("INSERT") {
                    // Don't log every insert
                }
            }
            Err(e) => {
                let err_msg = e.to_string();
                if !err_msg.contains("already exists")
                    && !err_msg.contains("duplicate column")
                    && !err_msg.contains("UNIQUE constraint")
                {
                    eprintln!("⚠️  [007] Statement {} failed: {}", idx + 1, err_msg);
                }
            }
        }
    }

    println!("  ✓ [007] Fatturazione Elettronica ready");
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
// Application Entry Point
// ───────────────────────────────────────────────────────────────────

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    // Load .env file for API keys (GROQ_API_KEY, etc.)
    // Try multiple locations: current dir, project root, app data dir
    if let Err(e) = dotenvy::dotenv() {
        eprintln!("⚠️  .env file not found or invalid: {}", e);
        eprintln!("   RAG/Groq features may not work without GROQ_API_KEY");
    } else {
        println!("✅ Environment variables loaded from .env");
    }

    let builder = tauri::Builder::default()
        // ─── Plugin Configuration ───
        .plugin(tauri_plugin_sql::Builder::default().build())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_store::Builder::default().build())
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_process::init());

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

            println!("🚀 Application ready");
            Ok(())
        })
        // ─── Invoke Handler ───
        .invoke_handler(tauri::generate_handler![
            // Clienti
            commands::get_clienti,
            commands::get_cliente,
            commands::create_cliente,
            commands::update_cliente,
            commands::delete_cliente,
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
            // Orari & Festività
            commands::get_orari_lavoro,
            commands::create_orario_lavoro,
            commands::delete_orario_lavoro,
            commands::get_giorni_festivi,
            commands::is_giorno_festivo,
            commands::create_giorno_festivo,
            commands::delete_giorno_festivo,
            commands::valida_orario_appuntamento,
            // Support & Diagnostics (Fluxion Care)
            commands::get_diagnostics_info,
            commands::export_support_bundle,
            commands::backup_database,
            commands::restore_database,
            commands::list_backups,
            commands::delete_backup,
            commands::get_remote_assist_instructions,
            // Loyalty & Pacchetti (Fase 5 - Quick Wins)
            commands::get_loyalty_info,
            commands::increment_loyalty_visits,
            commands::toggle_vip_status,
            commands::set_referral_source,
            commands::get_top_referrers,
            commands::get_loyalty_milestones,
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
            // Voice (Piper TTS - Fase 7)
            commands::check_piper_installed,
            commands::get_piper_status,
            commands::synthesize_speech,
            commands::speak_text,
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
        ])
        // ─── Run Application ───
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
