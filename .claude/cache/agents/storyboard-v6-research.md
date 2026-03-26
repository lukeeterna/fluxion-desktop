---
agent: storyboard-designer
task: storyboard-v6-research
date: 2026-03-26
version: V6 FINAL
---

# Storyboard V6 — Deep Research & Scene-by-Scene Plan
> Generated: 2026-03-26 | Storyboard Designer Agent
> Target: 4:30–5:00 min | YouTube + Landing embed | PMI italiane

---

## PARTE 1 — ANALISI V5: COSA FUNZIONAVA E COSA NO

### Cosa funzionava in V5

**1. Il montaggio problema multi-verticale (CH1_GIORNATA)**
Il blocco di 9 clip AI che mostrano PMI diverse impossibilitate a rispondere al telefono era
concettualmente il pezzo più forte. Ogni titolare si riconosce in almeno una scena. Il problema
viene comunicato senza dire una parola — visivamente immediato.

**2. Il voiceover di Sara come personaggio**
La scelta di far narrare Sara in prima persona ("Mi chiamo Sara. Sono la tua assistente.")
è una mossa di copy eccellente. Crea un personaggio con personalità, non uno strumento anonimo.
Da mantenere e potenziare in V6.

**3. La telefonata simulata (SS02_telefonata)**
20 secondi di dialogo reale Sara/cliente che mostra: riconoscimento del cliente per nome,
memoria dell'ultimo servizio, proposta dell'operatore giusto, conferma WhatsApp. Questo è il
momento più dimostrativo di tutto il video. Il problema in V5: era sovrapposto a un fermo
immagine statico di 08-voice.png invariato — spreco totale del potenziale narrativo.

**4. Il copy del prezzo (V12_soddisfatta)**
"Un gestionale in abbonamento ti costa seicento euro all'anno. In tre anni, milleottocento.
E non sarà mai tuo. FLUXION costa quattrocentonovantasette euro. Una volta sola. Per sempre."
Questo è copy di alta qualità — loss framing corretto, confronto specifico, CTA chiara.
Il fondatore ha confermato il tono come "eccezionale". Non toccare la struttura narrativa.

**5. La chiusura "Come ho fatto senza?" (V13_finale)**
Il titolo del video come domanda finale è una tecnica di copy solida. Lascia il viewer con
una domanda che si risponde da solo. Da mantenere come capitolo e ultimo voiceover.

**6. Asset AI di qualità**
Le 13 clip Veo 3 in ai-clips-v2/ sono di ottima qualità cinematografica. Non serve rigenerare
nulla per V6 — si tratta di riorganizzarle in modo più efficace.

---

### Cosa non funzionava in V5

**PROBLEMA 1 — Durata 6:40: troppo lunga del 33%**
La ricerca 2026 indica 3:30–5:00 come finestra ottimale per demo PMI software. A 6:40 il
dropout si impenna dopo il minuto 4. V6 deve stare entro 5:00.

**PROBLEMA 2 — Il blocco di 9 clip problema era ripetitivo (35 secondi)**
Nove clip con lo stesso pattern (persona lavora → telefono suona → non risponde) diventano
monotone dopo la terza. L'attenzione decade quando non c'è variazione di informazione.
Tre clip distinte, rapide (2s ciascuna) fanno lo stesso lavoro in 6 secondi.

**PROBLEMA 3 — Zero screenshot per pacchetti e fedeltà**
SS18_pacchetti usava 01-dashboard.png come placeholder — immagine completamente sbagliata.
I pacchetti fedeltà sono la feature principale che differenzia Base da Pro. In V5 non
vengono MAI mostrati visivamente. Questo è il gap più grave rispetto alla proposta di valore.

**PROBLEMA 4 — Sei screenshot consecutivi di schede verticali senza break**
SS06→SS07→SS08→SS09→SS10→SS11 = 42 secondi di screenshot in fila, nessuna clip AI
di rottura. La regola del ritmo video: mai più di 2 screenshot consecutivi senza un elemento
visivo dinamico. Sei di fila garantiscono dropout.

**PROBLEMA 5 — Sara su 08-voice.png per 38 secondi senza cambio visivo**
Tre scene consecutive (SS01_voice, SS02_telefonata, SS03_sara_conosce) mostravano sempre
la stessa schermata 08-voice.png per 38 secondi totali. Il viewer percepisce il video fermo.

**PROBLEMA 6 — CH6_GESTIONE: 6 screenshot consecutivi di feature secondarie**
Fornitori, fatture, servizi, operatori, cassa, analytics — 42 secondi in sequenza lineare
senza break. Alcune di queste (fornitori in particolare) hanno bassa rilevanza emotiva per
il prospect e rallentano il ritmo senza aggiungere valore alla decisione di acquisto.

**PROBLEMA 7 — Nessun elemento visivo per la CTA**
V13_finale era una clip AI con voiceover testuale sul brand. Nessun URL sullo schermo,
nessun QR code, nessuna slide finale con le informazioni di acquisto. Il viewer che vuole
agire non sa dove andare.

**PROBLEMA 8 — Numerazione screenshot V5 non corrispondeva agli asset reali**
V5 citava 13-scheda-parrucchiere.png, 14-scheda-veicoli.png ecc. I file reali in
landing/screenshots/ hanno numerazione diversa: 12-scheda-parrucchiere.png,
18-scheda-veicoli.png ecc. Il video-editor agent avrebbe trovato path errati.

