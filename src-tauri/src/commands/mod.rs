// ═══════════════════════════════════════════════════════════════════
// FLUXION - Commands Module
// Export all Tauri commands
// ═══════════════════════════════════════════════════════════════════

pub mod appuntamenti;
pub mod audit; // GDPR-compliant audit logging
pub mod appuntamenti_ddd; // DDD-layer commands (thin controllers)
pub mod cassa;
pub mod clienti;
pub mod dashboard; // Dashboard statistics
pub mod faq_template; // RAG locale leggero - template FAQ con variabili DB
pub mod fatture; // Fase 6: Fatturazione Elettronica FatturaPA
pub mod license;
pub mod loyalty; // Fase 5: Tessera timbri, VIP, Referral, Pacchetti
pub mod operatori;
pub mod orari;
pub mod rag; // RAG with Groq LLM for FAQ-based answers
pub mod schede_cliente; // Schede cliente verticali per settori specifici
pub mod license_ed25519; // License System Ed25519 (Phase 8.5) - Offline
pub mod servizi;
pub mod settings; // Settings - SMTP, configurazioni runtime
pub mod setup; // Setup Wizard - configurazione iniziale
pub mod supplier; // Supplier Management - fornitori e ordini (Fase 7.5)
pub mod support; // Fluxion Care: diagnostics, backup, support bundle
pub mod voice; // Piper TTS - offline text-to-speech
pub mod voice_calls; // Voice Agent - chiamate telefoniche VoIP (Fase 7)
pub mod voice_pipeline; // Voice Pipeline - Python voice agent management (Fase 7)
pub mod whatsapp; // WhatsApp local automation (NO API costs)
 // License system (Phase 8) - Keygen.sh integration

#[cfg(debug_assertions)]
pub mod mcp; // MCP commands for AI Live Testing (debug only)

// Re-export for convenience
pub use appuntamenti::*;
pub use appuntamenti_ddd::*;
pub use cassa::*;
pub use clienti::*;
pub use dashboard::*;
pub use faq_template::*;
pub use fatture::*;
pub use license::*;
pub use loyalty::*;
pub use operatori::*;
pub use orari::*;
pub use rag::*;
pub use schede_cliente::*;
// Re-export additional functions for lib.rs compatibility
pub use schede_cliente::delete_scheda_odontoiatrica;
pub use schede_cliente::has_scheda_odontoiatrica;
pub use schede_cliente::get_all_schede_odontoiatriche;
pub use schede_cliente::update_odontogramma;
pub use schede_cliente::add_trattamento_to_storia;
pub use license_ed25519::*;
pub use servizi::*;
pub use settings::*;
pub use setup::*;
pub use supplier::*;
pub use support::*;
pub use voice::*;
pub use voice_calls::*;
pub use voice_pipeline::*;
pub use audit::*;
pub use whatsapp::*;
