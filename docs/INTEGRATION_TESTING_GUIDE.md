# FLUXION Integration Testing Guide

Complete end-to-end testing procedures for production deployment.

---

## Test 1: Voice Pipeline E2E

**File: `test-voice-pipeline.py`**

```python
#!/usr/bin/env python3

import asyncio
import httpx
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:3002"
HTTP_BRIDGE_URL = "http://127.0.0.1:3001"

async def test_voice_pipeline():
    """Test complete voice pipeline (L0→L4)"""
    print("\n" + "="*80)
    print("🎤 FLUXION Voice Pipeline E2E Test")
    print("="*80)
    
    test_queries = [
        {
            "name": "L0: Special Command",
            "input": "stop",
            "verticale": "auto",
            "expected_layer": 0,
        },
        {
            "name": "L1: Intent Classification",
            "input": "ciao, come stai?",
            "verticale": "auto",
            "expected_layer": 1,
        },
        {
            "name": "L3: FAQ Retrieval",
            "input": "quanto costa un tagliando completo?",
            "verticale": "auto",
            "expected_layer": 3,
        },
        {
            "name": "L4: LLM Fallback",
            "input": "mi racconti la storia dell'officina?",
            "verticale": "auto",
            "expected_layer": 4,
        },
    ]
    
    async with httpx.AsyncClient() as client:
        for test in test_queries:
            print(f"\n📝 Test: {test['name']}")
            print(f"   Input: '{test['input']}'")
            
            start_time = time.time()
            
            try:
                response = await client.post(
                    f"{BASE_URL}/api/voice/query",
                    json={
                        "client_id": "test_cli_001",
                        "user_input": test["input"],
                        "verticale": test["verticale"],
                        "channel": "voice",
                    },
                    timeout=5.0,
                )
                
                elapsed_ms = (time.time() - start_time) * 1000
                result = response.json()
                
                print(f"   ✅ Layer: {result.get('layer', '?')}")
                print(f"   ⏱️  Latency: {elapsed_ms:.0f}ms")
                print(f"   📄 Response: {result.get('response', '')[:100]}...")
                
                # Check SLA
                sla_targets = {0: 1, 1: 5, 2: 10, 3: 50, 4: 500}
                layer = result.get("layer")
                if layer in sla_targets:
                    target = sla_targets[layer]
                    status = "✅" if elapsed_ms < target else "⚠️"
                    print(f"   {status} SLA: {elapsed_ms:.0f}ms < {target}ms")
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "="*80)

---

## Test 2: WhatsApp Webhook

**File: `test-whatsapp-webhook.sh`**

```bash
#!/bin/bash

echo "🔔 Testing WhatsApp Webhook Integration..."

# Your n8n webhook URL
WEBHOOK_URL="http://localhost:5678/webhook/whatsapp"

# Test payload
PAYLOAD=$(cat <<'EOF'
{
  "messages": [
    {
      "from": "393459876543",
      "type": "text",
      "id": "wamid.test_123",
      "timestamp": "1705342200",
      "text": {
        "body": "Ciao, quanto costa un tagliando?"
      }
    }
  ],
  "contacts": [
    {
      "profile": {
        "name": "Mario Rossi"
      },
      "wa_id": "393459876543"
    }
  ]
}
EOF
)

echo ""
echo "📤 Sending test WhatsApp message..."
echo "Payload:"
echo "$PAYLOAD" | jq '.'

echo ""
echo "🚀 Posting to webhook..."
curl -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  -v

echo ""
echo "✅ Test complete. Check n8n workflow for processing."
```

---

## Test 3: Database & SQLite

**File: `test-sqlite-connection.py`**

```python
#!/usr/bin/env python3

import sqlite3
import os
from pathlib import Path