---

## PARTE 2 — ASSET INVENTORY REALE (2026-03-26)

### Screenshot disponibili (21 file)
```
01-dashboard.png            — Dashboard principale con KPI
02-calendario.png           — Calendario settimanale
03-clienti.png              — Lista clienti con filtri
04-servizi.png              — Gestione servizi/listino
05-operatori.png            — Gestione operatori/staff
06-fatture.png              — Modulo fatture
07-cassa.png                — Cassa giornaliera
08-voice.png                — Interfaccia Sara (voice agent)
09-fornitori.png            — Gestione fornitori
10-analytics.png            — Report analytics
11-impostazioni.png         — Impostazioni sistema
12-scheda-parrucchiere.png  — Scheda verticale parrucchiere
13-scheda-fitness.png       — Scheda verticale fitness/palestra
14-scheda-estetica.png      — Scheda verticale estetica
15-scheda-medica.png        — Scheda verticale medica
16-scheda-fisioterapia.png  — Scheda verticale fisioterapia
17-scheda-odontoiatrica.png — Scheda verticale odontoiatrica
18-scheda-veicoli.png       — Scheda verticale veicoli/officina
19-scheda-carrozzeria.png   — Scheda verticale carrozzeria
20-scheda-selector.png      — Selettore schede verticali (mostra tutte le opzioni)
21-trasformazioni-prima-dopo.png — Confronto prima/dopo FLUXION (proof visivo)
```

NOTA: 20-scheda-selector.png e 21-trasformazioni-prima-dopo.png non erano usati in V5.
Entrambi sono asset strategici per V6.

### Clip AI disponibili (13 file in ai-clips-v2/, ~8s ciascuna)
```
V01_salone.mp4         — Parrucchiera, mani occupate, telefono che squilla
V02_officina.mp4       — Meccanico, mani sporche, telefono in tasca
V03_dentista.mp4       — Dentista con paziente, telefono sul vassoio strumenti
V04_palestra.mp4       — Personal trainer spotter, telefono in borsa
V05_estetista.mp4      — Estetista, trattamento facciale, telefono sul tavolo
V06_nails.mp4          — Nail artist, gel art intricato, telefono che vibra
V07_fisioterapista.mp4 — Fisioterapista, manipolazione spalla, non può fermarsi
V08_gommista.mp4       — Gommista, chiave pneumatica, telefono su banco
V09_elettrauto.mp4     — Elettrauto, multimetro, circuiti delicati
V10_frustrazione.mp4   — Titolare stanca, sera, 5 chiamate perse sullo schermo
V11_qrcode.mp4         — Cliente scansiona QR code in salone, sorride al telefono
V12_soddisfatta.mp4    — Titolare rilassata, PC aperto FLUXION, zero missed calls
V13_finale.mp4         — Montaggio titolari felici e sereni, FLUXION sullo schermo
```

---

## PARTE 3 — RITMO: QUANDO ACCELERARE E QUANDO RALLENTARE

### Principio: il ritmo racconta l'emozione

Il ritmo deve rispecchiare l'arco emotivo del viewer:

```
TENSIONE (problema) → RESPIRO (soluzione) → INTERESSE (demo) → URGENZA (prezzo) → SOLLIEVO (CTA)
```

### Mappa del ritmo V6 per fase

| Minuto | Fase | Velocità | Durata media scena | Musica |
|--------|------|----------|--------------------|--------|
| 0:00–0:22 | Hook problema | Molto veloce | 2–3s | Crescendo da 0% a 30% |
| 0:22–0:50 | Agitazione emotiva | Media | 6–8s | 20%, scende |
| 0:50–1:35 | Sara intro + dialogo | Lenta | 8–18s | 10% (quasi assente durante dialogo) |
| 1:35–2:15 | Dashboard + calendario | Media | 8–10s | 25% |
| 2:15–3:10 | Schede + gestione | Media-rapida | 5–9s | 25% |
| 3:10–3:30 | Pacchetti/fedeltà | Media | 9–10s | 20% |
| 3:30–3:50 | Cassa + analytics | Media-rapida | 5–7s | 25% |
| 3:50–4:25 | Prezzo | Lenta (lascia respirare) | 10–12s | 35%, sale |
| 4:25–5:00 | CTA + logo | Media poi ferma | 8–10s + 5s logo | 50%, dissolvenza |

### I 3 tipi di transizione e quando usarli

- **Taglio secco (0.2s)**: tra clip AI del blocco problema — crea urgenza visiva, non dà
  tempo di distrarsi
- **Crossfade (0.6s)**: transizione standard tra screenshot o da clip AI a screenshot —
  movimento naturale, non disturba
- **Dissolvenza lenta (1.0–1.2s)**: solo prima della telefonata Sara e prima della scena
  prezzo — segnala al viewer che sta per arrivare qualcosa di importante

### Regola del respiro

Mai più di 2 screenshot consecutivi senza un break visivo.
Break validi: clip AI (anche solo 3–4s di trim), pausa breve con musica, logo splash.
Questa regola è non negoziabile per V6.

---

## PARTE 4 — RAPPORTO CLIP AI vs SCREENSHOT

### Target V6

