# SDI FatturaPA Research — CoVe 2026
> Generato: 2026-03-02 | Task C1
> Fonte: Agenzia delle Entrate + normativa vigente 2026

---

## 1. Schema XML FatturaPA 1.3.2 (vigente 2026)

### Namespace & Versione
```xml
<?xml version="1.0" encoding="UTF-8"?>
<p:FatturaElettronica versione="FPR12"
  xmlns:p="http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2"
  xmlns:ds="http://www.w3.org/2000/09/xmldsig#"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2 http://www.fatturapa.gov.it/export/fatturazione/sdi/fatturapa/v1.2/Schema_del_file_xml_FatturaPA_versione_1.2.xsd">
```
- **FPR12** = FatturaPA ordinaria (privati B2B e B2C)
- **FPA12** = FatturaPA pubblica PA (enti pubblici)

### Struttura Minima FPR12 (B2B 1 riga servizio)
```xml
<p:FatturaElettronica versione="FPR12" xmlns:p="http://ivaservizi.agenziaentrate.gov.it/docs/xsd/fatture/v1.2">

  <!-- ─── HEADER ─── -->
  <FatturaElettronicaHeader>

    <DatiTrasmissione>
      <IdTrasmittente>
        <IdPaese>IT</IdPaese>
        <IdCodice>01234567890</IdCodice>   <!-- PIVA cedente o intermediario -->
      </IdTrasmittente>
      <ProgressivoInvio>00001</ProgressivoInvio>  <!-- univoco per trasmissione -->
      <FormatoTrasmissione>FPR12</FormatoTrasmissione>
      <CodiceDestinatario>ABCDEFG</CodiceDestinatario>  <!-- 7 char B2B, 0000000 B2C -->
      <!-- oppure per PEC: <PECDestinatario>email@pec.it</PECDestinatario> -->
    </DatiTrasmissione>

    <CedentePrestatore>
      <DatiAnagrafici>
        <IdFiscaleIVA>
          <IdPaese>IT</IdPaese>
          <IdCodice>01234567890</IdCodice>  <!-- P.IVA azienda -->
        </IdFiscaleIVA>
        <CodiceFiscale>RSSMRA80A01H501Z</CodiceFiscale>  <!-- CF titolare -->
        <Anagrafica>
          <Denominazione>Salone Parrucchieri SRL</Denominazione>
          <!-- OPPURE: <Nome>Mario</Nome><Cognome>Rossi</Cognome> per persone fisiche -->
        </Anagrafica>
        <RegimeFiscale>RF01</RegimeFiscale>  <!-- RF01=ordinario, RF19=forfettario -->
      </DatiAnagrafici>
      <Sede>
        <Indirizzo>Via Roma 1</Indirizzo>
        <CAP>20100</CAP>
        <Comune>Milano</Comune>
        <Provincia>MI</Provincia>
        <Nazione>IT</Nazione>
      </Sede>
    </CedentePrestatore>

    <CessionarioCommittente>
      <DatiAnagrafici>
        <IdFiscaleIVA>
          <IdPaese>IT</IdPaese>
          <IdCodice>09876543210</IdCodice>
        </IdFiscaleIVA>
        <Anagrafica>
          <Denominazione>Cliente SRL</Denominazione>
        </Anagrafica>
      </DatiAnagrafici>
      <Sede>
        <Indirizzo>Via Milano 5</Indirizzo>
        <CAP>00100</CAP>
        <Comune>Roma</Comune>
        <Provincia>RM</Provincia>
        <Nazione>IT</Nazione>
      </Sede>
    </CessionarioCommittente>

  </FatturaElettronicaHeader>

  <!-- ─── BODY ─── -->
  <FatturaElettronicaBody>

    <DatiGenerali>
      <DatiGeneraliDocumento>
        <TipoDocumento>TD01</TipoDocumento>  <!-- TD01=fattura, TD04=nota credito -->
        <Divisa>EUR</Divisa>
        <Data>2026-03-02</Data>
        <Numero>2026/001</Numero>
        <ImportoTotaleDocumento>61.00</ImportoTotaleDocumento>
        <!-- Bollo virtuale €2 se esente IVA e importo >77.47:
        <DatiBollo>
          <BolloVirtuale>SI</BolloVirtuale>
          <ImportoBollo>2.00</ImportoBollo>
        </DatiBollo>
        -->
      </DatiGeneraliDocumento>
    </DatiGenerali>

    <DatiBeniServizi>
      <DettaglioLinee>
        <NumeroLinea>1</NumeroLinea>
        <Descrizione>Taglio capelli uomo</Descrizione>
        <Quantita>1.00</Quantita>
        <PrezzoUnitario>50.00</PrezzoUnitario>
        <PrezzoTotale>50.00</PrezzoTotale>
        <AliquotaIVA>22.00</AliquotaIVA>
        <!-- Forfettari/esenti: <AliquotaIVA>0.00</AliquotaIVA><Natura>N2.2</Natura> -->
      </DettaglioLinee>

      <DatiRiepilogo>
        <AliquotaIVA>22.00</AliquotaIVA>
        <ImponibileImporto>50.00</ImponibileImporto>
        <Imposta>11.00</Imposta>
        <EsigibilitaIVA>I</EsigibilitaIVA>  <!-- I=immediata, D=differita, S=split payment -->
      </DatiRiepilogo>
    </DatiBeniServizi>

    <DatiPagamento>
      <CondizioniPagamento>TP02</CondizioniPagamento>  <!-- TP01=rate, TP02=completo, TP03=anticipo -->
      <DettaglioPagamento>
        <ModalitaPagamento>MP05</ModalitaPagamento>  <!-- MP05=bonifico, MP08=carta, MP01=contanti -->
        <DataScadenzaPagamento>2026-03-31</DataScadenzaPagamento>
        <ImportoPagamento>61.00</ImportoPagamento>
      </DettaglioPagamento>
    </DatiPagamento>

  </FatturaElettronicaBody>

</p:FatturaElettronica>
```

