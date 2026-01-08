# AI-Guided Live App Testing: Claude Code on Local Network

**Enterprise Testing Framework**
*Come Claude Code usa MCP per testare l'app "dal vivo" sulla rete locale*

---

## Executive Summary

**Scenario:** Claude Code o Cursor accede all'app Tauri in esecuzione sulla tua macchina di sviluppo (rete locale), interagisce con essa in tempo reale via MCP, documenta automaticamente errori, screenshot, e suggerisce fix.

```
Developer Workspace (macOS/Windows/Linux)
    ↓
Tauri App Running
    ├─ MCP Server Listening (/tmp/tauri-mcp.sock o named pipe)
    └─ Frontend: React (rete locale http://localhost:1420)

Claude Code / Cursor (Stesso dispositivo o rete locale)
    ↓ (IPC/WebSocket)
    ├─ take_screenshot()
    ├─ getDomContent()
    ├─ executeScript()
    ├─ mouse_click(x, y)
    ├─ type_text()
    └─ Documenta errori automaticamente
```

---

## 1. Setup: Rete Locale Testing

### Prerequisito: App Già Running

```bash
# Terminal 1: Start Tauri app
npm run dev

# Output:
# ✓ Frontend: http://localhost:1420
# ✓ Tauri window opened
# ✓ MCP Server: /tmp/tauri-mcp.sock (or \\.\pipe\tauri-mcp on Windows)
```

### MCP Configuration (Already Done)

```json
// ~/.config/Claude/claude_desktop_config.json
{
  "mcpServers": {
    "tauri-mcp": {
      "command": "node",
      "args": ["/Users/you/Projects/tauri-app/mcp-server-ts/build/index.js"],
      "env": {
        "TAURI_MCP_IPC_PATH": "/tmp/tauri-mcp.sock"
      }
    }
  }
}
```

### Test Connectivity

```bash
# In Claude Code chat, test:
# "Take a screenshot of the current app"

# Claude calls:
# - tauri-mcp → take_screenshot()
# - Returns: base64 PNG image
# - Claude displays it to you
```

---

## 2. Types of Tests Claude Code Can Run

### A. Visual Regression Tests

```
User (in Claude Code): "Compare the current UI with the baseline. Any visual changes?"

Claude:
1. take_screenshot() → Current state
2. Compare with baseline.png (from repo)
3. Report differences:
   - Button color changed
   - Layout shifted
   - Font size different
4. Suggests: "Revert CSS change or update baseline"
```

### B. User Flow Tests (End-to-End)

```
User: "Complete the sign-up flow with test data"

Claude:
1. take_screenshot() → See landing page
2. getDomContent() → Find signup button
3. mouse_click(signup_button_x, signup_button_y)
4. take_screenshot() → See form
5. type_text("john@example.com")
6. key_press("Tab")
7. type_text("SecurePass123")
8. mouse_click(submit_button)
9. wait(2000)
10. take_screenshot() → Verify success page
11. executeScript('localStorage.getItem("auth_token")') → Check token
12. Document: "✓ Sign-up flow completed successfully"
```

### C. Error State Testing

```
User: "Test the app with invalid inputs and document errors"

Claude:
1. take_screenshot() → Initial state
2. Tries: type_text("invalid-email") in email field
3. mouse_click(submit)
4. take_screenshot() → Error appears
5. getDomContent() → Extract error message
6. executeScript('document.querySelector(".error").innerText') → Get exact message
7. Document:
   ✗ Error: "Email is invalid"
   - Expected: Proper validation
   - Actual: Vague message
   - Suggestion: Make error message clearer
```

### D. Performance Tests

```
User: "Check if the app responds in under 1 second to interactions"

Claude:
1. executeScript('performance.mark("interaction_start")')
2. mouse_click(button)
3. executeScript('
     performance.mark("interaction_end");
     const measure = performance.measure("interaction",
       "interaction_start", "interaction_end");
     return measure.duration;
   ')
4. Result: 250ms ✓ (within threshold)
```

