// ═══════════════════════════════════════════════════════════════════
// FLUXION - Analytics Commands (Gap #9)
// Dashboard mensile KPI + export PDF "Report Attività"
// ═══════════════════════════════════════════════════════════════════

use printpdf::*;
use serde::Serialize;
use sqlx::SqlitePool;
use std::io::BufWriter;
use tauri::{AppHandle, Manager, State};

// ───────────────────────────────────────────────────────────────────
// Types
// ───────────────────────────────────────────────────────────────────

#[derive(Debug, Serialize, sqlx::FromRow)]
pub struct ServizioKpi {
    pub nome: String,
    pub conteggio: i64,
    pub revenue: f64,
}

#[derive(Debug, Serialize, sqlx::FromRow)]
pub struct OperatoreAnalytics {
    pub nome_completo: String,
    pub appuntamenti_completati: i64,
    pub revenue: f64,
}

#[derive(Debug, Serialize)]
pub struct AnalyticsMensili {
    pub anno: i32,
    pub mese: i32,
    pub mese_label: String,

    // Revenue
    pub revenue_mese: f64,
    pub revenue_mese_prec: f64,
    pub revenue_delta_pct: f64,

    // Appuntamenti breakdown
    pub appuntamenti_totali: i64,
    pub appuntamenti_completati: i64,
    pub appuntamenti_cancellati: i64,
    pub appuntamenti_no_show: i64,
    pub appuntamenti_confermati: i64,

    // Top 5 servizi per prenotazioni
    pub top_servizi: Vec<ServizioKpi>,

    // Top operatori per revenue
    pub top_operatori: Vec<OperatoreAnalytics>,

    // Clienti nuovi (prima visita in questo mese) vs ritorni
    pub clienti_nuovi: i64,
    pub clienti_ritorni: i64,

    // WA interactive confirm (Gap #4 KPI)
    pub wa_confermati: i64,
    pub wa_cancellati: i64,
    pub wa_confirm_rate: f64, // 0-100%
}

// ───────────────────────────────────────────────────────────────────
// Helpers
// ───────────────────────────────────────────────────────────────────

fn mese_label_it(anno: i32, mese: i32) -> String {
    const MESI: [&str; 12] = [
        "Gennaio",
        "Febbraio",
        "Marzo",
        "Aprile",
        "Maggio",
        "Giugno",
        "Luglio",
        "Agosto",
        "Settembre",
        "Ottobre",
        "Novembre",
        "Dicembre",
    ];
    let idx = ((mese - 1).clamp(0, 11)) as usize;
    format!("{} {}", MESI[idx], anno)
}

fn prev_month(anno: i32, mese: i32) -> (i32, i32) {
    if mese == 1 {
        (anno - 1, 12)
    } else {
        (anno, mese - 1)
    }
}

fn format_eur(value: f64) -> String {
    // Simple Italian currency format: €1.234,56
    let cents = (value * 100.0).round() as i64;
    let euros = cents / 100;
    let decimal = (cents % 100).unsigned_abs();
    let euros_fmt = format_thousands(euros);
    format!("€{},{:02}", euros_fmt, decimal)
}

fn format_thousands(n: i64) -> String {
    let s = n.abs().to_string();
    let mut result = String::new();
    for (i, c) in s.chars().rev().enumerate() {
        if i > 0 && i % 3 == 0 {
            result.push('.');
        }
        result.push(c);
    }
    if n < 0 {
        result.push('-');
    }
    result.chars().rev().collect()
}

// ───────────────────────────────────────────────────────────────────
// Command: get_analytics_mensili
// ───────────────────────────────────────────────────────────────────