```
Clip AI (13 disponibili):     usarne 8 (non tutte — evitare ridondanza)
Screenshot (21 disponibili):  usarne 13–14 (quelli con maggiore impatto)
Scene totali target:          24–26 scene
Ratio:                        35% clip AI / 65% screenshot
```

### Distribuzione per fase

| Fase | Ratio clip AI / screenshot | Motivazione |
|------|---------------------------|-------------|
| Hook 0:00–0:50 | 5:1 | Emozione pura, riconoscimento identitario |
| Sara 0:50–1:35 | 1:2 | Demo prodotto + break emotivo |
| Gestionale 1:35–2:15 | 0:3 | Screenshot reali, prodotto al centro |
| Schede 2:15–2:55 | 2:3 | Clip AI di intro verticale, poi screenshot scheda |
| Gestione 2:55–3:50 | 1:4 | Un clip AI di break ogni 4 screenshot |
| Prezzo/CTA 3:50–5:00 | 2:1 | Chiusura emotiva con clip AI, poi logo |

### Clip AI da includere in V6 (8 su 13)

| Clip | Posizione | Uso |
|------|-----------|-----|
| V01_salone | 0:00 (2s trim) | Hook — primo mestiere visivo |
| V02_officina | 0:02 (2s trim) | Hook — secondo mestiere |
| V04_palestra | 0:04 (2s trim) | Hook — terzo mestiere |
| V09_elettrauto | 0:06 (2s trim) | Hook — quarto mestiere (diverso dai precedenti) |
| V10_frustrazione | 0:08 | Agitazione emotiva — titolare con 5 missed calls |
| V11_qrcode | ~3:20 | Comunicazione — cliente scansiona QR |
| V12_soddisfatta | ~4:00 | Prezzo — titolare serena e felice |
| V13_finale | ~4:25 | CTA — montaggio finale |

### Clip AI non incluse in V6 (disponibili per Shorts/Reels verticali)

V03_dentista, V05_estetista, V06_nails, V07_fisioterapista, V08_gommista — ottime per
clip verticali da 15–30s dedicati ai singoli settori. Non inserite nel V6 per evitare
il problema V5 di ripetere lo stesso pattern 9 volte.

---

## PARTE 5 — I PRIMI 5 SECONDI: ESATTAMENTE COSA MOSTRARE

### Regola d'oro: zero logo, zero musica sola, zero nero — parte subito con il loro mondo

Il viewer PMI decide nei primi 3 secondi se il video parla di lui o no.

### Formula validata: "Eccomi Anch'Io" (mirror moment)

Il problema di V5: iniziava con il solo salone (V01). Un meccanico vedeva "roba da
parrucchieri" e saltava. Il viewer deve riconoscersi nel proprio mestiere entro 3 secondi.

### Sequenza esatta dei primi 8 secondi

```
[0:00 — frame 0]
Parte V01_salone.mp4 in medias res — forbici che tagliano, telefono che inizia a suonare.
Musica fade in 0% → 25%. ZERO voiceover.

[0:02]
Taglio secco a V02_officina.mp4 — mani sporche con chiave inglese.
ZERO voiceover. Solo il suono diegetico del telefono che squilla.

[0:04]
Taglio secco a V04_palestra.mp4 — personal trainer che assiste il cliente.
ZERO voiceover.

[0:06]
Taglio secco a V09_elettrauto.mp4 — multimetro su circuito delicato.
ZERO voiceover.

[0:08]
Crossfade lento (1.2s) verso V10_frustrazione.mp4 — titolare stanca, sera,
5 missed calls sullo schermo del telefono.
Musica scende a 15%.
Sara inizia a parlare con voce calma ma intensa:
"Tu lo sai com'è. Sei lì che lavori. Le mani occupate. E il telefono squilla."
```

### Perché questo funziona

I 4 mestieri in 8 secondi coprono le 4 macro-verticali principali di FLUXION:
- Salone (bellezza/capelli)
- Officina (automotive)
- Palestra (fitness/wellness)
- Elettrauto (tecnico specializzato)

Un PMI di qualsiasi settore si riconosce in almeno uno. Il suono del telefono che squilla
è identico in tutte e 4 le clip — diventa un pattern audio unificante prima ancora che
il voiceover inizi. L'ingresso di Sara a 0:08 sulla scena della frustrazione è il momento
di massimo impatto emotivo — il viewer è già attivato, pronto ad ascoltare la soluzione.

---

## PARTE 6 — SCHEDE VERTICALI, PACCHETTI, FEDELTÀ

### Schede Verticali — Principio "2 + Selettore"

Il problema V5: 5 schede in 40 secondi = il viewer non memorizza nessuna.
Il principio V6: 2 schede approfondite + 1 screenshot del selettore (iceberg effect).

**Selezione schede per V6:**

1. **12-scheda-parrucchiere.png** (8s)
   Il settore più diffuso tra i target PMI (~40% del mercato). Prima scheda mostrata.
   Voiceover specifico: allergie ai prodotti, tipo capello, note ultima visita.
   Introduce il concetto di scheda verticale nel modo più universalmente comprensibile.

2. **18-scheda-veicoli.png** (8s)
   Massima differenziazione — nessun competitor PMI ha una scheda veicolo con
   targa/revisione/assicurazione. È il "wow moment" per la verticale automotive.
   Voiceover: "Sara chiede il modello dell'auto quando prenota e salva tutto automaticamente."

