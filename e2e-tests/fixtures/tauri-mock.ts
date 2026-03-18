/**
 * FLUXION — Tauri IPC Mock Layer
 *
 * Injects window.__TAURI_INTERNALS__ with realistic Italian PMI demo data.
 * Used by Playwright for screenshot capture without running the Rust backend.
 *
 * Usage in Playwright:
 *   await page.addInitScript({ path: './fixtures/tauri-mock.ts' });
 */

// Demo business: "Salone Bella Vita" — a mid-size Italian hair salon
const DEMO_BUSINESS = {
  nome_attivita: 'Salone Bella Vita',
  verticale: 'salone',
  indirizzo: 'Via Roma 42, 20121 Milano',
  telefono: '02 8736 4521',
  email: 'info@salonebellavita.it',
  partita_iva: '12345678901',
  codice_fiscale: 'RSSMRA80A01F205X',
};

const CLIENTI = [
  { id: 1, nome: 'Maria', cognome: 'Rossi', telefono: '333 456 7890', email: 'maria.rossi@email.it', data_registrazione: '2025-06-15', note: 'Preferisce colore biondo cenere', visite_totali: 24, ultima_visita: '2026-03-15', is_vip: true, referral_source: 'passaparola' },
  { id: 2, nome: 'Giulia', cognome: 'Bianchi', telefono: '347 123 4567', email: 'g.bianchi@gmail.com', data_registrazione: '2025-09-22', note: 'Allergia ammoniaca', visite_totali: 12, ultima_visita: '2026-03-14', is_vip: false, referral_source: 'instagram' },
  { id: 3, nome: 'Francesca', cognome: 'Romano', telefono: '320 987 6543', email: 'fra.romano@libero.it', data_registrazione: '2024-11-03', note: '', visite_totali: 38, ultima_visita: '2026-03-16', is_vip: true, referral_source: 'sito_web' },
  { id: 4, nome: 'Luca', cognome: 'Ferrari', telefono: '339 222 3344', email: 'luca.ferrari@outlook.it', data_registrazione: '2026-01-10', note: 'Barba e capelli ogni 3 settimane', visite_totali: 6, ultima_visita: '2026-03-12', is_vip: false, referral_source: 'google' },
  { id: 5, nome: 'Anna', cognome: 'Colombo', telefono: '328 111 5566', email: '', data_registrazione: '2025-03-20', note: 'Pacchetto colore + piega mensile', visite_totali: 18, ultima_visita: '2026-03-17', is_vip: true, referral_source: 'passaparola' },
  { id: 6, nome: 'Marco', cognome: 'Esposito', telefono: '345 333 7788', email: 'marco.esp@gmail.com', data_registrazione: '2025-07-08', note: '', visite_totali: 15, ultima_visita: '2026-03-10', is_vip: false, referral_source: 'whatsapp' },
  { id: 7, nome: 'Elena', cognome: 'Ricci', telefono: '366 444 9900', email: 'elena.ricci@yahoo.it', data_registrazione: '2025-12-01', note: 'Extension capelli', visite_totali: 8, ultima_visita: '2026-03-13', is_vip: false, referral_source: 'instagram' },
  { id: 8, nome: 'Simone', cognome: 'Moretti', telefono: '331 555 1122', email: '', data_registrazione: '2026-02-14', note: '', visite_totali: 3, ultima_visita: '2026-03-08', is_vip: false, referral_source: 'google' },
  { id: 9, nome: 'Chiara', cognome: 'Conti', telefono: '340 666 3344', email: 'chiara.conti@pec.it', data_registrazione: '2024-08-11', note: 'Sempre puntuale, porta spesso amiche', visite_totali: 42, ultima_visita: '2026-03-18', is_vip: true, referral_source: 'passaparola' },
  { id: 10, nome: 'Paolo', cognome: 'Gallo', telefono: '338 777 5566', email: 'pgallo@email.it', data_registrazione: '2025-05-30', note: '', visite_totali: 10, ultima_visita: '2026-03-11', is_vip: false, referral_source: 'volantino' },
];

