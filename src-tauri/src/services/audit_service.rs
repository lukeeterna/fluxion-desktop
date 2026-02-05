//! Audit Service
//!
//! Business logic layer for audit logging with automatic retention calculation,
//! JSON diff computation, and GDPR compliance features.

use std::sync::Arc;

use chrono::{DateTime, Duration, Utc};
use serde::Serialize;
use thiserror::Error;

use crate::domain::audit::{
    AuditAction, AuditLog, AuditLogBuilder, AuditLogBuilderError, AuditLogQuery, AuditSource,
    GdprCategory, UserType,
};
use crate::domain::RepositoryError;
use crate::infra::repositories::audit_repository::AuditLogRepository;

/// Service errors
#[derive(Debug, Error)]
pub enum AuditServiceError {
    #[error("Repository error: {0}")]
    Repository(#[from] RepositoryError),

    #[error("Serialization error: {0}")]
    Serialization(#[from] serde_json::Error),

    #[error("Builder error: {0}")]
    Builder(#[from] AuditLogBuilderError),

    #[error("Invalid operation: {0}")]
    InvalidOperation(String),
}

/// Audit Service - Business logic for audit logging
pub struct AuditService {
    repository: Arc<dyn AuditLogRepository>,
    default_retention_years: i64,
}

impl AuditService {
    /// Create new AuditService with repository
    pub fn new(repository: Arc<dyn AuditLogRepository>) -> Self {
        Self {
            repository,
            default_retention_years: 7, // Default 7 years for GDPR
        }
    }

    /// Create with custom retention period
    pub fn with_retention_years(mut self, years: i64) -> Self {
        self.default_retention_years = years;
        self
    }

    /// Log a CREATE action
    pub async fn log_create<T: Serialize>(
        &self,
        user_id: Option<String>,
        user_type: UserType,
        entity_type: impl Into<String>,
        entity_id: impl Into<String>,
        data_after: &T,
        source: AuditSource,
        gdpr_category: GdprCategory,
    ) -> Result<AuditLog, AuditServiceError> {
        let entity_type = entity_type.into();
        let entity_id = entity_id.into();

        let log = AuditLogBuilder::new()
            .user_id(user_id.unwrap_or_default())
            .user_type(user_type)
            .action(AuditAction::Create)
            .entity_type(&entity_type)
            .entity_id(&entity_id)
            .source(source)
            .gdpr_category(gdpr_category)
            .data_after(data_after)?
            .retention_years(self.default_retention_years)
            .build()?;

        self.repository.save(&log).await?;
        Ok(log)
    }

    /// Log an UPDATE action with automatic diff calculation
    pub async fn log_update<T: Serialize>(
        &self,
        user_id: Option<String>,
        user_type: UserType,
        entity_type: impl Into<String>,
        entity_id: impl Into<String>,
        data_before: &T,
        data_after: &T,
        source: AuditSource,
        gdpr_category: GdprCategory,
    ) -> Result<AuditLog, AuditServiceError> {
        let entity_type = entity_type.into();
        let entity_id = entity_id.into();

        // Serialize data
        let before_json = serde_json::to_string(data_before)?;
        let after_json = serde_json::to_string(data_after)?;

        // Calculate changed fields
        let changed_fields = AuditLog::calculate_changed_fields(&before_json, &after_json)?;

        let mut builder = AuditLogBuilder::new()
            .user_id(user_id.unwrap_or_default())
            .user_type(user_type)
            .action(AuditAction::Update)
            .entity_type(&entity_type)
            .entity_id(&entity_id)
            .source(source)
            .gdpr_category(gdpr_category)
            .retention_years(self.default_retention_years);

        // Add data before/after
        if let Ok(b) = serde_json::from_str::<serde_json::Value>(&before_json) {
            builder = builder.data_before(&b)?;
        }
        if let Ok(a) = serde_json::from_str::<serde_json::Value>(&after_json) {
            builder = builder.data_after(&a)?;
        }

        let log = builder.changed_fields(changed_fields).build()?;

        self.repository.save(&log).await?;
        Ok(log)
    }

    /// Log a DELETE action
    pub async fn log_delete<T: Serialize>(
        &self,
        user_id: Option<String>,
        user_type: UserType,
        entity_type: impl Into<String>,
        entity_id: impl Into<String>,
        data_before: &T,
        source: AuditSource,
        gdpr_category: GdprCategory,
    ) -> Result<AuditLog, AuditServiceError> {
        let entity_type = entity_type.into();
        let entity_id = entity_id.into();

        let log = AuditLogBuilder::new()
            .user_id(user_id.unwrap_or_default())
            .user_type(user_type)
            .action(AuditAction::Delete)
            .entity_type(&entity_type)
            .entity_id(&entity_id)
            .source(source)
            .gdpr_category(gdpr_category)
            .data_before(data_before)?
            .retention_years(self.default_retention_years)
            .build()?;

        self.repository.save(&log).await?;
        Ok(log)
    }

    /// Log a VIEW action
    pub async fn log_view(
        &self,
        user_id: Option<String>,
        user_type: UserType,
        entity_type: impl Into<String>,
        entity_id: impl Into<String>,
        source: AuditSource,
        gdpr_category: GdprCategory,
    ) -> Result<AuditLog, AuditServiceError> {
        let entity_type = entity_type.into();
        let entity_id = entity_id.into();

        let log = AuditLogBuilder::new()
            .user_id(user_id.unwrap_or_default())
            .user_type(user_type)
            .action(AuditAction::View)
            .entity_type(&entity_type)
            .entity_id(&entity_id)
            .source(source)
            .gdpr_category(gdpr_category)
            .retention_years(self.default_retention_years)
            .build()?;

        self.repository.save(&log).await?;
        Ok(log)
    }

    /// Log a custom action with full control
    pub async fn log_custom(
        &self,
        builder: AuditLogBuilder,
    ) -> Result<AuditLog, AuditServiceError> {
        let log = builder.retention_years(self.default_retention_years).build()?;
        self.repository.save(&log).await?;
        Ok(log)
    }

    /// Query audit logs with filters
    pub async fn query(&self, query: &AuditLogQuery) -> Result<Vec<AuditLog>, AuditServiceError> {
        let logs = self.repository.query(query).await?;
        Ok(logs)
    }

    /// Get audit log count with filters
    pub async fn count(&self, query: &AuditLogQuery) -> Result<i64, AuditServiceError> {
        let count = self.repository.count(query).await?;
        Ok(count)
    }

    /// Get audit history for an entity
    pub async fn get_entity_history(
        &self,
        entity_type: impl Into<String>,
        entity_id: impl Into<String>,
        limit: i64,
    ) -> Result<Vec<AuditLog>, AuditServiceError> {
        let logs = self.repository.find_by_entity(&entity_type.into(), &entity_id.into(), limit).await?;
        Ok(logs)
    }

    /// Get audit logs by user
    pub async fn get_user_activity(
        &self,
        user_id: &str,
        limit: i64,
    ) -> Result<Vec<AuditLog>, AuditServiceError> {
        let logs = self.repository.find_by_user(user_id, limit).await?;
        Ok(logs)
    }

    /// Get audit logs for a date range
    pub async fn get_activity_report(
        &self,
        start: DateTime<Utc>,
        end: DateTime<Utc>,
        limit: i64,
    ) -> Result<Vec<AuditLog>, AuditServiceError> {
        let logs = self.repository.find_by_date_range(start, end, limit).await?;
        Ok(logs)
    }

    /// Run GDPR anonymization for expired records
    pub async fn run_gdpr_anonymization(&self) -> Result<usize, AuditServiceError> {
        let logs_to_anonymize = self.repository.find_needing_anonymization().await?;
        let count = logs_to_anonymize.len();

        for log in logs_to_anonymize {
            self.repository.mark_anonymized(&log.id).await?;
        }

        Ok(count)
    }

    /// Delete anonymized records that have exceeded retention period
    pub async fn cleanup_expired_logs(
        &self,
        retention_buffer_days: i64,
    ) -> Result<u64, AuditServiceError> {
        let cutoff = Utc::now() - Duration::days(retention_buffer_days);
        let deleted = self.repository.delete_expired(cutoff).await?;
        Ok(deleted)
    }

    /// Get statistics for dashboard
    pub async fn get_statistics(
        &self,
        start: DateTime<Utc>,
        end: DateTime<Utc>,
    ) -> Result<AuditStatistics, AuditServiceError> {
        let logs = self.repository.find_by_date_range(start, end, 10000).await?;

        let mut stats = AuditStatistics {
            total_logs: logs.len() as i64,
            create_count: 0,
            update_count: 0,
            delete_count: 0,
            view_count: 0,
            by_user_type: std::collections::HashMap::new(),
            by_source: std::collections::HashMap::new(),
            by_gdpr_category: std::collections::HashMap::new(),
        };

        for log in logs {
            match log.action {
                AuditAction::Create => stats.create_count += 1,
                AuditAction::Update => stats.update_count += 1,
                AuditAction::Delete => stats.delete_count += 1,
                AuditAction::View => stats.view_count += 1,
                _ => {} // Export, Anonymize, Login, Logout - non conteggiati nelle statistiche base
            }

            *stats.by_user_type.entry(format!("{:?}", log.user_type)).or_insert(0) += 1;
            *stats.by_source.entry(format!("{:?}", log.source)).or_insert(0) += 1;
            *stats.by_gdpr_category.entry(format!("{:?}", log.gdpr_category)).or_insert(0) += 1;
        }

        Ok(stats)
    }

    /// Reconstruct entity state at a specific point in time
    /// Returns the audit logs that would reconstruct the entity state
    pub async fn reconstruct_entity_history(
        &self,
        entity_type: impl Into<String>,
        entity_id: impl Into<String>,
        up_to: DateTime<Utc>,
    ) -> Result<Vec<AuditLog>, AuditServiceError> {
        let entity_type = entity_type.into();
        let entity_id = entity_id.into();

        // Get all logs for this entity up to the specified time
        let all_logs = self.repository.find_by_entity(&entity_type, &entity_id, 1000).await?;
        
        let filtered_logs: Vec<_> = all_logs
            .into_iter()
            .filter(|log| log.timestamp <= up_to)
            .collect();

        Ok(filtered_logs)
    }
}

/// Statistics for audit dashboard
#[derive(Debug, Clone, Default)]
pub struct AuditStatistics {
    pub total_logs: i64,
    pub create_count: i64,
    pub update_count: i64,
    pub delete_count: i64,
    pub view_count: i64,
    pub by_user_type: std::collections::HashMap<String, i64>,
    pub by_source: std::collections::HashMap<String, i64>,
    pub by_gdpr_category: std::collections::HashMap<String, i64>,
}

/// Convenience macros/helpers for common audit patterns
pub mod helpers {
    use super::*;

    /// Quick log for operator actions
    pub async fn log_operator_action<T: Serialize>(
        service: &AuditService,
        operator_id: &str,
        action: AuditAction,
        entity_type: &str,
        entity_id: &str,
        data_before: Option<&T>,
        data_after: Option<&T>,
    ) -> Result<AuditLog, AuditServiceError> {
        match action {
            AuditAction::Create => {
                if let Some(data) = data_after {
                    service.log_create(
                        Some(operator_id.to_string()),
                        UserType::Operator,
                        entity_type,
                        entity_id,
                        data,
                        AuditSource::Web,
                        GdprCategory::PersonalData,
                    ).await
                } else {
                    Err(AuditServiceError::InvalidOperation(
                        "Create action requires data_after".to_string(),
                    ))
                }
            }
            AuditAction::Update => {
                match (data_before, data_after) {
                    (Some(before), Some(after)) => {
                        service.log_update(
                            Some(operator_id.to_string()),
                            UserType::Operator,
                            entity_type,
                            entity_id,
                            before,
                            after,
                            AuditSource::Web,
                            GdprCategory::PersonalData,
                        ).await
                    }
                    _ => Err(AuditServiceError::InvalidOperation(
                        "Update action requires both data_before and data_after".to_string(),
                    )),
                }
            }
            AuditAction::Delete => {
                if let Some(data) = data_before {
                    service.log_delete(
                        Some(operator_id.to_string()),
                        UserType::Operator,
                        entity_type,
                        entity_id,
                        data,
                        AuditSource::Web,
                        GdprCategory::PersonalData,
                    ).await
                } else {
                    Err(AuditServiceError::InvalidOperation(
                        "Delete action requires data_before".to_string(),
                    ))
                }
            }
            AuditAction::View => {
                service.log_view(
                    Some(operator_id.to_string()),
                    UserType::Operator,
                    entity_type,
                    entity_id,
                    AuditSource::Web,
                    GdprCategory::PersonalData,
                ).await
            }
            _ => {
                // Export, Anonymize, Login, Logout - use custom log
                service.log_custom(
                    crate::domain::audit::AuditLogBuilder::new()
                        .user_id(operator_id)
                        .user_type(UserType::Operator)
                        .action(action)
                        .entity_type(entity_type)
                        .entity_id(entity_id)
                        .source(AuditSource::Web)
                        .gdpr_category(GdprCategory::PersonalData)
                ).await
            }
        }
    }

    /// Quick log for voice session actions
    pub async fn log_voice_action<T: Serialize>(
        service: &AuditService,
        session_id: &str,
        action: AuditAction,
        entity_type: &str,
        entity_id: &str,
        data_before: Option<&T>,
        data_after: Option<&T>,
    ) -> Result<AuditLog, AuditServiceError> {
        match action {
            AuditAction::Create => {
                if let Some(data) = data_after {
                    service.log_create(
                        Some(session_id.to_string()),
                        UserType::VoiceSession,
                        entity_type,
                        entity_id,
                        data,
                        AuditSource::Voice,
                        GdprCategory::VoiceSession,
                    ).await
                } else {
                    Err(AuditServiceError::InvalidOperation(
                        "Create action requires data_after".to_string(),
                    ))
                }
            }
            AuditAction::Update => {
                match (data_before, data_after) {
                    (Some(before), Some(after)) => {
                        service.log_update(
                            Some(session_id.to_string()),
                            UserType::VoiceSession,
                            entity_type,
                            entity_id,
                            before,
                            after,
                            AuditSource::Voice,
                            GdprCategory::VoiceSession,
                        ).await
                    }
                    _ => Err(AuditServiceError::InvalidOperation(
                        "Update action requires both data_before and data_after".to_string(),
                    )),
                }
            }
            AuditAction::Delete => {
                if let Some(data) = data_before {
                    service.log_delete(
                        Some(session_id.to_string()),
                        UserType::VoiceSession,
                        entity_type,
                        entity_id,
                        data,
                        AuditSource::Voice,
                        GdprCategory::VoiceSession,
                    ).await
                } else {
                    Err(AuditServiceError::InvalidOperation(
                        "Delete action requires data_before".to_string(),
                    ))
                }
            }
            AuditAction::View => {
                service.log_view(
                    Some(session_id.to_string()),
                    UserType::VoiceSession,
                    entity_type,
                    entity_id,
                    AuditSource::Voice,
                    GdprCategory::VoiceSession,
                ).await
            }
            _ => {
                // Export, Anonymize, Login, Logout - use custom log
                service.log_custom(
                    crate::domain::audit::AuditLogBuilder::new()
                        .user_id(session_id)
                        .user_type(UserType::VoiceSession)
                        .action(action)
                        .entity_type(entity_type)
                        .entity_id(entity_id)
                        .source(AuditSource::Voice)
                        .gdpr_category(GdprCategory::VoiceSession)
                ).await
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::domain::audit::{AuditAction, AuditSource, GdprCategory, UserType};
    use crate::infra::repositories::audit_repository::SqliteAuditLogRepository;
    use sqlx::SqlitePool;

    #[derive(Debug, Serialize, Clone)]
    struct TestEntity {
        id: String,
        name: String,
        email: String,
    }

    async fn create_test_service() -> (AuditService, SqlitePool) {
        let pool = SqlitePool::connect(":memory:").await.unwrap();

        sqlx::query(
            r#"
            CREATE TABLE audit_logs (
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

        let repo = Arc::new(SqliteAuditLogRepository::new(pool.clone())) as Arc<dyn AuditLogRepository>;
        let service = AuditService::new(repo);

        (service, pool)
    }

    #[tokio::test]
    async fn test_log_create() {
        let (service, _pool) = create_test_service().await;

        let entity = TestEntity {
            id: "123".to_string(),
            name: "Mario Rossi".to_string(),
            email: "mario@test.com".to_string(),
        };

        let log = service
            .log_create(
                Some("user1".to_string()),
                UserType::Operator,
                "cliente",
                "123",
                &entity,
                AuditSource::Web,
                GdprCategory::PersonalData,
            )
            .await
            .unwrap();

        assert_eq!(log.action, AuditAction::Create);
        assert_eq!(log.entity_type, "cliente");
        assert!(log.data_after.is_some());
    }

    #[tokio::test]
    async fn test_log_update_with_diff() {
        let (service, _pool) = create_test_service().await;

        let before = TestEntity {
            id: "123".to_string(),
            name: "Mario Rossi".to_string(),
            email: "mario@test.com".to_string(),
        };

        let after = TestEntity {
            id: "123".to_string(),
            name: "Mario Rossi".to_string(),
            email: "mario.rossi@test.com".to_string(),
        };

        let log = service
            .log_update(
                Some("user1".to_string()),
                UserType::Operator,
                "cliente",
                "123",
                &before,
                &after,
                AuditSource::Web,
                GdprCategory::PersonalData,
            )
            .await
            .unwrap();

        assert_eq!(log.action, AuditAction::Update);
        assert!(log.changed_fields.is_some());
        
        let changed: Vec<String> = serde_json::from_str(&log.changed_fields.unwrap()).unwrap();
        assert!(changed.contains(&"email".to_string()));
    }

    #[tokio::test]
    async fn test_log_delete() {
        let (service, _pool) = create_test_service().await;

        let entity = TestEntity {
            id: "123".to_string(),
            name: "Mario Rossi".to_string(),
            email: "mario@test.com".to_string(),
        };

        let log = service
            .log_delete(
                Some("user1".to_string()),
                UserType::Operator,
                "cliente",
                "123",
                &entity,
                AuditSource::Web,
                GdprCategory::PersonalData,
            )
            .await
            .unwrap();

        assert_eq!(log.action, AuditAction::Delete);
        assert!(log.data_before.is_some());
    }

    #[tokio::test]
    async fn test_helper_operator_create() {
        let (service, _pool) = create_test_service().await;

        let entity = TestEntity {
            id: "456".to_string(),
            name: "Giuseppe Verdi".to_string(),
            email: "giuseppe@test.com".to_string(),
        };

        let log = helpers::log_operator_action(
            &service,
            "operator123",
            AuditAction::Create,
            "cliente",
            "456",
            None::<&TestEntity>,
            Some(&entity),
        )
        .await
        .unwrap();

        assert_eq!(log.user_type, UserType::Operator);
        assert_eq!(log.source, AuditSource::Web);
    }

    #[tokio::test]
    async fn test_statistics() {
        let (service, _pool) = create_test_service().await;

        // Create some test logs
        for i in 0..5 {
            let entity = TestEntity {
                id: format!("{}", i),
                name: format!("User {}", i),
                email: format!("user{}@test.com", i),
            };

            service
                .log_create(
                    Some(format!("user{}", i)),
                    UserType::Operator,
                    "cliente",
                    format!("{}", i),
                    &entity,
                    AuditSource::Web,
                    GdprCategory::PersonalData,
                )
                .await
                .unwrap();
        }

        let stats = service
            .get_statistics(Utc::now() - Duration::hours(1), Utc::now())
            .await
            .unwrap();

        assert_eq!(stats.total_logs, 5);
        assert_eq!(stats.create_count, 5);
    }
}
