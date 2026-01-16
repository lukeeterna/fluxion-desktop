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
const PENDING_QUESTIONS_FILE = path.join(DATA_DIR, 'pending_questions.jsonl');
const CUSTOM_FAQ_FILE = path.join(__dirname, '..', 'data', 'faq_custom.md');

// Confidence threshold for auto-response
const CONFIDENCE_THRESHOLD = 0.5; // Below this = pass to operator

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
  const faqs = [];

  // 1. Load category-specific FAQs
  const filename = `faq_${category.toLowerCase()}.md`;
  const faqPath = path.join(__dirname, '..', 'data', filename);

  if (fs.existsSync(faqPath)) {
    const content = fs.readFileSync(faqPath, 'utf8');
    faqs.push(...parseFaqMarkdown(content));
  } else {
    console.log(`FAQ file not found: ${faqPath}`);
  }

  // 2. Load custom FAQs (operator-added) - ALWAYS loaded
  if (fs.existsSync(CUSTOM_FAQ_FILE)) {
    const customContent = fs.readFileSync(CUSTOM_FAQ_FILE, 'utf8');
    const customFaqs = parseFaqMarkdown(customContent);
    // Mark as custom for priority
    customFaqs.forEach(faq => faq.isCustom = true);
    faqs.push(...customFaqs);
    console.log(`📚 Loaded ${customFaqs.length} custom FAQs from operator`);
  }

  return faqs;
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
    return { results: [], maxConfidence: 0 };
  }

  const scores = faqs
    .map((faq) => {
      const text = `${faq.section} ${faq.question} ${faq.answer}`.toLowerCase();
      let score = 0;

      for (const word of queryWords) {
        if (text.includes(word)) {
          score += 1;
          // Boost score for question match
          if (faq.question.toLowerCase().includes(word)) {
            score += 0.5;
          }
          // Boost custom FAQs (operator-verified)
          if (faq.isCustom) {
            score += 0.3;
          }
        }
      }

      score /= queryWords.length;
      return { faq, score };
    })
    .filter(({ score }) => score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, topK);

  const maxConfidence = scores.length > 0 ? scores[0].score : 0;
  return { results: scores, maxConfidence };
}

// ═══════════════════════════════════════════════════════════════════
// PENDING QUESTIONS (Learning System)
// ═══════════════════════════════════════════════════════════════════

function savePendingQuestion(question, fromPhone, fromName, config) {
  const entry = {
    id: `pq_${Date.now()}`,
    question: question,
    fromPhone: fromPhone,
    fromName: fromName,
    category: config.faqCategory,
    timestamp: new Date().toISOString(),
    status: 'pending', // pending | answered | saved_as_faq
    operatorResponse: null,
    responseTimestamp: null,
  };

  fs.appendFileSync(PENDING_QUESTIONS_FILE, JSON.stringify(entry) + '\n');
  console.log(`   📝 Question saved for operator review: "${question.substring(0, 50)}..."`);
  return entry.id;
}

function getPendingQuestions() {
  if (!fs.existsSync(PENDING_QUESTIONS_FILE)) {
    return [];
  }

  const content = fs.readFileSync(PENDING_QUESTIONS_FILE, 'utf8');
  return content
    .split('\n')
    .filter(line => line.trim())
    .map(line => {
      try {
        return JSON.parse(line);
      } catch {
        return null;
      }
    })
    .filter(Boolean);
}

function updatePendingQuestion(questionId, updates) {
  const questions = getPendingQuestions();
  const updatedQuestions = questions.map(q => {
    if (q.id === questionId) {
      return { ...q, ...updates };
    }
    return q;
  });

  // Rewrite file
  fs.writeFileSync(
    PENDING_QUESTIONS_FILE,
    updatedQuestions.map(q => JSON.stringify(q)).join('\n') + '\n'
  );
}

