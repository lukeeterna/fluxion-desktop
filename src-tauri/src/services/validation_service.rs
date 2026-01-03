use chrono::{Datelike, NaiveDateTime, NaiveTime, Timelike, Utc};

use crate::domain::{
    AppuntamentoAggregate, DomainError, DomainSuggestion, DomainWarning, ValidationResult,
};

/// Validation Service - 3-Layer Validation Logic
pub struct ValidationService {
    // Configuration (caricata da config/validation-rules.yaml)
    pub pausa_minima_minuti: i32,
    pub orario_lavorativo_inizio: NaiveTime,
    pub orario_lavorativo_fine: NaiveTime,
}

impl ValidationService {
    pub fn new() -> Self {
        Self {
            pausa_minima_minuti: 15,
            orario_lavorativo_inizio: NaiveTime::from_hms_opt(9, 0, 0).unwrap(),
            orario_lavorativo_fine: NaiveTime::from_hms_opt(18, 0, 0).unwrap(),
        }
    }

    /// Validazione completa appuntamento (3-layer)
    pub async fn valida_appuntamento(
        &self,
        appuntamento: &AppuntamentoAggregate,
        appuntamenti_esistenti: &[AppuntamentoAggregate],
        giorni_festivi: &[(NaiveDateTime, String)],
    ) -> ValidationResult {
        let mut result = ValidationResult::new();

        // LAYER 1: HARD BLOCKS (blocco totale)
        self.check_appuntamento_passato(appuntamento, &mut result);
        self.check_conflict_operatore(appuntamento, appuntamenti_esistenti, &mut result);
        self.check_midnight_wrap(appuntamento, &mut result);

        // Se ci sono hard block, stop (non eseguire altri check)
        if result.is_blocked() {
            return result;
        }

        // LAYER 2: WARNINGS (continuabili con conferma)
        self.check_fuori_orario_lavorativo(appuntamento, &mut result);
        self.check_giorno_festivo(appuntamento, giorni_festivi, &mut result);

        // LAYER 3: SUGGERIMENTI (proattivi, non bloccanti)
        self.check_slot_migliore(appuntamento, appuntamenti_esistenti, &mut result);

        result
    }

    /// CHECK 1: Appuntamento nel passato (HARD BLOCK)
    fn check_appuntamento_passato(
        &self,
        appuntamento: &AppuntamentoAggregate,
        result: &mut ValidationResult,
    ) {
        let now = Utc::now().naive_utc();
        if appuntamento.data_ora < now {
            result.add_error(DomainError::AppuntamentoPassato {
                data: appuntamento.data_ora,
            });
        }
    }

    /// CHECK 2: Conflict operatore già impegnato (HARD BLOCK)
    fn check_conflict_operatore(
        &self,
        appuntamento: &AppuntamentoAggregate,
        appuntamenti_esistenti: &[AppuntamentoAggregate],
        result: &mut ValidationResult,
    ) {
        let inizio = appuntamento.data_ora;
        let fine = appuntamento.ora_fine();

        for existing in appuntamenti_esistenti {
            // Skip self (quando modifico appuntamento esistente)
            if existing.id == appuntamento.id {
                continue;
            }

            // Skip appuntamenti non confermati
            if !existing.is_confermato() {
                continue;
            }

            // Check stesso operatore
            if existing.operatore_id != appuntamento.operatore_id {
                continue;
            }

            let existing_inizio = existing.data_ora;
            let existing_fine = existing.ora_fine();

            // Check overlap
            if inizio < existing_fine && fine > existing_inizio {
                result.add_error(DomainError::ConflictOperatore {
                    operatore_id: appuntamento.operatore_id.clone(),
                    data_ora: appuntamento.data_ora,
                });
                return; // Stop al primo conflict
            }
        }
    }

    /// CHECK 3: Appuntamento supera mezzanotte (HARD BLOCK)
    fn check_midnight_wrap(
        &self,
        appuntamento: &AppuntamentoAggregate,
        result: &mut ValidationResult,
    ) {
        let ora_fine = appuntamento.ora_fine();

        // Se ora_fine è giorno diverso da ora_inizio → ha superato mezzanotte
        if ora_fine.date() != appuntamento.data_ora.date() {
            result.add_error(DomainError::OltreMezzanotte { ora_fine });
        }
    }

    /// CHECK 4: Fuori orario lavorativo (WARNING)
    fn check_fuori_orario_lavorativo(
        &self,
        appuntamento: &AppuntamentoAggregate,
        result: &mut ValidationResult,
    ) {
        let ora = appuntamento.data_ora.time();

        if ora < self.orario_lavorativo_inizio || ora > self.orario_lavorativo_fine {
            result.add_warning(DomainWarning::FuoriOrarioLavorativo {
                orario_richiesto: appuntamento.data_ora,
                orario_lavorativo_inizio: self.orario_lavorativo_inizio.to_string(),
                orario_lavorativo_fine: self.orario_lavorativo_fine.to_string(),
            });
        }
    }

    /// CHECK 5: Giorno festivo (WARNING)
    fn check_giorno_festivo(
        &self,
        appuntamento: &AppuntamentoAggregate,
        giorni_festivi: &[(NaiveDateTime, String)],
        result: &mut ValidationResult,
    ) {
        let data_appuntamento = appuntamento.data_ora.date();

        for (data_festivo, nome) in giorni_festivi {
            if data_festivo.date() == data_appuntamento {
                // Trova prossimo giorno lavorativo (semplificato: +1 giorno)
                let prossimo = appuntamento.data_ora + chrono::Duration::days(1);

                result.add_warning(DomainWarning::GiornoFestivo {
                    data: appuntamento.data_ora,
                    nome_festivita: nome.clone(),
                    prossimo_giorno_lavorativo: prossimo,
                });
                return;
            }
        }
    }

