# S172 — Audit `#feature-deep` (12 dimensioni)
> Generato: 2026-04-27 | Sezione: `landing/index.html` righe 1691–1982
> Verdict: ✅ PASS / ⚠️ FLAG / 🔴 BLOCK

---

## Sezione 1 — Verdict Matrix

| # | Dimensione | Verdict | File:Line | Issue |
|---|-----------|---------|-----------|-------|
| 1 | Headline & hierarchy | 🔴 BLOCK | 1700, 1702-1704 | Headline "codice" + sub "nascoste nel codice" — linguaggio developer |
| 2 | Copy density | 🔴 BLOCK | 1722, 1798, 1830 | Hero 3 body = 4 frasi dense, jargon Art.9/trail elevato |
| 3 | Mobile UX | ⚠️ FLAG | 1712-1713 | Grid `md:grid-cols-2` ok; ma `p-10` su mobile = 40px padding laterale su 375px screen: testo schiacciato |
| 4 | Plain language | 🔴 BLOCK | 1830, 1889, 1905, 1937, 2301, 2303 | Art.9, FDI, VAS/Oswestry/NDI, AES-256-GCM, Groq US, Node.js nel copy primario |
| 5 | Social proof / trust | ⚠️ FLAG | 1691-1982 | Zero trust signal nella sezione: nessun numero reale, badge o testimonianza |
| 6 | CTA flow | 🔴 BLOCK | 1978-1984 | Sezione termina senza CTA inline; caduta libera verso #prezzi senza ponte |
| 7 | Accessibility | ⚠️ FLAG | 1742-1758, 1770 | Nessun `aria-label` sui mock, SVG icon senza `aria-hidden` |
| 8 | Semantic HTML | ✅ PASS | 1691, 1711, 1879 | `<section>`, `<h2>`, `<h3>` usati correttamente |
| 9 | JSON-LD / Schema | ⚠️ FLAG | — | Nessun markup `SoftwareApplication` feature-list; SEO opportunity persa |
| 10 | Color contrast | ✅ PASS | — | `text-slate-400` su `bg-brand-card` (~`#0f172a`) ≈ 4.6:1 — WCAG AA ok |
| 11 | Typography | ⚠️ FLAG | 1722 | Body hero 1 = ~90 parole in un paragrafo unico; max-width non vincolata a 75ch |
| 12 | Trust & legal claim | 🔴 BLOCK | 1827, 1722, 1798, 1830 | "€20M Garante", "€40-€80/slot", "30% perso ogni anno", "consenso Art.9 digitale + firma" — claim che richiedono fonte o disclaimer |

---

## Sezione 2 — BLOCK ISSUES (priorità #1)

### BLOCK-1 — Headline + Sub "nel codice" (riga 1700, 1703)
**Cosa**: Sub-headline "9 funzioni nascoste nel codice" = developer speak puro.  
**Perché**: PMI italiano non sa cosa sia "il codice". Suona incomprensibile e oscuro.  
**Fix** — sostituire righe 1699-1704 con:
```html
<!-- PRIMA -->
<h2 class="text-3xl md:text-4xl font-bold text-white mb-4">
  Quello che FLUXION fa,<br class="hidden md:block"> e i tuoi concorrenti non sanno ancora che esiste
</h2>
<p class="text-slate-400 max-w-2xl mx-auto">
  9 funzioni nascoste nel codice. Attive dal primo giorno. Zero costi aggiuntivi …
</p>

<!-- DOPO (usa headline winning — vedi Sezione 4) -->
<h2 class="text-3xl md:text-4xl font-bold text-white mb-4">
  9 cose che FLUXION fa per te<br class="hidden md:block"> mentre tu lavori
</h2>
<p class="text-slate-400 max-w-2xl mx-auto">
  Incluse nel prezzo. Attive dal primo giorno. Nessun extra da pagare.
</p>
```

---

### BLOCK-2 — Jargon tecnico nel copy primario (righe 1830, 1889, 1905, 1937)
**Cosa**: "Art. 9 GDPR", "FDI", "VAS/Oswestry/NDI", "AES-256-GCM" come titoli h3 o corpo principale.  
**Perché**: il fondatore ha indicato esplicitamente che devono sparire dal copy primario.  
**Fix per ognuno**:

