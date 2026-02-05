use async_trait::async_trait;
use chrono::NaiveDateTime;

use super::{AppuntamentoAggregate, AppuntamentoId};

/// Repository error types
#[derive(Debug, thiserror::Error)]
pub enum RepositoryError {
    #[error("Database error: {0}")]
    Database(String),

    #[error("Not found: {0}")]
    NotFound(String),

    #[error("Conflict: {0}")]
    Conflict(String),

    #[error("Serialization error: {0}")]
    Serialization(String),
}

impl From<sqlx::Error> for RepositoryError {
    fn from(err: sqlx::Error) -> Self {
        match err {
            sqlx::Error::RowNotFound => RepositoryError::NotFound("Entity not found".to_string()),
            _ => RepositoryError::Database(err.to_string()),
        }
    }
}

impl From<serde_json::Error> for RepositoryError {
    fn from(err: serde_json::Error) -> Self {
        RepositoryError::Serialization(err.to_string())
    }
}

/// Appuntamento Repository trait (domain layer)
#[async_trait]
pub trait AppuntamentoRepository: Send + Sync {
    /// Find by ID
    async fn find_by_id(
        &self,
        id: AppuntamentoId,
    ) -> Result<Option<AppuntamentoAggregate>, RepositoryError>;

    /// Save (insert or update)
    async fn save(&self, aggregate: &AppuntamentoAggregate) -> Result<(), RepositoryError>;

    /// List all (non-deleted)
    async fn list(&self) -> Result<Vec<AppuntamentoAggregate>, RepositoryError>;

    /// List by cliente
    async fn list_by_cliente(
        &self,
        cliente_id: &str,
    ) -> Result<Vec<AppuntamentoAggregate>, RepositoryError>;

    /// List by operatore
    async fn list_by_operatore(
        &self,
        operatore_id: &str,
    ) -> Result<Vec<AppuntamentoAggregate>, RepositoryError>;

    /// List by date range
    async fn list_by_date_range(
        &self,
        start: NaiveDateTime,
        end: NaiveDateTime,
    ) -> Result<Vec<AppuntamentoAggregate>, RepositoryError>;

    /// List by operatore and date
    async fn list_by_operatore_and_date(
        &self,
        operatore_id: &str,
        date: NaiveDateTime,
    ) -> Result<Vec<AppuntamentoAggregate>, RepositoryError>;

    /// Find by operatore and date range
    async fn find_by_operatore_and_date_range(
        &self,
        operatore_id: &str,
        start: chrono::NaiveDate,
        end: chrono::NaiveDate,
    ) -> Result<Vec<AppuntamentoAggregate>, RepositoryError>;

    /// Delete (soft delete)
    async fn delete(&self, id: AppuntamentoId) -> Result<(), RepositoryError>;
}

/// Cliente Repository trait (future implementation)
#[async_trait]
pub trait ClienteRepository: Send + Sync {
    // TODO: Define methods
}

/// Operatore Repository trait (future implementation)
#[async_trait]
pub trait OperatoreRepository: Send + Sync {
    // TODO: Define methods
}

/// Servizio Repository trait (future implementation)
#[async_trait]
pub trait ServizioRepository: Send + Sync {
    // TODO: Define methods
}
