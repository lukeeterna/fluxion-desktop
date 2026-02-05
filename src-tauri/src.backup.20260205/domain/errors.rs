use thiserror::Error;

use super::appuntamento_aggregate::AppuntamentoStato;
use chrono::NaiveDateTime;

/// Domain errors per Appuntamento aggregate
#[derive(Debug, Error, Clone, PartialEq)]
pub enum DomainError {
    /// Transizione stato non valida
    #[error("Transizione stato non valida: da {from:?} a {to:?}")]
    TransizioneNonValida {
        from: AppuntamentoStato,
        to: AppuntamentoStato,
    },

    /// Appuntamento nel passato
    #[error("Appuntamento nel passato: {data}")]
    AppuntamentoPassato { data: NaiveDateTime },

    /// Conflict: operatore già impegnato in questo slot
    #[error("Operatore {operatore_id} già impegnato il {data_ora}")]
    ConflictOperatore {
        operatore_id: String,
        data_ora: NaiveDateTime,
    },

    /// Conflict: sala occupata
    #[error("Sala {sala_id} occupata il {data_ora}")]
    ConflictSala {
        sala_id: String,
        data_ora: NaiveDateTime,
    },

    /// Servizio richiede attrezzatura non disponibile
    #[error("Servizio richiede attrezzatura non disponibile: {attrezzatura}")]
    AttrezzaturaNonDisponibile { attrezzatura: String },

    /// Appuntamento supera mezzanotte
    #[error("Appuntamento termina dopo mezzanotte: {ora_fine}")]
    OltreMezzanotte { ora_fine: NaiveDateTime },

    /// Durata appuntamento non valida
    #[error("Durata appuntamento non valida: {durata_minuti} minuti")]
    DurataNonValida { durata_minuti: i32 },

    /// Cliente non trovato
    #[error("Cliente {cliente_id} non trovato")]
    ClienteNonTrovato { cliente_id: String },

    /// Operatore non trovato
    #[error("Operatore {operatore_id} non trovato")]
    OperatoreNonTrovato { operatore_id: String },

    /// Servizio non trovato
    #[error("Servizio {servizio_id} non trovato")]
    ServizioNonTrovato { servizio_id: String },

    /// Campo obbligatorio mancante
    #[error("Campo obbligatorio mancante: {campo}")]
    CampoMancante { campo: String },

    /// Valore non valido
    #[error("Valore non valido per {campo}: {valore}")]
    ValoreNonValido { campo: String, valore: String },
}

/// Warning (continuabili con conferma operatore)
#[derive(Debug, Clone, PartialEq)]
pub enum DomainWarning {
    /// Fuori orario lavorativo
    FuoriOrarioLavorativo {
        orario_richiesto: NaiveDateTime,
        orario_lavorativo_inizio: String,
        orario_lavorativo_fine: String,
    },

    /// Giorno festivo
    GiornoFestivo {
        data: NaiveDateTime,
        nome_festivita: String,
        prossimo_giorno_lavorativo: NaiveDateTime,
    },

    /// Cliente con storico ritardi pagamento
    ClienteStoricoRitardi {
        cliente_id: String,
        numero_ritardi: usize,
    },

    /// Operatore non specializzato per questo servizio
    OperatoreNonSpecializzato {
        operatore_id: String,
        servizio_id: String,
    },

    /// Pausa tra appuntamenti troppo breve
    PausaTroppoBreve {
        minuti_pausa: i32,
        minuti_raccomandati: i32,
    },
}

/// Suggerimenti proattivi (non bloccanti)
#[derive(Debug, Clone, PartialEq)]
pub enum DomainSuggestion {
    /// Slot migliore disponibile
    SlotMigliore {
        data_ora_suggerita: NaiveDateTime,
        motivo: String,
    },

    /// Cliente ha orario preferito storico
    OrarioPreferito {
        cliente_id: String,
        orario_preferito: String,
        disponibilita: Vec<NaiveDateTime>,
    },

    /// Operatore con specializzazione disponibile
    OperatoreSpecializzato {
        operatore_id: String,
        nome_operatore: String,
        disponibilita: Vec<NaiveDateTime>,
    },
}

/// Validation result con multi-layer errors/warnings/suggestions
#[derive(Debug, Clone)]
pub struct ValidationResult {
    pub hard_blocks: Vec<DomainError>,
    pub warnings: Vec<DomainWarning>,
    pub suggestions: Vec<DomainSuggestion>,
}

impl ValidationResult {
    pub fn new() -> Self {
        Self {
            hard_blocks: vec![],
            warnings: vec![],
            suggestions: vec![],
        }
    }

    pub fn is_blocked(&self) -> bool {
        !self.hard_blocks.is_empty()
    }

    pub fn has_warnings(&self) -> bool {
        !self.warnings.is_empty()
    }

    pub fn has_suggestions(&self) -> bool {
        !self.suggestions.is_empty()
    }

    pub fn add_error(&mut self, error: DomainError) {
        self.hard_blocks.push(error);
    }

    pub fn add_warning(&mut self, warning: DomainWarning) {
        self.warnings.push(warning);
    }

    pub fn add_suggestion(&mut self, suggestion: DomainSuggestion) {
        self.suggestions.push(suggestion);
    }
}

impl Default for ValidationResult {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_validation_result_empty_not_blocked() {
        let result = ValidationResult::new();
        assert!(!result.is_blocked());
        assert!(!result.has_warnings());
        assert!(!result.has_suggestions());
    }

    #[test]
    fn test_validation_result_with_error_blocked() {
        let mut result = ValidationResult::new();
        result.add_error(DomainError::AppuntamentoPassato {
            data: NaiveDateTime::parse_from_str("2020-01-01 10:00:00", "%Y-%m-%d %H:%M:%S")
                .unwrap(),
        });
        assert!(result.is_blocked());
    }

    #[test]
    fn test_validation_result_with_warning_not_blocked() {
        let mut result = ValidationResult::new();
        result.add_warning(DomainWarning::FuoriOrarioLavorativo {
            orario_richiesto: NaiveDateTime::parse_from_str(
                "2026-01-15 22:00:00",
                "%Y-%m-%d %H:%M:%S",
            )
            .unwrap(),
            orario_lavorativo_inizio: "09:00".to_string(),
            orario_lavorativo_fine: "18:00".to_string(),
        });
        assert!(!result.is_blocked());
        assert!(result.has_warnings());
    }
}
