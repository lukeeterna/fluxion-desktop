// ═══════════════════════════════════════════════════════════════════
// FLUXION - Commands Module
// Export all Tauri commands
// ═══════════════════════════════════════════════════════════════════

pub mod clienti;
pub mod servizi;
pub mod operatori;
pub mod appuntamenti;

// Re-export for convenience
pub use clienti::*;
pub use servizi::*;
pub use operatori::*;
pub use appuntamenti::*;