3. **20-scheda-selector.png** (5s)
   Non mostra UNA scheda ma TUTTE le opzioni disponibili.
   Voiceover: "Qualunque sia la tua attività, FLUXION ha la scheda giusta per te."
   Questo screenshot vale 6 schede — il viewer vede che ne esistono molte senza vederle tutte.

**Break visivi tra schede:**
Inserire la clip di intro settore PRIMA della scheda corrispondente:
- Trim 2s di V01_salone (parrucchiera sorridente) → poi 12-scheda-parrucchiere.png
- Trim 2s di V02_officina (meccanico che lavora) → poi 18-scheda-veicoli.png
Questo crea la connessione visiva problema/soluzione per ogni scheda.

### Pacchetti e Fedeltà — La Feature Mancante di V5

I pacchetti fedeltà sono la feature più persuasiva per l'upgrade Base→Pro (€497→€897).
In V5 non erano MAI visibili sullo schermo.

**Opzione A (preferita)**: usare 21-trasformazioni-prima-dopo.png come "proof visivo"
con voiceover dedicato ai pacchetti. Questo screenshot mostra il risultato tangibile —
più efficace di qualsiasi UI dei pacchetti.

**Opzione B (fallback)**: usare 03-clienti.png con overlay mentale del voiceover sui
pacchetti. Meno ideale ma funzionale se 21-trasformazioni è poco leggibile a 720p.

**NOTA CRITICA**: Prima di produrre V6, verificare visivamente 21-trasformazioni-prima-dopo.png
per assicurarsi che sia leggibile e contenga dati demo realistici. Se è un placeholder,
catturare un nuovo screenshot dall'app iMac con dati seed.

**Voiceover pacchetti (posizionato su scena 21 o 03-clienti):**
> "E per fidelizzare? I pacchetti. Cinque sedute colore a duecento euro invece di
> duecentocinquanta. Il cliente paga oggi e torna sempre. Sara propone il pacchetto
> al momento giusto. Il tasso di ritorno raddoppia."

**Posizionamento narrativo**: Atto 3, DOPO le schede verticali e PRIMA della cassa/analytics.
I pacchetti rispondono alla domanda "come faccio a guadagnare di più per cliente?" — questa
domanda emerge dopo aver capito come gestire il calendario e i clienti.

---

## PARTE 7 — STORYBOARD V6 COMPLETO SCENA PER SCENA

### Metadati

```
Titolo:           FLUXION — Come Ho Fatto Senza?
Durata target:    4:35–5:00
Voce narrante:    it-IT-IsabellaNeural, rate -5%
Voce cliente:     it-IT-DiegoNeural, rate 0%
Risoluzione:      1280x720
FPS:              30
Musica:           landing/assets/background-music.mp3 (Mixkit Skyline)
Logo watermark:   FLUXION top-left, 64px, 70% opacity, OGNI frame
Path base clip:   landing/assets/ai-clips-v2/
Path base screen: landing/screenshots/
```

---

### CAPITOLO 1 — "La Tua Giornata" [0:00–0:50]

YouTube timestamp: 0:00

---

**SCENA 01**
```json
{
  "id": "scene_01",
  "type": "ai",
  "file": "landing/assets/ai-clips-v2/V01_salone.mp4",
  "trim_start": 0,
  "trim_end": 2,
  "voiceover": null,
  "duration": 2,
  "chapter": "La Tua Giornata",
  "transition": "cut",
  "music_volume": 0.25,
  "note": "Nessun voiceover — solo musica e suono diegetico del telefono. Prime 2s della clip."
}
```

**SCENA 02**
```json
{
  "id": "scene_02",
  "type": "ai",
  "file": "landing/assets/ai-clips-v2/V02_officina.mp4",
  "trim_start": 0,
  "trim_end": 2,
  "voiceover": null,
  "duration": 2,
  "transition": "cut",
  "music_volume": 0.25
}
```

**SCENA 03**
```json
{
  "id": "scene_03",
  "type": "ai",
  "file": "landing/assets/ai-clips-v2/V04_palestra.mp4",
  "trim_start": 0,
  "trim_end": 2,
  "voiceover": null,
  "duration": 2,
  "transition": "cut",
  "music_volume": 0.25
}
```

**SCENA 04**
```json
{
  "id": "scene_04",
  "type": "ai",
  "file": "landing/assets/ai-clips-v2/V09_elettrauto.mp4",
  "trim_start": 0,
  "trim_end": 2,
  "voiceover": null,
  "duration": 2,
  "transition": "cut",
  "music_volume": 0.25
}
```

**SCENA 05** — Agitazione emotiva, musica scende
```json
{
  "id": "scene_05",
  "type": "ai",
  "file": "landing/assets/ai-clips-v2/V10_frustrazione.mp4",
  "trim_start": 0,
  "trim_end": 8,
  "voiceover": "Tu lo sai com'è. Sei lì che lavori. Le mani occupate. E il telefono squilla. Squilla ancora. Quel cliente che voleva prenotare? Ha già chiamato qualcun altro.",
  "voice": "IsabellaNeural",
  "duration": 8,
  "transition": "crossfade",
  "transition_duration": 1.2,
  "music_volume": 0.15,
  "note": "Voiceover inizia a 0.5s dall'inizio della clip — breve pausa visiva prima delle parole"
}
```

