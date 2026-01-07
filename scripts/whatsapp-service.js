#!/usr/bin/env node
/**
 * FLUXION - WhatsApp Auto-Responder Service
 * Uses whatsapp-web.js for local WhatsApp Web automation
 * Integrates with FLUXION IA (Groq) for intelligent auto-responses
 *
 * Usage:
 *   node scripts/whatsapp-service.js start    - Start service with QR login
 *   node scripts/whatsapp-service.js status   - Check connection status
 *   node scripts/whatsapp-service.js send <phone> <message>
 */

const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

// ═══════════════════════════════════════════════════════════════════
// CONFIGURATION
// ═══════════════════════════════════════════════════════════════════

const DATA_DIR = path.join(__dirname, '..', '.whatsapp-session');
const STATUS_FILE = path.join(DATA_DIR, 'status.json');
const CONFIG_FILE = path.join(DATA_DIR, 'config.json');
const MESSAGES_LOG = path.join(DATA_DIR, 'messages.jsonl');

// Default config
const DEFAULT_CONFIG = {
  autoResponderEnabled: true,
  faqCategory: 'salone',
  welcomeMessage: 'Ciao! Sono l\'assistente automatico. Come posso aiutarti?',
  businessName: 'FLUXION',
  businessPhone: process.env.WHATSAPP_PHONE || '',
  groqApiKey: process.env.GROQ_API_KEY || '',
  responseDelay: 1000, // ms delay before responding (more natural)
  maxResponsesPerHour: 60, // rate limit
};

// Ensure data directory exists
if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

// ═══════════════════════════════════════════════════════════════════
// CONFIGURATION MANAGEMENT
// ═══════════════════════════════════════════════════════════════════

function loadConfig() {
  if (!fs.existsSync(CONFIG_FILE)) {
    saveConfig(DEFAULT_CONFIG);
    return DEFAULT_CONFIG;
  }
  try {
    const content = fs.readFileSync(CONFIG_FILE, 'utf8');
    return { ...DEFAULT_CONFIG, ...JSON.parse(content) };
  } catch {
    return DEFAULT_CONFIG;
  }
}

function saveConfig(config) {
  fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2));
}

// ═══════════════════════════════════════════════════════════════════
// FAQ LOADING & RETRIEVAL
// ═══════════════════════════════════════════════════════════════════

function loadFaqs(category) {
  const filename = `faq_${category.toLowerCase()}.md`;
  const faqPath = path.join(__dirname, '..', 'data', filename);

  if (!fs.existsSync(faqPath)) {
    console.log(`FAQ file not found: ${faqPath}`);
    return [];
  }

  const content = fs.readFileSync(faqPath, 'utf8');
  return parseFaqMarkdown(content);
}

function parseFaqMarkdown(content) {
  const entries = [];
  let currentSection = '';

  for (const line of content.split('\n')) {
    const trimmed = line.trim();

    if (trimmed.startsWith('## ')) {
      currentSection = trimmed.slice(3);
    } else if (trimmed.startsWith('- ')) {
      const parts = trimmed.slice(2).split(':');
      if (parts.length >= 2) {
        entries.push({
          section: currentSection,
          question: parts[0].trim(),
          answer: parts.slice(1).join(':').trim(),
        });
      }
    }
  }

  return entries;
}

function findRelevantFaqs(query, faqs, topK = 5) {
  const queryLower = query.toLowerCase();
  const queryWords = queryLower
    .split(/\s+/)
    .filter((w) => w.length > 2);

  if (queryWords.length === 0) {
    return [];
  }

  const scores = faqs
    .map((faq) => {
      const text = `${faq.section} ${faq.question} ${faq.answer}`.toLowerCase();
      let score = 0;

      for (const word of queryWords) {
        if (text.includes(word)) {
          score += 1;
          if (faq.question.toLowerCase().includes(word)) {
            score += 0.5;
          }
        }
      }

      score /= queryWords.length;
      return { faq, score };
    })
    .filter(({ score }) => score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, topK);

  return scores;
}

// ═══════════════════════════════════════════════════════════════════
// GROQ LLM INTEGRATION
// ═══════════════════════════════════════════════════════════════════

