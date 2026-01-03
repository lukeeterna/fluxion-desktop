use async_trait::async_trait;
use chrono::{NaiveDateTime, Utc};
use serde::{Deserialize, Serialize};
use sqlx::SqlitePool;

use crate::domain::{
    AppuntamentoAggregate, AppuntamentoId, AppuntamentoRepository, AppuntamentoStato,
    OverrideInfo, RepositoryError,
};

/// DB representation of Appuntamento (SQLite row)
#[derive(Debug, sqlx::FromRow)]
struct AppuntamentoDB {
    id: String,
    cliente_id: String,
    servizio_id: String,
    operatore_id: String,
    data_ora_inizio: String, // ISO 8601
    durata_minuti: i32,
    stato: String,
    override_info: Option<String>, // JSON nullable
    note: Option<String>,
    created_at: String,
    updated_at: String,
}

/// Implementazione SQLite del repository
pub struct SqliteAppuntamentoRepository {
    pool: SqlitePool,
}

impl SqliteAppuntamentoRepository {
    pub fn new(pool: SqlitePool) -> Self {
        Self { pool }
    }

    /// Mapping DB → Domain
    fn to_domain(db: AppuntamentoDB) -> Result<AppuntamentoAggregate, RepositoryError> {
        let id = AppuntamentoId::from_string(&db.id)
            .map_err(|e| RepositoryError::Database(e.to_string()))?;

        let stato = AppuntamentoStato::from_str(&db.stato)
            .map_err(|e| RepositoryError::Database(e.to_string()))?;

        let data_ora = NaiveDateTime::parse_from_str(&db.data_ora_inizio, "%Y-%m-%dT%H:%M:%S")
            .or_else(|_| NaiveDateTime::parse_from_str(&db.data_ora_inizio, "%Y-%m-%d %H:%M:%S"))
            .map_err(|e| RepositoryError::Database(format!("Invalid datetime: {}", e)))?;

        let created_at = NaiveDateTime::parse_from_str(&db.created_at, "%Y-%m-%d %H:%M:%S")
            .map_err(|e| RepositoryError::Database(format!("Invalid created_at: {}", e)))?;

        let updated_at = NaiveDateTime::parse_from_str(&db.updated_at, "%Y-%m-%d %H:%M:%S")
            .map_err(|e| RepositoryError::Database(format!("Invalid updated_at: {}", e)))?;

        let override_info: Option<OverrideInfo> = match db.override_info {
            Some(json) => Some(serde_json::from_str(&json)?),
            None => None,
        };

        Ok(AppuntamentoAggregate {
            id,
            stato,
            cliente_id: db.cliente_id,
            operatore_id: db.operatore_id,
            servizio_id: db.servizio_id,
            data_ora,
            durata_minuti: db.durata_minuti,
            note: db.note,
            created_at,
            updated_at,
            override_info,
        })
    }

    /// Mapping Domain → DB values
    fn to_db_values(
        aggregate: &AppuntamentoAggregate,
    ) -> (
        String,
        String,
        String,
        String,
        String,
        i32,
        String,
        Option<String>,
        Option<String>,
        String,
        String,
    ) {
        let id = aggregate.id.to_string();
        let stato = aggregate.stato.as_str().to_string();
        let data_ora_inizio = aggregate.data_ora.format("%Y-%m-%dT%H:%M:%S").to_string();
        let created_at = aggregate.created_at.format("%Y-%m-%d %H:%M:%S").to_string();
        let updated_at = aggregate.updated_at.format("%Y-%m-%d %H:%M:%S").to_string();

        let override_info = aggregate
            .override_info
            .as_ref()
            .map(|info| serde_json::to_string(info).unwrap_or_default());

        (
            id,
            aggregate.cliente_id.clone(),
            aggregate.servizio_id.clone(),
            aggregate.operatore_id.clone(),
            data_ora_inizio,
            aggregate.durata_minuti,
            stato,
            override_info,
            aggregate.note.clone(),
            created_at,
            updated_at,
        )
    }
}

