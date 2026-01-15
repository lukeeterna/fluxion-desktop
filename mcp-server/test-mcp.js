#!/usr/bin/env node
/**
 * FLUXION MCP Server - Functional Test
 * Tests all tools and resources locally
 */

const Database = require("better-sqlite3");
const path = require("path");
require("dotenv").config();

const dbPath = process.env.FLUXION_DB_PATH || "/Volumes/MontereyT7/FLUXION/src-tauri/fluxion.db";

console.log("=".repeat(60));
console.log("FLUXION MCP Server - Functional Test");
console.log("=".repeat(60));
console.log(`Database: ${dbPath}\n`);

let db;
try {
  db = new Database(dbPath, { readonly: true });
  console.log("✅ Database connection: OK\n");
} catch (e) {
  console.error("❌ Database connection failed:", e.message);
  process.exit(1);
}

// Test 1: Count tables
console.log("📊 Database Tables:");
const tables = ["clienti", "appuntamenti", "servizi", "operatori"];
for (const table of tables) {
  try {
    const count = db.prepare(`SELECT COUNT(*) as count FROM ${table}`).get();
    console.log(`   ${table}: ${count.count} rows`);
  } catch (e) {
    console.log(`   ${table}: ❌ ${e.message}`);
  }
}

// Test 2: Search clienti simulation
console.log("\n🔍 Test search_clienti:");
try {
  const clients = db.prepare(`
    SELECT id, nome, cognome, telefono
    FROM clienti
    LIMIT 3
  `).all();
  console.log(`   Found ${clients.length} sample clients:`);
  clients.forEach(c => {
    console.log(`   - ${c.nome} ${c.cognome} (${c.telefono || "no phone"})`);
  });
} catch (e) {
  console.log(`   ❌ Error: ${e.message}`);
}

// Test 3: List servizi simulation
console.log("\n💼 Test list_servizi:");
try {
  const services = db.prepare(`
    SELECT id, nome, prezzo, durata_minuti, categoria
    FROM servizi
    WHERE attivo = 1
    LIMIT 5
  `).all();
  console.log(`   Found ${services.length} active services:`);
  services.forEach(s => {
    console.log(`   - ${s.nome}: €${s.prezzo} (${s.durata_minuti}min)`);
  });
} catch (e) {
  console.log(`   ❌ Error: ${e.message}`);
}

// Test 4: Today's appointments
console.log("\n📅 Test appuntamenti/oggi:");
try {
  const today = new Date().toISOString().split("T")[0];
  const appointments = db.prepare(`
    SELECT a.id, a.data_ora_inizio, c.nome, s.nome as servizio
    FROM appuntamenti a
    LEFT JOIN clienti c ON a.cliente_id = c.id
    LEFT JOIN servizi s ON a.servizio_id = s.id
    WHERE date(a.data_ora_inizio) = ?
    LIMIT 5
  `).all(today);
  console.log(`   Today (${today}): ${appointments.length} appointments`);
  appointments.forEach(a => {
    const time = a.data_ora_inizio ? a.data_ora_inizio.split("T")[1]?.substring(0, 5) : "?";
    console.log(`   - ${time}: ${a.nome || "?"} - ${a.servizio || "?"}`);
  });
} catch (e) {
  console.log(`   ❌ Error: ${e.message}`);
}

// Test 5: FAQ files
console.log("\n📚 Test FAQ files:");
const fs = require("fs");
const faqDir = path.join(__dirname, "../voice-agent/data");
const verticals = ["salone", "wellness", "medical", "auto", "altro"];
for (const v of verticals) {
  const faqPath = path.join(faqDir, `faq_${v}.json`);
  if (fs.existsSync(faqPath)) {
    try {
      const data = JSON.parse(fs.readFileSync(faqPath, "utf-8"));
      const count = Array.isArray(data) ? data.length : (data.faq_entries?.length || 0);
      console.log(`   faq_${v}.json: ${count} FAQ ✅`);
    } catch (e) {
      console.log(`   faq_${v}.json: ❌ parse error`);
    }
  } else {
    console.log(`   faq_${v}.json: ❌ not found`);
  }
}

// Test 6: Operatori
console.log("\n👥 Test operatori:");
try {
  const operators = db.prepare("SELECT id, nome, cognome FROM operatori LIMIT 5").all();
  console.log(`   Found ${operators.length} operators:`);
  operators.forEach(o => {
    console.log(`   - ${o.nome} ${o.cognome}`);
  });
} catch (e) {
  console.log(`   ❌ Error: ${e.message}`);
}

// Summary
console.log("\n" + "=".repeat(60));
console.log("✅ MCP Server Functional Test Complete");
console.log("=".repeat(60));
console.log("\nTo run MCP server:");
console.log("  cd mcp-server && npm start\n");

db.close();
