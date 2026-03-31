---
name: Fisioterapia Seed — Format and IVA Rules
description: Key decisions and schema facts used when writing the fisioterapia seed SQL
type: project
---

Seed created at `/Volumes/MontereyT7/FLUXION/scripts/seed-sara-fisioterapia.sql`.

**Why:** Fisioterapia is the first Salute-macro vertical seed with suppliers + fatture + incassi tables (medical seed and auto seed do not include those tables).

**How to apply:** When writing future Salute-vertical seeds (odontoiatra, veterinario), reuse the same table set and IVA logic below.

## Key Schema Facts

- `suppliers` table: id, nome, email, telefono, indirizzo, citta, cap, partita_iva, status, created_at, updated_at — no notes column
- `fatture` table: requires numero_completo (e.g. 'FV001/2026'), cliente_denominazione snapshot, imponibile_totale + iva_totale + totale_documento must be arithmetically consistent
- `fatture_righe`: prezzo_unitario is the NET price (ex-IVA). At 22% IVA: prezzo_unitario = prezzo_al_pubblico / 1.22
- `incassi`: metodo_pagamento values are 'contanti', 'carta', 'bonifico', 'satispay', 'assegno', 'buono', 'pacchetto', 'altro'
- `incassi` categoria values: 'servizio', 'prodotto', 'pacchetto', 'altro'

## IVA Rule — Fisioterapia Privata

Fisioterapia privata (fuori SSN) is subject to IVA 22% — NOT exempt.
Fisioterapia SSN/convenzionata would use natura='N4' (esente art.10 DPR 633/72) and aliquota_iva=0.

## Orari Medici

Medical verticals use 08:30-12:30 / 14:30-19:00 (not 09:00-13:00 / 14:00-19:00 like beauty).
giorno_settimana: 1=Lunedì, 2=Martedì, 3=Mercoledì, 4=Giovedì, 5=Venerdì, 6=Sabato.

## FK Trap

`incassi.cliente_id` must reference only client IDs defined in the same seed's `clienti` block.
The auto-generated range is cli-fis-01 through cli-fis-08 — never reference cli-fis-09 etc.