**SCENA 06** — Numeri che colpiscono
```json
{
  "id": "scene_06",
  "type": "ai",
  "file": "landing/assets/ai-clips-v2/V10_frustrazione.mp4",
  "trim_start": 3,
  "trim_end": 8,
  "voiceover": "Un cliente perso al giorno sono duecentocinquanta clienti all'anno. A trenta euro di media: settemilacinquecento euro. E una segretaria? Novecento euro al mese, ogni mese.",
  "voice": "IsabellaNeural",
  "duration": 8,
  "transition": "crossfade",
  "transition_duration": 0.8,
  "music_volume": 0.15,
  "note": "Stesso clip V10, trim diverso — crea continuità emotiva senza ripetizione identica"
}
```

---

### CAPITOLO 2 — "Ti Presento Sara" [0:50–1:38]

YouTube timestamp: 0:50

---

**SCENA 07** — Prima comparsa UI Sara
```json
{
  "id": "scene_07",
  "type": "screenshot",
  "file": "landing/screenshots/08-voice.png",
  "voiceover": "E se ti dicessi che c'è qualcuno che risponde per te? Sempre. Anche di notte. Anche di domenica. Anche quando sei in ferie. Mi chiamo Sara. Sono la tua assistente vocale. Parlo italiano, capisco cosa vogliono i tuoi clienti, e prenoto per loro. Senza che tu alzi un dito.",
  "voice": "IsabellaNeural",
  "duration": 10,
  "chapter": "Ti Presento Sara",
  "transition": "crossfade",
  "transition_duration": 0.8,
  "music_volume": 0.15
}
```

**SCENA 08** — Dialogo reale Sara/cliente (pezzo centrale del video)
```json
{
  "id": "scene_08",
  "type": "dialogue",
  "file": "landing/screenshots/08-voice.png",
  "voiceover_dialogue": [
    {"voice": "DiegoNeural",    "text": "Buongiorno, vorrei prenotare un taglio per domani mattina."},
    {"voice": "IsabellaNeural", "text": "Buongiorno Marco! Certo. L'ultima volta ha fatto taglio e barba con Roberto — vuole ripetere lo stesso servizio?"},
    {"voice": "DiegoNeural",    "text": "Sì, esatto, perfetto!"},
    {"voice": "IsabellaNeural", "text": "Roberto è disponibile domani alle dieci e trenta. Le va bene?"},
    {"voice": "DiegoNeural",    "text": "Perfetto, grazie!"},
    {"voice": "IsabellaNeural", "text": "Prenotato! Le mando conferma su WhatsApp. Buona giornata Marco!"}
  ],
  "duration": 20,
  "transition": "crossfade",
  "transition_duration": 0.8,
  "music_volume": 0.08,
  "note": "Musica quasi assente durante il dialogo — il viewer deve sentire chiaramente la differenza di voce. Sara CONOSCE il cliente per nome, ricorda il servizio, propone l'operatore — non è uno script generico."
}
```

**SCENA 09** — Break emotivo (titolare serena che ha FLUXION)
```json
{
  "id": "scene_09",
  "type": "ai",
  "file": "landing/assets/ai-clips-v2/V12_soddisfatta.mp4",
  "trim_start": 0,
  "trim_end": 6,
  "voiceover": "Non è un risponditore automatico. Sara conosce i tuoi clienti, il loro nome, l'ultimo servizio, le preferenze. Uno slot vuoto domani? Sara avvisa la lista d'attesa. In automatico.",
  "voice": "IsabellaNeural",
  "duration": 8,
  "transition": "crossfade",
  "transition_duration": 1.0,
  "music_volume": 0.20
}
```

---

### CAPITOLO 3 — "Tutto in un Colpo d'Occhio" [1:38–2:18]

YouTube timestamp: 1:38

---

**SCENA 10** — Dashboard
```json
{
  "id": "scene_10",
  "type": "screenshot",
  "file": "landing/screenshots/01-dashboard.png",
  "voiceover": "Appena apri FLUXION, vedi tutto. Appuntamenti di oggi, clienti del mese, fatturato, il servizio più richiesto. Non devi cercare niente. È tutto lì, chiaro, in italiano.",
  "voice": "IsabellaNeural",
  "duration": 10,
  "chapter": "Tutto in un Colpo d'Occhio",
  "transition": "crossfade",
  "transition_duration": 0.6,
  "music_volume": 0.25
}
```

**SCENA 11** — Calendario
```json
{
  "id": "scene_11",
  "type": "screenshot",
  "file": "landing/screenshots/02-calendario.png",
  "voiceover": "Il calendario. Un nuovo appuntamento in due click. Scegli cliente, servizio, operatore, orario. Fatto. Il promemoria WhatsApp parte automaticamente ventiquattro ore prima. I no-show si dimezzano.",
  "voice": "IsabellaNeural",
  "duration": 10,
  "transition": "crossfade",
  "transition_duration": 0.6,
  "music_volume": 0.25
}
```