async function callGroq(apiKey, systemPrompt, userMessage) {
  const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: 'llama-3.1-8b-instant',
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userMessage },
      ],
      temperature: 0.3,
      max_tokens: 300,
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Groq API error: ${response.status} - ${error}`);
  }

  const data = await response.json();
  return data.choices?.[0]?.message?.content || '';
}

async function generateAutoResponse(question, config) {
  const faqs = loadFaqs(config.faqCategory);
  const relevant = findRelevantFaqs(question, faqs);

  // Build context from relevant FAQs
  let context = '';
  for (const { faq, score } of relevant) {
    context += `Q: ${faq.question}\nA: ${faq.answer}\n\n`;
  }

  const systemPrompt = `Sei l'assistente WhatsApp di "${config.businessName}".

KNOWLEDGE BASE:
${context || 'Nessuna FAQ trovata per questa domanda.'}

REGOLE IMPORTANTI:
- Rispondi SOLO usando le informazioni dalla KNOWLEDGE BASE
- Se la domanda non è coperta, rispondi: "Mi dispiace, non ho questa informazione. Ti consiglio di chiamarci o passare in negozio!"
- Risposte BREVI (max 2-3 frasi, adatte a WhatsApp)
- Tono cordiale e professionale
- Puoi usare 1-2 emoji se appropriato
- NON inventare informazioni`;

  try {
    return await callGroq(config.groqApiKey, systemPrompt, question);
  } catch (error) {
    console.error('Groq API error:', error.message);
    return "Mi dispiace, c'è un problema tecnico. Prova a chiamarci direttamente!";
  }
}

// ═══════════════════════════════════════════════════════════════════
// RATE LIMITING
// ═══════════════════════════════════════════════════════════════════

const responseCounters = new Map(); // phone -> { count, resetTime }

function checkRateLimit(phone, config) {
  const now = Date.now();
  const hour = 60 * 60 * 1000;

  let counter = responseCounters.get(phone);
  if (!counter || now > counter.resetTime) {
    counter = { count: 0, resetTime: now + hour };
    responseCounters.set(phone, counter);
  }

  if (counter.count >= config.maxResponsesPerHour) {
    return false;
  }

  counter.count++;
  return true;
}

// ═══════════════════════════════════════════════════════════════════
// STATUS MANAGEMENT
// ═══════════════════════════════════════════════════════════════════

function getChromePath() {
  const platform = process.platform;
  const possiblePaths = {
    darwin: [
      '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
      '/Applications/Chromium.app/Contents/MacOS/Chromium',
    ],
    win32: [
      'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
      'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
      process.env.LOCALAPPDATA + '\\Google\\Chrome\\Application\\chrome.exe',
    ],
    linux: [
      '/usr/bin/google-chrome',
      '/usr/bin/chromium-browser',
      '/usr/bin/chromium',
    ],
  };

  const paths = possiblePaths[platform] || [];
  for (const p of paths) {
    if (fs.existsSync(p)) {
      return p;
    }
  }
  return null;
}

function updateStatus(status, info = {}) {
  const config = loadConfig();
  const data = {
    status,
    timestamp: new Date().toISOString(),
    autoResponderEnabled: config.autoResponderEnabled,
    faqCategory: config.faqCategory,
    ...info,
  };
  fs.writeFileSync(STATUS_FILE, JSON.stringify(data, null, 2));
  console.log(`[Status] ${status}`);
}

function getStatus() {
  if (!fs.existsSync(STATUS_FILE)) {
    return { status: 'not_initialized' };
  }
  return JSON.parse(fs.readFileSync(STATUS_FILE, 'utf8'));
}

function logMessage(messageData) {
  fs.appendFileSync(MESSAGES_LOG, JSON.stringify(messageData) + '\n');
}

// ═══════════════════════════════════════════════════════════════════
// WHATSAPP SERVICE
// ═══════════════════════════════════════════════════════════════════

async function startService() {
  console.log('═'.repeat(60));
  console.log('  FLUXION - WhatsApp Auto-Responder Service');
  console.log('═'.repeat(60));
  console.log('');

  const config = loadConfig();

  // Validate config
  if (!config.groqApiKey) {
    console.log('⚠️  GROQ_API_KEY not set. Auto-responses will use fallback messages.');
    console.log('   Set it in .env or via FLUXION app settings.');
    console.log('');
  }

  console.log(`📋 FAQ Category: ${config.faqCategory}`);
  console.log(`🤖 Auto-Responder: ${config.autoResponderEnabled ? 'ENABLED' : 'DISABLED'}`);
  console.log('');

  updateStatus('initializing');

  const chromePath = getChromePath();
  if (chromePath) {
    console.log(`🌐 Using Chrome: ${chromePath}`);
  } else {
    console.log('⚠️  Chrome not found. Will try Puppeteer bundled Chromium.');
  }

  const puppeteerConfig = {
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-accelerated-2d-canvas',
      '--no-first-run',
      '--no-zygote',
      '--disable-gpu',
    ],
  };

  if (chromePath) {
    puppeteerConfig.executablePath = chromePath;
  }

  const client = new Client({
    authStrategy: new LocalAuth({
      dataPath: DATA_DIR,
    }),
    puppeteer: puppeteerConfig,
  });

  // ─── QR Code ───
  client.on('qr', (qr) => {
    console.log('\n');
    console.log('═'.repeat(60));
    console.log('  📱 SCAN THIS QR CODE WITH WHATSAPP');
    console.log('═'.repeat(60));
    qrcode.generate(qr, { small: true });
    console.log('\n  Open WhatsApp > Settings > Linked Devices > Link a Device');
    console.log('═'.repeat(60));
    updateStatus('waiting_qr', { qr });
  });

  // ─── Loading ───
  client.on('loading_screen', (percent, message) => {
    console.log(`[Loading] ${percent}% - ${message}`);
    updateStatus('loading', { percent, message });
  });

  // ─── Auth ───
  client.on('authenticated', () => {
    console.log('✅ Authenticated with WhatsApp!');
    updateStatus('authenticated');
  });

  client.on('auth_failure', (msg) => {
    console.error('❌ Authentication failed:', msg);
    updateStatus('auth_failed', { error: msg });
  });

  // ─── Ready ───
  client.on('ready', () => {
    console.log('\n');
    console.log('═'.repeat(60));
    console.log('  ✅ WhatsApp Auto-Responder READY!');
    console.log('═'.repeat(60));
    console.log(`  Phone: ${client.info?.wid?.user || 'unknown'}`);
    console.log(`  Name: ${client.info?.pushname || 'unknown'}`);
    console.log('═'.repeat(60));
    console.log('');

    updateStatus('ready', {
      phone: client.info?.wid?.user || 'unknown',
      name: client.info?.pushname || 'unknown',
    });
  });

  // ─── Disconnected ───
  client.on('disconnected', (reason) => {
    console.log('❌ Disconnected:', reason);
    updateStatus('disconnected', { reason });
  });

  // ─── Message Handler (AUTO-RESPONDER) ───
  client.on('message', async (msg) => {
    // Ignore non-text messages, group messages, and own messages
    if (msg.type !== 'chat' || msg.isGroupMsg || msg.fromMe) {
      return;
    }

    const contact = await msg.getContact();
    const fromPhone = msg.from.replace('@c.us', '');
    const messageData = {
      from: fromPhone,
      name: contact.pushname || contact.name || 'Unknown',
      body: msg.body,
      timestamp: new Date().toISOString(),
      type: 'received',
    };

    logMessage(messageData);

    console.log(`\n📨 Message from ${messageData.name} (${fromPhone}):`);
    console.log(`   "${msg.body.substring(0, 100)}${msg.body.length > 100 ? '...' : ''}"`);

    // Check if auto-responder is enabled
    const config = loadConfig();
    if (!config.autoResponderEnabled) {
      console.log('   [Auto-responder disabled - no response sent]');
      return;
    }

    // Rate limiting
    if (!checkRateLimit(fromPhone, config)) {
      console.log('   [Rate limit reached - no response sent]');
      return;
    }

    // Generate response
    console.log('   🤖 Generating response...');

    let response;
    if (config.groqApiKey) {
      response = await generateAutoResponse(msg.body, config);
    } else {
      // Fallback: simple FAQ search without LLM
      const faqs = loadFaqs(config.faqCategory);
      const relevant = findRelevantFaqs(msg.body, faqs, 1);
      if (relevant.length > 0) {
        response = `${relevant[0].faq.answer}\n\nPer altre info, chiamaci o passa a trovarci! 😊`;
      } else {
        response = config.welcomeMessage;
      }
    }

    // Add delay for more natural feel
    await new Promise((r) => setTimeout(r, config.responseDelay));

    // Send response
    try {
      await msg.reply(response);

      const responseData = {
        to: fromPhone,
        body: response,
        timestamp: new Date().toISOString(),
        type: 'sent',
        inReplyTo: messageData.body.substring(0, 50),
      };
      logMessage(responseData);

      console.log(`   ✅ Response sent: "${response.substring(0, 60)}..."`);
    } catch (error) {
      console.error(`   ❌ Failed to send: ${error.message}`);
    }
  });

  // ─── Initialize ───
  try {
    await client.initialize();
  } catch (err) {
    console.error('❌ Failed to initialize:', err.message);
    updateStatus('error', { error: err.message });
    process.exit(1);
  }

  // ─── Graceful Shutdown ───
  process.on('SIGINT', async () => {
    console.log('\n\n🛑 Shutting down gracefully...');
    await client.destroy();
    updateStatus('stopped');
    process.exit(0);
  });

  process.on('SIGTERM', async () => {
    console.log('\n\n🛑 Shutting down gracefully...');
    await client.destroy();
    updateStatus('stopped');
    process.exit(0);
  });
}

// ═══════════════════════════════════════════════════════════════════
// CLI COMMANDS
// ═══════════════════════════════════════════════════════════════════

async function sendMessage(phone, message) {
  console.log(`📤 Sending message to ${phone}...`);

  const status = getStatus();
  if (status.status !== 'ready') {
    console.error('❌ WhatsApp not connected.');
    console.error('   Run: node scripts/whatsapp-service.js start');
    process.exit(1);
  }

  const chatId = phone.includes('@') ? phone : `${phone.replace(/\D/g, '')}@c.us`;

  const chromePath = getChromePath();
  const client = new Client({
    authStrategy: new LocalAuth({
      dataPath: DATA_DIR,
    }),
    puppeteer: {
      headless: true,
      executablePath: chromePath || undefined,
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
    },
  });

  client.on('ready', async () => {
    try {
      await client.sendMessage(chatId, message);
      console.log('✅ Message sent successfully!');
      await client.destroy();
      process.exit(0);
    } catch (err) {
      console.error('❌ Failed to send:', err.message);
      await client.destroy();
      process.exit(1);
    }
  });

  await client.initialize();
}

function showHelp() {
  console.log(`
