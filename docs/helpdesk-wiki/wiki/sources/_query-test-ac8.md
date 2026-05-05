---
title: "Query Test E2E — AC8 (Win10 install)"
type: query-test
slug: _query-test-ac8
sources_consumed: []
last_ingest: 2026-05-05
status: stable
related:
  - win10-installation
  - license-key
  - network-firewall
verticals: [all]
---

# Query Test E2E — AC8 PLAN.md

> Esecuzione query test obbligatoria per chiusura FASE 5 VERIFY S185-A. Simula caso d'uso reale: founder riceve email cliente con problema install Win10 → consulta wiki → compone risposta.

## Query simulata

> "Cliente PMI parrucchiere mi scrive: ho appena ricevuto FLUXION via email, come lo installo sul mio PC Windows 10? Mi serve aiuto step-by-step."

## Procedura agente (workflow QUERY HELPDESK.md sez. 2.2)

### Step 1: Read `index.md`
Identificate sezioni rilevanti: `## Entities` (win10-installation, license-key, network-firewall) + `## Concepts` (pricing-tiers — per contesto tier).

### Step 2: Identifica candidate pages
- `[[win10-installation]]` — entity primaria (procedura step-by-step)
- `[[license-key]]` — entity collegata (attivazione post-install)
- `[[network-firewall]]` — entity supporto (porte 3001/3002)
- `[[win10-fresh-compat-summary]]` — source summary tecnico (se cliente chiede dettagli)

### Step 3: Read candidate pages (eseguito)

### Step 4: Compose answer in italiano

---

## Risposta (da inviare al cliente PMI)

Buongiorno,

per installare FLUXION sul suo PC Windows 10 segua questa procedura semplificata:

**1. Download installer** (~415 MB)
- Apra il link nell'email post-acquisto
- Scarichi `Fluxion_1.0.1_x64-setup.exe`

**2. Installazione**
- Doppio-click sul file scaricato
- Se Windows mostra "Editore sconosciuto" → click "Maggiori informazioni" → "Esegui comunque" (l'installer non è firmato per scelta zero-cost, ma è autentico)
- L'installer è completamente automatico: include WebView2 Runtime e VC++ runtime statico — nessuna installazione manuale di componenti aggiuntivi richiesta

**3. Attivazione license**
- Al primo avvio FLUXION chiede la **license key** (88 caratteri base64 ricevuti via email)
- Copi e incolli la key
- Verifica offline (no internet richiesto in questo step)

**4. Setup Wizard**
- Selezioni il verticale "hair" → micro-categoria specifica (salone_donna / barbiere / salone_unisex / etc.)
- Inserisca dati attività (nome, orari)
- Pronto all'uso

**Se ha problemi**:
- "DLL mancante" → impossibile da v1.0.1 (static CRT linking risolve)
- License non valida → mi scriva a `fluxion.gestionale@gmail.com` con riferimento Stripe checkout
- Antivirus blocca → esclusione cartella FLUXION (no admin richiesto)

Cordiali saluti,
Gianluca — FLUXION

---

## Citazioni utilizzate (verifica AC8: ≥2 wiki + ≥1 raw)

- [[win10-installation]] — procedura step-by-step + errori comuni (entity primaria)
- [[license-key]] — attivazione post-install Ed25519 offline (entity collegata)
- [[network-firewall]] — porte localhost 3001/3002 (entity supporto, citata implicitamente in fix antivirus)
- [[win10-fresh-compat-summary]] — riferimento tecnico v1.0.1 static CRT
- [raw/install/win10-fresh-compat.md:21-34] — quote autoritativa "Static CRT elimina dipendenza vcruntime140.dll/msvcp140.dll"

**Verifica AC8**: ✅
- Citation wiki count: **4** (target ≥2 ✅)
- Citation raw count: **1** (target ≥1 ✅)
- Risposta in italiano ✅
- Tono chiaro tecnico-friendly ✅
- Founder email contact citata correttamente ✅

## File-back?

NO — questa pagina è il test E2E AC8 stesso (slug `_query-test-ac8`, prefisso `_` indica meta-content non query reale). Future query reali da support email → file-back come pages standard `wiki/concepts/<topic>.md`.
