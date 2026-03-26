---
name: wa_outreach_rules
description: Regole operative WhatsApp cold outreach — limiti, anti-ban, template, funnel
type: project
---

Regole operative per il Sales Agent WA FLUXION basate su dati empirici 2025.

**Limiti giornalieri:**
- Prime 4 settimane (numero nuovo): max 20 msg/giorno
- Dopo 4 settimane (numero aged): max 40-50 msg/giorno
- Delay tra messaggi: min 60s, ottimale 120s con distribuzione gaussiana
- Pausa lunga ogni 5 messaggi: 5-10 minuti

**Orari validi:** lunedi'-venerdi', 9:00-12:30 e 14:30-18:00 SOLO

**Anti-ban:**
- Variazione testo obbligatoria (min 40% differenza tra messaggi)
- Min 5 varianti per ogni sezione del template
- 1 solo link per messaggio (YouTube diretto, non accorciato)
- UTM parameters accettati da WA
- Profilo Business completo (foto, nome "Gianluca — FLUXION", status)
- 2-3 SIM di backup pronte

**Funnel WA → acquisto:**
WA messaggio (link YouTube) → YouTube video (6 min) → CTA in descrizione → Landing → Stripe

**Perche' YouTube, non landing:** CTR 18-22% vs 12%. Conversione finale 2.3% vs 1.1%.
WA mostra thumbnail automatica del video = anteprima che crea fiducia.

**Struttura messaggio ottimale:**
1. Apertura personalizzata (nome + attivita' + citta') — 1 frase
2. Hook dolore specifico per categoria — 1 frase
3. Link YouTube con UTM — 1 riga
4. Firma "Gianluca — FLUXION" — 1 riga

**Warning indicators da monitorare:**
- Delivery rate < 90% → alert
- Read rate < 30% → attenzione
- Response rate < 3% → rallenta
- Block rate > 2% → stop immediato

**Ban recovery:**
- Temporaneo (24-72h): aspetta 72h, riprendi con 5/giorno per 1 settimana
- Permanente: SIM backup, 2 settimane uso normale, poi warm-up standard

**Why:** Ban WA = stop immediato delle vendite. Le regole anti-ban sono NON NEGOZIABILI.

**How to apply:** Implementare nel Sales Agent Sprint 5. Ogni parametro di rate limiting
deve usare distribuzione randomizzata (non valori fissi) per sembrare umano.
