// ═══════════════════════════════════════════════════════════════════
// FLUXION - Commands Module
// Export all Tauri commands
// ═══════════════════════════════════════════════════════════════════

pub mod clienti;
pub mod servizi;
pub mod operatori;
pub mod appuntamenti;
pub mod appuntamenti_ddd; // DDD-layer commands (thin controllers)
pub mod whatsapp;
pub mod orari;

// Re-export for convenience
pub use clienti::*;
pub use servizi::*;
pub use operatori::*;
pub use appuntamenti::*;
pub use appuntamenti_ddd::*;
pub use whatsapp::*;
pub use orari::*;
