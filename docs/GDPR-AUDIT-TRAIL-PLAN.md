# GDPR Audit Trail - Implementation Plan

> **Progetto**: FLUXION - Gestionale Desktop PMI  
> **Stack**: Tauri 2.x (Rust) + React + SQLite + Python Voice Agent  
> **Stato**: Week 4 Release - 940 test passing  
> **Data Piano**: 2026-02-03

---

## Executive Summary

Questo piano dettaglia l'implementazione di un **GDPR-compliant audit trail system** per tracciare tutte le operazioni su dati personali (clienti, appuntamenti, consensi) con retention policy automatica.

---

## Phase 1: Database Schema

### 1.1 Migration SQL - `audit_logs` Table

**File**: `src-tauri/migrations/018_gdpr_audit_logs.sql`

```sql
-- ═══════════════════════════════════════════════════════════════
-- GDPR AUDIT LOGS - Migration 018
-- Tracciamento operazioni su dati personali (GDPR Art. 30)
-- ═══════════════════════════════════════════════════════════════

-- Tabella audit logs principale
CREATE TABLE IF NOT EXISTS audit_logs (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    
    -- Timestamp e sessione
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    session_id TEXT,                    -- ID sessione voice/web
    
    -- Utente/Operatore
    user_id TEXT,                       -- ID operatore (NULL per voice/automated)
    user_type TEXT NOT NULL DEFAULT 'system',  -- 'operatore', 'voice_agent', 'system', 'api'
    
    -- Azione
    action TEXT NOT NULL,               -- 'CREATE', 'UPDATE', 'DELETE', 'VIEW', 'EXPORT'
    action_subtype TEXT,                -- 'soft_delete', 'hard_delete', 'consent_grant', 'consent_revoke'
    
    -- Entità coinvolta
    entity_type TEXT NOT NULL,          -- 'cliente', 'appuntamento', 'consenso', 'fattura'
    entity_id TEXT NOT NULL,            -- ID record coinvolto
    
    -- Dati (JSON)
    data_before TEXT,                   -- JSON: stato precedente (NULL per CREATE)
    data_after TEXT,                    -- JSON: stato successivo (NULL per DELETE)
    data_diff TEXT,                     -- JSON: solo campi modificati (computed)
    
    -- GDPR Classification
    gdpr_category TEXT NOT NULL,        -- 'personal_data', 'consent', 'booking', 'billing', 'sensitive'
    gdpr_legal_basis TEXT,              -- 'consent', 'contract', 'legal_obligation', 'legitimate_interest'
    
    -- Sorgente
    source TEXT NOT NULL DEFAULT 'web', -- 'web', 'voice', 'api', 'import', 'system'
    source_ip TEXT,                     -- IP address (se disponibile)
    
    -- Context
    vertical TEXT,                      -- 'parrucchiere', 'estetista', etc.
    note TEXT,                          -- Note aggiuntive
    
    -- Retention
    retention_until TEXT,               -- Data cancellazione automatica
    
    -- Timestamps
    created_at TEXT DEFAULT (datetime('now'))
);

-- Indici per query performanti
CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_action ON audit_logs(action, entity_type);
CREATE INDEX idx_audit_user ON audit_logs(user_id, user_type);
CREATE INDEX idx_audit_gdpr_cat ON audit_logs(gdpr_category);
CREATE INDEX idx_audit_source ON audit_logs(source);
CREATE INDEX idx_audit_retention ON audit_logs(retention_until) WHERE retention_until IS NOT NULL;

-- Indice composito per report GDPR (es: "tutte le operazioni su un cliente")
CREATE INDEX idx_audit_entity_full ON audit_logs(entity_type, entity_id, timestamp DESC);

-- Tabella per configurazione retention policy
CREATE TABLE IF NOT EXISTS gdpr_settings (
    chiave TEXT PRIMARY KEY,
    valore TEXT NOT NULL,
    tipo TEXT DEFAULT 'string',         -- 'string', 'number', 'json'
    descrizione TEXT,
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Default retention periods (in giorni)
INSERT OR IGNORE INTO gdpr_settings (chiave, valore, tipo, descrizione) VALUES
    ('retention_personal_data', '2555', 'number', 'Retention dati personali (7 anni)'),
    ('retention_consent_logs', '1825', 'number', 'Retention log consensi (5 anni)'),
    ('retention_booking_logs', '1095', 'number', 'Retention log appuntamenti (3 anni)'),
    ('retention_voice_sessions', '365', 'number', 'Retention sessioni voice (1 anno)'),
    ('retention_audit_logs', '2555', 'number', 'Retention audit logs (7 anni)'),
    ('gdpr_enabled', 'true', 'boolean', 'Audit trail attivo'),
    ('last_cleanup_run', '', 'string', 'Ultima esecuzione cleanup');

-- View per report GDPR mensile
CREATE VIEW IF NOT EXISTS v_audit_summary_monthly AS
SELECT 
    strftime('%Y-%m', timestamp) as mese,
    entity_type,
    action,
    gdpr_category,
    source,
    COUNT(*) as totale_operazioni
FROM audit_logs
GROUP BY strftime('%Y-%m', timestamp), entity_type, action, gdpr_category, source
ORDER BY mese DESC, totale_operazioni DESC;

-- View per dati da cancellare (retention scaduta)
CREATE VIEW IF NOT EXISTS v_audit_expired AS
SELECT * FROM audit_logs
WHERE retention_until IS NOT NULL 
  AND datetime(retention_until) <= datetime('now');
```

### 1.2 Entity Audit View (per join rapide)

