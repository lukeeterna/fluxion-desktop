# FLUXION Video Demo — Sceneggiatura V4 "Lasciali a Bocca Aperta"

> **Target**: 2:30 - 3:00 minuti
> **Voce**: Edge-TTS it-IT-IsabellaNeural (-5% rate)
> **Tecnica**: Screenshot REALI statici + crossfade 0.5s + voiceover. ZERO zoompan. ZERO card Pillow.
> **Logo**: Watermark PNG burned su OGNI frame (top-left, 64px, 70% opacity)

---

## REGOLE TECNICHE (da V3 — lezioni apprese)

1. **ZERO card Pillow** — solo screenshot reali. Le card generate con Pillow hanno font brutti e appaiono nere
2. **ZERO zoompan** — le immagini sono statiche 1920x1080, crossfade tra una e l'altra
3. **ZERO ristorante** — non è una nostra verticale
4. **Massimo 15 clip** — meno clip = meno possibilità di desync
5. **Logo burned** via Pillow su ogni screenshot PRIMA di assemblare
6. **ffmpeg semplice**: `-loop 1 -t $DUR -i img.png` per ogni clip, poi concat con crossfade
7. **Audio**: un unico file MP3 Edge-TTS (tutto il copy concatenato), poi merge con slideshow

---

## STORYBOARD (15 scene, ~2:40)

### SCENA 1 — HOOK (0:00 - 0:12)
**Screenshot**: `01-dashboard.png`
**Voiceover**:
> "Il telefono squilla. Hai le mani occupate. Non puoi rispondere. Quel cliente ha già chiamato qualcun altro."

**Nota**: Dashboard in background sfocato (blur leggero via Pillow), voce drammatica. La prima cosa che vedi è FLUXION.

---

### SCENA 2 — AGITAZIONE (0:12 - 0:24)
**Screenshot**: `01-dashboard.png` (stessa, full sharp)
**Voiceover**:
> "Un cliente perso al giorno sono duecentocinquanta clienti all'anno. A trenta euro di media, sono settemilacinquecento euro buttati. E intanto, una receptionist ti costerebbe novecento euro al mese."

---

### SCENA 3 — DASHBOARD (0:24 - 0:40)
**Screenshot**: `01-dashboard.png`
**Voiceover**:
> "Ecco FLUXION. Appena lo apri, la dashboard ti mostra tutto. Appuntamenti di oggi, clienti totali, fatturato del mese, e il servizio più richiesto. Tutto in un colpo d'occhio."

---

### SCENA 4 — CALENDARIO (0:40 - 0:52)
**Screenshot**: `02-calendario.png`
**Voiceover**:
> "Il calendario. Vista settimanale, mensile, giornaliera. Per creare un appuntamento basta cliccare Nuovo Appuntamento. Scegli il cliente, il servizio, l'operatore, l'orario. Fatto. Due click."

---

### SCENA 5 — CLIENTI (0:52 - 1:04)
**Screenshot**: `03-clienti.png`
**Voiceover**:
> "La rubrica clienti. Nome, telefono, email, punteggio fedeltà. Clicchi su un cliente e vedi tutto: lo storico visite, le preferenze, le note. Sai esattamente cosa ha fatto l'ultima volta."

---

### SCENA 6 — SCHEDA PARRUCCHIERE (1:04 - 1:16)
**Screenshot**: `13-scheda-parrucchiere.png`
**Voiceover**:
> "Sei parrucchiere? Ogni cliente ha la sua scheda. Tipo di taglio, colore preferito, allergie ai prodotti. La prossima volta sai già cosa vuole. Sara risponde al telefono per te."

---

### SCENA 7 — SCHEDA VEICOLI (1:16 - 1:26)
**Screenshot**: `14-scheda-veicoli.png`
**Voiceover**:
> "Hai un'officina? La scheda veicolo tiene tutto: targa, chilometri, tagliandi, assicurazione. Sara prende l'appuntamento e salva il modello dell'auto. Tu non hai mosso un dito."

---

### SCENA 8 — SCHEDA ODONTOIATRICA (1:26 - 1:36)
**Screenshot**: `15-scheda-odontoiatrica.png`
**Voiceover**:
> "Studio medico? Anamnesi, allergie, piano terapeutico. Tutto nella scheda odontoiatrica. Il promemoria WhatsApp parte ventiquattro ore prima. La poltrona non resta vuota."

