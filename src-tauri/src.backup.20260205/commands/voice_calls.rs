// Voice Agent - Chiamate Telefoniche
// Gestione chiamate vocali per prenotazioni automatiche via VoIP

use serde::{Deserialize, Serialize};
use sqlx::SqlitePool;
use tauri::State;
use uuid::Uuid;

// ============================================================================
// Types
// ============================================================================

#[derive(Debug, Serialize, Deserialize, sqlx::FromRow)]
pub struct ChiamataVoice {
    pub id: String,
    pub telefono: String,
    pub cliente_id: Option<String>,
    pub direzione: String,
    pub durata_secondi: Option<i32>,
    pub trascrizione: Option<String>,
    pub intent_rilevato: Option<String>,
    pub esito: Option<String>,
    pub appuntamento_creato_id: Option<String>,
    pub sentiment: Option<String>,
    pub note: Option<String>,
    pub data_inizio: String,
    pub data_fine: Option<String>,
    pub created_at: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, sqlx::FromRow)]
pub struct VoiceAgentConfig {
    pub id: String,
    pub attivo: i32,
    pub voce_modello: String,
    pub saluto_personalizzato: Option<String>,
    pub orario_attivo_da: String,
    pub orario_attivo_a: String,
    pub giorni_attivi: String,
    pub max_chiamate_contemporanee: i32,
    pub timeout_risposta_secondi: i32,
    pub trasferisci_dopo_tentativi: i32,
    pub numero_trasferimento: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, sqlx::FromRow)]
pub struct VoiceAgentStats {
    pub id: String,
    pub data: String,
    pub chiamate_totali: i32,
    pub chiamate_completate: i32,
    pub chiamate_abbandonate: i32,
    pub appuntamenti_creati: i32,
    pub durata_media_secondi: f64,
    pub sentiment_positivo: i32,
    pub sentiment_neutro: i32,
    pub sentiment_negativo: i32,
}

#[derive(Debug, Deserialize)]
pub struct NuovaChiamata {
    pub telefono: String,
    pub cliente_id: Option<String>,
    pub direzione: String,
}

#[derive(Debug, Deserialize)]
pub struct AggiornaChiamata {
    pub trascrizione: Option<String>,
    pub intent_rilevato: Option<String>,
    pub esito: Option<String>,
    pub appuntamento_creato_id: Option<String>,
    pub sentiment: Option<String>,
    pub note: Option<String>,
}

// ============================================================================
// Commands - Chiamate
// ============================================================================

#[tauri::command]
pub async fn inizia_chiamata(
    pool: State<'_, SqlitePool>,
    data: NuovaChiamata,
) -> Result<ChiamataVoice, String> {
    let id = Uuid::new_v4().to_string();
    let now = chrono::Utc::now().to_rfc3339();

    sqlx::query(
        r#"
        INSERT INTO chiamate_voice (id, telefono, cliente_id, direzione, data_inizio)
        VALUES (?, ?, ?, ?, ?)
        "#,
    )
    .bind(&id)
    .bind(&data.telefono)
    .bind(&data.cliente_id)
    .bind(&data.direzione)
    .bind(&now)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Errore creazione chiamata: {}", e))?;

    get_chiamata(pool, id).await
}

#[tauri::command]
pub async fn termina_chiamata(
    pool: State<'_, SqlitePool>,
    id: String,
    update: AggiornaChiamata,
) -> Result<ChiamataVoice, String> {
    let now = chrono::Utc::now().to_rfc3339();

    let chiamata: ChiamataVoice = sqlx::query_as("SELECT * FROM chiamate_voice WHERE id = ?")
        .bind(&id)
        .fetch_one(pool.inner())
        .await
        .map_err(|e| format!("Chiamata non trovata: {}", e))?;

    let data_inizio = chrono::DateTime::parse_from_rfc3339(&chiamata.data_inizio)
        .map_err(|e| format!("Errore parsing data: {}", e))?;
    let data_fine = chrono::Utc::now();
    let durata = (data_fine - data_inizio.with_timezone(&chrono::Utc)).num_seconds() as i32;

    sqlx::query(
        r#"
        UPDATE chiamate_voice SET
            data_fine = ?,
            durata_secondi = ?,
            trascrizione = COALESCE(?, trascrizione),
            intent_rilevato = COALESCE(?, intent_rilevato),
            esito = COALESCE(?, esito),
            appuntamento_creato_id = COALESCE(?, appuntamento_creato_id),
            sentiment = COALESCE(?, sentiment),
            note = COALESCE(?, note)
        WHERE id = ?
        "#,
    )
    .bind(&now)
    .bind(durata)
    .bind(&update.trascrizione)
    .bind(&update.intent_rilevato)
    .bind(&update.esito)
    .bind(&update.appuntamento_creato_id)
    .bind(&update.sentiment)
    .bind(&update.note)
    .bind(&id)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Errore aggiornamento chiamata: {}", e))?;

    aggiorna_stats_chiamata(pool.inner(), &update.esito, durata, &update.sentiment).await?;

    get_chiamata(pool, id).await
}

