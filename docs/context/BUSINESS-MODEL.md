# Fluxion Business Model

## Licenze Lifetime (3 Livelli)

| Livello | Nome | Target |
|---------|------|--------|
| 1 | **Starter** | Freelancer, micro-attivita |
| 2 | **Professional** | PMI 1-5 dipendenti |
| 3 | **Enterprise** | PMI 5-15 dipendenti |

### Funzionalita a Pacchetti

| Modulo | Starter | Professional | Enterprise |
|--------|---------|--------------|------------|
| CRM Clienti | Y | Y | Y |
| Calendario/Booking | Y | Y | Y |
| Fatturazione Base | Y | Y | Y |
| WhatsApp (wa.me) | Y | Y | Y |
| Fatturazione SDI | N | Y | Y |
| Fluxion AI (Sara) | N | N | Y |
| Email SMTP | N | N | Y |
| Fornitori + Ordini | N | N | Y |
| VoIP Integration | N | N | Y |
| Multi-sede | N | N | Y |

### Costi Operativi

| Servizio | Costo/mese | Note |
|----------|------------|------|
| Groq API | 0 | Free tier, STT + LLM |
| Keygen.sh | 0-50 | Gestione licenze |

Email SMTP: cliente usa proprio Gmail (App Password). Costo 0 per vendor.

### Assistenza

| Tipo | Incluso | Costo |
|------|---------|-------|
| Documentazione + FAQ | Sempre | 0 |
| Aggiornamenti software | Lifetime | 0 |
| Assistenza remota | No | A pagamento |
| Personalizzazioni | No | Preventivo |

## Variabili Setup Wizard

| Categoria | Variabile | Obbligatoria |
|-----------|-----------|--------------|
| AI/LLM | `GROQ_API_KEY` | Si |
| SMTP | `SMTP_HOST`, `SMTP_PORT`, `EMAIL_FROM`, `EMAIL_PASSWORD` | Per Email |
| Azienda | `BUSINESS_NAME` | Si |
| Azienda | `AZIENDA_PARTITA_IVA`, dati fiscali | Per Fatture |
| VoIP | `VOIP_SIP_*` | Per VoIP |
| WhatsApp | `WHATSAPP_PHONE` | Per WA |

Implementazione:
1. Setup Wizard (Step 1-3): Raccoglie variabili essenziali
2. Impostazioni App: Modifica successiva
3. Database: Salvate in tabella `impostazioni`
4. Fallback: .env solo dev
