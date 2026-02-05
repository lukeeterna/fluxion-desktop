//! Audit Log Domain Model
//!
//! GDPR-compliant audit logging system for tracking all data changes
//! and user actions within the FLUXION application.

use chrono::{DateTime, Duration, Utc};
use serde::{Deserialize, Serialize};
use sqlx::FromRow;
use uuid::Uuid;

/// Audit Log Entry - Complete record of a system action
#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct AuditLog {
    pub id: String,
    pub timestamp: DateTime<Utc>,
    pub user_id: Option<String>,
    pub user_type: UserType,
    pub action: AuditAction,
    pub entity_type: String,
    pub entity_id: String,
    pub data_before: Option<String>,    // JSON
    pub data_after: Option<String>,     // JSON
    pub changed_fields: Option<String>, // JSON array
    pub gdpr_category: GdprCategory,
    pub source: AuditSource,
    pub legal_basis: Option<String>,
    pub retention_until: DateTime<Utc>,
    pub anonymized_at: Option<DateTime<Utc>>,
    pub ip_address: Option<String>,
    pub user_agent: Option<String>,
    pub request_id: Option<String>,
}

/// Type of user performing the action
#[derive(Debug, Clone, Copy, Serialize, Deserialize, sqlx::Type, PartialEq, Eq)]
#[sqlx(rename_all = "snake_case")]
pub enum UserType {
    /// Voice session (IVR/automated system)
    VoiceSession,
    /// Human operator
    Operator,
    /// System/automated process
    System,
}

/// Type of action performed
#[derive(Debug, Clone, Copy, Serialize, Deserialize, sqlx::Type, PartialEq, Eq)]
#[sqlx(rename_all = "UPPERCASE")]
pub enum AuditAction {
    /// Create new entity
    Create,
    /// Update existing entity
    Update,
    /// Delete/soft-delete entity
    Delete,
    /// View/read entity data
    View,
    /// Export data
    Export,
    /// Anonymize data
    Anonymize,
    /// Login action
    Login,
    /// Logout action
    Logout,
}

/// GDPR data category for compliance tracking
#[derive(Debug, Clone, Copy, Serialize, Deserialize, sqlx::Type, PartialEq, Eq)]
#[sqlx(rename_all = "snake_case")]
pub enum GdprCategory {
    /// Personal identifiable information
    PersonalData,
    /// Consent records
    Consent,
    /// Booking/appointment data
    Booking,
    /// Voice session recordings/metadata
    VoiceSession,
}

/// Source of the audit action
#[derive(Debug, Clone, Copy, Serialize, Deserialize, sqlx::Type, PartialEq, Eq)]
#[sqlx(rename_all = "snake_case")]
pub enum AuditSource {
    /// Voice channel (IVR/phone)
    Voice,
    /// Web application
    Web,
    /// API/integrations
    Api,
    /// Internal system process
    System,
}

impl AuditLog {
    /// Default retention period for audit logs (7 years for GDPR compliance)
    const DEFAULT_RETENTION_YEARS: i64 = 7;

    /// Create a new audit log entry
    pub fn new(
        user_id: Option<String>,
        user_type: UserType,
        action: AuditAction,
        entity_type: impl Into<String>,
        entity_id: impl Into<String>,
        source: AuditSource,
        gdpr_category: GdprCategory,
    ) -> Self {
        let now = Utc::now();
        let retention_until = now + Duration::days(365 * Self::DEFAULT_RETENTION_YEARS);

        Self {
            id: Uuid::new_v4().to_string(),
            timestamp: now,
            user_id,
            user_type,
            action,
            entity_type: entity_type.into(),
            entity_id: entity_id.into(),
            data_before: None,
            data_after: None,
            changed_fields: None,
            gdpr_category,
            source,
            legal_basis: None,
            retention_until,
            anonymized_at: None,
            ip_address: None,
            user_agent: None,
            request_id: None,
        }
    }

    /// Set the data before the action (for updates/deletes)
    pub fn with_data_before<T: Serialize>(mut self, data: &T) -> Result<Self, serde_json::Error> {
        self.data_before = Some(serde_json::to_string(data)?);
        Ok(self)
    }

    /// Set the data after the action (for creates/updates)
    pub fn with_data_after<T: Serialize>(mut self, data: &T) -> Result<Self, serde_json::Error> {
        self.data_after = Some(serde_json::to_string(data)?);
        Ok(self)
    }

    /// Set changed fields (for updates)
    pub fn with_changed_fields(mut self, fields: Vec<String>) -> Result<Self, serde_json::Error> {
        self.changed_fields = Some(serde_json::to_string(&fields)?);
        Ok(self)
    }

