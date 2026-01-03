pub mod appuntamento_aggregate;
pub mod errors;
pub mod repository;

pub use appuntamento_aggregate::{
    AppuntamentoAggregate, AppuntamentoId, AppuntamentoStato, OverrideInfo,
};
pub use errors::{DomainError, DomainSuggestion, DomainWarning, ValidationResult};
pub use repository::{AppuntamentoRepository, RepositoryError};
