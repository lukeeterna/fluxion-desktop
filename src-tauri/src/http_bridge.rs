// ═══════════════════════════════════════════════════════════════════
// FLUXION - HTTP Bridge for MCP Integration
// Connects MCP Server (5000) to Tauri Commands via HTTP (3001)
// ═══════════════════════════════════════════════════════════════════

use axum::{
    extract::{Json, Query, State},
    http::StatusCode,
    response::IntoResponse,
    routing::{get, post},
    Router,
};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use sqlx::SqlitePool;
use tauri::{AppHandle, Manager, WebviewWindow};
use tower_http::cors::{Any, CorsLayer};

// ────────────────────────────────────────────────────────────────────
// Types
// ────────────────────────────────────────────────────────────────────

#[derive(Debug, Deserialize)]
#[allow(dead_code)]
pub struct McpRequest {
    pub command: Option<String>,
    pub params: Option<Value>,
}

#[derive(Debug, Serialize)]
pub struct McpResponse {
    pub success: bool,
    pub data: Option<Value>,
    pub error: Option<String>,
    pub timestamp: String,
}

impl McpResponse {
    fn ok(data: Value) -> Self {
        Self {
            success: true,
            data: Some(data),
            error: None,
            timestamp: chrono::Local::now().to_rfc3339(),
        }
    }

    fn err(msg: impl Into<String>) -> Self {
        Self {
            success: false,
            data: None,
            error: Some(msg.into()),
            timestamp: chrono::Local::now().to_rfc3339(),
        }
    }
}

#[derive(Clone)]
pub struct BridgeState {
    pub app: AppHandle,
}

// ────────────────────────────────────────────────────────────────────
// HTTP Bridge Server
// ────────────────────────────────────────────────────────────────────

pub async fn start_http_bridge(
    app: AppHandle,
) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    let state = BridgeState { app };

    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods(Any)
        .allow_headers(Any);

    let router = Router::new()
        // Health & Info
        .route("/health", get(handle_health))
        .route("/api/mcp/ping", post(handle_ping))
        .route("/api/mcp/app-info", post(handle_app_info))
        // Screenshot & DOM
        .route("/api/mcp/screenshot", post(handle_screenshot))
        .route("/api/mcp/dom-content", post(handle_dom_content))
        // Script Execution
        .route("/api/mcp/execute-script", post(handle_execute_script))
        // Input Simulation
        .route("/api/mcp/mouse-click", post(handle_mouse_click))
        .route("/api/mcp/type-text", post(handle_type_text))
        .route("/api/mcp/key-press", post(handle_key_press))
        // Storage
        .route("/api/mcp/storage/get", post(handle_storage_get))
        .route("/api/mcp/storage/set", post(handle_storage_set))
        .route("/api/mcp/storage/clear", post(handle_storage_clear))
        // Voice Agent API - Clienti
        .route("/api/clienti/search", get(handle_clienti_search))
        // Voice Agent API - Appuntamenti
        .route(
            "/api/appuntamenti/disponibilita",
            post(handle_disponibilita),
        )
        .route("/api/appuntamenti/create", post(handle_crea_appuntamento))
        .route(
            "/api/appuntamenti/cancel",
            post(handle_cancella_appuntamento),
        )
        .route(
            "/api/appuntamenti/reschedule",
            post(handle_sposta_appuntamento),
        )
        // Voice Agent API - Client Appointments (E4-S1)
        .route(
            "/api/appuntamenti/cliente/:client_id",
            get(handle_client_appointments),
        )
        // Voice Agent API - FAQ Settings
        .route("/api/faq/settings", get(handle_faq_settings))
        // Voice Agent API - Verticale Config (business settings)
        .route("/api/verticale/config", get(handle_verticale_config))
        // Voice Agent API - Operatori
        .route("/api/operatori/list", get(handle_operatori_list))
        .route(
            "/api/operatori/disponibilita",
            post(handle_operatori_disponibilita),
        )
        // Voice Agent API - Clienti Create
        .route("/api/clienti/create", post(handle_clienti_create))
        // Voice Agent API - Waitlist
        .route("/api/waitlist/add", post(handle_waitlist_add))
        // Settings API - SMTP
        .route("/api/settings/smtp", get(handle_smtp_settings))
        .with_state(state)
        .layer(cors);

    let listener = tokio::net::TcpListener::bind("127.0.0.1:3001").await?;

    println!("🌉 HTTP Bridge started on http://127.0.0.1:3001");
    println!("   Endpoints: /health, /api/mcp/*");

    axum::serve(listener, router).await?;

    Ok(())
}

// ────────────────────────────────────────────────────────────────────
// Helper: Get Main Window
// ────────────────────────────────────────────────────────────────────

fn get_main_window(app: &AppHandle) -> Option<WebviewWindow> {
    app.get_webview_window("main")
}

// ────────────────────────────────────────────────────────────────────
// Handler: Health Check
// ────────────────────────────────────────────────────────────────────

async fn handle_health() -> impl IntoResponse {
    (
        StatusCode::OK,
        Json(json!({
            "status": "ok",
            "service": "FLUXION HTTP Bridge",
            "timestamp": chrono::Local::now().to_rfc3339()
        })),
    )
}

// ────────────────────────────────────────────────────────────────────
// Handler: Ping
// ────────────────────────────────────────────────────────────────────

async fn handle_ping(State(_state): State<BridgeState>) -> impl IntoResponse {
    let response = McpResponse::ok(json!({
        "status": "ok",
        "server": "FLUXION",
        "bridge": "HTTP",
        "timestamp": chrono::Local::now().to_rfc3339()
    }));
    (StatusCode::OK, Json(response))
}

// ────────────────────────────────────────────────────────────────────
// Handler: App Info
// ────────────────────────────────────────────────────────────────────

async fn handle_app_info(State(_state): State<BridgeState>) -> impl IntoResponse {
    let response = McpResponse::ok(json!({
        "name": "FLUXION",
        "version": env!("CARGO_PKG_VERSION"),
        "platform": std::env::consts::OS,
        "arch": std::env::consts::ARCH
    }));
    (StatusCode::OK, Json(response))
}

// ────────────────────────────────────────────────────────────────────
// Handler: Screenshot
// ────────────────────────────────────────────────────────────────────

