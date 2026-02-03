// ═══════════════════════════════════════════════════════════════════
// FLUXION - Audit Commands
// Tauri commands for GDPR-compliant audit logging
// Pattern: Command → Service → Repository
// ═══════════════════════════════════════════════════════════════════

use std::sync::Arc;

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use serde::Serialize as SerializeTrait;
use tauri::State;

use crate::{
    domain::audit::{AuditAction, AuditLog, AuditLogQuery, AuditSource, GdprCategory, UserType},
    infra::repositories::audit_repository::SqliteAuditLogRepository,
    services::audit_service::{AuditService, AuditStatistics},
    AppState,
};

pub type CmdResult<T> = Result<T, String>;

// ═══════════════════════════════════════════════════════════════════
// DTOs
// ═══════════════════════════════════════════════════════════════════

#[derive(Debug, Serialize)]
pub struct AuditLogDto {
    pub id: String,
    pub timestamp: String,
    pub user_id: Option<String>,
    pub user_type: String,
    pub action: String,
    pub entity_type: String,
    pub entity_id: String,
    pub changed_fields: Option<Vec<String>>,
    pub gdpr_category: String,
    pub source: String,
}

impl From<AuditLog> for AuditLogDto {
    fn from(log: AuditLog) -> Self {
        Self {
            id: log.id,
            timestamp: log.timestamp.to_rfc3339(),
            user_id: log.user_id,
            user_type: format!("{:?}", log.user_type).to_lowercase(),
            action: format!("{:?}", log.action).to_uppercase(),
            entity_type: log.entity_type,
            entity_id: log.entity_id,
            changed_fields: log
                .changed_fields
                .as_ref()
                .and_then(|f| serde_json::from_str(f).ok()),
            gdpr_category: format!("{:?}", log.gdpr_category).to_lowercase(),
            source: format!("{:?}", log.source).to_lowercase(),
        }
    }
}

#[derive(Debug, Serialize)]
pub struct GdprStatisticsDto {
    pub total_operations: i64,
    pub by_category: std::collections::HashMap<String, i64>,
    pub by_source: std::collections::HashMap<String, i64>,
    pub by_action: std::collections::HashMap<String, i64>,
    pub records_needing_anonymization: i64,
}

impl From<AuditStatistics> for GdprStatisticsDto {
    fn from(stats: AuditStatistics) -> Self {
        let mut by_action = std::collections::HashMap::new();
        by_action.insert("CREATE".to_string(), stats.create_count);
        by_action.insert("UPDATE".to_string(), stats.update_count);
        by_action.insert("DELETE".to_string(), stats.delete_count);
        by_action.insert("VIEW".to_string(), stats.view_count);

        Self {
            total_operations: stats.total_logs,
            by_category: stats.by_gdpr_category,
            by_source: stats.by_source,
            by_action,
            records_needing_anonymization: 0, // Calcolato separatamente
        }
    }
}

#[derive(Debug, Serialize)]
pub struct AnonymizationResultDto {
    pub records_anonymized: usize,
    pub errors: Vec<String>,
}

#[derive(Debug, Serialize)]
pub struct GdprSettingDto {
    pub key: String,
    pub value: String,
    pub updated_at: String,
}

#[derive(sqlx::FromRow)]
struct GdprSettingRow {
    key: String,
    value: String,
    updated_at: String,
}

#[derive(Debug, Deserialize)]
pub struct AuditQueryFilters {
    pub entity_type: Option<String>,
    pub entity_id: Option<String>,
    pub user_id: Option<String>,
    pub action: Option<String>,
    pub category: Option<String>,
    pub date_from: Option<DateTime<Utc>>,
    pub date_to: Option<DateTime<Utc>>,
    pub limit: Option<i64>,
    pub offset: Option<i64>,
}

// ═══════════════════════════════════════════════════════════════════
// Helper Functions
// ═══════════════════════════════════════════════════════════════════

/// Create audit service instance
fn create_audit_service(state: &AppState) -> AuditService {
    let repo = Arc::new(SqliteAuditLogRepository::new(state.db.clone())) as Arc<_>;
    AuditService::new(repo)
}

