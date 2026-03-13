// ═══════════════════════════════════════════════════════════════════
// FLUXION - Listini Fornitori Commands (Gap #5)
// Import Excel/CSV listini prezzi con storico variazioni
// ═══════════════════════════════════════════════════════════════════

use chrono::Utc;
use serde::{Deserialize, Serialize};
use sqlx::SqlitePool;
use tauri::State;
use uuid::Uuid;

// ═══════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════

#[derive(Debug, Serialize, Deserialize, Clone, sqlx::FromRow)]
pub struct ListinoFornitore {
    pub id: String,
    pub fornitore_id: String,
    pub nome_listino: String,
    pub data_import: String,
    pub data_validita: Option<String>,
    pub formato_fonte: String,
    pub righe_totali: i64,
    pub righe_inserite: i64,
    pub righe_aggiornate: i64,
    pub note: Option<String>,
    pub created_at: String,
}

#[derive(Debug, Serialize, Deserialize, Clone, sqlx::FromRow)]
pub struct ListinoRiga {
    pub id: String,
    pub listino_id: String,
    pub codice_articolo: Option<String>,
    pub descrizione: String,
    pub unita_misura: String,
    pub prezzo_acquisto: f64,
    pub sconto_pct: f64,
    pub prezzo_netto: Option<f64>,
    pub iva_pct: f64,
    pub categoria: Option<String>,
    pub ean: Option<String>,
    pub note: Option<String>,
    pub created_at: String,
}

#[derive(Debug, Serialize, Deserialize, Clone, sqlx::FromRow)]
pub struct ListinoVariazione {
    pub id: String,
    pub listino_riga_id: String,
    pub campo: String,
    pub valore_precedente: Option<String>,
    pub valore_nuovo: String,
    pub data_variazione: String,
}

