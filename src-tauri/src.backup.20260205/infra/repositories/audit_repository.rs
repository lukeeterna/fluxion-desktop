//! Audit Log Repository
//!
//! SQLite implementation of the AuditLogRepository trait.

use async_trait::async_trait;
use chrono::{DateTime, Utc};
use sqlx::SqlitePool;

use crate::domain::audit::{AuditLog, AuditLogQuery, AuditSource, GdprCategory, UserType};
use crate::domain::RepositoryError;

/// Repository trait for Audit Log operations
#[async_trait]
pub trait AuditLogRepository: Send + Sync {
    /// Save a new audit log entry
    async fn save(&self, audit_log: &AuditLog) -> Result<(), RepositoryError>;

    /// Find audit log by ID
    async fn find_by_id(&self, id: &str) -> Result<Option<AuditLog>, RepositoryError>;

    /// Query audit logs with filters
    async fn query(&self, query: &AuditLogQuery) -> Result<Vec<AuditLog>, RepositoryError>;

    /// Count audit logs matching query
    async fn count(&self, query: &AuditLogQuery) -> Result<i64, RepositoryError>;

    /// Get audit logs for a specific entity
    async fn find_by_entity(
        &self,
        entity_type: &str,
        entity_id: &str,
        limit: i64,
    ) -> Result<Vec<AuditLog>, RepositoryError>;

    /// Get audit logs by user
    async fn find_by_user(
        &self,
        user_id: &str,
        limit: i64,
    ) -> Result<Vec<AuditLog>, RepositoryError>;

    /// Get audit logs within a date range
    async fn find_by_date_range(
        &self,
        start: DateTime<Utc>,
        end: DateTime<Utc>,
        limit: i64,
    ) -> Result<Vec<AuditLog>, RepositoryError>;

    /// Mark audit log as anonymized (GDPR compliance)
    async fn mark_anonymized(&self, id: &str) -> Result<(), RepositoryError>;

    /// Get all audit logs that need anonymization
    async fn find_needing_anonymization(&self) -> Result<Vec<AuditLog>, RepositoryError>;

    /// Delete old audit logs (after retention period and anonymization)
    async fn delete_expired(&self, before: DateTime<Utc>) -> Result<u64, RepositoryError>;
}

/// SQLite implementation of AuditLogRepository
pub struct SqliteAuditLogRepository {
    pool: SqlitePool,
}

impl SqliteAuditLogRepository {
    pub fn new(pool: SqlitePool) -> Self {
        Self { pool }
    }

    /// Convert UserType to database string
    fn user_type_to_db(user_type: UserType) -> String {
        match user_type {
            UserType::VoiceSession => "voice_session",
            UserType::Operator => "operator",
            UserType::System => "system",
        }
        .to_string()
    }

    /// Convert database string to UserType
    fn user_type_from_db(s: &str) -> Result<UserType, RepositoryError> {
        match s {
            "voice_session" => Ok(UserType::VoiceSession),
            "operator" => Ok(UserType::Operator),
            "system" => Ok(UserType::System),
            _ => Err(RepositoryError::Serialization(format!(
                "Invalid user_type: {}",
                s
            ))),
        }
    }

    /// Convert AuditSource to database string
    fn source_to_db(source: AuditSource) -> String {
        match source {
            AuditSource::Voice => "voice",
            AuditSource::Web => "web",
            AuditSource::Api => "api",
            AuditSource::System => "system",
        }
        .to_string()
    }

    /// Convert database string to AuditSource
    fn source_from_db(s: &str) -> Result<AuditSource, RepositoryError> {
        match s {
            "voice" => Ok(AuditSource::Voice),
            "web" => Ok(AuditSource::Web),
            "api" => Ok(AuditSource::Api),
            "system" => Ok(AuditSource::System),
            _ => Err(RepositoryError::Serialization(format!(
                "Invalid source: {}",
                s
            ))),
        }
    }

    /// Convert GdprCategory to database string
    fn gdpr_category_to_db(category: GdprCategory) -> String {
        match category {
            GdprCategory::PersonalData => "personal_data",
            GdprCategory::Consent => "consent",
            GdprCategory::Booking => "booking",
            GdprCategory::VoiceSession => "voice_session",
        }
        .to_string()
    }

