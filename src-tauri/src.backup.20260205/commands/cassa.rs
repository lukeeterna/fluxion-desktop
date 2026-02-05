// ═══════════════════════════════════════════════════════════════════
// FLUXION - Cassa/Incassi Commands
// Gestione pagamenti e chiusure cassa
// ═══════════════════════════════════════════════════════════════════

use serde::{Deserialize, Serialize};
use sqlx::SqlitePool;
use tauri::State;

// ───────────────────────────────────────────────────────────────────
// Types
// ───────────────────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct Incasso {
    pub id: String,
    pub importo: f64,
    pub metodo_pagamento: String,
    pub cliente_id: Option<String>,
    pub appuntamento_id: Option<String>,
    pub fattura_id: Option<String>,
    pub descrizione: Option<String>,
    pub categoria: Option<String>,
    pub operatore_id: Option<String>,
    pub data_incasso: String,
    pub created_at: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CreateIncassoInput {
    pub importo: f64,
    pub metodo_pagamento: String,
    pub cliente_id: Option<String>,
    pub appuntamento_id: Option<String>,
    pub descrizione: Option<String>,
    pub categoria: Option<String>,
    pub operatore_id: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct ChiusuraCassa {
    pub id: String,
    pub data_chiusura: String,
    pub totale_contanti: f64,
    pub totale_carte: f64,
    pub totale_satispay: f64,
    pub totale_bonifici: f64,
    pub totale_altro: f64,
    pub totale_giornata: f64,
    pub numero_transazioni: i32,
    pub fondo_cassa_iniziale: f64,
    pub fondo_cassa_finale: f64,
    pub note: Option<String>,
    pub operatore_id: Option<String>,
    pub created_at: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ReportIncassiGiornata {
    pub data: String,
    pub totale: f64,
    pub totale_contanti: f64,
    pub totale_carte: f64,
    pub totale_satispay: f64,
    pub totale_altro: f64,
    pub numero_transazioni: i32,
    pub incassi: Vec<IncassoConDettagli>,
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct IncassoConDettagli {
    pub id: String,
    pub importo: f64,
    pub metodo_pagamento: String,
    pub descrizione: Option<String>,
    pub categoria: Option<String>,
    pub data_incasso: String,
    pub cliente_nome: Option<String>,
    pub servizio_nome: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct MetodoPagamento {
    pub codice: String,
    pub nome: String,
    pub icona: Option<String>,
    pub attivo: i32,
    pub ordine: i32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ReportPeriodo {
    pub data_inizio: String,
    pub data_fine: String,
    pub totale: f64,
    pub per_metodo: Vec<TotaleMetodo>,
    pub per_giorno: Vec<TotaleGiorno>,
    pub numero_transazioni: i32,
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct TotaleMetodo {
    pub metodo: String,
    pub totale: f64,
    pub count: i32,
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct TotaleGiorno {
    pub data: String,
    pub totale: f64,
    pub count: i32,
}

// ───────────────────────────────────────────────────────────────────
// Commands
// ───────────────────────────────────────────────────────────────────

/// Registra un nuovo incasso
#[tauri::command]
pub async fn registra_incasso(
    pool: State<'_, SqlitePool>,
    input: CreateIncassoInput,
) -> Result<Incasso, String> {
    let id = uuid::Uuid::new_v4().to_string();

    sqlx::query(
        r#"
        INSERT INTO incassi (
            id, importo, metodo_pagamento, cliente_id, appuntamento_id,
            descrizione, categoria, operatore_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        "#,
    )
    .bind(&id)
    .bind(input.importo)
    .bind(&input.metodo_pagamento)
    .bind(&input.cliente_id)
    .bind(&input.appuntamento_id)
    .bind(&input.descrizione)
    .bind(&input.categoria)
    .bind(&input.operatore_id)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Errore registrazione incasso: {}", e))?;

    // Fetch and return
    let incasso = sqlx::query_as::<_, Incasso>("SELECT * FROM incassi WHERE id = ?")
        .bind(&id)
        .fetch_one(pool.inner())
        .await
        .map_err(|e| format!("Errore lettura incasso: {}", e))?;

    Ok(incasso)
}

/// Ottieni incassi di oggi
#[tauri::command]
pub async fn get_incassi_oggi(
    pool: State<'_, SqlitePool>,
) -> Result<ReportIncassiGiornata, String> {
    let oggi = chrono::Local::now().format("%Y-%m-%d").to_string();
    get_incassi_giornata_internal(&pool, &oggi).await
}

/// Ottieni incassi di una specifica giornata
#[tauri::command]
pub async fn get_incassi_giornata(
    pool: State<'_, SqlitePool>,
    data: String,
) -> Result<ReportIncassiGiornata, String> {
    get_incassi_giornata_internal(&pool, &data).await
}

async fn get_incassi_giornata_internal(
    pool: &SqlitePool,
    data: &str,
) -> Result<ReportIncassiGiornata, String> {
    // Query incassi con dettagli cliente/servizio (runtime query for CI compatibility)
    let incassi: Vec<IncassoConDettagli> = sqlx::query_as::<_, IncassoConDettagli>(
        r#"
        SELECT
            i.id,
            i.importo,
            i.metodo_pagamento,
            i.descrizione,
            i.categoria,
            i.data_incasso,
            c.nome || ' ' || c.cognome as cliente_nome,
            s.nome as servizio_nome
        FROM incassi i
        LEFT JOIN clienti c ON i.cliente_id = c.id
        LEFT JOIN appuntamenti a ON i.appuntamento_id = a.id
        LEFT JOIN servizi s ON a.servizio_id = s.id
        WHERE date(i.data_incasso) = ?
        ORDER BY i.data_incasso DESC
        "#,
    )
    .bind(data)
    .fetch_all(pool)
    .await
    .map_err(|e| format!("Errore lettura incassi: {}", e))?;

    // Calcola totali
    let mut totale = 0.0;
    let mut totale_contanti = 0.0;
    let mut totale_carte = 0.0;
    let mut totale_satispay = 0.0;
    let mut totale_altro = 0.0;

    for inc in &incassi {
        totale += inc.importo;
        match inc.metodo_pagamento.as_str() {
            "contanti" => totale_contanti += inc.importo,
            "carta" => totale_carte += inc.importo,
            "satispay" => totale_satispay += inc.importo,
            _ => totale_altro += inc.importo,
        }
    }

    Ok(ReportIncassiGiornata {
        data: data.to_string(),
        totale,
        totale_contanti,
        totale_carte,
        totale_satispay,
        totale_altro,
        numero_transazioni: incassi.len() as i32,
        incassi,
    })
}

/// Ottieni report incassi per periodo
#[tauri::command]
pub async fn get_report_incassi_periodo(
    pool: State<'_, SqlitePool>,
    data_inizio: String,
    data_fine: String,
) -> Result<ReportPeriodo, String> {
    // Totali per metodo (runtime query for CI compatibility)
    let per_metodo: Vec<TotaleMetodo> = sqlx::query_as::<_, TotaleMetodo>(
        r#"
        SELECT
            metodo_pagamento as metodo,
            COALESCE(SUM(importo), 0.0) as totale,
            COUNT(*) as count
        FROM incassi
        WHERE date(data_incasso) BETWEEN ? AND ?
        GROUP BY metodo_pagamento
        ORDER BY totale DESC
        "#,
    )
    .bind(&data_inizio)
    .bind(&data_fine)
    .fetch_all(pool.inner())
    .await
    .map_err(|e| format!("Errore report per metodo: {}", e))?;

    // Totali per giorno (runtime query for CI compatibility)
    let per_giorno: Vec<TotaleGiorno> = sqlx::query_as::<_, TotaleGiorno>(
        r#"
        SELECT
            date(data_incasso) as data,
            COALESCE(SUM(importo), 0.0) as totale,
            COUNT(*) as count
        FROM incassi
        WHERE date(data_incasso) BETWEEN ? AND ?
        GROUP BY date(data_incasso)
        ORDER BY data ASC
        "#,
    )
    .bind(&data_inizio)
    .bind(&data_fine)
    .fetch_all(pool.inner())
    .await
    .map_err(|e| format!("Errore report per giorno: {}", e))?;

    // Totale complessivo
    let totale: f64 = per_metodo.iter().map(|m| m.totale).sum();
    let numero_transazioni: i32 = per_metodo.iter().map(|m| m.count).sum();

    Ok(ReportPeriodo {
        data_inizio,
        data_fine,
        totale,
        per_metodo,
        per_giorno,
        numero_transazioni,
    })
}

/// Chiudi cassa giornata
#[tauri::command]
pub async fn chiudi_cassa(
    pool: State<'_, SqlitePool>,
    data: String,
    fondo_cassa_finale: f64,
    note: Option<String>,
    operatore_id: Option<String>,
) -> Result<ChiusuraCassa, String> {
    // Verifica che non esista già chiusura per questa data (runtime query for CI)
    let existing: i32 =
        sqlx::query_scalar("SELECT COUNT(*) FROM chiusure_cassa WHERE data_chiusura = ?")
            .bind(&data)
            .fetch_one(pool.inner())
            .await
            .map_err(|e| format!("Errore verifica chiusura: {}", e))?;

    if existing > 0 {
        return Err(format!("Chiusura cassa già effettuata per il {}", data));
    }

    // Calcola totali giornata
    let report = get_incassi_giornata_internal(&pool, &data).await?;

    // Recupera fondo cassa iniziale da impostazioni (runtime query for CI)
    let fondo_iniziale: f64 = sqlx::query_scalar::<_, String>(
        "SELECT valore FROM impostazioni WHERE chiave = 'cassa_fondo_iniziale'",
    )
    .fetch_optional(pool.inner())
    .await
    .map_err(|e| format!("Errore lettura fondo cassa: {}", e))?
    .and_then(|v| v.parse().ok())
    .unwrap_or(100.0);

    // Crea chiusura
    let id = uuid::Uuid::new_v4().to_string();

    sqlx::query(
        r#"
        INSERT INTO chiusure_cassa (
            id, data_chiusura, totale_contanti, totale_carte, totale_satispay,
            totale_bonifici, totale_altro, totale_giornata, numero_transazioni,
            fondo_cassa_iniziale, fondo_cassa_finale, note, operatore_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        "#,
    )
    .bind(&id)
    .bind(&data)
    .bind(report.totale_contanti)
    .bind(report.totale_carte)
    .bind(report.totale_satispay)
    .bind(0.0) // bonifici in totale_altro per ora
    .bind(report.totale_altro)
    .bind(report.totale)
    .bind(report.numero_transazioni)
    .bind(fondo_iniziale)
    .bind(fondo_cassa_finale)
    .bind(&note)
    .bind(&operatore_id)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Errore chiusura cassa: {}", e))?;

    // Fetch and return
    let chiusura = sqlx::query_as::<_, ChiusuraCassa>("SELECT * FROM chiusure_cassa WHERE id = ?")
        .bind(&id)
        .fetch_one(pool.inner())
        .await
        .map_err(|e| format!("Errore lettura chiusura: {}", e))?;

    Ok(chiusura)
}

/// Ottieni storico chiusure cassa
#[tauri::command]
pub async fn get_chiusure_cassa(
    pool: State<'_, SqlitePool>,
    limit: Option<i32>,
) -> Result<Vec<ChiusuraCassa>, String> {
    let limit = limit.unwrap_or(30);

    let chiusure = sqlx::query_as::<_, ChiusuraCassa>(
        r#"
        SELECT * FROM chiusure_cassa
        ORDER BY data_chiusura DESC
        LIMIT ?
        "#,
    )
    .bind(limit)
    .fetch_all(pool.inner())
    .await
    .map_err(|e| format!("Errore lettura chiusure: {}", e))?;

    Ok(chiusure)
}

/// Ottieni metodi di pagamento attivi
#[tauri::command]
pub async fn get_metodi_pagamento(
    pool: State<'_, SqlitePool>,
) -> Result<Vec<MetodoPagamento>, String> {
    let metodi = sqlx::query_as::<_, MetodoPagamento>(
        "SELECT * FROM metodi_pagamento WHERE attivo = 1 ORDER BY ordine",
    )
    .fetch_all(pool.inner())
    .await
    .map_err(|e| format!("Errore lettura metodi pagamento: {}", e))?;

    Ok(metodi)
}

/// Elimina incasso (solo se stesso giorno e cassa non chiusa)
#[tauri::command]
pub async fn elimina_incasso(pool: State<'_, SqlitePool>, id: String) -> Result<(), String> {
    // Verifica che l'incasso sia di oggi
    let incasso = sqlx::query_as::<_, Incasso>("SELECT * FROM incassi WHERE id = ?")
        .bind(&id)
        .fetch_optional(pool.inner())
        .await
        .map_err(|e| format!("Errore lettura incasso: {}", e))?
        .ok_or("Incasso non trovato")?;

    let oggi = chrono::Local::now().format("%Y-%m-%d").to_string();
    let data_incasso = &incasso.data_incasso[..10]; // Prendi solo YYYY-MM-DD

    if data_incasso != oggi {
        return Err("Puoi eliminare solo incassi di oggi".to_string());
    }

    // Verifica che la cassa non sia già chiusa (runtime query for CI)
    let chiusa: i32 =
        sqlx::query_scalar("SELECT COUNT(*) FROM chiusure_cassa WHERE data_chiusura = ?")
            .bind(&oggi)
            .fetch_one(pool.inner())
            .await
            .map_err(|e| format!("Errore verifica chiusura: {}", e))?;

    if chiusa > 0 {
        return Err("Cassa già chiusa per oggi, impossibile eliminare".to_string());
    }

    // Elimina
    sqlx::query("DELETE FROM incassi WHERE id = ?")
        .bind(&id)
        .execute(pool.inner())
        .await
        .map_err(|e| format!("Errore eliminazione: {}", e))?;

    Ok(())
}
