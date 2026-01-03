// ═══════════════════════════════════════════════════════════════════
// FLUXION - WhatsApp Commands
// Template library + variable replacement (zero-cost wa.me approach)
// ═══════════════════════════════════════════════════════════════════

use serde::{Deserialize, Serialize};
use sqlx::{Row, SqlitePool};
use std::collections::HashMap;
use tauri::State;

// ───────────────────────────────────────────────────────────────────
// Types
// ───────────────────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct WhatsAppTemplate {
    pub id: String,
    pub nome: String,
    pub categoria: String,
    pub descrizione: Option<String>,
    pub template_text: String,
    pub variabili: Option<String>,  // JSON array
    pub predefinito: i64,
    pub attivo: i64,
    pub uso_count: i64,
    pub ultimo_uso: Option<String>,
    pub created_at: String,
    pub updated_at: String,
}

#[derive(Debug, Deserialize)]
pub struct CreateWhatsAppTemplateInput {
    pub nome: String,
    pub categoria: String,
    pub descrizione: Option<String>,
    pub template_text: String,
    pub variabili: Option<Vec<String>>,
}

#[derive(Debug, Deserialize)]
pub struct UpdateWhatsAppTemplateInput {
    pub nome: Option<String>,
    pub categoria: Option<String>,
    pub descrizione: Option<String>,
    pub template_text: Option<String>,
    pub variabili: Option<Vec<String>>,
    pub attivo: Option<i64>,
}

#[derive(Debug, Deserialize)]
pub struct FillTemplateInput {
    pub template_id: String,
    pub variables: HashMap<String, String>,
}

// ───────────────────────────────────────────────────────────────────
// Helper Functions
// ───────────────────────────────────────────────────────────────────

/// Replace {{variabili}} in template text with actual values
fn fill_template_variables(template_text: &str, variables: &HashMap<String, String>) -> String {
    let mut result = template_text.to_string();

    for (key, value) in variables.iter() {
        let placeholder = format!("{{{{{}}}}}", key);
        result = result.replace(&placeholder, value);
    }

    // Handle conditional lines (e.g., {{operatore_line}})
    // If operatore is present → show line, else remove
    if variables.contains_key("operatore") && !variables["operatore"].is_empty() {
        result = result.replace(
            "{{operatore_line}}",
            &format!("👤 Con: {}\n", variables["operatore"])
        );
    } else {
        result = result.replace("{{operatore_line}}", "");
    }

    result
}

// ───────────────────────────────────────────────────────────────────
// Commands
// ───────────────────────────────────────────────────────────────────

/// Get WhatsApp templates, optionally filtered by categoria
#[tauri::command]
pub async fn get_whatsapp_templates(
    pool: State<'_, SqlitePool>,
    categoria: Option<String>,
) -> Result<Vec<WhatsAppTemplate>, String> {
    let mut query = String::from(
        r#"
        SELECT * FROM whatsapp_templates
        WHERE attivo = 1
        "#
    );

    let mut bindings: Vec<String> = Vec::new();

    if let Some(cat) = categoria {
        query.push_str(" AND categoria = ?");
        bindings.push(cat);
    }

    query.push_str(" ORDER BY predefinito DESC, nome ASC");

    let mut q = sqlx::query(&query);
    for binding in bindings {
        q = q.bind(binding);
    }

    let rows = q
        .fetch_all(pool.inner())
        .await
        .map_err(|e| format!("Failed to fetch templates: {}", e))?;

    let mut result = Vec::new();
    for row in rows {
        result.push(WhatsAppTemplate {
            id: row.try_get("id").unwrap(),
            nome: row.try_get("nome").unwrap(),
            categoria: row.try_get("categoria").unwrap(),
            descrizione: row.try_get("descrizione").ok(),
            template_text: row.try_get("template_text").unwrap(),
            variabili: row.try_get("variabili").ok(),
            predefinito: row.try_get("predefinito").unwrap(),
            attivo: row.try_get("attivo").unwrap(),
            uso_count: row.try_get("uso_count").unwrap(),
            ultimo_uso: row.try_get("ultimo_uso").ok(),
            created_at: row.try_get("created_at").unwrap(),
            updated_at: row.try_get("updated_at").unwrap(),
        });
    }

    Ok(result)
}

