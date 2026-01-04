// ═══════════════════════════════════════════════════════════════════
// FLUXION - Commands Module
// Export all Tauri commands
// ═══════════════════════════════════════════════════════════════════

pub mod appuntamenti;
pub mod appuntamenti_ddd; // DDD-layer commands (thin controllers)
pub mod clienti;
pub mod loyalty; // Fase 5: Tessera timbri, VIP, Referral, Pacchetti
pub mod operatori;
pub mod orari;
pub mod servizi;
pub mod support; // Fluxion Care: diagnostics, backup, support bundle
pub mod whatsapp;

// Re-export for convenience
pub use appuntamenti::*;
pub use appuntamenti_ddd::*;
pub use clienti::*;
pub use loyalty::*;
pub use operatori::*;
pub use orari::*;
pub use servizi::*;
pub use support::*;
pub use whatsapp::*;
