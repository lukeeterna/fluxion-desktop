# KB Settoriale: Fisioterapista, Odontoiatra, Palestra — Research 2026

## 1. FISIOTERAPISTA

### Servizi e Prezzi (EUR)
| Servizio | Prezzo | Durata | ID Seed |
|----------|--------|--------|---------|
| Prima visita fisioterapica | 60-80 | 45 min | srv-prima-visita |
| Seduta fisioterapia (45min) | 45-60 | 45 min | srv-fisioterapia-45 |
| Seduta fisioterapia (60min) | 55-70 | 60 min | srv-fisioterapia-60 |
| Terapia manuale | 50-65 | 45 min | srv-terapia-manuale |
| Tecarterapia | 35-50 | 30 min | srv-tecar |
| Onde d'urto | 50-80 | 20 min | srv-onde-urto |
| Laser terapia | 30-45 | 20 min | srv-laser |
| Massoterapia | 40-55 | 50 min | srv-massoterapia |
| Riabilitazione post-operatoria | 50-70 | 60 min | srv-riabilitazione |
| Rieducazione posturale | 50-65 | 60 min | srv-posturale |
| Linfodrenaggio manuale | 50-70 | 60 min | srv-linfodrenaggio |
| Kinesiotaping | 15-25 | 15 min | srv-kinesio |
| Ginnastica correttiva | 40-55 | 45 min | srv-correttiva |
| Valutazione posturale | 40-60 | 45 min | srv-valutazione |

### Terminologia Medica Pazienti (NLU Keywords)
- **Condizioni**: cervicale, cervicalgia, lombalgia, mal di schiena, sciatica, ernia, protrusione
- **Patologie**: tendinite, borsite, distorsione, stiramento, contrattura, epicondilite, tunnel carpale
- **Anatomia**: spalla, ginocchio, anca, caviglia, polso, gomito, colonna vertebrale
- **Azioni**: riabilitazione, recupero, rieducazione, rinforzo, stretching, mobilizzazione

### Prescrizione e SSN
- **Privato**: NON serve prescrizione medica
- **SSN/ASL**: serve prescrizione del medico di base
- **Detrazione**: 19% nella dichiarazione dei redditi (spese sanitarie)
- **Assicurazioni**: molti studi convenzionati con fondi sanitari

### Orari Tipici
- **Standard**: Lun-Ven 08:00-13:00 / 14:30-19:30
- **Sabato**: 08:00-13:00 (non tutti)
- **Note**: sedute ogni 30-60 min, cicli di 6-10 sedute

### FAQ Templates
1. "Quanto costa una seduta?" → "Una seduta di fisioterapia costa €[PREZZO_FISIOTERAPIA_45] (45 min) o €[PREZZO_FISIOTERAPIA_60] (60 min). La prima visita è €[PREZZO_PRIMA_VISITA]"
2. "Serve la prescrizione medica?" → "Per il percorso privato non serve prescrizione. Per accesso tramite SSN serve la prescrizione del medico"
3. "Quante sedute servono?" → "Dipende dalla condizione. Mediamente un ciclo è di 6-10 sedute. Dopo la prima visita il dottore le darà un piano personalizzato"
4. "La fisioterapia è detraibile?" → "Sì, le spese sono detraibili al 19% nella dichiarazione dei redditi"
5. "Fate tecarterapia?" → "Sì, tecarterapia €[PREZZO_TECAR] per seduta"
6. "Trattate il mal di schiena?" → "Certamente, è una delle condizioni che trattiamo più frequentemente"
7. "Fate riabilitazione post-operatoria?" → "Sì, riabilitazione post-chirurgica €[PREZZO_RIABILITAZIONE] per seduta"
8. "Quanto dura una seduta?" → "Le sedute durano 45 o 60 minuti, a seconda del trattamento"
9. "Accettate convenzioni?" → "Sì, siamo convenzionati con diversi fondi sanitari. Ci dica il suo fondo e verifichiamo"
10. "Cosa devo portare alla prima visita?" → "Eventuale prescrizione medica, referti di esami (RX, risonanza), e abbigliamento comodo"
11. "Fate anche massaggi?" → "Sì, massoterapia €[PREZZO_MASSOTERAPIA], 50 minuti"
12. "Trattate anche bambini?" → "Sì, trattiamo anche pazienti in età pediatrica"
13. "Fate onde d'urto?" → "Sì, terapia con onde d'urto €[PREZZO_ONDE_URTO]"
14. "Ho la cervicale, potete aiutarmi?" → "Certamente, la cervicalgia è una condizione molto comune. La prima visita serve a valutare il trattamento migliore"

---

## 2. ODONTOIATRA / DENTISTA

### Servizi e Prezzi (EUR)
| Servizio | Prezzo | Durata | ID Seed |
|----------|--------|--------|---------|
| Prima visita odontoiatrica | 50-80 | 30 min | srv-prima-visita |
| Pulizia denti (igiene) | 60-90 | 45 min | srv-pulizia-denti |
| Otturazione (per dente) | 70-100 | 30 min | srv-otturazione |
| Devitalizzazione mono | 150-250 | 60 min | srv-devitalizzazione |
| Devitalizzazione pluri | 250-400 | 90 min | srv-devitalizzazione-pluri |
| Estrazione semplice | 80-120 | 30 min | srv-estrazione |
| Estrazione dente giudizio | 150-250 | 45 min | srv-estrazione-giudizio |
| Impianto singolo (corona incl.) | 1200-2500 | 90 min | srv-impianto |
| Sbiancamento professionale | 200-350 | 60 min | srv-sbiancamento |
| Panoramica (OPT) | 30-50 | 10 min | srv-panoramica |
| Corona/Capsula | 400-800 | 60 min | srv-corona |
| Faccetta estetica | 500-800 | 60 min | srv-faccetta |
| Bite notturno | 200-400 | 30 min | srv-bite |
| Sigillatura (bambini) | 30-50 | 15 min | srv-sigillatura |