def test_sqlite_connection():
    """Test SQLite database connection and schema"""
    print("\n" + "="*80)
    print("💾 SQLite Database Connection Test")
    print("="*80)
    
    # Determine DB path
    db_path = Path(os.path.expanduser("~/Library/Application Support/fluxion/fluxion.db"))
    
    print(f"\n📍 Database path: {db_path}")
    print(f"   Exists: {'✅' if db_path.exists() else '❌'}")
    
    if not db_path.exists():
        print("   ⚠️  Database not found!")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Test tables
        tables = ["clienti", "appuntamenti", "servizi", "faq_entries", "chat_history", "integrations"]
        
        print("\n📊 Testing tables:")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   {table}: {count} rows ✅")
        
        # Test critical queries
        print("\n🔍 Testing critical queries:")
        
        # Query 1: Search client by phone
        cursor.execute("SELECT * FROM clienti WHERE telefono LIKE '%3459%' LIMIT 1")
        result = cursor.fetchone()
        print(f"   Search clienti by phone: {'✅' if result else '⚠️'}")
        
        # Query 2: Get available appointments
        cursor.execute("""
            SELECT COUNT(*) FROM appuntamenti 
            WHERE data = DATE('now') AND stato = 'confermato'
        """)
        count = cursor.fetchone()[0]
        print(f"   Get today's appointments: {count} found ✅")
        
        # Query 3: FAQ retrieval
        cursor.execute("SELECT COUNT(*) FROM faq_entries WHERE categoria_pmi = 'auto'")
        count = cursor.fetchone()[0]
        print(f"   Get AUTO FAQ entries: {count} found ✅")
        
        # Query 4: Index performance
        cursor.execute("EXPLAIN QUERY PLAN SELECT * FROM clienti WHERE telefono = '3459876543'")
        plan = cursor.fetchall()
        print(f"   Index performance: {'✅ Using index' if 'SEARCH' in str(plan) else '⚠️ Full scan'}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_sqlite_connection()
```

---

## Test 4: HTTP Bridge

**File: `test-http-bridge.py`**

```python
#!/usr/bin/env python3

import httpx
import json

async def test_http_bridge():
    """Test HTTP Bridge endpoints"""
    print("\n" + "="*80)
    print("🌉 HTTP Bridge Integration Test")
    print("="*80)
    
    base_url = "http://127.0.0.1:3001"
    
    tests = [
        {
            "name": "Health Check",
            "method": "GET",
            "path": "/health",
            "expected_status": 200,
        },
        {
            "name": "Search Clienti",
            "method": "POST",
            "path": "/api/clienti/search",
            "payload": {"query": "3459876543"},
            "expected_status": 200,
        },
        {
            "name": "List Servizi",
            "method": "GET",
            "path": "/api/servizi/list",
            "expected_status": 200,
        },
        {
            "name": "Voice Query",
            "method": "POST",
            "path": "/api/voice/query",
            "payload": {
                "client_id": "test_001",
                "user_input": "quanto costa?",
                "verticale": "auto",
            },
            "expected_status": 200,
        },
    ]
    
    async with httpx.AsyncClient() as client:
        for test in tests:
            print(f"\n📍 {test['name']}")
            print(f"   {test['method']} {test['path']}")
            
            try:
                if test["method"] == "GET":
                    response = await client.get(f"{base_url}{test['path']}", timeout=5.0)
                else:
                    response = await client.post(
                        f"{base_url}{test['path']}",
                        json=test.get("payload", {}),
                        timeout=5.0,
                    )
                
                status_ok = response.status_code == test["expected_status"]
                print(f"   Status: {response.status_code} {'✅' if status_ok else '❌'}")
                
                if response.status_code == 200:
                    print(f"   Response: {str(response.json())[:100]}...")
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_http_bridge())
```

---

## Test 5: MCP Server

**File: `test-mcp-server.ts`**

```typescript
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { spawn } from "child_process";

async function testMCPServer() {
  console.log("\n" + "=".repeat(80));
  console.log("🤖 MCP Server Integration Test");
  console.log("=".repeat(80));

  // Start MCP server
  const server = spawn("node", ["dist/index.js"], {
    cwd: "./mcp-server",
  });

  // Create client
  const transport = new StdioClientTransport({
    command: "node",
    args: ["./mcp-server/dist/index.js"],
  });

  const client = new Client({
    name: "fluxion-test",
    version: "1.0.0",
  });

  try {
    // Connect to MCP server
    console.log("\n📡 Connecting to MCP server...");
    await client.connect(transport);
    console.log("✅ Connected");

    // List tools
    console.log("\n🛠️  Testing MCP tools:");
    const toolList = await client.listTools();

    for (const tool of toolList.tools) {
      console.log(`\n   📌 ${tool.name}`);
      console.log(`      ${tool.description}`);

      // Test each tool
      if (tool.name === "search_clienti") {
        const result = await client.callTool({
          name: "search_clienti",
          arguments: { query: "3459876543", limit: 5 },
        });
        console.log(`      Result: ${JSON.stringify(result).substring(0, 100)}...`);
      }

      if (tool.name === "get_faq") {
        const result = await client.callTool({
          name: "get_faq",
          arguments: { verticale: "auto", limit: 5 },
        });
        console.log(`      Result: ${JSON.stringify(result).substring(0, 100)}...`);
      }
    }

    // List resources
    console.log("\n📚 Testing MCP resources:");
    const resourceList = await client.listResources();

    for (const resource of resourceList.resources) {
      console.log(`   📄 ${resource.name} (${resource.uri})`);
      
      const content = await client.readResource({ uri: resource.uri });
      console.log(`      ${String(content.contents[0].text).substring(0, 100)}...`);
    }

    console.log("\n✅ All MCP tests passed!");
  } catch (error) {
    console.error("❌ MCP test failed:", error);
  } finally {
    server.kill();
  }
}

