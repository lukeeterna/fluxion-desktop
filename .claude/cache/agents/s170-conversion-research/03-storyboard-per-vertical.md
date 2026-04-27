# FLUXION — Storyboard & Conversion Analysis per Verticale
## Sessione S170 | Analisi 9 Video Verticali | Visual Storyteller

---

## DIAGNOSTICA PRELIMINARE — Il Gap Strutturale

Prima di analizzare ogni verticale, il problema sistemico che riguarda TUTTI i 9 video:

### Copione vs Realtà

| Verticale       | VO (s) | Final (s) | Excess (s) | VO Bloat vs 30s target | Verdict rapido |
|-----------------|--------|-----------|------------|------------------------|----------------|
| parrucchiere    | 40.4   | 74.7      | 34.3       | +10.4s (35% oltre)     | REWORK         |
| barbiere        | 25.0   | 58.9      | 34.0       | -5.0s (dentro range)   | REWORK         |
| officina        | 26.9   | 60.9      | 34.0       | -3.1s (dentro range)   | REWORK         |
| carrozzeria     | 26.0   | 60.0      | 34.0       | -4.0s (dentro range)   | REWORK         |
| dentista        | 45.5   | 79.7      | 34.2       | +15.5s (52% oltre)     | REPLACE VO     |
| centro_estetico | 47.2   | 81.4      | 34.3       | +17.2s (57% oltre)     | REPLACE VO     |
| nail_artist     | 42.0   | 76.2      | 34.2       | +12.0s (40% oltre)     | REPLACE VO     |
| palestra        | 26.9   | 60.8      | 34.0       | -3.1s (dentro range)   | REWORK         |
| fisioterapista  | 26.8   | 60.8      | 34.0       | -3.2s (dentro range)   | REWORK         |

**Perché il final dura sempre ~34s in PIU del voiceover?**
La struttura assembly `assemble_all.py` inserisce 5 screenshot statici tra clip1 e clip3. Con VO "corto" (25-27s), le immagini sono timed ai segmenti audio: clip1 8s + seg_1 + screenshots + seg_2 + screenshots + clip3 8s + CTA. Ma quando il VO è lungo (40-47s), i segmenti si allungano proporzionalmente e il video totale esplode a 75-81s.

**Regola di riassemblaggio:**
- VO target massimo: 26-28s (stile barbiere/officina/palestra — questi sono CORRETTI)
- Final target: 58-62s (3 clip x 8s + 5 screenshot x ~2s + VO 27s + transizioni)
- Oppure tagliare anche il visual: 3 clip x 6s + 3 screenshot x 3s + VO 28s = target ~55s
- **IDEALE per conversione**: VO 26s + minimal visuals = final 50-55s massimo

**I 4 video BLOATED (parrucchiere, dentista, centro_estetico, nail_artist) vanno riscritti con VO più corto. Il copione è eccellente — va solo COMPRESSO.**

---

## EXECUTIVE SUMMARY — Verdetti

| # | Verticale       | Verdict     | Priorità | Motivo principale                                    |
|---|-----------------|-------------|----------|------------------------------------------------------|
| 1 | Parrucchiere    | REWORK      | P1       | VO 40s vs target 26s. Taglia seg_1 e seg_2.          |
| 2 | Barbiere        | REWORK      | P3       | VO OK ma hook 0-3s generico. Nuovo hook Isabella.    |
| 3 | Officina        | REWORK      | P2       | VO OK. Hook da rafforzare. Dato €13k/anno manca.     |
| 4 | Carrozzeria     | KEEP        | P4       | VO ok, struttura corretta, dato ANIA forte.          |
| 5 | Dentista        | REPLACE VO  | P1       | VO 45s, seg_1 18.7s è insostenibile. Riscrivere.     |
| 6 | Centro Estetico | REPLACE VO  | P1       | VO 47s, il peggior bloat. €22.500 è il killer-arg.   |
| 7 | Nail Artist     | REPLACE VO  | P2       | VO 42s. Il concept è forte, VO va compresso.         |
| 8 | Palestra        | REWORK      | P3       | VO ok. Hook gennaio/aprile è visivo ma serve punch.  |
| 9 | Fisioterapista  | KEEP        | P4       | VO ok. Struttura clinica è corretta per il settore.  |

**KEEP = nessuna azione urgente | REWORK = rimontaggio FFmpeg + nuovo seg audio | REPLACE VO = riscrivere e rigenerare voiceover Edge-TTS**

---

## 1. PARRUCCHIERE

### A. Pain primario + trigger psicologico

Il titolare parrucchiere 50enne italiano ha un pain specifico che non è "le chiamate perse" in astratto — è **il colore preparato per niente**. Ha comprato il prodotto, ha speso 10 minuti a misurare la miscela, e il cliente non si è presentato. Soldi buttati + tempo perso + il profumo acre del colore che scorre via. Questo è fisico, olfattivo, reale.

Il trigger psicologico secondario è **Treatwell come nemico interno**: il fornitore che ti ha "aiutato" a trovare clienti ma ora prende il 25% ogni volta. Non è un competitor esterno — è qualcuno che gli sta in casa.

Profilo titolare: 45-55 anni, lavora da solo o con 1-2 dipendenti, ha l'agenda cartacea, non risponde mai al telefono mentre ha le mani occupate. Diffidente verso la tecnologia MA capisce immediatamente il risparmio economico quando è espresso in numeri concreti.

### B. Storyboard ideale 30s

```
0:00-0:03  HOOK (pattern interrupt)
           VISIVO: Close-up estremo — mano con guanto nero che versa
                   miscela colore rossastra nel lavandino. SLOW MOTION.
                   Gocce che cadono. Dissolvenza acqua rossa.
           AUDIO:  SILENZIO totale per 2.5s. Poi Isabella, voce bassa:
                   "Ottanta euro. Nel lavandino."

0:03-0:10  PAIN AGITATION
           VISIVO: Agenda cartacea. Primo piano. Tre nomi con croce rossa.
                   Telefono sul bancone — vibra una volta, due, tre.
                   La mano del parrucchiere con pennello in mano non si muove.
           AUDIO:  Isabella: "Ventotto clienti su cento non si presentano.
                   Venticinque percento a Treatwell sui nuovi.
                   Ogni. Singolo. Giorno."

0:10-0:22  SOLUZIONE (show, non tell)
           VISIVO: Screenshot 02-calendario.png con appuntamenti confermati.
                   Screenshot 12-scheda-parrucchiere.png — formula colore visibile.
                   Notifica WhatsApp: "Sara ha confermato 3 appuntamenti."
                   Stessa parrucchiera, ora serena, pennello in mano.
           AUDIO:  Isabella: "Con FLUXION, Sara risponde. Conosce la formula
                   di ogni cliente. Manda il promemoria. Il cliente si ricorda.
                   Zero Treatwell."

0:22-0:30  CTA
           VISIVO: Frame nero. Testo bianco: FLUXION
                   Sotto: €497 una volta.
                   Sotto: Treatwell: €4.320 in 3 anni + commissioni
                   Sotto: fluxion-landing.pages.dev
           AUDIO:  Isabella, lenta, senza musica:
                   "FLUXION. Quattrocentonovantasette euro. Una volta. Per sempre."
```