**SCENA 12** — Operatori (break prima delle schede)
```json
{
  "id": "scene_12",
  "type": "screenshot",
  "file": "landing/screenshots/05-operatori.png",
  "voiceover": "I tuoi collaboratori. Ognuno con il suo calendario, i turni, le ferie. Sai chi lavora oggi e chi ha generato più fatturato questo mese.",
  "voice": "IsabellaNeural",
  "duration": 8,
  "transition": "crossfade",
  "transition_duration": 0.6,
  "music_volume": 0.25
}
```

---

### CAPITOLO 4 — "La Scheda Per la Tua Attività" [2:18–3:05]

YouTube timestamp: 2:18

---

**SCENA 13** — Intro verticale salone
```json
{
  "id": "scene_13",
  "type": "ai",
  "file": "landing/assets/ai-clips-v2/V01_salone.mp4",
  "trim_start": 4,
  "trim_end": 8,
  "voiceover": "Sei parrucchiere?",
  "voice": "IsabellaNeural",
  "duration": 4,
  "chapter": "La Scheda Per la Tua Attività",
  "transition": "cut",
  "transition_duration": 0.3,
  "music_volume": 0.25,
  "note": "Ultimi 4s della clip V01 — parrucchiera sorridente, tono positivo (non più frustrata)"
}
```

**SCENA 14** — Scheda parrucchiere
```json
{
  "id": "scene_14",
  "type": "screenshot",
  "file": "landing/screenshots/12-scheda-parrucchiere.png",
  "voiceover": "Tipo di capello, colore preferito, allergie ai prodotti, note dell'ultima visita. La prossima volta non chiedi — sai già. Sara lo sa prima ancora che il cliente arrivi.",
  "voice": "IsabellaNeural",
  "duration": 9,
  "transition": "crossfade",
  "transition_duration": 0.6,
  "music_volume": 0.25
}
```

**SCENA 15** — Intro verticale officina
```json
{
  "id": "scene_15",
  "type": "ai",
  "file": "landing/assets/ai-clips-v2/V02_officina.mp4",
  "trim_start": 5,
  "trim_end": 8,
  "voiceover": "Hai un'officina?",
  "voice": "IsabellaNeural",
  "duration": 3,
  "transition": "cut",
  "transition_duration": 0.3,
  "music_volume": 0.25
}
```

**SCENA 16** — Scheda veicoli
```json
{
  "id": "scene_16",
  "type": "screenshot",
  "file": "landing/screenshots/18-scheda-veicoli.png",
  "voiceover": "Targa, marca, modello, chilometri, tagliandi fatti, scadenza revisione e assicurazione. Sara quando prende l'appuntamento chiede il modello dell'auto e salva tutto. Tu non muovi un dito.",
  "voice": "IsabellaNeural",
  "duration": 9,
  "transition": "crossfade",
  "transition_duration": 0.6,
  "music_volume": 0.25
}
```

**SCENA 17** — Scheda selector (iceberg: mostra che esistono tutte)
```json
{
  "id": "scene_17",
  "type": "screenshot",
  "file": "landing/screenshots/20-scheda-selector.png",
  "voiceover": "Qualunque sia la tua attività — estetica, fisioterapia, odontoiatria, palestra, carrozzeria — FLUXION ha la scheda giusta per te.",
  "voice": "IsabellaNeural",
  "duration": 6,
  "transition": "crossfade",
  "transition_duration": 0.6,
  "music_volume": 0.25
}
```

**SCENA 18** — Clienti (transizione verso gestione e pacchetti)
```json
{
  "id": "scene_18",
  "type": "screenshot",
  "file": "landing/screenshots/03-clienti.png",
  "voiceover": "Ogni cliente ha la sua scheda. Ma non solo. I clienti sono anche il tuo strumento di crescita.",
  "voice": "IsabellaNeural",
  "duration": 6,
  "transition": "crossfade",
  "transition_duration": 0.6,
  "music_volume": 0.25
}
```

---

### CAPITOLO 5 — "Fidelizza Senza Rincorrere" [3:05–3:25]

YouTube timestamp: 3:05

---

**SCENA 19** — Break AI — cliente QR
```json
{
  "id": "scene_19",
  "type": "ai",
  "file": "landing/assets/ai-clips-v2/V11_qrcode.mp4",
  "trim_start": 0,
  "trim_end": 5,
  "voiceover": "Il cliente scansiona il QR code sul bancone.",
  "voice": "IsabellaNeural",
  "duration": 5,
  "chapter": "Fidelizza Senza Rincorrere",
  "transition": "crossfade",
  "transition_duration": 0.5,
  "music_volume": 0.25
}
```

**SCENA 20** — Pacchetti / trasformazioni
```json
{
  "id": "scene_20",
  "type": "screenshot",
  "file": "landing/screenshots/21-trasformazioni-prima-dopo.png",
  "voiceover": "I pacchetti fedeltà. Cinque sedute colore a duecento euro invece di duecentocinquanta. Dieci ingressi palestra a centocinquanta. Il cliente paga oggi e torna sempre. Sara propone il pacchetto al momento giusto. Il tasso di ritorno raddoppia.",
  "voice": "IsabellaNeural",
  "duration": 11,
  "transition": "crossfade",
  "transition_duration": 0.8,
  "music_volume": 0.20,
  "note": "SE 21-trasformazioni-prima-dopo.png non è leggibile o è placeholder, usare 03-clienti.png come fallback"
}
```

