// ═══════════════════════════════════════════════════════════════════
// FLUXION - Orari Lavoro & Festività Commands
// Gestione orari apertura/chiusura e calendario festività italiane
// ═══════════════════════════════════════════════════════════════════

use crate::AppState;
use chrono::{Datelike, NaiveDate, NaiveDateTime, NaiveTime, Weekday};
use serde::{Deserialize, Serialize};
use sqlx::FromRow;
use tauri::State;

// ───────────────────────────────────────────────────────────────────
// Types
// ───────────────────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, FromRow)]
pub struct OrarioLavoro {
    pub id: String,
    pub giorno_settimana: i64, // 0=domenica, 1=lunedì, ..., 6=sabato
    pub ora_inizio: String,    // "HH:MM"
    pub ora_fine: String,      // "HH:MM"
    pub tipo: String,          // 'lavoro' | 'pausa'
    pub operatore_id: Option<String>,
}

#[derive(Debug, Clone, Serialize, FromRow)]
pub struct GiornoFestivo {
    pub id: String,
    pub data: String,        // "YYYY-MM-DD"
    pub descrizione: String,
    pub ricorrente: i64,     // 0 | 1
}

#[derive(Debug, Deserialize)]
pub struct CreateOrarioLavoroInput {
    pub giorno_settimana: i64,
    pub ora_inizio: String,
    pub ora_fine: String,
    pub tipo: String,
    pub operatore_id: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct CreateGiornoFestivoInput {
    pub data: String,
    pub descrizione: String,
    pub ricorrente: i64,
}

#[derive(Debug, Serialize)]
pub struct ValidazioneOrarioResult {
    pub disponibile: bool,
    pub motivo: Option<String>, // Se non disponibile, spiega perché
}

// ───────────────────────────────────────────────────────────────────
// Orari Lavoro - CRUD
// ───────────────────────────────────────────────────────────────────

#[tauri::command]
pub async fn get_orari_lavoro(
    giorno_settimana: Option<i64>,
    operatore_id: Option<String>,
    state: State<'_, AppState>,
) -> Result<Vec<OrarioLavoro>, String> {
    let db = &state.db;

    let orari = if let Some(giorno) = giorno_settimana {
        if let Some(op_id) = operatore_id {
            sqlx::query_as::<_, OrarioLavoro>(
                "SELECT * FROM orari_lavoro
                 WHERE giorno_settimana = ? AND (operatore_id = ? OR operatore_id IS NULL)
                 ORDER BY ora_inizio",
            )
            .bind(giorno)
            .bind(op_id)
            .fetch_all(db)
            .await
        } else {
            sqlx::query_as::<_, OrarioLavoro>(
                "SELECT * FROM orari_lavoro
                 WHERE giorno_settimana = ?
                 ORDER BY ora_inizio",
            )
            .bind(giorno)
            .fetch_all(db)
            .await
        }
    } else {
        sqlx::query_as::<_, OrarioLavoro>("SELECT * FROM orari_lavoro ORDER BY giorno_settimana, ora_inizio")
            .fetch_all(db)
            .await
    };

    orari.map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn create_orario_lavoro(
    input: CreateOrarioLavoroInput,
    state: State<'_, AppState>,
) -> Result<OrarioLavoro, String> {
    let db = &state.db;
    let id = uuid::Uuid::new_v4().to_string();

    sqlx::query(
        "INSERT INTO orari_lavoro (id, giorno_settimana, ora_inizio, ora_fine, tipo, operatore_id)
         VALUES (?, ?, ?, ?, ?, ?)",
    )
    .bind(&id)
    .bind(input.giorno_settimana)
    .bind(&input.ora_inizio)
    .bind(&input.ora_fine)
    .bind(&input.tipo)
    .bind(&input.operatore_id)
    .execute(db)
    .await
    .map_err(|e| e.to_string())?;

    sqlx::query_as::<_, OrarioLavoro>("SELECT * FROM orari_lavoro WHERE id = ?")
        .bind(&id)
        .fetch_one(db)
        .await
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn delete_orario_lavoro(
    id: String,
    state: State<'_, AppState>,
) -> Result<(), String> {
    let db = &state.db;

    sqlx::query("DELETE FROM orari_lavoro WHERE id = ?")
        .bind(&id)
        .execute(db)
        .await
        .map_err(|e| e.to_string())?;

    Ok(())
}

// ───────────────────────────────────────────────────────────────────
// Giorni Festivi - CRUD
// ───────────────────────────────────────────────────────────────────

#[tauri::command]
pub async fn get_giorni_festivi(
    anno: Option<i32>,
    state: State<'_, AppState>,
) -> Result<Vec<GiornoFestivo>, String> {
    let db = &state.db;

    let festivi = if let Some(year) = anno {
        let start = format!("{}-01-01", year);
        let end = format!("{}-12-31", year);

        sqlx::query_as::<_, GiornoFestivo>(
            "SELECT * FROM giorni_festivi
             WHERE data BETWEEN ? AND ?
             ORDER BY data",
        )
        .bind(start)
        .bind(end)
        .fetch_all(db)
        .await
    } else {
        sqlx::query_as::<_, GiornoFestivo>("SELECT * FROM giorni_festivi ORDER BY data")
            .fetch_all(db)
            .await
    };

    festivi.map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn is_giorno_festivo(
    data: String, // "YYYY-MM-DD"
    state: State<'_, AppState>,
) -> Result<bool, String> {
    let db = &state.db;

    let count: (i64,) = sqlx::query_as("SELECT COUNT(*) FROM giorni_festivi WHERE data = ?")
        .bind(&data)
        .fetch_one(db)
        .await
        .map_err(|e| e.to_string())?;

    Ok(count.0 > 0)
}

#[tauri::command]
pub async fn create_giorno_festivo(
    input: CreateGiornoFestivoInput,
    state: State<'_, AppState>,
) -> Result<GiornoFestivo, String> {
    let db = &state.db;
    let id = uuid::Uuid::new_v4().to_string();

    sqlx::query(
        "INSERT INTO giorni_festivi (id, data, descrizione, ricorrente)
         VALUES (?, ?, ?, ?)",
    )
    .bind(&id)
    .bind(&input.data)
    .bind(&input.descrizione)
    .bind(input.ricorrente)
    .execute(db)
    .await
    .map_err(|e| e.to_string())?;

    sqlx::query_as::<_, GiornoFestivo>("SELECT * FROM giorni_festivi WHERE id = ?")
        .bind(&id)
        .fetch_one(db)
        .await
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn delete_giorno_festivo(
    id: String,
    state: State<'_, AppState>,
) -> Result<(), String> {
    let db = &state.db;

    sqlx::query("DELETE FROM giorni_festivi WHERE id = ?")
        .bind(&id)
        .execute(db)
        .await
        .map_err(|e| e.to_string())?;

    Ok(())
}

// ───────────────────────────────────────────────────────────────────
// Validazione Orario Disponibile
// ───────────────────────────────────────────────────────────────────

#[tauri::command]
pub async fn valida_orario_appuntamento(
    data_ora_inizio: String, // "YYYY-MM-DDTHH:MM:SS" (NaiveDateTime format)
    durata_minuti: i64,
    operatore_id: Option<String>,
    state: State<'_, AppState>,
) -> Result<ValidazioneOrarioResult, String> {
    let db = &state.db;

    // Parse data/ora
    let dt = NaiveDateTime::parse_from_str(&data_ora_inizio, "%Y-%m-%dT%H:%M:%S")
        .map_err(|e| format!("Formato data/ora non valido: {}", e))?;

    let data = dt.date();
    let ora_inizio = dt.time();

    // Calcola ora_fine appuntamento
    let durata_seconds = durata_minuti * 60;
    let ora_fine = dt
        .checked_add_signed(chrono::Duration::seconds(durata_seconds))
        .ok_or("Durata non valida")?
        .time();

    // ═══════════════════════════════════════════════════════════════
    // CHECK 1: Appuntamento nel passato
    // ═══════════════════════════════════════════════════════════════
    let now = chrono::Local::now().naive_local();
    if dt < now {
        return Ok(ValidazioneOrarioResult {
            disponibile: false,
            motivo: Some("❌ Non puoi prenotare nel passato".to_string()),
        });
    }

    // ═══════════════════════════════════════════════════════════════
    // CHECK 2: Giorno festivo
    // ═══════════════════════════════════════════════════════════════
    let data_str = data.format("%Y-%m-%d").to_string();
    let festivo_count: (i64,) = sqlx::query_as(
        "SELECT COUNT(*) FROM giorni_festivi WHERE data = ?"
    )
    .bind(&data_str)
    .fetch_one(db)
    .await
    .map_err(|e| e.to_string())?;

    if festivo_count.0 > 0 {
        let festivo: GiornoFestivo = sqlx::query_as(
            "SELECT * FROM giorni_festivi WHERE data = ? LIMIT 1"
        )
        .bind(&data_str)
        .fetch_one(db)
        .await
        .map_err(|e| e.to_string())?;

        return Ok(ValidazioneOrarioResult {
            disponibile: false,
            motivo: Some(format!("🔴 Giorno festivo: {}", festivo.descrizione)),
        });
    }

    // ═══════════════════════════════════════════════════════════════
    // CHECK 3: Orari di lavoro
    // ═══════════════════════════════════════════════════════════════
    let giorno_settimana = match data.weekday() {
        Weekday::Sun => 0,
        Weekday::Mon => 1,
        Weekday::Tue => 2,
        Weekday::Wed => 3,
        Weekday::Thu => 4,
        Weekday::Fri => 5,
        Weekday::Sat => 6,
    };

    // Get orari lavoro per questo giorno (globali + specifici operatore)
    let orari: Vec<OrarioLavoro> = if let Some(ref op_id) = operatore_id {
        sqlx::query_as::<_, OrarioLavoro>(
            "SELECT * FROM orari_lavoro
             WHERE giorno_settimana = ? AND tipo = 'lavoro' AND (operatore_id = ? OR operatore_id IS NULL)
             ORDER BY ora_inizio"
        )
        .bind(giorno_settimana)
        .bind(op_id)
        .fetch_all(db)
        .await
        .map_err(|e| e.to_string())?
    } else {
        sqlx::query_as::<_, OrarioLavoro>(
            "SELECT * FROM orari_lavoro
             WHERE giorno_settimana = ? AND tipo = 'lavoro' AND operatore_id IS NULL
             ORDER BY ora_inizio"
        )
        .bind(giorno_settimana)
        .fetch_all(db)
        .await
        .map_err(|e| e.to_string())?
    };

    if orari.is_empty() {
        return Ok(ValidazioneOrarioResult {
            disponibile: false,
            motivo: Some("🔴 Giorno non lavorativo (chiuso)".to_string()),
        });
    }

    // Check se appuntamento cade dentro una fascia lavorativa
    let mut dentro_fascia_lavoro = false;

    for orario in &orari {
        let fascia_inizio = NaiveTime::parse_from_str(&orario.ora_inizio, "%H:%M")
            .map_err(|e| format!("Formato ora_inizio non valido: {}", e))?;
        let fascia_fine = NaiveTime::parse_from_str(&orario.ora_fine, "%H:%M")
            .map_err(|e| format!("Formato ora_fine non valido: {}", e))?;

        // Appuntamento deve:
        // 1. Iniziare >= ora apertura
        // 2. Finire <= ora chiusura
        if ora_inizio >= fascia_inizio && ora_fine <= fascia_fine {
            dentro_fascia_lavoro = true;
            break;
        }
    }

    if !dentro_fascia_lavoro {
        // Trova prima fascia lavorativa per suggerimento
        let prima_fascia = &orari[0];
        return Ok(ValidazioneOrarioResult {
            disponibile: false,
            motivo: Some(format!(
                "⏰ Fuori orario lavorativo. Orari disponibili: {} - {}",
                prima_fascia.ora_inizio,
                orari.last().unwrap().ora_fine
            )),
        });
    }

    // ═══════════════════════════════════════════════════════════════
    // CHECK 4: Appuntamento NON cade in pausa pranzo
    // ═══════════════════════════════════════════════════════════════
    let pause: Vec<OrarioLavoro> = if let Some(ref op_id) = operatore_id {
        sqlx::query_as::<_, OrarioLavoro>(
            "SELECT * FROM orari_lavoro
             WHERE giorno_settimana = ? AND tipo = 'pausa' AND (operatore_id = ? OR operatore_id IS NULL)"
        )
        .bind(giorno_settimana)
        .bind(op_id)
        .fetch_all(db)
        .await
        .map_err(|e| e.to_string())?
    } else {
        sqlx::query_as::<_, OrarioLavoro>(
            "SELECT * FROM orari_lavoro
             WHERE giorno_settimana = ? AND tipo = 'pausa' AND operatore_id IS NULL"
        )
        .bind(giorno_settimana)
        .fetch_all(db)
        .await
        .map_err(|e| e.to_string())?
    };

    for pausa in &pause {
        let pausa_inizio = NaiveTime::parse_from_str(&pausa.ora_inizio, "%H:%M")
            .map_err(|e| format!("Formato ora_inizio pausa non valido: {}", e))?;
        let pausa_fine = NaiveTime::parse_from_str(&pausa.ora_fine, "%H:%M")
            .map_err(|e| format!("Formato ora_fine pausa non valido: {}", e))?;

        // Check overlap con pausa (appuntamento non può sovrapporsi alla pausa)
        let overlap = !(ora_fine <= pausa_inizio || ora_inizio >= pausa_fine);

        if overlap {
            return Ok(ValidazioneOrarioResult {
                disponibile: false,
                motivo: Some(format!(
                    "☕ Appuntamento sovrapposto a pausa ({} - {})",
                    pausa.ora_inizio, pausa.ora_fine
                )),
            });
        }
    }

    // ═══════════════════════════════════════════════════════════════
    // CHECK 5: Durata vs chiusura (es. massaggio 50min, chiudo 20:00 → ultimo slot 19:10)
    // ═══════════════════════════════════════════════════════════════
    // Già gestito nel CHECK 3 (ora_fine <= fascia_fine)

    // ═══════════════════════════════════════════════════════════════
    // Validazione OK ✅
    // ═══════════════════════════════════════════════════════════════
    Ok(ValidazioneOrarioResult {
        disponibile: true,
        motivo: None,
    })
}