#[async_trait]
impl AppuntamentoRepository for SqliteAppuntamentoRepository {
    async fn find_by_id(
        &self,
        id: AppuntamentoId,
    ) -> Result<Option<AppuntamentoAggregate>, RepositoryError> {
        let id_str = id.to_string();

        let row: Option<AppuntamentoDB> = sqlx::query_as(
            r#"
            SELECT
                id, cliente_id, servizio_id, operatore_id,
                data_ora_inizio, durata_minuti, stato, override_info,
                note, created_at, updated_at
            FROM appuntamenti
            WHERE id = ? AND deleted_at IS NULL
            "#,
        )
        .bind(&id_str)
        .fetch_optional(&self.pool)
        .await?;

        match row {
            Some(db) => Ok(Some(Self::to_domain(db)?)),
            None => Ok(None),
        }
    }

    async fn save(&self, aggregate: &AppuntamentoAggregate) -> Result<(), RepositoryError> {
        let (
            id,
            cliente_id,
            servizio_id,
            operatore_id,
            data_ora_inizio,
            durata_minuti,
            stato,
            override_info,
            note,
            created_at,
            updated_at,
        ) = Self::to_db_values(aggregate);

        // Calcola data_ora_fine
        let data_ora_fine = aggregate.ora_fine().format("%Y-%m-%dT%H:%M:%S").to_string();

        // Upsert (INSERT or UPDATE)
        sqlx::query(
            r#"
            INSERT INTO appuntamenti (
                id, cliente_id, servizio_id, operatore_id,
                data_ora_inizio, data_ora_fine, durata_minuti,
                stato, override_info, note,
                created_at, updated_at,
                prezzo, prezzo_finale, sconto_percentuale
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0)
            ON CONFLICT(id) DO UPDATE SET
                cliente_id = excluded.cliente_id,
                servizio_id = excluded.servizio_id,
                operatore_id = excluded.operatore_id,
                data_ora_inizio = excluded.data_ora_inizio,
                data_ora_fine = excluded.data_ora_fine,
                durata_minuti = excluded.durata_minuti,
                stato = excluded.stato,
                override_info = excluded.override_info,
                note = excluded.note,
                updated_at = excluded.updated_at
            "#,
        )
        .bind(&id)
        .bind(&cliente_id)
        .bind(&servizio_id)
        .bind(&operatore_id)
        .bind(&data_ora_inizio)
        .bind(&data_ora_fine)
        .bind(durata_minuti)
        .bind(&stato)
        .bind(&override_info)
        .bind(&note)
        .bind(&created_at)
        .bind(&updated_at)
        .execute(&self.pool)
        .await?;

        Ok(())
    }

    async fn list(&self) -> Result<Vec<AppuntamentoAggregate>, RepositoryError> {
        let rows: Vec<AppuntamentoDB> = sqlx::query_as(
            r#"
            SELECT
                id, cliente_id, servizio_id, operatore_id,
                data_ora_inizio, durata_minuti, stato, override_info,
                note, created_at, updated_at
            FROM appuntamenti
            WHERE deleted_at IS NULL
            ORDER BY data_ora_inizio ASC
            "#,
        )
        .fetch_all(&self.pool)
        .await?;

        rows.into_iter()
            .map(Self::to_domain)
            .collect::<Result<Vec<_>, _>>()
    }

    async fn list_by_cliente(
        &self,
        cliente_id: &str,
    ) -> Result<Vec<AppuntamentoAggregate>, RepositoryError> {
        let rows: Vec<AppuntamentoDB> = sqlx::query_as(
            r#"
            SELECT
                id, cliente_id, servizio_id, operatore_id,
                data_ora_inizio, durata_minuti, stato, override_info,
                note, created_at, updated_at
            FROM appuntamenti
            WHERE cliente_id = ? AND deleted_at IS NULL
            ORDER BY data_ora_inizio DESC
            "#,
        )
        .bind(cliente_id)
        .fetch_all(&self.pool)
        .await?;

        rows.into_iter()
            .map(Self::to_domain)
            .collect::<Result<Vec<_>, _>>()
    }

    async fn list_by_operatore(
        &self,
        operatore_id: &str,
    ) -> Result<Vec<AppuntamentoAggregate>, RepositoryError> {
        let rows: Vec<AppuntamentoDB> = sqlx::query_as(
            r#"
            SELECT
                id, cliente_id, servizio_id, operatore_id,
                data_ora_inizio, durata_minuti, stato, override_info,
                note, created_at, updated_at
            FROM appuntamenti
            WHERE operatore_id = ? AND deleted_at IS NULL
            ORDER BY data_ora_inizio ASC
            "#,
        )
        .bind(operatore_id)
        .fetch_all(&self.pool)
        .await?;

        rows.into_iter()
            .map(Self::to_domain)
            .collect::<Result<Vec<_>, _>>()
    }