### C. Comparazione copione attuale

Il copione v2 è **eccellente concettualmente** ma verboso nell'esecuzione. I problemi sono nel seg_1 (14.9s) e nel seg_2 (18.1s):

- `seg_1` include la frase "Ogni. Singolo. Giorno." ma prima di arrivarci passa per tre concetti separati (no-show, colore, Treatwell). Per 30s, bisogna scegliere UNO dei tre.
- `seg_2` descrive troppo: "Conosce la formula colore di ogni cliente, il patch test, le allergie" — questo è copy da landing page, non da video 30s.
- Il hook 0-8s nel video reale è clip1 (mani in capelli) — non c'è il pattern interrupt del colore nel lavandino.

Gap principale: il video inizia con una scena generica di salone invece di aprire con il momento di dolore specifico (colore buttato / telefono perso).

### D. Verdict: REWORK

Mantenere le clip Veo3 esistenti. Riscrivere e rigenerare VO con Edge-TTS a 26s max. Non serve girare nulla di nuovo.

**Azione concreta:**
1. Riscrivere `seg_1.mp3`: max 8s — taglia a "Ventotto su cento non si presentano. Colore buttato. Treatwell prende il venticinque percento."
2. Riscrivere `seg_2.mp3`: max 11s — taglia a "Con FLUXION, Sara risponde. Il promemoria parte. Il cliente si ricorda. Zero Treatwell."
3. `seg_3.mp3` è già a 7.7s — OK, non toccare.
4. Rimontare con `assemble_all.py --vertical parrucchiere` usando nuovi segment audio.

### E. Hook alternativi 0-3s

1. **Hook colore**: (immagine/clip) Mano con guanto versa colore nel lavandino. Voce: "Ottanta euro. Nel lavandino." — massimo impatto fisico/economico
2. **Hook numerico**: (frame testo su nero) "28 clienti su 100 oggi non si sono presentati." — dato immediato, verifica istantanea
3. **Hook agenda**: (close-up agenda) Tre croci rosse in fila sulla pagina di oggi. Telefono che vibra sul bancone, ignorato. Silenzio. — cinematico, nessuna voce per 3s

**Raccomandazione**: Hook 1 (colore nel lavandino). Il dato numerico arriva dopo. L'immagine olfattiva è il pattern interrupt.

### F. CTA 24-30s

```
VISIVO: Nero assoluto.
Riga 1 (bold, bianco): FLUXION
Riga 2 (regular, bianco): €497 una volta. Per sempre.
Riga 3 (small, rosso #FF4040): Treatwell: €4.320 in 3 anni + commissioni
Riga 4 (teal #50C3D7): fluxion-landing.pages.dev

AUDIO: "FLUXION. Quattrocentonovantasette euro. Una volta. Per sempre."
Isabella, voce chiara, nessuna musica. Pausa 0.5s dopo "FLUXION".
```

Coerenza WA: Il template WA dice "Treatwell prende il 25% su ogni cliente nuovo. Noi zero. €497 una volta." — il video DEVE citare Treatwell esplicitamente nella CTA (lo fa già, OK).

---

## 2. BARBIERE

### A. Pain primario + trigger psicologico

Il barbiere 50enne ha un pain diverso dal parrucchiere: **la concorrenza fisica nel quartiere**. Non è astratta — è letteralmente "il barbiere dall'altra parte della strada". Ha visto aprire 2-3 nuovi negozi negli ultimi 3 anni (+40% mercato) e sente la pressione. Ogni chiamata persa è un cliente che prova il nuovo. Non tornerà.

Il trigger psicologico è **la fedeltà dei clienti percepita come proprietà personale**: il barbiere tradizionale crede che "i miei clienti sono fedeli, vengono da me da 15 anni". Il video deve incrinare questa certezza dolcemente — non con paura, ma con un dato di realtà: la fedeltà si mantiene con il servizio, e il servizio inizia dalla risposta al telefono.

Fisica impossibilità di rispondere: il rasoio a mano libera sulla nuca è il simbolo perfetto. Non è pigrizia — è sicurezza del cliente.

### B. Storyboard ideale 30s

```
0:00-0:03  HOOK
           VISIVO: Rasoio a mano libera aperto, lama lucida in piena luce.
                   La nuca del cliente. Il telefono vibra sul bancone.
                   Il barbiere: immobile. Non si muove.
           AUDIO:  SILENZIO. 3 vibrazioni fisiche. Silenzio. Isabella:
                   "Chiamata persa."

0:03-0:10  PAIN AGITATION
           VISIVO: Fuori dalla vetrina, un'insegna nuova: "NEW BARBERSHOP"
                   La poltrona accanto: vuota. Mantella sul bracciolo.
           AUDIO:  Isabella: "In Italia le barberie sono cresciute del
                   quaranta percento. La concorrenza è tre porte più in là.
                   Ogni chiamata persa è un cliente regalato."

0:10-0:22  SOLUZIONE
           VISIVO: Screenshot 02-calendario.png — appuntamenti pieni.
                   Screenshot 12-scheda-parrucchiere.png — storico cliente.
                   Notifica silenziosa: "Sara: Giovanni confermato 10:30."
                   Barbiere concentrato, rasoio in mano, specchio pieno.
           AUDIO:  Isabella: "Con FLUXION, Sara risponde mentre hai il
                   rasoio in mano. I tuoi clienti restano tuoi.
                   Zero abbonamenti. Zero commissioni."

0:22-0:30  CTA
           VISIVO: Nero. FLUXION / €497 una volta / Competitor: €4.320 in 3 anni
                   / fluxion-landing.pages.dev
           AUDIO:  "FLUXION. Quattrocentonovantasette euro. Una volta. Per sempre."
```

### C. Comparazione copione attuale

Il copione barbiere ha il VO più corto di tutti (25s) — è già nel range target. I clip Veo3 esistenti (6 clip: clip1_v1, clip1_v2, clip2_v1, clip2_v2, clip3_v1, clip3_v2) coprono bene le scene descritte.

Gap principale: il VO attuale non include il dato della concorrenza nel hook — lo dice nel seg_1 ma dopo 3s di silenzio. La prima frase vocale potrebbe essere più d'impatto.

Il video dura 58.9s — 5s sopra il range ideale 50-55s. Riducibile togliendo 1 screenshot dalla sequenza.

### D. Verdict: REWORK (lieve)

