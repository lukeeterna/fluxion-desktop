# 🔗 FLUXION Integrazioni - WhatsApp & API

> Integrazioni esterne: WhatsApp Business, notifiche, reminder.

---

## 📋 Indice

1. [WhatsApp Setup](#whatsapp-setup)
2. [Template Messaggi](#template-messaggi)
3. [Rate Limiting](#rate-limiting)
4. [Scheduler Reminder](#scheduler-reminder)
5. [Gestione Risposte](#gestione-risposte)

---

## WhatsApp Setup

### Stack

| Componente | Tecnologia |
|------------|------------|
| **Library** | whatsapp-web.js |
| **Auth** | LocalAuth (sessione locale) |
| **Queue** | node-cron (scheduler) |

### Credenziali

```bash
# .env
WHATSAPP_PHONE=+393281536308
WHATSAPP_SESSION_PATH=./data/whatsapp-session
```

### Installazione

```bash
npm install whatsapp-web.js qrcode-terminal
```

### Client Setup

```typescript
// integrations/whatsapp/client.ts
import { Client, LocalAuth, Message } from 'whatsapp-web.js';
import qrcode from 'qrcode-terminal';

const client = new Client({
    authStrategy: new LocalAuth({
        dataPath: process.env.WHATSAPP_SESSION_PATH
    }),
    puppeteer: {
        headless: true,
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage'
        ]
    }
});

// QR Code per prima autenticazione
client.on('qr', (qr) => {
    console.log('Scansiona questo QR con WhatsApp:');
    qrcode.generate(qr, { small: true });
});

// Connesso
client.on('ready', () => {
    console.log('✅ WhatsApp connesso!');
});

// Disconnesso
client.on('disconnected', (reason) => {
    console.log('❌ WhatsApp disconnesso:', reason);
});

// Messaggio in arrivo
client.on('message', async (msg: Message) => {
    await handleIncomingMessage(msg);
});

// Inizializza
client.initialize();

export { client };
```

---

## Template Messaggi

```typescript
// integrations/whatsapp/templates.ts

export const TEMPLATES = {
    /**
     * Conferma appuntamento
     */
    conferma: (data: {
        nome: string;
        servizio: string;
        data: string;
        ora: string;
        operatore?: string;
    }) => 
        `✅ *Prenotazione Confermata*\n\n` +
        `Ciao ${data.nome}!\n\n` +
        `📋 Servizio: ${data.servizio}\n` +
        `📅 Data: ${data.data}\n` +
        `🕐 Ora: ${data.ora}\n` +
        (data.operatore ? `👤 Con: ${data.operatore}\n` : '') +
        `\nPer modifiche, rispondi a questo messaggio.\n` +
        `A presto! 👋`,

    /**
     * Reminder 24 ore prima
     */
    reminder24h: (data: {
        nome: string;
        servizio: string;
        data: string;
        ora: string;
    }) =>
        `⏰ *Promemoria Appuntamento*\n\n` +
        `Ciao ${data.nome}!\n\n` +
        `Ti ricordiamo il tuo appuntamento di *domani*:\n\n` +
        `📋 ${data.servizio}\n` +
        `🕐 Ore ${data.ora}\n\n` +
        `Rispondi:\n` +
        `✅ *OK* per confermare\n` +
        `❌ *ANNULLA* per disdire`,

    /**
     * Reminder 2 ore prima
     */
    reminder2h: (data: {
        nome: string;
        ora: string;
    }) =>
        `🔔 *Ci vediamo tra poco!*\n\n` +
        `Ciao ${data.nome}, ti aspettiamo alle ${data.ora}.\n\n` +
        `A tra poco! 😊`,

    /**
     * Cancellazione
     */
    cancellazione: (data: {
        nome: string;
        data: string;
        ora: string;
    }) =>
        `❌ *Appuntamento Cancellato*\n\n` +
        `Ciao ${data.nome},\n\n` +
        `Il tuo appuntamento del ${data.data} alle ${data.ora} è stato cancellato.\n\n` +
        `Per una nuova prenotazione, rispondi a questo messaggio o chiamaci.`,

    /**
     * Spostamento
     */
    spostamento: (data: {
        nome: string;
        vecchiaData: string;
        vecchiaOra: string;
        nuovaData: string;
        nuovaOra: string;
    }) =>
        `📅 *Appuntamento Spostato*\n\n` +
        `Ciao ${data.nome}!\n\n` +
        `Il tuo appuntamento è stato spostato:\n\n` +
        `❌ Da: ${data.vecchiaData} alle ${data.vecchiaOra}\n` +
        `✅ A: ${data.nuovaData} alle ${data.nuovaOra}\n\n` +
        `A presto!`,

    /**
     * Auguri compleanno
     */
    compleanno: (data: {
        nome: string;
        sconto?: number;
    }) =>
        `🎂 *Tanti Auguri ${data.nome}!*\n\n` +
        `Ti auguriamo un fantastico compleanno! 🎉\n\n` +
        (data.sconto 
            ? `🎁 Come regalo, per te uno sconto del ${data.sconto}% sul prossimo appuntamento!\n\n`
            : '') +
        `Un abbraccio dal nostro team! 💝`,

    /**
     * Benvenuto nuovo cliente
     */
    benvenuto: (data: {
        nome: string;
        nomeAttivita: string;
    }) =>
        `👋 *Benvenuto/a ${data.nome}!*\n\n` +
        `Grazie per aver scelto ${data.nomeAttivita}!\n\n` +
        `Da oggi puoi:\n` +
        `📅 Prenotare appuntamenti\n` +
        `🔔 Ricevere promemoria\n` +
        `💬 Contattarci direttamente\n\n` +
        `Scrivi *PRENOTA* per fissare un appuntamento!`
};
```

---

## Rate Limiting

### Limiti WhatsApp (BYO Account)

| Periodo | Limite | Note |
|---------|--------|------|
| Per minuto | 3 msg | Evita ban |
| Per ora | 30 msg | Sicuro |
| Per giorno | 200 msg | Conservativo |

### Implementazione

```typescript
// integrations/whatsapp/ratelimit.ts

interface RateLimitState {
    minute: number;
    hour: number;
    day: number;
    lastMinuteReset: number;
    lastHourReset: number;
    lastDayReset: number;
}

const LIMITS = {
    perMinute: 3,
    perHour: 30,
    perDay: 200
};

class WhatsAppRateLimiter {
    private state: RateLimitState = {
        minute: 0,
        hour: 0,
        day: 0,
        lastMinuteReset: Date.now(),
        lastHourReset: Date.now(),
        lastDayReset: Date.now()
    };

    private resetIfNeeded(): void {
        const now = Date.now();
        
        // Reset minuto
        if (now - this.state.lastMinuteReset > 60000) {
            this.state.minute = 0;
            this.state.lastMinuteReset = now;
        }
        
        // Reset ora
        if (now - this.state.lastHourReset > 3600000) {
            this.state.hour = 0;
            this.state.lastHourReset = now;
        }
        
        // Reset giorno
        if (now - this.state.lastDayReset > 86400000) {
            this.state.day = 0;
            this.state.lastDayReset = now;
        }
    }

    canSend(): boolean {
        this.resetIfNeeded();
        
        return (
            this.state.minute < LIMITS.perMinute &&
            this.state.hour < LIMITS.perHour &&
            this.state.day < LIMITS.perDay
        );
    }

    recordSent(): void {
        this.state.minute++;
        this.state.hour++;
        this.state.day++;
    }

    getStatus(): { canSend: boolean; remaining: { minute: number; hour: number; day: number } } {
        this.resetIfNeeded();
        
        return {
            canSend: this.canSend(),
            remaining: {
                minute: LIMITS.perMinute - this.state.minute,
                hour: LIMITS.perHour - this.state.hour,
                day: LIMITS.perDay - this.state.day
            }
        };
    }
}

export const rateLimiter = new WhatsAppRateLimiter();
```

### Send con Rate Limit

```typescript
// integrations/whatsapp/sender.ts

import { client } from './client';
import { rateLimiter } from './ratelimit';

export async function sendWhatsAppMessage(
    phone: string,
    message: string
): Promise<{ success: boolean; error?: string }> {
    // Verifica rate limit
    if (!rateLimiter.canSend()) {
        return { 
            success: false, 
            error: 'Rate limit raggiunto. Riprova tra qualche minuto.' 
        };
    }

    // Normalizza numero italiano
    const normalizedPhone = normalizeItalianPhone(phone);
    const chatId = `${normalizedPhone}@c.us`;

    try {
        await client.sendMessage(chatId, message);
        rateLimiter.recordSent();
        
        return { success: true };
    } catch (error) {
        return { 
            success: false, 
            error: error instanceof Error ? error.message : 'Errore invio' 
        };
    }
}

function normalizeItalianPhone(phone: string): string {
    // Rimuovi tutto tranne numeri
    let cleaned = phone.replace(/\D/g, '');
    
    // Aggiungi prefisso Italia se manca
    if (cleaned.startsWith('0')) {
        cleaned = '39' + cleaned.substring(1);
    } else if (!cleaned.startsWith('39')) {
        cleaned = '39' + cleaned;
    }
    
    return cleaned;
}
```

---

## Scheduler Reminder

```typescript
// integrations/whatsapp/scheduler.ts

import cron from 'node-cron';
import { sendWhatsAppMessage } from './sender';
import { TEMPLATES } from './templates';
import { 
    getAppuntamentiDomani, 
    getAppuntamentiTraDueOre,
    markReminderSent 
} from '../../db/appuntamenti';

/**
 * Reminder 24h - Ogni giorno alle 10:00
 */
cron.schedule('0 10 * * *', async () => {
    console.log('⏰ Invio reminder 24h...');
    
    const appuntamenti = await getAppuntamentiDomani();
    
    for (const app of appuntamenti) {
        // Verifica consenso GDPR
        if (!app.cliente.consensoWhatsapp) continue;
        // Verifica reminder già inviato
        if (app.reminderInviato) continue;
        
        const message = TEMPLATES.reminder24h({
            nome: app.cliente.nome,
            servizio: app.servizio.nome,
            data: formatDate(app.dataOraInizio),
            ora: formatTime(app.dataOraInizio)
        });
        
        const result = await sendWhatsAppMessage(app.cliente.telefono, message);
        
        if (result.success) {
            await markReminderSent(app.id);
            console.log(`✅ Reminder inviato a ${app.cliente.nome}`);
        } else {
            console.error(`❌ Errore reminder ${app.cliente.nome}: ${result.error}`);
        }
        
        // Delay tra messaggi
        await sleep(2000);
    }
});

/**
 * Reminder 2h - Ogni 30 minuti
 */
cron.schedule('*/30 * * * *', async () => {
    const appuntamenti = await getAppuntamentiTraDueOre();
    
    for (const app of appuntamenti) {
        if (!app.cliente.consensoWhatsapp) continue;
        
        const message = TEMPLATES.reminder2h({
            nome: app.cliente.nome,
            ora: formatTime(app.dataOraInizio)
        });
        
        await sendWhatsAppMessage(app.cliente.telefono, message);
        await sleep(2000);
    }
});

/**
 * Auguri compleanno - Ogni giorno alle 09:00
 */
cron.schedule('0 9 * * *', async () => {
    const clientiCompleanno = await getClientiCompleannoOggi();
    
    for (const cliente of clientiCompleanno) {
        if (!cliente.consensoMarketing) continue;
        
        const message = TEMPLATES.compleanno({
            nome: cliente.nome,
            sconto: 10
        });
        
        await sendWhatsAppMessage(cliente.telefono, message);
        await sleep(2000);
    }
});

// Helpers
function sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function formatDate(isoDate: string): string {
    return new Date(isoDate).toLocaleDateString('it-IT', {
        weekday: 'long',
        day: 'numeric',
        month: 'long'
    });
}

function formatTime(isoDate: string): string {
    return new Date(isoDate).toLocaleTimeString('it-IT', {
        hour: '2-digit',
        minute: '2-digit'
    });
}
```

---

## Gestione Risposte

```typescript
// integrations/whatsapp/handlers.ts

import { Message } from 'whatsapp-web.js';
import { findClienteByPhone, logMessage } from '../../db';
import { sendWhatsAppMessage } from './sender';

export async function handleIncomingMessage(msg: Message): Promise<void> {
    const text = msg.body.toLowerCase().trim();
    const phone = msg.from.replace('@c.us', '');
    
    // Log messaggio
    const cliente = await findClienteByPhone(phone);
    await logMessage({
        clienteId: cliente?.id,
        telefono: phone,
        direzione: 'inbound',
        contenuto: msg.body
    });
    
    // Se cliente non trovato
    if (!cliente) {
        await msg.reply(
            '👋 Ciao! Non ti ho riconosciuto nel nostro sistema.\n\n' +
            'Per assistenza, contattaci al numero XXX-XXXXXXX.'
        );
        return;
    }
    
    // Intent detection
    if (text === 'ok' || text === 'confermo' || text === 'sì') {
        await handleConferma(cliente, msg);
    } 
    else if (text === 'annulla' || text === 'cancella' || text === 'disdico') {
        await handleCancellazione(cliente, msg);
    }
    else if (text === 'prenota' || text.includes('appuntamento') || text.includes('prenotare')) {
        await handleRichiestaPrenotazione(cliente, msg);
    }
    else if (text === 'orari' || text.includes('quando siete aperti')) {
        await handleOrari(cliente, msg);
    }
    else if (text === 'servizi' || text === 'listino' || text.includes('quanto costa')) {
        await handleServizi(cliente, msg);
    }
    else {
        // Risposta generica
        await msg.reply(
            `Ciao ${cliente.nome}! 👋\n\n` +
            `Come posso aiutarti?\n\n` +
            `📅 *PRENOTA* - Nuovo appuntamento\n` +
            `❌ *ANNULLA* - Cancella prenotazione\n` +
            `🕐 *ORARI* - Orari di apertura\n` +
            `💰 *SERVIZI* - Listino prezzi\n\n` +
            `Oppure chiamaci al XXX-XXXXXXX`
        );
    }
}

async function handleConferma(cliente: any, msg: Message): Promise<void> {
    // Trova appuntamento pendente conferma
    const appPendente = await getAppuntamentoPendenteConferma(cliente.id);
    
    if (appPendente) {
        await confermaAppuntamento(appPendente.id);
        await msg.reply(
            `✅ Perfetto ${cliente.nome}!\n\n` +
            `Il tuo appuntamento è confermato.\n` +
            `Ti aspettiamo!`
        );
    } else {
        await msg.reply('Non hai appuntamenti in attesa di conferma.');
    }
}

async function handleCancellazione(cliente: any, msg: Message): Promise<void> {
    const prossimoApp = await getProssimoAppuntamento(cliente.id);
    
    if (prossimoApp) {
        await cancellaAppuntamento(prossimoApp.id);
        await msg.reply(
            `❌ Appuntamento cancellato.\n\n` +
            `Se vuoi prenotare di nuovo, scrivi *PRENOTA*.`
        );
    } else {
        await msg.reply('Non hai appuntamenti da cancellare.');
    }
}

async function handleRichiestaPrenotazione(cliente: any, msg: Message): Promise<void> {
    await msg.reply(
        `📅 *Nuova Prenotazione*\n\n` +
        `Ciao ${cliente.nome}!\n\n` +
        `Per prenotare, chiamaci al XXX-XXXXXXX\n` +
        `o usa il nostro assistente vocale! 📞`
    );
}
```

---

## Database Messaggi

```sql
-- Log messaggi WhatsApp
CREATE TABLE messaggi_whatsapp (
    id TEXT PRIMARY KEY,
    cliente_id TEXT,
    telefono TEXT NOT NULL,
    direzione TEXT NOT NULL,  -- inbound/outbound
    tipo TEXT DEFAULT 'text',
    contenuto TEXT NOT NULL,
    stato TEXT DEFAULT 'sent',  -- pending/sent/delivered/read/failed
    template_id TEXT,
    errore TEXT,
    data_invio TEXT DEFAULT (datetime('now')),
    data_consegna TEXT,
    data_lettura TEXT,
    FOREIGN KEY (cliente_id) REFERENCES clienti(id)
);

CREATE INDEX idx_msg_telefono ON messaggi_whatsapp(telefono);
CREATE INDEX idx_msg_data ON messaggi_whatsapp(data_invio);
```

---

## 🔗 File Correlati

- Voice Agent: `CLAUDE-VOICE.md`
- Backend: `CLAUDE-BACKEND.md`

---

*Ultimo aggiornamento: 2025-12-28T18:00:00*
