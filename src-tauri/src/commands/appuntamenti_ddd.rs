// ═══════════════════════════════════════════════════════════════════
// FLUXION - Appuntamenti Commands (DDD Layer)
// Thin controllers usando service layer + repository pattern
// ═══════════════════════════════════════════════════════════════════

use chrono::NaiveDateTime;
use serde::{Deserialize, Serialize};
use tauri::State;

use crate::domain::{
    AppuntamentoAggregate, AppuntamentoId, DomainSuggestion, DomainWarning, ValidationResult,
};
use crate::AppState;

// ───────────────────────────────────────────────────────────────────
// DTOs (Request/Response)
// ───────────────────────────────────────────────────────────────────

/// DTO per creare bozza appuntamento
#[derive(Debug, Deserialize)]
pub struct CreaAppuntamentoBozzaDto {
    pub cliente_id: String,
    pub operatore_id: String,
    pub servizio_id: String,
    /// Format: "YYYY-MM-DDTHH:MM:SS" (naive)
    pub data_ora: String,
    pub durata_minuti: i32,
}

/// DTO per proporre appuntamento (con validazione)
#[derive(Debug, Deserialize)]
pub struct ProponiAppuntamentoDto {
    pub appuntamento_id: String,
}

/// DTO response con validation result
#[derive(Debug, Serialize)]
pub struct ProponiAppuntamentoResponse {
    pub appuntamento: AppuntamentoDto,
    pub validation: ValidationResultDto,
}

#[derive(Debug, Serialize)]
pub struct ValidationResultDto {
    pub is_blocked: bool,
    pub has_warnings: bool,
    pub has_suggestions: bool,
    pub hard_blocks: Vec<String>,
    pub warnings: Vec<WarningDto>,
    pub suggestions: Vec<SuggestionDto>,
}

#[derive(Debug, Serialize)]
pub struct WarningDto {
    pub tipo: String,
    pub messaggio: String,
}

#[derive(Debug, Serialize)]
pub struct SuggestionDto {
    pub tipo: String,
    pub messaggio: String,
}

/// DTO per conferma operatore con override
#[derive(Debug, Deserialize)]
pub struct ConfermaConOverrideDto {
    pub appuntamento_id: String,
    pub operatore_id: String,
    pub motivazione: Option<String>,
    pub warnings_ignorati: Vec<String>,
}

/// DTO per rifiuto operatore
#[derive(Debug, Deserialize)]
pub struct RifiutaAppuntamentoDto {
    pub appuntamento_id: String,
    pub motivazione: Option<String>,
}

