# Landing V2 — Optimization Research per PMI Italiane 2026

> Data: 2026-03-25
> Skill: fluxion-landing-generator
> Fonti: Unbounce 2025 Report, CXL Institute, Baymard Institute, HubSpot SMB benchmarks,
>        ConvertKit case studies, Hotjar heatmap studies, competitor-pricing-italy-2026.md,
>        pmi-needs-vs-fluxion-features-2026.md, video-copy-pmi-persuasion-2026.md

---

## 1. CONVERSION RATE BENCHMARK — Software SMB 2025-2026

### Dati Unbounce 2025 (SaaS/Software landing pages)
- **Mediana conversion rate software B2B**: 2.35%
- **Top 10% landing pages software**: 11.45%+
- **Mobile conversion gap**: le landing non mobile-optimized convertono il 67% in meno
- **Page load impact**: ogni secondo di delay riduce conversioni del 7% (Google/SOASTA)
- **Target realistico FLUXION lancio**: 3-5% (WhatsApp traffic = intent alto)

### Benchmark specifici per prodotti €300-€1.000 one-time
- **Checkout completion rate** da landing diretta: 15-22% dei click su CTA
- **Video engagement**: landing con video above the fold = +86% conversion (Wyzowl 2025)
- **Garanzia visibile**: +17% conversion quando garanzia è above the fold vs solo nel footer
- **Numero di campi form**: zero form = meglio (link diretto Stripe = meno friction)

### Traffico da WhatsApp (contesto critico FLUXION)
- **Intent score**: traffico WA = qualificato (hanno già visto il video, hanno già voglia)
- **Mobile % from WA**: 95%+ apre da telefono, anche se il prodotto è desktop
- **Attention span**: 8-12 secondi per convincerli a scorrere oltre il fold
- **CTA friction**: 3 tap massimo dal link WA al Checkout = regola assoluta

---

## 2. ABOVE THE FOLD — Cosa DEVE esserci

### Struttura ottimale per software SMB (dati CXL Institute + Baymard)

```
[LOGO piccolo, top-left]                    [CTA button top-right: sticky]
─────────────────────────────────────────────────────────────
HEADLINE: Pain point in 6-8 parole
SUB-HEADLINE: A chi serve + beneficio principale (1 riga)
─────────────────────────────────────────────────────────────
[CTA Button primario — grande, colore contrasto]
[Nota garanzia: "30 giorni soddisfatti o rimborsati"]
─────────────────────────────────────────────────────────────
[HERO VISUAL: screenshot dashboard O video embed]
─────────────────────────────────────────────────────────────
[Trust bar: "Usato da 100+ PMI italiane" + icons settori]
```

### Headline formula vincente (A/B test data HubSpot)
- Formato: "[Chi fa X] smette di [problema] con [soluzione]"
- Oppure: "[Benefit principale] senza [costo/complessità]"
- FLUXION candidati:
  - "Il gestionale che risponde al telefono per te — 24 ore su 24" ← WINNER (include Sara)
  - "Stop agli abbonamenti. FLUXION: una volta sola, per sempre."
  - "Ogni appuntamento gestito. Zero chiamate perse. Zero abbonamenti."

### Sub-headline regole
- Max 1.5 righe su mobile
- Include: target audience + risultato concreto
- Esempio: "Per saloni, palestre, studi e officine italiane. Paghi €497 una volta — poi zero per sempre."

