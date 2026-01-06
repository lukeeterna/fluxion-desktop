#!/usr/bin/env node
/**
 * FLUXION - WhatsApp Service (Local, NO API costs)
 * Uses whatsapp-web.js for local WhatsApp Web automation
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

const DATA_DIR = path.join(__dirname, '..', '.whatsapp-session');
const STATUS_FILE = path.join(DATA_DIR, 'status.json');

// Ensure data directory exists
if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

function updateStatus(status, info = {}) {
  const data = {
    status,
    timestamp: new Date().toISOString(),
    ...info,
  };
  fs.writeFileSync(STATUS_FILE, JSON.stringify(data, null, 2));
  console.log(`Status: ${status}`);
}

function getStatus() {
  if (!fs.existsSync(STATUS_FILE)) {
    return { status: 'not_initialized' };
  }
  return JSON.parse(fs.readFileSync(STATUS_FILE, 'utf8'));
}

async function startService() {
  console.log('='.repeat(50));
  console.log('FLUXION - WhatsApp Service');
  console.log('='.repeat(50));
  console.log('');

  updateStatus('initializing');

  const client = new Client({
    authStrategy: new LocalAuth({
      dataPath: DATA_DIR,
    }),
    puppeteer: {
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
    },
  });

  client.on('qr', (qr) => {
    console.log('\n');
    console.log('='.repeat(50));
    console.log('SCAN THIS QR CODE WITH WHATSAPP:');
    console.log('='.repeat(50));
    qrcode.generate(qr, { small: true });
    console.log('\nOpen WhatsApp > Settings > Linked Devices > Link a Device');
    updateStatus('waiting_qr', { qr });
  });

  client.on('loading_screen', (percent, message) => {
    console.log(`Loading: ${percent}% - ${message}`);
    updateStatus('loading', { percent, message });
  });

  client.on('authenticated', () => {
    console.log('Authenticated!');
    updateStatus('authenticated');
  });

  client.on('auth_failure', (msg) => {
    console.error('Authentication failed:', msg);
    updateStatus('auth_failed', { error: msg });
  });

  client.on('ready', () => {
    console.log('\n');
    console.log('='.repeat(50));
    console.log('WhatsApp is READY!');
    console.log('='.repeat(50));
    updateStatus('ready', {
      phone: client.info?.wid?.user || 'unknown',
      name: client.info?.pushname || 'unknown',
    });
  });

  client.on('disconnected', (reason) => {
    console.log('Disconnected:', reason);
    updateStatus('disconnected', { reason });
  });

  client.on('message', async (msg) => {
    // Log incoming messages for RAG processing
    const contact = await msg.getContact();
    const messageData = {
      from: msg.from,
      name: contact.pushname || contact.name || 'Unknown',
      body: msg.body,
      timestamp: new Date().toISOString(),
      type: msg.type,
    };

    // Append to messages log
    const messagesLogPath = path.join(DATA_DIR, 'messages.jsonl');
    fs.appendFileSync(messagesLogPath, JSON.stringify(messageData) + '\n');

    console.log(`Message from ${messageData.name}: ${msg.body.substring(0, 50)}...`);

    // TODO: Integrate with RAG for auto-responses
  });

  try {
    await client.initialize();
  } catch (err) {
    console.error('Failed to initialize:', err.message);
    updateStatus('error', { error: err.message });
    process.exit(1);
  }

  // Keep process alive
  process.on('SIGINT', async () => {
    console.log('\nShutting down...');
    await client.destroy();
    updateStatus('stopped');
    process.exit(0);
  });
}

async function sendMessage(phone, message) {
  console.log(`Sending message to ${phone}...`);

  const status = getStatus();
  if (status.status !== 'ready') {
    console.error('WhatsApp not connected. Run: node scripts/whatsapp-service.js start');
    process.exit(1);
  }

  // Format phone number (add @c.us suffix for WhatsApp)
  const chatId = phone.includes('@') ? phone : `${phone.replace(/\D/g, '')}@c.us`;

  const client = new Client({
    authStrategy: new LocalAuth({
      dataPath: DATA_DIR,
    }),
    puppeteer: {
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
    },
  });

  client.on('ready', async () => {
    try {
      await client.sendMessage(chatId, message);
      console.log('Message sent successfully!');
      updateStatus('ready');
      await client.destroy();
      process.exit(0);
    } catch (err) {
      console.error('Failed to send:', err.message);
      await client.destroy();
      process.exit(1);
    }
  });

  await client.initialize();
}

// CLI handling
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
  case 'send':
    if (args.length < 3) {
      console.error('Usage: node whatsapp-service.js send <phone> <message>');
      process.exit(1);
    }
    sendMessage(args[1], args.slice(2).join(' '));
    break;
  default:
    console.log(`
FLUXION WhatsApp Service

Commands:
  start           Start WhatsApp service (shows QR for login)
  status          Check connection status
  send <phone> <message>   Send a message

Examples:
  node scripts/whatsapp-service.js start
  node scripts/whatsapp-service.js status
  node scripts/whatsapp-service.js send 393281234567 "Ciao!"
`);
}