```sql
-- View: storico completo per cliente
CREATE VIEW IF NOT EXISTS v_cliente_audit_history AS
SELECT 
    al.*,
    c.nome as cliente_nome,
    c.cognome as cliente_cognome
FROM audit_logs al
LEFT JOIN clienti c ON al.entity_id = c.id AND al.entity_type = 'cliente'
WHERE al.entity_type = 'cliente' OR al.entity_type = 'consenso';
```

---

## Phase 2: Backend Rust

### 2.1 Domain Model - `src-tauri/src/domain/audit.rs`

**File**: `src-tauri/src/domain/audit.rs` (NEW)

```rust
//! GDPR Audit Trail Domain Model
//! 
//! Rappresenta il dominio audit per tracciamento operazioni GDPR.

use serde::{Deserialize, Serialize};
use chrono::NaiveDateTime;

/// Tipi di azione auditabili
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "UPPERCASE")]
pub enum AuditAction {
    Create,
    Update,
    Delete,
    View,
    Export,
}

/// Sottotipi di azione per casi specifici
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "snake_case")]
pub enum AuditActionSubtype {
    SoftDelete,
    HardDelete,
    ConsentGrant,
    ConsentRevoke,
    BulkUpdate,
}

/// Tipi di entità auditabili
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "snake_case")]
pub enum AuditEntityType {
    Cliente,
    Appuntamento,
    Consenso,
    Fattura,
    Servizio,
    Operatore,
}

/// Categorie GDPR per classificazione dati
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "snake_case")]
pub enum GdprCategory {
    PersonalData,       // Dati personali base (nome, telefono)
    Sensitive,          // Dati sensibili (salute, preferenze)
    Consent,            // Consensi
    Booking,            // Prenotazioni
    Billing,            // Fatturazione
}

/// Base legale GDPR
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "snake_case")]
pub enum GdprLegalBasis {
    Consent,
    Contract,
    LegalObligation,
    LegitimateInterest,
}

/// Sorgente dell'operazione
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "snake_case")]
pub enum AuditSource {
    Web,
    Voice,
    Api,
    Import,
    System,
}

/// Tipo di utente che ha eseguito l'azione
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "snake_case")]
pub enum UserType {
    Operatore,
    VoiceAgent,
    System,
    Api,
}

/// Record audit log
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuditLog {
    pub id: String,
    pub timestamp: NaiveDateTime,
    pub session_id: Option<String>,
    pub user_id: Option<String>,
    pub user_type: UserType,
    pub action: AuditAction,
    pub action_subtype: Option<AuditActionSubtype>,
    pub entity_type: AuditEntityType,
    pub entity_id: String,
    pub data_before: Option<serde_json::Value>,
    pub data_after: Option<serde_json::Value>,
    pub data_diff: Option<serde_json::Value>,
    pub gdpr_category: GdprCategory,
    pub gdpr_legal_basis: Option<GdprLegalBasis>,
    pub source: AuditSource,
    pub source_ip: Option<String>,
    pub vertical: Option<String>,
    pub note: Option<String>,
    pub retention_until: Option<NaiveDateTime>,
    pub created_at: NaiveDateTime,
}

/// Input per creazione audit log
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CreateAuditLogInput {
    pub session_id: Option<String>,
    pub user_id: Option<String>,
    pub user_type: UserType,
    pub action: AuditAction,
    pub action_subtype: Option<AuditActionSubtype>,
    pub entity_type: AuditEntityType,
    pub entity_id: String,
    pub data_before: Option<serde_json::Value>,
    pub data_after: Option<serde_json::Value>,
    pub gdpr_category: GdprCategory,
    pub gdpr_legal_basis: Option<GdprLegalBasis>,
    pub source: AuditSource,
    pub source_ip: Option<String>,
    pub vertical: Option<String>,
    pub note: Option<String>,
}

/// Filtri per query audit logs
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct AuditLogFilters {
    pub entity_type: Option<AuditEntityType>,
    pub entity_id: Option<String>,
    pub action: Option<AuditAction>,
    pub user_id: Option<String>,
    pub date_from: Option<NaiveDateTime>,
    pub date_to: Option<NaiveDateTime>,
    pub gdpr_category: Option<GdprCategory>,
    pub source: Option<AuditSource>,
    pub limit: Option<i64>,
}

/// Settings GDPR
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GdprSettings {
    pub retention_personal_data: i32,    // giorni
    pub retention_consent_logs: i32,
    pub retention_booking_logs: i32,
    pub retention_voice_sessions: i32,
    pub retention_audit_logs: i32,
    pub gdpr_enabled: bool,
}
```

### 2.2 Repository Trait - `src-tauri/src/domain/repository.rs` (Update)

Aggiungere al file esistente:

```rust
// Aggiungere al file esistente src-tauri/src/domain/repository.rs

use super::audit::{AuditLog, CreateAuditLogInput, AuditLogFilters, GdprSettings};

#[async_trait::async_trait]
pub trait AuditRepository: Send + Sync {
    /// Crea un nuovo audit log
    async fn create_audit_log(&self, input: CreateAuditLogInput) -> Result<AuditLog, DomainError>;
    
    /// Recupera audit log by ID
    async fn get_audit_log(&self, id: &str) -> Result<Option<AuditLog>, DomainError>;
    
    /// Query audit logs con filtri
    async fn query_audit_logs(&self, filters: AuditLogFilters) -> Result<Vec<AuditLog>, DomainError>;
    
    /// Recupera storico per entità specifica
    async fn get_entity_history(&self, entity_type: &str, entity_id: &str) -> Result<Vec<AuditLog>, DomainError>;
    
    /// Recupera settings GDPR
    async fn get_gdpr_settings(&self) -> Result<GdprSettings, DomainError>;
    
    /// Aggiorna settings GDPR
    async fn update_gdpr_settings(&self, settings: GdprSettings) -> Result<(), DomainError>;
    
    /// Cleanup logs scaduti (ritorna numero di record eliminati)
    async fn cleanup_expired_logs(&self) -> Result<i64, DomainError>;
    
    /// Calcola retention date per categoria
    fn calculate_retention_date(&self, category: &GdprCategory) -> NaiveDateTime;
}
```

