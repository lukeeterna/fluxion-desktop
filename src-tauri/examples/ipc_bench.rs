// ═══════════════════════════════════════════════════════════════════
// S191 D-2 — IPC Latency Benchmark (handler-side, no WebView channel)
//
// Misura la latenza dei 3 IPC commands clienti più chiamati:
//   - get_clienti        (no args, returns Vec<Cliente>)
//   - get_cliente {id}   (returns Cliente)
//   - search_clienti {q} (returns Vec<Cliente>, max 50)
//
// Path misurato:
//   SqlitePool query → sqlx FromRow → Vec<Cliente> → serde_json::to_string
//
// Path NON misurato (overhead aggiuntivo lato Tauri runtime, da letteratura
// Tauri 2.x v2 IPC ~5-15ms per round-trip su WKWebView macOS):
//   WKWebView postMessage ↔ tauri-runtime ipc dispatch ↔ command resolver
//
// SLO Gate 3: P95 < 100 ms end-to-end. Anche includendo +15 ms di buffer
// per il channel WebView, il margine resta sufficiente se questo bench
// produce P95 ≤ 80 ms.
//
// Uso (su iMac dove Cargo build è possibile):
//   FLUXION_DB=/tmp/fluxion-perf.db cargo run --release --example ipc_bench
//
// Output:
//   stdout: tabella P50/P95/P99 + JSON dump
//   /tmp/fluxion-d2-results.json
// ═══════════════════════════════════════════════════════════════════

use std::time::Instant;

use serde::{Deserialize, Serialize};
use sqlx::sqlite::SqlitePoolOptions;
use sqlx::SqlitePool;

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::FromRow)]
struct Cliente {
    pub id: String,
    pub nome: String,
    pub cognome: String,
    pub soprannome: Option<String>,
    pub email: Option<String>,
    pub telefono: String,
    pub data_nascita: Option<String>,
    pub indirizzo: Option<String>,
    pub cap: Option<String>,
    pub citta: Option<String>,
    pub provincia: Option<String>,
    pub codice_fiscale: Option<String>,
    pub partita_iva: Option<String>,
    pub codice_sdi: Option<String>,
    pub pec: Option<String>,
    pub note: Option<String>,
    pub tags: Option<String>,
    pub fonte: Option<String>,
    pub consenso_marketing: i32,
    pub consenso_whatsapp: i32,
    pub data_consenso: Option<String>,
    pub loyalty_visits: Option<i32>,
    pub loyalty_threshold: Option<i32>,
    pub is_vip: Option<i32>,
    pub referral_source: Option<String>,
    pub referral_cliente_id: Option<String>,
    pub created_at: String,
    pub updated_at: String,
    pub deleted_at: Option<String>,
}

// Replica esatta di commands::clienti::get_clienti (lib.rs:116) escluso State<>.
async fn handler_get_clienti(pool: &SqlitePool) -> Result<Vec<Cliente>, String> {
    let clienti = sqlx::query_as::<_, Cliente>(
        r#"
        SELECT * FROM clienti
        WHERE deleted_at IS NULL
        ORDER BY cognome ASC, nome ASC
        "#,
    )
    .fetch_all(pool)
    .await
    .map_err(|e| format!("Database error: {}", e))?;
    Ok(clienti)
}

async fn handler_get_cliente(pool: &SqlitePool, id: &str) -> Result<Cliente, String> {
    let cliente = sqlx::query_as::<_, Cliente>(
        r#"
        SELECT * FROM clienti
        WHERE id = ? AND deleted_at IS NULL
        "#,
    )
    .bind(id)
    .fetch_one(pool)
    .await
    .map_err(|e| match e {
        sqlx::Error::RowNotFound => format!("Cliente non trovato: {}", id),
        _ => format!("Database error: {}", e),
    })?;
    Ok(cliente)
}

async fn handler_search_clienti(pool: &SqlitePool, query: &str) -> Result<Vec<Cliente>, String> {
    let pattern = format!("%{}%", query);
    let clienti = sqlx::query_as::<_, Cliente>(
        r#"
        SELECT * FROM clienti
        WHERE deleted_at IS NULL
        AND (
            nome LIKE ? OR
            cognome LIKE ? OR
            telefono LIKE ? OR
            email LIKE ?
        )
        ORDER BY cognome ASC, nome ASC
        LIMIT 50
        "#,
    )
    .bind(&pattern)
    .bind(&pattern)
    .bind(&pattern)
    .bind(&pattern)
    .fetch_all(pool)
    .await
    .map_err(|e| format!("Database error: {}", e))?;
    Ok(clienti)
}