#[tauri::command]
pub async fn get_analytics_mensili(
    pool: State<'_, SqlitePool>,
    anno: i32,
    mese: i32,
) -> Result<AnalyticsMensili, String> {
    let mese_str = format!("{:04}-{:02}", anno, mese);
    let (anno_prec, mese_prec) = prev_month(anno, mese);
    let mese_prec_str = format!("{:04}-{:02}", anno_prec, mese_prec);

    // ── Revenue mese corrente (completato) ──────────────────────────
    let revenue_mese: f64 = sqlx::query_scalar(
        "SELECT COALESCE(SUM(prezzo_finale), 0.0) FROM appuntamenti
         WHERE stato = 'completato'
           AND strftime('%Y-%m', data_ora_inizio) = ?
           AND deleted_at IS NULL",
    )
    .bind(&mese_str)
    .fetch_one(pool.inner())
    .await
    .unwrap_or(0.0);

    // ── Revenue mese precedente ─────────────────────────────────────
    let revenue_mese_prec: f64 = sqlx::query_scalar(
        "SELECT COALESCE(SUM(prezzo_finale), 0.0) FROM appuntamenti
         WHERE stato = 'completato'
           AND strftime('%Y-%m', data_ora_inizio) = ?
           AND deleted_at IS NULL",
    )
    .bind(&mese_prec_str)
    .fetch_one(pool.inner())
    .await
    .unwrap_or(0.0);

    let revenue_delta_pct = if revenue_mese_prec > 0.0 {
        ((revenue_mese - revenue_mese_prec) / revenue_mese_prec) * 100.0
    } else if revenue_mese > 0.0 {
        100.0
    } else {
        0.0
    };

    // ── Appuntamenti breakdown ──────────────────────────────────────
    let appuntamenti_totali: i64 = sqlx::query_scalar(
        "SELECT COUNT(*) FROM appuntamenti
         WHERE strftime('%Y-%m', data_ora_inizio) = ?
           AND deleted_at IS NULL",
    )
    .bind(&mese_str)
    .fetch_one(pool.inner())
    .await
    .unwrap_or(0);

    let appuntamenti_completati: i64 = sqlx::query_scalar(
        "SELECT COUNT(*) FROM appuntamenti
         WHERE stato = 'completato'
           AND strftime('%Y-%m', data_ora_inizio) = ?
           AND deleted_at IS NULL",
    )
    .bind(&mese_str)
    .fetch_one(pool.inner())
    .await
    .unwrap_or(0);

    let appuntamenti_cancellati: i64 = sqlx::query_scalar(
        "SELECT COUNT(*) FROM appuntamenti
         WHERE stato IN ('cancellato', 'Cancellato')
           AND strftime('%Y-%m', data_ora_inizio) = ?
           AND deleted_at IS NULL",
    )
    .bind(&mese_str)
    .fetch_one(pool.inner())
    .await
    .unwrap_or(0);

    let appuntamenti_no_show: i64 = sqlx::query_scalar(
        "SELECT COUNT(*) FROM appuntamenti
         WHERE stato = 'no_show'
           AND strftime('%Y-%m', data_ora_inizio) = ?
           AND deleted_at IS NULL",
    )
    .bind(&mese_str)
    .fetch_one(pool.inner())
    .await
    .unwrap_or(0);

    let appuntamenti_confermati: i64 = sqlx::query_scalar(
        "SELECT COUNT(*) FROM appuntamenti
         WHERE stato IN ('confermato', 'Confermato')
           AND strftime('%Y-%m', data_ora_inizio) = ?
           AND deleted_at IS NULL",
    )
    .bind(&mese_str)
    .fetch_one(pool.inner())
    .await
    .unwrap_or(0);

    // ── Top 5 servizi ───────────────────────────────────────────────
    let top_servizi = sqlx::query_as::<_, ServizioKpi>(
        "SELECT s.nome,
                COUNT(*) AS conteggio,
                COALESCE(SUM(a.prezzo_finale), 0.0) AS revenue
         FROM appuntamenti a
         JOIN servizi s ON a.servizio_id = s.id
         WHERE strftime('%Y-%m', a.data_ora_inizio) = ?
           AND a.deleted_at IS NULL
           AND a.stato NOT IN ('cancellato', 'Cancellato')
         GROUP BY a.servizio_id
         ORDER BY conteggio DESC
         LIMIT 5",
    )
    .bind(&mese_str)
    .fetch_all(pool.inner())
    .await
    .unwrap_or_default();

    // ── Top operatori ───────────────────────────────────────────────
    let top_operatori = sqlx::query_as::<_, OperatoreAnalytics>(
        "SELECT o.nome || ' ' || o.cognome AS nome_completo,
                COUNT(*) AS appuntamenti_completati,
                COALESCE(SUM(a.prezzo_finale), 0.0) AS revenue
         FROM appuntamenti a
         JOIN operatori o ON a.operatore_id = o.id
         WHERE strftime('%Y-%m', a.data_ora_inizio) = ?
           AND a.stato = 'completato'
           AND a.deleted_at IS NULL
         GROUP BY a.operatore_id
         ORDER BY revenue DESC
         LIMIT 5",
    )
    .bind(&mese_str)
    .fetch_all(pool.inner())
    .await
    .unwrap_or_default();

    // ── Clienti nuovi vs ritorni ────────────────────────────────────
    // Nuovi: cliente la cui PRIMA visita assoluta (non cancellata) è in questo mese
    let clienti_nuovi: i64 = sqlx::query_scalar(
        "SELECT COUNT(DISTINCT a.cliente_id)
         FROM appuntamenti a
         WHERE strftime('%Y-%m', a.data_ora_inizio) = ?
           AND a.deleted_at IS NULL
           AND a.stato NOT IN ('cancellato', 'Cancellato', 'no_show')
           AND NOT EXISTS (
               SELECT 1 FROM appuntamenti prev
               WHERE prev.cliente_id = a.cliente_id
                 AND prev.deleted_at IS NULL
                 AND prev.stato NOT IN ('cancellato', 'Cancellato', 'no_show')
                 AND strftime('%Y-%m', prev.data_ora_inizio) < ?
           )",
    )
    .bind(&mese_str)
    .bind(&mese_str)
    .fetch_one(pool.inner())
    .await
    .unwrap_or(0);

    // Ritorni: aveva già appuntamenti in mesi precedenti
    let clienti_ritorni: i64 = sqlx::query_scalar(
        "SELECT COUNT(DISTINCT a.cliente_id)
         FROM appuntamenti a
         WHERE strftime('%Y-%m', a.data_ora_inizio) = ?
           AND a.deleted_at IS NULL
           AND a.stato NOT IN ('cancellato', 'Cancellato', 'no_show')
           AND EXISTS (
               SELECT 1 FROM appuntamenti prev
               WHERE prev.cliente_id = a.cliente_id
                 AND prev.deleted_at IS NULL
                 AND prev.stato NOT IN ('cancellato', 'Cancellato', 'no_show')
                 AND strftime('%Y-%m', prev.data_ora_inizio) < ?
           )",
    )
    .bind(&mese_str)
    .bind(&mese_str)
    .fetch_one(pool.inner())
    .await
    .unwrap_or(0);

    // ── WA Interactive Confirm rate (Gap #4 KPI) ────────────────────
    // Confermati = CamelCase 'Confermato' (impostato da whatsapp_callback.py)
    // Cancellati = CamelCase 'Cancellato' (impostato da whatsapp_callback.py)
    let wa_confermati: i64 = sqlx::query_scalar(
        "SELECT COUNT(*) FROM appuntamenti
         WHERE stato = 'Confermato'
           AND strftime('%Y-%m', data_ora_inizio) = ?
           AND deleted_at IS NULL",
    )
    .bind(&mese_str)
    .fetch_one(pool.inner())
    .await
    .unwrap_or(0);

    let wa_cancellati: i64 = sqlx::query_scalar(
        "SELECT COUNT(*) FROM appuntamenti
         WHERE stato = 'Cancellato'
           AND strftime('%Y-%m', data_ora_inizio) = ?
           AND deleted_at IS NULL",
    )
    .bind(&mese_str)
    .fetch_one(pool.inner())
    .await
    .unwrap_or(0);

    let wa_total = wa_confermati + wa_cancellati;
    let wa_confirm_rate = if wa_total > 0 {
        (wa_confermati as f64 / wa_total as f64) * 100.0
    } else {
        0.0
    };

    Ok(AnalyticsMensili {
        anno,
        mese,
        mese_label: mese_label_it(anno, mese),
        revenue_mese,
        revenue_mese_prec,
        revenue_delta_pct,
        appuntamenti_totali,
        appuntamenti_completati,
        appuntamenti_cancellati,
        appuntamenti_no_show,
        appuntamenti_confermati,
        top_servizi,
        top_operatori,
        clienti_nuovi,
        clienti_ritorni,
        wa_confermati,
        wa_cancellati,
        wa_confirm_rate,
    })
}