    /// Convert database string to GdprCategory
    fn gdpr_category_from_db(s: &str) -> Result<GdprCategory, RepositoryError> {
        match s {
            "personal_data" => Ok(GdprCategory::PersonalData),
            "consent" => Ok(GdprCategory::Consent),
            "booking" => Ok(GdprCategory::Booking),
            "voice_session" => Ok(GdprCategory::VoiceSession),
            _ => Err(RepositoryError::Serialization(format!(
                "Invalid gdpr_category: {}",
                s
            ))),
        }
    }

    /// Build SQL query with filters - Returns conditions only, params bound separately
    fn build_query_conditions(&self, query: &AuditLogQuery) -> Vec<(String, String)> {
        let mut conditions: Vec<(String, String)> = Vec::new();

        if let Some(ref user_id) = query.user_id {
            conditions.push(("user_id = ?".to_string(), user_id.clone()));
        }

        if let Some(user_type) = query.user_type {
            conditions.push(("user_type = ?".to_string(), Self::user_type_to_db(user_type)));
        }

        if let Some(ref action) = query.action {
            conditions.push(("action = ?".to_string(), format!("{:?}", action).to_uppercase()));
        }

        if let Some(ref entity_type) = query.entity_type {
            conditions.push(("entity_type = ?".to_string(), entity_type.clone()));
        }

        if let Some(ref entity_id) = query.entity_id {
            conditions.push(("entity_id = ?".to_string(), entity_id.clone()));
        }

        if let Some(source) = query.source {
            conditions.push(("source = ?".to_string(), Self::source_to_db(source)));
        }

        if let Some(category) = query.gdpr_category {
            conditions.push(("gdpr_category = ?".to_string(), Self::gdpr_category_to_db(category)));
        }

        if let Some(ref from_date) = query.from_date {
            conditions.push(("timestamp >= ?".to_string(), from_date.to_rfc3339()));
        }

        if let Some(ref to_date) = query.to_date {
            conditions.push(("timestamp <= ?".to_string(), to_date.to_rfc3339()));
        }

        conditions
    }
}