async fn handle_screenshot(State(state): State<BridgeState>) -> impl IntoResponse {
    let window = match get_main_window(&state.app) {
        Some(w) => w,
        None => {
            return (
                StatusCode::SERVICE_UNAVAILABLE,
                Json(McpResponse::err("Main window not available")),
            )
        }
    };

    match window.outer_size() {
        Ok(size) => {
            let response = McpResponse::ok(json!({
                "success": true,
                "width": size.width,
                "height": size.height,
                "message": "Window dimensions captured. Full screenshot requires screen-capture plugin."
            }));
            (StatusCode::OK, Json(response))
        }
        Err(e) => (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(McpResponse::err(format!(
                "Failed to get window size: {}",
                e
            ))),
        ),
    }
}

// ────────────────────────────────────────────────────────────────────
// Handler: DOM Content
// ────────────────────────────────────────────────────────────────────

async fn handle_dom_content(
    State(state): State<BridgeState>,
    Json(req): Json<McpRequest>,
) -> impl IntoResponse {
    let window = match get_main_window(&state.app) {
        Some(w) => w,
        None => {
            return (
                StatusCode::SERVICE_UNAVAILABLE,
                Json(McpResponse::err("Main window not available")),
            )
        }
    };

    let selector = req
        .params
        .as_ref()
        .and_then(|p| p.get("selector"))
        .and_then(|s| s.as_str());

    let js = if let Some(sel) = selector {
        format!(
            r#"
            (function() {{
                const el = document.querySelector('{}');
                if (el) {{
                    return el.outerHTML;
                }} else {{
                    return 'Element not found: {}';
                }}
            }})()
            "#,
            sel, sel
        )
    } else {
        r#"
        (function() {
            return document.documentElement.outerHTML;
        })()
        "#
        .to_string()
    };

    match window.eval(&js) {
        Ok(_) => {
            let response = McpResponse::ok(json!({
                "success": true,
                "selector": selector,
                "message": "DOM query executed"
            }));
            (StatusCode::OK, Json(response))
        }
        Err(e) => (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(McpResponse::err(format!("JS execution failed: {}", e))),
        ),
    }
}

// ────────────────────────────────────────────────────────────────────
// Handler: Execute Script
// ────────────────────────────────────────────────────────────────────

async fn handle_execute_script(
    State(state): State<BridgeState>,
    Json(req): Json<McpRequest>,
) -> impl IntoResponse {
    let window = match get_main_window(&state.app) {
        Some(w) => w,
        None => {
            return (
                StatusCode::SERVICE_UNAVAILABLE,
                Json(McpResponse::err("Main window not available")),
            )
        }
    };

    let script = req
        .params
        .as_ref()
        .and_then(|p| p.get("script"))
        .and_then(|s| s.as_str())
        .unwrap_or("")
        .to_string();

    if script.is_empty() {
        return (
            StatusCode::BAD_REQUEST,
            Json(McpResponse::err("Script is required")),
        );
    }

    match window.eval(&script) {
        Ok(_) => {
            let response = McpResponse::ok(json!({
                "success": true,
                "message": "Script executed successfully"
            }));
            (StatusCode::OK, Json(response))
        }
        Err(e) => (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(McpResponse::err(format!("Script error: {}", e))),
        ),
    }
}

// ────────────────────────────────────────────────────────────────────
// Handler: Mouse Click
// ────────────────────────────────────────────────────────────────────

async fn handle_mouse_click(
    State(state): State<BridgeState>,
    Json(req): Json<McpRequest>,
) -> impl IntoResponse {
    let window = match get_main_window(&state.app) {
        Some(w) => w,
        None => {
            return (
                StatusCode::SERVICE_UNAVAILABLE,
                Json(McpResponse::err("Main window not available")),
            )
        }
    };

    let params = req.params.unwrap_or_default();
    let x = params.get("x").and_then(|v| v.as_f64()).unwrap_or(0.0);
    let y = params.get("y").and_then(|v| v.as_f64()).unwrap_or(0.0);
    let button = params
        .get("button")
        .and_then(|v| v.as_str())
        .unwrap_or("left");

    let button_code = match button {
        "right" => 2,
        "middle" => 1,
        _ => 0,
    };

    let js = format!(
        r#"
        (function() {{
            const el = document.elementFromPoint({}, {});
            if (el) {{
                const event = new MouseEvent('click', {{
                    bubbles: true,
                    cancelable: true,
                    view: window,
                    clientX: {},
                    clientY: {},
                    button: {}
                }});
                el.dispatchEvent(event);
                return {{ success: true, element: el.tagName, id: el.id, className: el.className }};
            }} else {{
                return {{ success: false, error: 'No element at coordinates' }};
            }}
        }})()
        "#,
        x, y, x, y, button_code
    );

    match window.eval(&js) {
        Ok(_) => {
            let response = McpResponse::ok(json!({
                "success": true,
                "x": x,
                "y": y,
                "button": button
            }));
            (StatusCode::OK, Json(response))
        }
        Err(e) => (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(McpResponse::err(format!("Click simulation failed: {}", e))),
        ),
    }
}

// ────────────────────────────────────────────────────────────────────
// Handler: Type Text
// ────────────────────────────────────────────────────────────────────

async fn handle_type_text(
    State(state): State<BridgeState>,
    Json(req): Json<McpRequest>,
) -> impl IntoResponse {
    let window = match get_main_window(&state.app) {
        Some(w) => w,
        None => {
            return (
                StatusCode::SERVICE_UNAVAILABLE,
                Json(McpResponse::err("Main window not available")),
            )
        }
    };

    let text = req
        .params
        .as_ref()
        .and_then(|p| p.get("text"))
        .and_then(|s| s.as_str())
        .unwrap_or("")
        .to_string();

    let escaped_text = text
        .replace('\\', "\\\\")
        .replace('\'', "\\'")
        .replace('\n', "\\n");

    let js = format!(
        r#"
        (function() {{
            const el = document.activeElement;
            if (el && (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA' || el.isContentEditable)) {{
                if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {{
                    el.value += '{}';
                    el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                }} else {{
                    document.execCommand('insertText', false, '{}');
                }}
                return {{ success: true, element: el.tagName }};
            }} else {{
                return {{ success: false, error: 'No focusable element' }};
            }}
        }})()
        "#,
        escaped_text, escaped_text
    );

    match window.eval(&js) {
        Ok(_) => {
            let response = McpResponse::ok(json!({
                "success": true,
                "text": text,
                "length": text.len()
            }));
            (StatusCode::OK, Json(response))
        }
        Err(e) => (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(McpResponse::err(format!("Type text failed: {}", e))),
        ),
    }
}

