use crate::domain::{AppuntamentoAggregate, AppuntamentoId, DomainError, ValidationResult};
use crate::services::festivita_service::FestivitaService;
use crate::services::validation_service::ValidationService;
use chrono::NaiveDateTime;
use thiserror::Error;

/// Service errors (wrappano domain + infra errors)
#[derive(Debug, Error)]
pub enum ServiceError {
    #[error("Domain error: {0}")]
    Domain(#[from] DomainError),

    #[error("Database error: {0}")]
    Database(String),

    #[error("Not found: {0}")]
    NotFound(String),

    #[error("Validation failed: {0}")]
    ValidationFailed(String),
}

/// Appuntamento Service - Orchestration layer
pub struct AppuntamentoService {
    pub validation_service: ValidationService,
    pub festivita_service: FestivitaService,
    // Repository inject qui (async trait)
    // pub repository: Box<dyn AppuntamentoRepository>,
}

impl AppuntamentoService {
    pub fn new() -> Self {
        Self {
            validation_service: ValidationService::new(),
            festivita_service: FestivitaService::new(),
        }
    }

    /// Crea nuova bozza appuntamento
    pub async fn crea_bozza(
        &self,
        cliente_id: String,
        operatore_id: String,
        servizio_id: String,
        data_ora: NaiveDateTime,
        durata_minuti: i32,
    ) -> Result<AppuntamentoAggregate, ServiceError> {
        let aggregate = AppuntamentoAggregate::new_bozza(
            cliente_id,
            operatore_id,
            servizio_id,
            data_ora,
            durata_minuti,
        )?;

        // TODO: Save to repository
        // self.repository.save(&aggregate).await?;

        Ok(aggregate)
    }

    /// Valida e proponi appuntamento
    pub async fn proponi_appuntamento(
        &self,
        mut aggregate: AppuntamentoAggregate,
        appuntamenti_esistenti: &[AppuntamentoAggregate],
        giorni_festivi: &[(NaiveDateTime, String)],
    ) -> Result<(AppuntamentoAggregate, ValidationResult), ServiceError> {
        let validation = self
            .validation_service
            .valida_appuntamento(&aggregate, appuntamenti_esistenti, giorni_festivi)
            .await;

        aggregate.proponi(&validation)?;

        // TODO: Save to repository
        // self.repository.save(&aggregate).await?;

        Ok((aggregate, validation))
    }

    /// Cliente conferma proposta
    pub async fn conferma_cliente(
        &self,
        mut aggregate: AppuntamentoAggregate,
    ) -> Result<AppuntamentoAggregate, ServiceError> {
        aggregate.conferma_cliente()?;

        // TODO: Save + send notification to operator
        // self.repository.save(&aggregate).await?;
        // self.notifier.send_conferma_cliente(&aggregate).await?;

        Ok(aggregate)
    }

    /// Operatore accetta appuntamento
    pub async fn conferma_operatore(
        &self,
        mut aggregate: AppuntamentoAggregate,
    ) -> Result<AppuntamentoAggregate, ServiceError> {
        aggregate.conferma_operatore()?;

        // TODO: Save + send notification to cliente
        // self.repository.save(&aggregate).await?;
        // self.notifier.send_conferma_operatore(&aggregate).await?;

        Ok(aggregate)
    }

    /// Operatore forza conferma con override
    pub async fn conferma_con_override(
        &self,
        mut aggregate: AppuntamentoAggregate,
        operatore_id: String,
        motivazione: Option<String>,
        warnings_ignorati: Vec<String>,
    ) -> Result<AppuntamentoAggregate, ServiceError> {
        aggregate.conferma_con_override(operatore_id, motivazione, warnings_ignorati)?;

        // TODO: Save + audit log override
        // self.repository.save(&aggregate).await?;
        // self.audit_logger.log_override(&aggregate).await?;

        Ok(aggregate)
    }

