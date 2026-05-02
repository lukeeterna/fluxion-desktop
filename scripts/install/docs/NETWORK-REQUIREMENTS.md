# FLUXION — Requisiti di Rete (Network Requirements)

> **Per l'IT manager / amministratore di rete.**
> Questo documento elenca tutti gli endpoint che FLUXION deve poter
> contattare attraverso il firewall / proxy aziendale per funzionare
> correttamente in PMI con rete protetta.

## Test rapido (3 secondi)

Da terminale del PC dove si vuole installare FLUXION:

```bash
# macOS / Linux:
curl -fsS https://raw.githubusercontent.com/lukeeterna/fluxion-desktop/master/tools/network-test.sh | bash
```

Oppure scaricare lo script e eseguirlo manualmente:

```bash
git clone https://github.com/lukeeterna/fluxion-desktop.git
cd fluxion-desktop
bash tools/network-test.sh
```

**Esito atteso**: `9/9 OK` ed exit code `0`.
Se il risultato è diverso, vedere la tabella di whitelist sotto.

## Tabella endpoint richiesti (whitelist firewall)

Tutti gli endpoint usano **HTTPS porta 443** (TCP). Nessun servizio richiede
porte custom o connessioni inbound.

### CRITICAL — bloccare = app non funziona / non si aggiorna

| FQDN da consentire                                  | Porta | Scopo                                           |
| --------------------------------------------------- | ----- | ----------------------------------------------- |
| `fluxion-proxy.gianlucanewtech.workers.dev`         | 443   | Validazione licenza Ed25519 + LLM NLU per Sara |
| `api.github.com`                                    | 443   | Auto-update FLUXION (verifica nuove versioni)  |
| `github.com`                                        | 443   | Redirect verso asset di download               |
| `objects.githubusercontent.com`                     | 443   | Download MSI/DMG aggiornamenti                  |
| `*.githubusercontent.com`                           | 443   | Asset GitHub (CDN release)                      |

### IMPORTANT — bloccare = feature ridotte (app comunque funziona)

| FQDN da consentire                                  | Porta | Scopo                                                       |
| --------------------------------------------------- | ----- | ----------------------------------------------------------- |
| `o4511313987170304.ingest.de.sentry.io`             | 443   | Crash reporter privacy-safe (no PII, regione UE/GDPR)       |
| `*.ingest.de.sentry.io`                             | 443   | Sentry crash reporting (region DE / GDPR safe)              |
| `api.stripe.com`                                    | 443   | Solo durante acquisto licenza dal sito (post-acquisto: NO) |
| `js.stripe.com`                                     | 443   | Solo durante acquisto licenza dal sito                      |
| `checkout.stripe.com`                               | 443   | Solo durante acquisto licenza dal sito                      |
| `fluxion-landing.pages.dev`                         | 443   | Sito vetrina + pagina "come installare"                    |

### OPTIONAL — bloccare = Sara funziona ma con voce locale (qualità ridotta)

| FQDN da consentire                                  | Porta | Scopo                                                              |
| --------------------------------------------------- | ----- | ------------------------------------------------------------------ |
| `speech.platform.bing.com`                          | 443   | Sara voce italiana **Isabella Neural** Edge-TTS (qualità 9/10)    |
| `*.tts.speech.microsoft.com`                        | 443   | Microsoft Cognitive Services (TTS Sara online)                    |
| `api.groq.com`                                      | 443   | Fallback diretto LLM (di norma transitano via FLUXION proxy)      |

> Se tutti gli OPTIONAL sono bloccati, Sara userà **Piper** (TTS locale,
> qualità 7/10, completamente offline). L'esperienza utente resta accettabile.

## Endpoint NON richiesti (per chiarezza)

FLUXION **NON** contatta i seguenti servizi (mai):

- Google Analytics, Facebook Pixel, qualunque tracker pubblicitario
- Telemetria comportamento utente (cosa si clicca, dove si va)
- Server di terze parti per database o file utente
- AWS, Azure, GCP, server di hosting esterni
- WhatsApp / Twilio (l'integrazione WhatsApp avviene **lato cliente**, su
  numero del PMI, non passa da FLUXION cloud)

I dati cliente (anagrafiche, appuntamenti, fatture) restano **sempre**
nel database SQLite locale al PC dove FLUXION è installato.

## Connessioni locali (informative)

FLUXION usa due porte locali (loopback `127.0.0.1`, mai esposte in rete):

| Porta | Servizio                          | Bind         |
| ----- | --------------------------------- | ------------ |
| 3001  | HTTP Bridge Tauri (frontend↔Rust) | `127.0.0.1`  |
| 3002  | Voice Pipeline Sara (Python)      | `127.0.0.1`  |

Queste porte non sono visibili dall'esterno della macchina e non richiedono
modifiche al firewall.

## Whitelist consigliata per proxy aziendale

Se l'azienda usa **squid** / **FortiGate** / **pfSense** / **Sophos UTM**,
copia-incolla questo elenco minimo (CRITICAL + IMPORTANT):

```text
fluxion-proxy.gianlucanewtech.workers.dev
api.github.com
github.com
objects.githubusercontent.com
*.githubusercontent.com
o4511313987170304.ingest.de.sentry.io
*.ingest.de.sentry.io
api.stripe.com
js.stripe.com
checkout.stripe.com
fluxion-landing.pages.dev
```

Aggiungere anche gli OPTIONAL se si vuole la voce Sara di qualità massima:

```text
speech.platform.bing.com
*.tts.speech.microsoft.com
api.groq.com
```

## Cosa fare in caso di FAIL

### Endpoint CRITICAL bloccato

1. Eseguire `bash tools/network-test.sh` per identificare il/i FQDN bloccato/i.
2. Inoltrare la lista all'IT manager con il file
   [`scripts/install/docs/NETWORK-REQUIREMENTS.md`](./NETWORK-REQUIREMENTS.md)
   (questo documento) come riferimento.
3. Richiedere whitelist dei soli FQDN segnalati FAIL.
4. Re-eseguire il test → atteso `9/9 OK`.

### Endpoint IMPORTANT bloccato

L'app si installa e gestisce dati / WhatsApp / Sara correttamente.
La feature relativa (Sentry / acquisto / landing) sarà degradata o
non disponibile — vedere descrizione tabella sopra.

### Endpoint OPTIONAL bloccato

Sara userà voce Piper locale (italiana, qualità 7/10, offline).
Nessun impatto su funzionalità core.

## Privacy & Data Residency

- Tutti gli endpoint Sentry sono nella regione **UE/Germania** (`de.sentry.io`)
  → conformi GDPR, no Schrems II.
- Cloudflare Worker (`fluxion-proxy.gianlucanewtech.workers.dev`) gira sulla
  rete edge globale di Cloudflare; non memorizza dati cliente — è un puro
  router stateless verso Groq/Cerebras (anch'essi UE/USA).
- Il database SQLite **non lascia mai il PC del cliente**. Nessun dato
  anagrafico viene trasmesso ai nostri server.
- Diagnostic report (pulsante "Invia segnalazione" nelle Impostazioni) è
  **opt-in** — l'utente vede sempre l'anteprima JSON prima dell'invio e i
  dati sono privacy-safe (machine_hash SHA256, nessun PII cliente).

## Supporto IT manager

Per dubbi sulla whitelist o problemi di connettività:

**Email**: `fluxion.gestionale@gmail.com`

Allegare l'output di `bash tools/network-test.sh --json` per accelerare
la diagnosi.

## Storia revisioni

- **α.4** (2026-05-02): documento iniziale con tabella whitelist + test self-service.
