pub mod appuntamento_service;
pub mod festivita_service;
pub mod validation_service;

pub use appuntamento_service::{AppuntamentoService, ServiceError};
pub use festivita_service::{Festivita, FestivitaService};
pub use validation_service::ValidationService;