    /// Calculate changed fields from before/after data
    /// Returns a list of field names that have changed
    pub fn calculate_changed_fields(
        before: &str,
        after: &str,
    ) -> Result<Vec<String>, serde_json::Error> {
        let before_value: serde_json::Value = serde_json::from_str(before)?;
        let after_value: serde_json::Value = serde_json::from_str(after)?;

        let mut changed = Vec::new();

        if let (Some(before_obj), Some(after_obj)) =
            (before_value.as_object(), after_value.as_object())
        {
            // Check all keys from both objects
            let all_keys: std::collections::HashSet<_> =
                before_obj.keys().chain(after_obj.keys()).cloned().collect();

            for key in all_keys {
                let before_val = before_obj.get(&key);
                let after_val = after_obj.get(&key);

                if before_val != after_val {
                    changed.push(key);
                }
            }
        }

        Ok(changed)
    }

    /// Set legal basis for GDPR compliance
    pub fn with_legal_basis(mut self, basis: impl Into<String>) -> Self {
        self.legal_basis = Some(basis.into());
        self
    }

    /// Set request context (IP, user agent, request ID)
    pub fn with_request_context(
        mut self,
        ip_address: Option<String>,
        user_agent: Option<String>,
        request_id: Option<String>,
    ) -> Self {
        self.ip_address = ip_address;
        self.user_agent = user_agent;
        self.request_id = request_id;
        self
    }

    /// Set custom retention period
    pub fn with_retention_until(mut self, retention_until: DateTime<Utc>) -> Self {
        self.retention_until = retention_until;
        self
    }

    /// Check if this audit log entry should be anonymized
    pub fn should_anonymize(&self) -> bool {
        Utc::now() > self.retention_until && self.anonymized_at.is_none()
    }

    /// Get human-readable description of the action
    pub fn action_description(&self) -> String {
        format!(
            "{:?} on {} ({})",
            self.action, self.entity_type, self.entity_id
        )
    }
}

/// Builder for AuditLog entries
#[derive(Debug, Default)]
pub struct AuditLogBuilder {
    user_id: Option<String>,
    user_type: Option<UserType>,
    action: Option<AuditAction>,
    entity_type: Option<String>,
    entity_id: Option<String>,
    source: Option<AuditSource>,
    gdpr_category: Option<GdprCategory>,
    data_before: Option<String>,
    data_after: Option<String>,
    changed_fields: Option<Vec<String>>,
    legal_basis: Option<String>,
    ip_address: Option<String>,
    user_agent: Option<String>,
    request_id: Option<String>,
    retention_years: Option<i64>,
}

impl AuditLogBuilder {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn user_id(mut self, user_id: impl Into<String>) -> Self {
        self.user_id = Some(user_id.into());
        self
    }

    pub fn user_type(mut self, user_type: UserType) -> Self {
        self.user_type = Some(user_type);
        self
    }

    pub fn action(mut self, action: AuditAction) -> Self {
        self.action = Some(action);
        self
    }

    pub fn entity_type(mut self, entity_type: impl Into<String>) -> Self {
        self.entity_type = Some(entity_type.into());
        self
    }

    pub fn entity_id(mut self, entity_id: impl Into<String>) -> Self {
        self.entity_id = Some(entity_id.into());
        self
    }

    pub fn source(mut self, source: AuditSource) -> Self {
        self.source = Some(source);
        self
    }

    pub fn gdpr_category(mut self, category: GdprCategory) -> Self {
        self.gdpr_category = Some(category);
        self
    }

    pub fn data_before<T: Serialize>(mut self, data: &T) -> Result<Self, serde_json::Error> {
        self.data_before = Some(serde_json::to_string(data)?);
        Ok(self)
    }

    pub fn data_after<T: Serialize>(mut self, data: &T) -> Result<Self, serde_json::Error> {
        self.data_after = Some(serde_json::to_string(data)?);
        Ok(self)
    }

    pub fn changed_fields(mut self, fields: Vec<String>) -> Self {
        self.changed_fields = Some(fields);
        self
    }

    pub fn legal_basis(mut self, basis: impl Into<String>) -> Self {
        self.legal_basis = Some(basis.into());
        self
    }

    pub fn ip_address(mut self, ip: impl Into<String>) -> Self {
        self.ip_address = Some(ip.into());
        self
    }

    pub fn user_agent(mut self, agent: impl Into<String>) -> Self {
        self.user_agent = Some(agent.into());
        self
    }

    pub fn request_id(mut self, id: impl Into<String>) -> Self {
        self.request_id = Some(id.into());
        self
    }

    pub fn retention_years(mut self, years: i64) -> Self {
        self.retention_years = Some(years);
        self
    }