/// Get single template by ID
#[tauri::command]
pub async fn get_whatsapp_template(
    pool: State<'_, SqlitePool>,
    id: String,
) -> Result<WhatsAppTemplate, String> {
    sqlx::query_as::<_, WhatsAppTemplate>("SELECT * FROM whatsapp_templates WHERE id = ?")
        .bind(id)
        .fetch_one(pool.inner())
        .await
        .map_err(|e| format!("Template not found: {}", e))
}

/// Create custom WhatsApp template
#[tauri::command]
pub async fn create_whatsapp_template(
    pool: State<'_, SqlitePool>,
    input: CreateWhatsAppTemplateInput,
) -> Result<WhatsAppTemplate, String> {
    let id = uuid::Uuid::new_v4().to_string();
    let now = chrono::Utc::now().to_rfc3339();

    // Serialize variabili to JSON
    let variabili_json = match input.variabili {
        Some(vars) => Some(serde_json::to_string(&vars).unwrap()),
        None => None,
    };

    sqlx::query(
        r#"
        INSERT INTO whatsapp_templates (
            id, nome, categoria, descrizione, template_text, variabili,
            predefinito, attivo, uso_count, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, 0, 1, 0, ?, ?)
        "#,
    )
    .bind(&id)
    .bind(&input.nome)
    .bind(&input.categoria)
    .bind(&input.descrizione)
    .bind(&input.template_text)
    .bind(&variabili_json)
    .bind(&now)
    .bind(&now)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Failed to create template: {}", e))?;

    get_whatsapp_template(pool, id).await
}

/// Update WhatsApp template
#[tauri::command]
pub async fn update_whatsapp_template(
    pool: State<'_, SqlitePool>,
    id: String,
    input: UpdateWhatsAppTemplateInput,
) -> Result<WhatsAppTemplate, String> {
    let now = chrono::Utc::now().to_rfc3339();

    // Fetch current template
    let current = get_whatsapp_template(pool.clone(), id.clone()).await?;

    // Serialize variabili if provided
    let variabili_json = match input.variabili {
        Some(vars) => Some(serde_json::to_string(&vars).unwrap()),
        None => current.variabili,
    };

    sqlx::query(
        r#"
        UPDATE whatsapp_templates SET
            nome = ?, categoria = ?, descrizione = ?, template_text = ?,
            variabili = ?, attivo = ?, updated_at = ?
        WHERE id = ?
        "#,
    )
    .bind(input.nome.unwrap_or(current.nome))
    .bind(input.categoria.unwrap_or(current.categoria))
    .bind(input.descrizione.or(current.descrizione))
    .bind(input.template_text.unwrap_or(current.template_text))
    .bind(variabili_json)
    .bind(input.attivo.unwrap_or(current.attivo))
    .bind(&now)
    .bind(&id)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Failed to update template: {}", e))?;

    get_whatsapp_template(pool, id).await
}

/// Delete template (soft delete: attivo = 0)
#[tauri::command]
pub async fn delete_whatsapp_template(
    pool: State<'_, SqlitePool>,
    id: String,
) -> Result<(), String> {
    let now = chrono::Utc::now().to_rfc3339();

    sqlx::query("UPDATE whatsapp_templates SET attivo = 0, updated_at = ? WHERE id = ?")
        .bind(&now)
        .bind(&id)
        .execute(pool.inner())
        .await
        .map_err(|e| format!("Failed to delete template: {}", e))?;

    Ok(())
}

/// Fill template with variable values and track usage
#[tauri::command]
pub async fn fill_whatsapp_template(
    pool: State<'_, SqlitePool>,
    input: FillTemplateInput,
) -> Result<String, String> {
    // Fetch template
    let template = get_whatsapp_template(pool.clone(), input.template_id.clone()).await?;

    // Fill variables
    let filled_message = fill_template_variables(&template.template_text, &input.variables);

    // Update usage stats
    let now = chrono::Utc::now().to_rfc3339();
    sqlx::query(
        "UPDATE whatsapp_templates SET uso_count = uso_count + 1, ultimo_uso = ? WHERE id = ?"
    )
    .bind(&now)
    .bind(&input.template_id)
    .execute(pool.inner())
    .await
    .ok(); // Ignore error (non-critical)

    Ok(filled_message)
}