---

### SCENA 9 — SARA VOICE (1:36 - 1:54)
**Screenshot**: `08-voice.png`
**Voiceover**:
> "E poi c'è Sara. La tua receptionist che non va mai in ferie. Risponde al telefono ventiquattro ore su ventiquattro, in italiano perfetto. Capisce cosa vuole il cliente, prenota, e manda conferma WhatsApp. Tutto in automatico."

---

### SCENA 10 — SARA COSTO (1:54 - 2:04)
**Screenshot**: `08-voice.png`
**Voiceover**:
> "Come avere una segretaria. Ma non costa novecento euro al mese. È inclusa nella licenza FLUXION. Per sempre."

---

### SCENA 11 — CASSA (2:04 - 2:14)
**Screenshot**: `07-cassa.png`
**Voiceover**:
> "La cassa. A fine giornata sai esattamente quanto hai incassato. Contanti, carte, Satispay. Ogni transazione registrata."

---

### SCENA 12 — ANALYTICS (2:14 - 2:24)
**Screenshot**: `10-analytics.png`
**Voiceover**:
> "I report mensili. Fatturato, appuntamenti, top servizi, classifica operatori. Sai chi rende e dove investire."

---

### SCENA 13 — SERVIZI + OPERATORI (2:24 - 2:34)
**Screenshot**: `04-servizi.png`
**Voiceover**:
> "Il listino servizi con prezzi e durate. Gli operatori con ruoli e specializzazioni. Tutto organizzato, tutto in italiano."

---

### SCENA 14 — PREZZO (2:34 - 2:48)
**Screenshot**: `01-dashboard.png`
**Voiceover**:
> "Un gestionale in abbonamento ti costa seicento euro all'anno. In tre anni, milleottocento euro. E non sarà mai tuo. FLUXION costa quattrocentonovantasette euro. Una volta. Per sempre. Si ripaga in tre settimane."

---

### SCENA 15 — CTA (2:48 - 3:00)
**Screenshot**: `01-dashboard.png`
**Voiceover**:
> "FLUXION. Paghi una volta, usi per sempre. Nessun abbonamento. Nessuna commissione. Trenta giorni soddisfatti o rimborsati."

---

## NOTE IMPLEMENTATIVE

### Pipeline Semplificata (NO zoompan, NO card Pillow)

```python
# Per ogni scena:
1. Pillow: apri screenshot → burn logo top-left → salva in /tmp/
2. Edge-TTS: genera audio MP3 per il voiceover
3. ffprobe: leggi durata audio
4. ffmpeg: -loop 1 -t $DURATA -i prepared.png → clip.mp4 (statico)

# Assemblaggio:
5. ffmpeg concat demuxer (file list) → slideshow.mp4
6. ffmpeg: merge slideshow + audio concatenato
7. ffmpeg: fade in 1.5s + fade out 2s
8. ffmpeg: encoding finale H.264 High -crf 18 -movflags +faststart
```

### Screenshot Usati (15 scene, 10 screenshot unici)
```
01-dashboard.png        — scene 1, 2, 3, 14, 15
02-calendario.png       — scena 4
03-clienti.png          — scena 5
04-servizi.png          — scena 13
07-cassa.png            — scena 11
08-voice.png            — scene 9, 10
10-analytics.png        — scena 12
13-scheda-parrucchiere.png — scena 6
14-scheda-veicoli.png   — scena 7
15-scheda-odontoiatrica.png — scena 8
```

### Screenshot NON Usati (disponibili per future versioni)
```
05-operatori.png
06-fatture.png
09-fornitori.png
11-impostazioni.png
12-scheda-selector.png
16-scheda-estetica.png
17-scheda-fitness.png
```

### Verticali nel Video (3 su 6)
1. **Parrucchiere** — la più comune tra le PMI target
2. **Officina/Veicoli** — forte differenziazione (scheda veicolo unica)
3. **Odontoiatrica** — valore percepito alto (€200/slot vuoto)

### Verticali Escluse (per brevità)
- Estetica — simile a parrucchiere
- Fitness — nicchia più piccola
- Carrozzeria — sotto-nicchia di officina