### 2.3 Repository Implementation - `src-tauri/src/infra/repositories/audit_repo.rs`

**File**: `src-tauri/src/infra/repositories/audit_repo.rs` (NEW)

```rust
//! SQLite implementation of AuditRepository

use sqlx::SqlitePool;
use chrono::{NaiveDateTime, Duration};

use crate::domain::audit::*;
use crate::domain::repository::AuditRepository;
use crate::domain::errors::DomainError;

pub struct SqliteAuditRepository {
    pool: SqlitePool,
}

impl SqliteAuditRepository {
    pub fn new(pool: SqlitePool) -> Self {
        Self { pool }
    }
    
    /// Calcola la data di retention in base alla categoria
    fn calculate_retention(&self, category: &GdprCategory, settings: &GdprSettings) -> NaiveDateTime {
        let days = match category {
            GdprCategory::PersonalData => settings.retention_personal_data,
            GdprCategory::Consent => settings.retention_consent_logs,
            GdprCategory::Booking => settings.retention_booking_logs,
            GdprCategory::Billing => settings.retention_audit_logs,
            GdprCategory::Sensitive => settings.retention_personal_data,
        };
        
        NaiveDateTime::from_timestamp_opt(
            chrono::Local::now().timestamp() + (days as i64 * 86400), 
            0
        ).unwrap_or_else(|| chrono::Local::now().naive_local())
    }
}

#[async_trait::async_trait]
impl AuditRepository for SqliteAuditRepository {
    async fn create_audit_log(&self, input: CreateAuditLogInput) -> Result<AuditLog, DomainError> {
        let id = uuid::Uuid::new_v4().to_string();
        let now = chrono::Local::now().naive_local();
        
        // Calcola data retention
        let settings = self.get_gdpr_settings().await?;
        let retention = self.calculate_retention(&input.gdpr_category, &settings);
        
        // Calcola diff se UPDATE
        let diff = if input.action == AuditAction::Update {
            if let (Some(before), Some(after)) = (&input.data_before, &input.data_after) {
                Some(calculate_json_diff(before, after))
            } else {
                None
            }
        } else {
            None
        };
        
        sqlx::query(
            r#"
            INSERT INTO audit_logs (
                id, timestamp, session_id, user_id, user_type,
                action, action_subtype, entity_type, entity_id,
                data_before, data_after, data_diff,
                gdpr_category, gdpr_legal_basis, source, source_ip,
                vertical, note, retention_until, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            "#
        )
        .bind(&id)
        .bind(now)
        .bind(&input.session_id)
        .bind(&input.user_id)
        .bind(serde_json::to_string(&input.user_type).unwrap())
        .bind(serde_json::to_string(&input.action).unwrap())
        .bind(input.action_subtype.as_ref().map(|s| serde_json::to_string(s).unwrap()))
        .bind(serde_json::to_string(&input.entity_type).unwrap())
        .bind(&input.entity_id)
        .bind(input.data_before.as_ref().map(|v| v.to_string()))
        .bind(input.data_after.as_ref().map(|v| v.to_string()))
        .bind(diff.as_ref().map(|v| v.to_string()))
        .bind(serde_json::to_string(&input.gdpr_category).unwrap())
        .bind(input.gdpr_legal_basis.as_ref().map(|s| serde_json::to_string(s).unwrap()))
        .bind(serde_json::to_string(&input.source).unwrap())
        .bind(&input.source_ip)
        .bind(&input.vertical)
        .bind(&input.note)
        .bind(retention)
        .bind(now)
        .execute(&self.pool)
        .await
        .map_err(|e| DomainError::Database(e.to_string()))?;
        
        self.get_audit_log(&id).await?.ok_or(DomainError::NotFound("Audit log not created".to_string()))
    }
    
    // ... altri metodi del repository
}

/// Calcola differenza tra due oggetti JSON
fn calculate_json_diff(before: &serde_json::Value, after: &serde_json::Value) -> serde_json::Value {
    let mut diff = serde_json::Map::new();
    
    if let (Some(b_obj), Some(a_obj)) = (before.as_object(), after.as_object()) {
        for (key, after_val) in a_obj {
            match b_obj.get(key) {
                Some(before_val) if before_val != after_val => {
                    diff.insert(format!("{}_before", key), before_val.clone());
                    diff.insert(format!("{}_after", key), after_val.clone());
                }
                None => {
                    diff.insert(format!("{}_added", key), after_val.clone());
                }
                _ => {}
            }
        }
    }
    
    serde_json::Value::Object(diff)
}
```

### 2.4 Audit Service - `src-tauri/src/services/audit_service.rs`

**File**: `src-tauri/src/services/audit_service.rs` (NEW)