Il barbiere è il video migliore del lotto. Richiede solo:
1. Tagliare 1 screenshot dalla sequenza (da 5 a 4) per portarlo a ~55s
2. Rafforzare il primissimo momento del hook con la vibrazione del telefono

### E. Hook alternativi 0-3s

1. **Hook rasoio + silenzio**: Rasoio aperto sulla nuca. Telefono vibra. Silenzio. "Chiamata persa." — attuale, funziona
2. **Hook numerico + location**: Testo su nero: "+40% di barberie in 5 anni nel tuo quartiere." Fade in vetrina salone. — cognitivo, forte per chi già sente la pressione
3. **Hook sfida**: Isabella subito: "Hai il rasoio in mano. Il telefono squilla. Cosa fai?" — coinvolge direttamente il titolare

**Raccomandazione**: Hook 1 (attuale) è corretto ma va rallentato — 3 vibrazioni con pausa, poi "Chiamata persa." in voce bassa. Più cinematico.

### F. CTA 24-30s

```
VISIVO: Nero assoluto.
FLUXION
€497 una volta. Per sempre.
Competitor: €4.320 in 3 anni (rosso)
fluxion-landing.pages.dev (teal)

AUDIO: Standard Isabella senza musica.
```

Coerenza WA: Template WA parla di "chiamate perse" e "concorrenza nel quartiere" — allineato con il video. OK.

---

## 3. OFFICINA MECCANICA

### A. Pain primario + trigger psicologico

Il meccanico 50enne ha il pain più **quantificabile** di tutti: **€13.000/anno di lavoro non fatturato**. Non è una sensazione — è un calcolo (1h/giorno × €50/h × 260 giorni). Ma lui non lo sa ancora. Il video deve fargli fare questo calcolo mentale in tempo reale.

Il trigger psicologico è la **frustrazione accumulata**: risponde 13 volte al giorno a "è pronta la mia auto?". È una domanda che lo interrompe nel mezzo di un lavoro delicato, che gli sporca il telefono con le mani unte, che lui ha già risposto ieri. È ripetizione irritante, non dolore acuto.

### B. Storyboard ideale 30s

```
0:00-0:03  HOOK
           VISIVO: Mani sporche di grasso nero. Telefono sul bancone.
                   Screen del telefono: "13 chiamate perse."
                   Mani che si puliscono sullo straccio blu.
           AUDIO:  Isabella: "Tredici. Chiamate. Perse."
                   (pausa 0.5s tra ogni parola)

0:03-0:10  PAIN AGITATION
           VISIVO: Foglio con lista telefonate scritta a mano. 
                   Poi: calcolatrice. Poi: "€13.000/anno".
           AUDIO:  Isabella: "La metà sono 'è pronta la mia auto?'
                   Un'ora al giorno. Cinquanta euro l'ora.
                   Tredici mila euro di lavoro mai fatturato.
                   Ogni anno."

0:10-0:22  SOLUZIONE
           VISIVO: Screenshot 18-scheda-veicoli.png — veicolo con storia.
                   Screenshot 03-clienti.png — messaggio WhatsApp automatico.
                   Meccanico sotto il cofano, concentrato. Nessun telefono.
           AUDIO:  Isabella: "Con FLUXION, il WhatsApp parte da solo quando
                   l'auto è pronta. Il promemoria revisione sessanta giorni
                   prima. Sara risponde mentre sei sotto al cofano."

0:22-0:30  CTA
           VISIVO: Nero. FLUXION / €497 una volta / FAST Officina: €1.800-5.400
                   in 3 anni / fluxion-landing.pages.dev
           AUDIO:  Standard Isabella.
```

### C. Comparazione copione attuale

Il copione v2 per officina è solido e il VO dura 26.9s — quasi perfetto. Il problema è che `seg_1` (9.2s) include il calcolo €13.000/anno ma lo presenta come narrazione lunga invece di un impatto numerico immediato.

La frase "tredici mila euro l'anno di lavoro mai fatturato" arriva tardi nel seg_1. Va spostata nel hook.

### D. Verdict: REWORK (lieve)

Il video officina è tra i migliori del gruppo. Serve solo:
1. Spostare il dato €13.000 nel hook 0-3s
2. Tagliare 1 screenshot per ridurre da 60.9s a ~55s

### E. Hook alternativi 0-3s

1. **Hook numerico estremo**: Testo bianco su nero: "€13.000/anno di lavoro non fatturato." Fade in mani sporche. — Il numero fa fermare lo scroll immediatamente
2. **Hook fisico**: Mani sporche, 13 chiamate perse sullo schermo, straccio blu. Isabella: "Tredici. Chiamate. Perse." — cinematico
3. **Hook domanda**: Isabella: "Quante volte al giorno rispondi 'è pronta la sua auto?'" — diretto, ma meno visivo

**Raccomandazione**: Hook 1 (numerico) come frame iniziale 1.5s, poi dissolvenza su Hook 2 (fisico). Il dato €13k arriva prima ancora della voce.

### F. CTA 24-30s

Nota: il competitor FAST Officina (€1.800-5.400 in 3 anni) è meno impattante del confronto Treatwell. Considerare di usare il ROI diretto: "€497 vs €13.000/anno di telefonate. Quale preferisci?"

---

## 4. CARROZZERIA

### A. Pain primario + trigger psicologico

Il carrozziere ha il pain più **invisibile**: il cliente che chiama ogni 3 giorni non è aggressivo — è ansioso. Ha l'auto fuori, non sa niente, il processo assicurativo è opaco, si sente ignorato. Il carrozziere invece sa tutto — CID ricevuta, perito che passa domani, attesa autorizzazione dalla compagnia — ma non ha tempo di spiegarlo ogni volta.

Il trigger psicologico è la **cattiva reputazione non meritata**: il carrozziere fa un lavoro perfetto ma il cliente gli lascia 3 stelle su Google perché "non si sapeva mai niente". La qualità del lavoro è eclissata dalla mancanza di comunicazione.

### B. Storyboard ideale 30s

```
0:00-0:03  HOOK
           VISIVO: Il titolare cammina tra 5 auto in lavorazione.
                   Telefono all'orecchio: "Sì, stiamo aspettando il perito."
                   Immediatamente squilla di nuovo: "Sì, la sua Audi..."
                   Non riesce a finire una frase.
           AUDIO:  Isabella: "Dodici giorni di riparazione.
                   Quattro telefonate per sinistro."

0:03-0:10  PAIN AGITATION
           VISIVO: Scrivania coperta di fogli. Preventivo cartaceo con correzioni.
                   Telefono sul tavolo: "8 chiamate perse oggi."
                   Star rating Google: 3 stelle. Recensione: "Nessuna comunicazione."
           AUDIO:  Isabella: "Due virgola otto milioni di sinistri in Italia.
                   Ogni cliente chiama ogni tre giorni.
                   Il lavoro è perfetto. La reputazione no.
                   Ogni. Singolo. Sinistro."

0:10-0:22  SOLUZIONE
           VISIVO: Screenshot 19-scheda-carrozzeria.png — stato riparazione tracciato.
                   Screenshot 03-clienti.png — WhatsApp automatico.
                   "Autorizzazione ricevuta. Iniziamo domani."
                   Titolare accanto all'Audi, tranquillo. Telefono non squilla.
           AUDIO:  Isabella: "Con FLUXION, lo stato di riparazione va su
                   WhatsApp da solo. Il cliente non chiama più.
                   Sa già tutto. La carrozzeria torna silenziosa."

0:22-0:30  CTA
           VISIVO: Nero. FLUXION / €497 una volta / Competitor: €2.880-7.200
                   in 3 anni / fluxion-landing.pages.dev
           AUDIO:  Standard Isabella.
```

