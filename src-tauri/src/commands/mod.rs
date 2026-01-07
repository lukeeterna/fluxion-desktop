// ═══════════════════════════════════════════════════════════════════
// FLUXION - Commands Module
// Export all Tauri commands
// ═══════════════════════════════════════════════════════════════════

pub mod appuntamenti;
pub mod appuntamenti_ddd; // DDD-layer commands (thin controllers)
pub mod clienti;
pub mod dashboard; // Dashboard statistics
pub mod fatture; // Fase 6: Fatturazione Elettronica FatturaPA
pub mod loyalty; // Fase 5: Tessera timbri, VIP, Referral, Pacchetti
pub mod operatori;
pub mod orari;
pub mod servizi;
pub mod support; // Fluxion Care: diagnostics, backup, support bundle
pub mod voice; // Piper TTS - offline text-to-speech
pub mod whatsapp; // WhatsApp local automation (NO API costs)
pub mod rag; // RAG with Groq LLM for FAQ-based answers
pub mod setup; // Setup Wizard - configurazione iniziale
pub mod faq_template; // RAG locale leggero - template FAQ con variabili DB

// Re-export for convenience
pub use appuntamenti::*;
pub use appuntamenti_ddd::*;
pub use clienti::*;
pub use dashboard::*;
pub use fatture::*;
pub use loyalty::*;
pub use operatori::*;
pub use orari::*;
pub use servizi::*;
pub use support::*;
pub use voice::*;
pub use whatsapp::*;
pub use rag::*;
pub use setup::*;
pub use faq_template::*;