#[derive(Debug, Deserialize)]
pub struct RigaImportInput {
    pub codice_articolo: Option<String>,
    pub descrizione: String,
    pub unita_misura: Option<String>,
    pub prezzo_acquisto: f64,
    pub sconto_pct: Option<f64>,
    pub prezzo_netto: Option<f64>,
    pub iva_pct: Option<f64>,
    pub categoria: Option<String>,
    pub ean: Option<String>,
    pub note: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct ImportListinoRequest {
    pub fornitore_id: String,
    pub nome_listino: String,
    pub data_validita: Option<String>,
    pub formato_fonte: String,
    pub righe: Vec<RigaImportInput>,
}

#[derive(Debug, Serialize)]
pub struct ImportListinoResult {
    pub listino_id: String,
    pub righe_inserite: i64,
    pub righe_aggiornate: i64,
    pub righe_totali: i64,
    pub variazioni_registrate: i64,
}

// ═══════════════════════════════════════════════════════════════════
// HELPERS (row types for non-macro queries)
// ═══════════════════════════════════════════════════════════════════

#[derive(sqlx::FromRow)]
struct DuplicatoRow {
    id: String,
    prezzo_acquisto: f64,
    sconto_pct: f64,
    prezzo_netto: Option<f64>,
    iva_pct: f64,
}

// ═══════════════════════════════════════════════════════════════════
// COMMANDS
// ═══════════════════════════════════════════════════════════════════

/// Importa un listino fornitore con rilevamento duplicati e storico variazioni.
#[tauri::command]
pub async fn import_listino(
    pool: State<'_, SqlitePool>,
    request: ImportListinoRequest,
) -> Result<ImportListinoResult, String> {
    let pool = pool.inner();
    let listino_id = Uuid::new_v4().to_string();
    let now = Utc::now()
        .naive_utc()
        .format("%Y-%m-%d %H:%M:%S")
        .to_string();

    let righe_totali = request.righe.len() as i64;
    let mut righe_inserite: i64 = 0;
    let mut righe_aggiornate: i64 = 0;
    let mut variazioni_registrate: i64 = 0;

    // Crea testata listino
    sqlx::query(
        r#"INSERT INTO listini_fornitori
          (id, fornitore_id, nome_listino, data_validita, formato_fonte,
           righe_totali, righe_inserite, righe_aggiornate, created_at)
        VALUES (?, ?, ?, ?, ?, ?, 0, 0, ?)"#,
    )
    .bind(&listino_id)
    .bind(&request.fornitore_id)
    .bind(&request.nome_listino)
    .bind(&request.data_validita)
    .bind(&request.formato_fonte)
    .bind(righe_totali)
    .bind(&now)
    .execute(pool)
    .await
    .map_err(|e: sqlx::Error| e.to_string())?;

    // Processa ogni riga
    for riga in &request.righe {
        let unita = riga
            .unita_misura
            .clone()
            .unwrap_or_else(|| "pz".to_string());
        let sconto = riga.sconto_pct.unwrap_or(0.0);
        let iva = riga.iva_pct.unwrap_or(22.0);
        let prezzo_netto = riga
            .prezzo_netto
            .unwrap_or_else(|| riga.prezzo_acquisto * (1.0 - sconto / 100.0));

        // Cerca duplicato: stesso codice_articolo per lo stesso fornitore
        let duplicato: Option<DuplicatoRow> = if let Some(ref codice) = riga.codice_articolo {
            sqlx::query_as::<_, DuplicatoRow>(
                r#"SELECT lr.id, lr.prezzo_acquisto, lr.sconto_pct, lr.prezzo_netto, lr.iva_pct
                FROM listino_righe lr
                JOIN listini_fornitori lf ON lr.listino_id = lf.id
                WHERE lf.fornitore_id = ? AND lr.codice_articolo = ?
                ORDER BY lr.created_at DESC
                LIMIT 1"#,
            )
            .bind(&request.fornitore_id)
            .bind(codice)
            .fetch_optional(pool)
            .await
            .map_err(|e: sqlx::Error| e.to_string())?
        } else {
            None
        };

        if let Some(dup) = duplicato {
            // Aggiorna riga esistente
            let riga_id = dup.id.clone();

            sqlx::query(
                r#"UPDATE listino_righe
                SET prezzo_acquisto = ?, sconto_pct = ?, prezzo_netto = ?, iva_pct = ?,
                    descrizione = ?, categoria = ?, ean = ?, note = ?
                WHERE id = ?"#,
            )
            .bind(riga.prezzo_acquisto)
            .bind(sconto)
            .bind(prezzo_netto)
            .bind(iva)
            .bind(&riga.descrizione)
            .bind(&riga.categoria)
            .bind(&riga.ean)
            .bind(&riga.note)
            .bind(&riga_id)
            .execute(pool)
            .await
            .map_err(|e: sqlx::Error| e.to_string())?;

            // Registra variazioni sui campi cambiati
            let fields: &[(&str, f64, f64)] = &[
                ("prezzo_acquisto", dup.prezzo_acquisto, riga.prezzo_acquisto),
                ("sconto_pct", dup.sconto_pct, sconto),
                ("iva_pct", dup.iva_pct, iva),
            ];
            for (campo, vecchio, nuovo) in fields {
                if (vecchio - nuovo).abs() > 0.001 {
                    let var_id = Uuid::new_v4().to_string();
                    let vec_str = vecchio.to_string();
                    let new_str = nuovo.to_string();
                    sqlx::query(
                        r#"INSERT INTO listino_variazioni
                          (id, listino_riga_id, campo, valore_precedente, valore_nuovo)
                        VALUES (?, ?, ?, ?, ?)"#,
                    )
                    .bind(&var_id)
                    .bind(&riga_id)
                    .bind(campo)
                    .bind(&vec_str)
                    .bind(&new_str)
                    .execute(pool)
                    .await
                    .map_err(|e: sqlx::Error| e.to_string())?;
                    variazioni_registrate += 1;
                }
            }
            // Variazione prezzo_netto
            if let Some(old_netto) = dup.prezzo_netto {
                if (old_netto - prezzo_netto).abs() > 0.001 {
                    let var_id = Uuid::new_v4().to_string();
                    let vec_str = old_netto.to_string();
                    let new_str = prezzo_netto.to_string();
                    sqlx::query(
                        r#"INSERT INTO listino_variazioni
                          (id, listino_riga_id, campo, valore_precedente, valore_nuovo)
                        VALUES (?, ?, ?, ?, ?)"#,
                    )
                    .bind(&var_id)
                    .bind(&riga_id)
                    .bind("prezzo_netto")
                    .bind(&vec_str)
                    .bind(&new_str)
                    .execute(pool)
                    .await
                    .map_err(|e: sqlx::Error| e.to_string())?;
                    variazioni_registrate += 1;
                }
            }

            righe_aggiornate += 1;
        } else {
            // Inserisci nuova riga
            let riga_id = Uuid::new_v4().to_string();
            sqlx::query(
                r#"INSERT INTO listino_righe
                  (id, listino_id, codice_articolo, descrizione, unita_misura,
                   prezzo_acquisto, sconto_pct, prezzo_netto, iva_pct,
                   categoria, ean, note)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"#,
            )
            .bind(&riga_id)
            .bind(&listino_id)
            .bind(&riga.codice_articolo)
            .bind(&riga.descrizione)
            .bind(&unita)
            .bind(riga.prezzo_acquisto)
            .bind(sconto)
            .bind(prezzo_netto)
            .bind(iva)
            .bind(&riga.categoria)
            .bind(&riga.ean)
            .bind(&riga.note)
            .execute(pool)
            .await
            .map_err(|e: sqlx::Error| e.to_string())?;

            righe_inserite += 1;
        }
    }

    // Aggiorna contatori testata
    sqlx::query(
        r#"UPDATE listini_fornitori
        SET righe_inserite = ?, righe_aggiornate = ?
        WHERE id = ?"#,
    )
    .bind(righe_inserite)
    .bind(righe_aggiornate)
    .bind(&listino_id)
    .execute(pool)
    .await
    .map_err(|e: sqlx::Error| e.to_string())?;

    Ok(ImportListinoResult {
        listino_id,
        righe_inserite,
        righe_aggiornate,
        righe_totali,
        variazioni_registrate,
    })
}

/// Restituisce tutti i listini di un fornitore, ordinati per data decrescente.
#[tauri::command]
pub async fn get_listini_fornitore(
    pool: State<'_, SqlitePool>,
    fornitore_id: String,
) -> Result<Vec<ListinoFornitore>, String> {
    let pool = pool.inner();
    let listini: Vec<ListinoFornitore> = sqlx::query_as::<_, ListinoFornitore>(
        r#"SELECT id, fornitore_id, nome_listino, data_import, data_validita,
               formato_fonte, righe_totali, righe_inserite, righe_aggiornate,
               note, created_at
        FROM listini_fornitori
        WHERE fornitore_id = ?
        ORDER BY data_import DESC"#,
    )
    .bind(&fornitore_id)
    .fetch_all(pool)
    .await
    .map_err(|e: sqlx::Error| e.to_string())?;

    Ok(listini)
}

/// Restituisce le righe di un listino con paginazione opzionale.
#[tauri::command]
pub async fn get_listino_righe(
    pool: State<'_, SqlitePool>,
    listino_id: String,
) -> Result<Vec<ListinoRiga>, String> {
    let pool = pool.inner();
    let righe: Vec<ListinoRiga> = sqlx::query_as::<_, ListinoRiga>(
        r#"SELECT id, listino_id, codice_articolo, descrizione, unita_misura,
               prezzo_acquisto, sconto_pct, prezzo_netto, iva_pct,
               categoria, ean, note, created_at
        FROM listino_righe
        WHERE listino_id = ?
        ORDER BY descrizione ASC"#,
    )
    .bind(&listino_id)
    .fetch_all(pool)
    .await
    .map_err(|e: sqlx::Error| e.to_string())?;

    Ok(righe)
}

/// Elimina un listino e tutte le sue righe (CASCADE).
#[tauri::command]
pub async fn delete_listino(pool: State<'_, SqlitePool>, listino_id: String) -> Result<(), String> {
    let pool = pool.inner();
    sqlx::query("DELETE FROM listini_fornitori WHERE id = ?")
        .bind(&listino_id)
        .execute(pool)
        .await
        .map_err(|e: sqlx::Error| e.to_string())?;
    Ok(())
}

/// Restituisce le variazioni di prezzo registrate per una riga.
#[tauri::command]
pub async fn get_listino_variazioni(
    pool: State<'_, SqlitePool>,
    listino_riga_id: String,
) -> Result<Vec<ListinoVariazione>, String> {
    let pool = pool.inner();
    let variazioni: Vec<ListinoVariazione> = sqlx::query_as::<_, ListinoVariazione>(
        r#"SELECT id, listino_riga_id, campo, valore_precedente, valore_nuovo, data_variazione
        FROM listino_variazioni
        WHERE listino_riga_id = ?
        ORDER BY data_variazione DESC"#,
    )
    .bind(&listino_riga_id)
    .fetch_all(pool)
    .await
    .map_err(|e: sqlx::Error| e.to_string())?;

    Ok(variazioni)
}