### C. Comparazione copione attuale

Il copione carrozzeria è tra i più forti. Il VO (26s) è nel range target. La struttura è corretta.

Unico gap: il copione non menziona il danno reputazionale (recensioni negative) che è il trigger più emotivo per questo titolare. Il dato ANIA 2.8M sinistri è forte ma astratto.

### D. Verdict: KEEP

Il video carrozzeria è il più solido del gruppo. La durata 60s è accettabile. Nessuna azione urgente.

Miglioramento opzionale (low priority): aggiungere la "recensione Google" come elemento visivo nel seg_1 per colpire il trigger reputazionale.

### E. Hook alternativi 0-3s

1. **Hook attuale** (titolare tra le auto, telefonate): già funziona
2. **Hook recensione**: Close-up schermo con rating 3 stelle Google. "Lavoro eccellente ma nessuna comunicazione." Isabella: "Il lavoro era perfetto." — emozionalmente più forte
3. **Hook numero telefonate**: "Oggi: 8 telefonate per 3 auto." Testo su nero, poi fade carrozzeria — immediato

**Raccomandazione**: KEEP hook attuale. Se si fa una revisione futura, testare Hook 2 (recensione).

### F. CTA 24-30s

Standard. Considerare di aggiungere: "Il cliente non chiama più." come subline sopra il prezzo — riassume il beneficio principale in 5 parole.

---

## 5. DENTISTA

### A. Pain primario + trigger psicologico

Il dentista è il titolare con il **rischio legale più alto e il costo no-show più elevato**. Una poltrona a €200/ora vuota non è solo soldi persi — è un slot che non si recupera, un paziente che ha saltato un trattamento che serve alla sua salute, e una responsabilità dell'anamnesi che pende come una spada.

Il trigger psicologico è **la responsabilità professionale**: il dentista ha studiato 6 anni, ha fatto specializzazione, ha una carriera da proteggere. Un'allergia non registrata che causa un problema durante un intervento non è solo un errore amministrativo — è un incubo legale. La scheda cartacea illeggibile è una bomba a orologeria.

### B. Storyboard ideale 30s

```
0:00-0:03  HOOK
           VISIVO: Studio dentistico ore 9:15. Riunito acceso. Poltrona vuota.
                   Il dentista guarda l'orologio. La receptionist guarda il telefono.
                   Nessun paziente.
           AUDIO:  Isabella: "Poltrona vuota. Duecento euro l'ora.
                   È già la terza volta questo mese."

0:03-0:10  PAIN AGITATION
           VISIVO: Agenda — "Bianchi Mario 9:00" con croce sopra.
                   "- €200" scritto a mano.
                   Cartella paziente cartacea: riga illeggibile, firma sbiadita.
           AUDIO:  Isabella: "Ventitré pazienti su cento non si presentano.
                   [Dental Tribune Italia]
                   E l'anamnesi su carta — allergeni, farmaci —
                   se qualcosa va storto, quella cartella è tua responsabilità."

0:10-0:22  SOLUZIONE
           VISIVO: Screenshot 17-scheda-odontoiatrica.png — anamnesi digitale.
                   Screenshot 02-calendario.png — promemoria attivi.
                   Poltrona occupata. Paziente puntuale. Dentista sereno.
           AUDIO:  Isabella: "Con FLUXION, il promemoria parte ventiquattro
                   ore prima. I no-show scendono dal ventitre al sette percento.
                   L'anamnesi è digitale. Sul tuo computer."

0:22-0:30  CTA
           VISIVO: Nero. FLUXION / €497 una volta / XDENT: €7.200+ in 3 anni
                   / fluxion-landing.pages.dev
           AUDIO:  Standard Isabella.
```

### C. Comparazione copione attuale

PROBLEMA CRITICO: il VO dentista è 45.5s totali. `seg_1` da solo è 18.7s — quasi la lunghezza di un intero video barbiere. La narrazione è brillante ma dura il doppio del necessario.

Frasi da tagliare nel seg_1 attuale:
- "Una poltrona vuota costa duecento euro l'ora" — tenere
- "Ogni settimana, ogni studio" — tagliare (ridondante)
- "E l'anamnesi su carta — allergeni, farmaci, patologie pregresse — se qualcosa va storto, quella cartella è la tua responsabilità. [DPR 137/2012]" — ridurre a "L'anamnesi su carta — se qualcosa va storto, è tua responsabilità."

`seg_2` (19.3s) include "Sul tuo computer, non su server di nessuno" + "Sara risponde al telefono mentre hai le mani in bocca al paziente" — quest'ultima frase è potente ma arriva troppo tardi. Va spostata nel hook.

### D. Verdict: REPLACE VO

Riscrivere i tre segmenti audio e rigenerare con Edge-TTS. Le clip Veo3 esistenti vanno bene — il problema è esclusivamente nel VO.

**Azione concreta:**
1. Nuovo `seg_1.mp3` target 8s max: "Ventitré pazienti su cento non si presentano. Duecento euro l'ora. E l'anamnesi su carta — se sbaglia una riga, è tua responsabilità."
2. Nuovo `seg_2.mp3` target 11s max: "Con FLUXION, il promemoria parte. I no-show scendono al sette percento. L'anamnesi è digitale — leggibile, sicura, sul tuo computer."
3. `seg_3.mp3` OK (7.7s).

### E. Hook alternativi 0-3s

1. **Hook poltrona vuota**: Riunito acceso, poltrona vuota, orologio che segna 9:15. Isabella: "Duecento euro l'ora. Poltrona vuota." — concreto, immediato
2. **Hook anamnesi**: Close-up cartella paziente con firma illeggibile. Isabella: "Se questa firma sbaglia un allergene — sei tu il responsabile." — trigger legale diretto
3. **Hook costo annuale**: Testo su nero: "23 appuntamenti su 100 non si presentano." Poi il dentista che guarda l'orologio. — dato immediato

**Raccomandazione**: Hook 1 (poltrona vuota + costo). La specificità di €200/ora è il numero che rimane in testa.

### F. CTA 24-30s