// ────────────────────────────────────────────────────────────────────
// Handler: Key Press
// ────────────────────────────────────────────────────────────────────

async fn handle_key_press(
    State(state): State<BridgeState>,
    Json(req): Json<McpRequest>,
) -> impl IntoResponse {
    let window = match get_main_window(&state.app) {
        Some(w) => w,
        None => {
            return (
                StatusCode::SERVICE_UNAVAILABLE,
                Json(McpResponse::err("Main window not available")),
            )
        }
    };

    let params = req.params.unwrap_or_default();
    let key = params
        .get("key")
        .and_then(|s| s.as_str())
        .unwrap_or("")
        .to_string();

    let modifiers: Vec<String> = params
        .get("modifiers")
        .and_then(|m| m.as_array())
        .map(|arr| {
            arr.iter()
                .filter_map(|v| v.as_str().map(String::from))
                .collect()
        })
        .unwrap_or_default();

    let js = format!(
        r#"
        (function() {{
            const el = document.activeElement || document.body;
            const event = new KeyboardEvent('keydown', {{
                key: '{}',
                code: '{}',
                bubbles: true,
                cancelable: true,
                ctrlKey: {},
                shiftKey: {},
                altKey: {},
                metaKey: {}
            }});
            el.dispatchEvent(event);
            return {{ success: true, key: '{}', element: el.tagName }};
        }})()
        "#,
        key,
        key,
        modifiers.contains(&"Control".to_string()),
        modifiers.contains(&"Shift".to_string()),
        modifiers.contains(&"Alt".to_string()),
        modifiers.contains(&"Meta".to_string()),
        key
    );

    match window.eval(&js) {
        Ok(_) => {
            let response = McpResponse::ok(json!({
                "success": true,
                "key": key,
                "modifiers": modifiers
            }));
            (StatusCode::OK, Json(response))
        }
        Err(e) => (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(McpResponse::err(format!("Key press failed: {}", e))),
        ),
    }
}

// ────────────────────────────────────────────────────────────────────
// Handler: Storage Get
// ────────────────────────────────────────────────────────────────────

async fn handle_storage_get(
    State(state): State<BridgeState>,
    Json(req): Json<McpRequest>,
) -> impl IntoResponse {
    let window = match get_main_window(&state.app) {
        Some(w) => w,
        None => {
            return (
                StatusCode::SERVICE_UNAVAILABLE,
                Json(McpResponse::err("Main window not available")),
            )
        }
    };

    let key = req
        .params
        .as_ref()
        .and_then(|p| p.get("key"))
        .and_then(|s| s.as_str());

    let js = if let Some(k) = key {
        format!(
            r#"
            (function() {{
                return localStorage.getItem('{}');
            }})()
            "#,
            k
        )
    } else {
        r#"
        (function() {
            const items = {};
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                items[key] = localStorage.getItem(key);
            }
            return JSON.stringify(items);
        })()
        "#
        .to_string()
    };

    match window.eval(&js) {
        Ok(_) => {
            let response = McpResponse::ok(json!({
                "success": true,
                "key": key,
                "message": "Check console for localStorage value"
            }));
            (StatusCode::OK, Json(response))
        }
        Err(e) => (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(McpResponse::err(format!("Get localStorage failed: {}", e))),
        ),
    }
}

// ────────────────────────────────────────────────────────────────────
// Handler: Storage Set
// ────────────────────────────────────────────────────────────────────

async fn handle_storage_set(
    State(state): State<BridgeState>,
    Json(req): Json<McpRequest>,
) -> impl IntoResponse {
    let window = match get_main_window(&state.app) {
        Some(w) => w,
        None => {
            return (
                StatusCode::SERVICE_UNAVAILABLE,
                Json(McpResponse::err("Main window not available")),
            )
        }
    };

    let params = req.params.unwrap_or_default();
    let key = params
        .get("key")
        .and_then(|s| s.as_str())
        .unwrap_or("")
        .to_string();
    let value = params
        .get("value")
        .and_then(|s| s.as_str())
        .unwrap_or("")
        .to_string();

    let escaped_value = value.replace('\\', "\\\\").replace('\'', "\\'");

    let js = format!(
        r#"
        (function() {{
            localStorage.setItem('{}', '{}');
            return true;
        }})()
        "#,
        key, escaped_value
    );

    match window.eval(&js) {
        Ok(_) => {
            let response = McpResponse::ok(json!({
                "success": true,
                "key": key,
                "value": value
            }));
            (StatusCode::OK, Json(response))
        }
        Err(e) => (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(McpResponse::err(format!("Set localStorage failed: {}", e))),
        ),
    }
}

// ────────────────────────────────────────────────────────────────────
// Handler: Storage Clear
// ────────────────────────────────────────────────────────────────────

async fn handle_storage_clear(State(state): State<BridgeState>) -> impl IntoResponse {
    let window = match get_main_window(&state.app) {
        Some(w) => w,
        None => {
            return (
                StatusCode::SERVICE_UNAVAILABLE,
                Json(McpResponse::err("Main window not available")),
            )
        }
    };

    let js = r#"
        (function() {
            localStorage.clear();
            return true;
        })()
    "#;

    match window.eval(js) {
        Ok(_) => {
            let response = McpResponse::ok(json!({
                "success": true,
                "message": "localStorage cleared"
            }));
            (StatusCode::OK, Json(response))
        }
        Err(e) => (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(McpResponse::err(format!(
                "Clear localStorage failed: {}",
                e
            ))),
        ),
    }
}

// ────────────────────────────────────────────────────────────────────
// Voice Agent API Handlers
// ────────────────────────────────────────────────────────────────────

#[derive(Debug, Deserialize)]
struct ClientiSearchQuery {
    q: Option<String>,
    data_nascita: Option<String>, // YYYY-MM-DD fallback for disambiguation
}