```rust
//! High-level audit service for business logic

use sqlx::SqlitePool;
use std::sync::Arc;

use crate::domain::audit::*;
use crate::infra::repositories::audit_repo::SqliteAuditRepository;

pub struct AuditService {
    repo: Arc<dyn AuditRepository>,
}

impl AuditService {
    pub fn new(pool: SqlitePool) -> Self {
        Self {
            repo: Arc::new(SqliteAuditRepository::new(pool)),
        }
    }
    
    /// Log creazione cliente
    pub async fn log_cliente_created(
        &self,
        cliente: &Cliente,
        source: AuditSource,
        user_id: Option<String>,
    ) -> Result<(), String> {
        let input = CreateAuditLogInput {
            session_id: None,
            user_id,
            user_type: if source == AuditSource::Voice { 
                UserType::VoiceAgent 
            } else { 
                UserType::Operatore 
            },
            action: AuditAction::Create,
            action_subtype: None,
            entity_type: AuditEntityType::Cliente,
            entity_id: cliente.id.clone(),
            data_before: None,
            data_after: Some(serde_json::to_value(cliente).unwrap()),
            gdpr_category: GdprCategory::PersonalData,
            gdpr_legal_basis: Some(GdprLegalBasis::Consent),
            source,
            source_ip: None,
            vertical: None,
            note: Some("Cliente creato".to_string()),
        };
        
        self.repo.create_audit_log(input).await.map_err(|e| e.to_string())?;
        Ok(())
    }
    
    /// Log update cliente (con diff)
    pub async fn log_cliente_updated(
        &self,
        before: &Cliente,
        after: &Cliente,
        source: AuditSource,
        user_id: Option<String>,
    ) -> Result<(), String> {
        let input = CreateAuditLogInput {
            session_id: None,
            user_id,
            user_type: UserType::Operatore,
            action: AuditAction::Update,
            action_subtype: None,
            entity_type: AuditEntityType::Cliente,
            entity_id: after.id.clone(),
            data_before: Some(serde_json::to_value(before).unwrap()),
            data_after: Some(serde_json::to_value(after).unwrap()),
            gdpr_category: GdprCategory::PersonalData,
            gdpr_legal_basis: Some(GdprLegalBasis::Consent),
            source,
            source_ip: None,
            vertical: None,
            note: Some("Cliente modificato".to_string()),
        };
        
        self.repo.create_audit_log(input).await.map_err(|e| e.to_string())?;
        Ok(())
    }
    
    /// Log cancellazione cliente (soft delete)
    pub async fn log_cliente_deleted(
        &self,
        cliente: &Cliente,
        source: AuditSource,
        user_id: Option<String>,
    ) -> Result<(), String> {
        let input = CreateAuditLogInput {
            session_id: None,
            user_id,
            user_type: UserType::Operatore,
            action: AuditAction::Delete,
            action_subtype: Some(AuditActionSubtype::SoftDelete),
            entity_type: AuditEntityType::Cliente,
            entity_id: cliente.id.clone(),
            data_before: Some(serde_json::to_value(cliente).unwrap()),
            data_after: None,
            gdpr_category: GdprCategory::PersonalData,
            gdpr_legal_basis: Some(GdprLegalBasis::Consent),
            source,
            source_ip: None,
            vertical: None,
            note: Some("Cliente eliminato (soft delete)".to_string()),
        };
        
        self.repo.create_audit_log(input).await.map_err(|e| e.to_string())?;
        Ok(())
    }
    
    /// Log cambio consenso marketing/whatsapp
    pub async fn log_consent_changed(
        &self,
        cliente_id: &str,
        consent_type: &str,  // "marketing" o "whatsapp"
        old_value: bool,
        new_value: bool,
        source: AuditSource,
    ) -> Result<(), String> {
        let input = CreateAuditLogInput {
            session_id: None,
            user_id: None,
            user_type: UserType::System,
            action: AuditAction::Update,
            action_subtype: Some(if new_value { 
                AuditActionSubtype::ConsentGrant 
            } else { 
                AuditActionSubtype::ConsentRevoke 
            }),
            entity_type: AuditEntityType::Consenso,
            entity_id: cliente_id.to_string(),
            data_before: Some(serde_json::json!({ consent_type: old_value })),
            data_after: Some(serde_json::json!({ consent_type: new_value })),
            gdpr_category: GdprCategory::Consent,
            gdpr_legal_basis: Some(GdprLegalBasis::Consent),
            source,
            source_ip: None,
            vertical: None,
            note: Some(format!("Consenso {} modificato", consent_type)),
        };
        
        self.repo.create_audit_log(input).await.map_err(|e| e.to_string())?;
        Ok(())
    }
    
    /// Log appuntamento
    pub async fn log_appuntamento_action(
        &self,
        action: AuditAction,
        appuntamento: &Appuntamento,
        source: AuditSource,
        user_id: Option<String>,
    ) -> Result<(), String> {
        let input = CreateAuditLogInput {
            session_id: None,
            user_id,
            user_type: if source == AuditSource::Voice { 
                UserType::VoiceAgent 
            } else { 
                UserType::Operatore 
            },
            action,
            action_subtype: None,
            entity_type: AuditEntityType::Appuntamento,
            entity_id: appuntamento.id.clone(),
            data_before: None, // Popolato esternamente per UPDATE
            data_after: Some(serde_json::to_value(appuntamento).unwrap()),
            gdpr_category: GdprCategory::Booking,
            gdpr_legal_basis: Some(GdprLegalBasis::Contract),
            source,
            source_ip: None,
            vertical: None,
            note: None,
        };
        
        self.repo.create_audit_log(input).await.map_err(|e| e.to_string())?;
        Ok(())
    }
    
    /// Cleanup schedulato
    pub async fn run_cleanup(&self) -> Result<i64, String> {
        self.repo.cleanup_expired_logs().await.map_err(|e| e.to_string())
    }
}
```

### 2.5 Hook Points in Commands

**File**: `src-tauri/src/commands/clienti.rs` (Modifiche)