Il confronto XDENT €7.200+ in 3 anni è il più forte di tutti i verticali — è quasi 15x il prezzo FLUXION. Va mantenuto e EVIDENZIATO. Considerare bold rosso sul numero XDENT.

---

## 6. CENTRO ESTETICO

### A. Pain primario + trigger psicologico

L'estetista 50enne ha due pain che si sommano: **il rischio legale della scheda** (allergia non registrata durante trattamento = responsabilità civile + perdita licenza) e **Treatwell come parassita silenzioso** (€22.500/anno su fatturato medio €90k — un quarto del fatturato a una piattaforma).

Il trigger psicologico è **l'orgoglio della relazione con la cliente**: l'estetista vede le stesse clienti ogni 3-4 settimane da anni, le conosce, sa i loro problemi. Treatwell "porta" clienti nuove — ma le "porta via" anche, perché la relazione è con la piattaforma, non con il centro. Questo è una violazione del patto implicito.

### B. Storyboard ideale 30s

```
0:00-0:03  HOOK
           VISIVO: Ricevuta Treatwell sul bancone: €340 questo mese.
                   Mano che la prende. Il numero è ingrandito.
           AUDIO:  Isabella: "Ogni mese. Trecentoquaranta euro. A Treatwell."
                   Pausa. "Su novantamila euro di fatturato:
                   ventiduemila e cinquecento euro. All'anno."

0:03-0:10  PAIN AGITATION
           VISIVO: Pila di cartelle cartacee. Una cade — fogli sparsi.
                   Modulo di consenso con nome sbagliato sul bordo.
           AUDIO:  Isabella: "La scheda controindicazioni è un obbligo di legge.
                   Se usi il prodotto sbagliato su un'allergia che non ricordavi —
                   quella cartella è tua responsabilità."

0:10-0:22  SOLUZIONE
           VISIVO: Screenshot 14-scheda-estetica.png — controindicazioni visibili.
                   Screenshot 22-pacchetti.png — pacchetti promo.
                   Estetista che lavora, serena. Tablet vicino: "allergia nichel."
           AUDIO:  Isabella: "Con FLUXION, la scheda estetica è digitale.
                   Allergie, trattamenti, consenso. Pacchetti promo in 2 click.
                   I tuoi clienti sono tuoi. Non di una piattaforma."

0:22-0:30  CTA
           VISIVO: Nero. FLUXION / €497 una volta / Treatwell: €22.500/anno
                   (rosso, grande) / fluxion-landing.pages.dev
           AUDIO:  Standard Isabella.
```

### C. Comparazione copione attuale

PROBLEMA CRITICO: centro_estetico ha il VO PIU LUNGO di tutti (47.2s). `seg_1` è 20.3s e include calcoli matematici verbosi ("Su novantamila euro di fatturato: ventiduemila e cinquecento euro") che funzionano meglio come TESTO a schermo che come narrazione orale.

La frase più forte dell'intero copione è "I tuoi clienti sono tuoi, non di una piattaforma" — arriva nel seg_2 quasi all'ultimo secondo. Va spostata come hook o come chiusura del pain.

### D. Verdict: REPLACE VO

Il VO va completamente riscritto per portarlo a 26s. Il dato €22.500/anno va mostrato come testo a schermo (un frame statico di 2s con il numero grande), non narrato per intero.

**Azione concreta:**
1. Nuovo `seg_1.mp3` target 8s: "In Italia novantadue mila centri estetici. Treatwell prende il venticinque percento. La scheda controindicazioni è un obbligo di legge. Un'allergia non registrata è tua responsabilità."
2. Frame visivo aggiuntivo 2s: testo "€22.500/anno a Treatwell" (bianco su nero) — questo sostituisce la narrazione del calcolo
3. Nuovo `seg_2.mp3` target 10s: "Con FLUXION, la scheda è digitale. Allergie, pacchetti, sedute tracciate. Zero Treatwell. I tuoi clienti sono tuoi."
4. `seg_3.mp3` OK.

### E. Hook alternativi 0-3s

1. **Hook ricevuta Treatwell**: Primo piano ricevuta con €340. "Trecentoquaranta euro. A Treatwell. Questo mese." — specifico e viscerale
2. **Hook percentuale**: Testo su nero: "25% di ogni cliente nuovo va a Treatwell." Poi le mani dell'estetista al lavoro. — astratto ma diretto
3. **Hook cartella caduta**: Pile di cartelle, una cade, fogli sparsi, nome sbagliato visibile. SILENZIO. Isabella: "Conosci tutte le allergie delle tue clienti?" — trigger legale

**Raccomandazione**: Hook 1 (ricevuta) — il numero €340 mensile è tangibile e immediato. Molto più forte del dato GDPR/legale come apertura.

### F. CTA 24-30s

Il dato €22.500/anno è il più devastante di tutti i verticali. Va mostrato a schermo BIG (font 80px+, rosso) con una subline: "FLUXION: €497. UNA VOLTA." Contrasto visivo massimo.

---

## 7. NAIL ARTIST

### A. Pain primario + trigger psicologico

La nail artist ha il pain più **fisico e specifico**: il pennellino 0.5mm che richiede concentrazione assoluta. Non è metafora — una vibrazione del telefono mentre disegna il fiore rovinare 20 minuti di lavoro e richiedere di ricominciare da capo. Questo non è perdita di denaro astratta — è frustrazione concreta e visibile.

Il trigger psicologico è **il rispetto per la propria arte**: la nail artist è un'artigiana. Il suo lavoro è bello, richiede talento, è visibile. Essere interrotta da un telefono mentre crea è una violazione della concentrazione artistica, non solo un problema di business.

### B. Storyboard ideale 30s

```
0:00-0:03  HOOK
           VISIVO: MACRO ESTREMO. Pennellino 0.5mm su unghia preparata.
                   Smalto gel bianco. La mano trema appena — telefono vibra.
                   Il fiore non viene. La nail artist si ferma.
           AUDIO:  SILENZIO totale per 2s. Poi Isabella, quasi un sussurro:
                   "Il fiore non viene. Deve rifare."

0:03-0:10  PAIN AGITATION
           VISIVO: Postazione vuota. Unghie a metà lavoro rimaste sul tavolo.
                   Timer sul telefono: 1h 15min. Già partito.
           AUDIO:  Isabella: "Settantacinque minuti. Un no-show.
                   Sessanta euro non incassati.
                   E non puoi rispondere quando hai il pennellino in mano.
                   Ogni. Singolo. Giorno."

0:10-0:22  SOLUZIONE
           VISIVO: Screenshot 14-scheda-estetica.png — preferenze cliente.
                   Screenshot 02-calendario.png — agenda piena.
                   Notifica silenziosa: "Sara: Martina confermata 14:30."
                   Pennellino in mano, fiore perfetto. Mano ferma.
           AUDIO:  Isabella: "Con FLUXION, Sara risponde e prenota
                   mentre lavori. Il promemoria parte da solo.
                   Il no-show scende. Le tue mani restano ferme."

0:22-0:30  CTA
           VISIVO: Nero. FLUXION / €497 una volta / Competitor: €4.320 in 3 anni
                   / fluxion-landing.pages.dev
           AUDIO:  Standard Isabella.
```

