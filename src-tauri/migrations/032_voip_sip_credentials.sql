-- Migration 032: VoIP SIP credentials in voice_agent_config (F15)
-- Aggiunge colonne per configurazione SIP EHIWEB/Telnyx
ALTER TABLE voice_agent_config ADD COLUMN sip_username TEXT;
ALTER TABLE voice_agent_config ADD COLUMN sip_password TEXT;
ALTER TABLE voice_agent_config ADD COLUMN sip_server TEXT DEFAULT 'sip.ehiweb.it';
ALTER TABLE voice_agent_config ADD COLUMN sip_port INTEGER DEFAULT 5060;
ALTER TABLE voice_agent_config ADD COLUMN voip_attivo INTEGER DEFAULT 0;