```rust
// AGGIUNGERE in create_cliente:
#[tauri::command]
pub async fn create_cliente(
    pool: State<'_, SqlitePool>,
    input: CreateClienteInput,
    // Aggiungere parametro opzionale per source
    source: Option<String>,
) -> Result<Cliente, String> {
    // ... existing code ...
    
    // DOPO la creazione, loggare l'audit
    let audit_service = AuditService::new(pool.inner().clone());
    let audit_source = match source.as_deref() {
        Some("voice") => AuditSource::Voice,
        _ => AuditSource::Web,
    };
    
    if let Err(e) = audit_service.log_cliente_created(&cliente, audit_source, None).await {
        eprintln!("[AUDIT] Failed to log cliente creation: {}", e);
        // Non fallire l'operazione per errore audit
    }
    
    Ok(cliente)
}

// AGGIUNGERE in update_cliente:
#[tauri::command]
pub async fn update_cliente(
    pool: State<'_, SqlitePool>,
    input: UpdateClienteInput,
) -> Result<Cliente, String> {
    // RECUPERARE prima il cliente corrente per confronto
    let before = get_cliente(pool.clone(), input.id.clone()).await?;
    
    // ... existing update code ...
    
    let after = get_cliente(pool.clone(), input.id).await?;
    
    // Log audit
    let audit_service = AuditService::new(pool.inner().clone());
    if let Err(e) = audit_service.log_cliente_updated(&before, &after, AuditSource::Web, None).await {
        eprintln!("[AUDIT] Failed to log cliente update: {}", e);
    }
    
    Ok(after)
}

// AGGIUNGERE in delete_cliente:
#[tauri::command]
pub async fn delete_cliente(
    pool: State<'_, SqlitePool>, 
    id: String
) -> Result<(), String> {
    // RECUPERARE cliente prima della cancellazione
    let cliente = get_cliente(pool.clone(), id.clone()).await?;
    
    // ... existing delete code ...
    
    // Log audit
    let audit_service = AuditService::new(pool.inner().clone());
    if let Err(e) = audit_service.log_cliente_deleted(&cliente, AuditSource::Web, None).await {
        eprintln!("[AUDIT] Failed to log cliente deletion: {}", e);
    }
    
    Ok(())
}
```

**File**: `src-tauri/src/commands/appuntamenti.rs` (Modifiche similari)

```rust
// Hook in create_appuntamento, update_appuntamento, delete_appuntamento
// Pattern identico a clienti.rs
```

### 2.6 Tauri Commands per Audit

**File**: `src-tauri/src/commands/audit.rs` (NEW)

```rust
//! Tauri commands for audit log queries

use serde::{Deserialize, Serialize};
use sqlx::SqlitePool;
use tauri::State;

use crate::services::audit_service::AuditService;
use crate::domain::audit::{AuditLogFilters, GdprSettings};

#[derive(Debug, Serialize, Deserialize)]
pub struct AuditQueryParams {
    pub entity_type: Option<String>,
    pub entity_id: Option<String>,
    pub action: Option<String>,
    pub date_from: Option<String>,
    pub date_to: Option<String>,
    pub limit: Option<i64>,
}

/// Query audit logs con filtri
#[tauri::command]
pub async fn query_audit_logs(
    pool: State<'_, SqlitePool>,
    params: AuditQueryParams,
) -> Result<Vec<AuditLogResponse>, String> {
    let service = AuditService::new(pool.inner().clone());
    
    let filters = AuditLogFilters {
        entity_type: params.entity_type.and_then(|s| parse_entity_type(&s)),
        entity_id: params.entity_id,
        action: params.action.and_then(|s| parse_action(&s)),
        date_from: params.date_from.and_then(|d| parse_datetime(&d)),
        date_to: params.date_to.and_then(|d| parse_datetime(&d)),
        limit: params.limit,
        ..Default::default()
    };
    
    service.query_logs(filters).await.map_err(|e| e.to_string())
}

/// Recupera storico per entità
#[tauri::command]
pub async fn get_entity_audit_history(
    pool: State<'_, SqlitePool>,
    entity_type: String,
    entity_id: String,
) -> Result<Vec<AuditLogResponse>, String> {
    let service = AuditService::new(pool.inner().clone());
    service.get_entity_history(&entity_type, &entity_id).await.map_err(|e| e.to_string())
}

/// Recupera settings GDPR
#[tauri::command]
pub async fn get_gdpr_settings(
    pool: State<'_, SqlitePool>,
) -> Result<GdprSettings, String> {
    let service = AuditService::new(pool.inner().clone());
    service.get_settings().await.map_err(|e| e.to_string())
}

/// Esegue cleanup manuale (admin only)
#[tauri::command]
pub async fn run_audit_cleanup(
    pool: State<'_, SqlitePool>,
) -> Result<i64, String> {
    let service = AuditService::new(pool.inner().clone());
    service.run_cleanup().await
}

/// Esporta audit logs per report GDPR (CSV/JSON)
#[tauri::command]
pub async fn export_audit_logs(
    pool: State<'_, SqlitePool>,
    date_from: String,
    date_to: String,
    format: String,  // "json" o "csv"
) -> Result<String, String> {
    let service = AuditService::new(pool.inner().clone());
    service.export_logs(&date_from, &date_to, &format).await.map_err(|e| e.to_string())
}
```

---

## Phase 3: Voice Python Integration

### 3.1 Audit Client Module - `voice-agent/src/audit_client.py`

**File**: `voice-agent/src/audit_client.py` (NEW)

