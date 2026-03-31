# KB Settoriale: Barbiere, Gommista, Estetista/Nail — Research 2026

## 1. BARBIERE

### Servizi e Prezzi (EUR)
| Servizio | Prezzo | Durata | ID Seed |
|----------|--------|--------|---------|
| Taglio uomo classico | 18-22 | 25 min | srv-taglio-uomo |
| Taglio con sfumatura/fade | 20-25 | 30 min | srv-taglio-fade |
| Barba (taglio+rifinitura) | 10-15 | 15 min | srv-barba |
| Taglio + Barba combo | 25-32 | 40 min | srv-combo |
| Rasatura completa (rasoio) | 12-18 | 20 min | srv-rasatura |
| Shampoo | 5-8 | 10 min | srv-shampoo |
| Trattamento barba (olio/balsamo) | 15-20 | 20 min | srv-trattamento-barba |
| Colorazione uomo | 25-35 | 45 min | srv-colore-uomo |
| Taglio bambino (<12) | 10-15 | 20 min | srv-taglio-bambino |
| Taglio con disegno/design | 25-35 | 35 min | srv-taglio-design |

### Gergo Barbiere (NLU Keywords)
- **Tagli**: sfumatura, dissolvenza, fade, skin fade, high fade, low fade, mid fade, taper
- **Stili**: ciuffo, pompadour, undercut, mohawk, crew cut, buzz cut, mullet
- **Strumenti**: rasoio, lametta, clipper, macchinetta, forbici
- **Azioni**: regolazione, spuntata, rifinitura, sfoltire, scalatura
- **Barba**: modellatura, sagomatura, definizione, hot towel, vapore

### Orari Tipici
- **Classico**: Mar-Sab 08:30-12:30 / 15:00-19:30 (LUNEDÌ CHIUSO)
- **Moderno**: Lun-Sab 09:00-19:00 (orario continuato)
- **Picco**: Sabato (tutto il giorno), Venerdì pomeriggio

### FAQ Templates
1. "Quanto costa un taglio?" → "Un taglio uomo costa €[PREZZO_TAGLIO_UOMO]. Con sfumatura €[PREZZO_TAGLIO_FADE]"
2. "Fate anche la barba?" → "Certo! Barba €[PREZZO_BARBA], oppure combo taglio e barba €[PREZZO_COMBO]"
3. "Siete aperti il lunedì?" → "No, il lunedì siamo chiusi. Siamo aperti dal martedì al sabato"
4. "Bisogna prenotare?" → "Consigliamo di prenotare, soprattutto il sabato. Posso fissare un appuntamento?"
5. "Quanto tempo ci vuole per un taglio?" → "Un taglio classico circa 25 minuti, con sfumatura circa 30"
6. "Fate colorazioni uomo?" → "Sì, colorazione uomo a €[PREZZO_COLORE_UOMO], durata circa 45 minuti"
7. "Accettate carte?" → "Sì, accettiamo carte, contanti e Satispay"
8. "Tagliate anche i bambini?" → "Sì, taglio bambino (sotto 12 anni) €[PREZZO_TAGLIO_BAMBINO]"
9. "Avete prodotti in vendita?" → "Sì, cere, gel, oli per barba e prodotti professionali"
10. "Fate rasatura con rasoio?" → "Sì, rasatura tradizionale con rasoio €[PREZZO_RASATURA]"
11. "C'è parcheggio?" → "Sì, parcheggio gratuito nelle vicinanze / parcheggio convenzionato"
12. "Orari?" → "Siamo aperti [GIORNI_LAVORATIVI] dalle [ORARIO_APERTURA] alle [ORARIO_CHIUSURA]"
13. "Fate trattamenti barba?" → "Sì, trattamento con olio e balsamo €[PREZZO_TRATTAMENTO_BARBA]"

---

## 2. GOMMISTA

### Servizi e Prezzi (EUR)
| Servizio | Prezzo | Durata | ID Seed |
|----------|--------|--------|---------|
| Cambio gomme 4 ruote (smontaggio+montaggio+equilibratura) | 40-60 | 45 min | srv-cambio-gomme |
| Equilibratura 4 ruote | 20-30 | 20 min | srv-equilibratura |
| Convergenza (allineamento) | 40-60 | 30 min | srv-convergenza |
| Riparazione foratura | 15-25 | 20 min | srv-riparazione |
| Sostituzione valvola | 5-10 | 10 min | srv-valvola |
| Deposito stagionale (per set) | 20-40 | 15 min | srv-deposito |
| Controllo pressione | 0 (gratuito) | 5 min | srv-pressione |
| Sostituzione sensore TPMS | 30-50 | 15 min | srv-tpms |
| Montaggio gomme cliente | 30-40 | 30 min | srv-montaggio |
| Vendita pneumatici | variabile | - | srv-vendita-pneumatici |