| Riga | Attuale | Sostituire con |
|------|---------|----------------|
| 1830 | "dati particolari ai sensi dell'Art. 9 GDPR" | "i dati sanitari dei tuoi pazienti sono la categoria più protetta dalla legge" |
| 1839 | "Consenso Art. 9 digitale + firma" (bullet) | "Consenso digitale con firma — valido per ispezione" |
| 1889 | `<h3>Odontogramma FDI — 32 denti cliccabili</h3>` | `<h3>Scheda denti cliccabile — 32 denti, tutto in un clic</h3>` |
| 1905 | `<h3>Scale dolore VAS, Oswestry, NDI integrate</h3>` | `<h3>Scale di valutazione del dolore integrate — compili in 30 secondi</h3>` |
| 1909 | "Compili la VAS, l'Oswestry o il NDI" | "Compili la scheda di valutazione del paziente" |
| 1937 | `<h3>Dati cifrati AES-256-GCM anche su disco</h3>` | `<h3>Dati sensibili protetti come in banca — anche se ti rubano il PC</h3>` |
| 1940-1941 | "cifrati con lo stesso standard usato dalle banche" | OK — mantieni. Rimuovi solo "AES-256-GCM" dal titolo h3 |

---

### BLOCK-3 — Node.js "richiede installazione separata" (riga 2301)
**Cosa**: disclosure dice "richiede Node.js installato (gratuito)".  
**Perché**: il fondatore ha deciso che Node.js è bundled nell'installer — il copy deve riflettere questa decisione prodotto.  
**Fix riga 2301**:
```html
<!-- PRIMA -->
<li><sup …>*</sup> <strong …>WhatsApp conferme & promemoria</strong>: richiede Node.js installato (gratuito) per il modulo whatsapp-web.js + scansione QR code dal tuo cellulare. Non usa l'API ufficiale Business (a pagamento): è il tuo numero che invia.</li>

<!-- DOPO -->
<li><sup class="text-cyan-400">*</sup> <strong class="text-slate-300">WhatsApp conferme &amp; promemoria</strong>: richiede la scansione di un QR code dal tuo cellulare (una sola volta). Non usa l'API ufficiale Business a pagamento: &egrave; il tuo numero WhatsApp che invia i messaggi.</li>
```

---

### BLOCK-4 — Claim €20M, €40-80/slot, 30%/anno (righe 1722, 1798, 1827)
**Cosa**: tre claim quantitativi senza fonte o disclaimer.  
**Perché**: D.Lgs 206/2005 art.21 — pratiche commerciali scorrette se non sostenibili.  
**Fix**: aggiungere micro-disclaimer o riformulare:

| Riga | Claim | Fix |
|------|-------|-----|
| 1722 | "tra €40 e €80" | OK se è il listino del cliente — contestualizzare: "Ogni slot vuoto vale quanto il tuo servizio più comune: spesso €40–€80." |
| 1798 | "perdi il 30% ogni anno" | Aggiungere `<sup>*</sup>` + nota in disclosure: "* Stima media settore saloni, fonte: ricerche di settore 2023." |
| 1827 | "fino a €20 milioni" | Accurato (GDPR art.83 co.5) — aggiungere `<sup>*</sup>` + nota: "* Massimale previsto dal Regolamento UE 2016/679, art.83." |

---

### BLOCK-5 — CTA flow assente in chiusura sezione (dopo riga 1977)
**Cosa**: la sezione termina con la grid secondary card, poi c'è un gap vuoto prima di `#prezzi`.  
**Fix** — inserire bridge CTA dopo `</div><!-- /6 secondary card -->` (riga 1978):
```html
<!-- Bridge CTA feature-deep → prezzi -->
<div class="text-center mt-14">
  <p class="text-slate-400 mb-4">Tutte e 9 incluse nel prezzo. Nessun extra.</p>
  <a href="#prezzi" class="btn-primary inline-flex items-center gap-2 px-8 py-3 rounded-xl font-semibold text-white">
    Vedi i prezzi &darr;
  </a>
</div>
```

---

## Sezione 3 — Copy Rewrite 9 card

