# Gap #9 Research — Analytics Dashboard + PDF Report Mensile
> Sessione 42 — 2026-03-10 | CoVe 2026

## Status: IMPLEMENTATO (commit e182afa)

## Schema Tabelle Rilevanti

**appuntamenti**: stato (CamelCase: Confermato/Completato/Cancellato/no_show), prezzo_finale, data_ora_inizio, cliente_id, servizio_id, operatore_id
**clienti**: created_at, is_vip, loyalty_visits
**servizi**: nome, categoria, prezzo
**operatori**: nome, cognome
**fatture**: totale_documento, data_emissione, stato (emessa/pagata)
**messaggi_whatsapp**: stato, data_invio, direzione

## Comandi Tauri Creati

- `get_analytics_mensili(anno: i32, mese: i32)` → AnalyticsMensili (15+ KPI)
- `genera_report_pdf_mensile(anno: i32, mese: i32)` → String (file path)

## PDF Library

`printpdf = "0.7"` già in Cargo.toml — usato anche in media.rs (export_media_pdf)
Pattern: PdfDocument::new + BuiltinFont::Helvetica/HelveticaBold + layer.use_text + doc.save

## CoVe 2026 — Competitor Analysis

- **Fresha**: cloud-only, no PDF locale — FLUXION vince con offline
- **Mindbody**: SaaS €50-200/mese — FLUXION lifetime €497
- **Jane App**: clinic-only — FLUXION multi-vertical
- **Phorest**: no PDF nativo — FLUXION ha PDF

**Differenziante unico**: PDF generato 100% offline + openPath → nessuna dipendenza cloud

## WA Confirm Rate (Gap #4 KPI)

Gap #4 usa CamelCase: stato='Confermato' (confermato via WA) / stato='Cancellato' (cancellato via WA)
Query: COUNT(stato='Confermato') / (COUNT('Confermato') + COUNT('Cancellato')) * 100
