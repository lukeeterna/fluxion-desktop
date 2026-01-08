// ═══════════════════════════════════════════════════════════════════
// FLUXION - Commands Module
// Export all Tauri commands
// ═══════════════════════════════════════════════════════════════════

pub mod appuntamenti;
pub mod appuntamenti_ddd; // DDD-layer commands (thin controllers)
pub mod cassa;
pub mod clienti;
pub mod dashboard; // Dashboard statistics
pub mod faq_template; // RAG locale leggero - template FAQ con variabili DB
pub mod fatture; // Fase 6: Fatturazione Elettronica FatturaPA
pub mod loyalty; // Fase 5: Tessera timbri, VIP, Referral, Pacchetti
pub mod operatori;
pub mod orari;
pub mod rag; // RAG with Groq LLM for FAQ-based answers
pub mod servizi;
pub mod setup; // Setup Wizard - configurazione iniziale
pub mod support; // Fluxion Care: diagnostics, backup, support bundle
pub mod voice; // Piper TTS - offline text-to-speech
pub mod whatsapp; // WhatsApp local automation (NO API costs) // Sistema Cassa/Incassi - FLUXION gestionale puro

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
pub use loyalty::*;
pub use operatori::*;
pub use orari::*;
pub use rag::*;
pub use servizi::*;
pub use setup::*;
pub use support::*;
pub use voice::*;
pub use whatsapp::*;