    /// Operatore rifiuta appuntamento
    pub async fn rifiuta(
        &self,
        mut aggregate: AppuntamentoAggregate,
        motivazione: Option<String>,
    ) -> Result<AppuntamentoAggregate, ServiceError> {
        aggregate.rifiuta(motivazione)?;

        // TODO: Save + send notification to cliente
        // self.repository.save(&aggregate).await?;
        // self.notifier.send_rifiuto(&aggregate).await?;

        Ok(aggregate)
    }

    /// Cancella appuntamento
    pub async fn cancella(
        &self,
        mut aggregate: AppuntamentoAggregate,
    ) -> Result<AppuntamentoAggregate, ServiceError> {
        aggregate.cancella()?;

        // TODO: Save + send notification
        // self.repository.save(&aggregate).await?;
        // self.notifier.send_cancellazione(&aggregate).await?;

        Ok(aggregate)
    }

    /// Modifica appuntamento (solo Bozza/Proposta)
    pub async fn modifica(
        &self,
        mut aggregate: AppuntamentoAggregate,
        data_ora: Option<NaiveDateTime>,
        durata_minuti: Option<i32>,
        note: Option<String>,
    ) -> Result<AppuntamentoAggregate, ServiceError> {
        aggregate.modifica(data_ora, durata_minuti, note)?;

        // TODO: Save
        // self.repository.save(&aggregate).await?;

        Ok(aggregate)
    }

    /// Completa appuntamento (sistema automatico)
    pub async fn completa(
        &self,
        mut aggregate: AppuntamentoAggregate,
    ) -> Result<AppuntamentoAggregate, ServiceError> {
        aggregate.completa()?;

        // TODO: Save + trigger post-service workflow
        // self.repository.save(&aggregate).await?;
        // self.post_service_handler.trigger(&aggregate).await?;

        Ok(aggregate)
    }
}

impl Default for AppuntamentoService {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use chrono::NaiveDate;

    fn make_future_datetime() -> NaiveDateTime {
        NaiveDate::from_ymd_opt(2026, 12, 31)
            .unwrap()
            .and_hms_opt(14, 0, 0)
            .unwrap()
    }

    #[tokio::test]
    async fn test_crea_bozza_success() {
        let service = AppuntamentoService::new();

        let result = service
            .crea_bozza(
                "cliente1".to_string(),
                "operatore1".to_string(),
                "servizio1".to_string(),
                make_future_datetime(),
                60,
            )
            .await;

        assert!(result.is_ok());
        let aggregate = result.unwrap();
        assert_eq!(aggregate.cliente_id, "cliente1");
    }

    #[tokio::test]
    async fn test_proponi_appuntamento_success() {
        let service = AppuntamentoService::new();

        let aggregate = service
            .crea_bozza(
                "cliente1".to_string(),
                "operatore1".to_string(),
                "servizio1".to_string(),
                make_future_datetime(),
                60,
            )
            .await
            .unwrap();

        let result = service
            .proponi_appuntamento(aggregate, &[], &[])
            .await;

        assert!(result.is_ok());
        let (aggregate, validation) = result.unwrap();
        assert_eq!(aggregate.stato, crate::domain::AppuntamentoStato::Proposta);
        assert!(!validation.is_blocked());
    }

    #[tokio::test]
    async fn test_workflow_completo() {
        let service = AppuntamentoService::new();

        // 1. Crea bozza
        let aggregate = service
            .crea_bozza(
                "cliente1".to_string(),
                "operatore1".to_string(),
                "servizio1".to_string(),
                make_future_datetime(),
                60,
            )
            .await
            .unwrap();

        // 2. Proponi
        let (aggregate, _validation) = service
            .proponi_appuntamento(aggregate, &[], &[])
            .await
            .unwrap();

        // 3. Cliente conferma
        let aggregate = service.conferma_cliente(aggregate).await.unwrap();
        assert_eq!(
            aggregate.stato,
            crate::domain::AppuntamentoStato::InAttesaOperatore
        );

        // 4. Operatore conferma
        let aggregate = service.conferma_operatore(aggregate).await.unwrap();
        assert_eq!(
            aggregate.stato,
            crate::domain::AppuntamentoStato::Confermato
        );
    }
}