### Tipi Documento (TipoDocumento) più usati per PMI
| Codice | Descrizione |
|--------|-------------|
| TD01 | Fattura |
| TD04 | Nota di credito |
| TD06 | Parcella (professionisti) |
| TD17 | Integrazione/autofattura (reverse charge servizi esteri) |
| TD24 | Fattura differita (art.21 c.4 DPR 633/72) |

---

## 2. Regime Forfettario RF19

### Obbligo dal 2024
- **Tutti i forfettari** hanno obbligo FE dal **1/1/2024** (D.L. 36/2022)
- Soglia €25k: eliminata — obbligo per tutti a prescindere dal volume
- **Nessuna esenzione rimasta** nel 2026

### Campi specifici RF19
```xml
<RegimeFiscale>RF19</RegimeFiscale>  <!-- nella sezione CedentePrestatore -->
```
```xml
<!-- Linea servizio: IVA 0% con Natura N2.2 -->
<AliquotaIVA>0.00</AliquotaIVA>
<Natura>N2.2</Natura>  <!-- N2.2 = non soggetto art.1 c.58-84 L.190/2014 -->
```
```xml
<!-- DatiRiepilogo per regime forfettario -->
<DatiRiepilogo>
  <AliquotaIVA>0.00</AliquotaIVA>
  <Natura>N2.2</Natura>
  <ImponibileImporto>50.00</ImponibileImporto>
  <Imposta>0.00</Imposta>
  <RiferimentoNormativo>Operazione non soggetta IVA ai sensi dell'art. 1, commi da 54 a 89, L. 190/2014 - Regime Forfetario</RiferimentoNormativo>
</DatiRiepilogo>
```
- **Bollo virtuale** obbligatorio se imponibile >€77.47 e operazione esente

---

## 3. Intermediari SDI 2026 (raccomandati per PMI)

| Servizio | Prezzo | API | Note |
|----------|--------|-----|------|
| **Fattura24** | ~€1-2/fattura o €9.90/mese | REST + webhook | Più semplice, ottima DX |
| **Aruba PEC** | ~€0.50/fattura | REST | Affidabile, italiano, PEC integrata |
| **Fatture in Cloud** | Piano gratuito 5/mese | REST v2 | Ottimo per test, limit in free |
| **Invoicehub** | €49/anno illimitato | REST | Ottimo rapporto qualità/prezzo |
| **Namirial** | Enterprise | REST | Troppo costoso per PMI |

### **Raccomandazione per Fluxion: Fattura24**
- API REST semplice (POST XML → ricevi ID tracking)
- Webhook per aggiornamenti stato SDI
- Prezzi accessibili per PMI 1-15 dip.
- Documentazione chiara in italiano
- Alternative: Aruba se il cliente ha già PEC Aruba

### Flusso API Fattura24 (pseudocodice)
```
POST https://api.fattura24.com/api/v0/SaveInvoice
  headers: { apiKey: "xxx" }
  body: { xml: "<FatturaElettronica>...</FatturaElettronica>" }
→ { error: "0", description: "OK", fileId: "abc123" }

GET https://api.fattura24.com/api/v0/GetFile?fileId=abc123
→ { sdiStatus: "MC" | "NS" | "AT" | "DT" }
  -- MC=Messa in consegna, NS=Non recapitabile, AT=Accettata, DT=Decorrenza termini
```

---

## 4. DB Schema Changes (da aggiungere a migration 025)