### Gestione Urgenze
- Pattern: "mal di denti", "urgente", "emergenza", "dente rotto", "dolore forte"
- Sara risponde: "Abbiamo disponibilità per urgenze. Verifico subito il primo slot libero oggi"
- NON dare consigli medici, solo proporre appuntamento urgente

### Gergo Dentistico (NLU Keywords)
- **Igiene**: pulizia, detartrasi, ablazione tartaro, igiene orale
- **Restauro**: otturazione, piombatura (vecchio), composito, ceramica
- **Endodonzia**: devitalizzazione, cura canalare, canale radicolare
- **Chirurgia**: estrazione, avulsione, dente del giudizio, ottavo
- **Protesi**: corona, capsula, ponte, protesi fissa, protesi mobile
- **Estetica**: sbiancamento, bleaching, faccette, veneers
- **Ortodonzia**: apparecchio, brackets, allineatori, invisalign, bite
- **Diagnostica**: panoramica, OPT, radiografia, TAC dentale, CBCT
- **Patologie**: carie, gengivite, parodontite, tartaro, ascesso

### Orari Tipici
- **Standard**: Lun-Ven 09:00-13:00 / 14:00-19:00
- **Sabato**: 09:00-13:00 (non tutti)
- **Urgenze**: slot riservati ogni giorno

### FAQ Templates
1. "Quanto costa la pulizia dei denti?" → "L'igiene orale professionale costa €[PREZZO_PULIZIA_DENTI], durata circa 45 minuti"
2. "Ho mal di denti, potete ricevermi oggi?" → "Certamente, verifico subito la disponibilità per un'urgenza. Posso chiederle il nome?"
3. "Quanto costa un'otturazione?" → "Un'otturazione in composito estetico costa €[PREZZO_OTTURAZIONE]"
4. "Fate sbiancamento?" → "Sì, sbiancamento professionale €[PREZZO_SBIANCAMENTO], risultati visibili in una seduta"
5. "Quanto costa un impianto?" → "L'impianto singolo con corona inclusa parte da €[PREZZO_IMPIANTO]. Serve una prima visita per il preventivo personalizzato"
6. "Ogni quanto devo fare la pulizia?" → "Si consiglia ogni 6 mesi per una bocca sana"
7. "La pulizia dei denti fa male?" → "Può esserci un leggero fastidio, ma utilizziamo tecniche delicate per minimizzarlo"
8. "Accettate pagamento a rate?" → "Sì, offriamo piani di pagamento personalizzati senza interessi"
9. "Fate anche ortodonzia?" → "Sì, sia apparecchi tradizionali che allineatori trasparenti"
10. "I bambini da che età possono venire?" → "Consigliamo la prima visita dai 3-4 anni per un controllo preventivo"
11. "Quanto dura la pulizia?" → "Circa 45 minuti"
12. "Si può fare lo sbiancamento in gravidanza?" → "Si consiglia di attendere dopo il parto per precauzione"
13. "Fate panoramica digitale?" → "Sì, panoramica digitale €[PREZZO_PANORAMICA], risultato immediato"
14. "Che materiali usate per le otturazioni?" → "Utilizziamo compositi estetici di ultima generazione, dello stesso colore del dente"
15. "Il dente del giudizio va tolto?" → "Dipende dalla posizione. Con una visita e una panoramica valutiamo se è necessario"

---

## 3. PALESTRA / FITNESS — Gap Analysis

### Prezzi Seed Esistente (CONFERMATI market-accurate 2026)
- Abbonamento mensile: €49 ✓
- Trimestrale: €129 ✓
- Annuale: €449 ✓
- Personal Training singola: €45 ✓
- PT coppia: €70 ✓
- Corsi gruppo: €10-12 ✓
- Ingresso singolo: €12 ✓
- Massaggio sportivo: €50 ✓
- Sauna + bagno turco: €15 ✓

### FAQ Mancanti (da aggiungere a faq_palestra.json)
1. "Posso sospendere l'abbonamento?" → "È possibile sospendere per motivi medici con certificato, fino a 30 giorni"
2. "Cosa serve per iniziare?" → "Solo abbigliamento sportivo e scarpe da ginnastica pulite. Il primo giorno includiamo una valutazione gratuita"
3. "Conviene il mensile o l'annuale?" → "L'annuale conviene: €449 invece di €588 (12 mesi), risparmi €139"
4. "Ci sono docce e spogliatoi?" → "Sì, spogliatoi con docce calde, armadietti con chiave e asciugamani disponibili"
5. "Posso portare un amico a provare?" → "Certo! La prima prova è gratuita e senza impegno"
6. "C'è parcheggio?" → "Sì, parcheggio gratuito/convenzionato nelle vicinanze"
7. "Fate anche nuoto libero?" → "Sì, la piscina è accessibile con l'abbonamento. Serve cuffia e costume"
8. "A che ora è meno affollato?" → "Le ore meno affollate sono 10:00-12:00 e 14:00-16:00. La sera 18:00-20:00 è il picco"

### NLU Keywords Palestra
- **Abbonamenti**: iscrizione, tessera, abbonamento, mensile, trimestrale, annuale
- **Servizi**: personal trainer, PT, scheda, programma, valutazione
- **Corsi**: yoga, pilates, spinning, zumba, crossfit, acquagym, nuoto
- **Strutture**: sala pesi, piscina, sauna, bagno turco, spogliatoi
- **Obiettivi**: dimagrire, tonificare, massa muscolare, definizione, preparazione atletica
