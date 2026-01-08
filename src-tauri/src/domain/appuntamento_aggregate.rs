use chrono::{NaiveDateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

use super::errors::{DomainError, ValidationResult};

/// Appuntamento ID (value object)
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub struct AppuntamentoId(Uuid);

impl AppuntamentoId {
    pub fn new() -> Self {
        Self(Uuid::new_v4())
    }

    pub fn from_string(s: &str) -> Result<Self, DomainError> {
        Uuid::parse_str(s)
            .map(Self)
            .map_err(|_| DomainError::ValoreNonValido {
                campo: "id".to_string(),
                valore: s.to_string(),
            })
    }

    pub fn to_string(&self) -> String {
        self.0.to_string()
    }
}

impl Default for AppuntamentoId {
    fn default() -> Self {
        Self::new()
    }
}

/// Stati appuntamento (State Machine)
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum AppuntamentoStato {
    /// Bozza iniziale (non salvata definitivamente)
    Bozza,

    /// Proposta validata (cliente può vedere)
    Proposta,

    /// In attesa conferma operatore
    InAttesaOperatore,

    /// Confermato da operatore
    Confermato,

    /// Confermato con override warning (tracciato)
    ConfermatoConOverride,

    /// Rifiutato da operatore
    Rifiutato,

    /// Completato (data/ora passata)
    Completato,

    /// Cancellato (soft delete)
    Cancellato,
}

impl AppuntamentoStato {
    pub fn as_str(&self) -> &str {
        match self {
            Self::Bozza => "Bozza",
            Self::Proposta => "Proposta",
            Self::InAttesaOperatore => "InAttesaOperatore",
            Self::Confermato => "Confermato",
            Self::ConfermatoConOverride => "ConfermatoConOverride",
            Self::Rifiutato => "Rifiutato",
            Self::Completato => "Completato",
            Self::Cancellato => "Cancellato",
        }
    }

    pub fn from_str(s: &str) -> Result<Self, DomainError> {
        match s {
            "Bozza" => Ok(Self::Bozza),
            "Proposta" => Ok(Self::Proposta),
            "InAttesaOperatore" => Ok(Self::InAttesaOperatore),
            "Confermato" => Ok(Self::Confermato),
            "ConfermatoConOverride" => Ok(Self::ConfermatoConOverride),
            "Rifiutato" => Ok(Self::Rifiutato),
            "Completato" => Ok(Self::Completato),
            "Cancellato" => Ok(Self::Cancellato),
            _ => Err(DomainError::ValoreNonValido {
                campo: "stato".to_string(),
                valore: s.to_string(),
            }),
        }
    }
}

/// Override info (quando operatore forza conferma con warning)
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct OverrideInfo {
    pub timestamp: NaiveDateTime,
    pub operatore_id: String,
    pub motivazione: Option<String>,
    pub warnings_ignorati: Vec<String>,
}

/// Appuntamento Aggregate (DDD)
#[derive(Debug, Clone, PartialEq)]
pub struct AppuntamentoAggregate {
    pub id: AppuntamentoId,
    pub stato: AppuntamentoStato,
    pub cliente_id: String,
    pub operatore_id: String,
    pub servizio_id: String,
    pub data_ora: NaiveDateTime,
    pub durata_minuti: i32,
    pub note: Option<String>,
    pub created_at: NaiveDateTime,
    pub updated_at: NaiveDateTime,
    pub override_info: Option<OverrideInfo>,
}

impl AppuntamentoAggregate {
    /// Crea nuova bozza
    pub fn new_bozza(
        cliente_id: String,
        operatore_id: String,
        servizio_id: String,
        data_ora: NaiveDateTime,
        durata_minuti: i32,
    ) -> Result<Self, DomainError> {
        // Validazioni base
        if cliente_id.is_empty() {
            return Err(DomainError::CampoMancante {
                campo: "cliente_id".to_string(),
            });
        }
        if operatore_id.is_empty() {
            return Err(DomainError::CampoMancante {
                campo: "operatore_id".to_string(),
            });
        }
        if servizio_id.is_empty() {
            return Err(DomainError::CampoMancante {
                campo: "servizio_id".to_string(),
            });
        }
        if durata_minuti <= 0 {
            return Err(DomainError::DurataNonValida { durata_minuti });
        }

        let now = Utc::now().naive_utc();

        Ok(Self {
            id: AppuntamentoId::new(),
            stato: AppuntamentoStato::Bozza,
            cliente_id,
            operatore_id,
            servizio_id,
            data_ora,
            durata_minuti,
            note: None,
            created_at: now,
            updated_at: now,
            override_info: None,
        })
    }

    /// Valida e proponi appuntamento
    pub fn proponi(&mut self, validation: &ValidationResult) -> Result<(), DomainError> {
        // Check hard blocks
        if validation.is_blocked() {
            return Err(validation.hard_blocks[0].clone());
        }

        // Transizione Bozza → Proposta
        self.validate_transizione(&AppuntamentoStato::Proposta)?;
        self.stato = AppuntamentoStato::Proposta;
        self.updated_at = Utc::now().naive_utc();

        Ok(())
    }

    /// Cliente conferma proposta → InAttesaOperatore
    pub fn conferma_cliente(&mut self) -> Result<(), DomainError> {
        self.validate_transizione(&AppuntamentoStato::InAttesaOperatore)?;
        self.stato = AppuntamentoStato::InAttesaOperatore;
        self.updated_at = Utc::now().naive_utc();
        Ok(())
    }

    /// Operatore accetta appuntamento
    pub fn conferma_operatore(&mut self) -> Result<(), DomainError> {
        self.validate_transizione(&AppuntamentoStato::Confermato)?;
        self.stato = AppuntamentoStato::Confermato;
        self.updated_at = Utc::now().naive_utc();
        Ok(())
    }

    /// Operatore forza conferma con override (ignora warning)
    pub fn conferma_con_override(
        &mut self,
        operatore_id: String,
        motivazione: Option<String>,
        warnings_ignorati: Vec<String>,
    ) -> Result<(), DomainError> {
        self.validate_transizione(&AppuntamentoStato::ConfermatoConOverride)?;

        let now = Utc::now().naive_utc();
        self.override_info = Some(OverrideInfo {
            timestamp: now,
            operatore_id,
            motivazione,
            warnings_ignorati,
        });

        self.stato = AppuntamentoStato::ConfermatoConOverride;
        self.updated_at = now;
        Ok(())
    }

    /// Operatore rifiuta appuntamento
    pub fn rifiuta(&mut self, motivazione: Option<String>) -> Result<(), DomainError> {
        self.validate_transizione(&AppuntamentoStato::Rifiutato)?;
        self.note = motivazione; // Store rejection reason
        self.stato = AppuntamentoStato::Rifiutato;
        self.updated_at = Utc::now().naive_utc();
        Ok(())
    }

    /// Sistema completa appuntamento (data/ora superata)
    pub fn completa(&mut self) -> Result<(), DomainError> {
        self.validate_transizione(&AppuntamentoStato::Completato)?;

        // Verifica che data/ora sia effettivamente passata
        let now = Utc::now().naive_utc();
        let fine_appuntamento =
            self.data_ora + chrono::Duration::minutes(self.durata_minuti as i64);

        if fine_appuntamento > now {
            return Err(DomainError::ValoreNonValido {
                campo: "data_ora".to_string(),
                valore: "Appuntamento non ancora terminato".to_string(),
            });
        }

        self.stato = AppuntamentoStato::Completato;
        self.updated_at = now;
        Ok(())
    }

    /// Cancella appuntamento (soft delete)
    pub fn cancella(&mut self) -> Result<(), DomainError> {
        self.validate_transizione(&AppuntamentoStato::Cancellato)?;
        self.stato = AppuntamentoStato::Cancellato;
        self.updated_at = Utc::now().naive_utc();
        Ok(())
    }

    /// Modifica appuntamento (solo in stato Bozza/Proposta)
    pub fn modifica(
        &mut self,
        data_ora: Option<NaiveDateTime>,
        durata_minuti: Option<i32>,
        note: Option<String>,
    ) -> Result<(), DomainError> {
        // Solo Bozza/Proposta modificabili
        match self.stato {
            AppuntamentoStato::Bozza | AppuntamentoStato::Proposta => {}
            _ => {
                return Err(DomainError::TransizioneNonValida {
                    from: self.stato.clone(),
                    to: AppuntamentoStato::Bozza,
                })
            }
        }

        if let Some(dt) = data_ora {
            self.data_ora = dt;
        }
        if let Some(dur) = durata_minuti {
            if dur <= 0 {
                return Err(DomainError::DurataNonValida { durata_minuti: dur });
            }
            self.durata_minuti = dur;
        }
        if let Some(n) = note {
            self.note = Some(n);
        }

        // Se era Proposta, torna Bozza (richiede ri-validazione)
        if self.stato == AppuntamentoStato::Proposta {
            self.stato = AppuntamentoStato::Bozza;
        }

        self.updated_at = Utc::now().naive_utc();
        Ok(())
    }

    /// Validazione transizione stato
    fn validate_transizione(&self, target: &AppuntamentoStato) -> Result<(), DomainError> {
        let valid = match (&self.stato, target) {
            // Bozza → Proposta
            (AppuntamentoStato::Bozza, AppuntamentoStato::Proposta) => true,

            // Proposta → InAttesaOperatore
            (AppuntamentoStato::Proposta, AppuntamentoStato::InAttesaOperatore) => true,
            // Proposta → Bozza (modifica)
            (AppuntamentoStato::Proposta, AppuntamentoStato::Bozza) => true,

            // InAttesaOperatore → Confermato
            (AppuntamentoStato::InAttesaOperatore, AppuntamentoStato::Confermato) => true,
            // InAttesaOperatore → ConfermatoConOverride
            (AppuntamentoStato::InAttesaOperatore, AppuntamentoStato::ConfermatoConOverride) => {
                true
            }
            // InAttesaOperatore → Rifiutato
            (AppuntamentoStato::InAttesaOperatore, AppuntamentoStato::Rifiutato) => true,

            // Confermato → Completato
            (AppuntamentoStato::Confermato, AppuntamentoStato::Completato) => true,
            // Confermato → Cancellato
            (AppuntamentoStato::Confermato, AppuntamentoStato::Cancellato) => true,

            // ConfermatoConOverride → Completato
            (AppuntamentoStato::ConfermatoConOverride, AppuntamentoStato::Completato) => true,
            // ConfermatoConOverride → Cancellato
            (AppuntamentoStato::ConfermatoConOverride, AppuntamentoStato::Cancellato) => true,

            // Bozza → Cancellato (può cancellare bozza)
            (AppuntamentoStato::Bozza, AppuntamentoStato::Cancellato) => true,
            // Proposta → Cancellato
            (AppuntamentoStato::Proposta, AppuntamentoStato::Cancellato) => true,

            // Tutti gli altri non validi
            _ => false,
        };

        if valid {
            Ok(())
        } else {
            Err(DomainError::TransizioneNonValida {
                from: self.stato.clone(),
                to: target.clone(),
            })
        }
    }

    /// Calcola ora fine appuntamento
    pub fn ora_fine(&self) -> NaiveDateTime {
        self.data_ora + chrono::Duration::minutes(self.durata_minuti as i64)
    }

    /// Check se appuntamento è nel passato
    pub fn is_passato(&self) -> bool {
        self.data_ora < Utc::now().naive_utc()
    }

    /// Check se appuntamento è confermato (include override)
    pub fn is_confermato(&self) -> bool {
        matches!(
            self.stato,
            AppuntamentoStato::Confermato | AppuntamentoStato::ConfermatoConOverride
        )
    }

    // ─── Getter Methods (DDD Encapsulation) ───

    /// Get appuntamento ID
    pub fn id(&self) -> &AppuntamentoId {
        &self.id
    }

    /// Get stato corrente
    pub fn stato(&self) -> &AppuntamentoStato {
        &self.stato
    }

    /// Get cliente ID
    pub fn cliente_id(&self) -> &str {
        &self.cliente_id
    }

    /// Get operatore ID
    pub fn operatore_id(&self) -> &str {
        &self.operatore_id
    }

    /// Get servizio ID
    pub fn servizio_id(&self) -> &str {
        &self.servizio_id
    }

    /// Get data/ora
    pub fn data_ora(&self) -> NaiveDateTime {
        self.data_ora
    }

    /// Get durata in minuti
    pub fn durata_minuti(&self) -> i32 {
        self.durata_minuti
    }

    /// Get note
    pub fn note(&self) -> &Option<String> {
        &self.note
    }

    /// Get override info
    pub fn override_info(&self) -> Option<&OverrideInfo> {
        self.override_info.as_ref()
    }

    /// Get created_at
    pub fn created_at(&self) -> NaiveDateTime {
        self.created_at
    }

    /// Get updated_at
    pub fn updated_at(&self) -> NaiveDateTime {
        self.updated_at
    }
}

impl AppuntamentoAggregate {
    /// Alias per new_bozza (compatibilità test)
    pub fn new(
        cliente_id: String,
        operatore_id: String,
        servizio_id: String,
        data_ora: NaiveDateTime,
        durata_minuti: i32,
    ) -> Result<Self, DomainError> {
        Self::new_bozza(
            cliente_id,
            operatore_id,
            servizio_id,
            data_ora,
            durata_minuti,
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use chrono::NaiveDate;

    fn make_future_datetime() -> NaiveDateTime {
        NaiveDate::from_ymd_opt(2026, 12, 31)
            .unwrap()
            .and_hms_opt(10, 0, 0)
            .unwrap()
    }

    #[test]
    fn test_new_bozza_success() {
        let app = AppuntamentoAggregate::new_bozza(
            "cliente1".to_string(),
            "operatore1".to_string(),
            "servizio1".to_string(),
            make_future_datetime(),
            60,
        )
        .unwrap();

        assert_eq!(app.stato, AppuntamentoStato::Bozza);
        assert_eq!(app.cliente_id, "cliente1");
        assert_eq!(app.durata_minuti, 60);
    }

    #[test]
    fn test_new_bozza_missing_cliente_fails() {
        let result = AppuntamentoAggregate::new_bozza(
            "".to_string(),
            "operatore1".to_string(),
            "servizio1".to_string(),
            make_future_datetime(),
            60,
        );

        assert!(result.is_err());
        assert!(matches!(
            result.unwrap_err(),
            DomainError::CampoMancante { campo } if campo == "cliente_id"
        ));
    }

    #[test]
    fn test_new_bozza_invalid_durata_fails() {
        let result = AppuntamentoAggregate::new_bozza(
            "cliente1".to_string(),
            "operatore1".to_string(),
            "servizio1".to_string(),
            make_future_datetime(),
            0,
        );

        assert!(result.is_err());
        assert!(matches!(
            result.unwrap_err(),
            DomainError::DurataNonValida { .. }
        ));
    }

    #[test]
    fn test_bozza_to_proposta_success() {
        let mut app = AppuntamentoAggregate::new_bozza(
            "cliente1".to_string(),
            "operatore1".to_string(),
            "servizio1".to_string(),
            make_future_datetime(),
            60,
        )
        .unwrap();

        let validation = ValidationResult::new(); // No errors
        app.proponi(&validation).unwrap();

        assert_eq!(app.stato, AppuntamentoStato::Proposta);
    }

    #[test]
    fn test_bozza_to_proposta_with_hard_block_fails() {
        let mut app = AppuntamentoAggregate::new_bozza(
            "cliente1".to_string(),
            "operatore1".to_string(),
            "servizio1".to_string(),
            make_future_datetime(),
            60,
        )
        .unwrap();

        let mut validation = ValidationResult::new();
        validation.add_error(DomainError::AppuntamentoPassato {
            data: make_future_datetime(),
        });

        let result = app.proponi(&validation);
        assert!(result.is_err());
        assert_eq!(app.stato, AppuntamentoStato::Bozza); // Stato non cambia
    }

    #[test]
    fn test_proposta_to_in_attesa_operatore_success() {
        let mut app = AppuntamentoAggregate::new_bozza(
            "cliente1".to_string(),
            "operatore1".to_string(),
            "servizio1".to_string(),
            make_future_datetime(),
            60,
        )
        .unwrap();

        app.proponi(&ValidationResult::new()).unwrap();
        app.conferma_cliente().unwrap();

        assert_eq!(app.stato, AppuntamentoStato::InAttesaOperatore);
    }

    #[test]
    fn test_in_attesa_to_confermato_success() {
        let mut app = AppuntamentoAggregate::new_bozza(
            "cliente1".to_string(),
            "operatore1".to_string(),
            "servizio1".to_string(),
            make_future_datetime(),
            60,
        )
        .unwrap();

        app.proponi(&ValidationResult::new()).unwrap();
        app.conferma_cliente().unwrap();
        app.conferma_operatore().unwrap();

        assert_eq!(app.stato, AppuntamentoStato::Confermato);
    }

    #[test]
    fn test_in_attesa_to_rifiutato_success() {
        let mut app = AppuntamentoAggregate::new_bozza(
            "cliente1".to_string(),
            "operatore1".to_string(),
            "servizio1".to_string(),
            make_future_datetime(),
            60,
        )
        .unwrap();

        app.proponi(&ValidationResult::new()).unwrap();
        app.conferma_cliente().unwrap();
        app.rifiuta(Some("Imprevisto".to_string())).unwrap();

        assert_eq!(app.stato, AppuntamentoStato::Rifiutato);
        assert_eq!(app.note, Some("Imprevisto".to_string()));
    }

    #[test]
    fn test_conferma_con_override_success() {
        let mut app = AppuntamentoAggregate::new_bozza(
            "cliente1".to_string(),
            "operatore1".to_string(),
            "servizio1".to_string(),
            make_future_datetime(),
            60,
        )
        .unwrap();

        app.proponi(&ValidationResult::new()).unwrap();
        app.conferma_cliente().unwrap();
        app.conferma_con_override(
            "operatore1".to_string(),
            Some("Festivo ma urgente".to_string()),
            vec!["GiornoFestivo".to_string()],
        )
        .unwrap();

        assert_eq!(app.stato, AppuntamentoStato::ConfermatoConOverride);
        assert!(app.override_info.is_some());

        let override_info = app.override_info.unwrap();
        assert_eq!(override_info.operatore_id, "operatore1");
        assert_eq!(
            override_info.warnings_ignorati,
            vec!["GiornoFestivo".to_string()]
        );
    }

    #[test]
    fn test_modifica_bozza_success() {
        let mut app = AppuntamentoAggregate::new_bozza(
            "cliente1".to_string(),
            "operatore1".to_string(),
            "servizio1".to_string(),
            make_future_datetime(),
            60,
        )
        .unwrap();

        let new_datetime = NaiveDate::from_ymd_opt(2027, 1, 15)
            .unwrap()
            .and_hms_opt(14, 0, 0)
            .unwrap();

        app.modifica(
            Some(new_datetime),
            Some(90),
            Some("Note aggiornate".to_string()),
        )
        .unwrap();

        assert_eq!(app.data_ora, new_datetime);
        assert_eq!(app.durata_minuti, 90);
        assert_eq!(app.note, Some("Note aggiornate".to_string()));
        assert_eq!(app.stato, AppuntamentoStato::Bozza);
    }

    #[test]
    fn test_modifica_proposta_torna_bozza() {
        let mut app = AppuntamentoAggregate::new_bozza(
            "cliente1".to_string(),
            "operatore1".to_string(),
            "servizio1".to_string(),
            make_future_datetime(),
            60,
        )
        .unwrap();

        app.proponi(&ValidationResult::new()).unwrap();
        assert_eq!(app.stato, AppuntamentoStato::Proposta);

        app.modifica(None, Some(90), None).unwrap();

        assert_eq!(app.stato, AppuntamentoStato::Bozza); // Torna bozza
    }

    #[test]
    fn test_modifica_confermato_fails() {
        let mut app = AppuntamentoAggregate::new_bozza(
            "cliente1".to_string(),
            "operatore1".to_string(),
            "servizio1".to_string(),
            make_future_datetime(),
            60,
        )
        .unwrap();

        app.proponi(&ValidationResult::new()).unwrap();
        app.conferma_cliente().unwrap();
        app.conferma_operatore().unwrap();

        let result = app.modifica(None, Some(90), None);
        assert!(result.is_err());
    }

    #[test]
    fn test_cancella_confermato_success() {
        let mut app = AppuntamentoAggregate::new_bozza(
            "cliente1".to_string(),
            "operatore1".to_string(),
            "servizio1".to_string(),
            make_future_datetime(),
            60,
        )
        .unwrap();

        app.proponi(&ValidationResult::new()).unwrap();
        app.conferma_cliente().unwrap();
        app.conferma_operatore().unwrap();
        app.cancella().unwrap();

        assert_eq!(app.stato, AppuntamentoStato::Cancellato);
    }

    #[test]
    fn test_invalid_transition_bozza_to_confermato_fails() {
        let mut app = AppuntamentoAggregate::new_bozza(
            "cliente1".to_string(),
            "operatore1".to_string(),
            "servizio1".to_string(),
            make_future_datetime(),
            60,
        )
        .unwrap();

        let result = app.conferma_operatore();
        assert!(result.is_err());
        assert!(matches!(
            result.unwrap_err(),
            DomainError::TransizioneNonValida { .. }
        ));
    }

    #[test]
    fn test_ora_fine_calculation() {
        let app = AppuntamentoAggregate::new_bozza(
            "cliente1".to_string(),
            "operatore1".to_string(),
            "servizio1".to_string(),
            make_future_datetime(),
            90,
        )
        .unwrap();

        let expected_fine = make_future_datetime() + chrono::Duration::minutes(90);
        assert_eq!(app.ora_fine(), expected_fine);
    }
}
