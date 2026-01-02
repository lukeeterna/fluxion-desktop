-- ═══════════════════════════════════════════════════════════════════
-- FLUXION - Migration 002: WhatsApp Templates
-- Template library per messaggistica WhatsApp zero-cost (wa.me + copy/paste)
-- ═══════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS whatsapp_templates (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    nome TEXT NOT NULL,
    categoria TEXT NOT NULL,  -- 'conferma', 'reminder', 'marketing', 'loyalty', 'waitlist', 'emergenza'
    descrizione TEXT,
    template_text TEXT NOT NULL,
    variabili TEXT,  -- JSON array: ["nome", "data", "servizio", "operatore"]
    predefinito INTEGER DEFAULT 0,  -- 0=custom, 1=system template
    attivo INTEGER DEFAULT 1,
    uso_count INTEGER DEFAULT 0,
    ultimo_uso TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX idx_whatsapp_templates_categoria ON whatsapp_templates(categoria);
CREATE INDEX idx_whatsapp_templates_predefinito ON whatsapp_templates(predefinito);

-- ═══════════════════════════════════════════════════════════════════
-- SEED: 30+ Template Predefiniti (da FLUXION-LOYALTY-V3.md)
-- ═══════════════════════════════════════════════════════════════════

-- CATEGORIA: CONFERMA (Prenotazioni)
INSERT INTO whatsapp_templates (nome, categoria, descrizione, template_text, variabili, predefinito) VALUES
('Conferma Appuntamento', 'conferma', 'Conferma prenotazione standard',
'✅ *Prenotazione Confermata*

Ciao {{nome}}! 😊

📋 Servizio: {{servizio}}
📅 Data: {{data}}
🕐 Ora: {{ora}}
{{operatore_line}}
Ci vediamo! 👋',
'["nome", "servizio", "data", "ora", "operatore"]', 1),

('Conferma con Prezzo', 'conferma', 'Conferma con dettaglio prezzo',
'✅ *Prenotazione Confermata*

Ciao {{nome}}!

📋 {{servizio}}
📅 {{data}} alle {{ora}}
💰 Prezzo: €{{prezzo}}
{{operatore_line}}
A presto! 😊',
'["nome", "servizio", "data", "ora", "prezzo", "operatore"]', 1);

-- CATEGORIA: REMINDER
INSERT INTO whatsapp_templates (nome, categoria, descrizione, template_text, variabili, predefinito) VALUES
('Reminder 24h', 'reminder', 'Promemoria 24 ore prima',
'⏰ *Promemoria Appuntamento*

Ciao {{nome}}!

Domani alle {{ora}} hai appuntamento per:
📋 {{servizio}}
{{operatore_line}}
Rispondi OK per confermare ✅',
'["nome", "ora", "servizio", "operatore"]', 1),

('Reminder 2h', 'reminder', 'Promemoria 2 ore prima',
'⏰ *Promemoria*

Ciao {{nome}}!

Tra 2 ore ({{ora}}) ti aspettiamo per {{servizio}} 😊

A tra poco! 👋',
'["nome", "ora", "servizio"]', 1),

('Richiesta Conferma', 'reminder', 'Chiedi conferma presenza',
'Ciao {{nome}}! 😊

Appuntamento {{data}} alle {{ora}}.
Confermi che ci sei? Rispondi SÌ o NO 👍',
'["nome", "data", "ora"]', 1);

-- CATEGORIA: MARKETING
INSERT INTO whatsapp_templates (nome, categoria, descrizione, template_text, variabili, predefinito) VALUES
('Auguri Compleanno', 'marketing', 'Buon compleanno con sconto',
'🎉 *Buon Compleanno {{nome}}!* 🎂

Per festeggiare ti regaliamo uno sconto del 15% 🎁

Valido fino a {{scadenza}}.
Prenota quando vuoi! 😊',
'["nome", "scadenza"]', 1),

('Promozione Stagionale', 'marketing', 'Promo soft non aggressiva',
'Ciao {{nome}}! 🌸

Questo mese abbiamo una promozione su {{servizio}}:
{{benefit}}

Se ti interessa, scrivimi pure! 😊',
'["nome", "servizio", "benefit"]', 1),

('Cliente Dormiente', 'marketing', 'Riattivazione cliente inattivo 30+ giorni',
'Ciao {{nome}}! 😊

È tanto che non ti vediamo... ci manchi! 💚

Se vuoi prenotare, scrivimi pure.
A presto!',
'["nome"]', 1),

('Porta un Amico', 'marketing', 'Referral soft',
'Ciao {{nome}}! 💚

Se hai amiche/i che potrebbero gradire i nostri servizi, passa pure il nostro contatto 😊

Grazie per la fiducia!',
'["nome"]', 1);

-- CATEGORIA: LOYALTY
INSERT INTO whatsapp_templates (nome, categoria, descrizione, template_text, variabili, predefinito) VALUES
('Milestone Raggiunta', 'loyalty', 'Traguardo tessera timbri',
'🌟 *Complimenti {{nome}}!* 🎉

Hai raggiunto {{loyalty_visits}} visite!

Il prossimo servizio è scontato del 15% 💚
Grazie per la fedeltà! 😊',
'["nome", "loyalty_visits"]', 1),

('Quasi Traguardo', 'loyalty', 'Mancano pochi timbri',
'Ciao {{nome}}! ⭐

Mancano solo {{mancanti}} visite per il premio! 🎁
Sei quasi arrivata/o 💪

A presto! 😊',
'["nome", "mancanti"]', 1);

-- CATEGORIA: WAITLIST
INSERT INTO whatsapp_templates (nome, categoria, descrizione, template_text, variabili, predefinito) VALUES
('Aggiungi a Lista Attesa', 'waitlist', 'Slot occupato, proponi waitlist',
'Ciao {{nome}}! 😊

Lo slot {{data}} alle {{ora}} con {{operatore}} è occupato.

Posso metterti in lista d''attesa? Se si libera ti avviso subito via WhatsApp.

Ti va bene? Rispondi SÌ 👍',
'["nome", "data", "ora", "operatore"]', 1),

('Slot Libero', 'waitlist', 'Notifica slot disponibile',
'🎉 *Ottima notizia {{nome}}!*

Si è liberato lo slot:
📅 {{data}}
🕐 {{ora}}
👤 Con {{operatore}}

Vuoi prenotare? Rispondi entro 2h! ⏰',
'["nome", "data", "ora", "operatore"]', 1),

('Waitlist Scaduta', 'waitlist', 'Slot scaduto, offri alternative',
'Ciao {{nome}},

Il tempo per lo slot {{data}} {{ora}} è scaduto 😔

Vuoi che ti proponga un altro orario? Fammi sapere! 😊',
'["nome", "data", "ora"]', 1);

-- CATEGORIA: EMERGENZA
INSERT INTO whatsapp_templates (nome, categoria, descrizione, template_text, variabili, predefinito) VALUES
('Cancellazione Operatore', 'emergenza', 'Operatore assente improvviso',
'⚠️ Ciao {{nome}},

Purtroppo {{operatore}} non potrà esserci {{data}} alle {{ora}}.

Posso spostarti con un''altra collega o in un altro giorno?
Scusa il disagio! 🙏',
'["nome", "operatore", "data", "ora"]', 1),

('Cambio Orario', 'emergenza', 'Richiesta spostamento urgente',
'Ciao {{nome}},

Per un imprevisto dovremmo spostare il tuo appuntamento di {{data}} alle {{ora}}.

Ti andrebbe bene {{nuova_data}} alle {{nuova_ora}}?
Fammi sapere! 🙏',
'["nome", "data", "ora", "nuova_data", "nuova_ora"]', 1),

('Chiusura Straordinaria', 'emergenza', 'Chiusura imprevista',
'⚠️ Avviso Importante

{{data}} saremo chiusi per {{motivo}}.

Chi aveva appuntamento verrà contattato per riprogrammare.

Grazie per la comprensione! 🙏',
'["data", "motivo"]', 1),

('Ritardo', 'emergenza', 'Avviso ritardo operatore',
'Ciao {{nome}},

Siamo in leggero ritardo di circa {{minuti}} minuti.

Ti va bene aspettare o preferisci spostare?
Scusa! 🙏',
'["nome", "minuti"]', 1);

-- CATEGORIA: FOLLOW-UP
INSERT INTO whatsapp_templates (nome, categoria, descrizione, template_text, variabili, predefinito) VALUES
('Feedback Post Servizio', 'followup', 'Richiesta feedback dopo appuntamento',
'Ciao {{nome}}! 🌟

Grazie per essere passata/o oggi!

Come ti sei trovata/o? Se hai bisogno di qualcosa, scrivimi pure 😊

A presto! 💚',
'["nome"]', 1),

('Upsell Servizio', 'followup', 'Proposta servizio complementare',
'Ciao {{nome}}! 😊

Visto che hai fatto {{servizio}}, potresti gradire anche {{servizio_upsell}}.

Se ti interessa, fammi sapere!',
'["nome", "servizio", "servizio_upsell"]', 1),

('Thank You Referral', 'followup', 'Ringraziamento per passaparola',
'Grazie {{nome}}! 💚

{{amico}} mi ha detto che sei tu ad avergli/le consigliato i nostri servizi 😊

Ti siamo davvero grati! 🌟',
'["nome", "amico"]', 1);

-- CATEGORIA: PACCHETTI (Commerce)
INSERT INTO whatsapp_templates (nome, categoria, descrizione, template_text, variabili, predefinito) VALUES
('Proposta Pacchetto', 'pacchetti', 'Offri pacchetto servizi',
'Ciao {{nome}}! 🌟

Ti propongo il pacchetto "{{nome_pacchetto}}":
• {{servizi_inclusi}} servizi {{descrizione}}
• Prezzo: €{{prezzo}} (risparmi {{risparmio}}!)
• Validità: {{validita}} giorni

Se ti interessa, confermami pure! 😊',
'["nome", "nome_pacchetto", "servizi_inclusi", "descrizione", "prezzo", "risparmio", "validita"]', 1),

('Conferma Acquisto Pacchetto', 'pacchetti', 'Thank you post-acquisto',
'Grazie {{nome}}! 🎉

Pacchetto "{{nome_pacchetto}}" acquistato con successo!

Hai {{servizi_inclusi}} servizi disponibili, validi fino a {{scadenza}}.

A presto! 💚',
'["nome", "nome_pacchetto", "servizi_inclusi", "scadenza"]', 1),

('Pacchetto in Scadenza', 'pacchetti', 'Avviso scadenza imminente',
'Ciao {{nome}}! ⏰

Il tuo pacchetto "{{nome_pacchetto}}" scade il {{scadenza}}.

Hai ancora {{servizi_rimasti}} servizi da usare!
Prenota subito per non perderli 😊',
'["nome", "nome_pacchetto", "scadenza", "servizi_rimasti"]', 1);

-- CATEGORIA: CANCELLAZIONE/SPOSTAMENTO
INSERT INTO whatsapp_templates (nome, categoria, descrizione, template_text, variabili, predefinito) VALUES
('Conferma Cancellazione', 'cancellazione', 'Conferma annullamento appuntamento',
'Ok {{nome}}, cancellato l''appuntamento di {{data}} alle {{ora}}.

Se vuoi riprenotare, scrivimi pure! 😊',
'["nome", "data", "ora"]', 1),

('Conferma Spostamento', 'cancellazione', 'Conferma cambio data/ora',
'✅ Fatto {{nome}}!

Appuntamento spostato:
📅 Da: {{vecchia_data}} {{vecchia_ora}}
📅 A: {{nuova_data}} {{nuova_ora}}

Ci vediamo! 👋',
'["nome", "vecchia_data", "vecchia_ora", "nuova_data", "nuova_ora"]', 1),

('Cancellazione Tardiva', 'cancellazione', 'Cancellazione last minute (policy)',
'Ciao {{nome}},

Abbiamo ricevuto la tua richiesta di cancellazione per {{data}} alle {{ora}}.

Poiché mancano meno di 24h, questa volta facciamo un''eccezione, ma per il futuro ti chiediamo di avvisarci con almeno 24h di anticipo 🙏

Grazie!',
'["nome", "data", "ora"]', 1);

-- ═══════════════════════════════════════════════════════════════════
-- Total: 30 template predefiniti
-- Categorie: conferma(2), reminder(3), marketing(4), loyalty(2),
--            waitlist(3), emergenza(4), followup(3), pacchetti(3),
--            cancellazione(3), + custom user templates
-- ═══════════════════════════════════════════════════════════════════
