// ═══════════════════════════════════════════════════════════════════
// FLUXION - Schede Cliente Commands
// CRUD operations per schede verticali specifiche per settore
// ═══════════════════════════════════════════════════════════════════

use serde::{Deserialize, Serialize};
use sqlx::SqlitePool;
use tauri::State;

// ═══════════════════════════════════════════════════════════════════
// TYPES - Scheda Odontoiatrica
// ═══════════════════════════════════════════════════════════════════

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SchedaOdontoiatrica {
    pub id: Option<String>,
    pub cliente_id: String,
    pub odontogramma: serde_json::Value,
    pub prima_visita: Option<String>,
    pub ultima_visita: Option<String>,
    pub frequenza_controlli: Option<String>,
    pub spazzolino: Option<String>,
    pub filo_interdentale: bool,
    pub collutorio: bool,
    pub allergia_lattice: bool,
    pub allergia_anestesia: bool,
    pub allergie_altre: Option<String>,
    pub ortodonzia_in_corso: bool,
    pub tipo_apparecchio: Option<String>,
    pub data_inizio_ortodonzia: Option<String>,
    pub trattamenti: serde_json::Value,
    pub note_cliniche: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct SchedaOdontoiatricaRow {
    pub id: String,
    pub cliente_id: String,
    pub odontogramma: String,
    pub prima_visita: Option<String>,
    pub ultima_visita: Option<String>,
    pub frequenza_controlli: Option<String>,
    pub spazzolino: Option<String>,
    pub filo_interdentale: i32,
    pub collutorio: i32,
    pub allergia_lattice: i32,
    pub allergia_anestesia: i32,
    pub allergie_altre: Option<String>,
    pub ortodonzia_in_corso: i32,
    pub tipo_apparecchio: Option<String>,
    pub data_inizio_ortodonzia: Option<String>,
    pub trattamenti: String,
    pub note_cliniche: Option<String>,
}

// ═══════════════════════════════════════════════════════════════════
// TYPES - Scheda Fisioterapia
// ═══════════════════════════════════════════════════════════════════

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SchedaFisioterapia {
    pub id: Option<String>,
    pub cliente_id: String,
    pub motivo_primo_accesso: Option<String>,
    pub data_inizio_terapia: Option<String>,
    pub data_fine_terapia: Option<String>,
    pub diagnosi_medica: Option<String>,
    pub diagnosi_fisioterapica: Option<String>,
    pub zona_principale: Option<String>,
    pub zone_secondarie: serde_json::Value,
    pub valutazione_iniziale: serde_json::Value,
    pub scale_valutazione: serde_json::Value,
    pub numero_sedute_prescritte: Option<i32>,
    pub frequenza_settimanale: Option<String>,
    pub sedute_effettuate: serde_json::Value,
    pub esito_trattamento: Option<String>,
    pub controindicazioni: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct SchedaFisioterapiaRow {
    pub id: String,
    pub cliente_id: String,
    pub motivo_primo_accesso: Option<String>,
    pub data_inizio_terapia: Option<String>,
    pub data_fine_terapia: Option<String>,
    pub diagnosi_medica: Option<String>,
    pub diagnosi_fisioterapica: Option<String>,
    pub zona_principale: Option<String>,
    pub zone_secondarie: String,
    pub valutazione_iniziale: String,
    pub scale_valutazione: String,
    pub numero_sedute_prescritte: Option<i32>,
    pub frequenza_settimanale: Option<String>,
    pub sedute_effettuate: String,
    pub esito_trattamento: Option<String>,
    pub controindicazioni: Option<String>,
}

// ═══════════════════════════════════════════════════════════════════
// TYPES - Scheda Estetica
// ═══════════════════════════════════════════════════════════════════

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SchedaEstetica {
    pub id: Option<String>,
    pub cliente_id: String,
    pub fototipo: Option<i32>,
    pub tipo_pelle: Option<String>,
    pub allergie_prodotti: serde_json::Value,
    pub allergie_profumi: bool,
    pub allergie_henne: bool,
    pub trattamenti_precedenti: serde_json::Value,
    pub ultima_depilazione: Option<String>,
    pub metodo_depilazione: Option<String>,
    pub unghie_naturali: bool,
    pub problematiche_unghie: Option<String>,
    pub problematiche_viso: serde_json::Value,
    pub routine_skincare: Option<String>,
    pub peso_attuale: Option<f64>,
    pub obiettivo: Option<String>,
    pub gravidanza: bool,
    pub allattamento: bool,
    pub patologie_attive: serde_json::Value,
    pub note_trattamenti: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct SchedaEsteticaRow {
    pub id: String,
    pub cliente_id: String,
    pub fototipo: Option<i32>,
    pub tipo_pelle: Option<String>,
    pub allergie_prodotti: String,
    pub allergie_profumi: i32,
    pub allergie_henne: i32,
    pub trattamenti_precedenti: String,
    pub ultima_depilazione: Option<String>,
    pub metodo_depilazione: Option<String>,
    pub unghie_naturali: i32,
    pub problematiche_unghie: Option<String>,
    pub problematiche_viso: String,
    pub routine_skincare: Option<String>,
    pub peso_attuale: Option<f64>,
    pub obiettivo: Option<String>,
    pub gravidanza: i32,
    pub allattamento: i32,
    pub patologie_attive: String,
    pub note_trattamenti: Option<String>,
}

// ═══════════════════════════════════════════════════════════════════
// TYPES - Scheda Parrucchiere
// ═══════════════════════════════════════════════════════════════════

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SchedaParrucchiere {
    pub id: Option<String>,
    pub cliente_id: String,
    pub tipo_capello: Option<String>,
    pub porosita: Option<String>,
    pub lunghezza_attuale: Option<String>,
    pub base_naturale: Option<String>,
    pub colore_attuale: Option<String>,
    pub colorazioni_precedenti: serde_json::Value,
    pub decolorazioni: i32,
    pub permanente: i32,
    pub stirature_chimiche: i32,
    pub allergia_tinta: bool,
    pub allergia_ammoniaca: bool,
    pub test_pelle_eseguito: bool,
    pub data_test_pelle: Option<String>,
    pub servizi_abituali: serde_json::Value,
    pub frequenza_taglio: Option<String>,
    pub frequenza_colore: Option<String>,
    pub prodotti_casa: serde_json::Value,
    pub preferenze_colore: Option<String>,
    pub non_vuole: serde_json::Value,
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct SchedaParrucchiereRow {
    pub id: String,
    pub cliente_id: String,
    pub tipo_capello: Option<String>,
    pub porosita: Option<String>,
    pub lunghezza_attuale: Option<String>,
    pub base_naturale: Option<String>,
    pub colore_attuale: Option<String>,
    pub colorazioni_precedenti: String,
    pub decolorazioni: i32,
    pub permanente: i32,
    pub stirature_chimiche: i32,
    pub allergia_tinta: i32,
    pub allergia_ammoniaca: i32,
    pub test_pelle_eseguito: i32,
    pub data_test_pelle: Option<String>,
    pub servizi_abituali: String,
    pub frequenza_taglio: Option<String>,
    pub frequenza_colore: Option<String>,
    pub prodotti_casa: String,
    pub preferenze_colore: Option<String>,
    pub non_vuole: String,
}

// ═══════════════════════════════════════════════════════════════════
// TYPES - Scheda Veicoli
// ═══════════════════════════════════════════════════════════════════

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SchedaVeicoli {
    pub id: Option<String>,
    pub cliente_id: String,
    pub targa: String,
    pub marca: Option<String>,
    pub modello: Option<String>,
    pub anno: Option<i32>,
    pub alimentazione: Option<String>,
    pub cilindrata: Option<String>,
    pub kw: Option<i32>,
    pub telaio: Option<String>,
    pub ultima_revisione: Option<String>,
    pub scadenza_revisione: Option<String>,
    pub km_attuali: Option<i32>,
    pub km_ultimo_tagliando: Option<i32>,
    pub misura_gomme: Option<String>,
    pub tipo_gomme: Option<String>,
    pub preferenza_ricambi: Option<String>,
    pub note_veicolo: Option<String>,
    pub interventi: serde_json::Value,
    pub is_default: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct SchedaVeicoliRow {
    pub id: String,
    pub cliente_id: String,
    pub targa: String,
    pub marca: Option<String>,
    pub modello: Option<String>,
    pub anno: Option<i32>,
    pub alimentazione: Option<String>,
    pub cilindrata: Option<String>,
    pub kw: Option<i32>,
    pub telaio: Option<String>,
    pub ultima_revisione: Option<String>,
    pub scadenza_revisione: Option<String>,
    pub km_attuali: Option<i32>,
    pub km_ultimo_tagliando: Option<i32>,
    pub misura_gomme: Option<String>,
    pub tipo_gomme: Option<String>,
    pub preferenza_ricambi: Option<String>,
    pub note_veicolo: Option<String>,
    pub interventi: String,
    pub is_default: i32,
}

// ═══════════════════════════════════════════════════════════════════
// TYPES - Scheda Carrozzeria
// ═══════════════════════════════════════════════════════════════════

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SchedaCarrozzeria {
    pub id: Option<String>,
    pub cliente_id: String,
    pub veicolo_id: Option<String>,
    pub tipo_danno: Option<String>,
    pub posizione_danno: Option<String>,
    pub entita_danno: Option<String>,
    pub descrizione_danno: Option<String>,
    pub foto_pre: serde_json::Value,
    pub foto_post: serde_json::Value,
    pub preventivo_numero: Option<String>,
    pub importo_preventivo: Option<f64>,
    pub approvato: bool,
    pub data_ingresso: Option<String>,
    pub data_consegna_prevista: Option<String>,
    pub data_consegna_effettiva: Option<String>,
    pub lavorazioni: serde_json::Value,
    pub verniciatura: bool,
    pub codice_colore: Option<String>,
    pub sinistro_assicurativo: bool,
    pub compagnia: Option<String>,
    pub numero_sinistro: Option<String>,
    pub stato: String,
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct SchedaCarrozzeriaRow {
    pub id: String,
    pub cliente_id: String,
    pub veicolo_id: Option<String>,
    pub tipo_danno: Option<String>,
    pub posizione_danno: Option<String>,
    pub entita_danno: Option<String>,
    pub descrizione_danno: Option<String>,
    pub foto_pre: String,
    pub foto_post: String,
    pub preventivo_numero: Option<String>,
    pub importo_preventivo: Option<f64>,
    pub approvato: i32,
    pub data_ingresso: Option<String>,
    pub data_consegna_prevista: Option<String>,
    pub data_consegna_effettiva: Option<String>,
    pub lavorazioni: String,
    pub verniciatura: i32,
    pub codice_colore: Option<String>,
    pub sinistro_assicurativo: i32,
    pub compagnia: Option<String>,
    pub numero_sinistro: Option<String>,
    pub stato: String,
}

// ═══════════════════════════════════════════════════════════════════
// COMMANDS - Scheda Odontoiatrica
// ═══════════════════════════════════════════════════════════════════

#[tauri::command]
pub async fn get_scheda_odontoiatrica(
    pool: State<'_, SqlitePool>,
    cliente_id: String,
) -> Result<Option<SchedaOdontoiatrica>, String> {
    let row: Option<SchedaOdontoiatricaRow> = sqlx::query_as(
        r#"
        SELECT id, cliente_id, odontogramma, prima_visita, ultima_visita, 
               frequenza_controlli, spazzolino, filo_interdentale, collutorio,
               allergia_lattice, allergia_anestesia, allergie_altre,
               ortodonzia_in_corso, tipo_apparecchio, data_inizio_ortodonzia,
               trattamenti, note_cliniche
        FROM schede_odontoiatriche 
        WHERE cliente_id = ?
        "#
    )
    .bind(&cliente_id)
    .fetch_optional(&*pool)
    .await
    .map_err(|e| e.to_string())?;

    match row {
        Some(r) => Ok(Some(SchedaOdontoiatrica {
            id: Some(r.id),
            cliente_id: r.cliente_id,
            odontogramma: serde_json::from_str(&r.odontogramma).unwrap_or_default(),
            prima_visita: r.prima_visita,
            ultima_visita: r.ultima_visita,
            frequenza_controlli: r.frequenza_controlli,
            spazzolino: r.spazzolino,
            filo_interdentale: r.filo_interdentale != 0,
            collutorio: r.collutorio != 0,
            allergia_lattice: r.allergia_lattice != 0,
            allergia_anestesia: r.allergia_anestesia != 0,
            allergie_altre: r.allergie_altre,
            ortodonzia_in_corso: r.ortodonzia_in_corso != 0,
            tipo_apparecchio: r.tipo_apparecchio,
            data_inizio_ortodonzia: r.data_inizio_ortodonzia,
            trattamenti: serde_json::from_str(&r.trattamenti).unwrap_or_default(),
            note_cliniche: r.note_cliniche,
        })),
        None => Ok(None),
    }
}

#[tauri::command]
pub async fn upsert_scheda_odontoiatrica(
    pool: State<'_, SqlitePool>,
    cliente_id: String,
    data: SchedaOdontoiatrica,
) -> Result<String, String> {
    let id = data.id.unwrap_or_else(|| uuid::Uuid::new_v4().to_string());
    
    let odontogramma_json = serde_json::to_string(&data.odontogramma).map_err(|e| e.to_string())?;
    let trattamenti_json = serde_json::to_string(&data.trattamenti).map_err(|e| e.to_string())?;

    sqlx::query(
        r#"
        INSERT INTO schede_odontoiatriche (
            id, cliente_id, odontogramma, prima_visita, ultima_visita,
            frequenza_controlli, spazzolino, filo_interdentale, collutorio,
            allergia_lattice, allergia_anestesia, allergie_altre,
            ortodonzia_in_corso, tipo_apparecchio, data_inizio_ortodonzia,
            trattamenti, note_cliniche, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ON CONFLICT(id) DO UPDATE SET
            odontogramma = excluded.odontogramma,
            prima_visita = excluded.prima_visita,
            ultima_visita = excluded.ultima_visita,
            frequenza_controlli = excluded.frequenza_controlli,
            spazzolino = excluded.spazzolino,
            filo_interdentale = excluded.filo_interdentale,
            collutorio = excluded.collutorio,
            allergia_lattice = excluded.allergia_lattice,
            allergia_anestesia = excluded.allergia_anestesia,
            allergie_altre = excluded.allergie_altre,
            ortodonzia_in_corso = excluded.ortodonzia_in_corso,
            tipo_apparecchio = excluded.tipo_apparecchio,
            data_inizio_ortodonzia = excluded.data_inizio_ortodonzia,
            trattamenti = excluded.trattamenti,
            note_cliniche = excluded.note_cliniche,
            updated_at = datetime('now')
        "#
    )
    .bind(&id)
    .bind(&cliente_id)
    .bind(&odontogramma_json)
    .bind(&data.prima_visita)
    .bind(&data.ultima_visita)
    .bind(&data.frequenza_controlli)
    .bind(&data.spazzolino)
    .bind(data.filo_interdentale as i32)
    .bind(data.collutorio as i32)
    .bind(data.allergia_lattice as i32)
    .bind(data.allergia_anestesia as i32)
    .bind(&data.allergie_altre)
    .bind(data.ortodonzia_in_corso as i32)
    .bind(&data.tipo_apparecchio)
    .bind(&data.data_inizio_ortodonzia)
    .bind(&trattamenti_json)
    .bind(&data.note_cliniche)
    .execute(&*pool)
    .await
    .map_err(|e| e.to_string())?;

    Ok(id)
}

// ═══════════════════════════════════════════════════════════════════
// COMMANDS - Scheda Fisioterapia
// ═══════════════════════════════════════════════════════════════════

#[tauri::command]
pub async fn get_scheda_fisioterapia(
    pool: State<'_, SqlitePool>,
    cliente_id: String,
) -> Result<Option<SchedaFisioterapia>, String> {
    let row: Option<SchedaFisioterapiaRow> = sqlx::query_as(
        r#"
        SELECT id, cliente_id, motivo_primo_accesso, data_inizio_terapia, data_fine_terapia,
               diagnosi_medica, diagnosi_fisioterapica, zona_principale, zone_secondarie,
               valutazione_iniziale, scale_valutazione, numero_sedute_prescritte, frequenza_settimanale,
               sedute_effettuate, esito_trattamento, controindicazioni
        FROM schede_fisioterapia 
        WHERE cliente_id = ?
        "#
    )
    .bind(&cliente_id)
    .fetch_optional(&*pool)
    .await
    .map_err(|e| e.to_string())?;

    match row {
        Some(r) => Ok(Some(SchedaFisioterapia {
            id: Some(r.id),
            cliente_id: r.cliente_id,
            motivo_primo_accesso: r.motivo_primo_accesso,
            data_inizio_terapia: r.data_inizio_terapia,
            data_fine_terapia: r.data_fine_terapia,
            diagnosi_medica: r.diagnosi_medica,
            diagnosi_fisioterapica: r.diagnosi_fisioterapica,
            zona_principale: r.zona_principale,
            zone_secondarie: serde_json::from_str(&r.zone_secondarie).unwrap_or_default(),
            valutazione_iniziale: serde_json::from_str(&r.valutazione_iniziale).unwrap_or_default(),
            scale_valutazione: serde_json::from_str(&r.scale_valutazione).unwrap_or_default(),
            numero_sedute_prescritte: r.numero_sedute_prescritte,
            frequenza_settimanale: r.frequenza_settimanale,
            sedute_effettuate: serde_json::from_str(&r.sedute_effettuate).unwrap_or_default(),
            esito_trattamento: r.esito_trattamento,
            controindicazioni: r.controindicazioni,
        })),
        None => Ok(None),
    }
}

#[tauri::command]
pub async fn upsert_scheda_fisioterapia(
    pool: State<'_, SqlitePool>,
    cliente_id: String,
    data: SchedaFisioterapia,
) -> Result<String, String> {
    let id = data.id.unwrap_or_else(|| uuid::Uuid::new_v4().to_string());
    
    let zone_sec_json = serde_json::to_string(&data.zone_secondarie).map_err(|e| e.to_string())?;
    let val_iniz_json = serde_json::to_string(&data.valutazione_iniziale).map_err(|e| e.to_string())?;
    let scale_json = serde_json::to_string(&data.scale_valutazione).map_err(|e| e.to_string())?;
    let sedute_json = serde_json::to_string(&data.sedute_effettuate).map_err(|e| e.to_string())?;

    sqlx::query(
        r#"
        INSERT INTO schede_fisioterapia (
            id, cliente_id, motivo_primo_accesso, data_inizio_terapia, data_fine_terapia,
            diagnosi_medica, diagnosi_fisioterapica, zona_principale, zone_secondarie,
            valutazione_iniziale, scale_valutazione, numero_sedute_prescritte, frequenza_settimanale,
            sedute_effettuate, esito_trattamento, controindicazioni, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ON CONFLICT(id) DO UPDATE SET
            motivo_primo_accesso = excluded.motivo_primo_accesso,
            data_inizio_terapia = excluded.data_inizio_terapia,
            data_fine_terapia = excluded.data_fine_terapia,
            diagnosi_medica = excluded.diagnosi_medica,
            diagnosi_fisioterapica = excluded.diagnosi_fisioterapica,
            zona_principale = excluded.zona_principale,
            zone_secondarie = excluded.zone_secondarie,
            valutazione_iniziale = excluded.valutazione_iniziale,
            scale_valutazione = excluded.scale_valutazione,
            numero_sedute_prescritte = excluded.numero_sedute_prescritte,
            frequenza_settimanale = excluded.frequenza_settimanale,
            sedute_effettuate = excluded.sedute_effettuate,
            esito_trattamento = excluded.esito_trattamento,
            controindicazioni = excluded.controindicazioni,
            updated_at = datetime('now')
        "#
    )
    .bind(&id)
    .bind(&cliente_id)
    .bind(&data.motivo_primo_accesso)
    .bind(&data.data_inizio_terapia)
    .bind(&data.data_fine_terapia)
    .bind(&data.diagnosi_medica)
    .bind(&data.diagnosi_fisioterapica)
    .bind(&data.zona_principale)
    .bind(&zone_sec_json)
    .bind(&val_iniz_json)
    .bind(&scale_json)
    .bind(&data.numero_sedute_prescritte)
    .bind(&data.frequenza_settimanale)
    .bind(&sedute_json)
    .bind(&data.esito_trattamento)
    .bind(&data.controindicazioni)
    .execute(&*pool)
    .await
    .map_err(|e| e.to_string())?;

    Ok(id)
}

// ═══════════════════════════════════════════════════════════════════
// COMMANDS - Scheda Estetica
// ═══════════════════════════════════════════════════════════════════

#[tauri::command]
pub async fn get_scheda_estetica(
    pool: State<'_, SqlitePool>,
    cliente_id: String,
) -> Result<Option<SchedaEstetica>, String> {
    let row: Option<SchedaEsteticaRow> = sqlx::query_as(
        r#"
        SELECT id, cliente_id, fototipo, tipo_pelle, allergie_prodotti, allergie_profumi, allergie_henne,
               trattamenti_precedenti, ultima_depilazione, metodo_depilazione, unghie_naturali, problematiche_unghie,
               problematiche_viso, routine_skincare, peso_attuale, obiettivo, gravidanza, allattamento,
               patologie_attive, note_trattamenti
        FROM schede_estetica 
        WHERE cliente_id = ?
        "#
    )
    .bind(&cliente_id)
    .fetch_optional(&*pool)
    .await
    .map_err(|e| e.to_string())?;

    match row {
        Some(r) => Ok(Some(SchedaEstetica {
            id: Some(r.id),
            cliente_id: r.cliente_id,
            fototipo: r.fototipo,
            tipo_pelle: r.tipo_pelle,
            allergie_prodotti: serde_json::from_str(&r.allergie_prodotti).unwrap_or_default(),
            allergie_profumi: r.allergie_profumi != 0,
            allergie_henne: r.allergie_henne != 0,
            trattamenti_precedenti: serde_json::from_str(&r.trattamenti_precedenti).unwrap_or_default(),
            ultima_depilazione: r.ultima_depilazione,
            metodo_depilazione: r.metodo_depilazione,
            unghie_naturali: r.unghie_naturali != 0,
            problematiche_unghie: r.problematiche_unghie,
            problematiche_viso: serde_json::from_str(&r.problematiche_viso).unwrap_or_default(),
            routine_skincare: r.routine_skincare,
            peso_attuale: r.peso_attuale,
            obiettivo: r.obiettivo,
            gravidanza: r.gravidanza != 0,
            allattamento: r.allattamento != 0,
            patologie_attive: serde_json::from_str(&r.patologie_attive).unwrap_or_default(),
            note_trattamenti: r.note_trattamenti,
        })),
        None => Ok(None),
    }
}

#[tauri::command]
pub async fn upsert_scheda_estetica(
    pool: State<'_, SqlitePool>,
    cliente_id: String,
    data: SchedaEstetica,
) -> Result<String, String> {
    let id = data.id.unwrap_or_else(|| uuid::Uuid::new_v4().to_string());
    
    let all_prod_json = serde_json::to_string(&data.allergie_prodotti).map_err(|e| e.to_string())?;
    let tratt_prec_json = serde_json::to_string(&data.trattamenti_precedenti).map_err(|e| e.to_string())?;
    let prob_viso_json = serde_json::to_string(&data.problematiche_viso).map_err(|e| e.to_string())?;
    let patologie_json = serde_json::to_string(&data.patologie_attive).map_err(|e| e.to_string())?;

    sqlx::query(
        r#"
        INSERT INTO schede_estetica (
            id, cliente_id, fototipo, tipo_pelle, allergie_prodotti, allergie_profumi, allergie_henne,
            trattamenti_precedenti, ultima_depilazione, metodo_depilazione, unghie_naturali, problematiche_unghie,
            problematiche_viso, routine_skincare, peso_attuale, obiettivo, gravidanza, allattamento,
            patologie_attive, note_trattamenti, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ON CONFLICT(id) DO UPDATE SET
            fototipo = excluded.fototipo,
            tipo_pelle = excluded.tipo_pelle,
            allergie_prodotti = excluded.allergie_prodotti,
            allergie_profumi = excluded.allergie_profumi,
            allergie_henne = excluded.allergie_henne,
            trattamenti_precedenti = excluded.trattamenti_precedenti,
            ultima_depilazione = excluded.ultima_depilazione,
            metodo_depilazione = excluded.metodo_depilazione,
            unghie_naturali = excluded.unghie_naturali,
            problematiche_unghie = excluded.problematiche_unghie,
            problematiche_viso = excluded.problematiche_viso,
            routine_skincare = excluded.routine_skincare,
            peso_attuale = excluded.peso_attuale,
            obiettivo = excluded.obiettivo,
            gravidanza = excluded.gravidanza,
            allattamento = excluded.allattamento,
            patologie_attive = excluded.patologie_attive,
            note_trattamenti = excluded.note_trattamenti,
            updated_at = datetime('now')
        "#
    )
    .bind(&id)
    .bind(&cliente_id)
    .bind(&data.fototipo)
    .bind(&data.tipo_pelle)
    .bind(&all_prod_json)
    .bind(data.allergie_profumi as i32)
    .bind(data.allergie_henne as i32)
    .bind(&tratt_prec_json)
    .bind(&data.ultima_depilazione)
    .bind(&data.metodo_depilazione)
    .bind(data.unghie_naturali as i32)
    .bind(&data.problematiche_unghie)
    .bind(&prob_viso_json)
    .bind(&data.routine_skincare)
    .bind(&data.peso_attuale)
    .bind(&data.obiettivo)
    .bind(data.gravidanza as i32)
    .bind(data.allattamento as i32)
    .bind(&patologie_json)
    .bind(&data.note_trattamenti)
    .execute(&*pool)
    .await
    .map_err(|e| e.to_string())?;

    Ok(id)
}

// ═══════════════════════════════════════════════════════════════════
// COMMANDS - Scheda Parrucchiere
// ═══════════════════════════════════════════════════════════════════

#[tauri::command]
pub async fn get_scheda_parrucchiere(
    pool: State<'_, SqlitePool>,
    cliente_id: String,
) -> Result<Option<SchedaParrucchiere>, String> {
    let row: Option<SchedaParrucchiereRow> = sqlx::query_as(
        r#"
        SELECT id, cliente_id, tipo_capello, porosita, lunghezza_attuale, base_naturale, colore_attuale,
               colorazioni_precedenti, decolorazioni, permanente, stirature_chimiche, allergia_tinta,
               allergia_ammoniaca, test_pelle_eseguito, data_test_pelle, servizi_abituali,
               frequenza_taglio, frequenza_colore, prodotti_casa, preferenze_colore, non_vuole
        FROM schede_parrucchiere 
        WHERE cliente_id = ?
        "#
    )
    .bind(&cliente_id)
    .fetch_optional(&*pool)
    .await
    .map_err(|e| e.to_string())?;

    match row {
        Some(r) => Ok(Some(SchedaParrucchiere {
            id: Some(r.id),
            cliente_id: r.cliente_id,
            tipo_capello: r.tipo_capello,
            porosita: r.porosita,
            lunghezza_attuale: r.lunghezza_attuale,
            base_naturale: r.base_naturale,
            colore_attuale: r.colore_attuale,
            colorazioni_precedenti: serde_json::from_str(&r.colorazioni_precedenti).unwrap_or_default(),
            decolorazioni: r.decolorazioni,
            permanente: r.permanente,
            stirature_chimiche: r.stirature_chimiche,
            allergia_tinta: r.allergia_tinta != 0,
            allergia_ammoniaca: r.allergia_ammoniaca != 0,
            test_pelle_eseguito: r.test_pelle_eseguito != 0,
            data_test_pelle: r.data_test_pelle,
            servizi_abituali: serde_json::from_str(&r.servizi_abituali).unwrap_or_default(),
            frequenza_taglio: r.frequenza_taglio,
            frequenza_colore: r.frequenza_colore,
            prodotti_casa: serde_json::from_str(&r.prodotti_casa).unwrap_or_default(),
            preferenze_colore: r.preferenze_colore,
            non_vuole: serde_json::from_str(&r.non_vuole).unwrap_or_default(),
        })),
        None => Ok(None),
    }
}

#[tauri::command]
pub async fn upsert_scheda_parrucchiere(
    pool: State<'_, SqlitePool>,
    cliente_id: String,
    data: SchedaParrucchiere,
) -> Result<String, String> {
    let id = data.id.unwrap_or_else(|| uuid::Uuid::new_v4().to_string());
    
    let color_prec_json = serde_json::to_string(&data.colorazioni_precedenti).map_err(|e| e.to_string())?;
    let serv_abit_json = serde_json::to_string(&data.servizi_abituali).map_err(|e| e.to_string())?;
    let prod_casa_json = serde_json::to_string(&data.prodotti_casa).map_err(|e| e.to_string())?;
    let non_vuole_json = serde_json::to_string(&data.non_vuole).map_err(|e| e.to_string())?;

    sqlx::query(
        r#"
        INSERT INTO schede_parrucchiere (
            id, cliente_id, tipo_capello, porosita, lunghezza_attuale, base_naturale, colore_attuale,
            colorazioni_precedenti, decolorazioni, permanente, stirature_chimiche, allergia_tinta,
            allergia_ammoniaca, test_pelle_eseguito, data_test_pelle, servizi_abituali,
            frequenza_taglio, frequenza_colore, prodotti_casa, preferenze_colore, non_vuole, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ON CONFLICT(id) DO UPDATE SET
            tipo_capello = excluded.tipo_capello,
            porosita = excluded.porosita,
            lunghezza_attuale = excluded.lunghezza_attuale,
            base_naturale = excluded.base_naturale,
            colore_attuale = excluded.colore_attuale,
            colorazioni_precedenti = excluded.colorazioni_precedenti,
            decolorazioni = excluded.decolorazioni,
            permanente = excluded.permanente,
            stirature_chimiche = excluded.stirature_chimiche,
            allergia_tinta = excluded.allergia_tinta,
            allergia_ammoniaca = excluded.allergia_ammoniaca,
            test_pelle_eseguito = excluded.test_pelle_eseguito,
            data_test_pelle = excluded.data_test_pelle,
            servizi_abituali = excluded.servizi_abituali,
            frequenza_taglio = excluded.frequenza_taglio,
            frequenza_colore = excluded.frequenza_colore,
            prodotti_casa = excluded.prodotti_casa,
            preferenze_colore = excluded.preferenze_colore,
            non_vuole = excluded.non_vuole,
            updated_at = datetime('now')
        "#
    )
    .bind(&id)
    .bind(&cliente_id)
    .bind(&data.tipo_capello)
    .bind(&data.porosita)
    .bind(&data.lunghezza_attuale)
    .bind(&data.base_naturale)
    .bind(&data.colore_attuale)
    .bind(&color_prec_json)
    .bind(&data.decolorazioni)
    .bind(&data.permanente)
    .bind(&data.stirature_chimiche)
    .bind(data.allergia_tinta as i32)
    .bind(data.allergia_ammoniaca as i32)
    .bind(data.test_pelle_eseguito as i32)
    .bind(&data.data_test_pelle)
    .bind(&serv_abit_json)
    .bind(&data.frequenza_taglio)
    .bind(&data.frequenza_colore)
    .bind(&prod_casa_json)
    .bind(&data.preferenze_colore)
    .bind(&non_vuole_json)
    .execute(&*pool)
    .await
    .map_err(|e| e.to_string())?;

    Ok(id)
}

// ═══════════════════════════════════════════════════════════════════
// COMMANDS - Scheda Veicoli
// ═══════════════════════════════════════════════════════════════════

#[tauri::command]
pub async fn get_schede_veicoli(
    pool: State<'_, SqlitePool>,
    cliente_id: String,
) -> Result<Vec<SchedaVeicoli>, String> {
    let rows: Vec<SchedaVeicoliRow> = sqlx::query_as(
        r#"
        SELECT id, cliente_id, targa, marca, modello, anno, alimentazione, cilindrata, kw, telaio,
               ultima_revisione, scadenza_revisione, km_attuali, km_ultimo_tagliando, misura_gomme,
               tipo_gomme, preferenza_ricambi, note_veicolo, interventi, is_default
        FROM schede_veicoli 
        WHERE cliente_id = ?
        ORDER BY is_default DESC, created_at DESC
        "#
    )
    .bind(&cliente_id)
    .fetch_all(&*pool)
    .await
    .map_err(|e| e.to_string())?;

    let schede: Vec<SchedaVeicoli> = rows.into_iter().map(|r| {
        SchedaVeicoli {
            id: Some(r.id),
            cliente_id: r.cliente_id,
            targa: r.targa,
            marca: r.marca,
            modello: r.modello,
            anno: r.anno,
            alimentazione: r.alimentazione,
            cilindrata: r.cilindrata,
            kw: r.kw,
            telaio: r.telaio,
            ultima_revisione: r.ultima_revisione,
            scadenza_revisione: r.scadenza_revisione,
            km_attuali: r.km_attuali,
            km_ultimo_tagliando: r.km_ultimo_tagliando,
            misura_gomme: r.misura_gomme,
            tipo_gomme: r.tipo_gomme,
            preferenza_ricambi: r.preferenza_ricambi,
            note_veicolo: r.note_veicolo,
            interventi: serde_json::from_str(&r.interventi).unwrap_or_default(),
            is_default: r.is_default != 0,
        }
    }).collect();

    Ok(schede)
}

#[tauri::command]
pub async fn upsert_scheda_veicoli(
    pool: State<'_, SqlitePool>,
    cliente_id: String,
    data: SchedaVeicoli,
) -> Result<String, String> {
    let id = data.id.unwrap_or_else(|| uuid::Uuid::new_v4().to_string());
    
    let interventi_json = serde_json::to_string(&data.interventi).map_err(|e| e.to_string())?;

    sqlx::query(
        r#"
        INSERT INTO schede_veicoli (
            id, cliente_id, targa, marca, modello, anno, alimentazione, cilindrata, kw, telaio,
            ultima_revisione, scadenza_revisione, km_attuali, km_ultimo_tagliando, misura_gomme,
            tipo_gomme, preferenza_ricambi, note_veicolo, interventi, is_default, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ON CONFLICT(id) DO UPDATE SET
            targa = excluded.targa,
            marca = excluded.marca,
            modello = excluded.modello,
            anno = excluded.anno,
            alimentazione = excluded.alimentazione,
            cilindrata = excluded.cilindrata,
            kw = excluded.kw,
            telaio = excluded.telaio,
            ultima_revisione = excluded.ultima_revisione,
            scadenza_revisione = excluded.scadenza_revisione,
            km_attuali = excluded.km_attuali,
            km_ultimo_tagliando = excluded.km_ultimo_tagliando,
            misura_gomme = excluded.misura_gomme,
            tipo_gomme = excluded.tipo_gomme,
            preferenza_ricambi = excluded.preferenza_ricambi,
            note_veicolo = excluded.note_veicolo,
            interventi = excluded.interventi,
            is_default = excluded.is_default,
            updated_at = datetime('now')
        "#
    )
    .bind(&id)
    .bind(&cliente_id)
    .bind(&data.targa)
    .bind(&data.marca)
    .bind(&data.modello)
    .bind(&data.anno)
    .bind(&data.alimentazione)
    .bind(&data.cilindrata)
    .bind(&data.kw)
    .bind(&data.telaio)
    .bind(&data.ultima_revisione)
    .bind(&data.scadenza_revisione)
    .bind(&data.km_attuali)
    .bind(&data.km_ultimo_tagliando)
    .bind(&data.misura_gomme)
    .bind(&data.tipo_gomme)
    .bind(&data.preferenza_ricambi)
    .bind(&data.note_veicolo)
    .bind(&interventi_json)
    .bind(data.is_default as i32)
    .execute(&*pool)
    .await
    .map_err(|e| e.to_string())?;

    Ok(id)
}

// ═══════════════════════════════════════════════════════════════════
// COMMANDS - Scheda Carrozzeria
// ═══════════════════════════════════════════════════════════════════

#[tauri::command]
pub async fn get_schede_carrozzeria(
    pool: State<'_, SqlitePool>,
    cliente_id: String,
) -> Result<Vec<SchedaCarrozzeria>, String> {
    let rows: Vec<SchedaCarrozzeriaRow> = sqlx::query_as(
        r#"
        SELECT id, cliente_id, veicolo_id, tipo_danno, posizione_danno, entita_danno, descrizione_danno,
               foto_pre, foto_post, preventivo_numero, importo_preventivo, approvato, data_ingresso,
               data_consegna_prevista, data_consegna_effettiva, lavorazioni, verniciatura, codice_colore,
               sinistro_assicurativo, compagnia, numero_sinistro, stato
        FROM schede_carrozzeria 
        WHERE cliente_id = ?
        ORDER BY data_ingresso DESC
        "#
    )
    .bind(&cliente_id)
    .fetch_all(&*pool)
    .await
    .map_err(|e| e.to_string())?;

    let schede: Vec<SchedaCarrozzeria> = rows.into_iter().map(|r| {
        SchedaCarrozzeria {
            id: Some(r.id),
            cliente_id: r.cliente_id,
            veicolo_id: r.veicolo_id,
            tipo_danno: r.tipo_danno,
            posizione_danno: r.posizione_danno,
            entita_danno: r.entita_danno,
            descrizione_danno: r.descrizione_danno,
            foto_pre: serde_json::from_str(&r.foto_pre).unwrap_or_default(),
            foto_post: serde_json::from_str(&r.foto_post).unwrap_or_default(),
            preventivo_numero: r.preventivo_numero,
            importo_preventivo: r.importo_preventivo,
            approvato: r.approvato != 0,
            data_ingresso: r.data_ingresso,
            data_consegna_prevista: r.data_consegna_prevista,
            data_consegna_effettiva: r.data_consegna_effettiva,
            lavorazioni: serde_json::from_str(&r.lavorazioni).unwrap_or_default(),
            verniciatura: r.verniciatura != 0,
            codice_colore: r.codice_colore,
            sinistro_assicurativo: r.sinistro_assicurativo != 0,
            compagnia: r.compagnia,
            numero_sinistro: r.numero_sinistro,
            stato: r.stato,
        }
    }).collect();

    Ok(schede)
}

#[tauri::command]
pub async fn upsert_scheda_carrozzeria(
    pool: State<'_, SqlitePool>,
    cliente_id: String,
    data: SchedaCarrozzeria,
) -> Result<String, String> {
    let id = data.id.unwrap_or_else(|| uuid::Uuid::new_v4().to_string());
    
    let foto_pre_json = serde_json::to_string(&data.foto_pre).map_err(|e| e.to_string())?;
    let foto_post_json = serde_json::to_string(&data.foto_post).map_err(|e| e.to_string())?;
    let lavorazioni_json = serde_json::to_string(&data.lavorazioni).map_err(|e| e.to_string())?;

    sqlx::query(
        r#"
        INSERT INTO schede_carrozzeria (
            id, cliente_id, veicolo_id, tipo_danno, posizione_danno, entita_danno, descrizione_danno,
            foto_pre, foto_post, preventivo_numero, importo_preventivo, approvato, data_ingresso,
            data_consegna_prevista, data_consegna_effettiva, lavorazioni, verniciatura, codice_colore,
            sinistro_assicurativo, compagnia, numero_sinistro, stato, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ON CONFLICT(id) DO UPDATE SET
            veicolo_id = excluded.veicolo_id,
            tipo_danno = excluded.tipo_danno,
            posizione_danno = excluded.posizione_danno,
            entita_danno = excluded.entita_danno,
            descrizione_danno = excluded.descrizione_danno,
            foto_pre = excluded.foto_pre,
            foto_post = excluded.foto_post,
            preventivo_numero = excluded.preventivo_numero,
            importo_preventivo = excluded.importo_preventivo,
            approvato = excluded.approvato,
            data_ingresso = excluded.data_ingresso,
            data_consegna_prevista = excluded.data_consegna_prevista,
            data_consegna_effettiva = excluded.data_consegna_effettiva,
            lavorazioni = excluded.lavorazioni,
            verniciatura = excluded.verniciatura,
            codice_colore = excluded.codice_colore,
            sinistro_assicurativo = excluded.sinistro_assicurativo,
            compagnia = excluded.compagnia,
            numero_sinistro = excluded.numero_sinistro,
            stato = excluded.stato,
            updated_at = datetime('now')
        "#
    )
    .bind(&id)
    .bind(&cliente_id)
    .bind(&data.veicolo_id)
    .bind(&data.tipo_danno)
    .bind(&data.posizione_danno)
    .bind(&data.entita_danno)
    .bind(&data.descrizione_danno)
    .bind(&foto_pre_json)
    .bind(&foto_post_json)
    .bind(&data.preventivo_numero)
    .bind(&data.importo_preventivo)
    .bind(data.approvato as i32)
    .bind(&data.data_ingresso)
    .bind(&data.data_consegna_prevista)
    .bind(&data.data_consegna_effettiva)
    .bind(&lavorazioni_json)
    .bind(data.verniciatura as i32)
    .bind(&data.codice_colore)
    .bind(data.sinistro_assicurativo as i32)
    .bind(&data.compagnia)
    .bind(&data.numero_sinistro)
    .bind(&data.stato)
    .execute(&*pool)
    .await
    .map_err(|e| e.to_string())?;

    Ok(id)
}

// ═══════════════════════════════════════════════════════════════════
// COMANDI AGGIUNTIVI - Implementati per compatibilità lib.rs
// ═══════════════════════════════════════════════════════════════════

/// Verifica se esiste una scheda odontoiatrica per il cliente
#[tauri::command]
pub async fn has_scheda_odontoiatrica(
    pool: State<'_, SqlitePool>,
    cliente_id: String,
) -> Result<bool, String> {
    let exists: (i64,) = sqlx::query_as(
        "SELECT COUNT(*) FROM schede_odontoiatriche WHERE cliente_id = ?"
    )
    .bind(&cliente_id)
    .fetch_one(&*pool)
    .await
    .map_err(|e| e.to_string())?;
    
    Ok(exists.0 > 0)
}

/// Elimina una scheda odontoiatrica
#[tauri::command]
pub async fn delete_scheda_odontoiatrica(
    pool: State<'_, SqlitePool>,
    id: String,
) -> Result<(), String> {
    sqlx::query("DELETE FROM schede_odontoiatriche WHERE id = ?")
        .bind(&id)
        .execute(&*pool)
        .await
        .map_err(|e| e.to_string())?;
    
    Ok(())
}

/// Ottieni tutte le schede odontoiatriche (per admin)
#[tauri::command]
pub async fn get_all_schede_odontoiatriche(
    pool: State<'_, SqlitePool>,
) -> Result<Vec<SchedaOdontoiatricaRow>, String> {
    let rows: Vec<SchedaOdontoiatricaRow> = sqlx::query_as(
        "SELECT * FROM schede_odontoiatriche ORDER BY created_at DESC"
    )
    .fetch_all(&*pool)
    .await
    .map_err(|e| e.to_string())?;
    
    Ok(rows)
}

/// Aggiorna solo l'odontogramma (operazione specifica)
#[tauri::command]
pub async fn update_odontogramma(
    pool: State<'_, SqlitePool>,
    cliente_id: String,
    odontogramma: serde_json::Value,
) -> Result<(), String> {
    sqlx::query(
        "UPDATE schede_odontoiatriche SET odontogramma = ?, updated_at = datetime('now') WHERE cliente_id = ?"
    )
    .bind(odontogramma.to_string())
    .bind(&cliente_id)
    .execute(&*pool)
    .await
    .map_err(|e| e.to_string())?;
    
    Ok(())
}

/// Aggiunge un trattamento alla storia clinica
#[tauri::command]
pub async fn add_trattamento_to_storia(
    pool: State<'_, SqlitePool>,
    cliente_id: String,
    trattamento: serde_json::Value,
) -> Result<(), String> {
    // Leggi trattamenti esistenti
    let row: Option<(String,)> = sqlx::query_as(
        "SELECT trattamenti FROM schede_odontoiatriche WHERE cliente_id = ?"
    )
    .bind(&cliente_id)
    .fetch_optional(&*pool)
    .await
    .map_err(|e| e.to_string())?;
    
    if let Some((trattamenti_json,)) = row {
        let mut trattamenti: Vec<serde_json::Value> = 
            serde_json::from_str(&trattamenti_json).unwrap_or_default();
        trattamenti.push(trattamento);
        
        let updated = serde_json::to_string(&trattamenti)
            .map_err(|e| e.to_string())?;
        
        sqlx::query(
            "UPDATE schede_odontoiatriche SET trattamenti = ?, updated_at = datetime('now') WHERE cliente_id = ?"
        )
        .bind(updated)
        .bind(&cliente_id)
        .execute(&*pool)
        .await
        .map_err(|e| e.to_string())?;
    }
    
    Ok(())
}