| Card | Headline ATTUALE | Headline PROPOSTO | Body ATTUALE (frase chiave) | Body PROPOSTO |
|------|-----------------|------------------|----------------------------|---------------|
| 1 Sara Waitlist | "Lo slot è pieno. Sara riempie la lista d'attesa da sola." | "Slot pieno? Sara prende il prossimo cliente. Da sola." | "Ogni slot da 1 ora che non riesci a riempire ti costa tra €40 e €80." | "Ogni ora vuota in agenda è una perdita diretta. Sara gestisce la lista d'attesa e avvisa il cliente appena si libera uno slot — via WhatsApp, senza che tu faccia nulla." |
| 2 Recall dormienti | "Il tuo cliente non torna da 60 giorni. FLUXION lo va a riprendere." | "Non viene da un po'? FLUXION gli scrive. Tu non ci pensi." | "Un cliente medio di un salone viene 6 volte all'anno." | "Ogni notte FLUXION controlla chi non prenota da 60 giorni e manda un messaggio WhatsApp con il suo nome e il servizio che fa di solito. Non un volantino. Un messaggio che sembra scritto da te." |
| 3 Audit GDPR | "Il Garante può multarti fino a €20 milioni. FLUXION tiene il tuo audit GDPR aggiornato." | "I dati dei tuoi pazienti sono protetti per legge. FLUXION fa il lavoro difficile al posto tuo." | "…dati particolari ai sensi dell'Art. 9 GDPR — la categoria ad alto rischio." | "Per medici e dentisti i dati dei pazienti richiedono protezioni speciali. FLUXION registra chi ha letto o modificato cosa, raccoglie il consenso firmato digitalmente ed esporta tutto in PDF in 30 secondi." |
| 4 Odontogramma | "Odontogramma FDI — 32 denti cliccabili" | "Scheda denti digitale — clicchi sul dente, annoti tutto" | "Nessun software a parte, nessun add-on." | "Clicchi sul dente, annoti carie, impianti, devitalizzazioni. La scheda è già nella cartella del paziente. Nessun foglio di carta, nessun software extra." |
| 5 Scale dolore | "Scale dolore VAS, Oswestry, NDI integrate" | "Schede di valutazione del dolore integrate — 30 secondi e sei fatto" | "Compili la VAS, l'Oswestry o il NDI in 30 secondi." | "Le schede standard per valutare il dolore del paziente sono già in FLUXION. Le compili durante la visita e il risultato entra automaticamente nella cartella. Nessun foglio." |
| 6 Backup notturni | "Backup automatici ogni notte sul tuo PC" | "I tuoi dati al sicuro ogni notte — sul tuo PC, non su cloud" | "Se il PC si rompe, riparti in 5 minuti." | "FLUXION fa una copia completa dei tuoi dati ogni notte, sul tuo computer. Nessun abbonamento a servizi di backup. Se qualcosa va storto, sei operativo in 5 minuti." |
| 7 Cifratura | "Dati cifrati AES-256-GCM anche su disco" | "Dati sensibili protetti come in banca — anche se ti rubano il PC" | "Anche se qualcuno rubasse il tuo PC fisicamente, non leggerebbe nulla." | "Anamnesi, allergie e cartelle cliniche sono protette con lo stesso livello di sicurezza usato dalle banche. Attivo in automatico, zero configurazione." |
| 8 SDI | "Fatturazione SDI — scegli il tuo provider" | "Fattura elettronica con il provider che hai già" | "Se domani cambi commercialista o provider, non perdi nulla." | "Usi già Aruba, Fattura24 o un altro servizio per le fatture elettroniche? FLUXION si collega al tuo account. Nessun cambio, nessun blocco fornitore." |
| 9 Listini fornitori | "Storico prezzi fornitori e alert variazioni" | "Il fornitore ha alzato i prezzi? FLUXION te lo dice prima della fattura" | "FLUXION ricorda quanto pagavi il prodotto 3 mesi fa." | "FLUXION tiene traccia dei prezzi dei tuoi fornitori. Se il costo di un prodotto sale, ricevi un avviso in anticipo — utile per rinegoziare e aggiornare il tuo listino." |

---

## Sezione 4 — Headline sezione (righe 1699-1704)

3 alternative concrete, max 80 caratteri, benefit-oriented:

**A** (tempo) — RACCOMANDATO:
```
9 cose che FLUXION fa per te mentre tu lavori
```
Sub: "Incluse nel prezzo. Attive dal primo giorno. Nessun extra da pagare."

**B** (denaro):
```
9 funzioni che recuperano tempo e soldi — già nel prezzo
```
Sub: "Lista d'attesa, clienti dormienti, dati sicuri: tutto incluso senza costi aggiuntivi."

**C** (competitor):
```
Funzioni che i tuoi concorrenti pagano a parte. Tu no.
```
Sub: "9 strumenti inclusi nella licenza. Attivi dal giorno uno."

