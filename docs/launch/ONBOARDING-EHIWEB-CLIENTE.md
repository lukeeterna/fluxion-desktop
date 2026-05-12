# Onboarding Ehiweb VoIP per Cliente FLUXION

> **Versione**: 1.0 (S202, 2026-05-12)
> **Owner**: Founder + Claude CTO
> **Stato**: ✅ Procedura ufficiale (sostituisce qualsiasi guida precedente)

## Contesto architetturale

Sara è una receptionist AI **inbound-only via VoIP** (SIP trunk Ehiweb), **NON** funziona via microfono del PC cliente.

| Componente | Dove gira | Come riceve audio |
|------------|-----------|-------------------|
| Pipeline Sara | iMac founder (test) / PC cliente (prod) | inbound SIP via `sip.ehiweb.it:5060` |
| STT/TTS/LLM | locale (Piper, Whisper) + Groq | flusso audio decodificato G.711 |
| Frontend FLUXION | desktop Tauri | comunica con Sara via HTTP bridge :3001 |

**Conseguenza**: ogni cliente FLUXION che attiva Sara **deve** avere un numero VoIP attivo. Senza VoIP, Sara non riceve chiamate — il resto del gestionale funziona normalmente.

## Allineamento commerciale

| Piano FLUXION | Sara | Provider VoIP consigliato |
|---------------|------|---------------------------|
| **Base €497** | 1 mese trial | **VivaVox Free** Ehiweb (30 gg, 100 min, primo numero gratis, no carta) — match perfetto |
| **Pro €897** | inclusa lifetime | **VivaVox Flat** Ehiweb (€7,95/mese, €4,95 promo 6 mesi) post-trial |

Il trial VivaVox Free di Ehiweb dura 30 giorni → coincide con i 30 giorni di Sara inclusi in Base. **Zero costo cliente** durante il trial. **Zero anticipo FLUXION** (vincolo #5 zero-cost).

## Procedura cliente — 4 passi (~15 min totali)

### Step 1 — Registrazione VivaVox Free
- URL: <https://www.ehiweb.it/voip/>
- Form: dati personali + scelta prefisso geografico
- Pagamento: **non richiesto** per Free
- Output: account Ehiweb attivo

### Step 2 — Ricezione credenziali SIP
- Email da Ehiweb con:
  - `sip_username` (di solito = numero DID)
  - `sip_password`
  - numero DID assegnato (es. `0972 536918`)
- Timeline attivazione: **non documentata pubblicamente** (research gap, da misurare con primi 3 clienti reali)
- Mitigazione: spedire credenziali Ehiweb in parallelo al download FLUXION, non in serie

### Step 3 — Inserimento in FLUXION
- Setup Wizard step 6 oppure post-install: Impostazioni → VoIP / Sara
- Campi richiesti: `sip_username`, `sip_password`, `did_number`
- Campi precompilati (NON editabili dal cliente):
  - `sip_server = sip.ehiweb.it`
  - `sip_port = 5060`
  - `sip_transport = UDP`
  - `sip_realm = ehiweb.it`
  - `codec = G.711 PCMA/PCMU`
- Validazione: SIP REGISTER test real-time, feedback OK/KO immediato

### Step 4 — Upgrade pre-scadenza
- T-7 giorni dalla scadenza trial: banner in-app FLUXION
- Cliente passa a **VivaVox Flat** dal portale Ehiweb
- Credenziali SIP **non cambiano** → Sara continua senza interruzioni
- Migrazione automatizzata: **impossibile** (no provisioning API Ehiweb)

## Friction map

| Punto | Friction | Mitigazione |
|-------|----------|-------------|
| Registrazione Ehiweb fuori da FLUXION | Cliente esce dall'app | CTA prominente con deep-link, guida visuale 4 step su `fluxion-landing.pages.dev/voip-guida` |
| Attesa email credenziali | Tempo non garantito | Email FAQ inclusa, contatto supporto Ehiweb prominente |
| Copia-incolla credenziali | Errori tipografici | Validazione real-time SIP REGISTER nel campo |
| Conversione Free → Flat | Manuale, no API | Reminder T-7gg + email transazionale FLUXION |

## Anti-pattern (mai fare)

- ❌ Anticipare il costo VivaVox per il cliente (vincolo #5)
- ❌ Embedded SIP credentials in FLUXION (lock-in legale, no portabilità provider)
- ❌ "Sara funziona senza VoIP" — è FALSO, è inbound-only
- ❌ Forzare portabilità del numero esistente nel trial — richiede 5-10 gg lavorativi, brucia il trial

## Provider alternativi (tech debt v1.1)

In caso Ehiweb non sia disponibile o cliente preferisca altro:

| Provider | Pro | Costo base |
|----------|-----|------------|
| Messagenet | Italiano, SIP standard | ~€5/mese |
| VoipVoice | Italiano, supporto B2B | da €6/mese |
| Skebby | Italiano, focus PMI | personalizzato |

Tutti supportano codec G.711 → cliente può sostituire le 3 credenziali nei campi FLUXION senza ricompilazione.

## File modificati (S202)

- `landing/voip-guida/index.html` — header + 4-step + FAQ corrette (`È obbligatorio?` riformulata, pricing veritiero, mobile non supportato)
- `src/components/setup/SetupWizard.tsx` — step 6 con CTA prominente VivaVox Free + deep-link guida
- `docs/launch/ONBOARDING-EHIWEB-CLIENTE.md` — questo documento

## Open question (da chiudere con dati reali)

1. **Tempo attivazione VivaVox Free reale**: misurare con i primi 3 clienti — se >24h, riorganizzare onboarding email
2. **Portability success rate**: da misurare quando primo cliente richiede portabilità
3. **Conversione Free → Flat**: target ≥80% — sotto, rivedere copy banner T-7gg
4. **DPA contractor**: Ehiweb è DPA implicito? Verificare contratto VivaVox Free vs GDPR Art. 28 (data processor)

## Critiche strutturali residue

1. **Dipendenza single-provider** (Ehiweb): un loro outage = Sara giù per tutti i clienti. Tech debt v1.2: documentare migrazione SIP credentials a Messagenet in 5 min.
2. **No automazione provisioning**: cliente deve copia-incollare manualmente. Tech debt v1.3: valutare partnership Ehiweb per API white-label (post-50 clienti).
3. **Timeline attivazione opaca**: rischio percezione "non funziona subito" su clienti Base impazienti. Mitigazione: copy "Sara si attiva nelle prossime 24h" su email post-acquisto.
4. **Conversione Free → Flat ha churn risk**: cliente che dimentica può perdere Sara senza accorgersene. Mitigazione: 3 reminder (T-7, T-3, T-1) + grace period 48h on FLUXION side (Sara mostra "linea da rinnovare" invece di disabilitarsi silenziosamente).