### C. Comparazione copione attuale

Il VO nail_artist è 42s — terzo più lungo dopo centro_estetico e dentista. `seg_1` (15.9s) e `seg_2` (18.7s) sono entrambi troppo lunghi.

Il copione v2 ha una scrittura quasi poetica ("Il fiore non viene. Deve rifare.") che funziona bene come voiceover corto ma viene diluita nella versione lunga. Il problema è che il copione descrive in dettaglio ogni clip invece di lasciare che le clip parlino.

`seg_2` nel video attuale include "La tua postazione è sempre occupata" + "Le tue mani restano ferme" — queste sono due CTA separate che indeboliscono l'una l'altra. Serve UN messaggio principale.

**Messaggio principale**: Le tue mani restano ferme. Tutto il resto è conseguenza.

### D. Verdict: REPLACE VO

1. Nuovo `seg_1.mp3` target 7s: "Settantacinque minuti. Un no-show. Sessanta euro. E non puoi rispondere quando hai il pennellino in mano."
2. Nuovo `seg_2.mp3` target 10s: "Con FLUXION, Sara risponde e prenota. Il promemoria parte da solo. Le tue mani restano ferme."
3. `seg_3.mp3` OK.

### E. Hook alternativi 0-3s

1. **Hook macro pennellino**: Macro estremo, pennellino 0.5mm, vibrazione, fiore rovinato. SILENZIO + "Il fiore non viene." — visivamente più forte di qualsiasi video del lotto
2. **Hook dato**: Testo su nero: "1 no-show = 75 minuti + €60." Poi postazione vuota. — matematico, immediato
3. **Hook sfida**: Isabella: "Stai lavorando su un'unghia. Il telefono vibra. Riesci a non muoverti?" — coinvolge direttamente

**Raccomandazione**: Hook 1 (macro pennellino) — il nail art è il verticale con il B-roll più cinematograficamente bello di tutti. Il macro estremo è un pattern interrupt visivo unico. Va usato al massimo.

### F. CTA 24-30s

Considerare aggiungere: "Le tue mani restano ferme." come subline sopra €497 — richiama il beneficio emotivo principale del video.

---

## 8. PALESTRA

### A. Pain primario + trigger psicologico

Il titolare palestra 50enne ha il pain del **ciclo stagionale che si ripete ogni anno senza soluzione**: gennaio pieno, aprile mezzo vuoto, settembre risale, e lui non sa come spezzare questo ciclo. Ha provato sconti, ha provato le classi di gruppo, ha comprato nuovi attrezzi — ma a marzo la palestra si svuota lo stesso.

Il trigger psicologico è **la rassegnazione al ciclo**: "è normale, è sempre stato così". Il video deve mostrargli che il ciclo è spezzabile — non con miracoli, ma con un sistema che parla alle persone quando stanno per smettere.

Il secondo trigger è **la bomba a orologeria del certificato medico scaduto**: la responsabilità civile in caso di infortunio senza certificato valido. Non è teorica — un infortunio in palestra senza certificato valido espone il titolare a responsabilità diretta.

### B. Storyboard ideale 30s

```
0:00-0:03  HOOK
           VISIVO: Spin bike tutti occupati (gennaio). TAGLIO NETTO.
                   Stessa inquadratura, metà bike libere (aprile).
                   Data sovraimpressa: "GENNAIO" → "APRILE".
           AUDIO:  Isabella: "Gennaio: piena. Aprile: metà vuota.
                   Ogni. Anno."

0:03-0:10  PAIN AGITATION
           VISIVO: Registro presenze cartaceo: gennaio pieno, aprile vuoto.
                   Post-it: "Certificato medico scaduto — rinnova."
           AUDIO:  Isabella: "Il cinquanta percento abbandona entro tre mesi.
                   Non perché la palestra è brutta.
                   Perché nessuno li ha cercati quando hanno saltato
                   la prima settimana. E il certificato scaduto nel cassetto —
                   se cade qualcuno, sei tu il responsabile."

0:10-0:22  SOLUZIONE
           VISIVO: Screenshot 13-scheda-fitness.png — abbonamento + certificato.
                   Screenshot 23-fedelta.png — programma fedeltà.
                   Palestra a febbraio: stabile. Non piena come gennaio,
                   ma stabile. Il proprietario sereno.
           AUDIO:  Isabella: "Con FLUXION, il promemoria abbonamento parte
                   da solo. Il certificato — avviso trenta giorni prima.
                   Il programma fedeltà fa tornare chi stava per smettere.
                   Febbraio, marzo, aprile: stabile."

0:22-0:30  CTA
           VISIVO: Nero. FLUXION / €497 una volta / Competitor: €3.600-7.200
                   in 3 anni / fluxion-landing.pages.dev
           AUDIO:  Standard Isabella.
```

### C. Comparazione copione attuale

Il VO palestra è 26.9s — nel range target. La struttura è corretta. Il copione usa il contrasto visivo gennaio/aprile che è il più efficace dell'intero script.

Gap principale: il copione ha un seg_1 che include sia il dato IHRSA (50% abbandona) sia il dato certificato medico. Questi sono due pain separati e il video rischia di sembrare che parla di due problemi invece di uno. In 30s, scegliere il pain PRIMARIO: la retention (50% abbandona) è più universale e immediatamente comprensibile.

### D. Verdict: REWORK (lieve)

Il video palestra è tra i migliori. Serve solo:
1. Tagliare 1 screenshot per portare da 60.8s a ~55s
2. Chiarire se il pain principale è retention o certificato medico (consiglio: retention, più immediata)

### E. Hook alternativi 0-3s

1. **Hook stagionale**: Gennaio pieno → aprile vuoto (due frame). Isabella: "Gennaio: piena. Aprile: metà vuota. Ogni. Anno." — pattern universalmente riconosciuto
2. **Hook dato IHRSA**: Testo: "50% di chi si iscrive a gennaio non c'è ad aprile." — dato impattante ma astratto
3. **Hook diretto**: Isabella: "Quando è stata l'ultima volta che uno dei tuoi iscritti di gennaio è ancora qui ad aprile?" — personale, sfidante

**Raccomandazione**: Hook 1 (stagionale visivo) — il contrasto visivo gennaio/aprile è il più forte e non richiede testo. Il titolare lo riconosce immediatamente.

### F. CTA 24-30s

Aggiungere "Febbraio, marzo, aprile: stabile." come subline sopra il prezzo — sintetizza il beneficio in 4 parole.

