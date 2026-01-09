import * as net from "net";
import * as http from "http";
import { Buffer } from "node:buffer";
import SystemManagementAgent from "./monitoring-agent.js";
// ============================================================================
// FLUXION MCP Server - TCP Listener for Remote Testing
// ============================================================================
const MCP_SERVER_NAME = "fluxion-mcp";
const MCP_SERVER_VERSION = "1.0.0";
const TCP_HOST = "0.0.0.0";
const TCP_PORT = parseInt(process.env.TAURI_MCP_PORT || "5000");
const TAURI_HTTP_PORT = parseInt(process.env.TAURI_HTTP_PORT || "3001");
// ============================================================================
// Tool Definitions
// ============================================================================
const tools = [
    {
        name: "take_screenshot",
        description: "Capture a screenshot of the FLUXION app window",
        inputSchema: {
            type: "object",
            properties: {
                format: {
                    type: "string",
                    enum: ["base64", "file"],
                    description: "Return format: base64 PNG string or file path",
                    default: "base64",
                },
            },
            required: [],
        },
    },
    {
        name: "get_dom_content",
        description: "Get the current DOM content of the webview",
        inputSchema: {
            type: "object",
            properties: {
                selector: {
                    type: "string",
                    description: "CSS selector to target specific element (optional)",
                },
            },
            required: [],
        },
    },
    {
        name: "execute_script",
        description: "Execute JavaScript in the webview context",
        inputSchema: {
            type: "object",
            properties: {
                script: {
                    type: "string",
                    description: "JavaScript code to execute",
                },
            },
            required: ["script"],
        },
    },
    {
        name: "mouse_click",
        description: "Simulate mouse click at coordinates",
        inputSchema: {
            type: "object",
            properties: {
                x: { type: "number", description: "X coordinate" },
                y: { type: "number", description: "Y coordinate" },
                button: {
                    type: "string",
                    enum: ["left", "right", "middle"],
                    default: "left",
                },
            },
            required: ["x", "y"],
        },
    },
    {
        name: "type_text",
        description: "Type text in the currently focused element",
        inputSchema: {
            type: "object",
            properties: {
                text: { type: "string", description: "Text to type" },
            },
            required: ["text"],
        },
    },
    {
        name: "key_press",
        description: "Press keyboard key",
        inputSchema: {
            type: "object",
            properties: {
                key: {
                    type: "string",
                    description: 'Key to press (e.g., "Enter", "Tab", "Escape")',
                },
                modifiers: {
                    type: "array",
                    items: { type: "string", enum: ["Control", "Shift", "Alt", "Meta"] },
                    description: "Modifier keys to hold",
                },
            },
            required: ["key"],
        },
    },
    {
        name: "ping",
        description: "Test MCP server connectivity",
        inputSchema: {
            type: "object",
            properties: {},
            required: [],
        },
    },
    {
        name: "get_app_info",
        description: "Get information about the FLUXION app",
        inputSchema: {
            type: "object",
            properties: {},
            required: [],
        },
    },
];
// ============================================================================
// Tauri HTTP Bridge - Communicate with Tauri via HTTP (port 3001)
// ============================================================================
// Map tool names to HTTP bridge endpoints
const ENDPOINT_MAP = {
    ping: "/api/mcp/ping",
    get_app_info: "/api/mcp/app-info",
    take_screenshot: "/api/mcp/screenshot",
    get_dom_content: "/api/mcp/dom-content",
    execute_script: "/api/mcp/execute-script",
    mouse_click: "/api/mcp/mouse-click",
    type_text: "/api/mcp/type-text",
    key_press: "/api/mcp/key-press",
    storage_get: "/api/mcp/storage/get",
    storage_set: "/api/mcp/storage/set",
    storage_clear: "/api/mcp/storage/clear",
};
async function callTauriBridge(toolName, params = {}) {
    const endpoint = ENDPOINT_MAP[toolName];
    if (!endpoint) {
        throw new Error(`Unknown tool: ${toolName}`);
    }
    return new Promise((resolve, reject) => {
        const postData = JSON.stringify({ params });
        const options = {
            hostname: "127.0.0.1",
            port: TAURI_HTTP_PORT,
            path: endpoint,
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Content-Length": Buffer.byteLength(postData),
            },
        };
        const req = http.request(options, (res) => {
            let data = "";
            res.on("data", (chunk) => (data += chunk));
            res.on("end", () => {
                try {
                    const response = JSON.parse(data);
                    if (response.success) {
                        resolve(response.data);
                    }
                    else {
                        reject(new Error(response.error || "Bridge request failed"));
                    }
                }
                catch {
                    resolve(data);
                }
            });
        });
        req.on("error", (e) => {
            reject(new Error(`HTTP Bridge connection failed: ${e.message}. Is Tauri app running?`));
        });
        req.setTimeout(10000, () => {
            req.destroy();
            reject(new Error("HTTP Bridge request timeout"));
        });
        req.write(postData);
        req.end();
    });
}
// Health check for HTTP Bridge
async function checkBridgeHealth() {
    return new Promise((resolve) => {
        const req = http.get(`http://127.0.0.1:${TAURI_HTTP_PORT}/health`, (res) => {
            resolve(res.statusCode === 200);
        });
        req.on("error", () => resolve(false));
        req.setTimeout(2000, () => {
            req.destroy();
            resolve(false);
        });
    });
}
// ============================================================================
// Tool Handlers
// ============================================================================
async function handleTool(name, args) {
    console.log(`[MCP] Tool called: ${name}`, JSON.stringify(args));
    // Check if HTTP Bridge is available
    const bridgeAvailable = await checkBridgeHealth();
    switch (name) {
        case "ping":
            if (bridgeAvailable) {
                try {
                    const bridgeResult = await callTauriBridge("ping", {});
                    return {
                        ...bridgeResult,
                        mcp_server: MCP_SERVER_NAME,
                        mcp_version: MCP_SERVER_VERSION,
                    };
                }
                catch {
                    // Fallback to local response
                }
            }
            return {
                status: "ok",
                server: MCP_SERVER_NAME,
                version: MCP_SERVER_VERSION,
                bridge_available: bridgeAvailable,
                timestamp: new Date().toISOString(),
            };
        case "get_app_info":
            if (bridgeAvailable) {
                try {
                    return await callTauriBridge("get_app_info", {});
                }
                catch (error) {
                    console.error("[MCP] get_app_info failed:", error);
                }
            }
            return {
                name: "FLUXION",
                version: "unknown",
                platform: process.platform,
                status: bridgeAvailable ? "bridge_error" : "bridge_unavailable",
            };
        case "take_screenshot":
            if (!bridgeAvailable) {
                throw new Error("HTTP Bridge not available. Is Tauri app running?");
            }
            return await callTauriBridge("take_screenshot", args);
        case "get_dom_content":
            if (!bridgeAvailable) {
                throw new Error("HTTP Bridge not available. Is Tauri app running?");
            }
            return await callTauriBridge("get_dom_content", args);
        case "execute_script":
            if (!bridgeAvailable) {
                throw new Error("HTTP Bridge not available. Is Tauri app running?");
            }
            return await callTauriBridge("execute_script", args);
        case "mouse_click":
            if (!bridgeAvailable) {
                throw new Error("HTTP Bridge not available. Is Tauri app running?");
            }
            return await callTauriBridge("mouse_click", args);
        case "type_text":
            if (!bridgeAvailable) {
                throw new Error("HTTP Bridge not available. Is Tauri app running?");
            }
            return await callTauriBridge("type_text", args);
        case "key_press":
            if (!bridgeAvailable) {
                throw new Error("HTTP Bridge not available. Is Tauri app running?");
            }
            return await callTauriBridge("key_press", args);
        default:
            throw new Error(`Unknown tool: ${name}`);
    }
}
async function handleMessage(message) {
    let request;
    try {
        request = JSON.parse(message);
    }
    catch {
        return JSON.stringify({
            jsonrpc: "2.0",
            id: null,
            error: { code: -32700, message: "Parse error" },
        });
    }
    const response = {
        jsonrpc: "2.0",
        id: request.id,
    };
    try {
        switch (request.method) {
            case "initialize":
                response.result = {
                    protocolVersion: "2024-11-05",
                    capabilities: { tools: {} },
                    serverInfo: {
                        name: MCP_SERVER_NAME,
                        version: MCP_SERVER_VERSION,
                    },
                };
                break;
            case "tools/list":
                response.result = { tools };
                break;
            case "tools/call": {
                const params = request.params;
                const result = await handleTool(params.name, params.arguments || {});
                response.result = {
                    content: [
                        {
                            type: "text",
                            text: JSON.stringify(result, null, 2),
                        },
                    ],
                };
                break;
            }
            case "notifications/initialized":
                // No response needed for notifications
                return "";
            default:
                response.error = { code: -32601, message: `Method not found: ${request.method}` };
        }
    }
    catch (error) {
        response.error = {
            code: -32000,
            message: error instanceof Error ? error.message : String(error),
        };
    }
    return JSON.stringify(response);
}
// ============================================================================
// TCP Server
// ============================================================================
const tcpServer = net.createServer((socket) => {
    console.log(`[MCP] Client connected from ${socket.remoteAddress}:${socket.remotePort}`);
    let buffer = "";
    socket.on("data", async (data) => {
        buffer += data.toString();
        // Process complete messages (newline delimited)
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";
        for (const line of lines) {
            if (line.trim()) {
                const response = await handleMessage(line);
                if (response) {
                    socket.write(response + "\n");
                }
            }
        }
    });
    socket.on("error", (error) => {
        console.error(`[MCP] Socket error:`, error);
    });
    socket.on("close", () => {
        console.log(`[MCP] Client disconnected from ${socket.remoteAddress}`);
    });
});
// ============================================================================
// System Management Agent
// ============================================================================
const managementAgent = new SystemManagementAgent("./logs/mcp");
tcpServer.listen(TCP_PORT, TCP_HOST, async () => {
    // Check HTTP Bridge availability
    const bridgeAvailable = await checkBridgeHealth();
    const bridgeStatus = bridgeAvailable ? "✅ Connected" : "❌ Not available";
    console.log(`
╔════════════════════════════════════════════════════════╗
║  🔌 FLUXION MCP Server Started                         ║
╠════════════════════════════════════════════════════════╣
║  Server:  ${MCP_SERVER_NAME} v${MCP_SERVER_VERSION}                        ║
║  Host:    ${TCP_HOST}:${TCP_PORT}                                ║
║  Bridge:  http://127.0.0.1:${TAURI_HTTP_PORT} ${bridgeStatus}     ║
║  Tools:   ${tools.length} tools registered                         ║
║  Status:  Ready for connections                        ║
╚════════════════════════════════════════════════════════╝
  `);
    if (!bridgeAvailable) {
        console.log("[MCP] ⚠️  HTTP Bridge not available. Start Tauri app to enable all tools.");
    }
    // Start System Management Agent
    await managementAgent.start();
    console.log("[MCP] System Management Agent started");
});
tcpServer.on("error", (error) => {
    console.error("[MCP] Server error:", error);
    process.exit(1);
});
// Graceful shutdown
process.on("SIGINT", async () => {
    console.log("\n[MCP] Shutting down...");
    await managementAgent.stop();
    tcpServer.close(() => {
        console.log("[MCP] Server closed");
        process.exit(0);
    });
});
//# sourceMappingURL=index.js.map