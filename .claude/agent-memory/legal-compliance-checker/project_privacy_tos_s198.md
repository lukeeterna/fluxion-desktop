---
name: Privacy Policy e ToS S198
description: Documenti legali prodotti in S198 — privacy.html aggiornata + termini.html nuovo ToS completo
type: project
---

Privacy Policy (`landing/privacy.html`) e Terms of Service (`landing/termini.html`) prodotti in sessione S198 (2026-05-11).

**Perché:** PRE-LAUNCH-AUDIT S197 segnalava Compliance PARTIAL con privacy+ToS come P0 GDPR blocker.

**Cosa copre la privacy.html aggiornata:**
- Distinzione cliente FLUXION vs utenti finali del cliente (ruolo Titolare vs Responsabile art. 28)
- 6 sub-processor elencati con URL privacy 2026: Stripe, Resend, Cloudflare, Groq, Microsoft Edge-TTS, Sentry
- Sara STT: flusso audio → Groq US spiegato con responsabilità al cliente FLUXION per informativa chiamanti
- Sentry: solo error monitoring, no PII, no replay (nuovo rispetto alla versione precedente)
- Groq come sub-processor per STT (mancava nella versione precedente)
- Cookie: nessuno (CF edge analytics aggregati anonimizzati, no consenso richiesto)
- Trasferimenti extra-UE: EU-US DPF + SCC per tutti i provider US
- Tabella conservazione dati con 7 categorie distinte

**Cosa copre il termini.html (nuovo):**
- Licenza lifetime non esclusiva, 1 attività, non trasferibile senza procedura
- Piano Base vs Pro differenze chiare
- Garanzia 30gg commerciale + recesso legale 14gg D.Lgs. 206/2005 art. 59 comma 1 lett. o)
- Requisiti di sistema con disclaimer compatibilità
- Servizi AI inclusi: cambio provider consentito senza rimborso se funzionalità equivalente
- Disclaimer Sara: Licenziatario responsabile contenuti, informativa chiamanti obbligatoria
- Revoca licenza: SOLO frode, chargeback, violazione grave — mai per mancato rinnovo
- Foro: Potenza (PZ) — diritto italiano
- Link ODR Commissione Europea: ec.europa.eu/consumers/odr

**Gap residui da gestire separatamente:**
- DPA con Groq: Groq non offre DPA standard self-service per free-tier. Quando FLUXION supera la soglia di utilizzo che richiede account commerciale Groq, richiedere DPA formale. Per ora il DPA di Groq Cloud copre il transito STT tramite privacy policy standard.
- Cookie banner: non necessario perché nessun tracker. Se si aggiunge analytics in futuro, aggiornare sec. 10 e implementare banner.
- Lead magnet/newsletter: sezione 4 conservazione copre il caso ma non c'è ancora flusso newsletter attivo — verificare prima di attivarlo.

**How to apply:** Quando si modifica stack (nuovo sub-processor, nuova funzionalità cloud, analytics), aggiornare entrambi i file e incrementare data "Ultimo aggiornamento".