---

## 9. FISIOTERAPISTA

### A. Pain primario + trigger psicologico

Il fisioterapista 50enne ha il pain più **clinicamente specifico**: il paziente che interrompe il ciclo alla quinta seduta senza avviso non è solo un appuntamento perso — è un paziente che rischia la recidiva. Il fisioterapista lo sa: un ciclo incompleto è un danno alla salute del paziente. C'è una dimensione etica oltre a quella economica.

Il trigger psicologico è la **frustrazione professionale**: lui ha studiato, sa come trattare il paziente, ha un piano clinico preciso. Ma non può eseguire il piano se il paziente non si presenta e non può ricominciare da dove si era interrotto perché la scheda cartacea è illeggibile o incompleta.

### B. Storyboard ideale 30s

```
0:00-0:03  HOOK
           VISIVO: Fisioterapista che entra con la cartella. Sfoglia.
                   "Dov'eravamo rimasti? Quarta? Quinta?"
                   Il paziente: "Quinta. O sesta, non ricordo."
           AUDIO:  Isabella: "Quinta seduta. O sesta.
                   Il paziente non sa. Il fisioterapista neanche."

0:03-0:10  PAIN AGITATION
           VISIVO: Scheda cartacea: "VAS: 7/10 → 4/10 → ?" — riga vuota.
                   Il paziente non è venuto. La progressione si è fermata.
           AUDIO:  Isabella: "Un ciclo è dieci sedute. Se il paziente
                   salta la quinta — perdi cinquanta euro.
                   Ma soprattutto non sai più da dove ripartire.
                   Alla settima rischia la recidiva.
                   Ogni. Singolo. Ciclo."

0:10-0:22  SOLUZIONE
           VISIVO: Screenshot 16-scheda-fisioterapia.png — VAS tracciato.
                   Screenshot 02-calendario.png — promemoria attivi.
                   Fisioterapista che entra sicuro. Paziente che si fida.
           AUDIO:  Isabella: "Con FLUXION, la scheda traccia ogni seduta.
                   VAS, esercizi, note cliniche. Il promemoria parte da solo.
                   Il ciclo va a termine. Il paziente guarisce."

0:22-0:30  CTA
           VISIVO: Nero. FLUXION / €497 una volta / Competitor: €1.080-2.880
                   in 3 anni / fluxion-landing.pages.dev
           AUDIO:  Standard Isabella.
```

### C. Comparazione copione attuale

Il VO fisioterapista è 26.8s — perfettamente nel range. La struttura è quasi identica allo storyboard ideale. Il copione v2 usa il VAS (Visual Analogue Scale) come elemento specifico di credibilità — questo è esattamente il tipo di dettaglio settoriale che differenzia FLUXION da un software generico.

Gap unico: la frase "Il paziente guarisce" è la closing line del seg_2 nel copione — nel video attuale è sepolta nel mezzo di una frase più lunga. Va portata come chiusura isolata, con pausa prima.

### D. Verdict: KEEP

Il fisioterapista è il video tecnicamente più corretto. La durata 60.8s è accettabile. Il VO è nel range target. Il copione usa terminologia clinica credibile.

Miglioramento opzionale: isolare "Il paziente guarisce." come ultima frase del seg_2, con 0.3s di silenzio prima.

### E. Hook alternativi 0-3s

1. **Hook incertezza clinica**: Fisioterapista sfoglia cartella, "Dov'eravamo?" — il paziente incerto. Isabella: "Quinta seduta. O sesta. Nessuno sa." — autenticamente specifico
2. **Hook VAS**: Primo piano scheda: "VAS: 7 → 4 → ?" con riga vuota. Silenzio. — visualmente forte, tecnico
3. **Hook dato**: Testo: "25% dei pazienti salta una seduta senza avviso." [AIFI 2022] — numerico, verificabile

**Raccomandazione**: Hook 1 (incertezza clinica) — il dialogo "Quarta? Quinta?" è il momento più reale del copione. Il fisioterapista lo ha vissuto centinaia di volte.

### F. CTA 24-30s

Il confronto competitor (€1.080-2.880 in 3 anni) è il meno impattante di tutti i verticali — il costo dei gestionali fisio è già basso. Considerare di usare il ROI diretto: "€497 vs 1 ciclo interrotto ogni mese = €500/mese di lavoro perso." Più persuasivo del confronto software.

---

## QUICK WINS — Applicabili a Tutti i Video

### 1. Taglio screenshots: da 5 a 3

Tutti i video hanno 5 screenshot nella sequenza "soluzione". Tagliando a 3 (dashboard + scheda verticale + calendario) si riduce la durata di ~10s per ogni video. Impatto immediato su tutti e 9.

**FFmpeg operation** (identica per ogni verticale, cambia solo il tempo di ogni screenshot):
```bash
# Nel assemble_all.py, cambiare la lista screenshots da 5 a 3:
# PRIMA: problem_screens = screenshots[:2], solution_screens = screenshots[2:]  (5 totali)
# DOPO:  problem_screens = screenshots[:1], solution_screens = screenshots[1:3]  (3 totali)
```

### 2. CTA frame uniformata

Tutti i 9 CTA frame devono avere la stessa struttura visiva:
```
FLUXION                    (bianco, bold, 72px, centrato)
€497 una volta.            (bianco, regular, 48px)
[Competitor]: €X.XXX in 3 anni  (rosso #FF4040, 36px)
fluxion-landing.pages.dev  (teal #50C3D7, 36px)
```

Il frame rosso competitor va SEMPRE presente — è il contrasto che fa percepire €497 come conveniente.

### 3. Regola "Ogni. Singolo. [parola]."

Tutti i copioni usano questa chiusura di pain con pausa tra le parole. Nel VO attuale, la pausa è solo 0.2s. Portarla a 0.5s (parametro `--rate -10%` in Edge-TTS per quel segmento specifico) rende la sequenza molto più cinematica.

### 4. Musica: silenzio nel CTA

Tutti i video hanno la musica di sottofondo fino alla fine. Il CTA deve essere SILENZIO totale — solo la voce Isabella. L'assemble_all.py lo gestisce già (`silence_03s.mp3`) ma va verificato che il fade out della musica sia completato prima dell'inizio del `seg_3`.

### 5. Transition cut netto vs dissolvenza

Tra clip1 (hook) e inizio screenshots, usare CUT NETTO invece di dissolvenza 0.5s. Il contrasto brusco da "scena di dolore" a "schermata del software" amplifica il messaggio. La dissolvenza ammorbidisce un passaggio che deve essere deciso.

**FFmpeg**: rimuovere `xfade=transition=dissolve:duration=0.5` tra hook e prima screenshot frame.

---

## STANDARD FLUXION 2026 — Template Copione Video PMI

### Struttura Canonica 30s