```python
"""
GDPR Audit Trail Client for Voice Agent

Handles logging of voice operations to the SQLite database via HTTP Bridge.
"""

import json
import httpx
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from functools import wraps

HTTP_BRIDGE_URL = "http://127.0.0.1:3001"


@dataclass
class AuditEvent:
    """Rappresenta un evento audit da loggare."""
    action: str                          # 'CREATE', 'UPDATE', 'DELETE', 'VIEW'
    entity_type: str                     # 'cliente', 'appuntamento', 'consenso'
    entity_id: str
    data_before: Optional[Dict] = None
    data_after: Optional[Dict] = None
    session_id: Optional[str] = None
    gdpr_category: str = 'personal_data'  # 'personal_data', 'consent', 'booking'
    legal_basis: str = 'consent'
    note: Optional[str] = None


class AuditClient:
    """Client per inviare audit logs al backend Rust."""
    
    def __init__(self, bridge_url: str = HTTP_BRIDGE_URL):
        self.bridge_url = bridge_url
        self._queue: list = []
        self._enabled = True
    
    async def log_event(self, event: AuditEvent) -> bool:
        """Logga un evento audit."""
        if not self._enabled:
            return True
        
        payload = {
            'timestamp': datetime.now().isoformat(),
            'session_id': event.session_id,
            'user_id': None,  # Voice agent è system
            'user_type': 'voice_agent',
            'action': event.action,
            'entity_type': event.entity_type,
            'entity_id': event.entity_id,
            'data_before': json.dumps(event.data_before) if event.data_before else None,
            'data_after': json.dumps(event.data_after) if event.data_after else None,
            'gdpr_category': event.gdpr_category,
            'gdpr_legal_basis': event.legal_basis,
            'source': 'voice',
            'note': event.note,
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.bridge_url}/audit/log",
                    json=payload,
                    timeout=5.0
                )
                return response.status_code == 200
        except Exception as e:
            print(f"[AUDIT] Failed to log event: {e}")
            # Queue per retry async
            self._queue.append(payload)
            return False
    
    def log_sync(self, event: AuditEvent) -> None:
        """Versione sincrona per chiamate da codice sync."""
        try:
            asyncio.create_task(self.log_event(event))
        except Exception as e:
            print(f"[AUDIT] Failed to schedule audit log: {e}")
    
    # Helper methods per casi comuni
    
    async def log_cliente_created(self, cliente: Dict, session_id: Optional[str] = None):
        """Log creazione cliente."""
        await self.log_event(AuditEvent(
            action='CREATE',
            entity_type='cliente',
            entity_id=cliente.get('id', 'unknown'),
            data_after=cliente,
            session_id=session_id,
            gdpr_category='personal_data',
            note='Cliente creato via voice agent'
        ))
    
    async def log_appuntamento_created(self, appuntamento: Dict, session_id: Optional[str] = None):
        """Log creazione appuntamento."""
        await self.log_event(AuditEvent(
            action='CREATE',
            entity_type='appuntamento',
            entity_id=appuntamento.get('id', 'unknown'),
            data_after=appuntamento,
            session_id=session_id,
            gdpr_category='booking',
            legal_basis='contract',
            note='Appuntamento creato via voice agent'
        ))
    
    async def log_consent_updated(self, cliente_id: str, consenso_type: str, 
                                   value: bool, session_id: Optional[str] = None):
        """Log aggiornamento consenso."""
        await self.log_event(AuditEvent(
            action='UPDATE',
            entity_type='consenso',
            entity_id=cliente_id,
            data_after={consenso_type: value},
            session_id=session_id,
            gdpr_category='consent',
            note=f'Consenso {consenso_type} aggiornato via voice'
        ))
    
    async def log_voice_session(self, session_data: Dict):
        """Log sessione voice completa."""
        await self.log_event(AuditEvent(
            action='VIEW',  # Sessione voice = accesso ai dati
            entity_type='voice_session',
            entity_id=session_data.get('session_id', 'unknown'),
            data_after=session_data,
            session_id=session_data.get('session_id'),
            gdpr_category='personal_data',
            note=f"Voice session: {session_data.get('intent', 'unknown')}"
        ))


# Singleton instance
_audit_client: Optional[AuditClient] = None


def get_audit_client() -> AuditClient:
    """Get or create singleton audit client."""
    global _audit_client
    if _audit_client is None:
        _audit_client = AuditClient()
    return _audit_client


# Decorator per audit automatico

def audit_action(action: str, entity_type: str, gdpr_category: str = 'personal_data'):
    """
    Decorator per audit automatico di funzioni.
    
    Usage:
        @audit_action('CREATE', 'cliente')
        async def create_cliente(self, data):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Estrai session_id dai kwargs o args
            session_id = kwargs.get('session_id') or kwargs.get('call_sid')
            
            # Esegui funzione
            result = await func(*args, **kwargs)
            
            # Log audit
            client = get_audit_client()
            if isinstance(result, dict) and 'id' in result:
                await client.log_event(AuditEvent(
                    action=action,
                    entity_type=entity_type,
                    entity_id=result['id'],
                    data_after=result,
                    session_id=session_id,
                    gdpr_category=gdpr_category
                ))
            
            return result
        return wrapper
    return decorator
```

### 3.2 Integration in Orchestrator

**File**: `voice-agent/src/orchestrator.py` (Modifiche)

