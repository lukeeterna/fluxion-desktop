// ═══════════════════════════════════════════════════════════════════
// FLUXION - Media Commands (F06 Sprint A)
// Gestione foto e video nelle schede cliente
// ═══════════════════════════════════════════════════════════════════

use base64::{engine::general_purpose, Engine};
use printpdf::*;
use serde::{Deserialize, Serialize};
use sqlx::SqlitePool;
use std::io::BufWriter;
use std::path::PathBuf;
use tauri::{AppHandle, Manager, State};
use uuid::Uuid;

// ═══════════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════════

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
pub struct MediaRecord {
    pub id: Option<i64>,
    pub cliente_id: i64,
    pub media_path: String,
    pub thumb_path: Option<String>,
    pub tipo: String,
    pub categoria: String,
    pub appuntamento_id: Option<i64>,
    pub operatore_id: Option<i64>,
    pub dimensione_bytes: Option<i64>,
    pub larghezza_px: Option<i64>,
    pub altezza_px: Option<i64>,
    pub durata_sec: Option<i64>,
    pub consenso_gdpr: i64,
    pub visibilita: String,
    pub watermark: i64,
    pub note: Option<String>,
    pub tag: Option<String>,
    pub created_at: String,
    pub updated_at: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SaveMediaImageInput {
    pub cliente_id: i64,
    pub bytes_base64: String,
    pub original_name: String,
    pub larghezza_px: Option<i64>,
    pub altezza_px: Option<i64>,
    pub categoria: Option<String>,
    pub consenso_gdpr: Option<bool>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SaveMediaVideoInput {
    pub cliente_id: i64,
    pub video_base64: String,
    pub thumb_base64: String,
    pub original_name: String,
    pub durata_sec: Option<i64>,
    pub categoria: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct MediaConsentInput {
    pub cliente_id: i64,
    pub consenso_interno: bool,
    pub consenso_social: bool,
    pub consenso_clinico: bool,
}

// ═══════════════════════════════════════════════════════════════════
// HELPERS
// ═══════════════════════════════════════════════════════════════════

fn get_media_dir(app: &AppHandle, cliente_id: i64, sub: &str) -> Result<PathBuf, String> {
    let app_data = app
        .path()
        .app_data_dir()
        .map_err(|e| format!("Impossibile ottenere app data dir: {e}"))?;
    let dir = app_data
        .join("media")
        .join("clienti")
        .join(cliente_id.to_string())
        .join(sub);
    std::fs::create_dir_all(&dir)
        .map_err(|e| format!("Impossibile creare directory media: {e}"))?;
    Ok(dir)
}

fn relative_path(app: &AppHandle, absolute: &PathBuf) -> Result<String, String> {
    let app_data = app
        .path()
        .app_data_dir()
        .map_err(|e| format!("app_data_dir error: {e}"))?;
    absolute
        .strip_prefix(&app_data)
        .map(|p| p.to_string_lossy().replace('\\', "/"))
        .map_err(|e| format!("strip_prefix error: {e}"))
}

// ═══════════════════════════════════════════════════════════════════
// COMMANDS
// ═══════════════════════════════════════════════════════════════════

/// Salva immagine compressa nel filesystem e registra nel DB
#[tauri::command]
pub async fn save_media_image(
    pool: State<'_, SqlitePool>,
    app: AppHandle,
    input: SaveMediaImageInput,
) -> Result<MediaRecord, String> {
    let bytes = general_purpose::STANDARD
        .decode(&input.bytes_base64)
        .map_err(|e| format!("Decodifica base64 fallita: {e}"))?;

    let ext = if input.original_name.to_lowercase().ends_with(".png") {
        "png"
    } else {
        "jpg"
    };
    let file_name = format!("{}.{ext}", Uuid::new_v4());
    let dir = get_media_dir(&app, input.cliente_id, "foto")?;
    let abs_path = dir.join(&file_name);

    std::fs::write(&abs_path, &bytes).map_err(|e| format!("Scrittura file fallita: {e}"))?;

    let rel_path = relative_path(&app, &abs_path)?;
    let dim = bytes.len() as i64;
    let categoria = input.categoria.unwrap_or_else(|| "generale".to_string());
    let consenso = if input.consenso_gdpr.unwrap_or(false) { 1i64 } else { 0i64 };
    let now = chrono::Utc::now().format("%Y-%m-%d %H:%M:%S").to_string();

    let id = sqlx::query_scalar!(
        r#"INSERT INTO cliente_media
           (cliente_id, media_path, tipo, categoria, dimensione_bytes, larghezza_px, altezza_px,
            consenso_gdpr, visibilita, created_at, updated_at)
           VALUES (?, ?, 'foto', ?, ?, ?, ?, ?, 'interno', ?, ?)
           RETURNING id"#,
        input.cliente_id,
        rel_path,
        categoria,
        dim,
        input.larghezza_px,
        input.altezza_px,
        consenso,
        now,
        now,
    )
    .fetch_one(&*pool)
    .await
    .map_err(|e| format!("DB insert fallito: {e}"))?;

    let record = sqlx::query_as!(
        MediaRecord,
        "SELECT * FROM cliente_media WHERE id = ?",
        id
    )
    .fetch_one(&*pool)
    .await
    .map_err(|e| format!("DB fetch fallito: {e}"))?;

    Ok(record)
}

/// Salva video + thumbnail nel filesystem e registra nel DB
#[tauri::command]
pub async fn save_media_video(
    pool: State<'_, SqlitePool>,
    app: AppHandle,
    input: SaveMediaVideoInput,
) -> Result<MediaRecord, String> {
    let video_bytes = general_purpose::STANDARD
        .decode(&input.video_base64)
        .map_err(|e| format!("Decodifica video base64 fallita: {e}"))?;
    let thumb_bytes = general_purpose::STANDARD
        .decode(&input.thumb_base64)
        .map_err(|e| format!("Decodifica thumbnail base64 fallita: {e}"))?;

    let ext = if input.original_name.to_lowercase().ends_with(".mov") {
        "mov"
    } else {
        "mp4"
    };
    let uuid = Uuid::new_v4().to_string();
    let video_name = format!("{uuid}.{ext}");
    let thumb_name = format!("{uuid}_thumb.jpg");

    let video_dir = get_media_dir(&app, input.cliente_id, "video")?;
    let video_abs = video_dir.join(&video_name);
    let thumb_abs = video_dir.join(&thumb_name);

    std::fs::write(&video_abs, &video_bytes)
        .map_err(|e| format!("Scrittura video fallita: {e}"))?;
    std::fs::write(&thumb_abs, &thumb_bytes)
        .map_err(|e| format!("Scrittura thumbnail fallita: {e}"))?;

    let video_rel = relative_path(&app, &video_abs)?;
    let thumb_rel = relative_path(&app, &thumb_abs)?;
    let dim = video_bytes.len() as i64;
    let categoria = input.categoria.unwrap_or_else(|| "generale".to_string());
    let now = chrono::Utc::now().format("%Y-%m-%d %H:%M:%S").to_string();

    let id = sqlx::query_scalar!(
        r#"INSERT INTO cliente_media
           (cliente_id, media_path, thumb_path, tipo, categoria, dimensione_bytes, durata_sec,
            consenso_gdpr, visibilita, created_at, updated_at)
           VALUES (?, ?, ?, 'video', ?, ?, ?, 0, 'interno', ?, ?)
           RETURNING id"#,
        input.cliente_id,
        video_rel,
        thumb_rel,
        categoria,
        dim,
        input.durata_sec,
        now,
        now,
    )
    .fetch_one(&*pool)
    .await
    .map_err(|e| format!("DB insert video fallito: {e}"))?;

    let record = sqlx::query_as!(
        MediaRecord,
        "SELECT * FROM cliente_media WHERE id = ?",
        id
    )
    .fetch_one(&*pool)
    .await
    .map_err(|e| format!("DB fetch video fallito: {e}"))?;

    Ok(record)
}

/// Recupera lista media per un cliente (opzionalmente filtrata per tipo/categoria)
#[tauri::command]
pub async fn get_cliente_media(
    pool: State<'_, SqlitePool>,
    cliente_id: i64,
    tipo: Option<String>,
    categoria: Option<String>,
) -> Result<Vec<MediaRecord>, String> {
    let records = match (tipo, categoria) {
        (Some(t), Some(c)) => {
            sqlx::query_as!(
                MediaRecord,
                "SELECT * FROM cliente_media WHERE cliente_id = ? AND tipo = ? AND categoria = ? ORDER BY created_at DESC",
                cliente_id, t, c
            )
            .fetch_all(&*pool)
            .await
        }
        (Some(t), None) => {
            sqlx::query_as!(
                MediaRecord,
                "SELECT * FROM cliente_media WHERE cliente_id = ? AND tipo = ? ORDER BY created_at DESC",
                cliente_id, t
            )
            .fetch_all(&*pool)
            .await
        }
        (None, Some(c)) => {
            sqlx::query_as!(
                MediaRecord,
                "SELECT * FROM cliente_media WHERE cliente_id = ? AND categoria = ? ORDER BY created_at DESC",
                cliente_id, c
            )
            .fetch_all(&*pool)
            .await
        }
        (None, None) => {
            sqlx::query_as!(
                MediaRecord,
                "SELECT * FROM cliente_media WHERE cliente_id = ? ORDER BY created_at DESC",
                cliente_id
            )
            .fetch_all(&*pool)
            .await
        }
    }
    .map_err(|e| format!("Errore query media: {e}"))?;

    Ok(records)
}

/// Elimina media: file dal filesystem + record dal DB
#[tauri::command]
pub async fn delete_media(
    pool: State<'_, SqlitePool>,
    app: AppHandle,
    media_id: i64,
) -> Result<(), String> {
    let record = sqlx::query_as!(
        MediaRecord,
        "SELECT * FROM cliente_media WHERE id = ?",
        media_id
    )
    .fetch_optional(&*pool)
    .await
    .map_err(|e| format!("DB query fallita: {e}"))?
    .ok_or_else(|| format!("Media {media_id} non trovato"))?;

    // Delete file(s)
    let app_data = app
        .path()
        .app_data_dir()
        .map_err(|e| format!("app_data_dir error: {e}"))?;

    let abs_path = app_data.join(&record.media_path);
    if abs_path.exists() {
        std::fs::remove_file(&abs_path).map_err(|e| format!("Eliminazione file fallita: {e}"))?;
    }

    if let Some(thumb) = &record.thumb_path {
        let thumb_abs = app_data.join(thumb);
        if thumb_abs.exists() {
            let _ = std::fs::remove_file(&thumb_abs);
        }
    }

    // Delete from DB (cascade handles trasformazioni references)
    sqlx::query!("DELETE FROM cliente_media WHERE id = ?", media_id)
        .execute(&*pool)
        .await
        .map_err(|e| format!("DB delete fallito: {e}"))?;

    Ok(())
}

/// Legge il contenuto di un file media come base64 (per lightbox/preview)
#[tauri::command]
pub async fn read_media_file(
    app: AppHandle,
    relative_path: String,
) -> Result<String, String> {
    let app_data = app
        .path()
        .app_data_dir()
        .map_err(|e| format!("app_data_dir error: {e}"))?;

    // Security: prevent path traversal
    let clean = relative_path.replace("..", "").replace('\\', "/");
    let abs_path = app_data.join(&clean);

    // Ensure path is within app_data
    if !abs_path.starts_with(&app_data) {
        return Err("Accesso negato: path fuori dalla directory consentita".to_string());
    }

    let bytes =
        std::fs::read(&abs_path).map_err(|e| format!("Lettura file fallita: {e}"))?;

    Ok(general_purpose::STANDARD.encode(&bytes))
}

/// Aggiorna il campo note di un record media (usato per salvare annotazioni JSON)
#[tauri::command]
pub async fn update_media_note(
    pool: State<'_, SqlitePool>,
    media_id: i64,
    note: String,
) -> Result<(), String> {
    let now = chrono::Utc::now().format("%Y-%m-%d %H:%M:%S").to_string();
    sqlx::query!(
        "UPDATE cliente_media SET note = ?, updated_at = ? WHERE id = ?",
        note,
        now,
        media_id,
    )
    .execute(&*pool)
    .await
    .map_err(|e| format!("DB update note fallito: {e}"))?;
    Ok(())
}

/// Genera PDF rapporto fotografico per Carrozzeria o Fitness progress
/// Usa printpdf — testo + metadata (senza embedding immagini per compatibilità)
#[tauri::command]
pub async fn export_media_pdf(
    pool: State<'_, SqlitePool>,
    app: AppHandle,
    cliente_id: i64,
    tipo_report: String,
) -> Result<String, String> {
    // Recupera info cliente
    let nome_cliente = sqlx::query_scalar!(
        "SELECT nome || ' ' || COALESCE(cognome, '') FROM clienti WHERE id = ?",
        cliente_id,
    )
    .fetch_optional(&*pool)
    .await
    .map_err(|e| format!("DB cliente: {e}"))?
    .unwrap_or_else(|| format!("Cliente {cliente_id}"));

    // Recupera media filtrati per tipo report
    let categorie: Vec<&str> = match tipo_report.as_str() {
        "veicolo" => vec!["danno_veicolo", "lavorazione", "post_intervento"],
        "progress" => vec!["progress"],
        "trasformazioni" => vec!["trasformazione_prima", "trasformazione_dopo"],
        _ => vec!["generale"],
    };

    let records = sqlx::query_as!(
        MediaRecord,
        "SELECT * FROM cliente_media WHERE cliente_id = ? AND tipo = 'foto' ORDER BY categoria, created_at ASC",
        cliente_id,
    )
    .fetch_all(&*pool)
    .await
    .map_err(|e| format!("DB media: {e}"))?;

    let filtered: Vec<&MediaRecord> = records
        .iter()
        .filter(|r| categorie.contains(&r.categoria.as_str()))
        .collect();

    // Crea PDF A4
    let (doc, page1, layer1) = PdfDocument::new(
        "Rapporto Fotografico FLUXION",
        Mm(210.0),
        Mm(297.0),
        "Pagina 1",
    );

    let font = doc
        .add_builtin_font(BuiltinFont::HelveticaBold)
        .map_err(|e| format!("Font error: {e}"))?;
    let font_regular = doc
        .add_builtin_font(BuiltinFont::Helvetica)
        .map_err(|e| format!("Font error: {e}"))?;

    let layer = doc.get_page(page1).get_layer(layer1);

    // Header
    layer.use_text("FLUXION CRM — Rapporto Fotografico", 16.0, Mm(20.0), Mm(277.0), &font);
    layer.use_text(
        format!("Cliente: {nome_cliente}"),
        11.0,
        Mm(20.0),
        Mm(265.0),
        &font_regular,
    );
    layer.use_text(
        format!(
            "Tipo: {} | Data: {}",
            tipo_report,
            chrono::Utc::now().format("%d/%m/%Y"),
        ),
        9.0,
        Mm(20.0),
        Mm(258.0),
        &font_regular,
    );
    layer.use_text(
        format!("Totale foto: {}", filtered.len()),
        9.0,
        Mm(20.0),
        Mm(252.0),
        &font_regular,
    );

    // Separatore
    let line_pts = vec![
        (Point::new(Mm(20.0), Mm(248.0)), false),
        (Point::new(Mm(190.0), Mm(248.0)), false),
    ];
    let line = Line { points: line_pts, is_closed: false };
    layer.add_line(line);

    // Elenco foto per categoria
    let mut y = 240.0f32;
    let mut cur_cat = String::new();

    for record in &filtered {
        if record.categoria != cur_cat {
            if y < 30.0 {
                break; // evita overflow pagina (per MVP)
            }
            cur_cat = record.categoria.clone();
            let cat_label = match cur_cat.as_str() {
                "danno_veicolo" => "ENTRATA — Foto Danni",
                "lavorazione" => "LAVORAZIONE — Foto Processo",
                "post_intervento" => "USCITA — Foto Completato",
                "progress" => "PROGRESS FOTO",
                "trasformazione_prima" => "PRIMA",
                "trasformazione_dopo" => "DOPO",
                other => other,
            };
            y -= 8.0;
            layer.use_text(cat_label, 10.0, Mm(20.0), Mm(y), &font);
            y -= 4.0;
        }

        if y < 25.0 {
            break;
        }

        let data_str = &record.created_at[..10]; // yyyy-mm-dd
        let note_str = record.note.as_deref().unwrap_or("").chars().take(60).collect::<String>();
        let row = if note_str.is_empty() {
            format!("  [{data_str}] {}", record.media_path.split('/').last().unwrap_or(""))
        } else {
            format!(
                "  [{data_str}] {} — Note: {note_str}",
                record.media_path.split('/').last().unwrap_or("")
            )
        };
        layer.use_text(&row, 8.0, Mm(20.0), Mm(y), &font_regular);
        y -= 5.5;
    }

    if filtered.is_empty() {
        layer.use_text("Nessuna foto disponibile per questo report.", 10.0, Mm(20.0), Mm(240.0), &font_regular);
    }

    // Footer
    layer.use_text(
        "Generato da FLUXION CRM — Software gestionale PMI italiane",
        7.0,
        Mm(20.0),
        Mm(10.0),
        &font_regular,
    );

    // Salva PDF in Downloads
    let downloads = dirs_next::download_dir()
        .or_else(|| {
            app.path()
                .app_data_dir()
                .ok()
        })
        .ok_or("Impossibile trovare cartella Download")?;

    let file_name = format!(
        "rapporto_fotografico_{}_{}.pdf",
        cliente_id,
        chrono::Utc::now().format("%Y%m%d_%H%M%S"),
    );
    let pdf_path = downloads.join(&file_name);

    let file = std::fs::File::create(&pdf_path)
        .map_err(|e| format!("Creazione file PDF fallita: {e}"))?;
    let mut writer = BufWriter::new(file);
    doc.save(&mut writer)
        .map_err(|e| format!("Salvataggio PDF fallito: {e}"))?;

    Ok(pdf_path.to_string_lossy().into_owned())
}

/// Aggiorna consenso GDPR media di un cliente
#[tauri::command]
pub async fn update_media_consent(
    pool: State<'_, SqlitePool>,
    input: MediaConsentInput,
) -> Result<(), String> {
    let interno = if input.consenso_interno { 1i64 } else { 0i64 };
    let social = if input.consenso_social { 1i64 } else { 0i64 };
    let clinico = if input.consenso_clinico { 1i64 } else { 0i64 };
    let now = chrono::Utc::now().format("%Y-%m-%d %H:%M:%S").to_string();

    sqlx::query!(
        "UPDATE clienti SET media_consenso_interno = ?, media_consenso_social = ?,
         media_consenso_clinico = ?, media_consenso_data = ? WHERE id = ?",
        interno,
        social,
        clinico,
        now,
        input.cliente_id,
    )
    .execute(&*pool)
    .await
    .map_err(|e| format!("DB update consenso fallito: {e}"))?;

    Ok(())
}