/// Search clienti by name, surname, phone, email, soprannome, or data_nascita
/// Priority: nome → soprannome → data_nascita (fallback for disambiguation)
async fn handle_clienti_search(
    State(state): State<BridgeState>,
    Query(query): Query<ClientiSearchQuery>,
) -> impl IntoResponse {
    let search_term = query.q.unwrap_or_default();
    let data_nascita = query.data_nascita;

    if search_term.is_empty() && data_nascita.is_none() {
        return (StatusCode::OK, Json(json!([])));
    }

    // Get database pool from app state
    let pool = match state.app.try_state::<SqlitePool>() {
        Some(p) => p,
        None => {
            return (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(json!({"error": "Database not available"})),
            );
        }
    };

    // If data_nascita provided, use it for precise disambiguation
    if let Some(birth_date) = &data_nascita {
        let search_pattern = format!("%{}%", search_term);
        let result = sqlx::query_as::<_, ClienteRow>(
            r#"
            SELECT id, nome, cognome, telefono, email, soprannome, data_nascita
            FROM clienti
            WHERE deleted_at IS NULL
            AND data_nascita = ?
            AND (nome LIKE ? OR cognome LIKE ? OR soprannome LIKE ?)
            ORDER BY cognome ASC, nome ASC
            LIMIT 5
            "#,
        )
        .bind(birth_date)
        .bind(&search_pattern)
        .bind(&search_pattern)
        .bind(&search_pattern)
        .fetch_all(pool.inner())
        .await;

        return match result {
            Ok(clienti) => {
                let json_clienti: Vec<Value> = clienti
                    .iter()
                    .map(|c| {
                        json!({
                            "id": c.id,
                            "nome": c.nome,
                            "cognome": c.cognome,
                            "telefono": c.telefono,
                            "email": c.email,
                            "soprannome": c.soprannome,
                            "data_nascita": c.data_nascita
                        })
                    })
                    .collect();
                (StatusCode::OK, Json(json!(json_clienti)))
            }
            Err(e) => (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(json!({"error": format!("Database error: {}", e)})),
            ),
        };
    }

    // Standard search by name/phone/email/soprannome
    let search_pattern = format!("%{}%", search_term);

    let result = sqlx::query_as::<_, ClienteRow>(
        r#"
        SELECT id, nome, cognome, telefono, email, soprannome, data_nascita
        FROM clienti
        WHERE deleted_at IS NULL
        AND (
            nome LIKE ? OR
            cognome LIKE ? OR
            telefono LIKE ? OR
            email LIKE ? OR
            soprannome LIKE ?
        )
        ORDER BY cognome ASC, nome ASC
        LIMIT 10
        "#,
    )
    .bind(&search_pattern)
    .bind(&search_pattern)
    .bind(&search_pattern)
    .bind(&search_pattern)
    .bind(&search_pattern)
    .fetch_all(pool.inner())
    .await;

    match result {
        Ok(clienti) => {
            // If multiple results and no disambiguation, signal ambiguity
            let needs_disambiguation = clienti.len() > 1;
            let json_clienti: Vec<Value> = clienti
                .iter()
                .map(|c| {
                    json!({
                        "id": c.id,
                        "nome": c.nome,
                        "cognome": c.cognome,
                        "telefono": c.telefono,
                        "email": c.email,
                        "soprannome": c.soprannome,
                        "data_nascita": c.data_nascita
                    })
                })
                .collect();
            (
                StatusCode::OK,
                Json(json!({
                    "clienti": json_clienti,
                    "ambiguo": needs_disambiguation,
                    "messaggio": if needs_disambiguation {
                        "Trovati più clienti. Chiedi la data di nascita per disambiguare."
                    } else {
                        ""
                    }
                })),
            )
        }
        Err(e) => (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(json!({"error": format!("Database error: {}", e)})),
        ),
    }
}

#[derive(Debug, sqlx::FromRow)]
struct ClienteRow {
    id: String,
    nome: String,
    cognome: Option<String>,
    telefono: Option<String>,
    email: Option<String>,
    soprannome: Option<String>,
    data_nascita: Option<String>,
}

#[derive(Debug, Deserialize)]
struct DisponibilitaRequest {
    data: String,
    servizio: String,
}

/// Get available time slots for a date
async fn handle_disponibilita(
    State(state): State<BridgeState>,
    Json(req): Json<DisponibilitaRequest>,
) -> impl IntoResponse {
    // Get database pool
    let pool = match state.app.try_state::<SqlitePool>() {
        Some(p) => p,
        None => {
            return (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(json!({"error": "Database not available"})),
            );
        }
    };

    // Get busy slots for the date (extract time HH:MM from data_ora_inizio)
    // data_ora_inizio format: YYYY-MM-DDTHH:MM:SS
    let busy_slots: Vec<String> = sqlx::query_scalar(
        r#"
        SELECT substr(data_ora_inizio, 12, 5) as ora
        FROM appuntamenti
        WHERE date(data_ora_inizio) = ? AND stato NOT IN ('cancellato', 'no_show')
        "#,
    )
    .bind(&req.data)
    .fetch_all(pool.inner())
    .await
    .unwrap_or_default();

    // Generate available slots (09:00 - 19:00, every 30 min)
    let all_slots = vec![
        "09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "14:00", "14:30",
        "15:00", "15:30", "16:00", "16:30", "17:00", "17:30", "18:00", "18:30",
    ];

    let available: Vec<&str> = all_slots
        .into_iter()
        .filter(|s| !busy_slots.contains(&s.to_string()))
        .collect();

    (StatusCode::OK, Json(json!({ "slots": available })))
}

#[derive(Debug, Deserialize)]
struct CreaAppuntamentoRequest {
    cliente_id: String,
    servizio: String,
    data: String,
    ora: String,
    operatore_id: Option<String>, // Operator preference
}