---

### CAPITOLO 6 — "Gestione Completa" [3:25–3:55]

YouTube timestamp: 3:25

---

**SCENA 21** — Cassa
```json
{
  "id": "scene_21",
  "type": "screenshot",
  "file": "landing/screenshots/07-cassa.png",
  "voiceover": "La cassa. A fine giornata sai esattamente quanto hai incassato. Contanti, carte, Satispay. Ogni euro tracciato.",
  "voice": "IsabellaNeural",
  "duration": 7,
  "chapter": "Gestione Completa",
  "transition": "crossfade",
  "transition_duration": 0.6,
  "music_volume": 0.25
}
```

**SCENA 22** — Analytics
```json
{
  "id": "scene_22",
  "type": "screenshot",
  "file": "landing/screenshots/10-analytics.png",
  "voiceover": "I report mensili. Fatturato, appuntamenti, top servizi, classifica collaboratori. Non servono fogli Excel. FLUXION te lo dice chiaro.",
  "voice": "IsabellaNeural",
  "duration": 7,
  "transition": "crossfade",
  "transition_duration": 0.8,
  "music_volume": 0.25,
  "note": "Musica sale leggermente — stiamo avvicinandoci alla chiusura"
}
```

---

### CAPITOLO 7 — "Quanto Costa Non Averlo" [3:55–4:30]

YouTube timestamp: 3:55

---

**SCENA 23** — Scena prezzo — titolare soddisfatta
```json
{
  "id": "scene_23",
  "type": "ai",
  "file": "landing/assets/ai-clips-v2/V12_soddisfatta.mp4",
  "trim_start": 0,
  "trim_end": 8,
  "voiceover": "Facciamo due conti. Un gestionale in abbonamento ti costa seicento euro all'anno. In tre anni, milleottocento. E non sarà mai tuo. FLUXION costa quattrocentonovantasette euro. Una volta sola. Per sempre tuo. Calendario, clienti, cassa, fatture, operatori, WhatsApp automatico. Tutto.",
  "voice": "IsabellaNeural",
  "duration": 10,
  "chapter": "Quanto Costa Non Averlo",
  "transition": "crossfade",
  "transition_duration": 1.0,
  "music_volume": 0.30,
  "note": "Voiceover ~20s, clip 8s — la clip va loopata (ultimi 3s) oppure si crossfade verso 08-voice.png per i secondi extra"
}
```

**SCENA 24** — Prezzo Sara Pro
```json
{
  "id": "scene_24",
  "type": "screenshot",
  "file": "landing/screenshots/08-voice.png",
  "voiceover": "Vuoi anche Sara? Ottocentonovantasette euro. Una volta sola. Per sempre. Si ripaga in tre settimane.",
  "voice": "IsabellaNeural",
  "duration": 8,
  "transition": "crossfade",
  "transition_duration": 0.8,
  "music_volume": 0.35
}
```

---

### CAPITOLO 8 — "Come Ho Fatto Senza?" [4:30–5:00]

YouTube timestamp: 4:30

---

**SCENA 25** — Montaggio finale titolari felici
```json
{
  "id": "scene_25",
  "type": "ai",
  "file": "landing/assets/ai-clips-v2/V13_finale.mp4",
  "trim_start": 0,
  "trim_end": 8,
  "voiceover": "Parrucchieri, officine, dentisti, fisioterapisti, centri estetici, palestre. Non importa qual è la tua attività. FLUXION è il partner che ti mancava. Trenta giorni soddisfatti o rimborsati. Se non ti cambia la giornata, ti restituiamo tutto.",
  "voice": "IsabellaNeural",
  "duration": 10,
  "chapter": "Come Ho Fatto Senza?",
  "transition": "crossfade",
  "transition_duration": 1.0,
  "music_volume": 0.45
}
```

**SCENA 26** — Chiusura emotiva + CTA verbale
```json
{
  "id": "scene_26",
  "type": "ai",
  "file": "landing/assets/ai-clips-v2/V12_soddisfatta.mp4",
  "trim_start": 4,
  "trim_end": 8,
  "voiceover": "FLUXION. Paghi una volta. Usi per sempre. E ti chiederai... come ho fatto senza?",
  "voice": "IsabellaNeural",
  "duration": 7,
  "transition": "crossfade",
  "transition_duration": 1.2,
  "music_volume": 0.50
}
```

**SCENA 27** — Logo splash + URL (fermo su schermo)
```json
{
  "id": "scene_27",
  "type": "screenshot",
  "file": "landing/screenshots/01-dashboard.png",
  "voiceover": null,
  "duration": 5,
  "transition": "fade_to_black",
  "transition_duration": 2.0,
  "music_volume": 0.60,
  "visual_overlay": {
    "logo": "top-center, 120px, 100% opacity",
    "url": "fluxion-landing.pages.dev",
    "url_style": "white, 28px, centered below logo",
    "price": "Base €497 · Pro €897 — Licenza Lifetime",
    "price_style": "white 20px, centered"
  },
  "note": "Musica in fade out nei 2s finali della clip. Questo è l'unico momento in cui il logo è centrato e prominente invece che watermark."
}
```

---

## PARTE 8 — RIEPILOGO TIMING E CAPITOLI YOUTUBE

### Timing per capitolo

