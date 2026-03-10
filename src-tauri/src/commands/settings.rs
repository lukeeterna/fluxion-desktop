// ═══════════════════════════════════════════════════════════════════
// FLUXION - Settings Commands
// Gestione impostazioni configurabili via UI
// ═══════════════════════════════════════════════════════════════════

use base64::{engine::general_purpose::URL_SAFE_NO_PAD, Engine};
use rand::RngCore;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use sqlx::SqlitePool;
use std::sync::Arc;
use tauri::{AppHandle, Emitter, State};
use tokio::sync::Mutex as TokioMutex;

// ─────────────────────────────────────────────────────────────────────
// GOOGLE OAUTH2 CONFIG
// Desktop app credentials — client_secret is not truly secret for
// installed apps per Google's OAuth2 for Mobile/Desktop Apps guide.
// Replace with real credentials from Google Cloud Console.
// ─────────────────────────────────────────────────────────────────────

const GOOGLE_CLIENT_ID: &str = "YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com";
const GOOGLE_CLIENT_SECRET: &str = "YOUR_GOOGLE_CLIENT_SECRET";
const GOOGLE_AUTH_URL: &str = "https://accounts.google.com/o/oauth2/v2/auth";
const GOOGLE_TOKEN_URL: &str = "https://oauth2.googleapis.com/token";
const GOOGLE_USERINFO_URL: &str = "https://www.googleapis.com/oauth2/v3/userinfo";
const GMAIL_SCOPE: &str = "https://mail.google.com/ openid email profile";

// ─────────────────────────────────────────────────────────────────────
// TYPES
// ─────────────────────────────────────────────────────────────────────