/// Create a new appointment
async fn handle_crea_appuntamento(
    State(state): State<BridgeState>,
    Json(req): Json<CreaAppuntamentoRequest>,
) -> impl IntoResponse {
    // Get database pool
    let pool = match state.app.try_state::<SqlitePool>() {
        Some(p) => p,
        None => {
            return (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(json!({"success": false, "error": "Database not available"})),
            );
        }
    };

    // Generate new ID
    let id = uuid::Uuid::new_v4().to_string();
    let now = chrono::Local::now().to_rfc3339();

    // Get service info (ID, durata, prezzo)
    let service_info: Option<(String, i32, f64)> =
        sqlx::query_as("SELECT id, durata_minuti, prezzo FROM servizi WHERE nome LIKE ? LIMIT 1")
            .bind(format!("%{}%", req.servizio))
            .fetch_optional(pool.inner())
            .await
            .ok()
            .flatten();

    let (servizio_id, durata_minuti, prezzo) =
        service_info.unwrap_or_else(|| ("srv-default".to_string(), 30, 25.0));

    // Build data_ora_inizio (ISO 8601: YYYY-MM-DDTHH:MM:SS)
    let data_ora_inizio = format!("{}T{}:00", req.data, req.ora);

    // Calculate data_ora_fine
    let start_time = chrono::NaiveDateTime::parse_from_str(&data_ora_inizio, "%Y-%m-%dT%H:%M:%S")
        .unwrap_or_else(|_| chrono::Local::now().naive_local());
    let end_time = start_time + chrono::Duration::minutes(durata_minuti as i64);
    let data_ora_fine = end_time.format("%Y-%m-%dT%H:%M:%S").to_string();

    // Insert appointment with correct schema (including operatore_id)
    let result = sqlx::query(
        r#"
        INSERT INTO appuntamenti (
            id, cliente_id, servizio_id, operatore_id,
            data_ora_inizio, data_ora_fine, durata_minuti,
            stato, prezzo, sconto_percentuale, prezzo_finale,
            fonte_prenotazione, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, 'confermato', ?, 0, ?, 'voice', ?)
        "#,
    )
    .bind(&id)
    .bind(&req.cliente_id)
    .bind(&servizio_id)
    .bind(&req.operatore_id) // Operator preference (optional)
    .bind(&data_ora_inizio)
    .bind(&data_ora_fine)
    .bind(durata_minuti)
    .bind(prezzo)
    .bind(prezzo) // prezzo_finale = prezzo (no sconto)
    .bind(&now)
    .execute(pool.inner())
    .await;

    match result {
        Ok(_) => (
            StatusCode::OK,
            Json(json!({
                "success": true,
                "id": id,
                "message": format!("Appuntamento creato per {} alle {}", req.data, req.ora)
            })),
        ),
        Err(e) => (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(json!({
                "success": false,
                "error": format!("Failed to create appointment: {}", e)
            })),
        ),
    }
}

// ────────────────────────────────────────────────────────────────────
// Handler: Cancel Appointment (Soft Delete)
// ────────────────────────────────────────────────────────────────────

#[derive(Deserialize)]
struct CancellaAppuntamentoRequest {
    id: String,
}

/// Cancel an appointment (soft delete: sets stato = 'Cancellato')
async fn handle_cancella_appuntamento(
    State(state): State<BridgeState>,
    Json(req): Json<CancellaAppuntamentoRequest>,
) -> impl IntoResponse {
    let pool = match state.app.try_state::<SqlitePool>() {
        Some(p) => p,
        None => {
            return (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(json!({"success": false, "error": "Database not available"})),
            );
        }
    };

    let now = chrono::Local::now().to_rfc3339();

    let result = sqlx::query(
        "UPDATE appuntamenti SET stato = 'Cancellato', deleted_at = ?, updated_at = ? WHERE id = ?",
    )
    .bind(&now)
    .bind(&now)
    .bind(&req.id)
    .execute(pool.inner())
    .await;

    match result {
        Ok(r) => {
            if r.rows_affected() > 0 {
                (
                    StatusCode::OK,
                    Json(json!({
                        "success": true,
                        "message": "Appuntamento cancellato con successo"
                    })),
                )
            } else {
                (
                    StatusCode::NOT_FOUND,
                    Json(json!({
                        "success": false,
                        "error": "Appuntamento non trovato"
                    })),
                )
            }
        }
        Err(e) => (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(json!({
                "success": false,
                "error": format!("Errore cancellazione: {}", e)
            })),
        ),
    }
}

// ────────────────────────────────────────────────────────────────────
// Handler: Reschedule Appointment
// ────────────────────────────────────────────────────────────────────

#[derive(Deserialize)]
struct SpostaAppuntamentoRequest {
    id: String,
    data: String,
    ora: String,
}

/// Reschedule an appointment to a new date/time
async fn handle_sposta_appuntamento(
    State(state): State<BridgeState>,
    Json(req): Json<SpostaAppuntamentoRequest>,
) -> impl IntoResponse {
    let pool = match state.app.try_state::<SqlitePool>() {
        Some(p) => p,
        None => {
            return (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(json!({"success": false, "error": "Database not available"})),
            );
        }
    };

    // Get current appointment to preserve durata
    let existing: Option<(i32,)> =
        sqlx::query_as("SELECT durata_minuti FROM appuntamenti WHERE id = ?")
            .bind(&req.id)
            .fetch_optional(pool.inner())
            .await
            .ok()
            .flatten();

    let durata_minuti = existing.map(|e| e.0).unwrap_or(30);

    // Calculate new times
    let data_ora_inizio = format!("{}T{}:00", req.data, req.ora);
    let start_time = chrono::NaiveDateTime::parse_from_str(&data_ora_inizio, "%Y-%m-%dT%H:%M:%S")
        .unwrap_or_else(|_| chrono::Local::now().naive_local());
    let end_time = start_time + chrono::Duration::minutes(durata_minuti as i64);
    let data_ora_fine = end_time.format("%Y-%m-%dT%H:%M:%S").to_string();
    let now = chrono::Local::now().to_rfc3339();

    let result = sqlx::query(
        "UPDATE appuntamenti SET data_ora_inizio = ?, data_ora_fine = ?, updated_at = ? WHERE id = ?",
    )
    .bind(&data_ora_inizio)
    .bind(&data_ora_fine)
    .bind(&now)
    .bind(&req.id)
    .execute(pool.inner())
    .await;

    match result {
        Ok(r) => {
            if r.rows_affected() > 0 {
                (
                    StatusCode::OK,
                    Json(json!({
                        "success": true,
                        "message": format!("Appuntamento spostato a {} alle {}", req.data, req.ora)
                    })),
                )
            } else {
                (
                    StatusCode::NOT_FOUND,
                    Json(json!({
                        "success": false,
                        "error": "Appuntamento non trovato"
                    })),
                )
            }
        }
        Err(e) => (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(json!({
                "success": false,
                "error": format!("Errore spostamento: {}", e)
            })),
        ),
    }
}

// ────────────────────────────────────────────────────────────────────
// Handler: Get Client Appointments (E4-S1)
// ────────────────────────────────────────────────────────────────────