fn percentile(mut values: Vec<f64>, p: f64) -> f64 {
    if values.is_empty() {
        return 0.0;
    }
    values.sort_by(|a, b| a.partial_cmp(b).unwrap());
    let k = (values.len() as f64 - 1.0) * (p / 100.0);
    let lo = k.floor() as usize;
    let hi = (lo + 1).min(values.len() - 1);
    values[lo] + (values[hi] - values[lo]) * (k - lo as f64)
}

#[derive(Serialize)]
struct CmdStats {
    name: String,
    n: usize,
    min_ms: f64,
    max_ms: f64,
    mean_ms: f64,
    stdev_ms: f64,
    p50_ms: f64,
    p95_ms: f64,
    p99_ms: f64,
    serialize_p50_ms: f64,
    serialize_p95_ms: f64,
    payload_bytes_p50: usize,
    payload_bytes_p95: usize,
    slo_ms: f64,
    verdict: String,
}

fn finalize(name: &str, samples: &[(f64, f64, usize)], slo_ms: f64) -> CmdStats {
    // samples: (handler_ms, serialize_ms, payload_bytes)
    let handler: Vec<f64> = samples.iter().map(|s| s.0).collect();
    let ser: Vec<f64> = samples.iter().map(|s| s.1).collect();
    let mut bytes: Vec<usize> = samples.iter().map(|s| s.2).collect();
    bytes.sort_unstable();

    let n = handler.len();
    let mean = handler.iter().sum::<f64>() / n as f64;
    let variance = handler.iter().map(|v| (*v - mean).powi(2)).sum::<f64>() / n as f64;
    let stdev = variance.sqrt();
    let pmin = handler.iter().cloned().fold(f64::INFINITY, f64::min);
    let pmax = handler.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
    let p50 = percentile(handler.clone(), 50.0);
    let p95 = percentile(handler.clone(), 95.0);
    let p99 = percentile(handler.clone(), 99.0);

    let ser_p50 = percentile(ser.clone(), 50.0);
    let ser_p95 = percentile(ser, 95.0);

    let pb_idx_p50 = (bytes.len() - 1) / 2;
    let pb_idx_p95 = ((bytes.len() as f64 - 1.0) * 0.95) as usize;
    let payload_p50 = bytes[pb_idx_p50];
    let payload_p95 = bytes[pb_idx_p95.min(bytes.len() - 1)];

    let total_p95 = p95 + ser_p95;
    let verdict = if total_p95 < slo_ms {
        "PASS".to_string()
    } else {
        "FAIL".to_string()
    };

    CmdStats {
        name: name.to_string(),
        n,
        min_ms: pmin,
        max_ms: pmax,
        mean_ms: mean,
        stdev_ms: stdev,
        p50_ms: p50,
        p95_ms: p95,
        p99_ms: p99,
        serialize_p50_ms: ser_p50,
        serialize_p95_ms: ser_p95,
        payload_bytes_p50: payload_p50,
        payload_bytes_p95: payload_p95,
        slo_ms,
        verdict,
    }
}