#[async_trait]
impl AuditLogRepository for SqliteAuditLogRepository {
    async fn save(&self, audit_log: &AuditLog) -> Result<(), RepositoryError> {
        let timestamp = audit_log.timestamp.to_rfc3339();
        let retention_until = audit_log.retention_until.to_rfc3339();
        let anonymized_at = audit_log.anonymized_at.map(|dt| dt.to_rfc3339());

        sqlx::query(
            r#"
            INSERT INTO audit_log (
                id, timestamp, user_id, user_type, action, entity_type, entity_id,
                data_before, data_after, changed_fields, gdpr_category, source,
                legal_basis, retention_until, anonymized_at, ip_address, user_agent, request_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            "#,
        )
        .bind(&audit_log.id)
        .bind(&timestamp)
        .bind(&audit_log.user_id)
        .bind(Self::user_type_to_db(audit_log.user_type))
        .bind(format!("{:?}", audit_log.action).to_uppercase())
        .bind(&audit_log.entity_type)
        .bind(&audit_log.entity_id)
        .bind(&audit_log.data_before)
        .bind(&audit_log.data_after)
        .bind(&audit_log.changed_fields)
        .bind(Self::gdpr_category_to_db(audit_log.gdpr_category))
        .bind(Self::source_to_db(audit_log.source))
        .bind(&audit_log.legal_basis)
        .bind(&retention_until)
        .bind(&anonymized_at)
        .bind(&audit_log.ip_address)
        .bind(&audit_log.user_agent)
        .bind(&audit_log.request_id)
        .execute(&self.pool)
        .await?;

        Ok(())
    }

    async fn find_by_id(&self, id: &str) -> Result<Option<AuditLog>, RepositoryError> {
        let row: Option<AuditLogRow> = sqlx::query_as(
            r#"
            SELECT 
                id, timestamp, user_id, user_type, action, entity_type, entity_id,
                data_before, data_after, changed_fields, gdpr_category, source,
                legal_basis, retention_until, anonymized_at, ip_address, user_agent, request_id
            FROM audit_log
            WHERE id = ?
            "#,
        )
        .bind(id)
        .fetch_optional(&self.pool)
        .await?;

        match row {
            Some(r) => Ok(Some(r.to_domain()?)),
            None => Ok(None),
        }
    }

    async fn query(&self, query: &AuditLogQuery) -> Result<Vec<AuditLog>, RepositoryError> {
        let conditions = self.build_query_conditions(query);
        
        let where_clause = if conditions.is_empty() {
            "".to_string()
        } else {
            format!("WHERE {}", conditions.iter().map(|(c, _)| c.clone()).collect::<Vec<_>>().join(" AND "))
        };
        
        let sql = format!(r#"
            SELECT 
                id, timestamp, user_id, user_type, action, entity_type, entity_id,
                data_before, data_after, changed_fields, gdpr_category, source,
                legal_basis, retention_until, anonymized_at, ip_address, user_agent, request_id
            FROM audit_log
            {}
            ORDER BY timestamp DESC
        "#, where_clause);
        
        let mut db_query = sqlx::query_as::<_, AuditLogRow>(&sql);
        
        // Bind all parameters in order
        for (_, param) in &conditions {
            db_query = db_query.bind(param);
        }

        let rows: Vec<AuditLogRow> = db_query.fetch_all(&self.pool).await?;

        rows.into_iter()
            .map(|r| r.to_domain())
            .collect::<Result<Vec<_>, _>>()
    }

    async fn count(&self, query: &AuditLogQuery) -> Result<i64, RepositoryError> {
        let conditions = self.build_query_conditions(query);
        
        let where_clause = if conditions.is_empty() {
            "".to_string()
        } else {
            format!("WHERE {}", conditions.iter().map(|(c, _)| c.clone()).collect::<Vec<_>>().join(" AND "))
        };
        
        let sql = format!("SELECT COUNT(*) as count FROM audit_log {}", where_clause);

        let mut db_query = sqlx::query_as::<_, CountRow>(&sql);
        
        // Bind all parameters in order
        for (_, param) in &conditions {
            db_query = db_query.bind(param);
        }

        let row = db_query.fetch_one(&self.pool).await?;
        Ok(row.count)
    }

    async fn find_by_entity(
        &self,
        entity_type: &str,
        entity_id: &str,
        limit: i64,
    ) -> Result<Vec<AuditLog>, RepositoryError> {
        let rows: Vec<AuditLogRow> = sqlx::query_as(
            r#"
            SELECT 
                id, timestamp, user_id, user_type, action, entity_type, entity_id,
                data_before, data_after, changed_fields, gdpr_category, source,
                legal_basis, retention_until, anonymized_at, ip_address, user_agent, request_id
            FROM audit_log
            WHERE entity_type = ? AND entity_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
            "#,
        )
        .bind(entity_type)
        .bind(entity_id)
        .bind(limit)
        .fetch_all(&self.pool)
        .await?;

        rows.into_iter()
            .map(|r| r.to_domain())
            .collect::<Result<Vec<_>, _>>()
    }

    async fn find_by_user(
        &self,
        user_id: &str,
        limit: i64,
    ) -> Result<Vec<AuditLog>, RepositoryError> {
        let rows: Vec<AuditLogRow> = sqlx::query_as(
            r#"
            SELECT 
                id, timestamp, user_id, user_type, action, entity_type, entity_id,
                data_before, data_after, changed_fields, gdpr_category, source,
                legal_basis, retention_until, anonymized_at, ip_address, user_agent, request_id
            FROM audit_log
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
            "#,
        )
        .bind(user_id)
        .bind(limit)
        .fetch_all(&self.pool)
        .await?;

        rows.into_iter()
            .map(|r| r.to_domain())
            .collect::<Result<Vec<_>, _>>()
    }

    async fn find_by_date_range(
        &self,
        start: DateTime<Utc>,
        end: DateTime<Utc>,
        limit: i64,
    ) -> Result<Vec<AuditLog>, RepositoryError> {
        let rows: Vec<AuditLogRow> = sqlx::query_as(
            r#"
            SELECT 
                id, timestamp, user_id, user_type, action, entity_type, entity_id,
                data_before, data_after, changed_fields, gdpr_category, source,
                legal_basis, retention_until, anonymized_at, ip_address, user_agent, request_id
            FROM audit_log
            WHERE timestamp >= ? AND timestamp <= ?
            ORDER BY timestamp DESC
            LIMIT ?
            "#,
        )
        .bind(start.to_rfc3339())
        .bind(end.to_rfc3339())
        .bind(limit)
        .fetch_all(&self.pool)
        .await?;

        rows.into_iter()
            .map(|r| r.to_domain())
            .collect::<Result<Vec<_>, _>>()
    }

    async fn mark_anonymized(&self, id: &str) -> Result<(), RepositoryError> {
        let now = Utc::now().to_rfc3339();

        sqlx::query(
            r#"
            UPDATE audit_log
            SET anonymized_at = ?,
                user_id = '[ANONYMIZED]',
                ip_address = NULL,
                user_agent = NULL,
                data_before = NULL,
                data_after = NULL
            WHERE id = ?
            "#,
        )
        .bind(&now)
        .bind(id)
        .execute(&self.pool)
        .await?;

        Ok(())
    }

    async fn find_needing_anonymization(&self) -> Result<Vec<AuditLog>, RepositoryError> {
        let now = Utc::now().to_rfc3339();

        let rows: Vec<AuditLogRow> = sqlx::query_as(
            r#"
            SELECT 
                id, timestamp, user_id, user_type, action, entity_type, entity_id,
                data_before, data_after, changed_fields, gdpr_category, source,
                legal_basis, retention_until, anonymized_at, ip_address, user_agent, request_id
            FROM audit_log
            WHERE retention_until <= ? AND anonymized_at IS NULL
            "#,
        )
        .bind(&now)
        .fetch_all(&self.pool)
        .await?;

        rows.into_iter()
            .map(|r| r.to_domain())
            .collect::<Result<Vec<_>, _>>()
    }

    async fn delete_expired(&self, before: DateTime<Utc>) -> Result<u64, RepositoryError> {
        let before_str = before.to_rfc3339();

        let result = sqlx::query(
            r#"
            DELETE FROM audit_log
            WHERE anonymized_at IS NOT NULL AND retention_until <= ?
            "#,
        )
        .bind(&before_str)
        .execute(&self.pool)
        .await?;

        Ok(result.rows_affected())
    }
}

/// Database row representation for AuditLog
#[derive(Debug, sqlx::FromRow)]
struct AuditLogRow {
    id: String,
    timestamp: String,
    user_id: Option<String>,
    user_type: String,
    action: String,
    entity_type: String,
    entity_id: String,
    data_before: Option<String>,
    data_after: Option<String>,
    changed_fields: Option<String>,
    gdpr_category: String,
    source: String,
    legal_basis: Option<String>,
    retention_until: String,
    anonymized_at: Option<String>,
    ip_address: Option<String>,
    user_agent: Option<String>,
    request_id: Option<String>,
}

impl AuditLogRow {
    fn to_domain(self) -> Result<AuditLog, RepositoryError> {
        let timestamp = DateTime::parse_from_rfc3339(&self.timestamp)
            .map_err(|e| RepositoryError::Serialization(format!("Invalid timestamp: {}", e)))?
            .with_timezone(&Utc);

        let retention_until = DateTime::parse_from_rfc3339(&self.retention_until)
            .map_err(|e| RepositoryError::Serialization(format!("Invalid retention_until: {}", e)))?
            .with_timezone(&Utc);

        let anonymized_at = match self.anonymized_at {
            Some(s) => Some(
                DateTime::parse_from_rfc3339(&s)
                    .map_err(|e| RepositoryError::Serialization(format!("Invalid anonymized_at: {}", e)))?
                    .with_timezone(&Utc),
            ),
            None => None,
        };

        let user_type = SqliteAuditLogRepository::user_type_from_db(&self.user_type)?;
        let source = SqliteAuditLogRepository::source_from_db(&self.source)?;
        let gdpr_category = SqliteAuditLogRepository::gdpr_category_from_db(&self.gdpr_category)?;

        // Parse action (stored as UPPERCASE string)
        let action = match self.action.as_str() {
            "CREATE" => crate::domain::audit::AuditAction::Create,
            "UPDATE" => crate::domain::audit::AuditAction::Update,
            "DELETE" => crate::domain::audit::AuditAction::Delete,
            "VIEW" => crate::domain::audit::AuditAction::View,
            "EXPORT" => crate::domain::audit::AuditAction::Export,
            "ANONYMIZE" => crate::domain::audit::AuditAction::Anonymize,
            "LOGIN" => crate::domain::audit::AuditAction::Login,
            "LOGOUT" => crate::domain::audit::AuditAction::Logout,
            _ => {
                return Err(RepositoryError::Serialization(format!(
                    "Invalid action: {}",
                    self.action
                )))
            }
        };

        Ok(AuditLog {
            id: self.id,
            timestamp,
            user_id: self.user_id,
            user_type,
            action,
            entity_type: self.entity_type,
            entity_id: self.entity_id,
            data_before: self.data_before,
            data_after: self.data_after,
            changed_fields: self.changed_fields,
            gdpr_category,
            source,
            legal_basis: self.legal_basis,
            retention_until,
            anonymized_at,
            ip_address: self.ip_address,
            user_agent: self.user_agent,
            request_id: self.request_id,
        })
    }
}

/// Row for COUNT queries
#[derive(Debug, sqlx::FromRow)]
struct CountRow {
    count: i64,
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::domain::audit::{AuditAction, AuditLog, GdprCategory, UserType};

    async fn create_test_pool() -> SqlitePool {
        let pool = SqlitePool::connect(":memory:").await.unwrap();

        sqlx::query(
            r#"
            CREATE TABLE audit_log (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                user_id TEXT,
                user_type TEXT NOT NULL,
                action TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                data_before TEXT,
                data_after TEXT,
                changed_fields TEXT,
                gdpr_category TEXT NOT NULL,
                source TEXT NOT NULL,
                legal_basis TEXT,
                retention_until TEXT NOT NULL,
                anonymized_at TEXT,
                ip_address TEXT,
                user_agent TEXT,
                request_id TEXT
            )
            "#,
        )
        .execute(&pool)
        .await
        .unwrap();

        pool
    }

    #[tokio::test]
    async fn test_save_and_find() {
        let pool = create_test_pool().await;
        let repo = SqliteAuditLogRepository::new(pool);

        let log = AuditLog::new(
            Some("user123".to_string()),
            UserType::Operator,
            AuditAction::Create,
            "cliente",
            "cliente456",
            AuditSource::Web,
            GdprCategory::PersonalData,
        );

        repo.save(&log).await.unwrap();

        let found = repo.find_by_id(&log.id).await.unwrap();
        assert!(found.is_some());
        let found = found.unwrap();
        assert_eq!(found.user_id, Some("user123".to_string()));
        assert_eq!(found.entity_type, "cliente");
    }

    #[tokio::test]
    async fn test_find_by_entity() {
        let pool = create_test_pool().await;
        let repo = SqliteAuditLogRepository::new(pool);

        // Create multiple logs for same entity
        for i in 0..3 {
            let log = AuditLog::new(
                Some(format!("user{}", i)),
                UserType::Operator,
                AuditAction::Update,
                "cliente",
                "cliente789",
                AuditSource::Web,
                GdprCategory::PersonalData,
            );
            repo.save(&log).await.unwrap();
        }

        // Create log for different entity
        let other_log = AuditLog::new(
            Some("other".to_string()),
            UserType::System,
            AuditAction::Create,
            "appuntamento",
            "app1",
            AuditSource::System,
            GdprCategory::Booking,
        );
        repo.save(&other_log).await.unwrap();

        let logs = repo.find_by_entity("cliente", "cliente789", 10).await.unwrap();
        assert_eq!(logs.len(), 3);
    }

    #[tokio::test]
    async fn test_anonymize() {
        let pool = create_test_pool().await;
        let repo = SqliteAuditLogRepository::new(pool);

        let mut log = AuditLog::new(
            Some("user123".to_string()),
            UserType::Operator,
            AuditAction::View,
            "cliente",
            "cliente001",
            AuditSource::Web,
            GdprCategory::PersonalData,
        );
        log.ip_address = Some("192.168.1.1".to_string());

        repo.save(&log).await.unwrap();
        repo.mark_anonymized(&log.id).await.unwrap();

        let found = repo.find_by_id(&log.id).await.unwrap().unwrap();
        assert_eq!(found.user_id, Some("[ANONYMIZED]".to_string()));
        assert!(found.ip_address.is_none());
        assert!(found.anonymized_at.is_some());
    }
}
