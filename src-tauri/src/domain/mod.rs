pub mod appuntamento_aggregate;
pub mod errors;

pub use appuntamento_aggregate::{AppuntamentoAggregate, AppuntamentoId, AppuntamentoStato};
pub use errors::{DomainError, DomainSuggestion, DomainWarning, ValidationResult};