```sql
-- Migration 025: SDI FatturaPA (C1)
ALTER TABLE fatture ADD COLUMN sdi_stato TEXT NOT NULL DEFAULT 'non_inviata'
  CHECK(sdi_stato IN ('non_inviata', 'in_invio', 'inviata', 'consegnata',
                      'accettata', 'rifiutata', 'scartata', 'decorrenza_termini'));
ALTER TABLE fatture ADD COLUMN sdi_message_id TEXT;        -- fileId intermediario
ALTER TABLE fatture ADD COLUMN sdi_data_invio TEXT;        -- ISO datetime
ALTER TABLE fatture ADD COLUMN sdi_data_risposta TEXT;     -- ISO datetime
ALTER TABLE fatture ADD COLUMN xml_content TEXT;           -- XML generato (cache)
ALTER TABLE fatture ADD COLUMN progressivo_invio TEXT;     -- es: 2026/001 univoco per anno

CREATE INDEX IF NOT EXISTS idx_fatture_sdi_stato ON fatture(sdi_stato);

-- View utile per dashboard
CREATE VIEW IF NOT EXISTS v_fatture_sdi_pending AS
SELECT f.*, c.nome, c.cognome, c.partita_iva
FROM fatture f
LEFT JOIN clienti c ON c.id = f.cliente_id
WHERE f.sdi_stato IN ('non_inviata', 'in_invio', 'rifiutata', 'scartata')
  AND f.tipo_documento != 'ricevuta';  -- solo fatture B2B/PA
```

---

## 5. Acceptance Criteria Misurabili (C1)

- [ ] **AC1** — Pulsante "Genera XML" su fattura → XML FatturaPA 1.3.2 valido (namespace corretto, campi obbligatori presenti)
- [ ] **AC2** — XML generato supera validazione schema XSD ufficiale (o checklist manuale)
- [ ] **AC3** — Pulsante "Invia SDI" chiama API intermediario e salva `sdi_message_id` + `sdi_stato = 'inviata'`
- [ ] **AC4** — Polling/webhook aggiorna `sdi_stato` a accettata/rifiutata/scartata
- [ ] **AC5** — Badge stato visibile in lista fatture (colori: grigio=non_inviata, giallo=inviata, verde=accettata, rosso=rifiutata/scartata)
- [ ] **AC6** — Regime forfettario RF19: XML generato con AliquotaIVA=0, Natura=N2.2, RiferimentoNormativo
- [ ] **AC7** — `npm run type-check` → 0 errori

---

## 6. Architettura Implementazione

### XML Generation: Rust (quick-xml)
**Motivazione**: XML generato lato Rust garantisce sicurezza, nessuna dipendenza JS, formato UTF-8 corretto.

```toml
# Cargo.toml
quick-xml = { version = "0.31", features = ["serialize"] }
# oppure approccio template string (più semplice per schema fisso)
```

**Strategia**: template string Rust con format! macro — più leggibile e manutenibile di XML builder per schema relativamente fisso.

### Comandi Tauri Nuovi
```rust
// src-tauri/src/commands/fatture.rs aggiuntivi:
pub async fn genera_xml_fattura(pool, fattura_id) -> Result<String, String>
pub async fn invia_fattura_sdi(pool, fattura_id, api_key) -> Result<SdiResponse, String>
pub async fn get_sdi_stato(pool, fattura_id) -> Result<String, String>
pub async fn aggiorna_sdi_stato(pool, fattura_id, new_stato) -> Result<(), String>
```

### TypeScript: tipo SdiStato
```ts
export type SdiStato =
  | 'non_inviata'
  | 'in_invio'
  | 'inviata'
  | 'consegnata'
  | 'accettata'
  | 'rifiutata'
  | 'scartata'
  | 'decorrenza_termini';
```

---

## 7. Edge Case e Rischi

| Caso | Gestione |
|------|---------|
| Fattura con più servizi | 1 DettaglioLinee per riga, 1 DatiRiepilogo per aliquota |
| Nota di credito | TipoDocumento=TD04, ImportoTotaleDocumento negativo |
| Cliente privato B2C | CodiceDestinatario="0000000", aggiungere CF cliente |
| Timeout API intermediario | Retry max 3x, sdi_stato="in_invio" fino a risposta |
| ProgressivoInvio duplicato | Sequenza per anno fiscale, INDEX UNIQUE opzionale |
| Bollo virtuale (€2) | Aggiungi DatiBollo se N2.2/N4 e imponibile >€77.47 |
| Fattura a PA | FormatoTrasmissione=FPA12, CodiceDestinatario=6 char IPA |

---

## 8. Ordine Implementazione Consigliato

1. **Migration 025** — alter table fatture (30min)
2. **Rust: genera_xml_fattura** — template string con tutti i campi (3h)
   - Logica RF19 vs regime ordinario
   - Calcolo DatiRiepilogo per aliquota
3. **Rust: invia_fattura_sdi** — chiamata HTTP a Fattura24 API (2h)
4. **TypeScript: hook use-fatture-sdi** — query stato + mutation invia (1h)
5. **UI: badge SdiStato** in lista fatture (30min)
6. **UI: bottone Invia SDI** + dialog conferma (1h)
7. **Test manuale** — XML generato vs validatore AdE online (30min)