### Pattern Stagionali
- **Cambio invernali**: 15 ottobre → 15 novembre (obbligo dal 15 nov, eccetto catene)
- **Cambio estive**: 15 marzo → 15 aprile (obbligo entro 15 apr)
- **PICCO ASSOLUTO**: ottobre-novembre e marzo-aprile
- **Sara deve**: proattivamente ricordare le scadenze ai clienti

### Gergo Gommista (NLU Keywords)
- **Pneumatici**: gomme, copertoni, pneumatici, cerchi, cerchioni
- **Tecnico**: battistrada, spalla, fianco, tallone
- **Servizi**: convergenza, campanatura, bilanciatura, equilibratura
- **Tipi**: invernali, estive, 4 stagioni, M+S (mud and snow), run-flat, tubeless
- **Misure**: 205/55 R16, DOT (data produzione)
- **Accessori**: catene da neve, calze da neve, TPMS

### Orari Tipici
- **Standard**: Lun-Ven 08:00-12:30 / 14:30-18:30, Sab 08:00-12:00
- **Picco**: chiusura posticipata in periodo cambio stagionale

### FAQ Templates
1. "Quanto costa il cambio gomme?" → "Cambio 4 ruote completo (smontaggio, montaggio, equilibratura) €[PREZZO_CAMBIO_GOMME]"
2. "Quando devo cambiare le gomme invernali?" → "L'obbligo parte dal 15 novembre. Consigliamo di prenotare per ottobre per evitare code"
3. "Fate deposito gomme?" → "Sì, custodia stagionale €[PREZZO_DEPOSITO] per set di 4 gomme"
4. "Quanto costa riparare una foratura?" → "Riparazione foratura €[PREZZO_RIPARAZIONE]"
5. "Come faccio a sapere se le gomme sono da cambiare?" → "Il battistrada deve essere almeno 1,6mm. Porti l'auto e verifichiamo gratuitamente"
6. "Vendete anche pneumatici?" → "Sì, tutte le marche principali. Mi dica la misura e le faccio un preventivo"
7. "Quanto tempo ci vuole per il cambio?" → "Circa 45 minuti per 4 ruote"
8. "Serve prenotare?" → "Consigliamo di prenotare, soprattutto a ottobre e marzo. Posso fissare?"
9. "Fate convergenza?" → "Sì, allineamento ruote €[PREZZO_CONVERGENZA]"
10. "Posso portare le gomme mie?" → "Certo, montaggio gomme cliente €[PREZZO_MONTAGGIO]"
11. "Fate anche equilibratura?" → "Sì, equilibratura 4 ruote €[PREZZO_EQUILIBRATURA]"
12. "Controllate la pressione?" → "Sì, il controllo pressione è gratuito"
13. "Fate anche moto/scooter?" → "Sì, anche pneumatici moto e scooter"

---

## 3. ESTETISTA / NAIL ARTIST

### Servizi e Prezzi (EUR)

**Depilazione:**
| Servizio | Prezzo | Durata | ID Seed |
|----------|--------|--------|---------|
| Ceretta gambe intere | 25-35 | 30 min | srv-ceretta-gambe |
| Ceretta mezza gamba | 15-20 | 20 min | srv-ceretta-mezza |
| Ceretta inguine/brasiliana | 25-35 | 20 min | srv-ceretta-inguine |
| Ceretta sopracciglia | 8-12 | 10 min | srv-ceretta-sopracciglia |
| Ceretta baffetti | 5-8 | 5 min | srv-ceretta-baffetti |
| Ceretta ascelle | 8-12 | 10 min | srv-ceretta-ascelle |

**Viso:**
| Servizio | Prezzo | Durata | ID Seed |
|----------|--------|--------|---------|
| Pulizia viso | 40-60 | 60 min | srv-pulizia-viso |
| Trattamento anti-age | 50-80 | 60 min | srv-anti-age |
| Trattamento acne | 40-60 | 45 min | srv-trattamento-acne |
| Peeling chimico | 50-70 | 45 min | srv-peeling |
| Microneedling | 80-120 | 60 min | srv-microneedling |