/// Get upcoming appointments for a specific client
async fn handle_client_appointments(
    State(state): State<BridgeState>,
    axum::extract::Path(client_id): axum::extract::Path<String>,
) -> impl IntoResponse {
    let pool = match state.app.try_state::<SqlitePool>() {
        Some(p) => p,
        None => {
            return (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(json!({"appointments": [], "error": "Database not available"})),
            );
        }
    };

    // Get upcoming appointments (not cancelled, from today onwards)
    let today = chrono::Local::now().format("%Y-%m-%d").to_string();

    let appointments: Vec<(
        String,
        String,
        String,
        Option<String>,
        String,
        Option<String>,
    )> = sqlx::query_as(
        r#"
        SELECT
            a.id,
            date(a.data_ora_inizio) as data,
            time(a.data_ora_inizio) as ora,
            s.nome as servizio,
            a.stato,
            o.nome as operatore_nome
        FROM appuntamenti a
        LEFT JOIN servizi s ON a.servizio_id = s.id
        LEFT JOIN operatori o ON a.operatore_id = o.id
        WHERE a.cliente_id = ?
          AND a.stato != 'Cancellato'
          AND date(a.data_ora_inizio) >= ?
        ORDER BY a.data_ora_inizio ASC
        LIMIT 10
        "#,
    )
    .bind(&client_id)
    .bind(&today)
    .fetch_all(pool.inner())
    .await
    .unwrap_or_default();

    let result: Vec<serde_json::Value> = appointments
        .into_iter()
        .map(|(id, data, ora, servizio, stato, operatore)| {
            json!({
                "id": id,
                "data": data,
                "ora": ora,
                "servizio": servizio.unwrap_or_else(|| "Servizio".to_string()),
                "stato": stato,
                "operatore_nome": operatore
            })
        })
        .collect();

    (
        StatusCode::OK,
        Json(json!({
            "appointments": result,
            "count": result.len()
        })),
    )
}

/// Get all FAQ settings for template substitution
async fn handle_faq_settings(State(state): State<BridgeState>) -> impl IntoResponse {
    // Get database pool
    let pool = match state.app.try_state::<SqlitePool>() {
        Some(p) => p,
        None => {
            return (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(json!({"error": "Database not available"})),
            );
        }
    };

    // Query all faq_settings as key-value pairs
    let settings: Vec<(String, String)> =
        sqlx::query_as("SELECT chiave, valore FROM faq_settings ORDER BY chiave")
            .fetch_all(pool.inner())
            .await
            .unwrap_or_default();

    // Convert to object
    let mut result = serde_json::Map::new();
    for (key, value) in settings {
        result.insert(key, serde_json::Value::String(value));
    }

    (StatusCode::OK, Json(serde_json::Value::Object(result)))
}

// ────────────────────────────────────────────────────────────────────
// Handler: Verticale Config (Business Settings)
// ────────────────────────────────────────────────────────────────────

/// Get business configuration from impostazioni table
/// Returns: nome_attivita, orario_apertura, orario_chiusura, giorni_lavorativi, servizi
async fn handle_verticale_config(State(state): State<BridgeState>) -> impl IntoResponse {
    let pool = match state.app.try_state::<SqlitePool>() {
        Some(p) => p,
        None => {
            return (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(json!({"error": "Database not available"})),
            );
        }
    };

    // Helper to get a setting
    async fn get_setting(pool: &SqlitePool, chiave: &str) -> Option<String> {
        let result: Option<(String,)> =
            sqlx::query_as("SELECT valore FROM impostazioni WHERE chiave = ?")
                .bind(chiave)
                .fetch_optional(pool)
                .await
                .ok()?;
        result.map(|(v,)| v)
    }

    // Load all business settings
    let nome_attivita = get_setting(pool.inner(), "nome_attivita")
        .await
        .unwrap_or_else(|| "La tua attivita".to_string());

    let orario_apertura = get_setting(pool.inner(), "orario_apertura")
        .await
        .unwrap_or_else(|| "09:00".to_string());

    let orario_chiusura = get_setting(pool.inner(), "orario_chiusura")
        .await
        .unwrap_or_else(|| "19:00".to_string());

    let giorni_lavorativi = get_setting(pool.inner(), "giorni_lavorativi")
        .await
        .unwrap_or_else(|| "Lunedi-Sabato".to_string());

    let categoria_attivita = get_setting(pool.inner(), "categoria_attivita")
        .await
        .unwrap_or_else(|| "salone".to_string());

    // Default services based on category
    let servizi = match categoria_attivita.as_str() {
        "salone" => vec!["Taglio", "Piega", "Colore", "Barba", "Trattamento"],
        "auto" => vec!["Tagliando", "Revisione", "Riparazione", "Carrozzeria"],
        "wellness" => vec!["Massaggio", "Trattamento viso", "Manicure", "Pedicure"],
        "medical" => vec!["Visita", "Controllo", "Esame", "Terapia"],
        _ => vec!["Servizio 1", "Servizio 2", "Servizio 3"],
    };

    // Groq API key configurata dal wizard (Step 7) — usata come fallback da voice agent
    let groq_api_key = get_setting(pool.inner(), "groq_api_key")
        .await
        .unwrap_or_default();

    (
        StatusCode::OK,
        Json(json!({
            "nome_attivita": nome_attivita,
            "orario_apertura": orario_apertura,
            "orario_chiusura": orario_chiusura,
            "giorni_lavorativi": giorni_lavorativi,
            "categoria_attivita": categoria_attivita,
            "servizi": servizi,
            "groq_api_key": groq_api_key
        })),
    )
}

// ────────────────────────────────────────────────────────────────────
// Handler: Operatori List
// ────────────────────────────────────────────────────────────────────

#[derive(Debug, sqlx::FromRow)]
struct OperatoreRow {
    id: String,
    nome: String,
    cognome: Option<String>,
    specializzazioni: Option<String>,
    descrizione_positiva: Option<String>,
    anni_esperienza: Option<i32>,
}