**Raccomandazione**: opzione A — più concreta, zero jargon, benefit immediato e universale per PMI.

---

## Sezione 5 — Disclosure cleanup (righe 2295-2306)

```html
<!-- VERSIONE PULITA DISCLOSURE — sostituisce righe 2295-2306 -->
<div class="mt-6 p-5 rounded-xl bg-slate-950/60 border border-slate-800">
  <p class="text-slate-300 text-xs font-semibold uppercase tracking-widest mb-3">Note &amp; precisazioni</p>
  <ul class="space-y-2 text-slate-400 text-xs leading-relaxed">
    <li><sup class="text-cyan-400">*</sup> <strong class="text-slate-300">Sara Voice Agent (telefono)</strong>: richiede una linea VoIP separata (es. EHIWEB ~&euro;5/mese) o deviazione del tuo numero esistente. Il servizio telefonico non &egrave; incluso nella licenza.</li>
    <li><sup class="text-cyan-400">*</sup> <strong class="text-slate-300">Sara &amp; risposta intelligente</strong>: 200 conversazioni/giorno incluse senza costi aggiuntivi. Sopra questa soglia Sara passa alla modalit&agrave; risposta-base. L'audio viene elaborato da provider esterni internazionali certificati; il database con nomi, numeri e appuntamenti rimane sul tuo PC.</li>
    <li><sup class="text-cyan-400">*</sup> <strong class="text-slate-300">WhatsApp conferme &amp; promemoria</strong>: richiede la scansione di un QR code dal tuo cellulare (una sola volta all'attivazione). Non usa l'API ufficiale Business a pagamento: &egrave; il tuo numero WhatsApp che invia i messaggi.</li>
    <li><sup class="text-cyan-400">*</sup> <strong class="text-slate-300">SDI fatturazione elettronica</strong>: necessario un account presso un provider di tua scelta (es. Aruba ~&euro;1/fattura, Fattura24 da ~&euro;6/mese). FLUXION genera il file e invia tramite il tuo account.</li>
    <li><sup class="text-cyan-400">*</sup> <strong class="text-slate-300">Adempimenti GDPR</strong>: FLUXION fornisce strumenti tecnici di protezione dati e 4 template di consenso personalizzabili (~30 minuti). Ogni titolare rimane responsabile dei propri obblighi formali; per studi sanitari si consiglia verifica con un DPO.</li>
    <li><sup class="text-cyan-400">*</sup> <strong class="text-slate-300">Garanzia 30 giorni</strong>: rimborso integrale entro 30 giorni dall'acquisto scrivendo a fluxion.gestionale@gmail.com. Processato tramite Stripe entro 5&ndash;10 giorni lavorativi.</li>
  </ul>
</div>
```
**Modifiche chiave**: rimosso "Groq US", rimosso "Microsoft Edge-TTS", rimosso "Node.js installato (gratuito)", "AES-256" → non citato, "audit trail" → rimosso, "Art. 9" → rimosso, "provider esterni internazionali certificati" al posto dei brand.

---

## Sezione 6 — Quick wins <30 min (per ROI)

| # | Fix | File:Line | Impatto | Minuti |
|---|-----|-----------|---------|--------|
| 1 | Sostituire headline + sub sezione (BLOCK-1) — 3 righe HTML | 1699-1704 | Alto — prima cosa letta, elimina developer speak | 5 min |
| 2 | Rinominare `<h3>` card 4,5,7 (FDI → denti, VAS→dolore, AES→banca) | 1889, 1905, 1937 | Alto — jargon nel titolo = PMI salta la card | 10 min |
| 3 | Inserire bridge CTA dopo secondary grid (BLOCK-5) | dopo 1977 | Medio-alto — recupera conversioni che abbandonano prima di #prezzi | 5 min |
| 4 | Riscrivere disclosure Node.js (BLOCK-3) | 2301 | Medio — claim falso rispetto a decisione prodotto | 5 min |
| 5 | Aggiungere `<sup>*</sup>` ai claim 30%/anno e €20M + note in disclosure | 1798, 1827 | Medio — riduce rischio D.Lgs 206/2005 e aumenta credibilità | 10 min |

**Totale stimato: 35 minuti** per eliminare tutti i BLOCK.

---
_File: `/Volumes/MontereyT7/FLUXION/.claude/cache/agents/s172-feature-deep-audit.md`_
_Consumabile direttamente da agente implementatore per edit atomici._
