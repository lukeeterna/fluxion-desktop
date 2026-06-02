# FLUXION - Decisioni Architetturali

> **ADR (Architecture Decision Records) del progetto.**
> Decisioni prese e motivazioni.

---

## ADR-001: Fiscalità Italiana - FLUXION = Gestionale Puro

**Data**: 2026-01-07
**Status**: ✅ Approvato
**Decisione**: Opzione A - FLUXION gestisce solo logica gestionale, RT separato

### Contesto
PMI target (saloni, palestre, cliniche) emettono SCONTRINI, non fatture.
- Saloni, palestre, cliniche → Registratore Telematico (RT) per scontrini
- Fatture solo per clienti B2B che le richiedono (raro)

### Opzioni Valutate

| Opzione | Descrizione | Costo | Complessità |
|---------|-------------|-------|-------------|
| A | FLUXION = solo gestionale, RT separato | €0 | ✅ Bassa |
| B | FLUXION + RT Cloud (Effatta, etc.) | €20/mese | 🟡 Media |
| C | FLUXION = RT virtuale (certificazione AdE) | €0 ma 6+ mesi | 🔴 Altissima |

### Motivazioni Opzione A
- 50+ modelli RT con driver diversi = incubo compatibilità
- Installazione fisica NON gestibile da remoto
- RT Cloud costa €20-30/mese (contro policy FREE)
- PMI hanno GIÀ RT funzionante → non serve sostituirlo

### Flusso Quotidiano PMI
```
CLIENTE PAGA → FLUXION registra incasso → RT emette scontrino → AdE automatico
```

### Conseguenze
- FLUXION: clienti, appuntamenti, incassi, statistiche
- RT esistente (o da acquistare): scontrini → AdE
- Fatture B2B (rare): genera XML + FatturAE Bridge gratuito

---

## ADR-002: FatturAE Bridge per Fatture B2B

**Data**: 2026-01-07
**Status**: ✅ Approvato

### Decisione
Usare FatturAE (software gratuito Agenzia Entrate) come bridge per fatture B2B occasionali.

### Implementazione
1. Integrato nell'installer FLUXION
2. Rileva OS (Windows/macOS/Linux)
3. Scarica FatturAE se non presente
4. FLUXION genera XML → apre FatturAE → utente clicca Invia
5. 100% GRATUITO

### Risorse
- **API AdE**: https://api.corrispettivi.agenziaentrate.gov.it/v1
- **Spec OpenAPI**: github.com/teamdigitale/api-openapi-samples
- **Schema XML**: CorrispettiviType_1.0.xsd

---

## ADR-003: Remote Assistance via Tailscale + SSH

**Data**: 2026-01-07
**Status**: ✅ Approvato (MVP)

### Decisione
- **MVP**: Tailscale + SSH (Zero-cost, P2P, crittografato)
- **Enterprise**: RustDesk self-hosted (GUI, cross-platform)

### Perché Tailscale + SSH
- Costo: $0 (fino 100 device)
- Setup: 1 comando per macchina
- Sicurezza: WireGuard encryption, no port forwarding
- Latenza: P2P diretto, <50ms tipico
- NAT traversal: Automatico

### Comparativa

| Soluzione | Costo | Setup | GUI |
|-----------|-------|-------|-----|
| Tailscale+SSH | Free | 1 min | No |
| RustDesk | Free | 5 min | Si |
| TeamViewer | $$$ | 2 min | Si |
| AnyDesk | $$ | 2 min | Si |

---

## ADR-004: E2E Testing su Linux (no macOS)

**Data**: 2026-01-10
**Status**: ✅ Approvato

### Decisione
E2E tests eseguiti su Linux (ubuntu-22.04) in GitHub Actions, non su macOS.

### Motivazione
tauri-driver NON supporta macOS (no WKWebView WebDriver).

### Implementazione
- Ubuntu 22.04 in GitHub Actions
- xvfb per headless testing
- WebKitGTK driver
- Zero costi, ~20-25 min per run
- Per macOS locale: usare MCP Server per test manuali

---

## ADR-005: FLUXION IA come Opzione Licenza

**Data**: 2026-01-08
**Status**: ✅ Approvato

### Decisione
L'API Key Groq per FLUXION IA è un'opzione della licenza, configurabile SOLO nel Setup Wizard.

### Implementazione
- Campo API Key: SOLO nel Setup Wizard (Step 3), NON nelle Impostazioni
- Variabile DB: `fluxion_ia_key` nella tabella `impostazioni`
- Fallback: Se non presente, legge da .env `GROQ_API_KEY`

### Motivazione
Il cliente sceglie questa opzione all'acquisto della licenza.

---

## ADR-006: Sistema Fornitori + Email

**Data**: 2026-01-07
**Status**: 📋 Pianificato

### Decisione
Gestione ordini a fornitori con comunicazione automatizzata via Email e WhatsApp.

### Schema Database
- `email_providers`: Provider SMTP preconfigurati (Gmail, Libero, Outlook, Aruba)
- `email_config`: Configurazione email utente (crittografata)
- `fornitori`: Anagrafica fornitori
- `ordini_template`: Template ordini email/WhatsApp

### Rust Crate
- `lettre` per invio SMTP
- Password crittografata con `ring` o `aes-gcm`

---

## ADR-007: Hardware Binding Licenze — DEFERRED (trigger-based)

**Data**: 2026-06-02
**Status**: ⏸️ Deferred (build solo al trigger)

### Decisione
Il binding hardware (machine fingerprint + conteggio macchine per licenza) NON viene
implementato ora. La licenza Ed25519 resta email-bound, con revoca via refund-gate
(`purchase:{email}.refunded`) + heartbeat `/license/validate` (R-01-ter).

### Trigger per costruirlo
Costruire SOLO quando si osserva il **primo abuso multi-macchina reale su un cliente
pagante** (stessa licenza attiva su N macchine oltre soglia legittima). Fino ad allora,
fingerprint è già calcolato lato Rust (`generate_fingerprint`) e usato per HARDWARE_MISMATCH
sulle licenze `active`, ma NON viene fatto enforcement di conteggio macchine lato server.

### Motivazione
- Zero evidenza di abuso → enforcement preventivo = attrito su clienti legittimi
  (cambio Mac, reinstall, doppia postazione legittima PMI 1-15 dip.).
- Refund-gate + revoca remota coprono il vettore frode principale (refund-then-keep).
- Implementarlo richiede: tabella `license_machines` server-side, endpoint count, policy
  soglia, UX deautorizza-macchina → lavoro non giustificato senza dato reale.

---

> **Nota**: Per nuove decisioni, aggiungere qui con formato ADR-XXX.