    async fn list_by_date_range(
        &self,
        start: NaiveDateTime,
        end: NaiveDateTime,
    ) -> Result<Vec<AppuntamentoAggregate>, RepositoryError> {
        let start_str = start.format("%Y-%m-%dT%H:%M:%S").to_string();
        let end_str = end.format("%Y-%m-%dT%H:%M:%S").to_string();

        let rows: Vec<AppuntamentoDB> = sqlx::query_as(
            r#"
            SELECT
                id, cliente_id, servizio_id, operatore_id,
                data_ora_inizio, durata_minuti, stato, override_info,
                note, created_at, updated_at
            FROM appuntamenti
            WHERE data_ora_inizio >= ? AND data_ora_inizio <= ?
              AND deleted_at IS NULL
            ORDER BY data_ora_inizio ASC
            "#,
        )
        .bind(&start_str)
        .bind(&end_str)
        .fetch_all(&self.pool)
        .await?;

        rows.into_iter()
            .map(Self::to_domain)
            .collect::<Result<Vec<_>, _>>()
    }

    async fn list_by_operatore_and_date(
        &self,
        operatore_id: &str,
        date: NaiveDateTime,
    ) -> Result<Vec<AppuntamentoAggregate>, RepositoryError> {
        let date_str = date.format("%Y-%m-%d").to_string();

        let rows: Vec<AppuntamentoDB> = sqlx::query_as(
            r#"
            SELECT
                id, cliente_id, servizio_id, operatore_id,
                data_ora_inizio, durata_minuti, stato, override_info,
                note, created_at, updated_at
            FROM appuntamenti
            WHERE operatore_id = ?
              AND DATE(data_ora_inizio) = ?
              AND deleted_at IS NULL
            ORDER BY data_ora_inizio ASC
            "#,
        )
        .bind(operatore_id)
        .bind(&date_str)
        .fetch_all(&self.pool)
        .await?;

        rows.into_iter()
            .map(Self::to_domain)
            .collect::<Result<Vec<_>, _>>()
    }

    async fn delete(&self, id: AppuntamentoId) -> Result<(), RepositoryError> {
        let id_str = id.to_string();
        let now = Utc::now().naive_utc().format("%Y-%m-%d %H:%M:%S").to_string();

        sqlx::query(
            r#"
            UPDATE appuntamenti
            SET deleted_at = ?
            WHERE id = ?
            "#,
        )
        .bind(&now)
        .bind(&id_str)
        .execute(&self.pool)
        .await?;

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use chrono::NaiveDate;

    #[tokio::test]
    async fn test_save_and_find() {
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

        let repo = SqliteAppuntamentoRepository::new(pool);

        let aggregate = AppuntamentoAggregate::new_bozza(
            "cliente1".to_string(),
            "operatore1".to_string(),
            "servizio1".to_string(),
            NaiveDate::from_ymd_opt(2026, 12, 31)
                .unwrap()
                .and_hms_opt(14, 0, 0)
                .unwrap(),
            60,
        )
        .unwrap();

        let id = aggregate.id;

        // Save
        repo.save(&aggregate).await.unwrap();

        // Find
        let found = repo.find_by_id(id).await.unwrap();
        assert!(found.is_some());

        let found = found.unwrap();
        assert_eq!(found.cliente_id, "cliente1");
        assert_eq!(found.stato, AppuntamentoStato::Bozza);
    }

    #[tokio::test]
    async fn test_list_by_operatore() {
        let pool = SqlitePool::connect(":memory:").await.unwrap();

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

        let repo = SqliteAppuntamentoRepository::new(pool);

        // Save 2 appuntamenti per operatore1
        for i in 0..2 {
            let aggregate = AppuntamentoAggregate::new_bozza(
                format!("cliente{}", i),
                "operatore1".to_string(),
                "servizio1".to_string(),
                NaiveDate::from_ymd_opt(2026, 12, 31)
                    .unwrap()
                    .and_hms_opt(10 + i, 0, 0)
                    .unwrap(),
                60,
            )
            .unwrap();

            repo.save(&aggregate).await.unwrap();
        }

        // List
        let list = repo.list_by_operatore("operatore1").await.unwrap();
        assert_eq!(list.len(), 2);
    }
}