### E. Accessibility Tests

```
User: "Check if all buttons have proper labels and are keyboard accessible"

Claude:
1. getDomContent() → Scan DOM
2. executeScript('
     document.querySelectorAll("button").forEach(btn => {
       console.log({
         text: btn.innerText,
         ariaLabel: btn.getAttribute("aria-label"),
         tabIndex: btn.tabIndex
       });
     });
   ')
3. Document missing aria-labels
4. Suggest fixes
```

---

## 3. Automatic Error Documentation

### Error Capture Framework

Create `tests/ai-testing-report.ts` in your Tauri project:

```typescript
// src/lib/ai-testing-report.ts
export interface TestError {
  timestamp: string;
  type: "visual" | "functional" | "performance" | "accessibility";
  severity: "critical" | "high" | "medium" | "low";
  description: string;
  screenshot: string; // base64
  domContent: string;
  actionsTaken: string[];
  suggestedFix: string;
}

export interface TestReport {
  appName: string;
  version: string;
  testedAt: string;
  errors: TestError[];
  passedTests: string[];
  totalTests: number;
  summary: {
    passed: number;
    failed: number;
    successRate: number;
  };
}

// Example: Claude creates report automatically
export function generateReport(errors: TestError[]): TestReport {
  return {
    appName: "MyApp",
    version: "1.0.0",
    testedAt: new Date().toISOString(),
    errors,
    passedTests: [],
    totalTests: errors.length,
    summary: {
      passed: 0,
      failed: errors.length,
      successRate: 0,
    },
  };
}
```

### MCP Custom Tool for Error Logging

```rust
// src-tauri/src/mcp_commands.rs
use serde_json::{json, Value};
use std::fs;

#[derive(serde::Serialize, serde::Deserialize)]
pub struct TestError {
    pub timestamp: String,
    pub error_type: String,
    pub severity: String,
    pub description: String,
    pub screenshot: String, // base64
    pub suggested_fix: String,
}

pub async fn log_test_error(error: TestError) -> Result<String, String> {
    let report_dir = "test-reports";
    fs::create_dir_all(report_dir)
        .map_err(|e| e.to_string())?;

    let filename = format!(
        "{}/error_{}.json",
        report_dir,
        chrono::Local::now().format("%Y%m%d_%H%M%S")
    );

    fs::write(&filename, serde_json::to_string_pretty(&error).unwrap())
        .map_err(|e| e.to_string())?;

    println!("Test error logged: {}", filename);
    Ok(filename)
}
```

### Register in MCP Server

```typescript
// mcp-server-ts/src/index.ts
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request;

  switch (name) {
    case "take_screenshot":
      return screenshotTool();

    case "log_test_error":
      return await invokeCustomCommand("log_test_error", {
        timestamp: new Date().toISOString(),
        error_type: args.type,
        severity: args.severity,
        description: args.description,
        screenshot: args.screenshot,
        suggested_fix: args.suggested_fix,
      });

    case "get_test_report":
      return await getTestReport();

    default:
      throw new Error(`Unknown tool: ${name}`);
  }
});
```

---

## 4. Complete Testing Workflow: Example

### Scenario: Test User Authentication Flow

**In Claude Code Chat:**

```
User: "Test the complete login flow on my local Tauri app.
       Test with valid credentials, invalid email, empty fields.
       Document any errors you find."
```

**Claude Response (Automated Steps):**