const SERVIZI = [
  { id: 1, nome: 'Taglio Donna', durata: 45, prezzo: 35.00, categoria: 'taglio', attivo: 1 },
  { id: 2, nome: 'Taglio Uomo', durata: 30, prezzo: 22.00, categoria: 'taglio', attivo: 1 },
  { id: 3, nome: 'Piega', durata: 30, prezzo: 25.00, categoria: 'styling', attivo: 1 },
  { id: 4, nome: 'Colore Completo', durata: 90, prezzo: 65.00, categoria: 'colore', attivo: 1 },
  { id: 5, nome: 'Meches / Balayage', durata: 120, prezzo: 85.00, categoria: 'colore', attivo: 1 },
  { id: 6, nome: 'Trattamento Cheratina', durata: 60, prezzo: 55.00, categoria: 'trattamento', attivo: 1 },
  { id: 7, nome: 'Barba', durata: 20, prezzo: 15.00, categoria: 'uomo', attivo: 1 },
  { id: 8, nome: 'Taglio + Barba', durata: 45, prezzo: 32.00, categoria: 'uomo', attivo: 1 },
  { id: 9, nome: 'Acconciatura Sposa', durata: 120, prezzo: 120.00, categoria: 'evento', attivo: 1 },
  { id: 10, nome: 'Shampoo + Piega', durata: 40, prezzo: 30.00, categoria: 'styling', attivo: 1 },
];

const OPERATORI = [
  { id: 1, nome: 'Valentina', cognome: 'Marini', ruolo: 'Titolare / Senior Stylist', telefono: '333 100 2000', email: 'valentina@bellavita.it', attivo: 1, colore: '#8B5CF6' },
  { id: 2, nome: 'Roberto', cognome: 'Gatti', ruolo: 'Senior Barber', telefono: '347 200 3000', email: 'roberto@bellavita.it', attivo: 1, colore: '#3B82F6' },
  { id: 3, nome: 'Sara', cognome: 'De Luca', ruolo: 'Colorista', telefono: '320 300 4000', email: 'sara@bellavita.it', attivo: 1, colore: '#EC4899' },
  { id: 4, nome: 'Matteo', cognome: 'Greco', ruolo: 'Junior Stylist', telefono: '339 400 5000', email: 'matteo@bellavita.it', attivo: 1, colore: '#10B981' },
];

const TODAY = '2026-03-18';

const APPUNTAMENTI_OGGI = [
  { id: 1, cliente_id: 1, cliente_nome: 'Maria Rossi', servizio_id: 4, servizio_nome: 'Colore Completo', operatore_id: 3, operatore_nome: 'Sara De Luca', data: TODAY, ora: '09:00', durata: 90, stato: 'completato', prezzo: 65.00, note: '' },
  { id: 2, cliente_id: 9, cliente_nome: 'Chiara Conti', servizio_id: 5, servizio_nome: 'Meches / Balayage', operatore_id: 1, operatore_nome: 'Valentina Marini', data: TODAY, ora: '09:30', durata: 120, stato: 'completato', prezzo: 85.00, note: '' },
  { id: 3, cliente_id: 4, cliente_nome: 'Luca Ferrari', servizio_id: 8, servizio_nome: 'Taglio + Barba', operatore_id: 2, operatore_nome: 'Roberto Gatti', data: TODAY, ora: '10:00', durata: 45, stato: 'completato', prezzo: 32.00, note: '' },
  { id: 4, cliente_id: 5, cliente_nome: 'Anna Colombo', servizio_id: 1, servizio_nome: 'Taglio Donna', operatore_id: 4, operatore_nome: 'Matteo Greco', data: TODAY, ora: '11:00', durata: 45, stato: 'confermato', prezzo: 35.00, note: '' },
  { id: 5, cliente_id: 2, cliente_nome: 'Giulia Bianchi', servizio_id: 3, servizio_nome: 'Piega', operatore_id: 1, operatore_nome: 'Valentina Marini', data: TODAY, ora: '14:00', durata: 30, stato: 'confermato', prezzo: 25.00, note: '' },
  { id: 6, cliente_id: 7, cliente_nome: 'Elena Ricci', servizio_id: 6, servizio_nome: 'Trattamento Cheratina', operatore_id: 3, operatore_nome: 'Sara De Luca', data: TODAY, ora: '14:30', durata: 60, stato: 'confermato', prezzo: 55.00, note: '' },
  { id: 7, cliente_id: 6, cliente_nome: 'Marco Esposito', servizio_id: 2, servizio_nome: 'Taglio Uomo', operatore_id: 2, operatore_nome: 'Roberto Gatti', data: TODAY, ora: '15:30', durata: 30, stato: 'in_attesa', prezzo: 22.00, note: '' },
  { id: 8, cliente_id: 10, cliente_nome: 'Paolo Gallo', servizio_id: 7, servizio_nome: 'Barba', operatore_id: 2, operatore_nome: 'Roberto Gatti', data: TODAY, ora: '16:30', durata: 20, stato: 'in_attesa', prezzo: 15.00, note: '' },
];