```python
# AGGIUNGERE in imports:
from audit_client import get_audit_client, AuditEvent

# AGGIUNGERE in __init__:
def __init__(...):
    # ... existing init ...
    self.audit_client = get_audit_client()

# AGGIUNGERE dopo creazione cliente (nel metodo appropriato):
async def _create_cliente_from_extraction(self, extraction: Dict, session: VoiceSession) -> Dict:
    """Crea cliente e logga audit."""
    
    # ... existing creation logic ...
    
    # Log audit
    await self.audit_client.log_cliente_created(
        cliente=cliente_data,
        session_id=session.session_id
    )
    
    return cliente_data

# AGGIUNGERE dopo creazione appuntamento:
async def _finalize_booking(self, session: VoiceSession) -> Dict:
    """Finalizza booking con audit log."""
    
    # ... existing booking logic ...
    
    # Log audit
    await self.audit_client.log_appuntamento_created(
        appuntamento=appuntamento_data,
        session_id=session.session_id
    )
    
    return appuntamento_data

# AGGIUNGERE in gestione consensi:
async def _update_consent(self, cliente_id: str, consenso_type: str, 
                          value: bool, session: VoiceSession):
    """Aggiorna consenso con audit log."""
    
    # ... existing consent update ...
    
    # Log audit
    await self.audit_client.log_consent_updated(
        cliente_id=cliente_id,
        consenso_type=consenso_type,
        value=value,
        session_id=session.session_id
    )

# AGGIUNGERE alla fine della sessione:
async def end_session(self, session: VoiceSession, reason: str = "completed"):
    """Chiudi sessione e logga summary."""
    
    # Log session summary
    session_summary = {
        'session_id': session.session_id,
        'phone': session.phone_number,
        'duration_seconds': session.get_duration(),
        'intent': session.intent,
        'cliente_id': session.cliente_id,
        'booking_created': session.booking is not None,
        'escalation_triggered': session.escalation_triggered,
        'turns_count': len(session.conversation_history),
    }
    
    await self.audit_client.log_voice_session(session_summary)
    
    # ... existing end session logic ...
```

### 3.3 HTTP Bridge Endpoint

**File**: `src-tauri/src/http_bridge.rs` (Aggiungere endpoint)

```rust
//! Aggiungere handler per audit logs

use axum::{
    routing::post,
    Router,
    Json,
};

// POST /audit/log - Riceve audit log dal voice agent
async fn handle_audit_log(
    State(pool): State<SqlitePool>,
    Json(payload): Json<AuditLogPayload>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    let service = AuditService::new(pool);
    
    match service.log_from_voice(payload).await {
        Ok(_) => Ok(Json(json!({"success": true }))),
        Err(e) => {
            eprintln!("[BRIDGE] Audit log error: {}", e);
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

// Aggiungere alla configurazione router:
pub fn create_router(pool: SqlitePool) -> Router {
    Router::new()
        // ... existing routes ...
        .route("/audit/log", post(handle_audit_log))
        .with_state(pool)
}
```

---

## Phase 4: Retention & Cleanup

### 4.1 Configurazione Retention

**File**: `src-tauri/src/services/retention_service.rs`

```rust
//! Data Retention Policy Service

use tokio::time::{interval, Duration};
use sqlx::SqlitePool;

pub struct RetentionService {
    pool: SqlitePool,
    audit_service: AuditService,
}

impl RetentionService {
    pub fn new(pool: SqlitePool) -> Self {
        let audit_service = AuditService::new(pool.clone());
        Self { pool, audit_service }
    }
    
    /// Avvia cleanup schedulato (ogni 24 ore)
    pub async fn start_scheduled_cleanup(self) {
        let mut interval = interval(Duration::from_secs(24 * 3600));
        
        loop {
            interval.tick().await;
            
            match self.run_cleanup().await {
                Ok(deleted) => {
                    println!("[RETENTION] Cleanup completed: {} records deleted", deleted);
                    self.update_last_cleanup().await.ok();
                }
                Err(e) => {
                    eprintln!("[RETENTION] Cleanup failed: {}", e);
                }
            }
        }
    }
    
    /// Esegue cleanup immediato
    pub async fn run_cleanup(&self) -> Result<i64, String> {
        self.audit_service.run_cleanup().await
    }
    
    /// Aggiorna timestamp ultimo cleanup
    async fn update_last_cleanup(&self) -> Result<(), sqlx::Error> {
        let now = chrono::Local::now().to_rfc3339();
        sqlx::query(
            "UPDATE gdpr_settings SET valore = ?, updated_at = datetime('now') WHERE chiave = 'last_cleanup_run'"
        )
        .bind(now)
        .execute(&self.pool)
        .await?;
        Ok(())
    }
    
    /// Calcola spazio risparmiato dal cleanup
    pub async fn calculate_storage_saved(&self) -> Result<i64, String> {
        // Query per stimare spazio
        let result: (i64,) = sqlx::query_as(
            "SELECT COUNT(*) * 1024 FROM audit_logs WHERE retention_until < datetime('now')"
        )
        .fetch_one(&self.pool)
        .await
        .map_err(|e| e.to_string())?;
        
        Ok(result.0)  // Stima bytes
    }
}
```

### 4.2 Cleanup Manuale UI

**Frontend**: Aggiungere sezione Impostazioni > Privacy & GDPR

```typescript
// Componente React per gestione GDPR
interface GdprSettings {
  retention_personal_data: number;
  retention_consent_logs: number;
  retention_booking_logs: number;
  gdpr_enabled: boolean;
}

const GdprSettingsPanel: React.FC = () => {
  const [settings, setSettings] = useState<GdprSettings | null>(null);
  const [lastCleanup, setLastCleanup] = useState<string | null>(null);
  
  const runCleanup = async () => {
    const deleted = await invoke<number>('run_audit_cleanup');
    toast.success(`${deleted} record eliminati`);
  };
  
  const exportAudit = async (format: 'json' | 'csv') => {
    const data = await invoke<string>('export_audit_logs', {
      dateFrom: dateRange.from,
      dateTo: dateRange.to,
      format
    });
    downloadFile(data, `audit-export.${format}`);
  };
  
  return (
    <div className="gdpr-settings">
      <h2>GDPR & Privacy</h2>
      
      <section>
        <h3>Retention Policy</h3>
        <RetentionSettingsForm 
          settings={settings}
          onChange={updateSettings}
        />
      </section>
      
      <section>
        <h3>Audit Logs</h3>
        <button onClick={runCleanup}>Esegui Cleanup Ora</button>
        <button onClick={() => exportAudit('json')}>Esporta JSON</button>
        <button onClick={() => exportAudit('csv')}>Esporta CSV</button>
        {lastCleanup && <p>Ultimo cleanup: {lastCleanup}</p>}
      </section>
      
      <section>
        <h3>Storico Cliente</h3>
        <EntityAuditSearch />
      </section>
    </div>
  );
};
```

