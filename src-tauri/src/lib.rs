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

    // Run Migration 008: FAQ Template System + Soprannome Cliente
    let migration_008 = include_str!("../migrations/008_faq_template_soprannome.sql");
    let statements_008 = parse_sql_statements(migration_008);

    for (idx, statement) in statements_008.iter().enumerate() {
        let trimmed = statement.trim();
        if trimmed.is_empty() || trimmed.starts_with("--") {
            continue;
        }

        match sqlx::query(trimmed).execute(&pool).await {
            Ok(_) => {
                if trimmed.to_uppercase().starts_with("CREATE TABLE") {
                    let table_name = extract_table_name(trimmed);
                    println!("  ✓ [008] Created table: {}", table_name);
                } else if trimmed.to_uppercase().starts_with("ALTER TABLE") {
                    println!("  ✓ [008] Added soprannome column to clienti");
                } else if trimmed.to_uppercase().starts_with("CREATE INDEX") {
                    println!("  ✓ [008] Created index");
                }
            }
            Err(e) => {
                let err_msg = e.to_string();
                if !err_msg.contains("already exists")
                    && !err_msg.contains("duplicate column")
                    && !err_msg.contains("UNIQUE constraint")
                {
                    eprintln!("⚠️  [008] Statement {} failed: {}", idx + 1, err_msg);
                }
            }
        }
    }

    println!("  ✓ [008] FAQ Template System + Soprannome ready");

    // Run Migration 009: Sistema Cassa/Incassi
    let migration_009 = include_str!("../migrations/009_cassa_incassi.sql");
    let statements_009 = parse_sql_statements(migration_009);

    for (idx, statement) in statements_009.iter().enumerate() {
        let trimmed = statement.trim();
        if trimmed.is_empty() || trimmed.starts_with("--") {
            continue;
        }

        match sqlx::query(trimmed).execute(&pool).await {
            Ok(_) => {
                if trimmed.to_uppercase().starts_with("CREATE TABLE") {
                    let table_name = extract_table_name(trimmed);
                    println!("  ✓ [009] Created table: {}", table_name);
                }
            }
            Err(e) => {
                let err_msg = e.to_string();
                if !err_msg.contains("already exists")
                    && !err_msg.contains("duplicate column")
                    && !err_msg.contains("UNIQUE constraint")
                {
                    eprintln!("⚠️  [009] Statement {} failed: {}", idx + 1, err_msg);
                }
            }
        }
    }

    println!("  ✓ [009] Sistema Cassa/Incassi ready");

    // Run Migration 010: Mock Data (Demo/Testing)
    let migration_010 = include_str!("../migrations/010_mock_data.sql");
    let statements_010 = parse_sql_statements(migration_010);

    for (idx, statement) in statements_010.iter().enumerate() {
        let trimmed = statement.trim();
        if trimmed.is_empty() || trimmed.starts_with("--") {
            continue;
        }

        match sqlx::query(trimmed).execute(&pool).await {
            Ok(_) => {}
            Err(e) => {
                let err_msg = e.to_string();
                if !err_msg.contains("UNIQUE constraint") && !err_msg.contains("already exists") {
                    eprintln!("⚠️  [010] Statement {} failed: {}", idx + 1, err_msg);
                }
            }
        }
    }

    println!("  ✓ [010] Mock data loaded");

    // Run Migration 011: Voice Agent (Fase 7)
    let migration_011 = include_str!("../migrations/011_voice_agent.sql");
    let statements_011 = parse_sql_statements(migration_011);

    for (idx, statement) in statements_011.iter().enumerate() {
        let trimmed = statement.trim();
        if trimmed.is_empty() || trimmed.starts_with("--") {
            continue;
        }

        match sqlx::query(trimmed).execute(&pool).await {
            Ok(_) => {
                if trimmed.to_uppercase().starts_with("CREATE TABLE") {
                    let table_name = extract_table_name(trimmed);
                    println!("  ✓ [011] Created table: {}", table_name);
                }
            }
            Err(e) => {
                let err_msg = e.to_string();
                if !err_msg.contains("already exists")
                    && !err_msg.contains("duplicate column")
                    && !err_msg.contains("UNIQUE constraint")
                {
                    eprintln!("⚠️  [011] Statement {} failed: {}", idx + 1, err_msg);
                }
            }
        }
    }

    println!("  ✓ [011] Voice Agent tables ready");

    // Run Migration 012: Operatori Voice Agent Enhancement
    let migration_012 = include_str!("../migrations/012_operatori_voice_agent.sql");
    let statements_012 = parse_sql_statements(migration_012);

    for (idx, statement) in statements_012.iter().enumerate() {
        let trimmed = statement.trim();
        if trimmed.is_empty() || trimmed.starts_with("--") {
            continue;
        }

        match sqlx::query(trimmed).execute(&pool).await {
            Ok(_) => {
                if trimmed.to_uppercase().starts_with("ALTER TABLE") {
                    println!("  ✓ [012] Added column to operatori");
                }
            }
            Err(e) => {
                let err_msg = e.to_string();
                if !err_msg.contains("already exists") && !err_msg.contains("duplicate column") {
                    eprintln!("⚠️  [012] Statement {} failed: {}", idx + 1, err_msg);
                }
            }
        }
    }

    println!("  ✓ [012] Operatori Voice Agent Enhancement ready");

    // Run Migration 013: Waitlist con Priorità VIP
    let migration_013 = include_str!("../migrations/013_waitlist.sql");
    let statements_013 = parse_sql_statements(migration_013);

    for (idx, statement) in statements_013.iter().enumerate() {
        let trimmed = statement.trim();
        if trimmed.is_empty() || trimmed.starts_with("--") {
            continue;
        }

        match sqlx::query(trimmed).execute(&pool).await {
            Ok(_) => {
                if trimmed.to_uppercase().starts_with("CREATE TABLE") {
                    println!("  ✓ [013] Created table: waitlist");
                } else if trimmed.to_uppercase().starts_with("CREATE INDEX") {
                    println!("  ✓ [013] Created index for waitlist");
                }
            }
            Err(e) => {
                let err_msg = e.to_string();
                if !err_msg.contains("already exists") && !err_msg.contains("duplicate column") {
                    eprintln!("⚠️  [013] Statement {} failed: {}", idx + 1, err_msg);
                }
            }
        }
    }

    println!("  ✓ [013] Waitlist con Priorità VIP ready");

    // Run Migration 015: License System (Phase 8)
    let migration_015 = include_str!("../migrations/015_license_system.sql");
    let statements_015 = parse_sql_statements(migration_015);

    for (idx, statement) in statements_015.iter().enumerate() {
        let trimmed = statement.trim();
        if trimmed.is_empty() || trimmed.starts_with("--") {
            continue;
        }

        match sqlx::query(trimmed).execute(&pool).await {
            Ok(_) => {
                if trimmed.to_uppercase().starts_with("CREATE TABLE") {
                    let table_name = extract_table_name(trimmed);
                    println!("  ✓ [015] Created table: {}", table_name);
                } else if trimmed.to_uppercase().starts_with("CREATE INDEX") {
                    println!("  ✓ [015] Created index");
                }
            }
            Err(e) => {
                let err_msg = e.to_string();
                if !err_msg.contains("already exists") && !err_msg.contains("duplicate column") {
                    eprintln!("⚠️  [015] Statement {} failed: {}", idx + 1, err_msg);
                }
            }
        }
    }

    println!("  ✓ [015] License System ready");

    // Run Migration 016: Supplier Management (Fase 7.5)
    let migration_016 = include_str!("../migrations/016_suppliers.sql");
    let statements_016 = parse_sql_statements(migration_016);

    for (idx, statement) in statements_016.iter().enumerate() {
        let trimmed = statement.trim();
        if trimmed.is_empty() || trimmed.starts_with("--") {
            continue;
        }

        match sqlx::query(trimmed).execute(&pool).await {
            Ok(_) => {
                if trimmed.to_uppercase().starts_with("CREATE TABLE") {
                    let table_name = extract_table_name(trimmed);
                    println!("  ✓ [016] Created table: {}", table_name);
                } else if trimmed.to_uppercase().starts_with("CREATE INDEX") {
                    println!("  ✓ [016] Created index");
                }
            }
            Err(e) => {
                let err_msg = e.to_string();
                if !err_msg.contains("already exists") && !err_msg.contains("duplicate column") {
                    eprintln!("⚠️  [016] Statement {} failed: {}", idx + 1, err_msg);
                }
            }
        }
    }

    println!("  ✓ [016] Supplier Management ready");

    // Run Migration 017: SMTP Settings
    let migration_017 = include_str!("../migrations/017_smtp_settings.sql");
    let statements_017 = parse_sql_statements(migration_017);

    for (idx, statement) in statements_017.iter().enumerate() {
        let trimmed = statement.trim();
        if trimmed.is_empty() || trimmed.starts_with("--") {
            continue;
        }

        match sqlx::query(trimmed).execute(&pool).await {
            Ok(_) => {
                if trimmed.to_uppercase().starts_with("INSERT") {
                    // SMTP settings inserted
                }
            }
            Err(e) => {
                let err_msg = e.to_string();
                if !err_msg.contains("already exists") && !err_msg.contains("UNIQUE constraint") {
                    eprintln!("⚠️  [017] Statement {} failed: {}", idx + 1, err_msg);
                }
            }
        }
    }

    println!("  ✓ [017] SMTP Settings ready");

    // Run Migration 018: GDPR Audit Log System
    let migration_018 = include_str!("../migrations/018_gdpr_audit_logs.sql");
    let statements_018 = parse_sql_statements(migration_018);

    for (idx, statement) in statements_018.iter().enumerate() {
        let trimmed = statement.trim();
        if trimmed.is_empty() || trimmed.starts_with("--") {
            continue;
        }

        match sqlx::query(trimmed).execute(&pool).await {
            Ok(_) => {
                if trimmed.to_uppercase().starts_with("CREATE TABLE") {
                    let table_name = extract_table_name(trimmed);
                    println!("  ✓ [018] Created table: {}", table_name);
                } else if trimmed.to_uppercase().starts_with("CREATE INDEX") {
                    println!("  ✓ [018] Created index");
                } else if trimmed.to_uppercase().starts_with("CREATE VIEW") {
                    println!("  ✓ [018] Created view");
                } else if trimmed.to_uppercase().starts_with("INSERT") {
                    // Settings inserted
                }
            }
            Err(e) => {
                let err_msg = e.to_string();
                if !err_msg.contains("already exists") && !err_msg.contains("duplicate column") {
                    eprintln!("⚠️  [018] Statement {} failed: {}", idx + 1, err_msg);
                }
            }
        }
    }

    println!("  ✓ [018] GDPR Audit Log System ready");

    // Run Migration 019: Schede Clienti Verticali
    let migration_019 = include_str!("../migrations/019_schede_clienti_verticali.sql");
    let statements_019 = parse_sql_statements(migration_019);

    for (idx, statement) in statements_019.iter().enumerate() {
        let trimmed = statement.trim();
        if trimmed.is_empty() || trimmed.starts_with("--") {
            continue;
        }

        match sqlx::query(trimmed).execute(&pool).await {
            Ok(_) => {
                if trimmed.to_uppercase().starts_with("CREATE TABLE") {
                    let table_name = extract_table_name(trimmed);
                    println!("  ✓ [019] Created table: {}", table_name);
                } else if trimmed.to_uppercase().starts_with("CREATE INDEX") {
                    println!("  ✓ [019] Created index");
                } else if trimmed.to_uppercase().starts_with("INSERT") {
                    println!("  ✓ [019] Inserted settings");
                }
            }
            Err(e) => {
                let err_msg = e.to_string();
                if !err_msg.contains("already exists") && !err_msg.contains("duplicate column") {
                    eprintln!("⚠️  [019] Statement {} failed: {}", idx + 1, err_msg);
                }
            }
        }
    }

    println!("  ✓ [019] Schede Clienti Verticali ready");

    // Run Migration 020: License System Ed25519
    let migration_020 = include_str!("../migrations/020_license_ed25519.sql");
    let statements_020 = parse_sql_statements(migration_020);

    for (idx, statement) in statements_020.iter().enumerate() {
        let trimmed = statement.trim();
        if trimmed.is_empty() || trimmed.starts_with("--") {
            continue;
        }

        match sqlx::query(trimmed).execute(&pool).await {
            Ok(_) => {
                if trimmed.to_uppercase().starts_with("ALTER TABLE") {
                    println!("  ✓ [020] Altered table schema");
                } else if trimmed.to_uppercase().starts_with("CREATE INDEX") {
                    println!("  ✓ [020] Created index");
                }
            }
            Err(e) => {
                let err_msg = e.to_string();
                if !err_msg.contains("already exists") && !err_msg.contains("duplicate column") {
                    eprintln!("⚠️  [020] Statement {} failed: {}", idx + 1, err_msg);
                }
            }
        }
    }

    println!("  ✓ [020] License System Ed25519 ready");

    // ── Migration 021 ─────────────────────────────────────────────
    let migration_021 = include_str!("../migrations/021_setup_config.sql");
    let statements_021 = parse_sql_statements(migration_021);
    for (idx, statement) in statements_021.iter().enumerate() {
        let trimmed = statement.trim();
        if trimmed.is_empty() || trimmed.starts_with("--") {
            continue;
        }
        match sqlx::query(trimmed).execute(&pool).await {
            Ok(_) => {}
            Err(e) => {
                let err_msg = e.to_string();
                if !err_msg.contains("already exists") && !err_msg.contains("duplicate column") {
                    eprintln!("⚠️  [021] Statement {} failed: {}", idx + 1, err_msg);
                }
            }
        }
    }
    println!("  ✓ [021] Setup Config ready");

    // ── Migration 022 ─────────────────────────────────────────────
    let migration_022 = include_str!("../migrations/022_whatsapp_invii_pacchetti.sql");
    let statements_022 = parse_sql_statements(migration_022);
    for (idx, statement) in statements_022.iter().enumerate() {
        let trimmed = statement.trim();
        if trimmed.is_empty() || trimmed.starts_with("--") {
            continue;
        }
        match sqlx::query(trimmed).execute(&pool).await {
            Ok(_) => {}
            Err(e) => {
                let err_msg = e.to_string();
                if !err_msg.contains("already exists") && !err_msg.contains("duplicate column") {
                    eprintln!("⚠️  [022] Statement {} failed: {}", idx + 1, err_msg);
                }
            }
        }
    }
    println!("  ✓ [022] WhatsApp Invii Pacchetti ready");

    // ── Migration 023 ─────────────────────────────────────────────
    let migration_023 = include_str!("../migrations/023_groq_setup.sql");
    let statements_023 = parse_sql_statements(migration_023);
    for (idx, statement) in statements_023.iter().enumerate() {
        let trimmed = statement.trim();
        if trimmed.is_empty() || trimmed.starts_with("--") {
            continue;
        }
        match sqlx::query(trimmed).execute(&pool).await {
            Ok(_) => {}
            Err(e) => {
                let err_msg = e.to_string();
                if !err_msg.contains("already exists") && !err_msg.contains("duplicate column") {
                    eprintln!("⚠️  [023] Statement {} failed: {}", idx + 1, err_msg);
                }
            }
        }
    }
    println!("  ✓ [023] Groq Setup ready");

    // ── Migration 024 ─────────────────────────────────────────────
    let migration_024 = include_str!("../migrations/024_operatori_features.sql");
    let statements_024 = parse_sql_statements(migration_024);
    for (idx, statement) in statements_024.iter().enumerate() {
        let trimmed = statement.trim();
        if trimmed.is_empty() || trimmed.starts_with("--") {
            continue;
        }
        match sqlx::query(trimmed).execute(&pool).await {
            Ok(_) => {}
            Err(e) => {
                let err_msg = e.to_string();
                if !err_msg.contains("already exists") && !err_msg.contains("duplicate column") {
                    eprintln!("⚠️  [024] Statement {} failed: {}", idx + 1, err_msg);
                }
            }
        }
    }
    println!("  ✓ [024] Operatori Features (assenze, KPI) ready");

    // ── Migration 025 ─────────────────────────────────────────────
    let migration_025 = include_str!("../migrations/025_operatori_commissioni.sql");
    let statements_025 = parse_sql_statements(migration_025);
    for (idx, statement) in statements_025.iter().enumerate() {
        let trimmed = statement.trim();
        if trimmed.is_empty() || trimmed.starts_with("--") {
            continue;
        }
        match sqlx::query(trimmed).execute(&pool).await {
            Ok(_) => {}
            Err(e) => {
                let err_msg = e.to_string();
                if !err_msg.contains("already exists") && !err_msg.contains("duplicate column") {
                    eprintln!("⚠️  [025] Statement {} failed: {}", idx + 1, err_msg);
                }
            }
        }
    }
    println!("  ✓ [025] Operatori Commissioni ready");

    // ── Migration 026 ─────────────────────────────────────────────
    let migration_026 = include_str!("../migrations/026_impostazioni_sdi_key.sql");
    let statements_026 = parse_sql_statements(migration_026);
    for (idx, statement) in statements_026.iter().enumerate() {
        let trimmed = statement.trim();
        if trimmed.is_empty() || trimmed.starts_with("--") {
            continue;
        }
        match sqlx::query(trimmed).execute(&pool).await {
            Ok(_) => {}
            Err(e) => {
                let err_msg = e.to_string();
                if !err_msg.contains("already exists") && !err_msg.contains("duplicate column") {
                    eprintln!("⚠️  [026] Statement {} failed: {}", idx + 1, err_msg);
                }
            }
        }
    }
    println!("  ✓ [026] Impostazioni SDI Key ready");

    // ── Migration 027 ─────────────────────────────────────────────
    let migration_027 = include_str!("../migrations/027_scheda_fitness.sql");
    let statements_027 = parse_sql_statements(migration_027);
    for (idx, statement) in statements_027.iter().enumerate() {
        let trimmed = statement.trim();
        if trimmed.is_empty() || trimmed.starts_with("--") {
            continue;
        }
        match sqlx::query(trimmed).execute(&pool).await {
            Ok(_) => {}
            Err(e) => {
                let err_msg = e.to_string();
                if !err_msg.contains("already exists") && !err_msg.contains("duplicate column") {
                    eprintln!("⚠️  [027] Statement {} failed: {}", idx + 1, err_msg);
                }
            }
        }
    }
    println!("  ✓ [027] Scheda Fitness ready");

    // ── Migration 028 ─────────────────────────────────────────────
    let migration_028 = include_str!("../migrations/028_scheda_medica.sql");
    let statements_028 = parse_sql_statements(migration_028);
    for (idx, statement) in statements_028.iter().enumerate() {
        let trimmed = statement.trim();
        if trimmed.is_empty() || trimmed.starts_with("--") {
            continue;
        }
        match sqlx::query(trimmed).execute(&pool).await {
            Ok(_) => {}
            Err(e) => {
                let err_msg = e.to_string();
                if !err_msg.contains("already exists") && !err_msg.contains("duplicate column") {
                    eprintln!("⚠️  [028] Statement {} failed: {}", idx + 1, err_msg);
                }
            }
        }
    }
    println!("  ✓ [028] Scheda Medica ready");

    // ── Migration 029 ─────────────────────────────────────────────
    let migration_029 = include_str!("../migrations/029_sdi_multi_provider.sql");
    let statements_029 = parse_sql_statements(migration_029);
    for (idx, statement) in statements_029.iter().enumerate() {
        let trimmed = statement.trim();
        if trimmed.is_empty() || trimmed.starts_with("--") {
            continue;
        }
        match sqlx::query(trimmed).execute(&pool).await {
            Ok(_) => {}
            Err(e) => {
                let err_msg = e.to_string();
                if !err_msg.contains("already exists") && !err_msg.contains("duplicate column") {
                    eprintln!("⚠️  [029] Statement {} failed: {}", idx + 1, err_msg);
                }
            }
        }
    }
    println!("  ✓ [029] SDI Multi-Provider (Aruba + OpenAPI) ready");

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

    let builder = tauri::Builder::default()
        // ─── Plugin Configuration ───
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_store::Builder::default().build())
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_process::init());

    // ─── MCP Server Plugin (Remote Debugging via Claude Code / Cursor) ───
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

            // Auto-start WhatsApp service (non-blocking)
            // Will gracefully skip if Node.js or dependencies not available
            commands::whatsapp::auto_start_whatsapp(app.handle());

            // Start HTTP Bridge for MCP integration (Live Testing)
            // This enables Claude Code / MCP Server to interact with the app
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
            // Settings (SMTP, configurazioni runtime)
            commands::get_smtp_settings,
            commands::save_smtp_settings,
            commands::test_smtp_connection,
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
