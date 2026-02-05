pub mod appuntamento_aggregate;
pub mod audit;
pub mod errors;
pub mod repository;

pub use appuntamento_aggregate::{
    AppuntamentoAggregate, AppuntamentoId, AppuntamentoStato, OverrideInfo,
};
pub use audit::{
    AuditAction, AuditLog, AuditLogBuilder, AuditLogBuilderError, AuditLogQuery, AuditSource,
    GdprCategory, UserType,
};
pub use errors::{DomainError, DomainSuggestion, DomainWarning, ValidationResult};
pub use repository::{AppuntamentoRepository, RepositoryError};