#[tokio::main(flavor = "current_thread")]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let db_path = std::env::var("FLUXION_DB").unwrap_or_else(|_| "/tmp/fluxion-perf.db".into());
    let url = format!("sqlite:{}?mode=rw", db_path);
    println!("[db] {}", url);

    let pool = SqlitePoolOptions::new()
        .max_connections(4)
        .connect(&url)
        .await?;

    let n_active: (i64,) = sqlx::query_as("SELECT COUNT(*) FROM clienti WHERE deleted_at IS NULL")
        .fetch_one(&pool)
        .await?;
    println!("[db] clienti attivi: {}", n_active.0);
    if n_active.0 < 100 {
        eprintln!(
            "WARN: dataset piccolo ({} record). Per misurare il caso 1000+ clienti rigenera DB con tools/perf-d1/audit.py",
            n_active.0
        );
    }

    // Pick sample IDs e search terms da DB reale
    let sample_ids: Vec<(String,)> =
        sqlx::query_as("SELECT id FROM clienti WHERE deleted_at IS NULL ORDER BY id LIMIT 100")
            .fetch_all(&pool)
            .await?;
    let ids: Vec<String> = sample_ids.into_iter().map(|t| t.0).collect();

    // Search terms: prefissi comuni nomi italiani
    let search_terms = vec![
        "ros", "bia", "ver", "rom", "mar", "gio", "lui", "mil", "tor", "nap",
    ];

    let warmup = 5usize;
    let iters = 100usize;

    // ── Bench 1: get_clienti ──────────────────────────────────────
    println!("\n[bench] get_clienti (warmup {} + iter {})", warmup, iters);
    for _ in 0..warmup {
        let _ = handler_get_clienti(&pool).await?;
    }
    let mut s_get_clienti: Vec<(f64, f64, usize)> = Vec::with_capacity(iters);
    for _ in 0..iters {
        let t0 = Instant::now();
        let res = handler_get_clienti(&pool).await?;
        let handler_ms = t0.elapsed().as_secs_f64() * 1000.0;
        let t1 = Instant::now();
        let json = serde_json::to_string(&res)?;
        let ser_ms = t1.elapsed().as_secs_f64() * 1000.0;
        s_get_clienti.push((handler_ms, ser_ms, json.len()));
    }

    // ── Bench 2: get_cliente ──────────────────────────────────────
    println!(
        "[bench] get_cliente by id (warmup {} + iter {})",
        warmup, iters
    );
    for i in 0..warmup {
        let _ = handler_get_cliente(&pool, &ids[i % ids.len()]).await?;
    }
    let mut s_get_cliente: Vec<(f64, f64, usize)> = Vec::with_capacity(iters);
    for i in 0..iters {
        let id = &ids[i % ids.len()];
        let t0 = Instant::now();
        let res = handler_get_cliente(&pool, id).await?;
        let handler_ms = t0.elapsed().as_secs_f64() * 1000.0;
        let t1 = Instant::now();
        let json = serde_json::to_string(&res)?;
        let ser_ms = t1.elapsed().as_secs_f64() * 1000.0;
        s_get_cliente.push((handler_ms, ser_ms, json.len()));
    }

    // ── Bench 3: search_clienti ───────────────────────────────────
    println!(
        "[bench] search_clienti (warmup {} + iter {})",
        warmup, iters
    );
    for i in 0..warmup {
        let _ = handler_search_clienti(&pool, search_terms[i % search_terms.len()]).await?;
    }
    let mut s_search: Vec<(f64, f64, usize)> = Vec::with_capacity(iters);
    for i in 0..iters {
        let q = search_terms[i % search_terms.len()];
        let t0 = Instant::now();
        let res = handler_search_clienti(&pool, q).await?;
        let handler_ms = t0.elapsed().as_secs_f64() * 1000.0;
        let t1 = Instant::now();
        let json = serde_json::to_string(&res)?;
        let ser_ms = t1.elapsed().as_secs_f64() * 1000.0;
        s_search.push((handler_ms, ser_ms, json.len()));
    }

    // SLO 100ms includono buffer 15ms WebView channel non misurato qui
    // → benchmark target effettivo: P95(handler+serialize) < 85ms
    let slo_handler_plus_serialize_ms = 85.0;

    let r1 = finalize("get_clienti", &s_get_clienti, slo_handler_plus_serialize_ms);
    let r2 = finalize("get_cliente", &s_get_cliente, slo_handler_plus_serialize_ms);
    let r3 = finalize("search_clienti", &s_search, slo_handler_plus_serialize_ms);

    println!("\n┌──────────────────┬──────┬──────┬──────┬──────────┬────────┬──────────┐");
    println!("│ command          │ P50  │ P95  │ P99  │ ser_P95  │ bytes  │ verdict  │");
    println!("├──────────────────┼──────┼──────┼──────┼──────────┼────────┼──────────┤");
    for r in &[&r1, &r2, &r3] {
        println!(
            "│ {:<16} │ {:>4.1} │ {:>4.1} │ {:>4.1} │ {:>8.2} │ {:>6} │ {:<8} │",
            r.name,
            r.p50_ms,
            r.p95_ms,
            r.p99_ms,
            r.serialize_p95_ms,
            r.payload_bytes_p95,
            r.verdict
        );
    }
    println!("└──────────────────┴──────┴──────┴──────┴──────────┴────────┴──────────┘");
    println!("(tutti i tempi in ms; SLO target = handler_p95 + serialize_p95 < 85 ms; +15 ms buffer per WebView channel = SLO Gate 3 100 ms)");

    let bundle = serde_json::json!({
        "ts": chrono::Utc::now().to_rfc3339(),
        "db": db_path,
        "n_clienti_active": n_active.0,
        "warmup": warmup,
        "iters": iters,
        "slo_ms_handler_plus_serialize": slo_handler_plus_serialize_ms,
        "slo_ms_total_gate3": 100.0,
        "webview_buffer_ms": 15.0,
        "results": [r1, r2, r3],
    });

    std::fs::write(
        "/tmp/fluxion-d2-results.json",
        serde_json::to_string_pretty(&bundle)?,
    )?;
    println!("\n[json] /tmp/fluxion-d2-results.json");

    Ok(())
}