```
[0:00-0:03] HOOK — pattern interrupt
            REGOLA: una sola cosa, nessuna parola per i primi 2s.
            Poi UNA frase massimo. Deve rispondere a:
            "Cosa rompe la routine visiva di questo titolare?"

[0:03-0:10] PAIN AGITATION — dato reale + trigger emotivo
            REGOLA: un dato verificato + uno specifico visivo del settore.
            Chiusura obbligatoria: "Ogni. Singolo. [parola settoriale]."
            Target: max 7s di voiceover.

[0:10-0:22] SOLUZIONE — show, not tell
            REGOLA: mostrare il software in azione (screenshot).
            Nessuna descrizione di funzionalità. Mostrare il RISULTATO.
            Il beneficio principale in prima frase. Max 10s.
            Termina con: "Zero abbonamenti. Zero commissioni."

[0:22-0:30] CTA — singolo imperativo + prezzo + URL
            REGOLA: FLUXION + prezzo + contrasto competitor + URL.
            Nessuna musica. Solo voce. Pausa 0.5s dopo "FLUXION".
            Non più di 4 righe a schermo.
```

### Template Voiceover (lunghezze target Edge-TTS)

```python
seg_1_target = 7.0   # pain: dato + trigger + "Ogni. Singolo."
seg_2_target = 11.0  # soluzione: show + "Zero abbonamenti."
seg_3_target = 7.5   # CTA: "FLUXION. €497. Una volta. Per sempre."
total_vo     = 25.5  # margine di sicurezza verso target 28s
```

### Parametri Edge-TTS Standard

```bash
edge-tts --voice it-IT-IsabellaNeural \
         --rate -8% \          # leggermente più lenta del default
         --pitch -5Hz \        # tono leggermente più basso, più autorevole
         --text "..." \
         --write-media seg_1.mp3
```

Per la sequenza "Ogni. Singolo. [parola].", usare `--rate -15%` solo su quel segmento.

### Palette Visiva Standard

```
Fase dolore (clip1 + screenshots problema):
  - Filtro FFmpeg: colorbalance=rs=-0.1:gs=-0.1:bs=0.05 (freddo, desaturato)
  - Vignette: vignette=PI/4

Fase soluzione (screenshots soluzione + clip3):
  - Filtro FFmpeg: colorbalance=rs=0.05:gs=0.02:bs=-0.05 (caldo, leggermente)
  - Nessuna vignette

CTA frame:
  - Nero assoluto #000000
  - Nessun filtro
```

### Struttura Assembly Raccomandata

```
Clip1 (hook)        : 6s (non 8s — risparmia 2s per ogni video)
Screenshot pain ×1  : 3s (non 2 screenshot — uno solo, il più forte)
Seg_1 voiceover     : max 7s sovraimpressa su screenshot pain
Screenshot sol. ×2  : 3s + 3s
Seg_2 voiceover     : max 11s sovraimpressa su screenshot soluzione
Clip3 (soluzione)   : 6s (non 8s)
CTA frame           : seg_3 durata + 1s di pausa finale

TOTALE TARGET: 6 + 3 + (6 o 11 se vo lungo) + 6 + 6 + 8.5 = ~45-50s
```

---

## ROADMAP PRIORITIZZATA — Impatto Conversione × Effort

### P1 — Alta urgenza (fare prima, impatto massimo)

1. **Centro Estetico — REPLACE VO** (effort: 1h)
   - Verticale con il dato killer (€22.500/anno Treatwell)
   - VO attuale 47s è un abbandono garantito
   - Riscrivere 3 segmenti + rigenerare Edge-TTS + rimontare
   - Dato da mostrare a schermo come testo, non narrato

2. **Dentista — REPLACE VO** (effort: 1h)
   - VO 45.5s su un video dove il titolare è già scettico sulla tecnologia
   - Il dato XDENT €7.200 vs €497 è il confronto più forte del portafoglio
   - Stessa operazione: 3 segmenti nuovi + rimontaggio

3. **Parrucchiere — REPLACE VO** (effort: 1h)
   - Verticale con più volumi (110k saloni)
   - Il WA template cita Treatwell — il video deve allinearsi perfettamente
   - Priorità: hook del colore nel lavandino

### P2 — Media urgenza (2a settimana)

4. **Nail Artist — REPLACE VO** (effort: 1h)
   - VO 42s. Il concept è il più cinematograficamente forte — spreco non sfruttarlo
   - Il macro pennellino + silenzio 2s è il miglior hook dell'intero portafoglio

5. **Officina — REWORK** (effort: 30min)
   - Spostare dato €13.000 nel hook
   - Tagliare 1 screenshot

### P3 — Bassa urgenza (3a settimana)

6. **Barbiere — REWORK lieve** (effort: 20min)
   - Già il migliore del gruppo
   - Solo taglio 1 screenshot

7. **Palestra — REWORK lieve** (effort: 20min)
   - Chiarire pain primario (retention vs certificato)

### P4 — Mantenere (nessuna azione)

8. **Carrozzeria — KEEP**
9. **Fisioterapista — KEEP**

---

## NOTE OPERATIVE PER L'EDITOR

### Rigenerare VO con Edge-TTS

```bash
# Esempio per centro_estetico seg_1 nuovo
NUOVE_PAROLE="In Italia novantadue mila centri estetici. \
Treatwell prende il venticinque percento. \
La scheda controindicazioni è un obbligo di legge. \
Un'allergia non registrata è tua responsabilità."

edge-tts \
  --voice it-IT-IsabellaNeural \
  --rate -8% \
  --pitch -5Hz \
  --text "$NUOVE_PAROLE" \
  --write-media /Volumes/MontereyT7/FLUXION/video-factory/output/centro_estetico/seg_1.mp3
```

Verificare durata con `ffprobe` prima di rimontare. Target: 7-8s. Se troppo lungo, aumentare `--rate -5%`.

### Rimontare video dopo nuovo VO

```bash
cd /Volumes/MontereyT7/FLUXION/video-factory
python3 assemble_all.py centro_estetico
# oppure per tutti:
python3 assemble_all.py
```

### Verificare qualità output

```bash
# Check durata finale
ffprobe -v quiet -show_entries format=duration -of csv=p=0 \
  output/centro_estetico/centro_estetico_final_16x9.mp4

# Target: 50-60s. Se > 62s, tagliare altri screenshot dalla config.
```

### Upload YouTube aggiornato

Dopo rimontaggio, usare `scripts/youtube_batch_upload.py` con `--only centro_estetico` e `--privacy unlisted` per sovrascrivere il video esistente con lo stesso ID.

---

*Report generato: 2026-04-27 | Sessione S170 | Visual Storyteller*
*Asset analizzati: 9 video finali, 54 clip raw, 27 segmenti audio VO, 9 copioni v2*
*Prossimo step: iniziare da centro_estetico REPLACE VO (P1, massimo impatto)*