---

## Task Breakdown per Specialist

| # | Specialist | Task | Files | Est. Time | Priorità |
|---|------------|------|-------|-----------|----------|
| 1 | **Backend Rust** | Creare migration SQL audit_logs | `migrations/018_gdpr_audit_logs.sql` | 2h | P0 |
| 2 | **Backend Rust** | Definire domain model audit | `src/domain/audit.rs` | 2h | P0 |
| 3 | **Backend Rust** | Aggiornare repository trait | `src/domain/repository.rs` | 1h | P0 |
| 4 | **Backend Rust** | Implementare audit repository | `src/infra/repositories/audit_repo.rs` | 4h | P0 |
| 5 | **Backend Rust** | Creare audit service | `src/services/audit_service.rs` | 4h | P0 |
| 6 | **Backend Rust** | Creare Tauri commands audit | `src/commands/audit.rs` | 3h | P0 |
| 7 | **Backend Rust** | Aggiungere hooks in clienti.rs | `src/commands/clienti.rs` | 2h | P0 |
| 8 | **Backend Rust** | Aggiungere hooks in appuntamenti.rs | `src/commands/appuntamenti.rs` | 2h | P0 |
| 9 | **Backend Rust** | Aggiungere endpoint HTTP bridge audit | `src/http_bridge.rs` | 2h | P1 |
| 10 | **Backend Rust** | Creare retention service | `src/services/retention_service.rs` | 3h | P1 |
| 11 | **Voice Python** | Creare audit client module | `voice-agent/src/audit_client.py` | 3h | P0 |
| 12 | **Voice Python** | Integrare audit in orchestrator | `voice-agent/src/orchestrator.py` | 3h | P0 |
| 13 | **Voice Python** | Aggiungere audit in booking state machine | `voice-agent/src/booking_state_machine.py` | 2h | P1 |
| 14 | **Frontend** | Creare GDPR settings panel | `src/components/settings/GdprPanel.tsx` | 4h | P1 |
| 15 | **Frontend** | Creare componente storico cliente | `src/components/clients/ClientAuditHistory.tsx` | 3h | P1 |
| 16 | **QA** | Scrivere test integration audit | `tests/audit_integration_test.rs` | 4h | P0 |
| 17 | **QA** | Scrivere test voice audit | `voice-agent/tests/test_audit.py` | 3h | P1 |
| 18 | **DevOps** | Verificare retention in produzione | - | 2h | P2 |

---

## Testing Strategy

### Unit Tests

```rust
// src-tauri/src/services/audit_service_tests.rs
#[tokio::test]
async fn test_audit_log_creation() {
    let pool = setup_test_db().await;
    let service = AuditService::new(pool);
    
    let cliente = create_test_cliente();
    service.log_cliente_created(&cliente, AuditSource::Web, None).await.unwrap();
    
    // Verify
    let logs = service.query_logs(AuditLogFilters {
        entity_type: Some(AuditEntityType::Cliente),
        ..Default::default()
    }).await.unwrap();
    
    assert_eq!(logs.len(), 1);
    assert_eq!(logs[0].action, AuditAction::Create);
}
```

### Integration Tests

```python
# voice-agent/tests/test_audit.py
async def test_voice_booking_audit():
    """Test che la creazione booking via voice generi audit log."""
    orchestrator = create_test_orchestrator()
    
    # Simula chiamata voice che crea appuntamento
    result = await orchestrator.process("Vorrei prenotare per domani alle 15")
    
    # Verifica audit log creato
    logs = await query_audit_logs(entity_type='appuntamento')
    assert len(logs) == 1
    assert logs[0]['source'] == 'voice'
```

### E2E Tests

```typescript
// e2e/gdpr-audit.spec.ts
test('client creation is audited', async ({ page }) => {
  await page.goto('/clienti');
  await page.click('[data-testid="new-cliente"]');
  await page.fill('[name="nome"]', 'Test');
  await page.fill('[name="cognome"]', 'Audit');
  await page.fill('[name="telefono"]', '+39123456789');
  await page.click('[data-testid="save"]');
  
  // Verifica in audit logs
  await page.goto('/settings/gdpr');
  await page.click('[data-testid="view-logs"]');
  await expect(page.locator('text=CREATE')).toBeVisible();
  await expect(page.locator('text=cliente')).toBeVisible();
});
```

---

## GDPR Compliance Checklist

- [x] **Art. 30**: Registro delle attività di trattamento (audit_logs table)
- [x] **Art. 5(1)(f)**: Integrità e riservatezza (log immutabili)
- [x] **Art. 17**: Diritto all'oblio (retention policy + cleanup)
- [x] **Art. 25**: Privacy by design (audit integrato nei CRUD)
- [x] **Art. 32**: Sicurezza (log accessi e modifiche)

---

## Note Implementative

1. **Non-blocking**: I log audit non devono bloccare le operazioni utente. Usare `tokio::spawn` per log async.

2. **Retry**: Implementare retry con backoff per audit log falliti.

3. **Performance**: Gli indici su `timestamp` e `entity_id` sono critici per query rapide.

4. **Storage**: Stimare ~1KB per audit log. Per 1000 operazioni/giorno = ~350MB/anno.

5. **Backup**: I log audit devono essere inclusi nei backup per compliance legale.

---

*Piano creato da GSD Planner - FLUXION Week 4 Release*
