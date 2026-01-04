// ═══════════════════════════════════════════════════════════════════
// FLUXION - Fatturazione Elettronica Commands (Fase 6)
// FatturaPA XML generation, SDI integration, Invoice management
// ═══════════════════════════════════════════════════════════════════

use serde::{Deserialize, Serialize};
use sqlx::SqlitePool;
use tauri::State;

// ───────────────────────────────────────────────────────────────────
// Types
// ───────────────────────────────────────────────────────────────────

#[derive(Debug, Serialize, Deserialize, sqlx::FromRow)]
pub struct ImpostazioniFatturazione {
    pub id: String,
    pub denominazione: String,
    pub partita_iva: String,
    pub codice_fiscale: Option<String>,
    pub regime_fiscale: String,
    pub indirizzo: String,
    pub cap: String,
    pub comune: String,
    pub provincia: String,
    pub nazione: String,
    pub telefono: Option<String>,
    pub email: Option<String>,
    pub pec: Option<String>,
    pub prefisso_numerazione: Option<String>,
    pub ultimo_numero: i32,
    pub anno_corrente: i32,
    pub aliquota_iva_default: f64,
    pub natura_iva_default: Option<String>,
    pub iban: Option<String>,
    pub bic: Option<String>,
    pub nome_banca: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, sqlx::FromRow)]
pub struct Fattura {
    pub id: String,
    pub numero: i32,
    pub anno: i32,
    pub numero_completo: String,
    pub tipo_documento: String,
    pub data_emissione: String,
    pub data_scadenza: Option<String>,
    pub cliente_id: String,
    pub cliente_denominazione: String,
    pub cliente_partita_iva: Option<String>,
    pub cliente_codice_fiscale: Option<String>,
    pub cliente_indirizzo: Option<String>,
    pub cliente_cap: Option<String>,
    pub cliente_comune: Option<String>,
    pub cliente_provincia: Option<String>,
    pub cliente_nazione: String,
    pub cliente_codice_sdi: String,
    pub cliente_pec: Option<String>,
    pub imponibile_totale: f64,
    pub iva_totale: f64,
    pub totale_documento: f64,
    pub ritenuta_tipo: Option<String>,
    pub ritenuta_percentuale: Option<f64>,
    pub ritenuta_importo: Option<f64>,
    pub ritenuta_causale: Option<String>,
    pub bollo_virtuale: i32,
    pub bollo_importo: f64,
    pub modalita_pagamento: String,
    pub condizioni_pagamento: String,
    pub stato: String,
    pub sdi_id_trasmissione: Option<String>,
    pub sdi_data_invio: Option<String>,
    pub sdi_data_risposta: Option<String>,
    pub sdi_esito: Option<String>,
    pub sdi_errori: Option<String>,
    pub xml_filename: Option<String>,
    pub xml_content: Option<String>,
    pub appuntamento_id: Option<String>,
    pub ordine_id: Option<String>,
    pub fattura_origine_id: Option<String>,
    pub causale: Option<String>,
    pub note_interne: Option<String>,
    pub created_at: String,
    pub updated_at: String,
    pub deleted_at: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, sqlx::FromRow)]
pub struct FatturaRiga {
    pub id: String,
    pub fattura_id: String,
    pub numero_linea: i32,
    pub descrizione: String,
    pub codice_articolo: Option<String>,
    pub quantita: f64,
    pub unita_misura: String,
    pub prezzo_unitario: f64,
    pub sconto_percentuale: f64,
    pub sconto_importo: f64,
    pub prezzo_totale: f64,
    pub aliquota_iva: f64,
    pub natura: Option<String>,
    pub servizio_id: Option<String>,
    pub appuntamento_id: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, sqlx::FromRow)]
pub struct FatturaPagamento {
    pub id: String,
    pub fattura_id: String,
    pub data_pagamento: String,
    pub importo: f64,
    pub metodo: String,
    pub iban: Option<String>,
    pub riferimento: Option<String>,
    pub note: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, sqlx::FromRow)]
pub struct CodicePagamento {
    pub codice: String,
    pub descrizione: String,
}

#[derive(Debug, Serialize, Deserialize, sqlx::FromRow)]
pub struct CodiceNaturaIva {
    pub codice: String,
    pub descrizione: String,
    pub riferimento_normativo: Option<String>,
}

