# SDI Free — Alternativa a Fattura24 (CoVe 2026 FASE 1 Research)
> Generato: 2026-03-03 | Agente: general-purpose | Research SDI alternative gratuite

---

## Stato Attuale

L'integrazione Fattura24 è già funzionante: `useInviaSdiFattura` hook chiama `invia_fattura_sdi` Tauri command che fa POST a `https://api.fattura24.com/api/v0/SaveInvoice`. Il problema non è tecnico — è di **business model**: ogni cliente FLUXION deve pagare un piano Business Fattura24 separato (~€96-192/anno) per accesso API. Attrito di adozione significativo.

---

## 7 Opzioni Analizzate

### OPZIONE A — Accreditamento Diretto SDI (Web Service SDICoop)
- Costo transazione: €0
- Richiede firma digitale legale rappresentante (~€50/anno)
- Protocollo SOAP/WSDL, non REST — alta complessità Rust
- Burocrazia AdE: 4-8 settimane accreditamento
- Se Fluxion si accredita per conto dei clienti → diventa intermediario ufficiale con responsabilità legali
- **Verdict: NON PRATICABILE per v1.0**

### OPZIONE B — Invio via PEC Diretta
- AdE accetta XML come allegato PEC a `sdi01@pec.fatturapa.it`
- PEC costa €5-9/anno (molti PMI la hanno già)
- Automazione risposte SDI richiede client IMAP in Rust (crate `imap` + `zip`)
- Non real-time (email possono ritardare ore)
- **Verdict: Opzione futura v1.1, non per v1.0**

### OPZIONE C — Invoicetronic API
- https://invoicetronic.com/en/
- REST API moderna, SDK open source, sandbox gratuita
- Pricing: tiers transazioni prepagati (no scadenza, no abbonamento mensile)
- Firma digitale: €0.020; Webhook nativi gratuiti
- Azienda giovane ma DX solida
- **Verdict: ALTERNATIVA VALIDA, terza scelta**

### OPZIONE D — OpenAPI.com SDI
- https://openapi.com/products/italian-electronic-invoicing
- Prezzi pubblici e trasparenti
- Subscription: **€0.025/fattura** | Pay-as-you-go: €0.070/fattura
- Conservazione: €0.035/fattura | Firma digitale: €0.02/firma
- Nessun abbonamento mensile
- PMI 50 fatture/anno: **€1.25/anno** con subscription
- **Verdict: Costo più basso per volumi bassi. Ideale forfettari <30 fatt/anno**

### OPZIONE E — fattura-elettronica-api.it
- Sistema a crediti (1 credito = 1 fattura B2B, 3 crediti = 1 PA)
- Pricing opaco, non visibile senza registrazione
- **Verdict: Da esplorare solo come ultima opzione**

### OPZIONE F — Aruba Fatturazione Elettronica API ⭐ RACCOMANDATO
- https://fatturazioneelettronica.aruba.it/
- Piano base: **€29.90/anno** con invii ILLIMITATI
- Trial 3 mesi: €1 + IVA
- Conservazione decennale **inclusa** (obbligatoria per legge)
- REST API documentata
- Brand Aruba: il più riconosciuto in Italia per PMI
- Break-even vs OpenAPI subscription: 29.90 / 0.025 = 1196 fatture/anno
- Per PMI 20-200 fatture/anno: Aruba nettamente più conveniente
- **Verdict: RACCOMANDAZIONE PRIMARIA**

### OPZIONE G — Librerie Open Source
- `python-a38` (Truelite) e `italia/fatturapa-python` coprono generazione XML
- Non gestiscono invio SDI (richiede canale accreditato)
- FLUXION ha già generazione XML in Rust — irrilevante
- **Verdict: Non applicabile**

---

## Tabella Comparativa

| Opzione | Costo annuo (50 fatt/anno) | Costo/fattura | Integrazione | Affidabilità |
|---------|---------------------------|---------------|--------------|--------------|
| Fattura24 (attuale) | ~€96-192 | variabile | — (già fatto) | Alta |
| Accred. Diretto AdE | €0 | €0 | MOLTO ALTA (SOAP) | Massima |
| PEC diretta | €0-9 | €0 | Media (SMTP+IMAP) | Media |
| Invoicetronic | N/D (tiers) | N/D | Bassa (REST) | Media-Alta |
| OpenAPI.com | ~€1.25 | €0.025 | Bassa (REST) | Alta |
| **Aruba FE** ⭐ | **€29.90** | **€0 (illimitato)** | **Bassa (REST)** | **Altissima** |
| fattura-elettronica-api.it | N/D | ~€0.03-0.05 | Bassa (REST) | Media |

---

## Raccomandazione Finale — Architettura Multi-Provider

**Implementare supporto multi-provider** in FLUXION:

```
Priority 1: Aruba Fatturazione Elettronica
  → €29.90/anno, invii illimitati, conservazione inclusa, brand riconosciuto PMI

Priority 2: OpenAPI.com SDI
  → €0.025/fattura, pay-per-use, ideale forfettari <30 fatt/anno

Priority 3: Fattura24
  → Mantenuto per retrocompatibilità clienti esistenti
```

**Valore business**: Da €96-192/anno (Fattura24 Business) a €29.90/anno (Aruba) — rimozione principale ostacolo pricing nella fase di vendita FLUXION.

---

## Effort Implementazione FLUXION

| Componente | File | Effort |
|-----------|------|--------|
| Rust: trait `SdiProvider` + impl Aruba | `src-tauri/src/commands/fatture.rs` | 3h |
| Migration: `provider` field in `impostazioni_fatturazione` | `029_sdi_multi_provider.sql` | 30min |
| UI: selezione provider in Impostazioni | `src/pages/Impostazioni.tsx` | 2h |
| UI: aggiornamento hook per provider attivo | `src/hooks/use-fatture.ts` | 1h |
| **Totale** | | **~6-7h** |

**NON implementare**: accreditamento diretto SDI o PEC diretta per v1.0.

---

## Fonti

- [AdE - Modalità trasmissione FE](https://www.agenziaentrate.gov.it/portale/schede/comunicazioni/fatture-e-corrispettivi/faq-fe/risposte-alle-domande-piu-frequenti-categoria/modalita-di-trasmissione-delle-fatture-elettroniche)
- [Accreditamento diretto SDI](https://www.agenziaentrate.gov.it/portale/l-accreditamento-diretto-contributi)
- [Aruba FE API doc](https://fatturazioneelettronica.aruba.it/apidoc/docs.html)
- [Aruba FE listino prezzi](https://www.aruba.it/listino-fatturazione-elettronica.aspx)
- [OpenAPI.com SDI](https://openapi.com/products/italian-electronic-invoicing)
- [OpenAPI.com FAQ con pricing](https://console.openapi.com/apis/sdi/faq)
- [Invoicetronic](https://invoicetronic.com/en/) | [Pricing](https://invoicetronic.com/en/pricing/)
- [developers.italia.it FatturaPA](https://developers.italia.it/it/fatturapa/)

---

*Fonte: general-purpose agent — Web search + analisi integrazione Fattura24 esistente FLUXION*