/// Parse action string to AuditAction
fn parse_action(action: &str) -> AuditAction {
    match action {
        "CREATE" => AuditAction::Create,
        "UPDATE" => AuditAction::Update,
        "DELETE" => AuditAction::Delete,
        "VIEW" => AuditAction::View,
        "EXPORT" => AuditAction::Export,
        "ANONYMIZE" => AuditAction::Anonymize,
        "LOGIN" => AuditAction::Login,
        "LOGOUT" => AuditAction::Logout,
        _ => AuditAction::View,
    }
}

/// Parse GDPR category string to GdprCategory
fn parse_category(category: &str) -> GdprCategory {
    match category {
        "personal_data" => GdprCategory::PersonalData,
        "consent" => GdprCategory::Consent,
        "booking" => GdprCategory::Booking,
        "voice_session" => GdprCategory::VoiceSession,
        _ => GdprCategory::PersonalData,
    }
}

// ═══════════════════════════════════════════════════════════════════
// QUERY COMMANDS
// ═══════════════════════════════════════════════════════════════════

/// Get audit logs with filters
#[tauri::command]
pub async fn query_audit_logs(
    state: State<'_, AppState>,
    filters: AuditQueryFilters,
) -> CmdResult<Vec<AuditLogDto>> {
    let service = create_audit_service(&state);

    let query = AuditLogQuery {
        entity_type: filters.entity_type,
        entity_id: filters.entity_id,
        user_id: filters.user_id,
        action: filters.action.map(|a| parse_action(&a)),
        gdpr_category: filters.category.map(|c| parse_category(&c)),
        source: None,
        from_date: filters.date_from,
        to_date: filters.date_to,
        limit: filters.limit,
        offset: filters.offset,
    };

    service
        .query(&query)
        .await
        .map(|logs| logs.into_iter().map(AuditLogDto::from).collect())
        .map_err(|e| e.to_string())
}

/// Get entity history
#[tauri::command]
pub async fn get_entity_audit_history(
    state: State<'_, AppState>,
    entity_type: String,
    entity_id: String,
    limit: Option<i64>,
) -> CmdResult<Vec<AuditLogDto>> {
    let service = create_audit_service(&state);

    service
        .get_entity_history(&entity_type, &entity_id, limit.unwrap_or(100))
        .await
        .map(|logs| logs.into_iter().map(AuditLogDto::from).collect())
        .map_err(|e| e.to_string())
}

/// Get user activity
#[tauri::command]
pub async fn get_user_audit_activity(
    state: State<'_, AppState>,
    user_id: String,
    limit: Option<i64>,
) -> CmdResult<Vec<AuditLogDto>> {
    let service = create_audit_service(&state);

    service
        .get_user_activity(&user_id, limit.unwrap_or(100))
        .await
        .map(|logs| logs.into_iter().map(AuditLogDto::from).collect())
        .map_err(|e| e.to_string())
}

/// Get audit statistics
#[tauri::command]
pub async fn get_audit_statistics(
    state: State<'_, AppState>,
    date_from: Option<DateTime<Utc>>,
    date_to: Option<DateTime<Utc>>,
) -> CmdResult<GdprStatisticsDto> {
    let service = create_audit_service(&state);

    let start = date_from.unwrap_or_else(|| Utc::now() - chrono::Duration::days(30));
    let end = date_to.unwrap_or_else(|| Utc::now());

    let stats = service.get_statistics(start, end).await.map_err(|e| e.to_string())?;

    let dto = GdprStatisticsDto::from(stats);

    Ok(dto)
}

// ═══════════════════════════════════════════════════════════════════
// GDPR COMPLIANCE COMMANDS
// ═══════════════════════════════════════════════════════════════════

/// Trigger manual GDPR anonymization
#[tauri::command]
pub async fn run_gdpr_anonymization(state: State<'_, AppState>) -> CmdResult<AnonymizationResultDto> {
    let service = create_audit_service(&state);

    service
        .run_gdpr_anonymization()
        .await
        .map(|count| AnonymizationResultDto {
            records_anonymized: count,
            errors: vec![],
        })
        .map_err(|e| e.to_string())
}