/// DTO appuntamento (output)
#[derive(Debug, Serialize, Deserialize)]
pub struct AppuntamentoDto {
    pub id: String,
    pub cliente_id: String,
    pub operatore_id: String,
    pub servizio_id: String,
    pub data_ora: String, // ISO 8601
    pub durata_minuti: i32,
    pub stato: String,
    pub note: Option<String>,
    pub created_at: String,
    pub updated_at: String,
    pub override_info: Option<OverrideInfoDto>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct OverrideInfoDto {
    pub timestamp: String,
    pub operatore_id: String,
    pub motivazione: Option<String>,
    pub warnings_ignorati: Vec<String>,
}

// ───────────────────────────────────────────────────────────────────
// Mappers (Domain → DTO)
// ───────────────────────────────────────────────────────────────────

impl From<AppuntamentoAggregate> for AppuntamentoDto {
    fn from(agg: AppuntamentoAggregate) -> Self {
        Self {
            id: agg.id.to_string(),
            cliente_id: agg.cliente_id,
            operatore_id: agg.operatore_id,
            servizio_id: agg.servizio_id,
            data_ora: agg.data_ora.format("%Y-%m-%dT%H:%M:%S").to_string(),
            durata_minuti: agg.durata_minuti,
            stato: agg.stato.as_str().to_string(),
            note: agg.note,
            created_at: agg.created_at.format("%Y-%m-%d %H:%M:%S").to_string(),
            updated_at: agg.updated_at.format("%Y-%m-%d %H:%M:%S").to_string(),
            override_info: agg.override_info.map(|info| OverrideInfoDto {
                timestamp: info.timestamp.format("%Y-%m-%d %H:%M:%S").to_string(),
                operatore_id: info.operatore_id,
                motivazione: info.motivazione,
                warnings_ignorati: info.warnings_ignorati,
            }),
        }
    }
}

impl From<ValidationResult> for ValidationResultDto {
    fn from(vr: ValidationResult) -> Self {
        Self {
            is_blocked: vr.is_blocked(),
            has_warnings: vr.has_warnings(),
            has_suggestions: vr.has_suggestions(),
            hard_blocks: vr.hard_blocks.iter().map(|e| e.to_string()).collect(),
            warnings: vr
                .warnings
                .iter()
                .map(|w| match w {
                    DomainWarning::FuoriOrarioLavorativo {
                        orario_richiesto: _,
                        orario_lavorativo_inizio,
                        orario_lavorativo_fine,
                    } => WarningDto {
                        tipo: "FuoriOrarioLavorativo".to_string(),
                        messaggio: format!(
                            "⏰ Fuori orario lavorativo. Orari: {} - {}",
                            orario_lavorativo_inizio, orario_lavorativo_fine
                        ),
                    },
                    DomainWarning::GiornoFestivo {
                        data: _,
                        nome_festivita,
                        prossimo_giorno_lavorativo,
                    } => WarningDto {
                        tipo: "GiornoFestivo".to_string(),
                        messaggio: format!(
                            "🔴 Giorno festivo: {}. Prossimo giorno lavorativo: {}",
                            nome_festivita,
                            prossimo_giorno_lavorativo.format("%Y-%m-%d")
                        ),
                    },
                    DomainWarning::ClienteStoricoRitardi {
                        cliente_id: _,
                        numero_ritardi,
                    } => WarningDto {
                        tipo: "ClienteStoricoRitardi".to_string(),
                        messaggio: format!(
                            "⚠️ Cliente con {} ritardi pagamento ultimi 6 mesi",
                            numero_ritardi
                        ),
                    },
                    DomainWarning::OperatoreNonSpecializzato {
                        operatore_id: _,
                        servizio_id: _,
                    } => WarningDto {
                        tipo: "OperatoreNonSpecializzato".to_string(),
                        messaggio: "⚠️ Operatore non specializzato per questo servizio".to_string(),
                    },
                    DomainWarning::PausaTroppoBreve {
                        minuti_pausa,
                        minuti_raccomandati,
                    } => WarningDto {
                        tipo: "PausaTroppoBreve".to_string(),
                        messaggio: format!(
                            "⚠️ Pausa troppo breve ({} min). Raccomandati: {} min",
                            minuti_pausa, minuti_raccomandati
                        ),
                    },
                })
                .collect(),
            suggestions: vr
                .suggestions
                .iter()
                .map(|s| match s {
                    DomainSuggestion::SlotMigliore {
                        data_ora_suggerita,
                        motivo,
                    } => SuggestionDto {
                        tipo: "SlotMigliore".to_string(),
                        messaggio: format!(
                            "💡 Slot migliore disponibile: {} ({})",
                            data_ora_suggerita.format("%H:%M"),
                            motivo
                        ),
                    },
                    DomainSuggestion::OrarioPreferito {
                        cliente_id: _,
                        orario_preferito,
                        disponibilita: _,
                    } => SuggestionDto {
                        tipo: "OrarioPreferito".to_string(),
                        messaggio: format!("💡 Cliente preferisce orario: {}", orario_preferito),
                    },
                    DomainSuggestion::OperatoreSpecializzato {
                        operatore_id: _,
                        nome_operatore,
                        disponibilita: _,
                    } => SuggestionDto {
                        tipo: "OperatoreSpecializzato".to_string(),
                        messaggio: format!(
                            "💡 Operatore specializzato disponibile: {}",
                            nome_operatore
                        ),
                    },
                })
                .collect(),
        }
    }
}

// ───────────────────────────────────────────────────────────────────
// Commands (Thin Controllers)
// ───────────────────────────────────────────────────────────────────

/// Crea bozza appuntamento (stato: Bozza)
#[tauri::command]
pub async fn crea_appuntamento_bozza(
    state: State<'_, AppState>,
    dto: CreaAppuntamentoBozzaDto,
) -> Result<AppuntamentoDto, String> {
    let data_ora = NaiveDateTime::parse_from_str(&dto.data_ora, "%Y-%m-%dT%H:%M:%S")
        .map_err(|e| format!("Invalid datetime: {}", e))?;

    let aggregate = state
        .appuntamento_service
        .crea_bozza(
            dto.cliente_id,
            dto.operatore_id,
            dto.servizio_id,
            data_ora,
            dto.durata_minuti,
        )
        .await
        .map_err(|e| e.to_string())?;

    Ok(aggregate.into())
}

/// Valida e proponi appuntamento (stato: Bozza → Proposta)
///
/// Esegue validazione 3-layer e ritorna hard blocks/warnings/suggerimenti
#[tauri::command]
pub async fn proponi_appuntamento(
    state: State<'_, AppState>,
    dto: ProponiAppuntamentoDto,
) -> Result<ProponiAppuntamentoResponse, String> {
    let id = AppuntamentoId::from_string(&dto.appuntamento_id)
        .map_err(|e| format!("Invalid ID: {}", e))?;

    let aggregate = state
        .appuntamento_service
        .repository
        .find_by_id(id)
        .await
        .map_err(|e| e.to_string())?
        .ok_or_else(|| "Appuntamento not found".to_string())?;

    // Get existing appointments for conflict detection
    let appuntamenti_esistenti = state
        .appuntamento_service
        .repository
        .list_by_operatore(&aggregate.operatore_id)
        .await
        .map_err(|e| e.to_string())?;

    // Get festività (TODO: load from DB)
    let giorni_festivi = vec![];

    let (aggregate, validation) = state
        .appuntamento_service
        .proponi_appuntamento(aggregate, &appuntamenti_esistenti, &giorni_festivi)
        .await
        .map_err(|e| e.to_string())?;

    Ok(ProponiAppuntamentoResponse {
        appuntamento: aggregate.into(),
        validation: validation.into(),
    })
}

/// Cliente conferma proposta (stato: Proposta → InAttesaOperatore)
#[tauri::command]
pub async fn conferma_cliente_appuntamento(
    state: State<'_, AppState>,
    appuntamento_id: String,
) -> Result<AppuntamentoDto, String> {
    let id =
        AppuntamentoId::from_string(&appuntamento_id).map_err(|e| format!("Invalid ID: {}", e))?;

    let aggregate = state
        .appuntamento_service
        .repository
        .find_by_id(id)
        .await
        .map_err(|e| e.to_string())?
        .ok_or_else(|| "Appuntamento not found".to_string())?;

    let aggregate = state
        .appuntamento_service
        .conferma_cliente(aggregate)
        .await
        .map_err(|e| e.to_string())?;

    Ok(aggregate.into())
}

/// Operatore conferma appuntamento (stato: InAttesaOperatore → Confermato)
#[tauri::command]
pub async fn conferma_operatore_appuntamento(
    state: State<'_, AppState>,
    appuntamento_id: String,
) -> Result<AppuntamentoDto, String> {
    let id =
        AppuntamentoId::from_string(&appuntamento_id).map_err(|e| format!("Invalid ID: {}", e))?;

    let aggregate = state
        .appuntamento_service
        .repository
        .find_by_id(id)
        .await
        .map_err(|e| e.to_string())?
        .ok_or_else(|| "Appuntamento not found".to_string())?;

    let aggregate = state
        .appuntamento_service
        .conferma_operatore(aggregate)
        .await
        .map_err(|e| e.to_string())?;

    Ok(aggregate.into())
}

/// Operatore conferma con override warnings (stato: InAttesaOperatore → ConfermatoConOverride)
#[tauri::command]
pub async fn conferma_con_override_appuntamento(
    state: State<'_, AppState>,
    dto: ConfermaConOverrideDto,
) -> Result<AppuntamentoDto, String> {
    let id = AppuntamentoId::from_string(&dto.appuntamento_id)
        .map_err(|e| format!("Invalid ID: {}", e))?;

    let aggregate = state
        .appuntamento_service
        .repository
        .find_by_id(id)
        .await
        .map_err(|e| e.to_string())?
        .ok_or_else(|| "Appuntamento not found".to_string())?;

    let aggregate = state
        .appuntamento_service
        .conferma_con_override(
            aggregate,
            dto.operatore_id,
            dto.motivazione,
            dto.warnings_ignorati,
        )
        .await
        .map_err(|e| e.to_string())?;

    Ok(aggregate.into())
}

/// Operatore rifiuta appuntamento (stato: InAttesaOperatore → Rifiutato)
#[tauri::command]
pub async fn rifiuta_appuntamento(
    state: State<'_, AppState>,
    dto: RifiutaAppuntamentoDto,
) -> Result<AppuntamentoDto, String> {
    let id = AppuntamentoId::from_string(&dto.appuntamento_id)
        .map_err(|e| format!("Invalid ID: {}", e))?;

    let aggregate = state
        .appuntamento_service
        .repository
        .find_by_id(id)
        .await
        .map_err(|e| e.to_string())?
        .ok_or_else(|| "Appuntamento not found".to_string())?;

    let aggregate = state
        .appuntamento_service
        .rifiuta(aggregate, dto.motivazione)
        .await
        .map_err(|e| e.to_string())?;

    Ok(aggregate.into())
}

/// Cancella appuntamento (soft delete)
#[tauri::command]
pub async fn cancella_appuntamento_ddd(
    state: State<'_, AppState>,
    appuntamento_id: String,
) -> Result<AppuntamentoDto, String> {
    let id =
        AppuntamentoId::from_string(&appuntamento_id).map_err(|e| format!("Invalid ID: {}", e))?;

    let aggregate = state
        .appuntamento_service
        .repository
        .find_by_id(id)
        .await
        .map_err(|e| e.to_string())?
        .ok_or_else(|| "Appuntamento not found".to_string())?;

    let aggregate = state
        .appuntamento_service
        .cancella(aggregate)
        .await
        .map_err(|e| e.to_string())?;

    Ok(aggregate.into())
}

/// Sistema completa appuntamento automaticamente (stato: Confermato → Completato)
#[tauri::command]
pub async fn completa_appuntamento_auto(
    state: State<'_, AppState>,
    appuntamento_id: String,
) -> Result<AppuntamentoDto, String> {
    let id =
        AppuntamentoId::from_string(&appuntamento_id).map_err(|e| format!("Invalid ID: {}", e))?;

    let aggregate = state
        .appuntamento_service
        .repository
        .find_by_id(id)
        .await
        .map_err(|e| e.to_string())?
        .ok_or_else(|| "Appuntamento not found".to_string())?;

    let aggregate = state
        .appuntamento_service
        .completa(aggregate)
        .await
        .map_err(|e| e.to_string())?;

    Ok(aggregate.into())
}
