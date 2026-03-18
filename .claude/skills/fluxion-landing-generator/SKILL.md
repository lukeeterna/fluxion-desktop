# Skill: FLUXION Landing Page Generator — Enterprise Grade

> Research-driven landing page creation for Italian PMI market.
> Every section backed by conversion optimization research (Unbounce, HubSpot, ConvertKit benchmarks).

## Purpose

Generate a complete, conversion-optimized landing page for FLUXION that:
- Speaks the language of Italian SMB owners (NO technical jargon)
- Shows real screenshots of every feature
- Includes concrete examples per business category (NOT "verticali")
- Has clear pricing, FAQ, and trust signals
- Converts visitors → LemonSqueezy checkout

## Audience: Italian PMI Owners

**Who they are:**
- Titolari di saloni, palestre, studi medici, officine, centri estetici
- Età 30-55, tecnologicamente nella media
- Frustrati da software complicati, abbonamenti costosi, gestione carta
- Vogliono: semplicità, risparmio tempo, zero costi mensili

**Language rules (NON NEGOZIABILE):**
- MAI dire "verticali" → dire "il tuo settore" o "la tua attività"
- MAI dire "NLU", "FSM", "LLM" → dire "intelligenza artificiale" o "Sara capisce..."
- MAI dire "pipeline", "sidecar", "backend" → dire "funziona automaticamente"
- MAI dire "deployment" → dire "installazione"
- SEMPRE usare "tu" (informale ma rispettoso)
- Esempi CONCRETI: "Maria del salone in via Roma", "Dr. Rossi dello studio dentistico"

## Landing Structure (12 sections)

### 1. HERO
- Headline: benefit principale (risparmio tempo + zero costi mensili)
- Sub-headline: per chi è (titolari PMI italiane)
- CTA primario: "Prova Gratis" o "Guarda Come Funziona"
- Hero image: dashboard screenshot con dati reali

### 2. PAIN POINTS (Il problema)
- 3 problemi comuni dei titolari PMI
- Agendine di carta, clienti che non si presentano, software costosi
- Empatia, non tecnicismi

### 3. SOLUZIONE (Come Fluxion risolve)
- 3 pilastri: Comunicazione + Marketing + Gestione
- Un paragrafo per pilastro, linguaggio semplice
- Screenshot per ogni pilastro

### 4. FUNZIONALITÀ (con screenshot reali)
Per OGNI funzione:
- Titolo benefit-oriented (non feature-oriented)
- 2-3 righe di spiegazione per titolari non tecnici
- Screenshot reale dalla app
- Esempio concreto per un settore specifico

Funzionalità da mostrare:
1. **Calendario** — "Mai più doppie prenotazioni"
2. **Clienti** — "Ogni cliente ha la sua scheda personale"
3. **Sara AI** — "Un'assistente che risponde 24 ore su 24"
4. **WhatsApp** — "Conferme e promemoria automatici"
5. **Fatture** — "Fatturazione elettronica in un click"
6. **Cassa** — "Incassi sempre sotto controllo"
7. **Team** — "Gestisci il tuo staff senza fogli Excel"
8. **Statistiche** — "Scopri cosa funziona nella tua attività"
9. **Fornitori** — "Ordini e scadenze, tutto in ordine"

### 5. SARA (sezione dedicata)
- Come funziona (linguaggio semplice)
- Esempio conversazione reale
- "Inclusa nella licenza, zero costi aggiuntivi"

### 6. PER CHI È (settori con esempi)
NON dire "verticali". Mostrare:
- **Saloni e barbieri** — esempio concreto
- **Centri estetici e spa** — esempio concreto
- **Studi medici e dentistici** — esempio concreto
- **Palestre e centri fitness** — esempio concreto
- **Officine e carrozzerie** — esempio concreto
- **Studi professionali** — esempio concreto

Ogni settore: icona + 3 righe + "Scopri come Fluxion aiuta [settore]"

### 7. CONFRONTO
Tabella: Fluxion vs Fresha vs altri
- Costo mensile: €0 vs €XX/mese
- Commissioni: 0% vs 2-5%
- Sara AI: Inclusa vs Non disponibile
- Offline: Sì vs No
- Dati tuoi: 100% vs Cloud terzi

### 8. PREZZI
3 card chiare:
- Base €497 — per chi inizia
- Pro €897 — per chi vuole Sara + WhatsApp
- Clinic €1.497 — per studi medici multi-sede
"Una volta. Per sempre. Zero abbonamenti."

### 9. TESTIMONIANZE / SOCIAL PROOF
- Se non ci sono ancora: "Unisciti ai primi 100 titolari che stanno cambiando il modo di gestire la loro attività"
- Badge: "Soddisfatti o rimborsati 30 giorni"
- Trust: "I tuoi dati restano sul TUO computer"

### 10. FAQ
10 domande reali che un titolare farebbe:
- "Funziona senza internet?"
- "Posso trasferire i dati dal mio gestionale attuale?"
- "Ho bisogno di un tecnico per installarlo?"
- etc.

### 11. CTA FINALE
- Headline urgency (soft, non aggressivo)
- Ripeti prezzi
- CTA: link LemonSqueezy diretto

### 12. FOOTER
- Link legali, privacy, contatti
- Disclaimer servizi AI (come da CLAUDE.md)

## Technology

- HTML + Tailwind CSS (file unico, self-contained)
- Dark mode responsive (ma desktop-first — app è desktop)
- Immagini: `landing/screenshots/*.png`
- Hosting: Cloudflare Pages (già configurato: fluxion-landing.pages.dev)

## Quality Checks

Before publishing:
1. Lighthouse score > 90 (performance, accessibility, SEO)
2. Zero errori grammaticali/ortografici italiani
3. Tutti i link LemonSqueezy funzionanti
4. Tutte le immagini presenti e caricate
5. Mobile responsive (anche se app è desktop, landing si vede da mobile)
6. Meta tags OpenGraph per condivisione social
7. Schema.org markup per SEO

## Trigger

- User asks for "landing", "pagina vendita", "sito web"
- User invokes `/landing-generator`
- After screenshot capture completes