const DASHBOARD_STATS = {
  appuntamenti_oggi: 8,
  appuntamenti_settimana: 34,
  clienti_totali: 187,
  clienti_vip: 28,
  clienti_nuovi_mese: 12,
  fatturato_mese: 8420.00,
  fatture_da_pagare: 3,
  servizio_top_nome: 'Taglio Donna',
  servizio_top_conteggio: 156,
};

const FATTURE = [
  { id: 1, numero: '2026/001', numero_fattura: '2026/001', numero_completo: 'FT-2026/001', cliente_id: 1, cliente_nome: 'Maria Rossi', cliente_denominazione: 'Maria Rossi', data_emissione: '2026-03-01T10:00:00', data: '2026-03-01T10:00:00', importo_totale: 65.00, importo: 65.00, totale_documento: 65.00, stato: 'pagata', tipo: 'fattura', tipo_documento: 'TD01', sdi_esito: 'consegnata', xml_filename: 'IT12345678901_00001.xml', xml_content: null, note: '' },
  { id: 2, numero: '2026/002', numero_fattura: '2026/002', numero_completo: 'FT-2026/002', cliente_id: 3, cliente_nome: 'Francesca Romano', cliente_denominazione: 'Francesca Romano', data_emissione: '2026-03-03T11:00:00', data: '2026-03-03T11:00:00', importo_totale: 120.00, importo: 120.00, totale_documento: 120.00, stato: 'pagata', tipo: 'fattura', tipo_documento: 'TD01', sdi_esito: 'consegnata', xml_filename: 'IT12345678901_00002.xml', xml_content: null, note: '' },
  { id: 3, numero: '2026/003', numero_fattura: '2026/003', numero_completo: 'FT-2026/003', cliente_id: 9, cliente_nome: 'Chiara Conti', cliente_denominazione: 'Chiara Conti', data_emissione: '2026-03-05T09:30:00', data: '2026-03-05T09:30:00', importo_totale: 85.00, importo: 85.00, totale_documento: 85.00, stato: 'pagata', tipo: 'fattura', tipo_documento: 'TD01', sdi_esito: 'consegnata', xml_filename: 'IT12345678901_00003.xml', xml_content: null, note: '' },
  { id: 4, numero: '2026/004', numero_fattura: '2026/004', numero_completo: 'FT-2026/004', cliente_id: 2, cliente_nome: 'Giulia Bianchi', cliente_denominazione: 'Giulia Bianchi', data_emissione: '2026-03-08T14:00:00', data: '2026-03-08T14:00:00', importo_totale: 55.00, importo: 55.00, totale_documento: 55.00, stato: 'da_pagare', tipo: 'fattura', tipo_documento: 'TD01', sdi_esito: null, xml_filename: null, xml_content: null, note: '' },
  { id: 5, numero: '2026/005', numero_fattura: '2026/005', numero_completo: 'FT-2026/005', cliente_id: 7, cliente_nome: 'Elena Ricci', cliente_denominazione: 'Elena Ricci', data_emissione: '2026-03-12T16:00:00', data: '2026-03-12T16:00:00', importo_totale: 92.00, importo: 92.00, totale_documento: 92.00, stato: 'da_pagare', tipo: 'fattura', tipo_documento: 'TD01', sdi_esito: null, xml_filename: null, xml_content: null, note: '' },
  { id: 6, numero: '2026/006', numero_fattura: '2026/006', numero_completo: 'RC-2026/006', cliente_id: 5, cliente_nome: 'Anna Colombo', cliente_denominazione: 'Anna Colombo', data_emissione: '2026-03-15T10:30:00', data: '2026-03-15T10:30:00', importo_totale: 35.00, importo: 35.00, totale_documento: 35.00, stato: 'pagata', tipo: 'ricevuta', tipo_documento: 'TD04', sdi_esito: null, xml_filename: null, xml_content: null, note: '' },
  { id: 7, numero: '2026/007', numero_fattura: '2026/007', numero_completo: 'RC-2026/007', cliente_id: 4, cliente_nome: 'Luca Ferrari', cliente_denominazione: 'Luca Ferrari', data_emissione: '2026-03-17T11:00:00', data: '2026-03-17T11:00:00', importo_totale: 32.00, importo: 32.00, totale_documento: 32.00, stato: 'da_pagare', tipo: 'ricevuta', tipo_documento: 'TD04', sdi_esito: null, xml_filename: null, xml_content: null, note: '' },
];