    /// CHECK 6: Suggerimento slot migliore (SUGGESTION)
    fn check_slot_migliore(
        &self,
        appuntamento: &AppuntamentoAggregate,
        appuntamenti_esistenti: &[AppuntamentoAggregate],
        result: &mut ValidationResult,
    ) {
        // Trova slot con pausa più lunga dopo
        let fine = appuntamento.ora_fine();

        // Trova prossimo appuntamento operatore
        let prossimo = appuntamenti_esistenti
            .iter()
            .filter(|a| {
                a.operatore_id == appuntamento.operatore_id
                    && a.data_ora.date() == appuntamento.data_ora.date()
                    && a.data_ora > fine
            })
            .min_by_key(|a| a.data_ora);

        if let Some(next) = prossimo {
            let pausa_minuti = (next.data_ora - fine).num_minutes() as i32;

            if pausa_minuti < self.pausa_minima_minuti {
                result.add_warning(DomainWarning::PausaTroppoBreve {
                    minuti_pausa: pausa_minuti,
                    minuti_raccomandati: self.pausa_minima_minuti,
                });

                // Suggerisci slot alternativo (es. 30 min dopo)
                let slot_suggerito = fine + chrono::Duration::minutes(30);
                result.add_suggestion(DomainSuggestion::SlotMigliore {
                    data_ora_suggerita: slot_suggerito,
                    motivo: format!(
                        "Pausa più lunga ({} min) prima del prossimo appuntamento",
                        (next.data_ora - slot_suggerito).num_minutes()
                    ),
                });
            }
        }
    }
}

impl Default for ValidationService {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use chrono::NaiveDate;

    fn make_appuntamento(data_ora: NaiveDateTime, durata: i32) -> AppuntamentoAggregate {
        AppuntamentoAggregate::new_bozza(
            "cliente1".to_string(),
            "operatore1".to_string(),
            "servizio1".to_string(),
            data_ora,
            durata,
        )
        .unwrap()
    }

    #[test]
    fn test_appuntamento_passato_blocked() {
        let service = ValidationService::new();

        let passato = NaiveDate::from_ymd_opt(2020, 1, 1)
            .unwrap()
            .and_hms_opt(10, 0, 0)
            .unwrap();

        let app = make_appuntamento(passato, 60);

        let result = futures::executor::block_on(service.valida_appuntamento(&app, &[], &[]));

        assert!(result.is_blocked());
        assert_eq!(result.hard_blocks.len(), 1);
    }

    #[test]
    fn test_conflict_operatore_blocked() {
        let service = ValidationService::new();

        let data = NaiveDate::from_ymd_opt(2026, 12, 31)
            .unwrap()
            .and_hms_opt(10, 0, 0)
            .unwrap();

        let app1 = make_appuntamento(data, 60);
        let app2 = make_appuntamento(data + chrono::Duration::minutes(30), 60); // Overlap

        let result = futures::executor::block_on(service.valida_appuntamento(&app2, &[app1], &[]));

        assert!(result.is_blocked());
        assert!(matches!(
            result.hard_blocks[0],
            DomainError::ConflictOperatore { .. }
        ));
    }

    #[test]
    fn test_midnight_wrap_blocked() {
        let service = ValidationService::new();

        let data = NaiveDate::from_ymd_opt(2026, 12, 31)
            .unwrap()
            .and_hms_opt(23, 30, 0)
            .unwrap();

        let app = make_appuntamento(data, 60); // Termina 00:30 giorno dopo

        let result = futures::executor::block_on(service.valida_appuntamento(&app, &[], &[]));

        assert!(result.is_blocked());
        assert!(matches!(
            result.hard_blocks[0],
            DomainError::OltreMezzanotte { .. }
        ));
    }

    #[test]
    fn test_fuori_orario_lavorativo_warning() {
        let service = ValidationService::new();

        let data = NaiveDate::from_ymd_opt(2026, 12, 31)
            .unwrap()
            .and_hms_opt(22, 0, 0)
            .unwrap(); // 22:00 fuori orario

        let app = make_appuntamento(data, 30);

        let result = futures::executor::block_on(service.valida_appuntamento(&app, &[], &[]));

        assert!(!result.is_blocked());
        assert!(result.has_warnings());
        assert!(matches!(
            result.warnings[0],
            DomainWarning::FuoriOrarioLavorativo { .. }
        ));
    }

    #[test]
    fn test_giorno_festivo_warning() {
        let service = ValidationService::new();

        let capodanno = NaiveDate::from_ymd_opt(2026, 1, 1)
            .unwrap()
            .and_hms_opt(10, 0, 0)
            .unwrap();

        let app = make_appuntamento(capodanno, 60);

        let festivita = vec![(capodanno, "Capodanno".to_string())];

        let result =
            futures::executor::block_on(service.valida_appuntamento(&app, &[], &festivita));

        assert!(!result.is_blocked());
        assert!(result.has_warnings());
        assert!(matches!(
            result.warnings[0],
            DomainWarning::GiornoFestivo { .. }
        ));
    }

    #[test]
    fn test_validation_ok_no_errors() {
        let service = ValidationService::new();

        let data = NaiveDate::from_ymd_opt(2026, 12, 31)
            .unwrap()
            .and_hms_opt(14, 0, 0)
            .unwrap(); // Giovedì 14:00 (ok)

        let app = make_appuntamento(data, 60);

        let result = futures::executor::block_on(service.valida_appuntamento(&app, &[], &[]));

        assert!(!result.is_blocked());
        assert!(!result.has_warnings());
    }
}