#[tauri::command]
pub async fn get_chiamata(
    pool: State<'_, SqlitePool>,
    id: String,
) -> Result<ChiamataVoice, String> {
    sqlx::query_as::<_, ChiamataVoice>("SELECT * FROM chiamate_voice WHERE id = ?")
        .bind(&id)
        .fetch_one(pool.inner())
        .await
        .map_err(|e| format!("Chiamata non trovata: {}", e))
}

#[tauri::command]
pub async fn get_chiamate_oggi(pool: State<'_, SqlitePool>) -> Result<Vec<ChiamataVoice>, String> {
    let oggi = chrono::Local::now().format("%Y-%m-%d").to_string();

    sqlx::query_as::<_, ChiamataVoice>(
        r#"
        SELECT * FROM chiamate_voice
        WHERE date(data_inizio) = ? AND deleted_at IS NULL
        ORDER BY data_inizio DESC
        "#,
    )
    .bind(&oggi)
    .fetch_all(pool.inner())
    .await
    .map_err(|e| format!("Errore caricamento chiamate: {}", e))
}

#[tauri::command]
pub async fn get_storico_chiamate(
    pool: State<'_, SqlitePool>,
    telefono: Option<String>,
    cliente_id: Option<String>,
    limite: Option<i32>,
) -> Result<Vec<ChiamataVoice>, String> {
    let limit = limite.unwrap_or(50);

    let mut query = String::from("SELECT * FROM chiamate_voice WHERE deleted_at IS NULL");

    if telefono.is_some() {
        query.push_str(" AND telefono = ?");
    }
    if cliente_id.is_some() {
        query.push_str(" AND cliente_id = ?");
    }

    query.push_str(" ORDER BY data_inizio DESC LIMIT ?");

    let mut q = sqlx::query_as::<_, ChiamataVoice>(&query);

    if let Some(ref t) = telefono {
        q = q.bind(t);
    }
    if let Some(ref c) = cliente_id {
        q = q.bind(c);
    }
    q = q.bind(limit);

    q.fetch_all(pool.inner())
        .await
        .map_err(|e| format!("Errore caricamento storico: {}", e))
}

// ============================================================================
// Commands - Configurazione
// ============================================================================

#[tauri::command]
pub async fn get_voice_config(pool: State<'_, SqlitePool>) -> Result<VoiceAgentConfig, String> {
    sqlx::query_as::<_, VoiceAgentConfig>("SELECT * FROM voice_agent_config WHERE id = 'default'")
        .fetch_one(pool.inner())
        .await
        .map_err(|e| format!("Errore caricamento config: {}", e))
}

#[tauri::command]
pub async fn update_voice_config(
    pool: State<'_, SqlitePool>,
    config: VoiceAgentConfig,
) -> Result<VoiceAgentConfig, String> {
    let now = chrono::Utc::now().to_rfc3339();

    sqlx::query(
        r#"
        UPDATE voice_agent_config SET
            attivo = ?,
            voce_modello = ?,
            saluto_personalizzato = ?,
            orario_attivo_da = ?,
            orario_attivo_a = ?,
            giorni_attivi = ?,
            max_chiamate_contemporanee = ?,
            timeout_risposta_secondi = ?,
            trasferisci_dopo_tentativi = ?,
            numero_trasferimento = ?,
            updated_at = ?
        WHERE id = 'default'
        "#,
    )
    .bind(config.attivo)
    .bind(&config.voce_modello)
    .bind(&config.saluto_personalizzato)
    .bind(&config.orario_attivo_da)
    .bind(&config.orario_attivo_a)
    .bind(&config.giorni_attivi)
    .bind(config.max_chiamate_contemporanee)
    .bind(config.timeout_risposta_secondi)
    .bind(config.trasferisci_dopo_tentativi)
    .bind(&config.numero_trasferimento)
    .bind(&now)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Errore aggiornamento config: {}", e))?;

    get_voice_config(pool).await
}