const INCASSI_OGGI = {
  totale: 182.00,
  contanti: 97.00,
  carta: 85.00,
  bonifico: 0,
  altro: 0,
  numero_transazioni: 3,
};

// ── Mock invoke() handler ────────────────────────────────────────────

const MOCK_HANDLERS: Record<string, (args?: any) => any> = {
  // Setup
  get_setup_status: () => ({ is_completed: true, current_step: 'done', verticale: 'salone' }),
  get_setup_config: () => ({ ...DEMO_BUSINESS, is_completed: true }),

  // Dashboard
  get_dashboard_stats: () => DASHBOARD_STATS,
  get_appuntamenti_oggi: () => APPUNTAMENTI_OGGI,
  get_top_operatore_kpi: () => ({
    id: '1', nome_completo: 'Valentina Marini', mese: '2026-03',
    appuntamenti_completati: 89, no_show: 2, clienti_unici: 54,
    fatturato_generato: 3250.00, ticket_medio: 36.52
  }),
  get_top_operatori_mese: () => [
    { id: '1', nome_completo: 'Valentina Marini', mese: '2026-03', appuntamenti_completati: 89, no_show: 2, clienti_unici: 54, fatturato_generato: 3250.00, ticket_medio: 36.52 },
    { id: '2', nome_completo: 'Roberto Gatti', mese: '2026-03', appuntamenti_completati: 67, no_show: 1, clienti_unici: 42, fatturato_generato: 2180.00, ticket_medio: 32.54 },
    { id: '3', nome_completo: 'Sara De Luca', mese: '2026-03', appuntamenti_completati: 72, no_show: 3, clienti_unici: 38, fatturato_generato: 2890.00, ticket_medio: 40.14 },
  ],

  // Clienti
  get_clienti: () => CLIENTI,
  search_clienti: (args: any) => {
    const q = (args?.query || '').toLowerCase();
    return CLIENTI.filter(c =>
      `${c.nome} ${c.cognome}`.toLowerCase().includes(q)
    );
  },
  get_cliente: (args: any) => CLIENTI.find(c => c.id === args?.id) || CLIENTI[0],
  get_clienti_count: () => ({ total: 187, vip: 28, nuovi_mese: 12 }),

  // Servizi
  get_servizi: () => SERVIZI,

  // Operatori
  get_operatori: () => OPERATORI,
  get_operatore: (args: any) => OPERATORI.find(o => o.id === args?.id) || OPERATORI[0],
  get_operatore_servizi: () => [1, 2, 3, 4, 5],
  get_operatore_assenze: () => [],
  get_operatore_commissioni: () => [],

  // Appuntamenti
  get_appuntamenti: () => APPUNTAMENTI_OGGI,
  get_appuntamenti_giorno: () => APPUNTAMENTI_OGGI,
  get_appuntamenti_settimana: () => APPUNTAMENTI_OGGI,
  get_prossimi_appuntamenti: () => APPUNTAMENTI_OGGI.filter(a => a.stato !== 'completato'),
  get_appuntamento: (args: any) => APPUNTAMENTI_OGGI.find(a => a.id === args?.id) || APPUNTAMENTI_OGGI[0],

  // Fatture
  get_fatture: () => FATTURE,
  get_fatture_count: () => ({ total: 7, pagate: 4, da_pagare: 3 }),

  // Cassa
  get_incassi_oggi: () => ({
    data: TODAY,
    totale: 182.00,
    totale_contanti: 97.00,
    totale_carte: 85.00,
    totale_satispay: 0,
    totale_altro: 0,
    numero_transazioni: 3,
    incassi: [
      { id: '1', cliente_id: 1, cliente_nome: 'Maria Rossi', servizio_nome: 'Colore Completo', importo: 65.00, metodo_pagamento: 'carta', data: `${TODAY}T09:45:00`, data_incasso: `${TODAY}T09:45:00`, categoria: 'servizio', descrizione: 'Colore Completo', note: '' },
      { id: '2', cliente_id: 9, cliente_nome: 'Chiara Conti', servizio_nome: 'Meches / Balayage', importo: 85.00, metodo_pagamento: 'carta', data: `${TODAY}T11:30:00`, data_incasso: `${TODAY}T11:30:00`, categoria: 'servizio', descrizione: 'Meches / Balayage', note: '' },
      { id: '3', cliente_id: 4, cliente_nome: 'Luca Ferrari', servizio_nome: 'Taglio + Barba', importo: 32.00, metodo_pagamento: 'contanti', data: `${TODAY}T10:45:00`, data_incasso: `${TODAY}T10:45:00`, categoria: 'servizio', descrizione: 'Taglio + Barba', note: '' },
    ],
  }),
  get_incassi_giornata: () => ({
    data: TODAY,
    totale: 182.00,
    totale_contanti: 97.00,
    totale_carte: 85.00,
    totale_satispay: 0,
    totale_altro: 0,
    numero_transazioni: 3,
    incassi: [
      { id: '1', cliente_id: 1, cliente_nome: 'Maria Rossi', servizio_nome: 'Colore Completo', importo: 65.00, metodo_pagamento: 'carta', data: `${TODAY}T09:45:00`, data_incasso: `${TODAY}T09:45:00`, categoria: 'servizio', descrizione: 'Colore Completo', note: '' },
      { id: '2', cliente_id: 9, cliente_nome: 'Chiara Conti', servizio_nome: 'Meches / Balayage', importo: 85.00, metodo_pagamento: 'carta', data: `${TODAY}T11:30:00`, data_incasso: `${TODAY}T11:30:00`, categoria: 'servizio', descrizione: 'Meches / Balayage', note: '' },
      { id: '3', cliente_id: 4, cliente_nome: 'Luca Ferrari', servizio_nome: 'Taglio + Barba', importo: 32.00, metodo_pagamento: 'contanti', data: `${TODAY}T10:45:00`, data_incasso: `${TODAY}T10:45:00`, categoria: 'servizio', descrizione: 'Taglio + Barba', note: '' },
    ],
  }),
  get_chiusure_cassa: () => [],
  get_metodi_pagamento: () => ['contanti', 'carta', 'bonifico', 'satispay'],
  get_report_incassi_periodo: () => ({ totale: 8420.00, media_giornaliera: 468.00, giorni: 18 }),

  // Orari
  get_orari_lavoro: () => [
    { id: 1, giorno: 1, apertura: '09:00', chiusura: '19:00', pausa_inizio: '13:00', pausa_fine: '14:00' },
    { id: 2, giorno: 2, apertura: '09:00', chiusura: '19:00', pausa_inizio: '13:00', pausa_fine: '14:00' },
    { id: 3, giorno: 3, apertura: '09:00', chiusura: '19:00', pausa_inizio: '13:00', pausa_fine: '14:00' },
    { id: 4, giorno: 4, apertura: '09:00', chiusura: '19:00', pausa_inizio: '13:00', pausa_fine: '14:00' },
    { id: 5, giorno: 5, apertura: '09:00', chiusura: '19:00', pausa_inizio: '13:00', pausa_fine: '14:00' },
    { id: 6, giorno: 6, apertura: '09:00', chiusura: '14:00', pausa_inizio: null, pausa_fine: null },
  ],
  get_giorni_festivi: () => [
    { id: 1, data: '2026-04-06', descrizione: 'Pasquetta' },
    { id: 2, data: '2026-04-25', descrizione: 'Liberazione' },
    { id: 3, data: '2026-05-01', descrizione: 'Festa dei Lavoratori' },
    { id: 4, data: '2026-08-15', descrizione: 'Ferragosto' },
  ],

  // Voice
  get_voice_pipeline_status: () => ({ running: true, port: 3002, pid: 12345, health: { status: 'ok' } }),
  get_voice_agent_config: () => ({ nome_attivita: DEMO_BUSINESS.nome_attivita, whatsapp_number: '39 333 456 7890', ehiweb_number: null }),
  voice_greet: () => ({ success: true, response: 'Buongiorno! Sono Sara, l\'assistente del Salone Bella Vita. Come posso aiutarti?', audio_base64: null }),
  voice_process_text: () => ({ success: true, response: 'Certo! Per quando vorresti prenotare?', transcription: null, intent: 'booking', audio_base64: null }),
  voice_say: () => ({ success: true, audio_base64: null }),
  voice_reset_conversation: () => true,
  start_voice_pipeline: () => ({ running: true, port: 3002, pid: 12345, health: { status: 'ok' } }),
  stop_voice_pipeline: () => true,

  // Impostazioni
  get_impostazioni: () => ({
    nome_attivita: DEMO_BUSINESS.nome_attivita,
    indirizzo: DEMO_BUSINESS.indirizzo,
    telefono: DEMO_BUSINESS.telefono,
    email: DEMO_BUSINESS.email,
    partita_iva: DEMO_BUSINESS.partita_iva,
    verticale: 'salone',
  }),

  // License
  check_license: () => ({ valid: true, tier: 'pro', days_remaining: 999, features: ['sara', 'whatsapp', 'fatture', 'loyalty'] }),
  get_license_status: () => ({ active: true, tier: 'pro', expires: null }),
  get_license_status_ed25519: () => ({ valid: true, tier: 'pro', features: ['sara', 'whatsapp', 'fatture', 'loyalty'] }),
  check_feature_access: () => true,
  check_feature_access_ed25519: () => true,
  check_vertical_access_ed25519: () => true,
  get_machine_fingerprint: () => 'DEMO-MACHINE-001',
  get_machine_fingerprint_ed25519: () => 'DEMO-MACHINE-001',
  get_tier_info_ed25519: () => ({ tier: 'pro', name: 'Pro', features: ['sara', 'whatsapp', 'fatture'] }),

  // Analytics
  get_analytics_mensili: () => ({
    anno: 2026,
    mese: 3,
    mese_label: 'Marzo 2026',
    revenue_mese: 8420.00,
    revenue_mese_prec: 7650.00,
    revenue_delta_pct: 10.1,
    appuntamenti_totali: 156,
    appuntamenti_completati: 142,
    appuntamenti_cancellati: 6,
    appuntamenti_no_show: 4,
    appuntamenti_confermati: 4,
    clienti_nuovi: 12,
    clienti_ritorni: 98,
    wa_confermati: 89,
    wa_cancellati: 6,
    wa_confirm_rate: 93.7,
    top_servizi: [
      { nome: 'Taglio Donna', conteggio: 42, revenue: 1470 },
      { nome: 'Colore Completo', conteggio: 28, revenue: 1820 },
      { nome: 'Meches / Balayage', conteggio: 18, revenue: 1530 },
      { nome: 'Piega', conteggio: 32, revenue: 800 },
      { nome: 'Taglio Uomo', conteggio: 24, revenue: 528 },
    ],
    top_operatori: [
      { id: '1', nome: 'Valentina Marini', nome_completo: 'Valentina Marini', appuntamenti: 89, appuntamenti_completati: 89, revenue: 3250, clienti_unici: 54 },
      { id: '2', nome: 'Roberto Gatti', nome_completo: 'Roberto Gatti', appuntamenti: 67, appuntamenti_completati: 67, revenue: 2180, clienti_unici: 42 },
      { id: '3', nome: 'Sara De Luca', nome_completo: 'Sara De Luca', appuntamenti: 72, appuntamenti_completati: 72, revenue: 2890, clienti_unici: 38 },
    ],
  }),
  get_analytics_summary: () => ({
    fatturato_mese: 8420.00,
    fatturato_mese_precedente: 7650.00,
    variazione_percentuale: 10.1,
    appuntamenti_mese: 156,
    no_show_mese: 4,
    tasso_no_show: 2.6,
    clienti_nuovi: 12,
    servizio_piu_richiesto: 'Taglio Donna',
    giorno_piu_affollato: 'Sabato',
    ora_punta: '10:00-12:00',
  }),

  // Support / Diagnostics
  get_diagnostics_info: () => ({
    app_version: '1.0.0',
    os: 'macOS 14.3',
    memoria_usata: '245 MB',
    db_size: '12.4 MB',
    voice_pipeline: 'attivo',
    ultimo_backup: '2026-03-17 23:00',
  }),
  list_backups: () => [
    { path: 'backup-2026-03-17.db', size: '12.4 MB', date: '2026-03-17 23:00' },
    { path: 'backup-2026-03-16.db', size: '12.2 MB', date: '2026-03-16 23:00' },
  ],

  // FAQ / RAG
  list_faq_categories: () => ['Orari', 'Servizi', 'Prenotazioni', 'Pagamenti'],

  // Loyalty
  get_clienti_compleanno_settimana: () => [
    { cliente_id: 3, nome: 'Francesca', cognome: 'Romano', data_nascita: '1988-03-20', telefono: '320 987 6543' },
  ],
  get_loyalty_stats: () => ({ clienti_vip: 28, punti_attivi: 12450, premi_riscattati: 34 }),
  get_loyalty_milestones: () => [],
  get_loyalty_info: () => ({ visite: 0, punti: 0, is_vip: false, milestones: [] }),
  get_top_referrers: () => [],

  // Pacchetti
  get_pacchetti: () => [],
  get_cliente_pacchetti: () => [],

  // Impostazioni fatturazione
  get_impostazioni_fatturazione: () => ({
    ragione_sociale: 'Salone Bella Vita di Valentina Marini',
    partita_iva: '12345678901',
    codice_fiscale: 'MRNVNT85M41F205X',
    indirizzo: 'Via Roma 42',
    cap: '20121',
    citta: 'Milano',
    provincia: 'MI',
    regime_fiscale: 'RF01',
    formato_numero: 'YYYY/NNN',
    prossimo_numero: 8,
    aliquota_iva_default: 22,
    codice_natura_iva: null,
    codice_pagamento: 'MP01',
    banca_iban: 'IT60X0542811101000000123456',
    note_piede: '',
    sdi_provider: null,
  }),
  get_codici_natura_iva: () => [
    { codice: 'N1', descrizione: 'Escluse ex art.15' },
    { codice: 'N2.2', descrizione: 'Non soggette - altri casi' },
    { codice: 'N3.1', descrizione: 'Non imponibili - esportazioni' },
  ],
  get_codici_pagamento: () => [
    { codice: 'MP01', descrizione: 'Contanti' },
    { codice: 'MP05', descrizione: 'Bonifico' },
    { codice: 'MP08', descrizione: 'Carta di pagamento' },
  ],

  // SMTP
  get_smtp_settings: () => ({ configured: false }),

  // WhatsApp
  get_whatsapp_config: () => ({ enabled: true, auto_confirm: true, reminder_24h: true, reminder_1h: true }),
  get_whatsapp_templates: () => [],
  get_pending_questions: () => [],
  get_received_messages: () => [],
  get_whatsapp_status: () => ({ connected: true, numero: '39 333 456 7890' }),

  // Voice config
  get_voice_config: () => ({ enabled: true, tts_engine: 'edge-tts', voice: 'it-IT-IsabellaNeural' }),

  // Suppliers
  list_suppliers: () => [
    { id: 1, nome: "L'Oréal Professionnel", contatto: 'Marco Verdi', telefono: '02 1234 5678', email: 'ordini@loreal.it', note: 'Fornitore principale colori' },
    { id: 2, nome: 'Wella Italia', contatto: 'Laura Neri', telefono: '02 9876 5432', email: 'italia@wella.com', note: 'Trattamenti e shampoo' },
    { id: 3, nome: 'GHD Italy', contatto: '', telefono: '800 123 456', email: 'sales@ghd.it', note: 'Piastre e phon professionali' },
  ],

  // Schede cliente
  get_scheda_odontoiatrica: () => null,
  get_scheda_parrucchiere: () => null,
  get_scheda_estetica: () => null,
  get_scheda_medica: () => null,
  get_scheda_fitness: () => null,
};

// ── Inject into window ──────────────────────────────────────────────

(window as any).__TAURI_INTERNALS__ = {
  invoke: async (cmd: string, args?: any) => {
    const handler = MOCK_HANDLERS[cmd];
    if (handler) {
      // Simulate realistic network delay
      await new Promise(r => setTimeout(r, 50 + Math.random() * 100));
      return handler(args);
    }
    // Unknown command — return empty/null (don't throw, let UI handle gracefully)
    console.warn(`[TauriMock] Unhandled command: ${cmd}`, args);
    return null;
  },
  convertFileSrc: (path: string) => path,
  transformCallback: (callback: any) => {
    const id = Math.random().toString(36).slice(2);
    (window as any)[`_${id}`] = callback;
    return id;
  },
};

// Also mock @tauri-apps/api/core invoke for ESM imports
(window as any).__TAURI__ = (window as any).__TAURI_INTERNALS__;
