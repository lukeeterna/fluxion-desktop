/**
 * FLUXION MCP Server
 * Model Context Protocol server for Claude Code integration
 *
 * Tools:
 * - search_clienti: Search clients by phone/name/email
 * - create_appuntamento: Create new appointment
 * - get_disponibilita: Get available time slots
 * - get_faq: Get FAQ entries by vertical
 * - list_servizi: List services by vertical
 * - list_operatori: List operators
 *
 * Resources:
 * - fluxion://clienti: All clients
 * - fluxion://servizi: All services
 * - fluxion://faq/{verticale}: FAQ by vertical
 * - fluxion://appuntamenti/oggi: Today's appointments
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListResourcesRequestSchema,
  ListToolsRequestSchema,
  ReadResourceRequestSchema,
  Tool,
} from "@modelcontextprotocol/sdk/types.js";
import Database from "better-sqlite3";
import * as path from "path";
import * as os from "os";
import * as dotenv from "dotenv";

// Load environment variables
dotenv.config({ path: path.join(__dirname, "../.env") });

// Database path - macOS default
const getDbPath = (): string => {
  const customPath = process.env.FLUXION_DB_PATH;
  if (customPath) {
    return customPath.replace("~", os.homedir());
  }
  return path.join(os.homedir(), "Library/Application Support/fluxion/fluxion.db");
};

// Initialize database connection
let db: Database.Database;
try {
  const dbPath = getDbPath();
  db = new Database(dbPath, { readonly: false });
  db.pragma("journal_mode = WAL");
  console.error(`[MCP] Connected to database: ${dbPath}`);
} catch (error) {
  console.error(`[MCP] Database connection failed: ${error}`);
  process.exit(1);
}

// Initialize MCP Server
const server = new Server(
  {
    name: "fluxion-mcp",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
      resources: {},
    },
  }
);

// ============================================================
// TOOL DEFINITIONS
// ============================================================

const tools: Tool[] = [
  {
    name: "search_clienti",
    description: "Search for clients by phone number, email, name, or nickname (soprannome). Returns matching clients with their details.",
    inputSchema: {
      type: "object",
      properties: {
        query: {
          type: "string",
          description: "Search query - can be phone number, email, name, or nickname",
        },
        limit: {
          type: "number",
          description: "Maximum number of results to return (default: 10, max: 50)",
        },
      },
      required: ["query"],
    },
  },
  {
    name: "create_appuntamento",
    description: "Create a new appointment for a client. Requires client_id, servizio_id, date, and start time.",
    inputSchema: {
      type: "object",
      properties: {
        cliente_id: {
          type: "string",
          description: "Client ID (UUID)",
        },
        servizio_id: {
          type: "string",
          description: "Service ID (UUID)",
        },
        operatore_id: {
          type: "string",
          description: "Operator ID (optional)",
        },
        data: {
          type: "string",
          description: "Appointment date in YYYY-MM-DD format",
        },
        ora_inizio: {
          type: "string",
          description: "Start time in HH:MM format (24h)",
        },
        note: {
          type: "string",
          description: "Optional notes for the appointment",
        },
      },
      required: ["cliente_id", "servizio_id", "data", "ora_inizio"],
    },
  },
  {
    name: "get_disponibilita",
    description: "Get available appointment slots for a specific date and optionally a specific operator.",
    inputSchema: {
      type: "object",
      properties: {
        data: {
          type: "string",
          description: "Date to check availability (YYYY-MM-DD)",
        },
        operatore_id: {
          type: "string",
          description: "Optional: specific operator ID to check",
        },
        servizio_id: {
          type: "string",
          description: "Optional: service ID to get duration for slot calculation",
        },
      },
      required: ["data"],
    },
  },
  {
    name: "get_faq",
    description: "Get FAQ entries for a specific business vertical (salone, wellness, medical, auto, altro).",
    inputSchema: {
      type: "object",
      properties: {
        verticale: {
          type: "string",
          enum: ["salone", "wellness", "medical", "auto", "altro"],
          description: "Business vertical to get FAQs for",
        },
        categoria: {
          type: "string",
          description: "Optional: filter by FAQ category (pricing, hours, booking, policy, etc.)",
        },
        limit: {
          type: "number",
          description: "Maximum number of FAQs to return (default: 20)",
        },
      },
      required: ["verticale"],
    },
  },
  {
    name: "list_servizi",
    description: "List all available services, optionally filtered by vertical.",
    inputSchema: {
      type: "object",
      properties: {
        verticale: {
          type: "string",
          enum: ["salone", "wellness", "medical", "auto", "altro"],
          description: "Optional: filter services by vertical",
        },
        attivo: {
          type: "boolean",
          description: "Optional: filter by active status (default: true)",
        },
      },
    },
  },
  {
    name: "list_operatori",
    description: "List all operators/staff members.",
    inputSchema: {
      type: "object",
      properties: {
        servizio_id: {
          type: "string",
          description: "Optional: filter operators who can perform this service",
        },
      },
    },
  },
  {
    name: "get_cliente",
    description: "Get detailed information about a specific client by ID.",
    inputSchema: {
      type: "object",
      properties: {
        cliente_id: {
          type: "string",
          description: "Client ID (UUID)",
        },
      },
      required: ["cliente_id"],
    },
  },
  {
    name: "get_appuntamenti_cliente",
    description: "Get appointments for a specific client.",
    inputSchema: {
      type: "object",
      properties: {
        cliente_id: {
          type: "string",
          description: "Client ID (UUID)",
        },
        stato: {
          type: "string",
          enum: ["confermato", "completato", "cancellato"],
          description: "Optional: filter by appointment status",
        },
        limit: {
          type: "number",
          description: "Maximum number of appointments to return (default: 10)",
        },
      },
      required: ["cliente_id"],
    },
  },
];

// ============================================================
// TOOL HANDLERS
// ============================================================

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools,
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case "search_clienti":
        return handleSearchClienti(args as { query: string; limit?: number });

      case "create_appuntamento":
        return handleCreateAppuntamento(args as {
          cliente_id: string;
          servizio_id: string;
          operatore_id?: string;
          data: string;
          ora_inizio: string;
          note?: string;
        });

      case "get_disponibilita":
        return handleGetDisponibilita(args as {
          data: string;
          operatore_id?: string;
          servizio_id?: string;
        });

      case "get_faq":
        return handleGetFaq(args as {
          verticale: string;
          categoria?: string;
          limit?: number;
        });

      case "list_servizi":
        return handleListServizi(args as {
          verticale?: string;
          attivo?: boolean;
        });

      case "list_operatori":
        return handleListOperatori(args as { servizio_id?: string });

      case "get_cliente":
        return handleGetCliente(args as { cliente_id: string });

      case "get_appuntamenti_cliente":
        return handleGetAppuntamentiCliente(args as {
          cliente_id: string;
          stato?: string;
          limit?: number;
        });

      default:
        return {
          content: [{ type: "text", text: `Unknown tool: ${name}` }],
          isError: true,
        };
    }
  } catch (error: any) {
    console.error(`[MCP] Tool error (${name}):`, error);
    return {
      content: [{ type: "text", text: `Error: ${error.message}` }],
      isError: true,
    };
  }
});

// ============================================================
// TOOL HANDLER IMPLEMENTATIONS
// ============================================================

function handleSearchClienti(args: { query: string; limit?: number }) {
  const { query, limit = 10 } = args;
  const safeLimit = Math.min(limit, 50);

  const stmt = db.prepare(`
    SELECT
      id, nome, cognome, telefono, email,
      data_nascita, soprannome, note, punti_fedelta,
      created_at
    FROM clienti
    WHERE
      telefono LIKE ? OR
      email LIKE ? OR
      nome LIKE ? OR
      cognome LIKE ? OR
      soprannome LIKE ?
    ORDER BY cognome, nome
    LIMIT ?
  `);

  const searchPattern = `%${query}%`;
  const results = stmt.all(
    searchPattern,
    searchPattern,
    searchPattern,
    searchPattern,
    searchPattern,
    safeLimit
  );

  return {
    content: [
      {
        type: "text",
        text: JSON.stringify(
          {
            count: results.length,
            query,
            clients: results,
          },
          null,
          2
        ),
      },
    ],
  };
}

function handleCreateAppuntamento(args: {
  cliente_id: string;
  servizio_id: string;
  operatore_id?: string;
  data: string;
  ora_inizio: string;
  note?: string;
}) {
  const { cliente_id, servizio_id, operatore_id, data, ora_inizio, note } = args;

  // Get service duration to calculate end time
  const servizio = db
    .prepare("SELECT id, nome, durata_minuti, prezzo FROM servizi WHERE id = ?")
    .get(servizio_id) as any;

  if (!servizio) {
    throw new Error(`Service not found: ${servizio_id}`);
  }

  // Verify client exists
  const cliente = db
    .prepare("SELECT id, nome, cognome FROM clienti WHERE id = ?")
    .get(cliente_id) as any;

  if (!cliente) {
    throw new Error(`Client not found: ${cliente_id}`);
  }

  // Calculate start/end datetime
  const [hours, minutes] = ora_inizio.split(":").map(Number);
  const startMinutes = hours * 60 + minutes;
  const endMinutes = startMinutes + servizio.durata_minuti;
  const endHours = Math.floor(endMinutes / 60);
  const endMins = endMinutes % 60;
  const ora_fine = `${String(endHours).padStart(2, "0")}:${String(endMins).padStart(2, "0")}`;

  // Build ISO datetimes
  const data_ora_inizio = `${data}T${ora_inizio}:00`;
  const data_ora_fine = `${data}T${ora_fine}:00`;

  // Check for conflicts
  const conflict = db
    .prepare(`
      SELECT id FROM appuntamenti
      WHERE date(data_ora_inizio) = ?
        AND stato != 'cancellato'
        AND (
          (data_ora_inizio <= ? AND data_ora_fine > ?) OR
          (data_ora_inizio < ? AND data_ora_fine >= ?) OR
          (data_ora_inizio >= ? AND data_ora_fine <= ?)
        )
        ${operatore_id ? "AND operatore_id = ?" : ""}
    `)
    .get(
      data,
      data_ora_inizio, data_ora_inizio,
      data_ora_fine, data_ora_fine,
      data_ora_inizio, data_ora_fine,
      ...(operatore_id ? [operatore_id] : [])
    );

  if (conflict) {
    throw new Error(`Time slot conflict: another appointment exists at ${data} ${ora_inizio}`);
  }

  // Generate UUID
  const id = `app_${Date.now()}_${Math.random().toString(36).substring(2, 11)}`;

  // Insert appointment
  const stmt = db.prepare(`
    INSERT INTO appuntamenti (
      id, cliente_id, servizio_id, operatore_id,
      data_ora_inizio, data_ora_fine, durata_minuti, stato,
      prezzo, prezzo_finale, note,
      created_at, updated_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, 'confermato', ?, ?, ?, datetime('now'), datetime('now'))
  `);

  stmt.run(
    id,
    cliente_id,
    servizio_id,
    operatore_id || null,
    data_ora_inizio,
    data_ora_fine,
    servizio.durata_minuti,
    servizio.prezzo,
    servizio.prezzo,
    note || null
  );

  return {
    content: [
      {
        type: "text",
        text: JSON.stringify(
          {
            success: true,
            appointment: {
              id,
              cliente: `${cliente.nome} ${cliente.cognome}`,
              servizio: servizio.nome,
              data,
              ora_inizio,
              ora_fine,
              prezzo: servizio.prezzo,
            },
            message: `Appointment created for ${cliente.nome} ${cliente.cognome} on ${data} at ${ora_inizio}`,
          },
          null,
          2
        ),
      },
    ],
  };
}

function handleGetDisponibilita(args: {
  data: string;
  operatore_id?: string;
  servizio_id?: string;
}) {
  const { data, operatore_id, servizio_id } = args;

  // Get service duration if provided
  let slotDuration = 30; // default 30 minutes
  if (servizio_id) {
    const servizio = db
      .prepare("SELECT durata_minuti FROM servizi WHERE id = ?")
      .get(servizio_id) as any;
    if (servizio) {
      slotDuration = servizio.durata_minuti;
    }
  }

  // Get occupied slots for the given date
  let query = `
    SELECT data_ora_inizio, data_ora_fine, operatore_id
    FROM appuntamenti
    WHERE date(data_ora_inizio) = ? AND stato != 'cancellato'
  `;
  const params: any[] = [data];

  if (operatore_id) {
    query += " AND operatore_id = ?";
    params.push(operatore_id);
  }

  const occupied = db.prepare(query).all(...params) as any[];

  // Generate available slots (9:00 - 19:00)
  const slots: string[] = [];

  for (let hour = 9; hour < 19; hour++) {
    for (let minute = 0; minute < 60; minute += 30) {
      const time = `${String(hour).padStart(2, "0")}:${String(minute).padStart(2, "0")}`;

      // Check if slot would extend past closing time
      const slotEnd = hour * 60 + minute + slotDuration;
      if (slotEnd > 19 * 60) continue;

      // Check for conflicts
      let isAvailable = true;
      for (const occ of occupied) {
        // Extract time from ISO datetime
        const occStartTime = occ.data_ora_inizio.split("T")[1]?.substring(0, 5) || "00:00";
        const occEndTime = occ.data_ora_fine.split("T")[1]?.substring(0, 5) || "00:00";
        const occStart = occStartTime.split(":").map(Number);
        const occEnd = occEndTime.split(":").map(Number);
        const occStartMins = occStart[0] * 60 + occStart[1];
        const occEndMins = occEnd[0] * 60 + occEnd[1];
        const slotStartMins = hour * 60 + minute;
        const slotEndMins = slotStartMins + slotDuration;

        if (
          (slotStartMins >= occStartMins && slotStartMins < occEndMins) ||
          (slotEndMins > occStartMins && slotEndMins <= occEndMins) ||
          (slotStartMins <= occStartMins && slotEndMins >= occEndMins)
        ) {
          isAvailable = false;
          break;
        }
      }

      if (isAvailable) {
        slots.push(time);
      }
    }
  }

  return {
    content: [
      {
        type: "text",
        text: JSON.stringify(
          {
            data,
            operatore_id: operatore_id || "any",
            slot_duration_minutes: slotDuration,
            available_slots: slots,
            occupied_count: occupied.length,
          },
          null,
          2
        ),
      },
    ],
  };
}

function handleGetFaq(args: {
  verticale: string;
  categoria?: string;
  limit?: number;
}) {
  const { verticale, categoria, limit = 20 } = args;

  // Try to read from JSON files first (FLUXION uses JSON FAQ files)
  const fs = require("fs");
  const faqPath = path.join(__dirname, `../../voice-agent/data/faq_${verticale}.json`);

  try {
    if (fs.existsSync(faqPath)) {
      const faqData = JSON.parse(fs.readFileSync(faqPath, "utf-8"));
      let faqs = Array.isArray(faqData) ? faqData : faqData.faq_entries || [];

      if (categoria) {
        faqs = faqs.filter((f: any) => f.category === categoria);
      }

      faqs = faqs.slice(0, limit);

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(
              {
                source: "json_file",
                verticale,
                categoria: categoria || "all",
                count: faqs.length,
                faqs,
              },
              null,
              2
            ),
          },
        ],
      };
    }
  } catch (e) {
    console.error(`[MCP] Error reading FAQ file: ${e}`);
  }

  // Fallback to database
  let query = `
    SELECT faq_id, domanda, risposta_template, categoria, keywords
    FROM faq_entries
    WHERE categoria_pmi = ?
  `;
  const params: any[] = [verticale];

  if (categoria) {
    query += " AND categoria = ?";
    params.push(categoria);
  }

  query += " LIMIT ?";
  params.push(limit);

  const results = db.prepare(query).all(...params);

  return {
    content: [
      {
        type: "text",
        text: JSON.stringify(
          {
            source: "database",
            verticale,
            categoria: categoria || "all",
            count: results.length,
            faqs: results,
          },
          null,
          2
        ),
      },
    ],
  };
}

function handleListServizi(args: { verticale?: string; attivo?: boolean }) {
  const { verticale, attivo = true } = args;

  let query = `
    SELECT id, nome, descrizione, prezzo, durata_minuti, categoria, colore, attivo
    FROM servizi
    WHERE 1=1
  `;
  const params: any[] = [];

  if (verticale) {
    query += " AND (categoria = ? OR categoria LIKE ?)";
    params.push(verticale, `%${verticale}%`);
  }

  if (attivo !== undefined) {
    query += " AND attivo = ?";
    params.push(attivo ? 1 : 0);
  }

  query += " ORDER BY categoria, nome";

  const results = db.prepare(query).all(...params);

  return {
    content: [
      {
        type: "text",
        text: JSON.stringify(
          {
            count: results.length,
            verticale: verticale || "all",
            services: results,
          },
          null,
          2
        ),
      },
    ],
  };
}

function handleListOperatori(args: { servizio_id?: string }) {
  const { servizio_id } = args;

  let query = `
    SELECT id, nome, cognome, telefono, email, servizi_ids, orari_disponibilita
    FROM operatori
  `;

  const results = db.prepare(query).all() as any[];

  // Filter by service if provided
  let filtered = results;
  if (servizio_id) {
    filtered = results.filter((op) => {
      if (!op.servizi_ids) return false;
      try {
        const servizi = JSON.parse(op.servizi_ids);
        return servizi.includes(servizio_id);
      } catch {
        return op.servizi_ids.includes(servizio_id);
      }
    });
  }

  return {
    content: [
      {
        type: "text",
        text: JSON.stringify(
          {
            count: filtered.length,
            servizio_filter: servizio_id || "none",
            operators: filtered,
          },
          null,
          2
        ),
      },
    ],
  };
}

function handleGetCliente(args: { cliente_id: string }) {
  const { cliente_id } = args;

  const cliente = db
    .prepare(`
      SELECT
        id, nome, cognome, telefono, email,
        data_nascita, soprannome, note, punti_fedelta,
        created_at, updated_at
      FROM clienti
      WHERE id = ?
    `)
    .get(cliente_id);

  if (!cliente) {
    throw new Error(`Client not found: ${cliente_id}`);
  }

  // Get recent appointments
  const appointments = db
    .prepare(`
      SELECT
        a.id, a.data_ora_inizio, a.data_ora_fine, a.stato,
        s.nome as servizio_nome, s.prezzo
      FROM appuntamenti a
      JOIN servizi s ON a.servizio_id = s.id
      WHERE a.cliente_id = ?
      ORDER BY a.data_ora_inizio DESC
      LIMIT 5
    `)
    .all(cliente_id);

  return {
    content: [
      {
        type: "text",
        text: JSON.stringify(
          {
            client: cliente,
            recent_appointments: appointments,
          },
          null,
          2
        ),
      },
    ],
  };
}

function handleGetAppuntamentiCliente(args: {
  cliente_id: string;
  stato?: string;
  limit?: number;
}) {
  const { cliente_id, stato, limit = 10 } = args;

  let query = `
    SELECT
      a.id, a.data_ora_inizio, a.data_ora_fine, a.stato, a.note,
      s.nome as servizio_nome, s.prezzo, s.durata_minuti,
      o.nome as operatore_nome, o.cognome as operatore_cognome
    FROM appuntamenti a
    JOIN servizi s ON a.servizio_id = s.id
    LEFT JOIN operatori o ON a.operatore_id = o.id
    WHERE a.cliente_id = ?
  `;
  const params: any[] = [cliente_id];

  if (stato) {
    query += " AND a.stato = ?";
    params.push(stato);
  }

  query += " ORDER BY a.data_ora_inizio DESC LIMIT ?";
  params.push(limit);

  const results = db.prepare(query).all(...params);

  return {
    content: [
      {
        type: "text",
        text: JSON.stringify(
          {
            cliente_id,
            stato_filter: stato || "all",
            count: results.length,
            appointments: results,
          },
          null,
          2
        ),
      },
    ],
  };
}

// ============================================================
// RESOURCE HANDLERS
// ============================================================

server.setRequestHandler(ListResourcesRequestSchema, async () => ({
  resources: [
    {
      uri: "fluxion://clienti",
      name: "All Clients",
      description: "List of all clients in the FLUXION system",
      mimeType: "application/json",
    },
    {
      uri: "fluxion://servizi",
      name: "All Services",
      description: "List of all available services",
      mimeType: "application/json",
    },
    {
      uri: "fluxion://operatori",
      name: "All Operators",
      description: "List of all staff/operators",
      mimeType: "application/json",
    },
    {
      uri: "fluxion://appuntamenti/oggi",
      name: "Today's Appointments",
      description: "All appointments scheduled for today",
      mimeType: "application/json",
    },
    {
      uri: "fluxion://faq/salone",
      name: "FAQ - Salone",
      description: "FAQ entries for hair salons",
      mimeType: "application/json",
    },
    {
      uri: "fluxion://faq/wellness",
      name: "FAQ - Wellness",
      description: "FAQ entries for gyms and spas",
      mimeType: "application/json",
    },
    {
      uri: "fluxion://faq/medical",
      name: "FAQ - Medical",
      description: "FAQ entries for medical clinics",
      mimeType: "application/json",
    },
    {
      uri: "fluxion://faq/auto",
      name: "FAQ - Auto",
      description: "FAQ entries for auto repair shops",
      mimeType: "application/json",
    },
    {
      uri: "fluxion://stats",
      name: "System Statistics",
      description: "FLUXION system statistics and counts",
      mimeType: "application/json",
    },
  ],
}));

server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const { uri } = request.params;

  try {
    if (uri === "fluxion://clienti") {
      const clients = db
        .prepare(`
          SELECT id, nome, cognome, telefono, email, punti_fedelta
          FROM clienti
          ORDER BY cognome, nome
          LIMIT 100
        `)
        .all();

      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify({ count: clients.length, clients }, null, 2),
          },
        ],
      };
    }

    if (uri === "fluxion://servizi") {
      const services = db
        .prepare(`
          SELECT id, nome, prezzo, durata_minuti, categoria, attivo
          FROM servizi
          WHERE attivo = 1
          ORDER BY categoria, nome
        `)
        .all();

      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify({ count: services.length, services }, null, 2),
          },
        ],
      };
    }

    if (uri === "fluxion://operatori") {
      const operators = db
        .prepare(`
          SELECT id, nome, cognome, telefono, email
          FROM operatori
          ORDER BY cognome, nome
        `)
        .all();

      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify({ count: operators.length, operators }, null, 2),
          },
        ],
      };
    }

    if (uri === "fluxion://appuntamenti/oggi") {
      const appointments = db
        .prepare(`
          SELECT
            a.id, a.data_ora_inizio, a.data_ora_fine, a.stato,
            c.nome as cliente_nome, c.cognome as cliente_cognome, c.telefono,
            s.nome as servizio_nome, s.prezzo
          FROM appuntamenti a
          JOIN clienti c ON a.cliente_id = c.id
          JOIN servizi s ON a.servizio_id = s.id
          WHERE date(a.data_ora_inizio) = DATE('now')
          ORDER BY a.data_ora_inizio
        `)
        .all();

      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify(
              {
                date: new Date().toISOString().split("T")[0],
                count: appointments.length,
                appointments,
              },
              null,
              2
            ),
          },
        ],
      };
    }

    // FAQ resources
    if (uri.startsWith("fluxion://faq/")) {
      const verticale = uri.replace("fluxion://faq/", "");
      const fs = require("fs");
      const faqPath = path.join(__dirname, `../../voice-agent/data/faq_${verticale}.json`);

      if (fs.existsSync(faqPath)) {
        const faqData = JSON.parse(fs.readFileSync(faqPath, "utf-8"));
        const faqs = Array.isArray(faqData) ? faqData : faqData.faq_entries || [];

        return {
          contents: [
            {
              uri,
              mimeType: "application/json",
              text: JSON.stringify(
                {
                  verticale,
                  count: faqs.length,
                  faqs: faqs.slice(0, 50),
                },
                null,
                2
              ),
            },
          ],
        };
      }
    }

    if (uri === "fluxion://stats") {
      const clientCount = db.prepare("SELECT COUNT(*) as count FROM clienti").get() as any;
      const appointmentCount = db.prepare("SELECT COUNT(*) as count FROM appuntamenti").get() as any;
      const serviceCount = db.prepare("SELECT COUNT(*) as count FROM servizi WHERE attivo = 1").get() as any;
      const operatorCount = db.prepare("SELECT COUNT(*) as count FROM operatori").get() as any;
      const todayAppointments = db
        .prepare("SELECT COUNT(*) as count FROM appuntamenti WHERE date(data_ora_inizio) = DATE('now')")
        .get() as any;

      return {
        contents: [
          {
            uri,
            mimeType: "application/json",
            text: JSON.stringify(
              {
                timestamp: new Date().toISOString(),
                stats: {
                  total_clients: clientCount.count,
                  total_appointments: appointmentCount.count,
                  active_services: serviceCount.count,
                  operators: operatorCount.count,
                  appointments_today: todayAppointments.count,
                },
              },
              null,
              2
            ),
          },
        ],
      };
    }

    return {
      contents: [
        {
          uri,
          mimeType: "text/plain",
          text: `Unknown resource: ${uri}`,
        },
      ],
    };
  } catch (error: any) {
    console.error(`[MCP] Resource error (${uri}):`, error);
    return {
      contents: [
        {
          uri,
          mimeType: "text/plain",
          text: `Error reading resource: ${error.message}`,
        },
      ],
    };
  }
});

// ============================================================
// SERVER STARTUP
// ============================================================

async function main() {
  console.error("[MCP] Starting FLUXION MCP Server...");

  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.error("[MCP] FLUXION MCP Server started successfully");
  console.error("[MCP] Tools available:", tools.map((t) => t.name).join(", "));
}

main().catch((error) => {
  console.error("[MCP] Fatal error:", error);
  process.exit(1);
});