/// List all active operators with their specializations and descriptions
async fn handle_operatori_list(State(state): State<BridgeState>) -> impl IntoResponse {
    let pool = match state.app.try_state::<SqlitePool>() {
        Some(p) => p,
        None => {
            return (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(json!({"error": "Database not available"})),
            );
        }
    };

    let result = sqlx::query_as::<_, OperatoreRow>(
        r#"
        SELECT id, nome, cognome, specializzazioni, descrizione_positiva, anni_esperienza
        FROM operatori
        WHERE attivo = 1
        ORDER BY nome ASC
        "#,
    )
    .fetch_all(pool.inner())
    .await;

    match result {
        Ok(operatori) => {
            let json_operatori: Vec<Value> = operatori
                .iter()
                .map(|o| {
                    // Parse specializzazioni JSON array
                    let specs: Vec<String> = o
                        .specializzazioni
                        .as_ref()
                        .and_then(|s| serde_json::from_str(s).ok())
                        .unwrap_or_default();

                    json!({
                        "id": o.id,
                        "nome": o.nome,
                        "cognome": o.cognome,
                        "specializzazioni": specs,
                        "descrizione_positiva": o.descrizione_positiva,
                        "anni_esperienza": o.anni_esperienza.unwrap_or(0)
                    })
                })
                .collect();
            (StatusCode::OK, Json(json!(json_operatori)))
        }
        Err(e) => (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(json!({"error": format!("Database error: {}", e)})),
        ),
    }
}

// ────────────────────────────────────────────────────────────────────
// Handler: Operatore Disponibilità
// ────────────────────────────────────────────────────────────────────

#[derive(Debug, Deserialize)]
struct OperatoreDisponibilitaRequest {
    operatore_id: String,
    data: String,
    ora: Option<String>,
}

/// Check operator availability for a specific date (and optionally time)
async fn handle_operatori_disponibilita(
    State(state): State<BridgeState>,
    Json(req): Json<OperatoreDisponibilitaRequest>,
) -> impl IntoResponse {
    let pool = match state.app.try_state::<SqlitePool>() {
        Some(p) => p,
        None => {
            return (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(json!({"error": "Database not available"})),
            );
        }
    };

    // Get all appointments for this operator on this date
    let busy_slots: Vec<String> = sqlx::query_scalar(
        r#"
        SELECT substr(data_ora_inizio, 12, 5) as ora
        FROM appuntamenti
        WHERE operatore_id = ?
        AND date(data_ora_inizio) = ?
        AND stato NOT IN ('cancellato', 'no_show')
        "#,
    )
    .bind(&req.operatore_id)
    .bind(&req.data)
    .fetch_all(pool.inner())
    .await
    .unwrap_or_default();

    // If specific time requested, check if available
    if let Some(ora) = &req.ora {
        let is_available = !busy_slots.contains(ora);
        return (
            StatusCode::OK,
            Json(json!({
                "operatore_id": req.operatore_id,
                "data": req.data,
                "ora": ora,
                "disponibile": is_available
            })),
        );
    }

    // Otherwise return all available slots for this operator
    let all_slots = vec![
        "09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "14:00", "14:30",
        "15:00", "15:30", "16:00", "16:30", "17:00", "17:30", "18:00", "18:30",
    ];

    let available: Vec<&str> = all_slots
        .into_iter()
        .filter(|s| !busy_slots.contains(&s.to_string()))
        .collect();

    // If no available slots, suggest alternatives
    if available.is_empty() {
        // Get other available operators
        let alternatives =
            get_alternative_operators(pool.inner(), &req.data, &req.operatore_id).await;
        return (
            StatusCode::OK,
            Json(json!({
                "operatore_id": req.operatore_id,
                "data": req.data,
                "disponibile": false,
                "slots": [],
                "alternative_operators": alternatives
            })),
        );
    }

    (
        StatusCode::OK,
        Json(json!({
            "operatore_id": req.operatore_id,
            "data": req.data,
            "disponibile": true,
            "slots": available
        })),
    )
}

/// Get alternative operators with positive descriptions
async fn get_alternative_operators(pool: &SqlitePool, data: &str, exclude_id: &str) -> Vec<Value> {
    // Get all active operators except the excluded one
    let operators: Vec<OperatoreRow> = sqlx::query_as(
        r#"
        SELECT id, nome, cognome, specializzazioni, descrizione_positiva, anni_esperienza
        FROM operatori
        WHERE attivo = 1 AND id != ?
        ORDER BY anni_esperienza DESC
        "#,
    )
    .bind(exclude_id)
    .fetch_all(pool)
    .await
    .unwrap_or_default();

    let mut alternatives = Vec::new();

    for op in operators {
        // Check this operator's availability
        let busy_slots: Vec<String> = sqlx::query_scalar(
            r#"
            SELECT substr(data_ora_inizio, 12, 5) as ora
            FROM appuntamenti
            WHERE operatore_id = ?
            AND date(data_ora_inizio) = ?
            AND stato NOT IN ('cancellato', 'no_show')
            "#,
        )
        .bind(&op.id)
        .bind(data)
        .fetch_all(pool)
        .await
        .unwrap_or_default();

        let all_slots = vec![
            "09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "14:00",
            "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30", "18:00", "18:30",
        ];

        let available: Vec<&str> = all_slots
            .into_iter()
            .filter(|s| !busy_slots.contains(&s.to_string()))
            .collect();

        if !available.is_empty() {
            let specs: Vec<String> = op
                .specializzazioni
                .as_ref()
                .and_then(|s| serde_json::from_str(s).ok())
                .unwrap_or_default();

            alternatives.push(json!({
                "id": op.id,
                "nome": op.nome,
                "cognome": op.cognome,
                "specializzazioni": specs,
                "descrizione_positiva": op.descrizione_positiva,
                "anni_esperienza": op.anni_esperienza.unwrap_or(0),
                "slots_disponibili": available
            }));
        }
    }

    alternatives
}

// ────────────────────────────────────────────────────────────────────
// Handler: Clienti Create
// ────────────────────────────────────────────────────────────────────

#[derive(Debug, Deserialize)]
struct ClienteCreateRequest {
    nome: String,
    cognome: Option<String>,
    telefono: Option<String>,
    email: Option<String>,
    data_nascita: Option<String>,
    soprannome: Option<String>,
    note: Option<String>,
}

