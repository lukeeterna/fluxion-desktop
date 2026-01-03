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
    pub repository: Box<dyn AppuntamentoRepository>,
}

impl AppuntamentoService {
    pub fn new(repository: Box<dyn AppuntamentoRepository>) -> Self {
        Self {
            validation_service: ValidationService::new(),
            festivita_service: FestivitaService::new(),
            repository,
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

        self.repository.save(&aggregate).await?;

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

        self.repository.save(&aggregate).await?;

        Ok((aggregate, validation))
    }

    /// Cliente conferma proposta
    pub async fn conferma_cliente(
        &self,
        mut aggregate: AppuntamentoAggregate,
    ) -> Result<AppuntamentoAggregate, ServiceError> {
        aggregate.conferma_cliente()?;

        self.repository.save(&aggregate).await?;
        // TODO: send notification to operator
        // self.notifier.send_conferma_cliente(&aggregate).await?;

        Ok(aggregate)
    }

    /// Operatore accetta appuntamento
    pub async fn conferma_operatore(
        &self,
        mut aggregate: AppuntamentoAggregate,
    ) -> Result<AppuntamentoAggregate, ServiceError> {
        aggregate.conferma_operatore()?;

        self.repository.save(&aggregate).await?;
        // TODO: send notification to cliente
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

        self.repository.save(&aggregate).await?;
        // TODO: audit log override
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

        self.repository.save(&aggregate).await?;
        // TODO: send notification to cliente
        // self.notifier.send_rifiuto(&aggregate).await?;

        Ok(aggregate)
    }

    /// Cancella appuntamento
    pub async fn cancella(
        &self,
        mut aggregate: AppuntamentoAggregate,
    ) -> Result<AppuntamentoAggregate, ServiceError> {
        aggregate.cancella()?;

        self.repository.save(&aggregate).await?;
        // TODO: send notification
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

        self.repository.save(&aggregate).await?;

        Ok(aggregate)
    }

    /// Completa appuntamento (sistema automatico)
    pub async fn completa(
        &self,
        mut aggregate: AppuntamentoAggregate,
    ) -> Result<AppuntamentoAggregate, ServiceError> {
        aggregate.completa()?;

        self.repository.save(&aggregate).await?;
        // TODO: trigger post-service workflow
        // self.post_service_handler.trigger(&aggregate).await?;

        Ok(aggregate)
    }
}

// Note: No Default impl - service requires repository injection

#[cfg(test)]
mod tests {
    use super::*;
    use chrono::NaiveDate;
    use sqlx::SqlitePool;
    use crate::infra::SqliteAppuntamentoRepository;

    fn make_future_datetime() -> NaiveDateTime {
        NaiveDate::from_ymd_opt(2026, 12, 31)
            .unwrap()
            .and_hms_opt(14, 0, 0)
            .unwrap()
    }

    async fn create_test_service() -> AppuntamentoService {
        let pool = SqlitePool::connect(":memory:").await.unwrap();

        // Create table
        sqlx::query(
            r#"
            CREATE TABLE appuntamenti (
                id TEXT PRIMARY KEY,
                cliente_id TEXT NOT NULL,
                servizio_id TEXT NOT NULL,
                operatore_id TEXT NOT NULL,
                data_ora_inizio TEXT NOT NULL,
                data_ora_fine TEXT NOT NULL,
                durata_minuti INTEGER NOT NULL,
                stato TEXT NOT NULL,
                override_info TEXT,
                note TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                deleted_at TEXT,
                prezzo REAL DEFAULT 0,
                prezzo_finale REAL DEFAULT 0,
                sconto_percentuale REAL DEFAULT 0
            )
            "#,
        )
        .execute(&pool)
        .await
        .unwrap();

        let repo = Box::new(SqliteAppuntamentoRepository::new(pool));
        AppuntamentoService::new(repo)
    }

    #[tokio::test]
    async fn test_crea_bozza_success() {
        let service = create_test_service().await;

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
        let service = create_test_service().await;

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
        let service = create_test_service().await;

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