// ───────────────────────────────────────────────────────────────────
// Command: genera_report_pdf_mensile
// Genera PDF "Report Attività" in ~/Documents/Fluxion_Report_YYYY-MM.pdf
// ───────────────────────────────────────────────────────────────────

#[tauri::command]
pub async fn genera_report_pdf_mensile(
    pool: State<'_, SqlitePool>,
    app: AppHandle,
    anno: i32,
    mese: i32,
) -> Result<String, String> {
    // Recupera dati
    let dati = get_analytics_mensili(pool.clone(), anno, mese).await?;

    // Nome attività da impostazioni
    let nome_attivita: String =
        sqlx::query_scalar("SELECT valore FROM impostazioni WHERE chiave = 'nome_attivita'")
            .fetch_optional(pool.inner())
            .await
            .map_err(|e| e.to_string())?
            .unwrap_or_else(|| "La Mia Attività".to_string());

    // ── Crea documento PDF A4 portrait ─────────────────────────────
    let (doc, page1, layer1) = PdfDocument::new(
        format!("Report Attività {} — {}", nome_attivita, &dati.mese_label),
        Mm(210.0),
        Mm(297.0),
        "Layer 1",
    );

    let font_bold = doc
        .add_builtin_font(BuiltinFont::HelveticaBold)
        .map_err(|e| format!("Font bold error: {e}"))?;
    let font = doc
        .add_builtin_font(BuiltinFont::Helvetica)
        .map_err(|e| format!("Font error: {e}"))?;

    let layer = doc.get_page(page1).get_layer(layer1);

    // ── Header ──────────────────────────────────────────────────────
    let today = chrono::Local::now().format("%d/%m/%Y").to_string();

    layer.use_text("FLUXION", 22.0, Mm(20.0), Mm(275.0), &font_bold);
    layer.use_text(
        format!("Report Attività — {}", dati.mese_label),
        13.0,
        Mm(20.0),
        Mm(265.0),
        &font_bold,
    );
    layer.use_text(
        format!("Attività: {}  |  Generato il: {}", nome_attivita, today),
        9.0,
        Mm(20.0),
        Mm(258.0),
        &font,
    );

    // Linea separatore header
    let sep = Line {
        points: vec![
            (Point::new(Mm(20.0), Mm(254.0)), false),
            (Point::new(Mm(190.0), Mm(254.0)), false),
        ],
        is_closed: false,
    };
    layer.add_line(sep);

    // ── Sezione 1: KPI Revenue ──────────────────────────────────────
    let mut y = 244.0f32;

    layer.use_text("REVENUE", 10.0, Mm(20.0), Mm(y), &font_bold);
    y -= 7.0;

    let delta_sign = if dati.revenue_delta_pct >= 0.0 {
        "+"
    } else {
        ""
    };
    let delta_label = if dati.revenue_mese_prec > 0.0 {
        format!(
            "  ({}{:.1}% vs mese prec.: {})",
            delta_sign,
            dati.revenue_delta_pct,
            format_eur(dati.revenue_mese_prec)
        )
    } else {
        "  (nessun dato mese precedente)".to_string()
    };

    layer.use_text(
        format!(
            "  Fatturato mese: {}{}",
            format_eur(dati.revenue_mese),
            delta_label
        ),
        10.0,
        Mm(20.0),
        Mm(y),
        &font,
    );
    y -= 12.0;

    // ── Sezione 2: Appuntamenti ─────────────────────────────────────
    layer.use_text("APPUNTAMENTI", 10.0, Mm(20.0), Mm(y), &font_bold);
    y -= 7.0;
    layer.use_text(
        format!(
            "  Totali: {}   Completati: {}   Confermati: {}   Cancellati: {}   No-show: {}",
            dati.appuntamenti_totali,
            dati.appuntamenti_completati,
            dati.appuntamenti_confermati,
            dati.appuntamenti_cancellati,
            dati.appuntamenti_no_show,
        ),
        9.5,
        Mm(20.0),
        Mm(y),
        &font,
    );
    y -= 12.0;

    // ── Sezione 3: Clienti ──────────────────────────────────────────
    layer.use_text("CLIENTI", 10.0, Mm(20.0), Mm(y), &font_bold);
    y -= 7.0;
    layer.use_text(
        format!(
            "  Nuovi (prima visita): {}   Ritorni: {}   Totale attivi: {}",
            dati.clienti_nuovi,
            dati.clienti_ritorni,
            dati.clienti_nuovi + dati.clienti_ritorni,
        ),
        9.5,
        Mm(20.0),
        Mm(y),
        &font,
    );
    y -= 12.0;

    // ── Sezione 4: Top 5 Servizi ────────────────────────────────────
    layer.use_text("TOP 5 SERVIZI", 10.0, Mm(20.0), Mm(y), &font_bold);
    y -= 2.0;

    // Colonne header
    let col_svc_x = 25.0f32;
    let col_cnt_x = 130.0f32;
    let col_rev_x = 155.0f32;

    y -= 5.5;
    layer.use_text("#", 8.5, Mm(20.0), Mm(y), &font_bold);
    layer.use_text("Servizio", 8.5, Mm(col_svc_x), Mm(y), &font_bold);
    layer.use_text("Prenotazioni", 8.5, Mm(col_cnt_x), Mm(y), &font_bold);
    layer.use_text("Revenue", 8.5, Mm(col_rev_x), Mm(y), &font_bold);
    y -= 1.5;

    let sep2 = Line {
        points: vec![
            (Point::new(Mm(20.0), Mm(y)), false),
            (Point::new(Mm(190.0), Mm(y)), false),
        ],
        is_closed: false,
    };
    layer.add_line(sep2);
    y -= 5.0;

    if dati.top_servizi.is_empty() {
        layer.use_text("  Nessun dato disponibile", 9.0, Mm(20.0), Mm(y), &font);
        y -= 7.0;
    } else {
        for (i, svc) in dati.top_servizi.iter().enumerate() {
            let nome_trunc: String = svc.nome.chars().take(45).collect();
            layer.use_text(format!("{}", i + 1), 9.0, Mm(20.0), Mm(y), &font);
            layer.use_text(&nome_trunc, 9.0, Mm(col_svc_x), Mm(y), &font);
            layer.use_text(
                format!("{}", svc.conteggio),
                9.0,
                Mm(col_cnt_x),
                Mm(y),
                &font,
            );
            layer.use_text(format_eur(svc.revenue), 9.0, Mm(col_rev_x), Mm(y), &font);
            y -= 5.5;
        }
    }
    y -= 4.0;

    // ── Sezione 5: Operatori ────────────────────────────────────────
    if y > 50.0 {
        layer.use_text("OPERATORI DEL MESE", 10.0, Mm(20.0), Mm(y), &font_bold);
        y -= 2.0;

        let col_op_x = 25.0f32;
        let col_op_cnt_x = 130.0f32;
        let col_op_rev_x = 155.0f32;

        y -= 5.5;
        layer.use_text("#", 8.5, Mm(20.0), Mm(y), &font_bold);
        layer.use_text("Operatore", 8.5, Mm(col_op_x), Mm(y), &font_bold);
        layer.use_text("Appuntamenti", 8.5, Mm(col_op_cnt_x), Mm(y), &font_bold);
        layer.use_text("Revenue", 8.5, Mm(col_op_rev_x), Mm(y), &font_bold);
        y -= 1.5;

        let sep3 = Line {
            points: vec![
                (Point::new(Mm(20.0), Mm(y)), false),
                (Point::new(Mm(190.0), Mm(y)), false),
            ],
            is_closed: false,
        };
        layer.add_line(sep3);
        y -= 5.0;

        if dati.top_operatori.is_empty() {
            layer.use_text("  Nessun dato disponibile", 9.0, Mm(20.0), Mm(y), &font);
            y -= 7.0;
        } else {
            for (i, op) in dati.top_operatori.iter().enumerate() {
                if y < 30.0 {
                    break;
                }
                let nome_trunc: String = op.nome_completo.chars().take(45).collect();
                layer.use_text(format!("{}", i + 1), 9.0, Mm(20.0), Mm(y), &font);
                layer.use_text(&nome_trunc, 9.0, Mm(col_op_x), Mm(y), &font);
                layer.use_text(
                    format!("{}", op.appuntamenti_completati),
                    9.0,
                    Mm(col_op_cnt_x),
                    Mm(y),
                    &font,
                );
                layer.use_text(format_eur(op.revenue), 9.0, Mm(col_op_rev_x), Mm(y), &font);
                y -= 5.5;
            }
        }
        y -= 4.0;
    }

    // ── Sezione 6: WA Confirm Rate ──────────────────────────────────
    if y > 30.0 {
        layer.use_text(
            "TASSO CONFERMA WHATSAPP (Gap #4)",
            10.0,
            Mm(20.0),
            Mm(y),
            &font_bold,
        );
        y -= 7.0;
        layer.use_text(
            format!(
                "  Confermati: {}   Cancellati: {}   Tasso conferma: {:.1}%",
                dati.wa_confermati, dati.wa_cancellati, dati.wa_confirm_rate,
            ),
            9.5,
            Mm(20.0),
            Mm(y),
            &font,
        );
    }

    // ── Footer ──────────────────────────────────────────────────────
    let sep_footer = Line {
        points: vec![
            (Point::new(Mm(20.0), Mm(15.0)), false),
            (Point::new(Mm(190.0), Mm(15.0)), false),
        ],
        is_closed: false,
    };
    layer.add_line(sep_footer);
    layer.use_text(
        format!(
            "FLUXION CRM — Software gestionale per PMI italiane  |  Generato il {}  |  {} {}",
            today, dati.mese_label, dati.anno
        ),
        7.0,
        Mm(20.0),
        Mm(9.0),
        &font,
    );

    // ── Salva in ~/Documents ─────────────────────────────────────────
    let documents_dir = dirs_next::document_dir()
        .or_else(|| app.path().app_data_dir().ok())
        .ok_or("Impossibile trovare cartella Documenti")?;

    let file_name = format!("Fluxion_Report_{:04}-{:02}.pdf", anno, mese);
    let pdf_path = documents_dir.join(&file_name);

    let file =
        std::fs::File::create(&pdf_path).map_err(|e| format!("Creazione file PDF fallita: {e}"))?;
    let mut writer = BufWriter::new(file);
    doc.save(&mut writer)
        .map_err(|e| format!("Salvataggio PDF fallito: {e}"))?;

    Ok(pdf_path.to_string_lossy().into_owned())
}

// ───────────────────────────────────────────────────────────────────
// Unit helpers (no DB) — tested inline
// ───────────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_mese_label() {
        assert_eq!(mese_label_it(2026, 3), "Marzo 2026");
        assert_eq!(mese_label_it(2026, 1), "Gennaio 2026");
        assert_eq!(mese_label_it(2026, 12), "Dicembre 2026");
    }

    #[test]
    fn test_prev_month() {
        assert_eq!(prev_month(2026, 3), (2026, 2));
        assert_eq!(prev_month(2026, 1), (2025, 12));
    }

    #[test]
    fn test_format_eur() {
        assert_eq!(format_eur(1234.56), "€1.234,56");
        assert_eq!(format_eur(0.0), "€0,00");
        assert_eq!(format_eur(1000.0), "€1.000,00");
    }
}