    pub fn build(self) -> Result<AuditLog, AuditLogBuilderError> {
        let user_type = self
            .user_type
            .ok_or(AuditLogBuilderError::MissingField("user_type"))?;
        let action = self
            .action
            .ok_or(AuditLogBuilderError::MissingField("action"))?;
        let entity_type = self
            .entity_type
            .ok_or(AuditLogBuilderError::MissingField("entity_type"))?;
        let entity_id = self
            .entity_id
            .ok_or(AuditLogBuilderError::MissingField("entity_id"))?;
        let source = self
            .source
            .ok_or(AuditLogBuilderError::MissingField("source"))?;
        let gdpr_category = self
            .gdpr_category
            .ok_or(AuditLogBuilderError::MissingField("gdpr_category"))?;

        let now = Utc::now();
        let retention_years = self
            .retention_years
            .unwrap_or(AuditLog::DEFAULT_RETENTION_YEARS);
        let retention_until = now + Duration::days(365 * retention_years);

        let changed_fields_json = self
            .changed_fields
            .map(|f| serde_json::to_string(&f).unwrap_or_default());

        Ok(AuditLog {
            id: Uuid::new_v4().to_string(),
            timestamp: now,
            user_id: self.user_id,
            user_type,
            action,
            entity_type,
            entity_id,
            data_before: self.data_before,
            data_after: self.data_after,
            changed_fields: changed_fields_json,
            gdpr_category,
            source,
            legal_basis: self.legal_basis,
            retention_until,
            anonymized_at: None,
            ip_address: self.ip_address,
            user_agent: self.user_agent,
            request_id: self.request_id,
        })
    }
}

/// Errors that can occur when building an AuditLog
#[derive(Debug, thiserror::Error)]
pub enum AuditLogBuilderError {
    #[error("Missing required field: {0}")]
    MissingField(&'static str),
}

/// Query parameters for filtering audit logs
#[derive(Debug, Default, Clone)]
pub struct AuditLogQuery {
    pub user_id: Option<String>,
    pub user_type: Option<UserType>,
    pub action: Option<AuditAction>,
    pub entity_type: Option<String>,
    pub entity_id: Option<String>,
    pub source: Option<AuditSource>,
    pub gdpr_category: Option<GdprCategory>,
    pub from_date: Option<DateTime<Utc>>,
    pub to_date: Option<DateTime<Utc>>,
    pub limit: Option<i64>,
    pub offset: Option<i64>,
}

impl AuditLogQuery {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn by_user(mut self, user_id: impl Into<String>) -> Self {
        self.user_id = Some(user_id.into());
        self
    }

    pub fn by_entity(
        mut self,
        entity_type: impl Into<String>,
        entity_id: impl Into<String>,
    ) -> Self {
        self.entity_type = Some(entity_type.into());
        self.entity_id = Some(entity_id.into());
        self
    }

    pub fn by_action(mut self, action: AuditAction) -> Self {
        self.action = Some(action);
        self
    }

    pub fn by_date_range(mut self, from: DateTime<Utc>, to: DateTime<Utc>) -> Self {
        self.from_date = Some(from);
        self.to_date = Some(to);
        self
    }

    pub fn with_pagination(mut self, limit: i64, offset: i64) -> Self {
        self.limit = Some(limit);
        self.offset = Some(offset);
        self
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_audit_log_creation() {
        let log = AuditLog::new(
            Some("user123".to_string()),
            UserType::Operator,
            AuditAction::Create,
            "cliente",
            "cliente456",
            AuditSource::Web,
            GdprCategory::PersonalData,
        );

        assert_eq!(log.user_id, Some("user123".to_string()));
        assert_eq!(log.user_type, UserType::Operator);
        assert_eq!(log.action, AuditAction::Create);
        assert_eq!(log.entity_type, "cliente");
        assert_eq!(log.entity_id, "cliente456");
        assert!(log.anonymized_at.is_none());
    }

    #[test]
    fn test_builder_pattern() {
        let log = AuditLogBuilder::new()
            .user_id("user123")
            .user_type(UserType::System)
            .action(AuditAction::Update)
            .entity_type("appuntamento")
            .entity_id("app789")
            .source(AuditSource::Api)
            .gdpr_category(GdprCategory::Booking)
            .build()
            .expect("Failed to build audit log");

        assert_eq!(log.user_type, UserType::System);
        assert_eq!(log.action, AuditAction::Update);
    }

    #[test]
    fn test_builder_missing_fields() {
        let result = AuditLogBuilder::new().user_type(UserType::Operator).build();

        assert!(result.is_err());
    }

    #[test]
    fn test_calculate_changed_fields() {
        let before = r#"{"name": "Mario", "age": 30, "city": "Roma"}"#;
        let after = r#"{"name": "Mario", "age": 31, "city": "Roma"}"#;

        let changed = AuditLog::calculate_changed_fields(before, after).unwrap();
        assert_eq!(changed, vec!["age"]);
    }

    #[test]
    fn test_calculate_changed_fields_new_field() {
        let before = r#"{"name": "Mario"}"#;
        let after = r#"{"name": "Mario", "email": "mario@test.com"}"#;

        let changed = AuditLog::calculate_changed_fields(before, after).unwrap();
        assert!(changed.contains(&"email".to_string()));
    }

    #[test]
    fn test_should_anonymize() {
        let mut log = AuditLog::new(
            None,
            UserType::System,
            AuditAction::View,
            "test",
            "test123",
            AuditSource::System,
            GdprCategory::PersonalData,
        );
        // Set retention to past date
        log.retention_until = Utc::now() - Duration::days(1);

        assert!(log.should_anonymize());

        log.anonymized_at = Some(Utc::now());
        assert!(!log.should_anonymize());
    }
}