#[derive(Debug, Serialize, Deserialize, Default)]
pub struct SmtpSettings {
    pub smtp_host: String,
    pub smtp_port: i32,
    pub smtp_email_from: String,
    pub smtp_password: String,
    pub smtp_enabled: bool,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct GmailOAuthStatus {
    pub connected: bool,
    pub email: String,
}

/// In-flight PKCE session — lives only during the browser auth flow
pub struct OAuthPkceSession {
    pub code_verifier: String,
    pub state_token: String,
}

/// Tauri-managed state for the OAuth flow
pub struct OAuthState {
    pub session: Arc<TokioMutex<Option<OAuthPkceSession>>>,
}

impl Default for OAuthState {
    fn default() -> Self {
        Self {
            session: Arc::new(TokioMutex::new(None)),
        }
    }
}

// Internal deserialization types — not exposed to frontend
#[derive(Deserialize)]
struct TokenResponse {
    access_token: String,
    refresh_token: Option<String>,
    expires_in: i64,
}

#[derive(Deserialize)]
struct UserInfo {
    email: String,
}

// ─────────────────────────────────────────────────────────────────────
// HELPER FUNCTIONS
// ─────────────────────────────────────────────────────────────────────

async fn get_setting(pool: &SqlitePool, chiave: &str) -> Option<String> {
    let result: Option<(String,)> =
        sqlx::query_as("SELECT valore FROM impostazioni WHERE chiave = ?")
            .bind(chiave)
            .fetch_optional(pool)
            .await
            .ok()?;

    result.map(|(v,)| v)
}

async fn save_setting(
    pool: &SqlitePool,
    chiave: &str,
    valore: &str,
    tipo: &str,
) -> Result<(), String> {
    sqlx::query(
        "INSERT OR REPLACE INTO impostazioni (chiave, valore, tipo, updated_at) VALUES (?, ?, ?, datetime('now'))"
    )
    .bind(chiave)
    .bind(valore)
    .bind(tipo)
    .execute(pool)
    .await
    .map_err(|e| e.to_string())?;
    Ok(())
}

// ─────────────────────────────────────────────────────────────────────
// SMTP SETTINGS COMMANDS
// ─────────────────────────────────────────────────────────────────────

/// Ottieni le impostazioni SMTP correnti
#[tauri::command]
pub async fn get_smtp_settings(pool: State<'_, SqlitePool>) -> Result<SmtpSettings, String> {
    let smtp_host = get_setting(pool.inner(), "smtp_host")
        .await
        .unwrap_or_else(|| "smtp.gmail.com".to_string());

    let smtp_port = get_setting(pool.inner(), "smtp_port")
        .await
        .and_then(|v| v.parse().ok())
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

    Ok(SmtpSettings {
        smtp_host,
        smtp_port,
        smtp_email_from,
        smtp_password,
        smtp_enabled,
    })
}

/// Salva le impostazioni SMTP
#[tauri::command]
pub async fn save_smtp_settings(
    pool: State<'_, SqlitePool>,
    settings: SmtpSettings,
) -> Result<(), String> {
    save_setting(pool.inner(), "smtp_host", &settings.smtp_host, "string").await?;
    save_setting(
        pool.inner(),
        "smtp_port",
        &settings.smtp_port.to_string(),
        "number",
    )
    .await?;
    save_setting(
        pool.inner(),
        "smtp_email_from",
        &settings.smtp_email_from,
        "string",
    )
    .await?;
    save_setting(
        pool.inner(),
        "smtp_password",
        &settings.smtp_password,
        "string",
    )
    .await?;
    save_setting(
        pool.inner(),
        "smtp_enabled",
        if settings.smtp_enabled {
            "true"
        } else {
            "false"
        },
        "boolean",
    )
    .await?;

    println!("✅ SMTP settings saved for: {}", settings.smtp_email_from);
    Ok(())
}

/// Test connessione SMTP (senza inviare email)
#[tauri::command]
pub async fn test_smtp_connection(pool: State<'_, SqlitePool>) -> Result<bool, String> {
    let settings = get_smtp_settings(pool).await?;

    if settings.smtp_email_from.is_empty() || settings.smtp_password.is_empty() {
        return Err("SMTP email e password sono richiesti".to_string());
    }

    // Per ora ritorna true se le credenziali sono configurate
    // In futuro: test reale connessione SMTP
    Ok(true)
}

// ─────────────────────────────────────────────────────────────────────
// GMAIL OAUTH2 — PKCE HELPERS
// ─────────────────────────────────────────────────────────────────────

fn generate_code_verifier() -> String {
    let mut rng = rand::thread_rng();
    let mut bytes = [0u8; 32];
    rng.fill_bytes(&mut bytes);
    URL_SAFE_NO_PAD.encode(bytes)
}

fn generate_code_challenge(verifier: &str) -> String {
    let mut hasher = Sha256::new();
    hasher.update(verifier.as_bytes());
    let result = hasher.finalize();
    URL_SAFE_NO_PAD.encode(result)
}

fn generate_state_token() -> String {
    let mut rng = rand::thread_rng();
    let mut bytes = [0u8; 16];
    rng.fill_bytes(&mut bytes);
    URL_SAFE_NO_PAD.encode(bytes)
}

/// Exchange authorization code for access + refresh tokens
async fn exchange_code_for_tokens(
    code: &str,
    code_verifier: &str,
    redirect_uri: &str,
) -> Result<TokenResponse, String> {
    let client = reqwest::Client::new();
    let params = [
        ("code", code),
        ("client_id", GOOGLE_CLIENT_ID),
        ("client_secret", GOOGLE_CLIENT_SECRET),
        ("redirect_uri", redirect_uri),
        ("grant_type", "authorization_code"),
        ("code_verifier", code_verifier),
    ];
    let resp = client
        .post(GOOGLE_TOKEN_URL)
        .form(&params)
        .send()
        .await
        .map_err(|e| format!("Token request failed: {}", e))?;
    let status = resp.status();
    let body = resp
        .text()
        .await
        .map_err(|e| format!("Token body read failed: {}", e))?;
    serde_json::from_str::<TokenResponse>(&body)
        .map_err(|_| format!("Token exchange failed ({}): {}", status, body))
}

/// Get user email using the access token
async fn get_google_user_email(access_token: &str) -> Result<String, String> {
    let client = reqwest::Client::new();
    let resp = client
        .get(GOOGLE_USERINFO_URL)
        .bearer_auth(access_token)
        .send()
        .await
        .map_err(|e| format!("Userinfo request failed: {}", e))?;
    let info = resp
        .json::<UserInfo>()
        .await
        .map_err(|e| format!("Userinfo parse failed: {}", e))?;
    Ok(info.email)
}

/// Refresh an expired access token using the stored refresh token
async fn refresh_access_token(refresh_token: &str) -> Result<(String, i64), String> {
    #[derive(Deserialize)]
    struct RefreshResponse {
        access_token: String,
        expires_in: i64,
    }
    let client = reqwest::Client::new();
    let params = [
        ("client_id", GOOGLE_CLIENT_ID),
        ("client_secret", GOOGLE_CLIENT_SECRET),
        ("refresh_token", refresh_token),
        ("grant_type", "refresh_token"),
    ];
    let resp = client
        .post(GOOGLE_TOKEN_URL)
        .form(&params)
        .send()
        .await
        .map_err(|e| format!("Refresh request failed: {}", e))?;
    let data = resp
        .json::<RefreshResponse>()
        .await
        .map_err(|e| format!("Refresh parse failed: {}", e))?;
    let expiry = chrono::Utc::now().timestamp() + data.expires_in;
    Ok((data.access_token, expiry))
}

/// Internal: wait for the OAuth callback, exchange code, save tokens
async fn handle_oauth_callback(
    listener: tokio::net::TcpListener,
    redirect_uri: String,
    pool: SqlitePool,
    session_arc: Arc<TokioMutex<Option<OAuthPkceSession>>>,
) -> Result<String, String> {
    use tokio::io::{AsyncReadExt, AsyncWriteExt};

    // Wait for browser redirect — 5-minute timeout
    let (mut stream, _) = tokio::time::timeout(
        std::time::Duration::from_secs(300),
        listener.accept(),
    )
    .await
    .map_err(|_| "OAuth timeout: nessuna risposta entro 5 minuti".to_string())?
    .map_err(|e| e.to_string())?;

    // Read HTTP request
    let mut buf = vec![0u8; 8192];
    let n = stream.read(&mut buf).await.map_err(|e| e.to_string())?;
    let request = String::from_utf8_lossy(&buf[..n]);

    // Parse "GET /oauth/callback?code=...&state=... HTTP/1.1"
    let query_string = request
        .lines()
        .next()
        .and_then(|line| line.split('?').nth(1))
        .and_then(|q| q.split(' ').next())
        .unwrap_or("");

    let params: std::collections::HashMap<String, String> = query_string
        .split('&')
        .filter_map(|pair| {
            let mut parts = pair.splitn(2, '=');
            let key = parts
                .next()
                .and_then(|k| urlencoding::decode(k).ok())?
                .into_owned();
            let val = parts
                .next()
                .and_then(|v| urlencoding::decode(v).ok())?
                .into_owned();
            Some((key, val))
        })
        .collect();

    // Respond to the browser immediately
    let html = "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nConnection: close\r\n\r\n\
        <!DOCTYPE html><html><head><title>FLUXION</title></head>\
        <body style=\"font-family:system-ui,sans-serif;text-align:center;padding:60px;background:#0f172a;color:white\">\
        <h2 style=\"color:#22d3ee\">✅ Gmail connesso!</h2>\
        <p>Puoi chiudere questa finestra e tornare a FLUXION.</p>\
        <script>setTimeout(()=>window.close(),2000)</script>\
        </body></html>";
    let _ = stream.write_all(html.as_bytes()).await;

    let code = params
        .get("code")
        .ok_or("Parametro 'code' mancante dalla risposta Google")?
        .clone();
    let state = params
        .get("state")
        .ok_or("Parametro 'state' mancante dalla risposta Google")?
        .clone();

    // Validate CSRF state and retrieve code_verifier
    let code_verifier = {
        let mut session = session_arc.lock().await;
        let s = session
            .as_ref()
            .ok_or("Nessuna sessione OAuth attiva")?;
        if s.state_token != state {
            return Err("State token non valido — possibile attacco CSRF".to_string());
        }
        let verifier = s.code_verifier.clone();
        *session = None;
        verifier
    };

    // Exchange code for tokens
    let tokens = exchange_code_for_tokens(&code, &code_verifier, &redirect_uri).await?;
    let refresh_token = tokens
        .refresh_token
        .ok_or("Google non ha restituito un refresh token. Assicurati di usare prompt=consent.")?;

    // Get user email
    let email = get_google_user_email(&tokens.access_token).await?;

    // Persist all tokens + metadata
    let expiry = chrono::Utc::now().timestamp() + tokens.expires_in;
    save_setting(&pool, "gmail_access_token", &tokens.access_token, "string").await?;
    save_setting(&pool, "gmail_refresh_token", &refresh_token, "string").await?;
    save_setting(&pool, "gmail_email", &email, "string").await?;
    save_setting(&pool, "gmail_token_expiry", &expiry.to_string(), "number").await?;
    save_setting(&pool, "gmail_oauth_enabled", "true", "boolean").await?;
    // Also populate smtp_email_from for SMTP compatibility layer
    save_setting(&pool, "smtp_email_from", &email, "string").await?;

    println!("✅ Gmail OAuth2 connected: {}", email);
    Ok(email)
}

// ─────────────────────────────────────────────────────────────────────
// GMAIL OAUTH2 COMMANDS
// ─────────────────────────────────────────────────────────────────────

/// Avvia il flusso OAuth2 PKCE per Gmail.
/// Apre il browser di sistema → Google login → callback locale → token in DB.
/// Il risultato arriva via evento Tauri: "gmail-oauth-success" o "gmail-oauth-error".
#[tauri::command]
pub async fn start_gmail_oauth(
    app: AppHandle,
    pool: State<'_, SqlitePool>,
    oauth_state: State<'_, OAuthState>,
) -> Result<(), String> {
    let code_verifier = generate_code_verifier();
    let code_challenge = generate_code_challenge(&code_verifier);
    let state_token = generate_state_token();

    // Bind to a random available local port for the redirect callback
    let listener = tokio::net::TcpListener::bind("127.0.0.1:0")
        .await
        .map_err(|e| format!("Impossibile avviare server OAuth locale: {}", e))?;
    let port = listener
        .local_addr()
        .map_err(|e| e.to_string())?
        .port();
    let redirect_uri = format!("http://127.0.0.1:{}/oauth/callback", port);

    // Store PKCE session
    {
        let mut session = oauth_state.session.lock().await;
        *session = Some(OAuthPkceSession {
            code_verifier,
            state_token: state_token.clone(),
        });
    }

    // Build Google authorization URL
    let auth_url = format!(
        "{auth}?client_id={client_id}&redirect_uri={redirect}&response_type=code\
         &scope={scope}&code_challenge={challenge}&code_challenge_method=S256\
         &state={state}&access_type=offline&prompt=consent",
        auth = GOOGLE_AUTH_URL,
        client_id = urlencoding::encode(GOOGLE_CLIENT_ID),
        redirect = urlencoding::encode(&redirect_uri),
        scope = urlencoding::encode(GMAIL_SCOPE),
        challenge = code_challenge,
        state = state_token,
    );

    // Clone what needs to outlive this function
    let pool_clone = pool.inner().clone();
    let session_arc = Arc::clone(&oauth_state.session);

    // Spawn background task: wait for callback → exchange → persist → emit event
    tokio::spawn(async move {
        match handle_oauth_callback(listener, redirect_uri, pool_clone, session_arc).await {
            Ok(email) => {
                let _ = app.emit("gmail-oauth-success", serde_json::json!({ "email": email }));
            }
            Err(e) => {
                let _ = app.emit("gmail-oauth-error", serde_json::json!({ "message": e }));
            }
        }
    });

    // Open system browser (macOS)
    std::process::Command::new("open")
        .arg(&auth_url)
        .spawn()
        .map_err(|e| format!("Impossibile aprire il browser: {}", e))?;

    Ok(())
}

/// Ritorna lo stato della connessione Gmail OAuth2
#[tauri::command]
pub async fn get_gmail_oauth_status(
    pool: State<'_, SqlitePool>,
) -> Result<GmailOAuthStatus, String> {
    let connected = get_setting(pool.inner(), "gmail_oauth_enabled")
        .await
        .map(|v| v == "true")
        .unwrap_or(false);
    let email = get_setting(pool.inner(), "gmail_email")
        .await
        .unwrap_or_default();
    Ok(GmailOAuthStatus { connected, email })
}

/// Disconnette Gmail OAuth2 — cancella tutti i token dal DB
#[tauri::command]
pub async fn disconnect_gmail_oauth(pool: State<'_, SqlitePool>) -> Result<(), String> {
    save_setting(pool.inner(), "gmail_oauth_enabled", "false", "boolean").await?;
    save_setting(pool.inner(), "gmail_access_token", "", "string").await?;
    save_setting(pool.inner(), "gmail_refresh_token", "", "string").await?;
    save_setting(pool.inner(), "gmail_email", "", "string").await?;
    save_setting(pool.inner(), "gmail_token_expiry", "", "number").await?;
    println!("🔌 Gmail OAuth2 disconnected");
    Ok(())
}

/// Ritorna un access token fresco — auto-refresh se scaduto.
/// Usato dal Python voice agent per XOAUTH2 SMTP.
#[tauri::command]
pub async fn get_gmail_fresh_token(pool: State<'_, SqlitePool>) -> Result<String, String> {
    let connected = get_setting(pool.inner(), "gmail_oauth_enabled")
        .await
        .map(|v| v == "true")
        .unwrap_or(false);
    if !connected {
        return Err("Gmail OAuth non configurato".to_string());
    }

    let expiry: i64 = get_setting(pool.inner(), "gmail_token_expiry")
        .await
        .and_then(|v| v.parse().ok())
        .unwrap_or(0);
    let now = chrono::Utc::now().timestamp();

    // Refresh proactively 5 minutes before expiry
    if now + 300 >= expiry {
        let refresh_token = get_setting(pool.inner(), "gmail_refresh_token")
            .await
            .filter(|s| !s.is_empty())
            .ok_or("Refresh token mancante — riconnetti Gmail")?;
        let (new_token, new_expiry) = refresh_access_token(&refresh_token).await?;
        save_setting(pool.inner(), "gmail_access_token", &new_token, "string").await?;
        save_setting(
            pool.inner(),
            "gmail_token_expiry",
            &new_expiry.to_string(),
            "number",
        )
        .await?;
        return Ok(new_token);
    }

    get_setting(pool.inner(), "gmail_access_token")
        .await
        .filter(|s| !s.is_empty())
        .ok_or_else(|| "Access token mancante — riconnetti Gmail".to_string())
}