/// Create a new cliente (from Voice Agent or WhatsApp)
async fn handle_clienti_create(
    State(state): State<BridgeState>,
    Json(req): Json<ClienteCreateRequest>,
) -> impl IntoResponse {
    let pool = match state.app.try_state::<SqlitePool>() {
        Some(p) => p,
        None => {
            return (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(json!({"success": false, "error": "Database not available"})),
            );
        }
    };

    let id = uuid::Uuid::new_v4().to_string();
    let now = chrono::Local::now().to_rfc3339();

    let result = sqlx::query(
        r#"
        INSERT INTO clienti (
            id, nome, cognome, telefono, email, data_nascita, soprannome, note, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        "#,
    )
    .bind(&id)
    .bind(&req.nome)
    .bind(&req.cognome)
    .bind(&req.telefono)
    .bind(&req.email)
    .bind(&req.data_nascita)
    .bind(&req.soprannome)
    .bind(&req.note)
    .bind(&now)
    .execute(pool.inner())
    .await;

    match result {
        Ok(_) => (
            StatusCode::OK,
            Json(json!({
                "success": true,
                "id": id,
                "message": format!("Cliente {} creato con successo", req.nome)
            })),
        ),
        Err(e) => (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(json!({
                "success": false,
                "error": format!("Failed to create cliente: {}", e)
            })),
        ),
    }
}

// ────────────────────────────────────────────────────────────────────
// Handler: Waitlist Add
// ────────────────────────────────────────────────────────────────────

#[derive(Debug, Deserialize)]
struct WaitlistAddRequest {
    cliente_id: String,
    servizio: String,                    // Service name (we'll look up servizio_id)
    data_preferita: Option<String>,      // YYYY-MM-DD
    ora_preferita: Option<String>,       // HH:MM
    operatore_preferito: Option<String>, // Operator ID
    priorita: Option<String>,            // "normale", "vip", "urgente"
}

/// Add cliente to waitlist with optional VIP priority
/// Compatible with legacy schema (migration 005)
async fn handle_waitlist_add(
    State(state): State<BridgeState>,
    Json(req): Json<WaitlistAddRequest>,
) -> impl IntoResponse {
    let pool = match state.app.try_state::<SqlitePool>() {
        Some(p) => p,
        None => {
            return (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(json!({"success": false, "error": "Database not available"})),
            );
        }
    };

    // Look up servizio_id from servizio name
    let servizio_id: Option<(String,)> =
        sqlx::query_as("SELECT id FROM servizi WHERE nome LIKE ? LIMIT 1")
            .bind(format!("%{}%", req.servizio))
            .fetch_optional(pool.inner())
            .await
            .ok()
            .flatten();

    let servizio_id = servizio_id
        .map(|s| s.0)
        .unwrap_or_else(|| "srv-default".to_string());

    // Get default operator if not specified
    let operatore_id = match &req.operatore_preferito {
        Some(op) => op.clone(),
        None => {
            // Get first available operator
            let op: Option<(String,)> =
                sqlx::query_as("SELECT id FROM operatori WHERE attivo = 1 LIMIT 1")
                    .fetch_optional(pool.inner())
                    .await
                    .ok()
                    .flatten();
            op.map(|o| o.0).unwrap_or_else(|| "op-default".to_string())
        }
    };

    let id = uuid::Uuid::new_v4().to_string();
    let priorita_str = req.priorita.unwrap_or_else(|| "normale".to_string());

    // Map priority string to numeric value for legacy schema
    let priorita: i32 = match priorita_str.as_str() {
        "urgente" => 100,
        "vip" => 50,
        _ => 1,
    };

    // Use legacy schema column names
    let data_richiesta = req
        .data_preferita
        .unwrap_or_else(|| chrono::Local::now().format("%Y-%m-%d").to_string());
    let ora_richiesta = req.ora_preferita.unwrap_or_else(|| "09:00".to_string());

    let result = sqlx::query(
        r#"
        INSERT INTO waitlist (
            id, cliente_id, operatore_id, servizio_id,
            data_richiesta, ora_richiesta, priorita, stato
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, 'attivo')
        "#,
    )
    .bind(&id)
    .bind(&req.cliente_id)
    .bind(&operatore_id)
    .bind(&servizio_id)
    .bind(&data_richiesta)
    .bind(&ora_richiesta)
    .bind(priorita)
    .execute(pool.inner())
    .await;

    match result {
        Ok(_) => {
            let msg = match priorita_str.as_str() {
                "vip" => "Aggiunto alla lista d'attesa con priorità VIP",
                "urgente" => "Aggiunto alla lista d'attesa con priorità URGENTE",
                _ => "Aggiunto alla lista d'attesa",
            };
            (
                StatusCode::OK,
                Json(json!({
                    "success": true,
                    "id": id,
                    "priorita": priorita_str,
                    "message": msg
                })),
            )
        }
        Err(e) => (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(json!({
                "success": false,
                "error": format!("Failed to add to waitlist: {}", e)
            })),
        ),
    }
}

// ────────────────────────────────────────────────────────────────────
// Handler: SMTP Settings
// ────────────────────────────────────────────────────────────────────

async fn handle_smtp_settings(State(state): State<BridgeState>) -> impl IntoResponse {
    let pool = match state.app.try_state::<SqlitePool>() {
        Some(p) => p,
        None => {
            return (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(json!({"error": "Database not available"})),
            );
        }
    };

    // Helper to get setting
    async fn get_setting(pool: &SqlitePool, chiave: &str) -> Option<String> {
        let result: Option<(String,)> =
            sqlx::query_as("SELECT valore FROM impostazioni WHERE chiave = ?")
                .bind(chiave)
                .fetch_optional(pool)
                .await
                .ok()?;
        result.map(|(v,)| v)
    }

    let smtp_host = get_setting(pool.inner(), "smtp_host")
        .await
        .unwrap_or_else(|| "smtp.gmail.com".to_string());
    let smtp_port = get_setting(pool.inner(), "smtp_port")
        .await
        .and_then(|v| v.parse::<i32>().ok())
        .unwrap_or(587);
    let smtp_email_from = get_setting(pool.inner(), "smtp_email_from")
        .await
        .unwrap_or_default();
    let smtp_password = get_setting(pool.inner(), "smtp_password")
        .await
        .unwrap_or_default();
    let smtp_enabled = get_setting(pool.inner(), "smtp_enabled")
        .await
        .map(|v| v == "true")
        .unwrap_or(false);

    (
        StatusCode::OK,
        Json(json!({
            "smtp_host": smtp_host,
            "smtp_port": smtp_port,
            "smtp_email_from": smtp_email_from,
            "smtp_password": smtp_password,
            "smtp_enabled": smtp_enabled
        })),
    )
}