#[tauri::command]
pub async fn toggle_voice_agent(
    pool: State<'_, SqlitePool>,
    attivo: bool,
) -> Result<VoiceAgentConfig, String> {
    let now = chrono::Utc::now().to_rfc3339();

    sqlx::query("UPDATE voice_agent_config SET attivo = ?, updated_at = ? WHERE id = 'default'")
        .bind(if attivo { 1 } else { 0 })
        .bind(&now)
        .execute(pool.inner())
        .await
        .map_err(|e| format!("Errore toggle voice agent: {}", e))?;

    get_voice_config(pool).await
}

// ============================================================================
// Commands - Statistiche
// ============================================================================

#[tauri::command]
pub async fn get_voice_stats_oggi(pool: State<'_, SqlitePool>) -> Result<VoiceAgentStats, String> {
    let oggi = chrono::Local::now().format("%Y-%m-%d").to_string();

    sqlx::query(
        r#"
        INSERT OR IGNORE INTO voice_agent_stats (id, data)
        VALUES (?, ?)
        "#,
    )
    .bind(&oggi)
    .bind(&oggi)
    .execute(pool.inner())
    .await
    .map_err(|e| format!("Errore creazione stats: {}", e))?;

    sqlx::query_as::<_, VoiceAgentStats>("SELECT * FROM voice_agent_stats WHERE data = ?")
        .bind(&oggi)
        .fetch_one(pool.inner())
        .await
        .map_err(|e| format!("Errore caricamento stats: {}", e))
}

#[tauri::command]
pub async fn get_voice_stats_periodo(
    pool: State<'_, SqlitePool>,
    data_da: String,
    data_a: String,
) -> Result<Vec<VoiceAgentStats>, String> {
    sqlx::query_as::<_, VoiceAgentStats>(
        r#"
        SELECT * FROM voice_agent_stats
        WHERE data >= ? AND data <= ?
        ORDER BY data DESC
        "#,
    )
    .bind(&data_da)
    .bind(&data_a)
    .fetch_all(pool.inner())
    .await
    .map_err(|e| format!("Errore caricamento stats periodo: {}", e))
}

// ============================================================================
// Helper Functions
// ============================================================================

async fn aggiorna_stats_chiamata(
    pool: &SqlitePool,
    esito: &Option<String>,
    durata: i32,
    sentiment: &Option<String>,
) -> Result<(), String> {
    let oggi = chrono::Local::now().format("%Y-%m-%d").to_string();

    sqlx::query("INSERT OR IGNORE INTO voice_agent_stats (id, data) VALUES (?, ?)")
        .bind(&oggi)
        .bind(&oggi)
        .execute(pool)
        .await
        .map_err(|e| format!("Errore creazione stats: {}", e))?;

    let mut update_query =
        String::from("UPDATE voice_agent_stats SET chiamate_totali = chiamate_totali + 1");

    if let Some(ref e) = esito {
        match e.as_str() {
            "completata" => {
                update_query.push_str(", chiamate_completate = chiamate_completate + 1")
            }
            "abbandonata" => {
                update_query.push_str(", chiamate_abbandonate = chiamate_abbandonate + 1")
            }
            _ => {}
        }
    }

    if let Some(ref s) = sentiment {
        match s.as_str() {
            "positivo" => update_query.push_str(", sentiment_positivo = sentiment_positivo + 1"),
            "neutro" => update_query.push_str(", sentiment_neutro = sentiment_neutro + 1"),
            "negativo" => update_query.push_str(", sentiment_negativo = sentiment_negativo + 1"),
            _ => {}
        }
    }

    update_query.push_str(
        ", durata_media_secondi = (durata_media_secondi * (chiamate_totali - 1) + ?) / chiamate_totali",
    );

    update_query.push_str(" WHERE data = ?");

    sqlx::query(&update_query)
        .bind(durata)
        .bind(&oggi)
        .execute(pool)
        .await
        .map_err(|e| format!("Errore aggiornamento stats: {}", e))?;

    Ok(())
}