/// Cleanup expired audit logs
#[tauri::command]
pub async fn cleanup_expired_audit_logs(
    state: State<'_, AppState>,
    retention_buffer_days: Option<i64>,
) -> CmdResult<u64> {
    let service = create_audit_service(&state);

    service
        .cleanup_expired_logs(retention_buffer_days.unwrap_or(30))
        .await
        .map_err(|e| e.to_string())
}

/// Get GDPR settings
#[tauri::command]
pub async fn get_gdpr_settings(state: State<'_, AppState>) -> CmdResult<Vec<GdprSettingDto>> {
    let settings = sqlx::query_as!(
        GdprSettingRow,
        r#"SELECT key, value, updated_at FROM gdpr_settings"#
    )
    .fetch_all(&state.db)
    .await
    .map_err(|e| e.to_string())?;

    Ok(settings
        .into_iter()
        .map(|s| GdprSettingDto {
            key: s.key,
            value: s.value,
            updated_at: s.updated_at,
        })
        .collect())
}

/// Update GDPR setting
#[tauri::command]
pub async fn update_gdpr_setting(
    state: State<'_, AppState>,
    key: String,
    value: String,
) -> CmdResult<()> {
    sqlx::query!(
        r#"INSERT INTO gdpr_settings (key, value, updated_at) 
           VALUES (?, ?, datetime('now'))
           ON CONFLICT(key) DO UPDATE SET 
           value = excluded.value, 
           updated_at = excluded.updated_at"#,
        key,
        value
    )
    .execute(&state.db)
    .await
    .map_err(|e| e.to_string())?;

    Ok(())
}

// ═══════════════════════════════════════════════════════════════════
// AUDIT LOGGING HELPERS (for use by other commands)
// ═══════════════════════════════════════════════════════════════════

/// Log a create action (helper for other commands)
pub async fn log_create<T: SerializeTrait>(
    state: &AppState,
    user_id: Option<String>,
    entity_type: &str,
    entity_id: &str,
    data: &T,
) -> Result<(), String> {
    let service = create_audit_service(state);

    service
        .log_create(
            user_id,
            UserType::Operator,
            entity_type,
            entity_id,
            data,
            AuditSource::Web,
            GdprCategory::PersonalData,
        )
        .await
        .map_err(|e| e.to_string())?;

    Ok(())
}

/// Log an update action (helper for other commands)
pub async fn log_update<T: SerializeTrait>(
    state: &AppState,
    user_id: Option<String>,
    entity_type: &str,
    entity_id: &str,
    data_before: &T,
    data_after: &T,
) -> Result<(), String> {
    let service = create_audit_service(state);

    service
        .log_update(
            user_id,
            UserType::Operator,
            entity_type,
            entity_id,
            data_before,
            data_after,
            AuditSource::Web,
            GdprCategory::PersonalData,
        )
        .await
        .map_err(|e| e.to_string())?;

    Ok(())
}

/// Log a delete action (helper for other commands)
pub async fn log_delete<T: SerializeTrait>(
    state: &AppState,
    user_id: Option<String>,
    entity_type: &str,
    entity_id: &str,
    data_before: &T,
) -> Result<(), String> {
    let service = create_audit_service(state);

    service
        .log_delete(
            user_id,
            UserType::Operator,
            entity_type,
            entity_id,
            data_before,
            AuditSource::Web,
            GdprCategory::PersonalData,
        )
        .await
        .map_err(|e| e.to_string())?;

    Ok(())
}

/// Log a view action (helper for other commands)
pub async fn log_view(
    state: &AppState,
    user_id: Option<String>,
    entity_type: &str,
    entity_id: &str,
) -> Result<(), String> {
    let service = create_audit_service(state);

    service
        .log_view(
            user_id,
            UserType::Operator,
            entity_type,
            entity_id,
            AuditSource::Web,
            GdprCategory::PersonalData,
        )
        .await
        .map_err(|e| e.to_string())?;

    Ok(())
}
