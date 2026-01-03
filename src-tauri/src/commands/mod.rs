// ═══════════════════════════════════════════════════════════════════
// FLUXION - Commands Module
// Export all Tauri commands
// ═══════════════════════════════════════════════════════════════════

pub mod appuntamenti;
pub mod appuntamenti_ddd; // DDD-layer commands (thin controllers)
pub mod clienti;
pub mod operatori;
pub mod orari;
pub mod servizi;
pub mod whatsapp;

// Re-export for convenience
pub use appuntamenti::*;
pub use appuntamenti_ddd::*;
pub use clienti::*;
pub use operatori::*;
pub use orari::*;
pub use servizi::*;
pub use whatsapp::*;