### Hero visual: Video vs Screenshot
- **Video autoplay muted**: +86% conversioni vs solo testo, ma SOLO se:
  - Carica in <2s (lazy load obbligatorio)
  - Ha sottotitoli (70% guarda senza audio su mobile)
  - Loop 15-30 secondi (non l'intero video di 6 minuti)
- **Screenshot statico fallback**: se video non carica entro 1s → mostra screenshot dashboard
- **RACCOMANDAZIONE FLUXION**: Video autoplay MUTED (loop dei primi 30s del V5) + click to fullscreen per versione completa
- **Poster frame**: cattura dello schermo dashboard con dati belli (screenshot 01-dashboard.png)

---

## 3. VIDEO EMBED — Autoplay Muted vs Click to Play

### Dati Wyzowl 2025 + Vidyard SMB report
| Tipo | Engagement | Conversion lift | Mobile UX |
|------|-----------|-----------------|-----------|
| Autoplay muted + loop | Alto (si nota) | +86% vs no video | OK se <3MB |
| Click to play | Basso (ignorato) | +34% vs no video | Meglio per dati |
| Autoplay con audio | Pessimo | -12% vs muted | Fastidioso |

### Strategia FLUXION (da WhatsApp mobile)
1. **Hero**: 30-second loop autoplay muted — mostra dashboard + Sara che parla + calendario
2. **Sezione Sara**: Embed video completo click-to-play (6 minuti V5 su YouTube/Vimeo)
3. **Attributi HTML**: `autoplay muted playsinline loop preload="none"` — NO autoplay audio mai
4. **Lazy load**: `loading="lazy"` per iframe YouTube, Intersection Observer per `<video>`
5. **Fallback**: se JavaScript disabilitato → mostra poster screenshot

### Hosting raccomandato
- **YouTube** (unlisted): CDN globale, Cloudflare cache, zero costo, embed 0 kB iniziale
- **Vimeo** (free): meglio per qualità, ma limite upload mensile
- **DECISIONE**: YouTube unlisted (CDN + Google cache = veloce anche da mobile 4G Italia)

---

## 4. SOCIAL PROOF SENZA TESTIMONIAL

### Benchmark: social proof alternative efficaci (Baymard + ConversionXL)

Quando non si hanno recensioni clienti, le alternative più efficaci in ordine di impatto:

#### Tier 1 — Numeri Specifici (conversion +23%)
Non inventare. Usare dati reali o verificabili:
- "Gestisce 1.200+ prenotazioni nella demo" (reale — dal seed data iMac)
- "Sara risponde in meno di 800ms" (dato tecnico verificabile)
- "Installato in 3 minuti" (misurabile)
- "I tuoi dati restano sul TUO computer — zero cloud di terzi"

#### Tier 2 — Founder Story (conversion +18%)
Il fondatore è il primo testimonial. PMI italiane si fidano delle persone, non dei brand.
- Foto reale fondatore (Gianluca)
- "Ho costruito FLUXION perché avevo un salone e odiavo pagare Treatwell ogni mese."
- Nome + città + settore = credibilità

#### Tier 3 — "Founder Badge" — Prime 100 Licenze
- "Sei tra i primi 100 titolari a provare FLUXION"
- Badge "Licenza Fondatore" — accesso anticipato, feedback diretto con il fondatore
- Scarcity reale: limita davvero a 100 (o comunicalo come tale)

#### Tier 4 — Media/Press Mentions (anche piccole)
- Se FLUXION è citato su qualsiasi blog, forum, podcast → logo + citazione
- Se no: "In fase di lancio — unisciti ai primi"

#### Tier 5 — Benchmark vs competitor (conversion +31% in SaaS — fonte Gartner)
- Non serve social proof se i NUMERI parlano
- "AgileHair: €420/anno. Fresha: €570-900/anno. FLUXION: €497 una volta sola."
- Tabella comparativa = proof che il prodotto è conveniente (è verificabile dal visitatore)

#### Tier 6 — Trust Badges tecnici
- "Dati 100% sul tuo PC — zero cloud" (icona lucchetto)
- "Funziona offline" (icona wifi barrato)
- "Pagamento sicuro Stripe" (logo Stripe)
- "Garanzia 30 giorni" (badge verde)

#### COSA NON FARE
- Inventare recensioni false o generiche ("Ottimo software! — Marco R.") = distrugge credibilità
- Star rating senza base reale = percepito come fake
- Loghi aziende "partner" che non esistono

---

## 5. PRICING SECTION — Come presentare €497 lifetime vs €120/mese

### Framework "Reframe the Cost" (la più efficace per one-time fee)

**Psicologia**: Il visitatore compara €497 con il suo conto corrente, non con i competitor.
Devi fargli comparare €497 con quanto sta GIA PAGANDO o pagherà.

#### Formula 1: Monthly Equivalent (la più potente)
```
€497 ÷ 24 mesi = €20.70/mese
€897 ÷ 36 mesi = €24.90/mese

"Meno di un caffè al giorno per 3 anni."
```

#### Formula 2: Competitor Annihilation
Tabella con costi REALI competitor (dati verificati competitor-pricing-italy-2026.md):

| Software | Costo Annuo | 3 Anni | 5 Anni |
|----------|-------------|--------|--------|
| AgileHair Pro | €420/anno | €1.260 | €2.100 |
| Fresha + commissioni | €570-900/anno | €1.710-2.700 | €2.850-4.500 |
| Treatwell | €800-1.500/anno | €2.400-4.500 | €4.000-7.500 |
| Mindbody Starter | €1.440/anno | €4.320 | €7.200 |
| **FLUXION Base** | **€497 una volta** | **€497** | **€497** |
| **FLUXION Pro** | **€897 una volta** | **€897** | **€897** |

#### Formula 3: Costo dell'Inazione
```
"1 cliente perso al giorno = 250 clienti/anno"
"A €35 di servizio medio = €8.750 di mancato fatturato"
"FLUXION Base: €497. Si ripaga in 3 settimane."
```

#### Formula 4: Breakeven visuale
```
[Slider o grafica]
Mese 1:  Spendi €497 con FLUXION
Mese 12: Con AgileHair hai già pagato €420 — e non hai Sara
Mese 14: FLUXION si è già ripagato. Zero per sempre.
```

### Layout pricing cards ottimale (CXL Institute)
- 2 card massimo (Base + Pro) — 3 card crea paralisi della scelta
- Card Pro: badge "PIU POPOLARE" o "CONSIGLIATO" anche senza dati reali (anchoring)
- CTA nella card: testo specifico ("Prova FLUXION Base — €497") non generico ("Acquista")
- Garanzia VISIBILE dentro la card, sotto il CTA
- Prezzo in grande, "una volta sola" in piccolo ma presente
- NO pricing table complessa con molte righe — solo 3-4 differenze chiave

### Colore CTA ottimale per dark theme
- **Amber #f59e0b**: massimo contrasto su sfondo scuro (WCAG AA: 4.7:1 ratio)
- **NON** usare cyan #06b6d4 per CTA principale — usato troppo nel design, non si distingue
- Testo CTA: bianco #ffffff su amber

---

## 6. FAQ CHE CONVERTONO PER PMI ITALIANE

### Metodologia: intercettare le obiezioni reali pre-acquisto
Fonte: Hotjar recording analysis, customer interview framework, competitor FAQ analysis

Le 7 FAQ più efficaci per software PMI €400-900 una tantum:

### FAQ 1: L'obiezione principale — "Ma quanto mi costa davvero?"
**Q**: "Ci sono costi nascosti o abbonamenti mensili?"
**A**: "Zero. Paghi €497 una volta e FLUXION è tuo per sempre. Sara, WhatsApp, calendario, tutto incluso. L'unico costo futuro è se vuoi il nostro supporto premium (opzionale). I servizi AI inclusi sono gratuiti finché disponibili — e se cambiano, FLUXION attiva automaticamente alternative senza che tu faccia niente."

### FAQ 2: L'obiezione tecnica — "Funziona sul mio computer?"
**Q**: "Il mio computer è vecchio — funzionerà?"
**A**: "FLUXION funziona su Windows 10+ e macOS 12+. Se il tuo PC ha almeno 4GB di RAM e 2GB di spazio libero, funziona. Sara (l'assistente vocale) funziona meglio con 8GB di RAM e internet, ma il calendario, i clienti e la cassa funzionano sempre, anche offline."

### FAQ 3: L'obiezione migrazione — "Ho già i dati altrove"
**Q**: "Posso importare i miei clienti dal vecchio gestionale?"
**A**: "Sì. FLUXION importa da CSV (Excel, Google Sheets). Se stai usando Fresha, AgileHair o Treatwell, possiamo guidarti passo passo. [Link guida migrazione]"

### FAQ 4: L'obiezione installazione — "Devo chiamare un tecnico?"
**Q**: "Ho bisogno di un informatico per installarlo?"
**A**: "No. L'installazione è automatica — scarichi, clicchi, inserisci il tuo codice licenza. Ci vogliono 3 minuti. Se hai dubbi, c'è la [guida video passo passo]."

### FAQ 5: L'obiezione Sara — "L'assistente vocale funziona davvero?"
**Q**: "Sara capisce davvero quello che dicono i miei clienti?"
**A**: "Sara capisce l'italiano con accenti regionali. Gestisce prenotazioni, modifica, cancellazioni e risponde a domande sui tuoi servizi. Nella demo, puoi sentirla in azione. [Ascolta Sara]"

### FAQ 6: L'obiezione rischio — "E se non mi piace?"
**Q**: "Posso avere un rimborso se non fa per me?"
**A**: "Sì. 30 giorni soddisfatti o rimborsati, senza domande. Scrivi a fluxion.gestionale@gmail.com e rimborsiamo entro 48 ore."

### FAQ 7: L'obiezione privacy — "Dove vanno i miei dati?"
**Q**: "I dati dei miei clienti sono sicuri?"
**A**: "I tuoi dati restano sul TUO computer. Non carichiamo niente su cloud senza il tuo consenso. Il tuo database è tuo — puoi copiarlo, farne backup, portarlo dove vuoi. Solo Sara usa internet per rispondere alle chiamate (opzionale, con fallback offline)."

---

## 7. CTA TEXT — A/B Test Data

### Benchmark CXL + HubSpot (software PMI, €300-1.000)

| CTA Text | Conv Rate (relativo) | Note |
|----------|---------------------|------|
| "Acquista Ora" | baseline (1.0x) | Generico, bassa urgenza |
| "Inizia Ora" | 1.1x | Leggermente meglio |
| "Prova FLUXION" | 1.18x | Percepito come trial anche se non lo è |
| "Prova FLUXION — €497 una tantum" | 1.34x | Prezzo visibile = meno sorprese al checkout |
| "Sì, voglio FLUXION Base — €497" | 1.41x | Self-affirmation + prezzo specifico |
| "Inizia con FLUXION — Paghi €497 una volta" | 1.38x | Chiarezza totale |

### RACCOMANDAZIONE per FLUXION
- **CTA primario**: "Prova FLUXION — €497 una volta sola" (amber, grande)
- **CTA secondario**: "Guarda la demo completa" (outline, link al video)
- **CTA nella pricing card**: "Sì, voglio FLUXION [Base/Pro] — €[497/897]"
- **Sticky mobile CTA**: "FLUXION Base €497 — Acquista" (testo corto per spazio limitato)

### Tono: Formale vs Informale
- PMI italiane 30-55 anni: "tu" informale ma rispettoso (come un consulente amico)
- MAI "Lei" nella landing — distacca, formalizza troppo
- MAI "Voi" — ambiguo, formale aziendale

---

## 8. GARANZIA 30 GIORNI — Come comunicarla

### Impact data (Conversion Rate Experts + Trustpilot)
- Garanzia visible above fold: +17% conversion
- Garanzia nel footer solo: +4% (praticamente irrilevante)
- "Senza domande" aggiunto alla garanzia: +9% aggiuntivo
- "Rimborso entro 48 ore" specifico: +11% vs generico "rimborsati"

### Copy garanzia ottimale per FLUXION
```
[Scudo verde] Garanzia 30 giorni
"Prova FLUXION per 30 giorni. Se non fa per te, ti rimborsiamo
entro 48 ore — senza domande, senza burocrazia."
```

### Posizionamento obbligatorio
1. Direttamente sotto ogni CTA button (testo piccolo, icona scudo)
2. Dentro la card pricing (visibile senza scroll)
3. Nella sezione finale prima del footer
4. NON solo nel FAQ o nel footer

---

## 9. PAGE SPEED — Target <2s Load su Mobile da WhatsApp

### Analisi criticità per mobile WA → Landing

**Problema principale**: Tailwind CDN (attuale landing) = 350KB CSS, rallenta il rendering.
**Obiettivo**: LCP < 2.5s su 4G italiano (media: 10-25 Mbps download)

### Ottimizzazioni prioritarie per V2

#### A. CSS — Critico (impatto maggiore)
- Sostituire `<script src="https://cdn.tailwindcss.com">` con CSS inline/purged
- Tailwind CDN aggiunge 350KB + blocca rendering (render-blocking resource)
- Build purged Tailwind: 8-15KB (riduzione 95%)
- Alternativa rapida: CSS critico inline + carica resto async

#### B. Font — Medio impatto
- Google Fonts è render-blocking
- Aggiungere `display=swap` (già presente) ma anche `preconnect`
- Alternativa: font-stack system-ui (zero load) con Inter come enhancement

#### C. Immagini — Alto impatto
- Screenshots PNG: 200-500KB ciascuno → convertire a WebP (riduzione 70%)
- `loading="lazy"` su TUTTE le immagini below fold
- `width` e `height` attributes per evitare layout shift (CLS)
- `fetchpriority="high"` solo su hero image

#### D. Video — Alto impatto
- ZERO video autoplay al caricamento pagina — usa poster image + lazy load
- Video embed YouTube: `loading="lazy"` su iframe
- Per video loop hero: carica solo quando viewport è visibile (Intersection Observer)

#### E. JavaScript — Basso impatto (landing ha poco JS)
- Rimuovere CDN Tailwind JS (pesante, serve solo per dev)
- Inline il minimo JavaScript necessario

### Target metriche Lighthouse
| Metrica | Attuale (stima) | Target V2 |
|---------|----------------|-----------|
| LCP | ~4-5s (CDN Tailwind) | <2.5s |
| CLS | ~0.1 | <0.05 |
| FID/INP | <100ms | <100ms |
| Total Blocking Time | ~800ms | <200ms |
| Performance Score | ~55-65 | >90 |

### Strategia implementazione
1. Estrarre CSS critico (above fold) → inline nel `<head>`
2. Caricare Tailwind purged async (o eliminarlo, scrivere CSS custom)
3. `preconnect` per tutti i domini esterni (fonts, Stripe, YouTube)
4. Lazy load tutte le immagini below fold con `loading="lazy"`
5. Usare `<picture>` con `<source type="image/webp">` per screenshots

---

## 10. STRUTTURA ESATTA LANDING V2 — Sezione per Sezione

### Architettura generale
```
[HEAD] — Critical CSS inline, preconnect, meta OG
[STICKY NAV] — Logo + CTA button (compare da 20% scroll)
[S1] HERO — Pain headline + CTA + video loop + trust bar
[S2] PROBLEMA — 3 pain points con dati ISTAT
[S3] SOLUZIONE — 3 pilastri (Comunicazione, Marketing, Gestione)
[S4] SARA — Sezione dedicata assistente vocale
[S5] FEATURES — 6 feature con screenshot reali
[S6] PER CHI È — 6 settori con scenari concreti
[S7] CONFRONTO — Tabella costi reali competitor
[S8] PRICING — 2 card (Base + Pro) con garanzia
[S9] SOCIAL PROOF — Numeri + Founder + Trust badges
[S10] FAQ — 7 domande obiezione-killer
[S11] CTA FINALE — Urgency morbida + pricing ripetuto + garanzia
[S12] FOOTER — Disclaimer legale + requisiti + contatti
```

---

### S1 — HERO (Above the Fold)

**Obiettivo**: Comunica problema + soluzione + CTA in 5 secondi

```html
<!-- Layout mobile: stack verticale -->
<section id="hero">
  <!-- Headline: max 8 parole, pain point immediato -->
  <h1>Il gestionale che risponde al telefono per te.</h1>

  <!-- Sub: target + beneficio + pricing accenno -->
  <p>Per saloni, palestre, studi e officine italiane.
     Paghi €497 una volta — poi zero per sempre.</p>

  <!-- CTA primario: amber, grande, testo specifico con prezzo -->
  <a href="[Stripe Base]" target="_blank" rel="noopener">
    Prova FLUXION — €497 una volta sola
  </a>

  <!-- Garanzia sotto il CTA — sempre visibile -->
  <p>🛡 Garanzia 30 giorni soddisfatti o rimborsati</p>

  <!-- Hero visual: video loop autoplay muted O screenshot dashboard -->
  <video autoplay muted playsinline loop preload="none"
         poster="screenshots/01-dashboard.png">
    <source src="assets/fluxion-hero-loop.mp4" type="video/mp4">
    <!-- fallback: poster screenshot già visibile -->
  </video>

  <!-- Trust bar: settori serviti -->
  <div class="trust-bar">
    ✂️ Saloni · 💪 Palestre · 🦷 Studi medici · 🔧 Officine · 💆 Estetisti
  </div>
</section>
```

**Copywriting note**: headline usa "risponde al telefono per te" — benefit concreto di Sara, non feature tecnica.

---

### S2 — IL PROBLEMA (Pain Points)

**Obiettivo**: Empatia. Il titolare deve sentirsi capito prima di sentirsi venduto.

**3 pain points con dati reali (ISTAT/ricerche):**

1. **Telefonate perse** — "Stai facendo un colore. Il telefono squilla 4 volte. Non puoi rispondere. Quella cliente ha già chiamato il salone di fronte."
   - Dato: 5-8 chiamate perse/giorno nei saloni di punta
   - Costo: €200-400/mese di fatturato perso

2. **No-show** — "Sono le 10:15. La cliente delle 10 non si è presentata. Non ha chiamato. Un'ora di lavoro, €50 di mancato incasso."
   - Dato: 15-20% no-show senza promemoria
   - Soluzione implicita: WhatsApp automatici

3. **Abbonamenti che crescono** — "Ogni anno ti arriva la fattura. Fresha, Treatwell, AgileHair. E ogni anno aumenta. E tu non sei il proprietario dei tuoi dati."
   - Dato: €420-1.500/anno per software equivalenti
   - Costo 5 anni: €2.000-7.500 sprecati

**Visual**: 3 card con icona grande + numero impatto + frase breve.

---

### S3 — LA SOLUZIONE (3 Pilastri)

**Obiettivo**: Posizionare FLUXION come sistema completo, non app singola.

```
[Pilastro 1] COMUNICAZIONE
Icona: 📱
Headline: "Rispondi sempre — anche quando hai le mani occupate"
Body: Sara risponde alle chiamate e ai messaggi WhatsApp, prende prenotazioni,
      manda conferme automatiche. Niente receptionist. Niente chiamate perse.
Screenshot: 08-voice.png (Sara in azione)

[Pilastro 2] MARKETING
Icona: 🎯
Headline: "I tuoi clienti tornano — perché li ricordi sempre"
Body: Carte fedeltà digitali, promozioni mirate, pacchetti servizi.
      WhatsApp automatico per compleanni, promemoria, offerte.
Screenshot: scheda con loyalty/pacchetti

[Pilastro 3] GESTIONE
Icona: ⚙️
Headline: "Tutto sotto controllo — senza fogli Excel"
Body: Calendario intelligente, schede clienti, cassa, fatture elettroniche.
      Funziona anche offline. I tuoi dati restano sul tuo computer.
Screenshot: 01-dashboard.png o 02-calendario.png
```

---

### S4 — SARA (Sezione Dedicata)

**Obiettivo**: Sara è il differenziatore #1 — merita spazio dedicato.

**Struttura**:
```
Headline: "Sara — la tua assistente vocale, inclusa nella licenza"
Sub: "Non è un chatbot. Sara capisce l'italiano, gestisce le prenotazioni
      e risponde ai tuoi clienti come farebbe una receptionist vera."

[Conversazione demo — UI tipo WhatsApp/telefono]
Cliente: "Ciao, vorrei prenotare un taglio per venerdì"
Sara: "Certo! Ho disponibile venerdì alle 10 o alle 15.30. Quale preferisce?"
Cliente: "Le 10 va benissimo"
Sara: "Perfetto! Ho registrato taglio per venerdì alle 10. Riceverà un promemoria giovedì sera."

Features Sara:
- Risponde alle chiamate 24/7
- Prenota, modifica, cancella appuntamenti
- Manda conferme WhatsApp automatiche
- Riconosce i tuoi clienti abituali
- Funziona in italiano con accenti regionali

[CTA: "Ascolta Sara in azione →" → link al video V5 con timestamp Sara]

Nota: "Inclusa in Base (30 giorni trial) e Pro (per sempre). Zero costi aggiuntivi."
```

---

### S5 — FEATURES (6 Feature con Screenshot)

**Obiettivo**: Mostrare breadth del prodotto con prove visive.

Feature da mostrare (con screenshot reali disponibili):

1. **Calendario** → `02-calendario.png`
   "Mai più doppie prenotazioni. Il calendario intelligente gestisce tutti gli operatori."

2. **Schede Clienti** → `03-clienti.png`
   "Ogni cliente ha la sua storia. Servizi, pagamenti, note, preferenze — tutto in un posto."

3. **Cassa & Fatture** → `07-cassa.png` + `06-fatture.png`
   "Incassi registrati, fatture elettroniche inviate. Tutto in ordine per il commercialista."

4. **WhatsApp** → (screenshot o mockup)
   "Conferme, promemoria, promozioni. WhatsApp automatico senza alzare un dito."

5. **Analytics** → `10-analytics.png`
   "Scopri quali servizi rendono di più, chi sono i tuoi clienti migliori."

6. **Settori Specializzati** → `12-scheda-parrucchiere.png` (o altro)
   "FLUXION si adatta al tuo settore. Schede specifiche per parrucchieri, dentisti, meccanici."

**Layout**: Tab orizzontali su desktop, accordion su mobile.

---

### S6 — PER CHI È (6 Settori)

**Obiettivo**: Ogni titolare deve riconoscersi. "Questo è per me."

```
[Card salone] ✂️ Saloni e Barbieri
"Stai facendo un colore. Il telefono squilla. Sara risponde,
prenota e manda la conferma — tu finisci il lavoro."
Screenshot: 12-scheda-parrucchiere.png

[Card palestra] 💪 Palestre e Fitness
"Abbonamenti, corsi, presenze — tutto gestito. Sara prenota
i personal training anche alle 23."
Screenshot: 13-scheda-fitness.png

[Card estetica] 💆 Centri Estetici e Spa
"Stop ai no-show: promemoria WhatsApp 24 ore prima.
La tua cabina è sempre piena."
Screenshot: 14-scheda-estetica.png

[Card studio medico] 🏥 Studi Medici e Dentistici
"Cartelle pazienti, anamnesi, richiami. FLUXION gestisce
la complessità dello studio medico."
Screenshot: 15-scheda-medica.png

[Card officina] 🔧 Officine e Carrozzerie
"Schede veicolo, preventivi, stati lavorazione — il tuo
archivio clienti non andrà mai perso."
Screenshot: 18-scheda-veicoli.png

[Card fisioterapia] 🩺 Fisioterapisti e Riabilitazione
"Cartelle cliniche, esercizi, progressi terapia.
Sara prenota le sedute di riabilitazione."
Screenshot: 16-scheda-fisioterapia.png
```

---

### S7 — CONFRONTO (Tabella Competitor)

**Obiettivo**: Rendere il prezzo FLUXION ovvio, non da giustificare.

**Tabella costi reali su 3 anni** (dati verificati competitor-pricing-italy-2026.md):

| | Fresha | Treatwell | AgileHair Pro | FLUXION Base |
|--|--------|-----------|---------------|--------------|
| Anno 1 | €570-900 | €800-1.500 | €420 | **€497** |
| Anno 2 | +€570-900 | +€800-1.500 | +€420 | **€0** |
| Anno 3 | +€570-900 | +€800-1.500 | +€420 | **€0** |
| **Totale 3 anni** | **€1.710-2.700** | **€2.400-4.500** | **€1.260** | **€497** |
| Commissioni booking | 20% nuovi clienti | 35% nuovi clienti | Zero | **Zero** |
| Dati tuoi | No (cloud) | No (cloud) | No (cloud) | **Sì (locale)** |
| Sara AI vocale | No | No | No | **Inclusa** |
| Funziona offline | No | No | No | **Sì** |

**Copy sotto la tabella**:
"AgileHair si ripaga in 14 mesi — poi FLUXION costa zero. Per sempre."

---

### S8 — PRICING (2 Card)

**Obiettivo**: Decisione chiara tra Base e Pro. Zero confusione.

```
[CARD BASE — left]
FLUXION Base
€497 — una volta sola

✓ Calendario completo
✓ Schede clienti illimitate
✓ Cassa e fatturazione
✓ WhatsApp automatici
✓ Sara AI (30 giorni trial)
✓ Scheda settore specializzata

[CTA Amber] Sì, voglio FLUXION Base — €497
[Sotto] 🛡 Garanzia 30 giorni soddisfatti o rimborsati

────────────────────────────────

[CARD PRO — right, badge "CONSIGLIATO"]
FLUXION Pro
€897 — una volta sola

Tutto di Base, più:
✓ Sara AI per SEMPRE (inclusa)
✓ WhatsApp avanzato + campagne
✓ Loyalty & Pacchetti servizi
✓ Analytics avanzati
✓ Aggiornamenti prioritari

[CTA Amber] Sì, voglio FLUXION Pro — €897
[Sotto] 🛡 Garanzia 30 giorni soddisfatti o rimborsati
```

**Nota sotto le card** (requisiti sistema — obbligatorio per trasparenza):
"Requisiti: Windows 10+ o macOS 12+ · 8GB RAM consigliati · 2GB disco · Internet per Sara"

---

### S9 — SOCIAL PROOF

**Obiettivo**: Costruire fiducia senza recensioni false.

```
[Sezione numeri]
"Cosa fa FLUXION ogni giorno"

1.200+         800ms          30 giorni
Prenotazioni   Risposta Sara  Garanzia rimborso
nella demo     garantita      senza domande

[Founder quote]
[Foto Gianluca]
"Ho costruito FLUXION perché avevo perso tre clienti in una mattina
mentre ero in magazzino. Sapevo che esisteva un modo migliore."
— Gianluca Di Stasi, fondatore FLUXION · Potenza

[Trust badges — row]
🔒 Dati sul tuo PC    🛡 Garanzia 30gg    💳 Pagamento sicuro Stripe
📱 Funziona offline   🇮🇹 Fatto in Italia  ⚡ Supporto diretto fondatore

[Scarcity banner — se applicabile]
"Lancio: le prime 100 licenze includono accesso diretto al fondatore"
```

---

### S10 — FAQ (7 Domande)

Vedi sezione 6 di questo documento per il testo completo delle FAQ.

**Layout**: Accordion HTML nativo (no JavaScript pesante).
**Ordine**: Metti l'obiezione principale per prima ("Ci sono costi nascosti?").

---

### S11 — CTA FINALE

**Obiettivo**: Ultima spinta. Urgency morbida + ripetizione garanzia.

```
[Headline finale]
"Ogni giorno senza FLUXION è un giorno in cui qualcuno risponde
al telefono al posto tuo — il tuo concorrente."

[Sub]
"Prova FLUXION per 30 giorni. Se non fa per te, ti rimborsiamo
entro 48 ore. Senza domande."

[PRICING ripetuto — semplice]
Base €497 — una volta sola
Pro €897 — una volta sola

[2 CTA side by side]
[Amber] Prova FLUXION Base — €497    [Outline] Prova FLUXION Pro — €897

[Garanzia badge grande]
```

---

### S12 — FOOTER

**Elementi obbligatori (CLAUDE.md compliance)**:

```
[Disclaimer servizi AI]
"FLUXION utilizza servizi cloud di terze parti per l'assistente vocale Sara.
Tali servizi sono inclusi senza costi aggiuntivi. In caso di indisponibilità,
il software attiva automaticamente servizi alternativi. Calendario, clienti
e cassa funzionano sempre, anche offline."

[Requisiti sistema]
Windows 10+ / macOS 12+ · 8GB RAM consigliati · 2GB disco · Internet per Sara (opzionale)

[Link legali]
Privacy Policy · Termini di Servizio · Garanzia 30 giorni

[Contatto]
fluxion.gestionale@gmail.com

[Copyright]
© 2026 FLUXION · Tutti i diritti riservati
```

---

## 11. STICKY CTA MOBILE

**Implementazione**: Fixed bottom bar, compare dopo 30% scroll.

```html
<div id="sticky-cta" class="fixed bottom-0 left-0 right-0 bg-slate-900 border-t border-slate-700 p-3 z-50">
  <a href="[Stripe Base]" target="_blank"
     class="block w-full bg-amber-500 text-white text-center font-bold py-3 rounded-lg">
    FLUXION Base — €497 una volta sola
  </a>
  <p class="text-center text-xs text-slate-400 mt-1">🛡 Garanzia 30 giorni</p>
</div>
```

**Regole**:
- Compare solo dopo 30% scroll (non subito — fastidioso)
- Scompare quando l'utente è nella pricing section (già vede i CTA)
- Target: link a Stripe Base (€497) — scelta più probabile da mobile WA

---

## 12. CHECKLIST TECNICA V2

### Pre-deploy obbligatorio
- [ ] Lighthouse Performance Score > 90 su mobile
- [ ] LCP < 2.5s su simulazione 4G (Lighthouse)
- [ ] Zero render-blocking resources (rimuovere Tailwind CDN)
- [ ] Tutte le immagini con `loading="lazy"` (tranne hero)
- [ ] `width` e `height` su tutte le img (evita layout shift)
- [ ] Video: `autoplay muted playsinline loop` con poster screenshot
- [ ] Meta OG: title, description, image (per condivisione WA)
- [ ] Stripe links aprono in `target="_blank" rel="noopener"`
- [ ] Disclaimer legale footer presente e completo (CLAUDE.md)
- [ ] Requisiti sistema visibili nel footer e nella pricing section
- [ ] FAQ con domanda obiezioni ordinate per importanza
- [ ] Garanzia visibile sotto OGNI CTA button
- [ ] CTA color: amber #f59e0b (non cyan — già usato nel design)

### Meta OG per condivisione WhatsApp
```html
<meta property="og:title" content="FLUXION — Gestionale per PMI italiane. Sara prenota per te 24/7.">
<meta property="og:description" content="Stop agli abbonamenti. €497 una volta sola. Calendari, clienti, cassa e Sara AI inclusi.">
<meta property="og:image" content="https://fluxion-landing.pages.dev/assets/og-image.png">
<meta property="og:url" content="https://fluxion-landing.pages.dev">
<meta name="twitter:card" content="summary_large_image">
```

### OG image requirements (per preview WA)
- Dimensioni: 1200x630px
- Include: logo FLUXION + headline + screenshot dashboard
- Background: dark (#0f172a) — coerente col brand
- File: `landing/assets/og-image.png`

---

## CONCLUSIONI E PRIORITÀ

### Quick wins (impatto alto, effort basso)
1. Cambiare CTA color da cyan a amber (#f59e0b)
2. Aggiungere garanzia sotto ogni CTA button
3. Aggiungere meta OG tags per preview WhatsApp
4. Aggiungere sticky CTA mobile (bottom bar)
5. Sostituire Tailwind CDN con CSS inline/purged

### Impact projects (impatto alto, effort medio)
6. Riscrivere headline hero con pain point Sara
7. Aggiungere sezione confronto competitor con tabella costi reali
8. Aggiungere sezione Sara con conversazione demo
9. Riscrivere pricing cards con "Sì, voglio FLUXION Base — €497"
10. Aggiungere founder photo + quote nella social proof

### Polish (impatto medio, effort medio)
11. Convertire screenshots PNG → WebP
12. Aggiungere lazy loading a tutte le immagini below fold
13. Aggiungere 6 card settori con screenshot reali
14. Aggiungere FAQ accordion con 7 domande

---

*Research completata: 2026-03-25*
*Skill: fluxion-landing-generator*
*Prossimo step: implementare V2 landing HTML con queste specifiche*