**Corpo:**
| Servizio | Prezzo | Durata | ID Seed |
|----------|--------|--------|---------|
| Massaggio rilassante 60min | 50-70 | 60 min | srv-massaggio-relax |
| Massaggio anticellulite | 45-65 | 45 min | srv-anticellulite |
| Pressoterapia | 30-45 | 40 min | srv-pressoterapia |
| Bendaggi | 40-60 | 50 min | srv-bendaggi |

**Nail:**
| Servizio | Prezzo | Durata | ID Seed |
|----------|--------|--------|---------|
| Manicure semplice | 15-20 | 30 min | srv-manicure |
| Manicure semipermanente | 25-35 | 45 min | srv-semi |
| Ricostruzione unghie gel | 40-55 | 75 min | srv-gel |
| Refill gel | 25-35 | 45 min | srv-refill |
| Pedicure curativo | 25-35 | 45 min | srv-pedicure |
| Pedicure estetico + semi | 35-45 | 60 min | srv-pedicure-semi |
| Nail art (per unghia) | 2-5 | +5 min | srv-nail-art |
| Rimozione semi/gel | 10-15 | 20 min | srv-rimozione |
| French manicure | 30-40 | 50 min | srv-french |
| Baby boomer | 35-45 | 55 min | srv-baby-boomer |

### Gergo Estetista/Nail (NLU Keywords)
- **Nail**: semi, semipermanente, gel, ricostruzione, refill, french, baby boomer, nail art
- **Depilazione**: brasiliana, totale, integrale, parziale, ceretta, cera a caldo, cera a freddo
- **Viso**: anti-age, lifting, ringiovanimento, pulizia profonda, punti neri, comedoni
- **Corpo**: cellulite, linfodrenaggio, pressoterapia, rassodamento, tonificazione

### Orari Tipici
- **Standard**: Lun-Ven 09:00-13:00 / 14:30-19:00, Sab 09:00-13:00
- **Picco**: Venerdì e Sabato (pre-weekend), periodi pre-feste

### FAQ Templates
1. "Quanto costa la ceretta gambe?" → "Gambe intere €[PREZZO_CERETTA_GAMBE], mezza gamba €[PREZZO_CERETTA_MEZZA]"
2. "Quanto dura il semipermanente?" → "Lo smalto semipermanente dura circa 2-3 settimane"
3. "Ogni quanto devo fare il refill?" → "Il refill gel si consiglia ogni 3-4 settimane"
4. "Fate unghie in gel?" → "Sì, ricostruzione gel €[PREZZO_GEL], refill €[PREZZO_REFILL]"
5. "Quanto costa la pulizia viso?" → "Pulizia viso professionale €[PREZZO_PULIZIA_VISO], durata circa 60 minuti"
6. "Avete trattamenti anticellulite?" → "Sì, massaggio anticellulite €[PREZZO_ANTICELLULITE] e pressoterapia €[PREZZO_PRESSOTERAPIA]"
7. "Quanto tempo per una manicure?" → "Manicure semplice 30 minuti, con semipermanente circa 45 minuti"
8. "Posso venire con smalto già applicato?" → "Sì, la rimozione è inclusa nel servizio. Se solo rimozione: €[PREZZO_RIMOZIONE]"
9. "Fate depilazione uomo?" → "Sì, depilazione anche per uomo. Mi dica la zona e le dico il prezzo"
10. "Quali prodotti usate?" → "Utilizziamo solo prodotti professionali certificati"
11. "Fate nail art personalizzata?" → "Sì, nail art a partire da €[PREZZO_NAIL_ART] per unghia"
12. "La ceretta fa male?" → "Usiamo cere a bassa temperatura per minimizzare il fastidio"
13. "Offrite pacchetti?" → "Sì, abbiamo pacchetti con diversi trattamenti a prezzo scontato"
14. "Serve prenotare?" → "Sì, consigliamo di prenotare per garantire il posto. Posso fissare?"
15. "Fate trattamenti in gravidanza?" → "Sì, abbiamo trattamenti specifici sicuri in gravidanza. Ci avvisi così usiamo i prodotti adatti"
16. "Quanto costa la french manicure?" → "French manicure €[PREZZO_FRENCH], baby boomer €[PREZZO_BABY_BOOMER]"