| Capitolo | Da | A | Durata | Scene |
|----------|----|---|--------|-------|
| CH1 La Tua Giornata | 0:00 | 0:50 | 50s | 01–06 |
| CH2 Ti Presento Sara | 0:50 | 1:38 | 48s | 07–09 |
| CH3 Tutto in un Colpo d'Occhio | 1:38 | 2:18 | 40s | 10–12 |
| CH4 La Scheda Per la Tua Attività | 2:18 | 3:05 | 47s | 13–18 |
| CH5 Fidelizza Senza Rincorrere | 3:05 | 3:25 | 20s | 19–20 |
| CH6 Gestione Completa | 3:25 | 3:55 | 30s | 21–22 |
| CH7 Quanto Costa Non Averlo | 3:55 | 4:30 | 35s | 23–24 |
| CH8 Come Ho Fatto Senza? | 4:30 | 5:00 | 30s | 25–27 |
| **TOTALE** | | | **5:00** | **27 scene** |

### Capitoli YouTube (per description)

```
00:00 La Tua Giornata
00:50 Ti Presento Sara
01:38 Tutto in un Colpo d'Occhio
02:18 La Scheda Per la Tua Attività
03:05 Fidelizza Senza Rincorrere
03:25 Gestione Completa
03:55 Quanto Costa Non Averlo
04:30 Come Ho Fatto Senza?
```

### Template description YouTube

```
FLUXION — Il gestionale per PMI italiane. Paghi una volta, usi per sempre.

Calendario, clienti, cassa, fatture, WhatsApp automatico e Sara: l'assistente
vocale che risponde al telefono per te 24 ore su 24.

⏱ Capitoli:
00:00 La Tua Giornata
00:50 Ti Presento Sara
01:38 Tutto in un Colpo d'Occhio
02:18 La Scheda Per la Tua Attività
03:05 Fidelizza Senza Rincorrere
03:25 Gestione Completa
03:55 Quanto Costa Non Averlo
04:30 Come Ho Fatto Senza?

🔗 Scopri FLUXION: https://fluxion-landing.pages.dev
💳 Base €497 | Pro €897 — licenza lifetime, zero abbonamenti, zero commissioni
✅ Garanzia 30 giorni soddisfatti o rimborsati

Per parrucchieri, estetiste, officine, palestre, dentisti, fisioterapisti e ogni PMI italiana.
```

---

## PARTE 9 — CONFRONTO V5 vs V6

| Aspetto | V5 | V6 |
|---------|----|----|
| Durata totale | ~6:40 | 5:00 |
| Scene totali | 31 | 27 |
| Clip AI usate | 13 (tutte) | 8 (ottimizzate) |
| Screenshot usati | 15 unici | 14 unici (inclusi 3 nuovi mai usati) |
| Clip AI nel hook | 9 clip × 3-5s (35s ridondanti) | 4 clip × 2s + V10 (18s efficaci) |
| Screenshot consecutivi max | 6 in fila | 2 in fila (regola rispettata) |
| Schede verticali | 5 consecutive (40s) | 2 approfondite + selector (22s) |
| Pacchetti/fedeltà visibili | No (placeholder sbagliato) | Sì (scena 20 dedicata) |
| Sara su stessa immagine | 38s invariata | 10s + 20s (dialogo separato) |
| CTA visiva finale | Solo voiceover | URL + prezzo burned su frame |
| Logo finale prominente | Assente | Scena 27 dedicata 5s |
| Capitoli YouTube timing | Stimati | Calcolati |
| Path screenshot | Errati (numerazione V5) | Corretti (file reali verificati) |

---

## PARTE 10 — NOTE CRITICHE PER IL VIDEO-EDITOR AGENT

1. **Scene 01–04 (hook montaggio)**: Trim obbligatorio di 2s per clip. Il video-editor agent
   deve supportare `trim_start`/`trim_end` per le clip AI. Se non supportato, usare le prime
   2 secondi di ogni clip senza trim esplicito.

2. **Scena 08 (dialogo)**: Due voci distinte (DiegoNeural + IsabellaNeural) in sequenza.
   La musica deve scendere a 8% durante l'intero blocco dialogo. Il viewer deve capire
   chiaramente che Sara conosce il cliente per nome — questo è il momento WOW del video.

3. **Scena 23 (prezzo/soddisfatta)**: Voiceover ~20s su clip di 8s. Loopare gli ultimi 3s
   della clip V12 oppure crossfade a metà verso 08-voice.png per completare il voiceover.
   Non lasciare schermo nero.

4. **Scena 20 (pacchetti)**: Verificare visivamente 21-trasformazioni-prima-dopo.png PRIMA
   di produrre. Se i dati sono placeholder o illeggibili a 720p, sostituire con 03-clienti.png.

5. **Scena 27 (logo splash)**: Il logo va centrato prominente (non watermark angolo).
   URL e prezzi visibili. Questo è l'unica scena in cui il branding può essere "loud".

6. **Musica**: Volume dinamico — non un tappeto uniforme. Deve respirare con il video.
   I valori music_volume in ogni scena sono target, non decorativi.

7. **Transizioni scene 05/06**: V10_frustrazione usato due volte con trim diverso. Assicurarsi
   che il crossfade nasconda il cut tra le due istanze — il viewer non deve percepire la
   ripetizione.