// Input per creazione fattura
#[derive(Debug, Deserialize)]
pub struct CreateFatturaInput {
    pub cliente_id: String,
    pub tipo_documento: Option<String>,
    pub data_emissione: String,
    pub data_scadenza: Option<String>,
    pub modalita_pagamento: Option<String>,
    pub condizioni_pagamento: Option<String>,
    pub causale: Option<String>,
    pub note_interne: Option<String>,
    pub appuntamento_id: Option<String>,
    pub fattura_origine_id: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct CreateFatturaRigaInput {
    pub descrizione: String,
    pub codice_articolo: Option<String>,
    pub quantita: f64,
    pub unita_misura: Option<String>,
    pub prezzo_unitario: f64,
    pub sconto_percentuale: Option<f64>,
    pub aliquota_iva: f64,
    pub natura: Option<String>,
    pub servizio_id: Option<String>,
    pub appuntamento_id: Option<String>,
}

// Fattura con righe (per display)
#[derive(Debug, Serialize)]
pub struct FatturaCompleta {
    pub fattura: Fattura,
    pub righe: Vec<FatturaRiga>,
    pub pagamenti: Vec<FatturaPagamento>,
}

// ───────────────────────────────────────────────────────────────────
// Impostazioni Fatturazione
// ───────────────────────────────────────────────────────────────────

#[tauri::command]
pub async fn get_impostazioni_fatturazione(
    pool: State<'_, SqlitePool>,
) -> Result<ImpostazioniFatturazione, String> {
    sqlx::query_as::<_, ImpostazioniFatturazione>(
        "SELECT * FROM impostazioni_fatturazione WHERE id = 'default'",
    )
    .fetch_one(pool.inner())
    .await
    .map_err(|e| format!("Errore caricamento impostazioni: {}", e))
}

#[tauri::command]
pub async fn update_impostazioni_fatturazione(
    pool: State<'_, SqlitePool>,
    denominazione: String,
    partita_iva: String,
    codice_fiscale: Option<String>,
    regime_fiscale: String,
    indirizzo: String,
    cap: String,
    comune: String,
    provincia: String,
    telefono: Option<String>,
    email: Option<String>,
    pec: Option<String>,
    prefisso_numerazione: Option<String>,
    aliquota_iva_default: f64,
    natura_iva_default: Option<String>,
    iban: Option<String>,
    bic: Option<String>,
    nome_banca: Option<String>,
) -> Result<ImpostazioniFatturazione, String> {
    sqlx::query(
        r#"
        UPDATE impostazioni_fatturazione SET
            denominazione = ?,
            partita_iva = ?,
            codice_fiscale = ?,
            regime_fiscale = ?,
            indirizzo = ?,
            cap = ?,
            comune = ?,
            provincia = ?,
            telefono = ?,
            email = ?,
            pec = ?,
            prefisso_numerazione = ?,
            aliquota_iva_default = ?,
            natura_iva_default = ?,
            iban = ?,
            bic = ?,
            nome_banca = ?,
            updated_at = datetime('now')
        WHERE id = 'default'
        "#,
    )
    .bind(&denominazione)
    .bind(&partita_iva)
    .bind(&codice_fiscale)
    .bind(&regime_fiscale)
    .bind(&indirizzo)
    .bind(&cap)
    .bind(&comune)
    .bind(&provincia)
    .bind(&telefono)
    .bind(&email)
    .bind(&pec)
    .bind(&prefisso_numerazione)
    .bind(aliquota_iva_default)
    .bind(&natura_iva_default)
    .bind(&iban)
    .bind(&bic)
    .bind(&nome_banca)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Errore aggiornamento impostazioni: {}", e))?;

    get_impostazioni_fatturazione(pool).await
}

// ───────────────────────────────────────────────────────────────────
// Fatture CRUD
// ───────────────────────────────────────────────────────────────────

#[tauri::command]
pub async fn get_fatture(
    pool: State<'_, SqlitePool>,
    anno: Option<i32>,
    stato: Option<String>,
    cliente_id: Option<String>,
) -> Result<Vec<Fattura>, String> {
    let mut query = String::from(
        "SELECT * FROM fatture WHERE deleted_at IS NULL"
    );

    if let Some(a) = anno {
        query.push_str(&format!(" AND anno = {}", a));
    }
    if let Some(s) = &stato {
        query.push_str(&format!(" AND stato = '{}'", s));
    }
    if let Some(c) = &cliente_id {
        query.push_str(&format!(" AND cliente_id = '{}'", c));
    }

    query.push_str(" ORDER BY anno DESC, numero DESC");

    sqlx::query_as::<_, Fattura>(&query)
        .fetch_all(pool.inner())
        .await
        .map_err(|e| format!("Errore caricamento fatture: {}", e))
}

#[tauri::command]
pub async fn get_fattura(
    pool: State<'_, SqlitePool>,
    fattura_id: String,
) -> Result<FatturaCompleta, String> {
    let fattura = sqlx::query_as::<_, Fattura>(
        "SELECT * FROM fatture WHERE id = ? AND deleted_at IS NULL",
    )
    .bind(&fattura_id)
    .fetch_one(pool.inner())
    .await
    .map_err(|e| format!("Fattura non trovata: {}", e))?;

    let righe = sqlx::query_as::<_, FatturaRiga>(
        "SELECT * FROM fatture_righe WHERE fattura_id = ? ORDER BY numero_linea",
    )
    .bind(&fattura_id)
    .fetch_all(pool.inner())
    .await
    .map_err(|e| format!("Errore caricamento righe: {}", e))?;

    let pagamenti = sqlx::query_as::<_, FatturaPagamento>(
        "SELECT * FROM fatture_pagamenti WHERE fattura_id = ? ORDER BY data_pagamento",
    )
    .bind(&fattura_id)
    .fetch_all(pool.inner())
    .await
    .map_err(|e| format!("Errore caricamento pagamenti: {}", e))?;

    Ok(FatturaCompleta {
        fattura,
        righe,
        pagamenti,
    })
}

#[tauri::command]
pub async fn create_fattura(
    pool: State<'_, SqlitePool>,
    cliente_id: String,
    tipo_documento: Option<String>,
    data_emissione: String,
    data_scadenza: Option<String>,
    modalita_pagamento: Option<String>,
    condizioni_pagamento: Option<String>,
    causale: Option<String>,
    note_interne: Option<String>,
    appuntamento_id: Option<String>,
    fattura_origine_id: Option<String>,
) -> Result<Fattura, String> {
    // Get current year
    let anno: i32 = data_emissione[0..4]
        .parse()
        .map_err(|_| "Data emissione non valida")?;

    // Get and increment numero for this year
    let numero: i32 = sqlx::query_scalar(
        r#"
        INSERT INTO numeratore_fatture (anno, ultimo_numero)
        VALUES (?, 1)
        ON CONFLICT(anno) DO UPDATE SET ultimo_numero = ultimo_numero + 1
        RETURNING ultimo_numero
        "#,
    )
    .bind(anno)
    .fetch_one(pool.inner())
    .await
    .map_err(|e| format!("Errore generazione numero: {}", e))?;

    // Get impostazioni for prefix
    let impostazioni = get_impostazioni_fatturazione(pool.clone()).await?;
    let prefisso = impostazioni.prefisso_numerazione.unwrap_or_default();
    let numero_completo = if prefisso.is_empty() {
        format!("{}/{}", numero, anno)
    } else {
        format!("{}{}/{}", prefisso, numero, anno)
    };

    // Get cliente data for snapshot
    let cliente = sqlx::query_as::<_, ClienteSnapshot>(
        r#"
        SELECT
            nome || ' ' || cognome as denominazione,
            partita_iva,
            codice_fiscale,
            indirizzo,
            cap,
            citta as comune,
            provincia,
            COALESCE(codice_sdi, '0000000') as codice_sdi,
            pec
        FROM clienti WHERE id = ?
        "#,
    )
    .bind(&cliente_id)
    .fetch_one(pool.inner())
    .await
    .map_err(|e| format!("Cliente non trovato: {}", e))?;

    let tipo = tipo_documento.unwrap_or_else(|| "TD01".to_string());
    let mod_pag = modalita_pagamento.unwrap_or_else(|| "MP05".to_string());
    let cond_pag = condizioni_pagamento.unwrap_or_else(|| "TP02".to_string());

    let id = generate_id();

    sqlx::query(
        r#"
        INSERT INTO fatture (
            id, numero, anno, numero_completo, tipo_documento,
            data_emissione, data_scadenza,
            cliente_id, cliente_denominazione, cliente_partita_iva,
            cliente_codice_fiscale, cliente_indirizzo, cliente_cap,
            cliente_comune, cliente_provincia, cliente_codice_sdi, cliente_pec,
            modalita_pagamento, condizioni_pagamento,
            causale, note_interne, appuntamento_id, fattura_origine_id,
            stato
        ) VALUES (
            ?, ?, ?, ?, ?,
            ?, ?,
            ?, ?, ?,
            ?, ?, ?,
            ?, ?, ?, ?,
            ?, ?,
            ?, ?, ?, ?,
            'bozza'
        )
        "#,
    )
    .bind(&id)
    .bind(numero)
    .bind(anno)
    .bind(&numero_completo)
    .bind(&tipo)
    .bind(&data_emissione)
    .bind(&data_scadenza)
    .bind(&cliente_id)
    .bind(&cliente.denominazione)
    .bind(&cliente.partita_iva)
    .bind(&cliente.codice_fiscale)
    .bind(&cliente.indirizzo)
    .bind(&cliente.cap)
    .bind(&cliente.comune)
    .bind(&cliente.provincia)
    .bind(&cliente.codice_sdi)
    .bind(&cliente.pec)
    .bind(&mod_pag)
    .bind(&cond_pag)
    .bind(&causale)
    .bind(&note_interne)
    .bind(&appuntamento_id)
    .bind(&fattura_origine_id)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Errore creazione fattura: {}", e))?;

    sqlx::query_as::<_, Fattura>("SELECT * FROM fatture WHERE id = ?")
        .bind(&id)
        .fetch_one(pool.inner())
        .await
        .map_err(|e| format!("Errore recupero fattura: {}", e))
}

#[derive(Debug, sqlx::FromRow)]
struct ClienteSnapshot {
    denominazione: String,
    partita_iva: Option<String>,
    codice_fiscale: Option<String>,
    indirizzo: Option<String>,
    cap: Option<String>,
    comune: Option<String>,
    provincia: Option<String>,
    codice_sdi: String,
    pec: Option<String>,
}

fn generate_id() -> String {
    use std::time::{SystemTime, UNIX_EPOCH};
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_nanos();
    format!("{:032x}", now)
}

// ───────────────────────────────────────────────────────────────────
// Righe Fattura
// ───────────────────────────────────────────────────────────────────

#[tauri::command]
pub async fn add_riga_fattura(
    pool: State<'_, SqlitePool>,
    fattura_id: String,
    descrizione: String,
    codice_articolo: Option<String>,
    quantita: f64,
    unita_misura: Option<String>,
    prezzo_unitario: f64,
    sconto_percentuale: Option<f64>,
    aliquota_iva: f64,
    natura: Option<String>,
    servizio_id: Option<String>,
    appuntamento_id: Option<String>,
) -> Result<FatturaRiga, String> {
    // Get next line number
    let numero_linea: i32 = sqlx::query_scalar(
        "SELECT COALESCE(MAX(numero_linea), 0) + 1 FROM fatture_righe WHERE fattura_id = ?",
    )
    .bind(&fattura_id)
    .fetch_one(pool.inner())
    .await
    .map_err(|e| format!("Errore: {}", e))?;

    let sconto_pct = sconto_percentuale.unwrap_or(0.0);
    let sconto_importo = prezzo_unitario * quantita * sconto_pct / 100.0;
    let prezzo_totale = prezzo_unitario * quantita - sconto_importo;
    let um = unita_misura.unwrap_or_else(|| "PZ".to_string());

    let id = generate_id();

    sqlx::query(
        r#"
        INSERT INTO fatture_righe (
            id, fattura_id, numero_linea, descrizione, codice_articolo,
            quantita, unita_misura, prezzo_unitario,
            sconto_percentuale, sconto_importo, prezzo_totale,
            aliquota_iva, natura, servizio_id, appuntamento_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        "#,
    )
    .bind(&id)
    .bind(&fattura_id)
    .bind(numero_linea)
    .bind(&descrizione)
    .bind(&codice_articolo)
    .bind(quantita)
    .bind(&um)
    .bind(prezzo_unitario)
    .bind(sconto_pct)
    .bind(sconto_importo)
    .bind(prezzo_totale)
    .bind(aliquota_iva)
    .bind(&natura)
    .bind(&servizio_id)
    .bind(&appuntamento_id)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Errore aggiunta riga: {}", e))?;

    // Update fattura totals
    update_fattura_totals(pool.clone(), &fattura_id).await?;

    sqlx::query_as::<_, FatturaRiga>("SELECT * FROM fatture_righe WHERE id = ?")
        .bind(&id)
        .fetch_one(pool.inner())
        .await
        .map_err(|e| format!("Errore recupero riga: {}", e))
}

#[tauri::command]
pub async fn delete_riga_fattura(
    pool: State<'_, SqlitePool>,
    riga_id: String,
) -> Result<bool, String> {
    // Get fattura_id before deleting
    let fattura_id: String = sqlx::query_scalar(
        "SELECT fattura_id FROM fatture_righe WHERE id = ?",
    )
    .bind(&riga_id)
    .fetch_one(pool.inner())
    .await
    .map_err(|e| format!("Riga non trovata: {}", e))?;

    sqlx::query("DELETE FROM fatture_righe WHERE id = ?")
        .bind(&riga_id)
        .execute(pool.inner())
        .await
        .map_err(|e| format!("Errore eliminazione riga: {}", e))?;

    // Re-number remaining lines
    sqlx::query(
        r#"
        UPDATE fatture_righe
        SET numero_linea = (
            SELECT COUNT(*) FROM fatture_righe r2
            WHERE r2.fattura_id = fatture_righe.fattura_id
            AND r2.created_at <= fatture_righe.created_at
        )
        WHERE fattura_id = ?
        "#,
    )
    .bind(&fattura_id)
    .execute(pool.inner())
    .await
    .ok();

    // Update fattura totals
    update_fattura_totals(pool, &fattura_id).await?;

    Ok(true)
}

async fn update_fattura_totals(
    pool: State<'_, SqlitePool>,
    fattura_id: &str,
) -> Result<(), String> {
    // Get impostazioni to check regime
    let impostazioni = get_impostazioni_fatturazione(pool.clone()).await?;
    let is_forfettario = impostazioni.regime_fiscale == "RF19";

    // Calculate totals from righe
    let (imponibile, iva): (f64, f64) = if is_forfettario {
        // Forfettario: no IVA
        let imp: f64 = sqlx::query_scalar(
            "SELECT COALESCE(SUM(prezzo_totale), 0) FROM fatture_righe WHERE fattura_id = ?",
        )
        .bind(fattura_id)
        .fetch_one(pool.inner())
        .await
        .map_err(|e| format!("Errore calcolo totale: {}", e))?;
        (imp, 0.0)
    } else {
        // Regime ordinario: calcola IVA
        let imp: f64 = sqlx::query_scalar(
            "SELECT COALESCE(SUM(prezzo_totale), 0) FROM fatture_righe WHERE fattura_id = ?",
        )
        .bind(fattura_id)
        .fetch_one(pool.inner())
        .await
        .map_err(|e| format!("Errore calcolo imponibile: {}", e))?;

        let iva_tot: f64 = sqlx::query_scalar(
            r#"
            SELECT COALESCE(SUM(prezzo_totale * aliquota_iva / 100), 0)
            FROM fatture_righe
            WHERE fattura_id = ? AND natura IS NULL
            "#,
        )
        .bind(fattura_id)
        .fetch_one(pool.inner())
        .await
        .map_err(|e| format!("Errore calcolo IVA: {}", e))?;

        (imp, iva_tot)
    };

    let totale = imponibile + iva;

    // Check if bollo is needed (esente IVA > 77.47€)
    let bollo = if is_forfettario && imponibile > 77.47 { 1 } else { 0 };

    sqlx::query(
        r#"
        UPDATE fatture SET
            imponibile_totale = ?,
            iva_totale = ?,
            totale_documento = ?,
            bollo_virtuale = ?,
            updated_at = datetime('now')
        WHERE id = ?
        "#,
    )
    .bind(imponibile)
    .bind(iva)
    .bind(totale)
    .bind(bollo)
    .bind(fattura_id)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Errore aggiornamento totali: {}", e))?;

    Ok(())
}

// ───────────────────────────────────────────────────────────────────
// Stato Fattura
// ───────────────────────────────────────────────────────────────────

#[tauri::command]
pub async fn emetti_fattura(
    pool: State<'_, SqlitePool>,
    fattura_id: String,
) -> Result<Fattura, String> {
    // Check fattura exists and is in bozza state
    let fattura = sqlx::query_as::<_, Fattura>(
        "SELECT * FROM fatture WHERE id = ? AND deleted_at IS NULL",
    )
    .bind(&fattura_id)
    .fetch_one(pool.inner())
    .await
    .map_err(|e| format!("Fattura non trovata: {}", e))?;

    if fattura.stato != "bozza" {
        return Err("Solo le fatture in bozza possono essere emesse".to_string());
    }

    // Check has at least one line
    let count: i32 = sqlx::query_scalar(
        "SELECT COUNT(*) FROM fatture_righe WHERE fattura_id = ?",
    )
    .bind(&fattura_id)
    .fetch_one(pool.inner())
    .await
    .map_err(|e| format!("Errore: {}", e))?;

    if count == 0 {
        return Err("La fattura deve avere almeno una riga".to_string());
    }

    // Generate XML
    let xml = generate_fattura_xml(pool.clone(), &fattura_id).await?;

    // Get impostazioni for filename
    let impostazioni = get_impostazioni_fatturazione(pool.clone()).await?;
    let filename = format!(
        "IT{}_{:05}.xml",
        impostazioni.partita_iva, fattura.numero
    );

    // Update fattura
    sqlx::query(
        r#"
        UPDATE fatture SET
            stato = 'emessa',
            xml_filename = ?,
            xml_content = ?,
            updated_at = datetime('now')
        WHERE id = ?
        "#,
    )
    .bind(&filename)
    .bind(&xml)
    .bind(&fattura_id)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Errore emissione fattura: {}", e))?;

    sqlx::query_as::<_, Fattura>("SELECT * FROM fatture WHERE id = ?")
        .bind(&fattura_id)
        .fetch_one(pool.inner())
        .await
        .map_err(|e| format!("Errore recupero fattura: {}", e))
}

#[tauri::command]
pub async fn annulla_fattura(
    pool: State<'_, SqlitePool>,
    fattura_id: String,
    motivo: Option<String>,
) -> Result<Fattura, String> {
    let fattura = sqlx::query_as::<_, Fattura>(
        "SELECT * FROM fatture WHERE id = ? AND deleted_at IS NULL",
    )
    .bind(&fattura_id)
    .fetch_one(pool.inner())
    .await
    .map_err(|e| format!("Fattura non trovata: {}", e))?;

    if fattura.stato == "pagata" {
        return Err("Non puoi annullare una fattura già pagata".to_string());
    }

    let note = format!(
        "{}\n[ANNULLATA: {}]",
        fattura.note_interne.unwrap_or_default(),
        motivo.unwrap_or_else(|| "Motivo non specificato".to_string())
    );

    sqlx::query(
        r#"
        UPDATE fatture SET
            stato = 'annullata',
            note_interne = ?,
            updated_at = datetime('now')
        WHERE id = ?
        "#,
    )
    .bind(&note)
    .bind(&fattura_id)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Errore annullamento: {}", e))?;

    sqlx::query_as::<_, Fattura>("SELECT * FROM fatture WHERE id = ?")
        .bind(&fattura_id)
        .fetch_one(pool.inner())
        .await
        .map_err(|e| format!("Errore recupero fattura: {}", e))
}

#[tauri::command]
pub async fn delete_fattura(
    pool: State<'_, SqlitePool>,
    fattura_id: String,
) -> Result<bool, String> {
    let fattura = sqlx::query_as::<_, Fattura>(
        "SELECT * FROM fatture WHERE id = ? AND deleted_at IS NULL",
    )
    .bind(&fattura_id)
    .fetch_one(pool.inner())
    .await
    .map_err(|e| format!("Fattura non trovata: {}", e))?;

    if fattura.stato != "bozza" {
        return Err("Solo le fatture in bozza possono essere eliminate".to_string());
    }

    sqlx::query("UPDATE fatture SET deleted_at = datetime('now') WHERE id = ?")
        .bind(&fattura_id)
        .execute(pool.inner())
        .await
        .map_err(|e| format!("Errore eliminazione: {}", e))?;

    Ok(true)
}

// ───────────────────────────────────────────────────────────────────
// Pagamenti
// ───────────────────────────────────────────────────────────────────

#[tauri::command]
pub async fn registra_pagamento(
    pool: State<'_, SqlitePool>,
    fattura_id: String,
    data_pagamento: String,
    importo: f64,
    metodo: String,
    iban: Option<String>,
    riferimento: Option<String>,
    note: Option<String>,
) -> Result<FatturaPagamento, String> {
    let id = generate_id();

    sqlx::query(
        r#"
        INSERT INTO fatture_pagamenti (
            id, fattura_id, data_pagamento, importo, metodo, iban, riferimento, note
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        "#,
    )
    .bind(&id)
    .bind(&fattura_id)
    .bind(&data_pagamento)
    .bind(importo)
    .bind(&metodo)
    .bind(&iban)
    .bind(&riferimento)
    .bind(&note)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Errore registrazione pagamento: {}", e))?;

    // Check if fully paid
    let totale_documento: f64 = sqlx::query_scalar(
        "SELECT totale_documento FROM fatture WHERE id = ?",
    )
    .bind(&fattura_id)
    .fetch_one(pool.inner())
    .await
    .map_err(|e| format!("Errore: {}", e))?;

    let totale_pagato: f64 = sqlx::query_scalar(
        "SELECT COALESCE(SUM(importo), 0) FROM fatture_pagamenti WHERE fattura_id = ?",
    )
    .bind(&fattura_id)
    .fetch_one(pool.inner())
    .await
    .map_err(|e| format!("Errore: {}", e))?;

    if totale_pagato >= totale_documento {
        sqlx::query("UPDATE fatture SET stato = 'pagata', updated_at = datetime('now') WHERE id = ?")
            .bind(&fattura_id)
            .execute(pool.inner())
            .await
            .ok();
    }

    sqlx::query_as::<_, FatturaPagamento>("SELECT * FROM fatture_pagamenti WHERE id = ?")
        .bind(&id)
        .fetch_one(pool.inner())
        .await
        .map_err(|e| format!("Errore recupero pagamento: {}", e))
}

// ───────────────────────────────────────────────────────────────────
// Codici Lookup
// ───────────────────────────────────────────────────────────────────

#[tauri::command]
pub async fn get_codici_pagamento(
    pool: State<'_, SqlitePool>,
) -> Result<Vec<CodicePagamento>, String> {
    sqlx::query_as::<_, CodicePagamento>("SELECT * FROM codici_pagamento ORDER BY codice")
        .fetch_all(pool.inner())
        .await
        .map_err(|e| format!("Errore: {}", e))
}

#[tauri::command]
pub async fn get_codici_natura_iva(
    pool: State<'_, SqlitePool>,
) -> Result<Vec<CodiceNaturaIva>, String> {
    sqlx::query_as::<_, CodiceNaturaIva>("SELECT * FROM codici_natura_iva ORDER BY codice")
        .fetch_all(pool.inner())
        .await
        .map_err(|e| format!("Errore: {}", e))
}

// ───────────────────────────────────────────────────────────────────
// XML Generation (FatturaPA 1.2.2)
// ───────────────────────────────────────────────────────────────────

async fn generate_fattura_xml(
    pool: State<'_, SqlitePool>,
    fattura_id: &str,
) -> Result<String, String> {
    let fattura_completa = get_fattura(pool.clone(), fattura_id.to_string()).await?;
    let fattura = fattura_completa.fattura;
    let righe = fattura_completa.righe;

    let impostazioni = get_impostazioni_fatturazione(pool.clone()).await?;
    let is_forfettario = impostazioni.regime_fiscale == "RF19";

    // Build XML
    let mut xml = String::from(r#"<?xml version="1.0" encoding="UTF-8"?>
<p:FatturaElettronica versione="FPR12" xmlns:ds="http://www.w3.org/2000/09/xmldsig#" xmlns:p="http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2 http://www.fatturapa.gov.it/export/fatturazione/sdi/fatturapa/v1.2.2/Schema_del_file_xml_FatturaPA_v1.2.2.xsd">
  <FatturaElettronicaHeader>
    <DatiTrasmissione>
      <IdTrasmittente>
        <IdPaese>IT</IdPaese>
        <IdCodice>"#);
    xml.push_str(&impostazioni.partita_iva);
    xml.push_str(r#"</IdCodice>
      </IdTrasmittente>
      <ProgressivoInvio>"#);
    xml.push_str(&format!("{:05}", fattura.numero));
    xml.push_str(r#"</ProgressivoInvio>
      <FormatoTrasmissione>FPR12</FormatoTrasmissione>
      <CodiceDestinatario>"#);
    xml.push_str(&fattura.cliente_codice_sdi);
    xml.push_str(r#"</CodiceDestinatario>"#);

    // PEC if codice SDI is 0000000
    if fattura.cliente_codice_sdi == "0000000" {
        if let Some(ref pec) = fattura.cliente_pec {
            xml.push_str("\n      <PECDestinatario>");
            xml.push_str(pec);
            xml.push_str("</PECDestinatario>");
        }
    }

    xml.push_str(r#"
    </DatiTrasmissione>
    <CedentePrestatore>
      <DatiAnagrafici>
        <IdFiscaleIVA>
          <IdPaese>IT</IdPaese>
          <IdCodice>"#);
    xml.push_str(&impostazioni.partita_iva);
    xml.push_str(r#"</IdCodice>
        </IdFiscaleIVA>"#);

    if let Some(ref cf) = impostazioni.codice_fiscale {
        xml.push_str("\n        <CodiceFiscale>");
        xml.push_str(cf);
        xml.push_str("</CodiceFiscale>");
    }

    xml.push_str(r#"
        <Anagrafica>
          <Denominazione>"#);
    xml.push_str(&escape_xml(&impostazioni.denominazione));
    xml.push_str(r#"</Denominazione>
        </Anagrafica>
        <RegimeFiscale>"#);
    xml.push_str(&impostazioni.regime_fiscale);
    xml.push_str(r#"</RegimeFiscale>
      </DatiAnagrafici>
      <Sede>
        <Indirizzo>"#);
    xml.push_str(&escape_xml(&impostazioni.indirizzo));
    xml.push_str(r#"</Indirizzo>
        <CAP>"#);
    xml.push_str(&impostazioni.cap);
    xml.push_str(r#"</CAP>
        <Comune>"#);
    xml.push_str(&escape_xml(&impostazioni.comune));
    xml.push_str(r#"</Comune>
        <Provincia>"#);
    xml.push_str(&impostazioni.provincia);
    xml.push_str(r#"</Provincia>
        <Nazione>"#);
    xml.push_str(&impostazioni.nazione);
    xml.push_str(r#"</Nazione>
      </Sede>
    </CedentePrestatore>
    <CessionarioCommittente>
      <DatiAnagrafici>"#);

    // Cliente fiscal data
    if let Some(ref piva) = fattura.cliente_partita_iva {
        if !piva.is_empty() {
            xml.push_str(r#"
        <IdFiscaleIVA>
          <IdPaese>IT</IdPaese>
          <IdCodice>"#);
            xml.push_str(piva);
            xml.push_str(r#"</IdCodice>
        </IdFiscaleIVA>"#);
        }
    }

    if let Some(ref cf) = fattura.cliente_codice_fiscale {
        if !cf.is_empty() {
            xml.push_str("\n        <CodiceFiscale>");
            xml.push_str(cf);
            xml.push_str("</CodiceFiscale>");
        }
    }

    xml.push_str(r#"
        <Anagrafica>
          <Denominazione>"#);
    xml.push_str(&escape_xml(&fattura.cliente_denominazione));
    xml.push_str(r#"</Denominazione>
        </Anagrafica>
      </DatiAnagrafici>
      <Sede>
        <Indirizzo>"#);
    xml.push_str(&escape_xml(&fattura.cliente_indirizzo.unwrap_or_else(|| "N/D".to_string())));
    xml.push_str(r#"</Indirizzo>
        <CAP>"#);
    xml.push_str(&fattura.cliente_cap.unwrap_or_else(|| "00000".to_string()));
    xml.push_str(r#"</CAP>
        <Comune>"#);
    xml.push_str(&escape_xml(&fattura.cliente_comune.unwrap_or_else(|| "N/D".to_string())));
    xml.push_str(r#"</Comune>"#);

    if let Some(ref prov) = fattura.cliente_provincia {
        if !prov.is_empty() {
            xml.push_str("\n        <Provincia>");
            xml.push_str(prov);
            xml.push_str("</Provincia>");
        }
    }

    xml.push_str(r#"
        <Nazione>"#);
    xml.push_str(&fattura.cliente_nazione);
    xml.push_str(r#"</Nazione>
      </Sede>
    </CessionarioCommittente>
  </FatturaElettronicaHeader>
  <FatturaElettronicaBody>
    <DatiGenerali>
      <DatiGeneraliDocumento>
        <TipoDocumento>"#);
    xml.push_str(&fattura.tipo_documento);
    xml.push_str(r#"</TipoDocumento>
        <Divisa>EUR</Divisa>
        <Data>"#);
    xml.push_str(&fattura.data_emissione);
    xml.push_str(r#"</Data>
        <Numero>"#);
    xml.push_str(&fattura.numero_completo);
    xml.push_str(r#"</Numero>"#);

    // Bollo virtuale
    if fattura.bollo_virtuale == 1 {
        xml.push_str(r#"
        <DatiBollo>
          <BolloVirtuale>SI</BolloVirtuale>
          <ImportoBollo>"#);
        xml.push_str(&format!("{:.2}", fattura.bollo_importo));
        xml.push_str(r#"</ImportoBollo>
        </DatiBollo>"#);
    }

    // Causale (max 200 char per block)
    if let Some(ref causale) = fattura.causale {
        for chunk in causale.as_bytes().chunks(200) {
            xml.push_str("\n        <Causale>");
            xml.push_str(&escape_xml(&String::from_utf8_lossy(chunk)));
            xml.push_str("</Causale>");
        }
    }

    // Dicitura forfettario
    if is_forfettario {
        xml.push_str(r#"
        <Causale>Operazione effettuata ai sensi dell'articolo 1, commi da 54 a 89, della Legge n. 190/2014 - Regime forfettario. Operazione senza applicazione dell'IVA.</Causale>"#);
    }

    xml.push_str(r#"
      </DatiGeneraliDocumento>
    </DatiGenerali>
    <DatiBeniServizi>"#);

    // Righe dettaglio
    for riga in &righe {
        xml.push_str(r#"
      <DettaglioLinee>
        <NumeroLinea>"#);
        xml.push_str(&riga.numero_linea.to_string());
        xml.push_str(r#"</NumeroLinea>
        <Descrizione>"#);
        xml.push_str(&escape_xml(&riga.descrizione));
        xml.push_str(r#"</Descrizione>
        <Quantita>"#);
        xml.push_str(&format!("{:.2}", riga.quantita));
        xml.push_str(r#"</Quantita>
        <UnitaMisura>"#);
        xml.push_str(&riga.unita_misura);
        xml.push_str(r#"</UnitaMisura>
        <PrezzoUnitario>"#);
        xml.push_str(&format!("{:.2}", riga.prezzo_unitario));
        xml.push_str("</PrezzoUnitario>");

        if riga.sconto_percentuale > 0.0 {
            xml.push_str(r#"
        <ScontoMaggiorazione>
          <Tipo>SC</Tipo>
          <Percentuale>"#);
            xml.push_str(&format!("{:.2}", riga.sconto_percentuale));
            xml.push_str(r#"</Percentuale>
        </ScontoMaggiorazione>"#);
        }

        xml.push_str(r#"
        <PrezzoTotale>"#);
        xml.push_str(&format!("{:.2}", riga.prezzo_totale));
        xml.push_str(r#"</PrezzoTotale>
        <AliquotaIVA>"#);
        xml.push_str(&format!("{:.2}", riga.aliquota_iva));
        xml.push_str("</AliquotaIVA>");

        if let Some(ref natura) = riga.natura {
            xml.push_str("\n        <Natura>");
            xml.push_str(natura);
            xml.push_str("</Natura>");
        }

        xml.push_str(r#"
      </DettaglioLinee>"#);
    }

    // Riepilogo IVA
    xml.push_str(r#"
      <DatiRiepilogo>
        <AliquotaIVA>"#);

    if is_forfettario {
        xml.push_str("0.00</AliquotaIVA>\n        <Natura>");
        xml.push_str(&impostazioni.natura_iva_default.unwrap_or_else(|| "N2.2".to_string()));
        xml.push_str("</Natura>");
    } else {
        xml.push_str(&format!("{:.2}", impostazioni.aliquota_iva_default));
        xml.push_str("</AliquotaIVA>");
    }

    xml.push_str(r#"
        <ImponibileImporto>"#);
    xml.push_str(&format!("{:.2}", fattura.imponibile_totale));
    xml.push_str(r#"</ImponibileImporto>
        <Imposta>"#);
    xml.push_str(&format!("{:.2}", fattura.iva_totale));
    xml.push_str(r#"</Imposta>
        <EssigibilitaIVA>I</EsigibilitaIVA>"#);

    if is_forfettario {
        xml.push_str(r#"
        <RiferimentoNormativo>Art.1 commi 54-89 L.190/2014 - Regime forfettario</RiferimentoNormativo>"#);
    }

    xml.push_str(r#"
      </DatiRiepilogo>
    </DatiBeniServizi>
    <DatiPagamento>
      <CondizioniPagamento>"#);
    xml.push_str(&fattura.condizioni_pagamento);
    xml.push_str(r#"</CondizioniPagamento>
      <DettaglioPagamento>
        <ModalitaPagamento>"#);
    xml.push_str(&fattura.modalita_pagamento);
    xml.push_str(r#"</ModalitaPagamento>
        <ImportoPagamento>"#);
    xml.push_str(&format!("{:.2}", fattura.totale_documento));
    xml.push_str("</ImportoPagamento>");

    if let Some(ref scad) = fattura.data_scadenza {
        xml.push_str("\n        <DataScadenzaPagamento>");
        xml.push_str(scad);
        xml.push_str("</DataScadenzaPagamento>");
    }

    if let Some(ref iban) = impostazioni.iban {
        xml.push_str("\n        <IBAN>");
        xml.push_str(iban);
        xml.push_str("</IBAN>");
    }

    xml.push_str(r#"
      </DettaglioPagamento>
    </DatiPagamento>
  </FatturaElettronicaBody>
</p:FatturaElettronica>"#);

    Ok(xml)
}

fn escape_xml(s: &str) -> String {
    s.replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
        .replace('"', "&quot;")
        .replace('\'', "&apos;")
}

// ───────────────────────────────────────────────────────────────────
// Download XML
// ───────────────────────────────────────────────────────────────────

#[tauri::command]
pub async fn get_fattura_xml(
    pool: State<'_, SqlitePool>,
    fattura_id: String,
) -> Result<String, String> {
    let fattura = sqlx::query_as::<_, Fattura>(
        "SELECT * FROM fatture WHERE id = ? AND deleted_at IS NULL",
    )
    .bind(&fattura_id)
    .fetch_one(pool.inner())
    .await
    .map_err(|e| format!("Fattura non trovata: {}", e))?;

    fattura.xml_content.ok_or_else(|| "XML non ancora generato".to_string())
}