═══════════════════════════════════════════════════════════════
  FLUXION WhatsApp Auto-Responder Service
═══════════════════════════════════════════════════════════════

COMMANDS:
  start               Start WhatsApp service (shows QR for login)
  status              Check connection status
  send <phone> <msg>  Send a message manually
  config              Show current configuration
  enable              Enable auto-responder
  disable             Disable auto-responder
  category <name>     Set FAQ category (salone, auto, wellness, medical)

EXAMPLES:
  node scripts/whatsapp-service.js start
  node scripts/whatsapp-service.js status
  node scripts/whatsapp-service.js send 393281234567 "Ciao!"
  node scripts/whatsapp-service.js category salone
  node scripts/whatsapp-service.js enable

ENVIRONMENT VARIABLES:
  GROQ_API_KEY        API key for FLUXION IA (Groq LLM)
  WHATSAPP_PHONE      Your WhatsApp business phone number

`);
}

// ═══════════════════════════════════════════════════════════════════
// MAIN
// ═══════════════════════════════════════════════════════════════════

const args = process.argv.slice(2);
const command = args[0];

switch (command) {
  case 'start':
    startService();
    break;

  case 'status':
    const status = getStatus();
    console.log(JSON.stringify(status, null, 2));
    break;

  case 'config':
    const config = loadConfig();
    console.log(JSON.stringify(config, null, 2));
    break;

  case 'enable':
    const cfg1 = loadConfig();
    cfg1.autoResponderEnabled = true;
    saveConfig(cfg1);
    console.log('✅ Auto-responder ENABLED');
    break;

  case 'disable':
    const cfg2 = loadConfig();
    cfg2.autoResponderEnabled = false;
    saveConfig(cfg2);
    console.log('✅ Auto-responder DISABLED');
    break;

  case 'category':
    if (!args[1]) {
      console.error('Usage: category <name>');
      console.error('Available: salone, auto, wellness, medical');
      process.exit(1);
    }
    const cfg3 = loadConfig();
    cfg3.faqCategory = args[1].toLowerCase();
    saveConfig(cfg3);
    console.log(`✅ FAQ category set to: ${cfg3.faqCategory}`);
    break;

  case 'send':
    if (args.length < 3) {
      console.error('Usage: send <phone> <message>');
      process.exit(1);
    }
    sendMessage(args[1], args.slice(2).join(' '));
    break;

  default:
    showHelp();
}