```markdown
Starting Authentication Flow Testing...

### Step 1: Check Initial State
- ✓ take_screenshot()
- ✓ App loaded at localhost:1420
- ✓ Login form visible

### Step 2: Test Valid Login
1. getDomContent() → Found email input: id="email"
2. executeScript() → Get input position
3. mouse_click(245, 150) → Click email field
4. type_text("test@example.com")
5. key_press("Tab") → Move to password
6. type_text("ValidPass123")
7. mouse_click(500, 300) → Click login button
8. wait(1500)
9. take_screenshot() → Success page shown
10. ✓ PASS: Redirected to dashboard

### Step 3: Test Invalid Email
1. executeScript('document.querySelector("#email").value = ""') → Clear
2. type_text("not-an-email")
3. mouse_click(submit_button)
4. take_screenshot()
5. getDomContent()
6. executeScript('document.querySelector(".error").innerText')
   → Returns: "Please enter a valid email"
7. ✓ PASS: Error validation working

### Step 4: Test Empty Fields
1. mouse_click(email_field)
2. key_press("Control+A")
3. key_press("Backspace")
4. mouse_click(password_field)
5. mouse_click(submit_button)
6. wait(500)
7. take_screenshot()
8. ERROR FOUND:
   ✗ No error message displayed
   - Expected: "Email and password required"
   - Actual: Form submitted anyway (backend validation?)

   Logged error to: test-reports/error_20260108_201530.json

### Step 5: Test Session Persistence
1. get_local_storage() → Check auth_token
2. executeScript('window.location.reload()') → Reload page
3. wait(1000)
4. take_screenshot()
5. ✓ PASS: User still logged in after reload

## Summary Report

**Tests Run:** 5
**Passed:** 4 ✓
**Failed:** 1 ✗
**Success Rate:** 80%

**Critical Issues Found:**
1. Empty fields validation missing (Severity: HIGH)
   - Location: Login form
   - Suggestion: Add client-side validation before submit
   - Screenshot: [embedded]

**Generated Files:**
- test-reports/error_20260108_201530.json
- test-reports/summary_20260108.html
```

---

## 5. Real-Time Error Documentation

### Error JSON Auto-Generated

```json
{
  "timestamp": "2026-01-08T20:15:30Z",
  "error_type": "functional",
  "severity": "high",
  "description": "Empty form fields are submitted without validation error",
  "steps_to_reproduce": [
    "Click email field",
    "Leave empty",
    "Click password field",
    "Leave empty",
    "Click submit button"
  ],
  "expected_behavior": "Error message: 'Email and password required'",
  "actual_behavior": "Form submitted to backend without client-side validation",
  "screenshot": "base64_png_data_here...",
  "dom_at_error": "<form><input id=\"email\"/>...",
  "console_errors": [],
  "suggested_fix": "Add required attribute and onSubmit validation: if (!email || !password) { showError('...'); return; }",
  "impact": "Users can submit invalid data, wasting backend validation calls",
  "test_context": {
    "app_version": "1.0.0",
    "browser_equivalent": "Chromium WebView",
    "network": "localhost",
    "platform": "macOS"
  }
}
```

---

## 6. Network Local Setup

### Same Device (Development Machine)

```bash
# Terminal 1: Tauri app
npm run dev
# Output: http://localhost:1420

# Terminal 2: Claude Code / Cursor
# Open Claude Code IDE
# MCP auto-connects to /tmp/tauri-mcp.sock

# Chat: "Test the app"
# → Claude can now interact with app
```

### Network Access (From Another Machine)

```bash
# Machine A (Dev): Tauri app
npm run dev

# Check your local IP
ifconfig | grep "inet " | grep -v 127.0.0.1
# Example: 192.168.1.100

# Machine B (Testing): Access from another computer
# Configure MCP to connect to:
# TAURI_MCP_IPC_PATH=tcp://192.168.1.100:5000
```

---

## 7. Summary: Live Testing with Claude Code

**Workflow:**
1. Start Tauri app (`npm run dev`)
2. Open Claude Code IDE
3. Ask Claude to test your app:
   - "Test the login flow"
   - "Check for visual regressions"
   - "Document any errors you find"
4. Claude interacts with app via MCP
5. Errors auto-logged to JSON
6. HTML reports auto-generated
7. You review findings → Fix → Claude re-tests

**Key Advantages:**
- Real interaction, not mocked
- Visual feedback (screenshots)
- Error documentation automated
- Works on local network
- No headless browser needed
- AI understands context and UI

**Next:** Deploy to CI/CD for automated nightly testing!