function appendToCustomFaq(question, answer, section = 'Risposte Operatore') {
  // Create file with header if it doesn't exist
  if (!fs.existsSync(CUSTOM_FAQ_FILE)) {
    const header = `# FAQ Custom - Aggiunte dall'Operatore

> Questo file contiene le FAQ aggiunte manualmente dall'operatore.
> Il bot le usa per rispondere automaticamente alle domande future.

`;
    fs.writeFileSync(CUSTOM_FAQ_FILE, header);
  }

  // Check if section exists, if not add it
  let content = fs.readFileSync(CUSTOM_FAQ_FILE, 'utf8');
  if (!content.includes(`## ${section}`)) {
    content += `\n## ${section}\n\n`;
  }

  // Append new Q&A
  const newEntry = `- ${question}: ${answer}\n`;

  // Find section and append
  const sectionIndex = content.indexOf(`## ${section}`);
  const nextSectionIndex = content.indexOf('\n## ', sectionIndex + 1);

  if (nextSectionIndex === -1) {
    // Append at end
    content += newEntry;
  } else {
    // Insert before next section
    content = content.slice(0, nextSectionIndex) + newEntry + content.slice(nextSectionIndex);
  }

  fs.writeFileSync(CUSTOM_FAQ_FILE, content);
  console.log(`✅ FAQ saved: "${question.substring(0, 30)}..." → "${answer.substring(0, 30)}..."`);
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

async function generateAutoResponse(question, config, messageContext = {}) {
  const faqs = loadFaqs(config.faqCategory);
  const { results: relevant, maxConfidence } = findRelevantFaqs(question, faqs);

  console.log(`   📊 Confidence: ${(maxConfidence * 100).toFixed(1)}% (threshold: ${CONFIDENCE_THRESHOLD * 100}%)`);

  // ─── LOW CONFIDENCE: Pass to operator ───
  if (maxConfidence < CONFIDENCE_THRESHOLD) {
    console.log(`   ⚠️  Low confidence - saving for operator review`);

    // Save pending question for operator
    savePendingQuestion(
      question,
      messageContext.fromPhone || 'unknown',
      messageContext.fromName || 'unknown',
      config
    );

    // Return honest "I don't know" message
    return {
      response: `Non ho informazioni sufficienti su questo argomento. 🤔\n\nHo inoltrato la tua domanda al team, ti risponderanno a breve!\n\nPer urgenze puoi chiamarci direttamente. 📞`,
      confidence: maxConfidence,
      passedToOperator: true,
    };
  }

  // ─── HIGH CONFIDENCE: Auto-respond ───

  // Build context from relevant FAQs
  let context = '';
  for (const { faq } of relevant) {
    context += `Q: ${faq.question}\nA: ${faq.answer}\n\n`;
  }

  const systemPrompt = `Sei l'assistente WhatsApp di "${config.businessName}".

KNOWLEDGE BASE:
${context}

REGOLE IMPORTANTI:
- Rispondi SOLO usando le informazioni dalla KNOWLEDGE BASE sopra
- NON INVENTARE MAI informazioni non presenti (orari, prezzi, servizi)
- Se non trovi l'informazione nella knowledge base, dì che non hai questa info
- Risposte BREVI (max 2-3 frasi, adatte a WhatsApp)
- Tono cordiale e professionale
- Puoi usare 1-2 emoji se appropriato`;

  try {
    const response = await callGroq(config.groqApiKey, systemPrompt, question);
    return {
      response,
      confidence: maxConfidence,
      passedToOperator: false,
    };
  } catch (error) {
    console.error('Groq API error:', error.message);
    return {
      response: "Mi dispiace, c'è un problema tecnico. Prova a chiamarci direttamente! 📞",
      confidence: 0,
      passedToOperator: true,
    };
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

    const messageContext = {
      fromPhone,
      fromName: messageData.name,
    };

    let responseResult;
    if (config.groqApiKey) {
      responseResult = await generateAutoResponse(msg.body, config, messageContext);
    } else {
      // Fallback: simple FAQ search without LLM
      const faqs = loadFaqs(config.faqCategory);
      const { results: relevant, maxConfidence } = findRelevantFaqs(msg.body, faqs, 1);

      if (maxConfidence >= CONFIDENCE_THRESHOLD && relevant.length > 0) {
        responseResult = {
          response: `${relevant[0].faq.answer}\n\nPer altre info, chiamaci o passa a trovarci! 😊`,
          confidence: maxConfidence,
          passedToOperator: false,
        };
      } else {
        // Low confidence - save for operator
        savePendingQuestion(msg.body, fromPhone, messageData.name, config);
        responseResult = {
          response: `Non ho informazioni sufficienti su questo. 🤔\n\nHo passato la domanda al team, ti risponderanno a breve! 📞`,
          confidence: maxConfidence,
          passedToOperator: true,
        };
      }
    }

    // Add delay for more natural feel
    await new Promise((r) => setTimeout(r, config.responseDelay));

    // Send response
    try {
      await msg.reply(responseResult.response);

      const responseData = {
        to: fromPhone,
        body: responseResult.response,
        timestamp: new Date().toISOString(),
        type: 'sent',
        inReplyTo: messageData.body.substring(0, 50),
        confidence: responseResult.confidence,
        passedToOperator: responseResult.passedToOperator,
      };
      logMessage(responseData);

      if (responseResult.passedToOperator) {
        console.log(`   📤 Passed to operator (confidence: ${(responseResult.confidence * 100).toFixed(1)}%)`);
      } else {
        console.log(`   ✅ Auto-response sent (confidence: ${(responseResult.confidence * 100).toFixed(1)}%)`);
      }
    } catch (error) {
      console.error(`   ❌ Failed to send: ${error.message}`);
    }
  });

  // ─── Track Operator Responses (for learning) ───
  client.on('message_create', async (msg) => {
    // Only track our own messages (operator responses)
    if (!msg.fromMe || msg.type !== 'chat') {
      return;
    }

    const toPhone = msg.to.replace('@c.us', '');

    // Check if this is a response to a pending question
    const pendingQuestions = getPendingQuestions();
    const recentPending = pendingQuestions.find(
      (q) => q.fromPhone === toPhone && q.status === 'pending'
    );

    if (recentPending) {
      // Mark as answered and save operator response
      updatePendingQuestion(recentPending.id, {
        status: 'answered',
        operatorResponse: msg.body,
        responseTimestamp: new Date().toISOString(),
      });

      console.log(`\n📝 Operator response tracked for question: "${recentPending.question.substring(0, 40)}..."`);
      console.log(`   Response: "${msg.body.substring(0, 60)}..."`);
      console.log(`   💡 Open FLUXION app to save this as FAQ`);
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
// SUPPLIER ORDER FUNCTIONS
// ═══════════════════════════════════════════════════════════════════

/**
 * Send order to supplier via WhatsApp
 * @param {Client} client - WhatsApp client instance
 * @param {string} phoneNumber - Supplier phone (e.g., +393459876543)
 * @param {Object} orderData - Order details
 */
async function sendSupplierOrder(client, phoneNumber, orderData) {
  if (!client || !client.info) {
    console.warn('WhatsApp not connected');
    return false;
  }

  try {
    // Parse items if string
    let items = orderData.items;
    if (typeof items === 'string') {
      items = JSON.parse(items);
    }

    const itemsList = items
      .map(item => `  - ${item.sku}: ${item.qty}x EUR${item.price.toFixed(2)}`)
      .join('\n');

    const config = loadConfig();
    const businessName = config.businessName || 'FLUXION';

    const message = `*NUOVO ORDINE ${businessName}*

Ordine: #${orderData.ordine_numero}
Data: ${new Date().toLocaleDateString('it-IT')}

*Articoli:*
${itemsList}

*Importo Totale:* EUR${orderData.importo_totale.toFixed(2)}
*Consegna Prevista:* ${new Date(orderData.data_consegna_prevista).toLocaleDateString('it-IT')}

${orderData.notes ? `*Note:* ${orderData.notes}` : ''}

Conferma ricezione con "OK" o "MODIFICHE"`.trim();

    const chatId = phoneNumber.replace(/\D/g, '') + '@c.us';
    await client.sendMessage(chatId, message);

    console.log(`Order #${orderData.ordine_numero} sent to ${phoneNumber}`);

    // Log the interaction
    logMessage({
      to: phoneNumber,
      body: message,
      timestamp: new Date().toISOString(),
      type: 'supplier_order',
      orderId: orderData.id,
      orderNumero: orderData.ordine_numero,
    });

    return true;

  } catch (error) {
    console.error(`Failed to send supplier order: ${error.message}`);
    return false;
  }
}

/**
 * Send delivery reminder to supplier
 * @param {Client} client - WhatsApp client instance
 * @param {string} phoneNumber - Supplier phone
 * @param {string} orderNumero - Order number
 * @param {number} giorni - Days until delivery
 */
async function sendSupplierReminder(client, phoneNumber, orderNumero, giorni) {
  if (!client || !client.info) {
    console.warn('WhatsApp not connected');
    return false;
  }

  try {
    const message = `*PROMEMORIA CONSEGNA*

Ordine #${orderNumero}
Consegna tra *${giorni} giorni*

Stato preparazione:
- "IN CORSO" - preparazione in corso
- "RITARDO" - possibile ritardo
- "PRONTO" - pronto per consegna`.trim();

    const chatId = phoneNumber.replace(/\D/g, '') + '@c.us';
    await client.sendMessage(chatId, message);

    console.log(`Reminder sent to ${phoneNumber}`);

    logMessage({
      to: phoneNumber,
      body: message,
      timestamp: new Date().toISOString(),
      type: 'supplier_reminder',
      orderNumero,
      giorni,
    });

    return true;

  } catch (error) {
    console.error(`Failed to send reminder: ${error.message}`);
    return false;
  }
}

/**
 * Send order confirmation request to supplier
 * @param {Client} client - WhatsApp client instance
 * @param {string} phoneNumber - Supplier phone
 * @param {string} orderNumero - Order number
 * @param {string} supplierName - Supplier name
 */
async function sendConfirmationRequest(client, phoneNumber, orderNumero, supplierName) {
  if (!client || !client.info) {
    console.warn('WhatsApp not connected');
    return false;
  }

  try {
    const message = `Gentile ${supplierName},

Vi chiediamo cortesemente di confermare l'ordine #${orderNumero}.

Rispondete con:
- *CONFERMATO* - ordine accettato
- *MODIFICHE* - variazioni da discutere
- *RIFIUTATO* - impossibile evadere

Grazie!`.trim();

    const chatId = phoneNumber.replace(/\D/g, '') + '@c.us';
    await client.sendMessage(chatId, message);

    console.log(`Confirmation request sent to ${phoneNumber}`);

    logMessage({
      to: phoneNumber,
      body: message,
      timestamp: new Date().toISOString(),
      type: 'supplier_confirmation_request',
      orderNumero,
    });

    return true;

  } catch (error) {
    console.error(`Failed to send confirmation request: ${error.message}`);
    return false;
  }
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

  case 'pending':
    // Show pending questions for operator review
    const pending = getPendingQuestions().filter(q => q.status === 'pending');
    console.log(`\nPending Questions (${pending.length}):\n`);
    pending.forEach((q, i) => {
      console.log(`${i + 1}. [${q.id}] ${q.fromName} (${q.fromPhone})`);
      console.log(`   "${q.question.substring(0, 60)}..."`);
      console.log(`   ${new Date(q.timestamp).toLocaleString('it-IT')}\n`);
    });
    break;

  case 'save-faq':
    // Save answered question as FAQ
    if (args.length < 2) {
      console.error('Usage: save-faq <question_id>');
      process.exit(1);
    }
    const questions = getPendingQuestions();
    const targetQ = questions.find(q => q.id === args[1]);
    if (!targetQ) {
      console.error(`Question not found: ${args[1]}`);
      process.exit(1);
    }
    if (!targetQ.operatorResponse) {
      console.error('No operator response for this question yet.');
      process.exit(1);
    }
    appendToCustomFaq(targetQ.question, targetQ.operatorResponse);
    updatePendingQuestion(targetQ.id, { status: 'saved_as_faq' });
    console.log('FAQ saved successfully!');
    break;

  default:
    showHelp();
}

// ═══════════════════════════════════════════════════════════════════
// MODULE EXPORTS (for programmatic use)
// ═══════════════════════════════════════════════════════════════════

module.exports = {
  // Core functions
  loadConfig,
  saveConfig,
  getStatus,
  updateStatus,
  logMessage,

  // FAQ functions
  loadFaqs,
  findRelevantFaqs,

  // Pending questions (learning system)
  getPendingQuestions,
  updatePendingQuestion,
  appendToCustomFaq,
  savePendingQuestion,

  // Supplier functions
  sendSupplierOrder,
  sendSupplierReminder,
  sendConfirmationRequest,

  // Auto-response
  generateAutoResponse,

  // Constants
  DATA_DIR,
  CONFIDENCE_THRESHOLD,
};
