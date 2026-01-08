// ═══════════════════════════════════════════════════════════════════
// FLUXION - MCP Commands for AI Live Testing
// Commands invoked by MCP server for remote testing
// ═══════════════════════════════════════════════════════════════════

use serde::{Deserialize, Serialize};
use tauri::{AppHandle, Manager, WebviewWindow};

// ───────────────────────────────────────────────────────────────────
// Types
// ───────────────────────────────────────────────────────────────────

#[derive(Debug, Serialize)]
pub struct AppInfo {
    pub name: String,
    pub version: String,
    pub platform: String,
    pub arch: String,
}

#[derive(Debug, Serialize)]
pub struct ScreenshotResult {
    pub success: bool,
    pub width: u32,
    pub height: u32,
    pub message: String,
}

#[derive(Debug, Serialize)]
pub struct ScriptResult {
    pub success: bool,
    pub result: Option<String>,
    pub error: Option<String>,
}

// ───────────────────────────────────────────────────────────────────
// MCP Commands
// ───────────────────────────────────────────────────────────────────

/// Ping - test connectivity
#[tauri::command]
pub fn mcp_ping() -> Result<serde_json::Value, String> {
    Ok(serde_json::json!({
        "status": "ok",
        "server": "FLUXION",
        "timestamp": chrono::Local::now().to_rfc3339()
    }))
}

/// Get app info
#[tauri::command]
pub fn mcp_get_app_info() -> Result<AppInfo, String> {
    Ok(AppInfo {
        name: "FLUXION".to_string(),
        version: env!("CARGO_PKG_VERSION").to_string(),
        platform: std::env::consts::OS.to_string(),
        arch: std::env::consts::ARCH.to_string(),
    })
}

/// Take screenshot (placeholder - needs window-state plugin)
#[tauri::command]
pub async fn mcp_take_screenshot(window: WebviewWindow) -> Result<ScreenshotResult, String> {
    // Get window size
    let size = window
        .outer_size()
        .map_err(|e| format!("Failed to get window size: {}", e))?;

    // Note: Actual screenshot requires additional setup with image capture
    // For now, return dimensions and success status
    Ok(ScreenshotResult {
        success: true,
        width: size.width,
        height: size.height,
        message: "Screenshot dimensions captured. Full capture requires screen-capture plugin."
            .to_string(),
    })
}

/// Get DOM content via JavaScript injection
#[tauri::command]
pub async fn mcp_get_dom_content(
    window: WebviewWindow,
    selector: Option<String>,
) -> Result<String, String> {
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

    window
        .eval(&js)
        .map_err(|e| format!("JS execution failed: {}", e))?;

    Ok("DOM content requested - check console for result".to_string())
}

/// Execute arbitrary JavaScript
#[tauri::command]
pub async fn mcp_execute_script(
    window: WebviewWindow,
    script: String,
) -> Result<ScriptResult, String> {
    match window.eval(&script) {
        Ok(_) => Ok(ScriptResult {
            success: true,
            result: Some("Script executed successfully".to_string()),
            error: None,
        }),
        Err(e) => Ok(ScriptResult {
            success: false,
            result: None,
            error: Some(format!("Script error: {}", e)),
        }),
    }
}

/// Simulate mouse click via JavaScript
#[tauri::command]
pub async fn mcp_mouse_click(
    window: WebviewWindow,
    x: f64,
    y: f64,
    button: Option<String>,
) -> Result<serde_json::Value, String> {
    let button_code = match button.as_deref() {
        Some("right") => 2,
        Some("middle") => 1,
        _ => 0, // left
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
                return {{ success: true, element: el.tagName, id: el.id, class: el.className }};
            }} else {{
                return {{ success: false, error: 'No element at coordinates' }};
            }}
        }})()
        "#,
        x, y, x, y, button_code
    );

    window
        .eval(&js)
        .map_err(|e| format!("Click simulation failed: {}", e))?;

    Ok(serde_json::json!({
        "success": true,
        "x": x,
        "y": y,
        "button": button.unwrap_or_else(|| "left".to_string())
    }))
}

/// Type text in focused element
#[tauri::command]
pub async fn mcp_type_text(
    window: WebviewWindow,
    text: String,
) -> Result<serde_json::Value, String> {
    // Escape text for JavaScript
    let escaped_text = text
        .replace('\\', "\\\\")
        .replace('\'', "\\'")
        .replace('\n', "\\n");

    let js = format!(
        r#"
        (function() {{
            const el = document.activeElement;
            if (el && (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA' || el.isContentEditable)) {{
                // For input/textarea
                if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {{
                    el.value += '{}';
                    el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                }} else {{
                    // For contenteditable
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

    window
        .eval(&js)
        .map_err(|e| format!("Type text failed: {}", e))?;

    Ok(serde_json::json!({
        "success": true,
        "text": text,
        "length": text.len()
    }))
}

/// Press keyboard key
#[tauri::command]
pub async fn mcp_key_press(
    window: WebviewWindow,
    key: String,
    modifiers: Option<Vec<String>>,
) -> Result<serde_json::Value, String> {
    let mods = modifiers.unwrap_or_default();

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
        mods.contains(&"Control".to_string()),
        mods.contains(&"Shift".to_string()),
        mods.contains(&"Alt".to_string()),
        mods.contains(&"Meta".to_string()),
        key
    );

    window
        .eval(&js)
        .map_err(|e| format!("Key press failed: {}", e))?;

    Ok(serde_json::json!({
        "success": true,
        "key": key,
        "modifiers": mods
    }))
}

/// Get localStorage
#[tauri::command]
pub async fn mcp_get_local_storage(
    window: WebviewWindow,
    key: Option<String>,
) -> Result<serde_json::Value, String> {
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

    window
        .eval(&js)
        .map_err(|e| format!("Get localStorage failed: {}", e))?;

    Ok(serde_json::json!({
        "success": true,
        "message": "Check console for localStorage value"
    }))
}

/// Set localStorage
#[tauri::command]
pub async fn mcp_set_local_storage(
    window: WebviewWindow,
    key: String,
    value: String,
) -> Result<serde_json::Value, String> {
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

    window
        .eval(&js)
        .map_err(|e| format!("Set localStorage failed: {}", e))?;

    Ok(serde_json::json!({
        "success": true,
        "key": key,
        "value": value
    }))
}

/// Clear localStorage
#[tauri::command]
pub async fn mcp_clear_local_storage(window: WebviewWindow) -> Result<serde_json::Value, String> {
    let js = r#"
        (function() {
            localStorage.clear();
            return true;
        })()
    "#;

    window
        .eval(js)
        .map_err(|e| format!("Clear localStorage failed: {}", e))?;

    Ok(serde_json::json!({
        "success": true,
        "message": "localStorage cleared"
    }))
}