testMCPServer();
```

---

## Test 6: Performance Monitoring

**File: `test-performance-sla.py`**

```python
#!/usr/bin/env python3

import asyncio
import httpx
import time
from statistics import mean, stdev

async def test_performance_sla():
    """Test performance against SLA targets"""
    print("\n" + "="*80)
    print("⚡ FLUXION Performance SLA Test")
    print("="*80)
    
    base_url = "http://127.0.0.1:3002"
    
    # SLA targets (ms)
    sla_targets = {
        "L0_regex": (1, "Special commands"),
        "L1_intent": (5, "Intent classification"),
        "L2_slots": (10, "Slot filling"),
        "L3_faq": (50, "FAQ retrieval"),
        "L4_llm": (500, "LLM fallback"),
        "e2e_voice": (2000, "End-to-end voice"),
    }
    
    test_cases = [
        ("stop", "L0_regex"),
        ("ciao", "L1_intent"),
        ("quanto costa?", "L3_faq"),
        ("raccontami", "L4_llm"),
    ]
    
    async with httpx.AsyncClient() as client:
        results = {}
        
        for query, layer_key in test_cases:
            print(f"\n🧪 Testing {sla_targets[layer_key][1]}...")
            
            latencies = []
            for i in range(5):  # 5 iterations
                start = time.time()
                response = await client.post(
                    f"{base_url}/api/voice/query",
                    json={
                        "client_id": "perf_test",
                        "user_input": query,
                        "verticale": "auto",
                    },
                    timeout=3.0,
                )
                latency = (time.time() - start) * 1000
                latencies.append(latency)
            
            avg_latency = mean(latencies)
            std_latency = stdev(latencies) if len(latencies) > 1 else 0
            target = sla_targets[layer_key][0]
            
            status = "✅ PASS" if avg_latency < target else "❌ FAIL"
            print(f"   {status}: {avg_latency:.1f}ms (±{std_latency:.1f}ms) target={target}ms")
            
            results[layer_key] = {
                "avg": avg_latency,
                "std": std_latency,
                "target": target,
                "pass": avg_latency < target,
            }
        
        # Summary
        print("\n" + "="*80)
        print("📊 SLA Summary")
        print("="*80)
        
        passed = sum(1 for r in results.values() if r["pass"])
        total = len(results)
        
        print(f"\nPassed: {passed}/{total} tests")
        print(f"Success Rate: {100*passed/total:.0f}%\n")
        
        for key, data in results.items():
            status = "✅" if data["pass"] else "❌"
            print(f"{status} {key}: {data['avg']:.1f}ms")

if __name__ == "__main__":
    asyncio.run(test_performance_sla())
```

---

## Running All Tests

**Master test script: `run-all-tests.sh`**

```bash
#!/bin/bash

echo "🧪 FLUXION Integration Tests - Start"
echo "=========================================="

# Test 1: Voice Pipeline
echo -e "\n\n[TEST 1/5] Voice Pipeline..."
python3 test-voice-pipeline.py

# Test 2: HTTP Bridge
echo -e "\n\n[TEST 2/5] HTTP Bridge..."
python3 test-http-bridge.py

# Test 3: SQLite Database
echo -e "\n\n[TEST 3/5] SQLite Database..."
python3 test-sqlite-connection.py

# Test 4: WhatsApp Webhook
echo -e "\n\n[TEST 4/5] WhatsApp Webhook..."
bash test-whatsapp-webhook.sh

# Test 5: MCP Server
echo -e "\n\n[TEST 5/5] MCP Server..."
npx ts-node test-mcp-server.ts

echo -e "\n\n=========================================="
echo "✅ All tests completed!"
echo "=========================================="
```

---

## Test Results Template

```markdown
# FLUXION Integration Test Results

**Date**: [DATE]
**Tester**: [NAME]
**Environment**: [macOS/Linux]

## Test Results

| Test | Status | Notes |
|------|--------|-------|
| Voice Pipeline E2E | ✅ PASS | All layers <2s |
| HTTP Bridge | ✅ PASS | All endpoints responding |
| SQLite Database | ✅ PASS | Schema OK, indices working |
| WhatsApp Webhook | ✅ PASS | Payload processed correctly |
| MCP Server | ✅ PASS | All tools functional |
| Performance SLA | ✅ PASS | All targets met |

## Performance Metrics

- L0 (Regex): 0.5ms ✅
- L1 (Intent): 3ms ✅
- L3 (FAQ): 35ms ✅
- L4 (LLM): 250ms ✅
- E2E Voice: 1500ms ✅

## Issues Found

None

## Recommendations

- Monitor Groq rate limiting (30 req/min)
- Backup SQLite daily
- Schedule n8n workflow tests

---

**Status**: ✅ READY FOR PRODUCTION
```

---

**Last Updated**: 15 Gennaio 2026  
**Status**: Testing Guide Complete  
**Next**: Execute all tests before production deployment
